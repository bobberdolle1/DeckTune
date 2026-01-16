"""Property-based tests for Iron Seeker quality tier calculation.

Feature: iron-seeker, Property 12: Quality tier calculation
Validates: Requirements 4.1, 4.2
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.tuning.iron_seeker import QualityTier


# Property 12: Quality tier calculation
# For any undervolt value V: if V ≤ -35 then tier = "gold",
# if -35 < V ≤ -20 then tier = "silver", if V > -20 then tier = "bronze".
@given(value=st.integers(min_value=-100, max_value=50))
@settings(max_examples=100)
def test_property_12_quality_tier_calculation(value):
    """**Feature: iron-seeker, Property 12: Quality tier calculation**
    
    For any undervolt value V:
    - if V ≤ -35 then tier = "gold"
    - if -35 < V ≤ -20 then tier = "silver"
    - if V > -20 then tier = "bronze"
    
    **Validates: Requirements 4.1, 4.2**
    """
    tier = QualityTier.from_value(value)
    
    if value <= -35:
        assert tier == QualityTier.GOLD, f"Value {value} should be GOLD, got {tier}"
        assert tier.value == "gold"
    elif value <= -20:
        assert tier == QualityTier.SILVER, f"Value {value} should be SILVER, got {tier}"
        assert tier.value == "silver"
    else:
        assert tier == QualityTier.BRONZE, f"Value {value} should be BRONZE, got {tier}"
        assert tier.value == "bronze"


# Test boundary values explicitly
def test_quality_tier_boundary_gold_silver():
    """Test boundary between GOLD and SILVER at -35mV."""
    # -35 should be GOLD
    assert QualityTier.from_value(-35) == QualityTier.GOLD
    # -34 should be SILVER
    assert QualityTier.from_value(-34) == QualityTier.SILVER


def test_quality_tier_boundary_silver_bronze():
    """Test boundary between SILVER and BRONZE at -20mV."""
    # -20 should be SILVER
    assert QualityTier.from_value(-20) == QualityTier.SILVER
    # -19 should be BRONZE
    assert QualityTier.from_value(-19) == QualityTier.BRONZE


def test_quality_tier_zero():
    """Test that 0mV (no undervolt) is BRONZE."""
    assert QualityTier.from_value(0) == QualityTier.BRONZE


def test_quality_tier_extreme_values():
    """Test extreme undervolt values."""
    # Very deep undervolt should be GOLD
    assert QualityTier.from_value(-100) == QualityTier.GOLD
    # Positive value (overvolt) should be BRONZE
    assert QualityTier.from_value(10) == QualityTier.BRONZE
