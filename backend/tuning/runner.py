"""Test runner for stress tests.

Feature: decktune, Test Runner Module
Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6

Note: On SteamOS (read-only filesystem), stress-ng and memtester must be
bundled as static binaries in the bin/ directory since pacman is unavailable.
"""

import asyncio
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any

logger = logging.getLogger(__name__)

# Plugin directory for bundled binaries (set by Decky Loader)
PLUGIN_DIR = os.environ.get("DECKY_PLUGIN_DIR", ".")
BIN_DIR = os.path.join(PLUGIN_DIR, "bin")

# Bundled binary paths (static builds for SteamOS compatibility)
STRESS_NG_PATH = os.path.join(BIN_DIR, "stress-ng")
MEMTESTER_PATH = os.path.join(BIN_DIR, "memtester")


def _get_binary_path(binary_name: str) -> str:
    """Get path to binary, preferring bundled version.
    
    Falls back to system PATH if bundled binary not found.
    This allows development on systems with stress-ng installed.
    
    Args:
        binary_name: Name of the binary (stress-ng, memtester)
        
    Returns:
        Full path to binary or just the name for PATH lookup
    """
    bundled_paths = {
        "stress-ng": STRESS_NG_PATH,
        "memtester": MEMTESTER_PATH,
    }
    
    bundled_path = bundled_paths.get(binary_name)
    if bundled_path and os.path.isfile(bundled_path):
        return bundled_path
    
    # Fallback to system PATH
    return binary_name


@dataclass
class TestCase:
    """Definition of a stress test case.
    
    Attributes:
        name: Human-readable test name
        command: Command and arguments to execute (first element is binary name)
        timeout: Maximum execution time in seconds
        parse_fn: Function to parse output and determine pass/fail
    """
    name: str
    command: List[str]
    timeout: int
    parse_fn: Callable[[str], bool]


@dataclass
class TestResult:
    """Result of a test execution.
    
    Attributes:
        passed: Whether the test passed
        duration: Execution time in seconds
        logs: Captured stdout/stderr output
        error: Error message if test failed due to error (not test failure)
    """
    passed: bool
    duration: float
    logs: str
    error: Optional[str] = None


def _parse_stress_ng_output(output: str) -> bool:
    """Parse stress-ng output for success."""
    return "successful" in output.lower()


def _parse_memtester_output(output: str) -> bool:
    """Parse memtester output for success."""
    lower_output = output.lower()
    return "ok" in lower_output and "failure" not in lower_output


