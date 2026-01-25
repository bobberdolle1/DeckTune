"""Property tests for wizard verification test execution.

Feature: frequency-based-wizard, Property 21: Verification test execution
Validates: Requirements 9.5

Tests that the wizard runs verification tests at random frequencies after curve generation.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from hypothesis import given, settings, strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.tuning.frequency_wizard import (
    FrequencyWizard,
    FrequencyWizardConfig,
    VERIFICATION_TEST_COUNT
)
from backend.tuning.frequency_curve import FrequencyCurve, FrequencyPoint
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


@st.composite
def frequency_curve_strategy(draw):
    """Generate valid frequency curves with stable points."""
    num_points = draw(st.integers(min_value=5, max_value=20))
    
    points = []
    for i in range(num_points):
        freq = 400 + (i * 100)
        voltage = draw(st.integers(min_value=-50, max_value=-10))
        points.append(FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=voltage,
            stable=True,
            test_duration=10,
            timestamp=1000.0 + i
        ))
    
    return FrequencyCurve(
        core_id=0,
        points=points,
        created_at=1000.0,
        wizard_config={}
    )


class TestVerificationTestExecution:
    """Property tests for verification test execution functionality.
    
    Feature: frequency-based-wizard, Property 21: Verification test execution
    Validates: Requirements 9.5
    """
    
    def test_verification_test_count_constant(self):
        """The verification test count should be 5.
        
        Feature: frequency-based-wizard, Property 21: Verification test execution
        Validates: Requirements 9.5
        """
        assert VERIFICATION_TEST_COUNT == 5, \
            "VERIFICATION_TEST_COUNT should be 5"
    
    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100, deadline=None)
    def test_verification_tests_random_frequencies(self, curve):
        """For any completed wizard execution, the system should run verification tests at 3-5 random frequencies.
        
        Feature: frequency-based-wizard, Property 21: Verification test execution
        Validates: Requirements 9.5
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': 1000
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Track which frequencies were tested
        tested_frequencies = []
        
        # Mock run_frequency_locked_test to track calls
        async def tracking_test(core_id, freq_mhz, voltage_mv, duration):
            tested_frequencies.append(freq_mhz)
            return TestResult(passed=True, duration=1.0, logs="", error=None)
        
        test_runner.run_frequency_locked_test = tracking_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=10
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run verification
        async def run_verification():
            return await wizard._verify_curve(curve)
        
        result = asyncio.run(run_verification())
        
        # Verify: Should test between 3-5 frequencies (or min of stable points)
        stable_points = [p for p in curve.points if p.stable]
        expected_count = min(VERIFICATION_TEST_COUNT, len(stable_points))
        
        assert len(tested_frequencies) == expected_count, \
            f"Should test {expected_count} frequencies, tested {len(tested_frequencies)}"
        
        # Verify: All tested frequencies should be from the curve
        curve_frequencies = {p.frequency_mhz for p in stable_points}
        for freq in tested_frequencies:
            assert freq in curve_frequencies, \
                f"Tested frequency {freq} should be from the curve"
        
        # Verify: Verification should pass if all tests passed
        assert result is True, \
            "Verification should pass when all tests pass"
    
    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100, deadline=None)
    def test_verification_fails_if_any_test_fails(self, curve):
        """For any verification where at least one test fails, the verification should fail.
        
        Feature: frequency-based-wizard, Property 21: Verification test execution
        Validates: Requirements 9.5
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': 1000
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Track test call count
        test_call_count = 0
        
        # Mock run_frequency_locked_test to fail on first test
        async def failing_first_test(core_id, freq_mhz, voltage_mv, duration):
            nonlocal test_call_count
            test_call_count += 1
            
            if test_call_count == 1:
                # First test fails
                return TestResult(passed=False, duration=1.0, logs="", error="Test failed")
            else:
                # Other tests pass
                return TestResult(passed=True, duration=1.0, logs="", error=None)
        
        test_runner.run_frequency_locked_test = failing_first_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=10
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run verification
        async def run_verification():
            return await wizard._verify_curve(curve)
        
        result = asyncio.run(run_verification())
        
        # Verify: Verification should fail if any test fails
        assert result is False, \
            "Verification should fail when at least one test fails"
    
    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100, deadline=None)
    def test_verification_tests_use_curve_voltages(self, curve):
        """For any verification test, the voltage used should match the curve's voltage for that frequency.
        
        Feature: frequency-based-wizard, Property 21: Verification test execution
        Validates: Requirements 9.5
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': 1000
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Track frequency-voltage pairs tested
        tested_pairs = []
        
        # Mock run_frequency_locked_test to track calls
        async def tracking_test(core_id, freq_mhz, voltage_mv, duration):
            tested_pairs.append((freq_mhz, voltage_mv))
            return TestResult(passed=True, duration=1.0, logs="", error=None)
        
        test_runner.run_frequency_locked_test = tracking_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=10
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run verification
        async def run_verification():
            return await wizard._verify_curve(curve)
        
        asyncio.run(run_verification())
        
        # Verify: Each tested frequency should use the correct voltage from the curve
        curve_voltage_map = {p.frequency_mhz: p.voltage_mv for p in curve.points if p.stable}
        
        for freq, voltage in tested_pairs:
            expected_voltage = curve_voltage_map.get(freq)
            assert expected_voltage is not None, \
                f"Tested frequency {freq} should be in the curve"
            assert voltage == expected_voltage, \
                f"Voltage for {freq}MHz should be {expected_voltage}mV, got {voltage}mV"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
