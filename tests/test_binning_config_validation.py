"""Property-based tests for binning configuration validation.

Feature: decktune-3.0-automation, Binning Configuration
Property 41: Test duration validation
Property 42: Step size validation
Property 43: Start value validation
Validates: Requirements 10.2, 10.3, 10.4
"""

import pytest
from hypothesis import given, strategies as st


class MockSettings:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.data = {}
    
    def getSetting(self, key):
        return self.data.get(key)
    
    def setSetting(self, key, value):
        self.data[key] = value


class MockPlatform:
    """Mock platform info for testing."""
    
    def __init__(self):
        self.model = "Jupiter"
        self.variant = "LCD"
        self.safe_limit = -30
        self.detected = True


def create_mock_rpc():
    """Create a mock RPC instance for testing."""
    from backend.api.rpc import DeckTuneRPC
    from backend.api.events import EventEmitter
    
    platform = MockPlatform()
    settings = MockSettings()
    event_emitter = EventEmitter()
    
    rpc = DeckTuneRPC(
        platform=platform,
        ryzenadj=None,
        safety=None,
        event_emitter=event_emitter,
        settings_manager=settings
    )
    
    return rpc


# Property 41: Test duration validation
# For any test duration input, the value must be clamped to [30, 300] seconds
@given(test_duration=st.integers(min_value=-1000, max_value=1000))
@pytest.mark.asyncio
async def test_property_41_test_duration_validation(test_duration):
    """Property 41: Test duration validation.
    
    For any test duration input, values outside [30, 300] should be rejected.
    Validates: Requirements 10.2
    """
    mock_rpc = create_mock_rpc()
    config = {"test_duration": test_duration}
    result = await mock_rpc.update_binning_config(config)
    
    if 30 <= test_duration <= 300:
        # Valid range - should succeed
        assert result["success"] is True
        assert result["config"]["test_duration"] == test_duration
    else:
        # Invalid range - should fail
        assert result["success"] is False
        assert "error" in result
        assert "test_duration" in result["error"]


# Property 42: Step size validation
# For any step size input, the value must be clamped to [1, 10] mV
@given(step_size=st.integers(min_value=-100, max_value=100))
@pytest.mark.asyncio
async def test_property_42_step_size_validation(step_size):
    """Property 42: Step size validation.
    
    For any step size input, values outside [1, 10] should be rejected.
    Validates: Requirements 10.3
    """
    mock_rpc = create_mock_rpc()
    config = {"step_size": step_size}
    result = await mock_rpc.update_binning_config(config)
    
    if 1 <= step_size <= 10:
        # Valid range - should succeed
        assert result["success"] is True
        assert result["config"]["step_size"] == step_size
    else:
        # Invalid range - should fail
        assert result["success"] is False
        assert "error" in result
        assert "step_size" in result["error"]


# Property 43: Start value validation
# For any start value input, the value must be clamped to [-20, 0] mV
@given(start_value=st.integers(min_value=-100, max_value=100))
@pytest.mark.asyncio
async def test_property_43_start_value_validation(start_value):
    """Property 43: Start value validation.
    
    For any start value input, values outside [-20, 0] should be rejected.
    Validates: Requirements 10.4
    """
    mock_rpc = create_mock_rpc()
    config = {"start_value": start_value}
    result = await mock_rpc.update_binning_config(config)
    
    if -20 <= start_value <= 0:
        # Valid range - should succeed
        assert result["success"] is True
        assert result["config"]["start_value"] == start_value
    else:
        # Invalid range - should fail
        assert result["success"] is False
        assert "error" in result
        assert "start_value" in result["error"]


# Combined property test: Multiple config updates
@given(
    test_duration=st.integers(min_value=30, max_value=300),
    step_size=st.integers(min_value=1, max_value=10),
    start_value=st.integers(min_value=-20, max_value=0)
)
@pytest.mark.asyncio
async def test_combined_config_validation(test_duration, step_size, start_value):
    """Test that all valid config values can be set together.
    
    For any valid combination of config values, the update should succeed
    and all values should be persisted correctly.
    """
    mock_rpc = create_mock_rpc()
    config = {
        "test_duration": test_duration,
        "step_size": step_size,
        "start_value": start_value
    }
    
    result = await mock_rpc.update_binning_config(config)
    
    assert result["success"] is True
    assert result["config"]["test_duration"] == test_duration
    assert result["config"]["step_size"] == step_size
    assert result["config"]["start_value"] == start_value
    
    # Verify persistence
    saved_config = await mock_rpc.get_binning_config()
    assert saved_config["success"] is True
    assert saved_config["config"]["test_duration"] == test_duration
    assert saved_config["config"]["step_size"] == step_size
    assert saved_config["config"]["start_value"] == start_value
