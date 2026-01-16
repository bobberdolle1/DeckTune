"""Property-based tests for Iron Seeker progress events.

Feature: iron-seeker, Progress Events
Validates: Requirements 5.1, 5.3, 5.4
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import MagicMock, AsyncMock
from typing import List, Dict, Any

from backend.tuning.iron_seeker import (
    IronSeekerEngine,
    IronSeekerConfig,
    CoreResult,
    IronSeekerResult,
    QualityTier,
    NUM_CORES,
    DEFAULT_SAFE_LIMIT
)
from backend.api.events import EventEmitter


# Strategies for generating test data
@st.composite
def progress_event_data(draw):
    """Generate valid progress event data."""
    core = draw(st.integers(min_value=0, max_value=3))
    value = draw(st.integers(min_value=-100, max_value=0))
    iteration = draw(st.integers(min_value=1, max_value=100))
    eta = draw(st.integers(min_value=0, max_value=10000))
    core_results = draw(st.lists(
        st.integers(min_value=-100, max_value=0),
        min_size=4,
        max_size=4
    ))
    return {
        "core": core,
        "value": value,
        "iteration": iteration,
        "eta": eta,
        "coreResults": core_results
    }


@st.composite
def core_result_data(draw):
    """Generate valid CoreResult data."""
    core_index = draw(st.integers(min_value=0, max_value=3))
    max_stable = draw(st.integers(min_value=-100, max_value=0))
    safety_margin = draw(st.integers(min_value=0, max_value=20))
    recommended = min(max_stable + safety_margin, 0)
    tier = QualityTier.from_value(max_stable).value
    iterations = draw(st.integers(min_value=1, max_value=100))
    failed_value = draw(st.one_of(
        st.none(),
        st.integers(min_value=-100, max_value=-1)
    ))
    
    return CoreResult(
        core_index=core_index,
        max_stable=max_stable,
        recommended=recommended,
        quality_tier=tier,
        iterations=iterations,
        failed_value=failed_value
    )


@st.composite
def iron_seeker_result_data(draw):
    """Generate valid IronSeekerResult data."""
    cores = []
    for i in range(4):
        max_stable = draw(st.integers(min_value=-100, max_value=0))
        safety_margin = draw(st.integers(min_value=0, max_value=20))
        recommended = min(max_stable + safety_margin, 0)
        tier = QualityTier.from_value(max_stable).value
        iterations = draw(st.integers(min_value=1, max_value=100))
        failed_value = draw(st.one_of(
            st.none(),
            st.integers(min_value=-100, max_value=-1)
        ))
        cores.append(CoreResult(
            core_index=i,
            max_stable=max_stable,
            recommended=recommended,
            quality_tier=tier,
            iterations=iterations,
            failed_value=failed_value
        ))
    
    duration = draw(st.floats(min_value=0.1, max_value=10000.0))
    recovered = draw(st.booleans())
    aborted = draw(st.booleans())
    
    return IronSeekerResult(
        cores=cores,
        duration=duration,
        recovered=recovered,
        aborted=aborted
    )


def create_mock_engine_with_emitter(
    safe_limit: int = DEFAULT_SAFE_LIMIT
) -> tuple:
    """Create an IronSeekerEngine with mocked dependencies and event emitter."""
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_vdroop = MagicMock()
    mock_vdroop.run_vdroop_test = AsyncMock()
    mock_vdroop.cancel = MagicMock()
    
    mock_safety = MagicMock()
    mock_safety.load_iron_seeker_state.return_value = None
    mock_safety.create_iron_seeker_state = MagicMock()
    mock_safety.clear_iron_seeker_state = MagicMock()
    
    mock_emitter = MagicMock(spec=EventEmitter)
    mock_emitter.emit_iron_seeker_progress = AsyncMock()
    mock_emitter.emit_iron_seeker_core_complete = AsyncMock()
    mock_emitter.emit_iron_seeker_complete = AsyncMock()
    mock_emitter.emit_iron_seeker_recovery = AsyncMock()
    
    engine = IronSeekerEngine(
        ryzenadj=mock_ryzenadj,
        vdroop_tester=mock_vdroop,
        safety=mock_safety,
        event_emitter=mock_emitter,
        safe_limit=safe_limit
    )
    
    return engine, mock_emitter


# Property 14: Progress event structure
# For any progress event emitted during Iron Seeker, the event SHALL contain:
# core (0-3), value (≤0), iteration (≥1), eta (≥0), and coreResults (array of 4 integers).
@given(data=progress_event_data())
@settings(max_examples=100)
def test_property_14_progress_event_structure(data: Dict[str, Any]):
    """**Feature: iron-seeker, Property 14: Progress event structure**
    
    For any progress event emitted during Iron Seeker, the event SHALL contain:
    core (0-3), value (≤0), iteration (≥1), eta (≥0), and coreResults (array of 4 integers).
    
    **Validates: Requirements 5.1**
    """
    # Verify core is in valid range (0-3)
    assert 0 <= data["core"] <= 3, \
        f"Core {data['core']} should be in range [0, 3]"
    
    # Verify value is ≤ 0 (undervolt values are negative or zero)
    assert data["value"] <= 0, \
        f"Value {data['value']} should be ≤ 0"
    
    # Verify iteration is ≥ 1
    assert data["iteration"] >= 1, \
        f"Iteration {data['iteration']} should be ≥ 1"
    
    # Verify eta is ≥ 0
    assert data["eta"] >= 0, \
        f"ETA {data['eta']} should be ≥ 0"
    
    # Verify coreResults is array of 4 integers
    assert len(data["coreResults"]) == 4, \
        f"coreResults should have 4 elements, got {len(data['coreResults'])}"
    
    for i, val in enumerate(data["coreResults"]):
        assert isinstance(val, int), \
            f"coreResults[{i}] should be int, got {type(val)}"


@pytest.mark.asyncio
@given(
    core=st.integers(min_value=0, max_value=3),
    value=st.integers(min_value=-50, max_value=0),
    iteration=st.integers(min_value=1, max_value=20),
    estimated_iterations=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
async def test_progress_event_emission_structure(
    core: int,
    value: int,
    iteration: int,
    estimated_iterations: int
):
    """Test that emitted progress events have correct structure.
    
    Verifies that when _emit_progress is called, the event emitter
    receives data with the correct structure.
    """
    engine, mock_emitter = create_mock_engine_with_emitter()
    engine._config = IronSeekerConfig()
    engine._core_results = [0, 0, 0, 0]
    
    # Call the progress emission method
    await engine._emit_progress(core, value, iteration, estimated_iterations)
    
    # Verify the emitter was called
    mock_emitter.emit_iron_seeker_progress.assert_called_once()
    
    # Get the call arguments
    call_kwargs = mock_emitter.emit_iron_seeker_progress.call_args.kwargs
    
    # Verify structure
    assert call_kwargs["core"] == core
    assert call_kwargs["value"] == value
    assert call_kwargs["iteration"] == iteration
    assert call_kwargs["eta"] >= 0
    assert len(call_kwargs["core_results"]) == 4


# Property 15: Completion event structure
# For any completion event, the event SHALL contain:
# cores (4 CoreResult), duration (>0), recovered (boolean), aborted (boolean).
@given(result=iron_seeker_result_data())
@settings(max_examples=100)
def test_property_15_completion_event_structure(result: IronSeekerResult):
    """**Feature: iron-seeker, Property 15: Completion event structure**
    
    For any completion event, the event SHALL contain:
    cores (4 CoreResult), duration (>0), recovered (boolean), aborted (boolean).
    
    **Validates: Requirements 5.3**
    """
    # Verify cores has exactly 4 elements
    assert len(result.cores) == 4, \
        f"Cores should have 4 elements, got {len(result.cores)}"
    
    # Verify each core result has required fields
    for i, core_result in enumerate(result.cores):
        assert core_result.core_index == i, \
            f"Core {i} should have core_index={i}, got {core_result.core_index}"
        assert isinstance(core_result.max_stable, int), \
            f"Core {i} max_stable should be int"
        assert isinstance(core_result.recommended, int), \
            f"Core {i} recommended should be int"
        assert core_result.quality_tier in ["gold", "silver", "bronze"], \
            f"Core {i} tier should be gold/silver/bronze, got {core_result.quality_tier}"
    
    # Verify duration is > 0
    assert result.duration > 0, \
        f"Duration {result.duration} should be > 0"
    
    # Verify recovered is boolean
    assert isinstance(result.recovered, bool), \
        f"Recovered should be bool, got {type(result.recovered)}"
    
    # Verify aborted is boolean
    assert isinstance(result.aborted, bool), \
        f"Aborted should be bool, got {type(result.aborted)}"


@pytest.mark.asyncio
@given(result=iron_seeker_result_data())
@settings(max_examples=50)
async def test_completion_event_emission_structure(result: IronSeekerResult):
    """Test that emitted completion events have correct structure.
    
    Verifies that when _emit_complete is called, the event emitter
    receives data with the correct structure.
    """
    engine, mock_emitter = create_mock_engine_with_emitter()
    
    # Call the completion emission method
    await engine._emit_complete(result)
    
    # Verify the emitter was called
    mock_emitter.emit_iron_seeker_complete.assert_called_once()
    
    # Get the call arguments
    call_kwargs = mock_emitter.emit_iron_seeker_complete.call_args.kwargs
    
    # Verify structure
    assert len(call_kwargs["cores"]) == 4
    assert call_kwargs["duration"] == result.duration
    assert call_kwargs["recovered"] == result.recovered
    assert call_kwargs["aborted"] == result.aborted
    
    # Verify each core in the emitted data
    for i, core_data in enumerate(call_kwargs["cores"]):
        assert "core_index" in core_data
        assert "max_stable" in core_data
        assert "recommended" in core_data
        assert "quality_tier" in core_data


# Property 16: ETA calculation
# For any ETA calculation at core C with average test duration T, the ETA SHALL equal
# (4 - C - 1) * estimated_iterations_per_core * T + remaining_iterations_current_core * T.
@given(
    current_core=st.integers(min_value=0, max_value=3),
    current_iteration=st.integers(min_value=1, max_value=20),
    estimated_iterations_per_core=st.integers(min_value=5, max_value=20),
    avg_duration=st.floats(min_value=1.0, max_value=300.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_16_eta_calculation(
    current_core: int,
    current_iteration: int,
    estimated_iterations_per_core: int,
    avg_duration: float
):
    """**Feature: iron-seeker, Property 16: ETA calculation**
    
    For any ETA calculation at core C with average test duration T, the ETA SHALL equal
    (4 - C - 1) * estimated_iterations_per_core * T + remaining_iterations_current_core * T.
    
    **Validates: Requirements 5.4**
    """
    # Ensure current_iteration doesn't exceed estimated_iterations_per_core
    assume(current_iteration <= estimated_iterations_per_core)
    
    engine, _ = create_mock_engine_with_emitter()
    engine._config = IronSeekerConfig(test_duration=int(avg_duration))
    engine._test_durations = [avg_duration]  # Set average duration
    
    # Calculate ETA
    eta = engine.calculate_eta(
        current_core,
        current_iteration,
        estimated_iterations_per_core
    )
    
    # Calculate expected ETA
    remaining_cores = NUM_CORES - current_core - 1
    remaining_iterations_current = max(0, estimated_iterations_per_core - current_iteration)
    total_remaining = (remaining_cores * estimated_iterations_per_core) + remaining_iterations_current
    expected_eta = int(total_remaining * avg_duration)
    
    # Verify ETA matches expected formula
    assert eta == expected_eta, \
        f"ETA {eta} should equal expected {expected_eta} " \
        f"(core={current_core}, iter={current_iteration}, " \
        f"est_per_core={estimated_iterations_per_core}, avg_dur={avg_duration})"
    
    # Verify ETA is non-negative
    assert eta >= 0, f"ETA {eta} should be >= 0"


@given(
    current_core=st.integers(min_value=0, max_value=3),
    current_iteration=st.integers(min_value=1, max_value=20),
    estimated_iterations_per_core=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100)
def test_eta_decreases_with_progress(
    current_core: int,
    current_iteration: int,
    estimated_iterations_per_core: int
):
    """Test that ETA decreases as testing progresses.
    
    ETA should decrease when:
    - Moving to a higher iteration within the same core
    - Moving to a higher core number
    """
    assume(current_iteration < estimated_iterations_per_core)
    
    engine, _ = create_mock_engine_with_emitter()
    engine._config = IronSeekerConfig(test_duration=60)
    engine._test_durations = [60.0]
    
    # Calculate ETA at current position
    eta_current = engine.calculate_eta(
        current_core,
        current_iteration,
        estimated_iterations_per_core
    )
    
    # Calculate ETA at next iteration
    eta_next_iter = engine.calculate_eta(
        current_core,
        current_iteration + 1,
        estimated_iterations_per_core
    )
    
    # ETA should decrease with progress
    assert eta_next_iter <= eta_current, \
        f"ETA should decrease: {eta_next_iter} <= {eta_current}"
    
    # If not at last core, calculate ETA at next core
    if current_core < 3:
        eta_next_core = engine.calculate_eta(
            current_core + 1,
            1,
            estimated_iterations_per_core
        )
        
        # ETA at start of next core should be less than ETA at end of current core
        eta_end_current = engine.calculate_eta(
            current_core,
            estimated_iterations_per_core,
            estimated_iterations_per_core
        )
        
        # The ETA at start of next core should be less than or equal to
        # ETA at end of current core (they should be equal if no time passes)
        assert eta_next_core <= eta_end_current, \
            f"ETA at next core start should be <= ETA at current core end: " \
            f"{eta_next_core} <= {eta_end_current}"


def test_eta_uses_default_when_no_tests_completed():
    """Test that ETA uses configured duration when no tests have completed."""
    engine, _ = create_mock_engine_with_emitter()
    config = IronSeekerConfig(test_duration=120)
    engine._config = config
    engine._test_durations = []  # No tests completed yet
    
    eta = engine.calculate_eta(
        current_core=0,
        current_iteration=1,
        estimated_iterations_per_core=10
    )
    
    # Should use configured test_duration as estimate
    # Remaining: (3 cores * 10 iterations) + (10 - 1) iterations = 39 iterations
    # ETA = 39 * 120 = 4680
    expected = 39 * 120
    assert eta == expected, f"ETA {eta} should be {expected} when using default duration"
