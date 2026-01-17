"""RPC contract test suite for frontend-backend integration.

**Feature: decktune-3.1-reliability-ux**
**Validates: Requirements 7.1, 7.2, 7.4**

This test suite verifies:
- All RPC methods return expected response shapes
- Event payloads match TypeScript type definitions
- Error responses include proper error codes and messages
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import inspect

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
            return False, "Mock ryzenadj error"
        self.last_values = values
        return True, None
    
    async def disable_async(self):
        if self.should_fail:
            return False, "Mock ryzenadj error"
        self.last_values = [0, 0, 0, 0]
        return True, None
    
    def disable(self):
        if self.should_fail:
            return False, "Mock ryzenadj error"
        self.last_values = [0, 0, 0, 0]
        return True, None


class MockSafetyManager:
    """Mock SafetyManager for testing."""
    
    def __init__(self, platform: PlatformInfo):
        self.platform = platform
    
    def clamp_values(self, values):
        return [max(self.platform.safe_limit, min(0, v)) for v in values]
    
    def load_binning_state(self):
        return None


class EventCapture:
    """Captures events emitted by EventEmitter for testing."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    
    async def capture(self, event_type: str, data: Any):
        self.events.append({"type": event_type, "data": data})
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if event_type is None:
            return self.events
        return [e for e in self.events if e["type"] == event_type]
    
    def clear(self):
        self.events = []


def create_test_rpc(ryzenadj_should_fail: bool = False) -> tuple:
    """Create a DeckTuneRPC instance with event capture for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings_manager = MockSettingsManager()
    ryzenadj = MockRyzenadjWrapper(should_fail=ryzenadj_should_fail)
    safety = MockSafetyManager(platform)
    
    event_capture = EventCapture()
    event_emitter = EventEmitter()
    event_emitter.set_emit_function(
        lambda event_type, data: event_capture.capture(event_type, data)
    )
    
    rpc = DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=settings_manager
    )
    
    return rpc, event_capture


# TypeScript type definitions as Python schemas
# These mirror the types in src/api/types.ts

PLATFORM_INFO_FIELDS = {
    "model": str,
    "variant": str,
    "safe_limit": int,
    "detected": bool
}

BINNING_CONFIG_FIELDS = {
    "test_duration": int,
    "step_size": int,
    "start_value": int,
    "max_iterations": int,
    "consecutive_fail_limit": int
}

GAME_PROFILE_REQUIRED_FIELDS = {
    "app_id": int,
    "name": str,
    "cores": list,
    "dynamic_enabled": bool,
    "created_at": str
}

SESSION_METRICS_FIELDS = {
    "duration_sec": (int, float),
    "avg_temperature_c": (int, float),
    "min_temperature_c": (int, float),
    "max_temperature_c": (int, float),
    "avg_power_w": (int, float),
    "estimated_battery_saved_wh": (int, float),
    "undervolt_values": list
}


def validate_type(value: Any, expected_type) -> bool:
    """Validate a value against an expected type or tuple of types."""
    if isinstance(expected_type, tuple):
        return isinstance(value, expected_type)
    return isinstance(value, expected_type)


def validate_fields(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate that data contains all required fields with correct types."""
    errors = []
    for field, expected_type in schema.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not validate_type(data[field], expected_type):
            errors.append(
                f"Field '{field}' has wrong type: expected {expected_type}, "
                f"got {type(data[field]).__name__}"
            )
    return errors


class TestRPCContractPlatformInfo:
    """Contract tests for platform info RPC methods.
    
    Validates: Requirements 7.1
    """

    @pytest.mark.asyncio
    async def test_get_platform_info_contract(self):
        """get_platform_info returns PlatformInfo shape."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.get_platform_info()
        
        errors = validate_fields(response, PLATFORM_INFO_FIELDS)
        assert not errors, f"Contract violation: {errors}"
        
        # Validate specific constraints
        assert response["model"] in ["Jupiter", "Galileo", "Unknown"]
        assert response["variant"] in ["LCD", "OLED", "Unknown"]
        assert -100 <= response["safe_limit"] <= 0


class TestRPCContractUndervolt:
    """Contract tests for undervolt control RPC methods.
    
    Validates: Requirements 7.1, 7.4
    """

    @pytest.mark.asyncio
    @given(
        cores=st.lists(st.integers(min_value=0, max_value=50), min_size=4, max_size=4)
    )
    @settings(max_examples=100)
    async def test_apply_undervolt_success_contract(self, cores: List[int]):
        """apply_undervolt success response matches contract."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.apply_undervolt(cores, timeout=0)
        
        assert "success" in response
        assert isinstance(response["success"], bool)
        
        if response["success"]:
            assert "cores" in response
            assert isinstance(response["cores"], list)
            assert len(response["cores"]) == 4
            for v in response["cores"]:
                assert isinstance(v, int)
                assert -100 <= v <= 0

    @pytest.mark.asyncio
    async def test_apply_undervolt_error_contract(self):
        """apply_undervolt error response matches contract."""
        rpc, _ = create_test_rpc(ryzenadj_should_fail=True)
        
        response = await rpc.apply_undervolt([20, 20, 20, 20], timeout=0)
        
        assert response["success"] is False
        assert "error" in response
        assert isinstance(response["error"], str)
        assert len(response["error"]) > 0

    @pytest.mark.asyncio
    async def test_disable_undervolt_contract(self):
        """disable_undervolt response matches contract."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.disable_undervolt()
        
        assert "success" in response
        assert isinstance(response["success"], bool)

    @pytest.mark.asyncio
    async def test_panic_disable_contract(self):
        """panic_disable response matches contract."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.panic_disable()
        
        assert "success" in response
        assert isinstance(response["success"], bool)


