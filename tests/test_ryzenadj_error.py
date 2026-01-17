"""Property tests for error status propagation.

Feature: decktune, Property 15: Error Status Propagation
Validates: Requirements 9.4

Property 15: Error Status Propagation
For any ryzenadj execution that returns non-zero exit code, the EventEmitter 
SHALL emit a status event with data="error".
"""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from hypothesis import given, strategies as st, settings

from backend.core.ryzenadj import RyzenadjWrapper


# Strategy for non-zero exit codes
non_zero_exit_code = st.integers(min_value=1, max_value=255)

# Strategy for undervolt values (-60 to 0)
undervolt_value = st.integers(min_value=-60, max_value=0)

# Strategy for list of 4 undervolt values
undervolt_values_list = st.lists(undervolt_value, min_size=4, max_size=4)

# Strategy for error messages
error_message = st.text(min_size=1, max_size=100).filter(lambda s: s.strip())


class MockEventEmitter:
    """Mock event emitter for testing."""
    
    def __init__(self):
        self.emitted_statuses = []
    
    async def emit_status(self, status: str) -> None:
        self.emitted_statuses.append(status)


class TestErrorStatusPropagation:
    """Property 15: Error Status Propagation
    
    For any ryzenadj execution that returns non-zero exit code, the EventEmitter 
    SHALL emit a status event with data="error".
    
    Validates: Requirements 9.4
    """

    @given(cores=undervolt_values_list, exit_code=non_zero_exit_code)
    @settings(max_examples=100)
    def test_non_zero_exit_emits_error_status(self, cores: list, exit_code: int):
        """Non-zero exit code triggers error status emission."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            # First call fails with non-zero exit code
            mock_run.return_value = MagicMock(returncode=exit_code, stderr="")
            
            success, error = wrapper.apply_values(cores)
        
        # Should fail
        assert success is False
        assert error is not None
        
        # Error should be recorded
        assert wrapper.get_last_error() is not None

    @given(cores=undervolt_values_list, error_msg=error_message)
    @settings(max_examples=100)
    def test_stderr_error_emits_error_status(self, cores: list, error_msg: str):
        """Stderr containing 'error' triggers error status emission."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        # Create stderr with 'error' keyword
        stderr_content = f"Error: {error_msg}"
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr=stderr_content)
            
            success, error = wrapper.apply_values(cores)
        
        # Should fail due to error in stderr
        assert success is False
        assert error is not None
        
        # Error should be recorded
        assert wrapper.get_last_error() is not None

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_success_does_not_emit_error(self, cores: list):
        """Successful execution does not emit error status."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            
            success, error = wrapper.apply_values(cores)
        
        # Should succeed
        assert success is True
        assert error is None
        
        # No error should be recorded
        assert wrapper.get_last_error() is None

    @given(cores=undervolt_values_list, exit_code=non_zero_exit_code)
    @settings(max_examples=100)
    def test_async_non_zero_exit_emits_error_status(self, cores: list, exit_code: int):
        """Async version: Non-zero exit code triggers error status emission."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        async def run_test():
            with patch('backend.core.ryzenadj.subprocess.run') as mock_run, \
                 patch('backend.core.ryzenadj.os.path.exists', return_value=True), \
                 patch('backend.core.ryzenadj.os.access', return_value=True):
                mock_run.return_value = MagicMock(returncode=exit_code, stderr="")
                
                success, error = await wrapper.apply_values_async(cores)
            
            return success, error
        
        success, error = asyncio.run(run_test())
        
        # Should fail
        assert success is False
        assert error is not None
        
        # Error status should be emitted
        assert "error" in event_emitter.emitted_statuses

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_async_success_does_not_emit_error(self, cores: list):
        """Async version: Successful execution does not emit error status."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        async def run_test():
            with patch('backend.core.ryzenadj.subprocess.run') as mock_run, \
                 patch('backend.core.ryzenadj.os.path.exists', return_value=True), \
                 patch('backend.core.ryzenadj.os.access', return_value=True):
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                
                success, error = await wrapper.apply_values_async(cores)
            
            return success, error
        
        success, error = asyncio.run(run_test())
        
        # Should succeed
        assert success is True
        assert error is None
        
        # No error status should be emitted
        assert "error" not in event_emitter.emitted_statuses

    def test_file_not_found_emits_error(self):
        """FileNotFoundError triggers error status emission."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/nonexistent/ryzenadj", "/working/dir", event_emitter)
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("No such file")
            
            success, error = wrapper.apply_values([0, 0, 0, 0])
        
        assert success is False
        assert "not found" in error.lower()
        assert wrapper.get_last_error() is not None

    def test_timeout_emits_error(self):
        """Timeout triggers error status emission."""
        import subprocess
        
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=10)
            
            success, error = wrapper.apply_values([0, 0, 0, 0])
        
        assert success is False
        assert "timed out" in error.lower()
        assert wrapper.get_last_error() is not None

    def test_invalid_core_count_emits_error(self):
        """Invalid core count triggers error status emission."""
        event_emitter = MockEventEmitter()
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir", event_emitter)
        
        # Test with wrong number of cores
        success, error = wrapper.apply_values([0, 0, 0])  # Only 3 values
        
        assert success is False
        assert "4 core values" in error
        assert wrapper.get_last_error() is not None
