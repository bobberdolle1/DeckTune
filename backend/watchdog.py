"""Watchdog daemon for heartbeat monitoring and automatic rollback.

Feature: decktune
Validates: Requirements 4.2, 4.3
"""

import asyncio
import logging
import os
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .core.safety import SafetyManager

logger = logging.getLogger(__name__)


class Watchdog:
    """Monitor heartbeat and trigger rollback on timeout.
    
    The watchdog monitors a heartbeat file that should be updated periodically
    during tuning operations. If the heartbeat becomes stale (not updated for
    TIMEOUT seconds), the watchdog triggers a rollback to LKG values.
    
    This provides safety against system freezes during undervolt tuning.
    """
    
    HEARTBEAT_FILE = "/tmp/decktune_heartbeat"
    TUNING_FLAG = "/tmp/decktune_tuning_flag"
    HEARTBEAT_INTERVAL = 5   # seconds between heartbeat writes
    TIMEOUT = 30             # seconds before triggering rollback
    
    def __init__(self, safety: "SafetyManager"):
        """Initialize watchdog.
        
        Args:
            safety: SafetyManager instance for rollback operations
        """
        self.safety = safety
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._heartbeat_count = 0  # Track number of heartbeats written
    
    @property
    def is_running(self) -> bool:
        """Check if watchdog is currently running."""
        return self._running
    
    @property
    def heartbeat_count(self) -> int:
        """Get the number of heartbeats written since start."""
        return self._heartbeat_count
    
    def write_heartbeat(self) -> None:
        """Write current timestamp to heartbeat file.
        
        This should be called periodically during tuning operations
        to indicate the system is still responsive.
        """
        try:
            with open(self.HEARTBEAT_FILE, 'w') as f:
                f.write(str(time.time()))
            self._heartbeat_count += 1
            logger.debug(f"Heartbeat written: {self._heartbeat_count}")
        except IOError as e:
            logger.warning(f"Failed to write heartbeat: {e}")
    
    def read_heartbeat(self) -> Optional[float]:
        """Read the last heartbeat timestamp.
        
        Returns:
            The timestamp as float, or None if file doesn't exist or is invalid
        """
        try:
            if os.path.exists(self.HEARTBEAT_FILE):
                with open(self.HEARTBEAT_FILE, 'r') as f:
                    return float(f.read().strip())
        except (IOError, ValueError) as e:
            logger.warning(f"Failed to read heartbeat: {e}")
        return None
    
    def clear_heartbeat(self) -> None:
        """Remove the heartbeat file."""
        try:
            if os.path.exists(self.HEARTBEAT_FILE):
                os.remove(self.HEARTBEAT_FILE)
        except IOError as e:
            logger.warning(f"Failed to clear heartbeat file: {e}")
    
    def is_heartbeat_stale(self) -> bool:
        """Check if the heartbeat is stale (older than TIMEOUT).
        
        Returns:
            True if heartbeat is stale or missing, False otherwise
        """
        last_heartbeat = self.read_heartbeat()
        if last_heartbeat is None:
            return True
        
        elapsed = time.time() - last_heartbeat
        return elapsed >= self.TIMEOUT

    async def start(self) -> None:
        """Start heartbeat monitoring.
        
        This starts the monitoring loop that checks for stale heartbeats
        and triggers rollback if needed.
        """
        if self._running:
            logger.warning("Watchdog already running")
            return
        
        self._running = True
        self._heartbeat_count = 0
        
        # Write initial heartbeat
        self.write_heartbeat()
        
        # Start the monitoring loop
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Watchdog started")
    
    async def stop(self) -> None:
        """Stop monitoring.
        
        This stops the monitoring loop and cleans up the heartbeat file.
        """
        if not self._running:
            return
        
        self._running = False
        
        # Cancel the monitor task if running
        if self._monitor_task is not None:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
        
        # Clean up heartbeat file
        self.clear_heartbeat()
        logger.info("Watchdog stopped")
    
    async def _monitor_loop(self) -> None:
        """Check heartbeat periodically, trigger rollback if stale.
        
        This loop runs continuously while the watchdog is active,
        checking the heartbeat file at regular intervals.
        """
        check_interval = self.HEARTBEAT_INTERVAL  # Check at same rate as heartbeat
        
        while self._running:
            try:
                await asyncio.sleep(check_interval)
                
                if not self._running:
                    break
                
                # Check if heartbeat is stale
                if self.is_heartbeat_stale():
                    logger.warning(
                        f"Heartbeat stale for >= {self.TIMEOUT}s, triggering rollback"
                    )
                    await self._trigger_rollback()
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in watchdog monitor loop: {e}")
    
    async def _trigger_rollback(self) -> None:
        """Trigger rollback to LKG values.
        
        Called when heartbeat timeout is detected.
        """
        logger.warning("Watchdog triggering rollback to LKG values")
        
        try:
            success, error = self.safety.rollback_to_lkg()
            if success:
                logger.info("Watchdog rollback successful")
            else:
                logger.error(f"Watchdog rollback failed: {error}")
        except Exception as e:
            logger.error(f"Exception during watchdog rollback: {e}")
        
        # Stop the watchdog after rollback
        self._running = False
        self.clear_heartbeat()
