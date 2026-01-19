"""Property tests for HwmonInterface hardware write consistency.

Feature: fan-control-curves, Property 10: Hardware write consistency
Validates: Requirements 5.1

Tests that HwmonInterface correctly converts speed percentages to PWM values.
"""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import HwmonInterface


@given(speed_percent=st.integers(min_value=0, max_value=100))
@hyp_settings(max_examples=100)
def test_hardware_write_consistency(speed_percent):
    """Property 10: Hardware write consistency
    
    For any valid fan speed percentage, calling the apply function should
    result in the corresponding PWM value being written to the hwmon interface.
    
    The conversion formula is: pwm_value = round(speed_percent * 255 / 100)
    
    Feature: fan-control-curves, Property 10: Hardware write consistency
    Validates: Requirements 5.1
    """
    # Create a temporary directory structure mimicking hwmon
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        # Create mock PWM control file
        pwm_file = os.path.join(hwmon_dir, "pwm1")
        with open(pwm_file, 'w') as f:
            f.write("128")  # Initial value
        
        # Create mock temperature sensor file
        temp_file = os.path.join(hwmon_dir, "temp1_input")
        with open(temp_file, 'w') as f:
            f.write("50000")  # 50°C in millidegrees
        
        # Create HwmonInterface with mock directory
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        
        # Manually set paths since discovery might not work in test environment
        hwmon.pwm_control_path = pwm_file
        hwmon.temp_sensor_path = temp_file
        
        # Write the speed percentage
        result = hwmon.write_pwm(speed_percent)
        
        # Verify write succeeded
        assert result is True, f"Failed to write speed {speed_percent}%"
        
        # Read back the PWM value
        with open(pwm_file, 'r') as f:
            written_pwm = int(f.read().strip())
        
        # Calculate expected PWM value
        expected_pwm = int(round(speed_percent * 255 / 100))
        
        # Verify the written value matches expected conversion
        assert written_pwm == expected_pwm, \
            f"Speed {speed_percent}% should write PWM {expected_pwm}, but wrote {written_pwm}"


def test_hwmon_write_pwm_basic():
    """Test basic PWM write functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        pwm_file = os.path.join(hwmon_dir, "pwm1")
        with open(pwm_file, 'w') as f:
            f.write("0")
        
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        hwmon.pwm_control_path = pwm_file
        
        # Test 0%
        assert hwmon.write_pwm(0) is True
        with open(pwm_file, 'r') as f:
            assert int(f.read().strip()) == 0
        
        # Test 50%
        assert hwmon.write_pwm(50) is True
        with open(pwm_file, 'r') as f:
            assert int(f.read().strip()) == 128  # round(50 * 255 / 100)
        
        # Test 100%
        assert hwmon.write_pwm(100) is True
        with open(pwm_file, 'r') as f:
            assert int(f.read().strip()) == 255


def test_hwmon_write_pwm_invalid_range():
    """Test PWM write rejects invalid percentages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        pwm_file = os.path.join(hwmon_dir, "pwm1")
        with open(pwm_file, 'w') as f:
            f.write("128")
        
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        hwmon.pwm_control_path = pwm_file
        
        # Test invalid values
        assert hwmon.write_pwm(-1) is False
        assert hwmon.write_pwm(101) is False
        assert hwmon.write_pwm(200) is False


def test_hwmon_write_pwm_no_path():
    """Test PWM write fails gracefully when path not set."""
    hwmon = HwmonInterface(hwmon_path="/nonexistent")
    assert hwmon.write_pwm(50) is False


def test_hwmon_read_temperature():
    """Test temperature reading from hwmon."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        temp_file = os.path.join(hwmon_dir, "temp1_input")
        with open(temp_file, 'w') as f:
            f.write("65000")  # 65°C in millidegrees
        
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        hwmon.temp_sensor_path = temp_file
        
        temp = hwmon.read_temperature()
        assert temp == 65.0


def test_hwmon_read_temperature_no_path():
    """Test temperature reading fails gracefully when path not set."""
    hwmon = HwmonInterface(hwmon_path="/nonexistent")
    assert hwmon.read_temperature() is None


def test_hwmon_read_current_pwm():
    """Test reading current PWM value."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        pwm_file = os.path.join(hwmon_dir, "pwm1")
        with open(pwm_file, 'w') as f:
            f.write("128")  # 50% in PWM
        
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        hwmon.pwm_control_path = pwm_file
        
        speed = hwmon.read_current_pwm()
        assert speed == 50  # round(128 * 100 / 255)


def test_hwmon_read_current_pwm_no_path():
    """Test reading PWM fails gracefully when path not set."""
    hwmon = HwmonInterface(hwmon_path="/nonexistent")
    assert hwmon.read_current_pwm() is None


def test_hwmon_is_available():
    """Test is_available method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hwmon_dir = os.path.join(tmpdir, "hwmon0")
        os.makedirs(hwmon_dir)
        
        pwm_file = os.path.join(hwmon_dir, "pwm1")
        temp_file = os.path.join(hwmon_dir, "temp1_input")
        
        with open(pwm_file, 'w') as f:
            f.write("128")
        with open(temp_file, 'w') as f:
            f.write("50000")
        
        hwmon = HwmonInterface(hwmon_path=tmpdir)
        hwmon.pwm_control_path = pwm_file
        hwmon.temp_sensor_path = temp_file
        
        assert hwmon.is_available() is True
        
        # Test with missing PWM
        hwmon.pwm_control_path = None
        assert hwmon.is_available() is False
        
        # Test with missing temp sensor
        hwmon.pwm_control_path = pwm_file
        hwmon.temp_sensor_path = None
        assert hwmon.is_available() is False


def test_hwmon_discovery_no_devices():
    """Test device discovery with no hwmon devices."""
    hwmon = HwmonInterface(hwmon_path="/nonexistent")
    assert hwmon.temp_sensor_path is None
    assert hwmon.pwm_control_path is None
    assert hwmon.is_available() is False
