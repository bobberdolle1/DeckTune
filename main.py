"""DeckTune - Automated undervolting and tuning for Steam Deck.

This is the main plugin entry point that serves as a thin RPC wrapper,
delegating to the modular backend components.

Feature: decktune
Validates: Integration, Requirements 10.1, 10.3, 10.4
"""

import asyncio
import json
import os

import decky  # type: ignore
from settings import SettingsManager  # type: ignore

from backend.core.ryzenadj import RyzenadjWrapper
from backend.core.safety import SafetyManager
from backend.platform.detect import detect_platform
from backend.tuning.autotune import AutotuneEngine
from backend.tuning.runner import TestRunner
from backend.api.events import EventEmitter
from backend.api.rpc import DeckTuneRPC
from backend.watchdog import Watchdog

# Environment paths
SETTINGS_DIR = os.environ.get("DECKY_PLUGIN_SETTINGS_DIR")
PLUGIN_DIR = os.environ.get("DECKY_PLUGIN_DIR")

# Initialize settings manager
settings = SettingsManager(name="settings", settings_directory=SETTINGS_DIR)

# Binary paths
GYMDECK2_CLI_PATH = "./bin/gymdeck2"
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
        self.gymdeck_instance = None
        
        # Core components (initialized in init())
        self.platform = None
        self.ryzenadj = None
        self.safety = None
        self.event_emitter = None
        self.test_runner = None
        self.autotune_engine = None
        self.watchdog = None
        self.rpc = None

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
        self.ryzenadj = RyzenadjWrapper(
            RYZENADJ_CLI_PATH, 
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
        
        # 7. Initialize RPC handler
        self.rpc = DeckTuneRPC(
            platform=self.platform,
            ryzenadj=self.ryzenadj,
            safety=self.safety,
            event_emitter=self.event_emitter,
            settings_manager=settings,
            autotune_engine=self.autotune_engine,
            test_runner=self.test_runner
        )
        
        # 8. Check for boot recovery (Requirement: Integration)
        if self.safety.check_boot_recovery():
            decky.logger.info("Boot recovery triggered - rolling back to LKG values")
            # Safety manager already handles the rollback in check_boot_recovery()
        
        decky.logger.info("DeckTune plugin initialized")

    # ==================== Undervolt Control (delegated to RPC) ====================
    
    async def disable_undervolt(self):
        """Disable undervolt - reset all cores to 0."""
        decky.logger.info("Disabling undervolt")
        self._cancel_task()
        
        # Stop dynamic mode if running
        if self.gymdeck_instance:
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
        
        # Stop dynamic mode if running
        if self.gymdeck_instance:
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
        
        # Stop dynamic mode if running
        if self.gymdeck_instance:
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

    # ==================== Autotune (delegated to RPC) ====================
    
    async def start_autotune(self, mode="quick"):
        """Start autotune process."""
        # Stop dynamic mode if running
        if self.gymdeck_instance:
            await self.stop_gymdeck()
        
        return await self.rpc.start_autotune(mode)
    
    async def stop_autotune(self):
        """Stop running autotune."""
        return await self.rpc.stop_autotune()

    # ==================== Tests (delegated to RPC) ====================
    
    async def run_test(self, test_name):
        """Run a specific stress test."""
        return await self.rpc.run_test(test_name)
    
    async def get_test_history(self):
        """Get last 10 test results."""
        return await self.rpc.get_test_history()

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

    # ==================== Dynamic Mode (Gymdeck) ====================
    # Requirements: 10.1, 10.3, 10.4

    async def start_gymdeck(self, dynamic_settings):
        """Start gymdeck2 dynamic mode.
        
        Requirements: 10.1, 10.3
        """
        await self.stop_gymdeck()

        decky.logger.info("Starting Gymdeck in dynamic run mode...")

        # Update status to DYNAMIC RUNNING (Requirement 10.3)
        settings.setSetting("status", "DYNAMIC RUNNING")
        settings.setSetting("dynamicSettings", dynamic_settings)

        await decky.emit("server_event", {
            "type": "update_status",
            "data": "dynamic_running"
        })

        # Map strategy names (Requirement 10.1)
        strategy_map = {
            "MANUAL": "manual",
            "AGGRESSIVE": "aggressive",
            "DEFAULT": "default"
        }
        strategy = strategy_map.get(dynamic_settings.get("strategy", "DEFAULT"), "default")
        sample_interval = str(dynamic_settings.get("sampleInterval", 50000))

        # Build core arguments (Requirement 10.4)
        cores = dynamic_settings.get("cores", [])
        core_args = []
        for c in cores:
            core_args.append(str(c.get("maximumValue", 35)))
            core_args.append(str(c.get("minimumValue", 25)))
            core_args.append(str(c.get("threshold", 40.0)))

        manual_points_args = []
        for c in cores:
            manual_points_json = json.dumps(c.get("manualPoints", []))
            manual_points_args.append(manual_points_json)

        args = [
            "sudo",
            GYMDECK2_CLI_PATH,
            strategy,
            sample_interval,
            *core_args,
            *manual_points_args
        ]

        decky.logger.info(f"Gymdeck will be launched with arguments: {args}")

        try:
            self.gymdeck_instance = await asyncio.create_subprocess_exec(
                *args,
                cwd=PLUGIN_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=False,
            )
        except Exception as e:
            decky.logger.error(f"Failed to start Gymdeck: {e}")
            settings.setSetting("status", "Disabled")
            await decky.emit("server_event", {"type": "update_status", "data": "disabled"})
            return {"success": False, "error": str(e)}

        self.gymdeck_monitor_task = asyncio.create_task(self._monitor_gymdeck_output())
        return {"success": True, "status": "DYNAMIC RUNNING"}

    async def stop_gymdeck(self):
        """Stop gymdeck2 dynamic mode.
        
        Requirements: 10.3, 10.4
        """
        if self.gymdeck_monitor_task:
            self.gymdeck_monitor_task.cancel()
            self.gymdeck_monitor_task = None

        if self.gymdeck_instance and self.gymdeck_instance.returncode is None:
            decky.logger.info("Terminating Gymdeck process...")
            self.gymdeck_instance.terminate()
            try:
                await asyncio.wait_for(self.gymdeck_instance.wait(), timeout=5)
            except asyncio.TimeoutError:
                decky.logger.warning("Gymdeck did not exit in time; killing...")
                self.gymdeck_instance.kill()

        self.gymdeck_instance = None

        # Update status to Disabled (Requirement 10.3)
        settings.setSetting("status", "Disabled")
        await decky.emit("server_event", {"type": "update_status", "data": "disabled"})
        return {"success": True, "status": "Disabled"}

    async def _monitor_gymdeck_output(self):
        """Monitor gymdeck output and log periodically."""
        decky.logger.info("Monitoring Gymdeck output...")
        line_count = 0

        try:
            while True:
                if self.gymdeck_instance.stdout and not self.gymdeck_instance.stdout.at_eof():
                    line_count += 1
                    line = await self.gymdeck_instance.stdout.readline()
                    if line and line_count % 25 == 0:
                        decky.logger.info(f"GYMDECK: {line.rstrip()}")
                        line_count = 0

        except asyncio.CancelledError:
            decky.logger.info("Gymdeck monitoring task was cancelled.")
            raise

        finally:
            decky.logger.info("Gymdeck process ended or was terminated.")
            # Update status to Disabled when process ends (Requirement 10.3)
            settings.setSetting("status", "Disabled")
            await decky.emit("server_event", {"type": "update_status", "data": "disabled"})
            self.gymdeck_instance = None
            self.gymdeck_monitor_task = None
    
    def is_dynamic_running(self):
        """Check if dynamic mode is currently running.
        
        Returns:
            True if gymdeck2 process is active
        """
        return (
            self.gymdeck_instance is not None and 
            self.gymdeck_instance.returncode is None
        )
    
    async def get_dynamic_status(self):
        """Get current dynamic mode status.
        
        Returns:
            Dictionary with running status and current settings
            
        Requirements: 10.3
        """
        is_running = self.is_dynamic_running()
        current_status = settings.getSetting("status") or "Disabled"
        
        return {
            "running": is_running,
            "status": "DYNAMIC RUNNING" if is_running else current_status,
            "settings": settings.getSetting("dynamicSettings") or {}
        }
