"""Property-based tests for Vdroop process failure detection.

Feature: iron-seeker, Property 7: Process failure detection
Validates: Requirements 2.5
"""

import asyncio
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch

from backend.tuning.vdroop import VdroopTester, VdroopTestResult


# Property 7: Process failure detection
# For any stress-ng process that exits with non-zero code or times out,
# the test result SHALL be marked as failed.
@given(
    exit_code=st.integers(min_value=1, max_value=255)
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_7_nonzero_exit_code_detection(exit_code):
    """**Feature: iron-seeker, Property 7: Process failure detection**
    
    For any stress-ng process that exits with non-zero code,
    the test result SHALL be marked as failed.
    
    **Validates: Requirements 2.5**
    """
    tester = VdroopTester()
    
    # Mock the subprocess to return non-zero exit code
    mock_process = AsyncMock()
    mock_process.returncode = exit_code
    mock_process.communicate = AsyncMock(return_value=(b"output", b""))
    
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        result = await tester.run_vdroop_test(10, 100)
    
    # Result should be marked as failed
    assert result.passed is False
    assert result.exit_code == exit_code
    assert result.error is not None
    assert str(exit_code) in result.error


@pytest.mark.asyncio
async def test_timeout_detection():
    """Test that process timeout is detected as failure.
    
    **Validates: Requirements 2.5**
    """
    tester = VdroopTester()
    
    # Mock the subprocess to timeout
    mock_process = AsyncMock()
    mock_process.returncode = None
    mock_process.kill = MagicMock()
    mock_process.wait = AsyncMock()
    
    async def slow_communicate():
        await asyncio.sleep(100)  # Will be cancelled by timeout
        return (b"", b"")
    
    mock_process.communicate = slow_communicate
    
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        # Use very short duration to trigger timeout quickly
        # The actual timeout is duration + 10, so we mock wait_for to timeout
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            result = await tester.run_vdroop_test(1, 100)
    
    # Result should be marked as failed due to timeout
    assert result.passed is False
    assert "timeout" in result.error.lower() or "timed out" in result.error.lower()


@pytest.mark.asyncio
async def test_file_not_found_detection():
    """Test that missing stress-ng binary is detected as failure.
    
    **Validates: Requirements 2.5**
    """
    tester = VdroopTester()
    
    with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
        result = await tester.run_vdroop_test(10, 100)
    
    # Result should be marked as failed
    assert result.passed is False
    assert result.exit_code == -1
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_successful_process_passes():
    """Test that successful process (exit code 0) passes.
    
    This is the inverse property - verifying that success is correctly detected.
    """
    tester = VdroopTester()
    
    # Mock successful subprocess
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"successful run", b""))
    
    # Mock dmesg check to return no errors
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        with patch.object(tester, "_check_mce_errors", return_value=False):
            result = await tester.run_vdroop_test(10, 100)
    
    # Result should be marked as passed
    assert result.passed is True
    assert result.exit_code == 0
    assert result.error is None
    assert result.mce_detected is False


@pytest.mark.asyncio
async def test_mce_detection_fails_test():
    """Test that MCE errors in dmesg cause test failure.
    
    **Validates: Requirements 2.3**
    """
    tester = VdroopTester()
    
    # Mock successful subprocess
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"successful run", b""))
    
    # Mock dmesg check to return MCE errors
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        with patch.object(tester, "_check_mce_errors", return_value=True):
            result = await tester.run_vdroop_test(10, 100)
    
    # Result should be marked as failed due to MCE
    assert result.passed is False
    assert result.mce_detected is True
    assert "mce" in result.error.lower()


@given(
    exit_code=st.integers(min_value=0, max_value=255)
)
@settings(max_examples=50)
@pytest.mark.asyncio
async def test_exit_code_preserved_in_result(exit_code):
    """Test that exit code is correctly preserved in result."""
    tester = VdroopTester()
    
    mock_process = AsyncMock()
    mock_process.returncode = exit_code
    mock_process.communicate = AsyncMock(return_value=(b"output", b""))
    
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        with patch.object(tester, "_check_mce_errors", return_value=False):
            result = await tester.run_vdroop_test(10, 100)
    
    # Exit code should be preserved
    assert result.exit_code == exit_code
    
    # Only exit code 0 should pass
    if exit_code == 0:
        assert result.passed is True
    else:
        assert result.passed is False
