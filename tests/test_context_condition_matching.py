"""Property tests for context condition matching.

**Feature: decktune-3.0-automation, Property 1: Context condition matching**
**Validates: Requirements 1.1**

Property 1: Context condition matching
*For any* ContextCondition with battery_threshold B, power_mode P, and temp_threshold T,
and any SystemContext, the condition matches if and only if:
(B is None OR context.battery <= B) AND
(P is None OR context.power_mode == P) AND
(T is None OR context.temperature >= T).
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from backend.dynamic.context import ContextCondition, SystemContext


# Strategies for generating test data
battery_threshold_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=100))
power_mode_strategy = st.one_of(st.none(), st.sampled_from(["ac", "battery"]))
temp_threshold_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=100))

battery_percent_strategy = st.integers(min_value=0, max_value=100)
context_power_mode_strategy = st.sampled_from(["ac", "battery"])
temperature_strategy = st.integers(min_value=0, max_value=100)


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


class TestContextConditionMatching:
    """Property 1: Context condition matching
    
    *For any* ContextCondition with battery_threshold B, power_mode P, and temp_threshold T,
    and any SystemContext, the condition matches if and only if:
    (B is None OR context.battery <= B) AND
    (P is None OR context.power_mode == P) AND
    (T is None OR context.temperature >= T).
    
    **Feature: decktune-3.0-automation, Property 1: Context condition matching**
    **Validates: Requirements 1.1**
    """

    @given(condition=context_condition_strategy(), context=system_context_strategy())
    @settings(max_examples=100)
    def test_context_condition_matching_equivalence(
        self, condition: ContextCondition, context: SystemContext
    ):
        """Test that matches() returns True iff all specified conditions are satisfied.
        
        **Feature: decktune-3.0-automation, Property 1: Context condition matching**
        **Validates: Requirements 1.1**
        """
        # Calculate expected result based on the property definition
        battery_ok = (
            condition.battery_threshold is None or 
            context.battery_percent <= condition.battery_threshold
        )
        power_ok = (
            condition.power_mode is None or 
            context.power_mode == condition.power_mode
        )
        temp_ok = (
            condition.temp_threshold is None or 
            context.temperature_c >= condition.temp_threshold
        )
        
        expected = battery_ok and power_ok and temp_ok
        actual = condition.matches(context)
        
        assert actual == expected, (
            f"Mismatch for condition={condition}, context={context}: "
            f"expected={expected}, actual={actual}, "
            f"battery_ok={battery_ok}, power_ok={power_ok}, temp_ok={temp_ok}"
        )

    @given(condition=context_condition_strategy(), context=system_context_strategy())
    @settings(max_examples=100)
    def test_battery_threshold_semantics(
        self, condition: ContextCondition, context: SystemContext
    ):
        """Test that battery threshold means 'battery <= threshold'.
        
        **Feature: decktune-3.0-automation, Property 1: Context condition matching**
        **Validates: Requirements 1.1**
        """
        # Skip if battery threshold is not set
        assume(condition.battery_threshold is not None)
        # Skip if other conditions would cause mismatch
        assume(condition.power_mode is None or condition.power_mode == context.power_mode)
        assume(condition.temp_threshold is None or context.temperature_c >= condition.temp_threshold)
        
        result = condition.matches(context)
        
        if context.battery_percent <= condition.battery_threshold:
            assert result is True, (
                f"Should match when battery {context.battery_percent} <= threshold {condition.battery_threshold}"
            )
        else:
            assert result is False, (
                f"Should not match when battery {context.battery_percent} > threshold {condition.battery_threshold}"
            )

    @given(condition=context_condition_strategy(), context=system_context_strategy())
    @settings(max_examples=100)
    def test_power_mode_semantics(
        self, condition: ContextCondition, context: SystemContext
    ):
        """Test that power mode requires exact match.
        
        **Feature: decktune-3.0-automation, Property 1: Context condition matching**
        **Validates: Requirements 1.1**
        """
        # Skip if power mode is not set
        assume(condition.power_mode is not None)
        # Skip if other conditions would cause mismatch
        assume(condition.battery_threshold is None or context.battery_percent <= condition.battery_threshold)
        assume(condition.temp_threshold is None or context.temperature_c >= condition.temp_threshold)
        
        result = condition.matches(context)
        
        if context.power_mode == condition.power_mode:
            assert result is True, (
                f"Should match when power mode '{context.power_mode}' == '{condition.power_mode}'"
            )
        else:
            assert result is False, (
                f"Should not match when power mode '{context.power_mode}' != '{condition.power_mode}'"
            )

    @given(condition=context_condition_strategy(), context=system_context_strategy())
    @settings(max_examples=100)
    def test_temp_threshold_semantics(
        self, condition: ContextCondition, context: SystemContext
    ):
        """Test that temp threshold means 'temperature >= threshold'.
        
        **Feature: decktune-3.0-automation, Property 1: Context condition matching**
        **Validates: Requirements 1.1**
        """
        # Skip if temp threshold is not set
        assume(condition.temp_threshold is not None)
        # Skip if other conditions would cause mismatch
        assume(condition.battery_threshold is None or context.battery_percent <= condition.battery_threshold)
        assume(condition.power_mode is None or condition.power_mode == context.power_mode)
        
        result = condition.matches(context)
        
        if context.temperature_c >= condition.temp_threshold:
            assert result is True, (
                f"Should match when temp {context.temperature_c} >= threshold {condition.temp_threshold}"
            )
        else:
            assert result is False, (
                f"Should not match when temp {context.temperature_c} < threshold {condition.temp_threshold}"
            )

    @given(context=system_context_strategy())
    @settings(max_examples=100)
    def test_empty_condition_always_matches(self, context: SystemContext):
        """Test that a condition with no constraints always matches.
        
        **Feature: decktune-3.0-automation, Property 1: Context condition matching**
        **Validates: Requirements 1.1**
        """
        condition = ContextCondition()  # All None
        
        assert condition.matches(context) is True, (
            f"Empty condition should match any context: {context}"
        )
