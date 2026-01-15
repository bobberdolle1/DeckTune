"""Property tests for autotune rollback on failure.

Feature: decktune, Property 3: Autotune Rollback on Failure
Validates: Requirements 2.4

Property 3: Autotune Rollback on Failure
For any autotune session where a test fails at value V, the next tested value 
SHALL be V + step (less aggressive), and the final result for that core 
SHALL be >= V + step.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import asyncio
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from backend.tuning.autotune import AutotuneEngine, AutotuneConfig, AutotuneResult
from backend.platform.detect import PlatformInfo


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class MockEventEmitter:
    """Mock event emitter that records all emitted events."""
    
    def __init__(self):
        self.progress_events: List[dict] = []
        self.completion_events: List[AutotuneResult] = []
        self.status_events: List[str] = []
    
    async def emit_status(self, status: str) -> None:
        self.status_events.append(status)
    
    async def emit_tuning_progress(self, phase: str, core: int, value: int, eta: int) -> None:
        self.progress_events.append({
            "phase": phase,
            "core": core,
            "value": value,
            "eta": eta
        })
    
    async def emit_tuning_complete(self, result: AutotuneResult) -> None:
        self.completion_events.append(result)
    
    async def emit_test_progress(self, test_name: str, progress: int) -> None:
        pass
    
    async def emit_test_complete(self, result) -> None:
        pass


@dataclass
class MockTestResult:
    """Mock test result."""
    passed: bool
    duration: float = 0.1
    logs: str = "test output"
    error: Optional[str] = None


class MockTestRunner:
    """Mock test runner that fails at specified values."""
    
    def __init__(self, fail_at_values: List[int] = None):
        """
        Args:
            fail_at_values: List of undervolt values that should fail tests
        """
        self.fail_at_values = fail_at_values or []
        self.tested_values: List[Tuple[int, int]] = []  # (core, value) pairs
        self.test_count = 0
    
    async def run_test(self, test_name: str) -> MockTestResult:
        self.test_count += 1
        # Check if any of the current values should fail
        # This is set by the test before calling
        return MockTestResult(passed=self._should_pass)
    
    async def check_dmesg_errors(self) -> List[str]:
        return []
    
    def set_should_pass(self, should_pass: bool):
        self._should_pass = should_pass
    
    _should_pass: bool = True


class MockRyzenadj:
    """Mock ryzenadj wrapper that tracks applied values."""
    
    def __init__(self):
        self.applied_values: List[List[int]] = []
        self.current_values: List[int] = [0, 0, 0, 0]
    
    async def apply_values_async(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
        self.applied_values.append(cores.copy())
        self.current_values = cores.copy()
        return True, None
    
    def apply_values(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
        self.applied_values.append(cores.copy())
        self.current_values = cores.copy()
        return True, None


class MockSafetyManager:
    """Mock safety manager for testing."""
    
    def __init__(self, safe_limit: int = -30):
        self.platform = PlatformInfo(
            model="Jupiter",
            variant="LCD", 
            safe_limit=safe_limit,
            detected=True
        )
        self.lkg_values: List[int] = [0, 0, 0, 0]
        self.tuning_flag_created = False
        self.tuning_flag_removed = False
        self.rollback_called = False
    
    def clamp_values(self, values: List[int]) -> List[int]:
        return [max(self.platform.safe_limit, min(0, v)) for v in values]
    
    def save_lkg(self, values: List[int]) -> None:
        self.lkg_values = values.copy()
    
    def load_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def get_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def rollback_to_lkg(self) -> Tuple[bool, Optional[str]]:
        self.rollback_called = True
        return True, None
    
    def create_tuning_flag(self) -> None:
        self.tuning_flag_created = True
    
    def remove_tuning_flag(self) -> None:
        self.tuning_flag_removed = True


class ControlledTestRunner:
    """Test runner with controlled failure behavior for property testing."""
    
    def __init__(self, fail_threshold: int):
        """
        Args:
            fail_threshold: Values at or below this threshold will fail
        """
        self.fail_threshold = fail_threshold
        self.current_test_value: int = 0
        self.tested_values: List[int] = []
    
    def set_current_test_value(self, value: int):
        """Set the value being tested (called by autotune before test)."""
        self.current_test_value = value
    
    async def run_test(self, test_name: str) -> MockTestResult:
        self.tested_values.append(self.current_test_value)
        passed = self.current_test_value > self.fail_threshold
        return MockTestResult(
            passed=passed,
            error=None if passed else f"Failed at {self.current_test_value}"
        )
    
    async def check_dmesg_errors(self) -> List[str]:
        return []


# Strategies for property testing
fail_threshold_strategy = st.integers(min_value=-25, max_value=-5)
step_strategy = st.sampled_from([5, 10])
safe_limit_strategy = st.sampled_from([-30, -35, -25])


class TestAutotuneRollbackOnFailure:
    """Property 3: Autotune Rollback on Failure
    
    For any autotune session where a test fails at value V, the next tested 
    value SHALL be V + step (less aggressive), and the final result for that 
    core SHALL be >= V + step.
    
    Validates: Requirements 2.4
    """

    @given(
        fail_threshold=fail_threshold_strategy,
        step=step_strategy,
        safe_limit=safe_limit_strategy
    )
    @settings(max_examples=100)
    def test_final_value_greater_than_fail_value(
        self,
        fail_threshold: int,
        step: int,
        safe_limit: int
    ):
        """Final result for a core SHALL be >= first_fail + step."""
        # Skip if fail_threshold is below safe_limit (would never be tested)
        assume(fail_threshold >= safe_limit)
        
        # Create mocks
        event_emitter = MockEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        
        # Track what values are tested and their results
        tested_values_with_results: List[Tuple[int, bool]] = []
        
        class TrackingTestRunner:
            def __init__(self, threshold: int):
                self.threshold = threshold
                self.current_value = 0
            
            async def run_test(self, test_name: str) -> MockTestResult:
                passed = self.current_value > self.threshold
                tested_values_with_results.append((self.current_value, passed))
                return MockTestResult(passed=passed)
            
            async def check_dmesg_errors(self) -> List[str]:
                return []
        
        runner = TrackingTestRunner(fail_threshold)
        
        # Create engine with patched _apply_test_values to track current value
        engine = AutotuneEngine(ryzenadj, runner, safety, event_emitter)
        
        # Patch to track current test value
        original_apply = engine._apply_test_values
        async def patched_apply(values: List[int]):
            runner.current_value = values[0]  # Track core 0's value
            return await original_apply(values)
        engine._apply_test_values = patched_apply
        
        config = AutotuneConfig(
            mode="quick",
            start_value=0,
            step=step,
            test_duration_quick=30,
            test_duration_long=120
        )
        
        # Run autotune for core 0 only (simplified test)
        result = asyncio.get_event_loop().run_until_complete(
            engine._phase_a(0, config)
        )
        
        last_good, first_fail = result
        
        # Find the first failure in tested values
        first_fail_value = None
        for value, passed in tested_values_with_results:
            if not passed:
                first_fail_value = value
                break
        
        if first_fail_value is not None:
            # Property: final result >= first_fail + step
            assert last_good >= first_fail_value + step, (
                f"last_good ({last_good}) should be >= "
                f"first_fail ({first_fail_value}) + step ({step})"
            )

    @given(
        fail_threshold=fail_threshold_strategy,
        step=step_strategy
    )
    @settings(max_examples=100)
    def test_rollback_after_failure(
        self,
        fail_threshold: int,
        step: int
    ):
        """After a test fails, the applied values should rollback to last_good."""
        safe_limit = -30
        assume(fail_threshold >= safe_limit)
        assume(fail_threshold < 0)  # Must have at least one passing value
        
        event_emitter = MockEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        
        class TrackingTestRunner:
            def __init__(self, threshold: int):
                self.threshold = threshold
                self.current_value = 0
            
            async def run_test(self, test_name: str) -> MockTestResult:
                passed = self.current_value > self.threshold
                return MockTestResult(passed=passed)
            
            async def check_dmesg_errors(self) -> List[str]:
                return []
        
        runner = TrackingTestRunner(fail_threshold)
        engine = AutotuneEngine(ryzenadj, runner, safety, event_emitter)
        
        original_apply = engine._apply_test_values
        async def patched_apply(values: List[int]):
            runner.current_value = values[0]
            return await original_apply(values)
        engine._apply_test_values = patched_apply
        
        config = AutotuneConfig(
            mode="quick",
            start_value=0,
            step=step,
            test_duration_quick=30,
            test_duration_long=120
        )
        
        asyncio.get_event_loop().run_until_complete(
            engine._phase_a(0, config)
        )
        
        # After phase A completes, the last applied value should be last_good
        if ryzenadj.applied_values:
            final_applied = ryzenadj.applied_values[-1][0]
            # The final applied value should be > fail_threshold (i.e., passing)
            assert final_applied > fail_threshold, (
                f"Final applied value ({final_applied}) should be > "
                f"fail_threshold ({fail_threshold})"
            )

    def test_step_back_on_failure_example(self):
        """Concrete example: when test fails at -15, next test should be at -10."""
        event_emitter = MockEventEmitter()
        safety = MockSafetyManager(safe_limit=-30)
        ryzenadj = MockRyzenadj()
        
        # Fail at -15 and below
        fail_threshold = -15
        tested_values: List[int] = []
        
        class TrackingTestRunner:
            def __init__(self):
                self.current_value = 0
            
            async def run_test(self, test_name: str) -> MockTestResult:
                tested_values.append(self.current_value)
                passed = self.current_value > fail_threshold
                return MockTestResult(passed=passed)
            
            async def check_dmesg_errors(self) -> List[str]:
                return []
        
        runner = TrackingTestRunner()
        engine = AutotuneEngine(ryzenadj, runner, safety, event_emitter)
        
        original_apply = engine._apply_test_values
        async def patched_apply(values: List[int]):
            runner.current_value = values[0]
            return await original_apply(values)
        engine._apply_test_values = patched_apply
        
        config = AutotuneConfig(
            mode="quick",
            start_value=0,
            step=5,
            test_duration_quick=30,
            test_duration_long=120
        )
        
        result = asyncio.get_event_loop().run_until_complete(
            engine._phase_a(0, config)
        )
        
        last_good, first_fail = result
        
        # Should have tested: 0, -5, -10, -15 (fail)
        # last_good should be -10, first_fail should be -15
        assert last_good == -10, f"Expected last_good=-10, got {last_good}"
        assert first_fail == -15, f"Expected first_fail=-15, got {first_fail}"
        
        # Verify the sequence of tested values
        expected_sequence = [0, -5, -10, -15]
        assert tested_values == expected_sequence, (
            f"Expected test sequence {expected_sequence}, got {tested_values}"
        )
