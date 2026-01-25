"""Profile management for dynamic mode configurations.

This module provides a complete profile management system for dynamic mode,
allowing users to save, load, and switch between different configurations.

Feature: dynamic-mode-refactor
Validates: Requirements 16.1-16.6

# Profile System Overview

Profiles are named configurations that can be:
- Created, updated, deleted, and duplicated
- Exported/imported as JSON for sharing
- Persisted to disk for long-term storage
- Validated before use to ensure correctness

# Default Profiles

The system provides four built-in profiles:

1. **Battery Saver**: Conservative settings for maximum battery life
   - Strategy: conservative (5s ramp)
   - Sample interval: 200ms
   - Hysteresis: 10%
   - Undervolt range: -15mV to -25mV

2. **Balanced**: Default settings for everyday use
   - Strategy: balanced (2s ramp)
   - Sample interval: 100ms
   - Hysteresis: 5%
   - Undervolt range: -20mV to -30mV

3. **Performance**: Aggressive settings for maximum performance
   - Strategy: aggressive (500ms ramp)
   - Sample interval: 50ms
   - Hysteresis: 3%
   - Undervolt range: -25mV to -35mV

4. **Silent**: Optimized for quiet fan operation
   - Strategy: conservative (5s ramp)
   - Sample interval: 250ms
   - Hysteresis: 15%
   - Undervolt range: -20mV to -35mV

# Storage Format

Profiles are stored as JSON in a single file:
```json
{
  "profiles": {
    "My Profile": {
      "name": "My Profile",
      "description": "Custom profile for gaming",
      "config": { ... },
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-01-15T10:30:00Z"
    }
  }
}
```

# Usage Example

```python
from backend.dynamic.profiles import ProfileManager, DynamicProfile
from backend.dynamic.config import DynamicConfig

# Initialize manager with storage path
manager = ProfileManager(storage_path=Path("profiles.json"))

# List available profiles
profiles = manager.list_profiles()
print(f"Available: {profiles}")

# Get a profile
profile = manager.get_profile("Balanced")
if profile:
    # Use the configuration
    config = profile.config
    await controller.start(config)

# Create a custom profile
custom_profile = DynamicProfile(
    name="My Gaming Profile",
    description="Optimized for AAA games",
    config=DynamicConfig(strategy="aggressive", ...)
)
manager.create_profile(custom_profile)

# Export for sharing
json_str = manager.export_profile("My Gaming Profile")
send_to_friend(json_str)

# Import from friend
manager.import_profile(received_json)
```

# Thread Safety

ProfileManager is NOT thread-safe. If used in a multi-threaded environment,
external synchronization is required.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from .config import DynamicConfig, CoreConfig

logger = logging.getLogger(__name__)


@dataclass
class DynamicProfile:
    """A named dynamic mode configuration profile.
    
    Attributes:
        name: Profile display name
        description: Optional description of the profile
        config: The dynamic mode configuration
        created_at: ISO timestamp when profile was created
        updated_at: ISO timestamp when profile was last updated
    """
    name: str
    description: str = ""
    config: DynamicConfig = field(default_factory=DynamicConfig)
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        """Set timestamps if not provided."""
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "config": self.config.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicProfile":
        """Create DynamicProfile from dictionary."""
        config_data = data.get("config", {})
        config = DynamicConfig.from_dict(config_data)
        
        return cls(
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            config=config,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
    
    def validate(self) -> List[str]:
        """Validate the profile.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Profile name cannot be empty")
        
        if len(self.name) > 64:
            errors.append("Profile name must be 64 characters or less")
        
        # Validate the config
        config_errors = self.config.validate()
        for err in config_errors:
            errors.append(f"config: {err}")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if profile is valid."""
        return len(self.validate()) == 0


def _create_default_profiles() -> Dict[str, DynamicProfile]:
    """Create the default profiles.
    
    Returns:
        Dictionary of default profiles keyed by name
    """
    profiles = {}
    
    # Battery Saver - Conservative settings for maximum battery life
    profiles["Battery Saver"] = DynamicProfile(
        name="Battery Saver",
        description="Conservative settings for maximum battery life",
        config=DynamicConfig(
            strategy="conservative",
            sample_interval_ms=200,
            hysteresis_percent=10.0,
            status_interval_ms=2000,
            expert_mode=False,
            cores=[
                CoreConfig(min_mv=-15, max_mv=-25, threshold=60.0),
                CoreConfig(min_mv=-15, max_mv=-25, threshold=60.0),
                CoreConfig(min_mv=-15, max_mv=-25, threshold=60.0),
                CoreConfig(min_mv=-15, max_mv=-25, threshold=60.0),
            ],
        ),
    )
    
    # Balanced - Default balanced settings
    profiles["Balanced"] = DynamicProfile(
        name="Balanced",
        description="Balanced settings for everyday use",
        config=DynamicConfig(
            strategy="balanced",
            sample_interval_ms=100,
            hysteresis_percent=5.0,
            status_interval_ms=1000,
            expert_mode=False,
            cores=[
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
            ],
        ),
    )
    
    # Performance - Aggressive settings for maximum performance
    profiles["Performance"] = DynamicProfile(
        name="Performance",
        description="Aggressive settings for maximum performance",
        config=DynamicConfig(
            strategy="aggressive",
            sample_interval_ms=50,
            hysteresis_percent=3.0,
            status_interval_ms=500,
            expert_mode=False,
            cores=[
                CoreConfig(min_mv=-25, max_mv=-35, threshold=40.0),
                CoreConfig(min_mv=-25, max_mv=-35, threshold=40.0),
                CoreConfig(min_mv=-25, max_mv=-35, threshold=40.0),
                CoreConfig(min_mv=-25, max_mv=-35, threshold=40.0),
            ],
        ),
    )
    
    # Silent - Optimized for quiet operation
    profiles["Silent"] = DynamicProfile(
        name="Silent",
        description="Optimized for quiet fan operation",
        config=DynamicConfig(
            strategy="conservative",
            sample_interval_ms=250,
            hysteresis_percent=15.0,
            status_interval_ms=2000,
            expert_mode=False,
            cores=[
                CoreConfig(min_mv=-20, max_mv=-35, threshold=70.0),
                CoreConfig(min_mv=-20, max_mv=-35, threshold=70.0),
                CoreConfig(min_mv=-20, max_mv=-35, threshold=70.0),
                CoreConfig(min_mv=-20, max_mv=-35, threshold=70.0),
            ],
        ),
    )
    
    return profiles


class ProfileManager:
    """Manager for dynamic mode profiles.
    
    Handles CRUD operations, persistence, and default profiles.
    
    Requirements: 16.1-16.6
    """
    
    DEFAULT_PROFILE_NAMES = frozenset(["Battery Saver", "Balanced", "Performance", "Silent"])
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the profile manager.
        
        Args:
            storage_path: Path to store profiles JSON file.
                         If None, profiles are only kept in memory.
        """
        self._storage_path = storage_path
        self._profiles: Dict[str, DynamicProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load profiles from storage or create defaults."""
        # Start with default profiles
        self._profiles = _create_default_profiles()
        
        # Load user profiles from storage if available
        if self._storage_path and self._storage_path.exists():
            try:
                with open(self._storage_path, "r") as f:
                    data = json.load(f)
                
                user_profiles = data.get("profiles", {})
                for name, profile_data in user_profiles.items():
                    # Don't overwrite default profiles with stored versions
                    # unless they were explicitly modified
                    if name not in self.DEFAULT_PROFILE_NAMES or profile_data.get("_modified"):
                        profile = DynamicProfile.from_dict(profile_data)
                        self._profiles[name] = profile
                
                logger.info(f"Loaded {len(user_profiles)} profiles from {self._storage_path}")
            except Exception as e:
                logger.error(f"Failed to load profiles: {e}")
    
    def _save_profiles(self) -> bool:
        """Save profiles to storage.
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self._storage_path:
            return True
        
        try:
            # Ensure parent directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize profiles
            profiles_data = {}
            for name, profile in self._profiles.items():
                profile_dict = profile.to_dict()
                # Mark modified default profiles
                if name in self.DEFAULT_PROFILE_NAMES:
                    profile_dict["_modified"] = True
                profiles_data[name] = profile_dict
            
            data = {"profiles": profiles_data}
            
            with open(self._storage_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(profiles_data)} profiles to {self._storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """Get list of all profile names.
        
        Returns:
            List of profile names
        """
        return list(self._profiles.keys())
    
    def get_profile(self, name: str) -> Optional[DynamicProfile]:
        """Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            DynamicProfile if found, None otherwise
        """
        return self._profiles.get(name)
    
    def create_profile(self, profile: DynamicProfile) -> bool:
        """Create a new profile.
        
        Args:
            profile: Profile to create
            
        Returns:
            True if created successfully, False if name already exists or invalid
        """
        if profile.name in self._profiles:
            logger.warning(f"Profile '{profile.name}' already exists")
            return False
        
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid profile: {errors}")
            return False
        
        self._profiles[profile.name] = profile
        self._save_profiles()
        logger.info(f"Created profile '{profile.name}'")
        return True
    
    def update_profile(self, name: str, profile: DynamicProfile) -> bool:
        """Update an existing profile.
        
        Args:
            name: Name of profile to update
            profile: New profile data
            
        Returns:
            True if updated successfully, False otherwise
        """
        if name not in self._profiles:
            logger.warning(f"Profile '{name}' not found")
            return False
        
        errors = profile.validate()
        if errors:
            logger.error(f"Invalid profile: {errors}")
            return False
        
        # Update timestamp
        profile.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Handle rename
        if name != profile.name:
            if profile.name in self._profiles:
                logger.warning(f"Cannot rename to '{profile.name}': name already exists")
                return False
            del self._profiles[name]
        
        self._profiles[profile.name] = profile
        self._save_profiles()
        logger.info(f"Updated profile '{profile.name}'")
        return True
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile.
        
        Note: Default profiles can be deleted but will be recreated on next load.
        
        Args:
            name: Name of profile to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if name not in self._profiles:
            logger.warning(f"Profile '{name}' not found")
            return False
        
        del self._profiles[name]
        self._save_profiles()
        logger.info(f"Deleted profile '{name}'")
        return True
    
    def duplicate_profile(self, name: str, new_name: str) -> Optional[DynamicProfile]:
        """Duplicate an existing profile with a new name.
        
        Args:
            name: Name of profile to duplicate
            new_name: Name for the new profile
            
        Returns:
            New DynamicProfile if successful, None otherwise
        """
        if name not in self._profiles:
            logger.warning(f"Profile '{name}' not found")
            return None
        
        if new_name in self._profiles:
            logger.warning(f"Profile '{new_name}' already exists")
            return None
        
        if not new_name or not new_name.strip():
            logger.warning("New profile name cannot be empty")
            return None
        
        original = self._profiles[name]
        
        # Create a deep copy of the config
        config_dict = original.config.to_dict()
        new_config = DynamicConfig.from_dict(config_dict)
        
        new_profile = DynamicProfile(
            name=new_name,
            description=f"Copy of {original.name}",
            config=new_config,
        )
        
        self._profiles[new_name] = new_profile
        self._save_profiles()
        logger.info(f"Duplicated profile '{name}' as '{new_name}'")
        return new_profile
    
    def export_profile(self, name: str) -> Optional[str]:
        """Export a profile as JSON string.
        
        Args:
            name: Name of profile to export
            
        Returns:
            JSON string if successful, None otherwise
        """
        profile = self._profiles.get(name)
        if not profile:
            logger.warning(f"Profile '{name}' not found")
            return None
        
        return json.dumps(profile.to_dict(), indent=2)
    
    def import_profile(self, json_str: str, overwrite: bool = False) -> Optional[DynamicProfile]:
        """Import a profile from JSON string.
        
        Args:
            json_str: JSON string containing profile data
            overwrite: If True, overwrite existing profile with same name
            
        Returns:
            Imported DynamicProfile if successful, None otherwise
        """
        try:
            data = json.loads(json_str)
            profile = DynamicProfile.from_dict(data)
            
            errors = profile.validate()
            if errors:
                logger.error(f"Invalid profile data: {errors}")
                return None
            
            if profile.name in self._profiles and not overwrite:
                logger.warning(f"Profile '{profile.name}' already exists (use overwrite=True)")
                return None
            
            # Reset timestamps for imported profile
            now = datetime.now(timezone.utc).isoformat()
            profile.created_at = now
            profile.updated_at = now
            
            self._profiles[profile.name] = profile
            self._save_profiles()
            logger.info(f"Imported profile '{profile.name}'")
            return profile
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return None
    
    def export_all_profiles(self) -> str:
        """Export all profiles as JSON string.
        
        Returns:
            JSON string containing all profiles
        """
        profiles_data = {
            name: profile.to_dict()
            for name, profile in self._profiles.items()
        }
        return json.dumps({"profiles": profiles_data}, indent=2)
    
    def import_all_profiles(self, json_str: str, overwrite: bool = False) -> int:
        """Import multiple profiles from JSON string.
        
        Args:
            json_str: JSON string containing profiles data
            overwrite: If True, overwrite existing profiles
            
        Returns:
            Number of profiles successfully imported
        """
        try:
            data = json.loads(json_str)
            profiles_data = data.get("profiles", {})
            
            imported = 0
            for name, profile_data in profiles_data.items():
                profile = DynamicProfile.from_dict(profile_data)
                
                errors = profile.validate()
                if errors:
                    logger.warning(f"Skipping invalid profile '{name}': {errors}")
                    continue
                
                if profile.name in self._profiles and not overwrite:
                    logger.warning(f"Skipping existing profile '{profile.name}'")
                    continue
                
                self._profiles[profile.name] = profile
                imported += 1
            
            if imported > 0:
                self._save_profiles()
            
            logger.info(f"Imported {imported} profiles")
            return imported
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return 0
        except Exception as e:
            logger.error(f"Failed to import profiles: {e}")
            return 0
    
    def reset_to_defaults(self) -> None:
        """Reset all profiles to defaults, removing user profiles."""
        self._profiles = _create_default_profiles()
        self._save_profiles()
        logger.info("Reset profiles to defaults")
