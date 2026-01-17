"""Property tests for RPC error response structure.

**Feature: decktune-3.1-reliability-ux, Property 14: Error response structure**
**Validates: Requirements 7.4**

Property 14: Error response structure
For any RPC error response, the response SHALL contain an error code (string) 
and message (string).
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import Dict, Any, List

from backend.api.rpc import DeckTuneRPC
from backend.api.events import EventEmitter
from backend.platform.detect import PlatformInfo


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class MockRyzenadjWrapper:
    """Mock RyzenadjWrapper for testing."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.last_values = None
    
    async def diagnose(self):
        """Mock diagnose method for testing."""
        if self.should_fail:
            return {
                "available": False,
                "binary_found": False,
                "sudo_available": False,
                "test_run_success": False,
                "error": "Mock ryzenadj error"
            }
        return {
            "available": True,
            "binary_found": True,
            "sudo_available": True,
            "test_run_success": True,
            "error": None
        }
    
    async def apply_values_async(self, values):
        if self.should_fail:
            return False, "Mock ryzenadj error: command failed"
        self.last_values = values
        return True, None
    
    async def disable_async(self):
        if self.should_fail:
            return False, "Mock ryzenadj error: disable failed"
        self.last_values = [0, 0, 0, 0]
        return True, None
    
    def disable(self):
        if self.should_fail:
            return False, "Mock ryzenadj error: sync disable failed"
        self.last_values = [0, 0, 0, 0]
        return True, None


class MockSafetyManager:
    """Mock SafetyManager for testing."""
    
    def __init__(self, platform: PlatformInfo):
        self.platform = platform
    
    def clamp_values(self, values):
        """Clamp values to safe limits."""
        return [max(self.platform.safe_limit, min(0, v)) for v in values]
    
    def load_binning_state(self):
        return None


def create_test_rpc(ryzenadj_should_fail: bool = False) -> DeckTuneRPC:
    """Create a DeckTuneRPC instance for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings_manager = MockSettingsManager()
    ryzenadj = MockRyzenadjWrapper(should_fail=ryzenadj_should_fail)
    safety = MockSafetyManager(platform)
    event_emitter = EventEmitter()
    
    return DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=settings_manager
    )


def validate_error_response(response: Dict[str, Any]) -> List[str]:
    """Validate that an error response has proper structure.
    
    Args:
        response: The response dictionary to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Must have success field set to False
    if "success" not in response:
        errors.append("Error response missing 'success' field")
    elif response["success"] is not False:
        errors.append("Error response 'success' field should be False")
    
    # Must have error field with string message
    if "error" not in response:
        errors.append("Error response missing 'error' field")
    elif not isinstance(response["error"], str):
        errors.append(f"Error field should be string, got {type(response['error']).__name__}")
    elif len(response["error"]) == 0:
        errors.append("Error message should not be empty")
    
    return errors


