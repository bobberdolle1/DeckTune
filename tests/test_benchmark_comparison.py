"""Property-based tests for benchmark comparison math.

Feature: decktune-3.0-automation, Property 29: Benchmark comparison math
Validates: Requirements 7.3
"""

import pytest
from hypothesis import given, strategies as st

from backend.tuning.benchmark import BenchmarkRunner, BenchmarkResult


@given(
    score1=st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    score2=st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_benchmark_comparison_math(score1, score2):
    """Property 29: Benchmark comparison math.
    
    For any two benchmark results B1 and B2, the percentage change must equal
    ((B2.score - B1.score) / B1.score) * 100
    
    Validates: Requirements 7.3
    """
    # Create benchmark results with the given scores
    result1 = BenchmarkResult(
        score=score1,
        duration=10.0,
        cores_used=[0, 0, 0, 0],
        timestamp="2026-01-15T10:00:00Z"
    )
    
    result2 = BenchmarkResult(
        score=score2,
        duration=10.0,
        cores_used=[-25, -25, -25, -25],
        timestamp="2026-01-15T10:10:00Z"
    )
    
    # Create runner and compare results
    runner = BenchmarkRunner(test_runner=None)  # test_runner not needed for comparison
    comparison = runner.compare_results(result1, result2)
    
    # Calculate expected values
    expected_score_diff = score2 - score1
    expected_percent_change = (expected_score_diff / score1) * 100
    expected_improvement = expected_score_diff > 0
    
    # Verify comparison results
    assert abs(comparison['score_diff'] - expected_score_diff) < 0.01, \
        f"Score diff mismatch: {comparison['score_diff']} != {expected_score_diff}"
    
    assert abs(comparison['percent_change'] - expected_percent_change) < 0.01, \
        f"Percent change mismatch: {comparison['percent_change']} != {expected_percent_change}"
    
    assert comparison['improvement'] == expected_improvement, \
        f"Improvement flag mismatch: {comparison['improvement']} != {expected_improvement}"


def test_benchmark_comparison_equal_scores():
    """Test comparison when scores are equal (edge case)."""
    result1 = BenchmarkResult(
        score=100000.0,
        duration=10.0,
        cores_used=[0, 0, 0, 0],
        timestamp="2026-01-15T10:00:00Z"
    )
    
    result2 = BenchmarkResult(
        score=100000.0,
        duration=10.0,
        cores_used=[0, 0, 0, 0],
        timestamp="2026-01-15T10:10:00Z"
    )
    
    runner = BenchmarkRunner(test_runner=None)
    comparison = runner.compare_results(result1, result2)
    
    assert comparison['score_diff'] == 0.0
    assert comparison['percent_change'] == 0.0
    assert comparison['improvement'] is False


def test_benchmark_comparison_improvement():
    """Test comparison when current is better than baseline."""
    baseline = BenchmarkResult(
        score=100000.0,
        duration=10.0,
        cores_used=[0, 0, 0, 0],
        timestamp="2026-01-15T10:00:00Z"
    )
    
    current = BenchmarkResult(
        score=110000.0,
        duration=10.0,
        cores_used=[-25, -25, -25, -25],
        timestamp="2026-01-15T10:10:00Z"
    )
    
    runner = BenchmarkRunner(test_runner=None)
    comparison = runner.compare_results(baseline, current)
    
    assert comparison['score_diff'] == 10000.0
    assert abs(comparison['percent_change'] - 10.0) < 0.01
    assert comparison['improvement'] is True


def test_benchmark_comparison_degradation():
    """Test comparison when current is worse than baseline."""
    baseline = BenchmarkResult(
        score=100000.0,
        duration=10.0,
        cores_used=[0, 0, 0, 0],
        timestamp="2026-01-15T10:00:00Z"
    )
    
    current = BenchmarkResult(
        score=90000.0,
        duration=10.0,
        cores_used=[-50, -50, -50, -50],
        timestamp="2026-01-15T10:10:00Z"
    )
    
    runner = BenchmarkRunner(test_runner=None)
    comparison = runner.compare_results(baseline, current)
    
    assert comparison['score_diff'] == -10000.0
    assert abs(comparison['percent_change'] - (-10.0)) < 0.01
    assert comparison['improvement'] is False
