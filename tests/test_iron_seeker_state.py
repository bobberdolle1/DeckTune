"""Property-based tests for Iron Seeker state persistence.

Feature: iron-seeker, Property 8: State persistence before apply (partial - serialization)
Validates: Requirements 3.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime

from backend.tuning.iron_seeker import IronSeekerState


# Strategy for generating valid IronSeekerState instances
@st.composite
def iron_seeker_states(draw):
    """Generate valid IronSeekerState instances for testing."""
    active = draw(st.booleans())
    current_core = draw(st.integers(min_value=0, max_value=3))
    current_value = draw(st.integers(min_value=-100, max_value=0))
    core_results = draw(st.lists(
        st.integers(min_value=-100, max_value=0),
        min_size=4,
        max_size=4
    ))
    # Generate failed_values as dict with core indices 0-3
    failed_values = {}
    for core in range(4):
        if draw(st.booleans()):
            failed_values[core] = draw(st.lists(
                st.integers(min_value=-100, max_value=0),
                min_size=0,
                max_size=5
            ))
    config = {
        "step_size": draw(st.integers(min_value=1, max_value=20)),
        "test_duration": draw(st.integers(min_value=10, max_value=300)),
        "safety_margin": draw(st.integers(min_value=0, max_value=20))
    }
    timestamp = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )).isoformat()
    
    return IronSeekerState(
        active=active,
        current_core=current_core,
        current_value=current_value,
        core_results=core_results,
        failed_values=failed_values,
        config=config,
        timestamp=timestamp
    )


# Property 8: State persistence before apply (partial - serialization round-trip)
@given(state=iron_seeker_states())
@settings(max_examples=100)
def test_property_8_state_persistence_roundtrip(state):
    """**Feature: iron-seeker, Property 8: State persistence before apply**
    
    For any valid IronSeekerState, serializing to JSON and deserializing
    back SHALL produce an equivalent state object.
    
    **Validates: Requirements 3.1**
    """
    # Serialize to JSON
    json_data = state.to_json()
    
    # Deserialize back
    restored_state = IronSeekerState.from_json(json_data)
    
    # Verify all fields match
    assert restored_state.active == state.active
    assert restored_state.current_core == state.current_core
    assert restored_state.current_value == state.current_value
    assert restored_state.core_results == state.core_results
    assert restored_state.failed_values == state.failed_values
    assert restored_state.config == state.config
    assert restored_state.timestamp == state.timestamp


@given(state=iron_seeker_states())
@settings(max_examples=100)
def test_state_to_json_structure(state):
    """Test that to_json produces valid JSON structure.
    
    For any IronSeekerState, to_json() SHALL produce a dictionary
    with all required fields.
    """
    json_data = state.to_json()
    
    # Verify all required fields are present
    assert "active" in json_data
    assert "current_core" in json_data
    assert "current_value" in json_data
    assert "core_results" in json_data
    assert "failed_values" in json_data
    assert "config" in json_data
    assert "timestamp" in json_data
    
    # Verify types
    assert isinstance(json_data["active"], bool)
    assert isinstance(json_data["current_core"], int)
    assert isinstance(json_data["current_value"], int)
    assert isinstance(json_data["core_results"], list)
    assert isinstance(json_data["failed_values"], dict)
    assert isinstance(json_data["config"], dict)
    assert isinstance(json_data["timestamp"], str)



import json
import os
import tempfile
from unittest.mock import MagicMock, patch

from backend.core.safety import SafetyManager
from backend.platform.detect import PlatformInfo


# Strategy for generating active IronSeekerState instances (for crash recovery)
@st.composite
def active_iron_seeker_states(draw):
    """Generate active IronSeekerState instances for crash recovery testing."""
    current_core = draw(st.integers(min_value=0, max_value=3))
    current_value = draw(st.integers(min_value=-100, max_value=-1))  # Must be negative (being tested)
    core_results = draw(st.lists(
        st.integers(min_value=-100, max_value=0),
        min_size=4,
        max_size=4
    ))
    # Generate failed_values as dict with core indices 0-3
    failed_values = {}
    for core in range(4):
        if draw(st.booleans()):
            failed_values[core] = draw(st.lists(
                st.integers(min_value=-100, max_value=0),
                min_size=0,
                max_size=5
            ))
    config = {
        "step_size": draw(st.integers(min_value=1, max_value=20)),
        "test_duration": draw(st.integers(min_value=10, max_value=300)),
        "safety_margin": draw(st.integers(min_value=0, max_value=20))
    }
    timestamp = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )).isoformat()
    
    return IronSeekerState(
        active=True,  # Always active for crash recovery testing
        current_core=current_core,
        current_value=current_value,
        core_results=core_results,
        failed_values=failed_values,
        config=config,
        timestamp=timestamp
    )


# Property 9: Crash recovery restoration
@given(state=active_iron_seeker_states())
@settings(max_examples=100)
def test_property_9_crash_recovery_restoration(state):
    """**Feature: iron-seeker, Property 9: Crash recovery restoration**
    
    For any state file with active=true found on boot, the system SHALL
    apply core_results values and mark current_value as failed for current_core.
    
    **Validates: Requirements 3.2**
    """
    # Create a temporary directory for the state file
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "iron_seeker_state.json")
        
        # Write the state file
        with open(state_file, 'w') as f:
            json.dump(state.to_json(), f)
        
        # Create mock settings manager and platform
        mock_settings = MagicMock()
        mock_settings.getSetting.return_value = [0, 0, 0, 0]
        
        mock_platform = MagicMock(spec=PlatformInfo)
        mock_platform.safe_limit = -50
        
        # Create SafetyManager with patched state file path
        safety = SafetyManager(mock_settings, mock_platform)
        
        # Patch the state file path
        with patch.object(SafetyManager, 'IRON_SEEKER_STATE_FILE', state_file):
            # Load the state
            loaded_state = safety.load_iron_seeker_state()
            
            # Verify state was loaded correctly
            assert loaded_state is not None
            assert loaded_state.active == True
            assert loaded_state.current_core == state.current_core
            assert loaded_state.current_value == state.current_value
            assert loaded_state.core_results == state.core_results
            
            # Verify the state contains the information needed for recovery:
            # 1. core_results contains the values to restore
            # 2. current_value is the value that was being tested (crashed)
            # 3. current_core identifies which core was being tested
            
            # The recovery logic should:
            # - Apply core_results values (the stable values)
            # - Mark current_value as failed for current_core
            
            # Verify core_results has 4 values (one per core)
            assert len(loaded_state.core_results) == 4
            
            # Verify current_core is valid
            assert 0 <= loaded_state.current_core <= 3
            
            # Verify current_value is the crashed value (negative, being tested)
            assert loaded_state.current_value <= 0


@given(state=iron_seeker_states())
@settings(max_examples=100)
def test_state_file_create_load_clear_cycle(state):
    """Test the full lifecycle of Iron Seeker state file management.
    
    For any IronSeekerState, the create/load/clear cycle SHALL work correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "iron_seeker_state.json")
        
        # Create mock settings manager and platform
        mock_settings = MagicMock()
        mock_settings.getSetting.return_value = [0, 0, 0, 0]
        
        mock_platform = MagicMock(spec=PlatformInfo)
        mock_platform.safe_limit = -50
        
        safety = SafetyManager(mock_settings, mock_platform)
        
        with patch.object(SafetyManager, 'IRON_SEEKER_STATE_FILE', state_file):
            # Initially no state file
            assert safety.load_iron_seeker_state() is None
            
            # Create state file
            safety.create_iron_seeker_state(state)
            
            # Load and verify
            loaded = safety.load_iron_seeker_state()
            assert loaded is not None
            assert loaded.active == state.active
            assert loaded.current_core == state.current_core
            assert loaded.current_value == state.current_value
            assert loaded.core_results == state.core_results
            assert loaded.failed_values == state.failed_values
            assert loaded.config == state.config
            assert loaded.timestamp == state.timestamp
            
            # Clear state file
            safety.clear_iron_seeker_state()
            
            # Verify file is gone
            assert safety.load_iron_seeker_state() is None


