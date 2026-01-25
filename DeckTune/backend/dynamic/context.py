"""Context conditions and matching for contextual profile activation.

This module provides context-aware profile selection based on system state
(battery level, power mode, temperature). Profiles can specify conditions
that must be met for activation, enabling automatic profile switching
based on environmental factors.

Feature: decktune-3.0-automation
Validates: Requirements 1.1, 1.2, 1.5

# Context System Overview

The context system extends per-game profiles with environmental conditions:
- Battery threshold: Profile activates when battery <= threshold
- Power mode: Profile activates when power mode matches (ac/battery)
- Temperature threshold: Profile activates when temperature >= threshold

# Priority and Specificity

When multiple profiles match the current context, the most specific one wins:
- More conditions = higher specificity
- Ties broken by creation timestamp (newer wins)

# Fallback Chain

If no profile matches all conditions:
1. Try profiles matching only AppID
2. Fall back to global default

# Usage Example

```python
from backend.dynamic.context import ContextCondition, SystemContext, ContextMatcher

# Create a condition for battery saver mode
condition = ContextCondition(
    battery_threshold=30,
    power_mode="battery",
    temp_threshold=None
)

# Read current system context
context = await SystemContext.read_current()

# Check if condition matches
if condition.matches(context):
    print("Battery saver conditions met!")

# Find best matching profile
matcher = ContextMatcher()
best_profile = matcher.find_best_match(app_id=1091500, context=context, profiles=profiles)
```
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .profile_manager import GameProfile

logger = logging.getLogger(__name__)


@dataclass
class ContextCondition:
    """A single context condition for profile activation.
    
    Conditions are optional - None means "any value matches".
    All specified conditions must be met for the condition to match.
    
    Attributes:
        battery_threshold: Profile active when battery <= threshold (0-100%)
        power_mode: Profile active when power mode matches ("ac", "battery", or None for any)
        temp_threshold: Profile active when temperature >= threshold (0-100°C)
    
    Requirements: 1.1
    """
    battery_threshold: Optional[int] = None  # 0-100, profile active when battery <= threshold
    power_mode: Optional[str] = None         # "ac", "battery", or None (any)
    temp_threshold: Optional[int] = None     # 0-100°C, profile active when temp >= threshold
    
    def matches(self, context: "SystemContext") -> bool:
        """Check if this condition matches the current context.
        
        A condition matches if ALL specified (non-None) conditions are satisfied:
        - battery_threshold: context.battery_percent <= battery_threshold
        - power_mode: context.power_mode == power_mode
        - temp_threshold: context.temperature_c >= temp_threshold
        
        Args:
            context: Current system context to match against
            
        Returns:
            True if all specified conditions match, False otherwise
            
        Requirements: 1.1
        """
        # Check battery threshold (profile active when battery <= threshold)
        if self.battery_threshold is not None:
            if context.battery_percent > self.battery_threshold:
                return False
        
        # Check power mode (exact match required)
        if self.power_mode is not None:
            if context.power_mode != self.power_mode:
                return False
        
        # Check temperature threshold (profile active when temp >= threshold)
        if self.temp_threshold is not None:
            if context.temperature_c < self.temp_threshold:
                return False
        
        return True
    
    def specificity(self) -> int:
        """Return number of non-None conditions (higher = more specific).
        
        Used for priority ordering when multiple profiles match.
        
        Returns:
            Count of specified (non-None) conditions
            
        Requirements: 1.2
        """
        count = 0
        if self.battery_threshold is not None:
            count += 1
        if self.power_mode is not None:
            count += 1
        if self.temp_threshold is not None:
            count += 1
        return count
    
    def to_dict(self) -> dict:
        """Convert condition to dictionary for JSON serialization."""
        return {
            "battery_threshold": self.battery_threshold,
            "power_mode": self.power_mode,
            "temp_threshold": self.temp_threshold,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ContextCondition":
        """Create ContextCondition from dictionary.
        
        Args:
            data: Dictionary containing condition data
            
        Returns:
            ContextCondition instance
        """
        return cls(
            battery_threshold=data.get("battery_threshold"),
            power_mode=data.get("power_mode"),
            temp_threshold=data.get("temp_threshold"),
        )


@dataclass
class SystemContext:
    """Current system state for profile matching.
    
    Represents the current environmental conditions that are used
    to determine which contextual profile should be active.
    
    Attributes:
        battery_percent: Current battery level (0-100)
        power_mode: Current power mode ("ac" or "battery")
        temperature_c: Current CPU temperature in Celsius
    
    Requirements: 1.1, 1.3, 1.4
    """
    battery_percent: int      # 0-100
    power_mode: str           # "ac" or "battery"
    temperature_c: int        # Current CPU temperature
    
    # System paths for reading context (Steam Deck specific)
    BATTERY_CAPACITY_PATH = "/sys/class/power_supply/BAT1/capacity"
    AC_ADAPTER_PATH = "/sys/class/power_supply/ADP1/online"
    THERMAL_ZONE_PATH = "/sys/class/thermal/thermal_zone0/temp"
    
    # Alternative paths for different systems
    ALT_BATTERY_PATHS = [
        "/sys/class/power_supply/BAT0/capacity",
        "/sys/class/power_supply/battery/capacity",
    ]
    ALT_AC_PATHS = [
        "/sys/class/power_supply/AC/online",
        "/sys/class/power_supply/ACAD/online",
    ]
    ALT_THERMAL_PATHS = [
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/thermal/thermal_zone2/temp",
    ]
    
    @classmethod
    async def read_current(cls) -> "SystemContext":
        """Read current system context from hardware.
        
        Reads battery level, power mode, and temperature from system files.
        Uses safe defaults if reading fails.
        
        Returns:
            SystemContext with current system state
            
        Requirements: 1.3, 1.4
        """
        battery_percent = await cls._read_battery_percent()
        power_mode = await cls._read_power_mode()
        temperature_c = await cls._read_temperature()
        
        return cls(
            battery_percent=battery_percent,
            power_mode=power_mode,
            temperature_c=temperature_c,
        )
    
    @classmethod
    def read_current_sync(cls) -> "SystemContext":
        """Read current system context from hardware (synchronous version).
        
        Reads battery level, power mode, and temperature from system files.
        Uses safe defaults if reading fails.
        
        Returns:
            SystemContext with current system state
            
        Requirements: 1.3, 1.4
        """
        battery_percent = cls._read_battery_percent_sync()
        power_mode = cls._read_power_mode_sync()
        temperature_c = cls._read_temperature_sync()
        
        return cls(
            battery_percent=battery_percent,
            power_mode=power_mode,
            temperature_c=temperature_c,
        )
    
    @classmethod
    async def _read_battery_percent(cls) -> int:
        """Read battery percentage from system.
        
        Returns:
            Battery percentage (0-100), defaults to 100 on error
        """
        return cls._read_battery_percent_sync()
    
    @classmethod
    def _read_battery_percent_sync(cls) -> int:
        """Read battery percentage from system (synchronous).
        
        Tries primary path first, then alternative paths.
        
        Returns:
            Battery percentage (0-100), defaults to 100 on error
        """
        paths_to_try = [cls.BATTERY_CAPACITY_PATH] + cls.ALT_BATTERY_PATHS
        
        for path in paths_to_try:
            try:
                with open(path, "r") as f:
                    value = int(f.read().strip())
                    # Clamp to valid range
                    return max(0, min(100, value))
            except (IOError, ValueError):
                continue
        
        logger.warning("Failed to read battery level from any path, using default 100%")
        return 100
    
    @classmethod
    async def _read_power_mode(cls) -> str:
        """Read power mode from system.
        
        Returns:
            "ac" if plugged in, "battery" otherwise (defaults to "battery" on error)
        """
        return cls._read_power_mode_sync()
    
    @classmethod
    def _read_power_mode_sync(cls) -> str:
        """Read power mode from system (synchronous).
        
        Tries primary path first, then alternative paths.
        
        Returns:
            "ac" if plugged in, "battery" otherwise (defaults to "battery" on error)
        """
        paths_to_try = [cls.AC_ADAPTER_PATH] + cls.ALT_AC_PATHS
        
        for path in paths_to_try:
            try:
                with open(path, "r") as f:
                    online = int(f.read().strip())
                    return "ac" if online == 1 else "battery"
            except (IOError, ValueError):
                continue
        
        logger.warning("Failed to read power mode from any path, assuming battery mode")
        return "battery"
    
    @classmethod
    async def _read_temperature(cls) -> int:
        """Read CPU temperature from system.
        
        Returns:
            Temperature in Celsius, defaults to 50 on error
        """
        return cls._read_temperature_sync()
    
    @classmethod
    def _read_temperature_sync(cls) -> int:
        """Read CPU temperature from system (synchronous).
        
        Tries primary path first, then alternative paths.
        
        Returns:
            Temperature in Celsius, defaults to 50 on error
        """
        paths_to_try = [cls.THERMAL_ZONE_PATH] + cls.ALT_THERMAL_PATHS
        
        for path in paths_to_try:
            try:
                with open(path, "r") as f:
                    # Temperature is in millidegrees
                    temp_millidegrees = int(f.read().strip())
                    temp_c = temp_millidegrees // 1000
                    # Clamp to reasonable range
                    return max(0, min(150, temp_c))
            except (IOError, ValueError):
                continue
        
        logger.warning("Failed to read temperature from any path, using default 50°C")
        return 50
    
    def to_dict(self) -> dict:
        """Convert context to dictionary for JSON serialization."""
        return {
            "battery_percent": self.battery_percent,
            "power_mode": self.power_mode,
            "temperature_c": self.temperature_c,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SystemContext":
        """Create SystemContext from dictionary.
        
        Args:
            data: Dictionary containing context data
            
        Returns:
            SystemContext instance
        """
        return cls(
            battery_percent=data.get("battery_percent", 100),
            power_mode=data.get("power_mode", "battery"),
            temperature_c=data.get("temperature_c", 50),
        )


@dataclass
class ContextualProfile:
    """Profile with context conditions for activation.
    
    Extends the concept of GameProfile with environmental conditions.
    A contextual profile activates when both the AppID matches AND
    all context conditions are satisfied.
    
    Attributes:
        app_id: Steam AppID (None for global default)
        name: Profile display name
        cores: Undervolt values for each core [core0, core1, core2, core3] in mV
        dynamic_enabled: Whether dynamic mode is enabled for this profile
        dynamic_config: Dynamic mode configuration (if dynamic_enabled is True)
        conditions: Context conditions for activation
        created_at: ISO timestamp when profile was created
    
    Requirements: 1.1, 1.2
    """
    app_id: Optional[int]
    name: str
    cores: List[int]
    dynamic_enabled: bool = False
    dynamic_config: Optional[dict] = None
    conditions: ContextCondition = field(default_factory=ContextCondition)
    created_at: str = ""
    
    def __post_init__(self):
        """Set created_at timestamp if not provided."""
        from datetime import datetime, timezone
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
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
        # Check app_id match (None app_id in profile means global default)
        if self.app_id is not None and self.app_id != app_id:
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
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary for JSON serialization."""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "cores": self.cores,
            "dynamic_enabled": self.dynamic_enabled,
            "dynamic_config": self.dynamic_config,
            "conditions": self.conditions.to_dict(),
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ContextualProfile":
        """Create ContextualProfile from dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            ContextualProfile instance
        """
        conditions_data = data.get("conditions", {})
        conditions = ContextCondition.from_dict(conditions_data) if conditions_data else ContextCondition()
        
        return cls(
            app_id=data.get("app_id"),
            name=data.get("name", "Unknown"),
            cores=data.get("cores", [0, 0, 0, 0]),
            dynamic_enabled=data.get("dynamic_enabled", False),
            dynamic_config=data.get("dynamic_config"),
            conditions=conditions,
            created_at=data.get("created_at", ""),
        )


