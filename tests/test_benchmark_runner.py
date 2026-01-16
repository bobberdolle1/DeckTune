"""Unit tests for BenchmarkRunner.

Feature: decktune-3.0-automation, Benchmark Runner Tests
Validates: Requirements 7.1, 7.2

Tests stress-ng command construction, bogo-ops parsing, and error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from backend.tuning.benchmark import BenchmarkRunner, BenchmarkResult, BENCHMARK_DURATION
from backend.tuning.runner import TestRunner


@pytest.fixture
def mock_test_runner():
    """Create a mock TestRunner."""
    runner = Mock(spec=TestRunner)
    runner.get_missing_binaries.return_value = []  # All binaries available
    return runner


@pytest.fixture
def benchmark_runner(mock_test_runner):
    """Create a BenchmarkRunner with mock TestRunner."""
    return BenchmarkRunner(mock_test_runner)


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner class."""
    
    def test_parse_bogo_ops_standard_output(self, benchmark_runner):
        """Test parsing bogo ops from standard stress-ng output."""
        output = """stress-ng: info:  [12345] dispatching hogs: 4 matrix
stress-ng: info:  [12345] successful run completed in 10.00s
stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)
"""
        score = benchmark_runner._parse_bogo_ops(output)
        assert score == 123456.70
    
    def test_parse_bogo_ops_with_decimal(self, benchmark_runner):
        """Test parsing bogo ops with decimal values."""
        output = "stress-ng: info:  [12345] matrix: 999999 bogo ops in 10.00s (99999.99 bogo ops/s)"
        score = benchmark_runner._parse_bogo_ops(output)
        assert score == 99999.99
    
    def test_parse_bogo_ops_integer_value(self, benchmark_runner):
        """Test parsing bogo ops with integer value."""
        output = "stress-ng: info:  [12345] matrix: 1000000 bogo ops in 10.00s (100000 bogo ops/s)"
        score = benchmark_runner._parse_bogo_ops(output)
        assert score == 100000.0
    
    def test_parse_bogo_ops_case_insensitive(self, benchmark_runner):
        """Test parsing is case insensitive."""
        output = "stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 BOGO OPS/S)"
        score = benchmark_runner._parse_bogo_ops(output)
        assert score == 123456.70
    
    def test_parse_bogo_ops_not_found(self, benchmark_runner):
        """Test parsing returns None when pattern not found."""
        output = "stress-ng: error: some error occurred"
        score = benchmark_runner._parse_bogo_ops(output)
        assert score is None
    
    def test_parse_bogo_ops_empty_output(self, benchmark_runner):
        """Test parsing returns None for empty output."""
        output = ""
        score = benchmark_runner._parse_bogo_ops(output)
        assert score is None
    
    def test_parse_bogo_ops_malformed_number(self, benchmark_runner):
        """Test parsing returns None for malformed number."""
        output = "stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (abc bogo ops/s)"
        score = benchmark_runner._parse_bogo_ops(output)
        assert score is None
    
    @pytest.mark.asyncio
    async def test_run_benchmark_missing_binary(self, mock_test_runner):
        """Test error handling when stress-ng is not available."""
        mock_test_runner.get_missing_binaries.return_value = ["stress-ng"]
        runner = BenchmarkRunner(mock_test_runner)
        
        with pytest.raises(RuntimeError, match="stress-ng binary not found"):
            await runner.run_benchmark([0, 0, 0, 0])
    
    @pytest.mark.asyncio
    async def test_run_benchmark_success(self, benchmark_runner, mock_test_runner):
        """Test successful benchmark execution."""
        # Mock the subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (
            b"stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)\n",
            b""
        )
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                result = await benchmark_runner.run_benchmark([0, 0, 0, 0])
        
        assert isinstance(result, BenchmarkResult)
        assert result.score == 123456.70
        assert result.cores_used == [0, 0, 0, 0]
        assert result.duration > 0
        assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_run_benchmark_with_cores(self, benchmark_runner):
        """Test benchmark records correct core values."""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (
            b"stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (100000.00 bogo ops/s)\n",
            b""
        )
        
        cores = [-25, -25, -25, -25]
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                result = await benchmark_runner.run_benchmark(cores)
        
        assert result.cores_used == [-25, -25, -25, -25]
        # Verify original list wasn't modified
        assert cores == [-25, -25, -25, -25]
    
    @pytest.mark.asyncio
    async def test_run_benchmark_default_cores(self, benchmark_runner):
        """Test benchmark uses default cores when None provided."""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (
            b"stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (100000.00 bogo ops/s)\n",
            b""
        )
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                result = await benchmark_runner.run_benchmark(None)
        
        assert result.cores_used == [0, 0, 0, 0]
    
    @pytest.mark.asyncio
    async def test_run_benchmark_parse_failure(self, benchmark_runner):
        """Test error handling when bogo ops cannot be parsed."""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (
            b"stress-ng: error: some error occurred\n",
            b""
        )
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                with pytest.raises(RuntimeError, match="Failed to parse benchmark score"):
                    await benchmark_runner.run_benchmark([0, 0, 0, 0])
    
    @pytest.mark.asyncio
    async def test_run_benchmark_timeout(self, benchmark_runner):
        """Test error handling when benchmark times out."""
        mock_process = AsyncMock()
        # Simulate timeout by raising TimeoutError
        mock_process.communicate.side_effect = asyncio.TimeoutError()
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                with pytest.raises(RuntimeError, match="Benchmark timed out"):
                    await benchmark_runner.run_benchmark([0, 0, 0, 0])
    
    @pytest.mark.asyncio
    async def test_run_benchmark_execution_error(self, benchmark_runner):
        """Test error handling when subprocess execution fails."""
        with patch('asyncio.create_subprocess_exec', side_effect=OSError("Command not found")):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                with pytest.raises(RuntimeError, match="Benchmark execution failed"):
                    await benchmark_runner.run_benchmark([0, 0, 0, 0])
    
    @pytest.mark.asyncio
    async def test_run_benchmark_command_construction(self, benchmark_runner):
        """Test that stress-ng command is constructed correctly."""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (
            b"stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (100000.00 bogo ops/s)\n",
            b""
        )
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process) as mock_exec:
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                await benchmark_runner.run_benchmark([0, 0, 0, 0])
        
        # Verify command was called with correct arguments
        call_args = mock_exec.call_args[0]
        assert call_args[0] == '/usr/bin/stress-ng'
        assert '--matrix' in call_args
        assert '0' in call_args  # Use all CPUs
        assert '--timeout' in call_args
        assert f'{BENCHMARK_DURATION}s' in call_args
        assert '--metrics-brief' in call_args
    
    @pytest.mark.asyncio
    async def test_run_benchmark_stderr_included(self, benchmark_runner):
        """Test that stderr is included in output for parsing."""
        mock_process = AsyncMock()
        # Put bogo ops in stderr instead of stdout
        mock_process.communicate.return_value = (
            b"",
            b"stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)\n"
        )
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('backend.tuning.benchmark._get_binary_path', return_value='/usr/bin/stress-ng'):
                result = await benchmark_runner.run_benchmark([0, 0, 0, 0])
        
        # Should successfully parse from stderr
        assert result.score == 123456.70
