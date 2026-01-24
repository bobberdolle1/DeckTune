"""Integration tests for safety features and validation.

Feature: manual-dynamic-mode
Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5

Tests the complete safety feature implementation including:
- Frontend validation for min <= max
- Platform limit checks
- Dangerous configuration detection
- Safe defaults
"""

import pytest
from backend.dynamic.manual_validator import Validator, SAFE_DEFAULT_MIN_MV, SAFE_DEFAULT_MAX_MV, SAFE_DEFAULT_THRESHOLD


class TestSafetyFeatures:
    """Integration tests for safety features."""
    
    def test_safe_defaults_are_valid(self):
        """Safe default values SHALL pass validation.
        
        Validates: Requirements 7.5
        """
        validator = Validator()
        
        result = validator.validate_config(
            core_id=0,
            min_mv=SAFE_DEFAULT_MIN_MV,
            max_mv=SAFE_DEFAULT_MAX_MV,
            threshold=SAFE_DEFAULT_THRESHOLD
        )
        
        assert result.valid, f"Safe defaults should be valid, got errors: {result.errors}"
    
    def test_min_greater_than_max_validation_error(self):
        """Configuration with min > max SHALL fail validation.
        
        Validates: Requirements 7.1
        """
        validator = Validator()
        
        result = validator.validate_config(
            core_id=0,
            min_mv=-10,  # Less aggressive (closer to 0)
            max_mv=-50,  # More aggressive (more negative)
            threshold=50.0
        )
        
        assert not result.valid, "Validation should fail when min > max"
        assert len(result.errors) > 0, "Should have validation errors"
        
        # Check error message mentions min-max ordering
        error_text = " ".join(result.errors).lower()
        assert "min_mv" in error_text and "max_mv" in error_text
    
    def test_voltage_below_platform_min_validation_error(self):
        """Voltage below platform minimum SHALL fail validation.
        
        Validates: Requirements 7.2
        """
        validator = Validator()
        
        result = validator.validate_config(
            core_id=0,
            min_mv=-150,  # Below platform minimum
            max_mv=-100,
            threshold=50.0
        )
        
        assert not result.valid, "Validation should fail for voltage below platform min"
        assert len(result.errors) > 0, "Should have validation errors"
    
    def test_voltage_above_zero_validation_error(self):
        """Voltage above 0mV SHALL fail validation.
        
        Validates: Requirements 7.3
        """
        validator = Validator()
        
        result = validator.validate_config(
            core_id=0,
            min_mv=10,  # Above 0mV
            max_mv=20,  # Above 0mV
            threshold=50.0
        )
        
        assert not result.valid, "Validation should fail for voltage above 0mV"
        assert len(result.errors) > 0, "Should have validation errors"
    
    def test_dangerous_config_detection(self):
        """Aggressive voltage offsets SHALL be detected as dangerous.
        
        Validates: Requirements 7.4
        """
        validator = Validator()
        
        # Test with aggressive undervolt (below -50mV)
        is_dangerous = validator.is_dangerous_config(
            min_mv=-60,
            max_mv=-70
        )
        
        assert is_dangerous, "Configuration with voltages below -50mV should be dangerous"
    
    def test_safe_config_not_dangerous(self):
        """Safe voltage offsets SHALL not be detected as dangerous.
        
        Validates: Requirements 7.4
        """
        validator = Validator()
        
        # Test with safe undervolt (above -50mV)
        is_dangerous = validator.is_dangerous_config(
            min_mv=-30,
            max_mv=-15
        )
        
        assert not is_dangerous, "Safe configuration should not be dangerous"
    
    def test_voltage_clamping_to_platform_limits(self):
        """Voltages SHALL be clamped to platform limits.
        
        Validates: Requirements 7.2, 7.3
        """
        validator = Validator()
        
        # Test clamping below minimum
        clamped_low = validator.clamp_voltage(-150)
        assert clamped_low == validator.platform_min, (
            f"Voltage below min should be clamped to {validator.platform_min}"
        )
        
        # Test clamping above maximum
        clamped_high = validator.clamp_voltage(50)
        assert clamped_high == validator.platform_max, (
            f"Voltage above max should be clamped to {validator.platform_max}"
        )
        
        # Test no clamping for valid voltage
        valid_voltage = -30
        clamped_valid = validator.clamp_voltage(valid_voltage)
        assert clamped_valid == valid_voltage, (
            "Valid voltage should not be clamped"
        )
    
    def test_get_safe_defaults(self):
        """Validator SHALL provide safe default values.
        
        Validates: Requirements 7.5
        """
        validator = Validator()
        
        defaults = validator.get_safe_defaults()
        
        assert "min_mv" in defaults
        assert "max_mv" in defaults
        assert "threshold" in defaults
        
        # Verify defaults are valid
        result = validator.validate_config(
            core_id=0,
            min_mv=defaults["min_mv"],
            max_mv=defaults["max_mv"],
            threshold=defaults["threshold"]
        )
        
        assert result.valid, "Safe defaults should pass validation"
    
    def test_invalid_core_id_validation_error(self):
        """Invalid core ID SHALL fail validation."""
        validator = Validator()
        
        # Test core ID below 0
        result = validator.validate_config(
            core_id=-1,
            min_mv=-30,
            max_mv=-15,
            threshold=50.0
        )
        
        assert not result.valid, "Validation should fail for core_id < 0"
        
        # Test core ID above 3
        result = validator.validate_config(
            core_id=4,
            min_mv=-30,
            max_mv=-15,
            threshold=50.0
        )
        
        assert not result.valid, "Validation should fail for core_id > 3"
    
    def test_invalid_threshold_validation_error(self):
        """Invalid threshold SHALL fail validation."""
        validator = Validator()
        
        # Test threshold below 0
        result = validator.validate_config(
            core_id=0,
            min_mv=-30,
            max_mv=-15,
            threshold=-10.0
        )
        
        assert not result.valid, "Validation should fail for threshold < 0"
        
        # Test threshold above 100
        result = validator.validate_config(
            core_id=0,
            min_mv=-30,
            max_mv=-15,
            threshold=110.0
        )
        
        assert not result.valid, "Validation should fail for threshold > 100"
    
    def test_valid_configuration_passes_all_checks(self):
        """Valid configuration SHALL pass all validation checks."""
        validator = Validator()
        
        result = validator.validate_config(
            core_id=2,
            min_mv=-40,
            max_mv=-20,
            threshold=60.0
        )
        
        assert result.valid, f"Valid configuration should pass, got errors: {result.errors}"
        assert len(result.errors) == 0, "Valid configuration should have no errors"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
