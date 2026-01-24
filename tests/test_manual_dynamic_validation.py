"""Property tests for Manual Dynamic Mode configuration validation.

Feature: manual-dynamic-mode, Property 12: Validation min-max ordering
Feature: manual-dynamic-mode, Property 13: Voltage lower bound clamping
Feature: manual-dynamic-mode, Property 14: Voltage upper bound clamping
Validates: Requirements 7.1, 7.2, 7.3

Property 12: Validation min-max ordering
For any CoreConfig where MinimalValue is greater than MaximumValue, 
validation SHALL fail and prevent Apply.

Property 13: Voltage lower bound clamping
For any voltage value below the platform minimum limit, the clamped value 
SHALL equal the platform minimum.

Property 14: Voltage upper bound clamping
For any voltage value above 0mV, the clamped value SHALL equal 0mV.
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.dynamic.manual_validator import Validator, PLATFORM_MIN_LIMIT, PLATFORM_MAX_LIMIT


# Strategies for voltage values
voltage_value = st.integers(min_value=-150, max_value=50)  # Extended range to test clamping
valid_voltage = st.integers(min_value=PLATFORM_MIN_LIMIT, max_value=PLATFORM_MAX_LIMIT)
below_min_voltage = st.integers(min_value=-200, max_value=PLATFORM_MIN_LIMIT - 1)
above_max_voltage = st.integers(min_value=PLATFORM_MAX_LIMIT + 1, max_value=100)

# Strategy for threshold values
threshold_value = st.floats(min_value=-10.0, max_value=110.0)  # Extended range to test validation
valid_threshold = st.floats(min_value=0.0, max_value=100.0)

# Strategy for core IDs
core_id = st.integers(min_value=0, max_value=3)


class TestValidationMinMaxOrdering:
    """Property 12: Validation min-max ordering
    
    For any CoreConfig where MinimalValue is greater than MaximumValue, 
    validation SHALL fail and prevent Apply.
    
    Validates: Requirements 7.1
    """

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=valid_threshold
    )
    @settings(max_examples=100)
    def test_min_greater_than_max_fails_validation(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """When min_mv > max_mv, validation SHALL fail."""
        validator = Validator()
        
        # Only test cases where min > max
        if min_mv <= max_mv:
            return  # Skip this case
        
        result = validator.validate_config(core_id, min_mv, max_mv, threshold)
        
        assert not result.valid, (
            f"Validation should fail when min_mv ({min_mv}) > max_mv ({max_mv}), "
            f"but got valid={result.valid}"
        )
        
        # Check that the error message mentions min-max ordering
        error_text = " ".join(result.errors).lower()
        assert "min_mv" in error_text and "max_mv" in error_text, (
            f"Error should mention min_mv and max_mv ordering, got: {result.errors}"
        )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=valid_threshold
    )
    @settings(max_examples=100)
    def test_min_equal_or_less_than_max_passes_ordering_check(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """When min_mv <= max_mv, the min-max ordering check SHALL pass."""
        validator = Validator()
        
        # Only test cases where min <= max
        if min_mv > max_mv:
            return  # Skip this case
        
        result = validator.check_min_max_order(min_mv, max_mv)
        
        assert result, (
            f"Min-max ordering check should pass when min_mv ({min_mv}) <= max_mv ({max_mv})"
        )


class TestVoltageLowerBoundClamping:
    """Property 13: Voltage lower bound clamping
    
    For any voltage value below the platform minimum limit, the clamped value 
    SHALL equal the platform minimum.
    
    Validates: Requirements 7.2
    """

    @given(voltage=below_min_voltage)
    @settings(max_examples=100)
    def test_voltage_below_min_clamped_to_min(self, voltage: int):
        """Voltage below platform minimum SHALL be clamped to platform minimum."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped == PLATFORM_MIN_LIMIT, (
            f"Voltage {voltage} below platform min {PLATFORM_MIN_LIMIT} "
            f"should be clamped to {PLATFORM_MIN_LIMIT}, got {clamped}"
        )

    @given(voltage=valid_voltage)
    @settings(max_examples=100)
    def test_voltage_within_range_unchanged_lower_bound(self, voltage: int):
        """Voltage within valid range SHALL not be clamped at lower bound."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped == voltage, (
            f"Voltage {voltage} within valid range should remain unchanged, got {clamped}"
        )

    @given(voltage=voltage_value)
    @settings(max_examples=100)
    def test_clamped_voltage_never_below_min(self, voltage: int):
        """Clamped voltage SHALL never be below platform minimum."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped >= PLATFORM_MIN_LIMIT, (
            f"Clamped voltage {clamped} is below platform min {PLATFORM_MIN_LIMIT}"
        )


