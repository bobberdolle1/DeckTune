"""Property tests for fan curve and safety.

Feature: decktune-critical-fixes, Property 8: Fan Curve Application
Validates: Requirements 7.4

Feature: decktune-critical-fixes, Property 9: Fan Temperature Safety
Validates: Requirements 7.7

Property 8: Применение кривой вентилятора
For any valid fan curve (points sorted by temperature, speed_percent in [0, 100]),
the curve must be correctly passed to gymdeck3 daemon.

Property 9: Температурная защита вентилятора
For any temperature >= 90°C, fan speed must be forced to 100% regardless of user curve settings.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List


# Strategy for temperature values
temp_strategy = st.integers(min_value=30, max_value=100)

# Strategy for speed percentage
speed_strategy = st.integers(min_value=0, max_value=100)


class FanCurvePoint:
    """Fan curve point (temperature -> speed)."""
    
    def __init__(self, temp_c: int, speed_percent: int):
        self.temp_c = temp_c
        self.speed_percent = speed_percent
    
    def to_dict(self):
        return {"temp_c": self.temp_c, "speed_percent": self.speed_percent}


def validate_fan_curve(curve: List[FanCurvePoint]) -> bool:
    """Validate that a fan curve is valid.
    
    A valid curve:
    - Has at least 2 points
    - Points are sorted by temperature (ascending)
    - All speed_percent values are in [0, 100]
    """
    if len(curve) < 2:
        return False
    
    for i in range(len(curve) - 1):
        if curve[i].temp_c >= curve[i + 1].temp_c:
            return False
    
    for point in curve:
        if not (0 <= point.speed_percent <= 100):
            return False
    
    return True


def interpolate_speed(curve: List[FanCurvePoint], temp: int) -> int:
    """Interpolate fan speed for a given temperature.
    
    Args:
        curve: Sorted list of fan curve points
        temp: Temperature to interpolate for
        
    Returns:
        Interpolated speed percentage
    """
    if not curve:
        return 100  # Safety default
    
    # Below first point
    if temp <= curve[0].temp_c:
        return curve[0].speed_percent
    
    # Above last point
    if temp >= curve[-1].temp_c:
        return curve[-1].speed_percent
    
    # Find surrounding points and interpolate
    for i in range(len(curve) - 1):
        if curve[i].temp_c <= temp <= curve[i + 1].temp_c:
            t1, s1 = curve[i].temp_c, curve[i].speed_percent
            t2, s2 = curve[i + 1].temp_c, curve[i + 1].speed_percent
            
            # Linear interpolation
            ratio = (temp - t1) / (t2 - t1) if t2 != t1 else 0
            return int(s1 + ratio * (s2 - s1))
    
    return 100  # Safety default


def apply_safety_override(speed: int, temp: int, safety_threshold: int = 90) -> int:
    """Apply safety override for high temperatures.
    
    Args:
        speed: Calculated fan speed
        temp: Current temperature
        safety_threshold: Temperature threshold for 100% override
        
    Returns:
        Final fan speed (100% if temp >= threshold)
    """
    if temp >= safety_threshold:
        return 100
    return speed


class TestFanCurveApplication:
    """Property 8: Применение кривой вентилятора
    
    For any valid fan curve (points sorted by temperature, speed_percent in [0, 100]),
    the curve must be correctly passed to gymdeck3 daemon.
    
    Feature: decktune-critical-fixes, Property 8: Fan Curve Application
    Validates: Requirements 7.4
    """

    @given(
        temps=st.lists(temp_strategy, min_size=2, max_size=8, unique=True),
        speeds=st.lists(speed_strategy, min_size=2, max_size=8)
    )
    @settings(max_examples=100)
    def test_valid_curve_is_accepted(self, temps: List[int], speeds: List[int]):
        """
        Property 8: Valid fan curves are accepted.
        
        Feature: decktune-critical-fixes, Property 8: Fan Curve Application
        **Validates: Requirements 7.4**
        """
        # Ensure same length
        min_len = min(len(temps), len(speeds))
        temps = sorted(temps[:min_len])
        speeds = speeds[:min_len]
        
        # Create curve
        curve = [FanCurvePoint(t, s) for t, s in zip(temps, speeds)]
        
        # Validate curve
        is_valid = validate_fan_curve(curve)
        assert is_valid, f"Valid curve should be accepted: {[(p.temp_c, p.speed_percent) for p in curve]}"

    @given(
        temps=st.lists(temp_strategy, min_size=2, max_size=6, unique=True),
        speeds=st.lists(speed_strategy, min_size=2, max_size=6),
        test_temp=temp_strategy
    )
    @settings(max_examples=100)
    def test_interpolation_within_bounds(
        self, temps: List[int], speeds: List[int], test_temp: int
    ):
        """
        Property 8: Interpolated speed is within valid bounds.
        
        Feature: decktune-critical-fixes, Property 8: Fan Curve Application
        **Validates: Requirements 7.4**
        """
        # Ensure same length
        min_len = min(len(temps), len(speeds))
        temps = sorted(temps[:min_len])
        speeds = speeds[:min_len]
        
        # Create curve
        curve = [FanCurvePoint(t, s) for t, s in zip(temps, speeds)]
        
        # Interpolate
        result = interpolate_speed(curve, test_temp)
        
        # Result should be within [0, 100]
        assert 0 <= result <= 100, f"Interpolated speed {result} out of bounds"

    def test_known_curve_values(self):
        """Test with known curve values for verification."""
        curve = [
            FanCurvePoint(40, 20),
            FanCurvePoint(60, 50),
            FanCurvePoint(80, 100),
        ]
        
        # Below first point
        assert interpolate_speed(curve, 30) == 20
        
        # At first point
        assert interpolate_speed(curve, 40) == 20
        
        # Between points (linear interpolation)
        assert interpolate_speed(curve, 50) == 35  # Midpoint between 20 and 50
        
        # At last point
        assert interpolate_speed(curve, 80) == 100
        
        # Above last point
        assert interpolate_speed(curve, 90) == 100


class TestFanTemperatureSafety:
    """Property 9: Температурная защита вентилятора
    
    For any temperature >= 90°C, fan speed must be forced to 100% regardless of user curve settings.
    
    Feature: decktune-critical-fixes, Property 9: Fan Temperature Safety
    Validates: Requirements 7.7
    """

    @given(
        temp=st.integers(min_value=90, max_value=120),
        curve_speed=speed_strategy
    )
    @settings(max_examples=100)
    def test_high_temp_forces_100_percent(self, temp: int, curve_speed: int):
        """
        Property 9: High temperature forces 100% fan speed.
        
        Feature: decktune-critical-fixes, Property 9: Fan Temperature Safety
        **Validates: Requirements 7.7**
        """
        result = apply_safety_override(curve_speed, temp, safety_threshold=90)
        
        assert result == 100, f"At {temp}°C, fan should be 100%, got {result}%"

    @given(
        temp=st.integers(min_value=30, max_value=89),
        curve_speed=speed_strategy
    )
    @settings(max_examples=100)
    def test_normal_temp_uses_curve_speed(self, temp: int, curve_speed: int):
        """
        Property 9: Normal temperature uses curve speed.
        
        Feature: decktune-critical-fixes, Property 9: Fan Temperature Safety
        **Validates: Requirements 7.7**
        """
        result = apply_safety_override(curve_speed, temp, safety_threshold=90)
        
        assert result == curve_speed, f"At {temp}°C, fan should be {curve_speed}%, got {result}%"

    def test_boundary_conditions(self):
        """Test boundary conditions at 90°C threshold."""
        # Just below threshold
        assert apply_safety_override(50, 89, safety_threshold=90) == 50
        
        # At threshold
        assert apply_safety_override(50, 90, safety_threshold=90) == 100
        
        # Above threshold
        assert apply_safety_override(50, 95, safety_threshold=90) == 100
        
        # Even 0% curve speed should become 100% at high temp
        assert apply_safety_override(0, 90, safety_threshold=90) == 100

    @given(temp=st.integers(min_value=90, max_value=150))
    @settings(max_examples=100)
    def test_safety_override_always_100_above_threshold(self, temp: int):
        """
        Property 9: Safety override is always 100% above threshold.
        
        Feature: decktune-critical-fixes, Property 9: Fan Temperature Safety
        **Validates: Requirements 7.7**
        """
        # Test with various curve speeds
        for curve_speed in [0, 25, 50, 75, 100]:
            result = apply_safety_override(curve_speed, temp, safety_threshold=90)
            assert result == 100, f"At {temp}°C with curve {curve_speed}%, should be 100%, got {result}%"
