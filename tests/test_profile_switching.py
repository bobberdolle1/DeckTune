"""Integration tests for profile switching functionality.

Tests the complete workflow of automatic profile switching when games launch,
including fallback to global default and quick-create from active game.

Feature: decktune-3.0-automation
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from backend.dynamic.profile_manager import ProfileManager, GameProfile
from backend.platform.appwatcher import AppWatcher
from backend.api.events import EventEmitter


@pytest.fixture
def mock_settings():
    """Mock settings manager."""
    settings = {}
    
    class MockSettings:
        def getSetting(self, key, default=None):
            return settings.get(key, default)
        
        def setSetting(self, key, value):
            settings[key] = value
    
    return MockSettings()


@pytest.fixture
def mock_ryzenadj():
    """Mock RyzenadjWrapper."""
    mock = AsyncMock()
    mock.apply_values_async = AsyncMock(return_value=(True, None))
    return mock


@pytest.fixture
def mock_dynamic_controller():
    """Mock DynamicController."""
    mock = Mock()
    mock.is_running = Mock(return_value=False)
    mock.stop = AsyncMock()
    return mock


@pytest.fixture
def mock_event_emitter():
    """Mock EventEmitter."""
    mock = Mock()
    mock.emit_profile_changed = Mock()
    return mock


@pytest.fixture
def profile_manager(mock_settings, mock_ryzenadj, mock_dynamic_controller, mock_event_emitter):
    """Create ProfileManager instance with mocks."""
    return ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=mock_dynamic_controller,
        event_emitter=mock_event_emitter
    )


@pytest.fixture
def app_watcher(profile_manager):
    """Create AppWatcher instance."""
    return AppWatcher(
        profile_manager=profile_manager,
        poll_interval=0.1  # Fast polling for tests
    )


class TestProfileApplicationOnAppChange:
    """Test profile application when app changes.
    
    Requirements: 4.1, 4.2
    """
    
    @pytest.mark.asyncio
    async def test_apply_specific_profile_when_game_launches(
        self,
        profile_manager,
        mock_ryzenadj
    ):
        """Test that specific profile is applied when game with profile launches.
        
        Requirements: 4.2
        """
        # Create a profile for Cyberpunk 2077 (app_id: 1091500)
        profile = await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25],
            dynamic_enabled=False
        )
        
        assert profile is not None
        
        # Simulate app change to Cyberpunk 2077
        await profile_manager.on_app_change(1091500)
        
        # Verify profile was applied
        mock_ryzenadj.apply_values_async.assert_called_once_with([-25, -25, -25, -25])
        
        # Verify current app_id is set
        assert profile_manager._current_app_id == 1091500
    
    @pytest.mark.asyncio
    async def test_profile_event_emitted_on_switch(
        self,
        profile_manager,
        mock_event_emitter
    ):
        """Test that profile_changed event is emitted when profile switches.
        
        Requirements: 4.4
        """
        # Create a profile
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25]
        )
        
        # Apply profile
        await profile_manager.on_app_change(1091500)
        
        # Verify event was emitted
        mock_event_emitter.emit_profile_changed.assert_called_once_with(
            "Cyberpunk 2077",
            1091500
        )
    
    @pytest.mark.asyncio
    async def test_last_used_timestamp_updated(
        self,
        profile_manager
    ):
        """Test that last_used timestamp is updated when profile is applied.
        
        Requirements: 4.2
        """
        # Create a profile
        profile = await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25]
        )
        
        assert profile.last_used is None
        
        # Apply profile
        await profile_manager.on_app_change(1091500)
        
        # Get updated profile
        updated_profile = profile_manager.get_profile(1091500)
        
        # Verify last_used was set
        assert updated_profile.last_used is not None


class TestFallbackToGlobalDefault:
    """Test fallback to global default when no profile exists.
    
    Requirements: 4.3
    """
    
    @pytest.mark.asyncio
    async def test_apply_global_default_when_no_profile_exists(
        self,
        profile_manager,
        mock_ryzenadj
    ):
        """Test that global default is applied when no profile exists for game.
        
        Requirements: 4.3
        """
        # Set global default
        profile_manager.set_global_default(
            cores=[-15, -15, -15, -15],
            dynamic_enabled=False
        )
        
        # Simulate app change to game without profile (app_id: 999999)
        await profile_manager.on_app_change(999999)
        
        # Verify global default was applied
        mock_ryzenadj.apply_values_async.assert_called_once_with([-15, -15, -15, -15])
        
        # Verify current app_id is None (no specific profile)
        assert profile_manager._current_app_id is None
    
    @pytest.mark.asyncio
    async def test_global_default_event_emitted(
        self,
        profile_manager,
        mock_event_emitter
    ):
        """Test that event is emitted when global default is applied.
        
        Requirements: 4.3, 4.4
        """
        # Simulate app change to game without profile
        await profile_manager.on_app_change(999999)
        
        # Verify event was emitted with "Global Default"
        mock_event_emitter.emit_profile_changed.assert_called_once_with(
            "Global Default",
            None
        )
    
    @pytest.mark.asyncio
    async def test_apply_global_default_when_no_game_running(
        self,
        profile_manager,
        mock_ryzenadj
    ):
        """Test that global default is applied when no game is running.
        
        Requirements: 4.3
        """
        # Set global default
        profile_manager.set_global_default(
            cores=[-10, -10, -10, -10],
            dynamic_enabled=False
        )
        
        # Simulate no game running (app_id: None)
        await profile_manager.on_app_change(None)
        
        # Verify global default was applied
        mock_ryzenadj.apply_values_async.assert_called_once_with([-10, -10, -10, -10])


class TestQuickCreateFromActiveGame:
    """Test quick-create profile from active game.
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    
    @pytest.mark.asyncio
    async def test_create_profile_from_current_settings(
        self,
        profile_manager,
        mock_settings
    ):
        """Test creating profile from current active settings.
        
        Requirements: 5.2
        """
        # Set current settings
        mock_settings.setSetting("cores", [-20, -20, -20, -20])
        
        # Create profile from current settings
        profile = await profile_manager.create_from_current(
            app_id=1091500,
            name="Cyberpunk 2077"
        )
        
        assert profile is not None
        assert profile.app_id == 1091500
        assert profile.name == "Cyberpunk 2077"
        assert profile.cores == [-20, -20, -20, -20]
        assert profile.dynamic_enabled is False
    
    @pytest.mark.asyncio
    async def test_quick_create_captures_dynamic_config(
        self,
        profile_manager,
        mock_settings,
        mock_dynamic_controller
    ):
        """Test that quick-create captures dynamic mode configuration.
        
        Requirements: 5.2
        """
        # Set current settings with dynamic mode
        mock_settings.setSetting("cores", [-25, -25, -25, -25])
        mock_settings.setSetting("dynamic_config", {
            "strategy": "balanced",
            "simple_mode": True,
            "simple_value": -25
        })
        
        # Mock dynamic controller as running
        mock_dynamic_controller.is_running = Mock(return_value=True)
        
        # Create profile from current settings
        profile = await profile_manager.create_from_current(
            app_id=1091500,
            name="Cyberpunk 2077"
        )
        
        assert profile is not None
        assert profile.dynamic_enabled is True
        assert profile.dynamic_config is not None
        assert profile.dynamic_config["strategy"] == "balanced"
    
    @pytest.mark.asyncio
    async def test_quick_create_fails_if_profile_exists(
        self,
        profile_manager
    ):
        """Test that quick-create fails if profile already exists.
        
        Requirements: 5.1
        """
        # Create initial profile
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-20, -20, -20, -20]
        )
        
        # Try to create another profile with same app_id
        profile = await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077 v2",
            cores=[-25, -25, -25, -25]
        )
        
        # Should fail
        assert profile is None


