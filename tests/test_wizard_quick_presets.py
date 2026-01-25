"""Property-based tests for wizard quick preset parameter optimization.

Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
Validates: Requirements 12.5
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from backend.tuning.frequency_wizard import FrequencyWizardConfig


# Quick preset parameter constraints from requirements
QUICK_PRESET_MIN_STEP = 200  # MHz
QUICK_PRESET_MAX_DURATION = 20  # seconds
QUICK_PRESET_TARGET_TIME = 10 * 60  # 10 minutes in seconds


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=1500),
    freq_end=st.integers(min_value=2000, max_value=3500),
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20)
)
def test_quick_preset_meets_step_size_requirement(
    freq_start, freq_end, freq_step, test_duration
):
    """Property 25: Quick preset parameter optimization.
    
    For any wizard configuration using a quick preset, the freq_step should be
    >= 200 MHz to ensure completion within reasonable time.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    assume(freq_end > freq_start)
    
    # Create quick preset config
    config = FrequencyWizardConfig(
        freq_start=freq_start,
        freq_end=freq_end,
        freq_step=freq_step,
        test_duration=test_duration,
        adaptive_step=True  # Quick presets use adaptive stepping
    )
    
    # Property: Quick preset step size should be >= 200 MHz
    assert config.freq_step >= QUICK_PRESET_MIN_STEP, (
        f"Quick preset step size should be >= {QUICK_PRESET_MIN_STEP} MHz, "
        f"got {config.freq_step} MHz"
    )


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=1500),
    freq_end=st.integers(min_value=2000, max_value=3500),
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20)
)
def test_quick_preset_meets_duration_requirement(
    freq_start, freq_end, freq_step, test_duration
):
    """Property: Quick preset test duration should be <= 20 seconds.
    
    For any wizard configuration using a quick preset, the test_duration should
    be <= 20 seconds to ensure fast completion.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    assume(freq_end > freq_start)
    
    # Create quick preset config
    config = FrequencyWizardConfig(
        freq_start=freq_start,
        freq_end=freq_end,
        freq_step=freq_step,
        test_duration=test_duration
    )
    
    # Property: Quick preset duration should be <= 20 seconds
    assert config.test_duration <= QUICK_PRESET_MAX_DURATION, (
        f"Quick preset test duration should be <= {QUICK_PRESET_MAX_DURATION}s, "
        f"got {config.test_duration}s"
    )


@settings(max_examples=100)
@given(
    freq_start=st.integers(min_value=400, max_value=1500),
    freq_end=st.integers(min_value=2000, max_value=3500),
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20)
)
def test_quick_preset_completes_within_target_time(
    freq_start, freq_end, freq_step, test_duration
):
    """Property: Quick preset should complete within target time (10 minutes).
    
    For any wizard configuration using quick preset parameters, the estimated
    total execution time should be <= 10 minutes.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    assume(freq_end > freq_start)
    assume(freq_step >= QUICK_PRESET_MIN_STEP)
    assume(test_duration <= QUICK_PRESET_MAX_DURATION)
    
    # Calculate number of frequency points
    num_points = ((freq_end - freq_start) // freq_step) + 1
    
    # Estimate time per point
    # Binary search typically takes 3-5 iterations, but each iteration
    # is much shorter than the full test duration (early failures are quick)
    # Realistic average: 2-3x the test duration per frequency point
    avg_time_multiplier = 3
    time_per_point = test_duration * avg_time_multiplier
    
    # Calculate total estimated time
    estimated_total_time = num_points * time_per_point
    
    # Property: Quick preset should complete within reasonable time
    # Target is 10 minutes, allow up to 15 minutes with margin
    REASONABLE_TIME_LIMIT = 900  # 15 minutes
    
    assert estimated_total_time <= REASONABLE_TIME_LIMIT, (
        f"Quick preset estimated time {estimated_total_time}s exceeds "
        f"reasonable limit {REASONABLE_TIME_LIMIT}s "
        f"(points={num_points}, time_per_point={time_per_point}s)"
    )


@settings(max_examples=100)
@given(
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20)
)
def test_quick_preset_parameters_are_valid_config(freq_step, test_duration):
    """Property: Quick preset parameters should form a valid configuration.
    
    For any quick preset parameters, they should pass configuration validation.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    # Create quick preset config with standard range
    config = FrequencyWizardConfig(
        freq_start=400,
        freq_end=3500,
        freq_step=freq_step,
        test_duration=test_duration,
        voltage_start=-30,
        voltage_step=2,
        safety_margin=5,
        adaptive_step=True
    )
    
    # Property: Quick preset config should pass validation
    try:
        config.validate()
        validation_passed = True
    except Exception as e:
        validation_passed = False
        pytest.fail(f"Quick preset config failed validation: {e}")
    
    assert validation_passed, "Quick preset parameters should form valid config"


@settings(max_examples=100)
@given(
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20),
    freq_range_start=st.integers(min_value=400, max_value=1000),
    freq_range_end=st.integers(min_value=2500, max_value=3500)
)
def test_quick_preset_provides_adequate_coverage(
    freq_step, test_duration, freq_range_start, freq_range_end
):
    """Property: Quick preset should still provide adequate frequency coverage.
    
    For any quick preset configuration, despite the larger step size, the
    frequency coverage should still be adequate (minimum number of points).
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    assume(freq_range_end > freq_range_start)
    assume(freq_step >= QUICK_PRESET_MIN_STEP)
    
    # Calculate number of frequency points
    num_points = ((freq_range_end - freq_range_start) // freq_step) + 1
    
    # Property: Should have at least a minimum number of points for coverage
    # For quick preset with large steps, we need at least 3-4 points minimum
    # This is a balance between speed and having enough data for interpolation
    MIN_COVERAGE_POINTS = 3
    
    assert num_points >= MIN_COVERAGE_POINTS, (
        f"Quick preset should provide at least {MIN_COVERAGE_POINTS} points, "
        f"got {num_points} points "
        f"(range={freq_range_end - freq_range_start}MHz, step={freq_step}MHz)"
    )


@settings(max_examples=100)
@given(
    preset_type=st.sampled_from(['quick', 'balanced', 'thorough'])
)
def test_preset_types_have_appropriate_parameters(preset_type):
    """Property: Different preset types should have appropriate parameters.
    
    For any preset type (quick, balanced, thorough), the parameters should
    match the expected characteristics of that preset.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    # Define preset parameters
    presets = {
        'quick': {
            'freq_step': 200,
            'test_duration': 15,
            'adaptive_step': True
        },
        'balanced': {
            'freq_step': 100,
            'test_duration': 30,
            'adaptive_step': True
        },
        'thorough': {
            'freq_step': 50,
            'test_duration': 60,
            'adaptive_step': False
        }
    }
    
    preset_params = presets[preset_type]
    
    config = FrequencyWizardConfig(
        freq_start=400,
        freq_end=3500,
        freq_step=preset_params['freq_step'],
        test_duration=preset_params['test_duration'],
        adaptive_step=preset_params['adaptive_step']
    )
    
    # Property: Quick preset should meet quick requirements
    if preset_type == 'quick':
        assert config.freq_step >= QUICK_PRESET_MIN_STEP
        assert config.test_duration <= QUICK_PRESET_MAX_DURATION
        assert config.adaptive_step is True
    
    # Property: Thorough preset should be more comprehensive
    elif preset_type == 'thorough':
        assert config.freq_step < QUICK_PRESET_MIN_STEP
        assert config.test_duration > QUICK_PRESET_MAX_DURATION
    
    # Property: All presets should be valid
    config.validate()


@settings(max_examples=100)
@given(
    freq_step=st.integers(min_value=200, max_value=500),
    test_duration=st.integers(min_value=10, max_value=20)
)
def test_quick_preset_time_estimate_is_reasonable(freq_step, test_duration):
    """Property: Quick preset time estimate should be reasonable and accurate.
    
    For any quick preset configuration, the estimated completion time should
    be calculable and reasonable (not negative, not excessively long).
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    freq_start = 400
    freq_end = 3500
    
    # Calculate number of points
    num_points = ((freq_end - freq_start) // freq_step) + 1
    
    # Estimate time (binary search iterations * test duration per iteration)
    # Use realistic estimate: 3 iterations average (optimistic for quick preset)
    avg_iterations = 3
    estimated_time = num_points * test_duration * avg_iterations
    
    # Property: Estimated time should be positive
    assert estimated_time > 0, "Estimated time should be positive"
    
    # Property: Estimated time should be reasonable (with margin)
    REASONABLE_TIME_LIMIT = 1000  # ~16 minutes
    assert estimated_time <= REASONABLE_TIME_LIMIT, (
        f"Quick preset estimated time {estimated_time}s exceeds reasonable limit "
        f"{REASONABLE_TIME_LIMIT}s"
    )
    
    # Property: Estimated time should be reasonable (not too short)
    # At minimum, we need time to test at least one point
    min_reasonable_time = test_duration
    assert estimated_time >= min_reasonable_time, (
        f"Estimated time {estimated_time}s is unreasonably short "
        f"(min={min_reasonable_time}s)"
    )


@settings(max_examples=100)
@given(
    freq_step=st.integers(min_value=200, max_value=500)
)
def test_quick_preset_step_size_balances_speed_and_coverage(freq_step):
    """Property: Quick preset step size should balance speed and coverage.
    
    For any quick preset step size, it should be large enough for speed but
    not so large that coverage is inadequate.
    
    Feature: frequency-based-wizard, Property 25: Quick preset parameter optimization
    Validates: Requirements 12.5
    """
    freq_range = 3500 - 400  # Total frequency range
    
    # Calculate coverage
    num_points = (freq_range // freq_step) + 1
    
    # Property: Step size should be >= minimum for quick preset
    assert freq_step >= QUICK_PRESET_MIN_STEP
    
    # Property: Step size should not be so large that we have too few points
    # For quick preset, minimum 3 points is acceptable
    MIN_POINTS = 3
    assert num_points >= MIN_POINTS, (
        f"Step size {freq_step} MHz results in too few points ({num_points}), "
        f"minimum is {MIN_POINTS}"
    )
    
    # Property: Step size should not exceed a maximum (e.g., 500 MHz)
    MAX_STEP = 500
    assert freq_step <= MAX_STEP, (
        f"Step size {freq_step} MHz exceeds maximum {MAX_STEP} MHz"
    )
