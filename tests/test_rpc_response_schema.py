"""Property tests for RPC response schema compliance.

**Feature: decktune-3.1-reliability-ux, Property 13: RPC response schema compliance**
**Validates: Requirements 7.1**

Property 13: RPC response schema compliance
For any RPC method call, the response SHALL match the expected schema 
with all required fields present.
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from backend.api.rpc import DeckTuneRPC
from backend.api.events import EventEmitter
from backend.core.ryzenadj import RyzenadjWrapper
from backend.core.safety import SafetyManager
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
    
    def __init__(self):
        self.last_values = None
    
    async def apply_values_async(self, values):
        self.last_values = values
        return True, None
    
    async def disable_async(self):
        self.last_values = [0, 0, 0, 0]
        return True, None
    
    def disable(self):
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


def create_test_rpc() -> DeckTuneRPC:
    """Create a DeckTuneRPC instance for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings_manager = MockSettingsManager()
    ryzenadj = MockRyzenadjWrapper()
    safety = MockSafetyManager(platform)
    event_emitter = EventEmitter()
    
    return DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=settings_manager
    )


# Schema definitions for RPC responses
# These define the required fields and their types for each response type

PLATFORM_INFO_SCHEMA = {
    "model": str,
    "variant": str,
    "safe_limit": int,
    "detected": bool
}

SUCCESS_RESPONSE_SCHEMA = {
    "success": bool
}

UNDERVOLT_RESPONSE_SCHEMA = {
    "success": bool,
    # Optional: "cores" (list), "error" (str)
}

BINNING_STATUS_SCHEMA = {
    "success": bool,
    "running": bool
}

BINNING_CONFIG_SCHEMA = {
    "success": bool,
    "config": dict
}


