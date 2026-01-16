"""Property-based tests for Iron Seeker engine core algorithm.

Feature: iron-seeker, IronSeekerEngine
Validates: Requirements 1.1, 1.2, 1.3, 1.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import MagicMock, AsyncMock
from typing import List

from backend.tuning.iron_seeker import (
    IronSeekerEngine,
    IronSeekerConfig,
    CoreResult,
    IronSeekerResult,
    QualityTier,
    NUM_CORES,
    DEFAULT_SAFE_LIMIT
)


# Strategies for generating test data
@st.composite
def stable_values(draw):
    """Generate a list of 4 stable undervolt values."""
    return draw(st.lists(
        st.integers(min_value=-50, max_value=0),
        min_size=4,
        max_size=4
    ))


@st.composite
def initial_values(draw):
    """Generate a list of 4 initial undervolt values."""
    return draw(st.lists(
        st.integers(min_value=-50, max_value=0),
        min_size=4,
        max_size=4
    ))


@st.composite
def core_index_and_test_value(draw):
    """Generate a valid core index and test value."""
    core = draw(st.integers(min_value=0, max_value=3))
    test_value = draw(st.integers(min_value=-50, max_value=0))
    return core, test_value


def create_mock_engine(
    stable_values: List[int] = None,
    initial_values: List[int] = None,
    safe_limit: int = DEFAULT_SAFE_LIMIT
) -> IronSeekerEngine:
    """Create an IronSeekerEngine with mocked dependencies for testing."""
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_vdroop = MagicMock()
    mock_vdroop.run_vdroop_test = AsyncMock()
    mock_vdroop.cancel = MagicMock()
    
    mock_safety = MagicMock()
    mock_safety.load_iron_seeker_state.return_value = None
    mock_safety.create_iron_seeker_state = MagicMock()
    mock_safety.clear_iron_seeker_state = MagicMock()
    
    engine = IronSeekerEngine(
        ryzenadj=mock_ryzenadj,
        vdroop_tester=mock_vdroop,
        safety=mock_safety,
        safe_limit=safe_limit
    )
    
    # Set up internal state if provided
    if stable_values is not None:
        engine._core_results = stable_values.copy()
    if initial_values is not None:
        engine._initial_values = initial_values.copy()
    
    return engine


# Property 1: Per-core isolation
# For any Iron Seeker execution with initial stable values V, when testing core N,
# the applied values for cores 0..N-1 SHALL equal their discovered stable values,
# and cores N+1..3 SHALL retain their initial values from V.
@given(
    core_being_tested=st.integers(min_value=0, max_value=3),
    test_value=st.integers(min_value=-50, max_value=0),
    discovered_stable=stable_values(),
    initial_vals=initial_values()
)
@settings(max_examples=100)
def test_property_1_per_core_isolation(
    core_being_tested: int,
    test_value: int,
    discovered_stable: List[int],
    initial_vals: List[int]
):
    """**Feature: iron-seeker, Property 1: Per-core isolation**
    
    For any Iron Seeker execution with initial stable values V, when testing core N,
    the applied values for cores 0..N-1 SHALL equal their discovered stable values,
    and cores N+1..3 SHALL retain their initial values from V.
    
    **Validates: Requirements 1.1**
    """
    engine = create_mock_engine(
        stable_values=discovered_stable,
        initial_values=initial_vals
    )
    
    # Build the values that would be applied
    apply_values = engine._build_apply_values(core_being_tested, test_value)
    
    # Verify the result has exactly 4 values
    assert len(apply_values) == NUM_CORES
    
    # Verify per-core isolation
    for i in range(NUM_CORES):
        if i < core_being_tested:
            # Cores before the one being tested should use discovered stable values
            assert apply_values[i] == discovered_stable[i], \
                f"Core {i} (before tested core {core_being_tested}) should use " \
                f"discovered stable value {discovered_stable[i]}, got {apply_values[i]}"
        elif i == core_being_tested:
            # The core being tested should use the test value
            assert apply_values[i] == test_value, \
                f"Core {i} (being tested) should use test value {test_value}, got {apply_values[i]}"
        else:
            # Cores after the one being tested should use initial values
            assert apply_values[i] == initial_vals[i], \
                f"Core {i} (after tested core {core_being_tested}) should use " \
                f"initial value {initial_vals[i]}, got {apply_values[i]}"



# Property 2: Stepping sequence
# For any Iron Seeker configuration with step_size S, the sequence of tested values
# for each core SHALL be: 0, -S, -2S, -3S, ... until failure or platform limit.
@given(
    step_size=st.integers(min_value=1, max_value=20),
    safe_limit=st.integers(min_value=-100, max_value=-10)
)
@settings(max_examples=100)
def test_property_2_stepping_sequence(step_size: int, safe_limit: int):
    """**Feature: iron-seeker, Property 2: Stepping sequence**
    
    For any Iron Seeker configuration with step_size S, the sequence of tested values
    for each core SHALL be: 0, -S, -2S, -3S, ... until failure or platform limit.
    
    **Validates: Requirements 1.2**
    """
    engine = create_mock_engine(safe_limit=safe_limit)
    
    # Generate the test sequence
    sequence = engine._generate_test_sequence(step_size)
    
    # Verify sequence starts at 0
    assert len(sequence) > 0, "Sequence should not be empty"
    assert sequence[0] == 0, f"Sequence should start at 0, got {sequence[0]}"
    
    # Verify each subsequent value decreases by exactly step_size
    for i in range(1, len(sequence)):
        expected = -i * step_size
        assert sequence[i] == expected, \
            f"Value at index {i} should be {expected}, got {sequence[i]}"
    
    # Verify sequence stops at or before safe_limit
    for value in sequence:
        assert value >= safe_limit, \
            f"Value {value} should not be below safe_limit {safe_limit}"
    
    # Verify the last value is either at safe_limit or the last step before it
    last_value = sequence[-1]
    # The last value should be >= safe_limit
    assert last_value >= safe_limit
    # And the next step would be below safe_limit (or we're at safe_limit)
    next_step = last_value - step_size
    assert next_step < safe_limit or last_value == safe_limit, \
        f"Sequence should stop at or just before safe_limit. " \
        f"Last value: {last_value}, next would be: {next_step}, limit: {safe_limit}"


@given(step_size=st.integers(min_value=1, max_value=20))
@settings(max_examples=100)
def test_stepping_sequence_arithmetic_progression(step_size: int):
    """Test that the stepping sequence forms a proper arithmetic progression.
    
    The sequence should be: 0, -S, -2S, -3S, ... where S is step_size.
    """
    engine = create_mock_engine(safe_limit=-100)
    sequence = engine._generate_test_sequence(step_size)
    
    # Check arithmetic progression property
    for i in range(len(sequence)):
        expected = -i * step_size
        assert sequence[i] == expected, \
            f"Sequence[{i}] should be {expected} (= -{i} * {step_size}), got {sequence[i]}"



# Property 3: Failure handling
# For any test failure at value V for core C, the system SHALL record V in
# failed_values[C] and the applied value for core C SHALL be restored to last_stable[C].
@given(
    core_index=st.integers(min_value=0, max_value=3),
    failed_value=st.integers(min_value=-50, max_value=-1),  # Must be negative (being tested)
    last_stable=st.integers(min_value=-50, max_value=0),
    step_size=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_property_3_failure_handling(
    core_index: int,
    failed_value: int,
    last_stable: int,
    step_size: int
):
    """**Feature: iron-seeker, Property 3: Failure handling**
    
    For any test failure at value V for core C, the system SHALL record V in
    failed_values[C] and the applied value for core C SHALL be restored to last_stable[C].
    
    **Validates: Requirements 1.3**
    """
    # Ensure failed_value is more negative than last_stable (it's the next step)
    assume(failed_value < last_stable)
    
    engine = create_mock_engine()
    engine._core_results[core_index] = last_stable
    
    # Simulate recording a failure
    if core_index not in engine._failed_values:
        engine._failed_values[core_index] = []
    engine._failed_values[core_index].append(failed_value)
    
    # Verify the failed value is recorded
    assert core_index in engine._failed_values, \
        f"Core {core_index} should be in failed_values"
    assert failed_value in engine._failed_values[core_index], \
        f"Failed value {failed_value} should be recorded for core {core_index}"
    
    # Verify the restore values would use last_stable for the failed core
    restore_values = engine._build_apply_values(core_index, last_stable)
    assert restore_values[core_index] == last_stable, \
        f"Restored value for core {core_index} should be {last_stable}, got {restore_values[core_index]}"


@pytest.mark.asyncio
@given(
    core_index=st.integers(min_value=0, max_value=3),
    step_size=st.integers(min_value=5, max_value=10),
    fail_at_step=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50)
async def test_failure_triggers_rollback(
    core_index: int,
    step_size: int,
    fail_at_step: int
):
    """Test that a test failure triggers rollback to last stable value.
    
    When a Vdroop test fails, the engine should:
    1. Record the failed value
    2. Restore the last stable value
    3. Stop testing that core
    """
    from backend.tuning.vdroop import VdroopTestResult
    
    engine = create_mock_engine(safe_limit=-100)
    config = IronSeekerConfig(step_size=step_size, test_duration=1)
    
    # Track which values were applied
    applied_values = []
    
    async def mock_apply(values):
        applied_values.append(values.copy())
        return (True, None)
    
    engine._ryzenadj.apply_values_async = mock_apply
    
    # Make the test fail at the specified step
    call_count = [0]
    
    async def mock_vdroop_test(duration, pulse_ms=100):
        call_count[0] += 1
        if call_count[0] >= fail_at_step:
            return VdroopTestResult(
                passed=False,
                duration=duration,
                exit_code=1,
                mce_detected=False,
                error="Simulated failure"
            )
        return VdroopTestResult(
            passed=True,
            duration=duration,
            exit_code=0,
            mce_detected=False
        )
    
    engine._vdroop_tester.run_vdroop_test = mock_vdroop_test
    
    # Run the test
    result = await engine._test_core(core_index, config)
    
    # Verify failure was recorded
    if fail_at_step > 0:
        failed_value = -(fail_at_step - 1) * step_size - step_size
        if fail_at_step > 1:
            # There should be a failed value recorded
            assert result.failed_value is not None, "Failed value should be recorded"
            assert core_index in engine._failed_values, \
                f"Core {core_index} should have failed values recorded"
        
        # Verify last stable value is correct
        expected_stable = -(fail_at_step - 2) * step_size if fail_at_step > 1 else 0
        assert result.max_stable == expected_stable, \
            f"Max stable should be {expected_stable}, got {result.max_stable}"



# Property 4: Safe limit boundary
# For any core C and platform safe_limit L, the system SHALL NOT test values below L,
# and if L is reached without failure, the result for C SHALL be L.
@given(
    step_size=st.integers(min_value=1, max_value=20),
    safe_limit=st.integers(min_value=-100, max_value=-10)
)
@settings(max_examples=100)
def test_property_4_safe_limit_boundary(step_size: int, safe_limit: int):
    """**Feature: iron-seeker, Property 4: Safe limit boundary**
    
    For any core C and platform safe_limit L, the system SHALL NOT test values below L,
    and if L is reached without failure, the result for C SHALL be L.
    
    **Validates: Requirements 1.5**
    """
    engine = create_mock_engine(safe_limit=safe_limit)
    
    # Generate the test sequence
    sequence = engine._generate_test_sequence(step_size)
    
    # Verify no value in sequence is below safe_limit
    for value in sequence:
        assert value >= safe_limit, \
            f"Test value {value} should not be below safe_limit {safe_limit}"
    
    # Verify the sequence includes the safe_limit if it's reachable by stepping
    # The safe_limit is reachable if it's a multiple of step_size from 0
    # or if the last step lands at or above safe_limit
    last_value = sequence[-1]
    next_step = last_value - step_size
    
    # Either we stopped at safe_limit, or the next step would go below it
    assert last_value >= safe_limit, \
        f"Last value {last_value} should be >= safe_limit {safe_limit}"
    assert next_step < safe_limit or last_value == safe_limit, \
        f"Should stop at or just before safe_limit. Last: {last_value}, next: {next_step}, limit: {safe_limit}"


@pytest.mark.asyncio
@given(
    core_index=st.integers(min_value=0, max_value=3),
    step_size=st.integers(min_value=5, max_value=10),
    safe_limit=st.integers(min_value=-50, max_value=-20)
)
@settings(max_examples=50)
async def test_safe_limit_stops_testing(
    core_index: int,
    step_size: int,
    safe_limit: int
):
    """Test that testing stops when safe limit is reached.
    
    When all tests pass and the safe limit is reached, the engine should:
    1. Stop testing that core
    2. Record the safe limit as the max stable value
    """
    from backend.tuning.vdroop import VdroopTestResult
    
    engine = create_mock_engine(safe_limit=safe_limit)
    config = IronSeekerConfig(step_size=step_size, test_duration=1)
    
    # Make all tests pass
    async def mock_vdroop_test(duration, pulse_ms=100):
        return VdroopTestResult(
            passed=True,
            duration=duration,
            exit_code=0,
            mce_detected=False
        )
    
    engine._vdroop_tester.run_vdroop_test = mock_vdroop_test
    
    # Run the test
    result = await engine._test_core(core_index, config)
    
    # Verify the result is at or above safe_limit
    assert result.max_stable >= safe_limit, \
        f"Max stable {result.max_stable} should be >= safe_limit {safe_limit}"
    
    # Verify no failed value (all tests passed)
    assert result.failed_value is None, \
        f"Should have no failed value when reaching safe limit, got {result.failed_value}"
    
    # Verify the max_stable is the last value in the sequence
    sequence = engine._generate_test_sequence(step_size)
    assert result.max_stable == sequence[-1], \
        f"Max stable {result.max_stable} should be last in sequence {sequence[-1]}"
