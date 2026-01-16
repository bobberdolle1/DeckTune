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
        settings_manager = MockSettingsManager()
        
        # Create mock test runner
        mock_test_runner = Mock(spec=TestRunner)
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        
        # Mock stress-ng output for baseline (lower score)
        baseline_output = """
stress-ng: info:  [12345] matrix: 1000000 bogo ops in 10.00s (100000.00 bogo ops/s)
"""
        
        # Mock stress-ng output for after tuning (higher score)
        tuned_output = """
stress-ng: info:  [12346] matrix: 1200000 bogo ops in 10.00s (120000.00 bogo ops/s)
"""
        
        # Configure mock to return different outputs
        mock_test_runner.run_stress_ng = AsyncMock(side_effect=[
            (True, baseline_output, ""),  # First call: baseline
            (True, tuned_output, "")       # Second call: after tuning
        ])
        
        # Create benchmark runner
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Step 1: Run baseline benchmark
        baseline_result = await benchmark_runner.run_benchmark()
        
        # Verify baseline result
        assert baseline_result is not None, "Baseline benchmark should succeed"
        assert baseline_result.score == 100000.00, "Baseline score should be 100000"
        assert baseline_result.duration == 10.0, "Duration should be 10 seconds"
        
        # Step 2: Apply undervolt (simulated - in real scenario would call ryzenadj)
        # In this test, we just verify the workflow, not actual hardware changes
        
        # Step 3: Run benchmark after tuning
        tuned_result = await benchmark_runner.run_benchmark()
        
        # Verify tuned result
        assert tuned_result is not None, "Tuned benchmark should succeed"
        assert tuned_result.score == 120000.00, "Tuned score should be 120000"
        
        # Step 4: Compare results
        comparison = benchmark_runner.compare_results(baseline_result, tuned_result)
        
        # Verify comparison shows improvement
        assert comparison is not None, "Comparison should succeed"
        assert comparison['score_diff'] == 20000.00, "Score difference should be 20000"
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
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        
        # Mock outputs for different undervolt levels
        outputs = [
            (True, "stress-ng: info:  [1] matrix: 1000000 bogo ops in 10.00s (100000.00 bogo ops/s)", ""),
            (True, "stress-ng: info:  [2] matrix: 1100000 bogo ops in 10.00s (110000.00 bogo ops/s)", ""),
            (True, "stress-ng: info:  [3] matrix: 1150000 bogo ops in 10.00s (115000.00 bogo ops/s)", ""),
        ]
        
        mock_test_runner.run_stress_ng = AsyncMock(side_effect=outputs)
        
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Run benchmarks at different undervolt levels
        results = []
        for i in range(3):
            result = await benchmark_runner.run_benchmark()
            results.append(result)
        
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
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        
        # Mock stress-ng failure
        mock_test_runner.run_stress_ng = AsyncMock(return_value=(False, "", "stress-ng: error: failed to start"))
        
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Run benchmark
        result = await benchmark_runner.run_benchmark()
        
        # Verify failure is handled
        assert result is None, "Should return None on failure"
    
    @pytest.mark.asyncio
    async def test_benchmark_parses_various_output_formats(self):
        """Test that benchmark can parse various stress-ng output formats."""
        # Setup
        mock_test_runner = Mock(spec=TestRunner)
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Test various output formats
        test_cases = [
            # Standard format
            ("stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)", 123456.70),
            # Different spacing
            ("stress-ng: info: [12345] matrix: 1000000 bogo ops in 10.00s (100000.00 bogo ops/s)", 100000.00),
            # Large numbers
            ("stress-ng: info:  [12345] matrix: 9999999 bogo ops in 10.00s (999999.90 bogo ops/s)", 999999.90),
        ]
        
        for output, expected_score in test_cases:
            mock_test_runner.run_stress_ng = AsyncMock(return_value=(True, output, ""))
            result = await benchmark_runner.run_benchmark()
            
            assert result is not None, f"Should parse output: {output}"
            assert result.score == expected_score, f"Score should be {expected_score}"
    
    @pytest.mark.asyncio
    async def test_benchmark_stores_cores_used(self):
        """Test that benchmark result stores the undervolt values used during test."""
        # Setup
        settings_manager = MockSettingsManager()
        settings_manager.setSetting("cores", [-25, -25, -25, -25])
        
        mock_test_runner = Mock(spec=TestRunner)
        mock_test_runner.get_missing_binaries = Mock(return_value=[])
        mock_test_runner.run_stress_ng = AsyncMock(return_value=(
            True,
            "stress-ng: info:  [12345] matrix: 1000000 bogo ops in 10.00s (100000.00 bogo ops/s)",
            ""
        ))
        mock_test_runner.settings = settings_manager
        
        benchmark_runner = BenchmarkRunner(mock_test_runner)
        
        # Run benchmark
        result = await benchmark_runner.run_benchmark()
        
        # Verify cores_used is captured
        assert result is not None
        assert result.cores_used == [-25, -25, -25, -25], "Should capture current undervolt values"
