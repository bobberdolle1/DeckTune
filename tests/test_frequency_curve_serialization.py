"""Property tests for frequency curve serialization round-trip.

Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
Validates: Requirements 7.1, 7.2, 7.3

Property 2: Frequency curve serialization round-trip
For any valid frequency curve, serializing to JSON and then deserializing SHALL 
produce an equivalent curve with identical frequency points, voltages, and metadata.
"""

import time
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from backend.tuning.frequency_curve import FrequencyPoint, FrequencyCurve


# Strategies for generating test data
frequency_strategy = st.integers(min_value=400, max_value=3500)
voltage_strategy = st.integers(min_value=-100, max_value=0)
core_id_strategy = st.integers(min_value=0, max_value=7)
test_duration_strategy = st.integers(min_value=10, max_value=120)


def generate_sorted_frequencies(min_freq: int, max_freq: int, count: int):
    """Generate sorted list of unique frequencies."""
    if count < 2:
        count = 2
    step = max(1, (max_freq - min_freq) // (count - 1))
    freqs = []
    current = min_freq
    while len(freqs) < count and current <= max_freq:
        freqs.append(current)
        current += step
    if len(freqs) < 2:
        freqs = [min_freq, max_freq]
    elif freqs[-1] != max_freq:
        freqs[-1] = max_freq
    return freqs


@st.composite
def frequency_curve_strategy(draw):
    """Generate valid frequency curves."""
    core_id = draw(core_id_strategy)
    num_points = draw(st.integers(min_value=1, max_value=15))
    min_freq = draw(st.integers(min_value=400, max_value=2000))
    max_freq = draw(st.integers(min_value=min_freq + 50, max_value=3500))
    
    frequencies = generate_sorted_frequencies(min_freq, max_freq, num_points)
    
    points = []
    for freq in frequencies:
        voltage = draw(voltage_strategy)
        stable = draw(st.booleans())
        test_duration = draw(test_duration_strategy)
        timestamp = time.time() + draw(st.floats(min_value=-1000, max_value=1000))
        
        points.append(FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=voltage,
            stable=stable,
            test_duration=test_duration,
            timestamp=timestamp
        ))
    
    wizard_config = {
        'freq_start': draw(st.integers(min_value=400, max_value=1000)),
        'freq_end': draw(st.integers(min_value=2000, max_value=3500)),
        'freq_step': draw(st.integers(min_value=50, max_value=500)),
        'test_duration': draw(test_duration_strategy),
        'voltage_start': draw(voltage_strategy),
        'voltage_step': draw(st.integers(min_value=1, max_value=10)),
        'safety_margin': draw(st.integers(min_value=0, max_value=20))
    }
    
    return FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=time.time(),
        wizard_config=wizard_config
    )


