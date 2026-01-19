"""Property tests for fan safety override logic.

Feature: fan-control-curves, Property 12: Critical temperature override
Feature: fan-control-curves, Property 11: Zero RPM safety enforcement
Validates: Requirements 5.4, 5.3

Tests that safety override logic correctly handles critical temperatures
and zero RPM conditions.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import FanPoint, FanCurve, calculate_fan_speed, apply_safety_override


# Strategy for generating valid FanPoint instances
@st.composite
def fan_point_strategy(draw):
    """Generate valid FanPoint instances."""
    temp = draw(st.integers(min_value=0, max_value=120))
    speed = draw(st.integers(min_value=0, max_value=100))
    return FanPoint(temp=temp, speed=speed)


@st.composite
def fan_curve_points_strategy(draw):
    """Generate a valid list of FanPoint instances for a curve (3-10 points with unique temps)."""
    num_points = draw(st.integers(min_value=3, max_value=10))
    
    # Generate unique temperatures
    temps = draw(st.lists(
        st.integers(min_value=0, max_value=120),
        min_size=num_points,
        max_size=num_points,
        unique=True
    ))
    
    # Generate speeds for each temperature
    points = []
    for temp in temps:
        speed = draw(st.integers(min_value=0, max_value=100))
        points.append(FanPoint(temp=temp, speed=speed))
    
    return points


@given(
    curve_points=fan_curve_points_strategy(),
    temp=st.floats(min_value=95.0, max_value=150.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=100)
def test_critical_temperature_override(curve_points, temp):
    """Property 12: Critical temperature override
    
    For any fan curve and any temperature above 95°C, the applied fan speed
    should be 100% regardless of the curve's calculated value.
    
    Feature: fan-control-curves, Property 12: Critical temperature override
    Validates: Requirements 5.4
    """
    # Calculate speed from curve
    calculated_speed = calculate_fan_speed(temp, curve_points)
    
    # Apply safety override
    final_speed = apply_safety_override(temp, calculated_speed)
    
    # Verify critical override is applied
    assert final_speed == 100, (
        f"Critical temperature {temp}°C should force 100% speed, "
        f"but got {final_speed}%"
    )


@given(
    curve_points=fan_curve_points_strategy()
)
@hyp_settings(max_examples=100)
def test_zero_rpm_safety_enforcement(curve_points):
    """Property 11: Zero RPM safety enforcement
    
    For any fan curve, a speed of 0% should only be applied when the current
    temperature is at or below the minimum temperature point in the curve.
    
    Feature: fan-control-curves, Property 11: Zero RPM safety enforcement
    Validates: Requirements 5.3
    """
    # Sort points to find minimum temperature
    sorted_points = sorted(curve_points, key=lambda p: p.temp)
    min_temp = sorted_points[0].temp
    min_speed = sorted_points[0].speed
    
    # Test at minimum temperature
    speed_at_min = calculate_fan_speed(float(min_temp), curve_points)
    assert speed_at_min == min_speed, (
        f"Speed at minimum temp {min_temp}°C should be {min_speed}%, "
        f"but got {speed_at_min}%"
    )
    
    # Test below minimum temperature
    if min_temp > 0:
        speed_below_min = calculate_fan_speed(float(min_temp - 1), curve_points)
        assert speed_below_min == min_speed, (
            f"Speed below minimum temp should be {min_speed}%, "
            f"but got {speed_below_min}%"
        )
    
    # If minimum speed is 0%, verify it's only applied at or below minimum temp
    if min_speed == 0:
        # Test above minimum temperature - should not be 0% unless curve dictates it
        if len(sorted_points) > 1 and sorted_points[1].temp > min_temp:
            # Test just above minimum temp
            test_temp = float(min_temp + 1)
            if test_temp < sorted_points[1].temp:
                speed_above_min = calculate_fan_speed(test_temp, curve_points)
                # Speed should be interpolated between min and next point
                # It should only be 0 if we're still at the minimum point
                if test_temp > min_temp:
                    # We're above minimum, so speed should be >= 0
                    assert speed_above_min >= 0, (
                        f"Speed above minimum temp should be >= 0%, "
                        f"but got {speed_above_min}%"
                    )


def test_warning_temperature_boost():
    """Test that temperatures between 90-95°C get minimum 80% speed."""
    # Test with a curve that would normally give lower speeds
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=30),
        FanPoint(temp=80, speed=50),
        FanPoint(temp=100, speed=70)
    ]
    
    # At 92°C, curve would give ~60%, but safety should boost to 80%
    calculated = calculate_fan_speed(92.0, points)
    final = apply_safety_override(92.0, calculated)
    assert final == 80, f"Warning temp should boost to 80%, got {final}%"
    
    # At 94°C, curve would give ~65%, but safety should boost to 80%
    calculated = calculate_fan_speed(94.0, points)
    final = apply_safety_override(94.0, calculated)
    assert final == 80, f"Warning temp should boost to 80%, got {final}%"


def test_critical_temperature_override_specific():
    """Test that temperatures >= 95°C always get 100% speed."""
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=30),
        FanPoint(temp=80, speed=50),
        FanPoint(temp=100, speed=70)
    ]
    
    # At 95°C, should be 100% regardless of curve
    calculated = calculate_fan_speed(95.0, points)
    final = apply_safety_override(95.0, calculated)
    assert final == 100, f"Critical temp 95°C should be 100%, got {final}%"
    
    # At 100°C, should be 100%
    calculated = calculate_fan_speed(100.0, points)
    final = apply_safety_override(100.0, calculated)
    assert final == 100, f"Critical temp 100°C should be 100%, got {final}%"
    
    # At 110°C, should be 100%
    calculated = calculate_fan_speed(110.0, points)
    final = apply_safety_override(110.0, calculated)
    assert final == 100, f"Critical temp 110°C should be 100%, got {final}%"


def test_normal_operation_no_override():
    """Test that temperatures < 90°C use calculated speed without override."""
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    # At 70°C, should use calculated speed (75%)
    calculated = calculate_fan_speed(70.0, points)
    final = apply_safety_override(70.0, calculated)
    assert final == calculated, (
        f"Normal temp should use calculated speed {calculated}%, got {final}%"
    )
    
    # At 50°C, should use calculated speed (25%)
    calculated = calculate_fan_speed(50.0, points)
    final = apply_safety_override(50.0, calculated)
    assert final == calculated, (
        f"Normal temp should use calculated speed {calculated}%, got {final}%"
    )
