"""Property tests for frequency curve boundary clamping.

Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
Validates: Requirements 2.4

Property 4: Frequency curve boundary clamping
For any frequency curve, frequencies below the minimum tested frequency SHALL 
return the minimum voltage, and frequencies above the maximum tested frequency 
SHALL return the maximum voltage.
"""

import time
from hypothesis import given, strategies as st, settings
from backend.tuning.frequency_curve import FrequencyPoint, FrequencyCurve


# Strategies for generating test data
frequency_strategy = st.integers(min_value=400, max_value=3500)
voltage_strategy = st.integers(min_value=-100, max_value=0)
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
def frequency_curve_strategy(draw):
    """Generate valid frequency curves with at least 2 points."""
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


class TestFrequencyCurveBoundaryClamping:
    """Property 4: Frequency curve boundary clamping
    
    For any frequency curve, frequencies below the minimum tested frequency 
    SHALL return the minimum voltage, and frequencies above the maximum tested 
    frequency SHALL return the maximum voltage.
    
    Validates: Requirements 2.4
    """

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_frequency_below_minimum_returns_minimum_voltage(self, curve: FrequencyCurve):
        """Frequencies below minimum SHALL return minimum voltage.
        
        Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
        Validates: Requirements 2.4
        """
        min_freq = curve.points[0].frequency_mhz
        min_voltage = curve.points[0].voltage_mv
        
        # Test various frequencies below minimum
        test_freqs = [
            min_freq - 1,
            min_freq - 50,
            min_freq - 100,
            400  # Absolute minimum
        ]
        
        for test_freq in test_freqs:
            if test_freq < 400:  # Don't test below absolute minimum
                continue
            
            result = curve.get_voltage_for_frequency(test_freq)
            assert result == min_voltage, (
                f"Frequency {test_freq} MHz below minimum {min_freq} MHz "
                f"should return minimum voltage {min_voltage} mV, got {result} mV"
            )

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_frequency_above_maximum_returns_maximum_voltage(self, curve: FrequencyCurve):
        """Frequencies above maximum SHALL return maximum voltage.
        
        Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
        Validates: Requirements 2.4
        """
        max_freq = curve.points[-1].frequency_mhz
        max_voltage = curve.points[-1].voltage_mv
        
        # Test various frequencies above maximum
        test_freqs = [
            max_freq + 1,
            max_freq + 50,
            max_freq + 100,
            3500  # Absolute maximum
        ]
        
        for test_freq in test_freqs:
            if test_freq > 3500:  # Don't test above absolute maximum
                continue
            
            result = curve.get_voltage_for_frequency(test_freq)
            assert result == max_voltage, (
                f"Frequency {test_freq} MHz above maximum {max_freq} MHz "
                f"should return maximum voltage {max_voltage} mV, got {result} mV"
            )

    @given(
        curve=frequency_curve_strategy(),
        below_offset=st.integers(min_value=1, max_value=500)
    )
    @settings(max_examples=100)
    def test_any_frequency_below_minimum_clamps_to_minimum(
        self, 
        curve: FrequencyCurve,
        below_offset: int
    ):
        """Any frequency below minimum SHALL clamp to minimum voltage.
        
        Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
        Validates: Requirements 2.4
        """
        min_freq = curve.points[0].frequency_mhz
        min_voltage = curve.points[0].voltage_mv
        
        test_freq = max(400, min_freq - below_offset)
        
        result = curve.get_voltage_for_frequency(test_freq)
        assert result == min_voltage, (
            f"Frequency {test_freq} MHz (offset {below_offset} below minimum {min_freq} MHz) "
            f"should return minimum voltage {min_voltage} mV, got {result} mV"
        )

    @given(
        curve=frequency_curve_strategy(),
        above_offset=st.integers(min_value=1, max_value=500)
    )
    @settings(max_examples=100)
    def test_any_frequency_above_maximum_clamps_to_maximum(
        self, 
        curve: FrequencyCurve,
        above_offset: int
    ):
        """Any frequency above maximum SHALL clamp to maximum voltage.
        
        Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
        Validates: Requirements 2.4
        """
        max_freq = curve.points[-1].frequency_mhz
        max_voltage = curve.points[-1].voltage_mv
        
        test_freq = min(3500, max_freq + above_offset)
        
        result = curve.get_voltage_for_frequency(test_freq)
        assert result == max_voltage, (
            f"Frequency {test_freq} MHz (offset {above_offset} above maximum {max_freq} MHz) "
            f"should return maximum voltage {max_voltage} mV, got {result} mV"
        )

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_boundary_frequencies_equal_to_endpoints_return_exact_values(
        self, 
        curve: FrequencyCurve
    ):
        """Frequencies exactly at boundaries SHALL return exact endpoint voltages.
        
        Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping
        Validates: Requirements 2.4
        """
        min_freq = curve.points[0].frequency_mhz
        min_voltage = curve.points[0].voltage_mv
        max_freq = curve.points[-1].frequency_mhz
        max_voltage = curve.points[-1].voltage_mv
        
        # Test at exact minimum
        result_min = curve.get_voltage_for_frequency(min_freq)
        assert result_min == min_voltage, (
            f"Frequency at exact minimum {min_freq} MHz "
            f"should return {min_voltage} mV, got {result_min} mV"
        )
        
        # Test at exact maximum
        result_max = curve.get_voltage_for_frequency(max_freq)
        assert result_max == max_voltage, (
            f"Frequency at exact maximum {max_freq} MHz "
            f"should return {max_voltage} mV, got {result_max} mV"
        )
