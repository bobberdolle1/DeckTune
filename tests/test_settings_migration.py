"""Tests for settings migration from legacy storage.

Feature: ui-refactor-settings
Validates: Requirements 3.2

Tests that settings are correctly migrated from legacy Decky SettingsManager
to the new CoreSettingsManager.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.settings_manager import SettingsManager


def test_migration_from_legacy_expert_mode():
    """Test that expert_mode is migrated from legacy storage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(side_effect=lambda key: {
            "expert_mode": True,
            "expert_mode_confirmed": True
        }.get(key))
        
        # Create new settings manager with legacy manager
        manager = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        
        # Load settings (should trigger migration)
        settings = manager.load_all_settings()
        
        # Verify expert_mode was migrated
        assert settings.get("expert_mode") is True, "expert_mode should be migrated"
        assert settings.get("expert_mode_confirmed") is True, "expert_mode_confirmed should be migrated"
        
        # Verify migration was called
        assert legacy_settings.getSetting.call_count >= 2


def test_migration_flag_prevents_remigration():
    """Test that migration flag prevents repeated migration attempts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(side_effect=lambda key: {
            "expert_mode": True
        }.get(key))
        
        # First manager instance - should migrate
        manager1 = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        settings1 = manager1.load_all_settings()
        
        assert settings1.get("expert_mode") is True
        first_call_count = legacy_settings.getSetting.call_count
        
        # Second manager instance - should NOT migrate again
        manager2 = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        settings2 = manager2.load_all_settings()
        
        assert settings2.get("expert_mode") is True
        # Call count should not increase (migration already completed)
        assert legacy_settings.getSetting.call_count == first_call_count


def test_migration_with_no_legacy_data():
    """Test migration when no legacy data exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager with no data
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(return_value=None)
        
        # Create new settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        
        # Load settings
        settings = manager.load_all_settings()
        
        # Should have empty settings (no migration data)
        assert len(settings) == 0
        
        # Verify migration was attempted
        assert legacy_settings.getSetting.call_count >= 1


def test_migration_without_legacy_manager():
    """Test that migration is skipped when no legacy manager is provided."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create new settings manager without legacy manager
        manager = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=None)
        
        # Load settings
        settings = manager.load_all_settings()
        
        # Should have empty settings
        assert len(settings) == 0


def test_migration_persists_to_disk():
    """Test that migrated settings are persisted to disk."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(side_effect=lambda key: {
            "expert_mode": True,
            "expert_mode_confirmed": False
        }.get(key))
        
        # Create new settings manager and trigger migration
        manager1 = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        settings1 = manager1.load_all_settings()
        
        assert settings1.get("expert_mode") is True
        assert settings1.get("expert_mode_confirmed") is False
        
        # Create a new manager instance without legacy manager
        # Should load migrated settings from disk
        manager2 = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=None)
        settings2 = manager2.load_all_settings()
        
        assert settings2.get("expert_mode") is True
        assert settings2.get("expert_mode_confirmed") is False


def test_migration_handles_errors_gracefully():
    """Test that migration errors don't crash the system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager that raises an error
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(side_effect=Exception("Legacy storage error"))
        
        # Create new settings manager - should not crash
        manager = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        
        # Load settings - should return empty dict, not crash
        settings = manager.load_all_settings()
        
        # Should have empty settings (migration failed but system continues)
        assert len(settings) == 0


def test_migration_only_migrates_existing_values():
    """Test that only values that exist in legacy storage are migrated."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock legacy settings manager with only expert_mode
        legacy_settings = Mock()
        legacy_settings.getSetting = Mock(side_effect=lambda key: {
            "expert_mode": True
        }.get(key))  # expert_mode_confirmed returns None
        
        # Create new settings manager
        manager = SettingsManager(storage_dir=Path(temp_dir), legacy_settings_manager=legacy_settings)
        
        # Load settings
        settings = manager.load_all_settings()
        
        # Only expert_mode should be migrated
        assert settings.get("expert_mode") is True
        assert "expert_mode_confirmed" not in settings
