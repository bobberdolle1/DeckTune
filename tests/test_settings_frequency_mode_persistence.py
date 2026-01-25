"""
Property-based tests for frequency mode persistence in settings manager.

Feature: frequency-based-wizard, Property 7: Mode switching state consistency
Validates: Requirements 10.1, 10.2, 10.4, 10.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import tempfile
import shutil
import json
import time
from contextlib import contextmanager

from backend.core.settings_manager import SettingsManager


# Strategy for generating valid frequency mode states
frequency_mode_states = st.booleans()


# Strategy for generating valid wizard configs
wizard_config_strategy = st.fixed_dictionaries({
    "freq_start": st.integers(min_value=400, max_value=3500),
    "freq_end": st.integers(min_value=400, max_value=3500),
    "freq_step": st.integers(min_value=50, max_value=500),
    "test_duration": st.integers(min_value=10, max_value=120),
    "voltage_start": st.integers(min_value=-100, max_value=0),
    "voltage_step": st.integers(min_value=1, max_value=10),
    "safety_margin": st.integers(min_value=0, max_value=20),
    "parallel_cores": st.booleans(),
    "adaptive_step": st.booleans()
}).filter(lambda cfg: cfg["freq_end"] > cfg["freq_start"])


# Strategy for generating valid frequency curves
frequency_point_strategy = st.fixed_dictionaries({
    "frequency_mhz": st.integers(min_value=400, max_value=3500),
    "voltage_mv": st.integers(min_value=-100, max_value=0),
    "stable": st.booleans(),
    "test_duration": st.integers(min_value=10, max_value=120),
    "timestamp": st.floats(min_value=1000000000, max_value=2000000000)
})


def generate_sorted_frequency_points(points):
    """Sort frequency points by frequency to ensure valid curve."""
    return sorted(points, key=lambda p: p["frequency_mhz"])


frequency_curve_strategy = st.builds(
    lambda core_id, points, created_at, wizard_config: {
        "core_id": core_id,
        "points": generate_sorted_frequency_points(points),
        "created_at": created_at,
        "wizard_config": wizard_config
    },
    core_id=st.integers(min_value=0, max_value=15),
    points=st.lists(frequency_point_strategy, min_size=2, max_size=10, unique_by=lambda p: p["frequency_mhz"]),
    created_at=st.floats(min_value=1000000000, max_value=2000000000),
    wizard_config=wizard_config_strategy
)


@contextmanager
def temp_settings_dir():
    """Context manager for temporary settings directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@given(mode_enabled=frequency_mode_states)
@settings(max_examples=100, deadline=None)
def test_frequency_mode_persistence_round_trip(mode_enabled):
    """
    Property 7: Mode switching state consistency
    
    For any frequency mode state (enabled/disabled), saving the mode preference
    and then loading it should return the same state.
    
    Validates: Requirements 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager with temp directory
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save frequency mode state
        success = manager.save_setting("frequency_mode_enabled", mode_enabled)
        assert success, "Failed to save frequency mode state"
        
        # Create new manager instance to force reload from disk
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Retrieve frequency mode state
        retrieved_mode = manager2.get_setting("frequency_mode_enabled", None)
        
        # Verify state matches
        assert retrieved_mode == mode_enabled, \
            f"Mode persistence failed: saved {mode_enabled}, retrieved {retrieved_mode}"


@given(
    initial_mode=frequency_mode_states,
    switched_mode=frequency_mode_states
)
@settings(max_examples=100, deadline=None)
def test_mode_switching_preserves_state(initial_mode, switched_mode):
    """
    Property 7: Mode switching state consistency
    
    For any sequence of mode switches, the final persisted state should match
    the last mode that was set.
    
    Validates: Requirements 10.1, 10.2, 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Set initial mode
        success1 = manager.save_setting("frequency_mode_enabled", initial_mode)
        assert success1, "Failed to save initial mode"
        
        # Switch to new mode
        success2 = manager.save_setting("frequency_mode_enabled", switched_mode)
        assert success2, "Failed to save switched mode"
        
        # Create new manager to verify persistence
        manager2 = SettingsManager(storage_dir=temp_dir)
        final_mode = manager2.get_setting("frequency_mode_enabled", None)
        
        # Final state should match the last mode set
        assert final_mode == switched_mode, \
            f"Mode switching failed: set {switched_mode}, retrieved {final_mode}"


