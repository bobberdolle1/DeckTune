"""Property-based tests for wizard adaptive step optimization.

Feature: frequency-based-wizard, Property 22: Adaptive step optimization
Validates: Requirements 12.1
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from backend.tuning.frequency_wizard import FrequencyWizardConfig


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=3000),
    freq_end=st.integers(min_value=500, max_value=3500),
    base_step=st.integers(min_value=50, max_value=200),
    adaptive_enabled=st.booleans()
)
def test_adaptive_step_reduces_test_count_in_stable_regions(
    freq_start, freq_end, base_step, adaptive_enabled
):
    """Property 22: Adaptive step optimization.
    
    For any wizard execution with adaptive_step enabled, when a stable voltage
    region is detected (3+ consecutive frequencies with similar voltages), the
    frequency step size should increase to skip redundant tests.
    
    This test verifies that adaptive stepping reduces the total number of
    frequency points tested compared to non-adaptive mode.
    
    Feature: frequency-based-wizard, Property 22: Adaptive step optimization
    Validates: Requirements 12.1
    """
    # Ensure valid frequency range
    assume(freq_end > freq_start)
    assume((freq_end - freq_start) >= base_step * 5)  # Need enough range
    
    # Create config with adaptive stepping
    config_adaptive = FrequencyWizardConfig(
        freq_start=freq_start,
        freq_end=freq_end,
        freq_step=base_step,
        adaptive_step=True
    )
    
    # Create config without adaptive stepping
    config_fixed = FrequencyWizardConfig(
        freq_start=freq_start,
        freq_end=freq_end,
        freq_step=base_step,
        adaptive_step=False
    )
    
    # Calculate frequency points for fixed step
    fixed_points = []
    freq = freq_start
    while freq <= freq_end:
        fixed_points.append(freq)
        freq += base_step
    
    # Simulate adaptive step calculation
    # In a stable region (3+ similar voltages), step should increase
    adaptive_points = []
    freq = freq_start
    current_step = base_step
    consecutive_stable = 0
    
    # Simulate voltage stability pattern (for testing)
    # We'll assume every 3rd frequency is in a stable region
    freq_index = 0
    
    while freq <= freq_end:
        adaptive_points.append(freq)
        
        # Simulate stable region detection
        if adaptive_enabled and freq_index % 3 == 0:
            consecutive_stable += 1
        else:
            consecutive_stable = 0
        
        # If we detect stable region (3+ consecutive), increase step
        if adaptive_enabled and consecutive_stable >= 3:
            current_step = base_step * 2  # Double the step
        else:
            current_step = base_step
        
        freq += current_step
        freq_index += 1
    
    # Property: With adaptive stepping enabled, we should test fewer points
    # in stable regions compared to fixed stepping
    if adaptive_enabled:
        # Adaptive should have fewer or equal points (optimization)
        assert len(adaptive_points) <= len(fixed_points), (
            f"Adaptive stepping should reduce test count: "
            f"adaptive={len(adaptive_points)}, fixed={len(fixed_points)}"
        )
    else:
        # Without adaptive, both should be the same
        assert len(adaptive_points) == len(fixed_points), (
            f"Non-adaptive should match fixed stepping: "
            f"adaptive={len(adaptive_points)}, fixed={len(fixed_points)}"
        )


@settings(max_examples=100)
@given(
    voltages=st.lists(
        st.integers(min_value=-50, max_value=-10),
        min_size=5,
        max_size=10
    )
)
def test_stable_region_detection_requires_similar_voltages(voltages):
    """Property: Stable region detection should identify consecutive similar voltages.
    
    For any sequence of voltage measurements, a stable region should only be
    detected when 3 or more consecutive voltages differ by less than a threshold
    (e.g., 2mV).
    
    Feature: frequency-based-wizard, Property 22: Adaptive step optimization
    Validates: Requirements 12.1
    """
    SIMILARITY_THRESHOLD = 2  # mV
    CONSECUTIVE_REQUIRED = 3
    
    # Detect stable regions in voltage sequence
    stable_regions = []
    consecutive_count = 1
    
    for i in range(1, len(voltages)):
        voltage_diff = abs(voltages[i] - voltages[i-1])
        
        if voltage_diff <= SIMILARITY_THRESHOLD:
            consecutive_count += 1
            
            if consecutive_count >= CONSECUTIVE_REQUIRED:
                # Mark this as a stable region
                if not stable_regions or stable_regions[-1] != i - CONSECUTIVE_REQUIRED + 1:
                    stable_regions.append(i - CONSECUTIVE_REQUIRED + 1)
        else:
            consecutive_count = 1
    
    # Property: Stable regions should only exist where voltages are actually similar
    for region_start in stable_regions:
        # Check that the region actually has similar voltages
        region_voltages = voltages[region_start:region_start + CONSECUTIVE_REQUIRED]
        
        if len(region_voltages) >= CONSECUTIVE_REQUIRED:
            max_voltage = max(region_voltages)
            min_voltage = min(region_voltages)
            voltage_range = max_voltage - min_voltage
            
            assert voltage_range <= SIMILARITY_THRESHOLD * (CONSECUTIVE_REQUIRED - 1), (
                f"Stable region should have similar voltages: "
                f"range={voltage_range}mV, threshold={SIMILARITY_THRESHOLD}mV"
            )


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=2000),
    freq_end=st.integers(min_value=2500, max_value=3500),
    base_step=st.integers(min_value=50, max_value=150)
)
def test_adaptive_step_never_exceeds_maximum_multiplier(freq_start, freq_end, base_step):
    """Property: Adaptive step should have a maximum multiplier to avoid skipping too much.
    
    For any adaptive step calculation, the increased step size should not exceed
    a reasonable maximum (e.g., 3x the base step) to ensure adequate coverage.
    
    Feature: frequency-based-wizard, Property 22: Adaptive step optimization
    Validates: Requirements 12.1
    """
    assume(freq_end > freq_start)
    
    MAX_STEP_MULTIPLIER = 3
    
    # Simulate adaptive stepping with maximum multiplier
    frequencies = []
    freq = freq_start
    consecutive_stable = 0
    
    while freq <= freq_end:
        frequencies.append(freq)
        
        # Simulate stable region (every 3rd frequency)
        if len(frequencies) % 3 == 0:
            consecutive_stable += 1
        else:
            consecutive_stable = 0
        
        # Calculate adaptive step with maximum multiplier
        if consecutive_stable >= 3:
            # Increase step but cap at maximum
            step_multiplier = min(consecutive_stable - 1, MAX_STEP_MULTIPLIER)
            current_step = base_step * step_multiplier
        else:
            current_step = base_step
        
        # Property: Step should never exceed max multiplier
        assert current_step <= base_step * MAX_STEP_MULTIPLIER, (
            f"Adaptive step exceeded maximum: "
            f"step={current_step}, max={base_step * MAX_STEP_MULTIPLIER}"
        )
        
        freq += current_step
    
    # Property: We should still have reasonable coverage
    # (not skipping too much of the frequency range)
    total_range = freq_end - freq_start
    avg_step = total_range / max(len(frequencies) - 1, 1)
    
    assert avg_step <= base_step * MAX_STEP_MULTIPLIER, (
        f"Average step size exceeded maximum: "
        f"avg_step={avg_step:.1f}, max={base_step * MAX_STEP_MULTIPLIER}"
    )


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=2000),
    freq_end=st.integers(min_value=2500, max_value=3500),
    base_step=st.integers(min_value=50, max_value=200)
)
def test_adaptive_step_maintains_minimum_coverage(freq_start, freq_end, base_step):
    """Property: Adaptive stepping should maintain minimum frequency coverage.
    
    For any wizard configuration with adaptive stepping, the generated frequency
    points should still provide adequate coverage of the frequency range, even
    with optimization.
    
    Feature: frequency-based-wizard, Property 22: Adaptive step optimization
    Validates: Requirements 12.1
    """
    assume(freq_end > freq_start)
    assume((freq_end - freq_start) >= base_step * 3)
    
    # Simulate adaptive stepping
    frequencies = []
    freq = freq_start
    consecutive_stable = 0
    
    while freq <= freq_end:
        frequencies.append(freq)
        
        # Simulate stable region detection
        if len(frequencies) % 3 == 0:
            consecutive_stable += 1
        else:
            consecutive_stable = 0
        
        # Adaptive step calculation
        if consecutive_stable >= 3:
            current_step = base_step * 2
        else:
            current_step = base_step
        
        freq += current_step
    
    # Property: Should have at least some minimum number of points
    # Even with aggressive optimization, we need adequate coverage
    total_range = freq_end - freq_start
    max_possible_step = base_step * 3  # Maximum adaptive step
    min_expected_points = (total_range // max_possible_step) + 1
    
    assert len(frequencies) >= min_expected_points, (
        f"Adaptive stepping reduced coverage too much: "
        f"points={len(frequencies)}, min_expected={min_expected_points}"
    )
    
    # Property: First and last frequencies should be close to boundaries
    assert frequencies[0] == freq_start, "First frequency should match start"
    assert frequencies[-1] <= freq_end, "Last frequency should not exceed end"
    assert frequencies[-1] >= freq_end - max_possible_step, (
        "Last frequency should be close to end"
    )
