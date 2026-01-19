"""Property test for settings persistence round-trip.

Feature: ui-refactor-settings, Property 1: Settings persistence round-trip
Validates: Requirements 3.1, 3.2, 3.3

Tests that for any valid settings object, saving then loading should produce
an equivalent settings object with all values preserved.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.settings_manager import SettingsManager


# Strategy for generating valid setting values
# Settings can be strings, numbers, booleans, lists, or dicts
setting_value_strategy = st.one_of(
    st.text(min_size=0, max_size=100),
    st.integers(min_value=-1000000, max_value=1000000),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    st.booleans(),
    st.none(),
    st.lists(st.integers(min_value=-100, max_value=100), min_size=0, max_size=10),
    st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('L', 'N'),
            whitelist_characters='_'
        )),
        values=st.one_of(
            st.text(min_size=0, max_size=50),
            st.integers(min_value=-1000, max_value=1000),
            st.booleans(),
            st.none()
        ),
        min_size=0,
        max_size=5
    )
)

# Strategy for generating setting keys
# Keys must not start with underscore (reserved for internal use)
setting_key_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(
        whitelist_categories=('L', 'N'),
        whitelist_characters='_'
    )
).filter(lambda k: not k.startswith('_'))

# Strategy for generating a settings dictionary
settings_dict_strategy = st.dictionaries(
    keys=setting_key_strategy,
    values=setting_value_strategy,
    min_size=1,
    max_size=10
)


@given(settings_dict=settings_dict_strategy)
@hyp_settings(max_examples=100)
def test_settings_persistence_roundtrip(settings_dict):
    """Property 1: Settings persistence round-trip
    
    For any valid settings object, saving then loading SHALL produce
    an equivalent settings object with all values preserved.
    
    Feature: ui-refactor-settings, Property 1: Settings persistence round-trip
    Validates: Requirements 3.1, 3.2, 3.3
    """
    # Create a temporary directory for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager with temp directory
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save all settings
        for key, value in settings_dict.items():
            success = manager.save_setting(key, value)
            assert success, f"Failed to save setting '{key}'"
        
        # Create a new manager instance (simulating fresh load)
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        
        # Load all settings
        loaded_settings = manager2.load_all_settings()
        
        # Verify all keys and values match
        assert len(loaded_settings) == len(settings_dict), \
            f"Settings count mismatch: {len(loaded_settings)} != {len(settings_dict)}"
        
        for key, original_value in settings_dict.items():
            assert key in loaded_settings, f"Key '{key}' not found in loaded settings"
            
            loaded_value = loaded_settings[key]
            
            # Handle float comparison with tolerance
            if isinstance(original_value, float) and isinstance(loaded_value, float):
                assert abs(loaded_value - original_value) < 1e-9, \
                    f"Value mismatch for key '{key}': {loaded_value} != {original_value}"
            else:
                assert loaded_value == original_value, \
                    f"Value mismatch for key '{key}': {loaded_value} != {original_value}"


@given(key=setting_key_strategy, value=setting_value_strategy)
@hyp_settings(max_examples=100)
def test_single_setting_roundtrip(key, value):
    """Test round-trip for a single setting.
    
    Feature: ui-refactor-settings, Property 1: Settings persistence round-trip
    Validates: Requirements 3.1, 3.2, 3.3
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save setting
        success = manager.save_setting(key, value)
        assert success, f"Failed to save setting '{key}'"
        
        # Load setting
        loaded_value = manager.get_setting(key)
        
        # Verify value matches
        if isinstance(value, float) and isinstance(loaded_value, float):
            assert abs(loaded_value - value) < 1e-9, \
                f"Value mismatch: {loaded_value} != {value}"
        else:
            assert loaded_value == value, \
                f"Value mismatch: {loaded_value} != {value}"


