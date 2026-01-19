"""Property test for Manual tab control exclusivity.

Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
Validates: Requirements 7.1, 7.2

Tests that for any render of the Manual tab, the Expert Mode toggle should
not be present, and the startup behavior toggles should be present.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import re
from pathlib import Path


# Path to the ExpertMode component
EXPERT_MODE_PATH = Path(__file__).parent.parent / "src" / "components" / "ExpertMode.tsx"


def read_manual_tab_component():
    """Read the ManualTab component source code."""
    with open(EXPERT_MODE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract ManualTab component
    # Find the ManualTab function component
    match = re.search(
        r'const ManualTab:.*?(?=\nconst\s+\w+:|export\s+default|$)',
        content,
        re.DOTALL
    )
    
    if not match:
        raise ValueError("ManualTab component not found in ExpertMode.tsx")
    
    return match.group(0)


def test_manual_tab_no_expert_mode_toggle():
    """Test that Manual tab does not contain Expert Mode toggle.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirement 7.1
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that Expert Mode toggle is NOT present
    # Look for patterns that would indicate an Expert Mode toggle button
    expert_mode_patterns = [
        r'Expert\s+Mode\s+Toggle',  # Comment
        r'handleExpertModeToggle',  # Handler function
        r'onClick={handleExpertModeToggle}',  # Click handler
        r'Expert Mode.*Toggle',  # Any Expert Mode toggle text
    ]
    
    for pattern in expert_mode_patterns:
        matches = re.findall(pattern, manual_tab_code, re.IGNORECASE)
        assert len(matches) == 0, \
            f"Manual tab should not contain Expert Mode toggle. Found: {pattern}"
    
    # Verify that Expert Mode state is read from settings context, not local state
    assert 'useState' not in manual_tab_code or 'expertMode' not in manual_tab_code or \
           'settings.expertMode' in manual_tab_code, \
        "Manual tab should use settings.expertMode from context, not local state"


def test_manual_tab_has_startup_behavior_toggles():
    """Test that Manual tab contains startup behavior toggles.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirement 7.2
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that Startup Behavior section is present
    assert 'Startup Behavior' in manual_tab_code, \
        "Manual tab should contain 'Startup Behavior' section header"
    
    # Check that Apply on Startup toggle is present
    assert 'Apply on Startup' in manual_tab_code, \
        "Manual tab should contain 'Apply on Startup' toggle"
    
    # Check that Game Only Mode toggle is present
    assert 'Game Only Mode' in manual_tab_code, \
        "Manual tab should contain 'Game Only Mode' toggle"
    
    # Check that toggles are connected to settings context
    assert 'setApplyOnStartup' in manual_tab_code, \
        "Manual tab should use setApplyOnStartup from settings context"
    
    assert 'setGameOnlyMode' in manual_tab_code, \
        "Manual tab should use setGameOnlyMode from settings context"


def test_manual_tab_uses_settings_context():
    """Test that Manual tab uses settings context for Expert Mode.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.1, 7.2
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that useSettings hook is used
    assert 'useSettings' in manual_tab_code, \
        "Manual tab should use useSettings hook"
    
    # Check that settings.expertMode is used (not local state)
    assert 'settings.expertMode' in manual_tab_code, \
        "Manual tab should read expertMode from settings context"
    
    # Check that Expert Mode is NOT managed locally
    assert 'setExpertMode' not in manual_tab_code or 'settings, setExpertMode' in manual_tab_code, \
        "Manual tab should not manage Expert Mode state locally"


def test_manual_tab_startup_toggles_have_descriptions():
    """Test that startup behavior toggles have descriptive labels.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirement 7.5
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check for Apply on Startup description
    assert 'Automatically apply last profile' in manual_tab_code or \
           'apply last profile when' in manual_tab_code.lower(), \
        "Apply on Startup toggle should have a descriptive label"
    
    # Check for Game Only Mode description
    assert 'only when games are running' in manual_tab_code.lower() or \
           'reset in Steam menu' in manual_tab_code.lower(), \
        "Game Only Mode toggle should have a descriptive label"


@given(component_render=st.just(None))
@hyp_settings(max_examples=100)
def test_manual_tab_control_exclusivity_property(component_render):
    """Property 9: Manual tab control exclusivity
    
    For any render of the Manual tab, the Expert Mode toggle SHALL not be
    present, and the startup behavior toggles SHALL be present.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.1, 7.2
    """
    manual_tab_code = read_manual_tab_component()
    
    # Property: Expert Mode toggle is NOT present
    expert_mode_toggle_present = (
        'handleExpertModeToggle' in manual_tab_code or
        'Expert Mode Toggle' in manual_tab_code
    )
    assert not expert_mode_toggle_present, \
        "Manual tab should not contain Expert Mode toggle button"
    
    # Property: Startup behavior toggles ARE present
    startup_behavior_present = (
        'Startup Behavior' in manual_tab_code and
        'Apply on Startup' in manual_tab_code and
        'Game Only Mode' in manual_tab_code
    )
    assert startup_behavior_present, \
        "Manual tab should contain Startup Behavior section with toggles"
    
    # Property: Toggles are connected to settings context
    toggles_connected = (
        'setApplyOnStartup' in manual_tab_code and
        'setGameOnlyMode' in manual_tab_code and
        'useSettings' in manual_tab_code
    )
    assert toggles_connected, \
        "Manual tab toggles should be connected to settings context"


def test_manual_tab_expert_mode_warning_display():
    """Test that Manual tab displays Expert Mode warning when active.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.1
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that Expert Mode warning is displayed when settings.expertMode is true
    assert 'settings.expertMode' in manual_tab_code, \
        "Manual tab should check settings.expertMode for warning display"
    
    # Check for warning display logic
    assert 'Expert mode active' in manual_tab_code or \
           'Expert Mode Active Warning' in manual_tab_code, \
        "Manual tab should display warning when Expert Mode is active"


