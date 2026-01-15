"""Platform detection for Steam Deck models."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DMI_PRODUCT_NAME_PATH = "/sys/devices/virtual/dmi/id/product_name"


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


def detect_platform(dmi_path: str = DMI_PRODUCT_NAME_PATH) -> PlatformInfo:
    """Detect Steam Deck model from DMI info.
    
    Reads /sys/devices/virtual/dmi/id/product_name
    - "Jupiter" -> LCD, limit -30
    - "Galileo" -> OLED, limit -35
    - Unknown -> Conservative limit -25
    
    Args:
        dmi_path: Path to DMI product_name file (for testing)
        
    Returns:
        PlatformInfo with detected platform details
    """
    product_name = _read_dmi_product_name(dmi_path)
    return _map_product_name_to_platform(product_name)
