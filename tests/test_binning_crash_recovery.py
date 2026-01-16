"""Integration test for binning crash recovery.

Tests the complete crash recovery workflow:
1. Simulate crash during binning by leaving state file active
2. Restart plugin and verify boot recovery
3. Verify last_stable is restored

Requirements: 1.5, 2.3
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

from backend.platform.detect import PlatformInfo
from backend.core.safety import SafetyManager, BinningState
from backend.core.ryzenadj import RyzenadjWrapper


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


def create_default_platform() -> PlatformInfo:
    """Create a default LCD platform for testing."""
    return PlatformInfo(model="Jupiter", variant="LCD", safe_limit=-30, detected=True)


class TestBinningCrashRecovery:
    """Integration tests for binning crash recovery workflow."""
    
    def setup_method(self):
        """Set up test with a temporary file path."""
        self.temp_dir = tempfile.gettempdir()
        self.original_state_file = SafetyManager.BINNING_STATE_FILE
        SafetyManager.BINNING_STATE_FILE = os.path.join(self.temp_dir, "decktune_binning_state_test.json")
        
        # Clean up any existing test file
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
    
    def teardown_method(self):
        """Clean up binning state file after each test."""
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
        SafetyManager.BINNING_STATE_FILE = self.original_state_file
    
    def test_crash_recovery_restores_last_stable(self):
        """Test that crash recovery restores last_stable value after simulated crash."""
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        
        # Create mock ryzenadj wrapper
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(True, None))
        
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Simulate binning in progress - create state file with active=True
        # This simulates a crash during iteration 3, testing -20mV, with last_stable at -15mV
        safety.create_binning_state(
            current_value=-20,
            last_stable=-15,
            iteration=3,
            failed_values=[]
        )
        
        # Verify state file exists and is active
        state = safety.load_binning_state()
        assert state is not None
        assert state.active is True
        assert state.current_value == -20
        assert state.last_stable == -15
        
        # Simulate plugin restart - create new SafetyManager instance
        # This simulates what happens when the plugin loads after a crash
        safety_after_reboot = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Call check_boot_recovery - this should detect the crash and recover
        recovery_performed = safety_after_reboot.check_boot_recovery()
        
        # Verify recovery was performed
        assert recovery_performed is True, "Recovery should have been performed"
        
        # Verify that ryzenadj.apply_values was called with last_stable value
        mock_ryzenadj.apply_values.assert_called_once()
        applied_values = mock_ryzenadj.apply_values.call_args[0][0]
        assert applied_values == [-15, -15, -15, -15], "Should restore last_stable value to all cores"
        
        # Verify state file was cleared
        state_after_recovery = safety_after_reboot.load_binning_state()
        assert state_after_recovery is None, "State file should be cleared after recovery"
    
    def test_crash_recovery_logs_failed_value(self, caplog):
        """Test that crash recovery logs the failed test value."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(True, None))
        
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Simulate crash at -25mV with last_stable at -20mV
        safety.create_binning_state(
            current_value=-25,
            last_stable=-20,
            iteration=4,
            failed_values=[]
        )
        
        # Simulate reboot and recovery
        safety_after_reboot = SafetyManager(settings_manager, platform, mock_ryzenadj)
        safety_after_reboot.check_boot_recovery()
        
        # Verify that the failed value was logged
        assert any("failed value: -25" in record.message for record in caplog.records), \
            "Failed value should be logged"
        assert any("restoring last_stable: -20" in record.message for record in caplog.records), \
            "Last stable value should be logged"
    
    def test_crash_recovery_without_ryzenadj(self, caplog):
        """Test that crash recovery handles missing ryzenadj gracefully."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Setup without ryzenadj
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform, ryzenadj=None)
        
        # Simulate crash
        safety.create_binning_state(
            current_value=-20,
            last_stable=-15,
            iteration=3,
            failed_values=[]
        )
        
        # Simulate reboot and recovery
        safety_after_reboot = SafetyManager(settings_manager, platform, ryzenadj=None)
        recovery_performed = safety_after_reboot.check_boot_recovery()
        
        # Verify recovery was still performed (state cleared)
        assert recovery_performed is True
        
        # Verify warning was logged
        assert any("RyzenadjWrapper not configured" in record.message for record in caplog.records), \
            "Should log warning about missing ryzenadj"
        
        # Verify state file was still cleared
        state_after_recovery = safety_after_reboot.load_binning_state()
        assert state_after_recovery is None
    
    def test_no_recovery_when_binning_not_active(self):
        """Test that no recovery is performed when binning state is not active."""
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(True, None))
        
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Create state file with active=False (normal completion)
        state_data = {
            "active": False,
            "current_value": -20,
            "last_stable": -20,
            "iteration": 4,
            "failed_values": [],
            "timestamp": "2026-01-15T10:30:00Z"
        }
        with open(SafetyManager.BINNING_STATE_FILE, 'w') as f:
            json.dump(state_data, f)
        
        # Simulate reboot
        safety_after_reboot = SafetyManager(settings_manager, platform, mock_ryzenadj)
        recovery_performed = safety_after_reboot.check_boot_recovery()
        
        # Verify no recovery was performed
        assert recovery_performed is False, "No recovery should be performed when active=False"
        
        # Verify ryzenadj was not called
        mock_ryzenadj.apply_values.assert_not_called()
    
    def test_no_recovery_when_no_state_file(self):
        """Test that no recovery is performed when no state file exists."""
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(True, None))
        
        # Ensure no state file exists
        if os.path.exists(SafetyManager.BINNING_STATE_FILE):
            os.remove(SafetyManager.BINNING_STATE_FILE)
        
        # Simulate reboot
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        recovery_performed = safety.check_boot_recovery()
        
        # Verify no recovery was performed
        assert recovery_performed is False
        
        # Verify ryzenadj was not called
        mock_ryzenadj.apply_values.assert_not_called()
    
    def test_crash_recovery_with_failed_values_list(self):
        """Test crash recovery preserves failed values list in logs."""
        import logging
        
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(True, None))
        
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Simulate crash with some failed values
        safety.create_binning_state(
            current_value=-30,
            last_stable=-20,
            iteration=5,
            failed_values=[-35, -40]
        )
        
        # Verify state was created correctly
        state = safety.load_binning_state()
        assert state.failed_values == [-35, -40]
        
        # Simulate reboot and recovery
        safety_after_reboot = SafetyManager(settings_manager, platform, mock_ryzenadj)
        recovery_performed = safety_after_reboot.check_boot_recovery()
        
        # Verify recovery was performed
        assert recovery_performed is True
        
        # Verify last_stable was restored
        mock_ryzenadj.apply_values.assert_called_once_with([-20, -20, -20, -20])
    
    def test_crash_recovery_handles_ryzenadj_failure(self, caplog):
        """Test that crash recovery handles ryzenadj failure gracefully."""
        import logging
        caplog.set_level(logging.ERROR)
        
        # Setup
        platform = create_default_platform()
        settings_manager = MockSettingsManager()
        
        # Create mock ryzenadj that fails
        mock_ryzenadj = Mock(spec=RyzenadjWrapper)
        mock_ryzenadj.apply_values = Mock(return_value=(False, "Ryzenadj execution failed"))
        
        safety = SafetyManager(settings_manager, platform, mock_ryzenadj)
        
        # Simulate crash
        safety.create_binning_state(
            current_value=-25,
            last_stable=-20,
            iteration=4,
            failed_values=[]
        )
        
        # Simulate reboot and recovery
        safety_after_reboot = SafetyManager(settings_manager, platform, mock_ryzenadj)
        recovery_performed = safety_after_reboot.check_boot_recovery()
        
        # Verify recovery was attempted
        assert recovery_performed is True
        
        # Verify error was logged
        assert any("failed to restore last_stable" in record.message for record in caplog.records), \
            "Should log error when ryzenadj fails"
        
        # Verify state file was still cleared (recovery continues despite failure)
        state_after_recovery = safety_after_reboot.load_binning_state()
        assert state_after_recovery is None
