"""Platform capabilities and limits.

Feature: decktune-critical-fixes
Validates: Requirements 5.1, 5.2, 5.6
"""

from typing import Dict, Any

# Updated platform limits for extended undervolt support
# LCD (Jupiter): safe_limit = -50mV, absolute_limit = -70mV
# OLED (Galileo): safe_limit = -60mV, absolute_limit = -80mV
# UNKNOWN: safe_limit = -30mV (conservative for unknown devices)
PLATFORM_LIMITS: Dict[str, Dict[str, Any]] = {
    "LCD": {
        "safe_limit": -50,       # Updated from -30 (Requirement 5.1)
        "absolute_limit": -70,   # Updated from -40 (Requirement 5.2)
        "default_step": 5
    },
    "OLED": {
        "safe_limit": -60,       # Updated from -35 (Requirement 5.1)
        "absolute_limit": -80,   # Updated from -50 (Requirement 5.2)
        "default_step": 5
    },
    "UNKNOWN": {
        "safe_limit": -30,       # Conservative for unknown devices (Requirement 5.6)
        "absolute_limit": -40,
        "default_step": 5
    }
}


def get_platform_limits(variant: str) -> Dict[str, Any]:
    """Get limits for a specific platform variant.
    
    Args:
        variant: Platform variant ("LCD", "OLED", or "UNKNOWN")
        
    Returns:
        Dictionary with safe_limit, absolute_limit, and default_step
    """
    return PLATFORM_LIMITS.get(variant, PLATFORM_LIMITS["UNKNOWN"])


def get_safe_limit(variant: str) -> int:
    """Get safe undervolt limit for a platform variant.
    
    Args:
        variant: Platform variant ("LCD", "OLED", or "UNKNOWN")
        
    Returns:
        Safe undervolt limit (negative integer)
    """
    return get_platform_limits(variant)["safe_limit"]


def get_absolute_limit(variant: str) -> int:
    """Get absolute undervolt limit for a platform variant.
    
    Args:
        variant: Platform variant ("LCD", "OLED", or "UNKNOWN")
        
    Returns:
        Absolute undervolt limit (negative integer)
    """
    return get_platform_limits(variant)["absolute_limit"]


def get_default_step(variant: str) -> int:
    """Get default step size for autotune on a platform variant.
    
    Args:
        variant: Platform variant ("LCD", "OLED", or "UNKNOWN")
        
    Returns:
        Default step size (positive integer)
    """
    return get_platform_limits(variant)["default_step"]
