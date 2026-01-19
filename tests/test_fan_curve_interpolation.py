"""Property tests for fan curve linear interpolation.

Feature: fan-control-curves, Property 2: Linear interpolation correctness
Feature: fan-control-curves, Property 3: Output range invariant
Feature: fan-control-curves, Property 13: Interpolation determinism
Validates: Requirements 2.1, 2.4, 7.1

Tests that the calculate_fan_speed function correctly implements linear
interpolation and maintains output invariants.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import FanPoint, calculate_fan_speed


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
    curve_points=fan_curve_points_strategy()
)
@hyp_settings(max_examples=100)
def test_linear_interpolation_correctness(curve_points):
    """Property 2: Linear interpolation correctness
    
    For any valid fan curve and any temperature between two consecutive curve points,
    the calculated speed should satisfy the linear interpolation formula:
    speed = p1.speed + (temp - p1.temp) * (p2.speed - p1.speed) / (p2.temp - p1.temp)
    
    Feature: fan-control-curves, Property 2: Linear interpolation correctness
    Validates: Requirements 2.1
    """
    # Sort points by temperature
    sorted_points = sorted(curve_points, key=lambda p: p.temp)
    
    # Test interpolation between each consecutive pair of points
    for i in range(len(sorted_points) - 1):
        p1, p2 = sorted_points[i], sorted_points[i + 1]
        
        # Skip if points are at the same temperature (shouldn't happen with unique temps)
        if p1.temp == p2.temp:
            continue
        
        # Test a temperature in the middle of the two points
        mid_temp = (p1.temp + p2.temp) / 2.0
        
        # Calculate expected speed using linear interpolation formula
        ratio = (mid_temp - p1.temp) / (p2.temp - p1.temp)
        expected_speed = p1.speed + (p2.speed - p1.speed) * ratio
        expected_speed_int = int(round(expected_speed))
        
        # Calculate actual speed
        actual_speed = calculate_fan_speed(mid_temp, curve_points)
        
        # Verify they match
        assert actual_speed == expected_speed_int, (
            f"Interpolation mismatch: temp={mid_temp}, "
            f"expected={expected_speed_int}, actual={actual_speed}, "
            f"p1=({p1.temp}, {p1.speed}), p2=({p2.temp}, {p2.speed})"
        )


@given(
    curve_points=fan_curve_points_strategy(),
    temp=st.floats(min_value=-50.0, max_value=200.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=100)
def test_output_range_invariant(curve_points, temp):
    """Property 3: Output range invariant
    
    For any valid fan curve and any temperature value, the calculated fan speed
    should be an integer between 0 and 100 inclusive.
    
    Feature: fan-control-curves, Property 3: Output range invariant
    Validates: Requirements 2.4
    """
    speed = calculate_fan_speed(temp, curve_points)
    
    # Verify output is an integer
    assert isinstance(speed, int), f"Speed {speed} is not an integer"
    
    # Verify output is in valid range
    assert 0 <= speed <= 100, f"Speed {speed} is out of range [0, 100]"


@given(
    curve_points=fan_curve_points_strategy(),
    temp=st.floats(min_value=0.0, max_value=120.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=100)
def test_interpolation_determinism(curve_points, temp):
    """Property 13: Interpolation determinism
    
    For any fan curve and temperature value, calling the interpolation function
    multiple times with the same inputs should always produce the same output.
    
    Feature: fan-control-curves, Property 13: Interpolation determinism
    Validates: Requirements 7.1
    """
    # Call the function 10 times
    results = [calculate_fan_speed(temp, curve_points) for _ in range(10)]
    
    # All results should be identical
    assert len(set(results)) == 1, (
        f"Non-deterministic results for temp={temp}: {results}"
    )


def test_edge_case_below_minimum():
    """Test that temperatures below the minimum point return the minimum speed."""
    points = [
        FanPoint(temp=40, speed=20),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    # Test temperatures below minimum
    assert calculate_fan_speed(30.0, points) == 20
    assert calculate_fan_speed(0.0, points) == 20
    assert calculate_fan_speed(-10.0, points) == 20


def test_edge_case_above_maximum():
    """Test that temperatures above the maximum point return the maximum speed."""
    points = [
        FanPoint(temp=40, speed=20),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    # Test temperatures above maximum
    assert calculate_fan_speed(90.0, points) == 100
    assert calculate_fan_speed(120.0, points) == 100
    assert calculate_fan_speed(150.0, points) == 100


def test_edge_case_exactly_on_point():
    """Test that temperatures exactly on a point return that point's speed."""
    points = [
        FanPoint(temp=40, speed=20),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    # Test temperatures exactly on points
    assert calculate_fan_speed(40.0, points) == 20
    assert calculate_fan_speed(60.0, points) == 50
    assert calculate_fan_speed(80.0, points) == 100


def test_interpolation_between_points():
    """Test linear interpolation between two points."""
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=100),
        FanPoint(temp=80, speed=100)
    ]
    
    # Test interpolation between 40°C (0%) and 60°C (100%)
    # At 50°C, should be 50%
    assert calculate_fan_speed(50.0, points) == 50
    
    # At 45°C, should be 25%
    assert calculate_fan_speed(45.0, points) == 25
    
    # At 55°C, should be 75%
    assert calculate_fan_speed(55.0, points) == 75
