"""Watchdog daemon for heartbeat monitoring and automatic rollback.

Feature: decktune
Validates: Requirements 4.2, 4.3, 2.1, 2.2, 2.3, 2.4
Feature: decktune-3.0-automation
Validates: Requirements 3.2
"""

import asyncio
import logging
import os
import time
from typing import Optional, List, Tuple, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .core.safety import SafetyManager, ProgressiveRecovery
    from .core.blackbox import BlackBox

logger = logging.getLogger(__name__)


class Watchdog:
    """Monitor heartbeat and trigger rollback on timeout.
    
    The watchdog monitors a heartbeat file that should be updated periodically
    during tuning operations. If the heartbeat becomes stale (not updated for
    TIMEOUT seconds), the watchdog triggers progressive recovery:
    
    1. First attempt: reduce undervolt values by 5mV
    2. Wait for 2 heartbeat cycles to confirm stability
    3. If instability persists: full rollback to LKG values
    
    This provides safety against system freezes during undervolt tuning while
    attempting to preserve some power savings.
    
    Feature: decktune-3.0-automation
    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    
    HEARTBEAT_FILE = "/tmp/decktune_heartbeat"
    TUNING_FLAG = "/tmp/decktune_tuning_flag"
    HEARTBEAT_INTERVAL = 5   # seconds between heartbeat writes
    TIMEOUT = 30             # seconds before triggering rollback
    
    def __init__(
        self, 
        safety: "SafetyManager",
        progressive_recovery: Optional["ProgressiveRecovery"] = None,
        blackbox: Optional["BlackBox"] = None
    ):
        """Initialize watchdog.
        
        Args:
            safety: SafetyManager instance for rollback operations
            progressive_recovery: Optional ProgressiveRecovery instance for
                                  smart rollback. If None, uses direct rollback.
            blackbox: Optional BlackBox instance for metrics recording
        """
        self.safety = safety
        self._progressive_recovery = progressive_recovery
        self._blackbox = blackbox
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
    
    @property
    def progressive_recovery(self) -> Optional["ProgressiveRecovery"]:
        """Get the progressive recovery instance."""
        return self._progressive_recovery
    
    def set_progressive_recovery(self, recovery: "ProgressiveRecovery") -> None:
        """Set the progressive recovery instance.
        
        Args:
            recovery: ProgressiveRecovery instance to use for smart rollback
        """
        self._progressive_recovery = recovery
    
    def set_blackbox(self, blackbox: "BlackBox") -> None:
        """Set the BlackBox instance for metrics recording.
        
        Args:
            blackbox: BlackBox instance for recording metrics
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.2
        """
        self._blackbox = blackbox
    
    def _persist_blackbox(self, reason: str) -> Optional[str]:
        """Persist BlackBox buffer to disk.
        
        Called when instability is detected.
        
        Args:
            reason: Reason for persistence (e.g., "watchdog_timeout")
            
        Returns:
            Filename of saved recording, or None if save failed
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.2
        """
        if self._blackbox is None:
            return None
        
        filename = self._blackbox.persist_on_crash(reason)
        if filename:
            logger.info(f"BlackBox persisted on instability: {filename}")
        return filename
    
    def write_heartbeat(self) -> None:
        """Write current timestamp to heartbeat file.
        
        This should be called periodically during tuning operations
        to indicate the system is still responsive.
        
        Also notifies progressive recovery of successful heartbeat if
        recovery is in progress.
        """
        try:
            with open(self.HEARTBEAT_FILE, 'w') as f:
                f.write(str(time.time()))
            self._heartbeat_count += 1
            logger.debug(f"Heartbeat written: {self._heartbeat_count}")
            
            # Notify progressive recovery of heartbeat
            if self._progressive_recovery is not None and self._progressive_recovery.is_recovering:
                stability_confirmed, error = self._progressive_recovery.on_heartbeat()
                if stability_confirmed:
                    logger.info("Progressive recovery: stability confirmed after heartbeat")
                elif error:
                    logger.warning(f"Progressive recovery heartbeat error: {error}")
                    
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
        
        # Reset progressive recovery state if configured
        if self._progressive_recovery is not None:
            self._progressive_recovery.reset()
        
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
        
        # Reset progressive recovery state
        if self._progressive_recovery is not None:
            self._progressive_recovery.reset()
        
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
                    
                    # If progressive recovery is in REDUCED state, continue monitoring
                    if (self._progressive_recovery is not None and 
                        self._progressive_recovery.is_recovering):
                        logger.info("Progressive recovery in progress, continuing monitoring")
                        continue
                    
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in watchdog monitor loop: {e}")
    
    async def _trigger_rollback(self) -> None:
        """Trigger rollback to LKG values.
        
        Called when heartbeat timeout is detected. Uses progressive recovery
        if configured, otherwise falls back to direct LKG rollback.
        
        Also persists BlackBox metrics if configured.
        
        Feature: decktune-3.0-automation
        Validates: Requirements 2.1, 2.2, 2.3, 3.2
        """
        # Persist BlackBox before rollback
        self._persist_blackbox("watchdog_timeout")
        
        if self._progressive_recovery is not None:
            logger.warning("Watchdog triggering progressive recovery")
            
            try:
                success, error, state = self._progressive_recovery.on_instability_detected()
                
                if success:
                    from .core.safety import RecoveryStage
                    if state.stage == RecoveryStage.REDUCED:
                        logger.info(
                            f"Progressive recovery: values reduced to {state.reduced_values}, "
                            "waiting for stability"
                        )
                        # Don't stop watchdog - continue monitoring for stability
                        return
                    elif state.stage == RecoveryStage.ROLLBACK:
                        logger.info("Progressive recovery: full rollback completed")
                else:
                    logger.error(f"Progressive recovery failed: {error}")
                    
            except Exception as e:
                logger.error(f"Exception during progressive recovery: {e}")
                # Fall back to direct rollback
                logger.warning("Falling back to direct LKG rollback")
                self._direct_rollback()
        else:
            self._direct_rollback()
        
        # Stop the watchdog after rollback (unless in REDUCED state)
        self._running = False
        self.clear_heartbeat()
    
    def _direct_rollback(self) -> None:
        """Perform direct rollback to LKG values without progressive recovery."""
        logger.warning("Watchdog triggering direct rollback to LKG values")
        
        try:
            success, error = self.safety.rollback_to_lkg()
            if success:
                logger.info("Watchdog rollback successful")
            else:
                logger.error(f"Watchdog rollback failed: {error}")
        except Exception as e:
            logger.error(f"Exception during watchdog rollback: {e}")
