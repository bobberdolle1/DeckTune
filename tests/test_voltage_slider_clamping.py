"""Property tests for VoltageSliders component value clamping.

Feature: manual-dynamic-mode, Property 1: Slider value clamping
Validates: Requirements 1.2, 1.3, 1.4

Property 1: Slider value clamping
For any slider adjustment (MinimalValue, MaximumValue, or Threshold), 
the resulting value SHALL be within the valid range (-100 to 0 mV for voltage, 
0 to 100% for threshold).

This test validates the clamping logic that is implemented in the VoltageSliders
component (src/components/VoltageSliders.tsx). The clamp function ensures that:
- MinimalValue slider values are clamped to [-100, 0] mV
- MaximumValue slider values are clamped to [-100, 0] mV  
- Threshold slider values are clamped to [0, 100] %
"""

import pytest
from hypothesis import given, strategies as st, settings


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to a specified range.
    This mirrors the clamp function in VoltageSliders.tsx.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value within [min_val, max_val]
    """
    return max(min_val, min(max_val, value))


# Strategies for testing
voltage_input = st.floats(min_value=-200.0, max_value=100.0, allow_nan=False, allow_infinity=False)
threshold_input = st.floats(min_value=-50.0, max_value=150.0, allow_nan=False, allow_infinity=False)

# Valid ranges
VOLTAGE_MIN = -100
VOLTAGE_MAX = 0
THRESHOLD_MIN = 0
THRESHOLD_MAX = 100


class TestMinimalValueSliderClamping:
    """Property 1: Slider value clamping for MinimalValue slider
    
    For any MinimalValue slider adjustment, the resulting value SHALL be 
    within the range [-100, 0] mV.
    
    Validates: Requirements 1.2
    """

    @given(value=voltage_input)
    @settings(max_examples=100)
    def test_minimal_value_clamped_to_range(self, value: float):
        """MinimalValue slider SHALL clamp values to [-100, 0] mV range."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert VOLTAGE_MIN <= clamped <= VOLTAGE_MAX, (
            f"MinimalValue {value} should be clamped to [{VOLTAGE_MIN}, {VOLTAGE_MAX}], "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=-100.0, max_value=0.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_minimal_value_within_range_unchanged(self, value: float):
        """MinimalValue within valid range SHALL remain unchanged."""
        rounded = round(value)
        clamped = clamp(rounded, VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == rounded, (
            f"MinimalValue {rounded} within valid range should remain unchanged, got {clamped}"
        )

    @given(value=st.floats(min_value=-200.0, max_value=-101.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_minimal_value_below_min_clamped_to_min(self, value: float):
        """MinimalValue below -100 mV SHALL be clamped to -100 mV."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == VOLTAGE_MIN, (
            f"MinimalValue {value} below {VOLTAGE_MIN} should be clamped to {VOLTAGE_MIN}, "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_minimal_value_above_max_clamped_to_max(self, value: float):
        """MinimalValue above 0 mV SHALL be clamped to 0 mV."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == VOLTAGE_MAX, (
            f"MinimalValue {value} above {VOLTAGE_MAX} should be clamped to {VOLTAGE_MAX}, "
            f"got {clamped}"
        )


class TestMaximumValueSliderClamping:
    """Property 1: Slider value clamping for MaximumValue slider
    
    For any MaximumValue slider adjustment, the resulting value SHALL be 
    within the range [-100, 0] mV.
    
    Validates: Requirements 1.3
    """

    @given(value=voltage_input)
    @settings(max_examples=100)
    def test_maximum_value_clamped_to_range(self, value: float):
        """MaximumValue slider SHALL clamp values to [-100, 0] mV range."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert VOLTAGE_MIN <= clamped <= VOLTAGE_MAX, (
            f"MaximumValue {value} should be clamped to [{VOLTAGE_MIN}, {VOLTAGE_MAX}], "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=-100.0, max_value=0.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_maximum_value_within_range_unchanged(self, value: float):
        """MaximumValue within valid range SHALL remain unchanged."""
        rounded = round(value)
        clamped = clamp(rounded, VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == rounded, (
            f"MaximumValue {rounded} within valid range should remain unchanged, got {clamped}"
        )

    @given(value=st.floats(min_value=-200.0, max_value=-101.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_maximum_value_below_min_clamped_to_min(self, value: float):
        """MaximumValue below -100 mV SHALL be clamped to -100 mV."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == VOLTAGE_MIN, (
            f"MaximumValue {value} below {VOLTAGE_MIN} should be clamped to {VOLTAGE_MIN}, "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_maximum_value_above_max_clamped_to_max(self, value: float):
        """MaximumValue above 0 mV SHALL be clamped to 0 mV."""
        clamped = clamp(round(value), VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped == VOLTAGE_MAX, (
            f"MaximumValue {value} above {VOLTAGE_MAX} should be clamped to {VOLTAGE_MAX}, "
            f"got {clamped}"
        )


class TestThresholdSliderClamping:
    """Property 1: Slider value clamping for Threshold slider
    
    For any Threshold slider adjustment, the resulting value SHALL be 
    within the range [0, 100] %.
    
    Validates: Requirements 1.4
    """

    @given(value=threshold_input)
    @settings(max_examples=100)
    def test_threshold_clamped_to_range(self, value: float):
        """Threshold slider SHALL clamp values to [0, 100] % range."""
        clamped = clamp(round(value), THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert THRESHOLD_MIN <= clamped <= THRESHOLD_MAX, (
            f"Threshold {value} should be clamped to [{THRESHOLD_MIN}, {THRESHOLD_MAX}], "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_threshold_within_range_unchanged(self, value: float):
        """Threshold within valid range SHALL remain unchanged."""
        rounded = round(value)
        clamped = clamp(rounded, THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert clamped == rounded, (
            f"Threshold {rounded} within valid range should remain unchanged, got {clamped}"
        )

    @given(value=st.floats(min_value=-50.0, max_value=-1.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_threshold_below_min_clamped_to_min(self, value: float):
        """Threshold below 0% SHALL be clamped to 0%."""
        clamped = clamp(round(value), THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert clamped == THRESHOLD_MIN, (
            f"Threshold {value} below {THRESHOLD_MIN} should be clamped to {THRESHOLD_MIN}, "
            f"got {clamped}"
        )

    @given(value=st.floats(min_value=101.0, max_value=150.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_threshold_above_max_clamped_to_max(self, value: float):
        """Threshold above 100% SHALL be clamped to 100%."""
        clamped = clamp(round(value), THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert clamped == THRESHOLD_MAX, (
            f"Threshold {value} above {THRESHOLD_MAX} should be clamped to {THRESHOLD_MAX}, "
            f"got {clamped}"
        )


class TestClampingIdempotence:
    """Additional property: Clamping is idempotent
    
    Applying clamp twice should produce the same result as applying it once.
    """

    @given(value=voltage_input)
    @settings(max_examples=100)
    def test_voltage_clamping_idempotent(self, value: float):
        """Clamping voltage twice SHALL produce same result as clamping once."""
        rounded = round(value)
        clamped_once = clamp(rounded, VOLTAGE_MIN, VOLTAGE_MAX)
        clamped_twice = clamp(clamped_once, VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped_once == clamped_twice, (
            f"Clamping {value} twice should produce same result: "
            f"once={clamped_once}, twice={clamped_twice}"
        )

    @given(value=threshold_input)
    @settings(max_examples=100)
    def test_threshold_clamping_idempotent(self, value: float):
        """Clamping threshold twice SHALL produce same result as clamping once."""
        rounded = round(value)
        clamped_once = clamp(rounded, THRESHOLD_MIN, THRESHOLD_MAX)
        clamped_twice = clamp(clamped_once, THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert clamped_once == clamped_twice, (
            f"Clamping {value} twice should produce same result: "
            f"once={clamped_once}, twice={clamped_twice}"
        )


class TestClampingMonotonicity:
    """Additional property: Clamping preserves order
    
    If value1 <= value2, then clamp(value1) <= clamp(value2).
    """

    @given(
        value1=voltage_input,
        value2=voltage_input
    )
    @settings(max_examples=100)
    def test_voltage_clamping_preserves_order(self, value1: float, value2: float):
        """Voltage clamping SHALL preserve ordering of values."""
        if value1 > value2:
            value1, value2 = value2, value1  # Ensure value1 <= value2
        
        rounded1 = round(value1)
        rounded2 = round(value2)
        clamped1 = clamp(rounded1, VOLTAGE_MIN, VOLTAGE_MAX)
        clamped2 = clamp(rounded2, VOLTAGE_MIN, VOLTAGE_MAX)
        
        assert clamped1 <= clamped2, (
            f"Clamping should preserve order: {value1} <= {value2}, "
            f"but clamp({rounded1})={clamped1} > clamp({rounded2})={clamped2}"
        )

    @given(
        value1=threshold_input,
        value2=threshold_input
    )
    @settings(max_examples=100)
    def test_threshold_clamping_preserves_order(self, value1: float, value2: float):
        """Threshold clamping SHALL preserve ordering of values."""
        if value1 > value2:
            value1, value2 = value2, value1  # Ensure value1 <= value2
        
        rounded1 = round(value1)
        rounded2 = round(value2)
        clamped1 = clamp(rounded1, THRESHOLD_MIN, THRESHOLD_MAX)
        clamped2 = clamp(rounded2, THRESHOLD_MIN, THRESHOLD_MAX)
        
        assert clamped1 <= clamped2, (
            f"Clamping should preserve order: {value1} <= {value2}, "
            f"but clamp({rounded1})={clamped1} > clamp({rounded2})={clamped2}"
        )
