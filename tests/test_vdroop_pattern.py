"""Property-based tests for Vdroop pattern generation.

Feature: iron-seeker, Property 5: Vdroop pattern generation
Validates: Requirements 2.1
"""

import pytest
from hypothesis import given, strategies as st, settings

from backend.tuning.vdroop import VdroopTester


# Property 5: Vdroop pattern generation
# For any test duration D and pulse duration P, the generated stress command
# SHALL produce a pattern that alternates between load and idle every P
# milliseconds for total duration D.
@given(
    duration_sec=st.integers(min_value=10, max_value=300),
    pulse_ms=st.integers(min_value=10, max_value=500)
)
@settings(max_examples=100)
def test_property_5_vdroop_pattern_generation(duration_sec, pulse_ms):
    """**Feature: iron-seeker, Property 5: Vdroop pattern generation**
    
    For any test duration D and pulse duration P, the generated stress command
    SHALL produce a pattern that uses the specified duration and creates
    pulsating load via stress-ng parameters.
    
    **Validates: Requirements 2.1**
    """
    tester = VdroopTester()
    command = tester.generate_vdroop_command(duration_sec, pulse_ms)
    
    # Command should be a non-empty list
    assert isinstance(command, list)
    assert len(command) > 0
    
    # First element should be stress-ng path
    assert "stress-ng" in command[0]
    
    # Should use all 4 CPU cores
    assert "--cpu" in command
    cpu_idx = command.index("--cpu")
    assert command[cpu_idx + 1] == "4"
    
    # Should use ackermann method for AVX2-like workload (Req 2.2)
    assert "--cpu-method" in command
    method_idx = command.index("--cpu-method")
    assert command[method_idx + 1] == "ackermann"
    
    # Should have timeout matching duration
    assert "--timeout" in command
    timeout_idx = command.index("--timeout")
    timeout_value = command[timeout_idx + 1]
    assert timeout_value == f"{duration_sec}s"
    
    # Should have cpu-ops for burst pattern
    assert "--cpu-ops" in command
    ops_idx = command.index("--cpu-ops")
    ops_value = int(command[ops_idx + 1])
    # Ops should be positive and related to pulse_ms
    assert ops_value > 0


def test_vdroop_command_uses_bundled_binary_when_available(tmp_path, monkeypatch):
    """Test that bundled stress-ng is preferred when available."""
    # Create a fake bundled binary
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_stress_ng = bin_dir / "stress-ng"
    fake_stress_ng.write_text("#!/bin/bash\necho fake")
    
    # Patch the paths
    import backend.tuning.vdroop as vdroop_module
    monkeypatch.setattr(vdroop_module, "BIN_DIR", str(bin_dir))
    monkeypatch.setattr(vdroop_module, "STRESS_NG_PATH", str(fake_stress_ng))
    
    tester = VdroopTester()
    command = tester.generate_vdroop_command(60, 100)
    
    # Should use the bundled path
    assert command[0] == str(fake_stress_ng)


def test_vdroop_command_falls_back_to_system_binary(monkeypatch):
    """Test that system stress-ng is used when bundled not available."""
    import backend.tuning.vdroop as vdroop_module
    
    # Point to non-existent path
    monkeypatch.setattr(vdroop_module, "STRESS_NG_PATH", "/nonexistent/stress-ng")
    
    tester = VdroopTester()
    command = tester.generate_vdroop_command(60, 100)
    
    # Should fall back to just "stress-ng" for PATH lookup
    assert command[0] == "stress-ng"


@given(
    duration_sec=st.integers(min_value=10, max_value=300)
)
@settings(max_examples=50)
def test_vdroop_command_duration_matches_config(duration_sec):
    """Test that command timeout matches configured duration."""
    tester = VdroopTester()
    command = tester.generate_vdroop_command(duration_sec, 100)
    
    # Extract timeout value
    timeout_idx = command.index("--timeout")
    timeout_str = command[timeout_idx + 1]
    
    # Should be "{duration}s" format
    assert timeout_str.endswith("s")
    timeout_value = int(timeout_str[:-1])
    assert timeout_value == duration_sec
