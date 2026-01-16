"""Platform detection caching for faster startup.

This module provides caching for platform detection results to avoid
repeated DMI reads on startup.

Feature: decktune-3.1-reliability-ux
Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from .detect import PlatformInfo

logger = logging.getLogger(__name__)


@dataclass
class CachedPlatform:
    """Cached platform detection result.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 3.1
    """
    model: str           # "Jupiter", "Galileo", or "Unknown"
    variant: str         # "LCD", "OLED", or "UNKNOWN"
    safe_limit: int      # Maximum safe undervolt (-30, -35, or -25)
    cached_at: str       # ISO 8601 timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CachedPlatform":
        """Create CachedPlatform from dictionary.
        
        Args:
            data: Dictionary with model, variant, safe_limit, cached_at keys
            
        Returns:
            CachedPlatform instance
            
        Raises:
            KeyError: If required fields are missing
            TypeError: If field types are invalid
        """
        return cls(
            model=str(data["model"]),
            variant=str(data["variant"]),
            safe_limit=int(data["safe_limit"]),
            cached_at=str(data["cached_at"])
        )
    
    def to_platform_info(self) -> PlatformInfo:
        """Convert to PlatformInfo for use in the application.
        
        Returns:
            PlatformInfo with detected=True (since it was cached from a detection)
        """
        return PlatformInfo(
            model=self.model,
            variant=self.variant,
            safe_limit=self.safe_limit,
            detected=True
        )
    
    @classmethod
    def from_platform_info(cls, info: PlatformInfo) -> "CachedPlatform":
        """Create CachedPlatform from PlatformInfo.
        
        Args:
            info: PlatformInfo from fresh detection
            
        Returns:
            CachedPlatform with current timestamp
        """
        return cls(
            model=info.model,
            variant=info.variant,
            safe_limit=info.safe_limit,
            cached_at=datetime.now().isoformat()
        )


class PlatformCache:
    """Caches platform detection results for faster startup.
    
    Feature: decktune-3.1-reliability-ux, Property 4: Platform cache validity
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
    """
    
    CACHE_FILE = "platform_cache.json"
    CACHE_TTL_DAYS = 30
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the platform cache.
        
        Args:
            cache_dir: Directory to store cache file. If None, uses current directory.
        """
        self._cache_dir = cache_dir or Path(".")
        self._cached: Optional[CachedPlatform] = None
    
    @property
    def _cache_path(self) -> Path:
        """Get the full path to the cache file."""
        return self._cache_dir / self.CACHE_FILE
    
    def is_valid(self) -> bool:
        """Check if the cache is valid (exists and not expired).
        
        Returns:
            True if cache exists and is less than 30 days old, False otherwise
            
        Feature: decktune-3.1-reliability-ux, Property 4: Platform cache validity
        Validates: Requirements 3.3
        """
        if self._cached is None:
            return False
        
        try:
            cached_at = datetime.fromisoformat(self._cached.cached_at)
            age = datetime.now() - cached_at
            return age <= timedelta(days=self.CACHE_TTL_DAYS)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid cache timestamp: {e}")
            return False
    
    def load(self) -> Optional[PlatformInfo]:
        """Load cached platform data from file.
        
        Returns:
            PlatformInfo if cache exists and is valid, None otherwise
            
        Feature: decktune-3.1-reliability-ux, Property 5: Platform cache corruption resilience
        Validates: Requirements 3.2, 3.5
        """
        try:
            if not self._cache_path.exists():
                logger.debug("Platform cache file does not exist")
                return None
            
            content = self._cache_path.read_text(encoding='utf-8')
            if not content.strip():
                logger.debug("Platform cache file is empty")
                return None
            
            data = json.loads(content)
            self._cached = CachedPlatform.from_dict(data)
            
            if not self.is_valid():
                logger.info("Platform cache is expired, will re-detect")
                return None
            
            logger.info(f"Loaded platform from cache: {self._cached.model} ({self._cached.variant})")
            return self._cached.to_platform_info()
            
        except json.JSONDecodeError as e:
            logger.warning(f"Platform cache file is corrupted (invalid JSON): {e}")
            return None
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Platform cache file has invalid data: {e}")
            return None
        except (OSError, IOError) as e:
            logger.warning(f"Failed to read platform cache file: {e}")
            return None

    
    def save(self, platform: PlatformInfo) -> None:
        """Save platform detection result to cache.
        
        Args:
            platform: PlatformInfo from fresh detection
            
        Validates: Requirements 3.1
        """
        try:
            self._cached = CachedPlatform.from_platform_info(platform)
            
            # Ensure cache directory exists
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            self._cache_path.write_text(
                json.dumps(self._cached.to_dict(), indent=2),
                encoding='utf-8'
            )
            
            logger.info(f"Saved platform to cache: {platform.model} ({platform.variant})")
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to save platform cache: {e}")
    
    def clear(self) -> None:
        """Clear the cache file and in-memory cache.
        
        Validates: Requirements 3.4
        """
        self._cached = None
        
        try:
            if self._cache_path.exists():
                self._cache_path.unlink()
                logger.info("Platform cache cleared")
        except (OSError, IOError) as e:
            logger.warning(f"Failed to delete platform cache file: {e}")
