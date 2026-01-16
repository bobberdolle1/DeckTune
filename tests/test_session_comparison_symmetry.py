"""Property tests for session comparison symmetry.

**Feature: decktune-3.1-reliability-ux, Property 15: Session comparison symmetry**
**Validates: Requirements 8.6**

Property 15: Session comparison symmetry
For any two sessions A and B, compare_sessions(A, B) and compare_sessions(B, A) 
SHALL produce inverse diff values.
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from backend.core.session_manager import (
    Session, SessionMetrics, SessionManager, TelemetrySampleData
)


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


# Strategy for valid temperature values
valid_temperature = st.floats(min_value=30.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for valid power values
valid_power = st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False)


@st.composite
def session_with_samples(draw, index: int = 0):
    """Generate a session with random samples."""
    num_samples = draw(st.integers(min_value=1, max_value=20))
    base_time = 1700000000.0 + (index * 10000)
    
    samples = []
    for i in range(num_samples):
        samples.append(TelemetrySampleData(
            timestamp=base_time + i,
            temperature_c=draw(valid_temperature),
            power_w=draw(valid_power)
        ))
    
    return samples


class TestSessionComparisonSymmetry:
    """Property 15: Session comparison symmetry
    
    For any two sessions A and B, compare_sessions(A, B) and compare_sessions(B, A) 
    SHALL produce inverse diff values.
    
    **Feature: decktune-3.1-reliability-ux, Property 15: Session comparison symmetry**
    **Validates: Requirements 8.6**
    """

    @given(
        samples1=session_with_samples(index=0),
        samples2=session_with_samples(index=1)
    )
    @settings(max_examples=100)
    def test_comparison_produces_inverse_diffs(self, samples1, samples2):
        """compare_sessions(A, B) and compare_sessions(B, A) produce inverse diffs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create first session
            session1 = manager.start_session(game_name="Game_1")
            for sample in samples1:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            manager.end_session(session1.id)
            
            # Create second session
            session2 = manager.start_session(game_name="Game_2")
            for sample in samples2:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            manager.end_session(session2.id)
            
            # Compare A to B
            result_ab = manager.compare_sessions(session1.id, session2.id)
            # Compare B to A
            result_ba = manager.compare_sessions(session2.id, session1.id)
            
            assert result_ab is not None, "Comparison A->B should succeed"
            assert result_ba is not None, "Comparison B->A should succeed"
            
            diff_ab = result_ab["diff"]
            diff_ba = result_ba["diff"]
            
            # Check that diffs are inverse (sum to zero)
            for key in diff_ab.keys():
                sum_diff = diff_ab[key] + diff_ba[key]
                assert abs(sum_diff) < 0.0001, \
                    f"Diff for {key} should be inverse: {diff_ab[key]} + {diff_ba[key]} = {sum_diff}"

    @given(
        samples1=session_with_samples(index=0),
        samples2=session_with_samples(index=1)
    )
    @settings(max_examples=100)
    def test_diff_sign_is_correct(self, samples1, samples2):
        """Diff values have correct sign (session1 - session2)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create first session
            session1 = manager.start_session(game_name="Game_1")
            for sample in samples1:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            manager.end_session(session1.id)
            
            # Create second session
            session2 = manager.start_session(game_name="Game_2")
            for sample in samples2:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            manager.end_session(session2.id)
            
            # Get sessions to check metrics
            s1 = manager.get_session(session1.id)
            s2 = manager.get_session(session2.id)
            
            # Compare
            result = manager.compare_sessions(session1.id, session2.id)
            
            assert result is not None
            diff = result["diff"]
            
            # Verify diff is session1 - session2
            expected_avg_temp_diff = s1.metrics.avg_temperature_c - s2.metrics.avg_temperature_c
            assert abs(diff["avg_temperature_c"] - expected_avg_temp_diff) < 0.0001, \
                f"avg_temperature_c diff should be {expected_avg_temp_diff}, got {diff['avg_temperature_c']}"

    @given(samples=session_with_samples(index=0))
    @settings(max_examples=100)
    def test_self_comparison_has_zero_diff(self, samples):
        """Comparing a session to itself produces zero diffs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create session
            session = manager.start_session(game_name="Game_1")
            for sample in samples:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            manager.end_session(session.id)
            
            # Compare session to itself
            result = manager.compare_sessions(session.id, session.id)
            
            assert result is not None
            diff = result["diff"]
            
            # All diffs should be zero
            for key, value in diff.items():
                assert abs(value) < 0.0001, \
                    f"Self-comparison diff for {key} should be 0, got {value}"

    def test_comparison_with_missing_session_returns_none(self):
        """Comparing with non-existent session returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create one session
            session = manager.start_session(game_name="Game_1")
            manager.add_sample(temperature_c=70.0, power_w=15.0)
            manager.end_session(session.id)
            
            # Compare with non-existent session
            result = manager.compare_sessions(session.id, "non-existent-id")
            
            assert result is None, "Comparison with missing session should return None"
