"""Property tests for session metrics calculation.

**Feature: decktune-3.1-reliability-ux, Property 7: Session metrics calculation**
**Validates: Requirements 8.3**

Property 7: Session metrics calculation
For any completed session with N samples, the calculated metrics SHALL satisfy: 
min_temp ≤ avg_temp ≤ max_temp, and duration_sec equals (end_time - start_time).
"""

import pytest
import tempfile
import time
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
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


# Strategy for valid temperature values (typical CPU range)
valid_temperature = st.floats(min_value=30.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for valid power values (typical APU range)
valid_power = st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False)


@st.composite
def telemetry_samples(draw, min_samples: int = 1, max_samples: int = 100):
    """Generate a list of telemetry samples."""
    num_samples = draw(st.integers(min_value=min_samples, max_value=max_samples))
    base_time = 1700000000.0
    
    samples = []
    for i in range(num_samples):
        samples.append(TelemetrySampleData(
            timestamp=base_time + i,
            temperature_c=draw(valid_temperature),
            power_w=draw(valid_power)
        ))
    return samples


class TestSessionMetricsCalculation:
    """Property 7: Session metrics calculation
    
    For any completed session with N samples, the calculated metrics SHALL satisfy: 
    min_temp ≤ avg_temp ≤ max_temp, and duration_sec equals (end_time - start_time).
    
    **Feature: decktune-3.1-reliability-ux, Property 7: Session metrics calculation**
    **Validates: Requirements 8.3**
    """

    @given(samples=telemetry_samples(min_samples=1, max_samples=100))
    @settings(max_examples=100)
    def test_temperature_ordering_invariant(self, samples):
        """min_temp ≤ avg_temp ≤ max_temp for any session with samples."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Start session and add samples
            session = manager.start_session(game_name="Test Game")
            for sample in samples:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            
            # End session and get metrics
            metrics = manager.end_session(session.id)
            
            assert metrics is not None, "Metrics should be calculated"
            assert metrics.min_temperature_c <= metrics.avg_temperature_c, \
                f"min_temp ({metrics.min_temperature_c}) should be <= avg_temp ({metrics.avg_temperature_c})"
            assert metrics.avg_temperature_c <= metrics.max_temperature_c, \
                f"avg_temp ({metrics.avg_temperature_c}) should be <= max_temp ({metrics.max_temperature_c})"

    @given(duration_sec=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_duration_equals_time_difference(self, duration_sec):
        """duration_sec equals (end_time - start_time)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Create session with known start time
            start_time = datetime(2025, 1, 15, 10, 0, 0)
            end_time = start_time + timedelta(seconds=duration_sec)
            
            # Manually create session with controlled timestamps
            session = Session(
                id=Session.generate_id(),
                start_time=start_time.isoformat(),
                end_time=None,
                game_name="Test Game"
            )
            
            # Add a sample
            session.samples.append(TelemetrySampleData(
                timestamp=time.time(),
                temperature_c=70.0,
                power_w=15.0
            ))
            
            # Set end time
            session.end_time = end_time.isoformat()
            
            # Calculate metrics directly
            metrics = manager._calculate_metrics(session)
            
            # Allow small floating point tolerance
            assert abs(metrics.duration_sec - duration_sec) < 0.001, \
                f"Duration {metrics.duration_sec} should equal {duration_sec}"

    @given(samples=telemetry_samples(min_samples=1, max_samples=100))
    @settings(max_examples=100)
    def test_avg_temperature_is_mean_of_samples(self, samples):
        """avg_temperature_c is the arithmetic mean of sample temperatures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Start session and add samples
            session = manager.start_session(game_name="Test Game")
            for sample in samples:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            
            # End session and get metrics
            metrics = manager.end_session(session.id)
            
            # Calculate expected average
            expected_avg = sum(s.temperature_c for s in samples) / len(samples)
            
            assert abs(metrics.avg_temperature_c - expected_avg) < 0.0001, \
                f"avg_temp ({metrics.avg_temperature_c}) should equal mean ({expected_avg})"

    @given(samples=telemetry_samples(min_samples=1, max_samples=100))
    @settings(max_examples=100)
    def test_min_max_temperature_are_extremes(self, samples):
        """min_temp and max_temp are the actual min/max of sample temperatures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Start session and add samples
            session = manager.start_session(game_name="Test Game")
            for sample in samples:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            
            # End session and get metrics
            metrics = manager.end_session(session.id)
            
            # Calculate expected min/max
            expected_min = min(s.temperature_c for s in samples)
            expected_max = max(s.temperature_c for s in samples)
            
            assert abs(metrics.min_temperature_c - expected_min) < 0.0001, \
                f"min_temp ({metrics.min_temperature_c}) should equal {expected_min}"
            assert abs(metrics.max_temperature_c - expected_max) < 0.0001, \
                f"max_temp ({metrics.max_temperature_c}) should equal {expected_max}"

    @given(samples=telemetry_samples(min_samples=1, max_samples=100))
    @settings(max_examples=100)
    def test_avg_power_is_mean_of_samples(self, samples):
        """avg_power_w is the arithmetic mean of sample power values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Start session and add samples
            session = manager.start_session(game_name="Test Game")
            for sample in samples:
                manager.add_sample(
                    temperature_c=sample.temperature_c,
                    power_w=sample.power_w,
                    timestamp=sample.timestamp
                )
            
            # End session and get metrics
            metrics = manager.end_session(session.id)
            
            # Calculate expected average
            expected_avg = sum(s.power_w for s in samples) / len(samples)
            
            assert abs(metrics.avg_power_w - expected_avg) < 0.0001, \
                f"avg_power ({metrics.avg_power_w}) should equal mean ({expected_avg})"

    def test_empty_session_has_zero_metrics(self):
        """Session with no samples has zero temperature and power metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_manager = MockSettingsManager()
            manager = SessionManager(settings_manager, data_dir=Path(tmpdir))
            
            # Start and immediately end session (no samples)
            session = manager.start_session(game_name="Test Game")
            metrics = manager.end_session(session.id)
            
            assert metrics.avg_temperature_c == 0.0
            assert metrics.min_temperature_c == 0.0
            assert metrics.max_temperature_c == 0.0
            assert metrics.avg_power_w == 0.0
