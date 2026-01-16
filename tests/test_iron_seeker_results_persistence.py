"""Property-based tests for Iron Seeker results persistence.

Feature: iron-seeker, Property 13: Results persistence
Feature: iron-seeker, Property 18: Results storage structure
Validates: Requirements 4.4, 6.3
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import MagicMock

from backend.tuning.iron_seeker import (
    CoreResult,
    IronSeekerResult,
    IronSeekerStoredResult,
    QualityTier,
    NUM_CORES,
)


# Strategies for generating test data
@st.composite
def core_results_strategy(draw):
    """Generate a valid CoreResult."""
    core_index = draw(st.integers(min_value=0, max_value=3))
    max_stable = draw(st.integers(min_value=-100, max_value=0))
    safety_margin = draw(st.integers(min_value=0, max_value=20))
    recommended = min(max_stable + safety_margin, 0)
    tier = QualityTier.from_value(max_stable)
    iterations = draw(st.integers(min_value=1, max_value=100))
    failed_value = draw(st.one_of(st.none(), st.integers(min_value=-100, max_value=0)))
    
    return CoreResult(
        core_index=core_index,
        max_stable=max_stable,
        recommended=recommended,
        quality_tier=tier.value,
        iterations=iterations,
        failed_value=failed_value
    )


@st.composite
def iron_seeker_result_strategy(draw):
    """Generate a valid IronSeekerResult with exactly 4 cores."""
    cores = []
    for i in range(NUM_CORES):
        max_stable = draw(st.integers(min_value=-100, max_value=0))
        safety_margin = draw(st.integers(min_value=0, max_value=20))
        recommended = min(max_stable + safety_margin, 0)
        tier = QualityTier.from_value(max_stable)
        iterations = draw(st.integers(min_value=1, max_value=100))
        failed_value = draw(st.one_of(st.none(), st.integers(min_value=-100, max_value=0)))
        
        cores.append(CoreResult(
            core_index=i,
            max_stable=max_stable,
            recommended=recommended,
            quality_tier=tier.value,
            iterations=iterations,
            failed_value=failed_value
        ))
    
    duration = draw(st.floats(min_value=0.1, max_value=10000.0, allow_nan=False))
    recovered = draw(st.booleans())
    aborted = draw(st.booleans())
    
    return IronSeekerResult(
        cores=cores,
        duration=duration,
        recovered=recovered,
        aborted=aborted
    )


# Property 13: Results persistence
# For any successful Iron Seeker completion, the saved results SHALL contain
# exactly 4 CoreResult entries with valid max_stable, recommended, and tier fields.
@given(result=iron_seeker_result_strategy())
@settings(max_examples=100)
def test_property_13_results_persistence(result):
    """**Feature: iron-seeker, Property 13: Results persistence**
    
    For any successful Iron Seeker completion, the saved results SHALL contain
    exactly 4 CoreResult entries with valid max_stable, recommended, and tier fields.
    
    **Validates: Requirements 4.4**
    """
    # Convert to stored format
    stored = IronSeekerStoredResult.from_result(result)
    
    # Property: Must have exactly 4 core entries
    assert len(stored.cores) == NUM_CORES, (
        f"Expected {NUM_CORES} cores, got {len(stored.cores)}"
    )
    
    # Property: Each core must have valid fields
    valid_tiers = {"gold", "silver", "bronze"}
    for core in stored.cores:
        # Must have all required fields
        assert "index" in core, "Missing 'index' field"
        assert "max_stable" in core, "Missing 'max_stable' field"
        assert "recommended" in core, "Missing 'recommended' field"
        assert "tier" in core, "Missing 'tier' field"
        
        # max_stable must be <= 0
        assert core["max_stable"] <= 0, (
            f"max_stable {core['max_stable']} exceeds 0"
        )
        
        # recommended must be <= 0
        assert core["recommended"] <= 0, (
            f"recommended {core['recommended']} exceeds 0"
        )
        
        # tier must be valid
        assert core["tier"] in valid_tiers, (
            f"Invalid tier '{core['tier']}', expected one of {valid_tiers}"
        )
    
    # Property: Validation should pass
    assert stored.validate(), "Stored result failed validation"


# Property 18: Results storage structure
# For any saved Iron Seeker result, the storage SHALL contain both
# max_stable and recommended values for each core.
@given(result=iron_seeker_result_strategy())
@settings(max_examples=100)
def test_property_18_results_storage_structure(result):
    """**Feature: iron-seeker, Property 18: Results storage structure**
    
    For any saved Iron Seeker result, the storage SHALL contain both
    max_stable and recommended values for each core.
    
    **Validates: Requirements 6.3**
    """
    # Convert to stored format
    stored = IronSeekerStoredResult.from_result(result)
    
    # Convert to dict (as would be stored in settings)
    stored_dict = stored.to_dict()
    
    # Property: Must have cores, timestamp, and duration
    assert "cores" in stored_dict, "Missing 'cores' in stored dict"
    assert "timestamp" in stored_dict, "Missing 'timestamp' in stored dict"
    assert "duration" in stored_dict, "Missing 'duration' in stored dict"
    
    # Property: Each core must have both max_stable and recommended
    for i, core in enumerate(stored_dict["cores"]):
        assert "max_stable" in core, f"Core {i} missing 'max_stable'"
        assert "recommended" in core, f"Core {i} missing 'recommended'"
        
        # Verify the relationship: recommended >= max_stable (less negative)
        assert core["recommended"] >= core["max_stable"], (
            f"Core {i}: recommended {core['recommended']} < max_stable {core['max_stable']}"
        )
    
    # Property: Duration should be preserved
    assert stored_dict["duration"] == result.duration, (
        f"Duration mismatch: expected {result.duration}, got {stored_dict['duration']}"
    )


@given(result=iron_seeker_result_strategy())
@settings(max_examples=100)
def test_stored_result_round_trip(result):
    """Test that stored results can be serialized and deserialized correctly."""
    # Convert to stored format
    stored = IronSeekerStoredResult.from_result(result)
    
    # Convert to dict
    stored_dict = stored.to_dict()
    
    # Convert back from dict
    restored = IronSeekerStoredResult.from_dict(stored_dict)
    
    # Verify round-trip preserves data
    assert len(restored.cores) == len(stored.cores)
    assert restored.duration == stored.duration
    assert restored.timestamp == stored.timestamp
    
    for i in range(len(stored.cores)):
        assert restored.cores[i] == stored.cores[i]


def test_stored_result_validation_rejects_invalid():
    """Test that validation rejects invalid stored results."""
    # Missing cores
    invalid1 = IronSeekerStoredResult(
        cores=[],
        timestamp=datetime.now().isoformat(),
        duration=100.0
    )
    assert not invalid1.validate()
    
    # Wrong number of cores
    invalid2 = IronSeekerStoredResult(
        cores=[{"index": 0, "max_stable": -30, "recommended": -25, "tier": "silver"}],
        timestamp=datetime.now().isoformat(),
        duration=100.0
    )
    assert not invalid2.validate()
    
    # Missing required field
    invalid3 = IronSeekerStoredResult(
        cores=[
            {"index": 0, "max_stable": -30, "tier": "silver"},  # Missing recommended
            {"index": 1, "max_stable": -40, "recommended": -35, "tier": "gold"},
            {"index": 2, "max_stable": -25, "recommended": -20, "tier": "silver"},
            {"index": 3, "max_stable": -15, "recommended": -10, "tier": "bronze"},
        ],
        timestamp=datetime.now().isoformat(),
        duration=100.0
    )
    assert not invalid3.validate()
    
    # Invalid tier
    invalid4 = IronSeekerStoredResult(
        cores=[
            {"index": 0, "max_stable": -30, "recommended": -25, "tier": "platinum"},  # Invalid tier
            {"index": 1, "max_stable": -40, "recommended": -35, "tier": "gold"},
            {"index": 2, "max_stable": -25, "recommended": -20, "tier": "silver"},
            {"index": 3, "max_stable": -15, "recommended": -10, "tier": "bronze"},
        ],
        timestamp=datetime.now().isoformat(),
        duration=100.0
    )
    assert not invalid4.validate()


def test_stored_result_validation_accepts_valid():
    """Test that validation accepts valid stored results."""
    valid = IronSeekerStoredResult(
        cores=[
            {"index": 0, "max_stable": -30, "recommended": -25, "tier": "silver"},
            {"index": 1, "max_stable": -40, "recommended": -35, "tier": "gold"},
            {"index": 2, "max_stable": -25, "recommended": -20, "tier": "silver"},
            {"index": 3, "max_stable": -15, "recommended": -10, "tier": "bronze"},
        ],
        timestamp=datetime.now().isoformat(),
        duration=100.0
    )
    assert valid.validate()
