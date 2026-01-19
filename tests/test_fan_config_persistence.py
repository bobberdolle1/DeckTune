"""Property tests for fan control configuration persistence.

Feature: fan-control-curves, Property 1: Configuration persistence round-trip
Validates: Requirements 1.5

Feature: fan-control-curves, Property 8: Custom curve serialization round-trip
Validates: Requirements 3.4, 3.5
"""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from backend.core.fan_control import (
    FanPoint,
    FanCurve,
    FanControlService,
    HwmonInterface,
    PRESETS
)


# Strategy for generating valid FanPoint instances
@st.composite
def fan_point_strategy(draw):
    """Generate valid FanPoint instances."""
    temp = draw(st.integers(min_value=0, max_value=120))
    speed = draw(st.integers(min_value=0, max_value=100))
    return FanPoint(temp=temp, speed=speed)


# Strategy for generating valid FanCurve instances
@st.composite
def fan_curve_strategy(draw):
    """Generate valid FanCurve instances with unique temperatures."""
    num_points = draw(st.integers(min_value=3, max_value=10))
    
    # Generate unique temperatures
    temps = draw(st.lists(
        st.integers(min_value=0, max_value=120),
        min_size=num_points,
        max_size=num_points,
        unique=True
    ))
    
    # Generate speeds for each temperature
    speeds = draw(st.lists(
        st.integers(min_value=0, max_value=100),
        min_size=num_points,
        max_size=num_points
    ))
    
    # Create FanPoint objects
    points = [FanPoint(temp=t, speed=s) for t, s in zip(temps, speeds)]
    
    # Generate a valid curve name
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
        min_size=1,
        max_size=20
    ))
    
    return FanCurve(name=name, points=points, is_preset=False)


# Strategy for preset names
preset_name_strategy = st.sampled_from(list(PRESETS.keys()))


class TestConfigurationPersistence:
    """Property 1: Configuration persistence round-trip
    
    For any preset selection, saving the configuration and then loading it
    should restore the same preset.
    
    Feature: fan-control-curves, Property 1: Configuration persistence round-trip
    **Validates: Requirements 1.5**
    """
    
    @given(preset_name=preset_name_strategy)
    @settings(max_examples=100)
    def test_preset_persistence_roundtrip(self, preset_name: str):
        """
        Property 1: Preset configuration persists across save/load cycles.
        
        Feature: fan-control-curves, Property 1: Configuration persistence round-trip
        **Validates: Requirements 1.5**
        """
        # Create temporary config file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "fan_control.json")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service and set preset
            service = FanControlService(hwmon, config_path=config_path)
            service.active_curve = PRESETS[preset_name]
            service.active_curve_type = "preset"
            
            # Save configuration
            save_result = service._save_config()
            assert save_result, f"Failed to save configuration for preset '{preset_name}'"
            
            # Create new service instance (simulates restart)
            service2 = FanControlService(hwmon, config_path=config_path)
            
            # Verify preset was restored
            assert service2.active_curve is not None, "Active curve should not be None"
            assert service2.active_curve.name == preset_name, \
                f"Expected preset '{preset_name}', got '{service2.active_curve.name}'"
            assert service2.active_curve_type == "preset", \
                f"Expected curve type 'preset', got '{service2.active_curve_type}'"
            
            # Verify curve points match
            original_points = PRESETS[preset_name].points
            loaded_points = service2.active_curve.points
            
            assert len(loaded_points) == len(original_points), \
                f"Point count mismatch: expected {len(original_points)}, got {len(loaded_points)}"
            
            for orig, loaded in zip(original_points, loaded_points):
                assert orig.temp == loaded.temp, \
                    f"Temperature mismatch: expected {orig.temp}, got {loaded.temp}"
                assert orig.speed == loaded.speed, \
                    f"Speed mismatch: expected {orig.speed}, got {loaded.speed}"
    
    def test_missing_config_defaults_to_stock(self):
        """Test that missing config file defaults to Stock preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.json")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service with non-existent config
            service = FanControlService(hwmon, config_path=config_path)
            
            # Should default to Stock preset
            assert service.active_curve is not None
            assert service.active_curve.name == "stock"
            assert service.active_curve_type == "preset"
    
    def test_corrupted_config_falls_back_to_stock(self):
        """Test that corrupted config file falls back to Stock preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "fan_control.json")
            
            # Write corrupted JSON
            with open(config_path, 'w') as f:
                f.write("{ invalid json }")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service with corrupted config
            service = FanControlService(hwmon, config_path=config_path)
            
            # Should fall back to Stock preset
            assert service.active_curve is not None
            assert service.active_curve.name == "stock"
            assert service.active_curve_type == "preset"


