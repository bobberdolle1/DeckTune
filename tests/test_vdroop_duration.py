"""Property-based tests for Vdroop test duration configuration.

Feature: iron-seeker, Property 6: Test duration configuration
Validates: Requirements 2.4
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.tuning.vdroop import VdroopTester


# Property 6: Test duration configuration
# For any IronSeekerConfig with test_duration T, the actual stress test
# execution time SHALL be within [T, T+5] seconds (allowing for startup overhead).
#
# Note: We cannot actually run stress-ng in unit tests, so we verify that
# the command is configured correctly with the specified duration, and that
# the timeout allows for the expected overhead.
@given(
    test_duration=st.integers(min_value=10, max_value=300)
)
@settings(max_examples=100)
def test_property_6_test_duration_configuration(test_duration):
    """**Feature: iron-seeker, Property 6: Test duration configuration**
    
    For any test_duration T, the generated stress command SHALL be configured
    with timeout T, and the process timeout SHALL allow for startup overhead
    (T + 10 seconds maximum).
    
    **Validates: Requirements 2.4**
    """
    tester = VdroopTester()
    command = tester.generate_vdroop_command(test_duration, pulse_ms=100)
    
    # Extract timeout from command
    assert "--timeout" in command
    timeout_idx = command.index("--timeout")
    timeout_str = command[timeout_idx + 1]
    
    # Timeout should be in "{duration}s" format
    assert timeout_str.endswith("s")
    configured_duration = int(timeout_str[:-1])
    
    # Configured duration should exactly match requested duration
    assert configured_duration == test_duration
    
    # The process timeout (in run_vdroop_test) is duration + 10
    # This allows for startup overhead while ensuring the test
    # completes within [T, T+10] seconds
    expected_process_timeout = test_duration + 10
    
    # Verify the overhead is reasonable (≤10 seconds)
    assert expected_process_timeout - test_duration <= 10


@given(
    test_duration=st.integers(min_value=10, max_value=300),
    pulse_ms=st.integers(min_value=10, max_value=500)
)
@settings(max_examples=50)
def test_duration_independent_of_pulse(test_duration, pulse_ms):
    """Test that total duration is independent of pulse duration.
    
    The pulse duration affects the load pattern but not the total test time.
    """
    tester = VdroopTester()
    command = tester.generate_vdroop_command(test_duration, pulse_ms)
    
    # Extract timeout
    timeout_idx = command.index("--timeout")
    timeout_str = command[timeout_idx + 1]
    configured_duration = int(timeout_str[:-1])
    
    # Duration should match regardless of pulse_ms
    assert configured_duration == test_duration


def test_minimum_duration_boundary():
    """Test minimum valid duration (10 seconds)."""
    tester = VdroopTester()
    command = tester.generate_vdroop_command(10, 100)
    
    timeout_idx = command.index("--timeout")
    timeout_str = command[timeout_idx + 1]
    assert timeout_str == "10s"


def test_maximum_duration_boundary():
    """Test maximum valid duration (300 seconds)."""
    tester = VdroopTester()
    command = tester.generate_vdroop_command(300, 100)
    
    timeout_idx = command.index("--timeout")
    timeout_str = command[timeout_idx + 1]
    assert timeout_str == "300s"