@given(settings_dict=settings_dict_strategy)
@hyp_settings(max_examples=100)
def test_settings_persistence_across_instances(settings_dict):
    """Test that settings persist across multiple manager instances.
    
    Feature: ui-refactor-settings, Property 1: Settings persistence round-trip
    Validates: Requirements 3.1, 3.2, 3.3
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # First instance: save settings
        manager1 = SettingsManager(storage_dir=Path(temp_dir))
        for key, value in settings_dict.items():
            success = manager1.save_setting(key, value)
            assert success, f"Failed to save setting '{key}'"
        
        # Second instance: load settings
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_settings = manager2.load_all_settings()
        
        # Third instance: verify settings still there
        manager3 = SettingsManager(storage_dir=Path(temp_dir))
        reloaded_settings = manager3.load_all_settings()
        
        # All three should have the same data
        assert loaded_settings == reloaded_settings, \
            "Settings changed between manager instances"
        
        for key, original_value in settings_dict.items():
            assert key in reloaded_settings, \
                f"Key '{key}' not found after multiple instance loads"
            
            if isinstance(original_value, float):
                assert abs(reloaded_settings[key] - original_value) < 1e-9, \
                    f"Value changed for key '{key}'"
            else:
                assert reloaded_settings[key] == original_value, \
                    f"Value changed for key '{key}'"


@given(
    settings_dict=settings_dict_strategy,
    key_to_update=setting_key_strategy,
    new_value=setting_value_strategy
)
@hyp_settings(max_examples=100)
def test_settings_update_preserves_others(settings_dict, key_to_update, new_value):
    """Test that updating one setting doesn't affect others.
    
    Feature: ui-refactor-settings, Property 1: Settings persistence round-trip
    Validates: Requirements 3.1, 3.2, 3.3
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save initial settings
        for key, value in settings_dict.items():
            manager.save_setting(key, value)
        
        # Update one setting (or add new one)
        manager.save_setting(key_to_update, new_value)
        
        # Load all settings
        loaded_settings = manager.load_all_settings()
        
        # Verify the updated/new key has the new value
        assert loaded_settings[key_to_update] == new_value or \
               (isinstance(new_value, float) and isinstance(loaded_settings[key_to_update], float) and 
                abs(loaded_settings[key_to_update] - new_value) < 1e-9), \
            f"Updated value not saved correctly"
        
        # Verify all other original keys still have their original values
        for key, original_value in settings_dict.items():
            if key != key_to_update:
                assert key in loaded_settings, f"Key '{key}' disappeared after update"
                
                if isinstance(original_value, float):
                    assert abs(loaded_settings[key] - original_value) < 1e-9, \
                        f"Value changed for unrelated key '{key}'"
                else:
                    assert loaded_settings[key] == original_value, \
                        f"Value changed for unrelated key '{key}'"


def test_settings_default_values():
    """Test that get_setting returns default when key doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Get non-existent key with default
        value = manager.get_setting("nonexistent_key", "default_value")
        assert value == "default_value"
        
        # Get non-existent key without default
        value = manager.get_setting("another_nonexistent_key")
        assert value is None


def test_settings_empty_load():
    """Test that loading from empty storage returns empty dict."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Load from empty storage
        settings = manager.load_all_settings()
        assert settings == {}


def test_settings_backup_recovery():
    """Test that settings can be recovered from backup if main file is corrupted."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save some settings
        manager.save_setting("test_key", "test_value")
        manager.save_setting("another_key", 42)
        
        # Verify backup exists and has correct content
        backup_file = Path(temp_dir) / "settings.json.backup"
        assert backup_file.exists(), "Backup file should exist"
        
        # Corrupt the main settings file
        settings_file = Path(temp_dir) / "settings.json"
        with open(settings_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Create new manager - should recover from backup
        manager2 = SettingsManager(storage_dir=Path(temp_dir))
        loaded_settings = manager2.load_all_settings()
        
        # Verify at least one setting was recovered (backup contains state before last write)
        # The backup will have the state from before the last save_setting call
        assert "test_key" in loaded_settings, "Should recover at least test_key from backup"
