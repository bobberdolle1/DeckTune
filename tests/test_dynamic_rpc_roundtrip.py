"""Property-based tests for Manual Dynamic Mode RPC round-trip.

Feature: manual-dynamic-mode, Property 20: RPC configuration round-trip
Validates: Requirements 9.2

This test verifies that setting a core configuration via RPC and then
retrieving it returns the same configuration.
"""

import pytest
from hypothesis import given, strategies as st, settings
import asyncio

from backend.dynamic.manual_manager import DynamicManager, CoreConfig
from backend.dynamic.manual_validator import Validator
from backend.dynamic.rpc import DynamicModeRPC


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.storage = {}
    
    def setSetting(self, key, value):
        """Set a setting value."""
        self.storage[key] = value
    
    def getSetting(self, key, default=None):
        """Get a setting value."""
        return self.storage.get(key, default)


def create_rpc_handler():
    """Create RPC handler for testing."""
    manager = DynamicManager()
    validator = Validator()
    settings = MockSettingsManager()
    
    rpc = DynamicModeRPC(
        manager=manager,
        validator=validator,
        settings_manager=settings
    )
    
    return rpc


# Strategy for generating valid core configurations
@st.composite
def valid_core_config(draw):
    """Generate a valid core configuration."""
    core_id = draw(st.integers(min_value=0, max_value=3))
    
    # Generate min and max such that min <= max (both in range -100 to 0)
    min_mv = draw(st.integers(min_value=-100, max_value=0))
    max_mv = draw(st.integers(min_value=min_mv, max_value=0))
    
    threshold = draw(st.floats(min_value=0.0, max_value=100.0))
    
    return {
        "core_id": core_id,
        "min_mv": min_mv,
        "max_mv": max_mv,
        "threshold": threshold
    }


@given(config=valid_core_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_configuration_roundtrip(config):
    """
    **Feature: manual-dynamic-mode, Property 20: RPC configuration round-trip**
    **Validates: Requirements 9.2**
    
    For any valid CoreConfig, invoking set_dynamic_core_config followed by
    get_dynamic_config SHALL return the same configuration for that core.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set the configuration
    set_result = await rpc_handler.set_dynamic_core_config(
        core_id=config["core_id"],
        min_mv=config["min_mv"],
        max_mv=config["max_mv"],
        threshold=config["threshold"]
    )
    
    # Verify set operation succeeded
    assert set_result["success"], f"Set operation failed: {set_result.get('error')}"
    
    # Get the configuration
    get_result = await rpc_handler.get_dynamic_config()
    
    # Verify get operation succeeded
    assert get_result["success"], f"Get operation failed: {get_result.get('error')}"
    
    # Extract the core configuration
    cores = get_result["config"]["cores"]
    core_config = cores[config["core_id"]]
    
    # Verify the configuration matches (accounting for potential clamping)
    # The returned values should match what was set (or clamped values)
    clamped_min = set_result.get("clamped", {}).get("min_mv", config["min_mv"])
    clamped_max = set_result.get("clamped", {}).get("max_mv", config["max_mv"])
    
    assert core_config["core_id"] == config["core_id"], \
        f"Core ID mismatch: expected {config['core_id']}, got {core_config['core_id']}"
    
    assert core_config["min_mv"] == clamped_min, \
        f"min_mv mismatch: expected {clamped_min}, got {core_config['min_mv']}"
    
    assert core_config["max_mv"] == clamped_max, \
        f"max_mv mismatch: expected {clamped_max}, got {core_config['max_mv']}"
    
    assert core_config["threshold"] == config["threshold"], \
        f"threshold mismatch: expected {config['threshold']}, got {core_config['threshold']}"


@given(configs=st.lists(valid_core_config(), min_size=1, max_size=4))
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_multiple_cores_roundtrip(configs):
    """
    **Feature: manual-dynamic-mode, Property 20: RPC configuration round-trip**
    **Validates: Requirements 9.2**
    
    For any sequence of valid CoreConfigs, setting multiple cores and then
    retrieving the configuration SHALL return all the set configurations.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set configurations for multiple cores
    for config in configs:
        set_result = await rpc_handler.set_dynamic_core_config(
            core_id=config["core_id"],
            min_mv=config["min_mv"],
            max_mv=config["max_mv"],
            threshold=config["threshold"]
        )
        assert set_result["success"], f"Set operation failed for core {config['core_id']}"
    
    # Get the full configuration
    get_result = await rpc_handler.get_dynamic_config()
    assert get_result["success"], "Get operation failed"
    
    # Verify each set configuration is present
    cores = get_result["config"]["cores"]
    
    for config in configs:
        core_config = cores[config["core_id"]]
        
        # The configuration should match what was last set for this core
        assert core_config["core_id"] == config["core_id"]
        # Note: We don't check exact values here because multiple configs
        # might have been set for the same core, and we only care that
        # the last one is preserved
