"""
Property test for goal estimates availability.

**Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
**Validates: Requirements 5.4**

Property 11: Goal estimates availability
*For any* goal selection in the wizard, estimated battery improvement and 
temperature reduction SHALL be provided.

This test verifies that:
1. Every valid goal has battery improvement estimates
2. Every valid goal has temperature reduction estimates
3. Estimates are non-empty strings in the expected format
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from dataclasses import dataclass
from typing import Optional
import re


# ============================================================================
# Goal Estimates Model (mirrors frontend GOAL_ESTIMATES constant)
# ============================================================================

@dataclass
class GoalEstimate:
    """Goal estimate with battery and temperature improvements."""
    battery_improvement: str
    temp_reduction: str
    description: str


# The GOAL_ESTIMATES constant from the frontend
# This mirrors src/components/SetupWizard.tsx GOAL_ESTIMATES
GOAL_ESTIMATES = {
    'quiet': GoalEstimate(
        battery_improvement="+10-15%",
        temp_reduction="-8-12°C",
        description="Prioritizes lower temperatures and quieter fan operation. Best for casual gaming and media consumption.",
    ),
    'balanced': GoalEstimate(
        battery_improvement="+15-20%",
        temp_reduction="-5-8°C",
        description="Good balance between performance, battery life, and thermals. Recommended for most users.",
    ),
    'battery': GoalEstimate(
        battery_improvement="+20-30%",
        temp_reduction="-3-5°C",
        description="Maximizes battery life with aggressive power savings. Ideal for long gaming sessions away from power.",
    ),
    'performance': GoalEstimate(
        battery_improvement="+5-10%",
        temp_reduction="-2-4°C",
        description="Finds the most aggressive stable undervolt for maximum efficiency. For users who want every bit of optimization.",
    ),
}

# All valid goals
VALID_GOALS = ['quiet', 'balanced', 'battery', 'performance']


# ============================================================================
# Helper Functions
# ============================================================================

def get_estimate_for_goal(goal: str) -> Optional[GoalEstimate]:
    """Get the estimate for a given goal."""
    return GOAL_ESTIMATES.get(goal)


def is_valid_battery_estimate(estimate: str) -> bool:
    """
    Check if a battery estimate string is valid.
    
    Valid formats:
    - "+X-Y%" (e.g., "+10-15%")
    - "+X%" (e.g., "+10%")
    """
    if not estimate:
        return False
    
    # Pattern: +X-Y% or +X%
    pattern = r'^\+\d+(-\d+)?%$'
    return bool(re.match(pattern, estimate))


def is_valid_temp_estimate(estimate: str) -> bool:
    """
    Check if a temperature estimate string is valid.
    
    Valid formats:
    - "-X-Y°C" (e.g., "-8-12°C")
    - "-X°C" (e.g., "-8°C")
    """
    if not estimate:
        return False
    
    # Pattern: -X-Y°C or -X°C
    pattern = r'^-\d+(-\d+)?°C$'
    return bool(re.match(pattern, estimate))


# ============================================================================
# Strategies
# ============================================================================

goal_strategy = st.sampled_from(VALID_GOALS)


# ============================================================================
# Property Tests
# ============================================================================

class TestGoalEstimatesAvailability:
    """
    **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
    **Validates: Requirements 5.4**
    """

    @given(goal=goal_strategy)
    @hyp_settings(max_examples=100)
    def test_every_goal_has_estimates(self, goal: str):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Property: For any valid goal selection, an estimate SHALL exist.
        """
        estimate = get_estimate_for_goal(goal)
        
        assert estimate is not None, (
            f"Goal '{goal}' does not have an estimate defined!"
        )

    @given(goal=goal_strategy)
    @hyp_settings(max_examples=100)
    def test_every_goal_has_battery_improvement(self, goal: str):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Property: For any goal selection, battery improvement estimate SHALL be provided.
        """
        estimate = get_estimate_for_goal(goal)
        
        assert estimate is not None, f"Goal '{goal}' has no estimate"
        assert estimate.battery_improvement is not None, (
            f"Goal '{goal}' has no battery improvement estimate"
        )
        assert len(estimate.battery_improvement) > 0, (
            f"Goal '{goal}' has empty battery improvement estimate"
        )
        assert is_valid_battery_estimate(estimate.battery_improvement), (
            f"Goal '{goal}' has invalid battery improvement format: '{estimate.battery_improvement}'"
        )

    @given(goal=goal_strategy)
    @hyp_settings(max_examples=100)
    def test_every_goal_has_temp_reduction(self, goal: str):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Property: For any goal selection, temperature reduction estimate SHALL be provided.
        """
        estimate = get_estimate_for_goal(goal)
        
        assert estimate is not None, f"Goal '{goal}' has no estimate"
        assert estimate.temp_reduction is not None, (
            f"Goal '{goal}' has no temperature reduction estimate"
        )
        assert len(estimate.temp_reduction) > 0, (
            f"Goal '{goal}' has empty temperature reduction estimate"
        )
        assert is_valid_temp_estimate(estimate.temp_reduction), (
            f"Goal '{goal}' has invalid temperature reduction format: '{estimate.temp_reduction}'"
        )

    @given(goal=goal_strategy)
    @hyp_settings(max_examples=100)
    def test_every_goal_has_description(self, goal: str):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Property: For any goal selection, a description SHALL be provided.
        """
        estimate = get_estimate_for_goal(goal)
        
        assert estimate is not None, f"Goal '{goal}' has no estimate"
        assert estimate.description is not None, (
            f"Goal '{goal}' has no description"
        )
        assert len(estimate.description) > 0, (
            f"Goal '{goal}' has empty description"
        )

    def test_all_valid_goals_covered(self):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Verify that all valid goals have estimates defined.
        This is a completeness check.
        """
        for goal in VALID_GOALS:
            estimate = get_estimate_for_goal(goal)
            assert estimate is not None, f"Goal '{goal}' is missing from GOAL_ESTIMATES"
            assert estimate.battery_improvement, f"Goal '{goal}' missing battery_improvement"
            assert estimate.temp_reduction, f"Goal '{goal}' missing temp_reduction"
            assert estimate.description, f"Goal '{goal}' missing description"

    def test_estimates_are_positive_improvements(self):
        """
        **Feature: decktune-3.1-reliability-ux, Property 11: Goal estimates availability**
        **Validates: Requirements 5.4**
        
        Verify that battery estimates show positive improvements (+ prefix)
        and temperature estimates show reductions (- prefix).
        """
        for goal in VALID_GOALS:
            estimate = get_estimate_for_goal(goal)
            
            # Battery should be positive improvement
            assert estimate.battery_improvement.startswith('+'), (
                f"Goal '{goal}' battery estimate should start with '+': {estimate.battery_improvement}"
            )
            
            # Temperature should be reduction (negative)
            assert estimate.temp_reduction.startswith('-'), (
                f"Goal '{goal}' temp estimate should start with '-': {estimate.temp_reduction}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
