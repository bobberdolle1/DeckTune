"""BlackBox recorder for system metrics logging.

This module provides the BlackBox class which maintains a ring buffer of
system metrics for post-mortem analysis after crashes or instability events.

Feature: decktune-3.0-automation
Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""

import json
import logging
import os
from collections import deque
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MetricSample:
    """Single metric sample for BlackBox recording.
    
    Feature: decktune-3.0-automation
    Validates: Requirements 3.1, 3.4
    """
    timestamp: float  # Unix timestamp
    temperature_c: int  # CPU temperature in Celsius
    cpu_load_percent: float  # CPU load percentage (0-100)
    undervolt_values: List[int]  # Per-core undervolt values in mV
    fan_speed_rpm: int  # Fan speed in RPM
    fan_pwm: int  # Fan PWM value (0-255)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricSample":
        """Create MetricSample from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            temperature_c=data["temperature_c"],
            cpu_load_percent=data["cpu_load_percent"],
            undervolt_values=data["undervolt_values"],
            fan_speed_rpm=data["fan_speed_rpm"],
            fan_pwm=data["fan_pwm"]
        )


@dataclass
class BlackBoxRecording:
    """A persisted BlackBox recording.
    
    Feature: decktune-3.0-automation
    Validates: Requirements 3.2, 3.4
    """
    timestamp: str  # ISO timestamp when recording was saved
    reason: str  # Reason for recording (e.g., "watchdog_timeout", "instability")
    duration_sec: float  # Duration of recorded data in seconds
    samples: List[MetricSample] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "reason": self.reason,
            "duration_sec": self.duration_sec,
            "samples": [s.to_dict() for s in self.samples]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlackBoxRecording":
        """Create BlackBoxRecording from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            reason=data["reason"],
            duration_sec=data["duration_sec"],
            samples=[MetricSample.from_dict(s) for s in data.get("samples", [])]
        )


class BlackBox:
    """Ring buffer for system metrics with crash persistence.
    
    Maintains a rolling window of the last 30 seconds of system metrics
    (at 500ms intervals = 60 samples). When a crash or instability is
    detected, the buffer can be persisted to disk for post-mortem analysis.
    
    Feature: decktune-3.0-automation
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
    """
    
    BUFFER_DURATION_SEC = 30
    SAMPLE_INTERVAL_MS = 500
    BUFFER_SIZE = 60  # 30 seconds at 500ms intervals
    MAX_RECORDINGS = 5
    STORAGE_PATH = "/tmp/decktune_blackbox/"
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize BlackBox recorder.
        
        Args:
            storage_path: Optional custom storage path for recordings
        """
        self._buffer: deque[MetricSample] = deque(maxlen=self.BUFFER_SIZE)
        self._storage_path = Path(storage_path or self.STORAGE_PATH)
    
    @property
    def buffer(self) -> deque:
        """Get the internal buffer (for testing)."""
        return self._buffer
    
    @property
    def buffer_size(self) -> int:
        """Get current number of samples in buffer."""
        return len(self._buffer)
    
    def record_sample(self, sample: MetricSample) -> None:
        """Add sample to ring buffer.
        
        When buffer is full, oldest sample is automatically removed (FIFO).
        
        Args:
            sample: MetricSample to record
            
        Feature: decktune-3.0-automation, Property 9: Ring buffer FIFO behavior
        Validates: Requirements 3.1, 3.5
        """
        self._buffer.append(sample)
    
    def get_samples(self) -> List[MetricSample]:
        """Get all samples currently in buffer.
        
        Returns:
            List of MetricSample in insertion order (oldest first)
        """
        return list(self._buffer)
    
    def clear(self) -> None:
        """Clear all samples from buffer."""
        self._buffer.clear()
    
    def persist_on_crash(self, reason: str) -> Optional[str]:
        """Save buffer to timestamped JSON file.
        
        Creates a recording file with all current buffer contents.
        Automatically cleans up old recordings if MAX_RECORDINGS is exceeded.
        
        Args:
            reason: Reason for the crash/instability (e.g., "watchdog_timeout")
            
        Returns:
            Filename of saved recording, or None if save failed
            
        Feature: decktune-3.0-automation, Property 10: BlackBox persistence completeness
        Validates: Requirements 3.2, 3.4
        """
        if not self._buffer:
            logger.warning("BlackBox: No samples to persist")
            return None
        
        # Calculate duration from samples
        samples = list(self._buffer)
        if len(samples) >= 2:
            duration_sec = samples[-1].timestamp - samples[0].timestamp
        else:
            duration_sec = 0.0
        
        # Create recording
        recording = BlackBoxRecording(
            timestamp=datetime.now().isoformat(),
            reason=reason,
            duration_sec=duration_sec,
            samples=samples
        )
        
        # Ensure storage directory exists
        try:
            self._storage_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"BlackBox: Failed to create storage directory: {e}")
            return None
        
        # Generate filename with timestamp
        filename = f"blackbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self._storage_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(recording.to_dict(), f, indent=2)
            logger.info(f"BlackBox: Saved recording to {filepath}")
            
            # Clean up old recordings
            self._cleanup_old_recordings()
            
            return filename
        except (IOError, OSError) as e:
            logger.error(f"BlackBox: Failed to save recording: {e}")
            # Try to delete oldest recording and retry
            if self._delete_oldest_recording():
                try:
                    with open(filepath, 'w') as f:
                        json.dump(recording.to_dict(), f, indent=2)
                    logger.info(f"BlackBox: Saved recording after cleanup to {filepath}")
                    return filename
                except (IOError, OSError) as e2:
                    logger.error(f"BlackBox: Failed to save recording after cleanup: {e2}")
            return None
    
    def _cleanup_old_recordings(self) -> None:
        """Remove old recordings if MAX_RECORDINGS is exceeded."""
        try:
            recordings = self._list_recording_files()
            while len(recordings) > self.MAX_RECORDINGS:
                oldest = recordings.pop(0)  # Remove oldest (first in sorted list)
                filepath = self._storage_path / oldest["filename"]
                try:
                    os.remove(filepath)
                    logger.debug(f"BlackBox: Deleted old recording {oldest['filename']}")
                except OSError as e:
                    logger.warning(f"BlackBox: Failed to delete old recording: {e}")
        except Exception as e:
            logger.warning(f"BlackBox: Error during cleanup: {e}")
    
    def _delete_oldest_recording(self) -> bool:
        """Delete the oldest recording to free space.
        
        Returns:
            True if a recording was deleted, False otherwise
        """
        try:
            recordings = self._list_recording_files()
            if recordings:
                oldest = recordings[0]
                filepath = self._storage_path / oldest["filename"]
                os.remove(filepath)
                logger.info(f"BlackBox: Deleted oldest recording {oldest['filename']}")
                return True
        except Exception as e:
            logger.warning(f"BlackBox: Failed to delete oldest recording: {e}")
        return False
    
    def _list_recording_files(self) -> List[Dict[str, Any]]:
        """List recording files sorted by timestamp (oldest first).
        
        Returns:
            List of dicts with filename and timestamp
        """
        if not self._storage_path.exists():
            return []
        
        recordings = []
        for filepath in self._storage_path.glob("blackbox_*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                recordings.append({
                    "filename": filepath.name,
                    "timestamp": data.get("timestamp", ""),
                    "reason": data.get("reason", "unknown")
                })
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"BlackBox: Failed to read recording {filepath}: {e}")
        
        # Sort by timestamp (oldest first)
        recordings.sort(key=lambda r: r["timestamp"])
        return recordings
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """List last MAX_RECORDINGS with timestamps.
        
        Returns:
            List of dicts with filename, timestamp, and reason (newest first)
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.3
        """
        recordings = self._list_recording_files()
        # Return newest first, limited to MAX_RECORDINGS
        return list(reversed(recordings[-self.MAX_RECORDINGS:]))
    
    def load_recording(self, filename: str) -> Optional[BlackBoxRecording]:
        """Load a specific recording by filename.
        
        Args:
            filename: Name of the recording file
            
        Returns:
            BlackBoxRecording if found and valid, None otherwise
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.3
        """
        filepath = self._storage_path / filename
        
        if not filepath.exists():
            logger.warning(f"BlackBox: Recording not found: {filename}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return BlackBoxRecording.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"BlackBox: Failed to load recording {filename}: {e}")
            return None
