"""Property-based tests for frequency point data completeness.

Feature: frequency-based-wizard, Property 6: Frequency point data completeness
Validates: Requirements 1.3
"""

import time
import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, MagicMock, patch

from backend.tuning.frequency_wizard import FrequencyWizard, FrequencyWizardConfig
from backend.tuning.frequency_curve import FrequencyPoint
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


class TestFrequencyPointCompleteness:
    """Test frequency point data completeness.
    
    Property 6: For any stable frequency test result, the recorded frequency point
    should contain all required fields: frequency_mhz, voltage_mv, stable status,
    test_duration, and timestamp.
    """
    
    @given(
        freq_mhz=st.integers(min_value=400, max_value=3500),
        voltage_mv=st.integers(min_value=-100, max_value=0),
        test_duration=st.integers(min_value=10, max_value=120),
        safety_margin=st.integers(min_value=0, max_value=20)
    )
    @pytest.mark.asyncio
    async def test_frequency_point_has_all_required_fields(
        self,
        freq_mhz,
        voltage_mv,
        test_duration,
        safety_margin
    ):
        """Test that generated frequency points contain all required fields."""
        # Create mock dependencies
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = "schedutil"
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to always pass (stable)
        test_runner.run_frequency_locked_test = AsyncMock(
            return_value=TestResult(
                passed=True,
                duration=float(test_duration),
                logs="Test passed",
                error=None
            )
        )
        
        # Create wizard config
        # Ensure freq_end > freq_start for validation
        config = FrequencyWizardConfig(
            freq_start=freq_mhz,
            freq_end=freq_mhz + 50,  # Slightly higher to pass validation
            freq_step=100,  # Large step ensures only one point
            test_duration=test_duration,
            voltage_start=voltage_mv,
            voltage_step=2,
            safety_margin=safety_margin
        )
        
        # Create wizard
        wizard = FrequencyWizard(
            config=config,
            cpufreq_controller=cpufreq_controller,
            test_runner=test_runner
        )
        
        # Record time before test
        time_before = time.time()
        
        # Run wizard
        curve = await wizard.run(core_id=0)
        
        # Record time after test
        time_after = time.time()
        
        # Verify we got exactly one point
        assert len(curve.points) == 1, "Expected exactly one frequency point"
        
        point = curve.points[0]
        
        # Verify all required fields are present
        assert hasattr(point, 'frequency_mhz'), "Missing frequency_mhz field"
        assert hasattr(point, 'voltage_mv'), "Missing voltage_mv field"
        assert hasattr(point, 'stable'), "Missing stable field"
        assert hasattr(point, 'test_duration'), "Missing test_duration field"
        assert hasattr(point, 'timestamp'), "Missing timestamp field"
        
        # Verify field types
        assert isinstance(point.frequency_mhz, int), "frequency_mhz must be int"
        assert isinstance(point.voltage_mv, int), "voltage_mv must be int"
        assert isinstance(point.stable, bool), "stable must be bool"
        assert isinstance(point.test_duration, int), "test_duration must be int"
        assert isinstance(point.timestamp, float), "timestamp must be float"
        
        # Verify field values are reasonable
        assert point.frequency_mhz == freq_mhz, (
            f"frequency_mhz {point.frequency_mhz} does not match tested frequency {freq_mhz}"
        )
        
        assert -100 <= point.voltage_mv <= 0, (
            f"voltage_mv {point.voltage_mv} is outside valid range [-100, 0]"
        )
        
        assert point.stable is True, "Point should be marked as stable"
        
        assert point.test_duration == test_duration, (
            f"test_duration {point.test_duration} does not match config {test_duration}"
        )
        
        assert time_before <= point.timestamp <= time_after, (
            f"timestamp {point.timestamp} is outside test execution window "
            f"[{time_before}, {time_after}]"
        )
    
    @given(
        freq_mhz=st.integers(min_value=400, max_value=3500),
        test_duration=st.integers(min_value=10, max_value=120)
    )
    @pytest.mark.asyncio
    async def test_voltage_includes_safety_margin(self, freq_mhz, test_duration):
        """Test that recorded voltage includes the configured safety margin."""
        safety_margin = 5
        stable_voltage = -30
        
        # Create mock dependencies
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = "schedutil"
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to pass at stable_voltage
        async def mock_test(core_id, freq_mhz, voltage_mv, duration):
            # Pass if voltage >= stable_voltage (less aggressive)
            passed = voltage_mv >= stable_voltage
            return TestResult(
                passed=passed,
                duration=float(duration),
                logs="Test result",
                error=None
            )
        
        test_runner.run_frequency_locked_test = mock_test
        
        # Create wizard config
        # Ensure freq_end > freq_start for validation
        config = FrequencyWizardConfig(
            freq_start=freq_mhz,
            freq_end=freq_mhz + 50,  # Slightly higher to pass validation
            freq_step=100,  # Large step ensures only one point
            test_duration=test_duration,
            voltage_start=-50,  # Start more aggressive
            voltage_step=2,
            safety_margin=safety_margin
        )
        
        # Create wizard
        wizard = FrequencyWizard(
            config=config,
            cpufreq_controller=cpufreq_controller,
            test_runner=test_runner
        )
        
        # Run wizard
        curve = await wizard.run(core_id=0)
        
        # Verify voltage includes safety margin
        point = curve.points[0]
        expected_voltage = stable_voltage + safety_margin
        
        assert point.voltage_mv == expected_voltage, (
            f"Expected voltage {expected_voltage}mV (stable {stable_voltage}mV + "
            f"margin {safety_margin}mV), got {point.voltage_mv}mV"
        )
    
    @pytest.mark.asyncio
    async def test_multiple_points_all_have_required_fields(self):
        """Test that all points in a multi-point curve have required fields."""
        # Create mock dependencies
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = "schedutil"
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to always pass
        test_runner.run_frequency_locked_test = AsyncMock(
            return_value=TestResult(
                passed=True,
                duration=30.0,
                logs="Test passed",
                error=None
            )
        )
        
        # Create wizard config with multiple frequency points
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1200,
            freq_step=100,  # Will generate 3 points: 1000, 1100, 1200
            test_duration=30,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5
        )
        
        # Create wizard
        wizard = FrequencyWizard(
            config=config,
            cpufreq_controller=cpufreq_controller,
            test_runner=test_runner
        )
        
        # Run wizard
        curve = await wizard.run(core_id=0)
        
        # Verify we got 3 points
        assert len(curve.points) == 3, f"Expected 3 points, got {len(curve.points)}"
        
        # Verify all points have required fields
        required_fields = ['frequency_mhz', 'voltage_mv', 'stable', 'test_duration', 'timestamp']
        
        for i, point in enumerate(curve.points):
            for field in required_fields:
                assert hasattr(point, field), (
                    f"Point {i} missing required field '{field}'"
                )
            
            # Verify field types
            assert isinstance(point.frequency_mhz, int), f"Point {i}: frequency_mhz must be int"
            assert isinstance(point.voltage_mv, int), f"Point {i}: voltage_mv must be int"
            assert isinstance(point.stable, bool), f"Point {i}: stable must be bool"
            assert isinstance(point.test_duration, int), f"Point {i}: test_duration must be int"
            assert isinstance(point.timestamp, float), f"Point {i}: timestamp must be float"
    
    @pytest.mark.asyncio
    async def test_timestamp_increases_for_sequential_points(self):
        """Test that timestamps increase for sequentially tested points."""
        # Create mock dependencies
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = "schedutil"
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to always pass with small delay
        async def mock_test_with_delay(core_id, freq_mhz, voltage_mv, duration):
            import asyncio
            await asyncio.sleep(0.01)  # Small delay to ensure timestamps differ
            return TestResult(
                passed=True,
                duration=30.0,
                logs="Test passed",
                error=None
            )
        
        test_runner.run_frequency_locked_test = mock_test_with_delay
        
        # Create wizard config with multiple frequency points
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1200,
            freq_step=100,
            test_duration=30,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5
        )
        
        # Create wizard
        wizard = FrequencyWizard(
            config=config,
            cpufreq_controller=cpufreq_controller,
            test_runner=test_runner
        )
        
        # Run wizard
        curve = await wizard.run(core_id=0)
        
        # Verify timestamps increase
        for i in range(len(curve.points) - 1):
            assert curve.points[i].timestamp < curve.points[i + 1].timestamp, (
                f"Timestamp for point {i} ({curve.points[i].timestamp}) is not less than "
                f"timestamp for point {i+1} ({curve.points[i+1].timestamp})"
            )
