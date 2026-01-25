"""Property-based tests for wizard progress calculation accuracy.

Feature: frequency-based-wizard, Property 11: Progress calculation accuracy
Validates: Requirements 4.3
"""

import pytest
from hypothesis import given, strategies as st, assume

from backend.tuning.frequency_wizard import WizardProgress


class TestProgressCalculation:
    """Test wizard progress calculation accuracy.
    
    Property 11: For any wizard execution state with completed_points and total_points,
    the progress percentage should equal (completed_points / total_points) * 100.
    """
    
    @given(
        completed_points=st.integers(min_value=0, max_value=1000),
        total_points=st.integers(min_value=1, max_value=1000)
    )
    def test_progress_percentage_formula(self, completed_points, total_points):
        """Test that progress percentage matches the formula."""
        # Ensure completed_points <= total_points
        assume(completed_points <= total_points)
        
        # Create progress tracker
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points
        )
        
        # Calculate expected percentage
        expected_percent = (completed_points / total_points) * 100.0
        
        # Get actual percentage
        actual_percent = progress.calculate_progress_percent()
        
        # Verify they match (within floating point tolerance)
        assert abs(actual_percent - expected_percent) < 0.001, (
            f"Progress percentage {actual_percent}% does not match expected "
            f"{expected_percent}% (completed={completed_points}, total={total_points})"
        )
    
    @given(
        completed_points=st.integers(min_value=0, max_value=1000),
        total_points=st.integers(min_value=1, max_value=1000)
    )
    def test_progress_percentage_in_valid_range(self, completed_points, total_points):
        """Test that progress percentage is always in [0, 100] range."""
        # Ensure completed_points <= total_points
        assume(completed_points <= total_points)
        
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points
        )
        
        percent = progress.calculate_progress_percent()
        
        assert 0.0 <= percent <= 100.0, (
            f"Progress percentage {percent}% is outside valid range [0, 100]"
        )
    
    @given(total_points=st.integers(min_value=1, max_value=1000))
    def test_progress_zero_when_no_points_completed(self, total_points):
        """Test that progress is 0% when no points are completed."""
        progress = WizardProgress(
            running=True,
            completed_points=0,
            total_points=total_points
        )
        
        percent = progress.calculate_progress_percent()
        
        assert percent == 0.0, (
            f"Progress should be 0% when no points completed, got {percent}%"
        )
    
    @given(total_points=st.integers(min_value=1, max_value=1000))
    def test_progress_hundred_when_all_points_completed(self, total_points):
        """Test that progress is 100% when all points are completed."""
        progress = WizardProgress(
            running=True,
            completed_points=total_points,
            total_points=total_points
        )
        
        percent = progress.calculate_progress_percent()
        
        assert percent == 100.0, (
            f"Progress should be 100% when all points completed, got {percent}%"
        )
    
    @given(
        completed_points=st.integers(min_value=1, max_value=999),
        total_points=st.integers(min_value=2, max_value=1000)
    )
    def test_progress_increases_monotonically(self, completed_points, total_points):
        """Test that progress increases as more points are completed."""
        # Ensure we have room to increment
        assume(completed_points < total_points)
        
        # Create progress at current state
        progress1 = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points
        )
        
        # Create progress with one more point completed
        progress2 = WizardProgress(
            running=True,
            completed_points=completed_points + 1,
            total_points=total_points
        )
        
        percent1 = progress1.calculate_progress_percent()
        percent2 = progress2.calculate_progress_percent()
        
        assert percent2 > percent1, (
            f"Progress should increase when more points completed: "
            f"{percent1}% -> {percent2}%"
        )
    
    def test_progress_zero_when_total_points_zero(self):
        """Test edge case where total_points is 0."""
        progress = WizardProgress(
            running=True,
            completed_points=0,
            total_points=0
        )
        
        percent = progress.calculate_progress_percent()
        
        # Should return 0 to avoid division by zero
        assert percent == 0.0, (
            f"Progress should be 0% when total_points is 0, got {percent}%"
        )
    
    @given(
        completed_points=st.integers(min_value=0, max_value=100),
        total_points=st.integers(min_value=1, max_value=100)
    )
    def test_progress_dict_contains_correct_percentage(self, completed_points, total_points):
        """Test that to_dict() includes the correct progress percentage."""
        assume(completed_points <= total_points)
        
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points,
            current_frequency=1000,
            current_voltage=-30,
            estimated_remaining=60
        )
        
        progress_dict = progress.to_dict()
        
        # Verify dict contains progress_percent
        assert 'progress_percent' in progress_dict, (
            "to_dict() should include 'progress_percent' field"
        )
        
        # Verify it matches the calculated value
        expected_percent = (completed_points / total_points) * 100.0
        actual_percent = progress_dict['progress_percent']
        
        assert abs(actual_percent - expected_percent) < 0.001, (
            f"progress_percent in dict {actual_percent}% does not match expected "
            f"{expected_percent}%"
        )
    
    @given(
        completed_points=st.integers(min_value=0, max_value=100),
        total_points=st.integers(min_value=1, max_value=100)
    )
    def test_progress_dict_contains_all_fields(self, completed_points, total_points):
        """Test that to_dict() includes all required fields."""
        assume(completed_points <= total_points)
        
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points,
            current_frequency=1000,
            current_voltage=-30,
            estimated_remaining=60
        )
        
        progress_dict = progress.to_dict()
        
        # Verify all required fields are present
        required_fields = [
            'running',
            'current_frequency',
            'current_voltage',
            'progress_percent',
            'estimated_remaining',
            'completed_points',
            'total_points'
        ]
        
        for field in required_fields:
            assert field in progress_dict, (
                f"to_dict() missing required field '{field}'"
            )
    
    @given(
        completed_points=st.integers(min_value=0, max_value=100),
        total_points=st.integers(min_value=1, max_value=100)
    )
    def test_progress_values_match_in_dict(self, completed_points, total_points):
        """Test that to_dict() values match the progress object values."""
        assume(completed_points <= total_points)
        
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points,
            current_frequency=1500,
            current_voltage=-25,
            estimated_remaining=120
        )
        
        progress_dict = progress.to_dict()
        
        # Verify values match
        assert progress_dict['running'] == progress.running
        assert progress_dict['completed_points'] == progress.completed_points
        assert progress_dict['total_points'] == progress.total_points
        assert progress_dict['current_frequency'] == progress.current_frequency
        assert progress_dict['current_voltage'] == progress.current_voltage
        assert progress_dict['estimated_remaining'] == progress.estimated_remaining
    
    @given(
        step_size=st.integers(min_value=1, max_value=10),
        total_points=st.integers(min_value=10, max_value=100)
    )
    def test_progress_increments_correctly(self, step_size, total_points):
        """Test that progress increments correctly when points are added."""
        progress = WizardProgress(
            running=True,
            completed_points=0,
            total_points=total_points
        )
        
        # Increment by step_size
        for i in range(1, min(step_size + 1, total_points + 1)):
            progress.completed_points = i
            
            expected_percent = (i / total_points) * 100.0
            actual_percent = progress.calculate_progress_percent()
            
            assert abs(actual_percent - expected_percent) < 0.001, (
                f"After {i} points, progress {actual_percent}% does not match "
                f"expected {expected_percent}%"
            )
    
    @given(
        completed_points=st.integers(min_value=0, max_value=50),
        total_points=st.integers(min_value=1, max_value=50)
    )
    def test_progress_percentage_precision(self, completed_points, total_points):
        """Test that progress percentage maintains reasonable precision."""
        assume(completed_points <= total_points)
        
        progress = WizardProgress(
            running=True,
            completed_points=completed_points,
            total_points=total_points
        )
        
        percent = progress.calculate_progress_percent()
        
        # Verify it's a float
        assert isinstance(percent, float), (
            f"Progress percentage should be float, got {type(percent)}"
        )
        
        # Verify it has reasonable precision (not excessive decimal places)
        # The formula should give us standard floating point precision
        expected = (completed_points / total_points) * 100.0
        assert percent == expected, (
            f"Progress percentage {percent} does not exactly match formula result {expected}"
        )
