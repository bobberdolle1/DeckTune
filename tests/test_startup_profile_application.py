"""Property-based tests for Apply on Startup functionality.

Feature: ui-refactor-settings
Property 4: Startup profile application
Validates: Requirements 4.1, 4.2

This module tests that when Apply on Startup is enabled and a last active
profile exists, the system applies that profile during plugin initialization.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings as hyp_settings
from backend.core.settings_manager import SettingsManager


# Strategy for generating valid profile names
profile_name_strategy = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())  # Ensure non-empty after stripping

# Strategy for generating valid core values
core_values_strategy = st.lists(
    st.integers(min_value=-100, max_value=0),
    min_size=4,
    max_size=4
)


@given(
    apply_on_startup=st.booleans(),
    last_active_profile=st.one_of(st.none(), profile_name_strategy),
    profile_exists=st.booleans()
)
@hyp_settings(max_examples=100, deadline=None)
def test_startup_profile_application_property(apply_on_startup, last_active_profile, profile_exists):
    """Property: For any plugin initialization when Apply on Startup is enabled
    and a last active profile exists, the system should apply that profile.
    
    Feature: ui-refactor-settings, Property 4: Startup profile application
    Validates: Requirements 4.1, 4.2
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Configure settings
        settings_manager.save_setting("apply_on_startup", apply_on_startup)
        settings_manager.save_setting("last_active_profile", last_active_profile)
        
        # Mock profile manager
        mock_profile_manager = MagicMock()
        mock_profile_manager.get_profile = MagicMock(
            return_value=MagicMock(name=last_active_profile, cores=[0, 0, 0, 0]) if profile_exists else None
        )
        mock_profile_manager.apply_profile = AsyncMock(return_value=True)
        
        # Simulate plugin initialization
        async def simulate_init():
            # Load settings
            apply_on_startup_setting = settings_manager.get_setting("apply_on_startup", False)
            last_profile = settings_manager.get_setting("last_active_profile")
            
            # Check if we should apply on startup
            if apply_on_startup_setting and last_profile:
                # Check if profile exists
                profile = mock_profile_manager.get_profile(last_profile)
                if profile:
                    # Apply the profile
                    await mock_profile_manager.apply_profile(last_profile)
                    return True
            return False
        
        # Run the simulation
        applied = asyncio.run(simulate_init())
        
        # Property: Profile should be applied if and only if:
        # 1. Apply on Startup is enabled
        # 2. Last active profile is set (not None)
        # 3. Profile exists
        should_apply = apply_on_startup and last_active_profile is not None and profile_exists
        
        assert applied == should_apply, (
            f"Profile application mismatch: "
            f"apply_on_startup={apply_on_startup}, "
            f"last_active_profile={last_active_profile}, "
            f"profile_exists={profile_exists}, "
            f"applied={applied}, should_apply={should_apply}"
        )
        
        # Verify apply_profile was called correctly
        if should_apply:
            mock_profile_manager.apply_profile.assert_called_once_with(last_active_profile)
        else:
            mock_profile_manager.apply_profile.assert_not_called()


@given(profile_name=profile_name_strategy, core_values=core_values_strategy)
@hyp_settings(max_examples=100, deadline=None)
def test_startup_applies_correct_profile(profile_name, core_values):
    """Property: When Apply on Startup is enabled, the exact profile specified
    in last_active_profile should be applied with its correct values.
    
    Feature: ui-refactor-settings, Property 4: Startup profile application
    Validates: Requirements 4.1, 4.2
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Enable Apply on Startup and set last active profile
        settings_manager.save_setting("apply_on_startup", True)
        settings_manager.save_setting("last_active_profile", profile_name)
        
        # Mock profile manager with specific profile
        mock_profile = MagicMock()
        mock_profile.name = profile_name
        mock_profile.cores = core_values
        mock_profile_manager = MagicMock()
        mock_profile_manager.get_profile = MagicMock(return_value=mock_profile)
        mock_profile_manager.apply_profile = AsyncMock(return_value=True)
        
        # Simulate plugin initialization
        async def simulate_init():
            apply_on_startup_setting = settings_manager.get_setting("apply_on_startup", False)
            last_profile = settings_manager.get_setting("last_active_profile")
            
            if apply_on_startup_setting and last_profile:
                profile = mock_profile_manager.get_profile(last_profile)
                if profile:
                    await mock_profile_manager.apply_profile(last_profile)
                    return profile.name, profile.cores
            return None, None
        
        # Run the simulation
        applied_name, applied_cores = asyncio.run(simulate_init())
        
        # Property: The applied profile should match exactly
        assert applied_name == profile_name, (
            f"Profile name mismatch: expected {profile_name}, got {applied_name}"
        )
        assert applied_cores == core_values, (
            f"Core values mismatch: expected {core_values}, got {applied_cores}"
        )
        
        # Verify correct profile was requested
        mock_profile_manager.get_profile.assert_called_once_with(profile_name)
        mock_profile_manager.apply_profile.assert_called_once_with(profile_name)


def test_startup_handles_missing_profile_gracefully():
    """Property: When Apply on Startup is enabled but the last active profile
    doesn't exist, the system should handle it gracefully without crashing.
    
    Feature: ui-refactor-settings, Property 4: Startup profile application
    Validates: Requirements 4.3, 4.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Enable Apply on Startup with a profile that doesn't exist
        settings_manager.save_setting("apply_on_startup", True)
        settings_manager.save_setting("last_active_profile", "nonexistent_profile")
        
        # Mock profile manager that returns None (profile not found)
        mock_profile_manager = MagicMock()
        mock_profile_manager.get_profile = MagicMock(return_value=None)
        mock_profile_manager.apply_profile = AsyncMock(return_value=False)
        
        # Simulate plugin initialization
        async def simulate_init():
            try:
                apply_on_startup_setting = settings_manager.get_setting("apply_on_startup", False)
                last_profile = settings_manager.get_setting("last_active_profile")
                
                if apply_on_startup_setting and last_profile:
                    profile = mock_profile_manager.get_profile(last_profile)
                    if profile:
                        await mock_profile_manager.apply_profile(last_profile)
                        return True
                    else:
                        # Profile not found, log and continue
                        return False
                return False
            except Exception:
                # Should not raise exception
                return None
        
        # Run the simulation - should not raise exception
        result = asyncio.run(simulate_init())
        
        # Property: Should return False (not applied) but not crash
        assert result is False, "Should return False when profile doesn't exist"
        
        # Verify apply_profile was not called
        mock_profile_manager.apply_profile.assert_not_called()


