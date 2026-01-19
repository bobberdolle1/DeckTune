"""Property tests for FanCurve validation.

Feature: fan-control-curves, Property 5: Point count validation
Validates: Requirements 3.1

Tests that FanCurve correctly validates point count constraints.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import FanPoint, FanCurve


# Strategy for generating valid FanPoint instances
@st.composite
def fan_point_strategy(draw):
    """Generate valid FanPoint instances."""
    temp = draw(st.integers(min_value=0, max_value=120))
    speed = draw(st.integers(min_value=0, max_value=100))
    return FanPoint(temp=temp, speed=speed)


@given(
    num_points=st.one_of(
        st.integers(min_value=0, max_value=2),
        st.integers(min_value=11, max_value=20)
    )
)
@hyp_settings(max_examples=100)
def test_point_count_validation_rejects_invalid(num_points):
    """Property 5: Point count validation (rejection case)
    
    For any custom curve creation attempt, curves with fewer than 3 points
    or more than 10 points should be rejected.
    
    Feature: fan-control-curves, Property 5: Point count validation
    Validates: Requirements 3.1
    """
    # Generate unique temperature points to avoid duplicates
    points = []
    temps_used = set()
    for i in range(num_points):
        temp = i * 10  # Use evenly spaced temperatures
        if temp <= 120 and temp not in temps_used:
            points.append(FanPoint(temp=temp, speed=50))
            temps_used.add(temp)
    
    # Adjust if we couldn't generate enough unique points
    if len(points) != num_points:
        return  # Skip this test case
    
    if num_points < 3:
        with pytest.raises(ValueError, match=r"Curve must have at least 3 points"):
            FanCurve(name="test", points=points)
    else:  # num_points > 10
        with pytest.raises(ValueError, match=r"Curve cannot have more than 10 points"):
            FanCurve(name="test", points=points)


@given(
    num_points=st.integers(min_value=3, max_value=10)
)
@hyp_settings(max_examples=100)
def test_point_count_validation_accepts_valid(num_points):
    """Property 5: Point count validation (acceptance case)
    
    For any custom curve creation attempt, curves with 3-10 points
    should be accepted.
    
    Feature: fan-control-curves, Property 5: Point count validation
    Validates: Requirements 3.1
    """
    # Generate unique temperature points
    points = []
    for i in range(num_points):
        temp = i * 10  # Use evenly spaced temperatures (0, 10, 20, ...)
        points.append(FanPoint(temp=temp, speed=50))
    
    # Should not raise an exception
    curve = FanCurve(name="test", points=points)
    assert len(curve.points) == num_points


def test_fan_curve_basic_creation():
    """Test basic FanCurve creation with valid points."""
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    curve = FanCurve(name="test_curve", points=points)
    assert curve.name == "test_curve"
    assert len(curve.points) == 3
    assert curve.is_preset is False


def test_fan_curve_preset_flag():
    """Test FanCurve with is_preset flag."""
    points = [
        FanPoint(temp=40, speed=0),
        FanPoint(temp=60, speed=50),
        FanPoint(temp=80, speed=100)
    ]
    
    curve = FanCurve(name="stock", points=points, is_preset=True)
    assert curve.is_preset is True
