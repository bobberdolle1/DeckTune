"""Per-game profile management for DeckTune 3.0.

This module provides per-game profile management with automatic switching
based on the active Steam game. It extends the existing profiles.py module
which handles dynamic mode presets.

Feature: decktune-3.0-automation
Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4

# Per-Game Profile System Overview

Game profiles allow users to save different undervolt settings for each game:
- Each profile is associated with a Steam AppID
- Profiles store undervolt values and dynamic mode configuration
- Automatic profile switching when games launch
- Global default profile for games without specific profiles

# Storage Format

Profiles are stored in Decky settings under the "game_profiles" key:
```json
{
  "version": "3.0",
  "global_default": {
    "cores": [0, 0, 0, 0],
    "dynamic_enabled": false,
    "dynamic_config": null
  },
  "profiles": [
    {
      "app_id": 1091500,
      "name": "Cyberpunk 2077",
      "cores": [-25, -25, -25, -25],
      "dynamic_enabled": true,
      "dynamic_config": {
        "strategy": "balanced",
        "simple_mode": true,
        "simple_value": -25
      },
      "created_at": "2026-01-15T10:30:00Z",
      "last_used": "2026-01-15T14:20:00Z"
    }
  ]
}
```

# Usage Example

```python
from backend.dynamic.profile_manager import ProfileManager, GameProfile

# Initialize manager
manager = ProfileManager(settings_manager, ryzenadj, dynamic_controller, event_emitter)

# Create a profile for current game
profile = await manager.create_from_current(app_id=1091500, name="Cyberpunk 2077")

# Apply profile when game launches
await manager.apply_profile(app_id=1091500)

# Handle app change from watcher
await manager.on_app_change(app_id=1091500)
```
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..dynamic.controller import DynamicController
    from ..api.events import EventEmitter

logger = logging.getLogger(__name__)


@dataclass
class GameProfile:
    """Per-game profile configuration.
    
    Attributes:
        app_id: Steam AppID (unique identifier)
        name: Game name (from Steam or user-provided)
        cores: Undervolt values for each core [core0, core1, core2, core3] in mV
        dynamic_enabled: Whether dynamic mode is enabled for this profile
        dynamic_config: Dynamic mode configuration (if dynamic_enabled is True)
        created_at: ISO timestamp when profile was created
        last_used: ISO timestamp when profile was last applied (None if never used)
    
    Requirements: 3.1
    """
    app_id: int
    name: str
    cores: List[int]
    dynamic_enabled: bool = False
    dynamic_config: Optional[Dict[str, Any]] = None
    created_at: str = ""
    last_used: Optional[str] = None
    
    def __post_init__(self):
        """Set created_at timestamp if not provided."""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for JSON serialization."""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "cores": self.cores,
            "dynamic_enabled": self.dynamic_enabled,
            "dynamic_config": self.dynamic_config,
            "created_at": self.created_at,
            "last_used": self.last_used,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameProfile":
        """Create GameProfile from dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            GameProfile instance
        """
        return cls(
            app_id=data.get("app_id", 0),
            name=data.get("name", "Unknown Game"),
            cores=data.get("cores", [0, 0, 0, 0]),
            dynamic_enabled=data.get("dynamic_enabled", False),
            dynamic_config=data.get("dynamic_config"),
            created_at=data.get("created_at", ""),
            last_used=data.get("last_used"),
        )
    
    def validate(self) -> List[str]:
        """Validate the profile.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate app_id
        if not isinstance(self.app_id, int) or self.app_id <= 0:
            errors.append("app_id must be a positive integer")
        
        # Validate name
        if not self.name or not self.name.strip():
            errors.append("name cannot be empty")
        
        if len(self.name) > 128:
            errors.append("name must be 128 characters or less")
        
        # Validate cores array
        if not isinstance(self.cores, list):
            errors.append("cores must be a list")
        elif len(self.cores) != 4:
            errors.append("cores must contain exactly 4 values")
        else:
            for i, value in enumerate(self.cores):
                if not isinstance(value, int):
                    errors.append(f"cores[{i}] must be an integer")
                elif value < -100 or value > 0:
                    errors.append(f"cores[{i}] must be between -100 and 0 mV")
        
        # Validate dynamic_config if dynamic_enabled
        if self.dynamic_enabled and self.dynamic_config is None:
            errors.append("dynamic_config is required when dynamic_enabled is True")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if profile is valid."""
        return len(self.validate()) == 0


