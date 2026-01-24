"""Tests for platform limits RPC method.

Feature: manual-dynamic-mode
Validates: Requirements 7.2, 7.3

Tests the get_platform_limits RPC method that provides voltage limits
to the frontend for validation.
"""

import pytest
from backend.dynamic.rpc import DynamicModeRPC
from backend.dynamic.manual_manager import DynamicManager
from backend.dynamic.manual_validator import Validator, PLATFORM_MIN_LIMIT, PLATFORM_MAX_LIMIT
from backend.dynamic.gymdeck3_stub import Gymdeck3Stub


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
    
    def save(self):
        pass


@pytest.mark.asyncio
class TestPlatformLimitsRPC:
    """Tests for get_platform_limits RPC method."""
    
    async def test_get_platform_limits_returns_success(self):
        """get_platform_limits SHALL return success status.
        
        Validates: Requirements 7.2, 7.3
        """
        # Setup
        gymdeck3 = Gymdeck3Stub()
        manager = DynamicManager(gymdeck3)
        validator = Validator()
        settings = MockSettingsManager()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Execute
        response = await rpc.get_platform_limits()
        
        # Verify
        assert response["success"] is True
        assert "limits" in response
    
    async def test_get_platform_limits_returns_correct_values(self):
        """get_platform_limits SHALL return platform min and max limits.
        
        Validates: Requirements 7.2, 7.3
        """
        # Setup
        gymdeck3 = Gymdeck3Stub()
        manager = DynamicManager(gymdeck3)
        validator = Validator()
        settings = MockSettingsManager()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Execute
        response = await rpc.get_platform_limits()
        
        # Verify
        assert response["success"] is True
        limits = response["limits"]
        
        assert "min" in limits
        assert "max" in limits
        assert limits["min"] == PLATFORM_MIN_LIMIT
        assert limits["max"] == PLATFORM_MAX_LIMIT
    
    async def test_get_platform_limits_with_custom_validator(self):
        """get_platform_limits SHALL return custom platform limits.
        
        Validates: Requirements 7.2, 7.3
        """
        # Setup with custom platform minimum
        custom_min = -80
        gymdeck3 = Gymdeck3Stub()
        manager = DynamicManager(gymdeck3)
        validator = Validator(platform_min=custom_min)
        settings = MockSettingsManager()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Execute
        response = await rpc.get_platform_limits()
        
        # Verify
        assert response["success"] is True
        limits = response["limits"]
        
        assert limits["min"] == custom_min
        assert limits["max"] == PLATFORM_MAX_LIMIT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
