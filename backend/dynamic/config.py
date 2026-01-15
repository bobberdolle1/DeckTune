"""Configuration dataclasses for dynamic mode.

This module provides type-safe configuration structures for gymdeck3 dynamic mode,
including validation logic and serialization support.

Feature: dynamic-mode-refactor
Validates: Requirements 7.1, 10.1

# Configuration Hierarchy

- `DynamicConfig`: Top-level configuration for the entire dynamic mode system
  - `CoreConfig`: Per-core configuration (4 cores for Steam Deck)
    - min_mv, max_mv: Undervolt bounds in millivolts
    - threshold: Load percentage threshold for strategy decisions
    - custom_curve: Optional user-defined load-to-undervolt mapping

# Validation

All configuration classes provide `validate()` methods that return a list of
error messages. Empty list indicates valid configuration.

# Simple Mode

Simple mode allows users to control all cores with a single slider value.
When enabled, the `simple_value` is applied to all cores, overriding
individual core configurations.

# Expert Mode

Expert mode removes safety limits, allowing undervolt values from 0 to -100mV
instead of the normal safe range (0 to -35mV for OLED, -30mV for LCD).

# Example

```python
from backend.dynamic.config import DynamicConfig, CoreConfig

# Create a balanced configuration
config = DynamicConfig(
    strategy="balanced",
    sample_interval_ms=100,
    cores=[
        CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
        CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
        CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
        CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
    ],
    hysteresis_percent=5.0,
    expert_mode=False,
)

# Validate before use
errors = config.validate()
if errors:
    print(f"Invalid config: {errors}")
else:
    print("Config is valid!")
```
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Valid strategy names
VALID_STRATEGIES = ("conservative", "balanced", "aggressive", "custom")

# Sample interval bounds (milliseconds)
MIN_SAMPLE_INTERVAL_MS = 10
MAX_SAMPLE_INTERVAL_MS = 5000

# Hysteresis bounds (percent)
MIN_HYSTERESIS_PERCENT = 1.0
MAX_HYSTERESIS_PERCENT = 20.0

# Undervolt bounds (millivolts)
SAFE_UNDERVOLT_MIN = -35  # Most aggressive safe value (OLED)
SAFE_UNDERVOLT_MAX = 0    # No undervolt
EXPERT_UNDERVOLT_MIN = -100  # Expert mode allows deeper undervolt


@dataclass
class CoreConfig:
    """Configuration for a single CPU core.
    
    Attributes:
        min_mv: Minimum (less aggressive) undervolt value in mV
        max_mv: Maximum (more aggressive) undervolt value in mV
        threshold: Load threshold percentage for strategy switching
        custom_curve: Optional list of (load%, undervolt_mv) points for custom strategy
    """
    min_mv: int = -20
    max_mv: int = -35
    threshold: float = 50.0
    custom_curve: Optional[List[Tuple[float, int]]] = None
    
    def validate(self, expert_mode: bool = False) -> List[str]:
        """Validate core configuration.
        
        Args:
            expert_mode: If True, allow extended undervolt range
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Determine undervolt limits based on mode
        min_limit = EXPERT_UNDERVOLT_MIN if expert_mode else SAFE_UNDERVOLT_MIN
        
        # Validate min_mv (less aggressive, closer to 0)
        if self.min_mv > SAFE_UNDERVOLT_MAX:
            errors.append(f"min_mv ({self.min_mv}) must be <= {SAFE_UNDERVOLT_MAX}")
        if self.min_mv < min_limit:
            errors.append(f"min_mv ({self.min_mv}) must be >= {min_limit}")
            
        # Validate max_mv (more aggressive, more negative)
        if self.max_mv > SAFE_UNDERVOLT_MAX:
            errors.append(f"max_mv ({self.max_mv}) must be <= {SAFE_UNDERVOLT_MAX}")
        if self.max_mv < min_limit:
            errors.append(f"max_mv ({self.max_mv}) must be >= {min_limit}")
            
        # max_mv should be more negative (more aggressive) than min_mv
        if self.max_mv > self.min_mv:
            errors.append(f"max_mv ({self.max_mv}) must be <= min_mv ({self.min_mv})")
            
        # Validate threshold
        if not 0.0 <= self.threshold <= 100.0:
            errors.append(f"threshold ({self.threshold}) must be in range [0, 100]")
            
        # Validate custom curve if present
        if self.custom_curve is not None:
            if len(self.custom_curve) < 2:
                errors.append("custom_curve must have at least 2 points")
            else:
                prev_load = -1.0
                for i, (load, mv) in enumerate(self.custom_curve):
                    if not 0.0 <= load <= 100.0:
                        errors.append(f"custom_curve[{i}] load ({load}) must be in [0, 100]")
                    if load <= prev_load:
                        errors.append(f"custom_curve[{i}] load must be strictly increasing")
                    if mv > SAFE_UNDERVOLT_MAX or mv < min_limit:
                        errors.append(f"custom_curve[{i}] mv ({mv}) out of range")
                    prev_load = load
                    
        return errors
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "min_mv": self.min_mv,
            "max_mv": self.max_mv,
            "threshold": self.threshold,
            "custom_curve": self.custom_curve,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CoreConfig":
        """Create CoreConfig from dictionary."""
        custom_curve = data.get("custom_curve")
        if custom_curve is not None:
            # Convert list of lists to list of tuples
            custom_curve = [tuple(point) for point in custom_curve]
        return cls(
            min_mv=data.get("min_mv", -20),
            max_mv=data.get("max_mv", -35),
            threshold=data.get("threshold", 50.0),
            custom_curve=custom_curve,
        )


