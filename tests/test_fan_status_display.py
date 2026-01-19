"""Property tests for fan control status display consistency.

Feature: fan-control-curves, Property 9: Status display consistency
Validates: Requirements 6.3

Tests that the status display correctly reflects the interpolation calculation
for the active curve and current temperature.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import (
    FanPoint, FanCurve, FanControlService, HwmonInterface,
    calculate_fan_speed, apply_safety_override
)


# Strategy for generating valid FanPoint instances
@st.composite
def fan_point_strategy(draw):
    """Generate valid FanPoint instances."""
    temp = draw(st.integers(min_value=0, max_value=120))
    speed = draw(st.integers(min_value=0, max_value=100))
    return FanPoint(temp=temp, speed=speed)


@st.composite
def fan_curve_strategy(draw):
    """Generate a valid FanCurve with 3-10 unique temperature points."""
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
    
    curve_name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)))
    
    return FanCurve(name=curve_name, points=points, is_preset=False)


@given(
    curve=fan_curve_strategy(),
    temp=st.floats(min_value=0.0, max_value=120.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=100)
def test_status_display_consistency(curve, temp):
    """Property 9: Status display consistency
    
    For any active curve and current temperature, the displayed target speed
    should match the result of the interpolation calculation.
    
    Feature: fan-control-curves, Property 9: Status display consistency
    Validates: Requirements 6.3
    """
    # Create a mock hwmon interface
    mock_hwmon = Mock(spec=HwmonInterface)
    mock_hwmon.is_available.return_value = True
    mock_hwmon.read_temperature.return_value = temp
    mock_hwmon.read_current_pwm.return_value = 50  # Arbitrary current speed
    
    # Create service with temporary config path (won't be used since we mock everything)
    import tempfile
    import os
    config_path = os.path.join(tempfile.gettempdir(), f"test_fan_control_{os.getpid()}.json")
    service = FanControlService(hwmon_interface=mock_hwmon, config_path=config_path)
    
    # Set the active curve
    service.active_curve = curve
    service.active_curve_type = "custom"
    
    # Simulate monitoring loop state
    service._current_temp = temp
    
    # Calculate expected target speed using the same logic as monitoring loop
    calculated_speed = calculate_fan_speed(temp, curve.points)
    expected_target_speed = apply_safety_override(temp, calculated_speed)
    
    # Set the target speed as the monitoring loop would
    service._target_speed = expected_target_speed
    service._last_update = datetime.now(timezone.utc)
    
    # Get status
    status = service.get_current_status()
    
    # Verify that target_speed in status matches our calculation
    assert status["target_speed"] == expected_target_speed, (
        f"Status target_speed mismatch: "
        f"expected={expected_target_speed}, actual={status['target_speed']}, "
        f"temp={temp}, curve={curve.name}"
    )
    
    # Verify other status fields are consistent
    assert status["current_temp"] == temp
    assert status["active_curve"] == curve.name
    assert status["curve_type"] == "custom"
    assert status["hwmon_available"] is True


def test_status_display_with_preset():
    """Test status display with a preset curve."""
    # Create a mock hwmon interface
    mock_hwmon = Mock(spec=HwmonInterface)
    mock_hwmon.is_available.return_value = True
    mock_hwmon.read_temperature.return_value = 65.0
    mock_hwmon.read_current_pwm.return_value = 45
    
    # Create service
    service = FanControlService(hwmon_interface=mock_hwmon, config_path="/tmp/test_config.json")
    
    # Apply stock preset
    service.apply_preset("stock")
    
    # Simulate monitoring state
    temp = 65.0
    service._current_temp = temp
    calculated_speed = calculate_fan_speed(temp, service.active_curve.points)
    service._target_speed = apply_safety_override(temp, calculated_speed)
    service._last_update = datetime.now(timezone.utc)
    
    # Get status
    status = service.get_current_status()
    
    # Verify status
    assert status["active_curve"] == "stock"
    assert status["curve_type"] == "preset"
    assert status["current_temp"] == temp
    assert status["target_speed"] == service._target_speed


def test_status_display_with_safety_override():
    """Test that status display reflects safety overrides."""
    # Create a mock hwmon interface
    mock_hwmon = Mock(spec=HwmonInterface)
    mock_hwmon.is_available.return_value = True
    mock_hwmon.read_current_pwm.return_value = 100
    
    # Create service
    service = FanControlService(hwmon_interface=mock_hwmon, config_path="/tmp/test_config.json")
    
    # Apply stock preset
    service.apply_preset("stock")
    
    # Test critical temperature (>= 95°C)
    critical_temp = 96.0
    service._current_temp = critical_temp
    calculated_speed = calculate_fan_speed(critical_temp, service.active_curve.points)
    service._target_speed = apply_safety_override(critical_temp, calculated_speed)
    service._last_update = datetime.now(timezone.utc)
    
    status = service.get_current_status()
    
    # Should be 100% due to critical override
    assert status["target_speed"] == 100
    assert status["current_temp"] == critical_temp
    
    # Test warning temperature (>= 90°C)
    warning_temp = 92.0
    service._current_temp = warning_temp
    calculated_speed = calculate_fan_speed(warning_temp, service.active_curve.points)
    service._target_speed = apply_safety_override(warning_temp, calculated_speed)
    
    status = service.get_current_status()
    
    # Should be at least 80% due to warning boost
    assert status["target_speed"] >= 80
    assert status["current_temp"] == warning_temp


def test_status_display_no_monitoring():
    """Test status display when monitoring is not active."""
    # Create a mock hwmon interface
    mock_hwmon = Mock(spec=HwmonInterface)
    mock_hwmon.is_available.return_value = True
    mock_hwmon.read_current_pwm.return_value = None
    
    # Create service
    service = FanControlService(hwmon_interface=mock_hwmon, config_path="/tmp/test_config.json")
    
    # Get status without starting monitoring
    status = service.get_current_status()
    
    # Should have None values for monitoring-related fields
    assert status["current_temp"] is None
    assert status["target_speed"] is None
    assert status["monitoring_active"] is False
    assert status["last_update"] is None
    
    # But should still have curve information
    assert status["active_curve"] == "stock"  # Default
    assert status["curve_type"] == "preset"
