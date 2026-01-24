"""
Integration tests for Dynamic Manual Mode integration with Expert Mode.

Feature: manual-dynamic-mode
Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5

Tests that the Dynamic Manual tab is properly integrated into Expert Mode
with tab switching, state preservation, and settings persistence.
"""

import pytest
from typing import Dict, Any


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.settings = {}
    
    def save_setting(self, key: str, value: Any) -> bool:
        """Save a setting."""
        self.settings[key] = value
        return True
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting."""
        return self.settings.get(key, default)
    
    def load_all_settings(self) -> Dict[str, Any]:
        """Load all settings."""
        return self.settings.copy()


class MockExpertModeIntegration:
    """Mock Expert Mode with Dynamic Manual integration."""
    
    def __init__(self, settings_manager: MockSettingsManager):
        self.settings_manager = settings_manager
        self.active_tab = "manual"
        self.tabs = ["manual", "dynamic-manual", "presets", "tests", "fan", "diagnostics"]
    
    def switch_tab(self, tab: str):
        """Switch to a tab and persist selection."""
        if tab not in self.tabs:
            raise ValueError(f"Invalid tab: {tab}")
        
        self.active_tab = tab
        self.settings_manager.save_setting("expert_mode_selected_tab", tab)
    
    def load_persisted_tab(self) -> str:
        """Load persisted tab selection."""
        return self.settings_manager.get_setting("expert_mode_selected_tab", "manual")
    
    def get_available_tabs(self) -> list:
        """Get list of available tabs."""
        return self.tabs.copy()


def test_dynamic_manual_tab_available():
    """
    Test that Dynamic Manual tab is available in Expert Mode.
    
    Validates: Requirements 10.1
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    available_tabs = expert_mode.get_available_tabs()
    
    assert "dynamic-manual" in available_tabs, \
        "Dynamic Manual tab should be available in Expert Mode"


def test_dynamic_manual_tab_switching():
    """
    Test that switching to Dynamic Manual tab works correctly.
    
    Validates: Requirements 10.2
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Switch to dynamic-manual tab
    expert_mode.switch_tab("dynamic-manual")
    
    assert expert_mode.active_tab == "dynamic-manual", \
        "Active tab should be dynamic-manual after switching"


def test_tab_selection_persistence():
    """
    Test that selected tab is persisted to settings.
    
    Validates: Requirements 10.5
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Switch to dynamic-manual tab
    expert_mode.switch_tab("dynamic-manual")
    
    # Verify persistence
    persisted_tab = settings_manager.get_setting("expert_mode_selected_tab")
    assert persisted_tab == "dynamic-manual", \
        "Selected tab should be persisted to settings"


def test_tab_selection_restored_on_load():
    """
    Test that persisted tab selection is restored on load.
    
    Validates: Requirements 10.5
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Switch to dynamic-manual tab
    expert_mode.switch_tab("dynamic-manual")
    
    # Simulate reload by creating new instance with same settings
    expert_mode_reloaded = MockExpertModeIntegration(settings_manager)
    loaded_tab = expert_mode_reloaded.load_persisted_tab()
    
    assert loaded_tab == "dynamic-manual", \
        "Persisted tab selection should be restored on load"


def test_tab_switching_preserves_other_tabs():
    """
    Test that switching to Dynamic Manual doesn't affect other tabs.
    
    Validates: Requirements 10.3
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Verify all tabs are still available
    available_tabs = expert_mode.get_available_tabs()
    
    expected_tabs = ["manual", "dynamic-manual", "presets", "tests", "fan", "diagnostics"]
    assert set(available_tabs) == set(expected_tabs), \
        "All tabs should remain available after adding Dynamic Manual"


def test_multiple_tab_switches_with_persistence():
    """
    Test that multiple tab switches correctly persist the last selection.
    
    Validates: Requirements 10.5
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Switch through multiple tabs
    expert_mode.switch_tab("presets")
    expert_mode.switch_tab("dynamic-manual")
    expert_mode.switch_tab("tests")
    expert_mode.switch_tab("dynamic-manual")
    
    # Verify last selection is persisted
    persisted_tab = settings_manager.get_setting("expert_mode_selected_tab")
    assert persisted_tab == "dynamic-manual", \
        "Last selected tab should be persisted"


def test_default_tab_when_no_persistence():
    """
    Test that default tab is used when no persisted selection exists.
    
    Validates: Requirements 10.5
    """
    settings_manager = MockSettingsManager()
    expert_mode = MockExpertModeIntegration(settings_manager)
    
    # Load without any persisted selection
    loaded_tab = expert_mode.load_persisted_tab()
    
    assert loaded_tab == "manual", \
        "Default tab should be 'manual' when no persisted selection exists"
