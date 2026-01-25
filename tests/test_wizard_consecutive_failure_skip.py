"""Property tests for wizard consecutive failure skip.

Feature: frequency-based-wizard, Property 16: Consecutive failure skip
Validates: Requirements 9.4

Tests that the wizard skips frequencies after three consecutive test failures.
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
    ConsecutiveFailureError,
    CONSECUTIVE_FAILURE_THRESHOLD
)
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


@st.composite
def frequency_strategy(draw):
    """Generate valid frequencies."""
    return draw(st.integers(min_value=400, max_value=3500))


class TestConsecutiveFailureSkip:
    """Property tests for consecutive failure skip functionality.
    
    Feature: frequency-based-wizard, Property 16: Consecutive failure skip
    Validates: Requirements 9.4
    """
    
    @given(freq_mhz=frequency_strategy())
    @settings(max_examples=100, deadline=None)
    def test_consecutive_failure_threshold_is_three(self, freq_mhz):
        """For any frequency, the consecutive failure threshold should be 3.
        
        Feature: frequency-based-wizard, Property 16: Consecutive failure skip
        Validates: Requirements 9.4
        """
        # Verify the constant is correct
        assert CONSECUTIVE_FAILURE_THRESHOLD == 3, \
            "CONSECUTIVE_FAILURE_THRESHOLD should be 3"
    
    @given(freq_mhz=frequency_strategy())
    @settings(max_examples=100, deadline=None)
    def test_three_consecutive_failures_skip_frequency(self, freq_mhz):
        """For any frequency where three consecutive tests fail, the wizard should skip that frequency.
        
        Feature: frequency-based-wizard, Property 16: Consecutive failure skip
        Validates: Requirements 9.4
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        cpufreq.lock_frequency = Mock()
        cpufreq.unlock_frequency = Mock()
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics to return normal temperature
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': freq_mhz
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Mock run_frequency_locked_test to always fail
        async def failing_test(*args, **kwargs):
            return TestResult(passed=False, duration=1.0, logs="", error="Test failed")
        
        test_runner.run_frequency_locked_test = failing_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=10,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run the test
        async def run_test():
            point = await wizard._test_frequency_point(
                core_id=0,
                freq_mhz=freq_mhz
            )
            return point
        
        point = asyncio.run(run_test())
        
        # Verify: Frequency point should be marked as unstable
        assert point.stable is False, \
            f"Frequency {freq_mhz} MHz should be marked unstable after {CONSECUTIVE_FAILURE_THRESHOLD} consecutive failures"
        
        # Verify: Voltage should be 0 (no undervolt for unstable frequency)
        assert point.voltage_mv == 0, \
            "Unstable frequency should have voltage_mv = 0"
        
        # Verify: Test duration should be 0 (skipped)
        assert point.test_duration == 0, \
            "Skipped frequency should have test_duration = 0"
    
    @given(freq_mhz=frequency_strategy())
    @settings(max_examples=100, deadline=None)
    def test_fewer_than_three_failures_continue_testing(self, freq_mhz):
        """For any frequency with fewer than 3 consecutive failures, testing should continue.
        
        Feature: frequency-based-wizard, Property 16: Consecutive failure skip
        Validates: Requirements 9.4
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        cpufreq.lock_frequency = Mock()
        cpufreq.unlock_frequency = Mock()
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': freq_mhz
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Track test call count
        test_call_count = 0
        
        # Mock run_frequency_locked_test to fail twice, then succeed
        async def mixed_test(*args, **kwargs):
            nonlocal test_call_count
            test_call_count += 1
            
            if test_call_count <= 2:
                # First two tests fail
                return TestResult(passed=False, duration=1.0, logs="", error="Test failed")
            else:
                # Third test succeeds
                return TestResult(passed=True, duration=1.0, logs="", error=None)
        
        test_runner.run_frequency_locked_test = mixed_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=10,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run the test
        async def run_test():
            point = await wizard._test_frequency_point(
                core_id=0,
                freq_mhz=freq_mhz
            )
            return point
        
        point = asyncio.run(run_test())
        
        # Verify: Frequency point should be marked as stable (eventually succeeded)
        assert point.stable is True, \
            f"Frequency {freq_mhz} MHz should be marked stable after eventual success"
        
        # Verify: Test should have been called at least 3 times
        assert test_call_count >= 3, \
            f"Test should continue after 2 failures (called {test_call_count} times)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
