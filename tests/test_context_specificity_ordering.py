"""Property tests for profile specificity ordering.

**Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
**Validates: Requirements 1.2**

Property 2: Profile specificity ordering
*For any* set of profiles matching the same context, the selected profile SHALL have
the highest specificity (number of non-None conditions), with ties broken by
creation timestamp (newer wins).
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timezone, timedelta

from backend.dynamic.context import (
    ContextCondition,
    SystemContext,
    ContextualProfile,
    ContextMatcher,
)


# Strategies for generating test data
battery_threshold_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=100))
power_mode_strategy = st.one_of(st.none(), st.sampled_from(["ac", "battery"]))
temp_threshold_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=100))

battery_percent_strategy = st.integers(min_value=0, max_value=100)
context_power_mode_strategy = st.sampled_from(["ac", "battery"])
temperature_strategy = st.integers(min_value=0, max_value=100)

app_id_strategy = st.integers(min_value=1, max_value=9999999)
cores_strategy = st.lists(st.integers(min_value=-100, max_value=0), min_size=4, max_size=4)


@st.composite
def context_condition_strategy(draw):
    """Generate a valid ContextCondition."""
    return ContextCondition(
        battery_threshold=draw(battery_threshold_strategy),
        power_mode=draw(power_mode_strategy),
        temp_threshold=draw(temp_threshold_strategy),
    )


@st.composite
def system_context_strategy(draw):
    """Generate a valid SystemContext."""
    return SystemContext(
        battery_percent=draw(battery_percent_strategy),
        power_mode=draw(context_power_mode_strategy),
        temperature_c=draw(temperature_strategy),
    )


@st.composite
def contextual_profile_strategy(draw, app_id=None):
    """Generate a valid ContextualProfile."""
    if app_id is None:
        app_id = draw(st.one_of(st.none(), app_id_strategy))
    
    # Generate a unique timestamp
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    offset_seconds = draw(st.integers(min_value=0, max_value=1000000))
    created_at = (base_time + timedelta(seconds=offset_seconds)).isoformat()
    
    return ContextualProfile(
        app_id=app_id,
        name=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S')))),
        cores=draw(cores_strategy),
        dynamic_enabled=draw(st.booleans()),
        dynamic_config=None,
        conditions=draw(context_condition_strategy()),
        created_at=created_at,
    )


@st.composite
def matching_profile_strategy(draw, context: SystemContext, app_id: int):
    """Generate a ContextualProfile that matches the given context and app_id."""
    # Create conditions that will match the context
    battery_threshold = draw(st.one_of(
        st.none(),
        st.integers(min_value=context.battery_percent, max_value=100)
    ))
    power_mode = draw(st.one_of(
        st.none(),
        st.just(context.power_mode)
    ))
    temp_threshold = draw(st.one_of(
        st.none(),
        st.integers(min_value=0, max_value=context.temperature_c)
    ))
    
    conditions = ContextCondition(
        battery_threshold=battery_threshold,
        power_mode=power_mode,
        temp_threshold=temp_threshold,
    )
    
    # Generate a unique timestamp
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    offset_seconds = draw(st.integers(min_value=0, max_value=1000000))
    created_at = (base_time + timedelta(seconds=offset_seconds)).isoformat()
    
    return ContextualProfile(
        app_id=app_id,
        name=f"Profile_{draw(st.integers(min_value=1, max_value=9999))}",
        cores=draw(cores_strategy),
        dynamic_enabled=draw(st.booleans()),
        dynamic_config=None,
        conditions=conditions,
        created_at=created_at,
    )


class TestProfileSpecificityOrdering:
    """Property 2: Profile specificity ordering
    
    *For any* set of profiles matching the same context, the selected profile SHALL have
    the highest specificity (number of non-None conditions), with ties broken by
    creation timestamp (newer wins).
    
    **Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
    **Validates: Requirements 1.2**
    """

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_selected_profile_has_highest_specificity(
        self, context: SystemContext, app_id: int
    ):
        """Test that the selected profile has the highest specificity among matches.
        
        **Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
        **Validates: Requirements 1.2**
        """
        # Create profiles with different specificities that all match
        profiles = []
        
        # Profile with 0 conditions (always matches)
        profiles.append(ContextualProfile(
            app_id=app_id,
            name="No conditions",
            cores=[0, 0, 0, 0],
            conditions=ContextCondition(),
            created_at="2026-01-01T00:00:00+00:00",
        ))
        
        # Profile with 1 condition (battery)
        profiles.append(ContextualProfile(
            app_id=app_id,
            name="Battery only",
            cores=[-10, -10, -10, -10],
            conditions=ContextCondition(battery_threshold=100),  # Always matches
            created_at="2026-01-01T00:00:01+00:00",
        ))
        
        # Profile with 2 conditions (battery + power)
        profiles.append(ContextualProfile(
            app_id=app_id,
            name="Battery + Power",
            cores=[-20, -20, -20, -20],
            conditions=ContextCondition(
                battery_threshold=100,
                power_mode=context.power_mode,
            ),
            created_at="2026-01-01T00:00:02+00:00",
        ))
        
        # Profile with 3 conditions (all)
        profiles.append(ContextualProfile(
            app_id=app_id,
            name="All conditions",
            cores=[-30, -30, -30, -30],
            conditions=ContextCondition(
                battery_threshold=100,
                power_mode=context.power_mode,
                temp_threshold=0,  # Always matches (temp >= 0)
            ),
            created_at="2026-01-01T00:00:03+00:00",
        ))
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "All conditions", (
            f"Should select profile with highest specificity (3), got '{result.name}' "
            f"with specificity {result.conditions.specificity()}"
        )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_ties_broken_by_newer_timestamp(
        self, context: SystemContext, app_id: int
    ):
        """Test that ties in specificity are broken by newer created_at timestamp.
        
        **Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
        **Validates: Requirements 1.2**
        """
        # Create profiles with same specificity but different timestamps
        profiles = [
            ContextualProfile(
                app_id=app_id,
                name="Older profile",
                cores=[0, 0, 0, 0],
                conditions=ContextCondition(battery_threshold=100),
                created_at="2026-01-01T00:00:00+00:00",
            ),
            ContextualProfile(
                app_id=app_id,
                name="Newer profile",
                cores=[-10, -10, -10, -10],
                conditions=ContextCondition(battery_threshold=100),
                created_at="2026-01-02T00:00:00+00:00",
            ),
        ]
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles)
        
        assert result is not None, "Should find a matching profile"
        assert result.name == "Newer profile", (
            f"Should select newer profile when specificity is equal, got '{result.name}'"
        )

    @given(
        context=system_context_strategy(),
        app_id=app_id_strategy,
        num_profiles=st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=100)
    def test_selected_profile_specificity_is_maximum(
        self, context: SystemContext, app_id: int, num_profiles: int
    ):
        """Test that selected profile's specificity is >= all other matching profiles.
        
        **Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
        **Validates: Requirements 1.2**
        """
        # Generate profiles that all match the context
        profiles = []
        for i in range(num_profiles):
            # Create conditions that match the context with varying specificity
            battery_threshold = 100 if i % 3 >= 1 else None
            power_mode = context.power_mode if i % 3 >= 2 else None
            temp_threshold = 0 if i % 3 >= 3 else None
            
            profiles.append(ContextualProfile(
                app_id=app_id,
                name=f"Profile_{i}",
                cores=[0, 0, 0, 0],
                conditions=ContextCondition(
                    battery_threshold=battery_threshold,
                    power_mode=power_mode,
                    temp_threshold=temp_threshold,
                ),
                created_at=f"2026-01-01T00:00:{i:02d}+00:00",
            ))
        
        matcher = ContextMatcher()
        result = matcher.find_best_match(app_id, context, profiles)
        
        assert result is not None, "Should find a matching profile"
        
        # Verify selected profile has maximum specificity among matches
        matching_profiles = [p for p in profiles if p.matches_context(app_id, context)]
        max_specificity = max(p.priority() for p in matching_profiles)
        
        assert result.priority() == max_specificity, (
            f"Selected profile priority {result.priority()} should equal "
            f"max priority {max_specificity}"
        )

    @given(context=system_context_strategy(), app_id=app_id_strategy)
    @settings(max_examples=100)
    def test_specificity_counts_non_none_conditions(
        self, context: SystemContext, app_id: int
    ):
        """Test that specificity correctly counts non-None conditions.
        
        **Feature: decktune-3.0-automation, Property 2: Profile specificity ordering**
        **Validates: Requirements 1.2**
        """
        # Test all combinations of conditions
        test_cases = [
            (ContextCondition(), 0),
            (ContextCondition(battery_threshold=50), 1),
            (ContextCondition(power_mode="ac"), 1),
            (ContextCondition(temp_threshold=60), 1),
            (ContextCondition(battery_threshold=50, power_mode="ac"), 2),
            (ContextCondition(battery_threshold=50, temp_threshold=60), 2),
            (ContextCondition(power_mode="ac", temp_threshold=60), 2),
            (ContextCondition(battery_threshold=50, power_mode="ac", temp_threshold=60), 3),
        ]
        
        for condition, expected_specificity in test_cases:
            assert condition.specificity() == expected_specificity, (
                f"Condition {condition} should have specificity {expected_specificity}, "
                f"got {condition.specificity()}"
            )