class ContextMatcher:
    """Selects the best matching profile for current context.
    
    Implements the profile selection algorithm with priority ordering
    and fallback chain.
    
    Requirements: 1.2, 1.5
    """
    
    def find_best_match(
        self,
        app_id: Optional[int],
        context: SystemContext,
        profiles: List[ContextualProfile],
        global_default: Optional[ContextualProfile] = None,
    ) -> Optional[ContextualProfile]:
        """Find the most specific matching profile.
        
        Priority order:
        1. Profiles matching app_id + all context conditions (most specific first)
        2. Profiles matching only app_id (no context conditions)
        3. Global default
        
        When multiple profiles have the same specificity, the one with the
        newer created_at timestamp wins.
        
        Args:
            app_id: Steam AppID of the current game (None if no game running)
            context: Current system context
            profiles: List of contextual profiles to search
            global_default: Optional global default profile
            
        Returns:
            Best matching ContextualProfile, or None if no match found
            
        Requirements: 1.2, 1.5
        """
        # Find all matching profiles
        matching_profiles: List[ContextualProfile] = []
        
        for profile in profiles:
            if profile.matches_context(app_id, context):
                matching_profiles.append(profile)
        
        if not matching_profiles:
            # Fallback chain: try app_id only match (Requirements: 1.5)
            app_only_match = self._find_app_only_match(app_id, profiles)
            if app_only_match:
                return app_only_match
            
            # Final fallback: global default
            return global_default
        
        # Sort by priority (descending) and created_at (descending for ties)
        # Higher priority = more specific
        # Newer created_at wins ties
        matching_profiles.sort(
            key=lambda p: (p.priority(), p.created_at),
            reverse=True
        )
        
        return matching_profiles[0]
    
    def _find_app_only_match(
        self,
        app_id: Optional[int],
        profiles: List[ContextualProfile],
    ) -> Optional[ContextualProfile]:
        """Find a profile matching only app_id (ignoring context conditions).
        
        This is part of the fallback chain when no profile matches all conditions.
        
        Args:
            app_id: Steam AppID to match
            profiles: List of profiles to search
            
        Returns:
            Profile matching app_id with no context conditions, or None
            
        Requirements: 1.5
        """
        if app_id is None:
            return None
        
        # Find profiles that match app_id and have no context conditions
        app_only_profiles = [
            p for p in profiles
            if p.app_id == app_id and p.conditions.specificity() == 0
        ]
        
        if not app_only_profiles:
            return None
        
        # Sort by created_at (newer wins)
        app_only_profiles.sort(key=lambda p: p.created_at, reverse=True)
        return app_only_profiles[0]


