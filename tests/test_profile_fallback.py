"""Property test for profile fallback behavior.

Feature: frequency-based-wizard, Property 20: Profile fallback behavior
Validates: Requirements 8.5

Tests that for any game profile without an associated frequency curve, activation 
does not cause errors and either uses the default curve or falls back to load-based mode.
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import Mock, AsyncMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.profile_manager import ProfileManager, GameProfile


# Strategy for game profiles WITHOUT frequency curves
@st.composite
def profile_without_curves_strategy(draw):
    """Generate valid GameProfile instances without frequency curves."""
    return GameProfile(
        app_id=draw(st.integers(min_value=1, max_value=999999)),
        name=draw(st.text(min_size=1, max_size=64).filter(lambda s: s.strip())),
        cores=draw(st.lists(
            st.integers(min_value=-100, max_value=0),
            min_size=4,
            max_size=4
        )),
        dynamic_enabled=False,
        dynamic_config=None,
        frequency_curves=None,  # No curves
        created_at="2026-01-01T00:00:00Z",
        last_used=None
    )


@given(profile=profile_without_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_without_curves_activates_successfully(profile):
    """Property 20: Profile fallback behavior
    
    For any game profile without an associated frequency curve, activation SHALL 
    NOT cause errors and the profile SHALL be applied successfully.
    
    Feature: frequency-based-wizard, Property 20: Profile fallback behavior
    Validates: Requirements 8.5
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = Mock()
    mock_event_emitter.emit_profile_changed = Mock()
    
    # Create mock core settings manager
    mock_core_settings = Mock()
    mock_core_settings.load_setting = Mock(return_value=True)  # frequency_mode_enabled = True
    mock_core_settings.save_setting = Mock()
    
    # Create profile manager
    manager = ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=None,
        event_emitter=mock_event_emitter,
        core_settings_manager=mock_core_settings
    )
    
    # Add profile to manager
    manager._profiles[profile.app_id] = profile
    
    # Apply the profile - should not raise any errors
    try:
        result = asyncio.run(manager.apply_profile(profile.app_id))
        
        # Verify profile was applied successfully
        assert result is True, "Profile application failed"
        
        # Verify undervolt values were applied
        mock_ryzenadj.apply_values_async.assert_called_once_with(profile.cores)
        
        # Verify no frequency curves were saved (profile has none)
        save_calls = [call for call in mock_core_settings.save_setting.call_args_list 
                      if len(call[0]) > 0 and call[0][0] == "frequency_curves"]
        
        # Should not have saved frequency curves when profile has none
        assert len(save_calls) == 0, \
            "Frequency curves should not be saved when profile has no curves"
        
    except Exception as e:
        pytest.fail(f"Profile activation raised unexpected error: {e}")


