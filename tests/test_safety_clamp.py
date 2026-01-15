"""Property tests for value clamping invariant.

Feature: decktune, Property 2: Value Clamping Invariant
Validates: Requirements 1.5, 9.5

Property 2: Value Clamping Invariant
For any list of undervolt values and any platform, the Safety_Manager.clamp_values() output SHALL satisfy:
- All output values are >= platform.safe_limit
- All output values are <= 0
- If input value >= safe_limit, output equals input
- If input value < safe_limit, output equals safe_limit
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


# Strategy for undervolt values (typically -60 to +10 to cover edge cases)
undervolt_value = st.integers(min_value=-60, max_value=10)

# Strategy for list of 4 undervolt values
undervolt_values_list = st.lists(undervolt_value, min_size=4, max_size=4)

# Strategy for platform safe limits
platform_safe_limits = st.sampled_from([-30, -35, -25])


def create_platform_with_limit(safe_limit: int) -> PlatformInfo:
    """Create a PlatformInfo with the given safe limit."""
    if safe_limit == -30:
        return PlatformInfo(model="Jupiter", variant="LCD", safe_limit=-30, detected=True)
    elif safe_limit == -35:
        return PlatformInfo(model="Galileo", variant="OLED", safe_limit=-35, detected=True)
    else:
        return PlatformInfo(model="Unknown", variant="UNKNOWN", safe_limit=-25, detected=False)


class TestValueClampingInvariant:
    """Property 2: Value Clamping Invariant
    
    For any list of undervolt values and any platform, the Safety_Manager.clamp_values() 
    output SHALL satisfy:
    - All output values are >= platform.safe_limit
    - All output values are <= 0
    - If input value >= safe_limit, output equals input
    - If input value < safe_limit, output equals safe_limit
    
    Validates: Requirements 1.5, 9.5
    """

    @given(values=undervolt_values_list, safe_limit=platform_safe_limits)
    @settings(max_examples=100)
    def test_clamped_values_within_safe_limit(self, values: list, safe_limit: int):
        """All output values are >= platform.safe_limit."""
        platform = create_platform_with_limit(safe_limit)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        result = safety.clamp_values(values)
        
        for v in result:
            assert v >= safe_limit, f"Value {v} is below safe limit {safe_limit}"

    @given(values=undervolt_values_list, safe_limit=platform_safe_limits)
    @settings(max_examples=100)
    def test_clamped_values_not_positive(self, values: list, safe_limit: int):
        """All output values are <= 0."""
        platform = create_platform_with_limit(safe_limit)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        result = safety.clamp_values(values)
        
        for v in result:
            assert v <= 0, f"Value {v} is positive (should be <= 0)"

    @given(values=undervolt_values_list, safe_limit=platform_safe_limits)
    @settings(max_examples=100)
    def test_values_within_range_unchanged(self, values: list, safe_limit: int):
        """If input value >= safe_limit and <= 0, output equals input."""
        platform = create_platform_with_limit(safe_limit)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        result = safety.clamp_values(values)
        
        for i, (inp, out) in enumerate(zip(values, result)):
            if safe_limit <= inp <= 0:
                assert out == inp, f"Value at index {i}: input {inp} within range but output {out} differs"

    @given(values=undervolt_values_list, safe_limit=platform_safe_limits)
    @settings(max_examples=100)
    def test_values_below_limit_clamped(self, values: list, safe_limit: int):
        """If input value < safe_limit, output equals safe_limit."""
        platform = create_platform_with_limit(safe_limit)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        result = safety.clamp_values(values)
        
        for i, (inp, out) in enumerate(zip(values, result)):
            if inp < safe_limit:
                assert out == safe_limit, f"Value at index {i}: input {inp} below limit but output {out} != {safe_limit}"

    @given(values=undervolt_values_list, safe_limit=platform_safe_limits)
    @settings(max_examples=100)
    def test_output_length_matches_input(self, values: list, safe_limit: int):
        """Output list has same length as input list."""
        platform = create_platform_with_limit(safe_limit)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        result = safety.clamp_values(values)
        
        assert len(result) == len(values), f"Output length {len(result)} != input length {len(values)}"
