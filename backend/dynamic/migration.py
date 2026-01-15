"""Migration utilities for old dynamic settings format.

This module handles backward compatibility by migrating settings from the
old gymdeck2 format to the new gymdeck3 format. This ensures users don't
lose their configurations when upgrading.

Feature: dynamic-mode-refactor
Validates: Requirements 11.1-11.4

# Migration Overview

The old format used percentage-based values (0-100%) while the new format
uses millivolt values (0 to -35mV for safe mode, 0 to -100mV for expert mode).

## Old Format (gymdeck2)
```json
{
  "strategy": "DEFAULT" | "AGGRESSIVE" | "MANUAL",
  "sample_interval": 50000,  // microseconds
  "cores": [
    {
      "maximumValue": 100,  // percentage (0-100)
      "minimumValue": 0,    // percentage (0-100)
      "threshold": 50,
      "manualPoints": [{"load": 0, "value": 0}, ...]
    }
  ]
}
```

## New Format (gymdeck3)
```json
{
  "strategy": "conservative" | "balanced" | "aggressive" | "custom",
  "sample_interval_ms": 100,  // milliseconds
  "cores": [
    {
      "min_mv": -20,    // millivolts (0 to -35 safe, 0 to -100 expert)
      "max_mv": -35,    // millivolts (more negative = more aggressive)
      "threshold": 50.0,
      "custom_curve": [(0.0, -35), (100.0, 0)]  // optional
    }
  ],
  "hysteresis_percent": 5.0,
  "status_interval_ms": 1000,
  "expert_mode": false
}
```

# Strategy Name Mapping

- `DEFAULT` → `balanced`
- `AGGRESSIVE` → `aggressive`
- `MANUAL` → `custom`
- `conservative` → `DEFAULT` (reverse mapping, no old equivalent)

# Value Conversion

Percentage to millivolts conversion formula:
- `0%` → `0mV` (no undervolt)
- `100%` → `-35mV` (maximum safe undervolt)
- Formula: `mv = -(percent * 35 / 100)`

# Usage Example

```python
from backend.dynamic.migration import migrate_dynamic_settings, is_old_format

# Check if settings need migration
old_settings = load_settings_from_file()
if is_old_format(old_settings):
    # Migrate to new format
    new_config = migrate_dynamic_settings(old_settings)
    save_settings(new_config.to_dict())
```

# Error Handling

If migration fails for any reason, the function returns a default
DynamicConfig with safe settings rather than raising an exception.
This ensures the system remains functional even with corrupted settings.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .config import DynamicConfig, CoreConfig

logger = logging.getLogger(__name__)

# Strategy name mapping from old to new format
STRATEGY_MAP_OLD_TO_NEW = {
    "DEFAULT": "balanced",
    "AGGRESSIVE": "aggressive",
    "MANUAL": "custom",
}

STRATEGY_MAP_NEW_TO_OLD = {
    "balanced": "DEFAULT",
    "aggressive": "AGGRESSIVE",
    "custom": "MANUAL",
    "conservative": "DEFAULT",  # No old equivalent, map to DEFAULT
}


def migrate_dynamic_settings(old_settings: Dict[str, Any]) -> DynamicConfig:
    """Migrate old dynamicSettings format to new DynamicConfig.
    
    Old format:
    {
        "strategy": "DEFAULT" | "AGGRESSIVE" | "MANUAL",
        "sample_interval": 50000,  # microseconds
        "sampleInterval": 50000,   # alternative key
        "cores": [
            {
                "maximumValue": 100,
                "minimumValue": 0,
                "threshold": 0,
                "manualPoints": [{"load": 0, "value": 0}, ...]
            },
            ...
        ]
    }
    
    New format (gymdeck3):
    {
        "strategy": "conservative" | "balanced" | "aggressive" | "custom",
        "sample_interval_ms": 100,  # milliseconds
        "cores": [
            {
                "min_mv": -20,
                "max_mv": -35,
                "threshold": 50.0,
                "custom_curve": [(0.0, 0), (100.0, -35)]
            },
            ...
        ],
        "hysteresis_percent": 5.0,
        "status_interval_ms": 1000,
        "expert_mode": false
    }
    
    Args:
        old_settings: Old format dynamic settings dictionary
        
    Returns:
        New DynamicConfig instance
    """
    if not old_settings:
        logger.warning("Empty old settings, using defaults")
        return DynamicConfig()
    
    try:
        # Migrate strategy name
        old_strategy = old_settings.get("strategy", "DEFAULT")
        new_strategy = STRATEGY_MAP_OLD_TO_NEW.get(old_strategy, "balanced")
        
        # Migrate sample interval (old is in microseconds, new is in milliseconds)
        # Try both possible keys
        old_interval = old_settings.get("sample_interval") or old_settings.get("sampleInterval", 50000)
        new_interval_ms = max(10, min(5000, old_interval // 1000))
        
        # Migrate cores
        old_cores = old_settings.get("cores", [])
        new_cores = []
        
        for i, old_core in enumerate(old_cores[:4]):  # Max 4 cores
            new_core = _migrate_core_config(old_core, new_strategy)
            new_cores.append(new_core)
        
        # Ensure we have exactly 4 cores
        while len(new_cores) < 4:
            new_cores.append(CoreConfig())
        
        config = DynamicConfig(
            strategy=new_strategy,
            sample_interval_ms=new_interval_ms,
            cores=new_cores,
            hysteresis_percent=5.0,  # Default, not in old format
            status_interval_ms=1000,  # Default, not in old format
            expert_mode=False,  # Default, not in old format
        )
        
        logger.info(f"Migrated settings: {old_strategy} -> {new_strategy}")
        return config
        
    except Exception as e:
        logger.error(f"Migration failed: {e}, using defaults")
        return DynamicConfig()


def _migrate_core_config(old_core: Dict[str, Any], strategy: str) -> CoreConfig:
    """Migrate a single core configuration.
    
    Old format uses percentage values (0-100) for undervolt.
    New format uses millivolt values (0 to -100).
    
    Conversion: old_value% -> -(old_value * 0.35) mV (for safe limit -35)
    
    Args:
        old_core: Old core configuration dictionary
        strategy: New strategy name (for custom curve handling)
        
    Returns:
        New CoreConfig instance
    """
    # Get old values (percentages 0-100)
    old_max = old_core.get("maximumValue", old_core.get("maximum_value", 100))
    old_min = old_core.get("minimumValue", old_core.get("minimum_value", 0))
    old_threshold = old_core.get("threshold", 50)
    
    # Convert percentage to millivolts
    # Old: 0% = no undervolt, 100% = max undervolt
    # New: 0 mV = no undervolt, -35 mV = max safe undervolt
    new_min_mv = _percent_to_mv(old_min)  # Less aggressive
    new_max_mv = _percent_to_mv(old_max)  # More aggressive
    
    # Ensure min_mv >= max_mv (min is less negative)
    if new_min_mv < new_max_mv:
        new_min_mv, new_max_mv = new_max_mv, new_min_mv
    
    # Migrate custom curve if present and strategy is custom
    custom_curve = None
    if strategy == "custom":
        old_points = old_core.get("manualPoints", old_core.get("manual_points", []))
        if old_points:
            custom_curve = _migrate_custom_curve(old_points)
        else:
            # Custom strategy requires a curve - create default based on min/max values
            custom_curve = [(0.0, new_max_mv), (100.0, new_min_mv)]
    
    return CoreConfig(
        min_mv=new_min_mv,
        max_mv=new_max_mv,
        threshold=float(old_threshold),
        custom_curve=custom_curve,
    )


def _percent_to_mv(percent: int) -> int:
    """Convert old percentage value to millivolts.
    
    Old format: 0-100 where 100 = maximum undervolt
    New format: 0 to -35 mV (safe limit)
    
    Args:
        percent: Old percentage value (0-100)
        
    Returns:
        Millivolt value (0 to -35)
    """
    # Clamp to valid range
    percent = max(0, min(100, percent))
    # Convert: 0% -> 0mV, 100% -> -35mV
    return -int(percent * 35 / 100)


def _mv_to_percent(mv: int) -> int:
    """Convert millivolts back to percentage.
    
    Args:
        mv: Millivolt value (0 to -35)
        
    Returns:
        Percentage value (0-100)
    """
    # Clamp to valid range
    mv = max(-35, min(0, mv))
    # Convert: 0mV -> 0%, -35mV -> 100%
    return int(abs(mv) * 100 / 35)


def _migrate_custom_curve(old_points: List[Dict[str, Any]]) -> List[Tuple[float, int]]:
    """Migrate custom curve points.
    
    Old format: [{"load": 0, "value": 0}, {"load": 100, "value": 100}]
    New format: [(0.0, 0), (100.0, -35)]
    
    Args:
        old_points: List of old curve points
        
    Returns:
        List of (load%, mv) tuples
    """
    if not old_points:
        # Default curve: linear from 0 to max
        return [(0.0, -35), (100.0, 0)]
    
    new_curve = []
    seen_loads = set()
    
    for point in old_points:
        load = float(point.get("load", 0))
        old_value = point.get("value", 0)
        mv = _percent_to_mv(old_value)
        
        # Skip duplicate loads (keep first occurrence)
        if load in seen_loads:
            continue
        seen_loads.add(load)
        
        new_curve.append((load, mv))
    
    # Sort by load
    new_curve.sort(key=lambda p: p[0])
    
    # Ensure at least 2 points with distinct loads
    if len(new_curve) < 2:
        if len(new_curve) == 1:
            # Add endpoint at opposite end
            if new_curve[0][0] < 50:
                new_curve.append((100.0, 0))
            else:
                new_curve.insert(0, (0.0, -35))
        else:
            new_curve = [(0.0, -35), (100.0, 0)]
    
    return new_curve


def convert_to_old_format(config: DynamicConfig) -> Dict[str, Any]:
    """Convert new DynamicConfig back to old format.
    
    Used for backward compatibility with frontend until it's updated.
    
    Args:
        config: New DynamicConfig instance
        
    Returns:
        Old format dictionary
    """
    old_strategy = STRATEGY_MAP_NEW_TO_OLD.get(config.strategy, "DEFAULT")
    old_interval = config.sample_interval_ms * 1000  # Convert to microseconds
    
    old_cores = []
    for core in config.cores:
        old_core = {
            "maximumValue": _mv_to_percent(core.max_mv),
            "minimumValue": _mv_to_percent(core.min_mv),
            "threshold": int(core.threshold),
            "manualPoints": [],
        }
        
        if core.custom_curve:
            old_core["manualPoints"] = [
                {"load": int(load), "value": _mv_to_percent(mv)}
                for load, mv in core.custom_curve
            ]
        
        old_cores.append(old_core)
    
    return {
        "strategy": old_strategy,
        "sample_interval": old_interval,
        "sampleInterval": old_interval,  # Both keys for compatibility
        "cores": old_cores,
    }


def is_old_format(settings: Dict[str, Any]) -> bool:
    """Check if settings are in old format.
    
    Args:
        settings: Settings dictionary to check
        
    Returns:
        True if old format, False if new format
    """
    if not settings:
        return False
    
    # Old format uses uppercase strategy names
    strategy = settings.get("strategy", "")
    if strategy in ("DEFAULT", "AGGRESSIVE", "MANUAL"):
        return True
    
    # Old format uses sample_interval in microseconds (typically 50000)
    interval = settings.get("sample_interval") or settings.get("sampleInterval", 0)
    if interval > 5000:  # New format max is 5000ms
        return True
    
    # Old format cores have maximumValue/minimumValue
    cores = settings.get("cores", [])
    if cores and "maximumValue" in cores[0]:
        return True
    
    return False
