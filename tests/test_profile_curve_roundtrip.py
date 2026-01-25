"""Property test for profile frequency curve round-trip preservation.

Feature: frequency-based-wizard, Property 12: Profile curve round-trip preservation
Validates: Requirements 8.3, 8.4

Tests that for any valid GameProfile with frequency curves, exporting and then 
importing the profile preserves the frequency curve with identical frequency 
points and voltages.
"""

import pytest
import json
from hypothesis import given, strategies as st, settings as hyp_settings
from unittest.mock import Mock, AsyncMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.profile_manager import ProfileManager, GameProfile
from backend.tuning.frequency_curve import FrequencyCurve, FrequencyPoint


# Strategy for valid frequency points
@st.composite
def frequency_point_strategy(draw):
    """Generate valid FrequencyPoint instances."""
    return FrequencyPoint(
        frequency_mhz=draw(st.integers(min_value=400, max_value=3500)),
        voltage_mv=draw(st.integers(min_value=-100, max_value=0)),
        stable=draw(st.booleans()),
        test_duration=draw(st.integers(min_value=10, max_value=120)),
        timestamp=draw(st.floats(min_value=1000000000.0, max_value=2000000000.0))
    )


# Strategy for valid frequency curves
@st.composite
def frequency_curve_strategy(draw):
    """Generate valid FrequencyCurve instances with sorted points."""
    core_id = draw(st.integers(min_value=0, max_value=3))
    
    # Generate 2-10 points
    num_points = draw(st.integers(min_value=2, max_value=10))
    
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
            stable=draw(st.booleans()),
            test_duration=draw(st.integers(min_value=10, max_value=120)),
            timestamp=draw(st.floats(min_value=1000000000.0, max_value=2000000000.0))
        )
        points.append(point)
    
    return FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=draw(st.floats(min_value=1000000000.0, max_value=2000000000.0)),
        wizard_config={}
    )