@given(wizard_config=wizard_config_strategy)
@settings(max_examples=100, deadline=None)
def test_wizard_config_persistence(wizard_config):
    """
    Property 7: Mode switching state consistency (extended to wizard config)
    
    For any valid wizard configuration, saving and loading should preserve
    all configuration parameters.
    
    Validates: Requirements 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save wizard config
        success = manager.save_setting("last_wizard_config", wizard_config)
        assert success, "Failed to save wizard config"
        
        # Create new manager to force reload
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Retrieve wizard config
        retrieved_config = manager2.get_setting("last_wizard_config", None)
        
        # Verify all fields match
        assert retrieved_config == wizard_config, \
            f"Wizard config persistence failed: saved {wizard_config}, retrieved {retrieved_config}"


@given(curve=frequency_curve_strategy)
@settings(max_examples=100, deadline=None)
def test_frequency_curve_persistence(curve):
    """
    Property 7: Mode switching state consistency (extended to frequency curves)
    
    For any valid frequency curve, saving and loading should preserve
    all curve data including points, metadata, and configuration.
    
    Validates: Requirements 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save frequency curve
        core_id = curve["core_id"]
        success = manager.save_frequency_curve(core_id, curve)
        assert success, f"Failed to save frequency curve for core {core_id}"
        
        # Create new manager to force reload
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Retrieve frequency curve
        retrieved_curve = manager2.get_frequency_curve(core_id)
        
        # Verify curve matches
        assert retrieved_curve is not None, f"Failed to retrieve curve for core {core_id}"
        assert retrieved_curve == curve, \
            f"Curve persistence failed for core {core_id}: saved {curve}, retrieved {retrieved_curve}"


@given(
    curves=st.lists(frequency_curve_strategy, min_size=1, max_size=8, unique_by=lambda c: c["core_id"])
)
@settings(max_examples=100, deadline=None)
def test_multiple_curves_persistence(curves):
    """
    Property 7: Mode switching state consistency (extended to multiple curves)
    
    For any set of frequency curves for different cores, saving and loading
    should preserve all curves independently.
    
    Validates: Requirements 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save all curves
        for curve in curves:
            core_id = curve["core_id"]
            success = manager.save_frequency_curve(core_id, curve)
            assert success, f"Failed to save curve for core {core_id}"
        
        # Create new manager to force reload
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Retrieve and verify all curves
        all_curves = manager2.get_all_frequency_curves()
        
        for curve in curves:
            core_id = curve["core_id"]
            core_key = str(core_id)
            
            assert core_key in all_curves, f"Curve for core {core_id} not found in storage"
            
            retrieved_curve = all_curves[core_key]
            assert retrieved_curve == curve, \
                f"Curve mismatch for core {core_id}: saved {curve}, retrieved {retrieved_curve}"


@given(
    mode=frequency_mode_states,
    wizard_config=wizard_config_strategy,
    curve=frequency_curve_strategy
)
@settings(max_examples=100, deadline=None)
def test_combined_frequency_settings_persistence(mode, wizard_config, curve):
    """
    Property 7: Mode switching state consistency (comprehensive test)
    
    For any combination of frequency mode state, wizard config, and frequency curve,
    saving all settings and loading should preserve all data correctly.
    
    Validates: Requirements 10.1, 10.2, 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save all frequency-related settings
        success1 = manager.save_setting("frequency_mode_enabled", mode)
        success2 = manager.save_setting("last_wizard_config", wizard_config)
        success3 = manager.save_frequency_curve(curve["core_id"], curve)
        
        assert success1, "Failed to save frequency mode"
        assert success2, "Failed to save wizard config"
        assert success3, "Failed to save frequency curve"
        
        # Create new manager to force reload
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Retrieve all settings
        retrieved_mode = manager2.get_setting("frequency_mode_enabled", None)
        retrieved_config = manager2.get_setting("last_wizard_config", None)
        retrieved_curve = manager2.get_frequency_curve(curve["core_id"])
        
        # Verify all settings match
        assert retrieved_mode == mode, \
            f"Mode mismatch: saved {mode}, retrieved {retrieved_mode}"
        assert retrieved_config == wizard_config, \
            f"Config mismatch: saved {wizard_config}, retrieved {retrieved_config}"
        assert retrieved_curve == curve, \
            f"Curve mismatch: saved {curve}, retrieved {retrieved_curve}"


