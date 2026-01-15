#!/usr/bin/env python3
"""Manual integration testing script for dynamic mode refactor.

This script performs comprehensive end-to-end testing of the dynamic mode
system, including:
- Dynamic mode start/stop
- Load monitoring and value adaptation
- Expert mode with extended range
- Simple mode value propagation
- Migration from old settings format

Feature: dynamic-mode-refactor
Task: 18.3 Manual integration testing

Usage:
    python tests/manual_integration_test.py

Requirements:
    - gymdeck3 binary must be built and available in bin/
    - ryzenadj binary must be available (can be mocked for testing)
    - Must be run with appropriate permissions (or with mock ryzenadj)
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dynamic.controller import DynamicController
from backend.dynamic.config import DynamicConfig, CoreConfig, DynamicStatus
from backend.dynamic.migration import migrate_dynamic_settings, is_old_format
from backend.dynamic.profiles import ProfileManager, DynamicProfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockEventEmitter:
    """Mock event emitter for testing."""
    
    def __init__(self):
        self.events: List[tuple] = []
    
    async def emit_status(self, status: str):
        """Emit status event."""
        self.events.append(("status", status))
        logger.info(f"Event: status={status}")
    
    async def _emit_event(self, event_type: str, data: Any):
        """Emit generic event."""
        self.events.append((event_type, data))
        logger.info(f"Event: {event_type}={data}")


class IntegrationTestRunner:
    """Runner for manual integration tests."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
        
        # Paths
        self.workspace_root = Path(__file__).parent.parent
        # Use macOS binary for testing if available, otherwise use Linux binary
        gymdeck3_macos = self.workspace_root / "bin" / "gymdeck3-macos"
        if gymdeck3_macos.exists():
            self.gymdeck3_path = gymdeck3_macos
        else:
            self.gymdeck3_path = self.workspace_root / "bin" / "gymdeck3"
        self.ryzenadj_path = self.workspace_root / "bin" / "ryzenadj"
        
        # Check if we need to use mock ryzenadj
        if not self.ryzenadj_path.exists():
            logger.warning("ryzenadj not found, will use mock")
            self.ryzenadj_path = self._create_mock_ryzenadj()
        
        self.event_emitter = MockEventEmitter()
        self.controller = None
    
    def _create_mock_ryzenadj(self) -> Path:
        """Create a mock ryzenadj script for testing."""
        mock_path = self.workspace_root / "bin" / "mock_ryzenadj.sh"
        mock_path.parent.mkdir(parents=True, exist_ok=True)
        
        mock_script = """#!/bin/bash
# Mock ryzenadj for testing
echo "Mock ryzenadj called with: $@"
exit 0
"""
        mock_path.write_text(mock_script)
        mock_path.chmod(0o755)
        logger.info(f"Created mock ryzenadj at {mock_path}")
        return mock_path
    
    def assert_true(self, condition: bool, message: str):
        """Assert that condition is true."""
        if condition:
            logger.info(f"✓ PASS: {message}")
            self.passed += 1
        else:
            logger.error(f"✗ FAIL: {message}")
            self.failed += 1
    
    def assert_equal(self, actual, expected, message: str):
        """Assert that actual equals expected."""
        if actual == expected:
            logger.info(f"✓ PASS: {message}")
            self.passed += 1
        else:
            logger.error(f"✗ FAIL: {message} (expected {expected}, got {actual})")
            self.failed += 1
    
    async def test_dynamic_mode_start_stop(self):
        """Test 1: Dynamic mode start/stop."""
        logger.info("\n=== Test 1: Dynamic Mode Start/Stop ===")
        self.tests_run += 1
        
        try:
            # Create controller
            self.controller = DynamicController(
                ryzenadj_path=str(self.ryzenadj_path),
                gymdeck3_path=str(self.gymdeck3_path),
                event_emitter=self.event_emitter,
            )
            
            # Test initial state
            self.assert_true(
                not self.controller.is_running(),
                "Controller should not be running initially"
            )
            
            # Create a simple config
            config = DynamicConfig(
                strategy="balanced",
                sample_interval_ms=100,
                hysteresis_percent=5.0,
            )
            
            # Start dynamic mode
            logger.info("Starting dynamic mode...")
            success = await self.controller.start(config)
            self.assert_true(success, "Dynamic mode should start successfully")
            
            # Wait a bit for process to initialize
            await asyncio.sleep(1.0)
            
            # Check running state
            self.assert_true(
                self.controller.is_running(),
                "Controller should be running after start"
            )
            
            # Get status
            status = await self.controller.get_status()
            self.assert_true(status.running, "Status should show running=True")
            self.assert_equal(status.strategy, "balanced", "Strategy should be 'balanced'")
            
            # Wait for some status updates
            logger.info("Waiting for status updates...")
            await asyncio.sleep(3.0)
            
            # Check that we received events
            status_events = [e for e in self.event_emitter.events if e[0] == "dynamic_status"]
            self.assert_true(
                len(status_events) > 0,
                f"Should receive status events (got {len(status_events)})"
            )
            
            # Stop dynamic mode
            logger.info("Stopping dynamic mode...")
            success = await self.controller.stop()
            self.assert_true(success, "Dynamic mode should stop successfully")
            
            # Check stopped state
            self.assert_true(
                not self.controller.is_running(),
                "Controller should not be running after stop"
            )
            
            logger.info("✓ Test 1 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 1 failed with exception: {e}")
            self.failed += 1
    
    async def test_load_monitoring_and_adaptation(self):
        """Test 2: Load monitoring and value adaptation."""
        logger.info("\n=== Test 2: Load Monitoring and Value Adaptation ===")
        self.tests_run += 1
        
        try:
            # Create config with different thresholds
            config = DynamicConfig(
                strategy="aggressive",
                sample_interval_ms=50,
                hysteresis_percent=3.0,
                cores=[
                    CoreConfig(min_mv=-20, max_mv=-35, threshold=40.0),
                    CoreConfig(min_mv=-20, max_mv=-35, threshold=40.0),
                    CoreConfig(min_mv=-20, max_mv=-35, threshold=40.0),
                    CoreConfig(min_mv=-20, max_mv=-35, threshold=40.0),
                ],
            )
            
            # Start dynamic mode
            logger.info("Starting dynamic mode with aggressive strategy...")
            success = await self.controller.start(config)
            self.assert_true(success, "Dynamic mode should start")
            
            # Wait for status updates
            await asyncio.sleep(5.0)
            
            # Get status
            status = await self.controller.get_status()
            
            # Check that load values are present
            self.assert_true(
                len(status.load) == 4,
                f"Should have 4 load values (got {len(status.load)})"
            )
            
            # Check that load values are in valid range
            for i, load in enumerate(status.load):
                self.assert_true(
                    0.0 <= load <= 100.0,
                    f"Core {i} load should be in [0, 100] (got {load})"
                )
            
            # Check that values are present
            self.assert_true(
                len(status.values) == 4,
                f"Should have 4 undervolt values (got {len(status.values)})"
            )
            
            # Check that values are in valid range
            for i, value in enumerate(status.values):
                self.assert_true(
                    -35 <= value <= 0,
                    f"Core {i} value should be in [-35, 0] (got {value})"
                )
            
            # Check uptime is increasing
            uptime1 = status.uptime_ms
            await asyncio.sleep(2.0)
            status = await self.controller.get_status()
            uptime2 = status.uptime_ms
            self.assert_true(
                uptime2 > uptime1,
                f"Uptime should increase (was {uptime1}, now {uptime2})"
            )
            
            # Stop
            await self.controller.stop()
            logger.info("✓ Test 2 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 2 failed with exception: {e}")
            self.failed += 1
    
    async def test_expert_mode_extended_range(self):
        """Test 3: Expert mode with extended range."""
        logger.info("\n=== Test 3: Expert Mode Extended Range ===")
        self.tests_run += 1
        
        try:
            # Create config with expert mode enabled
            config = DynamicConfig(
                strategy="balanced",
                sample_interval_ms=100,
                expert_mode=True,
                cores=[
                    CoreConfig(min_mv=-50, max_mv=-80, threshold=50.0),
                    CoreConfig(min_mv=-50, max_mv=-80, threshold=50.0),
                    CoreConfig(min_mv=-50, max_mv=-80, threshold=50.0),
                    CoreConfig(min_mv=-50, max_mv=-80, threshold=50.0),
                ],
            )
            
            # Validate config
            errors = config.validate()
            self.assert_true(
                len(errors) == 0,
                f"Expert mode config should be valid (errors: {errors})"
            )
            
            # Test that values beyond safe limits are accepted in expert mode
            self.assert_true(
                config.cores[0].max_mv == -80,
                "Expert mode should allow -80mV"
            )
            
            # Start dynamic mode
            logger.info("Starting dynamic mode with expert mode...")
            success = await self.controller.start(config)
            self.assert_true(success, "Expert mode should start successfully")
            
            # Wait for status
            await asyncio.sleep(2.0)
            
            # Get status
            status = await self.controller.get_status()
            
            # Check that values can be beyond safe limits
            # (depending on load, they might not reach -80, but should be possible)
            logger.info(f"Expert mode values: {status.values}")
            
            # Stop
            await self.controller.stop()
            
            # Test that non-expert mode rejects these values
            config.expert_mode = False
            errors = config.validate()
            self.assert_true(
                len(errors) > 0,
                "Non-expert mode should reject values beyond safe limits"
            )
            
            logger.info("✓ Test 3 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 3 failed with exception: {e}")
            self.failed += 1
    
    async def test_simple_mode_propagation(self):
        """Test 4: Simple mode value propagation."""
        logger.info("\n=== Test 4: Simple Mode Value Propagation ===")
        self.tests_run += 1
        
        try:
            # Create config with simple mode
            config = DynamicConfig(
                strategy="balanced",
                sample_interval_ms=100,
                simple_mode=True,
                simple_value=-25,
            )
            
            # Test that get_effective_core_values returns same value for all cores
            effective_values = config.get_effective_core_values()
            self.assert_equal(
                len(effective_values), 4,
                "Should have 4 effective values"
            )
            self.assert_true(
                all(v == -25 for v in effective_values),
                f"All values should be -25 in simple mode (got {effective_values})"
            )
            
            # Test switching from per-core to simple mode
            per_core_config = DynamicConfig(
                strategy="balanced",
                simple_mode=False,
                cores=[
                    CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                    CoreConfig(min_mv=-22, max_mv=-32, threshold=50.0),
                    CoreConfig(min_mv=-18, max_mv=-28, threshold=50.0),
                    CoreConfig(min_mv=-20, max_mv=-30, threshold=50.0),
                ],
            )
            
            # Calculate average
            avg = per_core_config.calculate_simple_value_from_cores()
            expected_avg = round((-30 + -32 + -28 + -30) / 4)
            self.assert_equal(
                avg, expected_avg,
                f"Average should be {expected_avg}"
            )
            
            # Test switching from simple to per-core mode
            simple_config = DynamicConfig(
                strategy="balanced",
                simple_mode=True,
                simple_value=-27,
            )
            simple_config.apply_simple_value_to_cores()
            
            # Check all cores have the simple value
            for i, core in enumerate(simple_config.cores):
                self.assert_equal(
                    core.min_mv, -27,
                    f"Core {i} min_mv should be -27"
                )
                self.assert_equal(
                    core.max_mv, -27,
                    f"Core {i} max_mv should be -27"
                )
            
            # Start with simple mode
            logger.info("Starting dynamic mode with simple mode...")
            success = await self.controller.start(config)
            self.assert_true(success, "Simple mode should start successfully")
            
            await asyncio.sleep(2.0)
            
            # Get status
            status = await self.controller.get_status()
            logger.info(f"Simple mode values: {status.values}")
            
            # Stop
            await self.controller.stop()
            
            logger.info("✓ Test 4 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 4 failed with exception: {e}")
            self.failed += 1
    
    def test_migration_from_old_format(self):
        """Test 5: Migration from old settings format."""
        logger.info("\n=== Test 5: Migration from Old Settings Format ===")
        self.tests_run += 1
        
        try:
            # Create old format settings
            old_settings = {
                "strategy": "DEFAULT",
                "sample_interval": 50000,  # microseconds
                "cores": [
                    {
                        "maximumValue": 100,  # 100% = -35mV
                        "minimumValue": 50,   # 50% = -17.5mV
                        "threshold": 50,
                        "manualPoints": []
                    },
                    {
                        "maximumValue": 100,
                        "minimumValue": 50,
                        "threshold": 50,
                        "manualPoints": []
                    },
                    {
                        "maximumValue": 100,
                        "minimumValue": 50,
                        "threshold": 50,
                        "manualPoints": []
                    },
                    {
                        "maximumValue": 100,
                        "minimumValue": 50,
                        "threshold": 50,
                        "manualPoints": []
                    },
                ]
            }
            
            # Check that it's detected as old format
            self.assert_true(
                is_old_format(old_settings),
                "Should detect old format"
            )
            
            # Migrate
            new_config = migrate_dynamic_settings(old_settings)
            
            # Check strategy mapping
            self.assert_equal(
                new_config.strategy, "balanced",
                "DEFAULT should map to balanced"
            )
            
            # Check sample interval conversion
            self.assert_equal(
                new_config.sample_interval_ms, 50,
                "50000us should convert to 50ms"
            )
            
            # Check value conversion
            # 100% -> -35mV, 50% -> -17mV (rounded)
            for i, core in enumerate(new_config.cores):
                self.assert_true(
                    core.max_mv == -35,
                    f"Core {i} max_mv should be -35 (got {core.max_mv})"
                )
                self.assert_true(
                    -18 <= core.min_mv <= -17,
                    f"Core {i} min_mv should be ~-17 (got {core.min_mv})"
                )
            
            # Test AGGRESSIVE strategy mapping
            old_settings["strategy"] = "AGGRESSIVE"
            new_config = migrate_dynamic_settings(old_settings)
            self.assert_equal(
                new_config.strategy, "aggressive",
                "AGGRESSIVE should map to aggressive"
            )
            
            # Test MANUAL strategy mapping with custom curve
            old_settings["strategy"] = "MANUAL"
            old_settings["cores"][0]["manualPoints"] = [
                {"load": 0, "value": 100},
                {"load": 100, "value": 0}
            ]
            new_config = migrate_dynamic_settings(old_settings)
            self.assert_equal(
                new_config.strategy, "custom",
                "MANUAL should map to custom"
            )
            self.assert_true(
                new_config.cores[0].custom_curve is not None,
                "Custom curve should be migrated"
            )
            
            # Check custom curve conversion
            curve = new_config.cores[0].custom_curve
            self.assert_equal(
                len(curve), 2,
                "Custom curve should have 2 points"
            )
            # (0, 100%) -> (0.0, -35mV)
            # (100, 0%) -> (100.0, 0mV)
            self.assert_equal(curve[0], (0.0, -35), "First point should be (0.0, -35)")
            self.assert_equal(curve[1], (100.0, 0), "Second point should be (100.0, 0)")
            
            logger.info("✓ Test 5 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 5 failed with exception: {e}")
            self.failed += 1
    
    def test_profile_management(self):
        """Test 6: Profile management."""
        logger.info("\n=== Test 6: Profile Management ===")
        self.tests_run += 1
        
        try:
            # Create profile manager (no storage for testing)
            manager = ProfileManager(storage_path=None)
            
            # Check default profiles exist
            profiles = manager.list_profiles()
            self.assert_true(
                "Battery Saver" in profiles,
                "Battery Saver profile should exist"
            )
            self.assert_true(
                "Balanced" in profiles,
                "Balanced profile should exist"
            )
            self.assert_true(
                "Performance" in profiles,
                "Performance profile should exist"
            )
            self.assert_true(
                "Silent" in profiles,
                "Silent profile should exist"
            )
            
            # Get a profile
            balanced = manager.get_profile("Balanced")
            self.assert_true(
                balanced is not None,
                "Should get Balanced profile"
            )
            self.assert_equal(
                balanced.config.strategy, "balanced",
                "Balanced profile should use balanced strategy"
            )
            
            # Create custom profile
            custom_profile = DynamicProfile(
                name="Test Profile",
                description="Test profile for integration testing",
                config=DynamicConfig(strategy="aggressive"),
            )
            success = manager.create_profile(custom_profile)
            self.assert_true(success, "Should create custom profile")
            
            # Verify it exists
            test_profile = manager.get_profile("Test Profile")
            self.assert_true(
                test_profile is not None,
                "Should retrieve created profile"
            )
            
            # Duplicate profile
            duplicate = manager.duplicate_profile("Test Profile", "Test Profile Copy")
            self.assert_true(
                duplicate is not None,
                "Should duplicate profile"
            )
            
            # Export profile
            json_str = manager.export_profile("Test Profile")
            self.assert_true(
                json_str is not None,
                "Should export profile"
            )
            self.assert_true(
                "Test Profile" in json_str,
                "Exported JSON should contain profile name"
            )
            
            # Delete profile
            success = manager.delete_profile("Test Profile Copy")
            self.assert_true(success, "Should delete profile")
            
            logger.info("✓ Test 6 completed")
            
        except Exception as e:
            logger.error(f"✗ Test 6 failed with exception: {e}")
            self.failed += 1
    
    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("=" * 60)
        logger.info("Starting Manual Integration Tests")
        logger.info("=" * 60)
        
        # Check prerequisites
        if not self.gymdeck3_path.exists():
            logger.error(f"gymdeck3 binary not found at {self.gymdeck3_path}")
            logger.error("Please build gymdeck3 first: cd gymdeck3 && cargo build --release")
            return False
        
        logger.info(f"Using gymdeck3: {self.gymdeck3_path}")
        logger.info(f"Using ryzenadj: {self.ryzenadj_path}")
        
        # Run tests
        await self.test_dynamic_mode_start_stop()
        await self.test_load_monitoring_and_adaptation()
        await self.test_expert_mode_extended_range()
        await self.test_simple_mode_propagation()
        self.test_migration_from_old_format()
        self.test_profile_management()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Tests run: {self.tests_run}")
        logger.info(f"Assertions passed: {self.passed}")
        logger.info(f"Assertions failed: {self.failed}")
        
        if self.failed == 0:
            logger.info("\n✓ ALL TESTS PASSED!")
            return True
        else:
            logger.error(f"\n✗ {self.failed} ASSERTIONS FAILED")
            return False


async def main():
    """Main entry point."""
    runner = IntegrationTestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
