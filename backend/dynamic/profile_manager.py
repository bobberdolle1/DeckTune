"""Per-game profile management for DeckTune 3.0.

This module provides per-game profile management with automatic switching
based on the active Steam game. It extends the existing profiles.py module
which handles dynamic mode presets.

Feature: decktune-3.0-automation
Validates: Requirements 1.1, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4

# Per-Game Profile System Overview

Game profiles allow users to save different undervolt settings for each game:
- Each profile is associated with a Steam AppID
- Profiles store undervolt values and dynamic mode configuration
- Automatic profile switching when games launch
- Global default profile for games without specific profiles
- Context conditions for environment-based profile selection (battery, power mode, temperature)

# Storage Format

Profiles are stored in Decky settings under the "game_profiles" key:
```json
{
  "version": "3.1",
  "global_default": {
    "cores": [0, 0, 0, 0],
    "dynamic_enabled": false,
    "dynamic_config": null
  },
  "profiles": [
    {
      "app_id": 1091500,
      "name": "Cyberpunk 2077 - Battery Saver",
      "cores": [-20, -20, -20, -20],
      "dynamic_enabled": false,
      "dynamic_config": null,
      "conditions": {
        "battery_threshold": 30,
        "power_mode": "battery",
        "temp_threshold": null
      },
      "created_at": "2026-01-15T10:30:00Z",
      "last_used": "2026-01-15T14:20:00Z"
    }
  ]
}
```

# Usage Example

```python
from backend.dynamic.profile_manager import ProfileManager, GameProfile, ContextualGameProfile

# Initialize manager
manager = ProfileManager(settings_manager, ryzenadj, dynamic_controller, event_emitter)

# Create a contextual profile for current game
profile = await manager.create_contextual_profile(
    app_id=1091500,
    name="Cyberpunk 2077 - Battery Saver",
    cores=[-20, -20, -20, -20],
    conditions=ContextCondition(battery_threshold=30, power_mode="battery")
)

# Apply profile when game launches (context-aware)
await manager.apply_profile_for_context(app_id=1091500)

# Handle app change from watcher
await manager.on_app_change(app_id=1091500)

# Handle context changes
await manager.on_battery_change(25)  # Battery dropped to 25%
await manager.on_power_mode_change("battery")  # Unplugged from AC
```
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TYPE_CHECKING

from .context import ContextCondition, SystemContext, ContextMatcher
from ..tuning.frequency_curve import FrequencyCurve

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
        frequency_curves: Optional frequency curves for each core (dict mapping core_id to FrequencyCurve)
        created_at: ISO timestamp when profile was created
        last_used: ISO timestamp when profile was last applied (None if never used)
    
    Requirements: 3.1, 8.1
    """
    app_id: int
    name: str
    cores: List[int]
    dynamic_enabled: bool = False
    dynamic_config: Optional[Dict[str, Any]] = None
    frequency_curves: Optional[Dict[int, Dict[str, Any]]] = None  # Serialized FrequencyCurve data
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
            "frequency_curves": self.frequency_curves,
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
            frequency_curves=data.get("frequency_curves"),
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
        
        # Validate frequency_curves if present
        if self.frequency_curves is not None:
            if not isinstance(self.frequency_curves, dict):
                errors.append("frequency_curves must be a dictionary")
            else:
                for core_id, curve_data in self.frequency_curves.items():
                    try:
                        # Validate that core_id is an integer
                        core_id_int = int(core_id)
                        if core_id_int < 0 or core_id_int > 3:
                            errors.append(f"Invalid core_id {core_id_int} in frequency_curves")
                        
                        # Validate curve data structure
                        if not isinstance(curve_data, dict):
                            errors.append(f"Curve data for core {core_id} must be a dictionary")
                            continue
                        
                        # Try to deserialize and validate the curve
                        try:
                            curve = FrequencyCurve.from_dict(curve_data)
                            curve.validate()
                        except (KeyError, ValueError) as e:
                            errors.append(f"Invalid frequency curve for core {core_id}: {str(e)}")
                    except (ValueError, TypeError) as e:
                        errors.append(f"Invalid core_id '{core_id}' in frequency_curves: {str(e)}")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if profile is valid."""
        return len(self.validate()) == 0


@dataclass
class ContextualGameProfile(GameProfile):
    """Per-game profile with context conditions for activation.
    
    Extends GameProfile with environmental conditions that must be met
    for the profile to be activated. This enables automatic profile
    switching based on battery level, power mode, and temperature.
    
    Attributes:
        conditions: Context conditions for activation (battery, power mode, temperature)
        frequency_curves: Optional frequency curves for each core (inherited from GameProfile)
    
    Requirements: 1.1, 8.1
    """
    conditions: ContextCondition = field(default_factory=ContextCondition)
    
    def matches_context(self, app_id: Optional[int], context: SystemContext) -> bool:
        """Check if profile matches app_id and context conditions.
        
        A profile matches if:
        1. app_id matches (or profile.app_id is None for global default)
        2. All context conditions are satisfied
        
        Args:
            app_id: Steam AppID to match (None for no specific game)
            context: Current system context
            
        Returns:
            True if profile matches both app_id and context conditions
            
        Requirements: 1.1
        """
        # Check app_id match
        if self.app_id != app_id:
            return False
        
        # Check context conditions
        return self.conditions.matches(context)
    
    def priority(self) -> int:
        """Return priority based on specificity (more conditions = higher priority).
        
        Priority is calculated as:
        - Base priority from condition specificity (0-3)
        - +10 if app_id is specified (app-specific profiles have higher priority)
        
        Returns:
            Priority value (higher = more specific)
            
        Requirements: 1.2
        """
        base_priority = self.conditions.specificity()
        # App-specific profiles have higher priority than global defaults
        if self.app_id is not None:
            base_priority += 10
        return base_priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for JSON serialization."""
        data = super().to_dict()
        data["conditions"] = self.conditions.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextualGameProfile":
        """Create ContextualGameProfile from dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            ContextualGameProfile instance
        """
        conditions_data = data.get("conditions", {})
        conditions = ContextCondition.from_dict(conditions_data) if conditions_data else ContextCondition()
        
        return cls(
            app_id=data.get("app_id", 0),
            name=data.get("name", "Unknown Game"),
            cores=data.get("cores", [0, 0, 0, 0]),
            dynamic_enabled=data.get("dynamic_enabled", False),
            dynamic_config=data.get("dynamic_config"),
            frequency_curves=data.get("frequency_curves"),
            created_at=data.get("created_at", ""),
            last_used=data.get("last_used"),
            conditions=conditions,
        )
    
    @classmethod
    def from_game_profile(cls, profile: GameProfile, conditions: Optional[ContextCondition] = None) -> "ContextualGameProfile":
        """Create ContextualGameProfile from an existing GameProfile.
        
        Args:
            profile: Existing GameProfile to convert
            conditions: Optional context conditions (defaults to empty)
            
        Returns:
            ContextualGameProfile instance
        """
        return cls(
            app_id=profile.app_id,
            name=profile.name,
            cores=profile.cores,
            dynamic_enabled=profile.dynamic_enabled,
            dynamic_config=profile.dynamic_config,
            frequency_curves=profile.frequency_curves,
            created_at=profile.created_at,
            last_used=profile.last_used,
            conditions=conditions or ContextCondition(),
        )


