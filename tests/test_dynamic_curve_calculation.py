"""Property tests for Manual Dynamic Mode voltage curve calculation.

Feature: manual-dynamic-mode, Property 2: Voltage curve calculation below threshold
Feature: manual-dynamic-mode, Property 3: Voltage curve calculation above threshold
Validates: Requirements 2.4, 2.5

Property 2: Voltage curve calculation below threshold
For any core configuration, all curve points where CPULoad is less than or 
equal to Threshold SHALL have VoltageOffset equal to MinimalValue.

Property 3: Voltage curve calculation above threshold
For any core configuration, all curve points where CPULoad is greater than 
Threshold SHALL have VoltageOffset calculated as: 
min_mv + (max_mv - min_mv) * (load - threshold) / (100 - threshold).
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.dynamic.manual_manager import DynamicManager, CoreConfig


# Strategies for voltage values (valid range)
valid_voltage = st.integers(min_value=-100, max_value=0)

# Strategy for threshold values (valid range)
valid_threshold = st.floats(min_value=0.0, max_value=100.0)

# Strategy for core IDs
core_id = st.integers(min_value=0, max_value=3)

# Strategy for CPU load values
cpu_load = st.integers(min_value=0, max_value=100)


class TestVoltageCurveCalculationBelowThreshold:
    """Property 2: Voltage curve calculation below threshold
    
    For any core configuration, all curve points where CPULoad is less than or 
    equal to Threshold SHALL have VoltageOffset equal to MinimalValue.
    
    Validates: Requirements 2.4
    """

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=valid_threshold
    )
    @settings(max_examples=100)
    def test_curve_points_below_threshold_equal_min_mv(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """All curve points at or below threshold SHALL equal min_mv."""
        # Skip invalid configurations (min > max)
        if min_mv > max_mv:
            return
        
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # Check all points at or below threshold
        for point in curve_points:
            if point.load <= threshold:
                assert point.voltage == min_mv, (
                    f"Curve point at load {point.load} (threshold={threshold}) "
                    f"should have voltage {min_mv}, got {point.voltage}"
                )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=valid_threshold,
        load=cpu_load
    )
    @settings(max_examples=100)
    def test_calculate_voltage_below_threshold_returns_min_mv(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float,
        load: int
    ):
        """Calculate voltage for load <= threshold SHALL return min_mv."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        # Only test loads at or below threshold
        if load > threshold:
            return
        
        manager = DynamicManager()
        voltage = manager._calculate_voltage(load, min_mv, max_mv, threshold)
        
        assert voltage == min_mv, (
            f"Voltage at load {load} (threshold={threshold}) "
            f"should be {min_mv}, got {voltage}"
        )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=st.floats(min_value=0.0, max_value=99.9)  # Ensure some points below
    )
    @settings(max_examples=100)
    def test_all_points_below_threshold_are_consistent(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """All curve points below threshold SHALL have identical voltage values."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # Collect all voltages for points below threshold
        voltages_below_threshold = [
            point.voltage for point in curve_points if point.load <= threshold
        ]
        
        # All should be equal to min_mv
        if voltages_below_threshold:
            assert all(v == min_mv for v in voltages_below_threshold), (
                f"All voltages below threshold should be {min_mv}, "
                f"got {set(voltages_below_threshold)}"
            )


class TestVoltageCurveCalculationAboveThreshold:
    """Property 3: Voltage curve calculation above threshold
    
    For any core configuration, all curve points where CPULoad is greater than 
    Threshold SHALL have VoltageOffset calculated as: 
    min_mv + (max_mv - min_mv) * (load - threshold) / (100 - threshold).
    
    Validates: Requirements 2.5
    """

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=st.floats(min_value=0.0, max_value=99.9),  # Ensure some points above
        load=cpu_load
    )
    @settings(max_examples=100)
    def test_calculate_voltage_above_threshold_follows_formula(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float,
        load: int
    ):
        """Voltage for load > threshold SHALL follow interpolation formula."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        # Only test loads above threshold
        if load <= threshold:
            return
        
        # Skip edge case where threshold is 100 (no points above)
        if threshold >= 100:
            return
        
        manager = DynamicManager()
        voltage = manager._calculate_voltage(load, min_mv, max_mv, threshold)
        
        # Calculate expected voltage using the formula
        progress = (load - threshold) / (100 - threshold)
        expected_voltage = int(round(min_mv + (max_mv - min_mv) * progress))
        
        assert voltage == expected_voltage, (
            f"Voltage at load {load} (threshold={threshold}) "
            f"should be {expected_voltage}, got {voltage}"
        )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=st.floats(min_value=0.0, max_value=99.9)
    )
    @settings(max_examples=100)
    def test_curve_points_above_threshold_follow_formula(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """All curve points above threshold SHALL follow interpolation formula."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # Check all points above threshold
        for point in curve_points:
            if point.load > threshold:
                # Calculate expected voltage
                if threshold >= 100:
                    expected_voltage = max_mv
                else:
                    progress = (point.load - threshold) / (100 - threshold)
                    expected_voltage = int(round(min_mv + (max_mv - min_mv) * progress))
                
                assert point.voltage == expected_voltage, (
                    f"Curve point at load {point.load} (threshold={threshold}) "
                    f"should have voltage {expected_voltage}, got {point.voltage}"
                )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=st.floats(min_value=0.0, max_value=99.9)
    )
    @settings(max_examples=100)
    def test_voltage_at_load_100_equals_max_mv(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """Voltage at load=100 SHALL equal max_mv."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        manager = DynamicManager()
        voltage = manager._calculate_voltage(100, min_mv, max_mv, threshold)
        
        assert voltage == max_mv, (
            f"Voltage at load 100 should be {max_mv}, got {voltage}"
        )

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage,
        threshold=st.floats(min_value=0.1, max_value=99.9)
    )
    @settings(max_examples=100)
    def test_voltage_increases_monotonically_above_threshold(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ):
        """Voltage SHALL increase monotonically for loads above threshold."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # Get points above threshold
        points_above = [p for p in curve_points if p.load > threshold]
        
        # Check monotonic increase
        for i in range(len(points_above) - 1):
            current = points_above[i]
            next_point = points_above[i + 1]
            
            assert current.voltage <= next_point.voltage, (
                f"Voltage should increase monotonically: "
                f"load {current.load} has voltage {current.voltage}, "
                f"load {next_point.load} has voltage {next_point.voltage}"
            )


class TestVoltageCurveEdgeCases:
    """Test edge cases for voltage curve calculation."""

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage
    )
    @settings(max_examples=100)
    def test_threshold_at_zero_all_points_interpolated(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int
    ):
        """When threshold=0, all points except load=0 SHALL be interpolated."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        threshold = 0.0
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # Point at load=0 should be min_mv
        assert curve_points[0].voltage == min_mv
        
        # All other points should be interpolated
        for point in curve_points[1:]:
            progress = point.load / 100.0
            expected = int(round(min_mv + (max_mv - min_mv) * progress))
            assert point.voltage == expected

    @given(
        core_id=core_id,
        min_mv=valid_voltage,
        max_mv=valid_voltage
    )
    @settings(max_examples=100)
    def test_threshold_at_100_all_points_min_mv(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int
    ):
        """When threshold=100, all points SHALL equal min_mv."""
        # Skip invalid configurations
        if min_mv > max_mv:
            return
        
        threshold = 100.0
        manager = DynamicManager()
        manager.set_core_config(core_id, min_mv, max_mv, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # All points should be min_mv
        for point in curve_points:
            assert point.voltage == min_mv, (
                f"With threshold=100, all points should be {min_mv}, "
                f"got {point.voltage} at load {point.load}"
            )

    @given(
        core_id=core_id,
        voltage=valid_voltage
    )
    @settings(max_examples=100)
    def test_min_equals_max_constant_voltage(
        self,
        core_id: int,
        voltage: int
    ):
        """When min_mv == max_mv, all points SHALL have that voltage."""
        threshold = 50.0
        manager = DynamicManager()
        manager.set_core_config(core_id, voltage, voltage, threshold)
        
        curve_points = manager.get_curve_data(core_id)
        
        # All points should have the same voltage
        for point in curve_points:
            assert point.voltage == voltage, (
                f"With min_mv=max_mv={voltage}, all points should be {voltage}, "
                f"got {point.voltage} at load {point.load}"
            )

    @given(core_id=core_id)
    @settings(max_examples=100)
    def test_curve_has_101_points(self, core_id: int):
        """Curve data SHALL contain exactly 101 points (load 0-100)."""
        manager = DynamicManager()
        curve_points = manager.get_curve_data(core_id)
        
        assert len(curve_points) == 101, (
            f"Curve should have 101 points, got {len(curve_points)}"
        )
        
        # Verify load values are 0 to 100
        loads = [p.load for p in curve_points]
        assert loads == list(range(101)), (
            f"Curve loads should be 0-100, got {loads[:5]}...{loads[-5:]}"
        )
