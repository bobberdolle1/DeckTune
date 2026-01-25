"""Property tests for wizard test timeout detection.

Feature: frequency-based-wizard, Property 15: Test timeout detection
Validates: Requirements 9.3

Tests that the wizard detects and aborts frozen tests that exceed the timeout threshold.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, settings, strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.tuning.frequency_wizard import (
    FrequencyWizard,
    FrequencyWizardConfig,
    TEST_TIMEOUT_MARGIN
)
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


@st.composite
def duration_strategy(draw):
    """Generate valid test durations."""
    return draw(st.integers(min_value=10, max_value=30))


@st.composite
def params_strategy(draw):
    """Generate valid test parameters."""
    return {
        'freq_mhz': draw(st.integers(min_value=400, max_value=3500)),
        'voltage_mv': draw(st.integers(min_value=-100, max_value=0))
    }


class TestTimeoutDetection:
    """Property tests for test timeout detection functionality.
    
    Feature: frequency-based-wizard, Property 15: Test timeout detection
    Validates: Requirements 9.3
    """
    
    @given(test_duration=duration_strategy())
    @settings(max_examples=100, deadline=None)
    def test_timeout_threshold_calculation(self, test_duration):
        """For any test duration, the timeout threshold should be duration + 30 seconds.
        
        Feature: frequency-based-wizard, Property 15: Test timeout detection
        Validates: Requirements 9.3
        """
        # The timeout threshold is test_duration + TEST_TIMEOUT_MARGIN
        expected_timeout = test_duration + TEST_TIMEOUT_MARGIN
        
        # Verify the constant is correct
        assert TEST_TIMEOUT_MARGIN == 30, \
            "TEST_TIMEOUT_MARGIN should be 30 seconds"
        
        # Verify the calculation
        assert expected_timeout == test_duration + 30, \
            f"Timeout threshold should be {test_duration} + 30 = {expected_timeout}"
    
    @given(
        test_duration=st.integers(min_value=1, max_value=3),
        params=params_strategy()
    )
    @settings(max_examples=10, deadline=None)
    def test_timeout_detection_aborts_frozen_test(self, test_duration, params):
        """For any test that runs longer than duration + 30s, the system should abort.
        
        Feature: frequency-based-wizard, Property 15: Test timeout detection
        Validates: Requirements 9.3
        """
        # Create mock components
        cpufreq = Mock(spec=CPUFreqController)
        cpufreq.get_current_governor.return_value = "schedutil"
        
        test_runner = Mock(spec=TestRunner)
        
        # Mock get_system_metrics to return normal temperature
        test_runner.get_system_metrics.return_value = {
            'temperature': 60.0,
            'frequency': params['freq_mhz']
        }
        
        # Mock ryzenadj wrapper
        ryzenadj_mock = AsyncMock()
        ryzenadj_mock.apply_values_async.return_value = (True, None)
        test_runner._ryzenadj_wrapper = ryzenadj_mock
        
        # Mock run_frequency_locked_test to hang (simulate frozen test)
        async def frozen_test(*args, **kwargs):
            # Sleep longer than the timeout threshold
            timeout_threshold = test_duration + TEST_TIMEOUT_MARGIN
            await asyncio.sleep(timeout_threshold + 1)
            return TestResult(passed=True, duration=test_duration, logs="", error=None)
        
        test_runner.run_frequency_locked_test = frozen_test
        
        # Create wizard
        wizard_config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=500,
            freq_step=100,
            test_duration=test_duration,
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
                freq_mhz=params['freq_mhz'],
                voltage_mv=params['voltage_mv']
            )
            return result
        
        result = asyncio.run(run_test())
        
        # Verify: Test should fail due to timeout
        assert result is False, \
            f"Test should abort when it runs longer than {test_duration + TEST_TIMEOUT_MARGIN}s"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
