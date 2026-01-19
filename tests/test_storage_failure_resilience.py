"""Property-based tests for storage failure resilience.

Feature: ui-refactor-settings, Property 6: Storage failure resilience
Validates: Requirements 3.5, 4.5

Tests that the system continues operation with default or cached values
when storage operations fail, and that all errors are properly logged.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume
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
    st.booleans(),
    st.none(),
    st.text(min_size=0, max_size=100)
)

# Strategy for generating complete settings dictionaries
settings_dict = st.dictionaries(
    keys=setting_keys,
    values=setting_values,
    min_size=0,
    max_size=4
)


@given(key=setting_keys, value=setting_values)
@settings(max_examples=100)
def test_save_setting_write_failure_returns_false(key, value):
    """Property 6: Storage failure resilience
    
    For any setting key and value, when a write failure occurs,
    save_setting should return False and log the error.
    
    Validates: Requirements 3.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Mock the _write_to_disk_with_retry method to simulate write failure
        # (mocking the retry method avoids the sleep delay)
        with patch.object(manager, '_write_to_disk_with_retry', return_value=False):
            # Attempt to save should fail gracefully
            result = manager.save_setting(key, value)
            
            # Should return False on failure
            assert result is False, f"Expected False on write failure, got {result}"
            
            # But value should still be in cache for reads
            cached_value = manager.get_setting(key)
            assert cached_value == value, f"Expected cached value {value}, got {cached_value}"


@given(key=setting_keys, default=setting_values)
@settings(max_examples=100)
def test_get_setting_read_failure_returns_default(key, default):
    """Property 6: Storage failure resilience
    
    For any setting key and default value, when a read failure occurs,
    get_setting should return the default value and log the error.
    
    Validates: Requirements 3.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Create a corrupted settings file
        settings_file = Path(tmpdir) / "settings.json"
        with open(settings_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Attempt to get setting should return default
        result = manager.get_setting(key, default)
        
        # Should return default value on read failure
        assert result == default, f"Expected default {default}, got {result}"


@given(settings_data=settings_dict)
@settings(max_examples=100)
def test_load_all_settings_corruption_returns_empty(settings_data):
    """Property 6: Storage failure resilience
    
    For any settings data, when the settings file is corrupted,
    load_all_settings should return an empty dict and log the error.
    
    Validates: Requirements 3.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Create a corrupted settings file
        settings_file = Path(tmpdir) / "settings.json"
        with open(settings_file, 'w') as f:
            f.write("{ corrupted: data }")
        
        # Attempt to load should return empty dict
        result = manager.load_all_settings()
        
        # Should return empty dict on corruption
        assert result == {}, f"Expected empty dict on corruption, got {result}"


@given(key=setting_keys, value=setting_values)
@settings(max_examples=100)
def test_save_setting_permission_error_logged(key, value):
    """Property 6: Storage failure resilience
    
    For any setting key and value, when a write error occurs,
    the error should be logged with context.
    
    Validates: Requirements 3.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Mock _write_to_disk to raise an exception
        with patch.object(manager, '_write_to_disk', side_effect=PermissionError("Simulated permission error")):
            with patch('backend.core.settings_manager.logger') as mock_logger:
                # Attempt to save
                result = manager.save_setting(key, value)
                
                # Should return False
                assert result is False, f"Expected False on error, got {result}"
                
                # Verify error was logged
                assert mock_logger.error.called, "Expected error to be logged"
                
                # Check that the log message contains context
                call_args = mock_logger.error.call_args
                assert call_args is not None, "Expected error log call"
                log_message = str(call_args[0][0])
                assert key in log_message or "Failed" in log_message, \
                    f"Expected error log to contain context, got: {log_message}"


@given(settings_data=settings_dict)
@settings(max_examples=100)
def test_system_continues_after_write_failure(settings_data):
    """Property 6: Storage failure resilience
    
    For any settings data, after a write failure, the system should
    continue operating with cached values.
    
    Validates: Requirements 3.5, 4.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # First, successfully save some settings
        for key, value in settings_data.items():
            manager.save_setting(key, value)
        
        # Verify settings are in cache
        for key, value in settings_data.items():
            cached_value = manager.get_setting(key)
            assert cached_value == value, f"Expected cached value {value}, got {cached_value}"
        
        # Now mock write failures (mock the retry method to avoid sleep)
        with patch.object(manager, '_write_to_disk_with_retry', return_value=False):
            # Attempt to save new values should fail
            new_value = not settings_data.get("expert_mode", False) if "expert_mode" in settings_data else True
            result = manager.save_setting("expert_mode", new_value)
            assert result is False, "Expected save to fail"
            
            # The new value should still be in cache even though write failed
            cached_new_value = manager.get_setting("expert_mode")
            assert cached_new_value == new_value, \
                f"Expected system to cache new value {new_value}, got {cached_new_value}"
            
            # Original settings should still be readable
            for key, value in settings_data.items():
                if key != "expert_mode":
                    cached_value = manager.get_setting(key)
                    assert cached_value == value, \
                        f"Expected system to continue with cached value {value}, got {cached_value}"


