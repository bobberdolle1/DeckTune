"""Property tests for progressive recovery first step.

Feature: decktune-3.0-automation, Property 5: Progressive recovery first step
Validates: Requirements 2.1

Property 5: Progressive recovery first step
For any instability detection (missed heartbeats), the first action SHALL be 
to reduce all undervolt values by exactly REDUCTION_STEP (5mV), clamped to 
not exceed 0mV.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple, Optional

from backend.core.safety import ProgressiveRecovery, RecoveryState, RecoveryStage


# Strategy for valid undervolt values (negative integers, typical range -100 to 0)
valid_undervolt_value = st.integers(min_value=-100, max_value=0)
valid_undervolt_values = st.lists(valid_undervolt_value, min_size=4, max_size=4)


class MockValueStore:
    """Mock store for current and LKG values."""
    
    def __init__(self, current_values: List[int], lkg_values: List[int]):
        self.current_values = current_values.copy()
        self.lkg_values = lkg_values.copy()
        self.applied_values: Optional[List[int]] = None
        self.apply_success = True
        self.apply_error: Optional[str] = None
    
    def get_current(self) -> List[int]:
        return self.current_values.copy()
    
    def apply(self, values: List[int]) -> Tuple[bool, Optional[str]]:
        if self.apply_success:
            self.applied_values = values.copy()
            self.current_values = values.copy()
            return True, None
        return False, self.apply_error
    
    def get_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def save_lkg(self, values: List[int]) -> None:
        self.lkg_values = values.copy()


def create_progressive_recovery(
    current_values: List[int],
    lkg_values: List[int]
) -> Tuple[ProgressiveRecovery, MockValueStore]:
    """Create a ProgressiveRecovery instance with mock store."""
    store = MockValueStore(current_values, lkg_values)
    recovery = ProgressiveRecovery(
        get_current_values=store.get_current,
        apply_values=store.apply,
        get_lkg=store.get_lkg,
        save_lkg=store.save_lkg
    )
    return recovery, store


class TestProgressiveRecoveryFirstStep:
    """Property 5: Progressive recovery first step
    
    For any instability detection (missed heartbeats), the first action SHALL be 
    to reduce all undervolt values by exactly REDUCTION_STEP (5mV), clamped to 
    not exceed 0mV.
    
    Feature: decktune-3.0-automation, Property 5: Progressive recovery first step
    Validates: Requirements 2.1
    """

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_first_instability_reduces_by_reduction_step(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """First instability detection reduces values by exactly REDUCTION_STEP."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability detection
        success, error, state = recovery.on_instability_detected()
        
        # Should succeed
        assert success, f"First instability detection should succeed: {error}"
        
        # State should be REDUCED
        assert state.stage == RecoveryStage.REDUCED, \
            f"State should be REDUCED, got {state.stage}"
        
        # Applied values should be reduced by exactly REDUCTION_STEP
        expected_reduced = [min(v + ProgressiveRecovery.REDUCTION_STEP, 0) for v in current_values]
        assert store.applied_values == expected_reduced, \
            f"Applied values {store.applied_values} should equal expected {expected_reduced}"

    @given(current_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_reduction_clamped_to_zero(self, current_values: List[int]):
        """Reduced values are clamped to not exceed 0mV."""
        recovery, store = create_progressive_recovery(current_values, [0, 0, 0, 0])
        
        # Trigger instability detection
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        
        # All applied values should be <= 0
        for i, v in enumerate(store.applied_values):
            assert v <= 0, f"Value at index {i} should be <= 0, got {v}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_original_values_preserved_in_state(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Original values are preserved in recovery state."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability detection
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        
        # Original values should be preserved
        assert state.original_values == current_values, \
            f"Original values {state.original_values} should equal {current_values}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_reduced_values_stored_in_state(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Reduced values are stored in recovery state."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability detection
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        
        # Reduced values should match applied values
        assert state.reduced_values == store.applied_values, \
            f"State reduced values {state.reduced_values} should equal applied {store.applied_values}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_heartbeat_count_starts_at_zero(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Heartbeat count starts at zero after first instability."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability detection
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        
        # Heartbeat count should be 0
        assert state.heartbeats_since_reduction == 0, \
            f"Heartbeat count should be 0, got {state.heartbeats_since_reduction}"

    def test_values_near_zero_clamp_correctly(self):
        """Values close to zero are clamped correctly after reduction."""
        # Values that would exceed 0 after adding REDUCTION_STEP
        current_values = [-3, -2, -1, 0]
        recovery, store = create_progressive_recovery(current_values, [0, 0, 0, 0])
        
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        
        # Expected: [-3+5=2->0, -2+5=3->0, -1+5=4->0, 0+5=5->0]
        expected = [0, 0, 0, 0]
        assert store.applied_values == expected, \
            f"Applied values {store.applied_values} should be clamped to {expected}"

    def test_reduction_amount_is_exactly_5mv(self):
        """Reduction amount is exactly 5mV (REDUCTION_STEP constant)."""
        assert ProgressiveRecovery.REDUCTION_STEP == 5, \
            f"REDUCTION_STEP should be 5, got {ProgressiveRecovery.REDUCTION_STEP}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_reduction_amount_stored_in_state(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Reduction amount is stored in state."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        success, error, state = recovery.on_instability_detected()
        
        assert success, f"Should succeed: {error}"
        assert state.reduction_amount == ProgressiveRecovery.REDUCTION_STEP, \
            f"Reduction amount should be {ProgressiveRecovery.REDUCTION_STEP}, got {state.reduction_amount}"