class TestRunner:
    """Execute stress tests and monitor results.
    
    Provides stress testing capabilities for validating undervolt stability.
    Supports CPU, RAM, and combo stress tests with configurable timeouts.
    """
    
    # Test definitions per Requirements 3.1, 3.2, 3.3
    TESTS: Dict[str, TestCase] = {
        "cpu_quick": TestCase(
            name="CPU Quick",
            command=["stress-ng", "--cpu", "4", "--timeout", "30s"],
            timeout=35,
            parse_fn=_parse_stress_ng_output
        ),
        "cpu_long": TestCase(
            name="CPU Long",
            command=["stress-ng", "--cpu", "4", "--timeout", "5m"],
            timeout=310,
            parse_fn=_parse_stress_ng_output
        ),
        "cpu_loop": TestCase(
            name="CPU Loop (Infinite)",
            command=["stress-ng", "--cpu", "4", "--timeout", "0"],  # 0 = infinite
            timeout=0,  # No timeout - runs until cancelled
            parse_fn=_parse_stress_ng_output
        ),
        "ram_quick": TestCase(
            name="RAM Quick",
            command=["memtester", "512M", "1"],
            timeout=120,
            parse_fn=_parse_memtester_output
        ),
        "ram_thorough": TestCase(
            name="RAM Thorough (anta777-style)",
            command=["memtester", "2G", "3"],
            timeout=900,
            parse_fn=_parse_memtester_output
        ),
        "combo": TestCase(
            name="Combo Stress",
            command=["stress-ng", "--cpu", "4", "--vm", "2", "--timeout", "5m"],
            timeout=310,
            parse_fn=_parse_stress_ng_output
        )
    }

    # Sysfs paths for system metrics
    TEMP_PATHS = [
        "/sys/class/hwmon/hwmon0/temp1_input",
        "/sys/class/thermal/thermal_zone0/temp",
    ]
    
    FREQ_PATHS = [
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq",
    ]
    
    def __init__(self):
        """Initialize the test runner."""
        self._current_process: Optional[asyncio.subprocess.Process] = None
    
    def check_binaries(self) -> Dict[str, bool]:
        """Check availability of required binaries.
        
        Returns:
            Dictionary mapping binary name to availability status.
            Useful for diagnostics and UI warnings.
        """
        binaries = {
            "stress-ng": _get_binary_path("stress-ng"),
            "memtester": _get_binary_path("memtester"),
        }
        
        result = {}
        for name, path in binaries.items():
            if os.path.isabs(path):
                # Bundled binary - check if file exists and is executable
                result[name] = os.path.isfile(path) and os.access(path, os.X_OK)
            else:
                # System binary - check if in PATH
                import shutil
                result[name] = shutil.which(path) is not None
        
        return result
    
    def get_missing_binaries(self) -> List[str]:
        """Get list of missing required binaries.
        
        Returns:
            List of binary names that are not available
        """
        status = self.check_binaries()
        return [name for name, available in status.items() if not available]
    
    async def run_test(self, test_name: str) -> TestResult:
        """Execute a test case and return results.
        
        Args:
            test_name: Key from TESTS dictionary
            
        Returns:
            TestResult with pass/fail status, duration, logs, and any error
            
        Requirements: 3.4, 3.5
        """
        if test_name not in self.TESTS:
            return TestResult(
                passed=False,
                duration=0.0,
                logs="",
                error=f"Unknown test: {test_name}"
            )
        
        test_case = self.TESTS[test_name]
        start_time = time.time()
        logs = ""
        error = None
        passed = False
        
        # Resolve binary path (bundled or system)
        command = test_case.command.copy()
        command[0] = _get_binary_path(command[0])
        
        try:
            # Execute subprocess with timeout
            self._current_process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    self._current_process.communicate(),
                    timeout=test_case.timeout
                )
                
                # Combine stdout and stderr for logs
                logs = stdout.decode("utf-8", errors="replace")
                if stderr:
                    logs += "\n--- STDERR ---\n" + stderr.decode("utf-8", errors="replace")
                
                # Check exit code and parse output
                if self._current_process.returncode == 0:
                    passed = test_case.parse_fn(logs)
                    if not passed:
                        error = "Test output indicates failure"
                else:
                    passed = False
                    error = f"Process exited with code {self._current_process.returncode}"
                    
            except asyncio.TimeoutError:
                # Kill the process on timeout
                self._current_process.kill()
                await self._current_process.wait()
                passed = False
                error = f"Test timed out after {test_case.timeout} seconds"
                logs = f"[TIMEOUT] Process killed after {test_case.timeout}s"
                
        except FileNotFoundError:
            passed = False
            error = f"Command not found: {test_case.command[0]}"
            logs = ""
        except Exception as e:
            passed = False
            error = f"Execution error: {str(e)}"
            logs = ""
        finally:
            self._current_process = None
        
        duration = time.time() - start_time
        
        return TestResult(
            passed=passed,
            duration=duration,
            logs=logs,
            error=error
        )
    
    async def check_dmesg_errors(self) -> List[str]:
        """Check dmesg for MCE/segfault errors.
        
        Returns:
            List of error lines found in dmesg
            
        Requirements: 3.6
        """
        errors = []
        error_patterns = ["mce", "segfault", "machine check", "hardware error"]
        
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
            
            output = stdout.decode("utf-8", errors="replace")
            
            for line in output.splitlines():
                lower_line = line.lower()
                if any(pattern in lower_line for pattern in error_patterns):
                    errors.append(line.strip())
                    
        except (asyncio.TimeoutError, FileNotFoundError, Exception):
            # If dmesg fails, return empty list
            pass
        
        return errors
    
    async def monitor_dmesg_realtime(self, duration: int) -> List[str]:
        """Monitor dmesg for hardware errors in real-time during test.
        
        Captures the dmesg timestamp before test, then checks for new errors
        after the test completes.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            List of new error lines detected during the test period
        """
        errors = []
        error_patterns = ["mce", "machine check", "hardware error", "whea", "corrected error"]
        
        try:
            # Get current dmesg line count as baseline
            process = await asyncio.create_subprocess_exec(
                "dmesg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=5)
            baseline_lines = len(stdout.decode("utf-8", errors="replace").splitlines())
            
            # Wait for test duration
            await asyncio.sleep(duration)
            
            # Check for new errors
            process = await asyncio.create_subprocess_exec(
                "dmesg", "--level=err,crit,alert,emerg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10)
            output = stdout.decode("utf-8", errors="replace")
            lines = output.splitlines()
            
            # Check only new lines
            new_lines = lines[baseline_lines:] if len(lines) > baseline_lines else []
            
            for line in new_lines:
                lower_line = line.lower()
                if any(pattern in lower_line for pattern in error_patterns):
                    errors.append(line.strip())
                    
        except (asyncio.TimeoutError, FileNotFoundError, Exception):
            pass
        
        return errors
    
    def read_voltage_sensors(self) -> Dict[str, Optional[float]]:
        """Read actual voltage values from hwmon sensors.
        
        Attempts to read CPU core voltages from sysfs hwmon interface.
        Used to verify that voltage offsets are actually being applied.
        
        Returns:
            Dictionary with voltage readings in mV, or None if unavailable
        """
        voltages = {}
        
        # Common hwmon paths for CPU voltage on Steam Deck
        voltage_paths = [
            "/sys/class/hwmon/hwmon0/in0_input",  # Vcore
            "/sys/class/hwmon/hwmon1/in0_input",
            "/sys/class/hwmon/hwmon2/in0_input",
        ]
        
        for i, path in enumerate(voltage_paths):
            try:
                p = Path(path)
                if p.exists():
                    raw_value = p.read_text().strip()
                    # Voltage is usually in millivolts
                    voltage_mv = float(raw_value)
                    voltages[f"sensor_{i}"] = voltage_mv
                    break  # Use first available sensor
            except (ValueError, IOError, PermissionError):
                continue
        
        return voltages
    
    async def run_per_core_test(self, core_id: int, duration: int) -> TestResult:
        """Run stress test pinned to a specific CPU core.
        
        Uses taskset to pin the stress test to a single core for
        per-core stability validation.
        
        Args:
            core_id: CPU core ID (0-3 for Steam Deck)
            duration: Test duration in seconds
            
        Returns:
            TestResult with pass/fail status
        """
        start_time = time.time()
        logs = ""
        error = None
        passed = False
        
        # Build command with taskset for CPU affinity
        stress_ng_path = _get_binary_path("stress-ng")
        
        # CRITICAL FIX: Use stress-ng built-in --taskset instead of external taskset
        command = [
            stress_ng_path,
            "--cpu", "1",  # Single CPU worker
            "--taskset", str(core_id),  # Pin to specific core (stress-ng built-in)
            "--timeout", f"{duration}s",
            "--metrics-brief"  # Brief metrics output
        ]
        
        logger.info(f"[RUNNER] Per-core test: core={core_id}, duration={duration}s")
        
        try:
            self._current_process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    self._current_process.communicate(),
                    timeout=duration + 10
                )
                
                logs = stdout.decode("utf-8", errors="replace")
                if stderr:
                    logs += "\n--- STDERR ---\n" + stderr.decode("utf-8", errors="replace")
                
                logger.info(f"[RUNNER] Core {core_id} completed: returncode={self._current_process.returncode}")
                
                if self._current_process.returncode == 0:
                    passed = _parse_stress_ng_output(logs)
                    if not passed:
                        error = "Test output indicates failure"
                else:
                    passed = False
                    error = f"Process exited with code {self._current_process.returncode}"
                    
            except asyncio.TimeoutError:
                self._current_process.kill()
                await self._current_process.wait()
                passed = False
                error = f"Test timed out after {duration + 10} seconds"
                logs = f"[TIMEOUT] Process killed"
                
        except FileNotFoundError as e:
            passed = False
            error = f"stress-ng not found: {e}"
            logs = ""
            logger.error(f"[RUNNER] FileNotFoundError: {e}")
        except Exception as e:
            passed = False
            error = f"Execution error: {str(e)}"
            logs = ""
            logger.error(f"[RUNNER] Exception: {e}", exc_info=True)
        finally:
            self._current_process = None
        
        duration_actual = time.time() - start_time
        
        return TestResult(
            passed=passed,
            duration=duration_actual,
            logs=logs,
            error=error
        )
    
    async def run_benchmark_with_progress(
        self,
        duration: int = 10,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Run performance benchmark with progress updates.
        
        Executes a CPU-intensive benchmark and streams progress updates.
        
        Args:
            duration: Benchmark duration in seconds
            progress_callback: Optional callback for progress updates (0-100)
            
        Returns:
            Dictionary with score, max_temp, max_freq, duration
        """
        start_time = time.time()
        max_temp = 0.0
        max_freq = 0.0
        operations = 0
        
        stress_ng_path = _get_binary_path("stress-ng")
        
        try:
            # Start stress-ng benchmark
            process = await asyncio.create_subprocess_exec(
                stress_ng_path,
                "--cpu", "4",
                "--cpu-method", "ackermann",  # CPU-intensive method
                "--timeout", f"{duration}s",
                "--metrics-brief",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress and metrics
            for i in range(duration):
                await asyncio.sleep(1)
                
                # Update progress
                progress = int((i + 1) / duration * 100)
                if progress_callback:
                    progress_callback(progress)
                
                # Sample metrics
                metrics = self.get_system_metrics()
                if metrics.get("temperature"):
                    max_temp = max(max_temp, metrics["temperature"])
                if metrics.get("frequency"):
                    max_freq = max(max_freq, metrics["frequency"])
            
            # Wait for completion
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5
            )
            
            # Parse operations from output
            output = stdout.decode("utf-8", errors="replace")
            for line in output.splitlines():
                if "bogo ops" in line.lower():
                    try:
                        # Extract operations count
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "bogo" in part.lower() and i + 1 < len(parts):
                                operations = int(float(parts[i + 1]))
                                break
                    except (ValueError, IndexError):
                        pass
            
            # Calculate score (ops/sec)
            score = int(operations / duration) if duration > 0 else 0
            
            return {
                "score": score,
                "max_temp": round(max_temp, 1),
                "max_freq": round(max_freq, 1),
                "duration": duration,
                "operations": operations
            }
            
        except Exception as e:
            return {
                "score": 0,
                "max_temp": 0,
                "max_freq": 0,
                "duration": 0,
                "error": str(e)
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Read current temps and frequencies from sysfs.
        
        Returns:
            Dictionary with temperature (celsius) and frequency (MHz) if available
            
        Requirements: 3.6
        """
        metrics: Dict[str, Any] = {
            "temperature": None,
            "frequency": None
        }
        
        # Read temperature
        for temp_path in self.TEMP_PATHS:
            try:
                path = Path(temp_path)
                if path.exists():
                    raw_value = path.read_text().strip()
                    # Temperature is usually in millidegrees
                    temp_celsius = int(raw_value) / 1000.0
                    metrics["temperature"] = temp_celsius
                    break
            except (ValueError, IOError, PermissionError):
                continue
        
        # Read CPU frequency
        for freq_path in self.FREQ_PATHS:
            try:
                path = Path(freq_path)
                if path.exists():
                    raw_value = path.read_text().strip()
                    # Frequency is usually in kHz
                    freq_mhz = int(raw_value) / 1000.0
                    metrics["frequency"] = freq_mhz
                    break
            except (ValueError, IOError, PermissionError):
                continue
        
        return metrics