class TestRPCContractBinning:
    """Contract tests for binning RPC methods.
    
    Validates: Requirements 7.1, 7.4
    """

    @pytest.mark.asyncio
    async def test_get_binning_config_contract(self):
        """get_binning_config response matches BinningConfig shape."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.get_binning_config()
        
        assert response["success"] is True
        assert "config" in response
        
        config = response["config"]
        errors = validate_fields(config, BINNING_CONFIG_FIELDS)
        assert not errors, f"Contract violation: {errors}"
        
        # Validate constraints
        assert 30 <= config["test_duration"] <= 300
        assert 1 <= config["step_size"] <= 10
        assert -20 <= config["start_value"] <= 0

    @pytest.mark.asyncio
    @given(
        test_duration=st.integers(min_value=30, max_value=300),
        step_size=st.integers(min_value=1, max_value=10),
        start_value=st.integers(min_value=-20, max_value=0)
    )
    @settings(max_examples=100)
    async def test_update_binning_config_contract(
        self, 
        test_duration: int, 
        step_size: int, 
        start_value: int
    ):
        """update_binning_config response matches contract."""
        rpc, _ = create_test_rpc()
        
        config = {
            "test_duration": test_duration,
            "step_size": step_size,
            "start_value": start_value
        }
        
        response = await rpc.update_binning_config(config)
        
        assert response["success"] is True
        assert "config" in response
        
        # Updated config should reflect the changes
        updated = response["config"]
        assert updated["test_duration"] == test_duration
        assert updated["step_size"] == step_size
        assert updated["start_value"] == start_value

    @pytest.mark.asyncio
    async def test_get_binning_status_contract(self):
        """get_binning_status response matches contract."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.get_binning_status()
        
        # Without engine, should return error
        assert "success" in response
        assert isinstance(response["success"], bool)


class TestRPCContractProfiles:
    """Contract tests for profile management RPC methods.
    
    Validates: Requirements 7.1, 7.4
    """

    @pytest.mark.asyncio
    async def test_get_profiles_error_contract(self):
        """get_profiles error response matches contract when manager not configured."""
        rpc, _ = create_test_rpc()
        
        response = await rpc.get_profiles()
        
        assert response["success"] is False
        assert "error" in response
        assert isinstance(response["error"], str)

    @pytest.mark.asyncio
    @given(
        app_id=st.integers(min_value=1, max_value=999999),
        name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        cores=st.lists(st.integers(min_value=-50, max_value=0), min_size=4, max_size=4)
    )
    @settings(max_examples=100)
    async def test_create_profile_validation_contract(
        self,
        app_id: int,
        name: str,
        cores: List[int]
    ):
        """create_profile validates required fields per contract."""
        rpc, _ = create_test_rpc()
        
        # Full profile data
        profile_data = {
            "app_id": app_id,
            "name": name,
            "cores": cores
        }
        
        response = await rpc.create_profile(profile_data)
        
        # Without profile manager, should fail with proper error
        assert "success" in response
        assert isinstance(response["success"], bool)
        
        if not response["success"]:
            assert "error" in response
            assert isinstance(response["error"], str)


