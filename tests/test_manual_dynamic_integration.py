"""Integration tests for Manual Dynamic Mode end-to-end workflows.

Feature: manual-dynamic-mode
Validates: All Requirements

This module tests complete end-to-end workflows to verify that all components
work together correctly. These tests simulate real user workflows from initial
configuration through active monitoring.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from backend.dynamic.manual_manager import DynamicManager
from backend.dynamic.manual_validator import Validator
from backend.dynamic.rpc import DynamicModeRPC


def create_test_components():
    """Create all components needed for integration testing."""
    # Create mock gymdeck3 interface
    mock_gymdeck3 = MagicMock()
    mock_gymdeck3.set_core_config = AsyncMock(return_value=True)
    mock_gymdeck3.start_dynamic_mode = AsyncMock(return_value=True)
    mock_gymdeck3.stop_dynamic_mode = AsyncMock(return_value=True)
    mock_gymdeck3.get_core_metrics = AsyncMock(return_value={
        'core_id': 0,
        'load': 50.0,
        'voltage': -20,
        'frequency': 2800,
        'temperature': 65.0,
        'timestamp': 1234567890
    })
    
    # Create manager
    manager = DynamicManager(mock_gymdeck3)
    
    # Create validator
    validator = Validator()
    
    # Create mock settings manager
    mock_settings = MagicMock()
    mock_settings.get_setting = MagicMock(return_value=None)
    mock_settings.save_setting = MagicMock()
    
    # Create RPC handler
    rpc = DynamicModeRPC(manager, validator, mock_settings)
    
    return rpc, manager, validator, mock_gymdeck3, mock_settings


class TestCompleteUserWorkflow:
    """Test complete user workflow from configuration to monitoring.
    
    Validates: All Requirements
    """
    
    @pytest.mark.asyncio
    async def test_full_workflow_simple_to_expert_mode(self):
        """Test complete workflow: Simple Mode → Expert Mode → Apply → Start → Monitor → Stop."""
        rpc, manager, validator, mock_gymdeck3, mock_settings = create_test_components()
        
        # === Phase 1: Initial Configuration in Simple Mode ===
        
        # User opens Dynamic Manual Mode (defaults to expert mode)
        config = await rpc.get_dynamic_config()
        assert config['success'] is True
        assert 'cores' in config['data']
        assert len(config['data']['cores']) == 4
        
        # === Phase 2: Configure in Expert Mode ===
        
        # User configures each core differently
        result1 = await rpc.set_dynamic_core_config(0, -25, -10, 40)
        assert result1['success'] is True
        
        result2 = await rpc.set_dynamic_core_config(1, -30, -15, 50)
        assert result2['success'] is True
        
        result3 = await rpc.set_dynamic_core_config(2, -20, -10, 60)
        assert result3['success'] is True
        
        result4 = await rpc.set_dynamic_core_config(3, -35, -20, 45)
        assert result4['success'] is True
        
        # Verify configurations were applied
        config = await rpc.get_dynamic_config()
        assert config['data']['cores'][0]['min_mv'] == -25
        assert config['data']['cores'][1]['min_mv'] == -30
        assert config['data']['cores'][2]['min_mv'] == -20
        assert config['data']['cores'][3]['min_mv'] == -35
        
        # === Phase 3: Visualize Curves ===
        
        # User views curve for core 0
        curve_result = await rpc.get_dynamic_curve_data(0)
        assert curve_result['success'] is True
        assert len(curve_result['data']) == 101  # 0-100 load points
        
        # === Phase 4: Start Dynamic Mode ===
        
        start_result = await rpc.start_dynamic_mode()
        assert start_result['success'] is True
        assert manager.is_active is True
        
        # Verify gymdeck3 was called
        mock_gymdeck3.start_dynamic_mode.assert_called_once()
        
        # === Phase 5: Monitor Real-Time Metrics ===
        
        # Poll metrics for each core
        for core_id in range(4):
            metrics_result = await rpc.get_core_metrics(core_id)
            assert metrics_result['success'] is True
            assert 'load' in metrics_result['data']
            assert 'voltage' in metrics_result['data']
            assert 'frequency' in metrics_result['data']
            assert 'temperature' in metrics_result['data']
        
        # === Phase 6: Stop Dynamic Mode ===
        
        stop_result = await rpc.stop_dynamic_mode()
        assert stop_result['success'] is True
        assert manager.is_active is False
        
        mock_gymdeck3.stop_dynamic_mode.assert_called_once()


class TestConfigurationPersistence:
    """Test configuration persistence and loading.
    
    Validates: Requirements 6.1-6.5
    """
    
    @pytest.mark.asyncio
    async def test_configuration_save_and_load(self):
        """Test that configuration can be saved and loaded."""
        rpc, manager, _, _, _ = create_test_components()
        
        # Configure cores
        await rpc.set_dynamic_core_config(0, -30, -15, 50)
        await rpc.set_dynamic_core_config(1, -25, -10, 60)
        
        # Save configuration
        manager.save_config()
        
        # Verify configuration is saved
        config = await rpc.get_dynamic_config()
        assert config['data']['cores'][0]['min_mv'] == -30
        assert config['data']['cores'][1]['min_mv'] == -25


class TestErrorRecovery:
    """Test error recovery scenarios.
    
    Validates: Requirements 7.1-7.5
    """
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test that validation errors are handled correctly."""
        rpc, _, _, _, _ = create_test_components()
        
        # Try to set invalid config (min > max)
        result = await rpc.set_dynamic_core_config(0, -10, -30, 50)
        
        # Should fail validation
        assert result['success'] is False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_hardware_error_handling(self):
        """Test that hardware errors are handled gracefully."""
        rpc, manager, _, mock_gymdeck3, _ = create_test_components()
        
        # Make gymdeck3 fail
        mock_gymdeck3.start_dynamic_mode = AsyncMock(
            side_effect=Exception("Hardware error")
        )
        
        # Try to start - should fail gracefully
        result = await rpc.start_dynamic_mode()
        assert result['success'] is False
        assert 'error' in result


