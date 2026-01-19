"""Integration tests for fan control RPC endpoints.

Tests the complete workflow of fan control through RPC methods,
including preset application, custom curve creation, and status retrieval.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock

from backend.core.fan_control import HwmonInterface, FanControlService, FanPoint
from backend.api.rpc import DeckTuneRPC


@pytest.fixture
def mock_hwmon():
    """Create a mock hwmon interface."""
    hwmon = Mock(spec=HwmonInterface)
    hwmon.is_available.return_value = True
    hwmon.read_temperature.return_value = 65.0
    hwmon.read_current_pwm.return_value = 50
    hwmon.write_pwm.return_value = True
    return hwmon


@pytest.fixture
def temp_config_path():
    """Create a temporary config path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "fan_control.json")


@pytest.fixture
def fan_service(mock_hwmon, temp_config_path):
    """Create a FanControlService instance with mock hwmon."""
    service = FanControlService(mock_hwmon, temp_config_path)
    yield service
    # Stop monitoring if running
    if service._monitoring_active:
        service.stop_monitoring()


@pytest.fixture
def mock_settings():
    """Create a mock settings manager."""
    settings = Mock()
    settings.getSetting.return_value = None
    settings.setSetting.return_value = None
    return settings


@pytest.fixture
def rpc_handler(fan_service, mock_settings):
    """Create an RPC handler with fan control service."""
    # Create minimal mocks for required dependencies
    platform = Mock()
    platform.model = "Test Device"
    platform.variant = "Test"
    platform.safe_limit = -35
    platform.detected = True
    
    ryzenadj = Mock()
    safety = Mock()
    event_emitter = Mock()
    event_emitter.emit_status = AsyncMock()
    
    rpc = DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=mock_settings
    )
    
    # Set the fan control service
    rpc.set_fan_control_service(fan_service)
    
    return rpc


class TestPresetApplication:
    """Test preset application workflow."""
    
    @pytest.mark.asyncio
    async def test_apply_stock_preset(self, rpc_handler):
        """Test applying the Stock preset."""
        result = await rpc_handler.fan_apply_preset("stock")
        
        assert result["success"] is True
        assert result["preset"] == "stock"
    
    @pytest.mark.asyncio
    async def test_apply_silent_preset(self, rpc_handler):
        """Test applying the Silent preset."""
        result = await rpc_handler.fan_apply_preset("silent")
        
        assert result["success"] is True
        assert result["preset"] == "silent"
    
    @pytest.mark.asyncio
    async def test_apply_turbo_preset(self, rpc_handler):
        """Test applying the Turbo preset."""
        result = await rpc_handler.fan_apply_preset("turbo")
        
        assert result["success"] is True
        assert result["preset"] == "turbo"
    
    @pytest.mark.asyncio
    async def test_apply_invalid_preset(self, rpc_handler):
        """Test applying an invalid preset returns error."""
        result = await rpc_handler.fan_apply_preset("invalid")
        
        assert result["success"] is False
        assert "error" in result