def validate_schema(response: Dict[str, Any], schema: Dict[str, type]) -> List[str]:
    """Validate a response against a schema.
    
    Args:
        response: The response dictionary to validate
        schema: Dictionary mapping field names to expected types
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    for field, expected_type in schema.items():
        if field not in response:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(response[field], expected_type):
            errors.append(
                f"Field '{field}' has wrong type: expected {expected_type.__name__}, "
                f"got {type(response[field]).__name__}"
            )
    
    return errors


class TestRPCResponseSchemaCompliance:
    """Property 13: RPC response schema compliance
    
    For any RPC method call, the response SHALL match the expected schema 
    with all required fields present.
    
    **Feature: decktune-3.1-reliability-ux, Property 13: RPC response schema compliance**
    **Validates: Requirements 7.1**
    """

    @pytest.mark.asyncio
    async def test_get_platform_info_schema(self):
        """get_platform_info returns response matching PlatformInfo schema."""
        rpc = create_test_rpc()
        
        response = await rpc.get_platform_info()
        
        errors = validate_schema(response, PLATFORM_INFO_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"
        
        # Additional type checks
        assert isinstance(response["model"], str)
        assert isinstance(response["variant"], str)
        assert isinstance(response["safe_limit"], int)
        assert isinstance(response["detected"], bool)

    @pytest.mark.asyncio
    @given(
        cores=st.lists(
            st.integers(min_value=0, max_value=50),
            min_size=4,
            max_size=4
        )
    )
    @settings(max_examples=100)
    async def test_apply_undervolt_schema(self, cores: List[int]):
        """apply_undervolt returns response with success field."""
        rpc = create_test_rpc()
        
        response = await rpc.apply_undervolt(cores, timeout=0)
        
        # Must have success field
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool), "success must be boolean"
        
        # If successful, must have cores field
        if response["success"]:
            assert "cores" in response, "Successful response missing 'cores' field"
            assert isinstance(response["cores"], list), "cores must be a list"
            assert len(response["cores"]) == 4, "cores must have 4 elements"

    @pytest.mark.asyncio
    async def test_disable_undervolt_schema(self):
        """disable_undervolt returns response with success field."""
        rpc = create_test_rpc()
        
        response = await rpc.disable_undervolt()
        
        errors = validate_schema(response, SUCCESS_RESPONSE_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_panic_disable_schema(self):
        """panic_disable returns response with success field."""
        rpc = create_test_rpc()
        
        response = await rpc.panic_disable()
        
        errors = validate_schema(response, SUCCESS_RESPONSE_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_start_autotune_schema_no_engine(self):
        """start_autotune returns error response when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.start_autotune()
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)
        
        # When engine not configured, should have error
        if not response["success"]:
            assert "error" in response, "Failed response missing 'error' field"
            assert isinstance(response["error"], str)

    @pytest.mark.asyncio
    async def test_stop_autotune_schema_no_engine(self):
        """stop_autotune returns error response when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.stop_autotune()
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)
        
        if not response["success"]:
            assert "error" in response, "Failed response missing 'error' field"

    @pytest.mark.asyncio
    async def test_get_binning_status_schema_no_engine(self):
        """get_binning_status returns error response when engine not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.get_binning_status()
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)

    @pytest.mark.asyncio
    async def test_get_binning_config_schema(self):
        """get_binning_config returns response with config field."""
        rpc = create_test_rpc()
        
        response = await rpc.get_binning_config()
        
        errors = validate_schema(response, BINNING_CONFIG_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"
        
        # Config should have expected fields
        config = response["config"]
        assert "test_duration" in config
        assert "step_size" in config
        assert "start_value" in config

    @pytest.mark.asyncio
    @given(
        test_duration=st.integers(min_value=30, max_value=300),
        step_size=st.integers(min_value=1, max_value=10),
        start_value=st.integers(min_value=-20, max_value=0)
    )
    @settings(max_examples=100)
    async def test_update_binning_config_schema(
        self, 
        test_duration: int, 
        step_size: int, 
        start_value: int
    ):
        """update_binning_config returns response with success and config fields."""
        rpc = create_test_rpc()
        
        config = {
            "test_duration": test_duration,
            "step_size": step_size,
            "start_value": start_value
        }
        
        response = await rpc.update_binning_config(config)
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)
        
        if response["success"]:
            assert "config" in response, "Successful response missing 'config' field"
            assert isinstance(response["config"], dict)

    @pytest.mark.asyncio
    async def test_get_profiles_schema_no_manager(self):
        """get_profiles returns error response when manager not configured."""
        rpc = create_test_rpc()
        
        response = await rpc.get_profiles()
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)
        
        if not response["success"]:
            assert "error" in response, "Failed response missing 'error' field"

    @pytest.mark.asyncio
    @given(
        app_id=st.integers(min_value=1, max_value=999999),
        name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S'))),
        cores=st.lists(st.integers(min_value=-50, max_value=0), min_size=4, max_size=4)
    )
    @settings(max_examples=100)
    async def test_create_profile_schema_no_manager(
        self,
        app_id: int,
        name: str,
        cores: List[int]
    ):
        """create_profile returns error response when manager not configured."""
        rpc = create_test_rpc()
        
        profile_data = {
            "app_id": app_id,
            "name": name,
            "cores": cores
        }
        
        response = await rpc.create_profile(profile_data)
        
        assert "success" in response, "Response missing 'success' field"
        assert isinstance(response["success"], bool)
        
        # Without profile manager, should fail with error
        if not response["success"]:
            assert "error" in response, "Failed response missing 'error' field"
            assert isinstance(response["error"], str)

    @pytest.mark.asyncio
    async def test_all_responses_have_success_field(self):
        """All RPC methods return responses with a success field."""
        rpc = create_test_rpc()
        
        # Test methods that don't require special setup
        methods_to_test = [
            ("get_binning_config", {}),
            ("get_binning_status", {}),
            ("get_profiles", {}),
        ]
        
        for method_name, kwargs in methods_to_test:
            method = getattr(rpc, method_name)
            response = await method(**kwargs)
            
            assert "success" in response, \
                f"Method {method_name} response missing 'success' field"
            assert isinstance(response["success"], bool), \
                f"Method {method_name} 'success' field is not boolean"

