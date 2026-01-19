"""Property-based tests for settings context synchronization.

Feature: ui-refactor-settings, Property 5: Settings context synchronization
Validates: Requirements 10.2, 10.4

This module tests that settings updates through the context are properly
synchronized across all consumers within one render cycle.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from pathlib import Path
import tempfile
import asyncio

from backend.core.settings_manager import SettingsManager


# Strategy for generating valid setting keys
setting_keys = st.sampled_from([
    "expert_mode",
    "apply_on_startup",
    "game_only_mode",
    "last_active_profile"
])

# Strategy for generating valid setting values
setting_values = st.one_of(
    st.booleans(),  # For expert_mode, apply_on_startup, game_only_mode
    st.none(),      # For last_active_profile
    st.text(min_size=1, max_size=50)  # For last_active_profile
)


@given(
    key=setting_keys,
    value=setting_values
)
@hyp_settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_settings_update_synchronization(key, value):
    """
    **Feature: ui-refactor-settings, Property 5: Settings context synchronization**
    **Validates: Requirements 10.2, 10.4**
    
    Property: For any settings update through the settings manager,
    all subsequent reads should immediately reflect the updated value.
    
    This tests the synchronization guarantee that when a setting is updated,
    all consumers reading that setting will see the new value immediately.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save the setting
        success = manager.save_setting(key, value)
        assert success, f"Failed to save setting '{key}'"
        
        # Immediately read the setting back (simulating synchronization)
        loaded_value = manager.get_setting(key)
        
        # Verify the value is synchronized
        assert loaded_value == value, (
            f"Setting '{key}' not synchronized: expected {value}, got {loaded_value}"
        )
        
        # Simulate multiple consumers reading the same setting
        # (all should see the same value)
        for _ in range(5):
            consumer_value = manager.get_setting(key)
            assert consumer_value == value, (
                f"Consumer read inconsistent value for '{key}': "
                f"expected {value}, got {consumer_value}"
            )


@given(
    updates=st.lists(
        st.tuples(setting_keys, setting_values),
        min_size=1,
        max_size=10
    )
)
@hyp_settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_multiple_settings_synchronization(updates):
    """
    **Feature: ui-refactor-settings, Property 5: Settings context synchronization**
    **Validates: Requirements 10.2, 10.4**
    
    Property: For any sequence of settings updates, all settings should be
    synchronized and readable immediately after each update.
    
    This tests that multiple rapid updates maintain synchronization.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Track expected state
        expected_state = {}
        
        # Apply updates sequentially
        for key, value in updates:
            # Save the setting
            success = manager.save_setting(key, value)
            assert success, f"Failed to save setting '{key}'"
            
            # Update expected state
            expected_state[key] = value
            
            # Verify immediate synchronization
            loaded_value = manager.get_setting(key)
            assert loaded_value == value, (
                f"Setting '{key}' not synchronized after update: "
                f"expected {value}, got {loaded_value}"
            )
        
        # Verify all settings are still synchronized
        for key, expected_value in expected_state.items():
            actual_value = manager.get_setting(key)
            assert actual_value == expected_value, (
                f"Setting '{key}' lost synchronization: "
                f"expected {expected_value}, got {actual_value}"
            )


@given(
    initial_value=setting_values,
    updated_value=setting_values
)
@hyp_settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_settings_update_overwrites_previous(initial_value, updated_value):
    """
    **Feature: ui-refactor-settings, Property 5: Settings context synchronization**
    **Validates: Requirements 10.2, 10.4**
    
    Property: For any setting, updating it should overwrite the previous value
    and all consumers should see the new value, not the old one.
    
    This tests that updates properly replace old values.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        key = "expert_mode"
        
        # Save initial value
        success = manager.save_setting(key, initial_value)
        assert success, f"Failed to save initial setting '{key}'"
        
        # Verify initial value
        loaded_value = manager.get_setting(key)
        assert loaded_value == initial_value
        
        # Update to new value
        success = manager.save_setting(key, updated_value)
        assert success, f"Failed to update setting '{key}'"
        
        # Verify new value is synchronized (old value is gone)
        loaded_value = manager.get_setting(key)
        assert loaded_value == updated_value, (
            f"Setting '{key}' not synchronized after update: "
            f"expected {updated_value}, got {loaded_value}"
        )
        
        # Verify multiple reads all see the new value
        for _ in range(5):
            consumer_value = manager.get_setting(key)
            assert consumer_value == updated_value, (
                f"Consumer still seeing old value for '{key}': "
                f"expected {updated_value}, got {consumer_value}"
            )


@given(
    settings_dict=st.dictionaries(
        keys=setting_keys,
        values=setting_values,
        min_size=1,
        max_size=4
    )
)
@hyp_settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_load_all_settings_synchronization(settings_dict):
    """
    **Feature: ui-refactor-settings, Property 5: Settings context synchronization**
    **Validates: Requirements 10.2, 10.4**
    
    Property: For any set of settings, load_all_settings should return
    all settings that were previously saved, with synchronized values.
    
    This tests that bulk loading maintains synchronization.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save all settings
        for key, value in settings_dict.items():
            success = manager.save_setting(key, value)
            assert success, f"Failed to save setting '{key}'"
        
        # Load all settings
        loaded_settings = manager.load_all_settings()
        
        # Verify all settings are synchronized
        for key, expected_value in settings_dict.items():
            assert key in loaded_settings, f"Setting '{key}' missing from load_all_settings"
            actual_value = loaded_settings[key]
            assert actual_value == expected_value, (
                f"Setting '{key}' not synchronized in load_all_settings: "
                f"expected {expected_value}, got {actual_value}"
            )


@given(
    key=setting_keys,
    value=setting_values
)
@hyp_settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_settings_persistence_synchronization(key, value):
    """
    **Feature: ui-refactor-settings, Property 5: Settings context synchronization**
    **Validates: Requirements 10.2, 10.4**
    
    Property: For any setting saved by one manager instance,
    a new manager instance should immediately see the synchronized value.
    
    This tests that synchronization works across manager instances
    (simulating multiple components/contexts).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # First manager instance saves the setting
        manager1 = SettingsManager(storage_dir=Path(temp_dir))
        success = manager1.save_setting(key, value)
        assert success, f"Failed to save setting '{key}'"
        
        # Second manager instance (simulating another component/context)
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager2.get_setting(key)
        
        # Verify synchronization across instances
        assert loaded_value == value, (
            f"Setting '{key}' not synchronized across instances: "
            f"expected {value}, got {loaded_value}"
        )
        
        # Third manager instance (simulating yet another component)
        manager3 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager3.get_setting(key)
        
        # Verify still synchronized
        assert loaded_value == value, (
            f"Setting '{key}' not synchronized to third instance: "
            f"expected {value}, got {loaded_value}"
        )
