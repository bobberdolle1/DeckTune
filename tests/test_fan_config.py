"""Tests for fan control configuration.

Feature: Fan Control Integration (Phase 4)
"""

import pytest
from backend.dynamic.config import (
    FanConfig,
    FanCurvePoint,
    FanStatus,
    DynamicConfig,
    FAN_TEMP_MIN,
    FAN_TEMP_MAX,
    FAN_SPEED_MIN,
    FAN_SPEED_MAX,
)


class TestFanCurvePoint:
    """Tests for FanCurvePoint dataclass."""

    def test_default_values(self):
        """Test default values."""
        point = FanCurvePoint()
        assert point.temp_c == 50
        assert point.speed_percent == 50

    def test_custom_values(self):
        """Test custom values."""
        point = FanCurvePoint(temp_c=60, speed_percent=75)
        assert point.temp_c == 60
        assert point.speed_percent == 75

    def test_validate_valid_point(self):
        """Test validation of valid point."""
        point = FanCurvePoint(temp_c=50, speed_percent=50)
        errors = point.validate()
        assert errors == []

    def test_validate_invalid_temp(self):
        """Test validation rejects invalid temperature."""
        point = FanCurvePoint(temp_c=150, speed_percent=50)
        errors = point.validate()
        assert len(errors) == 1
        assert "temp_c" in errors[0]

    def test_validate_invalid_speed(self):
        """Test validation rejects invalid speed."""
        point = FanCurvePoint(temp_c=50, speed_percent=150)
        errors = point.validate()
        assert len(errors) == 1
        assert "speed_percent" in errors[0]

    def test_to_dict(self):
        """Test serialization to dict."""
        point = FanCurvePoint(temp_c=60, speed_percent=75)
        d = point.to_dict()
        assert d == {"temp_c": 60, "speed_percent": 75}

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {"temp_c": 60, "speed_percent": 75}
        point = FanCurvePoint.from_dict(d)
        assert point.temp_c == 60
        assert point.speed_percent == 75


class TestFanConfig:
    """Tests for FanConfig dataclass."""

    def test_default_values(self):
        """Test default values."""
        config = FanConfig()
        assert config.enabled is False
        assert config.mode == "default"
        assert len(config.curve) == 6
        assert config.zero_rpm_enabled is False
        assert config.hysteresis_temp == 2

    def test_validate_valid_config(self):
        """Test validation of valid config."""
        config = FanConfig()
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_mode(self):
        """Test validation rejects invalid mode."""
        config = FanConfig(mode="invalid")
        errors = config.validate()
        assert len(errors) == 1
        assert "mode" in errors[0]

    def test_validate_invalid_hysteresis(self):
        """Test validation rejects invalid hysteresis."""
        config = FanConfig(hysteresis_temp=20)
        errors = config.validate()
        assert len(errors) == 1
        assert "hysteresis_temp" in errors[0]

    def test_validate_custom_mode_needs_curve(self):
        """Test custom mode requires at least 2 curve points."""
        config = FanConfig(mode="custom", curve=[FanCurvePoint(50, 50)])
        errors = config.validate()
        assert len(errors) == 1
        assert "at least 2 points" in errors[0]

    def test_validate_curve_increasing_temps(self):
        """Test curve temperatures must be strictly increasing."""
        config = FanConfig(
            mode="custom",
            curve=[
                FanCurvePoint(60, 50),
                FanCurvePoint(50, 75),  # Not increasing
            ]
        )
        errors = config.validate()
        assert any("strictly increasing" in e for e in errors)

    def test_to_dict(self):
        """Test serialization to dict."""
        config = FanConfig(enabled=True, mode="custom")
        d = config.to_dict()
        assert d["enabled"] is True
        assert d["mode"] == "custom"
        assert "curve" in d
        assert "zero_rpm_enabled" in d
        assert "hysteresis_temp" in d

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {
            "enabled": True,
            "mode": "custom",
            "curve": [{"temp_c": 40, "speed_percent": 20}],
            "zero_rpm_enabled": True,
            "hysteresis_temp": 3,
        }
        config = FanConfig.from_dict(d)
        assert config.enabled is True
        assert config.mode == "custom"
        assert config.zero_rpm_enabled is True
        assert config.hysteresis_temp == 3


class TestFanStatus:
    """Tests for FanStatus dataclass."""

    def test_default_values(self):
        """Test default values."""
        status = FanStatus()
        assert status.temp_c == 0
        assert status.pwm == 0
        assert status.speed_percent == 0
        assert status.rpm is None
        assert status.mode == "default"
        assert status.safety_override is False

    def test_to_dict(self):
        """Test serialization to dict."""
        status = FanStatus(temp_c=65, pwm=128, speed_percent=50, rpm=3000)
        d = status.to_dict()
        assert d["temp_c"] == 65
        assert d["pwm"] == 128
        assert d["speed_percent"] == 50
        assert d["rpm"] == 3000

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {"temp_c": 65, "pwm": 128, "speed_percent": 50, "rpm": 3000}
        status = FanStatus.from_dict(d)
        assert status.temp_c == 65
        assert status.pwm == 128
        assert status.speed_percent == 50
        assert status.rpm == 3000


class TestDynamicConfigFanIntegration:
    """Tests for fan config integration in DynamicConfig."""

    def test_default_fan_config(self):
        """Test DynamicConfig has default fan config."""
        config = DynamicConfig()
        assert config.fan_config is not None
        assert isinstance(config.fan_config, FanConfig)
        assert config.fan_config.enabled is False

    def test_validate_includes_fan_config(self):
        """Test DynamicConfig validation includes fan config."""
        config = DynamicConfig()
        config.fan_config.mode = "invalid"
        errors = config.validate()
        assert any("fan_config" in e for e in errors)

    def test_to_dict_includes_fan_config(self):
        """Test DynamicConfig.to_dict includes fan_config."""
        config = DynamicConfig()
        config.fan_config.enabled = True
        d = config.to_dict()
        assert "fan_config" in d
        assert d["fan_config"]["enabled"] is True

    def test_from_dict_parses_fan_config(self):
        """Test DynamicConfig.from_dict parses fan_config."""
        d = {
            "strategy": "balanced",
            "fan_config": {
                "enabled": True,
                "mode": "custom",
            }
        }
        config = DynamicConfig.from_dict(d)
        assert config.fan_config.enabled is True
        assert config.fan_config.mode == "custom"
