"""Property tests for session history limit.

**Feature: decktune-3.1-reliability-ux, Property 6: Session history limit**
**Validates: Requirements 8.7**

Property 6: Session history limit
For any sequence of sessions, the active session list SHALL never exceed 
100 entries, and excess sessions SHALL be moved to archive.
"""

import pytest
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from backend.core.session_manager import Session, SessionMetrics, SessionManager


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class TestSessionHistoryLimit:
    """Property 6: Session history limit
    
    For any sequence of sessions, the active session list SHALL never exceed 
    100 entries, and excess sessions SHALL be moved to archive.
    
    **Feature: decktune-3.1-reliability-ux, Property 6: Session history limit**
    **Validates: Requirements 8.7**
    """

    @given(num_sessions=st.integers(min_value=1, max_value=150))
    @settings(max_examples=100)
    def test_active_sessions_never_exceed_limit(self, num_sessions: int):
        """Active session list never exceeds 100 entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create and end N sessions
            for i in range(num_sessions):
                session = manager.start_session(game_name=f"Game_{i}")
                # Add a sample so metrics can be calculated
                manager.add_sample(temperature_c=70.0, power_w=15.0)
                manager.end_session(session.id)
            
            assert len(manager._sessions) <= SessionManager.ACTIVE_LIMIT, \
                f"Active sessions {len(manager._sessions)} exceeds limit {SessionManager.ACTIVE_LIMIT}"

    @given(num_sessions=st.integers(min_value=101, max_value=150))
    @settings(max_examples=100)
    def test_excess_sessions_archived(self, num_sessions: int):
        """Excess sessions are moved to archive when limit exceeded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            data_dir = Path(tmpdir)
            manager = SessionManager(settings_manager, data_dir=data_dir)
            
            # Create and end N sessions
            for i in range(num_sessions):
                session = manager.start_session(game_name=f"Game_{i}")
                manager.add_sample(temperature_c=70.0, power_w=15.0)
                manager.end_session(session.id)
            
            # Check archive file exists and contains archived sessions
            archive_path = data_dir / SessionManager.ARCHIVE_FILE
            assert archive_path.exists(), "Archive file should exist"
            
            with open(archive_path, 'r') as f:
                archived = json.load(f)
            
            expected_archived = num_sessions - SessionManager.ACTIVE_LIMIT
            assert len(archived) == expected_archived, \
                f"Expected {expected_archived} archived sessions, got {len(archived)}"

    @given(num_sessions=st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_sessions_under_limit_not_archived(self, num_sessions: int):
        """Sessions under limit are not archived."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            data_dir = Path(tmpdir)
            manager = SessionManager(settings_manager, data_dir=data_dir)
            
            # Create and end N sessions where N <= 100
            for i in range(num_sessions):
                session = manager.start_session(game_name=f"Game_{i}")
                manager.add_sample(temperature_c=70.0, power_w=15.0)
                manager.end_session(session.id)
            
            # All sessions should be in active storage
            assert len(manager._sessions) == num_sessions, \
                f"Expected {num_sessions} active sessions, got {len(manager._sessions)}"
            
            # Archive file should not exist
            archive_path = data_dir / SessionManager.ARCHIVE_FILE
            assert not archive_path.exists(), "Archive file should not exist when under limit"

    @given(num_sessions=st.integers(min_value=101, max_value=150))
    @settings(max_examples=100)
    def test_oldest_sessions_archived_first(self, num_sessions: int):
        """Oldest sessions are archived first (FIFO)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            data_dir = Path(tmpdir)
            manager = SessionManager(settings_manager, data_dir=data_dir)
            
            # Create and end N sessions with unique game names
            for i in range(num_sessions):
                session = manager.start_session(game_name=f"Game_{i}")
                manager.add_sample(temperature_c=70.0, power_w=15.0)
                manager.end_session(session.id)
            
            # Check that active sessions are the most recent ones
            expected_first_active = num_sessions - SessionManager.ACTIVE_LIMIT
            first_active_game = manager._sessions[0].game_name
            assert first_active_game == f"Game_{expected_first_active}", \
                f"First active session should be Game_{expected_first_active}, got {first_active_game}"
            
            # Check that archived sessions are the oldest ones
            archive_path = data_dir / SessionManager.ARCHIVE_FILE
            with open(archive_path, 'r') as f:
                archived = json.load(f)
            
            # First archived should be Game_0
            assert archived[0]["game_name"] == "Game_0", \
                f"First archived session should be Game_0, got {archived[0]['game_name']}"

    def test_active_limit_is_100(self):
        """Active limit is 100 sessions."""
        assert SessionManager.ACTIVE_LIMIT == 100, \
            f"Active limit should be 100, got {SessionManager.ACTIVE_LIMIT}"
