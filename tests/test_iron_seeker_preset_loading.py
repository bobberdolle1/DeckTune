"""Property-based tests for Iron Seeker preset loading.

Feature: iron-seeker, Property 22: Preset loading
Validates: Requirements 8.3
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
import asyncio

from backend.tuning.iron_seeker import (
    IronSeekerPreset,
    load_iron_seeker_preset,
    load_iron_seeker_preset_sync,
)


# Strategy for generating valid quality tiers
tier_strategy = st.sampled_from(["gold", "silver", "bronze"])

# Strategy for generating valid undervolt values (0 to -100 mV)
undervolt_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid preset names
name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=1,
    max_size=64
).filter(lambda x: x.strip())

# Strategy for generating ISO timestamps
timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.isoformat())


def create_mock_ryzenadj(success: bool = True, error: str = None):
    """Create a mock RyzenadjWrapper for testing.
    
    Args:
        success: Whether apply_values should succeed
        error: Error message to return on failure
        
    Returns:
        Mock RyzenadjWrapper with apply_values and apply_values_async methods
    """
    mock = MagicMock()
    mock.apply_values = MagicMock(return_value=(success, error))
    mock.apply_values_async = AsyncMock(return_value=(success, error))
    return mock


@given(
    v0=undervolt_strategy,
    v1=undervolt_strategy,
    v2=undervolt_strategy,
    v3=undervolt_strategy,
    t0=tier_strategy,
    t1=tier_strategy,
    t2=tier_strategy,
    t3=tier_strategy,
    name=name_strategy,
    timestamp=timestamp_strategy
)
@settings(max_examples=100)
def test_property_22_preset_loading_sync(v0, v1, v2, v3, t0, t1, t2, t3, name, timestamp):
    """**Feature: iron-seeker, Property 22: Preset loading**
    
    For any per-core preset with values [V0, V1, V2, V3], loading the preset
    SHALL result in ryzenadj being called with those exact values.
    
    **Validates: Requirements 8.3**
    """
    values = [v0, v1, v2, v3]
    tiers = [t0, t1, t2, t3]
    
    preset = IronSeekerPreset(
        name=name,
        values=values,
        tiers=tiers,
        timestamp=timestamp
    )
    
    # Create mock ryzenadj
    mock_ryzenadj = create_mock_ryzenadj(success=True)
    
    # Load the preset
    success, error = load_iron_seeker_preset_sync(preset, mock_ryzenadj)
    
    # Verify success
    assert success is True, f"Preset loading should succeed, got error: {error}"
    assert error is None
    
    # Verify ryzenadj was called with exact values
    mock_ryzenadj.apply_values.assert_called_once_with(values)
    
    # Verify the exact values passed
    call_args = mock_ryzenadj.apply_values.call_args[0][0]
    assert call_args == values, f"ryzenadj should be called with {values}, got {call_args}"


@given(
    v0=undervolt_strategy,
    v1=undervolt_strategy,
    v2=undervolt_strategy,
    v3=undervolt_strategy,
    t0=tier_strategy,
    t1=tier_strategy,
    t2=tier_strategy,
    t3=tier_strategy,
    name=name_strategy,
    timestamp=timestamp_strategy
)
@settings(max_examples=100)
def test_property_22_preset_loading_async(v0, v1, v2, v3, t0, t1, t2, t3, name, timestamp):
    """**Feature: iron-seeker, Property 22: Preset loading (async)**
    
    For any per-core preset with values [V0, V1, V2, V3], loading the preset
    SHALL result in ryzenadj being called with those exact values.
    
    **Validates: Requirements 8.3**
    """
    values = [v0, v1, v2, v3]
    tiers = [t0, t1, t2, t3]
    
    preset = IronSeekerPreset(
        name=name,
        values=values,
        tiers=tiers,
        timestamp=timestamp
    )
    
    # Create mock ryzenadj
    mock_ryzenadj = create_mock_ryzenadj(success=True)
    
    # Load the preset (async)
    async def run_test():
        return await load_iron_seeker_preset(preset, mock_ryzenadj)
    
    success, error = asyncio.run(run_test())
    
    # Verify success
    assert success is True, f"Preset loading should succeed, got error: {error}"
    assert error is None
    
    # Verify ryzenadj was called with exact values
    mock_ryzenadj.apply_values_async.assert_called_once_with(values)
    
    # Verify the exact values passed
    call_args = mock_ryzenadj.apply_values_async.call_args[0][0]
    assert call_args == values, f"ryzenadj should be called with {values}, got {call_args}"


@given(
    v0=undervolt_strategy,
    v1=undervolt_strategy,
    v2=undervolt_strategy,
    v3=undervolt_strategy,
    t0=tier_strategy,
    t1=tier_strategy,
    t2=tier_strategy,
    t3=tier_strategy,
    name=name_strategy,
    timestamp=timestamp_strategy,
    error_msg=st.text(min_size=1, max_size=100)
)
@settings(max_examples=50)
def test_preset_loading_propagates_ryzenadj_errors(
    v0, v1, v2, v3, t0, t1, t2, t3, name, timestamp, error_msg
):
    """Test that preset loading propagates ryzenadj errors.
    
    When ryzenadj fails, the error should be propagated to the caller.
    
    **Validates: Requirements 8.3**
    """
    values = [v0, v1, v2, v3]
    tiers = [t0, t1, t2, t3]
    
    preset = IronSeekerPreset(
        name=name,
        values=values,
        tiers=tiers,
        timestamp=timestamp
    )
    
    # Create mock ryzenadj that fails
    mock_ryzenadj = create_mock_ryzenadj(success=False, error=error_msg)
    
    # Load the preset
    success, error = load_iron_seeker_preset_sync(preset, mock_ryzenadj)
    
    # Verify failure is propagated
    assert success is False
    assert error == error_msg


def test_preset_loading_validates_before_apply():
    """Test that preset loading validates the preset before applying.
    
    Invalid presets should be rejected without calling ryzenadj.
    """
    # Create a valid preset first
    preset = IronSeekerPreset(
        name="Test",
        values=[-30, -30, -30, -30],
        tiers=["gold", "gold", "gold", "gold"],
        timestamp="2026-01-16T12:00:00"
    )
    
    # Manually invalidate it
    preset.name = ""  # Empty name is invalid
    
    mock_ryzenadj = create_mock_ryzenadj(success=True)
    
    # Load should fail validation
    success, error = load_iron_seeker_preset_sync(preset, mock_ryzenadj)
    
    assert success is False
    assert "Invalid preset" in error
    
    # ryzenadj should NOT have been called
    mock_ryzenadj.apply_values.assert_not_called()


def test_preset_loading_validates_value_range():
    """Test that preset loading validates value ranges before applying."""
    preset = IronSeekerPreset(
        name="Test",
        values=[-30, -30, -30, -30],
        tiers=["gold", "gold", "gold", "gold"],
        timestamp="2026-01-16T12:00:00"
    )
    
    # Manually set invalid value (positive)
    preset.values[0] = 10
    
    mock_ryzenadj = create_mock_ryzenadj(success=True)
    
    # Load should fail validation
    success, error = load_iron_seeker_preset_sync(preset, mock_ryzenadj)
    
    assert success is False
    assert "Invalid preset" in error
    
    # ryzenadj should NOT have been called
    mock_ryzenadj.apply_values.assert_not_called()


@pytest.mark.asyncio
async def test_preset_loading_async_validates_before_apply():
    """Test that async preset loading validates the preset before applying."""
    preset = IronSeekerPreset(
        name="Test",
        values=[-30, -30, -30, -30],
        tiers=["gold", "gold", "gold", "gold"],
        timestamp="2026-01-16T12:00:00"
    )
    
    # Manually invalidate it
    preset.name = ""
    
    mock_ryzenadj = create_mock_ryzenadj(success=True)
    
    # Load should fail validation
    success, error = await load_iron_seeker_preset(preset, mock_ryzenadj)
    
    assert success is False
    assert "Invalid preset" in error
    
    # ryzenadj should NOT have been called
    mock_ryzenadj.apply_values_async.assert_not_called()
