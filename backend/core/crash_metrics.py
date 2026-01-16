"""Crash recovery metrics tracking.

This module provides crash recovery metrics tracking for DeckTune.
It records crash events, maintains a FIFO history, and exports data
for diagnostics.

Feature: decktune-3.1-reliability-ux
Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
"""

import logging
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CrashRecord:
    """Single crash recovery event record.
    
    Feature: decktune-3.1-reliability-ux, Property 2: Crash record completeness
    Validates: Requirements 1.2, 1.3
    """
    timestamp: str  # ISO 8601 format
    crashed_values: List[int]  # Values that caused crash (4 integers)
    restored_values: List[int]  # LKG values restored (4 integers)
    recovery_reason: str  # "boot_recovery", "watchdog_timeout", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrashRecord":
        """Create CrashRecord from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            crashed_values=data["crashed_values"],
            restored_values=data["restored_values"],
            recovery_reason=data["recovery_reason"]
        )
    
    def validate(self) -> bool:
        """Validate that all required fields are present and valid.
        
        Returns:
            True if record is valid, False otherwise
        """
        if not self.timestamp:
            return False
        if not isinstance(self.crashed_values, list) or len(self.crashed_values) != 4:
            return False
        if not isinstance(self.restored_values, list) or len(self.restored_values) != 4:
            return False
        if not self.recovery_reason:
            return False
        return True


@dataclass
class CrashMetrics:
    """Aggregated crash recovery metrics.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 1.2, 1.3
    """
    total_count: int = 0
    last_crash_date: Optional[str] = None  # ISO 8601 format
    history: List[CrashRecord] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_count": self.total_count,
            "last_crash_date": self.last_crash_date,
            "history": [r.to_dict() for r in self.history]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrashMetrics":
        """Create CrashMetrics from dictionary."""
        history = [CrashRecord.from_dict(r) for r in data.get("history", [])]
        return cls(
            total_count=data.get("total_count", 0),
            last_crash_date=data.get("last_crash_date"),
            history=history
        )


class CrashMetricsManager:
    """Manages crash recovery metrics with FIFO history.
    
    Tracks crash recovery events, maintains a limited history (FIFO),
    and provides export functionality for diagnostics.
    
    Feature: decktune-3.1-reliability-ux, Property 1: Crash history FIFO limit
    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
    """
    
    HISTORY_LIMIT = 50
    SETTINGS_KEY = "crash_metrics"
    
    def __init__(self, settings_manager):
        """Initialize the crash metrics manager.
        
        Args:
            settings_manager: Decky settings manager instance
        """
        self.settings_manager = settings_manager
        self._metrics: CrashMetrics = self._load_from_settings()
    
    def _load_from_settings(self) -> CrashMetrics:
        """Load crash metrics from settings.
        
        Returns:
            CrashMetrics loaded from settings, or empty metrics if not found
        """
        try:
            data = self.settings_manager.getSetting(self.SETTINGS_KEY)
            if data is None:
                return CrashMetrics()
            return CrashMetrics.from_dict(data)
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Failed to load crash metrics from settings: {e}")
            return CrashMetrics()
    
    def _save_to_settings(self) -> None:
        """Persist crash metrics to settings."""
        try:
            self.settings_manager.setSetting(
                self.SETTINGS_KEY,
                self._metrics.to_dict()
            )
        except Exception as e:
            logger.error(f"Failed to save crash metrics to settings: {e}")
    
    def record_crash(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ) -> None:
        """Record a crash recovery event.
        
        Creates a new CrashRecord and adds it to the history.
        Enforces FIFO limit by removing oldest entries when limit is reached.
        
        Args:
            crashed_values: Undervolt values that caused the crash (4 integers)
            restored_values: LKG values that were restored (4 integers)
            reason: Recovery reason (e.g., "boot_recovery", "watchdog_timeout")
            
        Feature: decktune-3.1-reliability-ux, Property 1: Crash history FIFO limit
        Validates: Requirements 1.1, 1.3, 1.5
        """
        timestamp = datetime.now().isoformat()
        
        record = CrashRecord(
            timestamp=timestamp,
            crashed_values=crashed_values.copy(),
            restored_values=restored_values.copy(),
            recovery_reason=reason
        )
        
        # Add to history
        self._metrics.history.append(record)
        
        # Enforce FIFO limit
        while len(self._metrics.history) > self.HISTORY_LIMIT:
            self._metrics.history.pop(0)
        
        # Update aggregate metrics
        self._metrics.total_count += 1
        self._metrics.last_crash_date = timestamp
        
        logger.info(
            f"Recorded crash recovery: reason={reason}, "
            f"crashed={crashed_values}, restored={restored_values}"
        )
        
        # Persist to settings
        self._save_to_settings()
    
    def get_metrics(self) -> CrashMetrics:
        """Get current crash metrics.
        
        Returns:
            CrashMetrics with total count, last crash date, and history
            
        Validates: Requirements 1.2
        """
        return self._metrics
    
    def export_for_diagnostics(self) -> Dict[str, Any]:
        """Export crash metrics for diagnostics archive.
        
        Returns:
            Dictionary containing all crash metrics data
            
        Validates: Requirements 1.4
        """
        return {
            "crash_metrics": self._metrics.to_dict()
        }
