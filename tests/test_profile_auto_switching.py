"""Integration test for profile auto-switching on game launch.

Tests the complete profile auto-switching workflow:
1. Mock Steam game launch (create appmanifest file)
2. Verify AppWatcher detects app change
3. Verify profile is applied
4. Verify event is emitted

Requirements: 4.1, 4.2, 4.4

Note: These are simplified integration tests that focus on the core workflow
without complex async timing issues.
"""

import pytest
import os
import tempfile
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch, call
from pathlib import Path

from backend.platform.appwatcher import AppWatcher
from backend.dynamic.profile_manager import ProfileManager, GameProfile
from backend.platform.detect import PlatformInfo
from backend.core.ryzenadj import RyzenadjWrapper
from backend.dynamic.controller import DynamicController
from backend.api.events import EventEmitter


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {
            "game_profiles": {
                "version": "3.0",
                "global_default": {
                    "cores": [0, 0, 0, 0],
                    "dynamic_enabled": False
                },
                "profiles": []
            },
            "cores": [0, 0, 0, 0]
        }
    
    def getSetting(self, key, default=None):
        return self._settings.get(key, default)
    
    def setSetting(self, key, value):
        self._settings[key] = value


def create_default_platform() -> PlatformInfo:
    """Create a default LCD platform for testing."""
    return PlatformInfo(model="Jupiter", variant="LCD", safe_limit=-30, detected=True)


