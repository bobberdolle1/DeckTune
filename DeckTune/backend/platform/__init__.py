"""Platform module - Steam Deck model detection and capabilities."""

from .detect import PlatformInfo, detect_platform, redetect_platform, _map_product_name_to_platform
from .caps import (
    PLATFORM_LIMITS,
    get_platform_limits,
    get_safe_limit,
    get_absolute_limit,
    get_default_step,
)
from .cache import CachedPlatform, PlatformCache

__all__ = [
    "PlatformInfo",
    "detect_platform",
    "redetect_platform",
    "_map_product_name_to_platform",
    "PLATFORM_LIMITS",
    "get_platform_limits",
    "get_safe_limit",
    "get_absolute_limit",
    "get_default_step",
    "CachedPlatform",
    "PlatformCache",
]