class TestCustomCurveCreation:
    """Test custom curve creation workflow."""
    
    @pytest.mark.asyncio
    async def test_create_valid_custom_curve(self, rpc_handler):
        """Test creating a valid custom curve."""
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        result = await rpc_handler.fan_create_custom("my_curve", points)
        
        assert result["success"] is True
        assert result["name"] == "my_curve"
        assert result["points"] == 3
    
    @pytest.mark.asyncio
    async def test_create_curve_with_invalid_points(self, rpc_handler):
        """Test creating a curve with too few points fails."""
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50}
        ]
        
        result = await rpc_handler.fan_create_custom("invalid_curve", points)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_curve_with_invalid_temp(self, rpc_handler):
        """Test creating a curve with invalid temperature fails."""
        points = [
            {"temp": -10, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        result = await rpc_handler.fan_create_custom("invalid_temp", points)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_curve_with_invalid_speed(self, rpc_handler):
        """Test creating a curve with invalid speed fails."""
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 150},
            {"temp": 80, "speed": 100}
        ]
        
        result = await rpc_handler.fan_create_custom("invalid_speed", points)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_load_custom_curve(self, rpc_handler):
        """Test loading a custom curve after creation."""
        # Create curve first
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        create_result = await rpc_handler.fan_create_custom("test_curve", points)
        assert create_result["success"] is True
        
        # Load the curve
        load_result = await rpc_handler.fan_load_custom("test_curve")
        
        assert load_result["success"] is True
        assert load_result["name"] == "test_curve"
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_curve(self, rpc_handler):
        """Test loading a non-existent curve fails."""
        result = await rpc_handler.fan_load_custom("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_delete_custom_curve(self, rpc_handler):
        """Test deleting a custom curve."""
        # Create curve first
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        create_result = await rpc_handler.fan_create_custom("delete_me", points)
        assert create_result["success"] is True
        
        # Delete the curve
        delete_result = await rpc_handler.fan_delete_custom("delete_me")
        
        assert delete_result["success"] is True
        assert delete_result["name"] == "delete_me"
        
        # Verify it's gone
        load_result = await rpc_handler.fan_load_custom("delete_me")
        assert load_result["success"] is False


class TestStatusRetrieval:
    """Test status retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_status(self, rpc_handler, mock_hwmon):
        """Test getting current status."""
        result = await rpc_handler.fan_get_status()
        
        assert result["success"] is True
        assert "current_temp" in result
        assert "current_speed" in result
        assert "target_speed" in result
        assert "active_curve" in result
        assert "curve_type" in result
        assert "monitoring_active" in result
        assert "hwmon_available" in result
    
    @pytest.mark.asyncio
    async def test_list_presets(self, rpc_handler):
        """Test listing available presets."""
        result = await rpc_handler.fan_list_presets()
        
        assert result["success"] is True
        assert "presets" in result
        assert "stock" in result["presets"]
        assert "silent" in result["presets"]
        assert "turbo" in result["presets"]
    
    @pytest.mark.asyncio
    async def test_list_custom_curves(self, rpc_handler):
        """Test listing custom curves."""
        # Create a couple of curves
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        await rpc_handler.fan_create_custom("curve1", points)
        await rpc_handler.fan_create_custom("curve2", points)
        
        # List curves
        result = await rpc_handler.fan_list_custom()
        
        assert result["success"] is True
        assert "custom_curves" in result
        assert "curve1" in result["custom_curves"]
        assert "curve2" in result["custom_curves"]


class TestErrorHandling:
    """Test error handling in RPC methods."""
    
    @pytest.mark.asyncio
    async def test_missing_fan_service(self, mock_settings):
        """Test RPC methods fail gracefully when fan service is not initialized."""
        # Create RPC without fan service
        platform = Mock()
        platform.model = "Test Device"
        
        rpc = DeckTuneRPC(
            platform=platform,
            ryzenadj=Mock(),
            safety=Mock(),
            event_emitter=Mock(),
            settings_manager=mock_settings
        )
        
        # Try to use fan control methods
        result = await rpc.fan_apply_preset("stock")
        assert result["success"] is False
        assert "not initialized" in result["error"]
        
        result = await rpc.fan_get_status()
        assert result["success"] is False
        assert "not initialized" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_curve_missing_keys(self, rpc_handler):
        """Test creating a curve with missing keys in points."""
        points = [
            {"temp": 40},  # Missing speed
            {"speed": 50},  # Missing temp
            {"temp": 80, "speed": 100}
        ]
        
        result = await rpc_handler.fan_create_custom("bad_curve", points)
        
        assert result["success"] is False
        assert "error" in result


class TestWorkflowIntegration:
    """Test complete workflows."""
    
    @pytest.mark.asyncio
    async def test_preset_to_custom_workflow(self, rpc_handler):
        """Test switching from preset to custom curve."""
        # Start with a preset
        result = await rpc_handler.fan_apply_preset("stock")
        assert result["success"] is True
        
        # Check status shows preset
        status = await rpc_handler.fan_get_status()
        assert status["active_curve"] == "stock"
        assert status["curve_type"] == "preset"
        
        # Create and load custom curve
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        create_result = await rpc_handler.fan_create_custom("my_custom", points)
        assert create_result["success"] is True
        
        load_result = await rpc_handler.fan_load_custom("my_custom")
        assert load_result["success"] is True
        
        # Check status shows custom curve
        status = await rpc_handler.fan_get_status()
        assert status["active_curve"] == "my_custom"
        assert status["curve_type"] == "custom"
    
    @pytest.mark.asyncio
    async def test_delete_active_curve_fallback(self, rpc_handler):
        """Test deleting the active custom curve falls back to Stock."""
        # Create and load custom curve
        points = [
            {"temp": 40, "speed": 0},
            {"temp": 60, "speed": 50},
            {"temp": 80, "speed": 100}
        ]
        
        await rpc_handler.fan_create_custom("active_curve", points)
        await rpc_handler.fan_load_custom("active_curve")
        
        # Verify it's active
        status = await rpc_handler.fan_get_status()
        assert status["active_curve"] == "active_curve"
        
        # Delete the active curve
        delete_result = await rpc_handler.fan_delete_custom("active_curve")
        assert delete_result["success"] is True
        
        # Check status falls back to Stock
        status = await rpc_handler.fan_get_status()
        assert status["active_curve"] == "stock"
        assert status["curve_type"] == "preset"
