"""Property tests for context change triggers re-evaluation.

**Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
**Validates: Requirements 1.3, 1.4**

Property 3: Context change triggers re-evaluation
*For any* change in battery level crossing a threshold OR power mode change,
the system SHALL call find_best_match() and switch profile if the result differs from current.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.dynamic.context import ContextCondition, SystemContext, ContextMatcher
from backend.dynamic.profile_manager import ProfileManager, ContextualGameProfile


# Strategies for generating test data
battery_percent_strategy = st.integers(min_value=0, max_value=100)
context_power_mode_strategy = st.sampled_from(["ac", "battery"])
temperature_strategy = st.integers(min_value=0, max_value=100)
app_id_strategy = st.integers(min_value=1, max_value=9999999)
cores_strategy = st.lists(st.integers(min_value=-100, max_value=0), min_size=4, max_size=4)


@st.composite
def system_context_strategy(draw):
    """Generate a valid SystemContext."""
    return SystemContext(
        battery_percent=draw(battery_percent_strategy),
        power_mode=draw(context_power_mode_strategy),
        temperature_c=draw(temperature_strategy),
    )


@st.composite
def battery_threshold_strategy(draw):
    """Generate a valid battery threshold (0-100 or None)."""
    return draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100)))


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key, default=None):
        return self._settings.get(key, default)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class MockRyzenadj:
    """Mock RyzenadjWrapper for testing."""
    
    def __init__(self):
        self.applied_values = []
    
    async def apply_values_async(self, cores):
        self.applied_values.append(cores)
        return (True, None)


class MockDynamicController:
    """Mock DynamicController for testing."""
    
    def __init__(self):
        self._running = False
    
    def is_running(self):
        return self._running
    
    async def stop(self):
        self._running = False


class MockEventEmitter:
    """Mock EventEmitter for testing."""
    
    def __init__(self):
        self.events = []
    
    async def emit_profile_changed(self, profile_name, app_id):
        self.events.append(("profile_changed", profile_name, app_id))
    
    async def emit_context_changed(self, context):
        self.events.append(("context_changed", context))
    
    async def emit_profile_switched_by_context(self, old_profile, new_profile, reason):
        self.events.append(("profile_switched_by_context", old_profile, new_profile, reason))


class TestContextChangeTriggersReevaluation:
    """Property 3: Context change triggers re-evaluation
    
    *For any* change in battery level crossing a threshold OR power mode change,
    the system SHALL call find_best_match() and switch profile if the result differs from current.
    
    **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
    **Validates: Requirements 1.3, 1.4**
    """

    def _create_profile_manager(self):
        """Create a ProfileManager with mocked dependencies."""
        settings = MockSettingsManager()
        ryzenadj = MockRyzenadj()
        dynamic_controller = MockDynamicController()
        event_emitter = MockEventEmitter()
        
        return ProfileManager(
            settings_manager=settings,
            ryzenadj=ryzenadj,
            dynamic_controller=dynamic_controller,
            event_emitter=event_emitter,
        )

    @given(
        old_battery=battery_percent_strategy,
        new_battery=battery_percent_strategy,
        threshold=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_battery_threshold_crossing_detected(
        self, old_battery: int, new_battery: int, threshold: int
    ):
        """Test that battery threshold crossing is correctly detected.
        
        **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
        **Validates: Requirements 1.3**
        """
        manager = self._create_profile_manager()
        
        # Add a contextual profile with the threshold
        profile = ContextualGameProfile(
            app_id=12345,
            name="Test Profile",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(battery_threshold=threshold),
            created_at="2026-01-01T00:00:00+00:00",
        )
        manager._contextual_profiles.append(profile)
        
        # Check if threshold was crossed
        crossed = manager._has_crossed_battery_threshold(old_battery, new_battery)
        
        # Calculate expected result
        # Threshold is crossed if we went from above to at/below, or from at/below to above
        expected_crossed = (
            (old_battery > threshold >= new_battery) or
            (old_battery <= threshold < new_battery)
        )
        
        assert crossed == expected_crossed, (
            f"Battery threshold crossing detection failed: "
            f"old={old_battery}, new={new_battery}, threshold={threshold}, "
            f"expected={expected_crossed}, actual={crossed}"
        )

    @given(
        old_mode=context_power_mode_strategy,
        new_mode=context_power_mode_strategy,
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_power_mode_change_triggers_reevaluation(
        self, old_mode: str, new_mode: str
    ):
        """Test that power mode change triggers profile re-evaluation.
        
        **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
        **Validates: Requirements 1.4**
        """
        manager = self._create_profile_manager()
        
        # Set up initial context
        manager._current_context = SystemContext(
            battery_percent=50,
            power_mode=old_mode,
            temperature_c=50,
        )
        manager._current_app_id = 12345
        
        # Add contextual profiles for different power modes
        ac_profile = ContextualGameProfile(
            app_id=12345,
            name="AC Profile",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(power_mode="ac"),
            created_at="2026-01-01T00:00:00+00:00",
        )
        battery_profile = ContextualGameProfile(
            app_id=12345,
            name="Battery Profile",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(power_mode="battery"),
            created_at="2026-01-01T00:00:01+00:00",
        )
        manager._contextual_profiles.extend([ac_profile, battery_profile])
        
        # Track if reevaluation was called
        reevaluate_called = False
        original_reevaluate = manager._reevaluate_profile
        
        async def mock_reevaluate():
            nonlocal reevaluate_called
            reevaluate_called = True
            # Don't actually reevaluate to avoid side effects
        
        manager._reevaluate_profile = mock_reevaluate
        
        # Change power mode
        await manager.on_power_mode_change(new_mode)
        
        # Verify reevaluation was triggered if mode changed
        if old_mode != new_mode:
            assert reevaluate_called, (
                f"Power mode change from {old_mode} to {new_mode} should trigger re-evaluation"
            )
        else:
            assert not reevaluate_called, (
                f"Same power mode {old_mode} should not trigger re-evaluation"
            )

    @given(
        old_battery=battery_percent_strategy,
        new_battery=battery_percent_strategy,
        threshold=st.integers(min_value=1, max_value=99),
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_battery_change_triggers_reevaluation_on_threshold_crossing(
        self, old_battery: int, new_battery: int, threshold: int
    ):
        """Test that battery change triggers re-evaluation when crossing threshold.
        
        **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
        **Validates: Requirements 1.3**
        """
        manager = self._create_profile_manager()
        
        # Set up initial context
        manager._current_context = SystemContext(
            battery_percent=old_battery,
            power_mode="battery",
            temperature_c=50,
        )
        manager._current_app_id = 12345
        
        # Add a contextual profile with the threshold
        profile = ContextualGameProfile(
            app_id=12345,
            name="Battery Saver",
            cores=[-15, -15, -15, -15],
            conditions=ContextCondition(battery_threshold=threshold),
            created_at="2026-01-01T00:00:00+00:00",
        )
        manager._contextual_profiles.append(profile)
        
        # Track if reevaluation was called
        reevaluate_called = False
        
        async def mock_reevaluate():
            nonlocal reevaluate_called
            reevaluate_called = True
        
        manager._reevaluate_profile = mock_reevaluate
        
        # Change battery level
        await manager.on_battery_change(new_battery)
        
        # Calculate if threshold was crossed
        threshold_crossed = (
            (old_battery > threshold >= new_battery) or
            (old_battery <= threshold < new_battery)
        )
        
        # Verify reevaluation was triggered if threshold was crossed
        if threshold_crossed:
            assert reevaluate_called, (
                f"Battery change from {old_battery} to {new_battery} crossing threshold {threshold} "
                f"should trigger re-evaluation"
            )
        else:
            assert not reevaluate_called, (
                f"Battery change from {old_battery} to {new_battery} not crossing threshold {threshold} "
                f"should not trigger re-evaluation"
            )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_reevaluation_calls_find_best_match(
        self, context: SystemContext, app_id: int
    ):
        """Test that re-evaluation uses find_best_match to select profile.
        
        **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
        **Validates: Requirements 1.3, 1.4**
        """
        manager = self._create_profile_manager()
        
        # Set up context
        manager._current_context = context
        manager._current_app_id = app_id
        
        # Add contextual profiles
        profile1 = ContextualGameProfile(
            app_id=app_id,
            name="Profile 1",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(battery_threshold=100),  # Always matches
            created_at="2026-01-01T00:00:00+00:00",
        )
        profile2 = ContextualGameProfile(
            app_id=app_id,
            name="Profile 2",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(
                battery_threshold=100,
                power_mode=context.power_mode,
            ),  # More specific
            created_at="2026-01-01T00:00:01+00:00",
        )
        manager._contextual_profiles.extend([profile1, profile2])
        
        # Track find_best_match calls
        find_best_match_called = False
        original_find_best_match = manager._context_matcher.find_best_match
        
        def mock_find_best_match(*args, **kwargs):
            nonlocal find_best_match_called
            find_best_match_called = True
            return original_find_best_match(*args, **kwargs)
        
        manager._context_matcher.find_best_match = mock_find_best_match
        
        # Trigger re-evaluation
        await manager._reevaluate_profile()
        
        # Verify find_best_match was called
        assert find_best_match_called, "Re-evaluation should call find_best_match"

    @given(
        old_mode=context_power_mode_strategy,
        new_mode=context_power_mode_strategy,
        app_id=app_id_strategy,
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_profile_switch_on_context_change(
        self, old_mode: str, new_mode: str, app_id: int
    ):
        """Test that profile is switched when context change results in different best match.
        
        **Feature: decktune-3.0-automation, Property 3: Context change triggers re-evaluation**
        **Validates: Requirements 1.3, 1.4**
        """
        # Skip if modes are the same (no change)
        assume(old_mode != new_mode)
        
        manager = self._create_profile_manager()
        
        # Set up initial context
        manager._current_context = SystemContext(
            battery_percent=50,
            power_mode=old_mode,
            temperature_c=50,
        )
        manager._current_app_id = app_id
        
        # Add contextual profiles for different power modes
        ac_profile = ContextualGameProfile(
            app_id=app_id,
            name="AC Profile",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(power_mode="ac"),
            created_at="2026-01-01T00:00:00+00:00",
        )
        battery_profile = ContextualGameProfile(
            app_id=app_id,
            name="Battery Profile",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(power_mode="battery"),
            created_at="2026-01-01T00:00:01+00:00",
        )
        manager._contextual_profiles.extend([ac_profile, battery_profile])
        
        # Set current profile based on old mode
        if old_mode == "ac":
            manager._current_profile = ac_profile
        else:
            manager._current_profile = battery_profile
        
        # Change power mode
        await manager.on_power_mode_change(new_mode)
        
        # Verify the correct profile was applied
        ryzenadj = manager.ryzenadj
        assert len(ryzenadj.applied_values) > 0, "Profile should have been applied"
        
        # Check that the applied values match the expected profile
        expected_profile = ac_profile if new_mode == "ac" else battery_profile
        assert ryzenadj.applied_values[-1] == expected_profile.cores, (
            f"Expected cores {expected_profile.cores}, got {ryzenadj.applied_values[-1]}"
        )

