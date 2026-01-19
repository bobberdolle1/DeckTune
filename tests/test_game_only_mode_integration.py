"""Integration tests for Game Only Mode controller.

Feature: ui-refactor-settings
Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5

This module tests the Game Only Mode controller integration with
the game state monitor and undervolt application.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
import tempfile

from backend.core.game_only_mode import GameOnlyModeController
from backend.core.game_state_monitor import GameStateMonitor
from backend.core.settings_manager import SettingsManager


@pytest.mark.asyncio
async def test_game_only_mode_enable_starts_monitoring():
    """Test that enabling Game Only Mode starts game state monitoring.
    
    Validates: Requirements 5.5, 6.1
    """
    # Create mocks
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = MagicMock()
    mock_event_emitter.emit_status = AsyncMock()
    
    # Create settings manager with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        settings_manager.save_setting("cores", [-10, -10, -10, -10])
        
        # Create game state monitor
        async def on_game_start(app_id: int):
            pass
        
        async def on_game_exit():
            pass
        
        monitor = GameStateMonitor(
            on_game_start=on_game_start,
            on_game_exit=on_game_exit,
            poll_interval=0.1
        )
        
        # Create controller
        controller = GameOnlyModeController(
            game_state_monitor=monitor,
            ryzenadj=mock_ryzenadj,
            settings_manager=settings_manager,
            event_emitter=mock_event_emitter
        )
        
        # Enable Game Only Mode
        success = await controller.enable()
        
        assert success is True, "Game Only Mode should enable successfully"
        assert controller.is_enabled() is True, "Controller should be enabled"
        assert monitor.is_running() is True, "Monitor should be running"
        
        # Cleanup
        await controller.disable()


@pytest.mark.asyncio
async def test_game_only_mode_disable_stops_monitoring():
    """Test that disabling Game Only Mode stops game state monitoring.
    
    Validates: Requirements 5.3, 6.5
    """
    # Create mocks
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = MagicMock()
    mock_event_emitter.emit_status = AsyncMock()
    
    # Create settings manager with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Create game state monitor
        async def on_game_start(app_id: int):
            pass
        
        async def on_game_exit():
            pass
        
        monitor = GameStateMonitor(
            on_game_start=on_game_start,
            on_game_exit=on_game_exit,
            poll_interval=0.1
        )
        
        # Create controller
        controller = GameOnlyModeController(
            game_state_monitor=monitor,
            ryzenadj=mock_ryzenadj,
            settings_manager=settings_manager,
            event_emitter=mock_event_emitter
        )
        
        # Enable then disable
        await controller.enable()
        success = await controller.disable()
        
        assert success is True, "Game Only Mode should disable successfully"
        assert controller.is_enabled() is False, "Controller should be disabled"
        assert monitor.is_running() is False, "Monitor should be stopped"
        
        # Verify undervolt was reset
        mock_ryzenadj.disable_async.assert_called_once()


@pytest.mark.asyncio
async def test_game_start_applies_profile():
    """Test that game start applies the saved profile.
    
    Validates: Requirements 5.1
    """
    # Create mocks
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = MagicMock()
    mock_event_emitter.emit_status = AsyncMock()
    
    # Create settings manager with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        test_profile = [-15, -15, -15, -15]
        settings_manager.save_setting("cores", test_profile)
        
        # Create game state monitor
        async def on_game_start(app_id: int):
            pass
        
        async def on_game_exit():
            pass
        
        monitor = GameStateMonitor(
            on_game_start=on_game_start,
            on_game_exit=on_game_exit,
            poll_interval=0.1
        )
        
        # Create controller
        controller = GameOnlyModeController(
            game_state_monitor=monitor,
            ryzenadj=mock_ryzenadj,
            settings_manager=settings_manager,
            event_emitter=mock_event_emitter
        )
        
        # Enable Game Only Mode
        await controller.enable()
        
        # Simulate game start
        await controller.on_game_start(123456)
        
        # Verify profile was applied
        mock_ryzenadj.apply_values_async.assert_called_once_with(test_profile)
        
        # Cleanup
        await controller.disable()


@pytest.mark.asyncio
async def test_game_exit_resets_undervolt():
    """Test that game exit resets undervolt to default.
    
    Validates: Requirements 5.2
    """
    # Create mocks
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = MagicMock()
    mock_event_emitter.emit_status = AsyncMock()
    
    # Create settings manager with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        settings_manager.save_setting("cores", [-10, -10, -10, -10])
        
        # Create game state monitor
        async def on_game_start(app_id: int):
            pass
        
        async def on_game_exit():
            pass
        
        monitor = GameStateMonitor(
            on_game_start=on_game_start,
            on_game_exit=on_game_exit,
            poll_interval=0.1
        )
        
        # Create controller
        controller = GameOnlyModeController(
            game_state_monitor=monitor,
            ryzenadj=mock_ryzenadj,
            settings_manager=settings_manager,
            event_emitter=mock_event_emitter
        )
        
        # Enable Game Only Mode
        await controller.enable()
        
        # Simulate game exit
        await controller.on_game_exit()
        
        # Verify undervolt was reset
        mock_ryzenadj.disable_async.assert_called_once()
        
        # Cleanup
        await controller.disable()


@pytest.mark.asyncio
async def test_game_transitions_complete_within_timeout():
    """Test that game state transitions complete within 2 seconds.
    
    Validates: Requirements 5.4
    """
    # Create mocks
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = MagicMock()
    mock_event_emitter.emit_status = AsyncMock()
    
    # Create settings manager with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        settings_manager.save_setting("cores", [-10, -10, -10, -10])
        
        # Create game state monitor
        async def on_game_start(app_id: int):
            pass
        
        async def on_game_exit():
            pass
        
        monitor = GameStateMonitor(
            on_game_start=on_game_start,
            on_game_exit=on_game_exit,
            poll_interval=0.1
        )
        
        # Create controller
        controller = GameOnlyModeController(
            game_state_monitor=monitor,
            ryzenadj=mock_ryzenadj,
            settings_manager=settings_manager,
            event_emitter=mock_event_emitter
        )
        
        # Enable Game Only Mode
        await controller.enable()
        
        # Test game start with timeout
        import time
        start_time = time.time()
        await controller.on_game_start(123456)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"Game start took {elapsed:.3f}s, exceeds 2 second limit"
        
        # Test game exit with timeout
        start_time = time.time()
        await controller.on_game_exit()
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"Game exit took {elapsed:.3f}s, exceeds 2 second limit"
        
        # Cleanup
        await controller.disable()
