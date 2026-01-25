"""Property-based tests for frequency wizard RPC response completeness.

Feature: frequency-based-wizard, Property 13: RPC response completeness
Validates: Requirements 11.2

This test ensures that get_frequency_wizard_progress returns all required
fields in the response when the wizard is running.
"""

import pytest
from hypothesis import given, strategies as st, assume

from backend.tuning.frequency_wizard import WizardProgress


@given(
    running=st.booleans(),
    current_frequency=st.integers(min_value=400, max_value=3500),
    current_voltage=st.integers(min_value=-100, max_value=0),
    completed_points=st.integers(min_value=0, max_value=100),
    total_points=st.integers(min_value=1, max_value=100),
    estimated_remaining=st.integers(min_value=0, max_value=10000)
)
def test_wizard_progress_response_completeness(
    running: bool,
    current_frequency: int,
    current_voltage: int,
    completed_points: int,
    total_points: int,
    estimated_remaining: int
):
    """Property 13: RPC response completeness.
    
    For any wizard progress state, the to_dict() method should return
    all required fields: running, current_frequency, current_voltage,
    progress_percent, estimated_remaining, completed_points, total_points.
    
    Feature: frequency-based-wizard, Property 13: RPC response completeness
    Validates: Requirements 11.2
    """
    # Ensure completed_points doesn't exceed total_points
    assume(completed_points <= total_points)
    
    # Create wizard progress
    progress = WizardProgress(
        running=running,
        current_frequency=current_frequency,
        current_voltage=current_voltage,
        completed_points=completed_points,
        total_points=total_points,
        estimated_remaining=estimated_remaining
    )
    
    # Convert to dictionary (simulates RPC response)
    response = progress.to_dict()
    
    # Verify all required fields are present
    required_fields = {
        'running',
        'current_frequency',
        'current_voltage',
        'progress_percent',
        'estimated_remaining',
        'completed_points',
        'total_points'
    }
    
    assert set(response.keys()) == required_fields, \
        f"Response missing required fields. Expected {required_fields}, got {set(response.keys())}"
    
    # Verify field types
    assert isinstance(response['running'], bool)
    assert isinstance(response['current_frequency'], int)
    assert isinstance(response['current_voltage'], int)
    assert isinstance(response['progress_percent'], (int, float))
    assert isinstance(response['estimated_remaining'], int)
    assert isinstance(response['completed_points'], int)
    assert isinstance(response['total_points'], int)
    
    # Verify field values match input
    assert response['running'] == running
    assert response['current_frequency'] == current_frequency
    assert response['current_voltage'] == current_voltage
    assert response['completed_points'] == completed_points
    assert response['total_points'] == total_points
    assert response['estimated_remaining'] == estimated_remaining
    
    # Verify progress_percent is calculated correctly
    expected_progress = (completed_points / total_points) * 100.0
    assert abs(response['progress_percent'] - expected_progress) < 0.01, \
        f"Progress percent mismatch: expected {expected_progress}, got {response['progress_percent']}"


def test_wizard_progress_response_when_not_running():
    """Test response completeness when wizard is not running.
    
    Ensures all fields are present even when running=False.
    """
    progress = WizardProgress(
        running=False,
        current_frequency=0,
        current_voltage=0,
        completed_points=0,
        total_points=0,
        estimated_remaining=0
    )
    
    response = progress.to_dict()
    
    # Verify all required fields are present
    required_fields = {
        'running',
        'current_frequency',
        'current_voltage',
        'progress_percent',
        'estimated_remaining',
        'completed_points',
        'total_points'
    }
    
    assert set(response.keys()) == required_fields
    assert response['running'] is False
    assert response['progress_percent'] == 0.0


def test_wizard_progress_response_at_completion():
    """Test response completeness when wizard completes.
    
    Ensures progress_percent is 100.0 when completed_points == total_points.
    """
    progress = WizardProgress(
        running=True,
        current_frequency=3500,
        current_voltage=-25,
        completed_points=30,
        total_points=30,
        estimated_remaining=0
    )
    
    response = progress.to_dict()
    
    assert response['progress_percent'] == 100.0
    assert response['completed_points'] == response['total_points']
