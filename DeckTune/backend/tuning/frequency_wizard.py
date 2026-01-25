"""Frequency-based voltage wizard for automated curve generation.

This module implements the frequency wizard that automatically tests voltage
stability across a range of CPU frequencies to generate optimal frequency-voltage
curves.

Feature: frequency-based-wizard
Validates: Requirements 1.1, 1.2, 1.4, 3.1-3.7, 4.1-4.4, 6.2, 6.4, 6.5, 9.1-9.5
"""

import asyncio
import logging
import time
import random
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

from .frequency_curve import FrequencyPoint, FrequencyCurve
from ..platform.cpufreq import CPUFreqController, CPUFreqError, PermissionError as CPUFreqPermissionError
from .runner import TestRunner

logger = logging.getLogger(__name__)

# Safety constants
TEMPERATURE_ABORT_THRESHOLD = 85.0  # Celsius
TEST_TIMEOUT_MARGIN = 30  # seconds added to test duration
CONSECUTIVE_FAILURE_THRESHOLD = 3  # Skip frequency after this many failures
VERIFICATION_TEST_COUNT = 5  # Number of random frequencies to verify


class WizardError(Exception):
    """Base exception for wizard operations."""
    pass


class WizardCancelled(WizardError):
    """Raised when wizard is cancelled by user."""
    pass


class ConfigurationError(WizardError):
    """Raised when wizard configuration is invalid."""
    pass


class ConsecutiveFailureError(WizardError):
    """Raised when consecutive test failures exceed threshold."""
    pass


