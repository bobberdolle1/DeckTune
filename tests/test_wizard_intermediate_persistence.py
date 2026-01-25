"""Property-based tests for wizard intermediate result persistence.

Feature: frequency-based-wizard, Property 24: Intermediate result persistence
Validates: Requirements 12.4
"""

import pytest
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings
from backend.tuning.frequency_curve import FrequencyPoint, FrequencyCurve


@settings(max_examples=100)
@given(
    core_id=st.integers(min_value=0, max_value=7),
    num_points=st.integers(min_value=1, max_value=20),
    frequencies=st.lists(
        st.integers(min_value=400, max_value=3500),
        min_size=1,
        max_size=20,
        unique=True
    ),
    voltages=st.lists(
        st.integers(min_value=-100, max_value=0),
        min_size=1,
        max_size=20
    )
)
def test_intermediate_results_can_be_saved_and_loaded(
    core_id, num_points, frequencies, voltages
):
    """Property 24: Intermediate result persistence.
    
    For any wizard execution, after each frequency point is completed, the
    partial results should be saved to storage to allow resumption after
    interruption.
    
    This test verifies that partial frequency curves can be serialized,
    saved, loaded, and deserialized without data loss.
    
    Feature: frequency-based-wizard, Property 24: Intermediate result persistence
    Validates: Requirements 12.4
    """
    # Ensure we have matching data
    num_points = min(num_points, len(frequencies), len(voltages))
    assume(num_points > 0)
    
    frequencies = sorted(frequencies[:num_points])
    voltages = voltages[:num_points]
    
    # Create partial frequency curve (simulating intermediate state)
    points = [
        FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=volt,
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + i
        )
        for i, (freq, volt) in enumerate(zip(frequencies, voltages))
    ]
    
    partial_curve = FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=1706198400.0,
        wizard_config={
            'freq_start': 400,
            'freq_end': 3500,
            'freq_step': 100
        }
    )
    
    # Serialize to JSON (simulating save)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
        json.dump(partial_curve.to_dict(), f)
    
    try:
        # Load from JSON (simulating resume)
        with open(temp_path, 'r') as f:
            loaded_data = json.load(f)
        
        loaded_curve = FrequencyCurve.from_dict(loaded_data)
        
        # Property: Loaded curve should match original
        assert loaded_curve.core_id == partial_curve.core_id
        assert len(loaded_curve.points) == len(partial_curve.points)
        assert loaded_curve.created_at == partial_curve.created_at
        
        # Verify each point
        for orig_point, loaded_point in zip(partial_curve.points, loaded_curve.points):
            assert loaded_point.frequency_mhz == orig_point.frequency_mhz
            assert loaded_point.voltage_mv == orig_point.voltage_mv
            assert loaded_point.stable == orig_point.stable
            assert loaded_point.test_duration == orig_point.test_duration
            assert loaded_point.timestamp == orig_point.timestamp
    
    finally:
        # Cleanup
        temp_path.unlink(missing_ok=True)


@settings(max_examples=100)
@given(
    num_completed=st.integers(min_value=1, max_value=15),
    num_total=st.integers(min_value=5, max_value=30)
)
def test_partial_curve_can_be_extended_after_resume(num_completed, num_total):
    """Property: Partial curves should be extendable after loading.
    
    For any partial frequency curve loaded from storage, it should be possible
    to add additional frequency points and continue the wizard execution.
    
    Feature: frequency-based-wizard, Property 24: Intermediate result persistence
    Validates: Requirements 12.4
    """
    assume(num_completed < num_total)
    
    # Create initial partial curve
    initial_points = [
        FrequencyPoint(
            frequency_mhz=400 + i * 100,
            voltage_mv=-30 - i,
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + i
        )
        for i in range(num_completed)
    ]
    
    partial_curve = FrequencyCurve(
        core_id=0,
        points=initial_points,
        created_at=1706198400.0,
        wizard_config={'freq_start': 400, 'freq_end': 3500, 'freq_step': 100}
    )
    
    # Simulate saving and loading
    curve_dict = partial_curve.to_dict()
    loaded_curve = FrequencyCurve.from_dict(curve_dict)
    
    # Add more points (simulating resume)
    additional_points = [
        FrequencyPoint(
            frequency_mhz=400 + (num_completed + i) * 100,
            voltage_mv=-30 - (num_completed + i),
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + num_completed + i
        )
        for i in range(num_total - num_completed)
    ]
    
    # Extend the loaded curve
    extended_curve = FrequencyCurve(
        core_id=loaded_curve.core_id,
        points=loaded_curve.points + additional_points,
        created_at=loaded_curve.created_at,
        wizard_config=loaded_curve.wizard_config
    )
    
    # Property: Extended curve should have all points
    assert len(extended_curve.points) == num_total
    
    # Property: Original points should be preserved
    for i in range(num_completed):
        assert extended_curve.points[i].frequency_mhz == initial_points[i].frequency_mhz
        assert extended_curve.points[i].voltage_mv == initial_points[i].voltage_mv
    
    # Property: New points should be appended
    for i in range(num_total - num_completed):
        idx = num_completed + i
        assert extended_curve.points[idx].frequency_mhz == additional_points[i].frequency_mhz
        assert extended_curve.points[idx].voltage_mv == additional_points[i].voltage_mv


