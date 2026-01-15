"""Platform capabilities and limits."""

from typing import Dict, Any

PLATFORM_LIMITS: Dict[str, Dict[str, Any]] = {
    "LCD": {
        "safe_limit": -30,
        "absolute_limit": -40,
        "default_step": 5
    },
    "OLED": {
        "safe_limit": -35,
        "absolute_limit": -50,
        "default_step": 5
    },
    "UNKNOWN": {
        "safe_limit": -25,
        "absolute_limit": -30,
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