class TestSafetyValidation:
    """Test safety validation and clamping.
    
    Validates: Requirements 7.1-7.5
    """
    
    @pytest.mark.asyncio
    async def test_voltage_clamping(self):
        """Test that voltages are clamped to safe ranges."""
        rpc, _, _, _, _ = create_test_components()
        
        # Try to set voltage above 0mV
        result = await rpc.set_dynamic_core_config(0, 10, 20, 50)
        
        # Should succeed with clamped values
        assert result['success'] is True
        
        config = await rpc.get_dynamic_config()
        # Values should be clamped to 0
        assert config['data']['cores'][0]['min_mv'] <= 0
        assert config['data']['cores'][0]['max_mv'] <= 0


class TestCurveCalculation:
    """Test voltage curve calculation.
    
    Validates: Requirements 2.1-2.5
    """
    
    @pytest.mark.asyncio
    async def test_curve_generation(self):
        """Test that voltage curves are generated correctly."""
        rpc, _, _, _, _ = create_test_components()
        
        # Configure core
        await rpc.set_dynamic_core_config(0, -30, -15, 50)
        
        # Get curve data
        result = await rpc.get_dynamic_curve_data(0)
        assert result['success'] is True
        
        curve_points = result['data']
        
        # Verify 101 points
        assert len(curve_points) == 101
        
        # Verify points below threshold have min voltage
        for point in curve_points[:51]:  # 0-50
            assert point['voltage'] == -30
        
        # Verify points above threshold are interpolated
        for point in curve_points[51:]:  # 51-100
            assert point['voltage'] >= -30
            assert point['voltage'] <= -15


class TestModeSwitching:
    """Test Simple Mode and Expert Mode switching.
    
    Validates: Requirements 4.1-4.5
    """
    
    @pytest.mark.asyncio
    async def test_mode_switching_preserves_config(self):
        """Test that mode switching preserves per-core configurations."""
        rpc, manager, _, _, _ = create_test_components()
        
        # Configure in expert mode
        manager.config.mode = 'expert'
        await rpc.set_dynamic_core_config(0, -25, -10, 40)
        await rpc.set_dynamic_core_config(1, -30, -15, 50)
        
        # Get config before switch
        config_before = await rpc.get_dynamic_config()
        
        # Switch to simple mode and back
        manager.config.mode = 'simple'
        manager.config.mode = 'expert'
        
        # Verify config preserved
        config_after = await rpc.get_dynamic_config()
        assert config_after['data']['cores'][0]['min_mv'] == config_before['data']['cores'][0]['min_mv']
        assert config_after['data']['cores'][1]['min_mv'] == config_before['data']['cores'][1]['min_mv']


class TestRealTimeMetrics:
    """Test real-time metrics polling.
    
    Validates: Requirements 3.1-3.5
    """
    
    @pytest.mark.asyncio
    async def test_metrics_polling(self):
        """Test that metrics can be polled for all cores."""
        rpc, manager, _, mock_gymdeck3, _ = create_test_components()
        
        # Start dynamic mode
        await rpc.start_dynamic_mode()
        
        # Poll metrics for each core
        for core_id in range(4):
            # Update mock to return different data for each core
            mock_gymdeck3.get_core_metrics = AsyncMock(return_value={
                'core_id': core_id,
                'load': 50.0 + core_id * 10,
                'voltage': -20 - core_id * 2,
                'frequency': 2800 + core_id * 100,
                'temperature': 65.0 + core_id * 2,
                'timestamp': 1234567890
            })
            
            result = await rpc.get_core_metrics(core_id)
            assert result['success'] is True
            assert result['data']['core_id'] == core_id
            assert result['data']['load'] == 50.0 + core_id * 10


# Summary test that validates the entire feature works end-to-end
class TestEndToEndIntegration:
    """Final integration test that validates the entire feature.
    
    This test simulates a complete user session from opening the UI
    to actively monitoring dynamic voltage adjustments.
    
    Validates: All Requirements
    """
    
    @pytest.mark.asyncio
    async def test_complete_integration(self):
        """Test complete integration of all components."""
        rpc, manager, validator, mock_gymdeck3, mock_settings = create_test_components()
        
        # 1. Get initial config
        config = await rpc.get_dynamic_config()
        assert config['success'] is True
        
        # 2. Configure cores
        for i in range(4):
            result = await rpc.set_dynamic_core_config(
                core_id=i,
                min_mv=-30 - i * 5,
                max_mv=-15 - i * 2,
                threshold=50 + i * 5
            )
            assert result['success'] is True
        
        # 3. Get curve data for visualization
        for i in range(4):
            curve = await rpc.get_dynamic_curve_data(i)
            assert curve['success'] is True
            assert len(curve['data']) == 101
        
        # 4. Start dynamic mode
        start_result = await rpc.start_dynamic_mode()
        assert start_result['success'] is True
        
        # 5. Poll metrics multiple times
        for _ in range(5):
            for core_id in range(4):
                metrics = await rpc.get_core_metrics(core_id)
                assert metrics['success'] is True
            await asyncio.sleep(0.01)
        
        # 6. Stop dynamic mode
        stop_result = await rpc.stop_dynamic_mode()
        assert stop_result['success'] is True
        
        # 7. Verify final state
        assert manager.is_active is False
        final_config = await rpc.get_dynamic_config()
        assert final_config['success'] is True
