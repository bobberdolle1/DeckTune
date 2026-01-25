"""Property-based tests for wizard cancellation state restoration.

Feature: frequency-based-wizard, Property 8: Wizard cancellation state restoration
Validates: Requirements 2.5, 6.4
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, MagicMock, call

from backend.tuning.frequency_wizard import FrequencyWizard, FrequencyWizardConfig, WizardCancelled
from backend.platform.cpufreq import CPUFreqController
from backend.tuning.runner import TestRunner, TestResult


class TestCancellationStateRestoration:
    """Test wizard cancellation state restoration.
    
    Property 8: For any wizard execution that is cancelled, the CPU governor and
    voltage settings after cancellation should match the state before the wizard started.
    """
    
    @given(
        original_governor=st.sampled_from(["schedutil", "performance", "powersave", "ondemand"]),
        freq_start=st.integers(min_value=400, max_value=2000),
        freq_step=st.integers(min_value=100, max_value=500)
    )
    @pytest.mark.asyncio
    async def test_governor_restored_after_cancellation(
        self,
        original_governor,
        freq_start,
        freq_step
    ):
        """Test that CPU governor is restored to original value after cancellation."""
        # Create mock cpufreq controller
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = original_governor
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        # Create mock test runner
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to always pass but take some time
        async def slow_test(core_id, freq_mhz, voltage_mv, duration):
            import asyncio
            await asyncio.sleep(0.01)  # Small delay
            return TestResult(
                passed=True,
                duration=30.0,
                logs="Test passed",
                error=None
            )
        
        test_runner.run_frequency_locked_test = slow_test
        
        # Create wizard config
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_start + freq_step * 3,  # Multiple points
            freq_step=freq_step,
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
        
        # Start wizard and cancel it immediately
        import asyncio
        
        async def cancel_after_delay():
            await asyncio.sleep(0.02)  # Let first test start
            wizard.cancel()
        
        # Run both tasks concurrently
        try:
            await asyncio.gather(
                wizard.run(core_id=0),
                cancel_after_delay()
            )
        except WizardCancelled:
            pass  # Expected
        
        # Verify unlock_frequency was called with original governor
        cpufreq_controller.unlock_frequency.assert_called()
        
        # Get the last call to unlock_frequency
        last_call = cpufreq_controller.unlock_frequency.call_args
        
        # Verify it was called with core_id=0 and original_governor
        assert last_call[0][0] == 0, "unlock_frequency not called with core_id=0"
        assert last_call[0][1] == original_governor, (
            f"Governor not restored to original value '{original_governor}', "
            f"got '{last_call[0][1]}'"
        )
    
    @given(
        original_governor=st.sampled_from(["schedutil", "performance", "powersave"]),
        freq_start=st.integers(min_value=400, max_value=2000)
    )
    @pytest.mark.asyncio
    async def test_voltage_restored_to_zero_after_cancellation(
        self,
        original_governor,
        freq_start
    ):
        """Test that voltage is restored to 0mV after cancellation."""
        # Create mock cpufreq controller
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = original_governor
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        # Create mock test runner with ryzenadj wrapper
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to always pass
        async def slow_test(core_id, freq_mhz, voltage_mv, duration):
            import asyncio
            await asyncio.sleep(0.01)
            return TestResult(
                passed=True,
                duration=30.0,
                logs="Test passed",
                error=None
            )
        
        test_runner.run_frequency_locked_test = slow_test
        
        # Create wizard config
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_start + 300,
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
        
        # Start wizard and cancel it
        import asyncio
        
        async def cancel_after_delay():
            await asyncio.sleep(0.02)
            wizard.cancel()
        
        try:
            await asyncio.gather(
                wizard.run(core_id=0),
                cancel_after_delay()
            )
        except WizardCancelled:
            pass
        
        # Verify voltage was restored to [0, 0, 0, 0]
        test_runner._ryzenadj_wrapper.apply_values_async.assert_called()
        
        # Check if any call was made with [0, 0, 0, 0]
        calls = test_runner._ryzenadj_wrapper.apply_values_async.call_args_list
        
        # The last call should be the restoration call
        last_call = calls[-1]
        assert last_call[0][0] == [0, 0, 0, 0], (
            f"Voltage not restored to [0, 0, 0, 0], got {last_call[0][0]}"
        )
    
    @pytest.mark.asyncio
    async def test_state_restored_even_on_exception(self):
        """Test that state is restored even if an exception occurs during wizard execution."""
        original_governor = "schedutil"
        
        # Create mock cpufreq controller
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = original_governor
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        # Create mock test runner
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Mock test to raise an exception
        async def failing_test(core_id, freq_mhz, voltage_mv, duration):
            raise RuntimeError("Test failed unexpectedly")
        
        test_runner.run_frequency_locked_test = failing_test
        
        # Create wizard config
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
        
        # Run wizard (should fail but still restore state)
        try:
            await wizard.run(core_id=0)
        except Exception:
            pass  # Expected to fail
        
        # Verify state was restored despite exception
        cpufreq_controller.unlock_frequency.assert_called_with(0, original_governor)
        
        # Verify voltage was restored
        calls = test_runner._ryzenadj_wrapper.apply_values_async.call_args_list
        assert len(calls) > 0, "No voltage restoration calls made"
        
        # Last call should restore to [0, 0, 0, 0]
        last_call = calls[-1]
        assert last_call[0][0] == [0, 0, 0, 0], (
            f"Voltage not restored after exception, got {last_call[0][0]}"
        )
    
    @pytest.mark.asyncio
    async def test_cancellation_during_binary_search(self):
        """Test that cancellation during binary search properly restores state."""
        original_governor = "schedutil"
        
        # Create mock cpufreq controller
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = original_governor
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        # Create mock test runner
        test_runner = MagicMock(spec=TestRunner)
        test_runner._ryzenadj_wrapper = AsyncMock()
        test_runner._ryzenadj_wrapper.apply_values_async = AsyncMock(return_value=(True, None))
        
        # Track number of tests run
        test_count = [0]
        
        # Mock test that cancels after a few iterations
        async def test_with_cancel(core_id, freq_mhz, voltage_mv, duration):
            import asyncio
            test_count[0] += 1
            
            # Cancel after 3 tests (during binary search)
            if test_count[0] == 3:
                wizard.cancel()
            
            await asyncio.sleep(0.01)
            return TestResult(
                passed=True,
                duration=30.0,
                logs="Test passed",
                error=None
            )
        
        test_runner.run_frequency_locked_test = test_with_cancel
        
        # Create wizard config
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1050,  # Must be > freq_start
            freq_step=100,  # Large step ensures single point
            test_duration=30,
            voltage_start=-50,  # Will require multiple binary search iterations
            voltage_step=2,
            safety_margin=5
        )
        
        # Create wizard
        wizard = FrequencyWizard(
            config=config,
            cpufreq_controller=cpufreq_controller,
            test_runner=test_runner
        )
        
        # Run wizard (should be cancelled)
        try:
            await wizard.run(core_id=0)
        except WizardCancelled:
            pass  # Expected
        
        # Verify state was restored
        cpufreq_controller.unlock_frequency.assert_called_with(0, original_governor)
        
        # Verify voltage was restored
        calls = test_runner._ryzenadj_wrapper.apply_values_async.call_args_list
        last_call = calls[-1]
        assert last_call[0][0] == [0, 0, 0, 0], (
            f"Voltage not restored after cancellation during binary search"
        )
    
    @given(
        original_governor=st.sampled_from(["schedutil", "performance", "powersave"])
    )
    @pytest.mark.asyncio
    async def test_multiple_cores_all_restored(self, original_governor):
        """Test that state is restored for the correct core when testing multiple cores."""
        # This test verifies that when testing core N, we restore core N's state
        
        # Create mock cpufreq controller
        cpufreq_controller = MagicMock(spec=CPUFreqController)
        cpufreq_controller.get_current_governor.return_value = original_governor
        cpufreq_controller.lock_frequency = MagicMock()
        cpufreq_controller.unlock_frequency = MagicMock()
        
        # Create mock test runner
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
        
        # Create wizard config
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1100,
            freq_step=100,
            test_duration=30,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5
        )
        
        # Test different cores
        for core_id in [0, 1, 2, 3]:
            # Reset mocks
            cpufreq_controller.unlock_frequency.reset_mock()
            
            # Create wizard
            wizard = FrequencyWizard(
                config=config,
                cpufreq_controller=cpufreq_controller,
                test_runner=test_runner
            )
            
            # Run wizard
            await wizard.run(core_id=core_id)
            
            # Verify unlock_frequency was called with correct core_id
            cpufreq_controller.unlock_frequency.assert_called()
            last_call = cpufreq_controller.unlock_frequency.call_args
            
            assert last_call[0][0] == core_id, (
                f"unlock_frequency not called with correct core_id {core_id}, "
                f"got {last_call[0][0]}"
            )
            assert last_call[0][1] == original_governor, (
                f"Governor not restored for core {core_id}"
            )
