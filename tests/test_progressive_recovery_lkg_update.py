"""Property tests for progressive recovery LKG update.

Feature: decktune-3.0-automation, Property 8: Recovery success updates LKG
Validates: Requirements 2.4

Property 8: Recovery success updates LKG
For any successful progressive recovery (stability confirmed after reduction), 
the LKG values SHALL be updated to the reduced values.
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
        self.lkg_save_count = 0
    
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
        self.lkg_save_count += 1


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


class TestProgressiveRecoveryLKGUpdate:
    """Property 8: Recovery success updates LKG
    
    For any successful progressive recovery (stability confirmed after reduction), 
    the LKG values SHALL be updated to the reduced values.
    
    Feature: decktune-3.0-automation, Property 8: Recovery success updates LKG
    Validates: Requirements 2.4
    """

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_successful_recovery_updates_lkg_to_reduced_values(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Successful recovery updates LKG to the reduced values."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability to enter REDUCED state
        recovery.on_instability_detected()
        reduced_values = recovery.state.reduced_values.copy()
        
        # Wait for stability (STABILITY_HEARTBEATS heartbeats)
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # LKG should be updated to reduced values
        assert store.saved_lkg == reduced_values, \
            f"LKG {store.saved_lkg} should equal reduced values {reduced_values}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_lkg_save_called_exactly_once_on_success(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """LKG save is called exactly once on successful recovery."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability and wait for stability
        recovery.on_instability_detected()
        
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # LKG should be saved exactly once
        assert store.lkg_save_count == 1, \
            f"LKG save count should be 1, got {store.lkg_save_count}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_lkg_not_updated_before_stability_confirmed(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """LKG is not updated before stability is confirmed."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability
        recovery.on_instability_detected()
        
        # One heartbeat (not enough for stability)
        recovery.on_heartbeat()
        
        # LKG should not be updated yet
        assert store.saved_lkg is None, \
            f"LKG should not be saved yet, but got {store.saved_lkg}"
        assert store.lkg_save_count == 0

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_lkg_not_updated_on_escalation(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """LKG is not updated when recovery escalates to full rollback."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability twice (escalation)
        recovery.on_instability_detected()
        recovery.on_instability_detected()
        
        # LKG should not be updated (rollback uses existing LKG)
        assert store.saved_lkg is None, \
            f"LKG should not be saved on escalation, but got {store.saved_lkg}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_reduced_values_are_correct_in_lkg(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """Reduced values saved to LKG are correctly calculated."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability and wait for stability
        recovery.on_instability_detected()
        
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # Calculate expected reduced values
        expected_reduced = [min(v + ProgressiveRecovery.REDUCTION_STEP, 0) for v in current_values]
        
        assert store.saved_lkg == expected_reduced, \
            f"Saved LKG {store.saved_lkg} should equal expected {expected_reduced}"

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_confirm_stability_returns_success(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """confirm_stability returns success when called in REDUCED state."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability
        recovery.on_instability_detected()
        
        # Manually confirm stability
        success, error = recovery.confirm_stability()
        
        assert success, f"confirm_stability should succeed: {error}"
        assert error is None

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_state_reset_after_lkg_update(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """State is reset to INITIAL after LKG update."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability and wait for stability
        recovery.on_instability_detected()
        
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # State should be reset
        assert recovery.state.stage == RecoveryStage.INITIAL
        assert not recovery.is_recovering

    def test_confirm_stability_fails_in_initial_state(self):
        """confirm_stability fails when not in REDUCED state."""
        current_values = [-30, -30, -30, -30]
        lkg_values = [-20, -20, -20, -20]
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Try to confirm stability without triggering instability first
        success, error = recovery.confirm_stability()
        
        assert not success
        assert error is not None
        assert store.saved_lkg is None

    def test_confirm_stability_fails_in_rollback_state(self):
        """confirm_stability fails when in ROLLBACK state."""
        current_values = [-30, -30, -30, -30]
        lkg_values = [-20, -20, -20, -20]
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger escalation to ROLLBACK state
        recovery.on_instability_detected()
        recovery.on_instability_detected()
        
        assert recovery.state.stage == RecoveryStage.ROLLBACK
        
        # Try to confirm stability
        success, error = recovery.confirm_stability()
        
        assert not success
        assert error is not None

    @given(current_values=valid_undervolt_values, lkg_values=valid_undervolt_values)
    @settings(max_examples=100)
    def test_new_lkg_is_retrievable_after_update(
        self, 
        current_values: List[int], 
        lkg_values: List[int]
    ):
        """New LKG values are retrievable after update."""
        recovery, store = create_progressive_recovery(current_values, lkg_values)
        
        # Trigger instability and wait for stability
        recovery.on_instability_detected()
        reduced_values = recovery.state.reduced_values.copy()
        
        for _ in range(ProgressiveRecovery.STABILITY_HEARTBEATS):
            recovery.on_heartbeat()
        
        # Get LKG should return the new values
        assert store.get_lkg() == reduced_values
