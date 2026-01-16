"""Platform detection for Steam Deck models."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DMI_PRODUCT_NAME_PATH = "/sys/devices/virtual/dmi/id/product_name"

# Module-level cache instance (initialized lazily)
_platform_cache: Optional["PlatformCache"] = None


@dataclass
class PlatformInfo:
    """Information about the detected Steam Deck platform."""
    model: str           # "Jupiter", "Galileo", or "Unknown"
    variant: str         # "LCD", "OLED", or "UNKNOWN"
    safe_limit: int      # Maximum safe undervolt (-30, -35, or -25)
    detected: bool       # True if successfully detected


def _read_dmi_product_name(path: str = DMI_PRODUCT_NAME_PATH) -> Optional[str]:
    """Read product name from DMI sysfs.
    
    Args:
        path: Path to DMI product_name file
        
    Returns:
        Product name string or None if read fails
    """
    try:
        return Path(path).read_text().strip()
    except (OSError, IOError) as e:
        logger.warning(f"Failed to read DMI product name from {path}: {e}")
        return None


def _map_product_name_to_platform(product_name: Optional[str]) -> PlatformInfo:
    """Map DMI product name to platform info.
    
    Args:
        product_name: Raw product name string from DMI
        
    Returns:
        PlatformInfo based on product name mapping
    """
    if product_name is None:
        return PlatformInfo(
            model="Unknown",
            variant="UNKNOWN",
            safe_limit=-25,
            detected=False
        )
    
    # Check for Jupiter (LCD Steam Deck)
    if "Jupiter" in product_name:
        return PlatformInfo(
            model="Jupiter",
            variant="LCD",
            safe_limit=-30,
            detected=True
        )
    
    # Check for Galileo (OLED Steam Deck)
    if "Galileo" in product_name:
        return PlatformInfo(
            model="Galileo",
            variant="OLED",
            safe_limit=-35,
            detected=True
        )
    
    # Unknown device - use conservative limits
    logger.warning(f"Unknown device product name: {product_name}, using conservative limits")
    return PlatformInfo(
        model="Unknown",
        variant="UNKNOWN",
        safe_limit=-25,
        detected=False
    )


def _detect_platform_fresh(dmi_path: str = DMI_PRODUCT_NAME_PATH) -> PlatformInfo:
    """Perform fresh platform detection from DMI.
    
    Args:
        dmi_path: Path to DMI product_name file (for testing)
        
    Returns:
        PlatformInfo with detected platform details
    """
    product_name = _read_dmi_product_name(dmi_path)
    return _map_product_name_to_platform(product_name)


def detect_platform(
    dmi_path: str = DMI_PRODUCT_NAME_PATH,
    cache_dir: Optional[Path] = None,
    use_cache: bool = True
) -> PlatformInfo:
    """Detect Steam Deck model from DMI info with caching.
    
    Checks cache first for faster startup. If cache is valid (< 30 days old),
    returns cached result. Otherwise performs fresh detection and updates cache.
    
    Reads /sys/devices/virtual/dmi/id/product_name
    - "Jupiter" -> LCD, limit -30
    - "Galileo" -> OLED, limit -35
    - Unknown -> Conservative limit -25
    
    Args:
        dmi_path: Path to DMI product_name file (for testing)
        cache_dir: Directory for cache file (for testing)
        use_cache: Whether to use caching (default True)
        
    Returns:
        PlatformInfo with detected platform details
        
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 3.1, 3.2
    """
    global _platform_cache
    
    if use_cache:
        # Import here to avoid circular imports
        from .cache import PlatformCache
        
        # Initialize or reuse cache
        if _platform_cache is None or cache_dir is not None:
            _platform_cache = PlatformCache(cache_dir=cache_dir)
        
        # Try to load from cache
        cached_platform = _platform_cache.load()
        if cached_platform is not None:
            logger.info(f"Using cached platform: {cached_platform.model} ({cached_platform.variant})")
            return cached_platform
    
    # Perform fresh detection
    platform = _detect_platform_fresh(dmi_path)
    
    # Save to cache if detection was successful and caching is enabled
    if use_cache and platform.detected and _platform_cache is not None:
        _platform_cache.save(platform)
    
    return platform


def redetect_platform(
    dmi_path: str = DMI_PRODUCT_NAME_PATH,
    cache_dir: Optional[Path] = None
) -> PlatformInfo:
    """Force fresh platform detection, clearing any cached data.
    
    Clears the cache and performs fresh DMI detection.
    
    Args:
        dmi_path: Path to DMI product_name file (for testing)
        cache_dir: Directory for cache file (for testing)
        
    Returns:
        PlatformInfo with freshly detected platform details
        
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 3.4
    """
    global _platform_cache
    
    # Import here to avoid circular imports
    from .cache import PlatformCache
    
    # Initialize or reuse cache
    if _platform_cache is None or cache_dir is not None:
        _platform_cache = PlatformCache(cache_dir=cache_dir)
    
    # Clear existing cache
    _platform_cache.clear()
    logger.info("Platform cache cleared, performing fresh detection")
    
    # Perform fresh detection
    platform = _detect_platform_fresh(dmi_path)
    
    # Save to cache if detection was successful
    if platform.detected:
        _platform_cache.save(platform)
    
    return platform
