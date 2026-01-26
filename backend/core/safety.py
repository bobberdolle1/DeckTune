"""Safety manager for LKG values, rollback, and safety limits."""

import json
import logging
import os
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING, Callable, Awaitable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from ..platform.detect import PlatformInfo
from ..tuning.iron_seeker import IronSeekerState, IronSeekerStoredResult

if TYPE_CHECKING:
    from .ryzenadj import RyzenadjWrapper
    from .crash_metrics import CrashMetricsManager

logger = logging.getLogger(__name__)


class RecoveryStage(Enum):
    """Stages of progressive recovery."""
    INITIAL = "initial"      # No recovery in progress
    REDUCED = "reduced"      # Values reduced, waiting for stability
    ROLLBACK = "rollback"    # Full rollback performed


@dataclass
class RecoveryState:
    """State of progressive recovery attempt.
    
    Feature: decktune-3.0-automation, Property 5: Progressive recovery first step
    Validates: Requirements 2.1
    """
    stage: RecoveryStage = RecoveryStage.INITIAL
    original_values: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    reduced_values: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    reduction_amount: int = 5  # mV reduced (default 5)
    heartbeats_since_reduction: int = 0


class ProgressiveRecovery:
    """Smart rollback with gradual value reduction.
    
    Instead of immediately rolling back to LKG values on instability detection,
    this class first attempts to reduce undervolt values by a small amount (5mV).
    If stability is confirmed after the reduction, the reduced values become
    the new LKG. If instability persists, a full rollback to LKG is performed.
    
    Feature: decktune-3.0-automation
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    REDUCTION_STEP = 5           # mV to reduce on first attempt
    STABILITY_HEARTBEATS = 2     # Heartbeats to wait after reduction
    
    def __init__(
        self,
        get_current_values: Callable[[], List[int]],
        apply_values: Callable[[List[int]], Tuple[bool, Optional[str]]],
        get_lkg: Callable[[], List[int]],
        save_lkg: Callable[[List[int]], None],
        emit_event: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None
    ):
        """Initialize progressive recovery.
        
        Args:
            get_current_values: Function to get current undervolt values
            apply_values: Function to apply new undervolt values
            get_lkg: Function to get LKG values
            save_lkg: Function to save new LKG values
            emit_event: Optional async function to emit events
        """
        self._get_current_values = get_current_values
        self._apply_values = apply_values
        self._get_lkg = get_lkg
        self._save_lkg = save_lkg
        self._emit_event = emit_event
        self._state = RecoveryState()
    
    @property
    def state(self) -> RecoveryState:
        """Get current recovery state."""
        return self._state
    
    @property
    def is_recovering(self) -> bool:
        """Check if recovery is in progress."""
        return self._state.stage == RecoveryStage.REDUCED
    
    def _reduce_values(self, values: List[int], reduction: int) -> List[int]:
        """Reduce undervolt values by the specified amount.
        
        Reduces each value by `reduction` mV, clamped to not exceed 0mV.
        Since undervolt values are negative, reducing means making them
        less negative (closer to 0).
        
        Args:
            values: Current undervolt values (negative integers)
            reduction: Amount to reduce by (positive integer)
            
        Returns:
            Reduced values, clamped to not exceed 0
            
        Feature: decktune-3.0-automation, Property 5: Progressive recovery first step
        Validates: Requirements 2.1
        """
        return [min(v + reduction, 0) for v in values]
    
    def on_instability_detected(self) -> Tuple[bool, Optional[str], RecoveryState]:
        """Handle instability detection.
        
        First attempt: reduce all values by REDUCTION_STEP (5mV).
        If already in reduced state and instability persists: full rollback to LKG.
        
        Returns:
            Tuple of (success, error_message, new_state)
            
        Feature: decktune-3.0-automation, Property 5: Progressive recovery first step
        Validates: Requirements 2.1
        """
        if self._state.stage == RecoveryStage.INITIAL:
            # First instability detection - try reduction
            original_values = self._get_current_values()
            reduced_values = self._reduce_values(original_values, self.REDUCTION_STEP)
            
            logger.info(
                f"Progressive recovery: reducing values from {original_values} "
                f"to {reduced_values} (reduction: {self.REDUCTION_STEP}mV)"
            )
            
            success, error = self._apply_values(reduced_values)
            
            if success:
                self._state = RecoveryState(
                    stage=RecoveryStage.REDUCED,
                    original_values=original_values,
                    reduced_values=reduced_values,
                    reduction_amount=self.REDUCTION_STEP,
                    heartbeats_since_reduction=0
                )
                logger.info("Progressive recovery: values reduced, waiting for stability")
                return True, None, self._state
            else:
                # Reduction failed, fall through to full rollback
                logger.warning(f"Progressive recovery: reduction failed ({error}), performing full rollback")
        
        # Either already in reduced state with continued instability,
        # or reduction failed - perform full rollback
        return self._perform_full_rollback()
    
    def _perform_full_rollback(self) -> Tuple[bool, Optional[str], RecoveryState]:
        """Perform full rollback to LKG values.
        
        Returns:
            Tuple of (success, error_message, new_state)
            
        Feature: decktune-3.0-automation, Property 7: Recovery escalation
        Validates: Requirements 2.3
        """
        lkg_values = self._get_lkg()
        logger.warning(f"Progressive recovery: performing full rollback to LKG {lkg_values}")
        
        success, error = self._apply_values(lkg_values)
        
        self._state = RecoveryState(
            stage=RecoveryStage.ROLLBACK,
            original_values=self._state.original_values if self._state.stage != RecoveryStage.INITIAL else lkg_values,
            reduced_values=lkg_values,
            reduction_amount=0,
            heartbeats_since_reduction=0
        )
        
        if success:
            logger.info("Progressive recovery: full rollback successful")
        else:
            logger.error(f"Progressive recovery: full rollback failed - {error}")
        
        return success, error, self._state
    
    def on_heartbeat(self) -> Tuple[bool, Optional[str]]:
        """Track heartbeats during recovery.
        
        Called on each successful heartbeat. If in reduced state, increments
        the heartbeat counter. When STABILITY_HEARTBEATS is reached, confirms
        stability and updates LKG.
        
        Returns:
            Tuple of (stability_confirmed, error_message)
            - stability_confirmed: True if stability was just confirmed
            - error_message: Error if LKG update failed
            
        Feature: decktune-3.0-automation, Property 6: Recovery stability wait
        Validates: Requirements 2.2
        """
        if self._state.stage != RecoveryStage.REDUCED:
            return False, None
        
        self._state.heartbeats_since_reduction += 1
        logger.debug(
            f"Progressive recovery: heartbeat {self._state.heartbeats_since_reduction}/"
            f"{self.STABILITY_HEARTBEATS}"
        )
        
        if self._state.heartbeats_since_reduction >= self.STABILITY_HEARTBEATS:
            return self.confirm_stability()
        
        return False, None
    
    def confirm_stability(self) -> Tuple[bool, Optional[str]]:
        """Called when stability confirmed after reduction.
        
        Updates LKG to the reduced values and resets recovery state.
        
        Returns:
            Tuple of (success, error_message)
            
        Feature: decktune-3.0-automation, Property 8: Recovery success updates LKG
        Validates: Requirements 2.4
        """
        if self._state.stage != RecoveryStage.REDUCED:
            return False, "Not in reduced state"
        
        reduced_values = self._state.reduced_values
        logger.info(f"Progressive recovery: stability confirmed, updating LKG to {reduced_values}")
        
        try:
            self._save_lkg(reduced_values)
            logger.info("Progressive recovery: LKG updated successfully")
            
            # Reset state
            self._state = RecoveryState()
            
            return True, None
        except Exception as e:
            error_msg = f"Failed to update LKG: {e}"
            logger.error(f"Progressive recovery: {error_msg}")
            return False, error_msg
    
    def reset(self) -> None:
        """Reset recovery state to initial."""
        self._state = RecoveryState()
        logger.debug("Progressive recovery: state reset")


@dataclass
class BinningState:
    """Persistent state for binning crash recovery."""
    active: bool  # Is binning currently running?
    current_value: int  # Value being tested
    last_stable: int  # Last value that passed
    iteration: int  # Current iteration number
    failed_values: List[int]  # Values that failed
    timestamp: str  # ISO timestamp


@dataclass
class DeckTuneSettings:
    """Settings schema for DeckTune."""
    # Global settings
    is_global: bool = False
    run_at_startup: bool = False
    is_run_automatically: bool = True
    timeout_apply: int = 15
    
    # Current values
    cores: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    status: str = "disabled"
    
    # LKG (Last Known Good)
    lkg_cores: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    lkg_timestamp: Optional[str] = None
    
    # Presets
    presets: List[dict] = field(default_factory=list)
    
    # Dynamic mode settings
    dynamic_settings: dict = field(default_factory=lambda: {
        "strategy": "DEFAULT",
        "sample_interval": 50000,
        "cores": []
    })
    
    # Test history
    test_history: List[dict] = field(default_factory=list)


class SafetyManager:
    """Manages LKG values, rollback, and safety limits."""
    
    TUNING_FLAG_FILE = "/tmp/decktune_tuning_flag"
    BINNING_STATE_FILE = "/tmp/decktune_binning_state.json"
    IRON_SEEKER_STATE_FILE = "/tmp/decktune_iron_seeker_state.json"
    
    def __init__(self, settings_manager, platform: PlatformInfo, 
                 ryzenadj: Optional["RyzenadjWrapper"] = None,
                 crash_metrics_manager: Optional["CrashMetricsManager"] = None):
        """Initialize the safety manager.
        
        Args:
            settings_manager: Decky settings manager instance
            platform: Detected platform information
            ryzenadj: Optional RyzenadjWrapper for applying values during rollback
            crash_metrics_manager: Optional CrashMetricsManager for recording crash events
        """
        self.settings_manager = settings_manager
        self.platform = platform
        self.ryzenadj = ryzenadj
        self.crash_metrics_manager = crash_metrics_manager
        self._lkg_values: List[int] = [0, 0, 0, 0]
        self._load_lkg_from_settings()
    
    def set_crash_metrics_manager(self, crash_metrics_manager: "CrashMetricsManager") -> None:
        """Set the CrashMetricsManager instance.
        
        Args:
            crash_metrics_manager: CrashMetricsManager instance
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 1.1
        """
        self.crash_metrics_manager = crash_metrics_manager
    
    def _load_lkg_from_settings(self) -> None:
        """Load LKG values from settings on init."""
        lkg = self.settings_manager.get_setting("lkg_cores")
        if lkg and isinstance(lkg, list) and len(lkg) == 4:
            self._lkg_values = lkg
    
    def clamp_values(self, values: List[int]) -> List[int]:
        """Clamp values to platform safe limits.
        
        Args:
            values: List of undervolt values
            
        Returns:
            List of clamped values within safe limits
        """
        safe_limit = self.platform.safe_limit
        clamped = []
        for v in values:
            # Ensure value is not below safe limit (more negative)
            if v < safe_limit:
                clamped.append(safe_limit)
            # Ensure value is not above 0
            elif v > 0:
                clamped.append(0)
            else:
                clamped.append(v)
        return clamped
    
    def save_lkg(self, values: List[int]) -> None:
        """Persist LKG values to settings.
        
        Args:
            values: List of stable undervolt values
        """
        self._lkg_values = values.copy()
        self.settings_manager.save_setting("lkg_cores", values)
        self.settings_manager.save_setting("lkg_timestamp", datetime.now().isoformat())
    
    def load_lkg(self) -> List[int]:
        """Load LKG values from settings.
        
        Returns:
            List of last known good undervolt values
        """
        lkg = self.settings_manager.get_setting("lkg_cores")
        if lkg and isinstance(lkg, list) and len(lkg) == 4:
            self._lkg_values = lkg
            return lkg
        return [0, 0, 0, 0]
    
    def get_lkg(self) -> List[int]:
        """Get current LKG values.
        
        Returns:
            List of last known good undervolt values
        """
        return self._lkg_values.copy()
    
    def set_ryzenadj(self, ryzenadj: "RyzenadjWrapper") -> None:
        """Set the RyzenadjWrapper instance for rollback operations.
        
        Args:
            ryzenadj: RyzenadjWrapper instance
        """
        self.ryzenadj = ryzenadj
    
    def rollback_to_lkg(self) -> Tuple[bool, Optional[str]]:
        """Apply LKG values immediately for emergency recovery.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        lkg_values = self.load_lkg()
        
        if self.ryzenadj is None:
            logger.warning("Cannot rollback: RyzenadjWrapper not configured")
            return False, "RyzenadjWrapper not configured"
        
        # Apply the LKG values
        success, error = self.ryzenadj.apply_values(lkg_values)
        
        if success:
            logger.info(f"Successfully rolled back to LKG values: {lkg_values}")
        else:
            logger.error(f"Failed to rollback to LKG values: {error}")
        
        return success, error
    
    def create_tuning_flag(self) -> None:
        """Create flag file indicating tuning in progress."""
        try:
            with open(self.TUNING_FLAG_FILE, 'w') as f:
                f.write(datetime.now().isoformat())
        except IOError:
            pass  # Best effort
    
    def remove_tuning_flag(self) -> None:
        """Remove tuning flag after successful completion."""
        try:
            if os.path.exists(self.TUNING_FLAG_FILE):
                os.remove(self.TUNING_FLAG_FILE)
        except IOError:
            pass  # Best effort
    
    def has_tuning_flag(self) -> bool:
        """Check if tuning flag exists.
        
        Returns:
            True if tuning was in progress when system stopped
        """
        return os.path.exists(self.TUNING_FLAG_FILE)
    
    def check_boot_recovery(self) -> bool:
        """Check if recovery needed on boot, perform if needed.
        
        If a tuning flag exists (indicating tuning was in progress when
        system stopped), this method will:
        1. Remove the tuning flag
        2. Rollback to LKG values if ryzenadj is configured
        3. Record crash event to crash metrics
        
        If a binning state file exists with active=True (indicating binning
        was in progress when system stopped), this method will:
        1. Restore the last_stable value
        2. Log the failed test value
        3. Clear the binning state
        4. Record crash event to crash metrics
        
        If an Iron Seeker state file exists with active=True (indicating
        Iron Seeker was in progress when system stopped), this method will:
        1. Restore the stable values (core_results)
        2. Log the crashed core and value
        3. Clear the Iron Seeker state
        4. Record crash event to crash metrics
        
        Returns:
            True if recovery was performed
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 1.1, 1.3
        """
        recovery_performed = False
        
        # Check for Iron Seeker crash recovery first (Requirements: 3.2)
        iron_seeker_state = self.load_iron_seeker_state()
        if iron_seeker_state is not None and iron_seeker_state.active:
            logger.warning(
                f"Iron Seeker crash detected - crashed at core {iron_seeker_state.current_core}, "
                f"value {iron_seeker_state.current_value}mV, "
                f"restoring stable values: {iron_seeker_state.core_results}"
            )
            
            # Build crashed values (current test values)
            crashed_values = iron_seeker_state.core_results.copy()
            crashed_values[iron_seeker_state.current_core] = iron_seeker_state.current_value
            
            # Store recovery info for event emission
            self._last_iron_seeker_recovery = {
                "crashed_core": iron_seeker_state.current_core,
                "crashed_value": iron_seeker_state.current_value,
                "restored_values": iron_seeker_state.core_results.copy()
            }
            
            # Restore stable values if ryzenadj is configured (Requirements: 3.2)
            if self.ryzenadj is not None:
                stable_values = iron_seeker_state.core_results
                success, error = self.ryzenadj.apply_values(stable_values)
                if success:
                    logger.info(f"Iron Seeker recovery: restored stable values {stable_values}")
                else:
                    logger.error(f"Iron Seeker recovery: failed to restore stable values - {error}")
            else:
                logger.warning("Iron Seeker recovery: RyzenadjWrapper not configured, skipping value restore")
            
            # Record crash to metrics (Feature: decktune-3.1-reliability-ux)
            if self.crash_metrics_manager is not None:
                self.crash_metrics_manager.record_crash(
                    crashed_values=crashed_values,
                    restored_values=iron_seeker_state.core_results.copy(),
                    reason="iron_seeker_crash"
                )
            
            # Clear the Iron Seeker state
            self.clear_iron_seeker_state()
            recovery_performed = True
        
        # Check for binning crash recovery
        binning_state = self.load_binning_state()
        if binning_state is not None and binning_state.active:
            logger.warning(
                f"Binning crash detected - failed value: {binning_state.current_value}, "
                f"restoring last_stable: {binning_state.last_stable}"
            )
            
            crashed_values = [binning_state.current_value] * 4
            restored_values = [binning_state.last_stable] * 4
            
            # Restore last_stable value if ryzenadj is configured
            if self.ryzenadj is not None:
                last_stable_values = [binning_state.last_stable] * 4
                success, error = self.ryzenadj.apply_values(last_stable_values)
                if success:
                    logger.info(f"Binning recovery: restored last_stable value {binning_state.last_stable}")
                else:
                    logger.error(f"Binning recovery: failed to restore last_stable - {error}")
            else:
                logger.warning("Binning recovery: RyzenadjWrapper not configured, skipping value restore")
            
            # Record crash to metrics (Feature: decktune-3.1-reliability-ux)
            if self.crash_metrics_manager is not None:
                self.crash_metrics_manager.record_crash(
                    crashed_values=crashed_values,
                    restored_values=restored_values,
                    reason="binning_crash"
                )
            
            # Clear the binning state
            self.clear_binning_state()
            recovery_performed = True
        
        # Check for regular tuning flag
        if self.has_tuning_flag():
            logger.warning("Tuning flag detected on boot - performing recovery")
            # Tuning was in progress - need to rollback
            self.remove_tuning_flag()
            
            # Get current values (crashed) and LKG values (to restore)
            current_values = self.settings_manager.get_setting("cores") or [0, 0, 0, 0]
            lkg_values = self.load_lkg()
            
            # Attempt to rollback to LKG values
            if self.ryzenadj is not None:
                success, error = self.rollback_to_lkg()
                if not success:
                    logger.error(f"Boot recovery rollback failed: {error}")
            else:
                logger.warning("Boot recovery: RyzenadjWrapper not configured, skipping rollback")
            
            # Record crash to metrics (Feature: decktune-3.1-reliability-ux)
            if self.crash_metrics_manager is not None:
                self.crash_metrics_manager.record_crash(
                    crashed_values=current_values,
                    restored_values=lkg_values,
                    reason="boot_recovery"
                )
            
            recovery_performed = True
        
        return recovery_performed
    
    def get_iron_seeker_recovery_info(self) -> Optional[Dict[str, Any]]:
        """Get Iron Seeker recovery info from the last boot recovery check.
        
        This method returns the recovery information captured during
        check_boot_recovery() if Iron Seeker crash recovery was performed.
        The info can be used to emit a recovery event to the frontend.
        
        Returns:
            Dictionary with crashed_core, crashed_value, restored_values
            if Iron Seeker recovery was performed, None otherwise
            
        Requirements: 3.4
        """
        return getattr(self, '_last_iron_seeker_recovery', None)
    
    def create_binning_state(
        self,
        current_value: int,
        last_stable: int,
        iteration: int,
        failed_values: Optional[List[int]] = None
    ) -> None:
        """Create binning state file for crash recovery.
        
        Args:
            current_value: Value currently being tested
            last_stable: Last value that passed testing
            iteration: Current iteration number
            failed_values: List of values that failed (optional)
        """
        state = BinningState(
            active=True,
            current_value=current_value,
            last_stable=last_stable,
            iteration=iteration,
            failed_values=failed_values or [],
            timestamp=datetime.now().isoformat()
        )
        
        try:
            with open(self.BINNING_STATE_FILE, 'w') as f:
                json.dump(asdict(state), f, indent=2)
            logger.debug(f"Created binning state: iteration={iteration}, current={current_value}, last_stable={last_stable}")
        except IOError as e:
            logger.warning(f"Failed to create binning state file: {e}")
    
    def update_binning_state(
        self,
        current_value: int,
        last_stable: int,
        iteration: int,
        failed_values: Optional[List[int]] = None
    ) -> None:
        """Update existing binning state file.
        
        Args:
            current_value: Value currently being tested
            last_stable: Last value that passed testing
            iteration: Current iteration number
            failed_values: List of values that failed (optional)
        """
        # Same implementation as create - overwrites the file
        self.create_binning_state(current_value, last_stable, iteration, failed_values)
    
    def clear_binning_state(self) -> None:
        """Remove binning state file after completion or cancellation."""
        try:
            if os.path.exists(self.BINNING_STATE_FILE):
                os.remove(self.BINNING_STATE_FILE)
                logger.debug("Cleared binning state file")
        except IOError as e:
            logger.warning(f"Failed to clear binning state file: {e}")
    
    def load_binning_state(self) -> Optional[BinningState]:
        """Load binning state from disk.
        
        Returns:
            BinningState if file exists and is valid, None otherwise
        """
        if not os.path.exists(self.BINNING_STATE_FILE):
            return None
        
        try:
            with open(self.BINNING_STATE_FILE, 'r') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ['active', 'current_value', 'last_stable', 'iteration', 'failed_values', 'timestamp']
            if not all(field in data for field in required_fields):
                logger.warning("Binning state file missing required fields")
                return None
            
            state = BinningState(
                active=data['active'],
                current_value=data['current_value'],
                last_stable=data['last_stable'],
                iteration=data['iteration'],
                failed_values=data['failed_values'],
                timestamp=data['timestamp']
            )
            
            logger.debug(f"Loaded binning state: iteration={state.iteration}, current={state.current_value}, last_stable={state.last_stable}")
            return state
            
        except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to load binning state file: {e}")
            return None

    # Iron Seeker state management methods
    # Requirements: 3.1, 3.2, 3.5
    
    def create_iron_seeker_state(self, state: IronSeekerState) -> None:
        """Create Iron Seeker state file for crash recovery.
        
        Persists the current Iron Seeker state to disk before applying
        a new test value. This enables recovery if the system crashes
        during testing.
        
        Args:
            state: IronSeekerState to persist
            
        Requirements: 3.1
        """
        try:
            with open(self.IRON_SEEKER_STATE_FILE, 'w') as f:
                json.dump(state.to_json(), f, indent=2)
            logger.debug(
                f"Created Iron Seeker state: core={state.current_core}, "
                f"value={state.current_value}"
            )
        except IOError as e:
            logger.warning(f"Failed to create Iron Seeker state file: {e}")
    
    def load_iron_seeker_state(self) -> Optional[IronSeekerState]:
        """Load Iron Seeker state from disk.
        
        Returns:
            IronSeekerState if file exists and is valid, None otherwise
            
        Requirements: 3.2
        """
        if not os.path.exists(self.IRON_SEEKER_STATE_FILE):
            return None
        
        try:
            with open(self.IRON_SEEKER_STATE_FILE, 'r') as f:
                data = json.load(f)
            
            state = IronSeekerState.from_json(data)
            logger.debug(
                f"Loaded Iron Seeker state: core={state.current_core}, "
                f"value={state.current_value}, active={state.active}"
            )
            return state
            
        except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to load Iron Seeker state file: {e}")
            # Delete corrupted state file
            self.clear_iron_seeker_state()
            return None
    
    def clear_iron_seeker_state(self) -> None:
        """Remove Iron Seeker state file after completion or cancellation.
        
        Requirements: 3.5
        """
        try:
            if os.path.exists(self.IRON_SEEKER_STATE_FILE):
                os.remove(self.IRON_SEEKER_STATE_FILE)
                logger.debug("Cleared Iron Seeker state file")
        except IOError as e:
            logger.warning(f"Failed to clear Iron Seeker state file: {e}")

    # Iron Seeker results persistence methods
    # Requirements: 4.4, 6.3
    
    def save_iron_seeker_results(self, stored_result: IronSeekerStoredResult) -> bool:
        """Save Iron Seeker results to settings.
        
        Persists the per-core values, quality tiers, and timestamp to settings
        for later retrieval and preset creation.
        
        Args:
            stored_result: IronSeekerStoredResult to persist
            
        Returns:
            True if saved successfully, False otherwise
            
        Requirements: 4.4, 6.3
        """
        try:
            # Validate before saving
            if not stored_result.validate():
                logger.error("Invalid Iron Seeker result structure, not saving")
                return False
            
            self.settings_manager.save_setting(
                "iron_seeker_results",
                stored_result.to_dict()
            )
            logger.info(f"Saved Iron Seeker results: {len(stored_result.cores)} cores")
            return True
        except Exception as e:
            logger.error(f"Failed to save Iron Seeker results: {e}")
            return False
    
    def load_iron_seeker_results(self) -> Optional[IronSeekerStoredResult]:
        """Load Iron Seeker results from settings.
        
        Returns:
            IronSeekerStoredResult if found and valid, None otherwise
            
        Requirements: 4.4
        """
        try:
            data = self.settings_manager.get_setting("iron_seeker_results")
            if data is None:
                return None
            
            stored_result = IronSeekerStoredResult.from_dict(data)
            
            # Validate loaded data
            if not stored_result.validate():
                logger.warning("Loaded Iron Seeker results failed validation")
                return None
            
            return stored_result
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to load Iron Seeker results: {e}")
            return None
    
    def clear_iron_seeker_results(self) -> None:
        """Clear saved Iron Seeker results from settings."""
        try:
            self.settings_manager.save_setting("iron_seeker_results", None)
            logger.debug("Cleared Iron Seeker results from settings")
        except Exception as e:
            logger.warning(f"Failed to clear Iron Seeker results: {e}")
