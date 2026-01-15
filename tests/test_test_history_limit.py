"""Property test for test history limit.

Feature: decktune, Property 11: Test History Limit
Validates: Requirements 7.4

Tests that for any sequence of N test executions where N > 10, 
the test_history list SHALL contain exactly 10 entries (the most recent 10).
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.rpc import DeckTuneRPC
from backend.platform.detect import PlatformInfo


# Maximum history size as defined in the design
MAX_HISTORY_SIZE = 10


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class MockTestResult:
    """Mock test result for testing."""
    
    def __init__(self, passed: bool = True, duration: float = 1.0):
        self.passed = passed
        self.duration = duration
        self.logs = "Test completed"
        self.error = None if passed else "Test failed"


def create_test_rpc() -> DeckTuneRPC:
    """Create a DeckTuneRPC instance for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings = MockSettingsManager()
    
    # Create minimal mocks for required dependencies
    ryzenadj = MagicMock()
    safety = MagicMock()
    event_emitter = MagicMock()
    event_emitter.emit_test_complete = AsyncMock()
    
    return DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=settings
    )


def add_test_to_history(rpc: DeckTuneRPC, test_name: str, passed: bool = True) -> None:
    """Add a test result to history using the internal method.
    
    Args:
        rpc: DeckTuneRPC instance
        test_name: Name of the test
        passed: Whether the test passed
    """
    result = MockTestResult(passed=passed)
    rpc._add_to_test_history(test_name, result)


# Strategy for generating test names
test_name_strategy = st.sampled_from([
    "cpu_quick", "cpu_long", "ram_quick", "ram_thorough", "combo"
])

# Strategy for generating test results
test_result_strategy = st.booleans()


@given(
    num_tests=st.integers(min_value=11, max_value=50)
)
@hyp_settings(max_examples=100)
def test_history_limit_property(num_tests):
    """Property 11: Test History Limit
    
    For any sequence of N test executions where N > 10, the test_history 
    list SHALL contain exactly 10 entries (the most recent 10).
    
    Feature: decktune, Property 11: Test History Limit
    Validates: Requirements 7.4
    """
    rpc = create_test_rpc()
    
    # Add N tests to history
    for i in range(num_tests):
        add_test_to_history(rpc, f"test_{i}", passed=(i % 2 == 0))
    
    # Get history
    history = rpc.settings.getSetting("test_history") or []
    
    # Verify exactly 10 entries
    assert len(history) == MAX_HISTORY_SIZE, \
        f"Expected {MAX_HISTORY_SIZE} entries, got {len(history)} after {num_tests} tests"


@given(
    num_tests=st.integers(min_value=11, max_value=30),
    test_names=st.lists(test_name_strategy, min_size=11, max_size=30)
)
@hyp_settings(max_examples=100)
def test_history_contains_most_recent(num_tests, test_names):
    """Test that history contains the most recent 10 entries.
    
    Feature: decktune, Property 11: Test History Limit
    Validates: Requirements 7.4
    """
    rpc = create_test_rpc()
    
    # Ensure we have enough test names
    test_names = test_names[:num_tests] if len(test_names) >= num_tests else test_names * (num_tests // len(test_names) + 1)
    test_names = test_names[:num_tests]
    
    # Add tests with unique identifiers
    for i in range(num_tests):
        # Use index as part of test name to track order
        add_test_to_history(rpc, f"{test_names[i]}_{i}", passed=True)
    
    # Get history
    history = rpc.settings.getSetting("test_history") or []
    
    # Verify exactly 10 entries
    assert len(history) == MAX_HISTORY_SIZE, \
        f"Expected {MAX_HISTORY_SIZE} entries, got {len(history)}"
    
    # Verify these are the most recent 10 (indices num_tests-10 to num_tests-1)
    expected_indices = list(range(num_tests - MAX_HISTORY_SIZE, num_tests))
    
    for i, entry in enumerate(history):
        expected_idx = expected_indices[i]
        expected_name = f"{test_names[expected_idx]}_{expected_idx}"
        assert entry["test_name"] == expected_name, \
            f"Entry {i} should be '{expected_name}', got '{entry['test_name']}'"


@given(
    num_tests=st.integers(min_value=1, max_value=10)
)
@hyp_settings(max_examples=100)
def test_history_under_limit(num_tests):
    """Test that history with <= 10 entries is not truncated.
    
    Feature: decktune, Property 11: Test History Limit
    Validates: Requirements 7.4
    """
    rpc = create_test_rpc()
    
    # Add N tests where N <= 10
    for i in range(num_tests):
        add_test_to_history(rpc, f"test_{i}", passed=True)
    
    # Get history
    history = rpc.settings.getSetting("test_history") or []
    
    # Verify all entries are present
    assert len(history) == num_tests, \
        f"Expected {num_tests} entries, got {len(history)}"


def test_history_exactly_at_limit():
    """Test that history with exactly 10 entries is preserved.
    
    Feature: decktune, Property 11: Test History Limit
    Validates: Requirements 7.4
    """
    rpc = create_test_rpc()
    
    # Add exactly 10 tests
    for i in range(10):
        add_test_to_history(rpc, f"test_{i}", passed=True)
    
    # Get history
    history = rpc.settings.getSetting("test_history") or []
    
    # Verify exactly 10 entries
    assert len(history) == 10, f"Expected 10 entries, got {len(history)}"
    
    # Add one more
    add_test_to_history(rpc, "test_10", passed=True)
    
    # Get history again
    history = rpc.settings.getSetting("test_history") or []
    
    # Still exactly 10 entries
    assert len(history) == 10, f"Expected 10 entries after adding 11th, got {len(history)}"
    
    # First entry should now be test_1 (test_0 was removed)
    assert history[0]["test_name"] == "test_1", \
        f"First entry should be 'test_1', got '{history[0]['test_name']}'"
    
    # Last entry should be test_10
    assert history[-1]["test_name"] == "test_10", \
        f"Last entry should be 'test_10', got '{history[-1]['test_name']}'"


@given(
    results=st.lists(test_result_strategy, min_size=15, max_size=30)
)
@hyp_settings(max_examples=100)
def test_history_preserves_pass_fail_status(results):
    """Test that pass/fail status is preserved in history.
    
    Feature: decktune, Property 11: Test History Limit
    Validates: Requirements 7.4
    """
    rpc = create_test_rpc()
    
    # Add tests with varying pass/fail status
    for i, passed in enumerate(results):
        add_test_to_history(rpc, f"test_{i}", passed=passed)
    
    # Get history
    history = rpc.settings.getSetting("test_history") or []
    
    # Verify exactly 10 entries
    assert len(history) == MAX_HISTORY_SIZE
    
    # Verify pass/fail status matches the last 10 results
    expected_results = results[-MAX_HISTORY_SIZE:]
    for i, entry in enumerate(history):
        assert entry["passed"] == expected_results[i], \
            f"Entry {i} passed status should be {expected_results[i]}, got {entry['passed']}"