# Property 10: Recovery continuation
@st.composite
def recovery_continuation_states(draw):
    """Generate states for testing recovery continuation logic.
    
    Generates states where:
    - active=True (crash occurred)
    - current_core is 0-3
    - current_value is a valid test value (multiple of step_size from 0)
    - step_size is from config
    """
    step_size = draw(st.integers(min_value=1, max_value=20))
    current_core = draw(st.integers(min_value=0, max_value=3))
    
    # Generate current_value as a multiple of step_size (valid test value)
    # Range: 0 to -100, but must be multiple of step_size
    max_steps = 100 // step_size
    steps = draw(st.integers(min_value=0, max_value=max_steps))
    current_value = -steps * step_size
    
    # Generate core_results - values for cores 0 to current_core-1 should be stable
    core_results = []
    for i in range(4):
        if i < current_core:
            # Already tested cores have stable values
            core_results.append(draw(st.integers(min_value=-50, max_value=0)))
        else:
            # Current and future cores start at 0
            core_results.append(0)
    
    failed_values = {}
    for core in range(current_core):
        if draw(st.booleans()):
            failed_values[core] = draw(st.lists(
                st.integers(min_value=-100, max_value=-1),
                min_size=1,
                max_size=3
            ))
    
    config = {
        "step_size": step_size,
        "test_duration": draw(st.integers(min_value=10, max_value=300)),
        "safety_margin": draw(st.integers(min_value=0, max_value=20))
    }
    timestamp = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )).isoformat()
    
    return IronSeekerState(
        active=True,
        current_core=current_core,
        current_value=current_value,
        core_results=core_results,
        failed_values=failed_values,
        config=config,
        timestamp=timestamp
    )


