"""Property tests for Expert Mode value range validation.

Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range
Validates: Requirements 13.2

Feature: decktune-critical-fixes, Property 6: Extended Expert Mode Range
Validates: Requirements 5.3

Property 13: Expert Mode Value Range
For any undervolt value V, if expert_mode is true then V in range [0, -100] 
SHALL be accepted; if expert_mode is false then V SHALL be clamped to platform limits.

Property 6 (Critical Fixes): Расширенный диапазон в Expert Mode
For any undervolt value in range [-100, 0], if Expert Mode is active and confirmed,
the value must be accepted without clamping to platform safe_limit.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from backend.dynamic.config import (
    CoreConfig,
    DynamicConfig,
    SAFE_UNDERVOLT_MIN,
    SAFE_UNDERVOLT_MAX,
    EXPERT_UNDERVOLT_MIN,
)


# Strategy for undervolt values covering full range including out-of-bounds
undervolt_value = st.integers(min_value=-150, max_value=50)

# Strategy for valid safe mode undervolt values
safe_undervolt_value = st.integers(min_value=SAFE_UNDERVOLT_MIN, max_value=SAFE_UNDERVOLT_MAX)

# Strategy for valid expert mode undervolt values
expert_undervolt_value = st.integers(min_value=EXPERT_UNDERVOLT_MIN, max_value=SAFE_UNDERVOLT_MAX)

# Strategy for values that are valid in expert mode but not in safe mode
expert_only_value = st.integers(min_value=EXPERT_UNDERVOLT_MIN, max_value=SAFE_UNDERVOLT_MIN - 1)


class TestExpertModeValueRange:
    """Property 13: Expert Mode Value Range
    
    For any undervolt value V:
    - If expert_mode is true, V in range [0, -100] SHALL be accepted
    - If expert_mode is false, V SHALL be clamped to platform limits [-35, 0]
    
    Validates: Requirements 13.2
    """

    @given(min_mv=safe_undervolt_value, max_mv=safe_undervolt_value)
    @settings(max_examples=100)
    def test_safe_mode_accepts_values_within_platform_limits(
        self, min_mv: int, max_mv: int
    ):
        """In safe mode, values within platform limits [-35, 0] are accepted.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Ensure min_mv >= max_mv (min is less negative)
        if min_mv < max_mv:
            min_mv, max_mv = max_mv, min_mv
        
        core = CoreConfig(min_mv=min_mv, max_mv=max_mv, threshold=50.0)
        errors = core.validate(expert_mode=False)
        
        # Should have no errors for values within safe range
        assert len(errors) == 0, f"Safe values {min_mv}, {max_mv} rejected: {errors}"

    @given(min_mv=expert_undervolt_value, max_mv=expert_undervolt_value)
    @settings(max_examples=100)
    def test_expert_mode_accepts_extended_range(
        self, min_mv: int, max_mv: int
    ):
        """In expert mode, values in extended range [-100, 0] are accepted.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Ensure min_mv >= max_mv (min is less negative)
        if min_mv < max_mv:
            min_mv, max_mv = max_mv, min_mv
        
        core = CoreConfig(min_mv=min_mv, max_mv=max_mv, threshold=50.0)
        errors = core.validate(expert_mode=True)
        
        # Should have no errors for values within expert range
        assert len(errors) == 0, f"Expert values {min_mv}, {max_mv} rejected: {errors}"

    @given(value=expert_only_value)
    @settings(max_examples=100)
    def test_safe_mode_rejects_expert_only_values(self, value: int):
        """In safe mode, values below platform limit are rejected.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Use the expert-only value for both min and max
        core = CoreConfig(min_mv=value, max_mv=value, threshold=50.0)
        errors = core.validate(expert_mode=False)
        
        # Should have errors for values below safe limit
        assert len(errors) > 0, f"Expert-only value {value} accepted in safe mode"
        # Check that the error mentions the limit
        error_text = " ".join(errors)
        assert str(SAFE_UNDERVOLT_MIN) in error_text or "must be >=" in error_text

    @given(value=expert_only_value)
    @settings(max_examples=100)
    def test_expert_mode_accepts_expert_only_values(self, value: int):
        """In expert mode, values below safe limit but within expert range are accepted.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Use the expert-only value for both min and max
        core = CoreConfig(min_mv=value, max_mv=value, threshold=50.0)
        errors = core.validate(expert_mode=True)
        
        # Should have no errors in expert mode
        assert len(errors) == 0, f"Expert-only value {value} rejected in expert mode: {errors}"

    @given(value=st.integers(min_value=-150, max_value=EXPERT_UNDERVOLT_MIN - 1))
    @settings(max_examples=100)
    def test_expert_mode_rejects_values_below_expert_limit(self, value: int):
        """Even in expert mode, values below -100mV are rejected.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        core = CoreConfig(min_mv=value, max_mv=value, threshold=50.0)
        errors = core.validate(expert_mode=True)
        
        # Should have errors for values below expert limit
        assert len(errors) > 0, f"Value {value} below expert limit accepted"

    @given(value=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_positive_values_rejected_in_both_modes(self, value: int):
        """Positive undervolt values are rejected in both modes.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        core = CoreConfig(min_mv=value, max_mv=value, threshold=50.0)
        
        # Should be rejected in safe mode
        safe_errors = core.validate(expert_mode=False)
        assert len(safe_errors) > 0, f"Positive value {value} accepted in safe mode"
        
        # Should also be rejected in expert mode
        expert_errors = core.validate(expert_mode=True)
        assert len(expert_errors) > 0, f"Positive value {value} accepted in expert mode"

    @given(
        min_mv=expert_undervolt_value,
        max_mv=expert_undervolt_value,
        expert_mode=st.booleans()
    )
    @settings(max_examples=100)
    def test_dynamic_config_propagates_expert_mode(
        self, min_mv: int, max_mv: int, expert_mode: bool
    ):
        """DynamicConfig.validate() correctly propagates expert_mode to core validation.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Ensure min_mv >= max_mv
        if min_mv < max_mv:
            min_mv, max_mv = max_mv, min_mv
        
        # Create config with 4 identical cores
        cores = [CoreConfig(min_mv=min_mv, max_mv=max_mv, threshold=50.0) for _ in range(4)]
        config = DynamicConfig(
            strategy="balanced",
            cores=cores,
            expert_mode=expert_mode
        )
        
        errors = config.validate()
        
        # Determine if values are within the appropriate range
        if expert_mode:
            # Expert mode: values should be valid if within [-100, 0]
            values_valid = EXPERT_UNDERVOLT_MIN <= max_mv <= SAFE_UNDERVOLT_MAX
        else:
            # Safe mode: values should be valid if within [-35, 0]
            values_valid = SAFE_UNDERVOLT_MIN <= max_mv <= SAFE_UNDERVOLT_MAX
        
        if values_valid:
            # Filter out non-value-related errors
            value_errors = [e for e in errors if "min_mv" in e or "max_mv" in e]
            assert len(value_errors) == 0, f"Valid values rejected: {value_errors}"
        else:
            # Should have value-related errors
            value_errors = [e for e in errors if "min_mv" in e or "max_mv" in e]
            assert len(value_errors) > 0, f"Invalid values accepted: min={min_mv}, max={max_mv}"

    @settings(max_examples=100)
    @given(
        safe_value=safe_undervolt_value,
        expert_value=expert_only_value
    )
    def test_mode_switch_changes_validation_result(
        self, safe_value: int, expert_value: int
    ):
        """Switching expert_mode changes whether expert-only values are accepted.
        
        **Feature: dynamic-mode-refactor, Property 13: Expert Mode Value Range**
        **Validates: Requirements 13.2**
        """
        # Create core with expert-only value
        core = CoreConfig(min_mv=expert_value, max_mv=expert_value, threshold=50.0)
        
        # Should be rejected in safe mode
        safe_errors = core.validate(expert_mode=False)
        assert len(safe_errors) > 0, "Expert value accepted in safe mode"
        
        # Should be accepted in expert mode
        expert_errors = core.validate(expert_mode=True)
        assert len(expert_errors) == 0, f"Expert value rejected in expert mode: {expert_errors}"

