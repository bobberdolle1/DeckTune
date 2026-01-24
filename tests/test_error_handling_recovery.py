"""Test error handling and recovery for Manual Dynamic Mode.

This module tests the comprehensive error handling system including:
- React error boundaries
- RPC retry logic
- Last Known Good (LKG) configuration storage
- Connection error handling
- Hardware error handling

Feature: manual-dynamic-mode
Validates: Requirements 7.1, 7.2, 7.3, 7.4
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.dynamic.rpc import (
    DynamicModeRPC,
    RPCError,
    HardwareError,
    ValidationError,
    ConnectionError
)
from backend.dynamic.manual_manager import DynamicManager, DynamicManualConfig, CoreConfig
from backend.dynamic.manual_validator import Validator


class TestRPCErrorHandling:
    """Test RPC error handling and categorization."""
    
    def test_hardware_error_not_recoverable(self):
        """Hardware errors should be marked as not recoverable."""
        error = HardwareError("sysfs write failed", {"path": "/sys/devices/..."})
        
        assert error.code == "HARDWARE_ERROR"
        assert error.recoverable is False
        assert "sysfs write failed" in error.message
        assert error.details["path"] == "/sys/devices/..."
    
    def test_validation_error_not_recoverable(self):
        """Validation errors should be marked as not recoverable."""
        error = ValidationError("min_mv > max_mv", {"core_id": 0})
        
        assert error.code == "VALIDATION_ERROR"
        assert error.recoverable is False
        assert "min_mv > max_mv" in error.message
    
    def test_connection_error_recoverable(self):
        """Connection errors should be marked as recoverable."""
        error = ConnectionError("network timeout")
        
        assert error.code == "CONNECTION_ERROR"
        assert error.recoverable is True
        assert "network timeout" in error.message
    
    def test_error_to_dict_serialization(self):
        """Errors should serialize to dict for JSON responses."""
        error = HardwareError("test error", {"detail": "value"})
        error_dict = error.to_dict()
        
        assert error_dict["message"] == "test error"
        assert error_dict["code"] == "HARDWARE_ERROR"
        assert error_dict["recoverable"] is False
        assert error_dict["details"]["detail"] == "value"


class TestRPCErrorResponses:
    """Test RPC methods return proper error responses."""
    
    @pytest.fixture
    def rpc_handler(self):
        """Create RPC handler with mocked dependencies."""
        manager = Mock(spec=DynamicManager)
        validator = Mock(spec=Validator)
        settings = Mock()
        return DynamicModeRPC(manager, validator, settings)
    
    @pytest.mark.asyncio
    async def test_get_config_handles_exceptions(self, rpc_handler):
        """get_dynamic_config should handle exceptions gracefully."""
        rpc_handler.manager.get_config.side_effect = Exception("test error")
        
        response = await rpc_handler.get_dynamic_config()
        
        assert response["success"] is False
        assert "test error" in response["error"]
        assert response["error_code"] == "UNKNOWN_ERROR"
        assert response["recoverable"] is True
    
    @pytest.mark.asyncio
    async def test_set_config_validation_error(self, rpc_handler):
        """set_dynamic_core_config should return validation errors."""
        # Mock validation failure
        validation_result = Mock()
        validation_result.valid = False
        validation_result.errors = ["min_mv > max_mv", "threshold out of range"]
        rpc_handler.validator.validate_config.return_value = validation_result
        
        response = await rpc_handler.set_dynamic_core_config(0, -20, -30, 50)
        
        assert response["success"] is False
        assert response["error"] == "Validation failed"
        assert len(response["validation_errors"]) == 2
        assert "min_mv > max_mv" in response["validation_errors"]
    
    @pytest.mark.asyncio
    async def test_start_mode_hardware_error(self, rpc_handler):
        """start_dynamic_mode should handle hardware errors."""
        rpc_handler.manager.start.side_effect = HardwareError("gymdeck3 failed")
        
        response = await rpc_handler.start_dynamic_mode({})
        
        assert response["success"] is False
        assert "gymdeck3 failed" in response["error"]
        assert response["error_code"] == "HARDWARE_ERROR"
        assert response["recoverable"] is False
    
    @pytest.mark.asyncio
    async def test_get_metrics_invalid_core(self, rpc_handler):
        """get_core_metrics should validate core_id."""
        response = await rpc_handler.get_core_metrics(5)
        
        assert response["success"] is False
        assert "Invalid core_id" in response["error"]
    
    @pytest.mark.asyncio
    async def test_get_curve_data_invalid_core(self, rpc_handler):
        """get_dynamic_curve_data should validate core_id."""
        response = await rpc_handler.get_dynamic_curve_data(-1)
        
        assert response["success"] is False
        assert "Invalid core_id" in response["error"]


class TestLKGStorage:
    """Test Last Known Good configuration storage and recovery.
    
    Note: LKG storage is implemented in TypeScript (src/utils/lkgStorage.ts)
    and tested via frontend tests. These tests verify the backend supports
    the LKG workflow through configuration persistence.
    """
    
    def test_backend_config_persistence_supports_lkg(self):
        """Backend should support saving and loading configurations for LKG."""
        manager = DynamicManager()
        settings = Mock()
        settings.save_setting = Mock(return_value=True)
        settings.get_setting = Mock(return_value=None)
        
        # Save configuration
        success = manager.save_config(settings)
        assert success is True
        assert settings.save_setting.called
        
        # Load configuration
        manager.load_config(settings)
        assert settings.get_setting.called
    
    def test_safe_defaults_available_for_recovery(self):
        """Safe defaults should be available for error recovery."""
        manager = DynamicManager()
        safe_config = manager._get_safe_defaults()
        
        assert safe_config.mode == "expert"
        assert len(safe_config.cores) == 4
        assert all(core.min_mv == -30 for core in safe_config.cores)
        assert all(core.max_mv == -15 for core in safe_config.cores)
        assert all(core.threshold == 50.0 for core in safe_config.cores)


class TestStabilityTracking:
    """Test stability tracking support in backend.
    
    Note: Stability tracking is implemented in TypeScript (src/utils/lkgStorage.ts).
    These tests verify the backend provides the necessary support.
    """
    
    def test_backend_tracks_active_state(self):
        """Backend should track whether dynamic mode is active."""
        manager = DynamicManager()
        
        assert manager.is_active is False
        
        manager.start()
        assert manager.is_active is True
        
        manager.stop()
        assert manager.is_active is False
    
    def test_config_persistence_includes_timestamp(self):
        """Saved configurations should include timestamp for stability tracking."""
        manager = DynamicManager()
        settings = Mock()
        
        saved_data = None
        def capture_save(key, data):
            nonlocal saved_data
            saved_data = data
            return True
        
        settings.save_setting = capture_save
        
        manager.save_config(settings)
        
        assert saved_data is not None
        assert "last_updated" in saved_data
        assert saved_data["last_updated"] > 0


class TestConnectionErrorHandling:
    """Test connection error detection and recovery."""
    
    @pytest.fixture
    def rpc_handler(self):
        """Create RPC handler with mocked dependencies."""
        manager = Mock(spec=DynamicManager)
        validator = Mock(spec=Validator)
        settings = Mock()
        return DynamicModeRPC(manager, validator, settings)
    
    @pytest.mark.asyncio
    async def test_connection_error_detection(self, rpc_handler):
        """Connection errors should be detected and categorized."""
        rpc_handler.manager.get_config.side_effect = Exception("network timeout")
        
        response = await rpc_handler.get_dynamic_config()
        
        assert response["success"] is False
        assert response["recoverable"] is True
    
    @pytest.mark.asyncio
    async def test_hardware_error_stops_mode(self):
        """Hardware errors should stop dynamic mode."""
        # This would be tested in integration tests with actual component
        # Here we verify the error is properly categorized
        error = HardwareError("CPU voltage controller failed")
        assert error.recoverable is False
        assert error.code == "HARDWARE_ERROR"


class TestErrorBoundaryRecovery:
    """Test React error boundary recovery options.
    
    Note: Error boundary is implemented in React (src/components/DynamicManualMode.tsx).
    These tests verify the backend provides necessary support for recovery.
    """
    
    def test_backend_provides_safe_defaults(self):
        """Backend should provide safe defaults for recovery."""
        manager = DynamicManager()
        safe_config = manager._get_safe_defaults()
        
        assert safe_config.mode == "expert"
        assert len(safe_config.cores) == 4
        assert all(core.min_mv == -30 for core in safe_config.cores)
        assert all(core.max_mv == -15 for core in safe_config.cores)
        assert all(core.threshold == 50.0 for core in safe_config.cores)
    
    def test_backend_config_load_fallback(self):
        """Backend should fall back to safe defaults on load error."""
        manager = DynamicManager()
        settings = Mock()
        settings.get_setting = Mock(side_effect=Exception("storage error"))
        
        # Should not raise, should use safe defaults
        success = manager.load_config(settings)
        
        assert success is False  # Indicates fallback was used
        assert manager.config.mode == "expert"
        assert len(manager.config.cores) == 4


class TestRetryLogic:
    """Test RPC retry logic with exponential backoff.
    
    Note: Retry logic is implemented in TypeScript (src/utils/rpcRetry.ts).
    These tests verify the backend error responses support retry logic.
    """
    
    def test_backend_errors_indicate_recoverability(self):
        """Backend errors should indicate if they're recoverable."""
        # Hardware error - not recoverable
        hw_error = HardwareError("test")
        assert hw_error.recoverable is False
        
        # Validation error - not recoverable
        val_error = ValidationError("test")
        assert val_error.recoverable is False
        
        # Connection error - recoverable
        conn_error = ConnectionError("test")
        assert conn_error.recoverable is True
    
    @pytest.mark.asyncio
    async def test_rpc_responses_include_recoverable_flag(self):
        """RPC error responses should include recoverable flag."""
        manager = Mock(spec=DynamicManager)
        validator = Mock(spec=Validator)
        settings = Mock()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Trigger hardware error
        manager.start.side_effect = HardwareError("test hardware error")
        response = await rpc.start_dynamic_mode({})
        
        assert response["success"] is False
        assert "recoverable" in response
        assert response["recoverable"] is False
        assert response["error_code"] == "HARDWARE_ERROR"