@settings(max_examples=100)
@given(
    save_interval=st.integers(min_value=1, max_value=5),
    total_points=st.integers(min_value=5, max_value=20)
)
def test_periodic_saves_preserve_progress(save_interval, total_points):
    """Property: Periodic saves should preserve wizard progress.
    
    For any wizard execution that saves intermediate results at regular
    intervals, the saved state should accurately reflect the progress made.
    
    Feature: frequency-based-wizard, Property 24: Intermediate result persistence
    Validates: Requirements 12.4
    """
    assume(save_interval < total_points)
    
    # Simulate wizard execution with periodic saves
    all_points = []
    saved_states = []
    
    for i in range(total_points):
        # Add a point
        point = FrequencyPoint(
            frequency_mhz=400 + i * 100,
            voltage_mv=-30 - i,
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + i
        )
        all_points.append(point)
        
        # Save periodically
        if (i + 1) % save_interval == 0 or i == total_points - 1:
            curve = FrequencyCurve(
                core_id=0,
                points=all_points.copy(),
                created_at=1706198400.0,
                wizard_config={'freq_start': 400, 'freq_end': 3500, 'freq_step': 100}
            )
            saved_states.append(curve.to_dict())
    
    # Property: Each saved state should have the correct number of points
    expected_saves = (total_points + save_interval - 1) // save_interval
    assert len(saved_states) >= expected_saves
    
    # Property: Each save should have more or equal points than the previous
    for i in range(1, len(saved_states)):
        prev_points = len(saved_states[i-1]['points'])
        curr_points = len(saved_states[i]['points'])
        assert curr_points >= prev_points, (
            f"Save {i} should have >= points than save {i-1}: "
            f"prev={prev_points}, curr={curr_points}"
        )
    
    # Property: Final save should have all points
    final_save = saved_states[-1]
    assert len(final_save['points']) == total_points


@settings(max_examples=100)
@given(
    interruption_point=st.integers(min_value=1, max_value=15),
    total_points=st.integers(min_value=10, max_value=30)
)
def test_resume_from_interruption_continues_correctly(interruption_point, total_points):
    """Property: Resuming from interruption should continue from last saved point.
    
    For any wizard execution interrupted at a specific point, resuming should
    continue from the last saved frequency point without re-testing completed
    frequencies.
    
    Feature: frequency-based-wizard, Property 24: Intermediate result persistence
    Validates: Requirements 12.4
    """
    assume(interruption_point < total_points)
    
    # Simulate wizard execution up to interruption
    completed_points = [
        FrequencyPoint(
            frequency_mhz=400 + i * 100,
            voltage_mv=-30 - i,
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + i
        )
        for i in range(interruption_point)
    ]
    
    # Save state at interruption
    interrupted_curve = FrequencyCurve(
        core_id=0,
        points=completed_points,
        created_at=1706198400.0,
        wizard_config={
            'freq_start': 400,
            'freq_end': 400 + (total_points - 1) * 100,
            'freq_step': 100
        }
    )
    
    # Serialize and deserialize (simulating save/load)
    saved_data = interrupted_curve.to_dict()
    resumed_curve = FrequencyCurve.from_dict(saved_data)
    
    # Property: Resumed curve should have all completed points
    assert len(resumed_curve.points) == interruption_point
    
    # Property: Next frequency to test should be after last completed
    if len(resumed_curve.points) > 0:
        last_freq = resumed_curve.points[-1].frequency_mhz
        next_freq = last_freq + interrupted_curve.wizard_config['freq_step']
        
        # Verify we can determine the next frequency correctly
        expected_next = 400 + interruption_point * 100
        assert next_freq == expected_next, (
            f"Next frequency after resume should be {expected_next}, got {next_freq}"
        )
    
    # Property: Wizard config should be preserved for resume
    assert resumed_curve.wizard_config == interrupted_curve.wizard_config


@settings(max_examples=100)
@given(
    num_points=st.integers(min_value=1, max_value=20),
    core_id=st.integers(min_value=0, max_value=7)
)
def test_intermediate_save_maintains_curve_validity(num_points, core_id):
    """Property: Intermediate saves should maintain curve validity.
    
    For any partial frequency curve saved during wizard execution, the saved
    curve should pass validation checks (sorted frequencies, valid voltage range).
    
    Feature: frequency-based-wizard, Property 24: Intermediate result persistence
    Validates: Requirements 12.4
    """
    # Create partial curve with random valid data
    frequencies = sorted([400 + i * 100 for i in range(num_points)])
    
    points = [
        FrequencyPoint(
            frequency_mhz=freq,
            voltage_mv=-30 - i,
            stable=True,
            test_duration=30,
            timestamp=1706198400.0 + i
        )
        for i, freq in enumerate(frequencies)
    ]
    
    partial_curve = FrequencyCurve(
        core_id=core_id,
        points=points,
        created_at=1706198400.0,
        wizard_config={'freq_start': 400, 'freq_end': 3500, 'freq_step': 100}
    )
    
    # Save and load
    saved_data = partial_curve.to_dict()
    loaded_curve = FrequencyCurve.from_dict(saved_data)
    
    # Property: Loaded curve should pass validation
    try:
        loaded_curve.validate()
        validation_passed = True
    except Exception as e:
        validation_passed = False
        pytest.fail(f"Loaded curve failed validation: {e}")
    
    assert validation_passed, "Intermediate save should maintain curve validity"
    
    # Property: Frequencies should remain sorted
    loaded_freqs = [p.frequency_mhz for p in loaded_curve.points]
    assert loaded_freqs == sorted(loaded_freqs), "Frequencies should remain sorted"
    
    # Property: Voltages should remain in valid range
    for point in loaded_curve.points:
        assert -100 <= point.voltage_mv <= 0, (
            f"Voltage {point.voltage_mv} outside valid range [-100, 0]"
        )
