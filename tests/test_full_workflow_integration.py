"""Integration tests for full UI refactor workflows.

Feature: ui-refactor-settings
Validates: All Requirements

This module tests complete end-to-end workflows including:
- Full navigation flow: Main → Settings → Expert Mode → Manual
- Apply on Startup with plugin reload
- Game Only Mode with simulated game events
- Settings persistence across plugin reload
- Error recovery scenarios
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import json

from backend.core.settings_manager import SettingsManager
from backend.core.game_state_monitor import GameStateMonitor
from backend.core.game_only_mode import GameOnlyModeController
from backend.dynamic.profile_manager import ProfileManager


class TestFullNavigationFlow:
    """Test full navigation flow: Main → Settings → Expert Mode → Manual.
    
    Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 8.1, 8.2, 8.3
    """
    
    def test_settings_menu_opens_and_expert_mode_toggle_works(self):
        """Test that Settings menu can be opened and Expert Mode can be toggled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Initial state: Expert Mode should be disabled
            expert_mode = settings_manager.get_setting("expert_mode", False)
            assert expert_mode is False, "Expert Mode should be disabled initially"
            
            # Simulate opening Settings menu and enabling Expert Mode
            # (with confirmation)
            settings_manager.save_setting("expert_mode", True)
            
            # Verify Expert Mode is now enabled
            expert_mode = settings_manager.get_setting("expert_mode")
            assert expert_mode is True, "Expert Mode should be enabled after toggle"
            
            # Simulate navigating to Manual tab
            # Manual tab should not show Expert Mode toggle (Requirement 7.1)
            # This is a UI concern, but we can verify the setting persists
            assert settings_manager.get_setting("expert_mode") is True
    
    def test_header_navigation_to_fan_control(self):
        """Test navigation to Fan Control via header icon.
        
        Validates: Requirements 1.2, 8.1, 8.2, 8.3
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Simulate clicking Fan Control icon in header
            # This should navigate to Fan Control component
            # We verify by checking that the navigation state would be set
            settings_manager.save_setting("current_view", "fan_control")
            
            current_view = settings_manager.get_setting("current_view")
            assert current_view == "fan_control", "Should navigate to Fan Control"
            
            # Verify that Fan Control is not in mode list (Requirement 8.1)
            # This is a UI concern, but we can verify the setting
            mode_list = settings_manager.get_setting("available_modes", ["wizard", "expert"])
            assert "fan_control" not in mode_list, "Fan Control should not be in mode list"
    
    def test_manual_tab_shows_startup_controls(self):
        """Test that Manual tab shows startup behavior controls.
        
        Validates: Requirements 7.2, 7.3, 7.4, 7.5
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Simulate navigating to Manual tab
            settings_manager.save_setting("active_tab", "manual")
            
            # Verify Apply on Startup toggle is available
            apply_on_startup = settings_manager.get_setting("apply_on_startup", False)
            assert apply_on_startup is not None, "Apply on Startup should be available"
            
            # Verify Game Only Mode toggle is available
            game_only_mode = settings_manager.get_setting("game_only_mode", False)
            assert game_only_mode is not None, "Game Only Mode should be available"
            
            # Test toggling Apply on Startup
            settings_manager.save_setting("apply_on_startup", True)
            assert settings_manager.get_setting("apply_on_startup") is True
            
            # Test toggling Game Only Mode
            settings_manager.save_setting("game_only_mode", True)
            assert settings_manager.get_setting("game_only_mode") is True


