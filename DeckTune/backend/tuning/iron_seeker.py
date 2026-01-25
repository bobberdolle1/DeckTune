"""Iron Seeker - Per-core undervolt optimization engine.

Feature: iron-seeker, Iron Seeker Engine
Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5,
           4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 8.1, 8.2, 8.3

This module implements the Iron Seeker algorithm for automatic per-core undervolt
discovery using Vdroop (transient load) stress testing.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..core.safety import SafetyManager
    from ..api.events import EventEmitter
    from .vdroop import VdroopTester

logger = logging.getLogger(__name__)


def calculate_recommended_value(max_stable: int, safety_margin: int) -> int:
    """Calculate recommended undervolt value with safety margin.
    
    The recommended value is calculated by adding the safety margin to the
    max_stable value (making it less negative / closer to 0), then clamping
    to ensure it doesn't exceed 0mV.
    
    Args:
        max_stable: Maximum stable undervolt value in mV (negative or zero)
        safety_margin: Safety margin to add in mV (positive)
        
    Returns:
        Recommended value in mV, clamped to not exceed 0
        
    Examples:
        >>> calculate_recommended_value(-30, 5)
        -25
        >>> calculate_recommended_value(-3, 5)
        0  # Clamped to 0
        >>> calculate_recommended_value(0, 5)
        0  # Already at 0
        
    Requirements: 6.1, 6.2
    """
    # Add margin (makes value less negative / closer to 0)
    recommended = max_stable + safety_margin
    # Clamp to not exceed 0 (Requirement 6.2)
    return min(recommended, 0)


class QualityTier(Enum):
    """Silicon quality tier based on achieved undervolt depth.
    
    Thresholds:
    - GOLD: ≤ -35mV (excellent silicon)
    - SILVER: -34mV to -20mV (average silicon)
    - BRONZE: > -20mV (below average silicon)
    
    Requirements: 4.1, 4.2
    """
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    
    @staticmethod
    def from_value(value: int) -> "QualityTier":
        """Calculate quality tier from undervolt value.
        
        Args:
            value: Undervolt value in mV (negative or zero)
            
        Returns:
            QualityTier based on thresholds
            
        Requirements: 4.1, 4.2
        """
        if value <= -35:
            return QualityTier.GOLD
        elif value <= -20:
            return QualityTier.SILVER
        else:
            return QualityTier.BRONZE


@dataclass
class IronSeekerConfig:
    """Configuration for Iron Seeker session.
    
    Attributes:
        step_size: Step increment in mV (default 5, valid range [1, 20])
        test_duration: Test duration per iteration in seconds (default 60, valid range [10, 300])
        safety_margin: Safety margin to add to results in mV (default 5, valid range [0, 20])
        vdroop_pulse_ms: Pulse duration for Vdroop test in ms (default 100)
    
    Requirements: 7.1, 7.2, 7.3
    """
    step_size: int = 5
    test_duration: int = 60
    safety_margin: int = 5
    vdroop_pulse_ms: int = 100
    
    def __post_init__(self) -> None:
        """Clamp configuration values to valid ranges.
        
        Requirements: 7.3
        """
        self.step_size = self._clamp(self.step_size, 1, 20)
        self.test_duration = self._clamp(self.test_duration, 10, 300)
        self.safety_margin = self._clamp(self.safety_margin, 0, 20)
        self.vdroop_pulse_ms = self._clamp(self.vdroop_pulse_ms, 10, 500)
    
    @staticmethod
    def _clamp(value: int, min_val: int, max_val: int) -> int:
        """Clamp value to range [min_val, max_val]."""
        if value < min_val:
            logger.warning(f"Clamping value {value} to minimum {min_val}")
            return min_val
        if value > max_val:
            logger.warning(f"Clamping value {value} to maximum {max_val}")
            return max_val
        return value


@dataclass
class CoreResult:
    """Result for a single CPU core.
    
    Attributes:
        core_index: Core number (0-3)
        max_stable: Maximum stable undervolt in mV (most negative that passed)
        recommended: Recommended value with safety margin in mV
        quality_tier: Quality tier string ("gold", "silver", or "bronze")
        iterations: Number of test iterations performed
        failed_value: Value that caused failure (if any), None if hit limit
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    core_index: int
    max_stable: int
    recommended: int
    quality_tier: str
    iterations: int
    failed_value: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class IronSeekerResult:
    """Complete Iron Seeker result.
    
    Attributes:
        cores: Results for all 4 cores
        duration: Total time in seconds
        recovered: True if recovered from crash
        aborted: True if cancelled or hit limit early
    
    Requirements: 1.4, 5.3
    """
    cores: List[CoreResult] = field(default_factory=list)
    duration: float = 0.0
    recovered: bool = False
    aborted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cores": [c.to_dict() for c in self.cores],
            "duration": self.duration,
            "recovered": self.recovered,
            "aborted": self.aborted
        }


