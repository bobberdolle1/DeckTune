"""DeckTune - Automated undervolting and tuning for Steam Deck.

This is the main plugin entry point that serves as a thin RPC wrapper,
delegating to the modular backend components.

Feature: decktune
Validates: Integration, Requirements 10.1, 10.3, 10.4, 10.7, 11.3, 13.1-13.5
"""

import asyncio
import json
import os
import sys

# Add plugin directory to Python path for module imports
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import decky  # type: ignore
from settings import SettingsManager  # type: ignore

from backend.core.ryzenadj import RyzenadjWrapper
from backend.core.safety import SafetyManager
from backend.platform.detect import detect_platform
from backend.tuning.autotune import AutotuneEngine
from backend.tuning.runner import TestRunner
from backend.tuning.binning import BinningEngine
from backend.tuning.benchmark import BenchmarkRunner
from backend.api.events import EventEmitter
from backend.api.rpc import DeckTuneRPC
from backend.watchdog import Watchdog
from backend.dynamic.controller import DynamicController
from backend.dynamic.config import DynamicConfig, CoreConfig
from backend.dynamic.migration import migrate_dynamic_settings, is_old_format
from backend.dynamic.profile_manager import ProfileManager
from backend.platform.appwatcher import AppWatcher

# Environment paths
SETTINGS_DIR = os.environ.get("DECKY_PLUGIN_SETTINGS_DIR")
PLUGIN_DIR = os.environ.get("DECKY_PLUGIN_DIR")

# Initialize settings manager
settings = SettingsManager(name="settings", settings_directory=SETTINGS_DIR)

# Binary paths
GYMDECK3_CLI_PATH = "./bin/gymdeck3"
RYZENADJ_CLI_PATH = "./bin/ryzenadj"

# Default settings
DEFAULT_SETTINGS = {
    "presets": [],
    "cores": [5, 5, 5, 5],
    "status": "Disabled",
    "lkg_cores": [0, 0, 0, 0],
    "lkg_timestamp": None,
    "settings": {
        "isGlobal": False,
        "runAtStartup": False,
        "isRunAutomatically": True,
        "timeoutApply": 15
    },
    "dynamicSettings": {
        "cores": [
            {"manualPoints": [], "maximumValue": 100, "minimumValue": 0, "threshold": 0},
            {"manualPoints": [], "maximumValue": 100, "minimumValue": 0, "threshold": 0},
            {"manualPoints": [], "maximumValue": 100, "minimumValue": 0, "threshold": 0},
            {"manualPoints": [], "maximumValue": 100, "minimumValue": 0, "threshold": 0},
        ],
        "strategy": "DEFAULT",
        "sampleInterval": 50000,
    },
    "expert_mode": False,  # Expert Overclocker Mode (Requirements 13.1-13.5)
    "expert_mode_confirmed": False,  # User has confirmed risks
    "simple_mode": False,  # Simple Mode toggle (Requirements 14.1, 14.2)
    "test_history": [],
}


