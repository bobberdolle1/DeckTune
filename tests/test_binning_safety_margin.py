"""Property test for binning safety margin recommendation.

Feature: decktune-3.0-automation, Property 6: Safety margin recommendation
Validates: Requirements 1.6, 1.7

Property 6: Safety margin recommendation
For any completed binning session with max_stable M, the recommended value must equal M + 5
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings

from backend.tuning.binning import BinningEngine, BinningConfig, BinningResult
from backend.platform.detect import PlatformInfo
from backend.core.safety import SafetyManager
from tests.test_binning_algorithm import (
    MockSettingsManager,
    MockRyzenadjWrapper,
    MockTestRunner,
    MockEventEmitter,
    create_default_platform
)


# Strategies for property testing
max_stable_strategy = st.integers(min_value=-50, max_value=0)


class TestBinningSafetyMargin:
    """Property 6: Safety margin recommendation
    
    For any completed binning session with max_stable M, the recommended value must equal M + 5
    
    Validates: Requirements 1.6, 1.7
    """
    
    @given(max_stable=max_stable_strategy)
    @settings(max_examples=100, deadline=None)
    def test_property_6_safety_margin_recommendation(self, max_stable: int):
        """Property 6: Safety margin recommendation
        
        For any completed binning session with max_stable M, the recommended value must equal M + 5
        
        Validates: Requirements 1.6, 1.7
        """
        # Setup
        platform = create_default_platform(safe_limit=-100)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        ryzenadj = MockRyzenadjWrapper()
        runner = MockTestRunner()
        event_emitter = MockEventEmitter()
        
        # Calculate how many passing tests we need to reach max_stable
        # Starting from -10 with step size 5: -10, -15, -20, -25, ...
        # We need to figure out how many steps to reach max_stable
        start_value = -10
        step_size = 5
        
        # Calculate number of iterations needed
        if max_stable >= start_value:
            # max_stable is less negative than start, so we start at max_stable
            start_value = max_stable
            num_passing = 1
        else:
            # Calculate steps: (start_value - max_stable) / step_size
            num_passing = ((start_value - max_stable) // step_size) + 1
        
        # Configure runner: pass enough tests to reach max_stable, then fail
        runner.test_results = [True] * num_passing + [False]
        
        config = BinningConfig(
            start_value=start_value,
            step_size=step_size,
            test_duration=1,
            max_iterations=50,
            consecutive_fail_limit=3
        )
        
        engine = BinningEngine(ryzenadj, runner, safety, event_emitter)
        
        # Run binning
        result = asyncio.run(engine.start(config))
        
        # Verify safety margin: recommended = max_stable + 5
        expected_recommended = result.max_stable + 5
        assert result.recommended == expected_recommended, \
            f"Recommended should be max_stable + 5 = {expected_recommended}, got {result.recommended}"
        
        # Also verify the relationship directly
        assert result.recommended - result.max_stable == 5, \
            f"Safety margin should be exactly 5mV, got {result.recommended - result.max_stable}mV"
    
    def test_safety_margin_with_zero_max_stable(self):
        """Safety margin should work when max_stable is 0 (no successful tests)."""
        # Setup
        platform = create_default_platform(safe_limit=-100)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        ryzenadj = MockRyzenadjWrapper()
        runner = MockTestRunner()
        event_emitter = MockEventEmitter()
        
        # Configure runner: fail immediately
        runner.test_results = [False]
        
        config = BinningConfig(
            start_value=-10,
            step_size=5,
            test_duration=1,
            max_iterations=10,
            consecutive_fail_limit=3
        )
        
        engine = BinningEngine(ryzenadj, runner, safety, event_emitter)
        
        # Run binning
        result = asyncio.run(engine.start(config))
        
        # Verify max_stable is 0 (no successful tests)
        assert result.max_stable == 0, f"max_stable should be 0, got {result.max_stable}"
        
        # Verify recommended is 5 (0 + 5)
        assert result.recommended == 5, f"recommended should be 5, got {result.recommended}"
    
    def test_safety_margin_with_negative_max_stable(self):
        """Safety margin should work with negative max_stable values."""
        # Setup
        platform = create_default_platform(safe_limit=-100)
        settings_manager = MockSettingsManager()
        safety = SafetyManager(settings_manager, platform)
        ryzenadj = MockRyzenadjWrapper()
        runner = MockTestRunner()
        event_emitter = MockEventEmitter()
        
        # Configure runner: pass 3 tests (-10, -15, -20), then fail
        runner.test_results = [True, True, True, False]
        
        config = BinningConfig(
            start_value=-10,
            step_size=5,
            test_duration=1,
            max_iterations=10,
            consecutive_fail_limit=3
        )
        
        engine = BinningEngine(ryzenadj, runner, safety, event_emitter)
        
        # Run binning
        result = asyncio.run(engine.start(config))
        
        # Verify max_stable is -20 (last successful test)
        assert result.max_stable == -20, f"max_stable should be -20, got {result.max_stable}"
        
        # Verify recommended is -15 (-20 + 5)
        assert result.recommended == -15, f"recommended should be -15, got {result.recommended}"
