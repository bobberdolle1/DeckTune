"""Validator for Manual Dynamic Mode configurations.

This module provides validation logic for dynamic mode configurations,
ensuring safety constraints and preventing dangerous voltage settings.

Feature: manual-dynamic-mode
Validates: Requirements 7.1, 7.2, 7.3, 7.4
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

# Platform voltage limits (millivolts)
PLATFORM_MIN_LIMIT = -100  # Most aggressive safe value
PLATFORM_MAX_LIMIT = 0     # No undervolt

# Safe default values
SAFE_DEFAULT_MIN_MV = -30
SAFE_DEFAULT_MAX_MV = -15
SAFE_DEFAULT_THRESHOLD = 50.0


@dataclass
class ValidationResult:
    """Result of configuration validation.
    
    Attributes:
        valid: Whether the configuration is valid
        errors: List of validation error messages
    """
    valid: bool
    errors: List[str]
    
    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context."""
        return self.valid


class Validator:
    """Validator for Manual Dynamic Mode configurations.
    
    Provides validation methods for core configurations, voltage ranges,
    and safety checks to prevent dangerous settings.
    
    Feature: manual-dynamic-mode
    Validates: Requirements 7.1, 7.2, 7.3, 7.4
    """
    
    def __init__(self, platform_min: int = PLATFORM_MIN_LIMIT):
        """Initialize the validator.
        
        Args:
            platform_min: Platform-specific minimum voltage limit
        """
        self.platform_min = platform_min
        self.platform_max = PLATFORM_MAX_LIMIT
        
        logger.info(f"Validator initialized with limits: [{self.platform_min}, {self.platform_max}] mV")
    
    def validate_config(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> ValidationResult:
        """Validate a core configuration.
        
        Checks:
        - Core ID is valid (0-3)
        - Voltage values are within platform limits
        - min_mv <= max_mv (min is less aggressive)
        - Threshold is in valid range (0-100)
        
        Args:
            core_id: Core identifier
            min_mv: Minimum undervolt value
            max_mv: Maximum undervolt value
            threshold: Load threshold percentage
            
        Returns:
            ValidationResult with validation status and errors
            
        Validates: Requirements 7.1
        """
        errors = []
        
        # Validate core ID
        if not 0 <= core_id < 4:
            errors.append(f"core_id must be 0-3, got {core_id}")
        
        # Validate voltage ranges
        if not self.validate_voltage_range(min_mv):
            errors.append(
                f"min_mv ({min_mv}) must be in range [{self.platform_min}, {self.platform_max}]"
            )
        
        if not self.validate_voltage_range(max_mv):
            errors.append(
                f"max_mv ({max_mv}) must be in range [{self.platform_min}, {self.platform_max}]"
            )
        
        # Validate min-max ordering
        if not self.check_min_max_order(min_mv, max_mv):
            errors.append(
                f"min_mv ({min_mv}) must be <= max_mv ({max_mv}) "
                "(min is less aggressive, closer to 0)"
            )
        
        # Validate threshold
        if not self.validate_threshold(threshold):
            errors.append(f"threshold ({threshold}) must be in range [0, 100]")
        
        valid = len(errors) == 0
        
        if not valid:
            logger.warning(f"Validation failed for core {core_id}: {errors}")
        
        return ValidationResult(valid=valid, errors=errors)
    
    def validate_voltage_range(self, voltage: int) -> bool:
        """Check if voltage is within platform limits.
        
        Args:
            voltage: Voltage offset in mV
            
        Returns:
            True if voltage is within limits
            
        Validates: Requirements 7.2, 7.3
        """
        return self.platform_min <= voltage <= self.platform_max
    
    def validate_threshold(self, threshold: float) -> bool:
        """Check if threshold is valid.
        
        Args:
            threshold: Load threshold percentage
            
        Returns:
            True if threshold is in range [0, 100]
        """
        return 0.0 <= threshold <= 100.0
    
    def check_min_max_order(self, min_mv: int, max_mv: int) -> bool:
        """Ensure min_mv <= max_mv.
        
        In undervolt terminology:
        - min_mv is less aggressive (closer to 0, e.g., -20)
        - max_mv is more aggressive (more negative, e.g., -35)
        
        Args:
            min_mv: Minimum (less aggressive) undervolt value
            max_mv: Maximum (more aggressive) undervolt value
            
        Returns:
            True if min_mv <= max_mv
            
        Validates: Requirements 7.1
        """
        return min_mv <= max_mv
    
    def clamp_voltage(self, voltage: int) -> int:
        """Clamp voltage to platform limits.
        
        Args:
            voltage: Voltage offset in mV
            
        Returns:
            Clamped voltage value
            
        Validates: Requirements 7.2, 7.3
        """
        if voltage < self.platform_min:
            logger.warning(f"Clamping voltage {voltage} to platform min {self.platform_min}")
            return self.platform_min
        elif voltage > self.platform_max:
            logger.warning(f"Clamping voltage {voltage} to platform max {self.platform_max}")
            return self.platform_max
        return voltage
    
    def get_safe_defaults(self) -> dict:
        """Get safe default configuration values.
        
        Returns:
            Dictionary with safe default values
            
        Validates: Requirements 7.5
        """
        return {
            "min_mv": SAFE_DEFAULT_MIN_MV,
            "max_mv": SAFE_DEFAULT_MAX_MV,
            "threshold": SAFE_DEFAULT_THRESHOLD
        }
    
    def is_dangerous_config(
        self,
        min_mv: int,
        max_mv: int
    ) -> bool:
        """Check if configuration is potentially dangerous.
        
        A configuration is considered dangerous if:
        - Any voltage is below -50mV (aggressive undervolt)
        
        Args:
            min_mv: Minimum undervolt value
            max_mv: Maximum undervolt value
            
        Returns:
            True if configuration is dangerous
            
        Validates: Requirements 7.4
        """
        DANGER_THRESHOLD = -50
        return min_mv < DANGER_THRESHOLD or max_mv < DANGER_THRESHOLD