class Plugin:
    """Main DeckTune plugin class - RPC router.
    
    This class serves as a thin wrapper that initializes all backend modules
    and routes RPC calls to the appropriate components.
    """
    
    def __init__(self):
        # Dynamic mode state
        self.gymdeck_monitor_task = None
        self.delay_task = None
        self.gymdeck_instance = None  # Legacy, kept for compatibility check
        
        # Core components (initialized in init())
        self.platform = None
        self.ryzenadj = None
        self.safety = None
        self.event_emitter = None
        self.test_runner = None
        self.autotune_engine = None
        self.binning_engine = None
        self.benchmark_runner = None
        self.watchdog = None
        self.rpc = None
        self.dynamic_controller = None  # New gymdeck3 controller
        self.profile_manager = None  # Per-game profile manager
        self.app_watcher = None  # Steam app watcher

    async def init(self):
        """Initialize plugin and all modules."""
        decky.logger.info("Initializing DeckTune plugin...")
        
        # Initialize default settings
        for key in DEFAULT_SETTINGS:
            if key == "dynamicSettings":
                dynamic = settings.getSetting(key)
                if dynamic:
                    for subkey in DEFAULT_SETTINGS[key]:
                        if dynamic.get(subkey) is None:
                            decky.logger.info(f"Setting {subkey} to default value")
                            settings.setSetting(subkey, DEFAULT_SETTINGS[key][subkey])
            if settings.getSetting(key) is None:
                decky.logger.info(f"Setting {key} to default value")
                settings.setSetting(key, DEFAULT_SETTINGS[key])
        
        # 1. Detect platform
        self.platform = detect_platform()
        decky.logger.info(f"Detected platform: {self.platform.model} ({self.platform.variant})")
        
        # 2. Initialize event emitter with decky.emit
        self.event_emitter = EventEmitter(decky.emit)
        
        # 3. Initialize core modules
        ryzenadj_binary_path = os.path.join(PLUGIN_DIR, RYZENADJ_CLI_PATH) if PLUGIN_DIR else RYZENADJ_CLI_PATH
        self.ryzenadj = RyzenadjWrapper(
            ryzenadj_binary_path, 
            PLUGIN_DIR, 
            event_emitter=self.event_emitter
        )
        
        self.safety = SafetyManager(settings, self.platform, ryzenadj=self.ryzenadj)
        
        # 4. Initialize test runner
        self.test_runner = TestRunner()
        
        # 5. Initialize autotune engine
        self.autotune_engine = AutotuneEngine(
            ryzenadj=self.ryzenadj,
            runner=self.test_runner,
            safety=self.safety,
            event_emitter=self.event_emitter
        )
        
        # 6. Initialize watchdog
        self.watchdog = Watchdog(self.safety)
        
        # 7. Initialize binning engine
        from backend.tuning.binning import BinningEngine
        self.binning_engine = BinningEngine(
            ryzenadj=self.ryzenadj,
            runner=self.test_runner,
            safety=self.safety,
            event_emitter=self.event_emitter
        )
        
        # 7.5. Initialize benchmark runner
        from backend.tuning.benchmark import BenchmarkRunner
        self.benchmark_runner = BenchmarkRunner(
            test_runner=self.test_runner
        )
        
        # 8. Initialize RPC handler
        self.rpc = DeckTuneRPC(
            platform=self.platform,
            ryzenadj=self.ryzenadj,
            safety=self.safety,
            event_emitter=self.event_emitter,
            settings_manager=settings,
            autotune_engine=self.autotune_engine,
            test_runner=self.test_runner,
            binning_engine=self.binning_engine,
            benchmark_runner=self.benchmark_runner
        )
        
        # 9. Initialize DynamicController for gymdeck3
        gymdeck3_path = os.path.join(PLUGIN_DIR, GYMDECK3_CLI_PATH) if PLUGIN_DIR else GYMDECK3_CLI_PATH
        ryzenadj_path = os.path.join(PLUGIN_DIR, RYZENADJ_CLI_PATH) if PLUGIN_DIR else RYZENADJ_CLI_PATH
        
        self.dynamic_controller = DynamicController(
            ryzenadj_path=ryzenadj_path,
            gymdeck3_path=gymdeck3_path,
            event_emitter=self.event_emitter,
            safety_manager=self.safety,
        )
        
        # 10. Initialize ProfileManager for per-game profiles
        self.profile_manager = ProfileManager(
            settings_manager=settings,
            ryzenadj=self.ryzenadj,
            dynamic_controller=self.dynamic_controller,
            event_emitter=self.event_emitter
        )
        
        # Set profile manager in RPC
        self.rpc.set_profile_manager(self.profile_manager)
        
        # 11. Initialize AppWatcher for automatic profile switching
        self.app_watcher = AppWatcher(
            profile_manager=self.profile_manager,
            poll_interval=2.0
        )
        
        # Set app watcher in RPC
        self.rpc.set_app_watcher(self.app_watcher)
        
        # Start AppWatcher
        await self.app_watcher.start()
        decky.logger.info("AppWatcher started for automatic profile switching")
        
        # 12. Check for boot recovery (Requirement: Integration)
        if self.safety.check_boot_recovery():
            decky.logger.info("Boot recovery triggered - rolling back to LKG values")
            # Safety manager already handles the rollback in check_boot_recovery()
            
            # Emit Iron Seeker recovery event if applicable (Requirements: 3.4)
            iron_seeker_recovery = self.safety.get_iron_seeker_recovery_info()
            if iron_seeker_recovery is not None:
                decky.logger.info(
                    f"Iron Seeker crash recovery: core {iron_seeker_recovery['crashed_core']}, "
                    f"value {iron_seeker_recovery['crashed_value']}mV"
                )
                await self.events.emit_iron_seeker_recovery(
                    crashed_core=iron_seeker_recovery['crashed_core'],
                    crashed_value=iron_seeker_recovery['crashed_value'],
                    restored_values=iron_seeker_recovery['restored_values']
                )
        
        decky.logger.info("DeckTune plugin initialized")

    # ==================== Undervolt Control (delegated to RPC) ====================
    
    async def disable_undervolt(self):
        """Disable undervolt - reset all cores to 0."""
        decky.logger.info("Disabling undervolt")
        self._cancel_task()
        
        # Stop dynamic mode if running (using new controller)
        if self.dynamic_controller and self.dynamic_controller.is_running():
            await self.stop_gymdeck()
        
        result = await self.rpc.disable_undervolt()
        return result

    async def apply_undervolt(self, core_values, timeout):
        """Apply undervolt values with optional delay.
        
        Args:
            core_values: List of positive values (will be negated)
            timeout: Delay in seconds before applying (0 for immediate)
        """
        decky.logger.info(f"Applying undervolt with values: {core_values} and timeout: {timeout}")
        
        # Stop dynamic mode if running (using new controller)
        if self.dynamic_controller and self.dynamic_controller.is_running():
            await self.stop_gymdeck()

        if timeout is not None and timeout > 0:
            await decky.emit("server_event", {"type": "update_status", "data": "scheduled"})
            self.delay_task = asyncio.create_task(asyncio.sleep(timeout))
            try:
                await self.delay_task
            except asyncio.CancelledError:
                decky.logger.info("Delay task was cancelled")
                return

        # Delegate to RPC handler (with timeout=0 since we already waited)
        result = await self.rpc.apply_undervolt(core_values, timeout=0)
        return result

    async def panic_disable(self):
        """Emergency disable - immediate reset to 0."""
        decky.logger.info("PANIC DISABLE triggered")
        self._cancel_task()
        
        # Stop dynamic mode if running (using new controller)
        if self.dynamic_controller and self.dynamic_controller.is_running():
            await self.stop_gymdeck()
        
        result = await self.rpc.panic_disable()
        return result

    def _cancel_task(self):
        """Cancel any pending delay task."""
        if self.delay_task:
            self.delay_task.cancel()
            self.delay_task = None

    # ==================== Platform Info (delegated to RPC) ====================
    
    async def get_platform_info(self):
        """Return platform detection results."""
        return await self.rpc.get_platform_info()
    
    async def redetect_platform(self):
        """Force fresh platform detection, clearing any cached data.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 3.4
        """
        return await self.rpc.redetect_platform()

    # ==================== Autotune (delegated to RPC) ====================
    
    async def start_autotune(self, mode="quick"):
        """Start autotune process."""
        # Stop dynamic mode if running (using new controller)
        if self.dynamic_controller and self.dynamic_controller.is_running():
            await self.stop_gymdeck()
        
        return await self.rpc.start_autotune(mode)
    
    async def stop_autotune(self):
        """Stop running autotune."""
        return await self.rpc.stop_autotune()

    # ==================== Silicon Binning ====================
    # Requirements: 8.1, 8.2, 8.3, 8.4, 10.1, 10.2, 10.3, 10.4, 10.5
    
    async def start_binning(self, config):
        """Start silicon binning process."""
        return await self.rpc.start_binning(config)
    
    async def stop_binning(self):
        """Stop running binning session."""
        return await self.rpc.stop_binning()
    
    async def get_binning_status(self):
        """Get current binning status."""
        return await self.rpc.get_binning_status()
    
    async def get_binning_config(self):
        """Get current binning configuration."""
        return await self.rpc.get_binning_config()
    
    async def update_binning_config(self, config):
        """Update binning configuration."""
        return await self.rpc.update_binning_config(config)

    # ==================== Tests (delegated to RPC) ====================
    
    async def check_binaries(self):
        """Check availability of stress test binaries (stress-ng, memtester)."""
        return await self.rpc.check_binaries()
    
    async def run_test(self, test_name):
        """Run a specific stress test."""
        return await self.rpc.run_test(test_name)
    
    async def get_test_history(self):
        """Get last 10 test results."""
        return await self.rpc.get_test_history()
    
    # ==================== Benchmark ====================
    # Requirements: 7.1, 7.4, 7.5
    
    async def run_benchmark(self):
        """Run 10-second performance benchmark."""
        return await self.rpc.run_benchmark()
    
    async def get_benchmark_history(self):
        """Get last 20 benchmark results with comparisons."""
        return await self.rpc.get_benchmark_history()

    # ==================== Preset Management (delegated to RPC) ====================

    async def save_preset(self, preset):
        """Save or update a preset."""
        return await self.rpc.save_preset(preset)

    async def update_preset(self, preset):
        """Update an existing preset."""
        # For backwards compatibility, delegate to save_preset
        return await self.rpc.save_preset(preset)

    async def delete_preset(self, app_id):
        """Delete a preset by app_id."""
        return await self.rpc.delete_preset(app_id)
    
    async def get_presets(self):
        """Get all presets."""
        return await self.rpc.get_presets()
    
    async def export_presets(self):
        """Export all presets as JSON."""
        return await self.rpc.export_presets()
    
    async def import_presets(self, json_data):
        """Import presets from JSON."""
        return await self.rpc.import_presets(json_data)

    # ==================== Profile Management (Per-Game Profiles) ====================
    # Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3, 5.4
    
    async def create_profile(self, profile_data):
        """Create a new game profile."""
        return await self.rpc.create_profile(profile_data)
    
    async def get_profiles(self):
        """Get all game profiles."""
        return await self.rpc.get_profiles()
    
    async def update_profile(self, app_id, updates):
        """Update an existing game profile."""
        return await self.rpc.update_profile(app_id, updates)
    
    async def delete_profile(self, app_id):
        """Delete a game profile."""
        return await self.rpc.delete_profile(app_id)
    
    async def create_profile_for_current_game(self):
        """Create a profile for the currently running game."""
        return await self.rpc.create_profile_for_current_game()
    
    async def export_profiles(self):
        """Export all profiles to JSON file."""
        return await self.rpc.export_profiles()
    
    async def import_profiles(self, json_data, strategy="skip"):
        """Import profiles from JSON."""
        return await self.rpc.import_profiles(json_data, strategy)

    # ==================== Diagnostics (delegated to RPC) ====================
    
    async def export_diagnostics(self):
        """Export diagnostics archive."""
        return await self.rpc.export_diagnostics()
    
    async def get_system_info(self):
        """Get system info for diagnostics tab."""
        return await self.rpc.get_system_info()

    # ==================== Settings Management ====================

    async def save_settings(self, new_settings):
        """Save settings object."""
        decky.logger.info(f"Saving settings: {new_settings}")
        settings.setSetting("settings", new_settings)

    async def save_setting(self, key, value):
        """Save a single setting."""
        decky.logger.info(f"Saving setting: {key} with value: {value}")
        settings.setSetting(key, value)

    async def get_setting(self, key):
        """Get a single setting."""
        decky.logger.info(f"Getting setting: {key}")
        return settings.getSetting(key)

    async def reset_config(self):
        """Reset all settings to defaults."""
        decky.logger.info("Resetting config")
        for key in DEFAULT_SETTINGS:
            settings.setSetting(key, DEFAULT_SETTINGS[key])
        return DEFAULT_SETTINGS

    async def fetch_config(self):
        """Fetch all configuration."""
        decky.logger.info("Fetching config")
        config = {}
        for key in DEFAULT_SETTINGS:
            config[key] = settings.getSetting(key)
        decky.logger.info(f"Config fetched: {config}")
        return config

    # ==================== Dynamic Mode (Gymdeck3) ====================
    # Requirements: 10.1-10.7, 11.3

    async def start_gymdeck(self, dynamic_settings):
        """Start gymdeck3 dynamic mode.
        
        Supports both old and new settings formats.
        Automatically migrates old format settings.
        
        Requirements: 10.1, 10.3, 10.7, 11.3
        """
        # Stop any existing dynamic mode
        await self.stop_gymdeck()

        decky.logger.info("Starting Gymdeck3 in dynamic run mode...")

        # Check if settings are in old format and migrate if needed
        if is_old_format(dynamic_settings):
            decky.logger.info("Migrating old dynamic settings format to new format")
            config = migrate_dynamic_settings(dynamic_settings)
        else:
            # Already in new format or create from dict
            config = DynamicConfig.from_dict(dynamic_settings) if isinstance(dynamic_settings, dict) else dynamic_settings
        
        # Apply expert mode setting from global settings
        expert_mode = settings.getSetting("expert_mode") or False
        expert_confirmed = settings.getSetting("expert_mode_confirmed") or False
        config.expert_mode = expert_mode and expert_confirmed

        # Validate configuration
        errors = config.validate()
        if errors:
            decky.logger.error(f"Invalid dynamic config: {errors}")
            await decky.emit("server_event", {"type": "update_status", "data": "error"})
            return {"success": False, "error": f"Invalid configuration: {errors}"}

        # Update status to DYNAMIC RUNNING (Requirement 10.3)
        settings.setSetting("status", "DYNAMIC RUNNING")
        settings.setSetting("dynamicSettings", dynamic_settings)  # Store original format for compatibility

        # Start using new DynamicController
        success = await self.dynamic_controller.start(config)
        
        if success:
            decky.logger.info(f"Gymdeck3 started with strategy: {config.strategy}")
            return {"success": True, "status": "DYNAMIC RUNNING"}
        else:
            settings.setSetting("status", "Disabled")
            await decky.emit("server_event", {"type": "update_status", "data": "disabled"})
            return {"success": False, "error": "Failed to start gymdeck3"}

    async def stop_gymdeck(self):
        """Stop gymdeck3 dynamic mode.
        
        Requirements: 10.3, 10.4
        """
        if self.dynamic_controller and self.dynamic_controller.is_running():
            decky.logger.info("Stopping Gymdeck3 process...")
            await self.dynamic_controller.stop()

        # Update status to Disabled (Requirement 10.3)
        settings.setSetting("status", "Disabled")
        await decky.emit("server_event", {"type": "update_status", "data": "disabled"})
        return {"success": True, "status": "Disabled"}
    
    def is_dynamic_running(self):
        """Check if dynamic mode is currently running.
        
        Returns:
            True if gymdeck3 process is active
        """
        return (
            self.dynamic_controller is not None and 
            self.dynamic_controller.is_running()
        )
    
    async def get_dynamic_status(self):
        """Get current dynamic mode status.
        
        Returns:
            Dictionary with running status and current settings
            
        Requirements: 10.3
        """
        is_running = self.is_dynamic_running()
        current_status = settings.getSetting("status") or "Disabled"
        
        # Get detailed status from controller if running
        if is_running and self.dynamic_controller:
            status = await self.dynamic_controller.get_status()
            return {
                "running": status.running,
                "status": "DYNAMIC RUNNING" if status.running else current_status,
                "settings": settings.getSetting("dynamicSettings") or {},
                "load": status.load,
                "values": status.values,
                "strategy": status.strategy,
                "uptime_ms": status.uptime_ms,
                "error": status.error,
            }
        
        return {
            "running": is_running,
            "status": "DYNAMIC RUNNING" if is_running else current_status,
            "settings": settings.getSetting("dynamicSettings") or {}
        }

    # ==================== Expert Mode ====================
    # Requirements: 13.1-13.5

    async def enable_expert_mode(self, confirmed: bool = False):
        """Enable Expert Overclocker Mode.
        
        Expert mode removes platform safety limits, allowing undervolt
        values from 0 to -100mV. Requires explicit user confirmation.
        
        Args:
            confirmed: User has explicitly confirmed understanding of risks
            
        Returns:
            Dictionary with success status and current expert mode state
            
        Requirements: 13.1-13.5
        """
        if not confirmed:
            decky.logger.warning("Expert mode enable attempted without confirmation")
            return {
                "success": False,
                "error": "Expert mode requires explicit confirmation of risks",
                "expert_mode": False,
                "confirmed": False
            }
        
        decky.logger.warning("EXPERT MODE ENABLED - Safety limits removed")
        decky.logger.warning("User has confirmed understanding of risks (instability, crashes, potential hardware damage)")
        
        settings.setSetting("expert_mode", True)
        settings.setSetting("expert_mode_confirmed", True)
        
        # Emit event to frontend for visual indicator
        await decky.emit("server_event", {
            "type": "expert_mode_changed",
            "data": {"enabled": True}
        })
        
        return {
            "success": True,
            "expert_mode": True,
            "confirmed": True,
            "message": "Expert mode enabled. Extended undervolt range (-100mV) now available."
        }

    async def disable_expert_mode(self):
        """Disable Expert Overclocker Mode.
        
        Returns to safe platform limits. Does not reset current values,
        but they will be clamped on next apply.
        
        Returns:
            Dictionary with success status
            
        Requirements: 13.1-13.5
        """
        decky.logger.info("Expert mode disabled - returning to safe limits")
        
        settings.setSetting("expert_mode", False)
        # Keep confirmed flag so user doesn't need to re-confirm if they re-enable
        # But after plugin update, this will be reset via DEFAULT_SETTINGS
        
        # Emit event to frontend
        await decky.emit("server_event", {
            "type": "expert_mode_changed",
            "data": {"enabled": False}
        })
        
        return {
            "success": True,
            "expert_mode": False,
            "message": "Expert mode disabled. Safe platform limits restored."
        }

    async def get_expert_mode_status(self):
        """Get current Expert Mode status.
        
        Returns:
            Dictionary with expert mode state and limits
            
        Requirements: 13.1-13.5
        """
        expert_mode = settings.getSetting("expert_mode") or False
        expert_confirmed = settings.getSetting("expert_mode_confirmed") or False
        
        # Determine current limits based on mode
        if expert_mode and expert_confirmed:
            min_limit = -100  # Expert mode allows deeper undervolt
        else:
            min_limit = self.platform.safe_limit if self.platform else -35
        
        return {
            "expert_mode": expert_mode,
            "confirmed": expert_confirmed,
            "active": expert_mode and expert_confirmed,
            "min_limit": min_limit,
            "max_limit": 0,
            "platform_safe_limit": self.platform.safe_limit if self.platform else -35
        }

    async def apply_expert_undervolt(self, core_values, timeout=0):
        """Apply undervolt values with expert mode validation.
        
        If expert mode is active, allows values up to -100mV.
        Otherwise, clamps to platform safe limits.
        Logs all expert mode value changes for diagnostics.
        
        Args:
            core_values: List of undervolt values (negative or will be negated)
            timeout: Delay in seconds before applying
            
        Returns:
            Dictionary with success status and applied values
            
        Requirements: 13.2, 13.7
        """
        expert_mode = settings.getSetting("expert_mode") or False
        expert_confirmed = settings.getSetting("expert_mode_confirmed") or False
        is_expert_active = expert_mode and expert_confirmed
        
        # Convert to negative values if positive
        negated_cores = [-abs(v) if v > 0 else v for v in core_values]
        
        # Determine limits
        if is_expert_active:
            min_limit = -100
            decky.logger.warning(f"EXPERT MODE: Applying values {negated_cores} (extended range)")
        else:
            min_limit = self.platform.safe_limit if self.platform else -35
        
        # Clamp values to current limits
        clamped_cores = [max(min_limit, min(0, v)) for v in negated_cores]
        
        # Log if values were clamped
        if clamped_cores != negated_cores:
            decky.logger.info(f"Values clamped from {negated_cores} to {clamped_cores}")
        
        # Log expert mode changes for diagnostics (Requirement 13.7)
        if is_expert_active:
            decky.logger.warning(f"EXPERT MODE VALUE CHANGE: {clamped_cores}")
        
        # Delegate to standard apply
        return await self.apply_undervolt(clamped_cores, timeout)

    # ==================== Fan Control ====================
    # Requirements: Fan Control Integration (Phase 4)
    
    async def get_fan_config(self):
        """Get current fan control configuration."""
        return await self.rpc.get_fan_config()
    
    async def set_fan_config(self, config):
        """Update fan control configuration."""
        return await self.rpc.set_fan_config(config)
    
    async def set_fan_curve(self, points):
        """Set custom fan curve points."""
        return await self.rpc.set_fan_curve(points)
    
    async def set_fan_mode(self, mode):
        """Set fan control mode (default, custom, fixed)."""
        return await self.rpc.set_fan_mode(mode)
    
    async def enable_fan_control(self, enabled):
        """Enable or disable fan control."""
        return await self.rpc.enable_fan_control(enabled)

    # ==================== Crash Metrics (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 1.2
    
    async def get_crash_metrics(self):
        """Get crash recovery metrics.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 1.2
        """
        return await self.rpc.get_crash_metrics()
    
    # ==================== Telemetry (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 2.3, 2.4
    
    async def get_telemetry(self, seconds=60):
        """Get recent telemetry samples.
        
        Args:
            seconds: Number of seconds of data to retrieve (default 60)
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 2.3, 2.4
        """
        return await self.rpc.get_telemetry(seconds)
    
    # ==================== Session History (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 8.4, 8.5, 8.6
    
    async def get_session_history(self, limit=30):
        """Get session history.
        
        Args:
            limit: Maximum number of sessions to return (default 30)
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.4
        """
        return await self.rpc.get_session_history(limit)
    
    async def get_session(self, session_id):
        """Get a specific session by ID.
        
        Args:
            session_id: UUID of the session to retrieve
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.5
        """
        return await self.rpc.get_session(session_id)
    
    async def compare_sessions(self, id1, id2):
        """Compare two sessions.
        
        Args:
            id1: UUID of first session
            id2: UUID of second session
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.6
        """
        return await self.rpc.compare_sessions(id1, id2)
    
    # ==================== Wizard (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 5.5, 5.6
    
    async def get_wizard_state(self):
        """Get wizard settings state.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.5, 5.6
        """
        return await self.rpc.get_wizard_state()
    
    async def complete_wizard(self, goal):
        """Complete the setup wizard with selected goal.
        
        Args:
            goal: Selected goal - one of: quiet, balanced, battery, performance
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.5
        """
        return await self.rpc.complete_wizard(goal)
    
    async def reset_wizard(self):
        """Reset wizard state to allow re-running.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.6
        """
        return await self.rpc.reset_wizard()

    # ==================== Plugin Lifecycle ====================
    
    async def _unload(self):
        """Clean up resources when plugin is unloaded.
        
        Stops AppWatcher and any other background tasks.
        
        Requirements: 4.6
        """
        decky.logger.info("Unloading DeckTune plugin...")
        
        # Stop AppWatcher
        if self.app_watcher and self.app_watcher.is_running():
            await self.app_watcher.stop()
            decky.logger.info("AppWatcher stopped")
        
        # Stop dynamic controller if running
        if self.dynamic_controller and self.dynamic_controller.is_running():
            await self.dynamic_controller.stop()
            decky.logger.info("DynamicController stopped")
        
        decky.logger.info("DeckTune plugin unloaded")
