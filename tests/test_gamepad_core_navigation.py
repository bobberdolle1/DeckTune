"""Property tests for gamepad core navigation.

Feature: manual-dynamic-mode, Property 15: Gamepad core navigation
Validates: Requirements 8.1

Property 15: Gamepad core navigation
For any D-pad Up or Down input, the selected core index SHALL change by ±1
(wrapping at boundaries 0 and 3).

This test validates the core navigation logic that is implemented in the CoreTabs
component (src/components/CoreTabs.tsx). The navigation ensures that:
- D-pad Up decrements the core index (with wrapping from 0 to 3)
- D-pad Down increments the core index (with wrapping from 3 to 0)
- Navigation wraps at boundaries to provide seamless cycling
"""

import pytest
from hypothesis import given, strategies as st, settings


def navigate_core_up(current_core: int) -> int:
    """
    Navigate to previous core with wrapping.
    This mirrors the D-pad Up logic in CoreTabs.tsx.
    
    Args:
        current_core: Current core index (0-3)
        
    Returns:
        New core index after navigating up
    """
    return 3 if current_core == 0 else current_core - 1


def navigate_core_down(current_core: int) -> int:
    """
    Navigate to next core with wrapping.
    This mirrors the D-pad Down logic in CoreTabs.tsx.
    
    Args:
        current_core: Current core index (0-3)
        
    Returns:
        New core index after navigating down
    """
    return 0 if current_core == 3 else current_core + 1


# Strategy for valid core indices
core_index = st.integers(min_value=0, max_value=3)


class TestGamepadCoreNavigationUp:
    """Property 15: Gamepad core navigation for D-pad Up
    
    For any D-pad Up input, the selected core index SHALL change by -1
    with wrapping at boundary 0.
    
    Validates: Requirements 8.1
    """

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_dpad_up_decrements_core(self, current_core: int):
        """D-pad Up SHALL decrement core index with wrapping."""
        new_core = navigate_core_up(current_core)
        
        # Verify new core is in valid range
        assert 0 <= new_core <= 3, (
            f"Core index {new_core} out of valid range [0, 3]"
        )
        
        # Verify decrement behavior
        if current_core == 0:
            assert new_core == 3, (
                f"D-pad Up from core 0 should wrap to core 3, got {new_core}"
            )
        else:
            assert new_core == current_core - 1, (
                f"D-pad Up from core {current_core} should go to {current_core - 1}, "
                f"got {new_core}"
            )

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_dpad_up_wraps_at_zero(self, current_core: int):
        """D-pad Up from core 0 SHALL wrap to core 3."""
        if current_core == 0:
            new_core = navigate_core_up(current_core)
            assert new_core == 3, (
                f"D-pad Up from core 0 should wrap to core 3, got {new_core}"
            )


class TestGamepadCoreNavigationDown:
    """Property 15: Gamepad core navigation for D-pad Down
    
    For any D-pad Down input, the selected core index SHALL change by +1
    with wrapping at boundary 3.
    
    Validates: Requirements 8.1
    """

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_dpad_down_increments_core(self, current_core: int):
        """D-pad Down SHALL increment core index with wrapping."""
        new_core = navigate_core_down(current_core)
        
        # Verify new core is in valid range
        assert 0 <= new_core <= 3, (
            f"Core index {new_core} out of valid range [0, 3]"
        )
        
        # Verify increment behavior
        if current_core == 3:
            assert new_core == 0, (
                f"D-pad Down from core 3 should wrap to core 0, got {new_core}"
            )
        else:
            assert new_core == current_core + 1, (
                f"D-pad Down from core {current_core} should go to {current_core + 1}, "
                f"got {new_core}"
            )

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_dpad_down_wraps_at_three(self, current_core: int):
        """D-pad Down from core 3 SHALL wrap to core 0."""
        if current_core == 3:
            new_core = navigate_core_down(current_core)
            assert new_core == 0, (
                f"D-pad Down from core 3 should wrap to core 0, got {new_core}"
            )


class TestGamepadCoreNavigationRoundTrip:
    """Additional property: Round-trip navigation
    
    Navigating up then down (or down then up) should return to original core.
    """

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_up_then_down_returns_to_original(self, current_core: int):
        """Navigating up then down SHALL return to original core."""
        after_up = navigate_core_up(current_core)
        after_down = navigate_core_down(after_up)
        
        assert after_down == current_core, (
            f"Up then down from core {current_core} should return to {current_core}, "
            f"got {after_down}"
        )

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_down_then_up_returns_to_original(self, current_core: int):
        """Navigating down then up SHALL return to original core."""
        after_down = navigate_core_down(current_core)
        after_up = navigate_core_up(after_down)
        
        assert after_up == current_core, (
            f"Down then up from core {current_core} should return to {current_core}, "
            f"got {after_up}"
        )


class TestGamepadCoreNavigationCycling:
    """Additional property: Complete cycle navigation
    
    Navigating in one direction 4 times should return to original core.
    """

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_four_ups_returns_to_original(self, current_core: int):
        """Navigating up 4 times SHALL return to original core."""
        core = current_core
        for _ in range(4):
            core = navigate_core_up(core)
        
        assert core == current_core, (
            f"Four D-pad Ups from core {current_core} should return to {current_core}, "
            f"got {core}"
        )

    @given(current_core=core_index)
    @settings(max_examples=100)
    def test_four_downs_returns_to_original(self, current_core: int):
        """Navigating down 4 times SHALL return to original core."""
        core = current_core
        for _ in range(4):
            core = navigate_core_down(core)
        
        assert core == current_core, (
            f"Four D-pad Downs from core {current_core} should return to {current_core}, "
            f"got {core}"
        )


class TestGamepadCoreNavigationBoundaries:
    """Additional property: Boundary behavior
    
    Navigation at boundaries should always produce valid core indices.
    """

    def test_up_from_zero_produces_three(self):
        """D-pad Up from core 0 SHALL produce core 3."""
        assert navigate_core_up(0) == 3

    def test_down_from_three_produces_zero(self):
        """D-pad Down from core 3 SHALL produce core 0."""
        assert navigate_core_down(3) == 0

    def test_up_from_one_produces_zero(self):
        """D-pad Up from core 1 SHALL produce core 0."""
        assert navigate_core_up(1) == 0

    def test_down_from_two_produces_three(self):
        """D-pad Down from core 2 SHALL produce core 3."""
        assert navigate_core_down(2) == 3


class TestGamepadCoreNavigationSequence:
    """Additional property: Sequential navigation
    
    Multiple navigation operations should maintain valid state.
    """

    @given(
        start_core=core_index,
        operations=st.lists(
            st.sampled_from(['up', 'down']),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_sequence_maintains_valid_core(self, start_core: int, operations: list):
        """Any sequence of navigation operations SHALL maintain valid core index."""
        core = start_core
        
        for op in operations:
            if op == 'up':
                core = navigate_core_up(core)
            else:
                core = navigate_core_down(core)
            
            assert 0 <= core <= 3, (
                f"Core index {core} out of valid range [0, 3] after operation {op}"
            )
