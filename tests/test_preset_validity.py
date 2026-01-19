"""Property tests for preset validity.

Feature: fan-control-curves, Property 14: Preset validity
Validates: Requirements 7.3

Tests that all predefined presets (Stock, Silent, Turbo) contain valid
curve points with temperatures in [0, 120] and speeds in [0, 100].
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.fan_control import PRESETS, FanPoint


@given(preset_name=st.sampled_from(list(PRESETS.keys())))
@hyp_settings(max_examples=100)
def test_preset_validity(preset_name):
    """Property 14: Preset validity
    
    For all predefined presets (Stock, Silent, Turbo), all curve points
    should pass validation (temperatures in [0, 120], speeds in [0, 100]).
    
    Feature: fan-control-curves, Property 14: Preset validity
    Validates: Requirements 7.3
    """
    preset = PRESETS[preset_name]
    
    # Verify preset exists and has points
    assert preset is not None
    assert len(preset.points) >= 3
    assert len(preset.points) <= 10
    
    # Verify all points have valid temperature and speed ranges
    for point in preset.points:
        assert isinstance(point, FanPoint)
        assert 0 <= point.temp <= 120, f"Preset {preset_name} has invalid temperature: {point.temp}"
        assert 0 <= point.speed <= 100, f"Preset {preset_name} has invalid speed: {point.speed}"
    
    # Verify preset is marked as preset
    assert preset.is_preset is True
    
    # Verify preset name matches
    assert preset.name == preset_name


def test_all_presets_exist():
    """Test that all expected presets are defined."""
    expected_presets = {"stock", "silent", "turbo"}
    assert set(PRESETS.keys()) == expected_presets


def test_stock_preset_definition():
    """Test Stock preset has correct definition."""
    stock = PRESETS["stock"]
    assert stock.name == "stock"
    assert len(stock.points) == 4
    
    # Verify specific points (sorted by temperature)
    points = sorted(stock.points, key=lambda p: p.temp)
    assert points[0].temp == 40 and points[0].speed == 0
    assert points[1].temp == 60 and points[1].speed == 40
    assert points[2].temp == 75 and points[2].speed == 70
    assert points[3].temp == 85 and points[3].speed == 100


def test_silent_preset_definition():
    """Test Silent preset has correct definition."""
    silent = PRESETS["silent"]
    assert silent.name == "silent"
    assert len(silent.points) == 4
    
    # Verify specific points (sorted by temperature)
    points = sorted(silent.points, key=lambda p: p.temp)
    assert points[0].temp == 50 and points[0].speed == 0
    assert points[1].temp == 70 and points[1].speed == 30
    assert points[2].temp == 85 and points[2].speed == 60
    assert points[3].temp == 95 and points[3].speed == 100


def test_turbo_preset_definition():
    """Test Turbo preset has correct definition."""
    turbo = PRESETS["turbo"]
    assert turbo.name == "turbo"
    assert len(turbo.points) == 4
    
    # Verify specific points (sorted by temperature)
    points = sorted(turbo.points, key=lambda p: p.temp)
    assert points[0].temp == 30 and points[0].speed == 20
    assert points[1].temp == 50 and points[1].speed == 60
    assert points[2].temp == 65 and points[2].speed == 80
    assert points[3].temp == 80 and points[3].speed == 100
