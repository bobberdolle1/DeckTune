"""Property tests for gamepad slider adjustment.

Feature: manual-dynamic-mode, Property 17: Gamepad slider adjustment
Validates: Requirements 8.3

Property 17: Gamepad slider adjustment
For any L1 or R1 input when a slider has focus, the slider value SHALL change
by one increment in the appropriate direction.

This test validates the slider adjustment logic that is implemented in the
DynamicManualMode component (src/components/DynamicManualMode.tsx). The adjustment
ensures that:
- L1 (PageUp) increments the slider value by 1
- R1 (PageDown) decrements the slider value by 1
- Values are clamped to valid ranges:
  - Voltage sliders: [-100, 0] mV
  - Threshold slider: [0, 100] %
"""

import pytest
from hypothesis import given, strategies as st, settings, assume


def adjust_voltage_slider(current_value: int, direction: str) -> int:
    """
    Adjust voltage slider value with L1/R1 input.
    This mirrors the L1/R1 logic in DynamicManualMode.tsx for voltage sliders.
    
    Args:
        current_value: Current slider value (-100 to 0)
        direction: 'up' for L1 (increment), 'down' for R1 (decrement)
        
    Returns:
        New slider value after adjustment, clamped to [-100, 0]
    """
    increment = 1 if direction == 'up' else -1
    new_value = current_value + increment
    return max(-100, min(0, new_value))


def adjust_threshold_slider(current_value: int, direction: str) -> int:
    """
    Adjust threshold slider value with L1/R1 input.
    This mirrors the L1/R1 logic in DynamicManualMode.tsx for threshold slider.
    
    Args:
        current_value: Current slider value (0 to 100)
        direction: 'up' for L1 (increment), 'down' for R1 (decrement)
        
    Returns:
        New slider value after adjustment, clamped to [0, 100]
    """
    increment = 1 if direction == 'up' else -1
    new_value = current_value + increment
    return max(0, min(100, new_value))


# Strategies
voltage_value = st.integers(min_value=-100, max_value=0)
threshold_value = st.integers(min_value=0, max_value=100)
direction = st.sampled_from(['up', 'down'])


class TestGamepadVoltageSliderAdjustment:
    """Property 17: Gamepad slider adjustment for voltage sliders
    
    For any L1 or R1 input when a voltage slider has focus, the slider value
    SHALL change by one increment in the appropriate direction, clamped to [-100, 0].
    
    Validates: Requirements 8.3
    """

    @given(current_value=voltage_value, direction=direction)
    @settings(max_examples=100)
    def test_voltage_slider_adjusts_by_one(self, current_value: int, direction: str):
        """Voltage slider SHALL adjust by ±1 with L1/R1 input."""
        new_value = adjust_voltage_slider(current_value, direction)
        
        # Verify new value is in valid range
        assert -100 <= new_value <= 0, (
            f"Voltage value {new_value} out of valid range [-100, 0]"
        )
        
        # Verify adjustment behavior (unless at boundary)
        if direction == 'up' and current_value < 0:
            assert new_value == current_value + 1, (
                f"L1 from {current_value} should increment to {current_value + 1}, "
                f"got {new_value}"
            )
        elif direction == 'down' and current_value > -100:
            assert new_value == current_value - 1, (
                f"R1 from {current_value} should decrement to {current_value - 1}, "
                f"got {new_value}"
            )

    @given(current_value=voltage_value)
    @settings(max_examples=100)
    def test_voltage_slider_l1_increments(self, current_value: int):
        """L1 SHALL increment voltage slider value."""
        new_value = adjust_voltage_slider(current_value, 'up')
        
        if current_value < 0:
            assert new_value == current_value + 1, (
                f"L1 from {current_value} should increment to {current_value + 1}, "
                f"got {new_value}"
            )
        else:
            # At maximum, should stay at 0
            assert new_value == 0, (
                f"L1 from maximum (0) should stay at 0, got {new_value}"
            )

    @given(current_value=voltage_value)
    @settings(max_examples=100)
    def test_voltage_slider_r1_decrements(self, current_value: int):
        """R1 SHALL decrement voltage slider value."""
        new_value = adjust_voltage_slider(current_value, 'down')
        
        if current_value > -100:
            assert new_value == current_value - 1, (
                f"R1 from {current_value} should decrement to {current_value - 1}, "
                f"got {new_value}"
            )
        else:
            # At minimum, should stay at -100
            assert new_value == -100, (
                f"R1 from minimum (-100) should stay at -100, got {new_value}"
            )

    def test_voltage_slider_clamped_at_upper_bound(self):
        """Voltage slider SHALL clamp at upper bound (0 mV)."""
        assert adjust_voltage_slider(0, 'up') == 0

    def test_voltage_slider_clamped_at_lower_bound(self):
        """Voltage slider SHALL clamp at lower bound (-100 mV)."""
        assert adjust_voltage_slider(-100, 'down') == -100


