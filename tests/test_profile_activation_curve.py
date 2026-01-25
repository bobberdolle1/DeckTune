"""Property test for profile activation curve application.

Feature: frequency-based-wizard, Property 19: Profile activation curve application
Validates: Requirements 8.2

Tests that for any game profile with an associated frequency curve, when the 
profile activates and frequency-based mode is enabled, the system applies that 
profile's frequency curve.
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import Mock, AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.profile_manager import ProfileManager, GameProfile
from backend.tuning.frequency_curve import FrequencyCurve, FrequencyPoint


# Strategy for valid frequency curves
@st.composite
def frequency_curve_strategy(draw):
    """Generate valid FrequencyCurve instances with sorted points."""
    core_id = draw(st.integers(min_value=0, max_value=3))
    
    # Generate 2-5 points
    num_points = draw(st.integers(min_value=2, max_value=5))
    
    # Generate unique frequencies and sort them
    frequencies = draw(st.lists(
        st.integers(min_value=400, max_value=3500),
        min_size=num_points,
        max_size=num_points,
        unique=True
    ))
    frequencies.sort()
    
    # Create points with sorted frequencies
    points = []
    for freq in frequencies:
        point = FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=draw(st.integers(min_value=-100, max_value=0)),
            stable=True,
            test_duration=30,
            timestamp=1000000000.0
        )
        points.append(point)
    
    return FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=1000000000.0,
        wizard_config={}
    )


# Strategy for game profiles with frequency curves
@st.composite
def profile_with_curves_strategy(draw):
    """Generate valid GameProfile instances with frequency curves."""
    # Generate 1-2 curves for different cores
    num_cores = draw(st.integers(min_value=1, max_value=2))
    core_ids = draw(st.lists(
        st.integers(min_value=0, max_value=3),
        min_size=num_cores,
        max_size=num_cores,
        unique=True
    ))
    
    frequency_curves = {}
    for core_id in core_ids:
        curve = draw(frequency_curve_strategy())
        curve.core_id = core_id  # Ensure core_id matches
        frequency_curves[core_id] = curve.to_dict()
    
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
        frequency_curves=frequency_curves,
        created_at="2026-01-01T00:00:00Z",
        last_used=None
    )


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_activation_applies_frequency_curves(profile):
    """Property 19: Profile activation curve application
    
    For any game profile with an associated frequency curve, when the profile 
    activates and frequency-based mode is enabled, the system SHALL apply that 
    profile's frequency curve.
    
    Feature: frequency-based-wizard, Property 19: Profile activation curve application
    Validates: Requirements 8.2
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
    
    # Apply the profile
    result = asyncio.run(manager.apply_profile(profile.app_id))
    
    # Verify profile was applied successfully
    assert result is True, "Profile application failed"
    
    # Verify undervolt values were applied
    mock_ryzenadj.apply_values_async.assert_called_once_with(profile.cores)
    
    # Verify frequency curves were saved to settings
    # The _apply_frequency_curves method should save curves to settings
    save_calls = [call for call in mock_core_settings.save_setting.call_args_list 
                  if len(call[0]) > 0 and call[0][0] == "frequency_curves"]
    
    if profile.frequency_curves:
        # Should have called save_setting with frequency_curves
        assert len(save_calls) > 0, \
            "Frequency curves were not saved to settings during profile activation"
        
        # Verify the saved curves match the profile's curves
        saved_curves = save_calls[0][0][1]
        assert saved_curves is not None, "Saved curves should not be None"
        
        # Verify all curves from profile are in saved curves
        for core_id in profile.frequency_curves.keys():
            core_id_str = str(core_id)
            assert core_id_str in saved_curves, \
                f"Core {core_id} curve not found in saved curves"


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_activation_skips_curves_when_mode_disabled(profile):
    """Property 19: Profile activation curve application - Mode Disabled
    
    For any game profile with an associated frequency curve, when the profile 
    activates but frequency-based mode is DISABLED, the system SHALL NOT apply 
    the frequency curve.
    
    Feature: frequency-based-wizard, Property 19: Profile activation curve application
    Validates: Requirements 8.2
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = Mock()
    mock_event_emitter.emit_profile_changed = Mock()
    
    # Create mock core settings manager with frequency mode DISABLED
    mock_core_settings = Mock()
    mock_core_settings.load_setting = Mock(return_value=False)  # frequency_mode_enabled = False
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
    
    # Verify undervolt values were applied
    mock_ryzenadj.apply_values_async.assert_called_once_with(profile.cores)
    
    # Verify frequency curves were NOT saved (mode is disabled)
    save_calls = [call for call in mock_core_settings.save_setting.call_args_list 
                  if len(call[0]) > 0 and call[0][0] == "frequency_curves"]
    
    # Should not have saved frequency curves when mode is disabled
    assert len(save_calls) == 0, \
        "Frequency curves should not be saved when frequency mode is disabled"


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_activation_validates_curves_before_applying(profile):
    """Property 19: Profile activation curve application - Validation
    
    For any game profile with an associated frequency curve, when the profile 
    activates, the system SHALL validate the curve before applying it.
    
    Feature: frequency-based-wizard, Property 19: Profile activation curve application
    Validates: Requirements 8.2
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
    
    # Apply the profile
    result = asyncio.run(manager.apply_profile(profile.app_id))
    
    # Verify profile was applied successfully
    assert result is True, "Profile application failed"
    
    # If curves were applied, they should be valid
    if profile.frequency_curves:
        save_calls = [call for call in mock_core_settings.save_setting.call_args_list 
                      if len(call[0]) > 0 and call[0][0] == "frequency_curves"]
        
        if len(save_calls) > 0:
            saved_curves = save_calls[0][0][1]
            
            # Verify each saved curve is valid
            for core_id_str, curve_data in saved_curves.items():
                # Should be able to deserialize and validate
                curve = FrequencyCurve.from_dict(curve_data)
                # validate() will raise ValueError if invalid
                assert curve.validate() is True, \
                    f"Saved curve for core {core_id_str} failed validation"
