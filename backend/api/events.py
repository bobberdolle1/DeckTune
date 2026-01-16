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
    
    async def emit_context_changed(self, context: dict) -> None:
        """Emit context change event.
        
        Args:
            context: Dictionary containing current system context
                    (battery_percent, power_mode, temperature_c)
            
        Requirements: 1.3, 1.4
        """
        logger.info(f"Context changed: {context}")
        await self._emit_event("context_changed", context)
    
    async def emit_profile_switched_by_context(
        self,
        old_profile: Optional[str],
        new_profile: str,
        reason: str
    ) -> None:
        """Emit profile switched by context event.
        
        Args:
            old_profile: Name of the previous profile (None if none)
            new_profile: Name of the new profile
            reason: Reason for the switch (e.g., "battery_threshold", "power_mode")
            
        Requirements: 1.3, 1.4
        """
        switch_data = {
            "old_profile": old_profile,
            "new_profile": new_profile,
            "reason": reason
        }
        logger.info(f"Profile switched by context: {old_profile} -> {new_profile} ({reason})")
        await self._emit_event("profile_switched_by_context", switch_data)
    
    # Iron Seeker Events
    # Requirements: 5.1, 5.2, 5.3, 3.4
    
    async def emit_iron_seeker_progress(
        self,
        core: int,
        value: int,
        iteration: int,
        eta: int,
        core_results: list
    ) -> None:
        """Emit Iron Seeker progress event.
        
        Args:
            core: Current core being tested (0-3)
            value: Current undervolt value being tested (mV, ≤0)
            iteration: Current iteration number (≥1)
            eta: Estimated time remaining in seconds (≥0)
            core_results: Results so far [c0, c1, c2, c3] (array of 4 integers)
            
        Requirements: 5.1
        """
        progress_data = {
            "core": core,
            "value": value,
            "iteration": iteration,
            "eta": eta,
            "coreResults": core_results
        }
        logger.debug(
            f"Iron Seeker progress: core={core}, value={value}mV, "
            f"iteration={iteration}, eta={eta}s"
        )
        await self._emit_event("iron_seeker_progress", progress_data)
    
    async def emit_iron_seeker_core_complete(
        self,
        core: int,
        max_stable: int,
        recommended: int,
        tier: str
    ) -> None:
        """Emit Iron Seeker core completion event.
        
        Args:
            core: Core that completed testing (0-3)
            max_stable: Maximum stable undervolt found (mV)
            recommended: Recommended value with safety margin (mV)
            tier: Quality tier ("gold", "silver", or "bronze")
            
        Requirements: 5.2
        """
        core_data = {
            "core": core,
            "maxStable": max_stable,
            "recommended": recommended,
            "tier": tier
        }
        logger.info(
            f"Iron Seeker core {core} complete: max_stable={max_stable}mV, "
            f"recommended={recommended}mV, tier={tier}"
        )
        await self._emit_event("iron_seeker_core_complete", core_data)
    
    async def emit_iron_seeker_complete(
        self,
        cores: list,
        duration: float,
        recovered: bool,
        aborted: bool
    ) -> None:
        """Emit Iron Seeker completion event.
        
        Args:
            cores: List of CoreResult dictionaries for all 4 cores
            duration: Total time in seconds (>0)
            recovered: True if recovered from crash
            aborted: True if cancelled or hit limit early
            
        Requirements: 5.3
        """
        complete_data = {
            "cores": cores,
            "duration": duration,
            "recovered": recovered,
            "aborted": aborted
        }
        logger.info(
            f"Iron Seeker complete: duration={duration:.1f}s, "
            f"recovered={recovered}, aborted={aborted}"
        )
        await self._emit_event("iron_seeker_complete", complete_data)
    
    async def emit_iron_seeker_recovery(
        self,
        crashed_core: int,
        crashed_value: int,
        restored_values: list
    ) -> None:
        """Emit Iron Seeker recovery event.
        
        Args:
            crashed_core: Core that was being tested when crash occurred (0-3)
            crashed_value: Value that was being tested when crash occurred (mV)
            restored_values: Values restored after recovery [c0, c1, c2, c3]
            
        Requirements: 3.4
        """
        recovery_data = {
            "crashedCore": crashed_core,
            "crashedValue": crashed_value,
            "restoredValues": restored_values
        }
        logger.info(
            f"Iron Seeker recovery: crashed at core {crashed_core}, "
            f"value {crashed_value}mV, restored: {restored_values}"
        )
        await self._emit_event("iron_seeker_recovery", recovery_data)

    # Progressive Recovery Events
    # Requirements: 2.5
    
    async def emit_progressive_recovery_started(
        self,
        original_values: list,
        reduced_values: list,
        reduction_amount: int
    ) -> None:
        """Emit progressive recovery started event.
        
        Args:
            original_values: Values before reduction [c0, c1, c2, c3]
            reduced_values: Values after reduction [c0, c1, c2, c3]
            reduction_amount: Amount reduced in mV
            
        Requirements: 2.5
        """
        recovery_data = {
            "originalValues": original_values,
            "reducedValues": reduced_values,
            "reductionAmount": reduction_amount
        }
        logger.info(
            f"Progressive recovery started: {original_values} -> {reduced_values} "
            f"(reduction: {reduction_amount}mV)"
        )
        await self._emit_event("progressive_recovery_started", recovery_data)
    
    async def emit_progressive_recovery_success(
        self,
        reduced_values: list,
        heartbeats_waited: int
    ) -> None:
        """Emit progressive recovery success event.
        
        Args:
            reduced_values: Values that became new LKG [c0, c1, c2, c3]
            heartbeats_waited: Number of heartbeats waited for stability
            
        Requirements: 2.4, 2.5
        """
        success_data = {
            "reducedValues": reduced_values,
            "heartbeatsWaited": heartbeats_waited
        }
        logger.info(
            f"Progressive recovery success: new LKG {reduced_values} "
            f"(waited {heartbeats_waited} heartbeats)"
        )
        await self._emit_event("progressive_recovery_success", success_data)
    
    async def emit_progressive_recovery_failed(
        self,
        original_values: list,
        lkg_values: list,
        reason: str
    ) -> None:
        """Emit progressive recovery failed event.
        
        Args:
            original_values: Values before recovery attempt [c0, c1, c2, c3]
            lkg_values: LKG values rolled back to [c0, c1, c2, c3]
            reason: Reason for failure (e.g., "instability_persisted")
            
        Requirements: 2.3, 2.5
        """
        failed_data = {
            "originalValues": original_values,
            "lkgValues": lkg_values,
            "reason": reason
        }
        logger.info(
            f"Progressive recovery failed: rolled back to LKG {lkg_values} "
            f"(reason: {reason})"
        )
        await self._emit_event("progressive_recovery_failed", failed_data)

    # BlackBox Events
    # Requirements: 3.2
    
    async def emit_blackbox_saved(
        self,
        filename: str,
        reason: str,
        sample_count: int,
        duration_sec: float
    ) -> None:
        """Emit blackbox saved event.
        
        Args:
            filename: Name of the saved recording file
            reason: Reason for saving (e.g., "watchdog_timeout", "crash_detected")
            sample_count: Number of samples in the recording
            duration_sec: Duration of recorded data in seconds
            
        Requirements: 3.2
        """
        saved_data = {
            "filename": filename,
            "reason": reason,
            "sampleCount": sample_count,
            "durationSec": duration_sec
        }
        logger.info(
            f"BlackBox saved: {filename} (reason: {reason}, "
            f"samples: {sample_count}, duration: {duration_sec:.1f}s)"
        )
        await self._emit_event("blackbox_saved", saved_data)

    # Telemetry Events
    # Feature: decktune-3.1-reliability-ux
    # Validates: Requirements 2.1, 2.2
    
    async def emit_telemetry_sample(
        self,
        timestamp: float,
        temperature_c: float,
        power_w: float,
        load_percent: float
    ) -> None:
        """Emit telemetry sample event.
        
        Args:
            timestamp: Unix timestamp of the sample
            temperature_c: CPU temperature in Celsius
            power_w: Power consumption in Watts
            load_percent: CPU load percentage (0-100)
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 2.1, 2.2
        """
        sample_data = {
            "timestamp": timestamp,
            "temperature_c": temperature_c,
            "power_w": power_w,
            "load_percent": load_percent
        }
        logger.debug(
            f"Telemetry sample: temp={temperature_c:.1f}°C, "
            f"power={power_w:.1f}W, load={load_percent:.1f}%"
        )
        await self._emit_event("telemetry_sample", sample_data)
