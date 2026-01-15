"""Property test for profile serialization round-trip.

Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
Validates: Requirements 16.2

Tests that for any valid DynamicProfile, serializing to JSON and deserializing
back produces an equivalent profile.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.config import DynamicConfig, CoreConfig, VALID_STRATEGIES
from backend.dynamic.profiles import DynamicProfile, ProfileManager


# Strategy for valid profile names (non-empty, max 64 chars)
profile_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S"), min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=64,
).filter(lambda s: s.strip())

# Strategy for profile descriptions
description_strategy = st.text(min_size=0, max_size=256)

# Strategy for valid strategy names
strategy_strategy = st.sampled_from(list(VALID_STRATEGIES))

# Strategy for sample interval (10-5000 ms)
sample_interval_strategy = st.integers(min_value=10, max_value=5000)

# Strategy for hysteresis percent (1.0-20.0)
hysteresis_strategy = st.floats(min_value=1.0, max_value=20.0, allow_nan=False, allow_infinity=False)

# Strategy for status interval (100-10000 ms)
status_interval_strategy = st.integers(min_value=100, max_value=10000)

# Strategy for undervolt values in safe range (0 to -35)
safe_undervolt_strategy = st.integers(min_value=-35, max_value=0)

# Strategy for threshold (0.0-100.0)
threshold_strategy = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)


# Strategy for CoreConfig (without custom curve for simplicity)
def core_config_strategy(expert_mode: bool = False):
    """Generate valid CoreConfig instances."""
    min_limit = -100 if expert_mode else -35
    
    @st.composite
    def _core_config(draw):
        # Generate two values and ensure min_mv >= max_mv (min is less negative)
        v1 = draw(st.integers(min_value=min_limit, max_value=0))
        v2 = draw(st.integers(min_value=min_limit, max_value=0))
        min_mv = max(v1, v2)  # Less negative (closer to 0)
        max_mv = min(v1, v2)  # More negative
        
        return CoreConfig(
            min_mv=min_mv,
            max_mv=max_mv,
            threshold=draw(threshold_strategy),
            custom_curve=None,  # Skip custom curves for basic test
        )
    
    return _core_config()


# Strategy for DynamicConfig (non-custom strategies)
@st.composite
def dynamic_config_strategy(draw):
    """Generate valid DynamicConfig instances."""
    # Use non-custom strategies to avoid custom_curve requirement
    strategy = draw(st.sampled_from(["conservative", "balanced", "aggressive"]))
    expert_mode = draw(st.booleans())
    
    cores = [draw(core_config_strategy(expert_mode)) for _ in range(4)]
    
    return DynamicConfig(
        strategy=strategy,
        sample_interval_ms=draw(sample_interval_strategy),
        cores=cores,
        hysteresis_percent=draw(hysteresis_strategy),
        status_interval_ms=draw(status_interval_strategy),
        expert_mode=expert_mode,
    )


# Strategy for DynamicProfile
@st.composite
def dynamic_profile_strategy(draw):
    """Generate valid DynamicProfile instances."""
    return DynamicProfile(
        name=draw(profile_name_strategy),
        description=draw(description_strategy),
        config=draw(dynamic_config_strategy()),
    )


@given(profile=dynamic_profile_strategy())
@hyp_settings(max_examples=100)
def test_profile_serialization_roundtrip(profile):
    """Property 15: Profile Serialization Round-Trip
    
    For any valid DynamicProfile, serializing to JSON and deserializing back
    SHALL produce an equivalent profile.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.2
    """
    # Serialize to dict
    profile_dict = profile.to_dict()
    
    # Deserialize back
    restored = DynamicProfile.from_dict(profile_dict)
    
    # Verify equivalence
    assert restored.name == profile.name, \
        f"Name mismatch: {profile.name} -> {restored.name}"
    
    assert restored.description == profile.description, \
        f"Description mismatch: {profile.description} -> {restored.description}"
    
    # Verify config equivalence
    assert restored.config.strategy == profile.config.strategy, \
        f"Strategy mismatch: {profile.config.strategy} -> {restored.config.strategy}"
    
    assert restored.config.sample_interval_ms == profile.config.sample_interval_ms, \
        f"Sample interval mismatch: {profile.config.sample_interval_ms} -> {restored.config.sample_interval_ms}"
    
    assert restored.config.hysteresis_percent == profile.config.hysteresis_percent, \
        f"Hysteresis mismatch: {profile.config.hysteresis_percent} -> {restored.config.hysteresis_percent}"
    
    assert restored.config.status_interval_ms == profile.config.status_interval_ms, \
        f"Status interval mismatch: {profile.config.status_interval_ms} -> {restored.config.status_interval_ms}"
    
    assert restored.config.expert_mode == profile.config.expert_mode, \
        f"Expert mode mismatch: {profile.config.expert_mode} -> {restored.config.expert_mode}"
    
    # Verify cores
    assert len(restored.config.cores) == len(profile.config.cores), \
        f"Core count mismatch: {len(profile.config.cores)} -> {len(restored.config.cores)}"
    
    for i, (orig_core, rest_core) in enumerate(zip(profile.config.cores, restored.config.cores)):
        assert rest_core.min_mv == orig_core.min_mv, \
            f"Core {i} min_mv mismatch: {orig_core.min_mv} -> {rest_core.min_mv}"
        assert rest_core.max_mv == orig_core.max_mv, \
            f"Core {i} max_mv mismatch: {orig_core.max_mv} -> {rest_core.max_mv}"
        assert rest_core.threshold == orig_core.threshold, \
            f"Core {i} threshold mismatch: {orig_core.threshold} -> {rest_core.threshold}"


@given(profile=dynamic_profile_strategy())
@hyp_settings(max_examples=100)
def test_profile_json_export_import_roundtrip(profile):
    """Property 15: Profile Serialization Round-Trip - JSON String
    
    For any valid DynamicProfile, exporting to JSON string and importing back
    SHALL produce an equivalent profile.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.2
    """
    import json
    
    # Export to JSON string
    json_str = json.dumps(profile.to_dict())
    
    # Import back
    data = json.loads(json_str)
    restored = DynamicProfile.from_dict(data)
    
    # Verify equivalence
    assert restored.name == profile.name
    assert restored.description == profile.description
    assert restored.config.strategy == profile.config.strategy
    assert restored.config.sample_interval_ms == profile.config.sample_interval_ms
    assert len(restored.config.cores) == 4


@given(profile=dynamic_profile_strategy())
@hyp_settings(max_examples=100)
def test_profile_validation_after_roundtrip(profile):
    """Property 15: Profile Serialization Round-Trip - Validation
    
    For any valid DynamicProfile, after serialization round-trip the profile
    SHALL still pass validation.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.2
    """
    # Serialize and deserialize
    profile_dict = profile.to_dict()
    restored = DynamicProfile.from_dict(profile_dict)
    
    # Both should be valid
    original_errors = profile.validate()
    restored_errors = restored.validate()
    
    assert len(original_errors) == 0, \
        f"Original profile invalid: {original_errors}"
    
    assert len(restored_errors) == 0, \
        f"Restored profile invalid: {restored_errors}"


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_config_serialization_roundtrip(config):
    """Property 15: Profile Serialization Round-Trip - Config Only
    
    For any valid DynamicConfig, serializing to dict and deserializing back
    SHALL produce an equivalent config.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.2
    """
    # Serialize to dict
    config_dict = config.to_dict()
    
    # Deserialize back
    restored = DynamicConfig.from_dict(config_dict)
    
    # Verify equivalence
    assert restored.strategy == config.strategy
    assert restored.sample_interval_ms == config.sample_interval_ms
    assert restored.hysteresis_percent == config.hysteresis_percent
    assert restored.status_interval_ms == config.status_interval_ms
    assert restored.expert_mode == config.expert_mode
    assert len(restored.cores) == len(config.cores)


def test_default_profiles_are_valid():
    """Test that all default profiles pass validation.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.4
    """
    manager = ProfileManager()
    
    for name in ProfileManager.DEFAULT_PROFILE_NAMES:
        profile = manager.get_profile(name)
        assert profile is not None, f"Default profile '{name}' not found"
        
        errors = profile.validate()
        assert len(errors) == 0, f"Default profile '{name}' invalid: {errors}"


def test_default_profiles_roundtrip():
    """Test that default profiles survive serialization round-trip.
    
    Feature: dynamic-mode-refactor, Property 15: Profile Serialization Round-Trip
    Validates: Requirements 16.2, 16.4
    """
    manager = ProfileManager()
    
    for name in ProfileManager.DEFAULT_PROFILE_NAMES:
        profile = manager.get_profile(name)
        
        # Serialize and deserialize
        profile_dict = profile.to_dict()
        restored = DynamicProfile.from_dict(profile_dict)
        
        assert restored.name == profile.name
        assert restored.config.strategy == profile.config.strategy
        assert restored.config.sample_interval_ms == profile.config.sample_interval_ms