# Strategy for game profiles with frequency curves
@st.composite
def profile_with_curves_strategy(draw):
    """Generate valid GameProfile instances with frequency curves."""
    # Generate 1-4 curves for different cores
    num_cores = draw(st.integers(min_value=1, max_value=4))
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
    
    # Generate dynamic_enabled and ensure dynamic_config is set if enabled
    dynamic_enabled = draw(st.booleans())
    dynamic_config = {"strategy": "balanced"} if dynamic_enabled else None
    
    return GameProfile(
        app_id=draw(st.integers(min_value=1, max_value=999999)),
        name=draw(st.text(min_size=1, max_size=64).filter(lambda s: s.strip())),
        cores=draw(st.lists(
            st.integers(min_value=-100, max_value=0),
            min_size=4,
            max_size=4
        )),
        dynamic_enabled=dynamic_enabled,
        dynamic_config=dynamic_config,
        frequency_curves=frequency_curves,
        created_at="2026-01-01T00:00:00Z",
        last_used=None
    )


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_curve_export_import_roundtrip(profile):
    """Property 12: Profile curve round-trip preservation
    
    For any valid GameProfile with frequency curves, exporting and then importing
    the profile SHALL preserve the frequency curve with identical frequency points
    and voltages.
    
    Feature: frequency-based-wizard, Property 12: Profile curve round-trip preservation
    Validates: Requirements 8.3, 8.4
    """
    # Create mock dependencies
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_event_emitter = Mock()
    mock_event_emitter.emit_profile_changed = Mock()
    
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
    import asyncio
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
    
    # Verify frequency curves are preserved
    if profile.frequency_curves:
        assert imported_profile.frequency_curves is not None, \
            "Frequency curves missing after import"
        
        assert len(imported_profile.frequency_curves) == len(profile.frequency_curves), \
            f"Curve count mismatch: {len(profile.frequency_curves)} -> {len(imported_profile.frequency_curves)}"
        
        # Verify each curve
        for core_id, orig_curve_data in profile.frequency_curves.items():
            # JSON serialization converts integer keys to strings
            core_id_str = str(core_id)
            assert core_id_str in imported_profile.frequency_curves, \
                f"Core {core_id} curve missing after import"
            
            imp_curve_data = imported_profile.frequency_curves[core_id_str]
            
            # Deserialize curves for comparison
            orig_curve = FrequencyCurve.from_dict(orig_curve_data)
            imp_curve = FrequencyCurve.from_dict(imp_curve_data)
            
            # Verify curve properties
            assert imp_curve.core_id == orig_curve.core_id, \
                f"Core ID mismatch: {orig_curve.core_id} -> {imp_curve.core_id}"
            
            assert len(imp_curve.points) == len(orig_curve.points), \
                f"Point count mismatch for core {core_id}: {len(orig_curve.points)} -> {len(imp_curve.points)}"
            
            # Verify each point
            for i, (orig_point, imp_point) in enumerate(zip(orig_curve.points, imp_curve.points)):
                assert imp_point.frequency_mhz == orig_point.frequency_mhz, \
                    f"Core {core_id} point {i} frequency mismatch: {orig_point.frequency_mhz} -> {imp_point.frequency_mhz}"
                
                assert imp_point.voltage_mv == orig_point.voltage_mv, \
                    f"Core {core_id} point {i} voltage mismatch: {orig_point.voltage_mv} -> {imp_point.voltage_mv}"
                
                assert imp_point.stable == orig_point.stable, \
                    f"Core {core_id} point {i} stable mismatch: {orig_point.stable} -> {imp_point.stable}"


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_curve_validation_after_roundtrip(profile):
    """Property 12: Profile curve round-trip preservation - Validation
    
    For any valid GameProfile with frequency curves, after export/import round-trip
    the profile SHALL still pass validation including curve validation.
    
    Feature: frequency-based-wizard, Property 12: Profile curve round-trip preservation
    Validates: Requirements 8.3, 8.4
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
    
    # Export and import
    json_str = manager.export_profiles()
    manager._profiles = {}
    
    import asyncio
    result = asyncio.run(manager.import_profiles(json_str, merge_strategy="overwrite"))
    
    # Get imported profile
    imported_profile = manager._profiles.get(profile.app_id)
    assert imported_profile is not None
    
    # Both should be valid
    original_errors = profile.validate()
    imported_errors = imported_profile.validate()
    
    assert len(original_errors) == 0, \
        f"Original profile invalid: {original_errors}"
    
    assert len(imported_errors) == 0, \
        f"Imported profile invalid: {imported_errors}"


@given(profile=profile_with_curves_strategy())
@hyp_settings(max_examples=100)
def test_profile_curve_serialization_preserves_interpolation(profile):
    """Property 12: Profile curve round-trip preservation - Interpolation
    
    For any valid GameProfile with frequency curves, after export/import round-trip
    the curve SHALL produce identical interpolated voltages for any frequency.
    
    Feature: frequency-based-wizard, Property 12: Profile curve round-trip preservation
    Validates: Requirements 8.3, 8.4
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
    
    # Export and import
    json_str = manager.export_profiles()
    manager._profiles = {}
    
    import asyncio
    result = asyncio.run(manager.import_profiles(json_str, merge_strategy="overwrite"))
    
    # Get imported profile
    imported_profile = manager._profiles.get(profile.app_id)
    assert imported_profile is not None
    
    # Test interpolation for each curve
    if profile.frequency_curves:
        for core_id, orig_curve_data in profile.frequency_curves.items():
            # JSON serialization converts integer keys to strings
            core_id_str = str(core_id)
            imp_curve_data = imported_profile.frequency_curves[core_id_str]
            
            orig_curve = FrequencyCurve.from_dict(orig_curve_data)
            imp_curve = FrequencyCurve.from_dict(imp_curve_data)
            
            # Test interpolation at various frequencies
            min_freq = orig_curve.points[0].frequency_mhz
            max_freq = orig_curve.points[-1].frequency_mhz
            
            # Test at boundaries and midpoints
            test_frequencies = [
                min_freq,
                max_freq,
                (min_freq + max_freq) // 2,
            ]
            
            for freq in test_frequencies:
                orig_voltage = orig_curve.get_voltage_for_frequency(freq)
                imp_voltage = imp_curve.get_voltage_for_frequency(freq)
                
                assert orig_voltage == imp_voltage, \
                    f"Core {core_id} interpolation mismatch at {freq} MHz: {orig_voltage} -> {imp_voltage}"