class TestVoltageUpperBoundClamping:
    """Property 14: Voltage upper bound clamping
    
    For any voltage value above 0mV, the clamped value SHALL equal 0mV.
    
    Validates: Requirements 7.3
    """

    @given(voltage=above_max_voltage)
    @settings(max_examples=100)
    def test_voltage_above_max_clamped_to_max(self, voltage: int):
        """Voltage above platform maximum (0mV) SHALL be clamped to 0mV."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped == PLATFORM_MAX_LIMIT, (
            f"Voltage {voltage} above platform max {PLATFORM_MAX_LIMIT} "
            f"should be clamped to {PLATFORM_MAX_LIMIT}, got {clamped}"
        )

    @given(voltage=valid_voltage)
    @settings(max_examples=100)
    def test_voltage_within_range_unchanged_upper_bound(self, voltage: int):
        """Voltage within valid range SHALL not be clamped at upper bound."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped == voltage, (
            f"Voltage {voltage} within valid range should remain unchanged, got {clamped}"
        )

    @given(voltage=voltage_value)
    @settings(max_examples=100)
    def test_clamped_voltage_never_above_max(self, voltage: int):
        """Clamped voltage SHALL never be above platform maximum (0mV)."""
        validator = Validator()
        
        clamped = validator.clamp_voltage(voltage)
        
        assert clamped <= PLATFORM_MAX_LIMIT, (
            f"Clamped voltage {clamped} is above platform max {PLATFORM_MAX_LIMIT}"
        )


class TestValidationCompleteness:
    """Additional validation tests to ensure comprehensive coverage."""

    @given(
        core_id=st.integers(min_value=-5, max_value=10),
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=valid_threshold
    )
    @settings(max_examples=100)
    def test_invalid_core_id_fails_validation(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """Core ID outside range [0, 3] SHALL fail validation."""
        validator = Validator()
        
        # Only test invalid core IDs
        if 0 <= core_id < 4:
            return  # Skip valid core IDs
        
        result = validator.validate_config(core_id, min_mv, max_mv, threshold)
        
        assert not result.valid, (
            f"Validation should fail for invalid core_id {core_id}"
        )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=threshold_value
    )
    @settings(max_examples=100)
    def test_invalid_threshold_fails_validation(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """Threshold outside range [0, 100] SHALL fail validation."""
        validator = Validator()
        
        # Only test invalid thresholds
        if 0.0 <= threshold <= 100.0:
            return  # Skip valid thresholds
        
        result = validator.validate_config(core_id, min_mv, max_mv, threshold)
        
        assert not result.valid, (
            f"Validation should fail for invalid threshold {threshold}"
        )

    @given(
        core_id=core_id,
        min_mv=voltage_value,
        max_mv=voltage_value,
        threshold=valid_threshold
    )
    @settings(max_examples=100)
    def test_voltage_outside_range_fails_validation(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """Voltage values outside platform limits SHALL fail validation."""
        validator = Validator()
        
        # Only test voltages outside valid range
        if (PLATFORM_MIN_LIMIT <= min_mv <= PLATFORM_MAX_LIMIT and
            PLATFORM_MIN_LIMIT <= max_mv <= PLATFORM_MAX_LIMIT):
            return  # Skip valid voltages
        
        result = validator.validate_config(core_id, min_mv, max_mv, threshold)
        
        assert not result.valid, (
            f"Validation should fail for voltages outside range: "
            f"min_mv={min_mv}, max_mv={max_mv}"
        )
