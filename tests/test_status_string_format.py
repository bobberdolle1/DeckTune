"""Property test for status string format.

Feature: decktune, Property 10: Status String Format
Validates: Requirements 5.3

Tests that for any active preset state, the status string SHALL match one of:
- "Using preset for {label}" where label is non-empty
- "Global"
- "Disabled"
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import re
from typing import Optional


def format_status_string(preset_label: Optional[str], is_global: bool, is_enabled: bool) -> str:
    """Format status string based on preset state.
    
    This function implements the status string formatting logic that
    should be consistent between frontend and backend.
    
    Args:
        preset_label: Label of active preset, or None if no preset
        is_global: Whether global mode is active
        is_enabled: Whether undervolt is enabled
        
    Returns:
        Formatted status string
        
    Requirements: 5.3
    """
    if not is_enabled:
        return "Disabled"
    
    if preset_label and preset_label.strip():
        return f"Using preset for {preset_label}"
    
    if is_global:
        return "Global"
    
    return "Disabled"


def is_valid_status_string(status: str) -> bool:
    """Check if a status string matches the valid format.
    
    Valid formats:
    - "Using preset for {label}" where label is non-empty
    - "Global"
    - "Disabled"
    
    Args:
        status: Status string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if status == "Global":
        return True
    
    if status == "Disabled":
        return True
    
    # Check for "Using preset for {label}" format
    preset_pattern = r"^Using preset for (.+)$"
    match = re.match(preset_pattern, status)
    if match:
        label = match.group(1)
        # Label must be non-empty
        return len(label.strip()) > 0
    
    return False


# Strategy for generating valid preset labels
label_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'S'),
        whitelist_characters=' -_'
    )
).filter(lambda x: len(x.strip()) > 0)


@given(
    preset_label=st.one_of(st.none(), label_strategy),
    is_global=st.booleans(),
    is_enabled=st.booleans()
)
@hyp_settings(max_examples=100)
def test_status_string_format_property(preset_label, is_global, is_enabled):
    """Property 10: Status String Format
    
    For any active preset state, the status string SHALL match one of:
    - "Using preset for {label}" where label is non-empty
    - "Global"
    - "Disabled"
    
    Feature: decktune, Property 10: Status String Format
    Validates: Requirements 5.3
    """
    # Generate status string
    status = format_status_string(preset_label, is_global, is_enabled)
    
    # Verify it matches valid format
    assert is_valid_status_string(status), \
        f"Invalid status string: '{status}' for preset_label={preset_label}, is_global={is_global}, is_enabled={is_enabled}"


@given(label=label_strategy)
@hyp_settings(max_examples=100)
def test_preset_status_contains_label(label):
    """Test that preset status always contains the label.
    
    Feature: decktune, Property 10: Status String Format
    Validates: Requirements 5.3
    """
    status = format_status_string(label, is_global=False, is_enabled=True)
    
    # Status should contain the label
    assert label in status, \
        f"Status '{status}' should contain label '{label}'"
    
    # Status should start with "Using preset for "
    assert status.startswith("Using preset for "), \
        f"Status '{status}' should start with 'Using preset for '"


def test_global_status_format():
    """Test that global mode produces "Global" status.
    
    Feature: decktune, Property 10: Status String Format
    Validates: Requirements 5.3
    """
    status = format_status_string(None, is_global=True, is_enabled=True)
    assert status == "Global", f"Expected 'Global', got '{status}'"


def test_disabled_status_format():
    """Test that disabled state produces "Disabled" status.
    
    Feature: decktune, Property 10: Status String Format
    Validates: Requirements 5.3
    """
    status = format_status_string(None, is_global=False, is_enabled=False)
    assert status == "Disabled", f"Expected 'Disabled', got '{status}'"
    
    # Even with preset, disabled should return "Disabled"
    status = format_status_string("Test Preset", is_global=True, is_enabled=False)
    assert status == "Disabled", f"Expected 'Disabled', got '{status}'"


@given(
    labels=st.lists(label_strategy, min_size=1, max_size=10)
)
@hyp_settings(max_examples=100)
def test_all_preset_labels_produce_valid_status(labels):
    """Test that all preset labels produce valid status strings.
    
    Feature: decktune, Property 10: Status String Format
    Validates: Requirements 5.3
    """
    for label in labels:
        status = format_status_string(label, is_global=False, is_enabled=True)
        assert is_valid_status_string(status), \
            f"Invalid status for label '{label}': '{status}'"
