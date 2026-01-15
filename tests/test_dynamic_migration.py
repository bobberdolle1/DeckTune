"""Property test for dynamic settings migration.

Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
Validates: Requirements 11.1, 11.2

Tests that for any valid old-format dynamicSettings, migration to new format
and back preserves semantic equivalence. Strategy name mapping:
DEFAULT→balanced, AGGRESSIVE→aggressive, MANUAL→custom.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings, assume

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.config import DynamicConfig, CoreConfig
from backend.dynamic.migration import (
    migrate_dynamic_settings,
    convert_to_old_format,
    is_old_format,
    STRATEGY_MAP_OLD_TO_NEW,
    STRATEGY_MAP_NEW_TO_OLD,
)


# Strategy for old format strategy names
old_strategy_strategy = st.sampled_from(["DEFAULT", "AGGRESSIVE", "MANUAL"])

# Strategy for old format sample interval (microseconds, typically 10000-5000000)
old_interval_strategy = st.integers(min_value=10000, max_value=5000000)

# Strategy for old format percentage values (0-100)
old_percent_strategy = st.integers(min_value=0, max_value=100)

# Strategy for old format threshold (0-100)
old_threshold_strategy = st.integers(min_value=0, max_value=100)

# Strategy for manual curve points
manual_point_strategy = st.fixed_dictionaries({
    "load": st.integers(min_value=0, max_value=100),
    "value": old_percent_strategy,
})

# Strategy for old format core config
old_core_strategy = st.fixed_dictionaries({
    "maximumValue": old_percent_strategy,
    "minimumValue": old_percent_strategy,
    "threshold": old_threshold_strategy,
    "manualPoints": st.lists(manual_point_strategy, min_size=0, max_size=5),
})

# Strategy for complete old format settings
old_settings_strategy = st.fixed_dictionaries({
    "strategy": old_strategy_strategy,
    "sample_interval": old_interval_strategy,
    "cores": st.lists(old_core_strategy, min_size=4, max_size=4),
})


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_preserves_strategy_semantics(old_settings):
    """Property 12: Settings Migration Round-Trip - Strategy Mapping
    
    For any valid old-format dynamicSettings, the strategy name SHALL be
    correctly mapped: DEFAULT→balanced, AGGRESSIVE→aggressive, MANUAL→custom.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    # Verify strategy mapping
    old_strategy = old_settings["strategy"]
    expected_new_strategy = STRATEGY_MAP_OLD_TO_NEW[old_strategy]
    
    assert new_config.strategy == expected_new_strategy, \
        f"Strategy mapping failed: {old_strategy} -> {new_config.strategy}, expected {expected_new_strategy}"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_roundtrip_strategy(old_settings):
    """Property 12: Settings Migration Round-Trip - Strategy Round-Trip
    
    For any valid old-format dynamicSettings, migrating to new format and back
    SHALL preserve the original strategy name.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    # Convert back to old format
    roundtrip_old = convert_to_old_format(new_config)
    
    # Strategy should match original
    assert roundtrip_old["strategy"] == old_settings["strategy"], \
        f"Strategy round-trip failed: {old_settings['strategy']} -> {new_config.strategy} -> {roundtrip_old['strategy']}"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_preserves_interval_order_of_magnitude(old_settings):
    """Property 12: Settings Migration Round-Trip - Interval Conversion
    
    For any valid old-format dynamicSettings, the sample interval SHALL be
    correctly converted from microseconds to milliseconds (divided by 1000).
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    # Old interval is in microseconds, new is in milliseconds
    old_interval_us = old_settings["sample_interval"]
    expected_interval_ms = max(10, min(5000, old_interval_us // 1000))
    
    assert new_config.sample_interval_ms == expected_interval_ms, \
        f"Interval conversion failed: {old_interval_us}us -> {new_config.sample_interval_ms}ms, expected {expected_interval_ms}ms"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_roundtrip_interval(old_settings):
    """Property 12: Settings Migration Round-Trip - Interval Round-Trip
    
    For any valid old-format dynamicSettings, migrating to new format and back
    SHALL preserve the sample interval (within clamping bounds).
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    # Convert back to old format
    roundtrip_old = convert_to_old_format(new_config)
    
    # Calculate expected clamped interval
    old_interval_us = old_settings["sample_interval"]
    clamped_ms = max(10, min(5000, old_interval_us // 1000))
    expected_roundtrip_us = clamped_ms * 1000
    
    assert roundtrip_old["sample_interval"] == expected_roundtrip_us, \
        f"Interval round-trip failed: {old_interval_us} -> {new_config.sample_interval_ms}ms -> {roundtrip_old['sample_interval']}"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_produces_valid_config(old_settings):
    """Property 12: Settings Migration Round-Trip - Valid Output
    
    For any valid old-format dynamicSettings, migration SHALL produce a
    valid DynamicConfig that passes validation.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    # Validate the new config
    errors = new_config.validate()
    
    assert len(errors) == 0, \
        f"Migration produced invalid config: {errors}"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_migration_preserves_core_count(old_settings):
    """Property 12: Settings Migration Round-Trip - Core Count
    
    For any valid old-format dynamicSettings, migration SHALL preserve
    exactly 4 cores.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    
    assert len(new_config.cores) == 4, \
        f"Core count mismatch: expected 4, got {len(new_config.cores)}"
    
    # Convert back
    roundtrip_old = convert_to_old_format(new_config)
    
    assert len(roundtrip_old["cores"]) == 4, \
        f"Round-trip core count mismatch: expected 4, got {len(roundtrip_old['cores'])}"


@given(old_settings=old_settings_strategy)
@hyp_settings(max_examples=100)
def test_is_old_format_detection(old_settings):
    """Test that old format is correctly detected.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.1, 11.2
    """
    # Old format should be detected
    assert is_old_format(old_settings), \
        f"Failed to detect old format: {old_settings}"
    
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    new_dict = new_config.to_dict()
    
    # New format should NOT be detected as old
    assert not is_old_format(new_dict), \
        f"New format incorrectly detected as old: {new_dict}"


def test_empty_settings_migration():
    """Test migration of empty settings uses defaults.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.4
    """
    # Empty dict
    config = migrate_dynamic_settings({})
    assert config.strategy == "balanced"
    assert config.sample_interval_ms == 100
    assert len(config.cores) == 4
    
    # None
    config = migrate_dynamic_settings(None)
    assert config.strategy == "balanced"


def test_partial_settings_migration():
    """Test migration of partial settings fills in defaults.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.4
    """
    partial = {
        "strategy": "AGGRESSIVE",
        # Missing sample_interval and cores
    }
    
    config = migrate_dynamic_settings(partial)
    
    assert config.strategy == "aggressive"
    assert config.sample_interval_ms == 50  # Default 50000us / 1000
    assert len(config.cores) == 4


def test_strategy_mapping_completeness():
    """Test that all old strategies have mappings.
    
    Feature: dynamic-mode-refactor, Property 12: Settings Migration Round-Trip
    Validates: Requirements 11.2
    """
    old_strategies = ["DEFAULT", "AGGRESSIVE", "MANUAL"]
    
    for old_strat in old_strategies:
        assert old_strat in STRATEGY_MAP_OLD_TO_NEW, \
            f"Missing mapping for old strategy: {old_strat}"
        
        new_strat = STRATEGY_MAP_OLD_TO_NEW[old_strat]
        assert new_strat in STRATEGY_MAP_NEW_TO_OLD, \
            f"Missing reverse mapping for new strategy: {new_strat}"
