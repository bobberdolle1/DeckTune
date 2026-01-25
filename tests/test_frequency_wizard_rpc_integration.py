"""Integration tests for frequency wizard RPC methods.

Feature: frequency-based-wizard
Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7

These tests verify that the RPC methods correctly handle frequency wizard
operations including starting, monitoring progress, cancelling, and managing
frequency curves.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from backend.api.rpc import DeckTuneRPC
from backend.tuning.frequency_wizard import FrequencyWizardConfig, WizardProgress
from backend.tuning.frequency_curve import FrequencyCurve, FrequencyPoint


@pytest.fixture
def mock_platform():
    """Create mock platform info."""
    platform = MagicMock()
    platform.model = "test_model"
    platform.variant = "test_variant"
    platform.safe_limit = -30
    platform.detected = True
    return platform


@pytest.fixture
def mock_ryzenadj():
    """Create mock ryzenadj wrapper."""
    ryzenadj = MagicMock()
    ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    return ryzenadj


@pytest.fixture
def mock_safety():
    """Create mock safety manager."""
    safety = MagicMock()
    return safety


@pytest.fixture
def mock_event_emitter():
    """Create mock event emitter."""
    emitter = MagicMock()
    emitter.emit_status = AsyncMock()
    return emitter


@pytest.fixture
def mock_settings():
    """Create mock settings manager."""
    settings = MagicMock()
    settings._settings = {}
    
    def get_setting(key, default=None):
        return settings._settings.get(key, default)
    
    def set_setting(key, value):
        settings._settings[key] = value
    
    settings.getSetting = get_setting
    settings.setSetting = set_setting
    
    return settings


@pytest.fixture
def mock_test_runner():
    """Create mock test runner."""
    runner = MagicMock()
    runner.run_frequency_locked_test = AsyncMock()
    runner.get_system_metrics = MagicMock(return_value={'temperature': 60.0})
    return runner


@pytest.fixture
def rpc(mock_platform, mock_ryzenadj, mock_safety, mock_event_emitter, mock_settings, mock_test_runner):
    """Create RPC instance with mocked dependencies."""
    rpc = DeckTuneRPC(
        platform=mock_platform,
        ryzenadj=mock_ryzenadj,
        safety=mock_safety,
        event_emitter=mock_event_emitter,
        settings_manager=mock_settings,
        test_runner=mock_test_runner
    )
    return rpc


@pytest.mark.asyncio
async def test_start_frequency_wizard_with_preset(rpc):
    """Test starting frequency wizard with a preset configuration."""
    config = {
        "core_id": 0,
        "preset": "quick"
    }
    
    with patch('backend.tuning.frequency_wizard.FrequencyWizard') as MockWizard:
        mock_wizard = MagicMock()
        mock_wizard._calculate_frequency_points = MagicMock(return_value=[400, 600, 800])
        MockWizard.return_value = mock_wizard
        
        result = await rpc.start_frequency_wizard(config)
        
        assert result["success"] is True
        assert "session_id" in result
        assert "estimated_duration" in result
        assert result["estimated_duration"] > 0


@pytest.mark.asyncio
async def test_start_frequency_wizard_with_custom_config(rpc):
    """Test starting frequency wizard with custom configuration."""
    config = {
        "core_id": 0,
        "freq_start": 400,
        "freq_end": 2000,
        "freq_step": 200,
        "test_duration": 20,
        "voltage_start": -25,
        "voltage_step": 2,
        "safety_margin": 5
    }
    
    with patch('backend.tuning.frequency_wizard.FrequencyWizard') as MockWizard:
        mock_wizard = MagicMock()
        mock_wizard._calculate_frequency_points = MagicMock(return_value=[400, 600, 800])
        MockWizard.return_value = mock_wizard
        
        result = await rpc.start_frequency_wizard(config)
        
        assert result["success"] is True
        assert "session_id" in result


@pytest.mark.asyncio
async def test_start_frequency_wizard_invalid_config(rpc):
    """Test starting frequency wizard with invalid configuration."""
    config = {
        "core_id": 0,
        "freq_start": 5000,  # Invalid: > 3500
        "freq_end": 3500
    }
    
    result = await rpc.start_frequency_wizard(config)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_get_frequency_wizard_progress_not_running(rpc):
    """Test getting progress when no wizard is running."""
    result = await rpc.get_frequency_wizard_progress()
    
    # Should return default values when not running
    assert result["running"] is False
    assert result["current_frequency"] == 0
    assert result["current_voltage"] == 0
    assert result["progress_percent"] == 0.0
    assert result["estimated_remaining"] == 0
    assert result["completed_points"] == 0
    assert result["total_points"] == 0


@pytest.mark.asyncio
async def test_get_frequency_wizard_progress_running(rpc):
    """Test getting progress when wizard is running."""
    # Simulate running wizard with progress
    progress = WizardProgress(
        running=True,
        current_frequency=1500,
        current_voltage=-25,
        completed_points=10,
        total_points=30,
        estimated_remaining=600
    )
    
    rpc._frequency_wizard_progress = {"test_session": progress}
    
    result = await rpc.get_frequency_wizard_progress()
    
    assert result["running"] is True
    assert result["current_frequency"] == 1500
    assert result["current_voltage"] == -25
    assert result["completed_points"] == 10
    assert result["total_points"] == 30
    assert result["estimated_remaining"] == 600
    assert abs(result["progress_percent"] - 33.33) < 0.1


@pytest.mark.asyncio
async def test_cancel_frequency_wizard_not_running(rpc):
    """Test cancelling when no wizard is running."""
    result = await rpc.cancel_frequency_wizard()
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_cancel_frequency_wizard_running(rpc):
    """Test cancelling a running wizard."""
    # Simulate running wizard
    mock_wizard = MagicMock()
    mock_wizard.cancel = MagicMock()
    
    rpc._frequency_wizards = {"test_session": mock_wizard}
    
    # Create a proper async task mock
    async def dummy_task():
        await asyncio.sleep(0.1)
    
    rpc._frequency_wizard_task = asyncio.create_task(dummy_task())
    
    result = await rpc.cancel_frequency_wizard()
    
    assert result["success"] is True
    mock_wizard.cancel.assert_called_once()


@pytest.mark.asyncio
async def test_get_frequency_curve_not_found(rpc):
    """Test getting frequency curve when none exists."""
    result = await rpc.get_frequency_curve(0)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_get_frequency_curve_exists(rpc):
    """Test getting existing frequency curve."""
    # Create test curve
    curve = FrequencyCurve(
        core_id=0,
        points=[
            FrequencyPoint(400, -30, True, 30, 1234567890.0),
            FrequencyPoint(800, -28, True, 30, 1234567920.0)
        ],
        created_at=1234567890.0,
        wizard_config={}
    )
    
    # Store in settings
    rpc.settings.setSetting("frequency_curves", {"0": curve.to_dict()})
    
    result = await rpc.get_frequency_curve(0)
    
    assert result["success"] is True
    assert "curve" in result
    assert result["curve"]["core_id"] == 0
    assert len(result["curve"]["points"]) == 2


@pytest.mark.asyncio
async def test_apply_frequency_curve_valid(rpc):
    """Test applying valid frequency curves."""
    curves = {
        "0": {
            "core_id": 0,
            "points": [
                {"frequency_mhz": 400, "voltage_mv": -30, "stable": True, "test_duration": 30, "timestamp": 1234567890.0},
                {"frequency_mhz": 800, "voltage_mv": -28, "stable": True, "test_duration": 30, "timestamp": 1234567920.0}
            ],
            "created_at": 1234567890.0,
            "wizard_config": {}
        }
    }
    
    result = await rpc.apply_frequency_curve(curves)
    
    assert result["success"] is True
    
    # Verify curves were saved
    saved_curves = rpc.settings.getSetting("frequency_curves")
    assert saved_curves is not None
    assert "0" in saved_curves


@pytest.mark.asyncio
async def test_apply_frequency_curve_invalid(rpc):
    """Test applying invalid frequency curves."""
    curves = {
        "0": {
            "core_id": 0,
            "points": [
                {"frequency_mhz": 400, "voltage_mv": -150, "stable": True, "test_duration": 30, "timestamp": 1234567890.0}  # Invalid voltage
            ],
            "created_at": 1234567890.0,
            "wizard_config": {}
        }
    }
    
    result = await rpc.apply_frequency_curve(curves)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_enable_frequency_mode(rpc):
    """Test enabling frequency-based mode."""
    result = await rpc.enable_frequency_mode()
    
    assert result["success"] is True
    
    # Verify flag was set
    assert rpc.settings.getSetting("frequency_mode_enabled") is True


@pytest.mark.asyncio
async def test_disable_frequency_mode(rpc):
    """Test disabling frequency-based mode."""
    # First enable it
    rpc.settings.setSetting("frequency_mode_enabled", True)
    
    result = await rpc.disable_frequency_mode()
    
    assert result["success"] is True
    
    # Verify flag was cleared
    assert rpc.settings.getSetting("frequency_mode_enabled") is False
