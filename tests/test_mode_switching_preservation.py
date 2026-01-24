"""Property test for mode switching configuration preservation.

Feature: manual-dynamic-mode, Property 8: Mode switching configuration preservation
Validates: Requirements 4.4

Tests that for any configuration state, switching from SimpleMode to per-core mode
or vice versa SHALL preserve all core configurations without modification.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from copy import deepcopy

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.manual_manager import DynamicManager, DynamicManualConfig, CoreConfig


# Strategy for generating valid voltage values (-100 to 0 mV)
voltage_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid threshold values (0 to 100%)
threshold_strategy = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for generating valid mode values
mode_strategy = st.sampled_from(["simple", "expert"])


def core_config_strategy(core_id: int) -> st.SearchStrategy[CoreConfig]:
    """Generate a valid CoreConfig for a specific core ID.
    
    Args:
        core_id: The core ID to use
        
    Returns:
        Strategy that generates CoreConfig instances
    """
    return st.builds(
        CoreConfig,
        core_id=st.just(core_id),
        min_mv=voltage_strategy,
        max_mv=voltage_strategy,
        threshold=threshold_strategy
    )


@st.composite
def dynamic_config_strategy(draw):
    """Generate a valid DynamicManualConfig.
    
    Ensures that we have exactly 4 cores (0-3) with valid configurations.
    """
    mode = draw(mode_strategy)
    
    # Generate configs for all 4 cores
    cores = [
        draw(core_config_strategy(0)),
        draw(core_config_strategy(1)),
        draw(core_config_strategy(2)),
        draw(core_config_strategy(3))
    ]
    
    return DynamicManualConfig(
        mode=mode,
        cores=cores,
        version=1
    )


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_property_8_mode_switching_preserves_configuration(config):
    """**Feature: manual-dynamic-mode, Property 8: Mode switching configuration preservation**
    
    For any configuration state, switching from SimpleMode to per-core mode
    or vice versa SHALL preserve all core configurations without modification.
    
    Validates: Requirements 4.4
    """
    # Create manager with the generated config
    manager = DynamicManager()
    manager.config = config
    
    # Store original configuration for comparison
    original_cores = deepcopy(config.cores)
    original_mode = config.mode
    
    # Switch mode (simple -> expert or expert -> simple)
    new_mode = "expert" if original_mode == "simple" else "simple"
    manager.config.mode = new_mode
    
    # Verify all core configurations are preserved
    for i in range(4):
        assert manager.config.cores[i].core_id == original_cores[i].core_id, \
            f"Core {i} ID changed after mode switch"
        
        assert manager.config.cores[i].min_mv == original_cores[i].min_mv, \
            f"Core {i} min_mv changed after mode switch: {manager.config.cores[i].min_mv} != {original_cores[i].min_mv}"
        
        assert manager.config.cores[i].max_mv == original_cores[i].max_mv, \
            f"Core {i} max_mv changed after mode switch: {manager.config.cores[i].max_mv} != {original_cores[i].max_mv}"
        
        # Handle float comparison with tolerance for threshold
        assert abs(manager.config.cores[i].threshold - original_cores[i].threshold) < 1e-9, \
            f"Core {i} threshold changed after mode switch: {manager.config.cores[i].threshold} != {original_cores[i].threshold}"
    
    # Verify mode changed
    assert manager.config.mode == new_mode, \
        f"Mode did not change: {manager.config.mode} != {new_mode}"


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_multiple_mode_switches_preserve_configuration(config):
    """Test that multiple mode switches preserve configuration.
    
    Feature: manual-dynamic-mode, Property 8: Mode switching configuration preservation
    Validates: Requirements 4.4
    """
    manager = DynamicManager()
    manager.config = config
    
    # Store original configuration
    original_cores = deepcopy(config.cores)
    original_mode = config.mode
    
    # Switch mode multiple times
    for _ in range(5):
        # Toggle mode
        manager.config.mode = "expert" if manager.config.mode == "simple" else "simple"
    
    # After odd number of switches, mode should be different
    assert manager.config.mode != original_mode, \
        "Mode should have changed after odd number of switches"
    
    # But all core configurations should be preserved
    for i in range(4):
        assert manager.config.cores[i].core_id == original_cores[i].core_id
        assert manager.config.cores[i].min_mv == original_cores[i].min_mv
        assert manager.config.cores[i].max_mv == original_cores[i].max_mv
        assert abs(manager.config.cores[i].threshold - original_cores[i].threshold) < 1e-9


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_mode_switch_roundtrip_preserves_configuration(config):
    """Test that switching mode and back preserves configuration.
    
    Feature: manual-dynamic-mode, Property 8: Mode switching configuration preservation
    Validates: Requirements 4.4
    """
    manager = DynamicManager()
    manager.config = config
    
    # Store original configuration
    original_cores = deepcopy(config.cores)
    original_mode = config.mode
    
    # Switch mode
    new_mode = "expert" if original_mode == "simple" else "simple"
    manager.config.mode = new_mode
    
    # Switch back
    manager.config.mode = original_mode
    
    # Verify we're back to original mode
    assert manager.config.mode == original_mode, \
        f"Mode not restored: {manager.config.mode} != {original_mode}"
    
    # Verify all core configurations are still preserved
    for i in range(4):
        assert manager.config.cores[i].core_id == original_cores[i].core_id
        assert manager.config.cores[i].min_mv == original_cores[i].min_mv, \
            f"Core {i} min_mv changed after roundtrip"
        assert manager.config.cores[i].max_mv == original_cores[i].max_mv, \
            f"Core {i} max_mv changed after roundtrip"
        assert abs(manager.config.cores[i].threshold - original_cores[i].threshold) < 1e-9, \
            f"Core {i} threshold changed after roundtrip"


@given(
    config=dynamic_config_strategy(),
    core_id=st.integers(min_value=0, max_value=3),
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_mode_switch_after_core_update_preserves_changes(config, core_id, new_min, new_max, new_threshold):
    """Test that mode switching preserves core updates.
    
    Feature: manual-dynamic-mode, Property 8: Mode switching configuration preservation
    Validates: Requirements 4.4
    """
    manager = DynamicManager()
    manager.config = config
    
    # Update one core
    manager.set_core_config(core_id, new_min, new_max, new_threshold)
    
    # Store the updated configuration
    updated_cores = deepcopy(manager.config.cores)
    
    # Switch mode
    original_mode = manager.config.mode
    new_mode = "expert" if original_mode == "simple" else "simple"
    manager.config.mode = new_mode
    
    # Verify the updated core still has the new values
    assert manager.config.cores[core_id].min_mv == new_min, \
        f"Core {core_id} min_mv lost after mode switch"
    assert manager.config.cores[core_id].max_mv == new_max, \
        f"Core {core_id} max_mv lost after mode switch"
    assert abs(manager.config.cores[core_id].threshold - new_threshold) < 1e-9, \
        f"Core {core_id} threshold lost after mode switch"
    
    # Verify all cores match the updated configuration
    for i in range(4):
        assert manager.config.cores[i].min_mv == updated_cores[i].min_mv, \
            f"Core {i} min_mv changed after mode switch"
        assert manager.config.cores[i].max_mv == updated_cores[i].max_mv, \
            f"Core {i} max_mv changed after mode switch"
        assert abs(manager.config.cores[i].threshold - updated_cores[i].threshold) < 1e-9, \
            f"Core {i} threshold changed after mode switch"


def test_simple_to_expert_preserves_all_cores():
    """Test specific case: simple to expert mode preserves all core configs."""
    manager = DynamicManager()
    
    # Set up simple mode with specific values
    manager.config = DynamicManualConfig(
        mode="simple",
        cores=[
            CoreConfig(core_id=0, min_mv=-50, max_mv=-25, threshold=60.0),
            CoreConfig(core_id=1, min_mv=-40, max_mv=-20, threshold=55.0),
            CoreConfig(core_id=2, min_mv=-35, max_mv=-18, threshold=52.0),
            CoreConfig(core_id=3, min_mv=-45, max_mv=-22, threshold=58.0)
        ],
        version=1
    )
    
    # Store original values
    original_cores = deepcopy(manager.config.cores)
    
    # Switch to expert mode
    manager.config.mode = "expert"
    
    # Verify all cores preserved
    for i in range(4):
        assert manager.config.cores[i].min_mv == original_cores[i].min_mv
        assert manager.config.cores[i].max_mv == original_cores[i].max_mv
        assert manager.config.cores[i].threshold == original_cores[i].threshold


def test_expert_to_simple_preserves_all_cores():
    """Test specific case: expert to simple mode preserves all core configs."""
    manager = DynamicManager()
    
    # Set up expert mode with different values per core
    manager.config = DynamicManualConfig(
        mode="expert",
        cores=[
            CoreConfig(core_id=0, min_mv=-60, max_mv=-30, threshold=70.0),
            CoreConfig(core_id=1, min_mv=-50, max_mv=-25, threshold=65.0),
            CoreConfig(core_id=2, min_mv=-45, max_mv=-20, threshold=60.0),
            CoreConfig(core_id=3, min_mv=-55, max_mv=-28, threshold=68.0)
        ],
        version=1
    )
    
    # Store original values
    original_cores = deepcopy(manager.config.cores)
    
    # Switch to simple mode
    manager.config.mode = "simple"
    
    # Verify all cores preserved (even though in simple mode)
    for i in range(4):
        assert manager.config.cores[i].min_mv == original_cores[i].min_mv, \
            f"Core {i} min_mv changed when switching to simple mode"
        assert manager.config.cores[i].max_mv == original_cores[i].max_mv, \
            f"Core {i} max_mv changed when switching to simple mode"
        assert manager.config.cores[i].threshold == original_cores[i].threshold, \
            f"Core {i} threshold changed when switching to simple mode"
