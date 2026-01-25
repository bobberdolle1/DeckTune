"""Benchmark runner for performance testing.

Feature: decktune-3.0-automation, Benchmark Module
Validates: Requirements 7.1, 7.2, 7.3, 7.5

Provides quick performance benchmarking using stress-ng matrix operations.
"""

import asyncio
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.tuning.runner import TestRunner, _get_binary_path


# Benchmark duration in seconds
BENCHMARK_DURATION = 10


@dataclass
class BenchmarkResult:
    """Result of benchmark run.
    
    Attributes:
        score: Operations per second (bogo ops/s)
        duration: Actual test duration in seconds
        cores_used: Undervolt values during test (mV)
        timestamp: ISO timestamp of benchmark execution
    """
    score: float
    duration: float
    cores_used: List[int]
    timestamp: str


class BenchmarkRunner:
    """Quick performance benchmarking using stress-ng.
    
    Executes 10-second stress-ng matrix operations and parses
    the bogo-ops metric for performance comparison.
    """
    
    def __init__(self, test_runner: TestRunner):
        """Initialize benchmark runner.
        
        Args:
            test_runner: TestRunner instance for executing stress-ng
        """
        self._test_runner = test_runner
    
    async def run_benchmark(self, cores_used: Optional[List[int]] = None) -> BenchmarkResult:
        """Run 10-second benchmark.
        
        Uses stress-ng --matrix with bogo-ops output parsing.
        
        Args:
            cores_used: Current undervolt values (for recording in result)
            
        Returns:
            BenchmarkResult with score and metadata
            
        Raises:
            RuntimeError: If stress-ng is not available or execution fails
            
        Requirements: 7.1, 7.2
        """
        if cores_used is None:
            cores_used = [0, 0, 0, 0]
        
        # Check if stress-ng is available
        missing = self._test_runner.get_missing_binaries()
        if "stress-ng" in missing:
            raise RuntimeError("stress-ng binary not found")
        
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Execute stress-ng with matrix workload
        stress_ng_path = _get_binary_path("stress-ng")
        command = [
            stress_ng_path,
            "--matrix", "0",  # Use all available CPUs
            "--timeout", f"{BENCHMARK_DURATION}s",
            "--metrics-brief"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=BENCHMARK_DURATION + 5  # Add buffer for startup/shutdown
            )
            
            output = stdout.decode("utf-8", errors="replace")
            if stderr:
                output += "\n" + stderr.decode("utf-8", errors="replace")
            
            # Parse bogo ops from output
            score = self._parse_bogo_ops(output)
            
            if score is None:
                raise RuntimeError(f"Failed to parse benchmark score from output: {output[:500]}")
            
            duration = time.time() - start_time
            
            return BenchmarkResult(
                score=score,
                duration=duration,
                cores_used=cores_used.copy(),
                timestamp=timestamp
            )
            
        except asyncio.TimeoutError:
            raise RuntimeError(f"Benchmark timed out after {BENCHMARK_DURATION + 5} seconds")
        except Exception as e:
            raise RuntimeError(f"Benchmark execution failed: {str(e)}")
    
    def _parse_bogo_ops(self, output: str) -> Optional[float]:
        """Parse bogo ops/s from stress-ng output.
        
        Example output:
        stress-ng: info:  [12345] matrix: 1234567 bogo ops in 10.00s (123456.70 bogo ops/s)
        
        Args:
            output: stress-ng stdout/stderr output
            
        Returns:
            Bogo ops per second, or None if not found
        """
        # Pattern to match: "123456.70 bogo ops/s"
        pattern = r'([\d.]+)\s+bogo\s+ops/s'
        match = re.search(pattern, output, re.IGNORECASE)
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None
    
    def compare_results(
        self,
        baseline: BenchmarkResult,
        current: BenchmarkResult
    ) -> Dict[str, Any]:
        """Compare two benchmark results.
        
        Args:
            baseline: Earlier benchmark result
            current: More recent benchmark result
            
        Returns:
            Dictionary with:
                - score_diff: Absolute difference in scores
                - percent_change: Percentage change from baseline
                - improvement: True if current is better than baseline
                
        Requirements: 7.3
        """
        score_diff = current.score - baseline.score
        percent_change = (score_diff / baseline.score) * 100
        improvement = score_diff > 0
        
        return {
            "score_diff": score_diff,
            "percent_change": percent_change,
            "improvement": improvement
        }
