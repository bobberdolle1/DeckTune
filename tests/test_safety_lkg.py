"""Property tests for LKG persistence.

Feature: decktune, Property 4: LKG Persistence After Success
Validates: Requirements 2.5, 4.6

Property 4: LKG Persistence After Success
For any successful stability test with values V, calling load_lkg() immediately after 
SHALL return values equivalent to V.
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.platform.detect import PlatformInfo
from backend.core.safety import SafetyManager


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


# Strategy for valid undervolt values (within typical range)
valid_undervolt_value = st.integers(min_value=-35, max_value=0)

# Strategy for list of 4 valid undervolt values
valid_undervolt_values_list = st.lists(valid_undervolt_value, min_size=4, max_size=4)


def create_default_platform() -> PlatformInfo:
    """Create a default LCD platform for testing."""
    return PlatformInfo(model="Jupiter", variant="LCD", safe_limit=-30, detected=True)


class TestLKGPersistence:
    """Property 4: LKG Persistence After Success
    
    For any successful stability test with values V, calling load_lkg() immediately 
    after SHALL return values equivalent to V.
    
    Validates: Requirements 2.5, 4.6
    """

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_save_then_load_returns_same_values(self, values: list):
        """Saving LKG values then loading returns equivalent values."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Save the values
        safety.save_lkg(values)
        
        # Load and verify
        loaded = safety.load_lkg()
        
        assert loaded == values, f"Loaded values {loaded} != saved values {values}"

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_save_persists_to_settings(self, values: list):
        """Saving LKG values persists them to settings manager."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Save the values
        safety.save_lkg(values)
        
        # Verify directly in settings
        stored = settings_manager.getSetting("lkg_cores")
        
        assert stored == values, f"Stored values {stored} != saved values {values}"

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_save_updates_internal_state(self, values: list):
        """Saving LKG values updates internal state immediately."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Save the values
        safety.save_lkg(values)
        
        # Get internal state
        internal = safety.get_lkg()
        
        assert internal == values, f"Internal state {internal} != saved values {values}"

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_save_sets_timestamp(self, values: list):
        """Saving LKG values sets a timestamp."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Save the values
        safety.save_lkg(values)
        
        # Verify timestamp was set
        timestamp = settings_manager.getSetting("lkg_timestamp")
        
        assert timestamp is not None, "Timestamp should be set after save_lkg"
        assert isinstance(timestamp, str), "Timestamp should be a string"

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_load_from_new_instance_returns_saved_values(self, values: list):
        """Loading LKG from a new SafetyManager instance returns saved values."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        
        # First instance saves values
        safety1 = SafetyManager(settings_manager, platform)
        safety1.save_lkg(values)
        
        # Second instance loads values (simulating restart)
        safety2 = SafetyManager(settings_manager, platform)
        loaded = safety2.load_lkg()
        
        assert loaded == values, f"New instance loaded {loaded} != saved values {values}"

    @given(values=valid_undervolt_values_list)
    @settings(max_examples=100)
    def test_get_lkg_returns_copy(self, values: list):
        """get_lkg returns a copy, not the internal list."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        safety.save_lkg(values)
        
        # Get the values
        result1 = safety.get_lkg()
        result2 = safety.get_lkg()
        
        # Modify result1
        result1[0] = 999
        
        # result2 should be unaffected
        assert result2 == values, "get_lkg should return a copy, not the internal list"
