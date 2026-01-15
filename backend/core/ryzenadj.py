"""Wrapper for ryzenadj CLI operations.

This module provides a wrapper around the ryzenadj CLI tool for applying
undervolt values to AMD APU cores on Steam Deck.

Feature: decktune
Validates: Requirements 9.1, 9.2, 9.3, 9.4
"""

import asyncio
import logging
import subprocess
from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.events import EventEmitter

logger = logging.getLogger(__name__)


class RyzenadjWrapper:
    """Wrapper for ryzenadj CLI operations.
    
    Provides methods to apply undervolt values to CPU cores using the
    ryzenadj command-line tool. Handles hex value calculation and
    subprocess execution.
    """
    
    def __init__(self, binary_path: str, working_dir: str, 
                 event_emitter: Optional["EventEmitter"] = None):
        """Initialize the ryzenadj wrapper.
        
        Args:
            binary_path: Path to ryzenadj binary
            working_dir: Working directory for subprocess calls
            event_emitter: Optional event emitter for status updates
        """
        self.binary_path = binary_path
        self.working_dir = working_dir
        self.event_emitter = event_emitter
        self._last_commands: List[str] = []  # Track commands for testing
        self._last_error: Optional[str] = None  # Track last error for testing
    
    def set_event_emitter(self, event_emitter: "EventEmitter") -> None:
        """Set the event emitter for status updates.
        
        Args:
            event_emitter: EventEmitter instance
        """
        self.event_emitter = event_emitter
    
    @staticmethod
    def calculate_hex(core: int, value: int) -> str:
        """Calculate hex value for ryzenadj --set-coper.
        
        Formula: (core * 0x100000) + (value & 0xFFFFF)
        
        The formula encodes both the core index and the undervolt value
        into a single hex value that ryzenadj understands.
        
        Args:
            core: Core index (0-3)
            value: Undervolt value (negative or zero integer)
            
        Returns:
            Hex string representation (uppercase with 0X prefix)
            
        Example:
            >>> RyzenadjWrapper.calculate_hex(0, -30)
            '0XFFFE2'
            >>> RyzenadjWrapper.calculate_hex(1, -30)
            '0X1FFFE2'
        """
        core_shifted = core * 0x100000
        magnitude = value & 0xFFFFF
        combined_value = core_shifted + magnitude
        return hex(combined_value).upper()

    async def _emit_error_status(self, error_msg: str) -> None:
        """Emit error status to frontend via event emitter.
        
        Args:
            error_msg: Error message to log
            
        Validates: Requirements 9.4
        """
        self._last_error = error_msg
        logger.error(f"Ryzenadj error: {error_msg}")
        
        if self.event_emitter is not None:
            try:
                await self.event_emitter.emit_status("error")
            except Exception as e:
                logger.warning(f"Failed to emit error status: {e}")
    
    def _emit_error_status_sync(self, error_msg: str) -> None:
        """Synchronously emit error status (schedules async emission).
        
        Args:
            error_msg: Error message to log
        """
        self._last_error = error_msg
        logger.error(f"Ryzenadj error: {error_msg}")
        
        if self.event_emitter is not None:
            try:
                # Try to get the running event loop and schedule the coroutine
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.event_emitter.emit_status("error"))
                else:
                    loop.run_until_complete(self.event_emitter.emit_status("error"))
            except RuntimeError:
                # No event loop available, log warning
                logger.warning("Cannot emit error status: no event loop available")
            except Exception as e:
                logger.warning(f"Failed to emit error status: {e}")
    
    def apply_values(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
        """Apply undervolt values to all cores.
        
        Executes `sudo ryzenadj --set-coper=<hex>` for each of the 4 cores.
        
        Args:
            cores: List of 4 integers (undervolt values, typically negative)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            
        Validates: Requirements 9.2, 9.4
        """
        if len(cores) != 4:
            error_msg = "Expected exactly 4 core values"
            self._emit_error_status_sync(error_msg)
            return False, error_msg
        
        self._last_commands = []  # Reset command tracking
        self._last_error = None  # Reset error tracking
        
        for core_idx, value in enumerate(cores):
            hex_value = self.calculate_hex(core_idx, value)
            command = ["sudo", self.binary_path, f"--set-coper={hex_value}"]
            self._last_commands.append(" ".join(command))
            
            logger.debug(f"Applying undervolt to core {core_idx}: {value} (hex: {hex_value})")
            
            try:
                result = subprocess.run(
                    command,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=10  # 10 second timeout per command
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else f"ryzenadj returned code {result.returncode}"
                    logger.error(f"ryzenadj failed for core {core_idx}: {error_msg}")
                    self._emit_error_status_sync(error_msg)
                    return False, error_msg
                    
                # Check stderr even on success (warnings)
                if result.stderr:
                    stderr_content = result.stderr.strip()
                    if stderr_content:
                        logger.warning(f"ryzenadj stderr for core {core_idx}: {stderr_content}")
                        # Only treat as error if it looks like an actual error
                        if "error" in stderr_content.lower() or "fail" in stderr_content.lower():
                            self._emit_error_status_sync(stderr_content)
                            return False, stderr_content
                            
            except subprocess.TimeoutExpired:
                error_msg = f"ryzenadj timed out for core {core_idx}"
                logger.error(error_msg)
                self._emit_error_status_sync(error_msg)
                return False, error_msg
            except FileNotFoundError:
                error_msg = f"ryzenadj binary not found at {self.binary_path}"
                logger.error(error_msg)
                self._emit_error_status_sync(error_msg)
                return False, error_msg
            except Exception as e:
                error_msg = f"Unexpected error running ryzenadj: {str(e)}"
                logger.error(error_msg)
                self._emit_error_status_sync(error_msg)
                return False, error_msg
        
        logger.info(f"Successfully applied undervolt values: {cores}")
        return True, None

    async def apply_values_async(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
        """Apply undervolt values to all cores (async version).
        
        Executes `sudo ryzenadj --set-coper=<hex>` for each of the 4 cores.
        This async version properly awaits error status emission.
        
        Args:
            cores: List of 4 integers (undervolt values, typically negative)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            
        Validates: Requirements 9.2, 9.4
        """
        if len(cores) != 4:
            error_msg = "Expected exactly 4 core values"
            await self._emit_error_status(error_msg)
            return False, error_msg
        
        self._last_commands = []  # Reset command tracking
        self._last_error = None  # Reset error tracking
        
        for core_idx, value in enumerate(cores):
            hex_value = self.calculate_hex(core_idx, value)
            command = ["sudo", self.binary_path, f"--set-coper={hex_value}"]
            self._last_commands.append(" ".join(command))
            
            logger.debug(f"Applying undervolt to core {core_idx}: {value} (hex: {hex_value})")
            
            try:
                # Run subprocess in executor to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda cmd=command: subprocess.run(
                        cmd,
                        cwd=self.working_dir,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else f"ryzenadj returned code {result.returncode}"
                    logger.error(f"ryzenadj failed for core {core_idx}: {error_msg}")
                    await self._emit_error_status(error_msg)
                    return False, error_msg
                    
                # Check stderr even on success (warnings)
                if result.stderr:
                    stderr_content = result.stderr.strip()
                    if stderr_content:
                        logger.warning(f"ryzenadj stderr for core {core_idx}: {stderr_content}")
                        if "error" in stderr_content.lower() or "fail" in stderr_content.lower():
                            await self._emit_error_status(stderr_content)
                            return False, stderr_content
                            
            except subprocess.TimeoutExpired:
                error_msg = f"ryzenadj timed out for core {core_idx}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            except FileNotFoundError:
                error_msg = f"ryzenadj binary not found at {self.binary_path}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            except Exception as e:
                error_msg = f"Unexpected error running ryzenadj: {str(e)}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
        
        logger.info(f"Successfully applied undervolt values: {cores}")
        return True, None
    
    def disable(self) -> Tuple[bool, Optional[str]]:
        """Reset all cores to 0 (no undervolt).
        
        Applies value 0 to all 4 cores, effectively disabling any undervolt.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            
        Validates: Requirements 9.3
        """
        logger.info("Disabling undervolt (resetting all cores to 0)")
        return self.apply_values([0, 0, 0, 0])
    
    async def disable_async(self) -> Tuple[bool, Optional[str]]:
        """Reset all cores to 0 (no undervolt) - async version.
        
        Applies value 0 to all 4 cores, effectively disabling any undervolt.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            
        Validates: Requirements 9.3
        """
        logger.info("Disabling undervolt (resetting all cores to 0)")
        return await self.apply_values_async([0, 0, 0, 0])
    
    def get_last_commands(self) -> List[str]:
        """Get the last executed commands (for testing purposes).
        
        Returns:
            List of command strings that were executed
        """
        return self._last_commands.copy()
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message (for testing purposes).
        
        Returns:
            Last error message or None if no error
        """
        return self._last_error