class TestCustomCurveSerialization:
    """Property 8: Custom curve serialization round-trip
    
    For any valid custom fan curve, serializing to JSON and then deserializing
    should produce an equivalent curve with identical points.
    
    Feature: fan-control-curves, Property 8: Custom curve serialization round-trip
    **Validates: Requirements 3.4, 3.5**
    """
    
    @given(curve=fan_curve_strategy())
    @settings(max_examples=100)
    def test_custom_curve_serialization_roundtrip(self, curve: FanCurve):
        """
        Property 8: Custom curves persist across save/load cycles.
        
        Feature: fan-control-curves, Property 8: Custom curve serialization round-trip
        **Validates: Requirements 3.4, 3.5**
        """
        # Create temporary config file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "fan_control.json")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service and add custom curve
            service = FanControlService(hwmon, config_path=config_path)
            service.custom_curves[curve.name] = curve
            service.active_curve = curve
            service.active_curve_type = "custom"
            
            # Save configuration
            save_result = service._save_config()
            assert save_result, f"Failed to save configuration for custom curve '{curve.name}'"
            
            # Create new service instance (simulates restart)
            service2 = FanControlService(hwmon, config_path=config_path)
            
            # Verify custom curve was restored
            assert curve.name in service2.custom_curves, \
                f"Custom curve '{curve.name}' not found in loaded configuration"
            
            loaded_curve = service2.custom_curves[curve.name]
            
            # Verify curve properties
            assert loaded_curve.name == curve.name, \
                f"Curve name mismatch: expected '{curve.name}', got '{loaded_curve.name}'"
            assert loaded_curve.is_preset == False, \
                "Custom curve should not be marked as preset"
            
            # Verify points match (after sorting, since FanCurve sorts on init)
            original_points = sorted(curve.points, key=lambda p: p.temp)
            loaded_points = sorted(loaded_curve.points, key=lambda p: p.temp)
            
            assert len(loaded_points) == len(original_points), \
                f"Point count mismatch: expected {len(original_points)}, got {len(loaded_points)}"
            
            for orig, loaded in zip(original_points, loaded_points):
                assert orig.temp == loaded.temp, \
                    f"Temperature mismatch: expected {orig.temp}, got {loaded.temp}"
                assert orig.speed == loaded.speed, \
                    f"Speed mismatch: expected {orig.speed}, got {loaded.speed}"
            
            # Verify active curve was restored
            assert service2.active_curve is not None
            assert service2.active_curve.name == curve.name
            assert service2.active_curve_type == "custom"
    
    @given(curves=st.lists(fan_curve_strategy(), min_size=1, max_size=5, unique_by=lambda c: c.name))
    @settings(max_examples=100)
    def test_multiple_custom_curves_persist(self, curves: list[FanCurve]):
        """Test that multiple custom curves persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "fan_control.json")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service and add multiple custom curves
            service = FanControlService(hwmon, config_path=config_path)
            for curve in curves:
                service.custom_curves[curve.name] = curve
            
            # Set first curve as active
            service.active_curve = curves[0]
            service.active_curve_type = "custom"
            
            # Save configuration
            save_result = service._save_config()
            assert save_result, "Failed to save configuration with multiple custom curves"
            
            # Create new service instance
            service2 = FanControlService(hwmon, config_path=config_path)
            
            # Verify all custom curves were restored
            assert len(service2.custom_curves) == len(curves), \
                f"Expected {len(curves)} custom curves, got {len(service2.custom_curves)}"
            
            for curve in curves:
                assert curve.name in service2.custom_curves, \
                    f"Custom curve '{curve.name}' not found in loaded configuration"
                
                loaded_curve = service2.custom_curves[curve.name]
                
                # Verify points match
                original_points = sorted(curve.points, key=lambda p: p.temp)
                loaded_points = sorted(loaded_curve.points, key=lambda p: p.temp)
                
                assert len(loaded_points) == len(original_points)
                for orig, loaded in zip(original_points, loaded_points):
                    assert orig.temp == loaded.temp
                    assert orig.speed == loaded.speed
    
    def test_config_file_permissions(self):
        """Test that config file is created with proper permissions (0600)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "fan_control.json")
            
            # Create mock hwmon interface
            hwmon = HwmonInterface(hwmon_path="/nonexistent")
            
            # Create service and save config
            service = FanControlService(hwmon, config_path=config_path)
            service._save_config()
            
            # Check file permissions (on Unix-like systems)
            if os.name != 'nt':  # Skip on Windows
                stat_info = os.stat(config_path)
                permissions = stat_info.st_mode & 0o777
                assert permissions == 0o600, \
                    f"Expected permissions 0600, got {oct(permissions)}"