@dataclass
class FrequencyWizardConfig:
    """Configuration for frequency wizard.
    
    Feature: frequency-based-wizard, Property 1: Configuration validation completeness
    Validates: Requirements 3.1-3.7
    """
    freq_start: int = 400  # MHz
    freq_end: int = 3500  # MHz
    freq_step: int = 100  # MHz
    test_duration: int = 30  # seconds per test
    voltage_start: int = -30  # mV starting point
    voltage_step: int = 2  # mV step for binary search
    safety_margin: int = 5  # mV added to stable voltage
    parallel_cores: bool = False  # Test cores in parallel
    adaptive_step: bool = True  # Increase step in stable regions
    save_interval: int = 1  # Save intermediate results every N points
    
    @classmethod
    def quick_preset(cls) -> 'FrequencyWizardConfig':
        """Create a quick preset configuration.
        
        Quick preset completes in ~10-15 minutes with larger steps and shorter tests.
        
        Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
        Validates: Requirements 12.5
        """
        return cls(
            freq_start=400,
            freq_end=3500,
            freq_step=200,  # Larger step for speed
            test_duration=15,  # Shorter tests
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5,
            adaptive_step=True,  # Enable adaptive stepping
            save_interval=1
        )
    
    @classmethod
    def balanced_preset(cls) -> 'FrequencyWizardConfig':
        """Create a balanced preset configuration.
        
        Balanced preset provides good coverage with reasonable time (~20-30 minutes).
        """
        return cls(
            freq_start=400,
            freq_end=3500,
            freq_step=100,
            test_duration=30,
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5,
            adaptive_step=True,
            save_interval=1
        )
    
    @classmethod
    def thorough_preset(cls) -> 'FrequencyWizardConfig':
        """Create a thorough preset configuration.
        
        Thorough preset provides maximum coverage with longer tests (~45-60 minutes).
        """
        return cls(
            freq_start=400,
            freq_end=3500,
            freq_step=50,  # Smaller step for more coverage
            test_duration=60,  # Longer tests for stability
            voltage_start=-30,
            voltage_step=2,
            safety_margin=5,
            adaptive_step=False,  # No adaptive stepping for thorough testing
            save_interval=5  # Save less frequently
        )
    
    def validate(self) -> None:
        """Validate configuration parameters.
        
        Raises:
            ConfigurationError: If any parameter is out of valid range
            
        Feature: frequency-based-wizard, Property 1: Configuration validation completeness
        Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
        """
        errors = []
        
        # Validate frequency range start
        if not (400 <= self.freq_start <= 3500):
            errors.append(
                f"freq_start must be between 400-3500 MHz, got {self.freq_start}"
            )
        
        # Validate frequency range end
        if self.freq_end <= self.freq_start:
            errors.append(
                f"freq_end ({self.freq_end}) must be greater than freq_start ({self.freq_start})"
            )
        
        # Validate frequency step
        if not (50 <= self.freq_step <= 500):
            errors.append(
                f"freq_step must be between 50-500 MHz, got {self.freq_step}"
            )
        
        # Validate test duration
        if not (10 <= self.test_duration <= 120):
            errors.append(
                f"test_duration must be between 10-120 seconds, got {self.test_duration}"
            )
        
        # Validate voltage start
        if not (-100 <= self.voltage_start <= 0):
            errors.append(
                f"voltage_start must be between -100 and 0 mV, got {self.voltage_start}"
            )
        
        # Validate voltage step
        if not (1 <= self.voltage_step <= 10):
            errors.append(
                f"voltage_step must be between 1-10 mV, got {self.voltage_step}"
            )
        
        # Validate safety margin
        if not (0 <= self.safety_margin <= 20):
            errors.append(
                f"safety_margin must be between 0-20 mV, got {self.safety_margin}"
            )
        
        if errors:
            raise ConfigurationError(
                "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrequencyWizardConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WizardProgress:
    """Progress tracking for wizard execution.
    
    Feature: frequency-based-wizard, Property 11: Progress calculation accuracy
    Validates: Requirements 4.1-4.4
    """
    running: bool = False
    current_frequency: int = 0  # MHz
    current_voltage: int = 0  # mV
    completed_points: int = 0
    total_points: int = 0
    estimated_remaining: int = 0  # seconds
    start_time: float = 0.0
    
    def calculate_progress_percent(self) -> float:
        """Calculate progress percentage.
        
        Feature: frequency-based-wizard, Property 11: Progress calculation accuracy
        Validates: Requirements 4.3
        """
        if self.total_points == 0:
            return 0.0
        return (self.completed_points / self.total_points) * 100.0
    
    def update_estimated_remaining(self) -> None:
        """Update estimated time remaining based on elapsed time and progress."""
        if self.completed_points == 0 or not self.running:
            self.estimated_remaining = 0
            return
        
        elapsed = time.time() - self.start_time
        avg_time_per_point = elapsed / self.completed_points
        remaining_points = self.total_points - self.completed_points
        self.estimated_remaining = int(avg_time_per_point * remaining_points)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for RPC response."""
        return {
            'running': self.running,
            'current_frequency': self.current_frequency,
            'current_voltage': self.current_voltage,
            'progress_percent': self.calculate_progress_percent(),
            'estimated_remaining': self.estimated_remaining,
            'completed_points': self.completed_points,
            'total_points': self.total_points
        }


class FrequencyWizard:
    """Automated frequency curve generation.
    
    Executes a full frequency sweep, testing voltage stability at each frequency
    point using binary search to find the optimal voltage offset.
    
    Feature: frequency-based-wizard
    Validates: Requirements 1.1, 1.2, 1.4, 3.1-3.7, 4.1-4.4, 6.2, 6.4, 6.5
    """
    
    def __init__(
        self,
        config: FrequencyWizardConfig,
        cpufreq_controller: CPUFreqController,
        test_runner: TestRunner,
        progress_callback: Optional[Callable[[WizardProgress], None]] = None,
        save_path: Optional[Path] = None
    ):
        """Initialize frequency wizard.
        
        Args:
            config: Wizard configuration
            cpufreq_controller: CPU frequency controller instance
            test_runner: Test runner instance
            progress_callback: Optional callback for progress updates
            save_path: Optional path for intermediate result persistence
        """
        self.config = config
        self.cpufreq = cpufreq_controller
        self.test_runner = test_runner
        self.progress_callback = progress_callback
        self.save_path = save_path
        
        self.progress = WizardProgress()
        self.cancelled = False
        self._original_governors: Dict[int, str] = {}
        self._original_voltages: List[int] = [0, 0, 0, 0]
        
        # Adaptive stepping state
        self._consecutive_stable_count = 0
        self._last_voltages: List[int] = []
        self._voltage_similarity_threshold = 2  # mV
    
    def cancel(self) -> None:
        """Cancel wizard execution.
        
        Sets cancellation flag. The wizard will stop after the current test
        completes and restore original settings.
        
        Feature: frequency-based-wizard, Property 8: Wizard cancellation state restoration
        Validates: Requirements 6.4
        """
        logger.info("Wizard cancellation requested")
        self.cancelled = True
    
    async def run(self, core_id: int) -> FrequencyCurve:
        """Execute full frequency sweep for a CPU core.
        
        Args:
            core_id: CPU core ID to test
            
        Returns:
            Complete frequency curve with all tested points
            
        Raises:
            WizardCancelled: If user cancels the wizard
            ConfigurationError: If configuration is invalid
            CPUFreqError: If frequency control fails
            WizardError: For other wizard errors
            
        Feature: frequency-based-wizard, Property 5: Wizard frequency coverage completeness
        Validates: Requirements 1.1, 1.4
        """
        # Validate configuration
        self.config.validate()
        
        logger.info(
            f"Starting frequency wizard for core {core_id}: "
            f"freq_range={self.config.freq_start}-{self.config.freq_end} MHz, "
            f"step={self.config.freq_step} MHz, "
            f"test_duration={self.config.test_duration}s"
        )
        
        # Calculate frequency points to test
        frequencies = self._calculate_frequency_points()
        
        # Try to load intermediate results
        loaded_points = self._load_intermediate_results(core_id)
        if loaded_points:
            logger.info(f"Resuming from {len(loaded_points)} previously completed points")
            points = loaded_points
            
            # Skip already completed frequencies
            completed_freqs = {p.frequency_mhz for p in points}
            frequencies = [f for f in frequencies if f not in completed_freqs]
            
            # Update progress
            self.progress.completed_points = len(points)
        else:
            points = []
        
        # Initialize progress tracking
        self.progress = WizardProgress(
            running=True,
            total_points=len(frequencies) + len(points),
            completed_points=len(points),
            start_time=time.time()
        )
        self._notify_progress()
        
        # Store original state for restoration
        try:
            self._original_governors[core_id] = self.cpufreq.get_current_governor(core_id)
            logger.info(f"Stored original governor: {self._original_governors[core_id]}")
        except CPUFreqError as e:
            logger.warning(f"Failed to get original governor: {e}")
            self._original_governors[core_id] = "schedutil"  # Default fallback
        
        # Test each frequency point
        try:
            freq_index = 0
            while freq_index < len(frequencies):
                freq_mhz = frequencies[freq_index]
                
                # Check for cancellation
                if self.cancelled:
                    logger.info("Wizard cancelled by user")
                    raise WizardCancelled("Wizard cancelled by user")
                
                # Update progress
                self.progress.current_frequency = freq_mhz
                self._notify_progress()
                
                # Test this frequency point
                logger.info(f"Testing frequency point: {freq_mhz} MHz")
                point = await self._test_frequency_point(core_id, freq_mhz)
                points.append(point)
                
                # Update progress
                self.progress.completed_points += 1
                self.progress.update_estimated_remaining()
                self._notify_progress()
                
                logger.info(
                    f"Completed {self.progress.completed_points}/{self.progress.total_points} "
                    f"({self.progress.calculate_progress_percent():.1f}%)"
                )
                
                # Save intermediate results periodically
                if self.progress.completed_points % self.config.save_interval == 0:
                    self._save_intermediate_results(core_id, points)
                
                # Calculate next step (adaptive or fixed)
                if point.stable and self.config.adaptive_step:
                    adaptive_step = self._calculate_adaptive_step(point.voltage_mv)
                    
                    # Skip ahead if adaptive step is larger
                    if adaptive_step > self.config.freq_step:
                        # Find next frequency to test
                        next_freq = freq_mhz + adaptive_step
                        
                        # Skip frequencies in between
                        while freq_index + 1 < len(frequencies) and frequencies[freq_index + 1] < next_freq:
                            freq_index += 1
                            logger.debug(f"Skipping frequency {frequencies[freq_index]} MHz (adaptive step)")
                
                freq_index += 1
        
        finally:
            # Always restore original settings
            await self._restore_original_state(core_id)
            self.progress.running = False
            self._notify_progress()
            
            # Save final results
            if points:
                self._save_intermediate_results(core_id, points)
        
        # Create frequency curve
        curve = FrequencyCurve(
            core_id=core_id,
            points=points,
            created_at=time.time(),
            wizard_config=self.config.to_dict()
        )
        
        # Validate curve
        curve.validate()
        
        logger.info(
            f"Wizard completed successfully: {len(points)} points generated, "
            f"{sum(1 for p in points if p.stable)} stable"
        )
        
        # Run verification tests
        logger.info("Running verification tests...")
        verification_passed = await self._verify_curve(curve)
        
        if not verification_passed:
            logger.warning("Verification tests failed - curve may be unstable")
        else:
            logger.info("Verification tests passed")
        
        return curve
    
    def _calculate_frequency_points(self) -> List[int]:
        """Calculate list of frequency points to test.
        
        Returns:
            List of frequencies in MHz, sorted ascending
            
        Feature: frequency-based-wizard, Property 5: Wizard frequency coverage completeness
        Validates: Requirements 1.1, 1.4
        """
        frequencies = []
        freq = self.config.freq_start
        
        while freq <= self.config.freq_end:
            frequencies.append(freq)
            freq += self.config.freq_step
        
        return frequencies
    
    def _calculate_adaptive_step(self, current_voltage: int) -> int:
        """Calculate adaptive step size based on voltage stability.
        
        If we detect a stable voltage region (3+ consecutive similar voltages),
        increase the step size to skip redundant tests.
        
        Args:
            current_voltage: Current voltage offset in mV
            
        Returns:
            Step size in MHz (base step or increased step)
            
        Feature: frequency-based-wizard, Property 22: Adaptive step optimization
        Validates: Requirements 12.1
        """
        if not self.config.adaptive_step:
            return self.config.freq_step
        
        # Track voltage history
        self._last_voltages.append(current_voltage)
        
        # Keep only recent voltages (last 5)
        if len(self._last_voltages) > 5:
            self._last_voltages.pop(0)
        
        # Check if we have enough history
        if len(self._last_voltages) < 3:
            return self.config.freq_step
        
        # Check if recent voltages are similar (stable region)
        recent_voltages = self._last_voltages[-3:]
        max_voltage = max(recent_voltages)
        min_voltage = min(recent_voltages)
        voltage_range = max_voltage - min_voltage
        
        if voltage_range <= self._voltage_similarity_threshold:
            # Stable region detected - increase step
            self._consecutive_stable_count += 1
            
            # Increase step size (max 3x base step)
            step_multiplier = min(2, 3)  # Start with 2x, max 3x
            adaptive_step = self.config.freq_step * step_multiplier
            
            logger.info(
                f"Stable region detected (range={voltage_range}mV), "
                f"increasing step to {adaptive_step}MHz"
            )
            
            return adaptive_step
        else:
            # Not stable - reset counter and use base step
            self._consecutive_stable_count = 0
            return self.config.freq_step
    
    def _save_intermediate_results(self, core_id: int, points: List[FrequencyPoint]) -> None:
        """Save intermediate results to allow resumption after interruption.
        
        Args:
            core_id: CPU core ID
            points: List of completed frequency points
            
        Feature: frequency-based-wizard, Property 24: Intermediate result persistence
        Validates: Requirements 12.4
        """
        if not self.save_path:
            return
        
        try:
            # Create partial curve
            partial_curve = FrequencyCurve(
                core_id=core_id,
                points=points,
                created_at=time.time(),
                wizard_config=self.config.to_dict()
            )
            
            # Save to file
            import json
            with open(self.save_path, 'w') as f:
                json.dump(partial_curve.to_dict(), f, indent=2)
            
            logger.debug(f"Saved intermediate results: {len(points)} points")
        
        except Exception as e:
            logger.warning(f"Failed to save intermediate results: {e}")
    
    def _load_intermediate_results(self, core_id: int) -> Optional[List[FrequencyPoint]]:
        """Load intermediate results from previous interrupted run.
        
        Args:
            core_id: CPU core ID
            
        Returns:
            List of previously completed points, or None if no save exists
            
        Feature: frequency-based-wizard, Property 24: Intermediate result persistence
        Validates: Requirements 12.4
        """
        if not self.save_path or not self.save_path.exists():
            return None
        
        try:
            import json
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            curve = FrequencyCurve.from_dict(data)
            
            # Verify it's for the same core and config
            if curve.core_id != core_id:
                logger.warning(
                    f"Intermediate save is for different core "
                    f"(saved={curve.core_id}, current={core_id})"
                )
                return None
            
            logger.info(f"Loaded intermediate results: {len(curve.points)} points")
            return curve.points
        
        except Exception as e:
            logger.warning(f"Failed to load intermediate results: {e}")
            return None
    
    async def _test_frequency_point(
        self,
        core_id: int,
        freq_mhz: int
    ) -> FrequencyPoint:
        """Find optimal voltage for a single frequency point.
        
        Uses binary search to find the maximum stable voltage offset (most aggressive
        undervolt) for the given frequency. Implements consecutive failure tracking
        to skip unstable frequencies.
        
        Args:
            core_id: CPU core ID
            freq_mhz: Frequency to test in MHz
            
        Returns:
            FrequencyPoint with test results
            
        Feature: frequency-based-wizard, Property 6: Frequency point data completeness
        Feature: frequency-based-wizard, Property 16: Consecutive failure skip
        Validates: Requirements 1.3, 9.4
        """
        logger.info(f"Testing frequency point: {freq_mhz} MHz")
        
        # Track consecutive failures for this frequency
        consecutive_failures = 0
        
        # Binary search for optimal voltage
        try:
            stable_voltage = await self._binary_search_voltage(
                core_id,
                freq_mhz,
                self.config.voltage_start,
                self.config.voltage_step
            )
        except ConsecutiveFailureError as e:
            # Three consecutive failures - skip this frequency
            logger.warning(
                f"Skipping frequency {freq_mhz} MHz after {CONSECUTIVE_FAILURE_THRESHOLD} "
                f"consecutive failures"
            )
            
            # Create unstable frequency point
            point = FrequencyPoint(
                frequency_mhz=freq_mhz,
                voltage_mv=0,  # No undervolt for unstable frequency
                stable=False,
                test_duration=0,
                timestamp=time.time()
            )
            
            return point
        
        # Add safety margin
        final_voltage = stable_voltage + self.config.safety_margin
        
        # Clamp to valid range
        final_voltage = max(-100, min(0, final_voltage))
        
        logger.info(
            f"Frequency {freq_mhz} MHz: stable_voltage={stable_voltage}mV, "
            f"final_voltage={final_voltage}mV (with {self.config.safety_margin}mV margin)"
        )
        
        # Create frequency point
        point = FrequencyPoint(
            frequency_mhz=freq_mhz,
            voltage_mv=final_voltage,
            stable=True,  # We only record stable points
            test_duration=self.config.test_duration,
            timestamp=time.time()
        )
        
        return point
    
    async def _binary_search_voltage(
        self,
        core_id: int,
        freq_mhz: int,
        voltage_start: int,
        voltage_step: int
    ) -> int:
        """Binary search for stable voltage at frequency.
        
        Searches for the most aggressive (lowest) stable voltage offset.
        Tracks consecutive failures and raises exception if threshold exceeded.
        
        Args:
            core_id: CPU core ID
            freq_mhz: Frequency to test in MHz
            voltage_start: Starting voltage offset in mV
            voltage_step: Voltage step size in mV
            
        Returns:
            Most aggressive stable voltage offset in mV
            
        Raises:
            ConsecutiveFailureError: If consecutive failures exceed threshold
            
        Feature: frequency-based-wizard, Property 9: Test failure recovery with safety margin
        Feature: frequency-based-wizard, Property 16: Consecutive failure skip
        Validates: Requirements 6.2, 9.4
        """
        # Start with conservative voltage (0 mV = no undervolt)
        voltage_low = voltage_start  # Most aggressive (e.g., -30)
        voltage_high = 0  # Most conservative (no undervolt)
        
        last_stable_voltage = 0  # Default to no undervolt if all tests fail
        consecutive_failures = 0
        
        logger.info(
            f"Binary search: freq={freq_mhz}MHz, "
            f"voltage_range=[{voltage_low}, {voltage_high}]mV, step={voltage_step}mV"
        )
        
        # Binary search loop
        while voltage_high - voltage_low > voltage_step:
            # Check for cancellation
            if self.cancelled:
                logger.info("Binary search cancelled")
                return last_stable_voltage
            
            # Calculate midpoint
            voltage_mid = (voltage_low + voltage_high) // 2
            
            # Round to nearest step
            voltage_mid = (voltage_mid // voltage_step) * voltage_step
            
            # Update progress
            self.progress.current_voltage = voltage_mid
            self._notify_progress()
            
            logger.info(f"Testing voltage: {voltage_mid}mV at {freq_mhz}MHz")
            
            # Run stability test
            is_stable = await self._test_voltage_stability(
                core_id,
                freq_mhz,
                voltage_mid
            )
            
            if is_stable:
                # Voltage is stable, try more aggressive
                last_stable_voltage = voltage_mid
                voltage_high = voltage_mid
                consecutive_failures = 0  # Reset failure counter
                logger.info(f"Voltage {voltage_mid}mV is STABLE")
            else:
                # Voltage is unstable, try more conservative
                voltage_low = voltage_mid
                consecutive_failures += 1
                logger.info(
                    f"Voltage {voltage_mid}mV is UNSTABLE "
                    f"(consecutive failures: {consecutive_failures})"
                )
                
                # Check if we've exceeded consecutive failure threshold
                if consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                    logger.warning(
                        f"Consecutive failure threshold reached ({consecutive_failures})"
                    )
                    raise ConsecutiveFailureError(
                        f"Failed {consecutive_failures} consecutive tests at {freq_mhz}MHz"
                    )
        
        logger.info(
            f"Binary search complete: freq={freq_mhz}MHz, "
            f"stable_voltage={last_stable_voltage}mV"
        )
        
        return last_stable_voltage
    
    async def _test_voltage_stability(
        self,
        core_id: int,
        freq_mhz: int,
        voltage_mv: int
    ) -> bool:
        """Test if a voltage is stable at a given frequency.
        
        Monitors temperature during test and aborts if it exceeds safety threshold.
        Implements timeout detection to catch frozen tests.
        
        Args:
            core_id: CPU core ID
            freq_mhz: Frequency in MHz
            voltage_mv: Voltage offset in mV
            
        Returns:
            True if stable, False if unstable
            
        Feature: frequency-based-wizard, Property 14: Temperature safety abort
        Validates: Requirements 9.1, 9.2, 9.3
        """
        try:
            # Start temperature monitoring task
            monitor_task = asyncio.create_task(
                self._monitor_temperature_during_test(self.config.test_duration)
            )
            
            # Start the actual test with timeout
            test_timeout = self.config.test_duration + TEST_TIMEOUT_MARGIN
            
            try:
                result = await asyncio.wait_for(
                    self.test_runner.run_frequency_locked_test(
                        core_id=core_id,
                        freq_mhz=freq_mhz,
                        voltage_mv=voltage_mv,
                        duration=self.config.test_duration
                    ),
                    timeout=test_timeout
                )
                
                # Cancel temperature monitoring
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
                
                # Check if temperature monitoring detected overheating
                if hasattr(self, '_temperature_abort_triggered') and self._temperature_abort_triggered:
                    logger.warning(
                        f"Test aborted due to temperature safety threshold: "
                        f"freq={freq_mhz}MHz, voltage={voltage_mv}mV"
                    )
                    return False
                
                return result.passed
            
            except asyncio.TimeoutError:
                # Test timed out - consider it frozen/unstable
                logger.error(
                    f"Test timeout detected (>{test_timeout}s): "
                    f"freq={freq_mhz}MHz, voltage={voltage_mv}mV"
                )
                
                # Cancel temperature monitoring
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
                
                return False
        
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            return False
    
    async def _monitor_temperature_during_test(self, duration: int) -> None:
        """Monitor CPU temperature during test and abort if threshold exceeded.
        
        Samples temperature every second and sets abort flag if temperature
        exceeds the safety threshold.
        
        Args:
            duration: Test duration in seconds
            
        Feature: frequency-based-wizard, Property 14: Temperature safety abort
        Validates: Requirements 9.1, 9.2
        """
        self._temperature_abort_triggered = False
        
        try:
            for _ in range(duration):
                await asyncio.sleep(1)
                
                # Read current temperature
                metrics = self.test_runner.get_system_metrics()
                temp = metrics.get('temperature')
                
                if temp is not None and temp > TEMPERATURE_ABORT_THRESHOLD:
                    logger.critical(
                        f"TEMPERATURE SAFETY ABORT: {temp:.1f}°C > {TEMPERATURE_ABORT_THRESHOLD}°C"
                    )
                    self._temperature_abort_triggered = True
                    
                    # Restore safe voltage immediately
                    try:
                        if hasattr(self.test_runner, '_ryzenadj_wrapper') and self.test_runner._ryzenadj_wrapper:
                            await self.test_runner._ryzenadj_wrapper.apply_values_async([0, 0, 0, 0])
                            logger.info("Emergency voltage restore to 0mV")
                    except Exception as e:
                        logger.error(f"Failed to restore voltage during temperature abort: {e}")
                    
                    break
        
        except asyncio.CancelledError:
            # Task was cancelled (test completed normally)
            pass
    
    async def _restore_original_state(self, core_id: int) -> None:
        """Restore original CPU governor and voltage settings.
        
        Args:
            core_id: CPU core ID
            
        Feature: frequency-based-wizard, Property 8: Wizard cancellation state restoration
        Validates: Requirements 2.5, 6.4
        """
        logger.info(f"Restoring original state for core {core_id}")
        
        # Restore governor
        try:
            original_governor = self._original_governors.get(core_id, "schedutil")
            self.cpufreq.unlock_frequency(core_id, original_governor)
            logger.info(f"Restored governor to '{original_governor}'")
        except CPUFreqError as e:
            logger.error(f"Failed to restore governor: {e}")
        
        # Restore voltage (reset to 0)
        try:
            # Get ryzenadj wrapper from test runner
            if hasattr(self.test_runner, '_ryzenadj_wrapper') and self.test_runner._ryzenadj_wrapper:
                await self.test_runner._ryzenadj_wrapper.apply_values_async([0, 0, 0, 0])
                logger.info("Restored voltage to 0mV")
        except Exception as e:
            logger.error(f"Failed to restore voltage: {e}")
    
    async def _verify_curve(self, curve: FrequencyCurve) -> bool:
        """Run verification tests at random frequencies to confirm curve stability.
        
        Selects 3-5 random stable frequency points from the curve and re-tests them
        to verify the curve is actually stable.
        
        Args:
            curve: Generated frequency curve to verify
            
        Returns:
            True if all verification tests passed, False otherwise
            
        Feature: frequency-based-wizard, Property 21: Verification test execution
        Validates: Requirements 9.5
        """
        # Get stable points from curve
        stable_points = [p for p in curve.points if p.stable]
        
        if len(stable_points) == 0:
            logger.warning("No stable points to verify")
            return False
        
        # Select random points to verify (3-5 points)
        num_verify = min(VERIFICATION_TEST_COUNT, len(stable_points))
        verify_points = random.sample(stable_points, num_verify)
        
        logger.info(f"Verifying {num_verify} random frequency points")
        
        # Test each verification point
        passed_count = 0
        failed_count = 0
        
        for point in verify_points:
            if self.cancelled:
                logger.info("Verification cancelled")
                return False
            
            logger.info(
                f"Verification test: freq={point.frequency_mhz}MHz, "
                f"voltage={point.voltage_mv}mV"
            )
            
            # Run stability test
            is_stable = await self._test_voltage_stability(
                curve.core_id,
                point.frequency_mhz,
                point.voltage_mv
            )
            
            if is_stable:
                passed_count += 1
                logger.info(f"Verification PASSED: {point.frequency_mhz}MHz")
            else:
                failed_count += 1
                logger.warning(f"Verification FAILED: {point.frequency_mhz}MHz")
        
        logger.info(
            f"Verification complete: {passed_count} passed, {failed_count} failed"
        )
        
        # Consider verification successful if all tests passed
        return failed_count == 0
    
    def _notify_progress(self) -> None:
        """Notify progress callback if set."""
        if self.progress_callback:
            try:
                self.progress_callback(self.progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