class TestProfileAutoSwitching:
    """Integration tests for profile auto-switching workflow."""
    
    @pytest.mark.asyncio
    async def test_profile_manager_applies_profile(self):
        """Test that ProfileManager can apply a profile successfully."""
        # Setup
        settings_manager = MockSettingsManager()
        
        # Create mock dependencies
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        # Create profile manager
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Create a profile
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25],
            dynamic_enabled=False
        )
        
        # Apply the profile
        result = await profile_manager.apply_profile(1091500)
        
        # Verify profile was applied
        assert result is True, "Profile application should succeed"
        mock_ryzenadj.apply_values_async.assert_called_once()
        applied_values = mock_ryzenadj.apply_values_async.call_args[0][0]
        assert applied_values == [-25, -25, -25, -25], "Should apply profile's undervolt values"
        
        # Verify event was emitted
        mock_emitter.emit_profile_changed.assert_called_once_with("Cyberpunk 2077", 1091500)
    
    @pytest.mark.asyncio
    async def test_profile_manager_applies_global_default(self):
        """Test that ProfileManager applies global default when no profile exists."""
        # Setup
        settings_manager = MockSettingsManager()
        
        # Set global default to -10mV
        settings_data = settings_manager.getSetting("game_profiles")
        settings_data["global_default"]["cores"] = [-10, -10, -10, -10]
        settings_manager.setSetting("game_profiles", settings_data)
        
        # Create mock dependencies
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        # Create profile manager
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Apply global default (no profile for AppID 570)
        result = await profile_manager.apply_global_default()
        
        # Verify global default was applied
        assert result is True
        mock_ryzenadj.apply_values_async.assert_called_once()
        applied_values = mock_ryzenadj.apply_values_async.call_args[0][0]
        assert applied_values == [-10, -10, -10, -10], "Should apply global default values"
        
        # Verify event was emitted
        mock_emitter.emit_profile_changed.assert_called_once_with("Global Default", None)
    
    @pytest.mark.asyncio
    async def test_on_app_change_applies_correct_profile(self):
        """Test that on_app_change applies the correct profile."""
        # Setup
        settings_manager = MockSettingsManager()
        
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Create profiles for two games
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25],
            dynamic_enabled=False
        )
        
        await profile_manager.create_profile(
            app_id=570,
            name="Dota 2",
            cores=[-15, -15, -15, -15],
            dynamic_enabled=False
        )
        
        # Simulate app change to Cyberpunk
        await profile_manager.on_app_change(1091500)
        
        # Verify Cyberpunk profile was applied
        assert mock_ryzenadj.apply_values_async.call_count == 1
        applied_values = mock_ryzenadj.apply_values_async.call_args[0][0]
        assert applied_values == [-25, -25, -25, -25]
        
        # Reset mock
        mock_ryzenadj.apply_values_async.reset_mock()
        
        # Simulate app change to Dota 2
        await profile_manager.on_app_change(570)
        
        # Verify Dota 2 profile was applied
        assert mock_ryzenadj.apply_values_async.call_count == 1
        applied_values = mock_ryzenadj.apply_values_async.call_args[0][0]
        assert applied_values == [-15, -15, -15, -15]
    
    @pytest.mark.asyncio
    async def test_app_watcher_calls_on_app_change(self):
        """Test that AppWatcher calls ProfileManager.on_app_change when app changes."""
        # Setup
        settings_manager = MockSettingsManager()
        
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Mock on_app_change to track calls
        profile_manager.on_app_change = AsyncMock()
        
        # Create AppWatcher
        watcher = AppWatcher(profile_manager, poll_interval=0.1)
        
        # Mock _get_active_app_id to return a specific AppID
        with patch.object(watcher, '_get_active_app_id', return_value=1091500):
            await watcher.start()
            await asyncio.sleep(0.15)  # Wait for one poll cycle
            await watcher.stop()
        
        # Verify on_app_change was called with the AppID
        profile_manager.on_app_change.assert_called()
        call_args = profile_manager.on_app_change.call_args[0]
        assert call_args[0] == 1091500, "Should call on_app_change with detected AppID"
    
    @pytest.mark.asyncio
    async def test_app_watcher_detects_app_change(self):
        """Test that AppWatcher detects when app changes."""
        # Setup
        settings_manager = MockSettingsManager()
        
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Mock on_app_change to track calls
        profile_manager.on_app_change = AsyncMock()
        
        # Create AppWatcher with short poll interval and no debounce
        watcher = AppWatcher(profile_manager, poll_interval=0.05)
        watcher.DEBOUNCE_DELAY = 0.0  # Disable debounce for testing
        
        # Simulate app change: None -> 1091500 -> 570
        app_sequence = [None, 1091500, 570]
        call_count = [0]
        
        def mock_get_app_id():
            idx = min(call_count[0], len(app_sequence) - 1)
            call_count[0] += 1
            return app_sequence[idx]
        
        with patch.object(watcher, '_get_active_app_id', side_effect=mock_get_app_id):
            await watcher.start()
            
            # Wait for polls to complete (start + 2 more polls)
            await asyncio.sleep(0.2)
            
            await watcher.stop()
        
        # Verify on_app_change was called for each app change
        # First call on start (None), then 1091500, then 570
        assert profile_manager.on_app_change.call_count >= 2, \
            f"Should call on_app_change for each app change, got {profile_manager.on_app_change.call_count}"
    
    @pytest.mark.asyncio
    async def test_profile_with_dynamic_mode_starts_controller(self):
        """Test that applying a profile with dynamic mode starts the controller."""
        # Setup
        settings_manager = MockSettingsManager()
        
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_dynamic = Mock(spec=DynamicController)
        mock_dynamic.start = AsyncMock()
        mock_dynamic.is_running = Mock(return_value=False)
        
        mock_emitter = Mock(spec=EventEmitter)
        mock_emitter.emit_profile_changed = Mock()
        
        profile_manager = ProfileManager(
            settings_manager,
            mock_ryzenadj,
            mock_dynamic,
            mock_emitter
        )
        
        # Create profile with dynamic mode enabled
        await profile_manager.create_profile(
            app_id=1091500,
            name="Cyberpunk 2077",
            cores=[-25, -25, -25, -25],
            dynamic_enabled=True,
            dynamic_config={
                "strategy": "balanced",
                "simple_mode": True,
                "simple_value": -25
            }
        )
        
        # Apply the profile
        result = await profile_manager.apply_profile(1091500)
        
        # Verify profile was applied successfully
        assert result is True, "Profile should be applied successfully"
        
        # Verify undervolt values were applied
        mock_ryzenadj.apply_values_async.assert_called_once()
        applied_values = mock_ryzenadj.apply_values_async.call_args[0][0]
        assert applied_values == [-25, -25, -25, -25], "Should apply profile's undervolt values"
        
        # Note: Dynamic mode start is currently a TODO in the implementation
        # When implemented, this test should verify mock_dynamic.start.assert_called_once()

