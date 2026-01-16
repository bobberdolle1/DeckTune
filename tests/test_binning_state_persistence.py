"""Property tests for binning state persistence.

Feature: decktune-3.0-automation, Property 8: State file structure
Validates: Requirements 2.1

Property 8: State file structure
For any persisted binning state, the JSON must contain fields: active, current_value, 
iteration, last_stable, failed_values, timestamp
"""

import pytest
import os
import json
import tempfile
from hypothesis import given, strategies as st, settings

from backend.platform.detect import PlatformInfo
from backend.core.safety import SafetyManager, BinningState


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


def create_default_platform() -> PlatformInfo:
    """Create a default LCD platform for testing."""
    return PlatformInfo(model="Jupiter", variant="LCD", safe_limit=-30, detected=True)


# Strategy for binning state values
current_value_strategy = st.integers(min_value=-50, max_value=0)
last_stable_strategy = st.integers(min_value=-35, max_value=0)
iteration_strategy = st.integers(min_value=0, max_value=20)
failed_values_strategy = st.lists(st.integers(min_value=-60, max_value=-10), max_size=10)


class TestBinningStatePersistence:
    """Property 8: State file structure
    
    For any persisted binning state, the JSON must contain fields: active, current_value, 
    iteration, last_stable, failed_values, timestamp
    
    Validates: Requirements 2.1
    """

    def setup_method(self):
        """Set up test with a temporary file path."""
        # Use a temporary directory that works on all platforms
        self.temp_dir = tempfile.gettempdir()
        self.original_state_file = SafetyManager.BINNING_STATE_FILE
        # Override the class constant for testing
        SafetyManager.BINNING_STATE_FILE = os.path.join(self.temp_dir, "decktune_binning_state_test.json")
        
        # Clean up any existing test file
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
    
    def teardown_method(self):
        """Clean up binning state file after each test."""
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
        # Restore original path
        SafetyManager.BINNING_STATE_FILE = self.original_state_file

    @given(
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        iteration=iteration_strategy,
        failed_values=failed_values_strategy
    )
    @settings(max_examples=100)
    def test_persisted_state_contains_all_required_fields(
        self, 
        current_value: int, 
        last_stable: int, 
        iteration: int, 
        failed_values: list
    ):
        """Persisted binning state JSON contains all required fields."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Create binning state
        safety.create_binning_state(current_value, last_stable, iteration, failed_values)
        
        # Read the file directly
        assert os.path.exists(SafetyManager.BINNING_STATE_FILE), "State file should exist"
        
        with open(SafetyManager.BINNING_STATE_FILE, 'r') as f:
            data = json.load(f)
        
        # Verify all required fields are present
        required_fields = ['active', 'current_value', 'last_stable', 'iteration', 'failed_values', 'timestamp']
        for field in required_fields:
            assert field in data, f"Field '{field}' missing from persisted state"

    @given(
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        iteration=iteration_strategy,
        failed_values=failed_values_strategy
    )
    @settings(max_examples=100)
    def test_persisted_state_values_match_input(
        self, 
        current_value: int, 
        last_stable: int, 
        iteration: int, 
        failed_values: list
    ):
        """Persisted binning state values match the input values."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Create binning state
        safety.create_binning_state(current_value, last_stable, iteration, failed_values)
        
        # Read the file directly
        with open(SafetyManager.BINNING_STATE_FILE, 'r') as f:
            data = json.load(f)
        
        # Verify values match
        assert data['active'] is True, "Active should be True"
        assert data['current_value'] == current_value, f"current_value mismatch"
        assert data['last_stable'] == last_stable, f"last_stable mismatch"
        assert data['iteration'] == iteration, f"iteration mismatch"
        assert data['failed_values'] == failed_values, f"failed_values mismatch"
        assert isinstance(data['timestamp'], str), "timestamp should be a string"

    @given(
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        iteration=iteration_strategy,
        failed_values=failed_values_strategy
    )
    @settings(max_examples=100)
    def test_load_binning_state_returns_correct_values(
        self, 
        current_value: int, 
        last_stable: int, 
        iteration: int, 
        failed_values: list
    ):
        """Loading binning state returns a BinningState with correct values."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Create binning state
        safety.create_binning_state(current_value, last_stable, iteration, failed_values)
        
        # Load it back
        state = safety.load_binning_state()
        
        assert state is not None, "load_binning_state should return a BinningState"
        assert isinstance(state, BinningState), "Should return BinningState instance"
        assert state.active is True, "active should be True"
        assert state.current_value == current_value, f"current_value mismatch"
        assert state.last_stable == last_stable, f"last_stable mismatch"
        assert state.iteration == iteration, f"iteration mismatch"
        assert state.failed_values == failed_values, f"failed_values mismatch"
        assert isinstance(state.timestamp, str), "timestamp should be a string"

    @given(
        current_value=current_value_strategy,
        last_stable=last_stable_strategy,
        iteration=iteration_strategy,
        failed_values=failed_values_strategy
    )
    @settings(max_examples=100)
    def test_update_binning_state_overwrites_file(
        self, 
        current_value: int, 
        last_stable: int, 
        iteration: int, 
        failed_values: list
    ):
        """Updating binning state overwrites the existing file."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Create initial state
        safety.create_binning_state(-10, 0, 1, [])
        
        # Update with new values
        safety.update_binning_state(current_value, last_stable, iteration, failed_values)
        
        # Load and verify new values
        state = safety.load_binning_state()
        
        assert state is not None
        assert state.current_value == current_value, "Should have updated current_value"
        assert state.last_stable == last_stable, "Should have updated last_stable"
        assert state.iteration == iteration, "Should have updated iteration"
        assert state.failed_values == failed_values, "Should have updated failed_values"

    def test_clear_binning_state_removes_file(self):
        """Clearing binning state removes the state file."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Create state
        safety.create_binning_state(-10, 0, 1, [])
        assert os.path.exists(SafetyManager.BINNING_STATE_FILE), "File should exist after create"
        
        # Clear state
        safety.clear_binning_state()
        assert not os.path.exists(SafetyManager.BINNING_STATE_FILE), "File should not exist after clear"

    def test_load_binning_state_returns_none_when_file_missing(self):
        """Loading binning state returns None when file doesn't exist."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Ensure file doesn't exist
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
        
        # Load should return None
        state = safety.load_binning_state()
        assert state is None, "Should return None when file doesn't exist"

    def test_load_binning_state_returns_none_for_invalid_json(self):
        """Loading binning state returns None for invalid JSON."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Write invalid JSON
        with open(SafetyManager.BINNING_STATE_FILE, 'w') as f:
            f.write("{ invalid json }")
        
        # Load should return None
        state = safety.load_binning_state()
        assert state is None, "Should return None for invalid JSON"

    def test_load_binning_state_returns_none_for_missing_fields(self):
        """Loading binning state returns None when required fields are missing."""
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        
        # Write JSON with missing fields
        with open(SafetyManager.BINNING_STATE_FILE, 'w') as f:
            json.dump({"active": True, "current_value": -10}, f)
        
        # Load should return None
        state = safety.load_binning_state()
        assert state is None, "Should return None when required fields are missing"
