"""Property tests for crash history FIFO limit.

**Feature: decktune-3.1-reliability-ux, Property 1: Crash history FIFO limit**
**Validates: Requirements 1.5**

Property 1: Crash history FIFO limit
For any sequence of crash records added to the history, the history length 
SHALL never exceed 50 entries, and when the limit is reached, the oldest 
entry SHALL be removed first.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from typing import List

from backend.core.crash_metrics import CrashRecord, CrashMetrics, CrashMetricsManager


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


# Strategy for valid undervolt values (within typical range)
valid_undervolt_value = st.integers(min_value=-100, max_value=0)

# Strategy for list of 4 valid undervolt values
valid_undervolt_values = st.lists(valid_undervolt_value, min_size=4, max_size=4)

# Strategy for recovery reasons
recovery_reason = st.sampled_from([
    "boot_recovery", "watchdog_timeout", "binning_crash", "iron_seeker_crash"
])


@st.composite
def crash_record_data(draw, index: int = 0):
    """Generate data for a crash record."""
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    timestamp = (base_time + timedelta(seconds=index)).isoformat()
    return {
        "timestamp": timestamp,
        "crashed_values": draw(valid_undervolt_values),
        "restored_values": draw(valid_undervolt_values),
        "recovery_reason": draw(recovery_reason)
    }


class TestCrashHistoryFIFOLimit:
    """Property 1: Crash history FIFO limit
    
    For any sequence of crash records added to the history, the history length 
    SHALL never exceed 50 entries, and when the limit is reached, the oldest 
    entry SHALL be removed first.
    
    **Feature: decktune-3.1-reliability-ux, Property 1: Crash history FIFO limit**
    **Validates: Requirements 1.5**
    """

    @given(num_records=st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_history_never_exceeds_limit(self, num_records: int):
        """History length never exceeds 50 entries."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        # Add N crash records
        for i in range(num_records):
            manager.record_crash(
                crashed_values=[-30, -30, -30, -30],
                restored_values=[-20, -20, -20, -20],
                reason=f"test_crash_{i}"
            )
        
        metrics = manager.get_metrics()
        
        assert len(metrics.history) <= CrashMetricsManager.HISTORY_LIMIT, \
            f"History length {len(metrics.history)} exceeds limit {CrashMetricsManager.HISTORY_LIMIT}"

    @given(num_records=st.integers(min_value=51, max_value=100))
    @settings(max_examples=100)
    def test_oldest_removed_when_limit_reached(self, num_records: int):
        """Oldest entry is removed when limit is reached (FIFO)."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        # Add N crash records with unique identifiers
        for i in range(num_records):
            manager.record_crash(
                crashed_values=[-30 - i, -30, -30, -30],  # Use index in values for tracking
                restored_values=[-20, -20, -20, -20],
                reason=f"crash_{i}"
            )
        
        metrics = manager.get_metrics()
        
        # Should have exactly HISTORY_LIMIT entries
        assert len(metrics.history) == CrashMetricsManager.HISTORY_LIMIT, \
            f"Expected {CrashMetricsManager.HISTORY_LIMIT} entries, got {len(metrics.history)}"
        
        # First entry should be the (N - LIMIT)th crash
        expected_first_index = num_records - CrashMetricsManager.HISTORY_LIMIT
        expected_first_reason = f"crash_{expected_first_index}"
        
        assert metrics.history[0].recovery_reason == expected_first_reason, \
            f"First entry should be '{expected_first_reason}', got '{metrics.history[0].recovery_reason}'"

    @given(num_records=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_history_under_limit_not_truncated(self, num_records: int):
        """History with <= 50 entries is not truncated."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        # Add N crash records where N <= 50
        for i in range(num_records):
            manager.record_crash(
                crashed_values=[-30, -30, -30, -30],
                restored_values=[-20, -20, -20, -20],
                reason=f"crash_{i}"
            )
        
        metrics = manager.get_metrics()
        
        assert len(metrics.history) == num_records, \
            f"Expected {num_records} entries, got {len(metrics.history)}"

    @given(num_records=st.integers(min_value=51, max_value=100))
    @settings(max_examples=100)
    def test_insertion_order_preserved(self, num_records: int):
        """Records are stored in insertion order (oldest first)."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        # Add N crash records
        for i in range(num_records):
            manager.record_crash(
                crashed_values=[-30, -30, -30, -30],
                restored_values=[-20, -20, -20, -20],
                reason=f"crash_{i}"
            )
        
        metrics = manager.get_metrics()
        
        # Verify order by checking reasons are sequential
        expected_start = num_records - CrashMetricsManager.HISTORY_LIMIT
        for i, record in enumerate(metrics.history):
            expected_reason = f"crash_{expected_start + i}"
            assert record.recovery_reason == expected_reason, \
                f"Record {i} should have reason '{expected_reason}', got '{record.recovery_reason}'"

    def test_history_limit_is_50(self):
        """History limit is 50 entries."""
        assert CrashMetricsManager.HISTORY_LIMIT == 50, \
            f"History limit should be 50, got {CrashMetricsManager.HISTORY_LIMIT}"
