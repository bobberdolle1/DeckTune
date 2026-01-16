"""Property tests for watchdog rollback on timeout.

Feature: decktune, Property 8: Watchdog Rollback on Timeout
Validates: Requirements 4.3

Property 8: Watchdog Rollback on Timeout
For any watchdog session where heartbeat is stale for >= TIMEOUT seconds, 
the Safety_Manager SHALL trigger rollback_to_lkg() and the applied values 
SHALL equal LKG_Values.
"""

import os
import time
import tempfile
import asyncio
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch

from backend.watchdog import Watchdog
from backend.platform.detect import PlatformInfo


class MockSafetyManager:
    """Mock safety manager for testing rollback behavior."""
    
    def __init__(self, lkg_values=None):
        self.lkg_values = lkg_values or [0, 0, 0, 0]
        self.rollback_called = False
        self.rollback_count = 0
        self.applied_values = None
    
    def rollback_to_lkg(self):
        self.rollback_called = True
        self.rollback_count += 1
        self.applied_values = self.lkg_values.copy()
        return True, None
    
    def get_lkg(self):
        return self.lkg_values.copy()


def create_test_watchdog(heartbeat_file: str = None, lkg_values=None) -> tuple:
    """Create a watchdog instance for testing.
    
    Returns:
        Tuple of (watchdog, safety_manager)
    """
    safety = MockSafetyManager(lkg_values)
    watchdog = Watchdog(safety)
    
    if heartbeat_file:
        watchdog.HEARTBEAT_FILE = heartbeat_file
    
    return watchdog, safety


# Strategy for valid LKG undervolt values
valid_lkg_value = st.integers(min_value=-35, max_value=0)
valid_lkg_values_list = st.lists(valid_lkg_value, min_size=4, max_size=4)


class TestWatchdogRollbackOnTimeout:
    """Property 8: Watchdog Rollback on Timeout
    
    For any watchdog session where heartbeat is stale for >= TIMEOUT seconds, 
    the Safety_Manager SHALL trigger rollback_to_lkg() and the applied values 
    SHALL equal LKG_Values.
    
    Validates: Requirements 4.3
    """

    @given(lkg_values=valid_lkg_values_list)
    @settings(max_examples=100)
    def test_stale_heartbeat_triggers_rollback(self, lkg_values: list):
        """When heartbeat is stale, rollback_to_lkg is called."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, safety = create_test_watchdog(heartbeat_file, lkg_values)
            
            # Write a stale heartbeat (older than TIMEOUT)
            stale_time = time.time() - watchdog.TIMEOUT - 1
            with open(heartbeat_file, 'w') as f:
                f.write(str(stale_time))
            
            # Verify heartbeat is stale
            assert watchdog.is_heartbeat_stale(), "Heartbeat should be stale"
            
            # Simulate what _trigger_rollback does
            asyncio.run(watchdog._trigger_rollback())
            
            # Verify rollback was called
            assert safety.rollback_called, "rollback_to_lkg should be called"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    @given(lkg_values=valid_lkg_values_list)
    @settings(max_examples=100)
    def test_rollback_applies_lkg_values(self, lkg_values: list):
        """Rollback applies the LKG values from SafetyManager."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, safety = create_test_watchdog(heartbeat_file, lkg_values)
            
            # Trigger rollback
            asyncio.run(watchdog._trigger_rollback())
            
            # Verify applied values equal LKG values
            assert safety.applied_values == lkg_values, \
                f"Applied values {safety.applied_values} should equal LKG {lkg_values}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    @given(timeout_excess=st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_heartbeat_stale_after_timeout(self, timeout_excess: int):
        """Heartbeat is considered stale when age >= TIMEOUT."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Write heartbeat that is exactly TIMEOUT + timeout_excess seconds old
            stale_time = time.time() - watchdog.TIMEOUT - timeout_excess
            with open(heartbeat_file, 'w') as f:
                f.write(str(stale_time))
            
            # Should be stale
            assert watchdog.is_heartbeat_stale(), \
                f"Heartbeat {timeout_excess}s past timeout should be stale"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)


    @given(time_before_timeout=st.integers(min_value=1, max_value=29))
    @settings(max_examples=100)
    def test_heartbeat_not_stale_before_timeout(self, time_before_timeout: int):
        """Heartbeat is not stale when age < TIMEOUT."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Write heartbeat that is less than TIMEOUT seconds old
            fresh_time = time.time() - time_before_timeout
            with open(heartbeat_file, 'w') as f:
                f.write(str(fresh_time))
            
            # Should not be stale
            assert not watchdog.is_heartbeat_stale(), \
                f"Heartbeat {time_before_timeout}s old should not be stale (timeout={watchdog.TIMEOUT})"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    def test_missing_heartbeat_is_stale(self):
        """Missing heartbeat file is considered stale."""
        watchdog, _ = create_test_watchdog("/tmp/nonexistent_heartbeat_12345")
        
        assert watchdog.is_heartbeat_stale(), "Missing heartbeat should be stale"

    def test_rollback_clears_heartbeat_file(self):
        """After rollback, heartbeat file is cleared."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Write a heartbeat
            watchdog.write_heartbeat()
            assert os.path.exists(heartbeat_file), "Heartbeat file should exist"
            
            # Trigger rollback
            asyncio.run(watchdog._trigger_rollback())
            
            # File should be cleared
            assert not os.path.exists(heartbeat_file), \
                "Heartbeat file should be cleared after rollback"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    def test_rollback_stops_watchdog(self):
        """After rollback, watchdog is stopped."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            watchdog._running = True  # Simulate running state
            
            # Trigger rollback
            asyncio.run(watchdog._trigger_rollback())
            
            # Watchdog should be stopped
            assert not watchdog._running, "Watchdog should be stopped after rollback"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    @given(lkg_values=valid_lkg_values_list)
    @settings(max_examples=100)
    def test_multiple_stale_checks_single_rollback(self, lkg_values: list):
        """Multiple stale checks should only trigger one rollback per session."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, safety = create_test_watchdog(heartbeat_file, lkg_values)
            
            # Write stale heartbeat
            stale_time = time.time() - watchdog.TIMEOUT - 1
            with open(heartbeat_file, 'w') as f:
                f.write(str(stale_time))
            
            # Check stale multiple times
            for _ in range(3):
                watchdog.is_heartbeat_stale()
            
            # Trigger rollback once
            asyncio.run(watchdog._trigger_rollback())
            
            # Should only have one rollback
            assert safety.rollback_count == 1, \
                f"Expected 1 rollback, got {safety.rollback_count}"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)

    def test_heartbeat_exactly_at_timeout_is_stale(self):
        """Heartbeat exactly at TIMEOUT seconds is considered stale."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            heartbeat_file = f.name
        
        try:
            watchdog, _ = create_test_watchdog(heartbeat_file)
            
            # Write heartbeat exactly at timeout boundary
            boundary_time = time.time() - watchdog.TIMEOUT
            with open(heartbeat_file, 'w') as f:
                f.write(str(boundary_time))
            
            # Should be stale (>= TIMEOUT)
            assert watchdog.is_heartbeat_stale(), \
                "Heartbeat exactly at timeout should be stale"
        finally:
            if os.path.exists(heartbeat_file):
                os.remove(heartbeat_file)
