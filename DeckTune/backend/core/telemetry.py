"""Real-time telemetry buffer for temperature and power data.

This module provides telemetry collection and buffering for DeckTune.
It records temperature, power, and load samples at 1-second intervals
and maintains a circular buffer for the last 5 minutes of data.

Feature: decktune-3.1-reliability-ux
Validates: Requirements 2.1, 2.2, 2.5
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class TelemetrySample:
    """Single telemetry sample with temperature, power, and load data.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 2.1, 2.2
    """
    timestamp: float  # Unix timestamp
    temperature_c: float  # CPU temperature in Celsius
    power_w: float  # Power consumption in Watts
    load_percent: float  # CPU load percentage (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetrySample":
        """Create TelemetrySample from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            temperature_c=data["temperature_c"],
            power_w=data["power_w"],
            load_percent=data["load_percent"]
        )


class TelemetryManager:
    """Manages real-time telemetry collection with circular buffer.
    
    Collects temperature, power, and load samples at 1-second intervals
    and maintains a circular buffer limited to 300 samples (5 minutes).
    
    Feature: decktune-3.1-reliability-ux, Property 3: Telemetry buffer circular behavior
    Validates: Requirements 2.1, 2.2, 2.5
    """
    
    BUFFER_SIZE = 300  # 5 minutes at 1Hz
    SAMPLE_INTERVAL = 1.0  # seconds
    
    def __init__(self):
        """Initialize the telemetry manager with empty buffer."""
        self._buffer: deque = deque(maxlen=self.BUFFER_SIZE)
    
    def record_sample(self, sample: TelemetrySample) -> None:
        """Record a telemetry sample to the buffer.
        
        When the buffer is full, the oldest sample is automatically
        removed (circular buffer behavior via deque maxlen).
        
        Args:
            sample: TelemetrySample to record
            
        Feature: decktune-3.1-reliability-ux, Property 3: Telemetry buffer circular behavior
        Validates: Requirements 2.1, 2.2, 2.5
        """
        self._buffer.append(sample)
        logger.debug(
            f"Recorded telemetry: temp={sample.temperature_c:.1f}°C, "
            f"power={sample.power_w:.1f}W, load={sample.load_percent:.1f}%"
        )
    
    def get_recent(self, seconds: int = 60) -> List[TelemetrySample]:
        """Get recent telemetry samples within the specified time window.
        
        Args:
            seconds: Number of seconds of data to retrieve (default 60)
            
        Returns:
            List of TelemetrySample within the time window, oldest first
            
        Validates: Requirements 2.3, 2.4
        """
        if not self._buffer:
            return []
        
        cutoff_time = time.time() - seconds
        return [
            sample for sample in self._buffer
            if sample.timestamp >= cutoff_time
        ]
    
    def get_all(self) -> List[TelemetrySample]:
        """Get all telemetry samples in the buffer.
        
        Returns:
            List of all TelemetrySample in buffer, oldest first
            
        Validates: Requirements 2.5
        """
        return list(self._buffer)
    
    def clear(self) -> None:
        """Clear all samples from the buffer."""
        self._buffer.clear()
        logger.debug("Telemetry buffer cleared")
    
    def __len__(self) -> int:
        """Return the current number of samples in the buffer."""
        return len(self._buffer)