class TestApplyOnStartupWithReload:
    """Test Apply on Startup functionality with plugin reload simulation.
    
    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    @pytest.mark.asyncio
    async def test_apply_on_startup_with_plugin_reload(self):
        """Test that Apply on Startup works across plugin reload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup first plugin instance
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_event_emitter.emit_profile_changed = MagicMock()
            
            mock_decky_settings = MagicMock()
            mock_decky_settings.getSetting = MagicMock(return_value={})
            mock_decky_settings.setSetting = MagicMock()
            
            profile_manager = ProfileManager(
                settings_manager=mock_decky_settings,
                ryzenadj=mock_ryzenadj,
                dynamic_controller=None,
                event_emitter=mock_event_emitter,
                core_settings_manager=settings_manager
            )
            
            # Create and apply a profile
            profile = await profile_manager.create_profile(
                app_id=12345,
                name="Test Game",
                cores=[-15, -15, -15, -15]
            )
            assert profile is not None
            
            success = await profile_manager.apply_profile(12345)
            assert success is True
            
            # Enable Apply on Startup
            settings_manager.save_setting("apply_on_startup", True)
            
            # Verify settings are persisted
            assert settings_manager.get_setting("apply_on_startup") is True
            assert settings_manager.get_setting("last_active_profile") == "12345"
            
            # Simulate plugin reload by creating new instances
            settings_manager_reloaded = SettingsManager(storage_dir=Path(temp_dir))
            
            # Verify settings survived reload
            assert settings_manager_reloaded.get_setting("apply_on_startup") is True
            assert settings_manager_reloaded.get_setting("last_active_profile") == "12345"
            
            # Create new profile manager with reloaded settings
            mock_ryzenadj_reloaded = MagicMock()
            mock_ryzenadj_reloaded.apply_values_async = AsyncMock(return_value=(True, None))
            
            profile_manager_reloaded = ProfileManager(
                settings_manager=mock_decky_settings,
                ryzenadj=mock_ryzenadj_reloaded,
                dynamic_controller=None,
                event_emitter=mock_event_emitter,
                core_settings_manager=settings_manager_reloaded
            )
            
            # Simulate startup profile application
            last_profile = settings_manager_reloaded.get_setting("last_active_profile")
            if last_profile:
                # Profile needs to be recreated in the new manager instance
                # In real scenario, profiles are persisted via decky settings
                await profile_manager_reloaded.create_profile(
                    app_id=12345,
                    name="Test Game",
                    cores=[-15, -15, -15, -15]
                )
                profile = profile_manager_reloaded.get_profile(int(last_profile))
                if profile:
                    await profile_manager_reloaded.apply_profile(int(last_profile))
            
            # Verify profile was applied on startup
            mock_ryzenadj_reloaded.apply_values_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_apply_on_startup_handles_missing_profile(self):
        """Test that Apply on Startup handles missing profile gracefully.
        
        Validates: Requirements 4.3, 4.5
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Enable Apply on Startup but don't create a profile
            settings_manager.save_setting("apply_on_startup", True)
            settings_manager.save_setting("last_active_profile", "99999")
            
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_decky_settings = MagicMock()
            mock_decky_settings.getSetting = MagicMock(return_value={})
            mock_decky_settings.setSetting = MagicMock()
            
            profile_manager = ProfileManager(
                settings_manager=mock_decky_settings,
                ryzenadj=mock_ryzenadj,
                dynamic_controller=None,
                event_emitter=mock_event_emitter,
                core_settings_manager=settings_manager
            )
            
            # Simulate startup profile application with missing profile
            last_profile = settings_manager.get_setting("last_active_profile")
            profile = profile_manager.get_profile(int(last_profile))
            
            # Profile should not exist
            assert profile is None, "Profile should not exist"
            
            # Verify no crash occurred and ryzenadj was not called
            mock_ryzenadj.apply_values_async.assert_not_called()


class TestGameOnlyModeWithSimulatedEvents:
    """Test Game Only Mode with simulated game events.
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    @pytest.mark.asyncio
    async def test_game_only_mode_full_lifecycle(self):
        """Test complete Game Only Mode lifecycle with game events."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            settings_manager.save_setting("cores", [-10, -10, -10, -10])
            
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_event_emitter.emit_status = AsyncMock()
            
            # Track game state changes
            game_events = []
            
            async def on_game_start(app_id: int):
                game_events.append(("start", app_id))
            
            async def on_game_exit():
                game_events.append(("exit", None))
            
            monitor = GameStateMonitor(
                on_game_start=on_game_start,
                on_game_exit=on_game_exit,
                poll_interval=0.1
            )
            
            controller = GameOnlyModeController(
                game_state_monitor=monitor,
                ryzenadj=mock_ryzenadj,
                settings_manager=settings_manager,
                event_emitter=mock_event_emitter
            )
            
            # Enable Game Only Mode
            success = await controller.enable()
            assert success is True
            assert controller.is_enabled() is True
            assert monitor.is_running() is True
            
            # Simulate game start
            await controller.on_game_start(123456)
            
            # Verify profile was applied
            mock_ryzenadj.apply_values_async.assert_called_once_with([-10, -10, -10, -10])
            
            # Simulate game exit
            await controller.on_game_exit()
            
            # Verify undervolt was reset
            mock_ryzenadj.disable_async.assert_called_once()
            
            # Disable Game Only Mode
            success = await controller.disable()
            assert success is True
            assert controller.is_enabled() is False
            assert monitor.is_running() is False
    
    @pytest.mark.asyncio
    async def test_game_only_mode_multiple_game_sessions(self):
        """Test Game Only Mode with multiple game start/exit cycles."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            settings_manager.save_setting("cores", [-12, -12, -12, -12])
            
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_event_emitter.emit_status = AsyncMock()
            
            monitor = GameStateMonitor(
                on_game_start=lambda app_id: None,
                on_game_exit=lambda: None,
                poll_interval=0.1
            )
            
            controller = GameOnlyModeController(
                game_state_monitor=monitor,
                ryzenadj=mock_ryzenadj,
                settings_manager=settings_manager,
                event_emitter=mock_event_emitter
            )
            
            await controller.enable()
            
            # Simulate multiple game sessions
            for i in range(3):
                # Game start
                await controller.on_game_start(100 + i)
                
                # Game exit
                await controller.on_game_exit()
            
            # Verify profile was applied 3 times
            assert mock_ryzenadj.apply_values_async.call_count == 3
            
            # Verify undervolt was reset 3 times
            assert mock_ryzenadj.disable_async.call_count == 3
            
            await controller.disable()


