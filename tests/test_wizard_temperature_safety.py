"""Property tests for wizard temperature safety abort.

Feature: frequency-based-wizard, Property 14: Temperature safety abort
Validates: Requirements 9.2

Tests that the wizard aborts tests when CPU temperature exceeds the safety threshold.
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, settings, strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.tuning.frequency_wizard import (
    FrequencyWizard,
    FrequencyWizardConfig,
    TEMPERATURE_ABORT_THRESHOLD
)
from backend.tuning.frequency_curve import FrequencyPoint
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


@st.composite
def temperature_above_threshold(draw):
    """Generate temperatures above the safety threshold."""
    return draw(st.floats(
        min_value=TEMPERATURE_ABORT_THRESHOLD + 0.1,
        max_value=120.0
    ))


@st.composite
def config_strategy(draw):
    """Generate valid test configurations."""
    return {
        'freq_mhz': draw(st.integers(min_value=400, max_value=3500)),
        'voltage_mv': draw(st.integers(min_value=-100, max_value=0)),
        'duration': draw(st.integers(min_value=10, max_value=30))
    }


class TestTemperatureSafetyAbort:
    """Property tests for temperature safety abort functionality.
    
    Feature: frequency-based-wizard, Property 14: Temperature safety abort
    Validates: Requirements 9.2
    """
    
    @given(
        temp=temperature_above_threshold(),
        config=config_strategy()
    )
    @settings(max_examples=10, deadline=None)
    def test_temperature_abort_triggers_on_high_temp(self, temp, config):
        """For any temperature above threshold, test should abort.
        
        Feature: frequency-based-wizard, Property 14: Temperature safety abort
        Validates: Requirements 9.2
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        cpufreq.lock_frequency = Mock()
        cpufreq.unlock_frequency = Mock()
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics to return high temperature
        test_runner.get_system_metrics.return_value = {
            'temperature': temp,
            'frequency': config['freq_mhz']
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Mock run_frequency_locked_test to take long enough for monitoring
        async def slow_test(*args, **kwargs):
            await asyncio.sleep(0.5)  # Give monitoring time to detect temperature
            return TestResult(passed=True, duration=0.5, logs="", error=None)
        
        test_runner.run_frequency_locked_test = slow_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=config['duration'],
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
            result = await wizard._test_voltage_stability(
                core_id=0,
                freq_mhz=config['freq_mhz'],
                voltage_mv=config['voltage_mv']
            )
            return result
        
        result = asyncio.run(run_test())
        
        # Verify: Test should fail due to temperature abort
        assert result is False, \
            f"Test should abort when temperature ({temp:.1f}°C) exceeds threshold ({TEMPERATURE_ABORT_THRESHOLD}°C)"
        
        # Verify: Temperature abort flag should be set
        assert hasattr(wizard, '_temperature_abort_triggered'), \
            "Wizard should have _temperature_abort_triggered attribute"
        assert wizard._temperature_abort_triggered is True, \
            "Temperature abort flag should be set to True"
        
        # Verify: Emergency voltage restore should be called
        ryzenadj_mock.apply_values_async.assert_called()
        
        # Check that voltage was restored to 0
        calls = ryzenadj_mock.apply_values_async.call_args_list
        assert any([0, 0, 0, 0] == call[0][0] for call in calls), \
            "Emergency voltage restore should set voltage to [0, 0, 0, 0]"
    
    @given(config=config_strategy())
    @settings(max_examples=10, deadline=None)
    def test_temperature_abort_restores_safe_voltage(self, config):
        """For any test that triggers temperature abort, voltage should be restored to 0mV.
        
        Feature: frequency-based-wizard, Property 14: Temperature safety abort
        Validates: Requirements 9.2
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics to return critical temperature
        test_runner.get_system_metrics.return_value = {
            'temperature': TEMPERATURE_ABORT_THRESHOLD + 5.0,
            'frequency': config['freq_mhz']
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Mock run_frequency_locked_test
        async def slow_test(*args, **kwargs):
            await asyncio.sleep(0.5)
            return TestResult(passed=True, duration=0.5, logs="", error=None)
        
        test_runner.run_frequency_locked_test = slow_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=config['duration']
        )
        
        wizard = FrequencyWizard(
            config=wizard_config,
            cpufreq_controller=cpufreq,
            test_runner=test_runner
        )
        
        # Run the test
        async def run_test():
            return await wizard._test_voltage_stability(
                core_id=0,
                freq_mhz=config['freq_mhz'],
                voltage_mv=config['voltage_mv']
            )
        
        asyncio.run(run_test())
        
        # Verify: Voltage should be restored to 0mV (safe value)
        ryzenadj_mock.apply_values_async.assert_called()
        
        # Find the emergency restore call
        calls = ryzenadj_mock.apply_values_async.call_args_list
        emergency_restore_found = False
        
        for call in calls:
            if call[0][0] == [0, 0, 0, 0]:
                emergency_restore_found = True
                break
        
        assert emergency_restore_found, \
            "Emergency voltage restore to [0, 0, 0, 0] should be called during temperature abort"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
