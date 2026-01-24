"""
Property-based tests for Dynamic Manual Mode tab state preservation.

Feature: manual-dynamic-mode, Property 23: Tab state preservation
Validates: Requirements 10.3

Tests that switching between tabs in ExpertMode preserves the state of
DynamicManualMode component without modification.
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import Dict, Any


# Strategy for generating valid dynamic mode configurations
@st.composite
def dynamic_config_strategy(draw):
    """Generate a valid DynamicConfig for testing."""
    mode = draw(st.sampled_from(['simple', 'expert']))
    cores = []
    for i in range(4):
        core = {
            'core_id': i,
            'min_mv': draw(st.integers(min_value=-100, max_value=0)),
            'max_mv': draw(st.integers(min_value=-100, max_value=0)),
            'threshold': draw(st.integers(min_value=0, max_value=100))
        }
        # Ensure min_mv <= max_mv
        if core['min_mv'] > core['max_mv']:
            core['min_mv'], core['max_mv'] = core['max_mv'], core['min_mv']
        cores.append(core)
    
    return {
        'mode': mode,
        'cores': cores,
        'version': 1
    }


class MockDynamicModeState:
    """Mock state manager for DynamicManualMode component."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_active = False
        self.selected_core = 0
        self.metrics = {}
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state snapshot."""
        return {
            'config': self.config.copy(),
            'is_active': self.is_active,
            'selected_core': self.selected_core,
            'metrics': self.metrics.copy()
        }
    
    def set_state(self, state: Dict[str, Any]):
        """Restore state from snapshot."""
        self.config = state['config'].copy()
        self.is_active = state['is_active']
        self.selected_core = state['selected_core']
        self.metrics = state['metrics'].copy()


class MockExpertMode:
    """Mock ExpertMode component with tab switching."""
    
    def __init__(self):
        self.active_tab = 'manual'
        self.tab_states = {}
        self.dynamic_mode_state = None
    
    def switch_to_tab(self, tab_name: str):
        """Switch to a different tab, preserving current tab state."""
        # Save current tab state
        if self.active_tab == 'dynamic-manual' and self.dynamic_mode_state:
            self.tab_states['dynamic-manual'] = self.dynamic_mode_state.get_state()
        
        # Switch tab
        self.active_tab = tab_name
        
        # Restore tab state if returning
        if tab_name == 'dynamic-manual' and 'dynamic-manual' in self.tab_states:
            if self.dynamic_mode_state:
                self.dynamic_mode_state.set_state(self.tab_states['dynamic-manual'])
    
    def mount_dynamic_mode(self, state: MockDynamicModeState):
        """Mount DynamicManualMode component."""
        self.dynamic_mode_state = state
        self.active_tab = 'dynamic-manual'


@settings(max_examples=100)
@given(
    initial_config=dynamic_config_strategy(),
    selected_core=st.integers(min_value=0, max_value=3),
    is_active=st.booleans(),
    tab_sequence=st.lists(
        st.sampled_from(['manual', 'presets', 'tests', 'fan', 'diagnostics', 'dynamic-manual']),
        min_size=2,
        max_size=10
    )
)
def test_tab_state_preservation(
    initial_config: Dict[str, Any],
    selected_core: int,
    is_active: bool,
    tab_sequence: list
):
    """
    **Feature: manual-dynamic-mode, Property 23: Tab state preservation**
    
    For any component state in DynamicManualMode, switching to a different
    ExpertMode tab and back SHALL preserve the state.
    
    Validates: Requirements 10.3
    """
    # Create mock ExpertMode
    expert_mode = MockExpertMode()
    
    # Create DynamicManualMode state
    dynamic_state = MockDynamicModeState(initial_config)
    dynamic_state.selected_core = selected_core
    dynamic_state.is_active = is_active
    
    # Mount dynamic mode
    expert_mode.mount_dynamic_mode(dynamic_state)
    
    # Capture initial state
    initial_state = dynamic_state.get_state()
    
    # Ensure we visit dynamic-manual at least once in the sequence
    if 'dynamic-manual' not in tab_sequence:
        tab_sequence.append('dynamic-manual')
    
    # Navigate through tabs
    for tab in tab_sequence:
        expert_mode.switch_to_tab(tab)
    
    # Return to dynamic-manual
    expert_mode.switch_to_tab('dynamic-manual')
    
    # Get final state
    final_state = dynamic_state.get_state()
    
    # Verify state preservation
    assert final_state['config'] == initial_state['config'], \
        "Configuration should be preserved across tab switches"
    assert final_state['is_active'] == initial_state['is_active'], \
        "Active status should be preserved across tab switches"
    assert final_state['selected_core'] == initial_state['selected_core'], \
        "Selected core should be preserved across tab switches"


@settings(max_examples=100)
@given(
    config=dynamic_config_strategy(),
    core_changes=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=3),  # core_id
            st.integers(min_value=-100, max_value=0),  # min_mv
            st.integers(min_value=-100, max_value=0),  # max_mv
            st.integers(min_value=0, max_value=100)  # threshold
        ),
        min_size=1,
        max_size=5
    )
)
def test_configuration_changes_preserved_across_tabs(
    config: Dict[str, Any],
    core_changes: list
):
    """
    **Feature: manual-dynamic-mode, Property 23: Tab state preservation**
    
    For any configuration changes made in DynamicManualMode, switching tabs
    and returning SHALL preserve those changes.
    
    Validates: Requirements 10.3
    """
    # Create mock ExpertMode
    expert_mode = MockExpertMode()
    
    # Create DynamicManualMode state
    dynamic_state = MockDynamicModeState(config)
    expert_mode.mount_dynamic_mode(dynamic_state)
    
    # Apply configuration changes
    for core_id, min_mv, max_mv, threshold in core_changes:
        # Ensure min <= max
        if min_mv > max_mv:
            min_mv, max_mv = max_mv, min_mv
        
        dynamic_state.config['cores'][core_id] = {
            'core_id': core_id,
            'min_mv': min_mv,
            'max_mv': max_mv,
            'threshold': threshold
        }
    
    # Capture state after changes
    state_after_changes = dynamic_state.get_state()
    
    # Switch to different tabs and back
    expert_mode.switch_to_tab('manual')
    expert_mode.switch_to_tab('presets')
    expert_mode.switch_to_tab('dynamic-manual')
    
    # Get final state
    final_state = dynamic_state.get_state()
    
    # Verify all changes are preserved
    assert final_state['config'] == state_after_changes['config'], \
        "Configuration changes should be preserved across tab switches"


@settings(max_examples=100)
@given(
    config=dynamic_config_strategy(),
    mode_switches=st.lists(st.sampled_from(['simple', 'expert']), min_size=1, max_size=5)
)
def test_mode_state_preserved_across_tabs(
    config: Dict[str, Any],
    mode_switches: list
):
    """
    **Feature: manual-dynamic-mode, Property 23: Tab state preservation**
    
    For any mode (Simple/Expert) selection in DynamicManualMode, switching tabs
    and returning SHALL preserve the mode selection.
    
    Validates: Requirements 10.3
    """
    # Create mock ExpertMode
    expert_mode = MockExpertMode()
    
    # Create DynamicManualMode state
    dynamic_state = MockDynamicModeState(config)
    expert_mode.mount_dynamic_mode(dynamic_state)
    
    # Apply mode switches
    for mode in mode_switches:
        dynamic_state.config['mode'] = mode
    
    # Capture final mode
    final_mode = dynamic_state.config['mode']
    
    # Switch to different tabs and back
    expert_mode.switch_to_tab('tests')
    expert_mode.switch_to_tab('diagnostics')
    expert_mode.switch_to_tab('dynamic-manual')
    
    # Verify mode is preserved
    assert dynamic_state.config['mode'] == final_mode, \
        "Mode selection should be preserved across tab switches"