class TestAppWatcherIntegration:
    """Test AppWatcher integration with ProfileManager.
    
    Requirements: 4.1, 4.6
    """
    
    @pytest.mark.asyncio
    async def test_watcher_detects_app_on_startup(
        self,
        app_watcher,
        profile_manager,
        mock_ryzenadj
    ):
        """Test that watcher detects current app on startup and applies profile.
        
        Requirements: 4.6
        """
        # Create a profile
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25]
        )
        
        # Mock app detection to return our app_id
        with patch.object(app_watcher, '_get_active_app_id', return_value=1091500):
            # Start watcher
            await app_watcher.start()
            
            # Give it a moment to detect and apply
            await asyncio.sleep(0.1)
            
            # Verify profile was applied
            mock_ryzenadj.apply_values_async.assert_called_with([-25, -25, -25, -25])
            
            # Stop watcher
            await app_watcher.stop()
    
    @pytest.mark.asyncio
    async def test_watcher_applies_global_default_when_no_game(
        self,
        app_watcher,
        profile_manager,
        mock_ryzenadj
    ):
        """Test that watcher applies global default when no game is running.
        
        Requirements: 4.3, 4.6
        """
        # Set global default
        profile_manager.set_global_default(
            cores=[-10, -10, -10, -10],
            dynamic_enabled=False
        )
        
        # Mock app detection to return None (no game)
        with patch.object(app_watcher, '_get_active_app_id', return_value=None):
            # Start watcher
            await app_watcher.start()
            
            # Give it a moment to detect and apply
            await asyncio.sleep(0.1)
            
            # Verify global default was applied
            mock_ryzenadj.apply_values_async.assert_called_with([-10, -10, -10, -10])
            
            # Stop watcher
            await app_watcher.stop()
    
    @pytest.mark.asyncio
    async def test_watcher_stops_cleanly(
        self,
        app_watcher
    ):
        """Test that watcher stops cleanly without errors.
        
        Requirements: 4.6
        """
        # Mock app detection
        with patch.object(app_watcher, '_get_active_app_id', return_value=None):
            # Start watcher
            await app_watcher.start()
            assert app_watcher.is_running()
            
            # Stop watcher
            await app_watcher.stop()
            assert not app_watcher.is_running()


