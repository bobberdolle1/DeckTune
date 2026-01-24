"""Property-based tests for Manual Dynamic Mode RPC curve data consistency.

Feature: manual-dynamic-mode, Property 21: RPC curve data consistency
Validates: Requirements 9.3

This test verifies that the curve data returned by get_dynamic_curve_data
matches the voltage curve calculation formula from the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.dynamic.manual_manager import DynamicManager
from backend.dynamic.manual_validator import Validator
from backend.dynamic.rpc import DynamicModeRPC


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.storage = {}
    
    def setSetting(self, key, value):
        """Set a setting value."""
        self.storage[key] = value
    
    def getSetting(self, key, default=None):
        """Get a setting value."""
        return self.storage.get(key, default)


def create_rpc_handler():
    """Create RPC handler for testing."""
    manager = DynamicManager()
    validator = Validator()
    settings = MockSettingsManager()
    
    rpc = DynamicModeRPC(
        manager=manager,
        validator=validator,
        settings_manager=settings
    )
    
    return rpc


def calculate_expected_voltage(load: float, min_mv: int, max_mv: int, threshold: float) -> int:
    """Calculate expected voltage for a given load using the design formula.
    
    From design document:
    voltage(load) = {
      min_mv                                    if load <= threshold
      min_mv + (max_mv - min_mv) * 
        (load - threshold) / (100 - threshold)  if load > threshold
    }
    """
    if load <= threshold:
        return min_mv
    else:
        if threshold >= 100:
            return max_mv
        
        progress = (load - threshold) / (100 - threshold)
        voltage = min_mv + (max_mv - min_mv) * progress
        return int(round(voltage))


# Strategy for generating valid core configurations
@st.composite
def valid_core_config(draw):
    """Generate a valid core configuration."""
    core_id = draw(st.integers(min_value=0, max_value=3))
    
    # Generate min and max such that min <= max (both in range -100 to 0)
    min_mv = draw(st.integers(min_value=-100, max_value=0))
    max_mv = draw(st.integers(min_value=min_mv, max_value=0))
    
    threshold = draw(st.floats(min_value=0.0, max_value=100.0))
    
    return {
        "core_id": core_id,
        "min_mv": min_mv,
        "max_mv": max_mv,
        "threshold": threshold
    }


@given(config=valid_core_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_curve_data_consistency(config):
    """
    **Feature: manual-dynamic-mode, Property 21: RPC curve data consistency**
    **Validates: Requirements 9.3**
    
    For any core configuration, the curve data returned by get_dynamic_curve_data
    SHALL match the voltage curve calculation formula.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set the configuration
    set_result = await rpc_handler.set_dynamic_core_config(
        core_id=config["core_id"],
        min_mv=config["min_mv"],
        max_mv=config["max_mv"],
        threshold=config["threshold"]
    )
    
    assert set_result["success"], f"Set operation failed: {set_result.get('error')}"
    
    # Get clamped values
    clamped_min = set_result.get("clamped", {}).get("min_mv", config["min_mv"])
    clamped_max = set_result.get("clamped", {}).get("max_mv", config["max_mv"])
    
    # Get the curve data
    curve_result = await rpc_handler.get_dynamic_curve_data(config["core_id"])
    
    assert curve_result["success"], f"Get curve data failed: {curve_result.get('error')}"
    
    curve_points = curve_result["curve_points"]
    
    # Verify we have 101 points (load 0-100)
    assert len(curve_points) == 101, \
        f"Expected 101 curve points, got {len(curve_points)}"
    
    # Verify each point matches the expected calculation
    for point in curve_points:
        load = point["load"]
        actual_voltage = point["voltage"]
        
        expected_voltage = calculate_expected_voltage(
            load, clamped_min, clamped_max, config["threshold"]
        )
        
        assert actual_voltage == expected_voltage, \
            f"Voltage mismatch at load {load}: expected {expected_voltage}, got {actual_voltage}"


