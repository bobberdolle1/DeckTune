"""Integration test for Simple Mode with DynamicController.

Feature: dynamic-mode-refactor
Validates: Requirements 14.1-14.7

Verifies that the DynamicController properly builds command-line arguments
for gymdeck3 when simple_mode is enabled.
"""

import pytest
from backend.dynamic.config import DynamicConfig, CoreConfig
from backend.dynamic.controller import DynamicController


class TestSimpleModeIntegration:
    """Integration tests for Simple Mode with DynamicController."""

    def test_build_args_with_simple_mode(self):
        """Controller builds correct args when simple_mode is True.
        
        **Feature: dynamic-mode-refactor**
        **Validates: Requirements 14.3, 14.7**
        """
        # Create a mock controller (we won't actually start it)
        controller = DynamicController(
            ryzenadj_path="/bin/ryzenadj",
            gymdeck3_path="/bin/gymdeck3",
            event_emitter=None,  # type: ignore
            safety_manager=None,
        )
        
        # Create config with simple mode enabled
        config = DynamicConfig(
            strategy="balanced",
            sample_interval_ms=100,
            simple_mode=True,
            simple_value=-30,
            cores=[
                CoreConfig(min_mv=-20, max_mv=-25, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-25, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-25, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-25, threshold=50.0),
            ],
        )
        
        # Build args
        args = controller._build_args(config)
        
        # Verify strategy and sample interval
        assert args[0] == "balanced"
        assert args[1] == "100000"  # Converted to microseconds
        
        # Verify simple mode propagates to all cores
        core_args = [arg for arg in args if arg.startswith("--core=")]
        assert len(core_args) == 4, "Should have 4 core arguments"
        
        # All cores should use simple_value (-30) for both min and max
        for i, core_arg in enumerate(core_args):
            # Format: --core=N:MIN:MAX:THRESHOLD
            parts = core_arg.split("=")[1].split(":")
            core_idx = int(parts[0])
            min_mv = int(parts[1])
            max_mv = int(parts[2])
            
            assert core_idx == i, f"Core index mismatch"
            assert min_mv == -30, f"Core {i} min_mv should be -30, got {min_mv}"
            assert max_mv == -30, f"Core {i} max_mv should be -30, got {max_mv}"

    def test_build_args_with_per_core_mode(self):
        """Controller builds correct args when simple_mode is False.
        
        **Feature: dynamic-mode-refactor**
        **Validates: Requirements 14.3**
        """
        controller = DynamicController(
            ryzenadj_path="/bin/ryzenadj",
            gymdeck3_path="/bin/gymdeck3",
            event_emitter=None,  # type: ignore
            safety_manager=None,
        )
        
        # Create config with per-core mode (simple_mode=False)
        config = DynamicConfig(
            strategy="balanced",
            sample_interval_ms=100,
            simple_mode=False,
            cores=[
                CoreConfig(min_mv=-15, max_mv=-25, threshold=50.0),
                CoreConfig(min_mv=-18, max_mv=-28, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                CoreConfig(min_mv=-22, max_mv=-32, threshold=50.0),
            ],
        )
        
        # Build args
        args = controller._build_args(config)
        
        # Verify per-core values are used
        core_args = [arg for arg in args if arg.startswith("--core=")]
        assert len(core_args) == 4
        
        expected_values = [
            (0, -15, -25),
            (1, -18, -28),
            (2, -20, -30),
            (3, -22, -32),
        ]
        
        for core_arg, (expected_idx, expected_min, expected_max) in zip(core_args, expected_values):
            parts = core_arg.split("=")[1].split(":")
            core_idx = int(parts[0])
            min_mv = int(parts[1])
            max_mv = int(parts[2])
            
            assert core_idx == expected_idx
            assert min_mv == expected_min, f"Core {core_idx} min_mv should be {expected_min}, got {min_mv}"
            assert max_mv == expected_max, f"Core {core_idx} max_mv should be {expected_max}, got {max_mv}"

    def test_get_effective_core_values_simple_mode(self):
        """get_effective_core_values returns simple_value for all cores in simple mode.
        
        **Feature: dynamic-mode-refactor**
        **Validates: Requirements 14.3**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=True,
            simple_value=-28,
        )
        
        values = config.get_effective_core_values()
        
        assert values == [-28, -28, -28, -28]

    def test_get_effective_core_values_per_core_mode(self):
        """get_effective_core_values returns individual max_mv in per-core mode.
        
        **Feature: dynamic-mode-refactor**
        **Validates: Requirements 14.3**
        """
        config = DynamicConfig(
            strategy="balanced",
            simple_mode=False,
            cores=[
                CoreConfig(min_mv=-15, max_mv=-25, threshold=50.0),
                CoreConfig(min_mv=-18, max_mv=-28, threshold=50.0),
                CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                CoreConfig(min_mv=-22, max_mv=-32, threshold=50.0),
            ],
        )
        
        values = config.get_effective_core_values()
        
        assert values == [-25, -28, -30, -32]
