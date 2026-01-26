"""Session history tracking with metrics.

This module provides session tracking for DeckTune gaming sessions.
It records session start/end times, calculates performance metrics,
and maintains a history with archival support.

Feature: decktune-3.1-reliability-ux
Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
"""

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Calculated metrics for a completed session.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 8.3
    """
    duration_sec: float  # Total session duration in seconds
    avg_temperature_c: float  # Average CPU temperature
    min_temperature_c: float  # Minimum CPU temperature
    max_temperature_c: float  # Maximum CPU temperature
    avg_power_w: float  # Average power consumption
    estimated_battery_saved_wh: float  # Estimated battery savings
    undervolt_values: List[int]  # Undervolt values used during session
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMetrics":
        """Create SessionMetrics from dictionary."""
        return cls(
            duration_sec=data["duration_sec"],
            avg_temperature_c=data["avg_temperature_c"],
            min_temperature_c=data["min_temperature_c"],
            max_temperature_c=data["max_temperature_c"],
            avg_power_w=data["avg_power_w"],
            estimated_battery_saved_wh=data["estimated_battery_saved_wh"],
            undervolt_values=data["undervolt_values"]
        )


@dataclass
class TelemetrySampleData:
    """Lightweight telemetry sample for session storage.
    
    Stores only essential fields to minimize storage size.
    """
    timestamp: float  # Unix timestamp
    temperature_c: float  # CPU temperature
    power_w: float  # Power consumption
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetrySampleData":
        """Create TelemetrySampleData from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            temperature_c=data["temperature_c"],
            power_w=data["power_w"]
        )


