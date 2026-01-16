"""Property tests for telemetry buffer circular behavior.

**Feature: decktune-3.1-reliability-ux, Property 3: Telemetry buffer circular behavior**
**Validates: Requirements 2.5**

Property 3: Telemetry buffer circular behavior
For any sequence of telemetry samples added to the buffer, the buffer length 
SHALL never exceed 300 samples, and adding a sample when full SHALL remove 
the oldest sample.
"""

import pytest
from hypothesis import given, strategies as st, settings
import time

from backend.core.telemetry import TelemetrySample, TelemetryManager


# Strategy for valid temperature values (typical CPU range)
valid_temperature = st.floats(min_value=30.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for valid power values (typical APU range)
valid_power = st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False)

# Strategy for valid load percentage
valid_load = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)


@st.composite
def telemetry_sample(draw, index: int = 0):
    """Generate a valid TelemetrySample."""
    base_time = 1700000000.0  # Fixed base timestamp for reproducibility
    return TelemetrySample(
        timestamp=base_time + index,
        temperature_c=draw(valid_temperature),
        power_w=draw(valid_power),
        load_percent=draw(valid_load)
    )


class TestTelemetryBufferCircularBehavior:
    """Property 3: Telemetry buffer circular behavior
    
    For any sequence of telemetry samples added to the buffer, the buffer length 
    SHALL never exceed 300 samples, and adding a sample when full SHALL remove 
    the oldest sample.
    
    **Feature: decktune-3.1-reliability-ux, Property 3: Telemetry buffer circular behavior**
    **Validates: Requirements 2.5**
    """

    @given(num_samples=st.integers(min_value=1, max_value=500))
    @settings(max_examples=100)
    def test_buffer_never_exceeds_limit(self, num_samples: int):
        """Buffer length never exceeds 300 samples."""
        manager = TelemetryManager()
        base_time = 1700000000.0
        
        # Add N samples
        for i in range(num_samples):
            sample = TelemetrySample(
                timestamp=base_time + i,
                temperature_c=70.0,
                power_w=15.0,
                load_percent=50.0
            )
            manager.record_sample(sample)
        
        assert len(manager) <= TelemetryManager.BUFFER_SIZE, \
            f"Buffer length {len(manager)} exceeds limit {TelemetryManager.BUFFER_SIZE}"

    @given(num_samples=st.integers(min_value=301, max_value=500))
    @settings(max_examples=100)
    def test_oldest_removed_when_full(self, num_samples: int):
        """Oldest sample is removed when buffer is full (circular behavior)."""
        manager = TelemetryManager()
        base_time = 1700000000.0
        
        # Add N samples with unique timestamps
        for i in range(num_samples):
            sample = TelemetrySample(
                timestamp=base_time + i,
                temperature_c=70.0 + (i % 10),  # Vary temp for tracking
                power_w=15.0,
                load_percent=50.0
            )
            manager.record_sample(sample)
        
        samples = manager.get_all()
        
        # Should have exactly BUFFER_SIZE entries
        assert len(samples) == TelemetryManager.BUFFER_SIZE, \
            f"Expected {TelemetryManager.BUFFER_SIZE} samples, got {len(samples)}"
        
        # First sample should be the (N - BUFFER_SIZE)th sample
        expected_first_timestamp = base_time + (num_samples - TelemetryManager.BUFFER_SIZE)
        
        assert samples[0].timestamp == expected_first_timestamp, \
            f"First sample timestamp should be {expected_first_timestamp}, got {samples[0].timestamp}"

    @given(num_samples=st.integers(min_value=1, max_value=300))
    @settings(max_examples=100)
    def test_buffer_under_limit_not_truncated(self, num_samples: int):
        """Buffer with <= 300 samples is not truncated."""
        manager = TelemetryManager()
        base_time = 1700000000.0
        
        # Add N samples where N <= 300
        for i in range(num_samples):
            sample = TelemetrySample(
                timestamp=base_time + i,
                temperature_c=70.0,
                power_w=15.0,
                load_percent=50.0
            )
            manager.record_sample(sample)
        
        assert len(manager) == num_samples, \
            f"Expected {num_samples} samples, got {len(manager)}"

    @given(num_samples=st.integers(min_value=301, max_value=500))
    @settings(max_examples=100)
    def test_insertion_order_preserved(self, num_samples: int):
        """Samples are stored in insertion order (oldest first)."""
        manager = TelemetryManager()
        base_time = 1700000000.0
        
        # Add N samples
        for i in range(num_samples):
            sample = TelemetrySample(
                timestamp=base_time + i,
                temperature_c=70.0,
                power_w=15.0,
                load_percent=50.0
            )
            manager.record_sample(sample)
        
        samples = manager.get_all()
        
        # Verify timestamps are in ascending order
        expected_start = num_samples - TelemetryManager.BUFFER_SIZE
        for i, sample in enumerate(samples):
            expected_timestamp = base_time + expected_start + i
            assert sample.timestamp == expected_timestamp, \
                f"Sample {i} should have timestamp {expected_timestamp}, got {sample.timestamp}"

    def test_buffer_size_is_300(self):
        """Buffer size is 300 samples (5 minutes at 1Hz)."""
        assert TelemetryManager.BUFFER_SIZE == 300, \
            f"Buffer size should be 300, got {TelemetryManager.BUFFER_SIZE}"