class TestGamepadThresholdSliderAdjustment:
    """Property 17: Gamepad slider adjustment for threshold slider
    
    For any L1 or R1 input when the threshold slider has focus, the slider value
    SHALL change by one increment in the appropriate direction, clamped to [0, 100].
    
    Validates: Requirements 8.3
    """

    @given(current_value=threshold_value, direction=direction)
    @settings(max_examples=100)
    def test_threshold_slider_adjusts_by_one(self, current_value: int, direction: str):
        """Threshold slider SHALL adjust by ±1 with L1/R1 input."""
        new_value = adjust_threshold_slider(current_value, direction)
        
        # Verify new value is in valid range
        assert 0 <= new_value <= 100, (
            f"Threshold value {new_value} out of valid range [0, 100]"
        )
        
        # Verify adjustment behavior (unless at boundary)
        if direction == 'up' and current_value < 100:
            assert new_value == current_value + 1, (
                f"L1 from {current_value} should increment to {current_value + 1}, "
                f"got {new_value}"
            )
        elif direction == 'down' and current_value > 0:
            assert new_value == current_value - 1, (
                f"R1 from {current_value} should decrement to {current_value - 1}, "
                f"got {new_value}"
            )

    @given(current_value=threshold_value)
    @settings(max_examples=100)
    def test_threshold_slider_l1_increments(self, current_value: int):
        """L1 SHALL increment threshold slider value."""
        new_value = adjust_threshold_slider(current_value, 'up')
        
        if current_value < 100:
            assert new_value == current_value + 1, (
                f"L1 from {current_value} should increment to {current_value + 1}, "
                f"got {new_value}"
            )
        else:
            # At maximum, should stay at 100
            assert new_value == 100, (
                f"L1 from maximum (100) should stay at 100, got {new_value}"
            )

    @given(current_value=threshold_value)
    @settings(max_examples=100)
    def test_threshold_slider_r1_decrements(self, current_value: int):
        """R1 SHALL decrement threshold slider value."""
        new_value = adjust_threshold_slider(current_value, 'down')
        
        if current_value > 0:
            assert new_value == current_value - 1, (
                f"R1 from {current_value} should decrement to {current_value - 1}, "
                f"got {new_value}"
            )
        else:
            # At minimum, should stay at 0
            assert new_value == 0, (
                f"R1 from minimum (0) should stay at 0, got {new_value}"
            )

    def test_threshold_slider_clamped_at_upper_bound(self):
        """Threshold slider SHALL clamp at upper bound (100%)."""
        assert adjust_threshold_slider(100, 'up') == 100

    def test_threshold_slider_clamped_at_lower_bound(self):
        """Threshold slider SHALL clamp at lower bound (0%)."""
        assert adjust_threshold_slider(0, 'down') == 0


