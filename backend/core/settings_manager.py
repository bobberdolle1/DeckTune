"""Settings Manager for persistent configuration storage.

Feature: ui-refactor-settings
Validates: Requirements 3.1, 3.2, 3.3, 10.3, 10.4

This module provides persistent storage for critical plugin settings
including Expert Mode, Apply on Startup, Game Only Mode, and last active profile.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages persistent storage of plugin settings.
    
    Provides atomic write operations with backup to prevent data corruption.
    Settings are stored in JSON format in the user's home directory.
    
    Storage location: ~/homebrew/settings/decktune/settings.json
    """
    
    def __init__(self, storage_dir: Optional[Path] = None, legacy_settings_manager=None):
        """Initialize the settings manager.
        
        Args:
            storage_dir: Optional custom storage directory. 
                        Defaults to ~/homebrew/settings/decktune/
            legacy_settings_manager: Optional Decky SettingsManager for migration
        """
        if storage_dir is None:
            home = Path.home()
            self.storage_dir = home / "homebrew" / "settings" / "decktune"
        else:
            self.storage_dir = Path(storage_dir)
        
        self.settings_file = self.storage_dir / "settings.json"
        self.backup_file = self.storage_dir / "settings.json.backup"
        self.legacy_settings_manager = legacy_settings_manager
        
        # Create directory structure if it doesn't exist
        self._ensure_directory_exists()
        
        # In-memory cache of settings
        self._cache: Dict[str, Any] = {}
        self._loaded = False
    
    def _ensure_directory_exists(self) -> None:
        """Create storage directory if it doesn't exist."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Settings directory ensured: {self.storage_dir}")
        except Exception as e:
            logger.error(f"Failed to create settings directory: {e}")
            raise
    
    def save_setting(self, key: str, value: Any) -> bool:
        """Save a single setting to persistent storage.
        
        Performs atomic write with backup to prevent corruption.
        Updates both the in-memory cache and disk storage.
        Falls back to cached values on write failure.
        Rejects keys starting with underscore (reserved for internal use).
        
        Args:
            key: Setting key (must not start with underscore)
            value: Setting value (must be JSON-serializable)
            
        Returns:
            True if save succeeded, False otherwise
            
        Validates: Requirements 3.1, 3.5, 10.3
        """
        try:
            # Reject keys starting with underscore (reserved for internal use)
            if key.startswith("_"):
                logger.warning(f"Attempted to save internal key '{key}', rejecting")
                return False
            
            # Load current settings if not already loaded
            if not self._loaded:
                try:
                    self._load_from_disk()
                except Exception as load_error:
                    logger.error(f"Failed to load settings before save: {load_error}")
                    # Continue with empty cache
                    self._cache = {}
                    self._loaded = True
            
            # Update cache first (so we have the value even if write fails)
            self._cache[key] = value
            
            # Write to disk atomically with retry
            return self._write_to_disk_with_retry()
            
        except Exception as e:
            logger.error(f"Failed to save setting '{key}' with value '{value}': {e}", exc_info=True)
            # Value is still in cache, so reads will work
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting from storage.
        
        Loads from disk on first access, then uses in-memory cache.
        Falls back to default value on any error.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist or on error
            
        Returns:
            Setting value or default if not found or on error
            
        Validates: Requirements 3.2, 3.5, 10.3
        """
        try:
            # Load from disk if not already loaded
            if not self._loaded:
                try:
                    self._load_from_disk()
                except Exception as load_error:
                    logger.error(f"Failed to load settings for get_setting('{key}'): {load_error}", exc_info=True)
                    # Continue with empty cache and return default
                    self._cache = {}
                    self._loaded = True
                    return default
            
            return self._cache.get(key, default)
            
        except Exception as e:
            logger.error(f"Failed to get setting '{key}': {e}", exc_info=True)
            return default
    
    def load_all_settings(self) -> Dict[str, Any]:
        """Load all settings from storage.
        
        Returns a copy of all settings. Loads from disk if not already loaded.
        Falls back to empty dict on any error.
        Filters out internal migration flags.
        
        Returns:
            Dictionary containing all settings, or empty dict on error
            
        Validates: Requirements 3.2, 3.5, 10.4
        """
        try:
            # Load from disk if not already loaded
            if not self._loaded:
                try:
                    self._load_from_disk()
                except Exception as load_error:
                    logger.error(f"Failed to load settings from disk: {load_error}", exc_info=True)
                    # Continue with empty cache
                    self._cache = {}
                    self._loaded = True
            
            # Return a copy to prevent external modification
            # Filter out internal migration flags
            return {k: v for k, v in self._cache.items() if not k.startswith("_")}
            
        except Exception as e:
            logger.error(f"Failed to load all settings: {e}", exc_info=True)
            return {}
    
    def _load_from_disk(self) -> None:
        """Load settings from disk into cache.
        
        Attempts to load from main file, falls back to backup if corrupted.
        Performs migration from legacy storage if needed.
        Logs all errors with context.
        
        Validates: Requirements 3.2, 3.5
        """
        # Try to load from main file
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                self._loaded = True
                logger.debug(f"Loaded settings from {self.settings_file}")
                return
            except json.JSONDecodeError as e:
                logger.warning(f"Settings file corrupted at {self.settings_file}: {e}, trying backup")
            except Exception as e:
                logger.error(f"Failed to load settings from {self.settings_file}: {e}", exc_info=True)
        
        # Try to load from backup
        if self.backup_file.exists():
            try:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                self._loaded = True
                logger.info(f"Loaded settings from backup: {self.backup_file}")
                # Try to restore main file from backup
                try:
                    shutil.copy2(self.backup_file, self.settings_file)
                    logger.info(f"Restored main settings file from backup")
                except Exception as restore_error:
                    logger.error(f"Failed to restore main file from backup: {restore_error}")
                return
            except json.JSONDecodeError as e:
                logger.error(f"Backup file also corrupted at {self.backup_file}: {e}")
            except Exception as e:
                logger.error(f"Failed to load backup settings from {self.backup_file}: {e}", exc_info=True)
        
        # No valid settings found, start with empty cache
        self._cache = {}
        self._loaded = True
        logger.info("No existing settings found, starting with empty cache")
        
        # Attempt migration from legacy storage
        self._migrate_from_legacy()
    
    def _write_to_disk(self) -> bool:
        """Write settings to disk atomically.
        
        Creates a backup before writing to prevent data loss.
        Uses a temporary file and atomic rename for safety.
        Logs all errors with context.
        
        Returns:
            True if write succeeded, False otherwise
            
        Validates: Requirements 3.5
        """
        try:
            # Create backup of existing file if it exists
            if self.settings_file.exists():
                try:
                    shutil.copy2(self.settings_file, self.backup_file)
                    logger.debug("Created settings backup")
                except Exception as backup_error:
                    logger.warning(f"Failed to create backup before write: {backup_error}")
                    # Continue anyway - better to try writing than to fail completely
            
            # Write to temporary file first
            temp_file = self.storage_dir / "settings.json.tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f, indent=2, ensure_ascii=False)
            except Exception as write_error:
                logger.error(f"Failed to write to temporary file {temp_file}: {write_error}", exc_info=True)
                # Clean up temp file if it exists
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
                return False
            
            # Atomic rename (on most filesystems)
            try:
                temp_file.replace(self.settings_file)
            except Exception as rename_error:
                logger.error(f"Failed to rename temp file to {self.settings_file}: {rename_error}", exc_info=True)
                # Clean up temp file
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
                return False
            
            logger.debug(f"Settings written to {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error writing settings to disk: {e}", exc_info=True)
            return False
    
    def _write_to_disk_with_retry(self, max_retries: int = 2, retry_delay: float = 0.5) -> bool:
        """Write settings to disk with retry logic.
        
        Attempts to write multiple times with delay between attempts.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay in seconds between retries
            
        Returns:
            True if write succeeded, False otherwise
            
        Validates: Requirements 3.5
        """
        import time
        
        for attempt in range(max_retries):
            if self._write_to_disk():
                return True
            
            if attempt < max_retries - 1:
                logger.warning(f"Write attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        
        logger.error(f"Failed to write settings after {max_retries} attempts")
        return False
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting from storage.
        
        Args:
            key: Setting key to delete
            
        Returns:
            True if deletion succeeded, False otherwise
            
        Validates: Requirements 3.5
        """
        try:
            if not self._loaded:
                try:
                    self._load_from_disk()
                except Exception as load_error:
                    logger.error(f"Failed to load settings before delete: {load_error}")
                    self._cache = {}
                    self._loaded = True
            
            if key in self._cache:
                del self._cache[key]
                return self._write_to_disk_with_retry()
            
            return True  # Key doesn't exist, nothing to delete
            
        except Exception as e:
            logger.error(f"Failed to delete setting '{key}': {e}", exc_info=True)
            return False
    
    def clear_all_settings(self) -> bool:
        """Clear all settings from storage.
        
        Returns:
            True if clear succeeded, False otherwise
            
        Validates: Requirements 3.5
        """
        try:
            self._cache = {}
            self._loaded = True
            return self._write_to_disk_with_retry()
            
        except Exception as e:
            logger.error(f"Failed to clear settings: {e}", exc_info=True)
            return False
    
    def _migrate_from_legacy(self) -> None:
        """Migrate settings from legacy Decky SettingsManager storage.
        
        Checks for legacy Expert Mode storage and migrates to new system.
        Sets migration flag to prevent re-migration.
        Logs migration results.
        
        Feature: ui-refactor-settings
        Validates: Requirements 3.2
        """
        # Check if migration has already been performed
        if self._cache.get("_migration_completed"):
            logger.debug("Migration already completed, skipping")
            return
        
        # Check if legacy settings manager is available
        if not self.legacy_settings_manager:
            logger.debug("No legacy settings manager provided, skipping migration")
            # Mark migration as completed even if no legacy manager
            self._cache["_migration_completed"] = True
            self._write_to_disk_with_retry()
            return
        
        logger.info("Starting migration from legacy storage")
        migrated_count = 0
        
        try:
            # Migrate Expert Mode setting
            legacy_expert_mode = self.legacy_settings_manager.getSetting("expert_mode")
            if legacy_expert_mode is not None:
                self._cache["expert_mode"] = legacy_expert_mode
                migrated_count += 1
                logger.info(f"Migrated expert_mode: {legacy_expert_mode}")
            
            # Migrate Expert Mode confirmation flag
            legacy_expert_mode_confirmed = self.legacy_settings_manager.getSetting("expert_mode_confirmed")
            if legacy_expert_mode_confirmed is not None:
                self._cache["expert_mode_confirmed"] = legacy_expert_mode_confirmed
                migrated_count += 1
                logger.info(f"Migrated expert_mode_confirmed: {legacy_expert_mode_confirmed}")
            
            # Note: apply_on_startup and game_only_mode are new features,
            # so there's no legacy data to migrate for them
            
            # Mark migration as completed
            self._cache["_migration_completed"] = True
            
            # Persist migrated settings
            if migrated_count > 0:
                success = self._write_to_disk_with_retry()
                if success:
                    logger.info(f"Migration completed successfully: {migrated_count} settings migrated")
                else:
                    logger.error("Migration completed but failed to persist settings")
            else:
                logger.info("Migration completed: no legacy settings found to migrate")
                # Still persist the migration flag
                self._write_to_disk_with_retry()
                
        except Exception as e:
            logger.error(f"Error during migration: {e}", exc_info=True)
            # Mark migration as completed anyway to prevent repeated attempts
            self._cache["_migration_completed"] = True
            try:
                self._write_to_disk_with_retry()
            except Exception:
                pass  # Best effort