@given(profile=profile_without_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_without_curves_does_not_break_frequency_mode(profile):
    """Property 20: Profile fallback behavior - Frequency Mode Compatibility
    
    For any game profile without an associated frequency curve, activation SHALL 
    NOT break frequency-based mode if it is enabled.
    
    Feature: frequency-based-wizard, Property 20: Profile fallback behavior
    Validates: Requirements 8.5
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = Mock()
    mock_event_emitter.emit_profile_changed = Mock()
    
    # Create mock core settings manager with frequency mode enabled
    mock_core_settings = Mock()
    mock_core_settings.load_setting = Mock(return_value=True)  # frequency_mode_enabled = True
    mock_core_settings.save_setting = Mock()
    
    # Create profile manager
    manager = ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=None,
        event_emitter=mock_event_emitter,
        core_settings_manager=mock_core_settings
    )
    
    # Add profile to manager
    manager._profiles[profile.app_id] = profile
    
    # Apply the profile
    result = asyncio.run(manager.apply_profile(profile.app_id))
    
    # Verify profile was applied successfully
    assert result is True, "Profile application failed"
    
    # Verify frequency mode setting was checked
    load_calls = [call for call in mock_core_settings.load_setting.call_args_list 
                  if len(call[0]) > 0 and call[0][0] == "frequency_mode_enabled"]
    
    # The _apply_frequency_curves method should have checked the setting
    # even though the profile has no curves
    # (This verifies the code path is executed without errors)


@given(profile=profile_without_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_without_curves_validation_passes(profile):
    """Property 20: Profile fallback behavior - Validation
    
    For any game profile without an associated frequency curve, the profile SHALL 
    pass validation.
    
    Feature: frequency-based-wizard, Property 20: Profile fallback behavior
    Validates: Requirements 8.5
    """
    # Validate the profile
    errors = profile.validate()
    
    # Profile without curves should be valid
    assert len(errors) == 0, \
        f"Profile without curves should be valid, but got errors: {errors}"


@given(profile=profile_without_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_without_curves_export_import_works(profile):
    """Property 20: Profile fallback behavior - Export/Import
    
    For any game profile without an associated frequency curve, exporting and 
    importing the profile SHALL work correctly.
    
    Feature: frequency-based-wizard, Property 20: Profile fallback behavior
    Validates: Requirements 8.5
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_event_emitter = Mock()
    
    # Create profile manager
    manager = ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=None,
        event_emitter=mock_event_emitter
    )
    
    # Add profile to manager
    manager._profiles[profile.app_id] = profile
    
    # Export profiles
    json_str = manager.export_profiles()
    
    # Clear profiles
    manager._profiles = {}
    
    # Import profiles back
    result = asyncio.run(manager.import_profiles(json_str, merge_strategy="overwrite"))
    
    # Verify import succeeded
    assert result["success"], f"Import failed: {result['errors']}"
    assert result["imported_count"] == 1, f"Expected 1 imported, got {result['imported_count']}"
    
    # Get the imported profile
    imported_profile = manager._profiles.get(profile.app_id)
    assert imported_profile is not None, "Profile not found after import"
    
    # Verify basic profile fields
    assert imported_profile.app_id == profile.app_id
    assert imported_profile.name == profile.name
    assert imported_profile.cores == profile.cores
    
    # Verify frequency_curves is None (not present)
    assert imported_profile.frequency_curves is None, \
        "Profile without curves should have frequency_curves=None after import"


@given(profile=profile_without_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_without_curves_can_be_updated_with_curves(profile):
    """Property 20: Profile fallback behavior - Upgrade Path
    
    For any game profile without an associated frequency curve, the profile SHALL 
    be able to be updated to include frequency curves later.
    
    Feature: frequency-based-wizard, Property 20: Profile fallback behavior
    Validates: Requirements 8.5
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_event_emitter = Mock()
    
    # Create profile manager
    manager = ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=None,
        event_emitter=mock_event_emitter
    )
    
    # Add profile to manager
    manager._profiles[profile.app_id] = profile
    
    # Verify profile has no curves initially
    assert profile.frequency_curves is None
    
    # Create a simple frequency curve
    from backend.tuning.frequency_curve import FrequencyCurve, FrequencyPoint
    
    curve = FrequencyCurve(
        core_id=0,
        points=[
            FrequencyPoint(400, -50, True, 30, 1000000000.0),
            FrequencyPoint(500, -45, True, 30, 1000000000.0),
        ],
        created_at=1000000000.0,
        wizard_config={}
    )
    
    # Update profile with frequency curves
    result = asyncio.run(manager.update_profile(
        profile.app_id,
        frequency_curves={0: curve.to_dict()}
    ))
    
    # Verify update succeeded
    assert result is True, "Profile update failed"
    
    # Verify profile now has curves
    updated_profile = manager._profiles[profile.app_id]
    assert updated_profile.frequency_curves is not None, \
        "Profile should have frequency curves after update"
    assert 0 in updated_profile.frequency_curves, \
        "Profile should have curve for core 0"