@given(curve=frequency_curve_strategy)
@settings(max_examples=100, deadline=None)
def test_curve_deletion_persistence(curve):
    """
    Property 7: Mode switching state consistency (deletion test)
    
    For any frequency curve, after saving and then deleting it, the curve
    should not be retrievable from storage.
    
    Validates: Requirements 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Save curve
        core_id = curve["core_id"]
        success1 = manager.save_frequency_curve(core_id, curve)
        assert success1, f"Failed to save curve for core {core_id}"
        
        # Verify curve exists
        retrieved_before = manager.get_frequency_curve(core_id)
        assert retrieved_before is not None, "Curve should exist after save"
        
        # Delete curve
        success2 = manager.delete_frequency_curve(core_id)
        assert success2, f"Failed to delete curve for core {core_id}"
        
        # Create new manager to force reload
        manager2 = SettingsManager(storage_dir=temp_dir)
        
        # Verify curve is gone
        retrieved_after = manager2.get_frequency_curve(core_id)
        assert retrieved_after is None, \
            f"Curve for core {core_id} should not exist after deletion, but found: {retrieved_after}"


def test_v3_to_v4_migration_adds_frequency_fields():
    """
    Test that v3 to v4 migration adds frequency-based mode fields.
    
    Validates: Requirements 7.2, 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create a v3 settings file manually
        settings_file = temp_dir / "settings.json"
        v3_settings = {
            "_settings_version": 3,
            "expert_mode": True,
            "apply_on_startup": False
        }
        
        with open(settings_file, 'w') as f:
            json.dump(v3_settings, f)
        
        # Create settings manager (should trigger migration)
        manager = SettingsManager(storage_dir=temp_dir)
        
        # Verify migration added frequency fields
        frequency_mode = manager.get_setting("frequency_mode_enabled", None)
        frequency_curves = manager.get_setting("frequency_curves", None)
        wizard_config = manager.get_setting("last_wizard_config", None)
        version = manager.get_setting("_settings_version", None)
        
        assert frequency_mode is not None, "Migration should add frequency_mode_enabled"
        assert frequency_mode == False, "Default frequency mode should be False"
        
        assert frequency_curves is not None, "Migration should add frequency_curves"
        assert frequency_curves == {}, "Default frequency_curves should be empty dict"
        
        assert wizard_config is not None, "Migration should add last_wizard_config"
        assert "freq_start" in wizard_config, "Wizard config should have freq_start"
        assert "freq_end" in wizard_config, "Wizard config should have freq_end"
        
        assert version == 4, "Version should be updated to 4"
        
        # Verify old settings are preserved
        expert_mode = manager.get_setting("expert_mode", None)
        apply_on_startup = manager.get_setting("apply_on_startup", None)
        
        assert expert_mode == True, "Migration should preserve expert_mode"
        assert apply_on_startup == False, "Migration should preserve apply_on_startup"


def test_migration_idempotent():
    """
    Test that running migration multiple times doesn't corrupt data.
    
    Validates: Requirements 7.2, 10.4, 10.5
    """
    with temp_settings_dir() as temp_dir:
        # Create initial v3 settings
        settings_file = temp_dir / "settings.json"
        v3_settings = {
            "_settings_version": 3,
            "expert_mode": True
        }
        
        with open(settings_file, 'w') as f:
            json.dump(v3_settings, f)
        
        # First migration
        manager1 = SettingsManager(storage_dir=temp_dir)
        mode1 = manager1.get_setting("frequency_mode_enabled", None)
        
        # Second migration (should be no-op)
        manager2 = SettingsManager(storage_dir=temp_dir)
        mode2 = manager2.get_setting("frequency_mode_enabled", None)
        
        # Third migration (should be no-op)
        manager3 = SettingsManager(storage_dir=temp_dir)
        mode3 = manager3.get_setting("frequency_mode_enabled", None)
        
        # All should have same value
        assert mode1 == mode2 == mode3 == False, \
            "Multiple migrations should produce consistent results"