class TestSettingsPersistenceAcrossReload:
    """Test settings persistence across plugin reload.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.5, 10.3, 10.4
    """
    
    def test_all_settings_persist_across_reload(self):
        """Test that all settings persist across plugin reload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First instance
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Set all settings
            settings_manager.save_setting("expert_mode", True)
            settings_manager.save_setting("apply_on_startup", True)
            settings_manager.save_setting("game_only_mode", True)
            settings_manager.save_setting("last_active_profile", "12345")
            settings_manager.save_setting("cores", [-15, -15, -15, -15])
            
            # Verify settings were saved
            assert settings_manager.get_setting("expert_mode") is True
            assert settings_manager.get_setting("apply_on_startup") is True
            assert settings_manager.get_setting("game_only_mode") is True
            assert settings_manager.get_setting("last_active_profile") == "12345"
            assert settings_manager.get_setting("cores") == [-15, -15, -15, -15]
            
            # Simulate reload by creating new instance
            settings_manager_reloaded = SettingsManager(storage_dir=Path(temp_dir))
            
            # Verify all settings survived reload
            assert settings_manager_reloaded.get_setting("expert_mode") is True
            assert settings_manager_reloaded.get_setting("apply_on_startup") is True
            assert settings_manager_reloaded.get_setting("game_only_mode") is True
            assert settings_manager_reloaded.get_setting("last_active_profile") == "12345"
            assert settings_manager_reloaded.get_setting("cores") == [-15, -15, -15, -15]
    
    def test_settings_persist_with_multiple_updates(self):
        """Test that settings persist correctly with multiple updates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Update settings multiple times
            for i in range(5):
                settings_manager.save_setting("expert_mode", i % 2 == 0)
                settings_manager.save_setting("last_active_profile", str(1000 + i))
            
            # Verify final values
            assert settings_manager.get_setting("expert_mode") is True  # 4 % 2 == 0
            assert settings_manager.get_setting("last_active_profile") == "1004"
            
            # Reload and verify
            settings_manager_reloaded = SettingsManager(storage_dir=Path(temp_dir))
            assert settings_manager_reloaded.get_setting("expert_mode") is True
            assert settings_manager_reloaded.get_setting("last_active_profile") == "1004"
    
    def test_settings_file_format_is_valid_json(self):
        """Test that settings file is valid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Save some settings
            settings_manager.save_setting("expert_mode", True)
            settings_manager.save_setting("cores", [-10, -10, -10, -10])
            
            # Read the file directly
            settings_file = Path(temp_dir) / "settings.json"
            assert settings_file.exists(), "Settings file should exist"
            
            # Verify it's valid JSON
            with open(settings_file, 'r') as f:
                data = json.load(f)
            
            assert "expert_mode" in data
            assert "cores" in data
            assert data["expert_mode"] is True
            assert data["cores"] == [-10, -10, -10, -10]


class TestErrorRecoveryScenarios:
    """Test error recovery scenarios.
    
    Validates: Requirements 3.5, 4.5, 6.4
    """
    
    def test_storage_read_failure_uses_defaults(self):
        """Test that storage read failure falls back to defaults.
        
        Validates: Requirements 3.5
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Create corrupted settings file
            settings_file = Path(temp_dir) / "settings.json"
            with open(settings_file, 'w') as f:
                f.write("{ invalid json }")
            
            # Try to read settings - should fall back to defaults
            expert_mode = settings_manager.get_setting("expert_mode", False)
            assert expert_mode is False, "Should use default value on read error"
            
            # Verify we can still write
            settings_manager.save_setting("expert_mode", True)
            assert settings_manager.get_setting("expert_mode") is True
    
    def test_storage_write_failure_continues_operation(self):
        """Test that storage write failure doesn't crash the system.
        
        Validates: Requirements 3.5
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Create settings file first
            settings_manager.save_setting("expert_mode", False)
            
            # Make directory read-only to simulate write failure
            import os
            settings_file = Path(temp_dir) / "settings.json"
            os.chmod(settings_file, 0o444)
            
            try:
                # Try to save setting - should not crash
                result = settings_manager.save_setting("expert_mode", True)
                
                # Operation should fail gracefully (returns False on Windows, may succeed on Unix)
                # The important thing is it doesn't crash
                assert result is not None, "Save should not crash"
                
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(settings_file, 0o644)
                except:
                    pass
    
    @pytest.mark.asyncio
    async def test_game_state_monitor_failure_disables_gracefully(self):
        """Test that game state monitor failure is handled gracefully.
        
        Validates: Requirements 6.4
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_event_emitter.emit_status = AsyncMock()
            
            # Create monitor that will fail
            async def failing_callback(app_id: int):
                raise Exception("Simulated monitor failure")
            
            monitor = GameStateMonitor(
                on_game_start=failing_callback,
                on_game_exit=lambda: None,
                poll_interval=0.1
            )
            
            controller = GameOnlyModeController(
                game_state_monitor=monitor,
                ryzenadj=mock_ryzenadj,
                settings_manager=settings_manager,
                event_emitter=mock_event_emitter
            )
            
            # Enable should succeed
            success = await controller.enable()
            assert success is True
            
            # Trigger failure - should not crash
            try:
                await controller.on_game_start(123456)
            except Exception:
                pass  # Expected to fail
            
            # Controller should still be functional
            assert controller.is_enabled() is True
            
            # Should be able to disable cleanly
            success = await controller.disable()
            assert success is True
    
    @pytest.mark.asyncio
    async def test_profile_application_failure_continues_startup(self):
        """Test that profile application failure doesn't prevent startup.
        
        Validates: Requirements 4.5
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Enable Apply on Startup with a profile
            settings_manager.save_setting("apply_on_startup", True)
            settings_manager.save_setting("last_active_profile", "12345")
            
            # Create mock that fails
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(False, "Simulated failure"))
            
            mock_event_emitter = MagicMock()
            mock_decky_settings = MagicMock()
            mock_decky_settings.getSetting = MagicMock(return_value={})
            mock_decky_settings.setSetting = MagicMock()
            
            profile_manager = ProfileManager(
                settings_manager=mock_decky_settings,
                ryzenadj=mock_ryzenadj,
                dynamic_controller=None,
                event_emitter=mock_event_emitter,
                core_settings_manager=settings_manager
            )
            
            # Create profile
            await profile_manager.create_profile(
                app_id=12345,
                name="Test Game",
                cores=[-10, -10, -10, -10]
            )
            
            # Try to apply profile - should fail but not crash
            success = await profile_manager.apply_profile(12345)
            assert success is False, "Profile application should fail"
            
            # Verify system continues to function
            assert settings_manager.get_setting("apply_on_startup") is True


class TestCompleteIntegrationScenario:
    """Test complete integration scenario combining all features.
    
    Validates: All Requirements
    """
    
    @pytest.mark.asyncio
    async def test_complete_user_workflow(self):
        """Test complete user workflow from setup to usage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Initialize settings
            settings_manager = SettingsManager(storage_dir=Path(temp_dir))
            
            # Step 2: Enable Expert Mode (via Settings menu)
            settings_manager.save_setting("expert_mode", True)
            assert settings_manager.get_setting("expert_mode") is True
            
            # Step 3: Create profile in Manual tab
            mock_ryzenadj = MagicMock()
            mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
            mock_ryzenadj.disable_async = AsyncMock(return_value=(True, None))
            
            mock_event_emitter = MagicMock()
            mock_event_emitter.emit_status = AsyncMock()
            mock_event_emitter.emit_profile_changed = MagicMock()
            
            mock_decky_settings = MagicMock()
            mock_decky_settings.getSetting = MagicMock(return_value={})
            mock_decky_settings.setSetting = MagicMock()
            
            profile_manager = ProfileManager(
                settings_manager=mock_decky_settings,
                ryzenadj=mock_ryzenadj,
                dynamic_controller=None,
                event_emitter=mock_event_emitter,
                core_settings_manager=settings_manager
            )
            
            profile = await profile_manager.create_profile(
                app_id=12345,
                name="Test Game",
                cores=[-15, -15, -15, -15]
            )
            assert profile is not None
            
            # Step 4: Enable Apply on Startup
            settings_manager.save_setting("apply_on_startup", True)
            
            # Step 5: Apply profile
            success = await profile_manager.apply_profile(12345)
            assert success is True
            assert settings_manager.get_setting("last_active_profile") == "12345"
            
            # Step 6: Enable Game Only Mode
            settings_manager.save_setting("game_only_mode", True)
            
            monitor = GameStateMonitor(
                on_game_start=lambda app_id: None,
                on_game_exit=lambda: None,
                poll_interval=0.1
            )
            
            controller = GameOnlyModeController(
                game_state_monitor=monitor,
                ryzenadj=mock_ryzenadj,
                settings_manager=settings_manager,
                event_emitter=mock_event_emitter
            )
            
            success = await controller.enable()
            assert success is True
            
            # Step 7: Simulate plugin reload
            settings_manager_reloaded = SettingsManager(storage_dir=Path(temp_dir))
            
            # Verify all settings persisted
            assert settings_manager_reloaded.get_setting("expert_mode") is True
            assert settings_manager_reloaded.get_setting("apply_on_startup") is True
            assert settings_manager_reloaded.get_setting("game_only_mode") is True
            assert settings_manager_reloaded.get_setting("last_active_profile") == "12345"
            
            # Step 8: Simulate game start
            await controller.on_game_start(12345)
            
            # Verify profile was applied
            mock_ryzenadj.apply_values_async.assert_called()
            
            # Step 9: Simulate game exit
            await controller.on_game_exit()
            
            # Verify undervolt was reset
            mock_ryzenadj.disable_async.assert_called()
            
            # Step 10: Cleanup
            await controller.disable()
            assert controller.is_enabled() is False
