"""Property tests for progressive recovery stability wait.

Feature: decktune-3.0-automation, Property 6: Recovery stability wait
Validates: Requirements 2.2

Property 6: Recovery stability wait
For any progressive recovery attempt, the system SHALL wait for exactly 
STABILITY_HEARTBEATS (2) heartbeat cycles before declaring success or 
proceeding to full rollback.
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
        self.saved_lkg: Optional[List[int]] = None
    
    def get_current(self) -> List[int]:
        return self.current_values.copy()
    
    def apply(self, values: List[int]) -> Tuple[bool, Optional[str]]:
        self.applied_values = values.copy()
        self.current_values = values.copy()
        return True, None
    
    def get_lkg(self) -> List[int]:
        return self.lkg_values.copy()
    
    def save_lkg(self, values: List[int]) -> None:
        self.saved_lkg = values.copy()
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


class TestProgressiveRecoveryStabilityWait:
    """Property 6: Recovery stability wait
    
    For any progressive recovery attempt, the system SHALL wait for exactly 
    STABILITY_HEARTBEATS (2) heartbeat cycles before declaring success or 
    proceeding to full rollback.
    
    Feature: decktune-3.0-automation, Property 6: Recovery stability wait
    Validates: Requirements 2.2
    """

    def test_stability_heartbeats_constant_is_2(self):
        """STABILITY_HEARTBEATS constant is exactly 2."""
        assert ProgressiveRecovery.STABILITY_HEARTBEATS == 2, \
            f"STABILITY_HEARTBEATS should be 2, got {ProgressiveRecovery.STABILITY_HEARTBEATS}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_first_heartbeat_does_not_confirm_stability(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """First heartbeat after reduction does not confirm stability."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability to enter REDUCED state
        recovery.on_instability_detected()
        assert recovery.state.stage == RecoveryStage.REDUCED
        
        # First heartbeat
        stability_confirmed, error = recovery.on_heartbeat()
        
        # Should not confirm stability yet
        assert not stability_confirmed, "First heartbeat should not confirm stability"
        assert recovery.state.heartbeats_since_reduction == 1

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_second_heartbeat_confirms_stability(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Second heartbeat after reduction confirms stability."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability to enter REDUCED state
        recovery.on_instability_detected()
        assert recovery.state.stage == RecoveryStage.REDUCED
        
        # First heartbeat
        stability_confirmed, _ = recovery.on_heartbeat()
        assert not stability_confirmed
        
        # Second heartbeat
        stability_confirmed, error = recovery.on_heartbeat()
        
        # Should confirm stability
        assert stability_confirmed, "Second heartbeat should confirm stability"
        assert error is None

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_heartbeat_count_increments_correctly(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Heartbeat count increments by 1 on each heartbeat."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability to enter REDUCED state
        recovery.on_instability_detected()
        assert recovery.state.heartbeats_since_reduction == 0
        
        # First heartbeat
        recovery.on_heartbeat()
        assert recovery.state.heartbeats_since_reduction == 1
        
        # Note: Second heartbeat confirms stability and resets state,
        # so we can't check count after that

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_heartbeat_in_initial_state_does_nothing(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Heartbeat in INITIAL state does not affect anything."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Should be in INITIAL state
        assert recovery.state.stage == RecoveryStage.INITIAL
        
        # Heartbeat should return False and not change state
        stability_confirmed, error = recovery.on_heartbeat()
        
        assert not stability_confirmed
        assert error is None
        assert recovery.state.stage == RecoveryStage.INITIAL
        assert recovery.state.heartbeats_since_reduction == 0

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_exactly_two_heartbeats_required(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Exactly STABILITY_HEARTBEATS (2) heartbeats are required for stability."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability to enter REDUCED state
        recovery.on_instability_detected()
        
        # Track stability confirmations
        confirmations = []
        
        for i in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            stability_confirmed, _ = recovery.on_heartbeat()
            confirmations.append(stability_confirmed)
        
        # Only the last heartbeat should confirm stability
        expected = [False] * (ProgressiveRecovery.STABILITY_HEARTBEATS - 1) + [True]
        assert confirmations == expected, \
            f"Expected {expected}, got {confirmations}"

    @given(
        current_values=valid_undervolt_values, 
        lkg_values=valid_undervolt_values,
        extra_heartbeats=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_heartbeats_before_instability_not_counted(
        self, 
        current_values: List[int], 
        lkg_values: List[int],
        extra_heartbeats: int
    ):
        """Heartbeats before instability detection are not counted."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Send heartbeats before instability (should be ignored)
        for _ in range(extra_heartbeats):
            recovery.on_heartbeat()
        
        # Trigger instability
        recovery.on_instability_detected()
        
        # Count should start at 0
        assert recovery.state.heartbeats_since_reduction == 0
        
        # Still need exactly STABILITY_HEARTBEATS to confirm
        for i in range(ProgressiveRecovery.STABILITY_HEARTBEATS - 1):
            stability_confirmed, _ = recovery.on_heartbeat()
            assert not stability_confirmed
        
        stability_confirmed, _ = recovery.on_heartbeat()
        assert stability_confirmed

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_state_reset_after_stability_confirmed(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """State is reset to INITIAL after stability is confirmed."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability and wait for stability
        recovery.on_instability_detected()
        
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # State should be reset
        assert recovery.state.stage == RecoveryStage.INITIAL
        assert recovery.state.heartbeats_since_reduction == 0
