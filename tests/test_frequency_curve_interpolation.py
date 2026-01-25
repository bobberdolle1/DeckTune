"""Property tests for frequency curve interpolation correctness.

Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness
Validates: Requirements 1.5, 2.2

Property 3: Frequency curve interpolation correctness
For any frequency curve with at least two points, and any frequency value between 
the minimum and maximum tested frequencies, the interpolated voltage SHALL be 
mathematically correct using linear interpolation between the surrounding points.
"""

import time
from hypothesis import given, strategies as st, settings, assume
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
    # Ensure we have at least 2 points and the last one is at max_freq
    if len(freqs) < 2:
        freqs = [min_freq, max_freq]
    elif freqs[-1] != max_freq:
        freqs[-1] = max_freq
    return freqs


@st.composite
def frequency_curve_strategy(draw):
    """Generate valid frequency curves with at least 2 points."""
    core_id = draw(core_id_strategy)
    
    # Generate at least 2 points
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


class TestFrequencyCurveInterpolation:
    """Property 3: Frequency curve interpolation correctness
    
    For any frequency curve with at least two points, and any frequency value 
    between the minimum and maximum tested frequencies, the interpolated voltage 
    SHALL be mathematically correct using linear interpolation between the 
    surrounding points.
    
    Validates: Requirements 1.5, 2.2
    """

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_interpolation_at_exact_points_returns_exact_voltage(self, curve: FrequencyCurve):
        """Interpolation at exact frequency points SHALL return exact voltage.
        
        Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness
        Validates: Requirements 1.5, 2.2
        """
        for point in curve.points:
            interpolated = curve.get_voltage_for_frequency(point.frequency_mhz)
            assert interpolated == point.voltage_mv, (
                f"Interpolation at exact point {point.frequency_mhz} MHz "
                f"should return {point.voltage_mv} mV, got {interpolated} mV"
            )

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_interpolation_between_points_is_mathematically_correct(self, curve: FrequencyCurve):
        """Interpolation between points SHALL use correct linear formula.
        
        Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness
        Validates: Requirements 1.5, 2.2
        """
        # Test interpolation between each pair of adjacent points
        for i in range(len(curve.points) - 1):
            p1 = curve.points[i]
            p2 = curve.points[i + 1]
            
            # Test midpoint
            mid_freq = (p1.frequency_mhz + p2.frequency_mhz) // 2
            
            # Skip if midpoint equals one of the endpoints
            if mid_freq == p1.frequency_mhz or mid_freq == p2.frequency_mhz:
                continue
            
            interpolated = curve.get_voltage_for_frequency(mid_freq)
            
            # Calculate expected value using linear interpolation formula
            # v = v1 + (v2 - v1) * (f - f1) / (f2 - f1)
            freq_range = p2.frequency_mhz - p1.frequency_mhz
            voltage_range = p2.voltage_mv - p1.voltage_mv
            freq_offset = mid_freq - p1.frequency_mhz
            expected = p1.voltage_mv + (voltage_range * freq_offset) // freq_range
            
            assert interpolated == expected, (
                f"Interpolation at {mid_freq} MHz between "
                f"({p1.frequency_mhz} MHz, {p1.voltage_mv} mV) and "
                f"({p2.frequency_mhz} MHz, {p2.voltage_mv} mV) "
                f"should return {expected} mV, got {interpolated} mV"
            )

    @given(
        curve=frequency_curve_strategy(),
        offset_ratio=st.floats(min_value=0.1, max_value=0.9)
    )
    @settings(max_examples=100)
    def test_interpolation_preserves_linear_relationship(
        self, 
        curve: FrequencyCurve,
        offset_ratio: float
    ):
        """Interpolated values SHALL maintain linear relationship.
        
        Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness
        Validates: Requirements 1.5, 2.2
        """
        # Test between first two points
        if len(curve.points) < 2:
            return
        
        p1 = curve.points[0]
        p2 = curve.points[1]
        
        # Calculate test frequency at given ratio
        freq_range = p2.frequency_mhz - p1.frequency_mhz
        if freq_range <= 1:
            return
        
        test_freq = p1.frequency_mhz + int(freq_range * offset_ratio)
        
        # Skip if test_freq equals an endpoint
        if test_freq == p1.frequency_mhz or test_freq == p2.frequency_mhz:
            return
        
        interpolated = curve.get_voltage_for_frequency(test_freq)
        
        # Verify the interpolated value is between the two endpoints
        min_voltage = min(p1.voltage_mv, p2.voltage_mv)
        max_voltage = max(p1.voltage_mv, p2.voltage_mv)
        
        assert min_voltage <= interpolated <= max_voltage, (
            f"Interpolated voltage {interpolated} mV at {test_freq} MHz "
            f"should be between {min_voltage} mV and {max_voltage} mV"
        )

    @given(curve=frequency_curve_strategy())
    @settings(max_examples=100)
    def test_interpolation_is_monotonic_for_monotonic_curves(self, curve: FrequencyCurve):
        """For monotonic curves, interpolation SHALL preserve monotonicity.
        
        Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness
        Validates: Requirements 1.5, 2.2
        """
        if len(curve.points) < 2:
            return
        
        # Check if curve is monotonic (all increasing or all decreasing)
        voltages = [p.voltage_mv for p in curve.points]
        is_increasing = all(voltages[i] <= voltages[i+1] for i in range(len(voltages)-1))
        is_decreasing = all(voltages[i] >= voltages[i+1] for i in range(len(voltages)-1))
        
        if not (is_increasing or is_decreasing):
            return  # Skip non-monotonic curves
        
        # Test interpolation at multiple points
        min_freq = curve.points[0].frequency_mhz
        max_freq = curve.points[-1].frequency_mhz
        
        if max_freq - min_freq < 10:
            return
        
        test_freqs = [
            min_freq + (max_freq - min_freq) // 4,
            min_freq + (max_freq - min_freq) // 2,
            min_freq + 3 * (max_freq - min_freq) // 4
        ]
        
        interpolated_values = [curve.get_voltage_for_frequency(f) for f in test_freqs]
        
        # Check monotonicity of interpolated values
        if is_increasing:
            for i in range(len(interpolated_values) - 1):
                assert interpolated_values[i] <= interpolated_values[i+1], (
                    f"Interpolated values should be increasing for increasing curve, "
                    f"but {interpolated_values[i]} > {interpolated_values[i+1]}"
                )
        else:  # is_decreasing
            for i in range(len(interpolated_values) - 1):
                assert interpolated_values[i] >= interpolated_values[i+1], (
                    f"Interpolated values should be decreasing for decreasing curve, "
                    f"but {interpolated_values[i]} < {interpolated_values[i+1]}"
                )