@dataclass
class DynamicConfig:
    """Configuration for dynamic mode operation.
    
    Attributes:
        strategy: Adaptation strategy name
        sample_interval_ms: CPU load sampling interval in milliseconds
        cores: Per-core configuration list
        hysteresis_percent: Dead-band margin for load changes
        status_interval_ms: JSON status output interval in milliseconds
        expert_mode: If True, allow extended undervolt range
        simple_mode: If True, single value applies to all cores
        simple_value: The single undervolt value used in simple mode (mV)
    """
    strategy: str = "balanced"
    sample_interval_ms: int = 100
    cores: List[CoreConfig] = field(default_factory=lambda: [CoreConfig() for _ in range(4)])
    hysteresis_percent: float = 5.0
    status_interval_ms: int = 1000
    expert_mode: bool = False
    simple_mode: bool = False
    simple_value: int = -25
    
    def validate(self) -> List[str]:
        """Validate the entire configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate strategy
        if self.strategy not in VALID_STRATEGIES:
            errors.append(f"strategy '{self.strategy}' must be one of {VALID_STRATEGIES}")
            
        # Validate sample interval
        if not MIN_SAMPLE_INTERVAL_MS <= self.sample_interval_ms <= MAX_SAMPLE_INTERVAL_MS:
            errors.append(
                f"sample_interval_ms ({self.sample_interval_ms}) must be in "
                f"range [{MIN_SAMPLE_INTERVAL_MS}, {MAX_SAMPLE_INTERVAL_MS}]"
            )
            
        # Validate hysteresis
        if not MIN_HYSTERESIS_PERCENT <= self.hysteresis_percent <= MAX_HYSTERESIS_PERCENT:
            errors.append(
                f"hysteresis_percent ({self.hysteresis_percent}) must be in "
                f"range [{MIN_HYSTERESIS_PERCENT}, {MAX_HYSTERESIS_PERCENT}]"
            )
            
        # Validate status interval
        if self.status_interval_ms < 100:
            errors.append(f"status_interval_ms ({self.status_interval_ms}) must be >= 100")
        if self.status_interval_ms > 10000:
            errors.append(f"status_interval_ms ({self.status_interval_ms}) must be <= 10000")
        
        # Validate simple_mode and simple_value
        if self.simple_mode:
            min_limit = EXPERT_UNDERVOLT_MIN if self.expert_mode else SAFE_UNDERVOLT_MIN
            if self.simple_value > SAFE_UNDERVOLT_MAX:
                errors.append(f"simple_value ({self.simple_value}) must be <= {SAFE_UNDERVOLT_MAX}")
            if self.simple_value < min_limit:
                errors.append(f"simple_value ({self.simple_value}) must be >= {min_limit}")
            
        # Validate cores
        if len(self.cores) != 4:
            errors.append(f"cores must have exactly 4 entries, got {len(self.cores)}")
        else:
            for i, core in enumerate(self.cores):
                core_errors = core.validate(self.expert_mode)
                for err in core_errors:
                    errors.append(f"cores[{i}]: {err}")
                    
        # Custom strategy requires custom curves
        if self.strategy == "custom":
            for i, core in enumerate(self.cores):
                if core.custom_curve is None:
                    errors.append(f"cores[{i}]: custom strategy requires custom_curve")
                    
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0
    
    def get_effective_core_values(self) -> List[int]:
        """Get the effective undervolt values for all cores.
        
        In simple_mode, returns the simple_value for all 4 cores.
        Otherwise, returns the max_mv from each core's config.
        
        Returns:
            List of 4 undervolt values in mV
            
        Requirements: 14.3 - Simple Mode Value Propagation
        """
        if self.simple_mode:
            # In simple mode, all cores get the same value
            return [self.simple_value] * 4
        else:
            # In per-core mode, use each core's max_mv
            return [core.max_mv for core in self.cores]
    
    def apply_simple_value_to_cores(self) -> None:
        """Apply the simple_value to all cores' min_mv and max_mv.
        
        This is used when switching from simple mode to per-core mode,
        or when simple_mode is active and we need to sync core configs.
        
        Requirements: 14.5 - When switching from Simple to per-core mode,
        the system SHALL copy current value to all cores.
        """
        for core in self.cores:
            core.min_mv = self.simple_value
            core.max_mv = self.simple_value
    
    def calculate_simple_value_from_cores(self) -> int:
        """Calculate simple_value as average of current core values.
        
        Used when switching from per-core to simple mode.
        
        Returns:
            Average of all cores' max_mv values (rounded)
            
        Requirements: 14.4 - When switching from per-core to Simple Mode,
        the system SHALL use average of current values.
        """
        if not self.cores:
            return -25  # Default
        total = sum(core.max_mv for core in self.cores)
        return round(total / len(self.cores))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "strategy": self.strategy,
            "sample_interval_ms": self.sample_interval_ms,
            "cores": [core.to_dict() for core in self.cores],
            "hysteresis_percent": self.hysteresis_percent,
            "status_interval_ms": self.status_interval_ms,
            "expert_mode": self.expert_mode,
            "simple_mode": self.simple_mode,
            "simple_value": self.simple_value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DynamicConfig":
        """Create DynamicConfig from dictionary."""
        cores_data = data.get("cores", [])
        cores = [CoreConfig.from_dict(c) for c in cores_data]
        # Ensure we have exactly 4 cores
        while len(cores) < 4:
            cores.append(CoreConfig())
        cores = cores[:4]
        
        return cls(
            strategy=data.get("strategy", "balanced"),
            sample_interval_ms=data.get("sample_interval_ms", 100),
            cores=cores,
            hysteresis_percent=data.get("hysteresis_percent", 5.0),
            status_interval_ms=data.get("status_interval_ms", 1000),
            expert_mode=data.get("expert_mode", False),
            simple_mode=data.get("simple_mode", False),
            simple_value=data.get("simple_value", -25),
        )


@dataclass
class DynamicStatus:
    """Status information from gymdeck3.
    
    Attributes:
        running: Whether gymdeck3 is currently running
        load: Per-core CPU load percentages
        values: Per-core applied undervolt values
        strategy: Current strategy name
        uptime_ms: Time since gymdeck3 started in milliseconds
        error: Error message if any
    """
    running: bool = False
    load: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    values: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    strategy: str = ""
    uptime_ms: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "running": self.running,
            "load": self.load,
            "values": self.values,
            "strategy": self.strategy,
            "uptime_ms": self.uptime_ms,
            "error": self.error,
        }
    
    @classmethod
    def from_json_line(cls, data: dict, running: bool = True) -> "DynamicStatus":
        """Create DynamicStatus from gymdeck3 JSON output line."""
        msg_type = data.get("type", "")
        
        if msg_type == "status":
            return cls(
                running=running,
                load=data.get("load", [0.0, 0.0, 0.0, 0.0]),
                values=data.get("values", [0, 0, 0, 0]),
                strategy=data.get("strategy", ""),
                uptime_ms=data.get("uptime_ms", 0),
                error=None,
            )
        elif msg_type == "error":
            return cls(
                running=running,
                error=data.get("message", "Unknown error"),
            )
        else:
            return cls(running=running)
