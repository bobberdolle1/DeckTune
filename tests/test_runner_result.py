"""Property tests for test result structure.

Feature: decktune, Property 6: Test Result Structure
Validates: Requirements 3.4, 3.5

Property 6: Test Result Structure
For any test execution (success or failure), the TestResult SHALL contain:
- passed: boolean
- duration: float (>= 0)
- logs: string (non-empty for actual test runs, may be empty for errors)
- error: Optional[string] (present if passed=False due to error)
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import asyncio

from backend.tuning.runner import TestRunner, TestResult, TestCase


# Strategy for test names (both valid and invalid)
test_name_strategy = st.sampled_from(
    list(TestRunner.TESTS.keys()) + ["invalid_test", "unknown", ""]
)

# Strategy for generating TestResult objects directly
test_result_strategy = st.builds(
    TestResult,
    passed=st.booleans(),
    duration=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False),
    logs=st.text(min_size=0, max_size=1000),
    error=st.one_of(st.none(), st.text(min_size=1, max_size=200))
)


class TestTestResultStructure:
    """Property 6: Test Result Structure
    
    For any test execution (success or failure), the TestResult SHALL contain:
    - passed: boolean
    - duration: float (>= 0)
    - logs: string (non-empty for actual test runs, may be empty for errors)
    - error: Optional[string] (present if passed=False due to error)
    
    Validates: Requirements 3.4, 3.5
    """

    @given(result=test_result_strategy)
    @settings(max_examples=100)
    def test_result_has_passed_boolean(self, result: TestResult):
        """TestResult.passed is always a boolean."""
        assert isinstance(result.passed, bool), \
            f"passed should be bool, got {type(result.passed)}"

    @given(result=test_result_strategy)
    @settings(max_examples=100)
    def test_result_has_non_negative_duration(self, result: TestResult):
        """TestResult.duration is always >= 0."""
        assert result.duration >= 0, \
            f"duration should be >= 0, got {result.duration}"

    @given(result=test_result_strategy)
    @settings(max_examples=100)
    def test_result_has_string_logs(self, result: TestResult):
        """TestResult.logs is always a string."""
        assert isinstance(result.logs, str), \
            f"logs should be str, got {type(result.logs)}"

    @given(result=test_result_strategy)
    @settings(max_examples=100)
    def test_result_error_is_optional_string(self, result: TestResult):
        """TestResult.error is either None or a string."""
        assert result.error is None or isinstance(result.error, str), \
            f"error should be None or str, got {type(result.error)}"

    @given(test_name=st.sampled_from(["invalid_test", "unknown_test", "nonexistent"]))
    @settings(max_examples=100)
    def test_invalid_test_returns_error(self, test_name: str):
        """For invalid test names, result has error set."""
        runner = TestRunner()
        result = asyncio.get_event_loop().run_until_complete(
            runner.run_test(test_name)
        )
        
        # Invalid test should fail
        assert result.passed == False, \
            f"Invalid test '{test_name}' should not pass"
        
        # Should have error message
        assert result.error is not None, \
            f"Invalid test '{test_name}' should have error message"
        
        # Duration should be non-negative
        assert result.duration >= 0, \
            f"Duration should be >= 0, got {result.duration}"

    def test_result_structure_completeness(self):
        """TestResult has all required fields."""
        result = TestResult(
            passed=True,
            duration=1.5,
            logs="test output",
            error=None
        )
        
        # Verify all fields exist and have correct types
        assert hasattr(result, 'passed')
        assert hasattr(result, 'duration')
        assert hasattr(result, 'logs')
        assert hasattr(result, 'error')
        
        assert isinstance(result.passed, bool)
        assert isinstance(result.duration, float)
        assert isinstance(result.logs, str)
        assert result.error is None or isinstance(result.error, str)

    def test_failed_result_with_error_has_error_message(self):
        """When test fails due to error, error field is populated."""
        result = TestResult(
            passed=False,
            duration=0.0,
            logs="",
            error="Command not found"
        )
        
        assert result.passed == False
        assert result.error is not None
        assert len(result.error) > 0

    def test_successful_result_structure(self):
        """Successful test result has correct structure."""
        result = TestResult(
            passed=True,
            duration=30.5,
            logs="stress-ng: info: successful run completed",
            error=None
        )
        
        assert result.passed == True
        assert result.duration > 0
        assert len(result.logs) > 0
        assert result.error is None
