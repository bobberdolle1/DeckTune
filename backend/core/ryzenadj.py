"""Wrapper for ryzenadj CLI operations.

This module provides a wrapper around the ryzenadj CLI tool for applying
undervolt values to AMD APU cores on Steam Deck.

Feature: decktune
Validates: Requirements 9.1, 9.2, 9.3, 9.4

Feature: decktune-critical-fixes
Validates: Requirements 1.1, 1.2, 1.5
"""

import asyncio
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

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
    
    async def diagnose(self) -> Dict[str, Any]:
        """Диагностика состояния ryzenadj.
        
        Проверяет доступность binary, права sudo, выполняет тестовый запуск.
        
        Returns:
            Dictionary с результатами диагностики:
            - binary_exists: bool - существует ли файл binary
            - binary_executable: bool - является ли файл исполняемым
            - sudo_available: bool - доступен ли sudo
            - test_command_result: Optional[str] - результат тестовой команды
            - error: Optional[str] - сообщение об ошибке (если есть)
            
        Feature: decktune-critical-fixes
        Validates: Requirements 1.1, 1.2, 1.5
        """
        result: Dict[str, Any] = {
            "binary_exists": False,
            "binary_executable": False,
            "sudo_available": False,
            "test_command_result": None,
            "error": None,
        }
        
        logger.info(f"Starting ryzenadj diagnostics for binary: {self.binary_path}")
        
        # 1. Проверка существования binary
        try:
            binary_exists = os.path.exists(self.binary_path)
            result["binary_exists"] = binary_exists
            logger.debug(f"Binary exists check: {binary_exists} (path: {self.binary_path})")
            
            if not binary_exists:
                error_msg = f"ryzenadj binary not found at {self.binary_path}"
                result["error"] = error_msg
                logger.error(error_msg)
                return result
        except Exception as e:
            error_msg = f"Error checking binary existence: {str(e)}"
            result["error"] = error_msg
            logger.error(error_msg)
            return result
        
        # 2. Проверка прав на исполнение
        try:
            binary_executable = os.access(self.binary_path, os.X_OK)
            result["binary_executable"] = binary_executable
            logger.debug(f"Binary executable check: {binary_executable}")
            
            if not binary_executable:
                error_msg = f"ryzenadj binary is not executable: {self.binary_path}"
                result["error"] = error_msg
                logger.error(error_msg)
                return result
        except Exception as e:
            error_msg = f"Error checking binary permissions: {str(e)}"
            result["error"] = error_msg
            logger.error(error_msg)
            return result
        
        # 3. Проверка доступности sudo
        try:
            logger.debug("Checking sudo availability...")
            sudo_check = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ["sudo", "-n", "true"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            )
            sudo_available = sudo_check.returncode == 0
            result["sudo_available"] = sudo_available
            logger.debug(f"Sudo availability check: {sudo_available}")
            
            if not sudo_available:
                error_msg = "sudo is not available without password (NOPASSWD not configured)"
                result["error"] = error_msg
                logger.warning(error_msg)
                # Продолжаем диагностику, так как sudo может запросить пароль
        except subprocess.TimeoutExpired:
            error_msg = "sudo check timed out"
            result["error"] = error_msg
            logger.warning(error_msg)
        except FileNotFoundError:
            error_msg = "sudo command not found"
            result["error"] = error_msg
            logger.error(error_msg)
            return result
        except Exception as e:
            error_msg = f"Error checking sudo: {str(e)}"
            result["error"] = error_msg
            logger.warning(error_msg)
        
        # 4. Тестовый запуск ryzenadj --info (безопасная команда)
        try:
            logger.debug("Running test command: ryzenadj --info")
            test_command = ["sudo", self.binary_path, "--info"]
            test_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    test_command,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            )
            
            if test_result.returncode == 0:
                result["test_command_result"] = test_result.stdout.strip() if test_result.stdout else "Success (no output)"
                result["error"] = None  # Очищаем предыдущие некритичные ошибки
                logger.info("ryzenadj test command executed successfully")
                logger.debug(f"Test command output: {result['test_command_result'][:200]}...")
            else:
                stderr_content = test_result.stderr.strip() if test_result.stderr else ""
                error_msg = f"ryzenadj test command failed (code {test_result.returncode}): {stderr_content}"
                result["test_command_result"] = None
                result["error"] = error_msg
                logger.error(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "ryzenadj test command timed out"
            result["error"] = error_msg
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Error running test command: {str(e)}"
            result["error"] = error_msg
            logger.error(error_msg)
        
        logger.info(f"Diagnostics complete: binary_exists={result['binary_exists']}, "
                   f"binary_executable={result['binary_executable']}, "
                   f"sudo_available={result['sudo_available']}, "
                   f"has_error={result['error'] is not None}")
        
        return result
    
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
            
        Feature: decktune-critical-fixes
        Validates: Requirements 1.1, 1.2, 9.2, 9.4
        """
        logger.info(f"apply_values_async called with cores: {cores}")
        
        # Валидация входных данных
        if len(cores) != 4:
            error_msg = "Expected exactly 4 core values"
            logger.error(f"Validation failed: {error_msg}")
            await self._emit_error_status(error_msg)
            return False, error_msg
        
        # Проверка диапазона значений
        for idx, value in enumerate(cores):
            if not isinstance(value, int):
                error_msg = f"Core {idx} value must be integer, got {type(value).__name__}"
                logger.error(f"Validation failed: {error_msg}")
                await self._emit_error_status(error_msg)
                return False, error_msg
            if value > 0:
                error_msg = f"Core {idx} value must be <= 0, got {value}"
                logger.error(f"Validation failed: {error_msg}")
                await self._emit_error_status(error_msg)
                return False, error_msg
            if value < -200:
                error_msg = f"Core {idx} value {value} is dangerously low (< -200mV)"
                logger.error(f"Validation failed: {error_msg}")
                await self._emit_error_status(error_msg)
                return False, error_msg
        
        logger.debug(f"Input validation passed for cores: {cores}")
        
        # Проверка доступности binary перед применением
        if not os.path.exists(self.binary_path):
            error_msg = f"ryzenadj binary not found at {self.binary_path}"
            logger.error(error_msg)
            await self._emit_error_status(error_msg)
            return False, error_msg
        
        if not os.access(self.binary_path, os.X_OK):
            error_msg = f"ryzenadj binary is not executable: {self.binary_path}"
            logger.error(error_msg)
            await self._emit_error_status(error_msg)
            return False, error_msg
        
        logger.debug(f"Binary check passed: {self.binary_path}")
        
        self._last_commands = []  # Reset command tracking
        self._last_error = None  # Reset error tracking
        
        for core_idx, value in enumerate(cores):
            hex_value = self.calculate_hex(core_idx, value)
            
            # Валидация hex-значения
            try:
                parsed_hex = int(hex_value, 16)
                logger.debug(f"Core {core_idx}: value={value}mV -> hex={hex_value} (parsed={parsed_hex})")
            except ValueError as e:
                error_msg = f"Invalid hex value generated for core {core_idx}: {hex_value}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            
            command = ["sudo", self.binary_path, f"--set-coper={hex_value}"]
            command_str = " ".join(command)
            self._last_commands.append(command_str)
            
            logger.info(f"Executing command for core {core_idx}: {command_str}")
            
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
                
                logger.debug(f"Core {core_idx} command completed: returncode={result.returncode}")
                
                if result.stdout:
                    stdout_content = result.stdout.strip()
                    if stdout_content:
                        logger.debug(f"Core {core_idx} stdout: {stdout_content}")
                
                if result.returncode != 0:
                    stderr_content = result.stderr.strip() if result.stderr else ""
                    error_msg = stderr_content if stderr_content else f"ryzenadj returned code {result.returncode}"
                    logger.error(f"ryzenadj failed for core {core_idx}: returncode={result.returncode}, stderr={stderr_content}")
                    await self._emit_error_status(error_msg)
                    return False, error_msg
                    
                # Check stderr even on success (warnings)
                if result.stderr:
                    stderr_content = result.stderr.strip()
                    if stderr_content:
                        logger.warning(f"ryzenadj stderr for core {core_idx} (success): {stderr_content}")
                        if "error" in stderr_content.lower() or "fail" in stderr_content.lower():
                            logger.error(f"Error keyword detected in stderr for core {core_idx}")
                            await self._emit_error_status(stderr_content)
                            return False, stderr_content
                
                logger.debug(f"Core {core_idx} undervolt applied successfully: {value}mV")
                            
            except subprocess.TimeoutExpired:
                error_msg = f"ryzenadj timed out for core {core_idx} (timeout=10s)"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            except FileNotFoundError:
                error_msg = f"ryzenadj binary not found at {self.binary_path}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            except PermissionError as e:
                error_msg = f"Permission denied running ryzenadj for core {core_idx}: {str(e)}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
            except Exception as e:
                error_msg = f"Unexpected error running ryzenadj for core {core_idx}: {type(e).__name__}: {str(e)}"
                logger.error(error_msg)
                await self._emit_error_status(error_msg)
                return False, error_msg
        
        logger.info(f"Successfully applied undervolt values to all 4 cores: {cores}")
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
