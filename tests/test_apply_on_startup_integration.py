"""Integration test for Apply on Startup functionality.

This test verifies that the Apply on Startup logic works correctly
when integrated with the ProfileManager and SettingsManager.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from backend.core.settings_manager import SettingsManager
from backend.dynamic.profile_manager import ProfileManager


def test_apply_on_startup_integration():
    """Integration test: Apply on Startup with ProfileManager."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Setup mock dependencies
        mock_ryzenadj = MagicMock()
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_event_emitter = MagicMock()
        mock_event_emitter.emit_profile_changed = MagicMock()
        
        mock_decky_settings = MagicMock()
        mock_decky_settings.getSetting = MagicMock(return_value={})
        mock_decky_settings.setSetting = MagicMock()
        
        # Create ProfileManager with core_settings_manager
        profile_manager = ProfileManager(
            settings_manager=mock_decky_settings,
            ryzenadj=mock_ryzenadj,
            dynamic_controller=None,
            event_emitter=mock_event_emitter,
            core_settings_manager=settings_manager
        )
        
        # Create a test profile
        async def setup_and_test():
            # Create profile
            profile = await profile_manager.create_profile(
                app_id=12345,
                name="Test Game",
                cores=[-10, -10, -10, -10]
            )
            assert profile is not None
            
            # Apply the profile (should update last_active_profile)
            success = await profile_manager.apply_profile(12345)
            assert success
            
            # Verify last_active_profile was updated
            last_profile = settings_manager.get_setting("last_active_profile")
            assert last_profile == "12345"
            
            # Enable Apply on Startup
            settings_manager.save_setting("apply_on_startup", True)
            
            # Simulate plugin restart - check if profile would be applied
            apply_on_startup = settings_manager.get_setting("apply_on_startup", False)
            last_active_profile = settings_manager.get_setting("last_active_profile")
            
            assert apply_on_startup is True
            assert last_active_profile == "12345"
            
            # Verify profile exists and can be retrieved
            profile = profile_manager.get_profile(12345)
            assert profile is not None
            assert profile.name == "Test Game"
            
            return True
        
        result = asyncio.run(setup_and_test())
        assert result is True


def test_last_active_profile_updates_on_each_apply():
    """Test that last_active_profile updates every time a profile is applied."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Setup mock dependencies
        mock_ryzenadj = MagicMock()
        mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
        
        mock_event_emitter = MagicMock()
        mock_event_emitter.emit_profile_changed = MagicMock()
        
        mock_decky_settings = MagicMock()
        mock_decky_settings.getSetting = MagicMock(return_value={})
        mock_decky_settings.setSetting = MagicMock()
        
        # Create ProfileManager with core_settings_manager
        profile_manager = ProfileManager(
            settings_manager=mock_decky_settings,
            ryzenadj=mock_ryzenadj,
            dynamic_controller=None,
            event_emitter=mock_event_emitter,
            core_settings_manager=settings_manager
        )
        
        async def test_multiple_applies():
            # Create multiple profiles
            await profile_manager.create_profile(
                app_id=111,
                name="Game 1",
                cores=[-5, -5, -5, -5]
            )
            await profile_manager.create_profile(
                app_id=222,
                name="Game 2",
                cores=[-10, -10, -10, -10]
            )
            await profile_manager.create_profile(
                app_id=333,
                name="Game 3",
                cores=[-15, -15, -15, -15]
            )
            
            # Apply profiles in sequence
            await profile_manager.apply_profile(111)
            assert settings_manager.get_setting("last_active_profile") == "111"
            
            await profile_manager.apply_profile(222)
            assert settings_manager.get_setting("last_active_profile") == "222"
            
            await profile_manager.apply_profile(333)
            assert settings_manager.get_setting("last_active_profile") == "333"
            
            # Apply first profile again
            await profile_manager.apply_profile(111)
            assert settings_manager.get_setting("last_active_profile") == "111"
            
            return True
        
        result = asyncio.run(test_multiple_applies())
        assert result is True
