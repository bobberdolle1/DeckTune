"""Property-based tests for Iron Seeker preset structure.

Feature: iron-seeker, Property 21: Preset structure
Validates: Requirements 8.2
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime

from backend.tuning.iron_seeker import (
    IronSeekerPreset,
    IronSeekerResult,
    IronSeekerStoredResult,
    CoreResult,
    QualityTier,
)


# Strategy for generating valid quality tiers
tier_strategy = st.sampled_from(["gold", "silver", "bronze"])

# Strategy for generating valid undervolt values (0 to -100 mV)
undervolt_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid preset names
name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=1,
    max_size=64
).filter(lambda x: x.strip())

# Strategy for generating ISO timestamps
timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.isoformat())


@given(
    name=name_strategy,
    values=st.lists(undervolt_strategy, min_size=4, max_size=4),
    tiers=st.lists(tier_strategy, min_size=4, max_size=4),
    timestamp=timestamp_strategy,
    description=st.text(max_size=200)
)
@settings(max_examples=100)
def test_property_21_preset_structure(name, values, tiers, timestamp, description):
    """**Feature: iron-seeker, Property 21: Preset structure**
    
    For any preset saved from Iron Seeker results, the preset SHALL contain:
    per-core values array, quality tiers array, and discovery timestamp.
    
    **Validates: Requirements 8.2**
    """
    # Create preset
    preset = IronSeekerPreset(
        name=name,
        values=values,
        tiers=tiers,
        timestamp=timestamp,
        description=description
    )
    
    # Verify preset contains required fields
    assert preset.name == name, "Preset must contain name"
    assert preset.values == values, "Preset must contain per-core values array"
    assert preset.tiers == tiers, "Preset must contain quality tiers array"
    assert preset.timestamp == timestamp, "Preset must contain discovery timestamp"
    
    # Verify structure constraints
    assert len(preset.values) == 4, "Preset must have exactly 4 per-core values"
    assert len(preset.tiers) == 4, "Preset must have exactly 4 quality tiers"
    
    # Verify serialization round-trip preserves structure
    preset_dict = preset.to_dict()
    
    assert "name" in preset_dict, "Serialized preset must contain name"
    assert "values" in preset_dict, "Serialized preset must contain values"
    assert "tiers" in preset_dict, "Serialized preset must contain tiers"
    assert "timestamp" in preset_dict, "Serialized preset must contain timestamp"
    
    assert preset_dict["values"] == values, "Serialized values must match"
    assert preset_dict["tiers"] == tiers, "Serialized tiers must match"
    assert preset_dict["timestamp"] == timestamp, "Serialized timestamp must match"
    
    # Verify deserialization produces equivalent preset
    restored = IronSeekerPreset.from_dict(preset_dict)
    
    assert restored.name == preset.name
    assert restored.values == preset.values
    assert restored.tiers == preset.tiers
    assert restored.timestamp == preset.timestamp
    assert restored.description == preset.description


@given(
    core0_stable=undervolt_strategy,
    core1_stable=undervolt_strategy,
    core2_stable=undervolt_strategy,
    core3_stable=undervolt_strategy,
    safety_margin=st.integers(min_value=0, max_value=20),
    name=name_strategy,
    description=st.text(max_size=200)
)
@settings(max_examples=100)
def test_preset_from_result_contains_required_fields(
    core0_stable, core1_stable, core2_stable, core3_stable,
    safety_margin, name, description
):
    """Test that presets created from IronSeekerResult contain required fields.
    
    For any IronSeekerResult, creating a preset SHALL produce a preset
    with per-core values array, quality tiers array, and discovery timestamp.
    
    **Validates: Requirements 8.2**
    """
    # Calculate recommended values (with safety margin, clamped to 0)
    def calc_recommended(max_stable):
        return min(max_stable + safety_margin, 0)
    
    # Create CoreResults
    cores = [
        CoreResult(
            core_index=0,
            max_stable=core0_stable,
            recommended=calc_recommended(core0_stable),
            quality_tier=QualityTier.from_value(core0_stable).value,
            iterations=5
        ),
        CoreResult(
            core_index=1,
            max_stable=core1_stable,
            recommended=calc_recommended(core1_stable),
            quality_tier=QualityTier.from_value(core1_stable).value,
            iterations=5
        ),
        CoreResult(
            core_index=2,
            max_stable=core2_stable,
            recommended=calc_recommended(core2_stable),
            quality_tier=QualityTier.from_value(core2_stable).value,
            iterations=5
        ),
        CoreResult(
            core_index=3,
            max_stable=core3_stable,
            recommended=calc_recommended(core3_stable),
            quality_tier=QualityTier.from_value(core3_stable).value,
            iterations=5
        ),
    ]
    
    result = IronSeekerResult(
        cores=cores,
        duration=120.5,
        recovered=False,
        aborted=False
    )
    
    # Create preset from result
    preset = IronSeekerPreset.from_result(result, name, description)
    
    # Verify preset contains required fields (Property 21)
    assert len(preset.values) == 4, "Preset must have exactly 4 per-core values"
    assert len(preset.tiers) == 4, "Preset must have exactly 4 quality tiers"
    assert preset.timestamp, "Preset must have a timestamp"
    
    # Verify values are the recommended values from the result
    expected_values = [calc_recommended(v) for v in [core0_stable, core1_stable, core2_stable, core3_stable]]
    assert preset.values == expected_values, "Preset values must be recommended values from result"
    
    # Verify tiers match the result
    expected_tiers = [QualityTier.from_value(v).value for v in [core0_stable, core1_stable, core2_stable, core3_stable]]
    assert preset.tiers == expected_tiers, "Preset tiers must match result tiers"


@given(
    values=st.lists(undervolt_strategy, min_size=4, max_size=4),
    tiers=st.lists(tier_strategy, min_size=4, max_size=4),
    timestamp=timestamp_strategy,
    name=name_strategy
)
@settings(max_examples=100)
def test_preset_serialization_roundtrip(values, tiers, timestamp, name):
    """Test that preset serialization is a round-trip.
    
    For any valid preset, serializing to dict and deserializing
    SHALL produce an equivalent preset.
    
    **Validates: Requirements 8.2**
    """
    preset = IronSeekerPreset(
        name=name,
        values=values,
        tiers=tiers,
        timestamp=timestamp
    )
    
    # Serialize and deserialize
    preset_dict = preset.to_dict()
    restored = IronSeekerPreset.from_dict(preset_dict)
    
    # Verify equivalence
    assert restored.name == preset.name
    assert restored.values == preset.values
    assert restored.tiers == preset.tiers
    assert restored.timestamp == preset.timestamp


def test_preset_validation_rejects_invalid_tier():
    """Test that preset validation rejects invalid tier values."""
    with pytest.raises(ValueError, match="must be one of"):
        IronSeekerPreset(
            name="Test",
            values=[-30, -30, -30, -30],
            tiers=["gold", "silver", "invalid", "bronze"],
            timestamp="2026-01-16T12:00:00"
        )


def test_preset_validation_rejects_wrong_values_count():
    """Test that preset validation rejects wrong number of values."""
    with pytest.raises(ValueError, match="must have exactly 4"):
        IronSeekerPreset(
            name="Test",
            values=[-30, -30, -30],  # Only 3 values
            tiers=["gold", "silver", "bronze", "gold"],
            timestamp="2026-01-16T12:00:00"
        )


def test_preset_validation_rejects_wrong_tiers_count():
    """Test that preset validation rejects wrong number of tiers."""
    with pytest.raises(ValueError, match="must have exactly 4"):
        IronSeekerPreset(
            name="Test",
            values=[-30, -30, -30, -30],
            tiers=["gold", "silver", "bronze"],  # Only 3 tiers
            timestamp="2026-01-16T12:00:00"
        )


def test_preset_validate_method():
    """Test the validate() method returns errors for invalid presets."""
    # Valid preset should have no errors
    valid_preset = IronSeekerPreset(
        name="Valid",
        values=[-30, -25, -35, -20],
        tiers=["silver", "silver", "gold", "silver"],
        timestamp="2026-01-16T12:00:00"
    )
    assert valid_preset.validate() == []
    assert valid_preset.is_valid()


def test_preset_validate_empty_name():
    """Test that validate() catches empty name."""
    # Create preset with valid structure first, then modify
    preset = IronSeekerPreset(
        name="temp",
        values=[-30, -30, -30, -30],
        tiers=["gold", "gold", "gold", "gold"],
        timestamp="2026-01-16T12:00:00"
    )
    # Manually set empty name to test validation
    preset.name = ""
    
    errors = preset.validate()
    assert any("name" in e.lower() for e in errors)
    assert not preset.is_valid()


def test_preset_validate_value_out_of_range():
    """Test that validate() catches values out of range."""
    preset = IronSeekerPreset(
        name="Test",
        values=[-30, -30, -30, -30],
        tiers=["gold", "gold", "gold", "gold"],
        timestamp="2026-01-16T12:00:00"
    )
    # Manually set invalid value
    preset.values[0] = 10  # Positive value is invalid
    
    errors = preset.validate()
    assert any("values[0]" in e for e in errors)
    assert not preset.is_valid()