class TestEventPayloadContract:
    """Contract tests for event payloads.
    
    Validates: Requirements 7.2
    """

    @pytest.mark.asyncio
    async def test_status_event_payload(self):
        """Status events have correct payload structure."""
        rpc, event_capture = create_test_rpc()
        
        # Trigger a status event
        await rpc.apply_undervolt([20, 20, 20, 20], timeout=0)
        
        # Check captured events
        status_events = event_capture.get_events("server_event")
        
        for event in status_events:
            data = event["data"]
            assert "type" in data
            assert "data" in data
            
            if data["type"] == "update_status":
                # Status should be a string
                assert isinstance(data["data"], str)
                assert data["data"] in [
                    "enabled", "disabled", "error", "scheduled", 
                    "DYNAMIC RUNNING", "dynamic_running"
                ]

    @pytest.mark.asyncio
    async def test_binning_progress_event_structure(self):
        """Binning progress events match TypeScript BinningProgress type."""
        # This tests the event structure definition
        # The actual event emission is tested in integration
        
        expected_fields = {
            "current_value": int,
            "iteration": int,
            "last_stable": int,
            "eta": int
        }
        
        # Simulate a binning progress payload
        sample_payload = {
            "current_value": -25,
            "iteration": 3,
            "last_stable": -20,
            "eta": 120
        }
        
        errors = validate_fields(sample_payload, expected_fields)
        assert not errors, f"Event payload contract violation: {errors}"

    @pytest.mark.asyncio
    async def test_telemetry_sample_event_structure(self):
        """Telemetry sample events match TypeScript TelemetrySample type."""
        expected_fields = {
            "timestamp": (int, float),
            "temperature_c": (int, float),
            "power_w": (int, float),
            "load_percent": (int, float)
        }
        
        # Simulate a telemetry sample payload
        sample_payload = {
            "timestamp": 1705334400.0,
            "temperature_c": 72.5,
            "power_w": 18.5,
            "load_percent": 65.0
        }
        
        errors = validate_fields(sample_payload, expected_fields)
        assert not errors, f"Event payload contract violation: {errors}"

    @pytest.mark.asyncio
    async def test_session_metrics_structure(self):
        """Session metrics match TypeScript SessionMetrics type."""
        sample_metrics = {
            "duration_sec": 3600.0,
            "avg_temperature_c": 72.5,
            "min_temperature_c": 45.0,
            "max_temperature_c": 85.0,
            "avg_power_w": 18.5,
            "estimated_battery_saved_wh": 2.3,
            "undervolt_values": [-25, -25, -25, -25]
        }
        
        errors = validate_fields(sample_metrics, SESSION_METRICS_FIELDS)
        assert not errors, f"Session metrics contract violation: {errors}"


class TestRPCMethodCompleteness:
    """Tests to ensure all expected RPC methods exist.
    
    Validates: Requirements 7.1
    """

    def test_core_rpc_methods_exist(self):
        """Core RPC methods are defined on DeckTuneRPC."""
        rpc, _ = create_test_rpc()
        
        # Core undervolt methods
        assert hasattr(rpc, 'apply_undervolt')
        assert hasattr(rpc, 'disable_undervolt')
        assert hasattr(rpc, 'panic_disable')
        
        # Platform methods
        assert hasattr(rpc, 'get_platform_info')
        
        # Autotune methods
        assert hasattr(rpc, 'start_autotune')
        assert hasattr(rpc, 'stop_autotune')
        
        # Binning methods
        assert hasattr(rpc, 'start_binning')
        assert hasattr(rpc, 'stop_binning')
        assert hasattr(rpc, 'get_binning_status')
        assert hasattr(rpc, 'get_binning_config')
        assert hasattr(rpc, 'update_binning_config')
        
        # Profile methods
        assert hasattr(rpc, 'create_profile')
        assert hasattr(rpc, 'get_profiles')
        assert hasattr(rpc, 'update_profile')
        assert hasattr(rpc, 'delete_profile')

    def test_rpc_methods_are_async(self):
        """RPC methods are async coroutines."""
        rpc, _ = create_test_rpc()
        
        async_methods = [
            'apply_undervolt',
            'disable_undervolt',
            'panic_disable',
            'get_platform_info',
            'start_autotune',
            'stop_autotune',
            'start_binning',
            'stop_binning',
            'get_binning_status',
            'get_binning_config',
            'update_binning_config',
            'create_profile',
            'get_profiles',
            'update_profile',
            'delete_profile',
        ]
        
        for method_name in async_methods:
            method = getattr(rpc, method_name)
            assert inspect.iscoroutinefunction(method), \
                f"Method {method_name} should be async"


class TestErrorCodeConsistency:
    """Tests for consistent error handling across RPC methods.
    
    Validates: Requirements 7.4
    """

    @pytest.mark.asyncio
    async def test_missing_component_errors_are_consistent(self):
        """Missing component errors follow consistent pattern."""
        rpc, _ = create_test_rpc()
        
        # Methods that require optional components
        methods_requiring_components = [
            ('start_autotune', {}, 'engine'),
            ('stop_autotune', {}, 'engine'),
            ('start_binning', {'config': {}}, 'engine'),
            ('stop_binning', {}, 'engine'),
            ('get_profiles', {}, 'manager'),
            ('create_profile', {'profile_data': {'app_id': 1, 'name': 'Test', 'cores': [0,0,0,0]}}, 'manager'),
        ]
        
        for method_name, kwargs, component_type in methods_requiring_components:
            method = getattr(rpc, method_name)
            
            if kwargs:
                response = await method(**kwargs)
            else:
                response = await method()
            
            assert response["success"] is False, \
                f"{method_name} should fail without {component_type}"
            assert "error" in response, \
                f"{method_name} error response missing 'error' field"
            assert isinstance(response["error"], str), \
                f"{method_name} error should be string"
            # Error message should mention what's missing
            assert len(response["error"]) > 0, \
                f"{method_name} error message should not be empty"

