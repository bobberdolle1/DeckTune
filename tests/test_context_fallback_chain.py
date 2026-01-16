"""Property tests for fallback chain behavior.

**Feature: decktune-3.0-automation, Property 4: Fallback chain**
**Validates: Requirements 1.5**

Property 4: Fallback chain
*For any* context where no profile matches all conditions, the system SHALL try:
(1) profiles matching only AppID, (2) global default.
The first non-empty match is used.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from backend.dynamic.context import (
    ContextCondition,
    SystemContext,
    ContextualProfile,
    ContextMatcher,
)


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


class TestFallbackChain:
    """Property 4: Fallback chain
    
    *For any* context where no profile matches all conditions, the system SHALL try:
    (1) profiles matching only AppID, (2) global default.
    The first non-empty match is used.
    
    **Feature: decktune-3.0-automation, Property 4: Fallback chain**
    **Validates: Requirements 1.5**
    """

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_fallback_to_app_only_profile(
        self, context: SystemContext, app_id: int
    ):
        """Test fallback to app-only profile when context conditions don't match.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        # Create a profile with context conditions that won't match
        # (battery threshold of -1 can never be satisfied since battery is 0-100)
        non_matching_profile = ContextualProfile(
            app_id=app_id,
            name="Non-matching context",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(
                battery_threshold=-1,  # Impossible to match
            ),
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        # Create an app-only profile (no context conditions)
        app_only_profile = ContextualProfile(
            app_id=app_id,
            name="App only",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(),  # No conditions
            created_at="2026-01-01T00:00:01+00:00",
        )
        
        global_default = ContextualProfile(
            app_id=None,
            name="Global default",
            cores=[0, 0, 0, 0],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:02+00:00",
        )
        
        profiles = [non_matching_profile, app_only_profile]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles, global_default)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "App only", (
            f"Should fall back to app-only profile, got '{result.name}'"
        )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_fallback_to_global_default(
        self, context: SystemContext, app_id: int
    ):
        """Test fallback to global default when no app-specific profile matches.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        # Create profiles for a different app_id
        other_app_id = app_id + 1
        
        other_app_profile = ContextualProfile(
            app_id=other_app_id,
            name="Other app profile",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        global_default = ContextualProfile(
            app_id=None,
            name="Global default",
            cores=[0, 0, 0, 0],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:01+00:00",
        )
        
        profiles = [other_app_profile]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles, global_default)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "Global default", (
            f"Should fall back to global default, got '{result.name}'"
        )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_no_match_returns_none_without_global_default(
        self, context: SystemContext, app_id: int
    ):
        """Test that None is returned when no profile matches and no global default.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        # Create profiles for a different app_id
        other_app_id = app_id + 1
        
        other_app_profile = ContextualProfile(
            app_id=other_app_id,
            name="Other app profile",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        profiles = [other_app_profile]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles, global_default=None)
        
        assert result is None, "Should return None when no match and no global default"

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_context_match_takes_priority_over_app_only(
        self, context: SystemContext, app_id: int
    ):
        """Test that context-matching profile takes priority over app-only profile.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        # Create an app-only profile (no context conditions)
        app_only_profile = ContextualProfile(
            app_id=app_id,
            name="App only",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(),  # No conditions
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        # Create a profile with context conditions that match
        context_matching_profile = ContextualProfile(
            app_id=app_id,
            name="Context matching",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(
                battery_threshold=100,  # Always matches (battery <= 100)
            ),
            created_at="2026-01-01T00:00:01+00:00",
        )
        
        profiles = [app_only_profile, context_matching_profile]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "Context matching", (
            f"Context-matching profile should take priority, got '{result.name}'"
        )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_app_specific_takes_priority_over_global(
        self, context: SystemContext, app_id: int
    ):
        """Test that app-specific profile takes priority over global default.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        # Create an app-only profile
        app_only_profile = ContextualProfile(
            app_id=app_id,
            name="App specific",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        # Create a global default with more conditions (higher specificity)
        global_default = ContextualProfile(
            app_id=None,
            name="Global default",
            cores=[0, 0, 0, 0],
            conditions=ContextCondition(
                battery_threshold=100,
                power_mode=context.power_mode,
            ),
            created_at="2026-01-01T00:00:01+00:00",
        )
        
        profiles = [app_only_profile]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles, global_default)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "App specific", (
            f"App-specific profile should take priority over global, got '{result.name}'"
        )

    @given(context=system_context_strategy())
    @settings(max_examples=100)
    def test_fallback_chain_order(self, context: SystemContext):
        """Test the complete fallback chain order.
        
        **Feature: decktune-3.0-automation, Property 4: Fallback chain**
        **Validates: Requirements 1.5**
        """
        app_id = 12345
        
        # Create profiles to test the full fallback chain
        # 1. Profile with context conditions that don't match
        non_matching = ContextualProfile(
            app_id=app_id,
            name="Non-matching",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(battery_threshold=-1),  # Never matches
            created_at="2026-01-01T00:00:00+00:00",
        )
        
        # 2. App-only profile (fallback level 1)
        app_only = ContextualProfile(
            app_id=app_id,
            name="App only",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:01+00:00",
        )
        
        # 3. Global default (fallback level 2)
        global_default = ContextualProfile(
            app_id=None,
            name="Global default",
            cores=[0, 0, 0, 0],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:02+00:00",
        )
        
        matcher = ContextMatcher()
        
        # Test with all profiles - should get app_only (matches app_id with no conditions)
        result = matcher.find_best_match(app_id, context, [non_matching, app_only], global_default)
        assert result.name == "App only", "Should use app-only profile"
        
        # Test without app_only - should get global default
        result = matcher.find_best_match(app_id, context, [non_matching], global_default)
        assert result.name == "Global default", "Should fall back to global default"
        
        # Test without any matching profiles and no global default
        result = matcher.find_best_match(app_id, context, [non_matching], None)
        assert result is None, "Should return None when no fallback available"
