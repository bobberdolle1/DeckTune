"""Property tests for undervolt status invariant.

Feature: decktune-critical-fixes, Property 2: Status Invariant
Validates: Requirements 1.3

Property 2: Инвариант статуса после применения undervolt
For any valid undervolt values, after successful application the system status
must be "enabled" and saved values must match applied values (with clamping).
"""

import asyncio
from typing import List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, strategies as st, settings, assume


# Strategy for undervolt values (-100 to 0)
undervolt_value = st.integers(min_value=-100, max_value=0)

# Strategy for 4 core values
core_values = st.lists(undervolt_value, min_size=4, max_size=4)


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def setSetting(self, key: str, value) -> None:
        self._settings[key] = value
    
    def getSetting(self, key: str, default=None):
        return self._settings.get(key, default)


class MockEventEmitter:
    """Mock event emitter for testing."""
    
    def __init__(self):
        self.last_status = None
        self.status_history = []
    
    async def emit_status(self, status: str) -> None:
        self.last_status = status
        self.status_history.append(status)


class MockRyzenadjWrapper:
    """Mock ryzenadj wrapper for testing."""
    
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.applied_values: Optional[List[int]] = None
        self._last_commands = []
    
    async def diagnose(self):
        return {
            "binary_exists": True,
            "binary_executable": True,
            "sudo_available": True,
            "test_command_result": "OK",
            "error": None
        }
    
    async def apply_values_async(self, cores: List[int]) -> Tuple[bool, Optional[str]]:
        self.applied_values = cores
        if self.should_succeed:
            return True, None
        return False, "Mock error"
    
    def get_last_commands(self) -> List[str]:
        return self._last_commands


class MockSafetyManager:
    """Mock safety manager for testing."""
    
    def __init__(self, safe_limit: int = -50):
        self.safe_limit = safe_limit
    
    def clamp_values(self, cores: List[int]) -> List[int]:
        """Clamp values to safe limit."""
        return [max(v, self.safe_limit) for v in cores]


