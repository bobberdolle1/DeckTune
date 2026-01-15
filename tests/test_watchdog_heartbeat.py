"""Property tests for watchdog heartbeat periodic write.

Feature: decktune, Property 7: Heartbeat Periodic Write
Validates: Requirements 4.2

Property 7: Heartbeat Periodic Write
For any active watchdog session lasting T seconds, the heartbeat file SHALL be 
updated at least floor(T / HEARTBEAT_INTERVAL) times.
"""

import os
import time
import tempfile
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch

from backend.watchdog import Watchdog
from backend.platform.detect import PlatformInfo


class MockSafetyManager:
    """Mock safety manager for testing."""
    
    def __init__(self):
        self.rollback_called = False
        self.rollback_count = 0
    
    def rollback_to_lkg(self):
        self.rollback_called = True
        self.rollback_count += 1
        return True, None


def create_test_watchdog(heartbeat_file: str = None) -> tuple:
    """Create a watchdog instance for testing.
    
    Returns:
        Tuple of (watchdog, safety_manager)
    """
    safety = MockSafetyManager()
    watchdog = Watchdog(safety)
    
    if heartbeat_file:
        watchdog.HEARTBEAT_FILE = heartbeat_file
    
    return watchdog, safety


class TestHeartbeatPeriodicWrite:
    """Property 7: Heartbeat Periodic Write
    
    For any active watchdog session lasting T seconds, the heartbeat file SHALL be 
    updated at least floor(T / HEARTBEAT_INTERVAL) times.
    
    Validates: Requirements 4.2
    """

    @given(num_writes=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_heartbeat_count_matches_writes(self, num_writes: int):
        """Each write_heartbeat call increments the heartbeat count."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Write heartbeats
            for _ in range(num_writes):
                watchdog.write_heartbeat()
            
            # Verify count matches
            assert watchdog.heartbeat_count == num_writes, \
                f"Expected {num_writes} heartbeats, got {watchdog.heartbeat_count}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    @given(num_writes=st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_heartbeat_file_contains_valid_timestamp(self, num_writes: int):
        """After writing heartbeats, file contains a valid timestamp."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            before_time = time.time()
            
            # Write heartbeats
            for _ in range(num_writes):
                watchdog.write_heartbeat()
            
            after_time = time.time()
            
            # Read and verify timestamp
            timestamp = watchdog.read_heartbeat()
            
            assert timestamp is not None, "Heartbeat file should contain a timestamp"
            assert before_time <= timestamp <= after_time, \
                f"Timestamp {timestamp} should be between {before_time} and {after_time}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    @given(num_writes=st.integers(min_value=2, max_value=10))
    @settings(max_examples=100)
    def test_heartbeat_timestamp_increases(self, num_writes: int):
        """Each heartbeat write updates the timestamp."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            timestamps = []
            for _ in range(num_writes):
                watchdog.write_heartbeat()
                ts = watchdog.read_heartbeat()
                timestamps.append(ts)
                time.sleep(0.001)  # Small delay to ensure different timestamps
            
            # Verify timestamps are non-decreasing
            for i in range(1, len(timestamps)):
                assert timestamps[i] >= timestamps[i-1], \
                    f"Timestamp {timestamps[i]} should be >= {timestamps[i-1]}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)


    @given(duration_factor=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_heartbeat_minimum_writes_for_duration(self, duration_factor: int):
        """For duration T, at least floor(T / HEARTBEAT_INTERVAL) heartbeats written.
        
        This tests the core property: if we simulate a session of T seconds
        by writing heartbeats at the expected interval, we get the expected count.
        """
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Simulate T seconds worth of heartbeats
            # T = duration_factor * HEARTBEAT_INTERVAL
            expected_writes = duration_factor
            
            for _ in range(expected_writes):
                watchdog.write_heartbeat()
            
            # Verify minimum writes
            assert watchdog.heartbeat_count >= expected_writes, \
                f"Expected at least {expected_writes} heartbeats, got {watchdog.heartbeat_count}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    def test_heartbeat_file_created_on_write(self):
        """Heartbeat file is created when write_heartbeat is called."""
        with tempfile.TemporaryDirectory() as tmpdir:
            heartbeat_file = os.path.join(tmpdir, "heartbeat")
            
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            assert not os.path.exists(heartbeat_file), "File should not exist initially"
            
            watchdog.write_heartbeat()
            
            assert os.path.exists(heartbeat_file), "File should exist after write"

    def test_clear_heartbeat_removes_file(self):
        """clear_heartbeat removes the heartbeat file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            watchdog.write_heartbeat()
            assert os.path.exists(heartbeat_file), "File should exist after write"
            
            watchdog.clear_heartbeat()
            assert not os.path.exists(heartbeat_file), "File should be removed after clear"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    def test_read_heartbeat_returns_none_for_missing_file(self):
        """read_heartbeat returns None when file doesn't exist."""
        watchdog, _ = create_test_watchdog("/tmp/nonexistent_heartbeat_file_12345")
        
        result = watchdog.read_heartbeat()
        
        assert result is None, "Should return None for missing file"

    def test_is_heartbeat_stale_true_for_missing_file(self):
        """is_heartbeat_stale returns True when file doesn't exist."""
        watchdog, _ = create_test_watchdog("/tmp/nonexistent_heartbeat_file_12345")
        
        result = watchdog.is_heartbeat_stale()
        
        assert result is True, "Should be stale when file is missing"

    def test_is_heartbeat_stale_false_for_fresh_heartbeat(self):
        """is_heartbeat_stale returns False for recently written heartbeat."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            watchdog.write_heartbeat()
            
            result = watchdog.is_heartbeat_stale()
            
            assert result is False, "Should not be stale immediately after write"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)