class ProfileManager:
    """Manager for per-game profiles with automatic switching.
    
    Handles CRUD operations, persistence, and profile application.
    Supports context-aware profile selection based on battery, power mode, and temperature.
    
    Requirements: 1.1, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4
    """
    
    STORAGE_KEY = "game_profiles"
    STORAGE_VERSION = "3.1"
    
    def __init__(
        self,
        settings_manager,
        ryzenadj: "RyzenadjWrapper",
        dynamic_controller: Optional["DynamicController"],
        event_emitter: "EventEmitter",
        core_settings_manager: Optional[Any] = None
    ):
        """Initialize the profile manager.
        
        Args:
            settings_manager: Decky settings manager instance
            ryzenadj: RyzenadjWrapper for applying undervolt values
            dynamic_controller: DynamicController for dynamic mode (optional)
            event_emitter: EventEmitter for status updates
            core_settings_manager: CoreSettingsManager for Apply on Startup tracking (optional)
        """
        self.settings = settings_manager
        self.ryzenadj = ryzenadj
        self.dynamic_controller = dynamic_controller
        self.event_emitter = event_emitter
        self.core_settings = core_settings_manager  # For Apply on Startup tracking
        
        # In-memory cache of profiles (keyed by app_id)
        self._profiles: Dict[int, GameProfile] = {}
        # Contextual profiles (list, since multiple can exist per app_id)
        self._contextual_profiles: List[ContextualGameProfile] = []
        self._global_default: Dict[str, Any] = {
            "cores": [0, 0, 0, 0],
            "dynamic_enabled": False,
            "dynamic_config": None
        }
        self._current_app_id: Optional[int] = None
        self._current_context: Optional[SystemContext] = None
        self._current_profile: Optional[ContextualGameProfile] = None
        
        # Context matcher for profile selection
        self._context_matcher = ContextMatcher()
        
        # Load profiles from settings
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load profiles from settings storage."""
        try:
            data = self.settings.get_setting(self.STORAGE_KEY, {})
            
            # Load global default
            if "global_default" in data:
                self._global_default = data["global_default"]
            
            # Load profiles (both legacy and contextual)
            profiles_list = data.get("profiles", [])
            for profile_data in profiles_list:
                # Check if this is a contextual profile (has conditions)
                if "conditions" in profile_data and profile_data["conditions"]:
                    profile = ContextualGameProfile.from_dict(profile_data)
                    if profile.is_valid():
                        self._contextual_profiles.append(profile)
                    else:
                        logger.warning(f"Skipping invalid contextual profile for app_id {profile.app_id}: {profile.validate()}")
                else:
                    # Legacy profile without conditions
                    profile = GameProfile.from_dict(profile_data)
                    if profile.is_valid():
                        self._profiles[profile.app_id] = profile
                    else:
                        logger.warning(f"Skipping invalid profile for app_id {profile.app_id}: {profile.validate()}")
            
            logger.info(f"Loaded {len(self._profiles)} game profiles and {len(self._contextual_profiles)} contextual profiles from settings")
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            # Initialize with empty profiles on error
            self._profiles = {}
            self._contextual_profiles = []
    
    def _save_profiles(self) -> bool:
        """Save profiles to settings storage.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert profiles to list (both legacy and contextual)
            profiles_list = [profile.to_dict() for profile in self._profiles.values()]
            profiles_list.extend([profile.to_dict() for profile in self._contextual_profiles])
            
            data = {
                "version": self.STORAGE_VERSION,
                "global_default": self._global_default,
                "profiles": profiles_list
            }
            
            self.settings.save_setting(self.STORAGE_KEY, data)
            logger.info(f"Saved {len(profiles_list)} profiles to settings")
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
        dynamic_config: Optional[Dict[str, Any]] = None,
        frequency_curves: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Optional[GameProfile]:
        """Create a new game profile.
        
        Args:
            app_id: Steam AppID
            name: Game name
            cores: Undervolt values for each core [core0, core1, core2, core3]
            dynamic_enabled: Whether dynamic mode is enabled
            dynamic_config: Dynamic mode configuration (required if dynamic_enabled is True)
            frequency_curves: Optional frequency curves for each core
            
        Returns:
            Created GameProfile if successful, None otherwise
            
        Requirements: 3.1, 3.5, 5.2, 8.1
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
            dynamic_config=dynamic_config,
            frequency_curves=frequency_curves
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
            current_cores = self.settings.get_setting("cores", [0, 0, 0, 0])
            
            # Get dynamic mode status
            dynamic_enabled = False
            dynamic_config = None
            
            if self.dynamic_controller:
                dynamic_enabled = self.dynamic_controller.is_running()
                if dynamic_enabled:
                    # Get current dynamic config from settings
                    dynamic_config = self.settings.get_setting("dynamic_config")
            
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

    async def create_contextual_profile(
        self,
        app_id: int,
        name: str,
        cores: List[int],
        conditions: ContextCondition,
        dynamic_enabled: bool = False,
        dynamic_config: Optional[Dict[str, Any]] = None,
        frequency_curves: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Optional[ContextualGameProfile]:
        """Create a new contextual game profile.
        
        Contextual profiles can have the same app_id but different conditions,
        allowing multiple profiles per game for different contexts.
        
        Args:
            app_id: Steam AppID
            name: Profile name
            cores: Undervolt values for each core [core0, core1, core2, core3]
            conditions: Context conditions for activation
            dynamic_enabled: Whether dynamic mode is enabled
            dynamic_config: Dynamic mode configuration (required if dynamic_enabled is True)
            frequency_curves: Optional frequency curves for each core
            
        Returns:
            Created ContextualGameProfile if successful, None otherwise
            
        Requirements: 1.1, 8.1
        """
        # Create profile
        profile = ContextualGameProfile(
            app_id=app_id,
            name=name,
            cores=cores,
            dynamic_enabled=dynamic_enabled,
            dynamic_config=dynamic_config,
            frequency_curves=frequency_curves,
            conditions=conditions
        )
        
        # Validate profile
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid contextual profile: {errors}")
            return None
        
        # Store profile
        self._contextual_profiles.append(profile)
        self._save_profiles()
        
        logger.info(f"Created contextual profile '{name}' (app_id: {app_id}, conditions: {conditions})")
        return profile

    
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
    
    def get_contextual_profiles(self, app_id: Optional[int] = None) -> List[ContextualGameProfile]:
        """Get contextual profiles, optionally filtered by app_id.
        
        Args:
            app_id: Optional Steam AppID to filter by
            
        Returns:
            List of ContextualGameProfile instances
            
        Requirements: 1.1
        """
        if app_id is None:
            return list(self._contextual_profiles)
        return [p for p in self._contextual_profiles if p.app_id == app_id]
    
    def get_all_contextual_profiles(self) -> List[ContextualGameProfile]:
        """Get all contextual profiles.
        
        Returns:
            List of all ContextualGameProfile instances
            
        Requirements: 1.1
        """
        return list(self._contextual_profiles)
    
    async def update_contextual_profile(
        self,
        profile_name: str,
        app_id: int,
        **kwargs
    ) -> bool:
        """Update an existing contextual profile.
        
        Args:
            profile_name: Name of the profile to update
            app_id: Steam AppID of the profile
            **kwargs: Fields to update (name, cores, dynamic_enabled, dynamic_config, conditions)
            
        Returns:
            True if updated successfully, False otherwise
            
        Requirements: 1.1
        """
        # Find the profile
        profile = None
        for p in self._contextual_profiles:
            if p.name == profile_name and p.app_id == app_id:
                profile = p
                break
        
        if not profile:
            logger.warning(f"Contextual profile '{profile_name}' for app_id {app_id} not found")
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
        if "conditions" in kwargs:
            profile.conditions = kwargs["conditions"]
        
        # Validate updated profile
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid contextual profile after update: {errors}")
            return False
        
        # Save changes
        self._save_profiles()
        
        # If this is the currently active profile, re-evaluate
        if self._current_profile and self._current_profile.name == profile_name:
            await self._reevaluate_profile()
        
        logger.info(f"Updated contextual profile '{profile_name}' for app_id {app_id}")
        return True
    
    async def delete_contextual_profile(self, profile_name: str, app_id: int) -> bool:
        """Delete a contextual profile.
        
        Args:
            profile_name: Name of the profile to delete
            app_id: Steam AppID of the profile
            
        Returns:
            True if deleted successfully, False if not found
            
        Requirements: 1.1
        """
        # Find and remove the profile
        for i, p in enumerate(self._contextual_profiles):
            if p.name == profile_name and p.app_id == app_id:
                is_active = (self._current_profile and 
                           self._current_profile.name == profile_name and
                           self._current_profile.app_id == app_id)
                
                del self._contextual_profiles[i]
                self._save_profiles()
                
                # If it was active, re-evaluate
                if is_active:
                    await self._reevaluate_profile()
                
                logger.info(f"Deleted contextual profile '{profile_name}' for app_id {app_id}")
                return True
        
        logger.warning(f"Contextual profile '{profile_name}' for app_id {app_id} not found")
        return False
    
    async def update_profile(
        self,
        app_id: int,
        **kwargs
    ) -> bool:
        """Update an existing profile.
        
        Args:
            app_id: Steam AppID of profile to update
            **kwargs: Fields to update (name, cores, dynamic_enabled, dynamic_config, frequency_curves)
            
        Returns:
            True if updated successfully, False otherwise
            
        Requirements: 3.3, 8.1
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
        if "frequency_curves" in kwargs:
            profile.frequency_curves = kwargs["frequency_curves"]
        
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
        
        Applies the undervolt values, frequency curves, and starts/stops dynamic mode as needed.
        Emits an event to the frontend with the active profile name.
        
        Args:
            app_id: Steam AppID of profile to apply
            
        Returns:
            True if applied successfully, False otherwise
            
        Requirements: 4.2, 4.4, 8.2
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
            
            # Apply frequency curves if present
            if profile.frequency_curves:
                await self._apply_frequency_curves(profile.frequency_curves)
            
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
            
            # Update last active profile for Apply on Startup
            # Feature: ui-refactor-settings, Validates: Requirements 4.2
            if self.core_settings:
                try:
                    self.core_settings.save_setting("last_active_profile", str(app_id))
                    logger.debug(f"Updated last_active_profile to {app_id}")
                except Exception as e:
                    logger.warning(f"Failed to update last_active_profile: {e}")
            
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
        self._current_app_id = app_id
        
        # If no game is running, apply global default
        if app_id is None:
            await self.apply_global_default()
            return
        
        # Try context-aware profile selection first
        if self._contextual_profiles:
            await self._reevaluate_profile()
        else:
            # Fall back to legacy profile selection
            profile = self._profiles.get(app_id)
            
            if profile:
                # Apply specific profile
                await self.apply_profile(app_id)
            else:
                # No profile found, apply global default
                logger.info(f"No profile found for app_id {app_id}, using global default")
                await self.apply_global_default()
    
    # ==================== Context Monitoring ====================
    
    async def on_battery_change(self, battery_percent: int) -> None:
        """Handle battery level change event.
        
        Called when battery level changes. Re-evaluates active profile
        if the change crosses a threshold.
        
        Args:
            battery_percent: New battery percentage (0-100)
            
        Requirements: 1.3
        """
        if self._current_context is None:
            self._current_context = SystemContext(
                battery_percent=battery_percent,
                power_mode="battery",
                temperature_c=50
            )
        else:
            old_battery = self._current_context.battery_percent
            self._current_context.battery_percent = battery_percent
            
            # Check if we crossed any threshold
            if self._has_crossed_battery_threshold(old_battery, battery_percent):
                logger.info(f"Battery crossed threshold: {old_battery}% -> {battery_percent}%")
                await self._reevaluate_profile()
    
    async def on_power_mode_change(self, power_mode: str) -> None:
        """Handle power mode change event.
        
        Called when power mode changes (AC plugged/unplugged).
        Re-evaluates active profile.
        
        Args:
            power_mode: New power mode ("ac" or "battery")
            
        Requirements: 1.4
        """
        if power_mode not in ("ac", "battery"):
            logger.warning(f"Invalid power mode: {power_mode}")
            return
        
        if self._current_context is None:
            self._current_context = SystemContext(
                battery_percent=100,
                power_mode=power_mode,
                temperature_c=50
            )
        else:
            old_mode = self._current_context.power_mode
            if old_mode != power_mode:
                self._current_context.power_mode = power_mode
                logger.info(f"Power mode changed: {old_mode} -> {power_mode}")
                await self._reevaluate_profile()
    
    async def on_temperature_change(self, temperature_c: int) -> None:
        """Handle temperature change event.
        
        Called when CPU temperature changes significantly.
        Re-evaluates active profile if the change crosses a threshold.
        
        Args:
            temperature_c: New temperature in Celsius
            
        Requirements: 1.1
        """
        if self._current_context is None:
            self._current_context = SystemContext(
                battery_percent=100,
                power_mode="battery",
                temperature_c=temperature_c
            )
        else:
            old_temp = self._current_context.temperature_c
            self._current_context.temperature_c = temperature_c
            
            # Check if we crossed any threshold
            if self._has_crossed_temp_threshold(old_temp, temperature_c):
                logger.info(f"Temperature crossed threshold: {old_temp}°C -> {temperature_c}°C")
                await self._reevaluate_profile()
    
    async def update_context(self, context: SystemContext) -> None:
        """Update the current system context and re-evaluate profile if needed.
        
        Args:
            context: New system context
            
        Requirements: 1.3, 1.4
        """
        old_context = self._current_context
        self._current_context = context
        
        # Check if context changed in a way that requires re-evaluation
        if old_context is None or self._context_changed_significantly(old_context, context):
            await self._reevaluate_profile()
    
    def get_current_context(self) -> Optional[SystemContext]:
        """Get the current system context.
        
        Returns:
            Current SystemContext or None if not set
        """
        return self._current_context
    
    def get_active_profile(self) -> Optional[ContextualGameProfile]:
        """Get the currently active contextual profile.
        
        Returns:
            Active ContextualGameProfile or None
        """
        return self._current_profile
    
    def _has_crossed_battery_threshold(self, old_value: int, new_value: int) -> bool:
        """Check if battery change crossed any profile threshold.
        
        Args:
            old_value: Previous battery percentage
            new_value: New battery percentage
            
        Returns:
            True if a threshold was crossed
        """
        # Get all battery thresholds from contextual profiles
        thresholds = set()
        for profile in self._contextual_profiles:
            if profile.conditions.battery_threshold is not None:
                thresholds.add(profile.conditions.battery_threshold)
        
        # Check if we crossed any threshold
        for threshold in thresholds:
            if (old_value > threshold >= new_value) or (old_value <= threshold < new_value):
                return True
        
        return False
    
    def _has_crossed_temp_threshold(self, old_value: int, new_value: int) -> bool:
        """Check if temperature change crossed any profile threshold.
        
        Args:
            old_value: Previous temperature
            new_value: New temperature
            
        Returns:
            True if a threshold was crossed
        """
        # Get all temperature thresholds from contextual profiles
        thresholds = set()
        for profile in self._contextual_profiles:
            if profile.conditions.temp_threshold is not None:
                thresholds.add(profile.conditions.temp_threshold)
        
        # Check if we crossed any threshold
        for threshold in thresholds:
            if (old_value < threshold <= new_value) or (old_value >= threshold > new_value):
                return True
        
        return False
    
    def _context_changed_significantly(self, old: SystemContext, new: SystemContext) -> bool:
        """Check if context changed in a way that requires profile re-evaluation.
        
        Args:
            old: Previous context
            new: New context
            
        Returns:
            True if re-evaluation is needed
        """
        # Power mode change always triggers re-evaluation
        if old.power_mode != new.power_mode:
            return True
        
        # Check battery threshold crossing
        if self._has_crossed_battery_threshold(old.battery_percent, new.battery_percent):
            return True
        
        # Check temperature threshold crossing
        if self._has_crossed_temp_threshold(old.temperature_c, new.temperature_c):
            return True
        
        return False
    
    async def _reevaluate_profile(self) -> None:
        """Re-evaluate and apply the best matching profile for current context.
        
        Called when context changes or app changes. Finds the best matching
        profile and applies it if different from current.
        
        Requirements: 1.2, 1.3, 1.4, 1.5
        """
        # Ensure we have a context
        if self._current_context is None:
            self._current_context = await SystemContext.read_current()
        
        # Convert contextual profiles to the format expected by ContextMatcher
        from .context import ContextualProfile as ContextMatcherProfile
        
        matcher_profiles = []
        for p in self._contextual_profiles:
            matcher_profiles.append(ContextMatcherProfile(
                app_id=p.app_id,
                name=p.name,
                cores=p.cores,
                dynamic_enabled=p.dynamic_enabled,
                dynamic_config=p.dynamic_config,
                conditions=p.conditions,
                created_at=p.created_at,
            ))
        
        # Create global default as a ContextualProfile for fallback
        global_default = ContextMatcherProfile(
            app_id=None,
            name="Global Default",
            cores=self._global_default.get("cores", [0, 0, 0, 0]),
            dynamic_enabled=self._global_default.get("dynamic_enabled", False),
            dynamic_config=self._global_default.get("dynamic_config"),
            conditions=ContextCondition(),
        )
        
        # Find best matching profile
        best_match = self._context_matcher.find_best_match(
            app_id=self._current_app_id,
            context=self._current_context,
            profiles=matcher_profiles,
            global_default=global_default,
        )
        
        if best_match is None:
            # No match found, apply global default
            await self.apply_global_default()
            return
        
        # Check if profile changed
        if self._current_profile is not None:
            if (self._current_profile.name == best_match.name and 
                self._current_profile.app_id == best_match.app_id):
                # Same profile, no change needed
                return
        
        # Apply the new profile
        await self._apply_contextual_profile(best_match)
    
    async def _apply_contextual_profile(self, profile) -> bool:
        """Apply a contextual profile's settings.
        
        Args:
            profile: ContextualProfile (from context.py) to apply
            
        Returns:
            True if applied successfully, False otherwise
            
        Requirements: 1.1, 4.2, 4.4, 8.2
        """
        try:
            # Apply undervolt values
            success, error = await self.ryzenadj.apply_values_async(profile.cores)
            if not success:
                logger.error(f"Failed to apply undervolt values: {error}")
                return False
            
            # Apply frequency curves if present (find the corresponding ContextualGameProfile)
            for p in self._contextual_profiles:
                if p.name == profile.name and p.app_id == profile.app_id:
                    if p.frequency_curves:
                        await self._apply_frequency_curves(p.frequency_curves)
                    break
            
            # Handle dynamic mode
            if self.dynamic_controller:
                if profile.dynamic_enabled and profile.dynamic_config:
                    logger.info(f"Dynamic mode enabled for profile '{profile.name}'")
                    # TODO: await self.dynamic_controller.start(profile.dynamic_config)
                else:
                    if self.dynamic_controller.is_running():
                        await self.dynamic_controller.stop()
                        logger.info(f"Dynamic mode disabled for profile '{profile.name}'")
            
            # Update current profile tracking
            # Find the corresponding ContextualGameProfile
            for p in self._contextual_profiles:
                if p.name == profile.name and p.app_id == profile.app_id:
                    self._current_profile = p
                    p.last_used = datetime.now(timezone.utc).isoformat()
                    self._save_profiles()
                    break
            else:
                # It's the global default
                self._current_profile = None
            
            # Emit event to frontend
            await self.event_emitter.emit_profile_changed(profile.name, profile.app_id)
            
            # Emit context change event
            await self.event_emitter.emit_context_changed(
                self._current_context.to_dict() if self._current_context else {}
            )
            
            logger.info(f"Applied contextual profile '{profile.name}' (app_id: {profile.app_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply contextual profile: {e}")
            return False
    
    async def _apply_frequency_curves(self, frequency_curves: Dict[int, Dict[str, Any]]) -> None:
        """Apply frequency curves to the frequency controller.
        
        Args:
            frequency_curves: Dictionary mapping core_id to serialized FrequencyCurve data
            
        Requirements: 8.2
        """
        try:
            # Use the core_settings manager if available
            if not hasattr(self, 'core_settings') or not self.core_settings:
                logger.debug("No core settings manager available, skipping curve application")
                return
            
            settings_mgr = self.core_settings
            
            # Check if frequency mode is enabled
            frequency_mode_enabled = settings_mgr.load_setting("frequency_mode_enabled", False)
            
            if not frequency_mode_enabled:
                logger.debug("Frequency mode not enabled, skipping curve application")
                return
            
            # Deserialize and validate curves
            curves = {}
            for core_id_str, curve_data in frequency_curves.items():
                try:
                    core_id = int(core_id_str)
                    curve = FrequencyCurve.from_dict(curve_data)
                    curve.validate()
                    curves[core_id] = curve
                    logger.debug(f"Loaded frequency curve for core {core_id}")
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to load frequency curve for core {core_id_str}: {e}")
                    continue
            
            # Apply curves through the frequency controller (via Rust)
            # This would typically be done through an RPC call or direct controller access
            # For now, we'll save them to settings so the Rust controller can pick them up
            settings_mgr.save_setting("frequency_curves", {
                str(core_id): curve.to_dict() for core_id, curve in curves.items()
            })
            
            logger.info(f"Applied {len(curves)} frequency curves from profile")
            
        except Exception as e:
            logger.error(f"Failed to apply frequency curves: {e}")
    
    # ==================== Import/Export ====================
    
    def export_profiles(self) -> str:
        """Export all profiles as JSON string.
        
        Includes version metadata, frequency curves, and all profiles formatted 
        with indentation for readability.
        
        Returns:
            JSON string containing all profiles
            
        Requirements: 9.1, 8.3
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
        
        Validates JSON structure, required fields, and frequency curves. Supports 
        merge strategies for handling conflicts with existing profiles.
        
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
            
        Requirements: 9.2, 9.3, 9.4, 8.4
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
                    
                    # Validate profile (this will also validate frequency curves)
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