class ProfileManager:
    """Manager for per-game profiles with automatic switching.
    
    Handles CRUD operations, persistence, and profile application.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4
    """
    
    STORAGE_KEY = "game_profiles"
    STORAGE_VERSION = "3.0"
    
    def __init__(
        self,
        settings_manager,
        ryzenadj: "RyzenadjWrapper",
        dynamic_controller: Optional["DynamicController"],
        event_emitter: "EventEmitter"
    ):
        """Initialize the profile manager.
        
        Args:
            settings_manager: Decky settings manager instance
            ryzenadj: RyzenadjWrapper for applying undervolt values
            dynamic_controller: DynamicController for dynamic mode (optional)
            event_emitter: EventEmitter for status updates
        """
        self.settings = settings_manager
        self.ryzenadj = ryzenadj
        self.dynamic_controller = dynamic_controller
        self.event_emitter = event_emitter
        
        # In-memory cache of profiles (keyed by app_id)
        self._profiles: Dict[int, GameProfile] = {}
        self._global_default: Dict[str, Any] = {
            "cores": [0, 0, 0, 0],
            "dynamic_enabled": False,
            "dynamic_config": None
        }
        self._current_app_id: Optional[int] = None
        
        # Load profiles from settings
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load profiles from settings storage."""
        try:
            data = self.settings.getSetting(self.STORAGE_KEY, {})
            
            # Load global default
            if "global_default" in data:
                self._global_default = data["global_default"]
            
            # Load profiles
            profiles_list = data.get("profiles", [])
            for profile_data in profiles_list:
                profile = GameProfile.from_dict(profile_data)
                if profile.is_valid():
                    self._profiles[profile.app_id] = profile
                else:
                    logger.warning(f"Skipping invalid profile for app_id {profile.app_id}: {profile.validate()}")
            
            logger.info(f"Loaded {len(self._profiles)} game profiles from settings")
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            # Initialize with empty profiles on error
            self._profiles = {}
    
    def _save_profiles(self) -> bool:
        """Save profiles to settings storage.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert profiles to list
            profiles_list = [profile.to_dict() for profile in self._profiles.values()]
            
            data = {
                "version": self.STORAGE_VERSION,
                "global_default": self._global_default,
                "profiles": profiles_list
            }
            
            self.settings.setSetting(self.STORAGE_KEY, data)
            logger.info(f"Saved {len(profiles_list)} game profiles to settings")
            return True
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            return False

    
    # ==================== Profile Creation ====================
    
    async def create_profile(
        self,
        app_id: int,
        name: str,
        cores: List[int],
        dynamic_enabled: bool = False,
        dynamic_config: Optional[Dict[str, Any]] = None
    ) -> Optional[GameProfile]:
        """Create a new game profile.
        
        Args:
            app_id: Steam AppID
            name: Game name
            cores: Undervolt values for each core [core0, core1, core2, core3]
            dynamic_enabled: Whether dynamic mode is enabled
            dynamic_config: Dynamic mode configuration (required if dynamic_enabled is True)
            
        Returns:
            Created GameProfile if successful, None otherwise
            
        Requirements: 3.1, 3.5, 5.2
        """
        # Check if profile already exists
        if app_id in self._profiles:
            logger.warning(f"Profile for app_id {app_id} already exists")
            return None
        
        # Create profile
        profile = GameProfile(
            app_id=app_id,
            name=name,
            cores=cores,
            dynamic_enabled=dynamic_enabled,
            dynamic_config=dynamic_config
        )
        
        # Validate profile
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid profile: {errors}")
            return None
        
        # Store profile
        self._profiles[app_id] = profile
        self._save_profiles()
        
        logger.info(f"Created profile for '{name}' (app_id: {app_id})")
        return profile
    
    async def create_from_current(
        self,
        app_id: int,
        name: str
    ) -> Optional[GameProfile]:
        """Create profile from current active settings.
        
        Captures the current undervolt values and dynamic mode configuration
        and saves them as a profile for the specified game.
        
        Args:
            app_id: Steam AppID
            name: Game name
            
        Returns:
            Created GameProfile if successful, None otherwise
            
        Requirements: 3.5, 5.2
        """
        try:
            # Get current undervolt values from settings
            current_cores = self.settings.getSetting("cores", [0, 0, 0, 0])
            
            # Get dynamic mode status
            dynamic_enabled = False
            dynamic_config = None
            
            if self.dynamic_controller:
                dynamic_enabled = self.dynamic_controller.is_running()
                if dynamic_enabled:
                    # Get current dynamic config from settings
                    dynamic_config = self.settings.getSetting("dynamic_config")
            
            # Create profile with captured settings
            return await self.create_profile(
                app_id=app_id,
                name=name,
                cores=current_cores,
                dynamic_enabled=dynamic_enabled,
                dynamic_config=dynamic_config
            )
        except Exception as e:
            logger.error(f"Failed to create profile from current settings: {e}")
            return None

    
    # ==================== Profile CRUD Operations ====================
    
    def get_profile(self, app_id: int) -> Optional[GameProfile]:
        """Get a profile by AppID.
        
        Args:
            app_id: Steam AppID
            
        Returns:
            GameProfile if found, None otherwise
            
        Requirements: 3.2
        """
        return self._profiles.get(app_id)
    
    def get_all_profiles(self) -> List[GameProfile]:
        """Get all profiles.
        
        Returns:
            List of all GameProfile instances
            
        Requirements: 3.2
        """
        return list(self._profiles.values())
    
    async def update_profile(
        self,
        app_id: int,
        **kwargs
    ) -> bool:
        """Update an existing profile.
        
        Args:
            app_id: Steam AppID of profile to update
            **kwargs: Fields to update (name, cores, dynamic_enabled, dynamic_config)
            
        Returns:
            True if updated successfully, False otherwise
            
        Requirements: 3.3
        """
        profile = self._profiles.get(app_id)
        if not profile:
            logger.warning(f"Profile for app_id {app_id} not found")
            return False
        
        # Update fields
        if "name" in kwargs:
            profile.name = kwargs["name"]
        if "cores" in kwargs:
            profile.cores = kwargs["cores"]
        if "dynamic_enabled" in kwargs:
            profile.dynamic_enabled = kwargs["dynamic_enabled"]
        if "dynamic_config" in kwargs:
            profile.dynamic_config = kwargs["dynamic_config"]
        
        # Validate updated profile
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid profile after update: {errors}")
            return False
        
        # Save changes
        self._save_profiles()
        
        # If this is the currently active profile, apply the changes
        if self._current_app_id == app_id:
            await self.apply_profile(app_id)
        
        logger.info(f"Updated profile for app_id {app_id}")
        return True
    
    async def delete_profile(self, app_id: int) -> bool:
        """Delete a profile by AppID.
        
        If the deleted profile is currently active, reverts to global default.
        
        Args:
            app_id: Steam AppID of profile to delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Requirements: 3.4
        """
        if app_id not in self._profiles:
            logger.warning(f"Profile for app_id {app_id} not found")
            return False
        
        # Check if this is the currently active profile
        is_active = (self._current_app_id == app_id)
        
        # Delete profile
        del self._profiles[app_id]
        self._save_profiles()
        
        # If it was active, revert to global default
        if is_active:
            await self.apply_global_default()
        
        logger.info(f"Deleted profile for app_id {app_id}")
        return True

    
    # ==================== Profile Application ====================
    
    async def apply_profile(self, app_id: int) -> bool:
        """Apply a profile's settings.
        
        Applies the undervolt values and starts/stops dynamic mode as needed.
        Emits an event to the frontend with the active profile name.
        
        Args:
            app_id: Steam AppID of profile to apply
            
        Returns:
            True if applied successfully, False otherwise
            
        Requirements: 4.2, 4.4
        """
        profile = self._profiles.get(app_id)
        if not profile:
            logger.warning(f"Profile for app_id {app_id} not found")
            return False
        
        try:
            # Update last_used timestamp
            profile.last_used = datetime.now(timezone.utc).isoformat()
            self._save_profiles()
            
            # Apply undervolt values
            success, error = await self.ryzenadj.apply_values_async(profile.cores)
            if not success:
                logger.error(f"Failed to apply undervolt values: {error}")
                return False
            
            # Handle dynamic mode
            if self.dynamic_controller:
                if profile.dynamic_enabled and profile.dynamic_config:
                    # Start dynamic mode with profile's config
                    # Note: This would need to be implemented in DynamicController
                    # For now, we'll just log it
                    logger.info(f"Dynamic mode enabled for profile '{profile.name}'")
                    # TODO: await self.dynamic_controller.start(profile.dynamic_config)
                else:
                    # Stop dynamic mode if it's running
                    if self.dynamic_controller.is_running():
                        await self.dynamic_controller.stop()
                        logger.info(f"Dynamic mode disabled for profile '{profile.name}'")
            
            # Update current app_id
            self._current_app_id = app_id
            
            # Emit event to frontend
            self.event_emitter.emit_profile_changed(profile.name, app_id)
            
            logger.info(f"Applied profile '{profile.name}' (app_id: {app_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply profile: {e}")
            return False

    
    # ==================== Global Default Handling ====================
    
    async def apply_global_default(self) -> bool:
        """Apply the global default settings.
        
        Used when no specific profile exists for the current game.
        
        Returns:
            True if applied successfully, False otherwise
            
        Requirements: 4.3
        """
        try:
            # Apply undervolt values from global default
            cores = self._global_default.get("cores", [0, 0, 0, 0])
            success, error = await self.ryzenadj.apply_values_async(cores)
            if not success:
                logger.error(f"Failed to apply global default values: {error}")
                return False
            
            # Handle dynamic mode
            if self.dynamic_controller:
                dynamic_enabled = self._global_default.get("dynamic_enabled", False)
                dynamic_config = self._global_default.get("dynamic_config")
                
                if dynamic_enabled and dynamic_config:
                    # Start dynamic mode with global config
                    logger.info("Dynamic mode enabled for global default")
                    # TODO: await self.dynamic_controller.start(dynamic_config)
                else:
                    # Stop dynamic mode if it's running
                    if self.dynamic_controller.is_running():
                        await self.dynamic_controller.stop()
                        logger.info("Dynamic mode disabled for global default")
            
            # Clear current app_id
            self._current_app_id = None
            
            # Emit event to frontend
            self.event_emitter.emit_profile_changed("Global Default", None)
            
            logger.info("Applied global default settings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply global default: {e}")
            return False
    
    def get_global_default(self) -> Dict[str, Any]:
        """Get the global default settings.
        
        Returns:
            Dictionary containing global default settings
        """
        return self._global_default.copy()
    
    def set_global_default(
        self,
        cores: List[int],
        dynamic_enabled: bool = False,
        dynamic_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Set the global default settings.
        
        Args:
            cores: Undervolt values for each core
            dynamic_enabled: Whether dynamic mode is enabled
            dynamic_config: Dynamic mode configuration
            
        Returns:
            True if set successfully, False otherwise
        """
        # Validate cores
        if not isinstance(cores, list) or len(cores) != 4:
            logger.error("cores must be a list of 4 integers")
            return False
        
        for i, value in enumerate(cores):
            if not isinstance(value, int) or value < -100 or value > 0:
                logger.error(f"cores[{i}] must be between -100 and 0 mV")
                return False
        
        # Update global default
        self._global_default = {
            "cores": cores,
            "dynamic_enabled": dynamic_enabled,
            "dynamic_config": dynamic_config
        }
        
        # Save to settings
        self._save_profiles()
        
        logger.info("Updated global default settings")
        return True
    
    # ==================== App Change Handling ====================
    
    async def on_app_change(self, app_id: Optional[int]) -> None:
        """Handle Steam app change event.
        
        Called by AppWatcher when the active game changes.
        Applies the appropriate profile or global default.
        
        Args:
            app_id: Steam AppID of the new active game (None if no game running)
            
        Requirements: 4.1, 4.2, 4.3
        """
        # If no game is running, apply global default
        if app_id is None:
            await self.apply_global_default()
            return
        
        # Check if we have a profile for this game
        profile = self._profiles.get(app_id)
        
        if profile:
            # Apply specific profile
            await self.apply_profile(app_id)
        else:
            # No profile found, apply global default
            logger.info(f"No profile found for app_id {app_id}, using global default")
            await self.apply_global_default()
    
    # ==================== Import/Export ====================
    
    def export_profiles(self) -> str:
        """Export all profiles as JSON string.
        
        Includes version metadata and all profiles formatted with indentation
        for readability.
        
        Returns:
            JSON string containing all profiles
            
        Requirements: 9.1
        """
        # Convert profiles to list
        profiles_list = [profile.to_dict() for profile in self._profiles.values()]
        
        # Create export data structure
        export_data = {
            "version": self.STORAGE_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "global_default": self._global_default,
            "profiles": profiles_list
        }
        
        # Format with indentation for readability
        json_str = json.dumps(export_data, indent=2, sort_keys=True)
        
        logger.info(f"Exported {len(profiles_list)} profiles")
        return json_str
    
    async def import_profiles(
        self,
        json_data: str,
        merge_strategy: str = "skip"
    ) -> Dict[str, Any]:
        """Import profiles from JSON string.
        
        Validates JSON structure and required fields. Supports merge strategies
        for handling conflicts with existing profiles.
        
        Args:
            json_data: JSON string containing profiles to import
            merge_strategy: How to handle conflicts - "skip", "overwrite", or "rename"
            
        Returns:
            Dictionary with import results:
            {
                "success": bool,
                "imported_count": int,
                "skipped_count": int,
                "conflicts": List[Dict],
                "errors": List[str]
            }
            
        Requirements: 9.2, 9.3, 9.4
        """
        result = {
            "success": False,
            "imported_count": 0,
            "skipped_count": 0,
            "conflicts": [],
            "errors": []
        }
        
        # Validate merge strategy
        if merge_strategy not in ["skip", "overwrite", "rename"]:
            result["errors"].append(f"Invalid merge strategy: {merge_strategy}")
            return result
        
        try:
            # Parse JSON
            try:
                import_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                result["errors"].append(f"Invalid JSON: {str(e)}")
                return result
            
            # Validate structure
            if not isinstance(import_data, dict):
                result["errors"].append("Import data must be a JSON object")
                return result
            
            if "profiles" not in import_data:
                result["errors"].append("Missing 'profiles' field in import data")
                return result
            
            if not isinstance(import_data["profiles"], list):
                result["errors"].append("'profiles' field must be an array")
                return result
            
            # Process each profile
            profiles_to_import = import_data["profiles"]
            
            for profile_data in profiles_to_import:
                # Validate required fields
                if not isinstance(profile_data, dict):
                    result["errors"].append("Profile must be a JSON object")
                    continue
                
                if "app_id" not in profile_data:
                    result["errors"].append("Profile missing required field: app_id")
                    continue
                
                app_id = profile_data.get("app_id")
                
                # Check for conflict
                existing_profile = self._profiles.get(app_id)
                
                if existing_profile:
                    # Conflict detected
                    conflict_info = {
                        "app_id": app_id,
                        "existing_name": existing_profile.name,
                        "import_name": profile_data.get("name", "Unknown"),
                        "strategy": merge_strategy
                    }
                    result["conflicts"].append(conflict_info)
                    
                    if merge_strategy == "skip":
                        # Skip this profile
                        result["skipped_count"] += 1
                        logger.info(f"Skipped profile for app_id {app_id} (already exists)")
                        continue
                    elif merge_strategy == "rename":
                        # Rename by appending timestamp
                        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                        profile_data["name"] = f"{profile_data.get('name', 'Unknown')} (imported {timestamp})"
                        # Note: We still use the same app_id, so this will overwrite
                        # A true rename would need to change the app_id, which doesn't make sense
                        # So we'll treat rename as overwrite with a modified name
                        logger.info(f"Renaming profile for app_id {app_id}")
                    # For "overwrite", we just continue and replace the existing profile
                
                # Create profile from import data
                try:
                    profile = GameProfile.from_dict(profile_data)
                    
                    # Validate profile
                    errors = profile.validate()
                    if errors:
                        result["errors"].append(f"Invalid profile for app_id {app_id}: {', '.join(errors)}")
                        continue
                    
                    # Import the profile
                    self._profiles[app_id] = profile
                    result["imported_count"] += 1
                    logger.info(f"Imported profile '{profile.name}' (app_id: {app_id})")
                    
                except Exception as e:
                    result["errors"].append(f"Failed to import profile for app_id {app_id}: {str(e)}")
                    continue
            
            # Save imported profiles
            if result["imported_count"] > 0:
                self._save_profiles()
                result["success"] = True
            else:
                result["success"] = len(result["errors"]) == 0
            
            logger.info(f"Import complete: {result['imported_count']} imported, {result['skipped_count']} skipped, {len(result['errors'])} errors")
            return result
            
        except Exception as e:
            result["errors"].append(f"Import failed: {str(e)}")
            logger.error(f"Profile import failed: {e}")
            return result
