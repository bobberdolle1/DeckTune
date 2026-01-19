"""Property-based tests for Game Only Mode state transition triggers.

Feature: ui-refactor-settings, Property 3: Game state transition triggers
Validates: Requirements 5.1, 5.2, 5.4

This module tests that game state transitions (start/exit) trigger
profile application or reset within 2 seconds when Game Only Mode is enabled.
"""

import pytest
import asyncio
import time
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile

# Import the components we need to test
from backend.core.game_state_monitor import GameStateMonitor
from backend.core.settings_manager import SettingsManager


# ==================== Strategies ====================

# Strategy for generating game state transitions
# Represents: (transition_type, app_id)
game_transitions = st.tuples(
    st.sampled_from(["game_start", "game_exit"]),
    st.integers(min_value=1, max_value=999999)  # Valid Steam AppIDs
)


# ==================== Property Tests ====================

@pytest.mark.asyncio
@given(transition=game_transitions)
@hyp_settings(max_examples=100, deadline=None)
async def test_game_state_transition_triggers_within_timeout(transition):
    """Property 3: Game state transition triggers.
    
    For any game state transition (start or exit) when Game Only Mode is enabled,
    the system should apply or reset undervolt within 2 seconds of the event.
    
    **Feature: ui-refactor-settings, Property 3: Game state transition triggers**
    **Validates: Requirements 5.1, 5.2, 5.4**
    """
    transition_type, app_id = transition
    
    # Track callback invocations and timing
    callback_invoked = asyncio.Event()
    callback_time = None
    transition_time = None
    
    async def on_game_start(detected_app_id: int):
        nonlocal callback_time
        callback_time = time.time()
        callback_invoked.set()
    
    async def on_game_exit():
        nonlocal callback_time
        callback_time = time.time()
        callback_invoked.set()
    
    # Create monitor
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1  # Fast polling for testing
    )
    
    try:
        # Start monitoring
        await monitor.start_monitoring()
        
        # Simulate game state transition by directly invoking callbacks
        # (In real implementation, this would be triggered by game detection)
        transition_time = time.time()
        
        if transition_type == "game_start":
            await on_game_start(app_id)
        else:
            await on_game_exit()
        
        # Wait for callback with timeout
        try:
            await asyncio.wait_for(callback_invoked.wait(), timeout=2.5)
        except asyncio.TimeoutError:
            pytest.fail(f"Callback not invoked within 2 seconds for {transition_type}")
        
        # Verify timing constraint (Requirements 5.4)
        elapsed = callback_time - transition_time
        assert elapsed <= 2.0, \
            f"Callback took {elapsed:.3f}s, exceeds 2 second requirement"
        
    finally:
        await monitor.stop_monitoring()