class TestRPCErrorResponseStructure:
    """Property 14: Error response structure
    
    For any RPC error response, the response SHALL contain an error code (string) 
    and message (string).
    
    **Feature: decktune-3.1-reliability-ux, Property 14: Error response structure**
    **Validates: Requirements 7.4**
    """

    @pytest.mark.asyncio
    async def test_autotune_no_engine_error_structure(self):
        """start_autotune error response has proper structure when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.start_autotune()
        
        # Should fail because no engine configured
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_stop_autotune_no_engine_error_structure(self):
        """stop_autotune error response has proper structure when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.stop_autotune()
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_binning_no_engine_error_structure(self):
        """start_binning error response has proper structure when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.start_binning({})
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_stop_binning_no_engine_error_structure(self):
        """stop_binning error response has proper structure when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.stop_binning()
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_profile_no_manager_error_structure(self):
        """get_profiles error response has proper structure when manager not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.get_profiles()
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_create_profile_no_manager_error_structure(self):
        """create_profile error response has proper structure when manager not configured."""
        rpc = create_test_rpc()
        
        profile_data = {
            "app_id": 12345,
            "name": "Test Game",
            "cores": [-20, -20, -20, -20]
        }
        
        response = await rpc.create_profile(profile_data)
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_create_profile_missing_fields_error_structure(self):
        """create_profile error response has proper structure when required fields missing."""
        rpc = create_test_rpc()
        
        # Missing app_id
        response = await rpc.create_profile({"name": "Test", "cores": [-20, -20, -20, -20]})
        assert response["success"] is False
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"
        
        # Missing name
        response = await rpc.create_profile({"app_id": 123, "cores": [-20, -20, -20, -20]})
        assert response["success"] is False
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"
        
        # Missing cores
        response = await rpc.create_profile({"app_id": 123, "name": "Test"})
        assert response["success"] is False
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    @given(
        test_duration=st.integers(min_value=-100, max_value=29) | st.integers(min_value=301, max_value=1000)
    )
    @settings(max_examples=100)
    async def test_binning_config_invalid_duration_error_structure(self, test_duration: int):
        """update_binning_config error response has proper structure for invalid duration."""
        rpc = create_test_rpc()
        
        config = {
            "test_duration": test_duration,  # Invalid: must be 30-300
            "step_size": 5,
            "start_value": -10
        }
        
        response = await rpc.update_binning_config(config)
        
        assert response["success"] is False, \
            f"Expected failure for invalid test_duration={test_duration}"
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    @given(
        step_size=st.integers(min_value=-100, max_value=0) | st.integers(min_value=11, max_value=100)
    )
    @settings(max_examples=100)
    async def test_binning_config_invalid_step_error_structure(self, step_size: int):
        """update_binning_config error response has proper structure for invalid step_size."""
        rpc = create_test_rpc()
        
        config = {
            "test_duration": 60,
            "step_size": step_size,  # Invalid: must be 1-10
            "start_value": -10
        }
        
        response = await rpc.update_binning_config(config)
        
        assert response["success"] is False, \
            f"Expected failure for invalid step_size={step_size}"
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    @given(
        start_value=st.integers(min_value=-100, max_value=-21) | st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    async def test_binning_config_invalid_start_error_structure(self, start_value: int):
        """update_binning_config error response has proper structure for invalid start_value."""
        rpc = create_test_rpc()
        
        config = {
            "test_duration": 60,
            "step_size": 5,
            "start_value": start_value  # Invalid: must be -20 to 0
        }
        
        response = await rpc.update_binning_config(config)
        
        assert response["success"] is False, \
            f"Expected failure for invalid start_value={start_value}"
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_ryzenadj_failure_error_structure(self):
        """apply_undervolt error response has proper structure when ryzenadj fails."""
        rpc = create_test_rpc(ryzenadj_should_fail=True)
        
        response = await rpc.apply_undervolt([20, 20, 20, 20], timeout=0)
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_disable_undervolt_failure_error_structure(self):
        """disable_undervolt error response has proper structure when ryzenadj fails."""
        rpc = create_test_rpc(ryzenadj_should_fail=True)
        
        response = await rpc.disable_undervolt()
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_update_profile_no_manager_error_structure(self):
        """update_profile error response has proper structure when manager not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.update_profile(12345, {"name": "Updated Name"})
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_delete_profile_no_manager_error_structure(self):
        """delete_profile error response has proper structure when manager not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.delete_profile(12345)
        
        assert response["success"] is False
        
        errors = validate_error_response(response)
        assert not errors, f"Error response validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_error_messages_are_descriptive(self):
        """Error messages should be descriptive and helpful."""
        rpc = create_test_rpc()
        
        # Test various error scenarios
        error_scenarios = [
            (rpc.start_autotune, {}, "autotune"),
            (rpc.stop_autotune, {}, "autotune"),
            (rpc.start_binning, {"config": {}}, "binning"),
            (rpc.stop_binning, {}, "binning"),
            (rpc.get_profiles, {}, "profile"),
        ]
        
        for method, kwargs, expected_keyword in error_scenarios:
            if kwargs:
                response = await method(**kwargs)
            else:
                response = await method()
            
            if not response["success"]:
                error_msg = response.get("error", "")
                # Error message should be non-empty and somewhat descriptive
                assert len(error_msg) > 5, \
                    f"Error message too short for {method.__name__}: '{error_msg}'"