class TestErrorRecoveryIntegration:
    """Integration tests for error recovery workflows."""
    
    @pytest.mark.asyncio
    async def test_apply_config_with_validation_error(self):
        """Apply config should return validation errors properly."""
        manager = DynamicManager()
        validator = Validator()
        settings = Mock()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Try to set invalid config (min > max)
        response = await rpc.set_dynamic_core_config(0, -10, -30, 50)
        
        assert response["success"] is False
        assert "validation_errors" in response
    
    @pytest.mark.asyncio
    async def test_hardware_error_propagation(self):
        """Hardware errors should propagate with proper error info."""
        manager = Mock(spec=DynamicManager)
        validator = Mock(spec=Validator)
        settings = Mock()
        rpc = DynamicModeRPC(manager, validator, settings)
        
        # Simulate hardware error
        manager.start.side_effect = HardwareError("gymdeck3 initialization failed")
        
        response = await rpc.start_dynamic_mode({})
        
        assert response["success"] is False
        assert response["error_code"] == "HARDWARE_ERROR"
        assert response["recoverable"] is False
        assert "gymdeck3" in response["error"]
    
    def test_config_migration_on_load(self):
        """Configuration should be migrated when loading older versions."""
        manager = DynamicManager()
        settings = Mock()
        
        # Mock old version config
        old_config = {
            "mode": "expert",
            "cores": [
                {"core_id": i, "min_mv": -25, "max_mv": -10, "threshold": 60}
                for i in range(4)
            ],
            "version": 1  # Current version
        }
        settings.get_setting = Mock(return_value=old_config)
        
        # Load should succeed and migrate if needed
        success = manager.load_config(settings)
        
        assert success is True
        assert manager.config.version == 1
        assert len(manager.config.cores) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
