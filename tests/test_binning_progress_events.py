"""Property tests for binning progress events.

Feature: decktune-critical-fixes, Property 7: Binning Progress Events
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6

Property 7: Полнота событий прогресса binning
For each binning iteration, the binning_progress event must contain all required fields:
current_value, iteration, last_stable, eta, max_iterations, percent_complete
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import List


# Strategy for binning progress values
iteration_strategy = st.integers(min_value=1, max_value=50)
max_iterations_strategy = st.integers(min_value=1, max_value=50)
current_value_strategy = st.integers(min_value=-100, max_value=0)
last_stable_strategy = st.integers(min_value=-100, max_value=0)
eta_strategy = st.integers(min_value=0, max_value=3600)


class MockEmitter:
    """Mock emitter that captures events."""
    
    def __init__(self):
        self.events: List[dict] = []
    
    async def __call__(self, event_type: str, data: dict):
        self.events.append({"type": event_type, "data": data})


class TestBinningProgressEvents:
    """Property 7: Полнота событий прогресса binning
    
    For each binning iteration, the binning_progress event must contain all required fields:
    current_value, iteration, last_stable, eta, max_iterations, percent_complete
    
    Feature: decktune-critical-fixes, Property 7: Binning Progress Events
    Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
    """

    @given(
        iteration=iteration_strategy,
        max_iterations=max_iterations_strategy,
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        eta=eta_strategy
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_progress_event_contains_all_required_fields(
        self,
        iteration: int,
        max_iterations: int,
        current_value: int,
        last_stable: int,
        eta: int
    ):
        """
        Property 7: Progress event contains all required fields.
        
        Feature: decktune-critical-fixes, Property 7: Binning Progress Events
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**
        """
        from backend.api.events import EventEmitter
        
        # Create emitter with mock
        mock_emit = MockEmitter()
        emitter = EventEmitter(mock_emit)
        
        # Emit progress event
        await emitter.emit_binning_progress(
            current_value=current_value,
            iteration=iteration,
            last_stable=last_stable,
            eta=eta,
            max_iterations=max_iterations
        )
        
        # Verify event was emitted
        assert len(mock_emit.events) == 1, "Should emit exactly one event"
        
        event = mock_emit.events[0]
        assert event["type"] == "server_event", f"Event type should be 'server_event', got {event['type']}"
        
        data = event["data"]["data"]
        
        # Verify all required fields are present
        required_fields = ["current_value", "iteration", "last_stable", "eta", "max_iterations", "percent_complete"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field values
        assert data["current_value"] == current_value
        assert data["iteration"] == iteration
        assert data["last_stable"] == last_stable
        assert data["eta"] == eta
        assert data["max_iterations"] == max_iterations

    @given(
        iteration=iteration_strategy,
        max_iterations=max_iterations_strategy
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_percent_complete_calculation(
        self,
        iteration: int,
        max_iterations: int
    ):
        """
        Property 7: percent_complete is correctly calculated.
        
        Feature: decktune-critical-fixes, Property 7: Binning Progress Events
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**
        """
        from backend.api.events import EventEmitter
        
        # Ensure iteration <= max_iterations for valid percentage
        if iteration > max_iterations:
            iteration = max_iterations
        
        # Create emitter with mock
        mock_emit = MockEmitter()
        emitter = EventEmitter(mock_emit)
        
        # Emit progress event
        await emitter.emit_binning_progress(
            current_value=-20,
            iteration=iteration,
            last_stable=-15,
            eta=60,
            max_iterations=max_iterations
        )
        
        # Verify percent_complete calculation
        event = mock_emit.events[0]
        data = event["data"]["data"]
        
        expected_percent = (iteration / max_iterations) * 100 if max_iterations > 0 else 0
        assert abs(data["percent_complete"] - expected_percent) < 0.01, \
            f"percent_complete should be {expected_percent}, got {data['percent_complete']}"

    @pytest.mark.asyncio
    async def test_progress_event_known_values(self):
        """Test with known values for verification."""
        from backend.api.events import EventEmitter
        
        mock_emit = MockEmitter()
        emitter = EventEmitter(mock_emit)
        
        # Test case 1: 50% progress
        await emitter.emit_binning_progress(
            current_value=-25,
            iteration=10,
            last_stable=-20,
            eta=300,
            max_iterations=20
        )
        
        event = mock_emit.events[0]
        data = event["data"]["data"]
        
        assert data["current_value"] == -25
        assert data["iteration"] == 10
        assert data["last_stable"] == -20
        assert data["eta"] == 300
        assert data["max_iterations"] == 20
        assert data["percent_complete"] == 50.0
        
        # Test case 2: 100% progress
        mock_emit.events.clear()
        await emitter.emit_binning_progress(
            current_value=-50,
            iteration=20,
            last_stable=-45,
            eta=0,
            max_iterations=20
        )
        
        event = mock_emit.events[0]
        data = event["data"]["data"]
        
        assert data["percent_complete"] == 100.0

    @given(
        iteration=iteration_strategy,
        max_iterations=max_iterations_strategy,
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        eta=eta_strategy
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_progress_event_field_types(
        self,
        iteration: int,
        max_iterations: int,
        current_value: int,
        last_stable: int,
        eta: int
    ):
        """
        Property 7: Progress event fields have correct types.
        
        Feature: decktune-critical-fixes, Property 7: Binning Progress Events
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**
        """
        from backend.api.events import EventEmitter
        
        mock_emit = MockEmitter()
        emitter = EventEmitter(mock_emit)
        
        await emitter.emit_binning_progress(
            current_value=current_value,
            iteration=iteration,
            last_stable=last_stable,
            eta=eta,
            max_iterations=max_iterations
        )
        
        event = mock_emit.events[0]
        data = event["data"]["data"]
        
        # Verify field types
        assert isinstance(data["current_value"], int), "current_value should be int"
        assert isinstance(data["iteration"], int), "iteration should be int"
        assert isinstance(data["last_stable"], int), "last_stable should be int"
        assert isinstance(data["eta"], int), "eta should be int"
        assert isinstance(data["max_iterations"], int), "max_iterations should be int"
        assert isinstance(data["percent_complete"], (int, float)), "percent_complete should be numeric"
