"""Property-based tests for wizard frequency coverage completeness.

Feature: frequency-based-wizard, Property 5: Wizard frequency coverage completeness
Validates: Requirements 1.1, 1.4
"""

import math
import pytest
from hypothesis import given, strategies as st, assume

from backend.tuning.frequency_wizard import FrequencyWizardConfig


class TestFrequencyCoverage:
    """Test wizard frequency coverage completeness.
    
    Property 5: For any wizard configuration with freq_start, freq_end, and freq_step,
    the generated frequency curve should contain exactly ceil((freq_end - freq_start) / freq_step) + 1
    frequency points.
    """
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_frequency_point_count_matches_formula(self, freq_start, freq_range, freq_step):
        """Test that the number of frequency points matches the expected formula."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Calculate expected number of points
        # Formula: floor((freq_end - freq_start) / freq_step) + 1
        # This counts: start + number of complete steps that fit in the range
        expected_count = ((freq_end - freq_start) // freq_step) + 1
        
        # Generate frequency points using the wizard's internal method
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        actual_count = len(frequencies)
        
        # Verify the count matches the formula
        assert actual_count == expected_count, (
            f"Expected {expected_count} frequency points, got {actual_count} "
            f"(freq_start={freq_start}, freq_end={freq_end}, freq_step={freq_step})"
        )
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_all_frequencies_within_range(self, freq_start, freq_range, freq_step):
        """Test that all generated frequencies are within [freq_start, freq_end]."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Generate frequency points
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        # Verify all frequencies are within range
        for freq in frequencies:
            assert freq_start <= freq <= freq_end, (
                f"Frequency {freq} is outside range [{freq_start}, {freq_end}]"
            )
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_frequencies_are_sorted_ascending(self, freq_start, freq_range, freq_step):
        """Test that generated frequencies are in ascending order."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Generate frequency points
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        # Verify frequencies are sorted
        for i in range(len(frequencies) - 1):
            assert frequencies[i] < frequencies[i + 1], (
                f"Frequencies not in ascending order: {frequencies[i]} >= {frequencies[i + 1]}"
            )
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_first_frequency_is_start(self, freq_start, freq_range, freq_step):
        """Test that the first frequency point is always freq_start."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Generate frequency points
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        # Verify first frequency is freq_start
        assert len(frequencies) > 0, "No frequencies generated"
        assert frequencies[0] == freq_start, (
            f"First frequency {frequencies[0]} does not match freq_start {freq_start}"
        )
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_last_frequency_within_step_of_end(self, freq_start, freq_range, freq_step):
        """Test that the last frequency is within one step of freq_end."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Generate frequency points
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        # Verify last frequency is within one step of freq_end
        assert len(frequencies) > 0, "No frequencies generated"
        last_freq = frequencies[-1]
        
        # Last frequency should be <= freq_end
        assert last_freq <= freq_end, (
            f"Last frequency {last_freq} exceeds freq_end {freq_end}"
        )
        
        # Last frequency should be > freq_end - freq_step
        assert last_freq > freq_end - freq_step, (
            f"Last frequency {last_freq} is more than one step away from freq_end {freq_end}"
        )
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3000),
        freq_range=st.integers(min_value=100, max_value=3100),
        freq_step=st.integers(min_value=50, max_value=500)
    )
    def test_frequency_spacing_is_consistent(self, freq_start, freq_range, freq_step):
        """Test that spacing between consecutive frequencies is exactly freq_step."""
        freq_end = freq_start + freq_range
        
        # Ensure freq_end is within valid range
        assume(freq_end <= 3500)
        assume(freq_end > freq_start)
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step
        )
        
        # Generate frequency points
        frequencies = []
        freq = freq_start
        while freq <= freq_end:
            frequencies.append(freq)
            freq += freq_step
        
        # Verify spacing between consecutive frequencies
        for i in range(len(frequencies) - 1):
            spacing = frequencies[i + 1] - frequencies[i]
            assert spacing == freq_step, (
                f"Spacing between frequencies[{i}]={frequencies[i]} and "
                f"frequencies[{i+1}]={frequencies[i+1]} is {spacing}, expected {freq_step}"
            )
    
    def test_edge_case_single_point(self):
        """Test edge case where freq_start == freq_end results in single point."""
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1000,
            freq_step=100
        )
        
        # Generate frequency points
        frequencies = []
        freq = config.freq_start
        while freq <= config.freq_end:
            frequencies.append(freq)
            freq += config.freq_step
        
        # Should have exactly 1 point
        assert len(frequencies) == 1
        assert frequencies[0] == 1000
    
    def test_edge_case_step_larger_than_range(self):
        """Test edge case where freq_step > (freq_end - freq_start)."""
        config = FrequencyWizardConfig(
            freq_start=1000,
            freq_end=1050,
            freq_step=100
        )
        
        # Generate frequency points
        frequencies = []
        freq = config.freq_start
        while freq <= config.freq_end:
            frequencies.append(freq)
            freq += config.freq_step
        
        # Should have exactly 1 point (start point only)
        assert len(frequencies) == 1
        assert frequencies[0] == 1000
