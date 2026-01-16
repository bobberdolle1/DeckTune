"""Property tests for BlackBox persistence completeness.

Feature: decktune-3.0-automation, Property 10: BlackBox persistence completeness
Validates: Requirements 3.2, 3.4

Property 10: BlackBox persistence completeness
For any persisted BlackBox recording, the file SHALL contain: timestamp, reason,
duration_sec, and samples array with all required fields (temperature_c,
cpu_load_percent, undervolt_values, fan_speed_rpm, fan_pwm).
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from typing import List
import time

from backend.core.blackbox import BlackBox, MetricSample, BlackBoxRecording


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

# Strategy for valid reason strings
valid_reason = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P'), whitelist_characters='_-'),
    min_size=1,
    max_size=50
)


@st.composite
def metric_sample_list(draw, min_size: int = 1, max_size: int = 60):
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


class TestBlackBoxPersistence:
    """Property 10: BlackBox persistence completeness
    
    For any persisted BlackBox recording, the file SHALL contain: timestamp, reason,
    duration_sec, and samples array with all required fields (temperature_c,
    cpu_load_percent, undervolt_values, fan_speed_rpm, fan_pwm).
    
    Feature: decktune-3.0-automation, Property 10: BlackBox persistence completeness
    Validates: Requirements 3.2, 3.4
    """

    @pytest.fixture(autouse=True)
    def setup_temp_storage(self):
        """Create temporary storage directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_persisted_file_contains_timestamp(self, samples: List[MetricSample], reason: str):
        """Persisted file contains timestamp field."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "timestamp" in data, "Recording must contain 'timestamp' field"
        assert isinstance(data["timestamp"], str), "timestamp must be a string"
        assert len(data["timestamp"]) > 0, "timestamp must not be empty"

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_persisted_file_contains_reason(self, samples: List[MetricSample], reason: str):
        """Persisted file contains reason field matching input."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "reason" in data, "Recording must contain 'reason' field"
        assert data["reason"] == reason, f"reason should be '{reason}', got '{data['reason']}'"

    @given(samples=metric_sample_list(min_size=2, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_persisted_file_contains_duration(self, samples: List[MetricSample], reason: str):
        """Persisted file contains duration_sec field."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "duration_sec" in data, "Recording must contain 'duration_sec' field"
        assert isinstance(data["duration_sec"], (int, float)), "duration_sec must be numeric"
        assert data["duration_sec"] >= 0, "duration_sec must be non-negative"

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_persisted_file_contains_samples_array(self, samples: List[MetricSample], reason: str):
        """Persisted file contains samples array."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "samples" in data, "Recording must contain 'samples' field"
        assert isinstance(data["samples"], list), "samples must be a list"
        assert len(data["samples"]) == len(samples), \
            f"samples count should be {len(samples)}, got {len(data['samples'])}"

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_each_sample_contains_required_fields(self, samples: List[MetricSample], reason: str):
        """Each sample in persisted file contains all required fields."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        required_fields = [
            "timestamp",
            "temperature_c",
            "cpu_load_percent",
            "undervolt_values",
            "fan_speed_rpm",
            "fan_pwm"
        ]
        
        for i, sample_data in enumerate(data["samples"]):
            for field in required_fields:
                assert field in sample_data, \
                    f"Sample {i} missing required field '{field}'"

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_sample_values_match_input(self, samples: List[MetricSample], reason: str):
        """Sample values in persisted file match input values."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for i, (original, persisted) in enumerate(zip(samples, data["samples"])):
            assert persisted["timestamp"] == original.timestamp, \
                f"Sample {i}: timestamp mismatch"
            assert persisted["temperature_c"] == original.temperature_c, \
                f"Sample {i}: temperature_c mismatch"
            assert abs(persisted["cpu_load_percent"] - original.cpu_load_percent) < 0.001, \
                f"Sample {i}: cpu_load_percent mismatch"
            assert persisted["undervolt_values"] == original.undervolt_values, \
                f"Sample {i}: undervolt_values mismatch"
            assert persisted["fan_speed_rpm"] == original.fan_speed_rpm, \
                f"Sample {i}: fan_speed_rpm mismatch"
            assert persisted["fan_pwm"] == original.fan_pwm, \
                f"Sample {i}: fan_pwm mismatch"

    @given(samples=metric_sample_list(min_size=1, max_size=60), reason=valid_reason)
    @settings(max_examples=100)
    def test_recording_can_be_loaded_back(self, samples: List[MetricSample], reason: str):
        """Persisted recording can be loaded back correctly."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash(reason)
        assume(filename is not None)
        
        # Load the recording back
        recording = blackbox.load_recording(filename)
        
        assert recording is not None, "Recording should be loadable"
        assert recording.reason == reason, f"Loaded reason should be '{reason}'"
        assert len(recording.samples) == len(samples), \
            f"Loaded samples count should be {len(samples)}"

    def test_empty_buffer_returns_none(self):
        """persist_on_crash returns None for empty buffer."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        result = blackbox.persist_on_crash("test_reason")
        
        assert result is None, "Should return None for empty buffer"

    def test_duration_calculated_correctly(self):
        """Duration is calculated from first to last sample timestamp."""
        blackbox = BlackBox(storage_path=self.temp_dir)
        
        base_time = time.time()
        samples = [
            MetricSample(
                timestamp=base_time,
                temperature_c=50,
                cpu_load_percent=50.0,
                undervolt_values=[-20, -20, -20, -20],
                fan_speed_rpm=3000,
                fan_pwm=128
            ),
            MetricSample(
                timestamp=base_time + 10.0,  # 10 seconds later
                temperature_c=55,
                cpu_load_percent=60.0,
                undervolt_values=[-20, -20, -20, -20],
                fan_speed_rpm=3500,
                fan_pwm=140
            )
        ]
        
        for sample in samples:
            blackbox.record_sample(sample)
        
        filename = blackbox.persist_on_crash("test")
        assert filename is not None
        
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert abs(data["duration_sec"] - 10.0) < 0.001, \
            f"Duration should be ~10.0, got {data['duration_sec']}"
