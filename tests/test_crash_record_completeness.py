"""Property tests for crash record completeness.

**Feature: decktune-3.1-reliability-ux, Property 2: Crash record completeness**
**Validates: Requirements 1.3**

Property 2: Crash record completeness
For any crash recovery event, the recorded CrashRecord SHALL contain non-null 
values for timestamp, crashed_values (4 integers), restored_values (4 integers), 
and recovery_reason.
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import List

from backend.core.crash_metrics import CrashRecord, CrashMetricsManager


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


class TestCrashRecordCompleteness:
    """Property 2: Crash record completeness
    
    For any crash recovery event, the recorded CrashRecord SHALL contain non-null 
    values for timestamp, crashed_values (4 integers), restored_values (4 integers), 
    and recovery_reason.
    
    **Feature: decktune-3.1-reliability-ux, Property 2: Crash record completeness**
    **Validates: Requirements 1.3**
    """

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_recorded_crash_has_timestamp(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash has non-null timestamp."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.timestamp is not None, "Timestamp should not be None"
        assert isinstance(record.timestamp, str), "Timestamp should be a string"
        assert len(record.timestamp) > 0, "Timestamp should not be empty"

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_recorded_crash_has_crashed_values(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash has crashed_values with 4 integers."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.crashed_values is not None, "crashed_values should not be None"
        assert isinstance(record.crashed_values, list), "crashed_values should be a list"
        assert len(record.crashed_values) == 4, "crashed_values should have 4 elements"
        assert all(isinstance(v, int) for v in record.crashed_values), \
            "All crashed_values should be integers"

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_recorded_crash_has_restored_values(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash has restored_values with 4 integers."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.restored_values is not None, "restored_values should not be None"
        assert isinstance(record.restored_values, list), "restored_values should be a list"
        assert len(record.restored_values) == 4, "restored_values should have 4 elements"
        assert all(isinstance(v, int) for v in record.restored_values), \
            "All restored_values should be integers"

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_recorded_crash_has_recovery_reason(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash has non-null recovery_reason."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.recovery_reason is not None, "recovery_reason should not be None"
        assert isinstance(record.recovery_reason, str), "recovery_reason should be a string"
        assert len(record.recovery_reason) > 0, "recovery_reason should not be empty"

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_recorded_crash_preserves_input_values(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash preserves the input values exactly."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.crashed_values == crashed_values, \
            f"crashed_values mismatch: expected {crashed_values}, got {record.crashed_values}"
        assert record.restored_values == restored_values, \
            f"restored_values mismatch: expected {restored_values}, got {record.restored_values}"
        assert record.recovery_reason == reason, \
            f"recovery_reason mismatch: expected {reason}, got {record.recovery_reason}"

    @given(
        crashed_values=valid_undervolt_values,
        restored_values=valid_undervolt_values,
        reason=recovery_reason
    )
    @settings(max_examples=100)
    def test_crash_record_validates_successfully(
        self,
        crashed_values: List[int],
        restored_values: List[int],
        reason: str
    ):
        """Recorded crash passes validation."""
        settings_manager = MockSettingsManager()
        manager = CrashMetricsManager(settings_manager)
        
        manager.record_crash(
            crashed_values=crashed_values,
            restored_values=restored_values,
            reason=reason
        )
        
        metrics = manager.get_metrics()
        record = metrics.history[-1]
        
        assert record.validate(), "CrashRecord should pass validation"
