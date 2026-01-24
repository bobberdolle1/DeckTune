"""Dynamic Manual Mode Manager.

This module provides the DynamicManager class for managing per-core dynamic
voltage control in Manual Dynamic Mode. It handles configuration management,
voltage curve calculation, and interaction with gymdeck3.

Feature: manual-dynamic-mode
Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CoreConfig:
    """Configuration for a single CPU core.
    
    Attributes:
        core_id: Core identifier (0-3)
        min_mv: Minimum (less aggressive) undervolt value in mV (-100 to 0)
        max_mv: Maximum (more aggressive) undervolt value in mV (-100 to 0)
        threshold: Load threshold percentage for voltage transition (0-100)
    """
    core_id: int
    min_mv: int = -30
    max_mv: int = -15
    threshold: float = 50.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "core_id": self.core_id,
            "min_mv": self.min_mv,
            "max_mv": self.max_mv,
            "threshold": self.threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreConfig":
        """Create CoreConfig from dictionary."""
        return cls(
            core_id=data.get("core_id", 0),
            min_mv=data.get("min_mv", -30),
            max_mv=data.get("max_mv", -15),
            threshold=data.get("threshold", 50.0)
        )


@dataclass
class DynamicManualConfig:
    """Configuration for Manual Dynamic Mode.
    
    Attributes:
        mode: 'simple' or 'expert'
        cores: Per-core configuration list (4 cores)
        version: Configuration version for migration
    """
    mode: str = "expert"
    cores: List[CoreConfig] = field(default_factory=lambda: [
        CoreConfig(core_id=0),
        CoreConfig(core_id=1),
        CoreConfig(core_id=2),
        CoreConfig(core_id=3)
    ])
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "mode": self.mode,
            "cores": [core.to_dict() for core in self.cores],
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicManualConfig":
        """Create DynamicManualConfig from dictionary."""
        cores_data = data.get("cores", [])
        cores = [CoreConfig.from_dict(c) for c in cores_data]
        
        # Ensure we have exactly 4 cores
        while len(cores) < 4:
            cores.append(CoreConfig(core_id=len(cores)))
        cores = cores[:4]
        
        return cls(
            mode=data.get("mode", "expert"),
            cores=cores,
            version=data.get("version", 1)
        )


@dataclass
class CurvePoint:
    """A point on the voltage curve.
    
    Attributes:
        load: CPU load percentage (0-100)
        voltage: Voltage offset in mV (-100 to 0)
    """
    load: float
    voltage: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "load": self.load,
            "voltage": self.voltage
        }


@dataclass
class CoreMetrics:
    """Real-time metrics for a CPU core.
    
    Attributes:
        core_id: Core identifier
        load: CPU load percentage (0-100)
        voltage: Current voltage offset in mV
        frequency: CPU frequency in MHz
        temperature: Temperature in Celsius
        timestamp: Unix timestamp
    """
    core_id: int
    load: float
    voltage: int
    frequency: int
    temperature: float
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "core_id": self.core_id,
            "load": self.load,
            "voltage": self.voltage,
            "frequency": self.frequency,
            "temperature": self.temperature,
            "timestamp": self.timestamp
        }


class DynamicManager:
    """Manager for Manual Dynamic Mode operations.
    
    Handles configuration management, voltage curve calculation,
    and interaction with gymdeck3 for per-core dynamic voltage control.
    
    Feature: manual-dynamic-mode
    Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    def __init__(self, gymdeck3_interface=None):
        """Initialize the DynamicManager.
        
        Args:
            gymdeck3_interface: Optional gymdeck3 interface for hardware control
        """
        self.gymdeck3 = gymdeck3_interface
        self.config = DynamicManualConfig()
        self.is_active = False
        
        logger.info("DynamicManager initialized")
    
    def get_config(self) -> DynamicManualConfig:
        """Get current configuration.
        
        Returns:
            Current DynamicManualConfig
            
        Validates: Requirements 9.1
        """
        return self.config
    
    def set_core_config(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> bool:
        """Update configuration for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            min_mv: Minimum undervolt value in mV (-100 to 0)
            max_mv: Maximum undervolt value in mV (-100 to 0)
            threshold: Load threshold percentage (0-100)
            
        Returns:
            True if configuration was updated successfully
            
        Validates: Requirements 9.2
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return False
        
        self.config.cores[core_id].min_mv = min_mv
        self.config.cores[core_id].max_mv = max_mv
        self.config.cores[core_id].threshold = threshold
        
        logger.info(f"Updated core {core_id} config: min={min_mv}, max={max_mv}, threshold={threshold}")
        return True
    
    def set_all_cores_config(
        self,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> bool:
        """Update configuration for all cores (Simple Mode).
        
        Propagates the same voltage settings to all cores simultaneously.
        This is used in Simple Mode to apply unified settings.
        
        Args:
            min_mv: Minimum undervolt value in mV (-100 to 0)
            max_mv: Maximum undervolt value in mV (-100 to 0)
            threshold: Load threshold percentage (0-100)
            
        Returns:
            True if configuration was updated successfully
            
        Validates: Requirements 4.2, 4.3
        """
        for core in self.config.cores:
            core.min_mv = min_mv
            core.max_mv = max_mv
            core.threshold = threshold
        
        logger.info(f"Updated all cores config: min={min_mv}, max={max_mv}, threshold={threshold}")
        return True
    
    def get_curve_data(self, core_id: int) -> List[CurvePoint]:
        """Calculate voltage curve points for visualization.
        
        Generates 101 curve points (load 0-100) based on the core's
        configuration using piecewise linear interpolation.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            List of CurvePoint objects representing the voltage curve
            
        Validates: Requirements 9.3, 2.4, 2.5
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return []
        
        core_config = self.config.cores[core_id]
        curve_points = []
        
        # Generate 101 points (load 0 to 100)
        for load in range(101):
            voltage = self._calculate_voltage(
                load,
                core_config.min_mv,
                core_config.max_mv,
                core_config.threshold
            )
            curve_points.append(CurvePoint(load=float(load), voltage=voltage))
        
        return curve_points
    
    def _calculate_voltage(
        self,
        load: float,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> int:
        """Calculate voltage offset for a given load.
        
        Uses piecewise linear interpolation:
        - Below threshold: returns min_mv
        - Above threshold: linear interpolation from min_mv to max_mv
        
        Args:
            load: CPU load percentage (0-100)
            min_mv: Minimum undervolt value
            max_mv: Maximum undervolt value
            threshold: Load threshold percentage
            
        Returns:
            Voltage offset in mV
            
        Validates: Requirements 2.4, 2.5
        """
        if load <= threshold:
            # Below threshold: use minimum value
            return min_mv
        else:
            # Above threshold: linear interpolation
            if threshold >= 100:
                return max_mv
            
            progress = (load - threshold) / (100 - threshold)
            voltage = min_mv + (max_mv - min_mv) * progress
            return int(round(voltage))
    
    def start(self) -> bool:
        """Start dynamic voltage adjustment.
        
        Activates dynamic mode with the current configuration.
        
        Returns:
            True if started successfully
            
        Validates: Requirements 5.1, 9.5
        """
        if self.is_active:
            logger.warning("Dynamic mode already active")
            return False
        
        # TODO: Integrate with gymdeck3 when available
        if self.gymdeck3:
            # Apply configuration to gymdeck3
            pass
        
        self.is_active = True
        logger.info("Dynamic Manual Mode started")
        return True
    
    def stop(self) -> bool:
        """Stop dynamic voltage adjustment.
        
        Deactivates dynamic mode and resets voltages.
        
        Returns:
            True if stopped successfully
            
        Validates: Requirements 5.3
        """
        if not self.is_active:
            logger.warning("Dynamic mode not active")
            return False
        
        # TODO: Integrate with gymdeck3 when available
        if self.gymdeck3:
            # Stop gymdeck3
            pass
        
        self.is_active = False
        logger.info("Dynamic Manual Mode stopped")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of dynamic mode.
        
        Returns a dictionary containing the current operational status
        of the dynamic mode system, including whether it's active.
        
        Returns:
            Dictionary with status information:
                - active: bool indicating if dynamic mode is running
                - config: current configuration summary
                
        Validates: Requirements 5.2, 5.4
        """
        return {
            "active": self.is_active,
            "config": {
                "mode": self.config.mode,
                "version": self.config.version
            }
        }
    
    def get_core_metrics(self, core_id: int) -> Optional[CoreMetrics]:
        """Get current metrics for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            CoreMetrics object or None if unavailable
            
        Validates: Requirements 9.4
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return None
        
        # TODO: Integrate with gymdeck3 when available
        # For now, return stub data
        import time
        return CoreMetrics(
            core_id=core_id,
            load=0.0,
            voltage=0,
            frequency=0,
            temperature=0.0,
            timestamp=time.time()
        )
    
    def save_config(self, settings_manager) -> bool:
        """Save configuration to backend settings.
        
        Persists the current dynamic mode configuration to the backend
        settings storage. The configuration includes mode, per-core settings,
        and version information for migration support.
        
        Args:
            settings_manager: Settings manager instance
            
        Returns:
            True if saved successfully, False otherwise
            
        Validates: Requirements 6.2
        """
        try:
            config_dict = self.config.to_dict()
            # Add timestamp for tracking
            import time
            config_dict["last_updated"] = int(time.time())
            
            success = settings_manager.save_setting("dynamic_manual_mode", config_dict)
            if success:
                logger.info("Dynamic Manual Mode config saved")
            else:
                logger.error("Failed to save config via settings manager")
            return success
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def load_config(self, settings_manager) -> bool:
        """Load configuration from backend settings.
        
        Loads the dynamic mode configuration from backend settings storage.
        Performs migration if the stored version is older than the current version.
        Falls back to safe defaults if no configuration is found or on error.
        
        Args:
            settings_manager: Settings manager instance
            
        Returns:
            True if loaded successfully, False if using defaults
            
        Validates: Requirements 6.2, 6.4, 6.5
        """
        try:
            config_data = settings_manager.get_setting("dynamic_manual_mode")
            if config_data:
                # Perform migration if needed
                migrated_data = self._migrate_config(config_data)
                self.config = DynamicManualConfig.from_dict(migrated_data)
                logger.info("Dynamic Manual Mode config loaded")
                return True
            else:
                logger.info("No saved config found, using safe defaults")
                self.config = self._get_safe_defaults()
                return False
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using safe defaults")
            self.config = self._get_safe_defaults()
            return False
    
    def _migrate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to current version.
        
        Handles version updates and ensures backward compatibility.
        Currently supports version 1 (initial version).
        
        Args:
            config_data: Configuration dictionary to migrate
            
        Returns:
            Migrated configuration dictionary
            
        Validates: Requirements 6.5
        """
        current_version = 1
        stored_version = config_data.get("version", 1)
        
        if stored_version == current_version:
            # No migration needed
            return config_data
        
        # Future migrations would go here
        # Example:
        # if stored_version < 2:
        #     config_data = self._migrate_v1_to_v2(config_data)
        
        logger.info(f"Migrated config from version {stored_version} to {current_version}")
        config_data["version"] = current_version
        return config_data
    
    def _get_safe_defaults(self) -> DynamicManualConfig:
        """Get safe default configuration.
        
        Returns a configuration with conservative voltage settings
        that are safe for all supported hardware.
        
        Default values:
        - Mode: expert
        - MinimalValue: -30mV (conservative undervolt)
        - MaximumValue: -15mV (mild undervolt)
        - Threshold: 50% (balanced transition point)
        
        Returns:
            DynamicManualConfig with safe default values
            
        Validates: Requirements 6.5, 7.5
        """
        return DynamicManualConfig(
            mode="expert",
            cores=[
                CoreConfig(core_id=0, min_mv=-30, max_mv=-15, threshold=50.0),
                CoreConfig(core_id=1, min_mv=-30, max_mv=-15, threshold=50.0),
                CoreConfig(core_id=2, min_mv=-30, max_mv=-15, threshold=50.0),
                CoreConfig(core_id=3, min_mv=-30, max_mv=-15, threshold=50.0)
            ],
            version=1
        )
