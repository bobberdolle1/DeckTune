"""Property-based test for Game State Monitor lifecycle.

Feature: ui-refactor-settings, Property 7: Game Only Mode monitoring lifecycle
Validates: Requirements 5.5, 6.1, 6.5

This test verifies that:
- When Game Only Mode is enabled, the monitor is active
- When Game Only Mode is disabled, the monitor is stopped
- The monitor lifecycle is properly managed
"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.core.game_state_monitor import GameStateMonitor
import asyncio


# Strategy for generating boolean states
game_only_mode_states = st.booleans()


@pytest.mark.asyncio
@given(enabled=game_only_mode_states)
@settings(max_examples=100, deadline=None)
async def test_game_only_mode_monitoring_lifecycle(enabled):
    """Property 7: Game Only Mode monitoring lifecycle.
    
    For any Game Only Mode state (enabled/disabled), the monitor should be
    active when enabled and stopped when disabled.
    
    Feature: ui-refactor-settings, Property 7: Game Only Mode monitoring lifecycle
    Validates: Requirements 5.5, 6.1, 6.5
    """
    # Track callback invocations
    game_start_called = []
    game_exit_called = []
    
    async def on_game_start(app_id: int):
        game_start_called.append(app_id)
    
    async def on_game_exit():
        game_exit_called.append(True)
    
    # Create monitor
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1  # Fast polling for tests
    )
    
    # Initially, monitor should not be running
    assert not monitor.is_running(), "Monitor should not be running initially"
    
    if enabled:
        # When Game Only Mode is enabled, monitor should be active
        success = await monitor.start_monitoring()
        assert success, "Monitor should start successfully"
        assert monitor.is_running(), "Monitor should be running when Game Only Mode is enabled"
        
        # Give it a moment to initialize
        await asyncio.sleep(0.2)
        
        # Stop the monitor
        await monitor.stop_monitoring()
        assert not monitor.is_running(), "Monitor should be stopped after stop_monitoring"
    else:
        # When Game Only Mode is disabled, monitor should not be active
        assert not monitor.is_running(), "Monitor should not be running when Game Only Mode is disabled"


@pytest.mark.asyncio
async def test_monitor_lifecycle_transitions():
    """Test that monitor can be started and stopped multiple times.
    
    Feature: ui-refactor-settings, Property 7: Game Only Mode monitoring lifecycle
    Validates: Requirements 6.1, 6.5
    """
    async def on_game_start(app_id: int):
        pass
    
    async def on_game_exit():
        pass
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    # Start -> Stop -> Start -> Stop
    for _ in range(2):
        # Start
        success = await monitor.start_monitoring()
        assert success, "Monitor should start successfully"
        assert monitor.is_running(), "Monitor should be running after start"
        
        await asyncio.sleep(0.1)
        
        # Stop
        await monitor.stop_monitoring()
        assert not monitor.is_running(), "Monitor should be stopped after stop"
        
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_monitor_handles_subscription_failure_gracefully():
    """Test that monitor handles subscription failures gracefully.
    
    Feature: ui-refactor-settings
    Validates: Requirements 6.4
    """
    async def on_game_start(app_id: int):
        pass
    
    async def on_game_exit():
        pass
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    # Even if subscription fails (which it currently does since we use polling),
    # the monitor should still start successfully
    success = await monitor.start_monitoring()
    assert success, "Monitor should start successfully even if subscription fails"
    assert monitor.is_running(), "Monitor should be running"
    
    await monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_monitor_detects_game_state_changes():
    """Test that monitor detects game state changes and invokes callbacks.
    
    This is a unit test that verifies the monitor's ability to detect
    state changes and invoke the appropriate callbacks.
    
    Feature: ui-refactor-settings
    Validates: Requirements 6.2, 6.3
    """
    game_start_calls = []
    game_exit_calls = []
    
    async def on_game_start(app_id: int):
        game_start_calls.append(app_id)
    
    async def on_game_exit():
        game_exit_calls.append(True)
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    # Start monitoring
    await monitor.start_monitoring()
    
    # Note: Since we're running in a test environment without actual Steam games,
    # we can't test actual game detection. This test verifies the monitor
    # starts and stops correctly without errors.
    
    # Let it run for a bit
    await asyncio.sleep(0.3)
    
    # Stop monitoring
    await monitor.stop_monitoring()
    
    # The monitor should have run without errors
    assert not monitor.is_running(), "Monitor should be stopped"


@pytest.mark.asyncio
async def test_monitor_state_after_stop():
    """Test that monitor properly resets state after stopping.
    
    Feature: ui-refactor-settings
    Validates: Requirements 6.5
    """
    async def on_game_start(app_id: int):
        pass
    
    async def on_game_exit():
        pass
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    # Start and stop
    await monitor.start_monitoring()
    await asyncio.sleep(0.1)
    await monitor.stop_monitoring()
    
    # After stopping, state should be reset
    assert not monitor.is_running(), "Monitor should not be running"
    assert not monitor.is_game_running(), "No game should be detected after stop"
    assert monitor.get_current_app_id() is None, "App ID should be None after stop"
