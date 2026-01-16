"""Property-based tests for Iron Seeker safety margin calculation.

Feature: iron-seeker, Property 17: Safety margin with clamping
Validates: Requirements 6.1, 6.2
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.tuning.iron_seeker import calculate_recommended_value


# Property 17: Safety margin with clamping
# For any max_stable value M and safety_margin S, the recommended value SHALL be min(M + S, 0).
@given(
    max_stable=st.integers(min_value=-100, max_value=0),
    safety_margin=st.integers(min_value=0, max_value=20)
)
@settings(max_examples=100)
def test_property_17_safety_margin_with_clamping(max_stable, safety_margin):
    """**Feature: iron-seeker, Property 17: Safety margin with clamping**
    
    For any max_stable value M and safety_margin S, the recommended value
    SHALL be min(M + S, 0).
    
    This ensures:
    1. The safety margin is added to max_stable (Requirement 6.1)
    2. The result never exceeds 0mV (Requirement 6.2)
    
    **Validates: Requirements 6.1, 6.2**
    """
    recommended = calculate_recommended_value(max_stable, safety_margin)
    
    # Property: recommended == min(max_stable + safety_margin, 0)
    expected = min(max_stable + safety_margin, 0)
    assert recommended == expected, (
        f"For max_stable={max_stable}, safety_margin={safety_margin}: "
        f"expected {expected}, got {recommended}"
    )
    
    # Additional invariants:
    # 1. Recommended value should never exceed 0
    assert recommended <= 0, f"Recommended value {recommended} exceeds 0"
    
    # 2. Recommended value should be >= max_stable (less negative or equal)
    assert recommended >= max_stable, (
        f"Recommended {recommended} is more negative than max_stable {max_stable}"
    )


@given(
    max_stable=st.integers(min_value=-100, max_value=-10),
    safety_margin=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100)
def test_safety_margin_no_clamping_needed(max_stable, safety_margin):
    """Test cases where clamping is not needed (result stays negative).
    
    When max_stable + safety_margin < 0, the result should be exactly
    max_stable + safety_margin without clamping.
    """
    # Only test cases where no clamping is needed
    if max_stable + safety_margin >= 0:
        return  # Skip this case, covered by clamping test
    
    recommended = calculate_recommended_value(max_stable, safety_margin)
    
    # Should be exactly max_stable + safety_margin
    assert recommended == max_stable + safety_margin


@given(
    max_stable=st.integers(min_value=-5, max_value=0),
    safety_margin=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
def test_safety_margin_clamping_to_zero(max_stable, safety_margin):
    """Test cases where clamping to 0 is required.
    
    When max_stable + safety_margin >= 0, the result should be clamped to 0.
    """
    # Only test cases where clamping is needed
    if max_stable + safety_margin < 0:
        return  # Skip this case, covered by no-clamping test
    
    recommended = calculate_recommended_value(max_stable, safety_margin)
    
    # Should be clamped to 0
    assert recommended == 0


def test_safety_margin_boundary_cases():
    """Test specific boundary cases for safety margin calculation."""
    # Case 1: Exact boundary (result is exactly 0)
    assert calculate_recommended_value(-5, 5) == 0
    
    # Case 2: Just below boundary (result is -1)
    assert calculate_recommended_value(-6, 5) == -1
    
    # Case 3: Would exceed 0 without clamping
    assert calculate_recommended_value(-3, 5) == 0
    
    # Case 4: Zero max_stable
    assert calculate_recommended_value(0, 5) == 0
    
    # Case 5: Zero safety margin
    assert calculate_recommended_value(-30, 0) == -30
    
    # Case 6: Both zero
    assert calculate_recommended_value(0, 0) == 0
