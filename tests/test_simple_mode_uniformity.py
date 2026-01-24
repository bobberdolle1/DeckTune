"""Property test for Simple Mode configuration uniformity.

Feature: manual-dynamic-mode, Property 7: Simple mode configuration uniformity
Validates: Requirements 4.3

Tests that for any Apply operation in SimpleMode, all core configurations
transmitted to gymdeck3 SHALL be identical.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import Mock, AsyncMock
import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.manual_manager import DynamicManager, DynamicManualConfig, CoreConfig
from backend.dynamic.rpc import DynamicModeRPC
from backend.dynamic.manual_validator import Validator


# Strategy for generating valid voltage values (-100 to 0 mV)
voltage_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid threshold values (0 to 100%)
threshold_strategy = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)


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
def simple_mode_config_strategy(draw):
    """Generate a valid DynamicManualConfig in Simple Mode.
    
    Ensures that we have exactly 4 cores (0-3) with potentially different
    initial configurations (to test uniformity after apply).
    """
    # Generate configs for all 4 cores (can have different values initially)
    cores = [
        draw(core_config_strategy(0)),
        draw(core_config_strategy(1)),
        draw(core_config_strategy(2)),
        draw(core_config_strategy(3))
    ]
    
    return DynamicManualConfig(
        mode="simple",
        cores=cores,
        version=1
    )


@given(
    config=simple_mode_config_strategy(),
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_property_7_simple_mode_configuration_uniformity(config, new_min, new_max, new_threshold):
    """**Feature: manual-dynamic-mode, Property 7: Simple mode configuration uniformity**
    
    For any Apply operation in SimpleMode, all core configurations
    transmitted to gymdeck3 SHALL be identical.
    
    This test verifies that when configuration is applied in Simple Mode,
    all cores receive identical settings.
    
    Validates: Requirements 4.3
    """
    # Skip if min > max (invalid configuration)
    if new_min > new_max:
        return
    
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Apply configuration to all cores (simulating Apply button in Simple Mode)
    manager.set_all_cores_config(
        min_mv=new_min,
        max_mv=new_max,
        threshold=new_threshold
    )
    
    # Verify all cores have identical configuration
    reference_config = manager.config.cores[0]
    
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == reference_config.min_mv, \
            f"Core {i} min_mv ({manager.config.cores[i].min_mv}) != Core 0 min_mv ({reference_config.min_mv})"
        
        assert manager.config.cores[i].max_mv == reference_config.max_mv, \
            f"Core {i} max_mv ({manager.config.cores[i].max_mv}) != Core 0 max_mv ({reference_config.max_mv})"
        
        assert abs(manager.config.cores[i].threshold - reference_config.threshold) < 1e-9, \
            f"Core {i} threshold ({manager.config.cores[i].threshold}) != Core 0 threshold ({reference_config.threshold})"
    
    # Verify all cores have the exact values that were set
    for i in range(4):
        assert manager.config.cores[i].min_mv == new_min, \
            f"Core {i} min_mv should be {new_min}"
        assert manager.config.cores[i].max_mv == new_max, \
            f"Core {i} max_mv should be {new_max}"
        assert abs(manager.config.cores[i].threshold - new_threshold) < 1e-9, \
            f"Core {i} threshold should be {new_threshold}"


@given(
    config=simple_mode_config_strategy(),
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_property_7_rpc_apply_uniformity(config, new_min, new_max, new_threshold):
    """**Feature: manual-dynamic-mode, Property 7: Simple mode configuration uniformity**
    
    For any Apply operation in SimpleMode via RPC, all core configurations
    SHALL be identical.
    
    This test verifies the RPC layer ensures uniformity when applying
    configuration in Simple Mode.
    
    Validates: Requirements 4.3
    """
    # Skip if min > max (invalid configuration)
    if new_min > new_max:
        return
    
    # Create manager and RPC handler
    manager = DynamicManager()
    validator = Validator()
    settings_mock = Mock()
    settings_mock.save_setting = Mock(return_value=True)
    
    rpc = DynamicModeRPC(manager, validator, settings_mock)
    
    # Set up simple mode
    manager.config = config
    manager.config.mode = "simple"
    
    # Apply configuration via RPC (simulating frontend Apply in Simple Mode)
    result = asyncio.run(rpc.set_all_cores_config(
        min_mv=new_min,
        max_mv=new_max,
        threshold=new_threshold
    ))
    
    # Verify RPC call succeeded
    assert result["success"], f"RPC call failed: {result.get('error', 'Unknown error')}"
    
    # Verify all cores have identical configuration
    reference_config = manager.config.cores[0]
    
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == reference_config.min_mv, \
            f"Core {i} min_mv != Core 0 min_mv after RPC apply"
        
        assert manager.config.cores[i].max_mv == reference_config.max_mv, \
            f"Core {i} max_mv != Core 0 max_mv after RPC apply"
        
        assert abs(manager.config.cores[i].threshold - reference_config.threshold) < 1e-9, \
            f"Core {i} threshold != Core 0 threshold after RPC apply"


@given(config=simple_mode_config_strategy())
@hyp_settings(max_examples=100)
def test_property_7_start_dynamic_mode_uniformity(config):
    """**Feature: manual-dynamic-mode, Property 7: Simple mode configuration uniformity**
    
    For any start_dynamic_mode operation in SimpleMode, all core configurations
    transmitted SHALL be identical.
    
    Validates: Requirements 4.3
    """
    # First ensure all cores have the same config (as they should in Simple Mode)
    manager = DynamicManager()
    manager.config = config
    manager.config.mode = "simple"
    
    # Apply uniform configuration
    reference = config.cores[0]
    manager.set_all_cores_config(
        min_mv=reference.min_mv,
        max_mv=reference.max_mv,
        threshold=reference.threshold
    )
    
    # Verify uniformity before starting
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == reference.min_mv
        assert manager.config.cores[i].max_mv == reference.max_mv
        assert abs(manager.config.cores[i].threshold - reference.threshold) < 1e-9
    
    # Start dynamic mode (this would transmit config to gymdeck3)
    success = manager.start()
    assert success, "Failed to start dynamic mode"
    
    # Verify configuration remains uniform after start
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == reference.min_mv, \
            f"Core {i} config changed after start"
        assert manager.config.cores[i].max_mv == reference.max_mv, \
            f"Core {i} config changed after start"
        assert abs(manager.config.cores[i].threshold - reference.threshold) < 1e-9, \
            f"Core {i} config changed after start"


def test_simple_mode_uniformity_specific_case():
    """Test specific case: Simple Mode ensures uniform configuration."""
    manager = DynamicManager()
    
    # Set up simple mode with different initial values per core
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
    
    # Apply uniform configuration
    manager.set_all_cores_config(min_mv=-60, max_mv=-30, threshold=70.0)
    
    # Verify all cores have identical configuration
    for i in range(4):
        assert manager.config.cores[i].min_mv == -60
        assert manager.config.cores[i].max_mv == -30
        assert manager.config.cores[i].threshold == 70.0
    
    # Verify all cores match each other
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == manager.config.cores[0].min_mv
        assert manager.config.cores[i].max_mv == manager.config.cores[0].max_mv
        assert manager.config.cores[i].threshold == manager.config.cores[0].threshold


def test_simple_mode_uniformity_after_multiple_applies():
    """Test that uniformity is maintained after multiple Apply operations."""
    manager = DynamicManager()
    
    # Set up simple mode
    manager.config = DynamicManualConfig(
        mode="simple",
        cores=[
            CoreConfig(core_id=0, min_mv=-30, max_mv=-15, threshold=50.0),
            CoreConfig(core_id=1, min_mv=-30, max_mv=-15, threshold=50.0),
            CoreConfig(core_id=2, min_mv=-30, max_mv=-15, threshold=50.0),
            CoreConfig(core_id=3, min_mv=-30, max_mv=-15, threshold=50.0)
        ],
        version=1
    )
    
    # Apply multiple different configurations
    configs_to_apply = [
        (-40, -20, 55.0),
        (-50, -25, 60.0),
        (-35, -18, 52.0),
        (-45, -22, 58.0)
    ]
    
    for min_mv, max_mv, threshold in configs_to_apply:
        manager.set_all_cores_config(min_mv=min_mv, max_mv=max_mv, threshold=threshold)
        
        # After each apply, verify uniformity
        for i in range(1, 4):
            assert manager.config.cores[i].min_mv == manager.config.cores[0].min_mv, \
                f"Uniformity broken after apply: Core {i} min_mv != Core 0"
            assert manager.config.cores[i].max_mv == manager.config.cores[0].max_mv, \
                f"Uniformity broken after apply: Core {i} max_mv != Core 0"
            assert manager.config.cores[i].threshold == manager.config.cores[0].threshold, \
                f"Uniformity broken after apply: Core {i} threshold != Core 0"
        
        # Verify all cores have the expected values
        for i in range(4):
            assert manager.config.cores[i].min_mv == min_mv
            assert manager.config.cores[i].max_mv == max_mv
            assert manager.config.cores[i].threshold == threshold
