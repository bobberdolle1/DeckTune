"""Autotune engine for automatic undervolt value discovery.

Feature: decktune, Autotune Engine Module
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6

This module implements the automatic undervolt value discovery algorithm
that finds optimal undervolt values for each CPU core through systematic
testing with stress tests.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..core.safety import SafetyManager
    from ..api.events import EventEmitter
    from .runner import TestRunner

logger = logging.getLogger(__name__)


@dataclass
class AutotuneConfig:
    """Configuration for autotune session.
    
    Attributes:
        mode: "quick" or "thorough" - determines test duration and phases
        start_value: Starting undervolt value (typically 0)
        step: Step size for coarse search (typically 5)
        test_duration_quick: Test duration in seconds for quick mode (30)
        test_duration_long: Test duration in seconds for thorough mode (120)
    
    Requirements: 2.1, 2.2
    """
    mode: str = "quick"
    start_value: int = 0
    step: int = 5
    test_duration_quick: int = 30
    test_duration_long: int = 120


@dataclass
class AutotuneResult:
    """Result of an autotune session.
    
    Attributes:
        cores: Final optimal values per core [core0, core1, core2, core3]
        duration: Total time in seconds for the autotune session
        tests_run: Number of tests executed during the session
        stable: True if all cores found stable values
    
    Requirements: 2.5
    """
    cores: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    duration: float = 0.0
    tests_run: int = 0
    stable: bool = False


class AutotuneEngine:
    """Automatic undervolt value discovery engine.
    
    Implements a two-phase algorithm for finding optimal undervolt values:
    
    Phase A (Coarse Search):
    - For each core, step down from start_value by -step until failure
    - Record first_fail and last_good values
    - Uses quick tests (30 seconds)
    
    Phase B (Binary Search Refinement, thorough mode only):
    - Refine between last_good and first_fail
    - Find optimal value within ±2 tolerance
    - Uses longer tests (120 seconds)
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
    """
    
    NUM_CORES = 4
    
    def __init__(
        self,
        ryzenadj: "RyzenadjWrapper",
        runner: "TestRunner",
        safety: "SafetyManager",
        event_emitter: "EventEmitter"
    ):
        """Initialize the autotune engine.
        
        Args:
            ryzenadj: RyzenadjWrapper for applying undervolt values
            runner: TestRunner for executing stress tests
            safety: SafetyManager for LKG persistence and value clamping
            event_emitter: EventEmitter for progress updates to frontend
        """
        self.ryzenadj = ryzenadj
        self.runner = runner
        self.safety = safety
        self.event_emitter = event_emitter
        
        self._cancelled = False
        self._running = False
        self._tests_run = 0
        self._current_values: List[int] = [0, 0, 0, 0]

    def cancel(self) -> None:
        """Cancel the running autotune session.
        
        Sets the cancelled flag which will be checked between test iterations.
        """
        logger.info("Autotune cancellation requested")
        self._cancelled = True
    
    def is_running(self) -> bool:
        """Check if autotune is currently running.
        
        Returns:
            True if autotune session is in progress
        """
        return self._running
    
    def _get_test_name(self, mode: str) -> str:
        """Get the appropriate test name based on mode.
        
        Args:
            mode: "quick" or "thorough"
            
        Returns:
            Test name key for TestRunner.TESTS
        """
        return "cpu_quick" if mode == "quick" else "cpu_long"
    
    def _estimate_eta(
        self,
        phase: str,
        current_core: int,
        cores_remaining: int,
        tests_per_core_estimate: int,
        test_duration: int
    ) -> int:
        """Estimate remaining time in seconds.
        
        Args:
            phase: Current phase ("A" or "B")
            current_core: Current core being tested
            cores_remaining: Number of cores left to test
            tests_per_core_estimate: Estimated tests per core
            test_duration: Duration of each test in seconds
            
        Returns:
            Estimated time remaining in seconds
        """
        remaining_tests = cores_remaining * tests_per_core_estimate
        return remaining_tests * test_duration
    
    async def _emit_progress(
        self,
        phase: str,
        core: int,
        value: int,
        eta: int
    ) -> None:
        """Emit progress event to frontend.
        
        Args:
            phase: Current phase ("A" or "B")
            core: Current core index (0-3)
            value: Current undervolt value being tested
            eta: Estimated time remaining in seconds
            
        Requirements: 2.6
        """
        await self.event_emitter.emit_tuning_progress(
            phase=phase,
            core=core,
            value=value,
            eta=max(0, eta)
        )
    
    async def _apply_test_values(self, values: List[int]) -> Tuple[bool, Optional[str]]:
        """Apply undervolt values for testing.
        
        Clamps values to platform limits before applying.
        
        Args:
            values: List of 4 undervolt values
            
        Returns:
            Tuple of (success, error_message)
        """
        clamped = self.safety.clamp_values(values)
        self._current_values = clamped.copy()
        return await self.ryzenadj.apply_values_async(clamped)
    
    async def _run_stability_test(self, test_name: str) -> bool:
        """Run a stability test and return pass/fail.
        
        Also checks dmesg for MCE/segfault errors after the test.
        
        Args:
            test_name: Test name key for TestRunner.TESTS
            
        Returns:
            True if test passed, False otherwise
            
        Requirements: 2.3
        """
        self._tests_run += 1
        
        result = await self.runner.run_test(test_name)
        
        if not result.passed:
            logger.info(f"Stability test failed: {result.error or 'test failure'}")
            return False
        
        # Check dmesg for hardware errors
        dmesg_errors = await self.runner.check_dmesg_errors()
        if dmesg_errors:
            logger.warning(f"dmesg errors detected: {dmesg_errors}")
            return False
        
        return True

    async def _phase_a(
        self,
        core: int,
        config: AutotuneConfig
    ) -> Tuple[int, int]:
        """Phase A: Coarse search for single core.
        
        Steps down from start_value by -step until failure, then records
        the last_good and first_fail values.
        
        Args:
            core: Core index (0-3)
            config: Autotune configuration
            
        Returns:
            Tuple of (last_good, first_fail) values
            - last_good: Last value that passed stability test
            - first_fail: First value that failed stability test
            
        Requirements: 2.1, 2.3, 2.4
        """
        test_name = self._get_test_name(config.mode)
        safe_limit = self.safety.platform.safe_limit
        
        current_value = config.start_value
        last_good = config.start_value
        first_fail = safe_limit  # Default to safe limit if we never fail
        
        # Build test values array - keep other cores at their current values
        test_values = self._current_values.copy()
        
        # Estimate tests per core for ETA calculation
        tests_per_core = abs(safe_limit - config.start_value) // config.step + 1
        
        logger.info(f"Phase A: Starting coarse search for core {core}")
        
        while current_value >= safe_limit:
            if self._cancelled:
                logger.info(f"Phase A cancelled for core {core}")
                break
            
            # Update test values for this core
            test_values[core] = current_value
            
            # Calculate ETA
            remaining_steps = abs(current_value - safe_limit) // config.step
            cores_remaining = self.NUM_CORES - core - 1
            eta = self._estimate_eta(
                "A",
                core,
                cores_remaining,
                tests_per_core,
                config.test_duration_quick
            ) + (remaining_steps * config.test_duration_quick)
            
            # Emit progress
            await self._emit_progress("A", core, current_value, eta)
            
            # Apply values
            success, error = await self._apply_test_values(test_values)
            if not success:
                logger.error(f"Failed to apply values for core {core}: {error}")
                # Treat apply failure as test failure
                first_fail = current_value
                break
            
            # Run stability test
            logger.info(f"Phase A: Testing core {core} at value {current_value}")
            passed = await self._run_stability_test(test_name)
            
            if passed:
                last_good = current_value
                # Step down to more aggressive undervolt
                current_value -= config.step
            else:
                # Test failed - record first_fail and stop
                first_fail = current_value
                logger.info(
                    f"Phase A: Core {core} failed at {current_value}, "
                    f"last_good={last_good}"
                )
                
                # Rollback to last good value (Requirement 2.4)
                test_values[core] = last_good
                await self._apply_test_values(test_values)
                break
        
        # If we reached safe_limit without failure, last_good is the limit
        if current_value < safe_limit and first_fail == safe_limit:
            last_good = safe_limit
            logger.info(f"Phase A: Core {core} reached safe limit {safe_limit}")
        
        logger.info(
            f"Phase A complete for core {core}: "
            f"last_good={last_good}, first_fail={first_fail}"
        )
        
        return last_good, first_fail

    async def _phase_b(
        self,
        core: int,
        last_good: int,
        first_fail: int,
        config: AutotuneConfig
    ) -> int:
        """Phase B: Binary search refinement for single core.
        
        Refines the optimal value between last_good and first_fail using
        binary search. Only runs in thorough mode.
        
        Args:
            core: Core index (0-3)
            last_good: Last value that passed (from Phase A)
            first_fail: First value that failed (from Phase A)
            config: Autotune configuration
            
        Returns:
            Optimal undervolt value for this core
            
        Requirements: 2.2
        """
        # If last_good equals first_fail or they're adjacent, no refinement needed
        if last_good >= first_fail or abs(last_good - first_fail) <= config.step:
            logger.info(
                f"Phase B: No refinement needed for core {core}, "
                f"using last_good={last_good}"
            )
            return last_good
        
        test_name = "cpu_long"  # Use longer tests for thorough mode
        
        # Build test values array
        test_values = self._current_values.copy()
        
        low = first_fail  # More aggressive (lower/more negative)
        high = last_good  # Less aggressive (higher/less negative)
        best_value = last_good
        
        logger.info(
            f"Phase B: Starting binary search for core {core} "
            f"between {low} and {high}"
        )
        
        # Binary search with tolerance of 2
        tolerance = 2
        iterations = 0
        max_iterations = 10  # Safety limit
        
        while high - low > tolerance and iterations < max_iterations:
            if self._cancelled:
                logger.info(f"Phase B cancelled for core {core}")
                break
            
            iterations += 1
            mid = (low + high) // 2
            
            # Calculate ETA (rough estimate)
            remaining_iterations = max(0, int(
                (high - low) / tolerance
            ).bit_length() - iterations)
            eta = remaining_iterations * config.test_duration_long
            
            # Emit progress
            await self._emit_progress("B", core, mid, eta)
            
            # Update test values for this core
            test_values[core] = mid
            
            # Apply values
            success, error = await self._apply_test_values(test_values)
            if not success:
                logger.error(f"Failed to apply values for core {core}: {error}")
                # Treat as failure, move to less aggressive
                low = mid
                continue
            
            # Run stability test
            logger.info(f"Phase B: Testing core {core} at value {mid}")
            passed = await self._run_stability_test(test_name)
            
            if passed:
                # Test passed, try more aggressive
                best_value = mid
                high = mid
                logger.info(f"Phase B: Core {core} passed at {mid}")
            else:
                # Test failed, move to less aggressive (Requirement 2.4)
                low = mid
                logger.info(f"Phase B: Core {core} failed at {mid}")
                
                # Rollback to best known value
                test_values[core] = best_value
                await self._apply_test_values(test_values)
        
        logger.info(f"Phase B complete for core {core}: optimal={best_value}")
        return best_value

    async def run(self, config: AutotuneConfig) -> AutotuneResult:
        """Execute the autotune algorithm.
        
        Orchestrates the full autotune process:
        1. Create tuning flag for safety
        2. Execute Phase A for all cores (coarse search)
        3. Execute Phase B for all cores if thorough mode (binary refinement)
        4. Save results as LKG
        5. Remove tuning flag
        
        Args:
            config: Autotune configuration
            
        Returns:
            AutotuneResult with final values and statistics
            
        Requirements: 2.1, 2.2, 2.5
        """
        if self._running:
            logger.warning("Autotune already running")
            return AutotuneResult(
                cores=[0, 0, 0, 0],
                duration=0.0,
                tests_run=0,
                stable=False
            )
        
        self._running = True
        self._cancelled = False
        self._tests_run = 0
        self._current_values = [0, 0, 0, 0]
        
        start_time = time.time()
        final_values = [0, 0, 0, 0]
        phase_a_results: List[Tuple[int, int]] = []
        stable = True
        
        logger.info(f"Starting autotune in {config.mode} mode")
        
        try:
            # Create tuning flag for safety recovery
            self.safety.create_tuning_flag()
            
            # Phase A: Coarse search for all cores
            for core in range(self.NUM_CORES):
                if self._cancelled:
                    logger.info("Autotune cancelled during Phase A")
                    stable = False
                    break
                
                last_good, first_fail = await self._phase_a(core, config)
                phase_a_results.append((last_good, first_fail))
                
                # Update current values with the result
                self._current_values[core] = last_good
                final_values[core] = last_good
            
            # Phase B: Binary search refinement (thorough mode only)
            if config.mode == "thorough" and not self._cancelled:
                logger.info("Starting Phase B (binary search refinement)")
                
                for core in range(self.NUM_CORES):
                    if self._cancelled:
                        logger.info("Autotune cancelled during Phase B")
                        stable = False
                        break
                    
                    if core < len(phase_a_results):
                        last_good, first_fail = phase_a_results[core]
                        
                        # Only refine if there's a gap between last_good and first_fail
                        if last_good > first_fail:
                            optimal = await self._phase_b(
                                core, last_good, first_fail, config
                            )
                            final_values[core] = optimal
                            self._current_values[core] = optimal
            
            # Apply final values
            if not self._cancelled:
                clamped_values = self.safety.clamp_values(final_values)
                success, error = await self._apply_test_values(clamped_values)
                
                if success:
                    # Save as LKG (Requirement 2.5)
                    self.safety.save_lkg(clamped_values)
                    logger.info(f"Autotune complete, saved LKG: {clamped_values}")
                else:
                    logger.error(f"Failed to apply final values: {error}")
                    stable = False
            
        except Exception as e:
            logger.exception(f"Autotune error: {e}")
            stable = False
            
            # Attempt rollback on error
            try:
                self.safety.rollback_to_lkg()
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
        
        finally:
            # Always remove tuning flag
            self.safety.remove_tuning_flag()
            self._running = False
        
        duration = time.time() - start_time
        
        result = AutotuneResult(
            cores=final_values,
            duration=duration,
            tests_run=self._tests_run,
            stable=stable and not self._cancelled
        )
        
        # Emit completion event
        await self.event_emitter.emit_tuning_complete(result)
        
        logger.info(
            f"Autotune finished: cores={result.cores}, "
            f"duration={result.duration:.1f}s, "
            f"tests={result.tests_run}, stable={result.stable}"
        )
        
        return result
