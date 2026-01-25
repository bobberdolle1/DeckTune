"""Property tests for frequency curve validation.

Feature: frequency-based-wizard, Property 10: Curve validation on load
Validates: Requirements 7.4, 7.5

Property 10: Curve validation on load
For any frequency curve loaded from storage, if any voltage value is outside 
the range [-100, 0] or if frequency values are not in ascending order, the 
validation SHALL fail and reject the curve.
"""

import time
from hypothesis import given, strategies as st, settings, assume
import pytest
from backend.tuning.frequency_curve import FrequencyPoint, FrequencyCurve


# Strategies for generating test data
frequency_strategy = st.integers(min_value=400, max_value=3500)
voltage_strategy = st.integers(min_value=-100, max_value=0)
invalid_voltage_strategy = st.one_of(
    st.integers(min_value=-1000, max_value=-101),
    st.integers(min_value=1, max_value=1000)
)
core_id_strategy = st.integers(min_value=0, max_value=7)


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
def valid_frequency_curve_strategy(draw):
    """Generate valid frequency curves."""
    core_id = draw(core_id_strategy)
    num_points = draw(st.integers(min_value=2, max_value=10))
    min_freq = draw(st.integers(min_value=400, max_value=2000))
    max_freq = draw(st.integers(min_value=min_freq + 100, max_value=3500))
    
    frequencies = generate_sorted_frequencies(min_freq, max_freq, num_points)
    
    points = []
    for freq in frequencies:
        voltage = draw(voltage_strategy)
        points.append(FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=voltage,
            stable=True,
            test_duration=30,
            timestamp=time.time()
        ))
    
    return FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=time.time(),
        wizard_config={}
    )