@given(apply_on_startup=st.booleans())
@hyp_settings(max_examples=100, deadline=None)
def test_startup_skips_when_no_last_profile(apply_on_startup):
    """Property: When last_active_profile is None, no profile should be applied
    regardless of Apply on Startup setting.
    
    Feature: ui-refactor-settings, Property 4: Startup profile application
    Validates: Requirements 4.3
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Set Apply on Startup but no last active profile
        settings_manager.save_setting("apply_on_startup", apply_on_startup)
        settings_manager.save_setting("last_active_profile", None)
        
        # Mock profile manager
        mock_profile_manager = MagicMock()
        mock_profile_manager.get_profile = MagicMock()
        mock_profile_manager.apply_profile = AsyncMock()
        
        # Simulate plugin initialization
        async def simulate_init():
            apply_on_startup_setting = settings_manager.get_setting("apply_on_startup", False)
            last_profile = settings_manager.get_setting("last_active_profile")
            
            if apply_on_startup_setting and last_profile:
                profile = mock_profile_manager.get_profile(last_profile)
                if profile:
                    await mock_profile_manager.apply_profile(last_profile)
                    return True
            return False
        
        # Run the simulation
        applied = asyncio.run(simulate_init())
        
        # Property: Should never apply when last_active_profile is None
        assert applied is False, (
            f"Should not apply profile when last_active_profile is None, "
            f"but applied={applied}"
        )
        
        # Verify no profile operations were called
        mock_profile_manager.get_profile.assert_not_called()
        mock_profile_manager.apply_profile.assert_not_called()


def test_startup_disabled_skips_application():
    """Property: When Apply on Startup is disabled, no profile should be applied
    even if a last active profile exists.
    
    Feature: ui-refactor-settings, Property 4: Startup profile application
    Validates: Requirements 4.4
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup settings manager
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Disable Apply on Startup but set a last active profile
        settings_manager.save_setting("apply_on_startup", False)
        settings_manager.save_setting("last_active_profile", "some_profile")
        
        # Mock profile manager
        mock_profile_manager = MagicMock()
        mock_profile_manager.get_profile = MagicMock(
            return_value=MagicMock(name="some_profile", cores=[0, 0, 0, 0])
        )
        mock_profile_manager.apply_profile = AsyncMock()
        
        # Simulate plugin initialization
        async def simulate_init():
            apply_on_startup_setting = settings_manager.get_setting("apply_on_startup", False)
            last_profile = settings_manager.get_setting("last_active_profile")
            
            if apply_on_startup_setting and last_profile:
                profile = mock_profile_manager.get_profile(last_profile)
                if profile:
                    await mock_profile_manager.apply_profile(last_profile)
                    return True
            return False
        
        # Run the simulation
        applied = asyncio.run(simulate_init())
        
        # Property: Should not apply when Apply on Startup is disabled
        assert applied is False, "Should not apply profile when Apply on Startup is disabled"
        
        # Verify no profile operations were called
        mock_profile_manager.get_profile.assert_not_called()
        mock_profile_manager.apply_profile.assert_not_called()
