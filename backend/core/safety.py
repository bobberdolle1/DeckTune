"""Safety manager for LKG values, rollback, and safety limits."""

import json
import logging
import os
from typing import List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from ..platform.detect import PlatformInfo

if TYPE_CHECKING:
    from .ryzenadj import RyzenadjWrapper

logger = logging.getLogger(__name__)


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
        
        Returns:
            True if recovery was performed
        """
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
            
            return True
        return False