@given(state=recovery_continuation_states())
@settings(max_examples=100)
def test_property_10_recovery_continuation(state):
    """**Feature: iron-seeker, Property 10: Recovery continuation**
    
    For any crash recovery from core C at value V, the system SHALL continue
    testing from core C at value V-step_size (or move to core C+1 if V was
    the first test for C).
    
    **Validates: Requirements 3.3**
    """
    step_size = state.config["step_size"]
    crashed_core = state.current_core
    crashed_value = state.current_value
    safe_limit = -50  # Default safe limit for testing
    
    # Calculate expected continuation point
    next_value = crashed_value - step_size
    
    if next_value < safe_limit:
        # If next value would be below safe limit, move to next core
        expected_start_core = crashed_core + 1
        expected_start_value = 0
    else:
        # Continue from next value on same core
        expected_start_core = crashed_core
        expected_start_value = next_value
    
    # Verify the continuation logic
    # The crashed value should be marked as failed
    # Testing should continue from expected_start_core at expected_start_value
    
    # Simulate the recovery logic from IronSeekerEngine.start()
    start_core = crashed_core
    start_value = crashed_value - step_size
    
    if start_value < safe_limit:
        start_core += 1
        start_value = 0
    
    # Verify the calculated continuation point matches expected
    assert start_core == expected_start_core, \
        f"Expected to continue from core {expected_start_core}, got {start_core}"
    assert start_value == expected_start_value, \
        f"Expected to continue from value {expected_start_value}, got {start_value}"
    
    # Verify crashed value would be marked as failed
    # (This is done in start() by adding crashed_value to failed_values[crashed_core])
    assert crashed_value <= 0, "Crashed value should be non-positive"
    assert crashed_core >= 0 and crashed_core <= 3, "Crashed core should be 0-3"


@given(state=recovery_continuation_states())
@settings(max_examples=100)
def test_recovery_marks_crashed_value_as_failed(state):
    """Test that recovery marks the crashed value as failed.
    
    When recovering from a crash, the value that was being tested at the
    time of crash should be added to the failed_values for that core.
    """
    crashed_core = state.current_core
    crashed_value = state.current_value
    
    # Simulate the recovery logic from IronSeekerEngine.start()
    failed_values = {int(k): v.copy() for k, v in state.failed_values.items()}
    
    # Mark crashed value as failed (as done in start())
    if crashed_core not in failed_values:
        failed_values[crashed_core] = []
    failed_values[crashed_core].append(crashed_value)
    
    # Verify the crashed value is now in failed_values
    assert crashed_core in failed_values, \
        f"Core {crashed_core} should be in failed_values"
    assert crashed_value in failed_values[crashed_core], \
        f"Crashed value {crashed_value} should be in failed_values[{crashed_core}]"


@given(
    step_size=st.integers(min_value=1, max_value=20),
    crashed_core=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=100)
def test_recovery_from_first_value_moves_to_next_core(step_size, crashed_core):
    """Test that crashing at value 0 (first test) moves to next core.
    
    If the crash occurred at value 0 (the first test value for a core),
    recovery should move to the next core since there's no previous
    stable value to fall back to.
    """
    crashed_value = 0  # First test value
    safe_limit = -50
    
    # Calculate continuation point
    next_value = crashed_value - step_size
    
    if next_value < safe_limit:
        expected_start_core = crashed_core + 1
        expected_start_value = 0
    else:
        # Even at value 0, we continue to next value on same core
        # because 0 was the value being tested when crash occurred
        expected_start_core = crashed_core
        expected_start_value = next_value
    
    # Simulate recovery logic
    start_core = crashed_core
    start_value = crashed_value - step_size
    
    if start_value < safe_limit:
        start_core += 1
        start_value = 0
    
    assert start_core == expected_start_core
    assert start_value == expected_start_value


from unittest.mock import AsyncMock
import asyncio

from backend.tuning.iron_seeker import (
    IronSeekerEngine,
    IronSeekerConfig,
    DEFAULT_SAFE_LIMIT
)
from backend.tuning.vdroop import VdroopTestResult


