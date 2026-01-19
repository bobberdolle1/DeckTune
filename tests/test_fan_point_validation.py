"""Property tests for FanPoint validation.

Feature: fan-control-curves, Property 6: Temperature range validation
Feature: fan-control-curves, Property 7: Speed range validation
Validates: Requirements 3.2, 3.3

Tests that FanPoint correctly validates temperature and speed ranges.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import FanPoint


@given(
    temp=st.one_of(
        st.integers(max_value=-1),
        st.integers(min_value=121)
    ),
    speed=st.integers(min_value=0, max_value=100)
)
@hyp_settings(max_examples=100)
def test_temperature_range_validation(temp, speed):
    """Property 6: Temperature range validation
    
    For any fan point, temperatures outside the range [0, 120] should be
    rejected during validation.
    
    Feature: fan-control-curves, Property 6: Temperature range validation
    Validates: Requirements 3.2
    """
    with pytest.raises(ValueError, match=r"Temperature .* out of range \[0, 120\]"):
        FanPoint(temp=temp, speed=speed)


@given(
    temp=st.integers(min_value=0, max_value=120),
    speed=st.one_of(
        st.integers(max_value=-1),
        st.integers(min_value=101)
    )
)
@hyp_settings(max_examples=100)
def test_speed_range_validation(temp, speed):
    """Property 7: Speed range validation
    
    For any fan point, speeds outside the range [0, 100] should be
    rejected during validation.
    
    Feature: fan-control-curves, Property 7: Speed range validation
    Validates: Requirements 3.3
    """
    with pytest.raises(ValueError, match=r"Speed .* out of range \[0, 100\]"):
        FanPoint(temp=temp, speed=speed)


@given(
    temp=st.integers(min_value=0, max_value=120),
    speed=st.integers(min_value=0, max_value=100)
)
@hyp_settings(max_examples=100)
def test_valid_fan_point_creation(temp, speed):
    """Test that valid FanPoint instances can be created.
    
    For any temperature in [0, 120] and speed in [0, 100], FanPoint
    creation should succeed.
    """
    point = FanPoint(temp=temp, speed=speed)
    assert point.temp == temp
    assert point.speed == speed


def test_fan_point_immutability():
    """Test that FanPoint is immutable (frozen dataclass)."""
    point = FanPoint(temp=50, speed=60)
    
    with pytest.raises(AttributeError):
        point.temp = 70
    
    with pytest.raises(AttributeError):
        point.speed = 80
