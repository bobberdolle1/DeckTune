"""RPC handlers for Manual Dynamic Mode.

This module provides RPC methods for frontend communication with the
Manual Dynamic Mode feature, including configuration management, curve
data retrieval, and real-time metrics monitoring.

Feature: manual-dynamic-mode
Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5

Enhanced with:
- Comprehensive error handling
- Hardware error detection
- Connection error reporting
"""

import logging
from typing import Dict, List, Any, Optional

from .manual_manager import DynamicManager, CoreMetrics
from .manual_validator import Validator

logger = logging.getLogger(__name__)


class RPCError(Exception):
    """Base exception for RPC errors.
    
    Attributes:
        message: Human-readable error message
        code: Error code for programmatic handling
        recoverable: Whether the error can be retried
        details: Additional error context
    """
    
    def __init__(
        self,
        message: str,
        code: str = "RPC_ERROR",
        recoverable: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": self.message,
            "code": self.code,
            "recoverable": self.recoverable,
            "details": self.details
        }


class HardwareError(RPCError):
    """Hardware-related error (not recoverable)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="HARDWARE_ERROR",
            recoverable=False,
            details=details
        )


class ValidationError(RPCError):
    """Validation error (not recoverable without config change)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            recoverable=False,
            details=details
        )


class ConnectionError(RPCError):
    """Connection error (recoverable with retry)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            recoverable=True,
            details=details
        )


class DynamicModeRPC:
    """RPC methods for Manual Dynamic Mode.
    
    Provides all RPC endpoints for dynamic mode control:
    - Configuration retrieval and updates
    - Voltage curve data for visualization
    - Start/stop dynamic mode
    - Real-time core metrics
    
    Feature: manual-dynamic-mode
    Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
    
    Enhanced with comprehensive error handling for:
    - Hardware errors (gymdeck3 failures)
    - Validation errors (invalid configurations)
    - Connection errors (transient failures)
    """
    
    def __init__(
        self,
        manager: DynamicManager,
        validator: Validator,
        settings_manager
    ):
        """Initialize the RPC handler.
        
        Args:
            manager: DynamicManager instance
            validator: Validator instance
            settings_manager: Settings manager for persistence
        """
        self.manager = manager
        self.validator = validator
        self.settings = settings_manager
        
        logger.info("DynamicModeRPC initialized")
    
    def _handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle and format errors for RPC responses.
        
        Categorizes errors and returns appropriate error responses:
        - Hardware errors: Not recoverable, require user intervention
        - Validation errors: Not recoverable without config change
        - Connection errors: Recoverable with retry
        - Unknown errors: Treated as recoverable
        
        Args:
            error: Exception that occurred
            operation: Name of the operation that failed
            
        Returns:
            Dictionary with error information
        """
        if isinstance(error, (HardwareError, ValidationError, ConnectionError)):
            logger.error(f"{operation} failed with {error.code}: {error.message}")
            return {
                "success": False,
                "error": error.message,
                "error_code": error.code,
                "recoverable": error.recoverable,
                "details": error.details
            }
        else:
            # Unknown error - log and treat as recoverable
            logger.error(f"{operation} failed with unknown error: {error}", exc_info=True)
            return {
                "success": False,
                "error": str(error),
                "error_code": "UNKNOWN_ERROR",
                "recoverable": True
            }
    
    async def get_dynamic_config(self) -> Dict[str, Any]:
        """Get current dynamic mode configuration for all cores.
        
        Returns:
            Dictionary with success status and configuration data:
            {
                "success": True,
                "config": {
                    "mode": "simple" | "expert",
                    "cores": [
                        {"core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50},
                        ...
                    ],
                    "version": 1
                }
            }
            
        Validates: Requirements 9.1
        """
        try:
            config = self.manager.get_config()
            
            return {
                "success": True,
                "config": config.to_dict()
            }
        except Exception as e:
            return self._handle_error(e, "get_dynamic_config")
    
    async def set_dynamic_core_config(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> Dict[str, Any]:
        """Update configuration for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            min_mv: Minimum undervolt value in mV (-100 to 0)
            max_mv: Maximum undervolt value in mV (-100 to 0)
            threshold: Load threshold percentage (0-100)
            
        Returns:
            Dictionary with success status and any validation errors:
            {
                "success": True/False,
                "error": "error message" (if failed),
                "validation_errors": ["error1", "error2"] (if validation failed)
            }
            
        Validates: Requirements 9.2
        """
        try:
            # Validate configuration
            validation_result = self.validator.validate_config(
                core_id, min_mv, max_mv, threshold
            )
            
            if not validation_result.valid:
                logger.warning(
                    f"Validation failed for core {core_id}: {validation_result.errors}"
                )
                return {
                    "success": False,
                    "error": "Validation failed",
                    "validation_errors": validation_result.errors
                }
            
            # Clamp values to platform limits
            clamped_min = self.validator.clamp_voltage(min_mv)
            clamped_max = self.validator.clamp_voltage(max_mv)
            
            # Update configuration
            success = self.manager.set_core_config(
                core_id, clamped_min, clamped_max, threshold
            )
            
            if success:
                # Save to settings
                self.manager.save_config(self.settings)
                
                return {
                    "success": True,
                    "clamped": {
                        "min_mv": clamped_min,
                        "max_mv": clamped_max
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update core configuration"
                }
                
        except Exception as e:
            return self._handle_error(e, "set_dynamic_core_config")
    
    async def set_all_cores_config(
        self,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> Dict[str, Any]:
        """Update configuration for all cores (Simple Mode).
        
        Applies the same voltage settings to all cores simultaneously.
        Used in Simple Mode to ensure uniform configuration.
        
        Args:
            min_mv: Minimum undervolt value in mV (-100 to 0)
            max_mv: Maximum undervolt value in mV (-100 to 0)
            threshold: Load threshold percentage (0-100)
            
        Returns:
            Dictionary with success status and any validation errors:
            {
                "success": True/False,
                "error": "error message" (if failed),
                "validation_errors": ["error1", "error2"] (if validation failed)
            }
            
        Validates: Requirements 4.2, 4.3
        Property 6: Simple mode value propagation
        Property 7: Simple mode configuration uniformity
        """
        try:
            # Validate configuration (use core 0 for validation)
            validation_result = self.validator.validate_config(
                0, min_mv, max_mv, threshold
            )
            
            if not validation_result.valid:
                logger.warning(
                    f"Validation failed for all cores: {validation_result.errors}"
                )
                return {
                    "success": False,
                    "error": "Validation failed",
                    "validation_errors": validation_result.errors
                }
            
            # Clamp values to platform limits
            clamped_min = self.validator.clamp_voltage(min_mv)
            clamped_max = self.validator.clamp_voltage(max_mv)
            
            # Update configuration for all cores
            success = self.manager.set_all_cores_config(
                clamped_min, clamped_max, threshold
            )
            
            if success:
                # Save to settings
                self.manager.save_config(self.settings)
                
                return {
                    "success": True,
                    "clamped": {
                        "min_mv": clamped_min,
                        "max_mv": clamped_max
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update all cores configuration"
                }
                
        except Exception as e:
            return self._handle_error(e, "set_all_cores_config")
    
    async def get_dynamic_curve_data(self, core_id: int) -> Dict[str, Any]:
        """Get voltage curve data for visualization.
        
        Returns 101 curve points (load 0-100) representing the voltage
        curve for the specified core.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            Dictionary with success status and curve points:
            {
                "success": True,
                "curve_points": [
                    {"load": 0, "voltage": -30},
                    {"load": 1, "voltage": -30},
                    ...
                ]
            }
            
        Validates: Requirements 9.3
        """
        try:
            if not 0 <= core_id < 4:
                return {
                    "success": False,
                    "error": f"Invalid core_id: {core_id}. Must be 0-3."
                }
            
            curve_points = self.manager.get_curve_data(core_id)
            
            return {
                "success": True,
                "curve_points": [point.to_dict() for point in curve_points]
            }
        except Exception as e:
            return self._handle_error(e, "get_dynamic_curve_data")
    
    async def start_dynamic_mode(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start dynamic voltage adjustment with the provided configuration.
        
        Args:
            config: Configuration dictionary with mode and cores data
            
        Returns:
            Dictionary with success status:
            {
                "success": True/False,
                "error": "error message" (if failed)
            }
            
        Validates: Requirements 9.5, 5.1
        """
        try:
            # Validate and apply configuration if provided
            if config:
                mode = config.get("mode", "expert")
                cores_data = config.get("cores", [])
                
                # Update manager configuration
                self.manager.config.mode = mode
                
                # Update each core configuration
                for core_data in cores_data:
                    core_id = core_data.get("core_id")
                    min_mv = core_data.get("min_mv")
                    max_mv = core_data.get("max_mv")
                    threshold = core_data.get("threshold")
                    
                    if core_id is not None:
                        # Validate
                        validation_result = self.validator.validate_config(
                            core_id, min_mv, max_mv, threshold
                        )
                        
                        if not validation_result.valid:
                            return {
                                "success": False,
                                "error": f"Validation failed for core {core_id}",
                                "validation_errors": validation_result.errors
                            }
                        
                        # Clamp and set
                        clamped_min = self.validator.clamp_voltage(min_mv)
                        clamped_max = self.validator.clamp_voltage(max_mv)
                        self.manager.set_core_config(
                            core_id, clamped_min, clamped_max, threshold
                        )
            
            # Start dynamic mode
            success = self.manager.start()
            
            if success:
                # Save configuration
                self.manager.save_config(self.settings)
                
                logger.info("Dynamic Manual Mode started")
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "Failed to start dynamic mode (may already be active)"
                }
                
        except Exception as e:
            return self._handle_error(e, "start_dynamic_mode")
    
    async def stop_dynamic_mode(self) -> Dict[str, Any]:
        """Stop dynamic voltage adjustment.
        
        Returns:
            Dictionary with success status:
            {
                "success": True/False,
                "error": "error message" (if failed)
            }
            
        Validates: Requirements 5.3
        """
        try:
            success = self.manager.stop()
            
            if success:
                logger.info("Dynamic Manual Mode stopped")
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "Failed to stop dynamic mode (may not be active)"
                }
                
        except Exception as e:
            return self._handle_error(e, "stop_dynamic_mode")
    
    async def get_core_metrics(self, core_id: int) -> Dict[str, Any]:
        """Get current metrics for a specific core.
        
        Returns real-time measurements including CPU load, voltage offset,
        frequency, and temperature.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            Dictionary with success status and metrics:
            {
                "success": True,
                "metrics": {
                    "core_id": 0,
                    "load": 45.2,
                    "voltage": -25,
                    "frequency": 2800,
                    "temperature": 65.5,
                    "timestamp": 1234567890.123
                }
            }
            
        Validates: Requirements 9.4
        """
        try:
            if not 0 <= core_id < 4:
                return {
                    "success": False,
                    "error": f"Invalid core_id: {core_id}. Must be 0-3."
                }
            
            metrics = self.manager.get_core_metrics(core_id)
            
            if metrics:
                return {
                    "success": True,
                    "metrics": metrics.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "Metrics unavailable (dynamic mode may not be active)"
                }
                
        except Exception as e:
            return self._handle_error(e, "get_core_metrics")
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get platform-specific voltage limits.
        
        Returns the minimum and maximum allowed voltage offsets for the
        current platform. These limits are used for validation and clamping.
        
        Returns:
            Dictionary with success status and limits:
            {
                "success": True,
                "limits": {
                    "min": -100,
                    "max": 0
                }
            }
            
        Validates: Requirements 7.2, 7.3
        """
        try:
            return {
                "success": True,
                "limits": {
                    "min": self.validator.platform_min,
                    "max": self.validator.platform_max
                }
            }
        except Exception as e:
            return self._handle_error(e, "get_platform_limits")
