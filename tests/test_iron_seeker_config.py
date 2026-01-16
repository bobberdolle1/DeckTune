"""Property-based tests for Iron Seeker configuration.

Feature: iron-seeker, Property 20: Configuration clamping
Validates: Requirements 7.3
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.tuning.iron_seeker import IronSeekerConfig


# Property 20: Configuration clamping
# For any configuration with step_size < 1 or > 20, the value SHALL be clamped to [1, 20];
# for test_duration < 10 or > 300, clamped to [10, 300];
# for safety_margin < 0 or > 20, clamped to [0, 20].
@given(
    step_size=st.integers(min_value=-100, max_value=200),
    test_duration=st.integers(min_value=-100, max_value=500),
    safety_margin=st.integers(min_value=-100, max_value=100),
    vdroop_pulse_ms=st.integers(min_value=-100, max_value=1000)
)
@settings(max_examples=100)
def test_property_20_configuration_clamping(step_size, test_duration, safety_margin, vdroop_pulse_ms):
    """**Feature: iron-seeker, Property 20: Configuration clamping**
    
    For any configuration values outside valid ranges, the values SHALL be
    clamped to their respective valid ranges:
    - step_size: [1, 20]
    - test_duration: [10, 300]
    - safety_margin: [0, 20]
    - vdroop_pulse_ms: [10, 500]
    
    **Validates: Requirements 7.3**
    """
    config = IronSeekerConfig(
        step_size=step_size,
        test_duration=test_duration,
        safety_margin=safety_margin,
        vdroop_pulse_ms=vdroop_pulse_ms
    )
    
    # Verify step_size is clamped to [1, 20]
    assert 1 <= config.step_size <= 20, f"step_size {config.step_size} not in [1, 20]"
    if step_size < 1:
        assert config.step_size == 1
    elif step_size > 20:
        assert config.step_size == 20
    else:
        assert config.step_size == step_size
    
    # Verify test_duration is clamped to [10, 300]
    assert 10 <= config.test_duration <= 300, f"test_duration {config.test_duration} not in [10, 300]"
    if test_duration < 10:
        assert config.test_duration == 10
    elif test_duration > 300:
        assert config.test_duration == 300
    else:
        assert config.test_duration == test_duration
    
    # Verify safety_margin is clamped to [0, 20]
    assert 0 <= config.safety_margin <= 20, f"safety_margin {config.safety_margin} not in [0, 20]"
    if safety_margin < 0:
        assert config.safety_margin == 0
    elif safety_margin > 20:
        assert config.safety_margin == 20
    else:
        assert config.safety_margin == safety_margin
    
    # Verify vdroop_pulse_ms is clamped to [10, 500]
    assert 10 <= config.vdroop_pulse_ms <= 500, f"vdroop_pulse_ms {config.vdroop_pulse_ms} not in [10, 500]"
    if vdroop_pulse_ms < 10:
        assert config.vdroop_pulse_ms == 10
    elif vdroop_pulse_ms > 500:
        assert config.vdroop_pulse_ms == 500
    else:
        assert config.vdroop_pulse_ms == vdroop_pulse_ms


@given(
    step_size=st.integers(min_value=1, max_value=20),
    test_duration=st.integers(min_value=10, max_value=300),
    safety_margin=st.integers(min_value=0, max_value=20),
    vdroop_pulse_ms=st.integers(min_value=10, max_value=500)
)
@settings(max_examples=100)
def test_valid_config_values_unchanged(step_size, test_duration, safety_margin, vdroop_pulse_ms):
    """Test that valid configuration values are not modified.
    
    For any configuration values within valid ranges, the values SHALL
    remain unchanged after construction.
    """
    config = IronSeekerConfig(
        step_size=step_size,
        test_duration=test_duration,
        safety_margin=safety_margin,
        vdroop_pulse_ms=vdroop_pulse_ms
    )
    
    assert config.step_size == step_size
    assert config.test_duration == test_duration
    assert config.safety_margin == safety_margin
    assert config.vdroop_pulse_ms == vdroop_pulse_ms


def test_default_config_values():
    """Test that default configuration values are correct.
    
    Requirements: 7.2
    """
    config = IronSeekerConfig()
    
    assert config.step_size == 5
    assert config.test_duration == 60
    assert config.safety_margin == 5
    assert config.vdroop_pulse_ms == 100
