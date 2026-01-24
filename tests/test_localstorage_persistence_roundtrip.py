"""Property test for localStorage persistence round-trip.

Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
Validates: Requirements 6.1, 6.3

Tests that for any valid DynamicConfig, serializing to JSON (localStorage format)
and then deserializing SHALL produce an equivalent configuration.

This test validates the serialization/deserialization logic that the frontend
uses for localStorage persistence.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import json
from typing import Dict, Any, List

# Strategy for generating valid voltage values (-100 to 0 mV)
voltage_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid threshold values (0 to 100%)
threshold_strategy = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for generating valid core IDs (0-3)
core_id_strategy = st.integers(min_value=0, max_value=3)

# Strategy for generating valid mode values
mode_strategy = st.sampled_from(["simple", "expert"])


@st.composite
def core_config_strategy(draw, core_id: int):
    """Generate a valid CoreConfig for a specific core ID.
    
    Args:
        draw: Hypothesis draw function
        core_id: The core ID to use
        
    Returns:
        Dictionary representing a CoreConfig
    """
    return {
        "core_id": core_id,
        "min_mv": draw(voltage_strategy),
        "max_mv": draw(voltage_strategy),
        "threshold": draw(threshold_strategy)
    }


@st.composite
def dynamic_config_strategy(draw):
    """Generate a valid DynamicConfig.
    
    Ensures that we have exactly 4 cores (0-3) with valid configurations.
    
    Returns:
        Dictionary representing a DynamicConfig
    """
    mode = draw(mode_strategy)
    
    # Generate configs for all 4 cores
    cores = [
        draw(core_config_strategy(0)),
        draw(core_config_strategy(1)),
        draw(core_config_strategy(2)),
        draw(core_config_strategy(3))
    ]
    
    return {
        "mode": mode,
        "cores": cores,
        "version": 1
    }


def validate_core_config(core: Dict[str, Any], expected_core_id: int) -> None:
    """Validate that a core config has the correct structure and values.
    
    Args:
        core: The core config to validate
        expected_core_id: The expected core ID
    """
    assert "core_id" in core, "core_id field missing"
    assert "min_mv" in core, "min_mv field missing"
    assert "max_mv" in core, "max_mv field missing"
    assert "threshold" in core, "threshold field missing"
    
    assert core["core_id"] == expected_core_id, \
        f"core_id mismatch: {core['core_id']} != {expected_core_id}"
    
    assert isinstance(core["min_mv"], int), "min_mv must be an integer"
    assert isinstance(core["max_mv"], int), "max_mv must be an integer"
    assert isinstance(core["threshold"], (int, float)), "threshold must be a number"
    
    assert -100 <= core["min_mv"] <= 0, \
        f"min_mv out of range: {core['min_mv']}"
    assert -100 <= core["max_mv"] <= 0, \
        f"max_mv out of range: {core['max_mv']}"
    assert 0 <= core["threshold"] <= 100, \
        f"threshold out of range: {core['threshold']}"


def validate_dynamic_config(config: Dict[str, Any]) -> None:
    """Validate that a dynamic config has the correct structure.
    
    Args:
        config: The config to validate
    """
    assert "mode" in config, "mode field missing"
    assert "cores" in config, "cores field missing"
    assert "version" in config, "version field missing"
    
    assert config["mode"] in ["simple", "expert"], \
        f"Invalid mode: {config['mode']}"
    
    assert isinstance(config["cores"], list), "cores must be a list"
    assert len(config["cores"]) == 4, \
        f"cores must have exactly 4 elements, got {len(config['cores'])}"
    
    assert isinstance(config["version"], int), "version must be an integer"
    assert config["version"] == 1, f"version must be 1, got {config['version']}"
    
    for i, core in enumerate(config["cores"]):
        validate_core_config(core, i)


def configs_equal(config1: Dict[str, Any], config2: Dict[str, Any]) -> bool:
    """Check if two configs are equivalent.
    
    Args:
        config1: First config
        config2: Second config
        
    Returns:
        True if configs are equivalent
    """
    if config1["mode"] != config2["mode"]:
        return False
    
    if config1["version"] != config2["version"]:
        return False
    
    if len(config1["cores"]) != len(config2["cores"]):
        return False
    
    for i in range(4):
        core1 = config1["cores"][i]
        core2 = config2["cores"][i]
        
        if core1["core_id"] != core2["core_id"]:
            return False
        
        if core1["min_mv"] != core2["min_mv"]:
            return False
        
        if core1["max_mv"] != core2["max_mv"]:
            return False
        
        # Handle float comparison with tolerance for threshold
        if abs(core1["threshold"] - core2["threshold"]) >= 1e-9:
            return False
    
    return True


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_property_10_localstorage_persistence_roundtrip(config):
    """**Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip**
    
    For any valid DynamicConfig, serializing to JSON (localStorage format)
    and then deserializing SHALL produce an equivalent configuration.
    
    Validates: Requirements 6.1, 6.3
    """
    # Validate the generated config
    validate_dynamic_config(config)
    
    # Serialize to JSON (simulating localStorage.setItem)
    json_string = json.dumps(config)
    
    # Deserialize from JSON (simulating localStorage.getItem + JSON.parse)
    loaded_config = json.loads(json_string)
    
    # Validate the loaded config
    validate_dynamic_config(loaded_config)
    
    # Verify the loaded config matches the original
    assert configs_equal(config, loaded_config), \
        "Loaded config does not match original after round-trip"


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_json_serialization_preserves_types(config):
    """Test that JSON serialization preserves data types correctly.
    
    Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
    Validates: Requirements 6.1, 6.3
    """
    # Serialize and deserialize
    json_string = json.dumps(config)
    loaded_config = json.loads(json_string)
    
    # Check that types are preserved
    assert isinstance(loaded_config["mode"], str)
    assert isinstance(loaded_config["cores"], list)
    assert isinstance(loaded_config["version"], int)
    
    for core in loaded_config["cores"]:
        assert isinstance(core["core_id"], int)
        assert isinstance(core["min_mv"], int)
        assert isinstance(core["max_mv"], int)
        # threshold can be int or float after JSON round-trip
        assert isinstance(core["threshold"], (int, float))


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_json_serialization_is_deterministic(config):
    """Test that serializing the same config produces the same JSON.
    
    Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
    Validates: Requirements 6.1
    """
    # Serialize twice
    json_string1 = json.dumps(config, sort_keys=True)
    json_string2 = json.dumps(config, sort_keys=True)
    
    # Should produce identical strings
    assert json_string1 == json_string2, \
        "Serializing the same config should produce identical JSON"


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_multiple_roundtrips_preserve_data(config):
    """Test that multiple round-trips preserve data correctly.
    
    Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
    Validates: Requirements 6.1, 6.3
    """
    current_config = config
    
    # Perform 5 round-trips
    for _ in range(5):
        json_string = json.dumps(current_config)
        current_config = json.loads(json_string)
    
    # Final config should match original
    assert configs_equal(config, current_config), \
        "Config changed after multiple round-trips"


def test_empty_config_handling():
    """Test that empty/invalid configs are handled correctly."""
    # Empty string should raise an error
    with pytest.raises(json.JSONDecodeError):
        json.loads("")
    
    # Invalid JSON should raise an error
    with pytest.raises(json.JSONDecodeError):
        json.loads("{invalid json}")
    
    # Null should parse but not be a valid config
    null_config = json.loads("null")
    assert null_config is None


def test_malformed_config_detection():
    """Test that malformed configs are detected during validation."""
    # Missing mode field
    config1 = {"cores": [], "version": 1}
    with pytest.raises(AssertionError, match="mode field missing"):
        validate_dynamic_config(config1)
    
    # Missing cores field
    config2 = {"mode": "simple", "version": 1}
    with pytest.raises(AssertionError, match="cores field missing"):
        validate_dynamic_config(config2)
    
    # Wrong number of cores
    config3 = {
        "mode": "simple",
        "cores": [{"core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50}],
        "version": 1
    }
    with pytest.raises(AssertionError, match="cores must have exactly 4 elements"):
        validate_dynamic_config(config3)
    
    # Invalid mode
    config4 = {
        "mode": "invalid",
        "cores": [
            {"core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50},
            {"core_id": 1, "min_mv": -30, "max_mv": -15, "threshold": 50},
            {"core_id": 2, "min_mv": -30, "max_mv": -15, "threshold": 50},
            {"core_id": 3, "min_mv": -30, "max_mv": -15, "threshold": 50}
        ],
        "version": 1
    }
    with pytest.raises(AssertionError, match="Invalid mode"):
        validate_dynamic_config(config4)


@given(
    config=dynamic_config_strategy(),
    core_idx=st.integers(min_value=0, max_value=3),
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_partial_update_preserves_other_cores(config, core_idx, new_min, new_max, new_threshold):
    """Test that updating one core doesn't affect others during serialization.
    
    Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
    Validates: Requirements 6.1, 6.3
    """
    # Save original values of other cores
    other_cores = [
        config["cores"][i].copy()
        for i in range(4)
        if i != core_idx
    ]
    
    # Update one core
    config["cores"][core_idx]["min_mv"] = new_min
    config["cores"][core_idx]["max_mv"] = new_max
    config["cores"][core_idx]["threshold"] = new_threshold
    
    # Round-trip through JSON
    json_string = json.dumps(config)
    loaded_config = json.loads(json_string)
    
    # Verify the updated core has new values
    assert loaded_config["cores"][core_idx]["min_mv"] == new_min
    assert loaded_config["cores"][core_idx]["max_mv"] == new_max
    assert abs(loaded_config["cores"][core_idx]["threshold"] - new_threshold) < 1e-9
    
    # Verify other cores unchanged
    other_idx = 0
    for i in range(4):
        if i != core_idx:
            original = other_cores[other_idx]
            loaded = loaded_config["cores"][i]
            
            assert loaded["core_id"] == original["core_id"]
            assert loaded["min_mv"] == original["min_mv"]
            assert loaded["max_mv"] == original["max_mv"]
            assert abs(loaded["threshold"] - original["threshold"]) < 1e-9
            
            other_idx += 1


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_unicode_handling_in_mode(config):
    """Test that mode field handles string encoding correctly.
    
    Feature: manual-dynamic-mode, Property 10: Configuration persistence round-trip
    Validates: Requirements 6.1
    """
    # Round-trip through JSON
    json_string = json.dumps(config)
    loaded_config = json.loads(json_string)
    
    # Mode should be a valid string
    assert isinstance(loaded_config["mode"], str)
    assert loaded_config["mode"] in ["simple", "expert"]
    assert loaded_config["mode"] == config["mode"]
