"""Property tests for progressive recovery escalation.

Feature: decktune-3.0-automation, Property 7: Recovery escalation
Validates: Requirements 2.3

Property 7: Recovery escalation
For any progressive recovery where instability persists after STABILITY_HEARTBEATS, 
the system SHALL perform full rollback to LKG values.
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import List, Tuple, Optional

from backend.core.safety import ProgressiveRecovery, RecoveryState, RecoveryStage


# Strategy for valid undervolt values
valid_undervolt_value = st.integers(min_value=-100, max_value=0)
valid_undervolt_values = st.lists(valid_undervolt_value, min_size=4, max_size=4)


class MockValueStore:
    """Mock store for current and LKG values."""
    
    def __init__(self, current_values: List[int], lkg_values: List[int]):
        self.current_values = current_values.copy()
        self.lkg_values = lkg_values.copy()
        self.applied_values: Optional[List[int]] = None
        self.apply_history: List[List[int]] = []
    
    def get_current(self) -> List[int]:
        return self.current_values.copy()
    
    def apply(self, values: List[int]) -> Tuple[bool, Optional[str]]:
        self.applied_values = values.copy()
        self.apply_history.append(values.copy())
        self.current_values = values.copy()
        return True, None
    
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


class TestProgressiveRecoveryEscalation:
    """Property 7: Recovery escalation
    
    For any progressive recovery where instability persists after STABILITY_HEARTBEATS, 
    the system SHALL perform full rollback to LKG values.
    
    Feature: decktune-3.0-automation, Property 7: Recovery escalation
    Validates: Requirements 2.3
    """

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_second_instability_triggers_full_rollback(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Second instability detection triggers full rollback to LKG."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # First instability - should reduce values
        success1, error1, state1 = recovery.on_instability_detected()
        assert success1
        assert state1.stage == RecoveryStage.REDUCED
        
        # Second instability (persists) - should rollback to LKG
        success2, error2, state2 = recovery.on_instability_detected()
        
        assert success2, f"Full rollback should succeed: {error2}"
        assert state2.stage == RecoveryStage.ROLLBACK
        assert store.applied_values == lkg_values, \
            f"Applied values {store.applied_values} should equal LKG {lkg_values}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_rollback_applies_exact_lkg_values(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Full rollback applies exactly the LKG values."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger reduction then escalation
        recovery.on_instability_detected()
        recovery.on_instability_detected()
        
        # Last applied values should be exactly LKG
        assert store.applied_values == lkg_values

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_state_is_rollback_after_escalation(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """State is ROLLBACK after escalation."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger reduction then escalation
        recovery.on_instability_detected()
        _, _, state = recovery.on_instability_detected()
        
        assert state.stage == RecoveryStage.ROLLBACK

    @given(
        current_values=valid_undervolt_values, 
        lkg_values=valid_undervolt_values,
        heartbeats_before_instability=st.integers(min_value=0, max_value=1)
    )
    @settings(max_examples=100)
    def test_instability_before_stability_confirmed_triggers_rollback(
        self, 
        current_values: List[int], 
        lkg_values: List[int],
        heartbeats_before_instability: int
    ):
        """Instability before STABILITY_HEARTBEATS triggers rollback."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # First instability - reduce
        recovery.on_instability_detected()
        
        # Some heartbeats (but not enough for stability)
        for _ in range(heartbeats_before_instability):
            recovery.on_heartbeat()
        
        # Another instability before stability confirmed
        success, error, state = recovery.on_instability_detected()
        
        assert success
        assert state.stage == RecoveryStage.ROLLBACK
        assert store.applied_values == lkg_values

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_apply_history_shows_reduction_then_rollback(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Apply history shows reduction first, then rollback to LKG."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger reduction then escalation
        recovery.on_instability_detected()
        recovery.on_instability_detected()
        
        # Should have 2 apply calls
        assert len(store.apply_history) == 2
        
        # First should be reduced values
        expected_reduced = [min(v + ProgressiveRecovery.REDUCTION_STEP, 0) for v in current_values]
        assert store.apply_history[0] == expected_reduced
        
        # Second should be LKG
        assert store.apply_history[1] == lkg_values

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_original_values_preserved_through_escalation(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Original values are preserved through escalation."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger reduction
        _, _, state1 = recovery.on_instability_detected()
        original_from_reduction = state1.original_values
        
        # Trigger escalation
        _, _, state2 = recovery.on_instability_detected()
        
        # Original values should be preserved
        assert state2.original_values == original_from_reduction == current_values

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_third_instability_still_applies_lkg(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Third instability detection still applies LKG values."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # First instability - reduce
        recovery.on_instability_detected()
        
        # Second instability - rollback
        recovery.on_instability_detected()
        
        # Third instability - should still apply LKG
        success, error, state = recovery.on_instability_detected()
        
        assert success
        assert store.applied_values == lkg_values

    def test_escalation_after_one_heartbeat(self):
        """Escalation works correctly after exactly one heartbeat."""
        current_values = [-30, -30, -30, -30]
        lkg_values = [-20, -20, -20, -20]
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # First instability - reduce
        recovery.on_instability_detected()
        
        # One heartbeat (not enough for stability)
        recovery.on_heartbeat()
        assert recovery.state.heartbeats_since_reduction == 1
        
        # Another instability - should escalate
        success, error, state = recovery.on_instability_detected()
        
        assert success
        assert state.stage == RecoveryStage.ROLLBACK
        assert store.applied_values == lkg_values

    def test_escalation_resets_heartbeat_count(self):
        """Escalation resets heartbeat count to 0."""
        current_values = [-30, -30, -30, -30]
        lkg_values = [-20, -20, -20, -20]
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # First instability - reduce
        recovery.on_instability_detected()
        
        # One heartbeat
        recovery.on_heartbeat()
        
        # Escalate
        _, _, state = recovery.on_instability_detected()
        
        assert state.heartbeats_since_reduction == 0