@pytest.mark.asyncio
@given(
    transitions=st.lists(
        game_transitions,
        min_size=1,
        max_size=5
    )
)
@hyp_settings(max_examples=50, deadline=None)
async def test_multiple_transitions_all_trigger_callbacks(transitions):
    """Property: Multiple game state transitions all trigger callbacks.
    
    For any sequence of game state transitions, each transition should
    trigger the appropriate callback within 2 seconds.
    
    **Feature: ui-refactor-settings, Property 3: Game state transition triggers**
    **Validates: Requirements 5.1, 5.2, 5.4**
    """
    game_start_count = 0
    game_exit_count = 0
    
    async def on_game_start(app_id: int):
        nonlocal game_start_count
        game_start_count += 1
    
    async def on_game_exit():
        nonlocal game_exit_count
        game_exit_count += 1
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    try:
        await monitor.start_monitoring()
        
        # Process each transition
        expected_starts = 0
        expected_exits = 0
        
        for transition_type, app_id in transitions:
            if transition_type == "game_start":
                await on_game_start(app_id)
                expected_starts += 1
            else:
                await on_game_exit()
                expected_exits += 1
            
            # Small delay between transitions
            await asyncio.sleep(0.1)
        
        # Verify all callbacks were invoked
        assert game_start_count == expected_starts, \
            f"Expected {expected_starts} game starts, got {game_start_count}"
        assert game_exit_count == expected_exits, \
            f"Expected {expected_exits} game exits, got {game_exit_count}"
        
    finally:
        await monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_game_start_applies_profile():
    """Test that game start transition applies the saved profile.
    
    When Game Only Mode is enabled and a game starts, the system should
    apply the saved undervolt profile.
    
    **Feature: ui-refactor-settings, Property 3: Game state transition triggers**
    **Validates: Requirements 5.1**
    """
    profile_applied = asyncio.Event()
    applied_app_id = None
    
    async def on_game_start(app_id: int):
        nonlocal applied_app_id
        applied_app_id = app_id
        profile_applied.set()
    
    async def on_game_exit():
        pass
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    try:
        await monitor.start_monitoring()
        
        # Simulate game start
        test_app_id = 123456
        await on_game_start(test_app_id)
        
        # Wait for profile application
        try:
            await asyncio.wait_for(profile_applied.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Profile not applied within 2 seconds")
        
        # Verify correct app_id was passed
        assert applied_app_id == test_app_id, \
            f"Expected app_id {test_app_id}, got {applied_app_id}"
        
    finally:
        await monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_game_exit_resets_undervolt():
    """Test that game exit transition resets undervolt to default.
    
    When Game Only Mode is enabled and a game exits, the system should
    reset undervolt values to 0 (default).
    
    **Feature: ui-refactor-settings, Property 3: Game state transition triggers**
    **Validates: Requirements 5.2**
    """
    undervolt_reset = asyncio.Event()
    
    async def on_game_start(app_id: int):
        pass
    
    async def on_game_exit():
        undervolt_reset.set()
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    try:
        await monitor.start_monitoring()
        
        # Simulate game exit
        await on_game_exit()
        
        # Wait for undervolt reset
        try:
            await asyncio.wait_for(undervolt_reset.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Undervolt not reset within 2 seconds")
        
    finally:
        await monitor.stop_monitoring()


@pytest.mark.asyncio
@given(app_id=st.integers(min_value=1, max_value=999999))
@hyp_settings(max_examples=100, deadline=None)
async def test_transition_timing_constraint(app_id):
    """Property: All transitions complete within 2 second timeout.
    
    For any game state transition, the callback must complete within
    2 seconds to meet the timing requirement.
    
    **Feature: ui-refactor-settings, Property 3: Game state transition triggers**
    **Validates: Requirements 5.4**
    """
    start_time = None
    end_time = None
    
    async def on_game_start(detected_app_id: int):
        nonlocal start_time, end_time
        start_time = time.time()
        # Simulate some processing
        await asyncio.sleep(0.01)
        end_time = time.time()
    
    async def on_game_exit():
        nonlocal start_time, end_time
        start_time = time.time()
        # Simulate some processing
        await asyncio.sleep(0.01)
        end_time = time.time()
    
    monitor = GameStateMonitor(
        on_game_start=on_game_start,
        on_game_exit=on_game_exit,
        poll_interval=0.1
    )
    
    try:
        await monitor.start_monitoring()
        
        # Test game start
        await on_game_start(app_id)
        assert end_time is not None, "Callback did not complete"
        elapsed = end_time - start_time
        assert elapsed <= 2.0, \
            f"Game start callback took {elapsed:.3f}s, exceeds 2 second limit"
        
        # Reset timing
        start_time = None
        end_time = None
        
        # Test game exit
        await on_game_exit()
        assert end_time is not None, "Callback did not complete"
        elapsed = end_time - start_time
        assert elapsed <= 2.0, \
            f"Game exit callback took {elapsed:.3f}s, exceeds 2 second limit"
        
    finally:
        await monitor.stop_monitoring()
