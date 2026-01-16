"""Event emitter for frontend communication.

Feature: decktune, API and Events Module
Validates: Requirements 2.6

This module provides event emission capabilities for communicating
status updates, autotune progress, and test results to the frontend.
"""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tuning.autotune import AutotuneResult
    from ..tuning.runner import TestResult
    from ..tuning.binning import BinningResult

logger = logging.getLogger(__name__)


class EventEmitter:
    """Emit events to frontend via Decky.
    
    Provides methods to emit various event types to the frontend:
    - Status updates (enabled/disabled/error/scheduled/dynamic_running)
    - Autotune progress (phase, core, value, ETA)
    - Autotune completion
    - Test progress and completion
    
    Requirements: 2.6
    """
    
    def __init__(self, decky_emit=None):
        """Initialize the event emitter.
        
        Args:
            decky_emit: The decky.emit function for sending events.
                       If None, events will only be logged.
        """
        self._emit = decky_emit
    
    def set_emit_function(self, emit_fn) -> None:
        """Set the emit function for sending events.
        
        Args:
            emit_fn: The decky.emit function
        """
        self._emit = emit_fn
    
    async def _emit_event(self, event_type: str, data: Any) -> None:
        """Internal method to emit an event.
        
        Args:
            event_type: Type of event (e.g., "update_status", "tuning_progress")
            data: Event payload data
        """
        if self._emit is not None:
            try:
                await self._emit("server_event", {
                    "type": event_type,
                    "data": data
                })
                logger.debug(f"Emitted event: {event_type} with data: {data}")
            except Exception as e:
                logger.warning(f"Failed to emit event {event_type}: {e}")
        else:
            logger.debug(f"Event (no emitter): {event_type} with data: {data}")
    
    async def emit_status(self, status: str) -> None:
        """Emit status update.
        
        Args:
            status: Status string - one of:
                   "enabled", "disabled", "error", "scheduled", "dynamic_running"
        """
        logger.info(f"Status update: {status}")
        await self._emit_event("update_status", status)
    
    async def emit_tuning_progress(
        self,
        phase: str,
        core: int,
        value: int,
        eta: int
    ) -> None:
        """Emit autotune progress.
        
        Args:
            phase: Current phase ("A" or "B")
            core: Current core index (0-3)
            value: Current undervolt value being tested
            eta: Estimated time remaining in seconds
            
        Requirements: 2.6
        """
        progress_data = {
            "phase": phase,
            "core": core,
            "value": value,
            "eta": eta
        }
        logger.debug(f"Tuning progress: phase={phase}, core={core}, value={value}, eta={eta}")
        await self._emit_event("tuning_progress", progress_data)
    
    async def emit_tuning_complete(self, result: "AutotuneResult") -> None:
        """Emit autotune completion.
        
        Args:
            result: AutotuneResult with final values and statistics
        """
        result_data = {
            "cores": result.cores,
            "duration": result.duration,
            "tests_run": result.tests_run,
            "stable": result.stable
        }
        logger.info(f"Tuning complete: {result_data}")
        await self._emit_event("tuning_complete", result_data)
    
    async def emit_test_progress(self, test_name: str, progress: int) -> None:
        """Emit test progress percentage.
        
        Args:
            test_name: Name of the running test
            progress: Progress percentage (0-100)
        """
        progress_data = {
            "test_name": test_name,
            "progress": progress
        }
        logger.debug(f"Test progress: {test_name} at {progress}%")
        await self._emit_event("test_progress", progress_data)
    
    async def emit_test_complete(self, result: "TestResult") -> None:
        """Emit test completion.
        
        Args:
            result: TestResult with pass/fail status and details
        """
        result_data = {
            "passed": result.passed,
            "duration": result.duration,
            "logs": result.logs,
            "error": result.error
        }
        logger.info(f"Test complete: passed={result.passed}, duration={result.duration:.1f}s")
        await self._emit_event("test_complete", result_data)
    
    async def emit_binning_progress(
        self,
        current_value: int,
        iteration: int,
        last_stable: int,
        eta: int
    ) -> None:
        """Emit binning progress.
        
        Args:
            current_value: Current test value being tested
            iteration: Current iteration number
            last_stable: Last stable value found
            eta: Estimated time remaining in seconds
            
        Requirements: 8.1, 8.2
        """
        progress_data = {
            "current_value": current_value,
            "iteration": iteration,
            "last_stable": last_stable,
            "eta": eta
        }
        logger.debug(f"Binning progress: iteration={iteration}, current={current_value}, "
                    f"last_stable={last_stable}, eta={eta}s")
        await self._emit_event("binning_progress", progress_data)
    
    async def emit_binning_complete(self, result: "BinningResult") -> None:
        """Emit binning completion.
        
        Args:
            result: BinningResult with discovered limits and statistics
            
        Requirements: 8.3, 8.4
        """
        result_data = {
            "max_stable": result.max_stable,
            "recommended": result.recommended,
            "iterations": result.iterations,
            "duration": result.duration,
            "aborted": result.aborted
        }
        logger.info(f"Binning complete: max_stable={result.max_stable}, "
                   f"recommended={result.recommended}, iterations={result.iterations}")
        await self._emit_event("binning_complete", result_data)
    
    async def emit_binning_error(self, error_message: str) -> None:
        """Emit binning error.
        
        Args:
            error_message: Error message describing the failure
            
        Requirements: 8.3, 8.4
        """
        error_data = {
            "error": error_message
        }
        logger.error(f"Binning error: {error_message}")
        await self._emit_event("binning_error", error_data)

    
    async def emit_profile_changed(self, profile_name: str, app_id: Optional[int]) -> None:
        """Emit profile change event.
        
        Args:
            profile_name: Name of the active profile
            app_id: Steam AppID (None for global default)
            
        Requirements: 4.4
        """
        profile_data = {
            "profile_name": profile_name,
            "app_id": app_id
        }
        logger.info(f"Profile changed: {profile_name} (app_id: {app_id})")
        await self._emit_event("profile_changed", profile_data)