@dataclass
class IronSeekerStoredResult:
    """Stored Iron Seeker result format for settings persistence.
    
    This is the format used to persist Iron Seeker results to settings.
    It contains both raw max_stable values and recommended values with margin.
    
    Attributes:
        cores: List of per-core result dictionaries with index, max_stable, recommended, tier
        timestamp: ISO timestamp of when the results were saved
        duration: Total time in seconds for the Iron Seeker run
    
    Requirements: 4.4, 6.3
    """
    cores: List[Dict[str, Any]]
    timestamp: str
    duration: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary suitable for storage in settings
            
        Requirements: 6.3
        """
        return {
            "cores": self.cores,
            "timestamp": self.timestamp,
            "duration": self.duration
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "IronSeekerStoredResult":
        """Create IronSeekerStoredResult from dictionary.
        
        Args:
            data: Dictionary from settings
            
        Returns:
            IronSeekerStoredResult instance
            
        Raises:
            KeyError: If required fields are missing
        """
        return IronSeekerStoredResult(
            cores=data["cores"],
            timestamp=data["timestamp"],
            duration=data["duration"]
        )
    
    @staticmethod
    def from_result(result: "IronSeekerResult") -> "IronSeekerStoredResult":
        """Create IronSeekerStoredResult from IronSeekerResult.
        
        Converts the runtime result format to the storage format.
        
        Args:
            result: IronSeekerResult from a completed run
            
        Returns:
            IronSeekerStoredResult ready for persistence
            
        Requirements: 4.4, 6.3
        """
        cores = []
        for core_result in result.cores:
            cores.append({
                "index": core_result.core_index,
                "max_stable": core_result.max_stable,
                "recommended": core_result.recommended,
                "tier": core_result.quality_tier
            })
        
        return IronSeekerStoredResult(
            cores=cores,
            timestamp=datetime.now().isoformat(),
            duration=result.duration
        )
    
    def validate(self) -> bool:
        """Validate the stored result structure.
        
        Checks that:
        - There are exactly 4 core results
        - Each core has required fields (index, max_stable, recommended, tier)
        - Tier values are valid
        
        Returns:
            True if valid, False otherwise
            
        Requirements: 4.4
        """
        if len(self.cores) != NUM_CORES:
            return False
        
        valid_tiers = {"gold", "silver", "bronze"}
        
        for core in self.cores:
            required_fields = {"index", "max_stable", "recommended", "tier"}
            if not all(field in core for field in required_fields):
                return False
            if core["tier"] not in valid_tiers:
                return False
        
        return True


@dataclass
class IronSeekerState:
    """Persistent state for crash recovery.
    
    This state is persisted to disk before each test iteration to enable
    recovery in case of system crash or reboot during testing.
    
    Attributes:
        active: Is Iron Seeker currently running?
        current_core: Core being tested (0-3)
        current_value: Value being tested (mV)
        core_results: Stable values found so far [c0, c1, c2, c3]
        failed_values: Failed values per core {core_index: [values]}
        config: Configuration snapshot
        timestamp: ISO timestamp
    
    Requirements: 3.1, 3.2
    """
    active: bool
    current_core: int
    current_value: int
    core_results: List[int]
    failed_values: Dict[int, List[int]]
    config: Dict[str, int]
    timestamp: str
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary.
        
        Requirements: 3.1
        """
        return {
            "active": self.active,
            "current_core": self.current_core,
            "current_value": self.current_value,
            "core_results": self.core_results,
            "failed_values": {str(k): v for k, v in self.failed_values.items()},
            "config": self.config,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> "IronSeekerState":
        """Create IronSeekerState from JSON dictionary.
        
        Args:
            data: Dictionary from JSON parsing
            
        Returns:
            IronSeekerState instance
            
        Raises:
            KeyError: If required fields are missing
            TypeError: If field types are invalid
            
        Requirements: 3.2
        """
        return IronSeekerState(
            active=data["active"],
            current_core=data["current_core"],
            current_value=data["current_value"],
            core_results=data["core_results"],
            failed_values={int(k): v for k, v in data["failed_values"].items()},
            config=data["config"],
            timestamp=data["timestamp"]
        )


@dataclass
class IronSeekerPreset:
    """Preset containing per-core undervolt values from Iron Seeker results.
    
    This class represents a saved preset that can be created from Iron Seeker
    results and later loaded to apply per-core undervolt values.
    
    Attributes:
        name: Preset display name
        values: Per-core undervolt values [core0, core1, core2, core3] in mV
        tiers: Per-core quality tiers ["gold", "silver", "bronze", ...]
        timestamp: ISO timestamp of when the preset was created
        description: Optional description of the preset
    
    Requirements: 8.2
    """
    name: str
    values: List[int]
    tiers: List[str]
    timestamp: str
    description: str = ""
    
    def __post_init__(self) -> None:
        """Validate preset structure on creation."""
        if len(self.values) != 4:
            raise ValueError(f"values must have exactly 4 entries, got {len(self.values)}")
        if len(self.tiers) != 4:
            raise ValueError(f"tiers must have exactly 4 entries, got {len(self.tiers)}")
        
        valid_tiers = {"gold", "silver", "bronze"}
        for i, tier in enumerate(self.tiers):
            if tier not in valid_tiers:
                raise ValueError(f"tiers[{i}] '{tier}' must be one of {valid_tiers}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary suitable for storage
            
        Requirements: 8.2
        """
        return {
            "name": self.name,
            "values": self.values,
            "tiers": self.tiers,
            "timestamp": self.timestamp,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "IronSeekerPreset":
        """Create IronSeekerPreset from dictionary.
        
        Args:
            data: Dictionary from storage
            
        Returns:
            IronSeekerPreset instance
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If structure is invalid
            
        Requirements: 8.2
        """
        return IronSeekerPreset(
            name=data["name"],
            values=data["values"],
            tiers=data["tiers"],
            timestamp=data["timestamp"],
            description=data.get("description", "")
        )
    
    @staticmethod
    def from_result(result: "IronSeekerResult", name: str, description: str = "") -> "IronSeekerPreset":
        """Create IronSeekerPreset from IronSeekerResult.
        
        Converts the runtime result format to a preset that can be saved.
        Uses the recommended values (with safety margin applied).
        
        Args:
            result: IronSeekerResult from a completed run
            name: Name for the preset
            description: Optional description
            
        Returns:
            IronSeekerPreset ready for storage
            
        Requirements: 8.2
        """
        values = [core.recommended for core in result.cores]
        tiers = [core.quality_tier for core in result.cores]
        
        return IronSeekerPreset(
            name=name,
            values=values,
            tiers=tiers,
            timestamp=datetime.now().isoformat(),
            description=description
        )
    
    @staticmethod
    def from_stored_result(stored: "IronSeekerStoredResult", name: str, description: str = "") -> "IronSeekerPreset":
        """Create IronSeekerPreset from IronSeekerStoredResult.
        
        Converts the stored result format to a preset.
        Uses the recommended values (with safety margin applied).
        
        Args:
            stored: IronSeekerStoredResult from settings
            name: Name for the preset
            description: Optional description
            
        Returns:
            IronSeekerPreset ready for storage
            
        Requirements: 8.2
        """
        values = [core["recommended"] for core in stored.cores]
        tiers = [core["tier"] for core in stored.cores]
        
        return IronSeekerPreset(
            name=name,
            values=values,
            tiers=tiers,
            timestamp=stored.timestamp,
            description=description
        )
    
    def validate(self) -> List[str]:
        """Validate the preset structure.
        
        Returns:
            List of validation error messages (empty if valid)
            
        Requirements: 8.2
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Preset name cannot be empty")
        
        if len(self.name) > 64:
            errors.append("Preset name must be 64 characters or less")
        
        if len(self.values) != 4:
            errors.append(f"values must have exactly 4 entries, got {len(self.values)}")
        
        if len(self.tiers) != 4:
            errors.append(f"tiers must have exactly 4 entries, got {len(self.tiers)}")
        
        valid_tiers = {"gold", "silver", "bronze"}
        for i, tier in enumerate(self.tiers):
            if tier not in valid_tiers:
                errors.append(f"tiers[{i}] '{tier}' must be one of {valid_tiers}")
        
        # Validate undervolt values are in reasonable range
        for i, value in enumerate(self.values):
            if value > 0:
                errors.append(f"values[{i}] ({value}) must be <= 0")
            if value < -100:
                errors.append(f"values[{i}] ({value}) must be >= -100")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if preset is valid.
        
        Returns:
            True if valid, False otherwise
        """
        return len(self.validate()) == 0


# Number of CPU cores on Steam Deck
NUM_CORES = 4

# Default platform safe limit (used if not provided)
DEFAULT_SAFE_LIMIT = -50


class IronSeekerEngine:
    """Per-core undervolt optimization engine.
    
    Iron Seeker tests each CPU core independently to find the optimal
    undervolt value, accounting for silicon lottery variations between cores.
    
    The algorithm:
    1. For each core (0-3), starting from 0mV
    2. Step down by step_size until failure or platform limit
    3. Run Vdroop stress test at each value
    4. Record max stable value and calculate quality tier
    5. Apply safety margin to get recommended value
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    
    def __init__(
        self,
        ryzenadj: "RyzenadjWrapper",
        vdroop_tester: "VdroopTester",
        safety: "SafetyManager",
        event_emitter: Optional["EventEmitter"] = None,
        safe_limit: int = DEFAULT_SAFE_LIMIT
    ):
        """Initialize the Iron Seeker engine.
        
        Args:
            ryzenadj: RyzenadjWrapper for applying undervolt values
            vdroop_tester: VdroopTester for running stress tests
            safety: SafetyManager for state persistence and recovery
            event_emitter: Optional EventEmitter for progress events
            safe_limit: Platform safe limit (most negative allowed value)
            
        Requirements: 1.1
        """
        self._ryzenadj = ryzenadj
        self._vdroop_tester = vdroop_tester
        self._safety = safety
        self._event_emitter = event_emitter
        self._safe_limit = safe_limit
        
        # Runtime state
        self._running = False
        self._cancelled = False
        self._config: Optional[IronSeekerConfig] = None
        
        # Per-core tracking during execution
        self._core_results: List[int] = [0, 0, 0, 0]  # Stable values found
        self._failed_values: Dict[int, List[int]] = {}  # Failed values per core
        self._initial_values: List[int] = [0, 0, 0, 0]  # Values before Iron Seeker
        
        # Timing for ETA calculation
        self._start_time: float = 0.0
        self._test_durations: List[float] = []  # Track actual test durations
        
        # Progress tracking
        self._current_iteration: int = 0  # Current iteration within core
        self._total_iterations_per_core: int = 0  # Estimated iterations per core
    
    def is_running(self) -> bool:
        """Check if Iron Seeker is currently running.
        
        Returns:
            True if Iron Seeker is actively testing
            
        Requirements: 1.1
        """
        return self._running
    
    def cancel(self) -> None:
        """Cancel the running Iron Seeker session.
        
        Sets the cancelled flag which will be checked between test iterations.
        When the main loop detects cancellation, it will:
        1. Stop testing immediately
        2. Restore the initial values (from before Iron Seeker started)
        3. Clear the state file
        
        Requirements: 3.5
        """
        logger.info("Iron Seeker cancellation requested")
        self._cancelled = True
        # Also cancel the vdroop tester if it's running
        if self._vdroop_tester is not None:
            self._vdroop_tester.cancel()
    
    def check_recovery(self, restore_values: bool = True) -> Optional[IronSeekerState]:
        """Check for and load any existing recovery state.
        
        If an active state file is found (indicating a crash during testing),
        this method will:
        1. Load the state file
        2. Identify the crashed value (current_value at time of crash)
        3. Optionally restore the stable values (core_results) via ryzenadj
        
        Args:
            restore_values: If True, restore stable values via ryzenadj.
                           Set to False when called from start() since values
                           will be applied during testing.
        
        Returns:
            IronSeekerState if recovery is needed, None otherwise
            
        Requirements: 3.2, 3.3
        """
        state = self._safety.load_iron_seeker_state()
        
        if state is None or not state.active:
            return None
        
        logger.warning(
            f"Iron Seeker crash recovery: detected crash at core {state.current_core}, "
            f"value {state.current_value}mV"
        )
        
        # Restore the stable values that were recorded before the crash
        # These are the last known good values for each core
        if restore_values:
            stable_values = state.core_results.copy()
            
            logger.info(f"Restoring stable values: {stable_values}")
            
            # Apply the stable values via ryzenadj
            try:
                success, error = self._ryzenadj.apply_values(stable_values)
                if success:
                    logger.info("Successfully restored stable values after crash recovery")
                else:
                    logger.error(f"Failed to restore stable values: {error}")
            except Exception as e:
                logger.error(f"Exception during crash recovery value restoration: {e}")
        
        return state
    
    def _calculate_recommended(self, max_stable: int, safety_margin: int) -> int:
        """Calculate recommended value with safety margin.
        
        Args:
            max_stable: Maximum stable undervolt value (negative)
            safety_margin: Safety margin to add (positive)
            
        Returns:
            Recommended value, clamped to not exceed 0
            
        Requirements: 6.1, 6.2
        """
        return calculate_recommended_value(max_stable, safety_margin)
    
    def _build_apply_values(self, core_being_tested: int, test_value: int) -> List[int]:
        """Build the values array to apply during testing.
        
        When testing core N:
        - Cores 0..N-1: Use their discovered stable values
        - Core N: Use the test value
        - Cores N+1..3: Use initial values (from before Iron Seeker)
        
        Args:
            core_being_tested: Index of core being tested (0-3)
            test_value: Value to apply to the core being tested
            
        Returns:
            List of 4 values to apply
            
        Requirements: 1.1
        """
        values = []
        for i in range(NUM_CORES):
            if i < core_being_tested:
                # Already tested cores: use their stable values
                values.append(self._core_results[i])
            elif i == core_being_tested:
                # Core being tested: use test value
                values.append(test_value)
            else:
                # Not yet tested cores: use initial values
                values.append(self._initial_values[i])
        return values
    
    def _generate_test_sequence(self, step_size: int) -> List[int]:
        """Generate the sequence of values to test for a core.
        
        Sequence: 0, -step_size, -2*step_size, ... until safe_limit
        
        Args:
            step_size: Step increment in mV
            
        Returns:
            List of values to test in order
            
        Requirements: 1.2
        """
        sequence = []
        value = 0
        while value >= self._safe_limit:
            sequence.append(value)
            value -= step_size
        return sequence
    
    def calculate_eta(
        self,
        current_core: int,
        current_iteration: int,
        estimated_iterations_per_core: int
    ) -> int:
        """Calculate estimated time remaining for Iron Seeker.
        
        ETA is calculated based on:
        - Remaining cores to test
        - Average test duration from completed tests
        - Remaining iterations for current core
        
        Formula:
        ETA = (remaining_cores * iterations_per_core * avg_duration) +
              (remaining_iterations_current_core * avg_duration)
        
        Args:
            current_core: Core currently being tested (0-3)
            current_iteration: Current iteration within the core (1-based)
            estimated_iterations_per_core: Estimated total iterations per core
            
        Returns:
            Estimated seconds remaining (≥0)
            
        Requirements: 5.4
        """
        # Calculate average test duration
        if self._test_durations:
            avg_duration = sum(self._test_durations) / len(self._test_durations)
        elif self._config:
            # Use configured duration as estimate if no tests completed yet
            avg_duration = self._config.test_duration
        else:
            avg_duration = 60  # Default fallback
        
        # Remaining cores after current one
        remaining_cores = NUM_CORES - current_core - 1
        
        # Remaining iterations in current core
        remaining_iterations_current = max(0, estimated_iterations_per_core - current_iteration)
        
        # Total remaining iterations
        total_remaining = (remaining_cores * estimated_iterations_per_core) + remaining_iterations_current
        
        # Calculate ETA
        eta = int(total_remaining * avg_duration)
        
        return max(0, eta)
    
    async def _emit_progress(
        self,
        core: int,
        value: int,
        iteration: int,
        estimated_iterations_per_core: int
    ) -> None:
        """Emit progress event during testing.
        
        Args:
            core: Current core being tested (0-3)
            value: Current test value (mV)
            iteration: Current iteration (1-based)
            estimated_iterations_per_core: Estimated iterations per core
            
        Requirements: 5.1
        """
        if self._event_emitter is None:
            return
        
        eta = self.calculate_eta(core, iteration, estimated_iterations_per_core)
        
        await self._event_emitter.emit_iron_seeker_progress(
            core=core,
            value=value,
            iteration=iteration,
            eta=eta,
            core_results=self._core_results.copy()
        )
    
    async def _emit_core_complete(self, result: CoreResult) -> None:
        """Emit core completion event.
        
        Args:
            result: CoreResult for the completed core
            
        Requirements: 5.2
        """
        if self._event_emitter is None:
            return
        
        await self._event_emitter.emit_iron_seeker_core_complete(
            core=result.core_index,
            max_stable=result.max_stable,
            recommended=result.recommended,
            tier=result.quality_tier
        )
    
    async def _emit_complete(self, result: "IronSeekerResult") -> None:
        """Emit completion event.
        
        Args:
            result: Complete IronSeekerResult
            
        Requirements: 5.3
        """
        if self._event_emitter is None:
            return
        
        cores_data = [c.to_dict() for c in result.cores]
        
        await self._event_emitter.emit_iron_seeker_complete(
            cores=cores_data,
            duration=result.duration,
            recovered=result.recovered,
            aborted=result.aborted
        )
    
    async def _emit_recovery(
        self,
        crashed_core: int,
        crashed_value: int,
        restored_values: List[int]
    ) -> None:
        """Emit recovery event.
        
        Args:
            crashed_core: Core that was being tested when crash occurred
            crashed_value: Value that was being tested when crash occurred
            restored_values: Values restored after recovery
            
        Requirements: 3.4
        """
        if self._event_emitter is None:
            return
        
        await self._event_emitter.emit_iron_seeker_recovery(
            crashed_core=crashed_core,
            crashed_value=crashed_value,
            restored_values=restored_values
        )
    
    async def _persist_state(
        self,
        current_core: int,
        current_value: int,
        config: IronSeekerConfig
    ) -> None:
        """Persist current state for crash recovery.
        
        Args:
            current_core: Core being tested
            current_value: Value being tested
            config: Current configuration
            
        Requirements: 3.1
        """
        state = IronSeekerState(
            active=True,
            current_core=current_core,
            current_value=current_value,
            core_results=self._core_results.copy(),
            failed_values={k: v.copy() for k, v in self._failed_values.items()},
            config={
                "step_size": config.step_size,
                "test_duration": config.test_duration,
                "safety_margin": config.safety_margin
            },
            timestamp=datetime.now().isoformat()
        )
        self._safety.create_iron_seeker_state(state)
    
    async def _test_core(
        self,
        core_index: int,
        config: IronSeekerConfig,
        start_value: int = 0
    ) -> CoreResult:
        """Test a single core to find its maximum stable undervolt.
        
        Args:
            core_index: Core to test (0-3)
            config: Iron Seeker configuration
            start_value: Starting value (for recovery continuation)
            
        Returns:
            CoreResult with the test results
            
        Requirements: 1.1, 1.2, 1.3, 1.5, 5.1
        """
        test_sequence = self._generate_test_sequence(config.step_size)
        estimated_iterations_per_core = len(test_sequence)
        
        # If recovering, skip values already tested
        if start_value != 0:
            test_sequence = [v for v in test_sequence if v <= start_value]
        
        max_stable = 0  # Best stable value found (most negative)
        iterations = 0
        failed_value = None
        
        for test_value in test_sequence:
            if self._cancelled:
                logger.info(f"Core {core_index} testing cancelled")
                break
            
            iterations += 1
            
            # Emit progress event (Req 5.1)
            await self._emit_progress(
                core=core_index,
                value=test_value,
                iteration=iterations,
                estimated_iterations_per_core=estimated_iterations_per_core
            )
            
            # Persist state before applying (Req 3.1)
            await self._persist_state(core_index, test_value, config)
            
            # Build values array with proper isolation (Req 1.1)
            apply_values = self._build_apply_values(core_index, test_value)
            
            # Apply the values
            logger.info(f"Testing core {core_index} at {test_value}mV, applying: {apply_values}")
            success, error = await self._ryzenadj.apply_values_async(apply_values)
            
            if not success:
                logger.error(f"Failed to apply values: {error}")
                failed_value = test_value
                break
            
            # Run Vdroop test
            test_start = time.time()
            result = await self._vdroop_tester.run_vdroop_test(
                config.test_duration,
                config.vdroop_pulse_ms
            )
            test_duration = time.time() - test_start
            self._test_durations.append(test_duration)
            
            if result.passed:
                # Test passed - this value is stable
                max_stable = test_value
                logger.info(f"Core {core_index}: {test_value}mV PASSED")
                
                # Check if we've hit the safe limit (Req 1.5)
                if test_value <= self._safe_limit:
                    logger.info(f"Core {core_index}: reached safe limit {self._safe_limit}mV")
                    break
            else:
                # Test failed - record and stop (Req 1.3)
                failed_value = test_value
                if core_index not in self._failed_values:
                    self._failed_values[core_index] = []
                self._failed_values[core_index].append(test_value)
                logger.info(f"Core {core_index}: {test_value}mV FAILED - {result.error}")
                
                # Restore last stable value (Req 1.3)
                restore_values = self._build_apply_values(core_index, max_stable)
                await self._ryzenadj.apply_values_async(restore_values)
                break
        
        # Update core results
        self._core_results[core_index] = max_stable
        
        # Calculate quality tier and recommended value
        tier = QualityTier.from_value(max_stable)
        recommended = self._calculate_recommended(max_stable, config.safety_margin)
        
        return CoreResult(
            core_index=core_index,
            max_stable=max_stable,
            recommended=recommended,
            quality_tier=tier.value,
            iterations=iterations,
            failed_value=failed_value
        )
    
    async def start(
        self,
        config: Optional[IronSeekerConfig] = None,
        initial_values: Optional[List[int]] = None
    ) -> IronSeekerResult:
        """Start the Iron Seeker per-core optimization.
        
        Args:
            config: Configuration for the session (uses defaults if None)
            initial_values: Initial undervolt values (defaults to [0,0,0,0])
            
        Returns:
            IronSeekerResult with per-core results
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, 3.4
        """
        if self._running:
            logger.warning("Iron Seeker already running")
            return IronSeekerResult(aborted=True)
        
        self._running = True
        self._cancelled = False
        self._config = config or IronSeekerConfig()
        self._start_time = time.time()
        self._test_durations = []
        
        # Initialize tracking
        self._initial_values = initial_values or [0, 0, 0, 0]
        self._core_results = [0, 0, 0, 0]
        self._failed_values = {}
        
        recovered = False
        start_core = 0
        start_value = 0
        
        # Check for recovery state (don't restore values here, we'll apply during testing)
        recovery_state = self.check_recovery(restore_values=False)
        if recovery_state is not None and recovery_state.active:
            logger.info(f"Recovering from crash at core {recovery_state.current_core}, "
                       f"value {recovery_state.current_value}")
            recovered = True
            
            # Restore previous progress
            self._core_results = recovery_state.core_results.copy()
            self._failed_values = {int(k): v.copy() for k, v in recovery_state.failed_values.items()}
            
            # Mark crashed value as failed
            crashed_core = recovery_state.current_core
            crashed_value = recovery_state.current_value
            if crashed_core not in self._failed_values:
                self._failed_values[crashed_core] = []
            self._failed_values[crashed_core].append(crashed_value)
            
            # Emit recovery event (Req 3.4)
            await self._emit_recovery(
                crashed_core=crashed_core,
                crashed_value=crashed_value,
                restored_values=self._core_results.copy()
            )
            
            # Continue from next value or next core
            start_core = crashed_core
            start_value = crashed_value - self._config.step_size
            
            # If we've gone past the limit, move to next core
            if start_value < self._safe_limit:
                start_core += 1
                start_value = 0
        
        results: List[CoreResult] = []
        
        try:
            # Test each core sequentially (Req 1.1)
            for core_index in range(start_core, NUM_CORES):
                if self._cancelled:
                    logger.info("Iron Seeker cancelled")
                    break
                
                # Determine starting value for this core
                core_start_value = start_value if core_index == start_core else 0
                
                logger.info(f"Starting test for core {core_index} from {core_start_value}mV")
                
                core_result = await self._test_core(
                    core_index,
                    self._config,
                    core_start_value
                )
                results.append(core_result)
                
                # Emit core completion event (Req 5.2)
                await self._emit_core_complete(core_result)
                
                logger.info(
                    f"Core {core_index} complete: max_stable={core_result.max_stable}mV, "
                    f"tier={core_result.quality_tier}"
                )
            
            # Add results for cores that were already completed (from recovery)
            if recovered and start_core > 0:
                for core_index in range(start_core):
                    # Create result from recovered data
                    max_stable = self._core_results[core_index]
                    tier = QualityTier.from_value(max_stable)
                    recommended = self._calculate_recommended(max_stable, self._config.safety_margin)
                    failed = self._failed_values.get(core_index, [None])[-1] if core_index in self._failed_values else None
                    
                    results.insert(core_index, CoreResult(
                        core_index=core_index,
                        max_stable=max_stable,
                        recommended=recommended,
                        quality_tier=tier.value,
                        iterations=0,  # Unknown from recovery
                        failed_value=failed
                    ))
            
            # If cancelled, restore initial values (Req 3.5)
            if self._cancelled:
                logger.info(f"Restoring initial values after cancellation: {self._initial_values}")
                try:
                    await self._ryzenadj.apply_values_async(self._initial_values)
                except Exception as e:
                    logger.error(f"Failed to restore initial values on cancellation: {e}")
            
        finally:
            # Clear state file on completion (Req 3.5)
            self._safety.clear_iron_seeker_state()
            self._running = False
        
        duration = time.time() - self._start_time
        
        final_result = IronSeekerResult(
            cores=results,
            duration=duration,
            recovered=recovered,
            aborted=self._cancelled
        )
        
        # Emit completion event (Req 5.3)
        await self._emit_complete(final_result)
        
        return final_result


async def load_iron_seeker_preset(
    preset: IronSeekerPreset,
    ryzenadj: "RyzenadjWrapper"
) -> tuple[bool, Optional[str]]:
    """Load and apply an Iron Seeker preset.
    
    Applies the per-core undervolt values from the preset to the CPU
    using ryzenadj.
    
    Args:
        preset: IronSeekerPreset to load
        ryzenadj: RyzenadjWrapper for applying values
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        
    Requirements: 8.3
    """
    # Validate preset before applying
    errors = preset.validate()
    if errors:
        error_msg = f"Invalid preset: {', '.join(errors)}"
        logger.error(error_msg)
        return False, error_msg
    
    # Apply the per-core values
    logger.info(f"Loading Iron Seeker preset '{preset.name}' with values: {preset.values}")
    
    success, error = await ryzenadj.apply_values_async(preset.values)
    
    if success:
        logger.info(f"Successfully loaded preset '{preset.name}'")
    else:
        logger.error(f"Failed to load preset '{preset.name}': {error}")
    
    return success, error


def load_iron_seeker_preset_sync(
    preset: IronSeekerPreset,
    ryzenadj: "RyzenadjWrapper"
) -> tuple[bool, Optional[str]]:
    """Load and apply an Iron Seeker preset (synchronous version).
    
    Applies the per-core undervolt values from the preset to the CPU
    using ryzenadj.
    
    Args:
        preset: IronSeekerPreset to load
        ryzenadj: RyzenadjWrapper for applying values
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        
    Requirements: 8.3
    """
    # Validate preset before applying
    errors = preset.validate()
    if errors:
        error_msg = f"Invalid preset: {', '.join(errors)}"
        logger.error(error_msg)
        return False, error_msg
    
    # Apply the per-core values
    logger.info(f"Loading Iron Seeker preset '{preset.name}' with values: {preset.values}")
    
    success, error = ryzenadj.apply_values(preset.values)
    
    if success:
        logger.info(f"Successfully loaded preset '{preset.name}'")
    else:
        logger.error(f"Failed to load preset '{preset.name}': {error}")
    
    return success, error
