"""Safety manager for LKG values, rollback, and safety limits."""

import json
import logging
import os
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field, asdict
from datetime import datetime

from ..platform.detect import PlatformInfo
from ..tuning.iron_seeker import IronSeekerState, IronSeekerStoredResult

if TYPE_CHECKING:
    from .ryzenadj import RyzenadjWrapper

logger = logging.getLogger(__name__)


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
                 ryzenadj: Optional["RyzenadjWrapper"] = None):
        """Initialize the safety manager.
        
        Args:
            settings_manager: Decky settings manager instance
            platform: Detected platform information
            ryzenadj: Optional RyzenadjWrapper for applying values during rollback
        """
        self.settings_manager = settings_manager
        self.platform = platform
        self.ryzenadj = ryzenadj
        self._lkg_values: List[int] = [0, 0, 0, 0]
        self._load_lkg_from_settings()
    
    def _load_lkg_from_settings(self) -> None:
        """Load LKG values from settings on init."""
        lkg = self.settings_manager.getSetting("lkg_cores")
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
        self.settings_manager.setSetting("lkg_cores", values)
        self.settings_manager.setSetting("lkg_timestamp", datetime.now().isoformat())
    
    def load_lkg(self) -> List[int]:
        """Load LKG values from settings.
        
        Returns:
            List of last known good undervolt values
        """
        lkg = self.settings_manager.getSetting("lkg_cores")
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
        
        If a binning state file exists with active=True (indicating binning
        was in progress when system stopped), this method will:
        1. Restore the last_stable value
        2. Log the failed test value
        3. Clear the binning state
        
        If an Iron Seeker state file exists with active=True (indicating
        Iron Seeker was in progress when system stopped), this method will:
        1. Restore the stable values (core_results)
        2. Log the crashed core and value
        3. Clear the Iron Seeker state
        
        Returns:
            True if recovery was performed
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
            
            # Clear the binning state
            self.clear_binning_state()
            recovery_performed = True
        
        # Check for regular tuning flag
        if self.has_tuning_flag():
            logger.warning("Tuning flag detected on boot - performing recovery")
            # Tuning was in progress - need to rollback
            self.remove_tuning_flag()
            
            # Attempt to rollback to LKG values
            if self.ryzenadj is not None:
                success, error = self.rollback_to_lkg()
                if not success:
                    logger.error(f"Boot recovery rollback failed: {error}")
            else:
                logger.warning("Boot recovery: RyzenadjWrapper not configured, skipping rollback")
            
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
            
            self.settings_manager.setSetting(
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
            data = self.settings_manager.getSetting("iron_seeker_results")
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
            self.settings_manager.setSetting("iron_seeker_results", None)
            logger.debug("Cleared Iron Seeker results from settings")
        except Exception as e:
            logger.warning(f"Failed to clear Iron Seeker results: {e}")