@dataclass
class Session:
    """Gaming session record with metrics.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 8.1, 8.3
    """
    id: str  # UUID
    start_time: str  # ISO 8601 format
    end_time: Optional[str] = None  # ISO 8601 format, None if session is active
    game_name: Optional[str] = None
    app_id: Optional[int] = None
    metrics: Optional[SessionMetrics] = None
    samples: List[TelemetrySampleData] = field(default_factory=list)
    
    @staticmethod
    def generate_id() -> str:
        """Generate a new UUID for session ID."""
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "game_name": self.game_name,
            "app_id": self.app_id,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "samples": [s.to_dict() for s in self.samples]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        metrics = None
        if data.get("metrics"):
            metrics = SessionMetrics.from_dict(data["metrics"])
        
        samples = []
        for s in data.get("samples", []):
            samples.append(TelemetrySampleData.from_dict(s))
        
        return cls(
            id=data["id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            game_name=data.get("game_name"),
            app_id=data.get("app_id"),
            metrics=metrics,
            samples=samples
        )
    
    def is_active(self) -> bool:
        """Check if session is still active (not ended)."""
        return self.end_time is None


class SessionManager:
    """Manages gaming session history with metrics.
    
    Tracks gaming sessions, calculates performance metrics,
    and maintains a history with archival support for older sessions.
    
    Feature: decktune-3.1-reliability-ux
    Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
    """
    
    ACTIVE_LIMIT = 100  # Max sessions in active storage
    HISTORY_DEFAULT_LIMIT = 30  # Default limit for get_history()
    ARCHIVE_FILE = "sessions_archive.json"
    SETTINGS_KEY = "sessions"
    
    # Baseline power for battery savings calculation (typical Steam Deck idle)
    BASELINE_POWER_W = 25.0
    
    def __init__(self, settings_manager, data_dir: Optional[Path] = None):
        """Initialize the session manager.
        
        Args:
            settings_manager: Decky settings manager instance
            data_dir: Directory for archive files (defaults to settings dir)
        """
        self.settings_manager = settings_manager
        self._data_dir = data_dir or Path.home() / ".config" / "decktune"
        self._sessions: List[Session] = self._load_from_settings()
        self._active_session: Optional[Session] = None
    
    def _load_from_settings(self) -> List[Session]:
        """Load sessions from settings.
        
        Returns:
            List of sessions loaded from settings, or empty list if not found
        """
        try:
            data = self.settings_manager.get_setting(self.SETTINGS_KEY)
            if data is None:
                return []
            return [Session.from_dict(s) for s in data]
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Failed to load sessions from settings: {e}")
            return []
    
    def _save_to_settings(self) -> None:
        """Persist sessions to settings."""
        try:
            self.settings_manager.save_setting(
                self.SETTINGS_KEY,
                [s.to_dict() for s in self._sessions]
            )
        except Exception as e:
            logger.error(f"Failed to save sessions to settings: {e}")
    
    def start_session(
        self,
        game_name: Optional[str] = None,
        app_id: Optional[int] = None
    ) -> Session:
        """Start a new gaming session.
        
        Args:
            game_name: Optional name of the game being played
            app_id: Optional Steam app ID
            
        Returns:
            The newly created Session
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.1
        """
        # End any existing active session first
        if self._active_session is not None:
            logger.warning("Ending previous active session before starting new one")
            self.end_session(self._active_session.id)
        
        session = Session(
            id=Session.generate_id(),
            start_time=datetime.now().isoformat(),
            game_name=game_name,
            app_id=app_id
        )
        
        self._active_session = session
        logger.info(f"Started session {session.id} for game: {game_name or 'Unknown'}")
        
        return session
    
    def add_sample(
        self,
        temperature_c: float,
        power_w: float,
        timestamp: Optional[float] = None
    ) -> None:
        """Add a telemetry sample to the active session.
        
        Args:
            temperature_c: CPU temperature in Celsius
            power_w: Power consumption in Watts
            timestamp: Unix timestamp (defaults to current time)
        """
        if self._active_session is None:
            return
        
        import time
        sample = TelemetrySampleData(
            timestamp=timestamp or time.time(),
            temperature_c=temperature_c,
            power_w=power_w
        )
        self._active_session.samples.append(sample)
    
    def end_session(self, session_id: str) -> Optional[SessionMetrics]:
        """End a session and calculate metrics.
        
        Args:
            session_id: ID of the session to end
            
        Returns:
            Calculated SessionMetrics, or None if session not found
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.2, 8.3
        """
        if self._active_session is None or self._active_session.id != session_id:
            logger.warning(f"Session {session_id} not found or not active")
            return None
        
        session = self._active_session
        session.end_time = datetime.now().isoformat()
        
        # Calculate metrics from samples
        metrics = self._calculate_metrics(session)
        session.metrics = metrics
        
        # Add to history
        self._sessions.append(session)
        self._active_session = None
        
        # Archive if over limit
        self.archive_old_sessions()
        
        # Persist
        self._save_to_settings()
        
        logger.info(f"Ended session {session_id}, duration: {metrics.duration_sec:.1f}s")
        
        return metrics
    
    def _calculate_metrics(self, session: Session) -> SessionMetrics:
        """Calculate metrics from session samples.
        
        Args:
            session: Session to calculate metrics for
            
        Returns:
            Calculated SessionMetrics
            
        Feature: decktune-3.1-reliability-ux, Property 7: Session metrics calculation
        Validates: Requirements 8.3
        """
        # Calculate duration from timestamps
        start_dt = datetime.fromisoformat(session.start_time)
        end_dt = datetime.fromisoformat(session.end_time) if session.end_time else datetime.now()
        duration_sec = (end_dt - start_dt).total_seconds()
        
        # Default values if no samples
        if not session.samples:
            return SessionMetrics(
                duration_sec=duration_sec,
                avg_temperature_c=0.0,
                min_temperature_c=0.0,
                max_temperature_c=0.0,
                avg_power_w=0.0,
                estimated_battery_saved_wh=0.0,
                undervolt_values=[0, 0, 0, 0]
            )
        
        # Calculate temperature stats
        temps = [s.temperature_c for s in session.samples]
        avg_temp = sum(temps) / len(temps)
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Calculate power stats
        powers = [s.power_w for s in session.samples]
        avg_power = sum(powers) / len(powers)
        
        # Estimate battery savings (baseline - actual) * duration in hours
        # Assumes undervolting reduces power consumption
        duration_hours = duration_sec / 3600.0
        power_saved_w = max(0, self.BASELINE_POWER_W - avg_power)
        battery_saved_wh = power_saved_w * duration_hours
        
        return SessionMetrics(
            duration_sec=duration_sec,
            avg_temperature_c=avg_temp,
            min_temperature_c=min_temp,
            max_temperature_c=max_temp,
            avg_power_w=avg_power,
            estimated_battery_saved_wh=battery_saved_wh,
            undervolt_values=[0, 0, 0, 0]  # Will be set by caller if available
        )
    
    def get_history(self, limit: int = 30) -> List[Session]:
        """Get recent session history.
        
        Args:
            limit: Maximum number of sessions to return (default 30)
            
        Returns:
            List of sessions, most recent first
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.4
        """
        # Return most recent sessions first
        return list(reversed(self._sessions[-limit:]))
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a specific session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session if found, None otherwise
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.5
        """
        # Check active session first
        if self._active_session and self._active_session.id == session_id:
            return self._active_session
        
        # Search history
        for session in self._sessions:
            if session.id == session_id:
                return session
        
        return None
    
    def compare_sessions(self, id1: str, id2: str) -> Optional[Dict[str, Any]]:
        """Compare two sessions and return metric differences.
        
        The diff values are calculated as (session1 - session2), so positive
        values mean session1 is higher. This ensures symmetry: comparing
        (A, B) and (B, A) produces inverse diff values.
        
        Args:
            id1: ID of first session
            id2: ID of second session
            
        Returns:
            Dictionary with comparison data, or None if sessions not found
            
        Feature: decktune-3.1-reliability-ux, Property 15: Session comparison symmetry
        Validates: Requirements 8.6
        """
        session1 = self.get_session(id1)
        session2 = self.get_session(id2)
        
        if session1 is None or session2 is None:
            logger.warning(f"Cannot compare: session not found (id1={id1}, id2={id2})")
            return None
        
        if session1.metrics is None or session2.metrics is None:
            logger.warning("Cannot compare: one or both sessions have no metrics")
            return None
        
        m1 = session1.metrics
        m2 = session2.metrics
        
        return {
            "session1": session1.to_dict(),
            "session2": session2.to_dict(),
            "diff": {
                "duration_sec": m1.duration_sec - m2.duration_sec,
                "avg_temperature_c": m1.avg_temperature_c - m2.avg_temperature_c,
                "min_temperature_c": m1.min_temperature_c - m2.min_temperature_c,
                "max_temperature_c": m1.max_temperature_c - m2.max_temperature_c,
                "avg_power_w": m1.avg_power_w - m2.avg_power_w,
                "estimated_battery_saved_wh": m1.estimated_battery_saved_wh - m2.estimated_battery_saved_wh,
            }
        }
    
    def archive_old_sessions(self) -> int:
        """Archive sessions when active storage exceeds limit.
        
        Moves oldest sessions to archive file when count exceeds ACTIVE_LIMIT.
        
        Returns:
            Number of sessions archived
            
        Feature: decktune-3.1-reliability-ux, Property 6: Session history limit
        Validates: Requirements 8.7
        """
        if len(self._sessions) <= self.ACTIVE_LIMIT:
            return 0
        
        # Calculate how many to archive
        to_archive_count = len(self._sessions) - self.ACTIVE_LIMIT
        sessions_to_archive = self._sessions[:to_archive_count]
        
        # Keep only the most recent sessions
        self._sessions = self._sessions[to_archive_count:]
        
        # Append to archive file
        archive_path = self._data_dir / self.ARCHIVE_FILE
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing archive
            existing_archive = []
            if archive_path.exists():
                try:
                    with open(archive_path, 'r') as f:
                        existing_archive = json.load(f)
                except (json.JSONDecodeError, IOError):
                    logger.warning("Failed to load existing archive, starting fresh")
            
            # Append new sessions
            existing_archive.extend([s.to_dict() for s in sessions_to_archive])
            
            # Save archive
            with open(archive_path, 'w') as f:
                json.dump(existing_archive, f)
            
            logger.info(f"Archived {to_archive_count} sessions to {archive_path}")
            
        except Exception as e:
            logger.error(f"Failed to archive sessions: {e}")
            # Put sessions back if archive failed
            self._sessions = sessions_to_archive + self._sessions
            return 0
        
        return to_archive_count
    
    def get_active_session(self) -> Optional[Session]:
        """Get the currently active session.
        
        Returns:
            Active session if one exists, None otherwise
        """
        return self._active_session
    
    def export_for_diagnostics(self) -> Dict[str, Any]:
        """Export session history for diagnostics archive.
        
        Returns:
            Dictionary containing session history summary
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.8
        """
        return {
            "session_count": len(self._sessions),
            "active_session": self._active_session.to_dict() if self._active_session else None,
            "recent_sessions": [s.to_dict() for s in self.get_history(10)]
        }
