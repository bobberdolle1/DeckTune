"""Property tests for BlackBox ring buffer FIFO behavior.

Feature: decktune-3.0-automation, Property 9: Ring buffer FIFO behavior
Validates: Requirements 3.1, 3.5

Property 9: Ring buffer FIFO behavior
For any BlackBox with buffer capacity C, after inserting N > C samples,
the buffer SHALL contain exactly the last C samples in insertion order.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List
import time

from backend.core.blackbox import BlackBox, MetricSample


# Strategy for valid temperature values (0-100°C)
valid_temperature = st.integers(min_value=0, max_value=100)

# Strategy for valid CPU load (0-100%)
valid_cpu_load = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for valid undervolt values (negative integers, typical range -100 to 0)
valid_undervolt_value = st.integers(min_value=-100, max_value=0)
valid_undervolt_values = st.lists(valid_undervolt_value, min_size=4, max_size=4)

# Strategy for valid fan speed (0-6000 RPM)
valid_fan_speed = st.integers(min_value=0, max_value=6000)

# Strategy for valid PWM (0-255)
valid_pwm = st.integers(min_value=0, max_value=255)


@st.composite
def metric_sample(draw, base_timestamp: float = None):
    """Generate a valid MetricSample."""
    if base_timestamp is None:
        base_timestamp = time.time()
    
    return MetricSample(
        timestamp=base_timestamp + draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)),
        temperature_c=draw(valid_temperature),
        cpu_load_percent=draw(valid_cpu_load),
        undervolt_values=draw(valid_undervolt_values),
        fan_speed_rpm=draw(valid_fan_speed),
        fan_pwm=draw(valid_pwm)
    )


@st.composite
def metric_sample_list(draw, min_size: int = 1, max_size: int = 200):
    """Generate a list of MetricSamples with increasing timestamps."""
    count = draw(st.integers(min_value=min_size, max_value=max_size))
    base_timestamp = time.time()
    samples = []
    
    for i in range(count):
        sample = MetricSample(
            timestamp=base_timestamp + i * 0.5,  # 500ms intervals
            temperature_c=draw(valid_temperature),
            cpu_load_percent=draw(valid_cpu_load),
            undervolt_values=draw(valid_undervolt_values),
            fan_speed_rpm=draw(valid_fan_speed),
            fan_pwm=draw(valid_pwm)
        )
        samples.append(sample)
    
    return samples


class TestBlackBoxFIFO:
    """Property 9: Ring buffer FIFO behavior
    
    For any BlackBox with buffer capacity C, after inserting N > C samples,
    the buffer SHALL contain exactly the last C samples in insertion order.
    
    Feature: decktune-3.0-automation, Property 9: Ring buffer FIFO behavior
    Validates: Requirements 3.1, 3.5
    """

    @given(samples=metric_sample_list(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_buffer_contains_last_c_samples_when_overflow(self, samples: List[MetricSample]):
        """After inserting N > C samples, buffer contains exactly last C samples."""
        blackbox = BlackBox()
        capacity = blackbox.BUFFER_SIZE
        
        # Insert all samples
        for sample in samples:
            blackbox.record_sample(sample)
        
        # Get buffer contents
        buffer_contents = blackbox.get_samples()
        
        # Buffer should contain at most C samples
        assert len(buffer_contents) <= capacity, \
            f"Buffer size {len(buffer_contents)} exceeds capacity {capacity}"
        
        # If we inserted more than capacity, buffer should be full
        if len(samples) >= capacity:
            assert len(buffer_contents) == capacity, \
                f"Buffer should be full ({capacity}), got {len(buffer_contents)}"
            
            # Buffer should contain exactly the last C samples
            expected_samples = samples[-capacity:]
            for i, (actual, expected) in enumerate(zip(buffer_contents, expected_samples)):
                assert actual.timestamp == expected.timestamp, \
                    f"Sample {i}: timestamp mismatch. Expected {expected.timestamp}, got {actual.timestamp}"
        else:
            # Buffer should contain all samples
            assert len(buffer_contents) == len(samples), \
                f"Buffer should contain all {len(samples)} samples, got {len(buffer_contents)}"

    @given(samples=metric_sample_list(min_size=61, max_size=150))
    @settings(max_examples=100)
    def test_oldest_samples_removed_on_overflow(self, samples: List[MetricSample]):
        """Oldest samples are removed when buffer overflows (FIFO)."""
        blackbox = BlackBox()
        capacity = blackbox.BUFFER_SIZE
        
        # Ensure we have more samples than capacity
        assume(len(samples) > capacity)
        
        # Insert all samples
        for sample in samples:
            blackbox.record_sample(sample)
        
        buffer_contents = blackbox.get_samples()
        
        # First sample in buffer should be the (N - C + 1)th inserted sample
        expected_first_index = len(samples) - capacity
        expected_first = samples[expected_first_index]
        
        assert buffer_contents[0].timestamp == expected_first.timestamp, \
            f"First sample should be sample {expected_first_index}, " \
            f"expected timestamp {expected_first.timestamp}, got {buffer_contents[0].timestamp}"

    @given(samples=metric_sample_list(min_size=1, max_size=60))
    @settings(max_examples=100)
    def test_insertion_order_preserved(self, samples: List[MetricSample]):
        """Samples are stored in insertion order."""
        blackbox = BlackBox()
        
        # Insert all samples
        for sample in samples:
            blackbox.record_sample(sample)
        
        buffer_contents = blackbox.get_samples()
        
        # Verify order by checking timestamps are non-decreasing
        for i in range(1, len(buffer_contents)):
            assert buffer_contents[i].timestamp >= buffer_contents[i-1].timestamp, \
                f"Samples not in order: sample {i-1} timestamp {buffer_contents[i-1].timestamp} " \
                f"> sample {i} timestamp {buffer_contents[i].timestamp}"

    @given(samples=metric_sample_list(min_size=1, max_size=60))
    @settings(max_examples=100)
    def test_buffer_size_never_exceeds_capacity(self, samples: List[MetricSample]):
        """Buffer size never exceeds capacity at any point."""
        blackbox = BlackBox()
        capacity = blackbox.BUFFER_SIZE
        
        for sample in samples:
            blackbox.record_sample(sample)
            assert blackbox.buffer_size <= capacity, \
                f"Buffer size {blackbox.buffer_size} exceeds capacity {capacity}"

    def test_buffer_capacity_is_60(self):
        """Buffer capacity is 60 (30 seconds at 500ms intervals)."""
        blackbox = BlackBox()
        assert blackbox.BUFFER_SIZE == 60, \
            f"Buffer size should be 60, got {blackbox.BUFFER_SIZE}"

    def test_empty_buffer_returns_empty_list(self):
        """Empty buffer returns empty list."""
        blackbox = BlackBox()
        assert blackbox.get_samples() == [], \
            "Empty buffer should return empty list"
        assert blackbox.buffer_size == 0, \
            "Empty buffer size should be 0"

    @given(sample=metric_sample())
    @settings(max_examples=100)
    def test_single_sample_stored_correctly(self, sample: MetricSample):
        """Single sample is stored and retrievable."""
        blackbox = BlackBox()
        
        blackbox.record_sample(sample)
        
        buffer_contents = blackbox.get_samples()
        assert len(buffer_contents) == 1, \
            f"Buffer should contain 1 sample, got {len(buffer_contents)}"
        assert buffer_contents[0].timestamp == sample.timestamp, \
            f"Sample timestamp mismatch"

    def test_clear_empties_buffer(self):
        """Clear removes all samples from buffer."""
        blackbox = BlackBox()
        
        # Add some samples
        for i in range(10):
            sample = MetricSample(
                timestamp=time.time() + i,
                temperature_c=50,
                cpu_load_percent=50.0,
                undervolt_values=[-20, -20, -20, -20],
                fan_speed_rpm=3000,
                fan_pwm=128
            )
            blackbox.record_sample(sample)
        
        assert blackbox.buffer_size > 0, "Buffer should have samples"
        
        blackbox.clear()
        
        assert blackbox.buffer_size == 0, "Buffer should be empty after clear"
        assert blackbox.get_samples() == [], "get_samples should return empty list after clear"
