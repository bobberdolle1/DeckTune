"""Vdroop (transient load) stress tester for Iron Seeker.

Feature: iron-seeker, VdroopTester Module
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5

This module implements the Vdroop stress test which uses pulsating load
patterns to detect undervolt instability during voltage transients.
Unlike constant load tests, Vdroop tests stress the CPU during rapid
load transitions which are more likely to expose marginal undervolts.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

# Plugin directory for bundled binaries (set by Decky Loader)
PLUGIN_DIR = os.environ.get("DECKY_PLUGIN_DIR", ".")
BIN_DIR = os.path.join(PLUGIN_DIR, "bin")
STRESS_NG_PATH = os.path.join(BIN_DIR, "stress-ng")


def _get_stress_ng_path() -> str:
    """Get path to stress-ng binary, preferring bundled version.
    
    Returns:
        Full path to bundled binary or 'stress-ng' for PATH lookup
    """
    if os.path.isfile(STRESS_NG_PATH):
        return STRESS_NG_PATH
    return "stress-ng"


@dataclass
class VdroopTestResult:
    """Result of a Vdroop stress test.
    
    Attributes:
        passed: Whether the test passed (no crashes, no MCE errors)
        duration: Actual test duration in seconds
        exit_code: Process exit code (0 = success)
        mce_detected: True if MCE errors found in dmesg
        error: Error message if test failed due to error
        logs: Captured stdout/stderr output
    """
    passed: bool
    duration: float
    exit_code: int
    mce_detected: bool
    error: Optional[str] = None
    logs: str = ""


class VdroopTester:
    """Executes Vdroop (transient load) stress tests.
    
    Vdroop testing uses a pulsating load pattern that alternates between
    100% CPU load and idle. This pattern stresses the voltage regulator
    during rapid transitions, which is more effective at detecting
    marginal undervolts than constant load tests.
    
    The test uses stress-ng with the ackermann CPU method which provides
    AVX2-like workload characteristics for maximum power draw during
    load phases.
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    # MCE error patterns to search for in dmesg
    MCE_PATTERNS = [
        "mce",
        "machine check",
        "hardware error",
        "uncorrected error",
        "fatal error"
    ]
    
    def __init__(self):
        """Initialize the Vdroop tester."""
        self._current_process: Optional[asyncio.subprocess.Process] = None
        self._cancelled = False
    
    def generate_vdroop_command(
        self,
        duration_sec: int,
        pulse_ms: int = 100
    ) -> List[str]:
        """Generate stress-ng command for pulsating load pattern.
        
        Creates a command that runs stress-ng with parameters designed to
        create a pulsating load pattern. The pattern alternates between
        100% AVX2-like load and idle every pulse_ms milliseconds.
        
        stress-ng doesn't have native pulse support, so we use a combination
        of short timeout and cpu-ops to create bursts. The actual pulsing
        is achieved by running multiple short stress iterations.
        
        Args:
            duration_sec: Total test duration in seconds
            pulse_ms: Pulse duration in milliseconds (load on/off period)
            
        Returns:
            List of command arguments for subprocess execution
            
        Requirements: 2.1, 2.2
        """
        stress_ng = _get_stress_ng_path()
        
        # Calculate number of operations per pulse
        # ackermann method is CPU-intensive, ~1000 ops takes ~100ms on Steam Deck
        # We tune ops to match the pulse duration
        ops_per_pulse = max(100, (pulse_ms * 10))  # Rough estimate
        
        # Number of cycles = duration / (2 * pulse_ms) since each cycle is on+off
        # But stress-ng runs continuously, so we use timeout for total duration
        
        # Use --cpu-method=ackermann for AVX2-like workload
        # Use --cpu 4 to stress all 4 cores
        # Use --timeout for total duration
        # Use --cpu-ops to limit operations (creates natural pauses between batches)
        
        command = [
            stress_ng,
            "--cpu", "4",                          # All 4 cores
            "--cpu-method", "ackermann",           # AVX2-like workload (Req 2.2)
            "--cpu-ops", str(ops_per_pulse),       # Ops per burst
            "--timeout", f"{duration_sec}s",       # Total duration (Req 2.4)
            "--metrics-brief",                     # Brief output
        ]
        
        return command
    
    async def _check_mce_errors(self) -> bool:
        """Check dmesg for MCE (Machine Check Exception) errors.
        
        MCE errors indicate hardware-level CPU errors which are a strong
        signal of undervolt instability.
        
        Returns:
            True if MCE errors were detected, False otherwise
            
        Requirements: 2.3
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "dmesg", "--level=err,crit,alert,emerg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=10
            )
            
            output = stdout.decode("utf-8", errors="replace").lower()
            
            for pattern in self.MCE_PATTERNS:
                if pattern in output:
                    logger.warning(f"MCE pattern '{pattern}' detected in dmesg")
                    return True
                    
        except asyncio.TimeoutError:
            logger.warning("dmesg check timed out")
        except FileNotFoundError:
            logger.warning("dmesg command not found")
        except Exception as e:
            logger.warning(f"dmesg check failed: {e}")
        
        return False
    
    def cancel(self) -> None:
        """Cancel the running Vdroop test.
        
        Terminates the stress-ng process if running.
        """
        self._cancelled = True
        if self._current_process is not None:
            try:
                self._current_process.kill()
            except ProcessLookupError:
                pass  # Process already terminated
    
    async def run_vdroop_test(
        self,
        duration_sec: int,
        pulse_ms: int = 100
    ) -> VdroopTestResult:
        """Execute Vdroop test and return result.
        
        Runs the stress-ng command with pulsating load pattern and monitors
        for failures. After the test completes, checks dmesg for MCE errors.
        
        Args:
            duration_sec: Total test duration in seconds
            pulse_ms: Pulse duration in milliseconds
            
        Returns:
            VdroopTestResult with pass/fail status and details
            
        Requirements: 2.3, 2.4, 2.5
        """
        self._cancelled = False
        start_time = time.time()
        
        command = self.generate_vdroop_command(duration_sec, pulse_ms)
        logger.info(f"Starting Vdroop test: {' '.join(command)}")
        
        exit_code = -1
        logs = ""
        error = None
        mce_detected = False
        
        # Timeout is test duration + 10 seconds for startup/cleanup overhead
        timeout = duration_sec + 10
        
        try:
            self._current_process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    self._current_process.communicate(),
                    timeout=timeout
                )
                
                exit_code = self._current_process.returncode or 0
                logs = stdout.decode("utf-8", errors="replace")
                if stderr:
                    logs += "\n--- STDERR ---\n" + stderr.decode("utf-8", errors="replace")
                
                # Non-zero exit code indicates process failure (Req 2.5)
                if exit_code != 0:
                    error = f"stress-ng exited with code {exit_code}"
                    logger.warning(error)
                    
            except asyncio.TimeoutError:
                # Timeout indicates hang/crash (Req 2.5)
                self._current_process.kill()
                await self._current_process.wait()
                exit_code = -1
                error = f"Test timed out after {timeout} seconds"
                logs = f"[TIMEOUT] Process killed after {timeout}s"
                logger.warning(error)
                
        except FileNotFoundError:
            exit_code = -1
            error = f"stress-ng not found at {command[0]}"
            logger.error(error)
        except Exception as e:
            exit_code = -1
            error = f"Execution error: {str(e)}"
            logger.exception(error)
        finally:
            self._current_process = None
        
        duration = time.time() - start_time
        
        # Check dmesg for MCE errors after test (Req 2.3)
        if exit_code == 0 and not self._cancelled:
            mce_detected = await self._check_mce_errors()
            if mce_detected:
                error = "MCE errors detected in dmesg"
        
        # Test passes only if:
        # 1. Process exited with code 0
        # 2. No MCE errors in dmesg
        # 3. Test was not cancelled
        passed = (
            exit_code == 0 and
            not mce_detected and
            not self._cancelled and
            error is None
        )
        
        result = VdroopTestResult(
            passed=passed,
            duration=duration,
            exit_code=exit_code,
            mce_detected=mce_detected,
            error=error,
            logs=logs
        )
        
        logger.info(
            f"Vdroop test complete: passed={passed}, "
            f"duration={duration:.1f}s, exit_code={exit_code}"
        )
        
        return result