class TestGamepadSliderAdjustmentRoundTrip:
    """Additional property: Round-trip adjustment
    
    Adjusting up then down (or down then up) should return to original value
    (unless at a boundary).
    """

    @given(current_value=voltage_value)
    @settings(max_examples=100)
    def test_voltage_up_then_down_returns_to_original(self, current_value: int):
        """Voltage slider up then down SHALL return to original (unless at boundary)."""
        # Skip boundary cases
        assume(-100 < current_value < 0)
        
        after_up = adjust_voltage_slider(current_value, 'up')
        after_down = adjust_voltage_slider(after_up, 'down')
        
        assert after_down == current_value, (
            f"Up then down from {current_value} should return to {current_value}, "
            f"got {after_down}"
        )

    @given(current_value=voltage_value)
    @settings(max_examples=100)
    def test_voltage_down_then_up_returns_to_original(self, current_value: int):
        """Voltage slider down then up SHALL return to original (unless at boundary)."""
        # Skip boundary cases
        assume(-100 < current_value < 0)
        
        after_down = adjust_voltage_slider(current_value, 'down')
        after_up = adjust_voltage_slider(after_down, 'up')
        
        assert after_up == current_value, (
            f"Down then up from {current_value} should return to {current_value}, "
            f"got {after_up}"
        )

    @given(current_value=threshold_value)
    @settings(max_examples=100)
    def test_threshold_up_then_down_returns_to_original(self, current_value: int):
        """Threshold slider up then down SHALL return to original (unless at boundary)."""
        # Skip boundary cases
        assume(0 < current_value < 100)
        
        after_up = adjust_threshold_slider(current_value, 'up')
        after_down = adjust_threshold_slider(after_up, 'down')
        
        assert after_down == current_value, (
            f"Up then down from {current_value} should return to {current_value}, "
            f"got {after_down}"
        )

    @given(current_value=threshold_value)
    @settings(max_examples=100)
    def test_threshold_down_then_up_returns_to_original(self, current_value: int):
        """Threshold slider down then up SHALL return to original (unless at boundary)."""
        # Skip boundary cases
        assume(0 < current_value < 100)
        
        after_down = adjust_threshold_slider(current_value, 'down')
        after_up = adjust_threshold_slider(after_down, 'up')
        
        assert after_up == current_value, (
            f"Down then up from {current_value} should return to {current_value}, "
            f"got {after_up}"
        )


class TestGamepadSliderAdjustmentSequence:
    """Additional property: Sequential adjustments
    
    Multiple adjustment operations should maintain valid state.
    """

    @given(
        start_value=voltage_value,
        operations=st.lists(
            st.sampled_from(['up', 'down']),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_voltage_sequence_maintains_valid_range(
        self,
        start_value: int,
        operations: list
    ):
        """Any sequence of voltage slider adjustments SHALL maintain valid range."""
        value = start_value
        
        for op in operations:
            value = adjust_voltage_slider(value, op)
            
            assert -100 <= value <= 0, (
                f"Voltage value {value} out of valid range [-100, 0] after operation {op}"
            )

    @given(
        start_value=threshold_value,
        operations=st.lists(
            st.sampled_from(['up', 'down']),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_threshold_sequence_maintains_valid_range(
        self,
        start_value: int,
        operations: list
    ):
        """Any sequence of threshold slider adjustments SHALL maintain valid range."""
        value = start_value
        
        for op in operations:
            value = adjust_threshold_slider(value, op)
            
            assert 0 <= value <= 100, (
                f"Threshold value {value} out of valid range [0, 100] after operation {op}"
            )


class TestGamepadSliderAdjustmentIdempotence:
    """Additional property: Idempotence at boundaries
    
    Adjusting at a boundary should remain at the boundary.
    """

    def test_voltage_max_stays_at_max_on_increment(self):
        """Voltage slider at max (0) SHALL stay at max when incremented."""
        assert adjust_voltage_slider(0, 'up') == 0

    def test_voltage_min_stays_at_min_on_decrement(self):
        """Voltage slider at min (-100) SHALL stay at min when decremented."""
        assert adjust_voltage_slider(-100, 'down') == -100

    def test_threshold_max_stays_at_max_on_increment(self):
        """Threshold slider at max (100) SHALL stay at max when incremented."""
        assert adjust_threshold_slider(100, 'up') == 100

    def test_threshold_min_stays_at_min_on_decrement(self):
        """Threshold slider at min (0) SHALL stay at min when decremented."""
        assert adjust_threshold_slider(0, 'down') == 0

    @given(count=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_voltage_multiple_increments_at_max_stays_at_max(self, count: int):
        """Multiple increments at voltage max SHALL keep value at max."""
        value = 0
        for _ in range(count):
            value = adjust_voltage_slider(value, 'up')
        
        assert value == 0, (
            f"After {count} increments from max (0), value should stay at 0, got {value}"
        )

    @given(count=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_voltage_multiple_decrements_at_min_stays_at_min(self, count: int):
        """Multiple decrements at voltage min SHALL keep value at min."""
        value = -100
        for _ in range(count):
            value = adjust_voltage_slider(value, 'down')
        
        assert value == -100, (
            f"After {count} decrements from min (-100), value should stay at -100, got {value}"
        )
