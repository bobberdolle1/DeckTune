"""Property test for settings menu state isolation.

Feature: ui-refactor-settings, Property 10: Settings menu state isolation
Validates: Requirements 9.4, 9.5

Tests that for any settings change made in the Settings Menu, the change
should persist even if the menu is closed without explicit save action.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.settings_manager import SettingsManager


# Strategy for generating setting changes
# Represents: (setting_key, initial_value, new_value)
setting_change_strategy = st.tuples(
    st.sampled_from(["expert_mode", "apply_on_startup", "game_only_mode"]),
    st.booleans(),  # initial_value
    st.booleans()   # new_value
)


@given(change=setting_change_strategy)
@hyp_settings(max_examples=100)
def test_settings_menu_state_isolation(change):
    """Property 10: Settings menu state isolation
    
    For any settings change made in the Settings Menu, the change SHALL
    persist even if the menu is closed without explicit save action.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    setting_key, initial_value, new_value = change
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Set initial value
        manager.save_setting(setting_key, initial_value)
        
        # Verify initial value is saved
        loaded_value = manager.get_setting(setting_key, None)
        assert loaded_value == initial_value, \
            f"Initial value not saved correctly: {loaded_value} != {initial_value}"
        
        # Simulate opening Settings Menu and changing a setting
        # In the UI, this happens when user toggles a setting
        # The change is saved immediately (auto-save)
        manager.save_setting(setting_key, new_value)
        
        # Simulate closing the Settings Menu without explicit save button
        # (Requirements 9.4, 9.5: changes auto-save, no explicit save needed)
        
        # Create a new manager instance to simulate fresh load
        # (as if the plugin was reloaded or settings were re-read)
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        
        # Verify the change persisted
        loaded_value = manager2.get_setting(setting_key, None)
        assert loaded_value == new_value, \
            f"Setting change did not persist: expected {new_value}, got {loaded_value}"


@given(
    changes=st.lists(
        st.tuples(
            st.sampled_from(["expert_mode", "apply_on_startup", "game_only_mode"]),
            st.booleans()
        ),
        min_size=1,
        max_size=5
    )
)
@hyp_settings(max_examples=100, deadline=None)
def test_multiple_settings_changes_persist(changes):
    """Test that multiple settings changes all persist without explicit save.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Track expected final state
        expected_state = {}
        
        # Apply all changes (simulating user toggling multiple settings)
        for setting_key, new_value in changes:
            manager.save_setting(setting_key, new_value)
            expected_state[setting_key] = new_value
        
        # Close menu (no explicit save action)
        # Create new manager to verify persistence
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        
        # Verify all changes persisted
        for setting_key, expected_value in expected_state.items():
            loaded_value = manager2.get_setting(setting_key, None)
            assert loaded_value == expected_value, \
                f"Setting '{setting_key}' did not persist: expected {expected_value}, got {loaded_value}"


@given(setting_key=st.sampled_from(["expert_mode", "apply_on_startup", "game_only_mode"]))
@hyp_settings(max_examples=100)
def test_settings_persist_across_menu_open_close(setting_key):
    """Test that settings persist across multiple menu open/close cycles.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Cycle 1: Open menu, change setting, close menu
        manager.save_setting(setting_key, True)
        
        # Verify persistence
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        assert manager2.get_setting(setting_key, None) is True
        
        # Cycle 2: Open menu again, change setting again, close menu
        manager3 = SettingsManager(storage_dir=Path(temp_dir))
        manager3.save_setting(setting_key, False)
        
        # Verify persistence again
        manager4 = SettingsManager(storage_dir=Path(temp_dir))
        assert manager4.get_setting(setting_key, None) is False


def test_settings_auto_save_no_explicit_button():
    """Test that settings auto-save without requiring explicit save button.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # User opens Settings Menu
        # User toggles Expert Mode
        manager.save_setting("expert_mode", True)
        
        # User closes menu by clicking backdrop or close button
        # No explicit "Save" button is clicked
        
        # Verify the change persisted
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager2.get_setting("expert_mode", False)
        assert loaded_value is True, \
            "Expert Mode should be saved automatically without explicit save button"


def test_settings_menu_close_preserves_changes():
    """Test that closing the menu preserves all changes made.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Initial state
        manager.save_setting("expert_mode", False)
        manager.save_setting("apply_on_startup", False)
        manager.save_setting("game_only_mode", False)
        
        # User opens Settings Menu and makes changes
        manager.save_setting("expert_mode", True)
        manager.save_setting("apply_on_startup", True)
        
        # User closes menu (backdrop click or close button)
        
        # Verify all changes persisted
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        assert manager2.get_setting("expert_mode", False) is True
        assert manager2.get_setting("apply_on_startup", False) is True
        assert manager2.get_setting("game_only_mode", False) is False


@given(
    initial_state=st.booleans(),
    intermediate_changes=st.lists(st.booleans(), min_size=1, max_size=5),
    final_value=st.booleans()
)
@hyp_settings(max_examples=100, deadline=None)
def test_settings_isolation_with_rapid_changes(initial_state, intermediate_changes, final_value):
    """Test that rapid setting changes all persist correctly.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Set initial state
        manager.save_setting("expert_mode", initial_state)
        
        # Make rapid changes (simulating user toggling quickly)
        for value in intermediate_changes:
            manager.save_setting("expert_mode", value)
        
        # Final change
        manager.save_setting("expert_mode", final_value)
        
        # Close menu
        
        # Verify final value persisted
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager2.get_setting("expert_mode", None)
        assert loaded_value == final_value, \
            f"Final value did not persist: expected {final_value}, got {loaded_value}"


def test_settings_menu_backdrop_dismiss_preserves_changes():
    """Test that dismissing menu via backdrop click preserves changes.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Initial state
        manager.save_setting("game_only_mode", False)
        
        # User opens Settings Menu
        # User toggles Game Only Mode
        manager.save_setting("game_only_mode", True)
        
        # User clicks backdrop to dismiss menu (no explicit save)
        
        # Verify change persisted
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager2.get_setting("game_only_mode", False)
        assert loaded_value is True, \
            "Setting should persist even when menu dismissed via backdrop"


def test_settings_menu_close_button_preserves_changes():
    """Test that closing menu via close button preserves changes.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Initial state
        manager.save_setting("apply_on_startup", False)
        
        # User opens Settings Menu
        # User toggles Apply on Startup
        manager.save_setting("apply_on_startup", True)
        
        # User clicks close button (no explicit save)
        
        # Verify change persisted
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_value = manager2.get_setting("apply_on_startup", False)
        assert loaded_value is True, \
            "Setting should persist even when menu closed via close button"


@given(
    setting_changes=st.dictionaries(
        keys=st.sampled_from(["expert_mode", "apply_on_startup", "game_only_mode"]),
        values=st.booleans(),
        min_size=1,
        max_size=3
    )
)
@hyp_settings(max_examples=100)
def test_all_settings_persist_independently(setting_changes):
    """Test that all settings persist independently without interference.
    
    Feature: ui-refactor-settings, Property 10: Settings menu state isolation
    Validates: Requirements 9.4, 9.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Apply all setting changes
        for key, value in setting_changes.items():
            manager.save_setting(key, value)
        
        # Close menu
        
        # Verify all settings persisted correctly
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        for key, expected_value in setting_changes.items():
            loaded_value = manager2.get_setting(key, None)
            assert loaded_value == expected_value, \
                f"Setting '{key}' did not persist: expected {expected_value}, got {loaded_value}"
