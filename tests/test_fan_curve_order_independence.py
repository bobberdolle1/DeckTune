"""Property tests for FanCurve input order independence.

Feature: fan-control-curves, Property 4: Input order independence
Validates: Requirements 2.5

Tests that FanCurve produces the same sorted result regardless of
the order in which points are provided.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import random

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import FanPoint, FanCurve


# Strategy for generating valid FanPoint instances with unique temperatures
@st.composite
def unique_fan_points_strategy(draw, min_points=3, max_points=10):
    """Generate a list of FanPoint instances with unique temperatures."""
    num_points = draw(st.integers(min_value=min_points, max_value=max_points))
    
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


@given(points=unique_fan_points_strategy())
@hyp_settings(max_examples=100)
def test_input_order_independence(points):
    """Property 4: Input order independence
    
    For any set of fan curve points, the sorted points should be the same
    regardless of the order in which the points were provided.
    
    Feature: fan-control-curves, Property 4: Input order independence
    Validates: Requirements 2.5
    """
    # Create curve with original order
    curve1 = FanCurve(name="test1", points=points.copy())
    
    # Create curve with shuffled order
    shuffled_points = points.copy()
    random.shuffle(shuffled_points)
    curve2 = FanCurve(name="test2", points=shuffled_points)
    
    # Both curves should have the same sorted points
    assert len(curve1.points) == len(curve2.points)
    
    for p1, p2 in zip(curve1.points, curve2.points):
        assert p1.temp == p2.temp, \
            f"Temperature mismatch: {p1.temp} != {p2.temp}"
        assert p1.speed == p2.speed, \
            f"Speed mismatch at temp {p1.temp}: {p1.speed} != {p2.speed}"


@given(points=unique_fan_points_strategy())
@hyp_settings(max_examples=100)
def test_points_are_sorted_by_temperature(points):
    """Test that FanCurve always sorts points by temperature.
    
    Feature: fan-control-curves, Property 4: Input order independence
    Validates: Requirements 2.5
    """
    curve = FanCurve(name="test", points=points)
    
    # Verify points are sorted by temperature
    for i in range(len(curve.points) - 1):
        assert curve.points[i].temp < curve.points[i + 1].temp, \
            f"Points not sorted: {curve.points[i].temp} >= {curve.points[i + 1].temp}"


def test_order_independence_simple_case():
    """Test order independence with a simple known case."""
    points_ascending = [
        FanPoint(temp=40, speed=20),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=80)
    ]
    
    points_descending = [
        FanPoint(temp=80, speed=80),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=40, speed=20)
    ]
    
    points_mixed = [
        FanPoint(temp=60, speed=50),
        FanPoint(temp=40, speed=20),
        FanPoint(temp=80, speed=80)
    ]
    
    curve1 = FanCurve(name="asc", points=points_ascending)
    curve2 = FanCurve(name="desc", points=points_descending)
    curve3 = FanCurve(name="mixed", points=points_mixed)
    
    # All should have the same sorted order
    for i in range(3):
        assert curve1.points[i].temp == curve2.points[i].temp == curve3.points[i].temp
        assert curve1.points[i].speed == curve2.points[i].speed == curve3.points[i].speed
