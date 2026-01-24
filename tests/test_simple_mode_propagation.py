"""Property test for Simple Mode value propagation.

Feature: manual-dynamic-mode, Property 6: Simple mode value propagation
Validates: Requirements 4.2

Tests that for any control adjustment in SimpleMode, all cores SHALL have
identical values for the adjusted parameter.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.manual_manager import DynamicManager, DynamicManualConfig, CoreConfig


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
    initial configurations (to test propagation).
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
    new_min=voltage_strategy
)
@hyp_settings(max_examples=100)
def test_property_6_simple_mode_min_mv_propagation(config, new_min):
    """**Feature: manual-dynamic-mode, Property 6: Simple mode value propagation**
    
    For any control adjustment in SimpleMode, all cores SHALL have
    identical values for the adjusted parameter.
    
    This test verifies that when min_mv is updated in Simple Mode,
    all cores receive the same value.
    
    Validates: Requirements 4.2
    """
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Update all cores with new min_mv value
    manager.set_all_cores_config(
        min_mv=new_min,
        max_mv=manager.config.cores[0].max_mv,
        threshold=manager.config.cores[0].threshold
    )
    
    # Verify all cores have identical min_mv
    for i in range(4):
        assert manager.config.cores[i].min_mv == new_min, \
            f"Core {i} min_mv ({manager.config.cores[i].min_mv}) != {new_min}"
    
    # Verify all cores have the same min_mv as each other
    first_core_min = manager.config.cores[0].min_mv
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == first_core_min, \
            f"Core {i} min_mv ({manager.config.cores[i].min_mv}) != Core 0 min_mv ({first_core_min})"


@given(
    config=simple_mode_config_strategy(),
    new_max=voltage_strategy
)
@hyp_settings(max_examples=100)
def test_property_6_simple_mode_max_mv_propagation(config, new_max):
    """**Feature: manual-dynamic-mode, Property 6: Simple mode value propagation**
    
    For any control adjustment in SimpleMode, all cores SHALL have
    identical values for the adjusted parameter.
    
    This test verifies that when max_mv is updated in Simple Mode,
    all cores receive the same value.
    
    Validates: Requirements 4.2
    """
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Update all cores with new max_mv value
    manager.set_all_cores_config(
        min_mv=manager.config.cores[0].min_mv,
        max_mv=new_max,
        threshold=manager.config.cores[0].threshold
    )
    
    # Verify all cores have identical max_mv
    for i in range(4):
        assert manager.config.cores[i].max_mv == new_max, \
            f"Core {i} max_mv ({manager.config.cores[i].max_mv}) != {new_max}"
    
    # Verify all cores have the same max_mv as each other
    first_core_max = manager.config.cores[0].max_mv
    for i in range(1, 4):
        assert manager.config.cores[i].max_mv == first_core_max, \
            f"Core {i} max_mv ({manager.config.cores[i].max_mv}) != Core 0 max_mv ({first_core_max})"


@given(
    config=simple_mode_config_strategy(),
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_property_6_simple_mode_threshold_propagation(config, new_threshold):
    """**Feature: manual-dynamic-mode, Property 6: Simple mode value propagation**
    
    For any control adjustment in SimpleMode, all cores SHALL have
    identical values for the adjusted parameter.
    
    This test verifies that when threshold is updated in Simple Mode,
    all cores receive the same value.
    
    Validates: Requirements 4.2
    """
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Update all cores with new threshold value
    manager.set_all_cores_config(
        min_mv=manager.config.cores[0].min_mv,
        max_mv=manager.config.cores[0].max_mv,
        threshold=new_threshold
    )
    
    # Verify all cores have identical threshold
    for i in range(4):
        assert abs(manager.config.cores[i].threshold - new_threshold) < 1e-9, \
            f"Core {i} threshold ({manager.config.cores[i].threshold}) != {new_threshold}"
    
    # Verify all cores have the same threshold as each other
    first_core_threshold = manager.config.cores[0].threshold
    for i in range(1, 4):
        assert abs(manager.config.cores[i].threshold - first_core_threshold) < 1e-9, \
            f"Core {i} threshold ({manager.config.cores[i].threshold}) != Core 0 threshold ({first_core_threshold})"


@given(
    config=simple_mode_config_strategy(),
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_property_6_simple_mode_all_parameters_propagation(config, new_min, new_max, new_threshold):
    """**Feature: manual-dynamic-mode, Property 6: Simple mode value propagation**
    
    For any control adjustment in SimpleMode, all cores SHALL have
    identical values for the adjusted parameter.
    
    This test verifies that when all parameters are updated in Simple Mode,
    all cores receive identical values.
    
    Validates: Requirements 4.2
    """
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Update all cores with new values
    manager.set_all_cores_config(
        min_mv=new_min,
        max_mv=new_max,
        threshold=new_threshold
    )
    
    # Verify all cores have identical configuration
    for i in range(4):
        assert manager.config.cores[i].min_mv == new_min, \
            f"Core {i} min_mv ({manager.config.cores[i].min_mv}) != {new_min}"
        assert manager.config.cores[i].max_mv == new_max, \
            f"Core {i} max_mv ({manager.config.cores[i].max_mv}) != {new_max}"
        assert abs(manager.config.cores[i].threshold - new_threshold) < 1e-9, \
            f"Core {i} threshold ({manager.config.cores[i].threshold}) != {new_threshold}"
    
    # Verify all cores match Core 0
    for i in range(1, 4):
        assert manager.config.cores[i].min_mv == manager.config.cores[0].min_mv, \
            f"Core {i} min_mv != Core 0 min_mv"
        assert manager.config.cores[i].max_mv == manager.config.cores[0].max_mv, \
            f"Core {i} max_mv != Core 0 max_mv"
        assert abs(manager.config.cores[i].threshold - manager.config.cores[0].threshold) < 1e-9, \
            f"Core {i} threshold != Core 0 threshold"


@given(
    config=simple_mode_config_strategy(),
    updates=st.lists(
        st.tuples(voltage_strategy, voltage_strategy, threshold_strategy),
        min_size=1,
        max_size=10
    )
)
@hyp_settings(max_examples=100)
def test_property_6_simple_mode_multiple_updates_propagation(config, updates):
    """**Feature: manual-dynamic-mode, Property 6: Simple mode value propagation**
    
    For any sequence of control adjustments in SimpleMode, all cores SHALL
    maintain identical values after each update.
    
    Validates: Requirements 4.2
    """
    manager = DynamicManager()
    manager.config = config
    
    # Ensure we're in simple mode
    assert manager.config.mode == "simple"
    
    # Apply multiple updates
    for new_min, new_max, new_threshold in updates:
        manager.set_all_cores_config(
            min_mv=new_min,
            max_mv=new_max,
            threshold=new_threshold
        )
        
        # After each update, verify all cores are identical
        for i in range(1, 4):
            assert manager.config.cores[i].min_mv == manager.config.cores[0].min_mv, \
                f"After update, Core {i} min_mv != Core 0 min_mv"
            assert manager.config.cores[i].max_mv == manager.config.cores[0].max_mv, \
                f"After update, Core {i} max_mv != Core 0 max_mv"
            assert abs(manager.config.cores[i].threshold - manager.config.cores[0].threshold) < 1e-9, \
                f"After update, Core {i} threshold != Core 0 threshold"


def test_simple_mode_propagation_specific_case():
    """Test specific case: Simple Mode propagates values to all cores."""
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
    
    # Update all cores with new values
    manager.set_all_cores_config(min_mv=-60, max_mv=-30, threshold=70.0)
    
    # Verify all cores now have identical values
    for i in range(4):
        assert manager.config.cores[i].min_mv == -60, \
            f"Core {i} min_mv should be -60"
        assert manager.config.cores[i].max_mv == -30, \
            f"Core {i} max_mv should be -30"
        assert manager.config.cores[i].threshold == 70.0, \
            f"Core {i} threshold should be 70.0"