@given(config=valid_core_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_curve_below_threshold(config):
    """
    **Feature: manual-dynamic-mode, Property 21: RPC curve data consistency**
    **Validates: Requirements 9.3, 2.4**
    
    For any core configuration, all curve points where load <= threshold
    SHALL have voltage equal to min_mv.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set the configuration
    set_result = await rpc_handler.set_dynamic_core_config(
        core_id=config["core_id"],
        min_mv=config["min_mv"],
        max_mv=config["max_mv"],
        threshold=config["threshold"]
    )
    
    assert set_result["success"]
    
    # Get clamped min value
    clamped_min = set_result.get("clamped", {}).get("min_mv", config["min_mv"])
    
    # Get the curve data
    curve_result = await rpc_handler.get_dynamic_curve_data(config["core_id"])
    assert curve_result["success"]
    
    curve_points = curve_result["curve_points"]
    
    # Check all points below or at threshold
    for point in curve_points:
        if point["load"] <= config["threshold"]:
            assert point["voltage"] == clamped_min, \
                f"At load {point['load']} (<= threshold {config['threshold']}), " \
                f"expected voltage {clamped_min}, got {point['voltage']}"


@given(config=valid_core_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_curve_above_threshold(config):
    """
    **Feature: manual-dynamic-mode, Property 21: RPC curve data consistency**
    **Validates: Requirements 9.3, 2.5**
    
    For any core configuration, all curve points where load > threshold
    SHALL follow the linear interpolation formula.
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set the configuration
    set_result = await rpc_handler.set_dynamic_core_config(
        core_id=config["core_id"],
        min_mv=config["min_mv"],
        max_mv=config["max_mv"],
        threshold=config["threshold"]
    )
    
    assert set_result["success"]
    
    # Get clamped values
    clamped_min = set_result.get("clamped", {}).get("min_mv", config["min_mv"])
    clamped_max = set_result.get("clamped", {}).get("max_mv", config["max_mv"])
    
    # Get the curve data
    curve_result = await rpc_handler.get_dynamic_curve_data(config["core_id"])
    assert curve_result["success"]
    
    curve_points = curve_result["curve_points"]
    
    # Check all points above threshold
    for point in curve_points:
        if point["load"] > config["threshold"]:
            expected = calculate_expected_voltage(
                point["load"], clamped_min, clamped_max, config["threshold"]
            )
            
            assert point["voltage"] == expected, \
                f"At load {point['load']} (> threshold {config['threshold']}), " \
                f"expected voltage {expected}, got {point['voltage']}"


@given(config=valid_core_config())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_rpc_curve_monotonic(config):
    """
    **Feature: manual-dynamic-mode, Property 21: RPC curve data consistency**
    **Validates: Requirements 9.3**
    
    For any core configuration where min_mv <= max_mv, the voltage curve
    SHALL be monotonically non-decreasing (voltage increases or stays same as load increases).
    """
    # Create fresh RPC handler for this test
    rpc_handler = create_rpc_handler()
    
    # Set the configuration
    set_result = await rpc_handler.set_dynamic_core_config(
        core_id=config["core_id"],
        min_mv=config["min_mv"],
        max_mv=config["max_mv"],
        threshold=config["threshold"]
    )
    
    assert set_result["success"]
    
    # Get the curve data
    curve_result = await rpc_handler.get_dynamic_curve_data(config["core_id"])
    assert curve_result["success"]
    
    curve_points = curve_result["curve_points"]
    
    # Check monotonicity
    for i in range(len(curve_points) - 1):
        current_voltage = curve_points[i]["voltage"]
        next_voltage = curve_points[i + 1]["voltage"]
        
        assert next_voltage >= current_voltage, \
            f"Curve is not monotonic: voltage decreased from {current_voltage} " \
            f"to {next_voltage} between load {curve_points[i]['load']} and {curve_points[i+1]['load']}"