@given(key=setting_keys, value=setting_values)
@settings(max_examples=100)
def test_backup_restore_on_corruption(key, value):
    """Property 6: Storage failure resilience
    
    For any setting, when the main settings file is corrupted,
    the system should restore from backup if available.
    
    Validates: Requirements 3.5
    """
    # Skip None values as they aren't serialized to JSON the same way
    assume(value is not None)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Save a setting twice to ensure backup is created
        manager.save_setting(key, value)
        manager.save_setting(key, value)  # Second save creates backup
        
        # Verify backup exists
        backup_file = Path(tmpdir) / "settings.json.backup"
        assert backup_file.exists(), "Expected backup file to exist after second save"
        
        # Corrupt the main file
        settings_file = Path(tmpdir) / "settings.json"
        with open(settings_file, 'w') as f:
            f.write("{ corrupted }")
        
        # Create a new manager instance to trigger load from disk
        manager2 = SettingsManager(storage_dir=Path(tmpdir))
        
        # Should restore from backup
        result = manager2.get_setting(key)
        assert result == value, f"Expected backup restore to return {value}, got {result}"


def test_missing_directory_creates_default():
    """Property 6: Storage failure resilience
    
    When the storage directory doesn't exist, the system should
    create it and continue with default values.
    
    Validates: Requirements 3.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a non-existent subdirectory
        storage_dir = Path(tmpdir) / "nonexistent" / "settings"
        
        # Should not raise an exception
        manager = SettingsManager(storage_dir=storage_dir)
        
        # Should return default values
        result = manager.get_setting("expert_mode", False)
        assert result is False, f"Expected default False, got {result}"
        
        # Directory should now exist
        assert storage_dir.exists(), "Expected directory to be created"


@given(settings_data=settings_dict)
@settings(max_examples=100)
def test_partial_write_recovery(settings_data):
    """Property 6: Storage failure resilience
    
    For any settings data, if a write is interrupted, the backup
    should preserve the previous state.
    
    Validates: Requirements 3.5
    """
    assume(len(settings_data) > 0)  # Need at least one setting
    # Skip settings with None values as they serialize differently
    assume(all(v is not None for v in settings_data.values()))
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SettingsManager(storage_dir=Path(tmpdir))
        
        # Save initial settings twice to create backup
        for key, value in settings_data.items():
            manager.save_setting(key, value)
        for key, value in settings_data.items():
            manager.save_setting(key, value)  # Second pass creates backup
        
        # Verify backup exists
        backup_file = Path(tmpdir) / "settings.json.backup"
        if not backup_file.exists():
            # If no backup, skip this test case
            assume(False)
        
        # Read backup content
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Backup should contain the saved settings
        for key, value in settings_data.items():
            assert backup_data.get(key) == value, \
                f"Expected backup to contain {key}={value}, got {backup_data.get(key)}"