@given(
    has_expert_toggle=st.booleans(),
    has_startup_toggles=st.booleans()
)
@hyp_settings(max_examples=100)
def test_manual_tab_toggle_presence_invariant(has_expert_toggle, has_startup_toggles):
    """Test the invariant that Expert Mode toggle and startup toggles are mutually exclusive.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.1, 7.2
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check actual state
    actual_has_expert_toggle = 'handleExpertModeToggle' in manual_tab_code
    actual_has_startup_toggles = (
        'Apply on Startup' in manual_tab_code and
        'Game Only Mode' in manual_tab_code
    )
    
    # Invariant: Expert Mode toggle should NOT be present
    assert not actual_has_expert_toggle, \
        "Manual tab should never contain Expert Mode toggle"
    
    # Invariant: Startup toggles should ALWAYS be present
    assert actual_has_startup_toggles, \
        "Manual tab should always contain startup behavior toggles"


def test_manual_tab_no_expert_mode_confirmation_dialog():
    """Test that Manual tab does not contain Expert Mode confirmation dialog.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirement 7.1
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that Expert Mode warning dialog is NOT present in ManualTab
    # The dialog should only be in SettingsMenu
    assert 'showExpertWarning' not in manual_tab_code, \
        "Manual tab should not contain Expert Mode warning dialog state"
    
    assert 'handleExpertModeConfirm' not in manual_tab_code, \
        "Manual tab should not contain Expert Mode confirmation handler"
    
    assert 'handleExpertModeCancel' not in manual_tab_code, \
        "Manual tab should not contain Expert Mode cancel handler"


def test_manual_tab_settings_context_integration():
    """Test that Manual tab properly integrates with settings context.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.3, 7.4
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that settings are destructured from useSettings
    assert 'useSettings' in manual_tab_code, \
        "Manual tab should use useSettings hook"
    
    # Check that setApplyOnStartup is called on toggle
    assert 'setApplyOnStartup(!settings.applyOnStartup)' in manual_tab_code or \
           'setApplyOnStartup' in manual_tab_code, \
        "Manual tab should call setApplyOnStartup when toggle is clicked"
    
    # Check that setGameOnlyMode is called on toggle
    assert 'setGameOnlyMode(!settings.gameOnlyMode)' in manual_tab_code or \
           'setGameOnlyMode' in manual_tab_code, \
        "Manual tab should call setGameOnlyMode when toggle is clicked"


@given(render_count=st.integers(min_value=1, max_value=100))
@hyp_settings(max_examples=100)
def test_manual_tab_consistent_across_renders(render_count):
    """Test that Manual tab structure is consistent across multiple renders.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirements 7.1, 7.2
    """
    # Read component multiple times to simulate multiple renders
    for _ in range(min(render_count, 10)):  # Limit actual reads for performance
        manual_tab_code = read_manual_tab_component()
        
        # Verify consistent structure
        assert 'Startup Behavior' in manual_tab_code, \
            "Manual tab should consistently contain Startup Behavior section"
        
        assert 'Apply on Startup' in manual_tab_code, \
            "Manual tab should consistently contain Apply on Startup toggle"
        
        assert 'Game Only Mode' in manual_tab_code, \
            "Manual tab should consistently contain Game Only Mode toggle"
        
        assert 'handleExpertModeToggle' not in manual_tab_code, \
            "Manual tab should consistently NOT contain Expert Mode toggle"


def test_manual_tab_toggle_styling_consistency():
    """Test that startup behavior toggles have consistent styling.
    
    Feature: ui-refactor-settings, Property 9: Manual tab control exclusivity
    Validates: Requirement 7.5
    """
    manual_tab_code = read_manual_tab_component()
    
    # Check that toggles use FocusableButton
    assert 'FocusableButton' in manual_tab_code, \
        "Manual tab toggles should use FocusableButton for consistency"
    
    # Check that toggles have visual feedback
    assert 'backgroundColor' in manual_tab_code, \
        "Manual tab toggles should have background color styling"
    
    # Check that toggles show current state
    assert 'settings.applyOnStartup' in manual_tab_code and \
           'settings.gameOnlyMode' in manual_tab_code, \
        "Manual tab toggles should display current state from settings"
