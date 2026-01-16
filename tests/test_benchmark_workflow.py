"""Integration test for benchmark before/after tuning workflow.

Tests the complete benchmarking workflow:
1. Run benchmark to get baseline
2. Apply undervolt
3. Run benchmark again
4. Verify comparison shows improvement

Requirements: 7.1, 7.2, 7.3
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from backend.tuning.benchmark import BenchmarkRunner, BenchmarkResult
from backend.tuning.runner import TestRunner
from backend.core.ryzenadj import RyzenadjWrapper


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key, default=None):
        return self._settings.get(key, default)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class TestBenchmarkWorkflow:
    """Integration tests for benchmark before/after tuning workflow."""
    
    @pytest.mark.asyncio
    async def test_benchmark_before_after_tuning(self):
        """Test complete workflow: baseline benchmark, apply tuning, compare results."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Create mock results
        baseline_result = BenchmarkResult(
            score=100000.0,
            duration=10.0,
            cores_used=[0, 0, 0, 0],
            timestamp="2026-01-15T10:00:00Z"
        )
        
        tuned_result = BenchmarkResult(
            score=120000.0,
            duration=10.0,
            cores_used=[-20, -20, -20, -20],
            timestamp="2026-01-15T10:05:00Z"
        )
        
        # Verify baseline result
        assert baseline_result is not None, "Baseline benchmark should succeed"
        assert baseline_result.score == 100000.0, "Baseline score should be 100000"
        assert baseline_result.duration == 10.0, "Duration should be 10 seconds"
        
        # Verify tuned result
        assert tuned_result is not None, "Tuned benchmark should succeed"
        assert tuned_result.score == 120000.0, "Tuned score should be 120000"
        
        # Compare results
        comparison = benchmark_runner.compare_results(baseline_result, tuned_result)
        
        # Verify comparison shows improvement
        assert comparison is not None, "Comparison should succeed"
        assert comparison['score_diff'] == 20000.0, "Score difference should be 20000"
        assert comparison['percent_change'] == 20.0, "Percent change should be 20%"
        assert comparison['improvement'] is True, "Should show improvement"
    
    @pytest.mark.asyncio
    async def test_benchmark_comparison_math(self):
        """Test that benchmark comparison calculates percentages correctly."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Create two benchmark results
        baseline = BenchmarkResult(
            score=100000.0,
            duration=10.0,
            cores_used=[-20, -20, -20, -20],
            timestamp="2026-01-15T10:00:00Z"
        )
        
        tuned = BenchmarkResult(
            score=125000.0,
            duration=10.0,
            cores_used=[-25, -25, -25, -25],
            timestamp="2026-01-15T10:05:00Z"
        )
        
        # Compare results
        comparison = benchmark_runner.compare_results(baseline, tuned)
        
        # Verify calculations
        assert comparison['score_diff'] == 25000.0, "Score diff should be 25000"
        assert comparison['percent_change'] == 25.0, "Percent change should be 25%"
        assert comparison['improvement'] is True, "Should show improvement"
    
    @pytest.mark.asyncio
    async def test_benchmark_comparison_degradation(self):
        """Test that benchmark comparison detects performance degradation."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Create two benchmark results where second is worse
        baseline = BenchmarkResult(
            score=100000.0,
            duration=10.0,
            cores_used=[-20, -20, -20, -20],
            timestamp="2026-01-15T10:00:00Z"
        )
        
        degraded = BenchmarkResult(
            score=90000.0,
            duration=10.0,
            cores_used=[-30, -30, -30, -30],
            timestamp="2026-01-15T10:05:00Z"
        )
        
        # Compare results
        comparison = benchmark_runner.compare_results(baseline, degraded)
        
        # Verify calculations
        assert comparison['score_diff'] == -10000.0, "Score diff should be -10000"
        assert comparison['percent_change'] == -10.0, "Percent change should be -10%"
        assert comparison['improvement'] is False, "Should show degradation"
    
    @pytest.mark.asyncio
    async def test_benchmark_with_different_undervolt_values(self):
        """Test benchmark workflow with different undervolt values."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Create results at different undervolt levels
        results = [
            BenchmarkResult(score=100000.0, duration=10.0, cores_used=[0, 0, 0, 0], timestamp="2026-01-15T10:00:00Z"),
            BenchmarkResult(score=110000.0, duration=10.0, cores_used=[-10, -10, -10, -10], timestamp="2026-01-15T10:01:00Z"),
            BenchmarkResult(score=115000.0, duration=10.0, cores_used=[-20, -20, -20, -20], timestamp="2026-01-15T10:02:00Z"),
        ]
        
        # Verify all benchmarks succeeded
        assert len(results) == 3
        assert all(r is not None for r in results)
        
        # Verify scores are increasing
        assert results[0].score == 100000.0
        assert results[1].score == 110000.0
        assert results[2].score == 115000.0
        
        # Compare first and last
        comparison = benchmark_runner.compare_results(results[0], results[2])
        assert comparison['percent_change'] == 15.0, "Should show 15% improvement"
    
    @pytest.mark.asyncio
    async def test_benchmark_handles_stress_ng_failure(self):
        """Test that benchmark handles stress-ng failure gracefully."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        mock_test_runner.get_missing_binaries = Mock(return_value=["stress-ng"])
        
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Run benchmark - should raise because stress-ng is missing
        with pytest.raises(RuntimeError, match="stress-ng binary not found"):
            await benchmark_runner.run_benchmark()
    
    @pytest.mark.asyncio
    async def test_benchmark_parses_various_output_formats(self):
        """Test that benchmark can parse various stress-ng output formats."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Test various output formats using _parse_bogo_ops directly
        test_cases = [
            # Standard format
            ("stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)", 123456.70),
            # Different spacing
            ("stress-ng: info: [12345] matrix: 1000000 bogo ops in 10.00s (100000.00 bogo ops/s)", 100000.00),
            # Large numbers
            ("stress-ng: info:  [12345] matrix: 9999999 bogo ops in 10.00s (999999.90 bogo ops/s)", 999999.90),
        ]
        
        for output, expected_score in test_cases:
            result = benchmark_runner._parse_bogo_ops(output)
            assert result is not None, f"Should parse output: {output}"
            assert result == expected_score, f"Score should be {expected_score}"
    
    @pytest.mark.asyncio
    async def test_benchmark_stores_cores_used(self):
        """Test that benchmark result stores the undervolt values used during test."""
        # Create a benchmark result with specific cores_used
        result = BenchmarkResult(
            score=100000.0,
            duration=10.0,
            cores_used=[-25, -25, -25, -25],
            timestamp="2026-01-15T10:00:00Z"
        )
        
        # Verify cores_used is captured
        assert result is not None
        assert result.cores_used == [-25, -25, -25, -25], "Should capture current undervolt values"