class TestProfileSwitchingWorkflow:
    """Test complete profile switching workflow.
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    
    @pytest.mark.asyncio
    async def test_complete_profile_switch_workflow(
        self,
        profile_manager,
        mock_ryzenadj,
        mock_event_emitter
    ):
        """Test complete workflow: create profiles, switch between games, fallback to default.
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        # Create profiles for two games
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25]
        )
        
        await profile_manager.create_profile(
            app_id=1245620,
            name="Elden Ring",
            cores=[-20, -20, -20, -20]
        )
        
        # Set global default
        profile_manager.set_global_default(
            cores=[-15, -15, -15, -15],
            dynamic_enabled=False
        )
        
        # Simulate launching Cyberpunk 2077
        await profile_manager.on_app_change(1091500)
        assert mock_ryzenadj.apply_values_async.call_args[0][0] == [-25, -25, -25, -25]
        mock_event_emitter.emit_profile_changed.assert_called_with("Cyberpunk 2077", 1091500)
        
        # Reset mocks
        mock_ryzenadj.reset_mock()
        mock_event_emitter.reset_mock()
        
        # Simulate switching to Elden Ring
        await profile_manager.on_app_change(1245620)
        assert mock_ryzenadj.apply_values_async.call_args[0][0] == [-20, -20, -20, -20]
        mock_event_emitter.emit_profile_changed.assert_called_with("Elden Ring", 1245620)
        
        # Reset mocks
        mock_ryzenadj.reset_mock()
        mock_event_emitter.reset_mock()
        
        # Simulate launching game without profile
        await profile_manager.on_app_change(999999)
        assert mock_ryzenadj.apply_values_async.call_args[0][0] == [-15, -15, -15, -15]
        mock_event_emitter.emit_profile_changed.assert_called_with("Global Default", None)
        
        # Reset mocks
        mock_ryzenadj.reset_mock()
        mock_event_emitter.reset_mock()
        
        # Simulate exiting all games
        await profile_manager.on_app_change(None)
        assert mock_ryzenadj.apply_values_async.call_args[0][0] == [-15, -15, -15, -15]
        mock_event_emitter.emit_profile_changed.assert_called_with("Global Default", None)
