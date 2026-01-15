"""Property tests for Simple Mode value propagation.

Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation
Validates: Requirements 14.3

Property 14: Simple Mode Value Propagation
For any single slider value V in Simple Mode, all 4 cores SHALL receive exactly value V.
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.dynamic.config import (
    CoreConfig,
    DynamicConfig,
    SAFE_UNDERVOLT_MIN,
    SAFE_UNDERVOLT_MAX,
    EXPERT_UNDERVOLT_MIN,
)


# Strategy for valid safe mode undervolt values
safe_undervolt_value = st.integers(min_value=SAFE_UNDERVOLT_MIN, max_value=SAFE_UNDERVOLT_MAX)

# Strategy for valid expert mode undervolt values
expert_undervolt_value = st.integers(min_value=EXPERT_UNDERVOLT_MIN, max_value=SAFE_UNDERVOLT_MAX)


class TestSimpleModeValuePropagation:
    """Property 14: Simple Mode Value Propagation
    
    For any single slider value V in Simple Mode, all 4 cores SHALL receive
    exactly value V.
    
    Validates: Requirements 14.3
    """

    @given(simple_value=safe_undervolt_value)
    @settings(max_examples=100)
    def test_simple_mode_propagates_value_to_all_cores(self, simple_value: int):
        """In simple mode, get_effective_core_values returns same value for all cores.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.3**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=simple_value,
        )
        
        effective_values = config.get_effective_core_values()
        
        # All 4 cores should have exactly the simple_value
        assert len(effective_values) == 4, f"Expected 4 values, got {len(effective_values)}"
        for i, value in enumerate(effective_values):
            assert value == simple_value, (
                f"Core {i} has value {value}, expected {simple_value}"
            )

    @given(simple_value=expert_undervolt_value)
    @settings(max_examples=100)
    def test_simple_mode_expert_range_propagates_to_all_cores(self, simple_value: int):
        """In expert simple mode, extended range values propagate to all cores.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.3**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=simple_value,
            expert_mode=True,
        )
        
        effective_values = config.get_effective_core_values()
        
        # All 4 cores should have exactly the simple_value
        assert len(effective_values) == 4
        assert all(v == simple_value for v in effective_values), (
            f"Not all cores have value {simple_value}: {effective_values}"
        )

    @given(
        core0_mv=safe_undervolt_value,
        core1_mv=safe_undervolt_value,
        core2_mv=safe_undervolt_value,
        core3_mv=safe_undervolt_value,
    )
    @settings(max_examples=100)
    def test_per_core_mode_returns_individual_values(
        self, core0_mv: int, core1_mv: int, core2_mv: int, core3_mv: int
    ):
        """When simple_mode is False, each core returns its own max_mv.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.3**
        """
        cores = [
            CoreConfig(min_mv=0, max_mv=core0_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core1_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core2_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core3_mv, threshold=50.0),
        ]
        
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=False,
            cores=cores,
        )
        
        effective_values = config.get_effective_core_values()
        
        assert effective_values[0] == core0_mv
        assert effective_values[1] == core1_mv
        assert effective_values[2] == core2_mv
        assert effective_values[3] == core3_mv

    @given(simple_value=safe_undervolt_value)
    @settings(max_examples=100)
    def test_apply_simple_value_to_cores_sets_all_cores(self, simple_value: int):
        """apply_simple_value_to_cores sets all cores to simple_value.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.5**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=simple_value,
        )
        
        config.apply_simple_value_to_cores()
        
        # All cores should now have min_mv and max_mv set to simple_value
        for i, core in enumerate(config.cores):
            assert core.min_mv == simple_value, (
                f"Core {i} min_mv is {core.min_mv}, expected {simple_value}"
            )
            assert core.max_mv == simple_value, (
                f"Core {i} max_mv is {core.max_mv}, expected {simple_value}"
            )

    @given(
        core0_mv=safe_undervolt_value,
        core1_mv=safe_undervolt_value,
        core2_mv=safe_undervolt_value,
        core3_mv=safe_undervolt_value,
    )
    @settings(max_examples=100)
    def test_calculate_simple_value_from_cores_averages(
        self, core0_mv: int, core1_mv: int, core2_mv: int, core3_mv: int
    ):
        """calculate_simple_value_from_cores returns average of core values.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.4**
        """
        cores = [
            CoreConfig(min_mv=0, max_mv=core0_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core1_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core2_mv, threshold=50.0),
            CoreConfig(min_mv=0, max_mv=core3_mv, threshold=50.0),
        ]
        
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=False,
            cores=cores,
        )
        
        calculated = config.calculate_simple_value_from_cores()
        expected = round((core0_mv + core1_mv + core2_mv + core3_mv) / 4)
        
        assert calculated == expected, (
            f"Calculated {calculated}, expected average {expected}"
        )

    @given(simple_value=safe_undervolt_value)
    @settings(max_examples=100)
    def test_simple_mode_validation_accepts_valid_values(self, simple_value: int):
        """Simple mode with valid values passes validation.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.6**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=simple_value,
            expert_mode=False,
        )
        
        errors = config.validate()
        simple_errors = [e for e in errors if "simple_value" in e]
        
        assert len(simple_errors) == 0, f"Valid simple_value rejected: {simple_errors}"

    @given(value=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_simple_mode_rejects_positive_values(self, value: int):
        """Simple mode rejects positive undervolt values.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.6**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=value,
        )
        
        errors = config.validate()
        simple_errors = [e for e in errors if "simple_value" in e]
        
        assert len(simple_errors) > 0, f"Positive simple_value {value} accepted"

    @given(value=st.integers(min_value=-150, max_value=SAFE_UNDERVOLT_MIN - 1))
    @settings(max_examples=100)
    def test_simple_mode_safe_rejects_expert_values(self, value: int):
        """In safe mode, simple_value below platform limit is rejected.
        
        **Feature: dynamic-mode-refactor, Property 14: Simple Mode Value Propagation**
        **Validates: Requirements 14.6**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=value,
            expert_mode=False,
        )
        
        errors = config.validate()
        simple_errors = [e for e in errors if "simple_value" in e]
        
        assert len(simple_errors) > 0, f"Expert-only simple_value {value} accepted in safe mode"
