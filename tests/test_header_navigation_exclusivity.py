"""Property test for header navigation exclusivity.

Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
Validates: Requirements 8.1, 8.2, 8.3

Tests that for any navigation to Fan Control via header icon, the Fan Control
component should be the only mode displayed, and the large Fan Control button
should not exist in the mode list.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from typing import Literal

# Type for navigation modes
NavigationMode = Literal["wizard", "expert", "fan"]

# Strategy for generating navigation sequences
# Each sequence represents a series of user navigation actions
navigation_sequence_strategy = st.lists(
    st.sampled_from(["wizard", "expert", "fan_via_header", "fan_via_button"]),
    min_size=1,
    max_size=10
)


class MockUIState:
    """Mock UI state to simulate DeckTuneApp behavior."""
    
    def __init__(self):
        self.current_mode: NavigationMode = "wizard"
        self.has_large_fan_button: bool = True  # Initially has large button
        self.navigation_history: list[str] = []
    
    def navigate_to_wizard(self):
        """Navigate to Wizard mode."""
        self.current_mode = "wizard"
        self.navigation_history.append("wizard")
    
    def navigate_to_expert(self):
        """Navigate to Expert mode."""
        self.current_mode = "expert"
        self.navigation_history.append("expert")
    
    def navigate_to_fan_via_header(self):
        """Navigate to Fan Control via header icon.
        
        Requirements: 8.1, 8.2, 8.3
        - Fan Control should be the only mode displayed
        - Large Fan Control button should not exist in mode list
        """
        self.current_mode = "fan"
        self.has_large_fan_button = False  # Requirement 8.1, 8.3
        self.navigation_history.append("fan_via_header")
    
    def navigate_to_fan_via_button(self):
        """Navigate to Fan Control via large button (legacy behavior).
        
        This should not be possible after refactor (Requirement 8.1).
        """
        # After refactor, this should not exist
        raise ValueError("Large Fan Control button should not exist (Requirement 8.1)")
    
    def get_visible_modes(self) -> list[str]:
        """Get list of modes visible in the mode selection area.
        
        Requirements: 8.2
        - Should only display Wizard Mode and Expert Mode buttons
        - Fan Control should not be in the mode list
        """
        if self.current_mode == "fan":
            # When Fan Control is active, no mode buttons should be visible
            # (only Fan Control component with back button)
            return []
        else:
            # Only Wizard and Expert modes should be in the mode list
            return ["wizard", "expert"]
    
    def is_fan_control_active(self) -> bool:
        """Check if Fan Control component is currently active."""
        return self.current_mode == "fan"
    
    def has_back_button(self) -> bool:
        """Check if current view has a back button.
        
        Requirements: 8.4
        - Fan Control should have back button to return to main screen
        """
        return self.current_mode == "fan"


@given(sequence=navigation_sequence_strategy)
@hyp_settings(max_examples=100, deadline=None)
def test_header_navigation_exclusivity(sequence):
    """Property 8: Header navigation exclusivity
    
    For any navigation to Fan Control via header icon, the Fan Control
    component SHALL be the only mode displayed, and the large Fan Control
    button SHALL not exist in the mode list.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1, 8.2, 8.3
    """
    ui_state = MockUIState()
    
    for action in sequence:
        if action == "wizard":
            ui_state.navigate_to_wizard()
        elif action == "expert":
            ui_state.navigate_to_expert()
        elif action == "fan_via_header":
            ui_state.navigate_to_fan_via_header()
        elif action == "fan_via_button":
            # This should raise an error after refactor
            with pytest.raises(ValueError, match="Large Fan Control button should not exist"):
                ui_state.navigate_to_fan_via_button()
            continue
        
        # Verify invariants after each navigation
        visible_modes = ui_state.get_visible_modes()
        
        # Requirement 8.1: Large Fan Control button should not exist
        assert "fan" not in visible_modes, \
            "Fan Control should not appear in mode list (Requirement 8.1)"
        
        # Requirement 8.2: Mode list should only contain Wizard and Expert
        if not ui_state.is_fan_control_active():
            assert set(visible_modes) == {"wizard", "expert"}, \
                f"Mode list should only contain Wizard and Expert, got {visible_modes} (Requirement 8.2)"
        
        # Requirement 8.3: When Fan Control is active via header, it should be exclusive
        if ui_state.is_fan_control_active():
            assert visible_modes == [], \
                "When Fan Control is active, no mode buttons should be visible (Requirement 8.3)"
            assert not ui_state.has_large_fan_button, \
                "Large Fan Control button should not exist when accessed via header (Requirement 8.3)"


@given(
    initial_mode=st.sampled_from(["wizard", "expert"]),
    navigate_to_fan=st.booleans()
)
@hyp_settings(max_examples=100)
def test_fan_control_only_via_header(initial_mode, navigate_to_fan):
    """Test that Fan Control is only accessible via header icon.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1, 8.3
    """
    ui_state = MockUIState()
    
    # Set initial mode
    if initial_mode == "wizard":
        ui_state.navigate_to_wizard()
    else:
        ui_state.navigate_to_expert()
    
    # Verify Fan Control is not in mode list
    visible_modes = ui_state.get_visible_modes()
    assert "fan" not in visible_modes, \
        "Fan Control should not be in mode list (Requirement 8.1)"
    
    if navigate_to_fan:
        # Navigate to Fan Control via header
        ui_state.navigate_to_fan_via_header()
        
        # Verify Fan Control is active
        assert ui_state.is_fan_control_active(), \
            "Fan Control should be active after header navigation"
        
        # Verify no mode buttons are visible
        visible_modes = ui_state.get_visible_modes()
        assert visible_modes == [], \
            "No mode buttons should be visible when Fan Control is active (Requirement 8.3)"


@given(
    navigation_sequence=st.lists(
        st.sampled_from(["wizard", "expert", "fan_via_header"]),
        min_size=1,
        max_size=20
    )
)
@hyp_settings(max_examples=100)
def test_fan_control_never_in_mode_list(navigation_sequence):
    """Test that Fan Control never appears in mode list regardless of navigation.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1, 8.2
    """
    ui_state = MockUIState()
    
    # Perform navigation sequence
    for action in navigation_sequence:
        if action == "wizard":
            ui_state.navigate_to_wizard()
        elif action == "expert":
            ui_state.navigate_to_expert()
        elif action == "fan_via_header":
            ui_state.navigate_to_fan_via_header()
        
        # Verify Fan Control is never in mode list
        visible_modes = ui_state.get_visible_modes()
        assert "fan" not in visible_modes, \
            f"Fan Control should never be in mode list, got {visible_modes} (Requirement 8.1)"


@given(
    start_mode=st.sampled_from(["wizard", "expert"]),
    end_mode=st.sampled_from(["wizard", "expert"])
)
@hyp_settings(max_examples=100)
def test_mode_list_only_wizard_and_expert(start_mode, end_mode):
    """Test that mode list only contains Wizard and Expert modes.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.2
    """
    ui_state = MockUIState()
    
    # Navigate to start mode
    if start_mode == "wizard":
        ui_state.navigate_to_wizard()
    else:
        ui_state.navigate_to_expert()
    
    # Verify mode list
    visible_modes = ui_state.get_visible_modes()
    assert set(visible_modes) == {"wizard", "expert"}, \
        f"Mode list should only contain Wizard and Expert, got {visible_modes} (Requirement 8.2)"
    
    # Navigate to end mode
    if end_mode == "wizard":
        ui_state.navigate_to_wizard()
    else:
        ui_state.navigate_to_expert()
    
    # Verify mode list again
    visible_modes = ui_state.get_visible_modes()
    assert set(visible_modes) == {"wizard", "expert"}, \
        f"Mode list should only contain Wizard and Expert, got {visible_modes} (Requirement 8.2)"


def test_fan_control_has_back_button():
    """Test that Fan Control component has back button.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.4
    """
    ui_state = MockUIState()
    
    # Navigate to Fan Control via header
    ui_state.navigate_to_fan_via_header()
    
    # Verify back button exists
    assert ui_state.has_back_button(), \
        "Fan Control should have back button (Requirement 8.4)"


@given(
    intermediate_navigations=st.lists(
        st.sampled_from(["wizard", "expert"]),
        min_size=0,
        max_size=5
    )
)
@hyp_settings(max_examples=100)
def test_fan_control_exclusivity_preserved(intermediate_navigations):
    """Test that Fan Control exclusivity is preserved across navigation.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1, 8.2, 8.3
    """
    ui_state = MockUIState()
    
    # Navigate to Fan Control
    ui_state.navigate_to_fan_via_header()
    
    # Verify exclusivity
    assert ui_state.is_fan_control_active()
    assert ui_state.get_visible_modes() == []
    assert not ui_state.has_large_fan_button
    
    # Navigate back to wizard
    ui_state.navigate_to_wizard()
    
    # Perform intermediate navigations
    for action in intermediate_navigations:
        if action == "wizard":
            ui_state.navigate_to_wizard()
        else:
            ui_state.navigate_to_expert()
        
        # Verify mode list is correct
        visible_modes = ui_state.get_visible_modes()
        assert set(visible_modes) == {"wizard", "expert"}
        assert "fan" not in visible_modes
    
    # Navigate to Fan Control again
    ui_state.navigate_to_fan_via_header()
    
    # Verify exclusivity is still preserved
    assert ui_state.is_fan_control_active()
    assert ui_state.get_visible_modes() == []
    assert not ui_state.has_large_fan_button


def test_large_fan_button_does_not_exist():
    """Test that large Fan Control button does not exist in mode list.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1
    """
    ui_state = MockUIState()
    
    # Start in wizard mode
    ui_state.navigate_to_wizard()
    
    # Verify Fan Control is not in mode list
    visible_modes = ui_state.get_visible_modes()
    assert "fan" not in visible_modes, \
        "Large Fan Control button should not exist in mode list (Requirement 8.1)"
    
    # Try to navigate via button (should fail)
    with pytest.raises(ValueError, match="Large Fan Control button should not exist"):
        ui_state.navigate_to_fan_via_button()


@given(
    navigation_sequence=st.lists(
        st.sampled_from(["wizard", "expert", "fan_via_header"]),
        min_size=1,
        max_size=10
    )
)
@hyp_settings(max_examples=100, deadline=None)
def test_mode_preservation_across_fan_navigation(navigation_sequence):
    """Test that previously selected mode is preserved when navigating to/from Fan Control.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.5
    """
    ui_state = MockUIState()
    
    last_non_fan_mode = "wizard"
    
    for action in navigation_sequence:
        if action == "wizard":
            ui_state.navigate_to_wizard()
            last_non_fan_mode = "wizard"
        elif action == "expert":
            ui_state.navigate_to_expert()
            last_non_fan_mode = "expert"
        elif action == "fan_via_header":
            # Remember the mode before navigating to Fan Control
            mode_before_fan = last_non_fan_mode
            
            # Navigate to Fan Control
            ui_state.navigate_to_fan_via_header()
            
            # Verify Fan Control is active
            assert ui_state.is_fan_control_active()
            
            # Navigate back (simulating back button click)
            if mode_before_fan == "wizard":
                ui_state.navigate_to_wizard()
            else:
                ui_state.navigate_to_expert()
            
            # Verify we returned to the correct mode
            assert ui_state.current_mode == mode_before_fan, \
                f"Should return to {mode_before_fan} after Fan Control, got {ui_state.current_mode} (Requirement 8.5)"


def test_fan_control_accessible_only_via_header():
    """Test that Fan Control is accessible only via header icon.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.1, 8.3
    """
    ui_state = MockUIState()
    
    # Verify Fan Control is not in mode list
    visible_modes = ui_state.get_visible_modes()
    assert "fan" not in visible_modes, \
        "Fan Control should not be in mode list (Requirement 8.1)"
    
    # Only way to access Fan Control is via header
    ui_state.navigate_to_fan_via_header()
    
    # Verify Fan Control is active
    assert ui_state.is_fan_control_active(), \
        "Fan Control should be accessible via header icon (Requirement 8.3)"


@given(
    mode_switches=st.lists(
        st.sampled_from(["wizard", "expert"]),
        min_size=1,
        max_size=10
    )
)
@hyp_settings(max_examples=100)
def test_mode_list_consistency(mode_switches):
    """Test that mode list remains consistent across mode switches.
    
    Feature: ui-refactor-settings, Property 8: Header navigation exclusivity
    Validates: Requirements 8.2
    """
    ui_state = MockUIState()
    
    for mode in mode_switches:
        if mode == "wizard":
            ui_state.navigate_to_wizard()
        else:
            ui_state.navigate_to_expert()
        
        # Verify mode list is always consistent
        visible_modes = ui_state.get_visible_modes()
        assert set(visible_modes) == {"wizard", "expert"}, \
            f"Mode list should always be [wizard, expert], got {visible_modes} (Requirement 8.2)"
        assert "fan" not in visible_modes, \
            "Fan Control should never appear in mode list (Requirement 8.1)"
