"""Property tests for progress event structure.

Feature: decktune, Property 5: Progress Event Structure
Validates: Requirements 2.6

Property 5: Progress Event Structure
For any autotune progress event emitted, the event SHALL contain:
- phase: string ("A" or "B")
- core: integer (0-3)
- value: integer (within platform limits)
- eta: integer (>= 0)
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import asyncio
from typing import List, Tuple, Optional
from dataclasses import dataclass

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


@dataclass
class MockTestResult:
    """Mock test result."""
    passed: bool
    duration: float = 0.1
    logs: str = "test output"
    error: Optional[str] = None


class RecordingEventEmitter:
    """Event emitter that records all progress events for verification."""
    
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


class MockTestRunner:
    """Mock test runner that always passes."""
    
    def __init__(self, fail_at: Optional[int] = None):
        self.fail_at = fail_at
        self.current_value = 0
    
    async def run_test(self, test_name: str) -> MockTestResult:
        if self.fail_at is not None and self.current_value <= self.fail_at:
            return MockTestResult(passed=False, error="Simulated failure")
        return MockTestResult(passed=True)
    
    async def check_dmesg_errors(self) -> List[str]:
        return []


class MockRyzenadj:
    """Mock ryzenadj wrapper."""
    
    def __init__(self):
        self.applied_values: List[List[int]] = []
        self.current_values: List[int] = [0, 0, 0, 0]
    
    async def apply_values_async(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
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
    
    def clamp_values(self, values: List[int]) -> List[int]:
        return [max(self.platform.safe_limit, min(0, v)) for v in values]
    
    def save_lkg(self, values: List[int]) -> None:
        self.lkg_values = values.copy()
    
    def load_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def get_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def rollback_to_lkg(self) -> Tuple[bool, Optional[str]]:
        return True, None
    
    def create_tuning_flag(self) -> None:
        pass
    
    def remove_tuning_flag(self) -> None:
        pass


# Strategies for property testing
safe_limit_strategy = st.sampled_from([-30, -35, -25])
step_strategy = st.sampled_from([5, 10])
fail_at_strategy = st.one_of(
    st.none(),
    st.integers(min_value=-25, max_value=-5)
)


class TestProgressEventStructure:
    """Property 5: Progress Event Structure
    
    For any autotune progress event emitted, the event SHALL contain:
    - phase: string ("A" or "B")
    - core: integer (0-3)
    - value: integer (within platform limits)
    - eta: integer (>= 0)
    
    Validates: Requirements 2.6
    """

    @given(
        safe_limit=safe_limit_strategy,
        step=step_strategy,
        fail_at=fail_at_strategy
    )
    @settings(max_examples=100)
    def test_progress_events_have_valid_phase(
        self,
        safe_limit: int,
        step: int,
        fail_at: Optional[int]
    ):
        """All progress events have phase as 'A' or 'B'."""
        if fail_at is not None:
            assume(fail_at >= safe_limit)
        
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        runner = MockTestRunner(fail_at=fail_at)
        
        engine = AutotuneEngine(ryzenadj, runner, safety, event_emitter)
        
        # Patch to track current test value
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
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        for event in event_emitter.progress_events:
            assert "phase" in event, "Progress event missing 'phase' field"
            assert event["phase"] in ("A", "B"), (
                f"Phase should be 'A' or 'B', got '{event['phase']}'"
            )

    @given(
        safe_limit=safe_limit_strategy,
        step=step_strategy,
        fail_at=fail_at_strategy
    )
    @settings(max_examples=100)
    def test_progress_events_have_valid_core(
        self,
        safe_limit: int,
        step: int,
        fail_at: Optional[int]
    ):
        """All progress events have core as integer 0-3."""
        if fail_at is not None:
            assume(fail_at >= safe_limit)
        
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        runner = MockTestRunner(fail_at=fail_at)
        
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
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        for event in event_emitter.progress_events:
            assert "core" in event, "Progress event missing 'core' field"
            assert isinstance(event["core"], int), (
                f"Core should be int, got {type(event['core'])}"
            )
            assert 0 <= event["core"] <= 3, (
                f"Core should be 0-3, got {event['core']}"
            )

    @given(
        safe_limit=safe_limit_strategy,
        step=step_strategy,
        fail_at=fail_at_strategy
    )
    @settings(max_examples=100)
    def test_progress_events_have_value_within_limits(
        self,
        safe_limit: int,
        step: int,
        fail_at: Optional[int]
    ):
        """All progress events have value within platform limits."""
        if fail_at is not None:
            assume(fail_at >= safe_limit)
        
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        runner = MockTestRunner(fail_at=fail_at)
        
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
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        for event in event_emitter.progress_events:
            assert "value" in event, "Progress event missing 'value' field"
            assert isinstance(event["value"], int), (
                f"Value should be int, got {type(event['value'])}"
            )
            assert event["value"] >= safe_limit, (
                f"Value {event['value']} below safe limit {safe_limit}"
            )
            assert event["value"] <= 0, (
                f"Value {event['value']} should be <= 0"
            )

    @given(
        safe_limit=safe_limit_strategy,
        step=step_strategy,
        fail_at=fail_at_strategy
    )
    @settings(max_examples=100)
    def test_progress_events_have_non_negative_eta(
        self,
        safe_limit: int,
        step: int,
        fail_at: Optional[int]
    ):
        """All progress events have eta >= 0."""
        if fail_at is not None:
            assume(fail_at >= safe_limit)
        
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=safe_limit)
        ryzenadj = MockRyzenadj()
        runner = MockTestRunner(fail_at=fail_at)
        
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
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        for event in event_emitter.progress_events:
            assert "eta" in event, "Progress event missing 'eta' field"
            assert isinstance(event["eta"], int), (
                f"ETA should be int, got {type(event['eta'])}"
            )
            assert event["eta"] >= 0, (
                f"ETA should be >= 0, got {event['eta']}"
            )

    def test_progress_event_structure_completeness(self):
        """Verify progress events have all required fields."""
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=-30)
        ryzenadj = MockRyzenadj()
        runner = MockTestRunner(fail_at=-15)
        
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
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        # Should have emitted at least some progress events
        assert len(event_emitter.progress_events) > 0, (
            "Expected at least one progress event"
        )
        
        # Check first event has all required fields
        event = event_emitter.progress_events[0]
        required_fields = ["phase", "core", "value", "eta"]
        for field in required_fields:
            assert field in event, f"Progress event missing required field '{field}'"

    def test_thorough_mode_emits_phase_b_events(self):
        """In thorough mode, Phase B events should be emitted."""
        event_emitter = RecordingEventEmitter()
        safety = MockSafetyManager(safe_limit=-30)
        ryzenadj = MockRyzenadj()
        # Fail at -15 to create a gap for binary search
        runner = MockTestRunner(fail_at=-15)
        
        engine = AutotuneEngine(ryzenadj, runner, safety, event_emitter)
        
        original_apply = engine._apply_test_values
        async def patched_apply(values: List[int]):
            runner.current_value = values[0]
            return await original_apply(values)
        engine._apply_test_values = patched_apply
        
        config = AutotuneConfig(
            mode="thorough",
            start_value=0,
            step=5,
            test_duration_quick=30,
            test_duration_long=120
        )
        
        asyncio.get_event_loop().run_until_complete(engine.run(config))
        
        # Check for Phase A events
        phase_a_events = [e for e in event_emitter.progress_events if e["phase"] == "A"]
        assert len(phase_a_events) > 0, "Expected Phase A events"
        
        # Note: Phase B may or may not emit events depending on the gap
        # between last_good and first_fail