class ContextReader:
    """Reads and monitors system context for profile switching.
    
    Provides continuous monitoring of battery level, power mode, and temperature
    with callbacks for context changes.
    
    Requirements: 1.3, 1.4
    """
    
    def __init__(
        self,
        on_battery_change: Optional[callable] = None,
        on_power_mode_change: Optional[callable] = None,
        on_temperature_change: Optional[callable] = None,
    ):
        """Initialize the context reader.
        
        Args:
            on_battery_change: Callback for battery level changes (receives int)
            on_power_mode_change: Callback for power mode changes (receives str)
            on_temperature_change: Callback for temperature changes (receives int)
        """
        self._on_battery_change = on_battery_change
        self._on_power_mode_change = on_power_mode_change
        self._on_temperature_change = on_temperature_change
        
        self._last_context: Optional[SystemContext] = None
        self._running = False
    
    def read_current(self) -> SystemContext:
        """Read current system context.
        
        Returns:
            Current SystemContext
        """
        return SystemContext.read_current_sync()
    
    async def read_current_async(self) -> SystemContext:
        """Read current system context (async version).
        
        Returns:
            Current SystemContext
        """
        return await SystemContext.read_current()
    
    def check_for_changes(self) -> Optional[SystemContext]:
        """Check for context changes and trigger callbacks.
        
        Reads current context and compares with last known context.
        Triggers appropriate callbacks if changes are detected.
        
        Returns:
            New SystemContext if changes detected, None otherwise
        """
        current = self.read_current()
        
        if self._last_context is None:
            self._last_context = current
            return current
        
        changes_detected = False
        
        # Check battery change
        if current.battery_percent != self._last_context.battery_percent:
            changes_detected = True
            if self._on_battery_change:
                self._on_battery_change(current.battery_percent)
        
        # Check power mode change
        if current.power_mode != self._last_context.power_mode:
            changes_detected = True
            if self._on_power_mode_change:
                self._on_power_mode_change(current.power_mode)
        
        # Check temperature change (only significant changes, e.g., 5°C)
        temp_diff = abs(current.temperature_c - self._last_context.temperature_c)
        if temp_diff >= 5:
            changes_detected = True
            if self._on_temperature_change:
                self._on_temperature_change(current.temperature_c)
        
        self._last_context = current
        
        return current if changes_detected else None
    
    def get_last_context(self) -> Optional[SystemContext]:
        """Get the last read context.
        
        Returns:
            Last SystemContext or None if never read
        """
        return self._last_context
    
    def reset(self) -> None:
        """Reset the context reader state."""
        self._last_context = None