class TestFrequencyCurveSerialization:
    """Property 2: Frequency curve serialization round-trip
    
    For any valid frequency curve, serializing to JSON and then deserializing 
    SHALL produce an equivalent curve with identical frequency points, voltages, 
    and metadata.
    
    Validates: Requirements 7.1, 7.2, 7.3
    """

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_to_dict_from_dict_round_trip_preserves_all_data(self, curve: FrequencyCurve):
        """Dict serialization round-trip SHALL preserve all curve data.
        
        Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
        Validates: Requirements 7.1, 7.2, 7.3
        """
        # Serialize to dict
        curve_dict = curve.to_dict()
        
        # Deserialize from dict
        restored_curve = FrequencyCurve.from_dict(curve_dict)
        
        # Verify all fields match
        assert restored_curve.core_id == curve.core_id, "core_id mismatch"
        assert restored_curve.created_at == curve.created_at, "created_at mismatch"
        assert restored_curve.wizard_config == curve.wizard_config, "wizard_config mismatch"
        assert len(restored_curve.points) == len(curve.points), "points count mismatch"
        
        # Verify each point
        for i, (original, restored) in enumerate(zip(curve.points, restored_curve.points)):
            assert restored.frequency_mhz == original.frequency_mhz, (
                f"Point {i}: frequency_mhz mismatch"
            )
            assert restored.voltage_mv == original.voltage_mv, (
                f"Point {i}: voltage_mv mismatch"
            )
            assert restored.stable == original.stable, (
                f"Point {i}: stable mismatch"
            )
            assert restored.test_duration == original.test_duration, (
                f"Point {i}: test_duration mismatch"
            )
            assert restored.timestamp == original.timestamp, (
                f"Point {i}: timestamp mismatch"
            )

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_to_json_from_json_round_trip_preserves_all_data(self, curve: FrequencyCurve):
        """JSON serialization round-trip SHALL preserve all curve data.
        
        Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
        Validates: Requirements 7.1, 7.2, 7.3
        """
        # Serialize to JSON
        json_str = curve.to_json()
        
        # Verify it's valid JSON
        json.loads(json_str)  # Should not raise
        
        # Deserialize from JSON
        restored_curve = FrequencyCurve.from_json(json_str)
        
        # Verify all fields match
        assert restored_curve.core_id == curve.core_id
        assert restored_curve.created_at == curve.created_at
        assert restored_curve.wizard_config == curve.wizard_config
        assert len(restored_curve.points) == len(curve.points)
        
        # Verify each point
        for original, restored in zip(curve.points, restored_curve.points):
            assert restored.frequency_mhz == original.frequency_mhz
            assert restored.voltage_mv == original.voltage_mv
            assert restored.stable == original.stable
            assert restored.test_duration == original.test_duration
            assert restored.timestamp == original.timestamp

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_file_save_load_round_trip_preserves_all_data(self, curve: FrequencyCurve):
        """File save/load round-trip SHALL preserve all curve data.
        
        Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
        Validates: Requirements 7.1, 7.2, 7.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_curve.json"
            
            # Save to file
            curve.save_to_file(filepath)
            
            # Verify file exists and is valid JSON
            assert filepath.exists()
            with open(filepath, 'r') as f:
                json.load(f)  # Should not raise
            
            # Load from file
            restored_curve = FrequencyCurve.load_from_file(filepath)
            
            # Verify all fields match
            assert restored_curve.core_id == curve.core_id
            assert restored_curve.created_at == curve.created_at
            assert restored_curve.wizard_config == curve.wizard_config
            assert len(restored_curve.points) == len(curve.points)
            
            # Verify each point
            for original, restored in zip(curve.points, restored_curve.points):
                assert restored.frequency_mhz == original.frequency_mhz
                assert restored.voltage_mv == original.voltage_mv
                assert restored.stable == original.stable
                assert restored.test_duration == original.test_duration
                assert restored.timestamp == original.timestamp

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_serialized_json_is_human_readable(self, curve: FrequencyCurve):
        """Serialized JSON SHALL be human-readable with proper formatting.
        
        Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
        Validates: Requirements 7.1, 7.2, 7.3
        """
        json_str = curve.to_json()
        
        # Should contain newlines (indented)
        assert '\n' in json_str, "JSON should be indented for readability"
        
        # Should be parseable
        parsed = json.loads(json_str)
        
        # Should contain expected top-level keys
        assert 'core_id' in parsed
        assert 'points' in parsed
        assert 'created_at' in parsed
        assert 'wizard_config' in parsed

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_multiple_round_trips_preserve_data(self, curve: FrequencyCurve):
        """Multiple serialization round-trips SHALL preserve data integrity.
        
        Feature: frequency-based-wizard, Property 2: Frequency curve serialization round-trip
        Validates: Requirements 7.1, 7.2, 7.3
        """
        # First round-trip
        json_str_1 = curve.to_json()
        curve_1 = FrequencyCurve.from_json(json_str_1)
        
        # Second round-trip
        json_str_2 = curve_1.to_json()
        curve_2 = FrequencyCurve.from_json(json_str_2)
        
        # Third round-trip
        json_str_3 = curve_2.to_json()
        curve_3 = FrequencyCurve.from_json(json_str_3)
        
        # All should be identical
        assert curve_3.core_id == curve.core_id
        assert curve_3.created_at == curve.created_at
        assert len(curve_3.points) == len(curve.points)
        
        for original, restored in zip(curve.points, curve_3.points):
            assert restored.frequency_mhz == original.frequency_mhz
            assert restored.voltage_mv == original.voltage_mv
            assert restored.stable == original.stable