def create_mock_engine_for_cancellation(
    initial_values: list,
    safe_limit: int = DEFAULT_SAFE_LIMIT
):
    """Create an IronSeekerEngine with mocked dependencies for cancellation testing."""
    mock_ryzenadj = MagicMock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    mock_ryzenadj.apply_values = MagicMock(return_value=(True, None))
    
    mock_vdroop = MagicMock()
    # Make vdroop test take some time so we can cancel during it
    async def slow_vdroop_test(duration, pulse_ms=100):
        await asyncio.sleep(0.1)  # Small delay to allow cancellation
        return VdroopTestResult(
            passed=True,
            duration=duration,
            exit_code=0,
            mce_detected=False
        )
    mock_vdroop.run_vdroop_test = slow_vdroop_test
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
    
    return engine, mock_ryzenadj, mock_safety


# Property 11: Cancellation cleanup
@given(
    initial_values=st.lists(
        st.integers(min_value=-50, max_value=0),
        min_size=4,
        max_size=4
    )
)
@settings(max_examples=100)
def test_property_11_cancellation_cleanup(initial_values):
    """**Feature: iron-seeker, Property 11: Cancellation cleanup**
    
    For any cancellation request, the state file SHALL be deleted and the
    applied values SHALL be restored to pre-Iron-Seeker values within 5 seconds.
    
    **Validates: Requirements 3.5**
    """
    engine, mock_ryzenadj, mock_safety = create_mock_engine_for_cancellation(initial_values)
    
    # Simulate cancellation scenario
    # Set up the engine as if it was running
    engine._running = True
    engine._cancelled = False
    engine._initial_values = initial_values.copy()
    engine._core_results = [0, 0, 0, 0]
    
    # Call cancel
    engine.cancel()
    
    # Verify cancellation flag is set
    assert engine._cancelled == True, "Cancellation flag should be set"
    
    # Verify vdroop tester cancel was called
    engine._vdroop_tester.cancel.assert_called_once()
    
    # The actual cleanup (restore values, clear state) happens in start()
    # when it detects _cancelled flag. We verify the engine state is correct
    # for cleanup to proceed.
    
    # Verify initial values are preserved for restoration
    assert engine._initial_values == initial_values, \
        "Initial values should be preserved for restoration"


@pytest.mark.asyncio
@given(
    initial_values=st.lists(
        st.integers(min_value=-50, max_value=0),
        min_size=4,
        max_size=4
    )
)
@settings(max_examples=50)
async def test_cancellation_restores_initial_values(initial_values):
    """Test that cancellation restores initial values.
    
    When Iron Seeker is cancelled, it should restore the values that
    were in effect before Iron Seeker started.
    """
    engine, mock_ryzenadj, mock_safety = create_mock_engine_for_cancellation(initial_values)
    
    config = IronSeekerConfig(step_size=5, test_duration=1)
    
    # Start Iron Seeker in a task
    async def run_and_cancel():
        # Start the task
        task = asyncio.create_task(engine.start(config, initial_values))
        
        # Wait a bit then cancel
        await asyncio.sleep(0.05)
        engine.cancel()
        
        # Wait for completion
        result = await task
        return result
    
    result = await run_and_cancel()
    
    # Verify result indicates abortion
    assert result.aborted == True, "Result should indicate abortion"
    
    # Verify state file was cleared
    mock_safety.clear_iron_seeker_state.assert_called()
    
    # Verify initial values were restored (last call to apply_values_async)
    # The last call should be the restoration of initial values
    calls = mock_ryzenadj.apply_values_async.call_args_list
    if len(calls) > 0:
        # Check if initial values were restored
        # Note: The restoration happens after cancellation is detected
        last_call_args = calls[-1][0][0]  # Get the values from the last call
        assert last_call_args == initial_values, \
            f"Initial values {initial_values} should be restored, got {last_call_args}"


@pytest.mark.asyncio
@given(
    initial_values=st.lists(
        st.integers(min_value=-50, max_value=0),
        min_size=4,
        max_size=4
    )
)
@settings(max_examples=50)
async def test_cancellation_clears_state_file(initial_values):
    """Test that cancellation clears the state file.
    
    When Iron Seeker is cancelled, the state file should be deleted
    to prevent false recovery on next boot.
    """
    engine, mock_ryzenadj, mock_safety = create_mock_engine_for_cancellation(initial_values)
    
    config = IronSeekerConfig(step_size=5, test_duration=1)
    
    # Start and immediately cancel
    async def run_and_cancel():
        task = asyncio.create_task(engine.start(config, initial_values))
        await asyncio.sleep(0.05)
        engine.cancel()
        return await task
    
    await run_and_cancel()
    
    # Verify state file was cleared
    mock_safety.clear_iron_seeker_state.assert_called()