class TestUndervoltStatusInvariant:
    """Property 2: Инвариант статуса после применения undervolt
    
    For any valid undervolt values, after successful application:
    - Status must be "enabled"
    - Saved values must match applied values (with clamping)
    
    Feature: decktune-critical-fixes, Property 2: Status Invariant
    Validates: Requirements 1.3
    """

    @pytest.mark.asyncio
    @given(cores=core_values)
    @settings(max_examples=100)
    async def test_status_enabled_after_successful_apply(self, cores: List[int]):
        """
        Property 2: After successful undervolt application, status is "enabled".
        
        Feature: decktune-critical-fixes, Property 2: Status Invariant
        **Validates: Requirements 1.3**
        """
        # Setup mocks
        settings_manager = MockSettingsManager()
        event_emitter = MockEventEmitter()
        ryzenadj = MockRyzenadjWrapper(should_succeed=True)
        safety = MockSafetyManager(safe_limit=-50)
        
        # Import and create RPC handler
        from backend.api.rpc import DeckTuneRPC
        from backend.platform.detect import PlatformInfo
        
        platform = PlatformInfo(
            model="Jupiter",
            variant="LCD",
            safe_limit=-50,
            detected=True
        )
        
        rpc = DeckTuneRPC(
            platform=platform,
            ryzenadj=ryzenadj,
            safety=safety,
            event_emitter=event_emitter,
            settings_manager=settings_manager
        )
        
        # Apply undervolt
        result = await rpc.apply_undervolt(cores, timeout=0)
        
        # Verify status invariant
        assert result["success"] is True, f"Apply should succeed, got error: {result.get('error')}"
        assert settings_manager.getSetting("status") == "enabled", \
            f"Status should be 'enabled', got {settings_manager.getSetting('status')}"
        assert event_emitter.last_status == "enabled", \
            f"Event status should be 'enabled', got {event_emitter.last_status}"

    @pytest.mark.asyncio
    @given(cores=core_values)
    @settings(max_examples=100)
    async def test_saved_values_match_clamped_applied(self, cores: List[int]):
        """
        Property 2: Saved values match applied values (with clamping).
        
        Feature: decktune-critical-fixes, Property 2: Status Invariant
        **Validates: Requirements 1.3**
        """
        # Setup mocks
        settings_manager = MockSettingsManager()
        event_emitter = MockEventEmitter()
        ryzenadj = MockRyzenadjWrapper(should_succeed=True)
        safe_limit = -50
        safety = MockSafetyManager(safe_limit=safe_limit)
        
        # Import and create RPC handler
        from backend.api.rpc import DeckTuneRPC
        from backend.platform.detect import PlatformInfo
        
        platform = PlatformInfo(
            model="Jupiter",
            variant="LCD",
            safe_limit=safe_limit,
            detected=True
        )
        
        rpc = DeckTuneRPC(
            platform=platform,
            ryzenadj=ryzenadj,
            safety=safety,
            event_emitter=event_emitter,
            settings_manager=settings_manager
        )
        
        # Apply undervolt
        result = await rpc.apply_undervolt(cores, timeout=0)
        
        # Calculate expected clamped values
        negated_cores = [-abs(v) if v > 0 else v for v in cores]
        expected_clamped = [max(v, safe_limit) for v in negated_cores]
        
        # Verify saved values match clamped values
        saved_cores = settings_manager.getSetting("cores")
        assert saved_cores == expected_clamped, \
            f"Saved cores {saved_cores} should match clamped {expected_clamped}"
        
        # Verify returned cores match
        assert result["cores"] == expected_clamped, \
            f"Returned cores {result['cores']} should match clamped {expected_clamped}"

    @pytest.mark.asyncio
    @given(cores=core_values)
    @settings(max_examples=100)
    async def test_status_error_on_failure(self, cores: List[int]):
        """
        Property 2 (inverse): On failure, status should be "error".
        
        Feature: decktune-critical-fixes, Property 2: Status Invariant
        **Validates: Requirements 1.3**
        """
        # Setup mocks with failure
        settings_manager = MockSettingsManager()
        event_emitter = MockEventEmitter()
        ryzenadj = MockRyzenadjWrapper(should_succeed=False)
        safety = MockSafetyManager(safe_limit=-50)
        
        # Import and create RPC handler
        from backend.api.rpc import DeckTuneRPC
        from backend.platform.detect import PlatformInfo
        
        platform = PlatformInfo(
            model="Jupiter",
            variant="LCD",
            safe_limit=-50,
            detected=True
        )
        
        rpc = DeckTuneRPC(
            platform=platform,
            ryzenadj=ryzenadj,
            safety=safety,
            event_emitter=event_emitter,
            settings_manager=settings_manager
        )
        
        # Apply undervolt (should fail)
        result = await rpc.apply_undervolt(cores, timeout=0)
        
        # Verify failure handling
        assert result["success"] is False, "Apply should fail"
        assert "error" in result, "Result should contain error"
        assert event_emitter.last_status == "error", \
            f"Event status should be 'error', got {event_emitter.last_status}"

    @pytest.mark.asyncio
    async def test_known_values_status_invariant(self):
        """Test with known values for verification."""
        # Setup mocks
        settings_manager = MockSettingsManager()
        event_emitter = MockEventEmitter()
        ryzenadj = MockRyzenadjWrapper(should_succeed=True)
        safety = MockSafetyManager(safe_limit=-50)
        
        # Import and create RPC handler
        from backend.api.rpc import DeckTuneRPC
        from backend.platform.detect import PlatformInfo
        
        platform = PlatformInfo(
            model="Jupiter",
            variant="LCD",
            safe_limit=-50,
            detected=True
        )
        
        rpc = DeckTuneRPC(
            platform=platform,
            ryzenadj=ryzenadj,
            safety=safety,
            event_emitter=event_emitter,
            settings_manager=settings_manager
        )
        
        # Test case 1: Values within safe limit
        result = await rpc.apply_undervolt([-30, -30, -30, -30], timeout=0)
        assert result["success"] is True
        assert result["cores"] == [-30, -30, -30, -30]
        assert settings_manager.getSetting("status") == "enabled"
        
        # Test case 2: Values exceeding safe limit (should be clamped)
        result = await rpc.apply_undervolt([-60, -70, -80, -90], timeout=0)
        assert result["success"] is True
        assert result["cores"] == [-50, -50, -50, -50]  # All clamped to -50
        
        # Test case 3: Positive values (should be negated)
        result = await rpc.apply_undervolt([30, 30, 30, 30], timeout=0)
        assert result["success"] is True
        assert result["cores"] == [-30, -30, -30, -30]  # Negated
