"""Property-based tests for status indicator state consistency.

Feature: manual-dynamic-mode, Property 9: Status indicator state consistency
Validates: Requirements 5.2, 5.4

This test verifies that the status indicator correctly reflects the active/inactive
state of dynamic mode based on RPC responses.
"""

import pytest
from hypothesis import given, strategies as st, settings
import asyncio

from backend.dynamic.manual_manager import DynamicManager
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


# Strategy for generating valid configurations
@st.composite
def valid_dynamic_config(draw):
    """Generate a valid dynamic configuration."""
    mode = draw(st.sampled_from(['simple', 'expert']))
    
    cores = []
    for core_id in range(4):
        min_mv = draw(st.integers(min_value=-100, max_value=0))
        max_mv = draw(st.integers(min_value=min_mv, max_value=0))
        threshold = draw(st.floats(min_value=0.0, max_value=100.0))
        
        cores.append({
            "core_id": core_id,
            "min_mv": min_mv,
            "max_mv": max_mv,
            "threshold": threshold
        })
    
    return {
        "mode": mode,
        "cores": cores,
        "version": 1
    }


@given(config=valid_dynamic_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_status_indicator_active_after_start(config):
    """
    **Feature: manual-dynamic-mode, Property 9: Status indicator state consistency**
    **Validates: Requirements 5.2**
    
    For any successful start_dynamic_mode RPC response, the status indicator
    SHALL display "Active".
    
    This test verifies that when start_dynamic_mode returns success=True,
    the system state reflects that dynamic mode is active.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Start dynamic mode with the configuration
    start_result = await rpc_handler.start_dynamic_mode(config=config)
    
    # Verify start operation succeeded
    assert start_result["success"], f"Start operation failed: {start_result.get('error')}"
    
    # Verify the manager's state reflects active status
    # The RPC handler's manager should now be in active state
    assert rpc_handler.manager.is_active, \
        "Manager should be active after successful start_dynamic_mode"
    
    # Verify we can query the status and it returns active
    # (In a real frontend, this would be reflected in the UI status indicator)
    status = rpc_handler.manager.get_status()
    assert status["active"], \
        "Status should indicate active after successful start_dynamic_mode"


@given(config=valid_dynamic_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_status_indicator_inactive_after_stop(config):
    """
    **Feature: manual-dynamic-mode, Property 9: Status indicator state consistency**
    **Validates: Requirements 5.4**
    
    For any successful stop_dynamic_mode RPC response, the status indicator
    SHALL display "Inactive".
    
    This test verifies that when stop_dynamic_mode returns success=True,
    the system state reflects that dynamic mode is inactive.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # First start dynamic mode
    start_result = await rpc_handler.start_dynamic_mode(config=config)
    assert start_result["success"], "Start operation should succeed"
    assert rpc_handler.manager.is_active, "Manager should be active after start"
    
    # Now stop dynamic mode
    stop_result = await rpc_handler.stop_dynamic_mode()
    
    # Verify stop operation succeeded
    assert stop_result["success"], f"Stop operation failed: {stop_result.get('error')}"
    
    # Verify the manager's state reflects inactive status
    assert not rpc_handler.manager.is_active, \
        "Manager should be inactive after successful stop_dynamic_mode"
    
    # Verify we can query the status and it returns inactive
    status = rpc_handler.manager.get_status()
    assert not status["active"], \
        "Status should indicate inactive after successful stop_dynamic_mode"


@given(config=valid_dynamic_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_status_indicator_start_stop_cycle(config):
    """
    **Feature: manual-dynamic-mode, Property 9: Status indicator state consistency**
    **Validates: Requirements 5.2, 5.4**
    
    For any sequence of start/stop operations, the status indicator SHALL
    correctly reflect the current state after each operation.
    
    This test verifies that the status indicator remains consistent through
    multiple start/stop cycles.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Initial state should be inactive
    assert not rpc_handler.manager.is_active, "Initial state should be inactive"
    
    # Cycle through start/stop multiple times
    for cycle in range(3):
        # Start
        start_result = await rpc_handler.start_dynamic_mode(config=config)
        assert start_result["success"], f"Start operation failed in cycle {cycle}"
        assert rpc_handler.manager.is_active, \
            f"Manager should be active after start in cycle {cycle}"
        
        status = rpc_handler.manager.get_status()
        assert status["active"], \
            f"Status should indicate active after start in cycle {cycle}"
        
        # Stop
        stop_result = await rpc_handler.stop_dynamic_mode()
        assert stop_result["success"], f"Stop operation failed in cycle {cycle}"
        assert not rpc_handler.manager.is_active, \
            f"Manager should be inactive after stop in cycle {cycle}"
        
        status = rpc_handler.manager.get_status()
        assert not status["active"], \
            f"Status should indicate inactive after stop in cycle {cycle}"


@pytest.mark.asyncio
async def test_status_indicator_initial_state():
    """
    **Feature: manual-dynamic-mode, Property 9: Status indicator state consistency**
    **Validates: Requirements 5.2, 5.4**
    
    For any newly initialized system, the status indicator SHALL display "Inactive"
    before any start operation.
    
    This test verifies the initial state is always inactive.
    """
    # Create fresh RPC handler
    rpc_handler = create_rpc_handler()
    
    # Verify initial state is inactive
    assert not rpc_handler.manager.is_active, \
        "Initial state should be inactive"
    
    status = rpc_handler.manager.get_status()
    assert not status["active"], \
        "Initial status should indicate inactive"


@given(config=valid_dynamic_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_status_indicator_persists_across_config_changes(config):
    """
    **Feature: manual-dynamic-mode, Property 9: Status indicator state consistency**
    **Validates: Requirements 5.2, 5.4**
    
    For any active dynamic mode, changing configuration SHALL NOT affect the
    active status until stop is called.
    
    This test verifies that the status indicator remains active even when
    configuration is updated while dynamic mode is running.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Start dynamic mode
    start_result = await rpc_handler.start_dynamic_mode(config=config)
    assert start_result["success"], "Start operation should succeed"
    assert rpc_handler.manager.is_active, "Manager should be active after start"
    
    # Update configuration for a core
    update_result = await rpc_handler.set_dynamic_core_config(
        core_id=0,
        min_mv=-50,
        max_mv=-25,
        threshold=60.0
    )
    assert update_result["success"], "Config update should succeed"
    
    # Verify status is still active after config change
    assert rpc_handler.manager.is_active, \
        "Manager should remain active after configuration update"
    
    status = rpc_handler.manager.get_status()
    assert status["active"], \
        "Status should remain active after configuration update"
    
    # Stop should still work
    stop_result = await rpc_handler.stop_dynamic_mode()
    assert stop_result["success"], "Stop operation should succeed"
    assert not rpc_handler.manager.is_active, \
        "Manager should be inactive after stop"