class TestFrequencyCurveValidation:
    """Property 10: Curve validation on load
    
    For any frequency curve loaded from storage, if any voltage value is outside 
    the range [-100, 0] or if frequency values are not in ascending order, the 
    validation SHALL fail and reject the curve.
    
    Validates: Requirements 7.4, 7.5
    """

    @given(curve=valid_frequency_curve_strategy())
    @settings(max_examples=100)
    def test_valid_curve_passes_validation(self, curve: FrequencyCurve):
        """Valid curves SHALL pass validation without errors.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Should not raise
        result = curve.validate()
        assert result is True

    @given(
        curve=valid_frequency_curve_strategy(),
        invalid_voltage=invalid_voltage_strategy,
        point_index=st.integers(min_value=0, max_value=9)
    )
    @settings(max_examples=100)
    def test_curve_with_out_of_range_voltage_fails_validation(
        self, 
        curve: FrequencyCurve,
        invalid_voltage: int,
        point_index: int
    ):
        """Curves with voltages outside [-100, 0] SHALL fail validation.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Ensure point_index is valid
        if point_index >= len(curve.points):
            point_index = len(curve.points) - 1
        
        # Inject invalid voltage
        curve.points[point_index].voltage_mv = invalid_voltage
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            curve.validate()
        
        assert "outside valid range" in str(exc_info.value).lower()

    @given(curve=valid_frequency_curve_strategy())
    @settings(max_examples=100)
    def test_curve_with_unsorted_frequencies_fails_validation(self, curve: FrequencyCurve):
        """Curves with unsorted frequencies SHALL fail validation.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Need at least 2 points to swap
        if len(curve.points) < 2:
            return
        
        # Swap first two points to break sorting
        curve.points[0], curve.points[1] = curve.points[1], curve.points[0]
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            curve.validate()
        
        assert "not in ascending order" in str(exc_info.value).lower()

    @given(curve=valid_frequency_curve_strategy())
    @settings(max_examples=100)
    def test_curve_with_duplicate_frequencies_fails_validation(self, curve: FrequencyCurve):
        """Curves with duplicate frequencies SHALL fail validation.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Need at least 2 points
        if len(curve.points) < 2:
            return
        
        # Make second point have same frequency as first
        curve.points[1].frequency_mhz = curve.points[0].frequency_mhz
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            curve.validate()
        
        assert "duplicate frequency" in str(exc_info.value).lower()

    @given(
        core_id=core_id_strategy,
        invalid_voltage=invalid_voltage_strategy
    )
    @settings(max_examples=100)
    def test_from_dict_with_invalid_voltage_fails(
        self, 
        core_id: int,
        invalid_voltage: int
    ):
        """Deserialization SHALL validate and reject invalid voltages.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        curve_dict = {
            'core_id': core_id,
            'points': [
                {
                    'frequency_mhz': 1000,
                    'voltage_mv': invalid_voltage,
                    'stable': True,
                    'test_duration': 30,
                    'timestamp': time.time()
                }
            ],
            'created_at': time.time(),
            'wizard_config': {}
        }
        
        # Should raise ValueError during validation
        with pytest.raises(ValueError) as exc_info:
            FrequencyCurve.from_dict(curve_dict)
        
        assert "outside valid range" in str(exc_info.value).lower()

    @given(core_id=core_id_strategy)
    @settings(max_examples=100)
    def test_from_dict_with_unsorted_frequencies_fails(self, core_id: int):
        """Deserialization SHALL validate and reject unsorted frequencies.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        curve_dict = {
            'core_id': core_id,
            'points': [
                {
                    'frequency_mhz': 2000,
                    'voltage_mv': -30,
                    'stable': True,
                    'test_duration': 30,
                    'timestamp': time.time()
                },
                {
                    'frequency_mhz': 1000,  # Out of order
                    'voltage_mv': -25,
                    'stable': True,
                    'test_duration': 30,
                    'timestamp': time.time()
                }
            ],
            'created_at': time.time(),
            'wizard_config': {}
        }
        
        # Should raise ValueError during validation
        with pytest.raises(ValueError) as exc_info:
            FrequencyCurve.from_dict(curve_dict)
        
        assert "not in ascending order" in str(exc_info.value).lower()

    @given(core_id=core_id_strategy)
    @settings(max_examples=100)
    def test_empty_curve_fails_validation(self, core_id: int):
        """Curves with no points SHALL fail validation.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        curve = FrequencyCurve(
            core_id=core_id,
            points=[],
            created_at=time.time(),
            wizard_config={}
        )
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            curve.validate()
        
        assert "no points" in str(exc_info.value).lower()

    @given(
        curve=valid_frequency_curve_strategy(),
        voltage_offset=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_voltage_exactly_at_boundaries_is_valid(
        self, 
        curve: FrequencyCurve,
        voltage_offset: int
    ):
        """Voltages exactly at -100 or 0 SHALL be valid.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Test with voltage at -100 (minimum boundary)
        curve.points[0].voltage_mv = -100
        assert curve.validate() is True
        
        # Test with voltage at 0 (maximum boundary)
        if len(curve.points) > 1:
            curve.points[1].voltage_mv = 0
            assert curve.validate() is True

    @given(curve=valid_frequency_curve_strategy())
    @settings(max_examples=100)
    def test_from_json_validates_curve(self, curve: FrequencyCurve):
        """JSON deserialization SHALL validate the curve.
        
        Feature: frequency-based-wizard, Property 10: Curve validation on load
        Validates: Requirements 7.4, 7.5
        """
        # Valid curve should deserialize successfully
        json_str = curve.to_json()
        restored = FrequencyCurve.from_json(json_str)
        assert restored.validate() is True
        
        # Modify JSON to have invalid voltage
        import json
        curve_dict = json.loads(json_str)
        curve_dict['points'][0]['voltage_mv'] = 100  # Invalid
        invalid_json = json.dumps(curve_dict)
        
        # Should raise ValueError
        with pytest.raises(ValueError):
            FrequencyCurve.from_json(invalid_json)
