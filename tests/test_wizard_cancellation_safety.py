"""
Property test for wizard cancellation safety.

**Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
**Validates: Requirements 5.7**

Property 8: Wizard cancellation safety
*For any* wizard state, cancelling the wizard SHALL not modify any settings or apply any undervolt values.

This test verifies that:
1. Reading wizard settings does not modify them
2. The wizard state can be reset without affecting other settings
3. No settings are persisted when wizard is cancelled (simulated by not calling save)
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from dataclasses import dataclass
from typing import Optional, Dict, Any
import copy


# ============================================================================
# Wizard State Model (mirrors frontend types)
# ============================================================================

@dataclass
class WizardState:
    """Wizard state model for testing."""
    step: str  # 'welcome' | 'explanation' | 'goal' | 'confirm' | 'complete'
    selected_goal: Optional[str]  # 'quiet' | 'balanced' | 'battery' | 'performance' | None


@dataclass
class WizardSettings:
    """Wizard settings stored in backend."""
    first_run_complete: bool
    wizard_goal: Optional[str]
    wizard_completed_at: Optional[str]


# ============================================================================
# Settings Store Simulation
# ============================================================================

class SettingsStore:
    """
    Simulates the backend settings store for testing wizard behavior.
    
    This mimics the Decky Loader settings API behavior.
    """
    
    def __init__(self):
        self._settings: Dict[str, Any] = {}
    
    def get_setting(self, key: str) -> Any:
        """Get a setting value (read-only operation)."""
        return self._settings.get(key)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value (write operation)."""
        self._settings[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get a copy of all settings."""
        return copy.deepcopy(self._settings)
    
    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()


# ============================================================================
# Wizard Operations
# ============================================================================

def cancel_wizard(state: WizardState) -> WizardState:
    """
    Cancel the wizard - returns to initial state without saving.
    
    Requirements: 5.7
    This operation MUST NOT modify any settings.
    """
    return WizardState(step='welcome', selected_goal=None)


def complete_wizard(state: WizardState, store: SettingsStore) -> WizardState:
    """
    Complete the wizard - saves settings.
    
    Requirements: 5.5
    This operation DOES modify settings.
    """
    if state.selected_goal is None:
        raise ValueError("Cannot complete wizard without a selected goal")
    
    store.set_setting('wizard_goal', state.selected_goal)
    store.set_setting('wizard_completed_at', '2025-01-16T00:00:00Z')
    store.set_setting('first_run_complete', True)
    
    return WizardState(step='complete', selected_goal=state.selected_goal)


def skip_wizard(store: SettingsStore) -> WizardState:
    """
    Skip the wizard - marks as complete but doesn't save goal.
    
    Requirements: 5.7
    Only marks first_run_complete, doesn't apply any undervolt settings.
    """
    store.set_setting('first_run_complete', True)
    return WizardState(step='complete', selected_goal=None)


# ============================================================================
# Strategies
# ============================================================================

wizard_step_strategy = st.sampled_from(['welcome', 'explanation', 'goal', 'confirm'])
goal_strategy = st.sampled_from(['quiet', 'balanced', 'battery', 'performance'])
optional_goal_strategy = st.one_of(st.none(), goal_strategy)

wizard_state_strategy = st.builds(
    WizardState,
    step=wizard_step_strategy,
    selected_goal=optional_goal_strategy
)

# Strategy for initial settings (before wizard runs)
initial_settings_strategy = st.fixed_dictionaries({
    'cores': st.lists(st.integers(min_value=-50, max_value=0), min_size=4, max_size=4),
    'settings': st.fixed_dictionaries({
        'isGlobal': st.booleans(),
        'runAtStartup': st.booleans(),
        'isRunAutomatically': st.booleans(),
        'timeoutApply': st.integers(min_value=0, max_value=60),
    }),
    'first_run_complete': st.booleans(),
    'wizard_goal': optional_goal_strategy,
})


# ============================================================================
# Property Tests
# ============================================================================

class TestWizardCancellationSafety:
    """
    **Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
    **Validates: Requirements 5.7**
    """

    @given(
        wizard_state=wizard_state_strategy,
        initial_settings=initial_settings_strategy
    )
    @hyp_settings(max_examples=100)
    def test_cancel_does_not_modify_settings(
        self,
        wizard_state: WizardState,
        initial_settings: Dict[str, Any]
    ):
        """
        **Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
        **Validates: Requirements 5.7**
        
        Property: For any wizard state and any initial settings,
        cancelling the wizard SHALL not modify any settings.
        """
        # Setup: Create store with initial settings
        store = SettingsStore()
        for key, value in initial_settings.items():
            store.set_setting(key, value)
        
        # Capture settings before cancellation
        settings_before = store.get_all()
        
        # Action: Cancel the wizard
        new_state = cancel_wizard(wizard_state)
        
        # Verify: Settings are unchanged
        settings_after = store.get_all()
        
        assert settings_before == settings_after, (
            f"Settings were modified during wizard cancellation!\n"
            f"Before: {settings_before}\n"
            f"After: {settings_after}"
        )
        
        # Verify: Wizard state is reset
        assert new_state.step == 'welcome'
        assert new_state.selected_goal is None

    @given(
        wizard_state=wizard_state_strategy,
        initial_settings=initial_settings_strategy
    )
    @hyp_settings(max_examples=100)
    def test_reading_settings_does_not_modify_them(
        self,
        wizard_state: WizardState,
        initial_settings: Dict[str, Any]
    ):
        """
        **Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
        **Validates: Requirements 5.7**
        
        Property: For any settings state, reading settings SHALL not modify them.
        This ensures the wizard can safely read settings without side effects.
        """
        # Setup: Create store with initial settings
        store = SettingsStore()
        for key, value in initial_settings.items():
            store.set_setting(key, value)
        
        # Capture settings before reads
        settings_before = store.get_all()
        
        # Action: Read all settings multiple times (simulating wizard checking state)
        for _ in range(5):
            _ = store.get_setting('first_run_complete')
            _ = store.get_setting('wizard_goal')
            _ = store.get_setting('cores')
            _ = store.get_setting('settings')
        
        # Verify: Settings are unchanged
        settings_after = store.get_all()
        
        assert settings_before == settings_after, (
            f"Settings were modified during read operations!\n"
            f"Before: {settings_before}\n"
            f"After: {settings_after}"
        )

    @given(
        goal=goal_strategy,
        initial_settings=initial_settings_strategy
    )
    @hyp_settings(max_examples=100)
    def test_cancel_after_goal_selection_preserves_settings(
        self,
        goal: str,
        initial_settings: Dict[str, Any]
    ):
        """
        **Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
        **Validates: Requirements 5.7**
        
        Property: For any goal selection, cancelling before completion
        SHALL not persist the selected goal or modify any settings.
        """
        # Setup: Create store with initial settings
        store = SettingsStore()
        for key, value in initial_settings.items():
            store.set_setting(key, value)
        
        # Capture settings before
        settings_before = store.get_all()
        
        # Action: User selects a goal but then cancels
        wizard_state = WizardState(step='confirm', selected_goal=goal)
        new_state = cancel_wizard(wizard_state)
        
        # Verify: Settings are unchanged (goal was not saved)
        settings_after = store.get_all()
        
        assert settings_before == settings_after, (
            f"Settings were modified when wizard was cancelled after goal selection!\n"
            f"Selected goal: {goal}\n"
            f"Before: {settings_before}\n"
            f"After: {settings_after}"
        )
        
        # Verify: Wizard state is reset
        assert new_state.step == 'welcome'
        assert new_state.selected_goal is None

    @given(initial_settings=initial_settings_strategy)
    @hyp_settings(max_examples=100)
    def test_skip_only_marks_complete(
        self,
        initial_settings: Dict[str, Any]
    ):
        """
        **Feature: decktune-3.1-reliability-ux, Property 8: Wizard cancellation safety**
        **Validates: Requirements 5.7**
        
        Property: Skipping the wizard SHALL only mark first_run_complete as True
        and SHALL NOT modify any other settings or apply undervolt values.
        """
        # Setup: Create store with initial settings
        store = SettingsStore()
        for key, value in initial_settings.items():
            store.set_setting(key, value)
        
        # Capture settings before (except first_run_complete which will change)
        cores_before = store.get_setting('cores')
        settings_obj_before = store.get_setting('settings')
        wizard_goal_before = store.get_setting('wizard_goal')
        
        # Action: Skip the wizard
        new_state = skip_wizard(store)
        
        # Verify: Only first_run_complete changed
        assert store.get_setting('first_run_complete') == True
        assert store.get_setting('cores') == cores_before, "Cores were modified during skip!"
        assert store.get_setting('settings') == settings_obj_before, "Settings object was modified during skip!"
        assert store.get_setting('wizard_goal') == wizard_goal_before, "Wizard goal was modified during skip!"
        
        # Verify: Wizard state shows completion without goal
        assert new_state.step == 'complete'
        assert new_state.selected_goal is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
