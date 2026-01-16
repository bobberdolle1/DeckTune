"""RPC handlers for Decky frontend communication.

Feature: decktune, API and Events Module
Validates: All RPC endpoints

This module provides the RPC interface for frontend communication,
including platform info, undervolt control, autotune, tests, presets,
and diagnostics methods.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..core.safety import SafetyManager
    from ..platform.detect import PlatformInfo
    from ..tuning.autotune import AutotuneEngine, AutotuneConfig
    from ..tuning.runner import TestRunner
    from ..tuning.binning import BinningEngine
    from ..tuning.benchmark import BenchmarkRunner
    from ..dynamic.profile_manager import ProfileManager
    from ..platform.appwatcher import AppWatcher
    from .events import EventEmitter

logger = logging.getLogger(__name__)


class DeckTuneRPC:
    """RPC methods for frontend communication.
    
    Provides all RPC endpoints for the DeckTune plugin:
    - Platform info methods
    - Undervolt control methods (apply, disable, panic)
    - Autotune methods (start, stop)
    - Test methods (run, history)
    
    Note: Preset management and diagnostics methods are implemented
    in subtasks 10.3 and 10.4 respectively.
    """
    
    def __init__(
        self,
        platform: "PlatformInfo",
        ryzenadj: "RyzenadjWrapper",
        safety: "SafetyManager",
        event_emitter: "EventEmitter",
        settings_manager,
        autotune_engine: Optional["AutotuneEngine"] = None,
        test_runner: Optional["TestRunner"] = None,
        binning_engine: Optional["BinningEngine"] = None,
        profile_manager: Optional["ProfileManager"] = None,
        app_watcher: Optional["AppWatcher"] = None,
        benchmark_runner: Optional["BenchmarkRunner"] = None
    ):
        """Initialize the RPC handler.
        
        Args:
            platform: Detected platform information
            ryzenadj: RyzenadjWrapper for applying undervolt values
            safety: SafetyManager for LKG and safety operations
            event_emitter: EventEmitter for status updates
            settings_manager: Decky settings manager instance
            autotune_engine: Optional AutotuneEngine for autotune operations
            test_runner: Optional TestRunner for stress tests
            binning_engine: Optional BinningEngine for silicon binning
            profile_manager: Optional ProfileManager for per-game profiles
            app_watcher: Optional AppWatcher for detecting active games
            benchmark_runner: Optional BenchmarkRunner for performance benchmarking
        """
        self.platform = platform
        self.ryzenadj = ryzenadj
        self.safety = safety
        self.event_emitter = event_emitter
        self.settings = settings_manager
        self.autotune_engine = autotune_engine
        self.test_runner = test_runner
        self.binning_engine = binning_engine
        self.profile_manager = profile_manager
        self.app_watcher = app_watcher
        self.benchmark_runner = benchmark_runner
        
        self._delay_task: Optional[asyncio.Task] = None
        self._autotune_task: Optional[asyncio.Task] = None
        self._binning_task: Optional[asyncio.Task] = None
        self._benchmark_task: Optional[asyncio.Task] = None
    
    def set_autotune_engine(self, engine: "AutotuneEngine") -> None:
        """Set the autotune engine.
        
        Args:
            engine: AutotuneEngine instance
        """
        self.autotune_engine = engine
    
    def set_test_runner(self, runner: "TestRunner") -> None:
        """Set the test runner.
        
        Args:
            runner: TestRunner instance
        """
        self.test_runner = runner
    
    def set_binning_engine(self, engine: "BinningEngine") -> None:
        """Set the binning engine.
        
        Args:
            engine: BinningEngine instance
        """
        self.binning_engine = engine
    
    def set_profile_manager(self, manager: "ProfileManager") -> None:
        """Set the profile manager.
        
        Args:
            manager: ProfileManager instance
        """
        self.profile_manager = manager
    
    def set_app_watcher(self, watcher: "AppWatcher") -> None:
        """Set the app watcher.
        
        Args:
            watcher: AppWatcher instance
        """
        self.app_watcher = watcher
    
    def set_benchmark_runner(self, runner: "BenchmarkRunner") -> None:
        """Set the benchmark runner.
        
        Args:
            runner: BenchmarkRunner instance
        """
        self.benchmark_runner = runner
    
    # ==================== Platform Info ====================
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """Return platform detection results.
        
        Returns:
            Dictionary with model, variant, safe_limit, and detected status
        """
        return {
            "model": self.platform.model,
            "variant": self.platform.variant,
            "safe_limit": self.platform.safe_limit,
            "detected": self.platform.detected
        }
    
    # ==================== Undervolt Control ====================
    
    async def apply_undervolt(
        self,
        cores: List[int],
        timeout: int = 0
    ) -> Dict[str, Any]:
        """Apply undervolt values with optional delay.
        
        Args:
            cores: List of 4 undervolt values (positive values will be negated)
            timeout: Delay in seconds before applying (0 for immediate)
            
        Returns:
            Dictionary with success status and any error message
        """
        logger.info(f"Applying undervolt with values: {cores}, timeout: {timeout}")
        
        # Cancel any pending delay task
        self._cancel_delay_task()
        
        if timeout > 0:
            await self.event_emitter.emit_status("scheduled")
            self._delay_task = asyncio.create_task(asyncio.sleep(timeout))
            try:
                await self._delay_task
            except asyncio.CancelledError:
                logger.info("Delay task was cancelled")
                return {"success": False, "error": "Cancelled"}
        
        # Convert to negative values if positive and clamp to safe limits
        negated_cores = [-abs(v) if v > 0 else v for v in cores]
        clamped_cores = self.safety.clamp_values(negated_cores)
        
        success, error = await self.ryzenadj.apply_values_async(clamped_cores)
        
        if success:
            self.settings.setSetting("cores", clamped_cores)
            self.settings.setSetting("status", "enabled")
            await self.event_emitter.emit_status("enabled")
            logger.info(f"Undervolt applied: {clamped_cores}")
            return {"success": True, "cores": clamped_cores}
        else:
            await self.event_emitter.emit_status("error")
            logger.error(f"Failed to apply undervolt: {error}")
            return {"success": False, "error": error}
    
    async def disable_undervolt(self) -> Dict[str, Any]:
        """Reset all cores to 0 (no undervolt).
        
        Returns:
            Dictionary with success status and any error message
        """
        logger.info("Disabling undervolt")
        self._cancel_delay_task()
        
        success, error = await self.ryzenadj.disable_async()
        
        if success:
            self.settings.setSetting("status", "disabled")
            await self.event_emitter.emit_status("disabled")
            return {"success": True}
        else:
            await self.event_emitter.emit_status("error")
            return {"success": False, "error": error}
    
    async def panic_disable(self) -> Dict[str, Any]:
        """Emergency disable - immediate reset to 0.
        
        Cancels any pending operations and immediately resets all cores.
        
        Returns:
            Dictionary with success status
        """
        logger.warning("PANIC DISABLE triggered")
        
        # Cancel all pending tasks
        self._cancel_delay_task()
        self._cancel_autotune()
        
        success, error = self.ryzenadj.disable()
        
        self.settings.setSetting("status", "disabled")
        await self.event_emitter.emit_status("disabled")
        
        if success:
            return {"success": True}
        else:
            logger.error(f"Panic disable failed: {error}")
            return {"success": False, "error": error}
    
    def _cancel_delay_task(self) -> None:
        """Cancel any pending delay task."""
        if self._delay_task and not self._delay_task.done():
            self._delay_task.cancel()
            self._delay_task = None
    
    def _cancel_autotune(self) -> None:
        """Cancel running autotune."""
        if self.autotune_engine and self.autotune_engine.is_running():
            self.autotune_engine.cancel()
        if self._autotune_task and not self._autotune_task.done():
            self._autotune_task.cancel()
            self._autotune_task = None
    
    # ==================== Autotune ====================
    
    async def start_autotune(self, mode: str = "quick") -> Dict[str, Any]:
        """Start autotune process.
        
        Args:
            mode: "quick" or "thorough"
            
        Returns:
            Dictionary with success status or error if already running
        """
        if self.autotune_engine is None:
            return {"success": False, "error": "Autotune engine not configured"}
        
        if self.autotune_engine.is_running():
            return {"success": False, "error": "Autotune already running"}
        
        logger.info(f"Starting autotune in {mode} mode")
        
        # Import here to avoid circular imports
        from ..tuning.autotune import AutotuneConfig
        
        config = AutotuneConfig(mode=mode)
        
        # Run autotune in background task
        self._autotune_task = asyncio.create_task(
            self._run_autotune(config)
        )
        
        return {"success": True, "mode": mode}
    
    async def _run_autotune(self, config: "AutotuneConfig") -> None:
        """Run autotune and handle completion.
        
        Args:
            config: Autotune configuration
        """
        try:
            result = await self.autotune_engine.run(config)
            
            if result.stable:
                self.settings.setSetting("cores", result.cores)
                self.settings.setSetting("status", "enabled")
            else:
                self.settings.setSetting("status", "disabled")
                
        except asyncio.CancelledError:
            logger.info("Autotune task cancelled")
            self.settings.setSetting("status", "disabled")
            await self.event_emitter.emit_status("disabled")
        except Exception as e:
            logger.exception(f"Autotune error: {e}")
            self.settings.setSetting("status", "error")
            await self.event_emitter.emit_status("error")
    
    async def stop_autotune(self) -> Dict[str, Any]:
        """Cancel running autotune.
        
        Returns:
            Dictionary with success status
        """
        if self.autotune_engine is None:
            return {"success": False, "error": "Autotune engine not configured"}
        
        if not self.autotune_engine.is_running():
            return {"success": False, "error": "Autotune not running"}
        
        logger.info("Stopping autotune")
        self._cancel_autotune()
        
        return {"success": True}
    
    # ==================== Silicon Binning ====================
    
    async def start_binning(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start silicon binning process.
        
        Args:
            config: Dictionary with optional keys:
                   - test_duration: Test duration in seconds (30-300)
                   - step_size: Step size in mV (1-10)
                   - start_value: Starting value in mV (-20 to 0)
                   
        Returns:
            Dictionary with success status or error if already running
            
        Requirements: 8.1, 10.1
        """
        if self.binning_engine is None:
            return {"success": False, "error": "Binning engine not configured"}
        
        if self.binning_engine.is_running():
            return {"success": False, "error": "Binning already running"}
        
        # Import here to avoid circular imports
        from ..tuning.binning import BinningConfig
        
        # Validate and extract config parameters
        try:
            test_duration = config.get("test_duration", 60)
            step_size = config.get("step_size", 5)
            start_value = config.get("start_value", -10)
            
            # Validate ranges
            if not (30 <= test_duration <= 300):
                return {"success": False, "error": f"test_duration must be between 30 and 300, got {test_duration}"}
            
            if not (1 <= step_size <= 10):
                return {"success": False, "error": f"step_size must be between 1 and 10, got {step_size}"}
            
            if not (-20 <= start_value <= 0):
                return {"success": False, "error": f"start_value must be between -20 and 0, got {start_value}"}
            
            # Create BinningConfig
            binning_config = BinningConfig(
                start_value=start_value,
                step_size=step_size,
                test_duration=test_duration,
                max_iterations=config.get("max_iterations", 20),
                consecutive_fail_limit=config.get("consecutive_fail_limit", 3)
            )
            
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid binning config: {e}")
            return {"success": False, "error": f"Invalid config: {e}"}
        
        logger.info(f"Starting binning with config: {binning_config}")
        
        # Run binning in background task
        self._binning_task = asyncio.create_task(
            self._run_binning(binning_config)
        )
        
        return {"success": True, "config": {
            "test_duration": test_duration,
            "step_size": step_size,
            "start_value": start_value
        }}
    
    async def _run_binning(self, config: "BinningConfig") -> None:
        """Run binning and handle completion.
        
        Args:
            config: BinningConfig instance
        """
        try:
            result = await self.binning_engine.start(config)
            
            # Emit completion event
            await self.event_emitter.emit_binning_complete(result)
            
            logger.info(f"Binning completed: max_stable={result.max_stable}, "
                       f"recommended={result.recommended}")
                
        except asyncio.CancelledError:
            logger.info("Binning task cancelled")
            await self.event_emitter.emit_status("disabled")
        except Exception as e:
            logger.exception(f"Binning error: {e}")
            await self.event_emitter.emit_binning_error(str(e))
    
    async def stop_binning(self) -> Dict[str, Any]:
        """Cancel running binning session.
        
        Returns:
            Dictionary with success status
        """
        if self.binning_engine is None:
            return {"success": False, "error": "Binning engine not configured"}
        
        if not self.binning_engine.is_running():
            return {"success": False, "error": "Binning not running"}
        
        logger.info("Stopping binning")
        self.binning_engine.cancel()
        
        if self._binning_task and not self._binning_task.done():
            self._binning_task.cancel()
            self._binning_task = None
        
        return {"success": True}
    
    async def get_binning_status(self) -> Dict[str, Any]:
        """Get current binning status.
        
        Returns:
            Dictionary with running status and current state if active
        """
        if self.binning_engine is None:
            return {"success": False, "error": "Binning engine not configured"}
        
        is_running = self.binning_engine.is_running()
        
        result = {
            "success": True,
            "running": is_running
        }
        
        # If running, include current state from safety manager
        if is_running:
            state = self.safety.load_binning_state()
            if state:
                result["current_value"] = state.get("current_value")
                result["last_stable"] = state.get("last_stable")
                result["iteration"] = state.get("iteration")
        
        return result
    
    async def get_binning_config(self) -> Dict[str, Any]:
        """Get current binning configuration.
        
        Returns:
            Dictionary with binning config settings
            
        Requirements: 10.1, 10.5
        """
        config = self.settings.getSetting("binning_config") or {
            "test_duration": 60,
            "step_size": 5,
            "start_value": -10,
            "max_iterations": 20,
            "consecutive_fail_limit": 3
        }
        
        return {"success": True, "config": config}
    
    async def update_binning_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update binning configuration.
        
        Args:
            config: Dictionary with config keys to update:
                   - test_duration: Test duration in seconds (30-300)
                   - step_size: Step size in mV (1-10)
                   - start_value: Starting value in mV (-20 to 0)
                   
        Returns:
            Dictionary with success status and updated config
            
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
        """
        # Get current config
        current_config = self.settings.getSetting("binning_config") or {
            "test_duration": 60,
            "step_size": 5,
            "start_value": -10,
            "max_iterations": 20,
            "consecutive_fail_limit": 3
        }
        
        # Validate and update each field
        if "test_duration" in config:
            test_duration = config["test_duration"]
            if not (30 <= test_duration <= 300):
                return {"success": False, "error": f"test_duration must be between 30 and 300, got {test_duration}"}
            current_config["test_duration"] = test_duration
        
        if "step_size" in config:
            step_size = config["step_size"]
            if not (1 <= step_size <= 10):
                return {"success": False, "error": f"step_size must be between 1 and 10, got {step_size}"}
            current_config["step_size"] = step_size
        
        if "start_value" in config:
            start_value = config["start_value"]
            if not (-20 <= start_value <= 0):
                return {"success": False, "error": f"start_value must be between -20 and 0, got {start_value}"}
            current_config["start_value"] = start_value
        
        if "max_iterations" in config:
            current_config["max_iterations"] = config["max_iterations"]
        
        if "consecutive_fail_limit" in config:
            current_config["consecutive_fail_limit"] = config["consecutive_fail_limit"]
        
        # Persist config
        self.settings.setSetting("binning_config", current_config)
        
        logger.info(f"Updated binning config: {current_config}")
        return {"success": True, "config": current_config}
    
    # ==================== Profile Management ====================
    # Requirements: 3.1, 3.2, 3.3, 3.4
    
    async def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new game profile.
        
        Args:
            profile_data: Dictionary with profile fields:
                - app_id: Steam AppID (required)
                - name: Game name (required)
                - cores: Undervolt values [core0, core1, core2, core3] (required)
                - dynamic_enabled: Whether dynamic mode is enabled (optional, default False)
                - dynamic_config: Dynamic mode configuration (optional)
                
        Returns:
            Dictionary with success status and created profile
            
        Requirements: 3.1
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            # Extract required fields
            app_id = profile_data.get("app_id")
            name = profile_data.get("name")
            cores = profile_data.get("cores")
            
            # Validate required fields
            if app_id is None:
                return {"success": False, "error": "app_id is required"}
            if not name:
                return {"success": False, "error": "name is required"}
            if not cores:
                return {"success": False, "error": "cores is required"}
            
            # Extract optional fields
            dynamic_enabled = profile_data.get("dynamic_enabled", False)
            dynamic_config = profile_data.get("dynamic_config")
            
            # Create profile
            profile = await self.profile_manager.create_profile(
                app_id=app_id,
                name=name,
                cores=cores,
                dynamic_enabled=dynamic_enabled,
                dynamic_config=dynamic_config
            )
            
            if profile:
                logger.info(f"Created profile for '{name}' (app_id: {app_id})")
                return {
                    "success": True,
                    "profile": profile.to_dict()
                }
            else:
                return {"success": False, "error": "Failed to create profile (may already exist or invalid data)"}
                
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_profiles(self) -> Dict[str, Any]:
        """Get all game profiles.
        
        Returns:
            Dictionary with success status and list of profiles
            
        Requirements: 3.2
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            profiles = self.profile_manager.get_all_profiles()
            profiles_list = [profile.to_dict() for profile in profiles]
            
            return {
                "success": True,
                "profiles": profiles_list,
                "count": len(profiles_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to get profiles: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_profile(self, app_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing game profile.
        
        Args:
            app_id: Steam AppID of profile to update
            updates: Dictionary with fields to update (name, cores, dynamic_enabled, dynamic_config)
            
        Returns:
            Dictionary with success status
            
        Requirements: 3.3
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            success = await self.profile_manager.update_profile(app_id, **updates)
            
            if success:
                logger.info(f"Updated profile for app_id: {app_id}")
                return {"success": True}
            else:
                return {"success": False, "error": f"Profile with app_id {app_id} not found"}
                
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_profile(self, app_id: int) -> Dict[str, Any]:
        """Delete a game profile.
        
        Args:
            app_id: Steam AppID of profile to delete
            
        Returns:
            Dictionary with success status
            
        Requirements: 3.4
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            success = await self.profile_manager.delete_profile(app_id)
            
            if success:
                logger.info(f"Deleted profile for app_id: {app_id}")
                return {"success": True}
            else:
                return {"success": False, "error": f"Profile with app_id {app_id} not found"}
                
        except Exception as e:
            logger.error(f"Failed to delete profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_profile_for_current_game(self) -> Dict[str, Any]:
        """Create a profile for the currently running game.
        
        Detects the current AppID from AppWatcher, auto-populates the app_id
        and game name, and captures current undervolt and dynamic settings.
        
        Returns:
            Dictionary with success status and created profile, or error if no game is running
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        if not self.app_watcher:
            return {"success": False, "error": "AppWatcher not initialized"}
        
        try:
            # Get current AppID from AppWatcher
            current_app_id = self.app_watcher.get_current_app_id()
            
            if current_app_id is None:
                logger.info("No game is currently running")
                return {
                    "success": False,
                    "error": "No game is currently running. Launch a game first, then try again."
                }
            
            # Check if profile already exists
            existing_profile = self.profile_manager.get_profile(current_app_id)
            if existing_profile:
                return {
                    "success": False,
                    "error": f"Profile for app_id {current_app_id} already exists. Use update instead."
                }
            
            # Try to get game name from Steam (simplified - just use AppID for now)
            # In a full implementation, we could parse appmanifest files for the game name
            game_name = f"Game {current_app_id}"
            
            # Try to get a better name from appmanifest
            try:
                from pathlib import Path
                import re
                
                steamapps_dir = Path.home() / ".steam" / "steam" / "steamapps"
                manifest_file = steamapps_dir / f"appmanifest_{current_app_id}.acf"
                
                if manifest_file.exists():
                    with open(manifest_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Look for "name" field
                    name_match = re.search(r'"name"\s+"([^"]+)"', content)
                    if name_match:
                        game_name = name_match.group(1)
                        logger.info(f"Found game name from appmanifest: {game_name}")
            except Exception as e:
                logger.debug(f"Could not get game name from appmanifest: {e}")
            
            # Create profile from current settings
            profile = await self.profile_manager.create_from_current(
                app_id=current_app_id,
                name=game_name
            )
            
            if profile:
                logger.info(f"Created profile for current game '{game_name}' (app_id: {current_app_id})")
                return {
                    "success": True,
                    "profile": profile.to_dict(),
                    "message": f"Profile created for {game_name}"
                }
            else:
                return {"success": False, "error": "Failed to create profile from current settings"}
                
        except Exception as e:
            logger.error(f"Failed to create profile for current game: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== Profile Import/Export ====================
    
    async def export_profiles(self) -> Dict[str, Any]:
        """Export all profiles to JSON file in home directory.
        
        Returns:
            Dictionary with success status and file path
            
        Requirements: 9.5
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            # Export profiles as JSON string
            json_data = self.profile_manager.export_profiles()
            
            # Save to home directory
            home_dir = Path.home()
            export_path = home_dir / "decktune_profiles_export.json"
            
            with open(export_path, 'w') as f:
                f.write(json_data)
            
            logger.info(f"Exported profiles to {export_path}")
            return {
                "success": True,
                "file_path": str(export_path),
                "profile_count": len(self.profile_manager.get_all_profiles())
            }
            
        except Exception as e:
            logger.error(f"Failed to export profiles: {e}")
            return {"success": False, "error": str(e)}
    
    async def import_profiles(
        self,
        json_data: str,
        strategy: str = "skip"
    ) -> Dict[str, Any]:
        """Import profiles from JSON data.
        
        Args:
            json_data: JSON string containing profiles to import
            strategy: Merge strategy - "skip", "overwrite", or "rename"
            
        Returns:
            Dictionary with import results
            
        Requirements: 9.5
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            # Import profiles
            result = await self.profile_manager.import_profiles(json_data, strategy)
            
            logger.info(f"Import complete: {result['imported_count']} imported, {result['skipped_count']} skipped")
            return result
            
        except Exception as e:
            logger.error(f"Failed to import profiles: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== Tests ====================
    
    async def check_binaries(self) -> Dict[str, Any]:
        """Check availability of required stress test binaries.
        
        Returns:
            Dictionary with binary status and list of missing binaries.
            Useful for UI warnings on SteamOS where binaries must be bundled.
        """
        if self.test_runner is None:
            return {"success": False, "error": "Test runner not configured"}
        
        status = self.test_runner.check_binaries()
        missing = self.test_runner.get_missing_binaries()
        
        return {
            "success": True,
            "binaries": status,
            "missing": missing,
            "all_available": len(missing) == 0
        }
    
    async def run_test(self, test_name: str) -> Dict[str, Any]:
        """Run a specific stress test.
        
        Args:
            test_name: Name of test from TestRunner.TESTS
            
        Returns:
            Dictionary with test result
        """
        if self.test_runner is None:
            return {"success": False, "error": "Test runner not configured"}
        
        logger.info(f"Running test: {test_name}")
        
        result = await self.test_runner.run_test(test_name)
        
        # Add to test history
        self._add_to_test_history(test_name, result)
        
        # Emit completion event
        await self.event_emitter.emit_test_complete(result)
        
        return {
            "success": True,
            "passed": result.passed,
            "duration": result.duration,
            "logs": result.logs,
            "error": result.error
        }
    
    def _add_to_test_history(self, test_name: str, result) -> None:
        """Add test result to history, keeping last 10.
        
        Args:
            test_name: Name of the test
            result: TestResult object
        """
        from datetime import datetime
        
        history = self.settings.getSetting("test_history") or []
        
        entry = {
            "test_name": test_name,
            "passed": result.passed,
            "duration": result.duration,
            "timestamp": datetime.now().isoformat(),
            "cores_tested": self.settings.getSetting("cores") or [0, 0, 0, 0]
        }
        
        history.append(entry)
        
        # Keep only last 10 entries
        if len(history) > 10:
            history = history[-10:]
        
        self.settings.setSetting("test_history", history)
    
    async def get_test_history(self) -> List[Dict[str, Any]]:
        """Get last 10 test results.
        
        Returns:
            List of test history entries
        """
        return self.settings.getSetting("test_history") or []
    
    # ==================== Preset Management ====================
    # Requirements: 5.1, 5.5
    
    async def save_preset(self, preset: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update a preset.
        
        Args:
            preset: Dictionary with app_id, label, value, timeout, use_timeout
            
        Returns:
            Dictionary with success status
            
        Requirements: 5.1
        """
        logger.info(f"Saving preset: {preset}")
        
        presets = self.settings.getSetting("presets") or []
        
        # Remove existing preset with same app_id
        app_id = preset.get("app_id")
        presets = [p for p in presets if p.get("app_id") != app_id]
        
        # Create new preset entry
        from datetime import datetime
        new_preset = {
            "app_id": app_id,
            "label": preset.get("label", ""),
            "value": preset.get("value", [0, 0, 0, 0]),
            "timeout": preset.get("timeout", 0),
            "use_timeout": preset.get("use_timeout", False),
            "created_at": datetime.now().isoformat(),
            "tested": preset.get("tested", False)
        }
        
        presets.append(new_preset)
        self.settings.setSetting("presets", presets)
        
        logger.info(f"Preset saved: {new_preset}")
        return {"success": True, "preset": new_preset}
    
    async def delete_preset(self, app_id: int) -> Dict[str, Any]:
        """Delete a preset by app_id.
        
        Args:
            app_id: Application ID of the preset to delete
            
        Returns:
            Dictionary with success status
        """
        logger.info(f"Deleting preset with app_id: {app_id}")
        
        presets = self.settings.getSetting("presets") or []
        original_count = len(presets)
        
        presets = [p for p in presets if p.get("app_id") != app_id]
        
        if len(presets) == original_count:
            return {"success": False, "error": f"Preset with app_id {app_id} not found"}
        
        self.settings.setSetting("presets", presets)
        return {"success": True}
    
    async def get_presets(self) -> List[Dict[str, Any]]:
        """Get all presets.
        
        Returns:
            List of preset dictionaries
        """
        return self.settings.getSetting("presets") or []
    
    async def export_presets(self) -> str:
        """Export all presets as JSON string.
        
        Returns:
            JSON string containing all presets
            
        Requirements: 5.5
        """
        import json
        
        presets = self.settings.getSetting("presets") or []
        
        export_data = {
            "version": "1.0",
            "presets": presets
        }
        
        return json.dumps(export_data, indent=2)
    
    async def import_presets(self, json_data: str) -> Dict[str, Any]:
        """Import presets from JSON string.
        
        Args:
            json_data: JSON string containing presets
            
        Returns:
            Dictionary with success status and count of imported presets
            
        Requirements: 5.5
        """
        import json
        
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse preset JSON: {e}")
            return {"success": False, "error": f"Invalid JSON: {e}"}
        
        # Handle both formats: {"presets": [...]} and [...]
        if isinstance(data, dict):
            imported_presets = data.get("presets", [])
        elif isinstance(data, list):
            imported_presets = data
        else:
            return {"success": False, "error": "Invalid preset format"}
        
        if not isinstance(imported_presets, list):
            return {"success": False, "error": "Presets must be a list"}
        
        # Validate and merge presets
        existing_presets = self.settings.getSetting("presets") or []
        existing_app_ids = {p.get("app_id") for p in existing_presets}
        
        imported_count = 0
        for preset in imported_presets:
            if not isinstance(preset, dict):
                continue
            
            app_id = preset.get("app_id")
            if app_id is None:
                continue
            
            # Skip if already exists (don't overwrite)
            if app_id in existing_app_ids:
                continue
            
            # Validate required fields
            if "value" not in preset or not isinstance(preset["value"], list):
                continue
            
            # Add preset with defaults for missing fields
            from datetime import datetime
            new_preset = {
                "app_id": app_id,
                "label": preset.get("label", ""),
                "value": preset["value"],
                "timeout": preset.get("timeout", 0),
                "use_timeout": preset.get("use_timeout", False),
                "created_at": preset.get("created_at", datetime.now().isoformat()),
                "tested": preset.get("tested", False)
            }
            
            existing_presets.append(new_preset)
            existing_app_ids.add(app_id)
            imported_count += 1
        
        self.settings.setSetting("presets", existing_presets)
        
        logger.info(f"Imported {imported_count} presets")
        return {"success": True, "imported_count": imported_count}

    
    # ==================== Diagnostics ====================
    # Requirements: 8.1, 8.2
    
    async def export_diagnostics(self) -> Dict[str, Any]:
        """Create diagnostics archive and return path.
        
        Creates a tar.gz archive containing:
        - Last 200 lines of plugin logs
        - Current config and LKG values
        - System info (uname, SteamOS version, device type)
        - Last 100 lines of dmesg
        
        Returns:
            Dictionary with success status and archive path
            
        Requirements: 8.1
        """
        import os
        import tarfile
        import tempfile
        import subprocess
        import json
        from datetime import datetime
        
        logger.info("Exporting diagnostics")
        
        # Create temp directory for files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"decktune_diagnostics_{timestamp}.tar.gz"
        
        # Use home directory for output (user-accessible)
        home_dir = os.path.expanduser("~")
        archive_path = os.path.join(home_dir, archive_name)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 1. Plugin logs (last 200 lines)
                logs_path = os.path.join(temp_dir, "plugin_logs.txt")
                await self._write_plugin_logs(logs_path, 200)
                
                # 2. Config and LKG values
                config_path = os.path.join(temp_dir, "config.json")
                await self._write_config(config_path)
                
                # 3. System info
                sysinfo_path = os.path.join(temp_dir, "system_info.txt")
                await self._write_system_info(sysinfo_path)
                
                # 4. dmesg (last 100 lines)
                dmesg_path = os.path.join(temp_dir, "dmesg.txt")
                await self._write_dmesg(dmesg_path, 100)
                
                # Create tar.gz archive
                with tarfile.open(archive_path, "w:gz") as tar:
                    for filename in ["plugin_logs.txt", "config.json", 
                                    "system_info.txt", "dmesg.txt"]:
                        filepath = os.path.join(temp_dir, filename)
                        if os.path.exists(filepath):
                            tar.add(filepath, arcname=filename)
            
            logger.info(f"Diagnostics exported to: {archive_path}")
            return {"success": True, "path": archive_path}
            
        except Exception as e:
            logger.exception(f"Failed to export diagnostics: {e}")
            return {"success": False, "error": str(e)}
    
    async def _write_plugin_logs(self, path: str, lines: int) -> None:
        """Write plugin logs to file.
        
        Args:
            path: Output file path
            lines: Number of lines to include
        """
        import os
        
        # Try to find plugin log file
        log_paths = [
            os.path.expanduser("~/.local/share/decky/logs/decktune.log"),
            "/tmp/decktune.log",
        ]
        
        log_content = ""
        for log_path in log_paths:
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        all_lines = f.readlines()
                        log_content = "".join(all_lines[-lines:])
                    break
                except Exception:
                    continue
        
        if not log_content:
            log_content = "No plugin logs found"
        
        with open(path, 'w') as f:
            f.write(log_content)
    
    async def _write_config(self, path: str) -> None:
        """Write current config to JSON file.
        
        Args:
            path: Output file path
        """
        import json
        
        config = {
            "cores": self.settings.getSetting("cores") or [0, 0, 0, 0],
            "lkg_cores": self.settings.getSetting("lkg_cores") or [0, 0, 0, 0],
            "lkg_timestamp": self.settings.getSetting("lkg_timestamp"),
            "status": self.settings.getSetting("status") or "disabled",
            "presets_count": len(self.settings.getSetting("presets") or []),
            "platform": {
                "model": self.platform.model,
                "variant": self.platform.variant,
                "safe_limit": self.platform.safe_limit,
                "detected": self.platform.detected
            }
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    async def _write_system_info(self, path: str) -> None:
        """Write system info to file.
        
        Args:
            path: Output file path
        """
        import subprocess
        import platform
        
        info_lines = []
        
        # uname
        try:
            uname_result = subprocess.run(
                ["uname", "-a"],
                capture_output=True,
                text=True,
                timeout=5
            )
            info_lines.append(f"uname: {uname_result.stdout.strip()}")
        except Exception:
            info_lines.append(f"uname: {platform.uname()}")
        
        # SteamOS version
        try:
            with open("/etc/os-release", 'r') as f:
                os_release = f.read()
            info_lines.append(f"\n/etc/os-release:\n{os_release}")
        except Exception:
            info_lines.append("SteamOS version: Unknown")
        
        # Device type
        info_lines.append(f"\nDevice: {self.platform.model} ({self.platform.variant})")
        info_lines.append(f"Safe limit: {self.platform.safe_limit}")
        info_lines.append(f"Detected: {self.platform.detected}")
        
        # Python version
        info_lines.append(f"\nPython: {platform.python_version()}")
        
        with open(path, 'w') as f:
            f.write("\n".join(info_lines))
    
    async def _write_dmesg(self, path: str, lines: int) -> None:
        """Write dmesg output to file.
        
        Args:
            path: Output file path
            lines: Number of lines to include
        """
        import subprocess
        
        dmesg_content = ""
        try:
            result = subprocess.run(
                ["dmesg"],
                capture_output=True,
                text=True,
                timeout=10
            )
            all_lines = result.stdout.splitlines()
            dmesg_content = "\n".join(all_lines[-lines:])
        except Exception as e:
            dmesg_content = f"Failed to read dmesg: {e}"
        
        with open(path, 'w') as f:
            f.write(dmesg_content)
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system info for diagnostics tab.
        
        Returns:
            Dictionary with system information
            
        Requirements: 8.2
        """
        import platform
        import subprocess
        
        info = {
            "platform": {
                "model": self.platform.model,
                "variant": self.platform.variant,
                "safe_limit": self.platform.safe_limit,
                "detected": self.platform.detected
            },
            "python_version": platform.python_version(),
            "uname": str(platform.uname()),
            "steamos_version": "Unknown"
        }
        
        # Try to get SteamOS version
        try:
            with open("/etc/os-release", 'r') as f:
                for line in f:
                    if line.startswith("VERSION_ID="):
                        info["steamos_version"] = line.split("=")[1].strip().strip('"')
                        break
        except Exception:
            pass
        
        # Get current status
        info["current_status"] = self.settings.getSetting("status") or "disabled"
        info["current_cores"] = self.settings.getSetting("cores") or [0, 0, 0, 0]
        info["lkg_cores"] = self.settings.getSetting("lkg_cores") or [0, 0, 0, 0]
        
        return info

    # ==================== Benchmark ====================
    # Requirements: 7.1, 7.4, 7.5
    
    async def run_benchmark(self) -> Dict[str, Any]:
        """Run 10-second performance benchmark.
        
        Blocks other operations during benchmark execution.
        Stores result in benchmark_history (keeps last 20).
        
        Returns:
            Dictionary with benchmark result and comparison with previous run
            
        Requirements: 7.1, 7.4, 7.5
        """
        if self.benchmark_runner is None:
            return {"success": False, "error": "Benchmark runner not configured"}
        
        # Check if benchmark or other operations are running
        if self._is_operation_running():
            return {
                "success": False,
                "error": "Another operation is running. Please wait for it to complete."
            }
        
        logger.info("Starting benchmark")
        
        # Get current undervolt values for recording
        cores_used = self.settings.getSetting("cores") or [0, 0, 0, 0]
        
        # Run benchmark in background task
        self._benchmark_task = asyncio.create_task(
            self._run_benchmark_task(cores_used)
        )
        
        try:
            result = await self._benchmark_task
            return result
        except asyncio.CancelledError:
            logger.info("Benchmark task cancelled")
            return {"success": False, "error": "Benchmark cancelled"}
        except Exception as e:
            logger.exception(f"Benchmark error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._benchmark_task = None
    
    async def _run_benchmark_task(self, cores_used: List[int]) -> Dict[str, Any]:
        """Execute benchmark and store result.
        
        Args:
            cores_used: Current undervolt values
            
        Returns:
            Dictionary with benchmark result
        """
        try:
            # Run the benchmark
            result = await self.benchmark_runner.run_benchmark(cores_used)
            
            # Store result in history
            self._add_to_benchmark_history(result)
            
            # Get comparison with previous result if available
            history = self.settings.getSetting("benchmark_history") or []
            comparison = None
            
            if len(history) >= 2:
                # Compare with previous result (second to last)
                from ..tuning.benchmark import BenchmarkResult
                
                prev_entry = history[-2]
                prev_result = BenchmarkResult(
                    score=prev_entry["score"],
                    duration=prev_entry["duration"],
                    cores_used=prev_entry["cores_used"],
                    timestamp=prev_entry["timestamp"]
                )
                
                comparison = self.benchmark_runner.compare_results(prev_result, result)
            
            logger.info(f"Benchmark completed: score={result.score:.2f} bogo ops/s")
            
            return {
                "success": True,
                "result": {
                    "score": result.score,
                    "duration": result.duration,
                    "cores_used": result.cores_used,
                    "timestamp": result.timestamp
                },
                "comparison": comparison
            }
            
        except RuntimeError as e:
            logger.error(f"Benchmark failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _add_to_benchmark_history(self, result) -> None:
        """Add benchmark result to history, keeping last 20.
        
        Args:
            result: BenchmarkResult object
        """
        history = self.settings.getSetting("benchmark_history") or []
        
        entry = {
            "score": result.score,
            "duration": result.duration,
            "cores_used": result.cores_used,
            "timestamp": result.timestamp
        }
        
        history.append(entry)
        
        # Keep only last 20 entries
        if len(history) > 20:
            history = history[-20:]
        
        self.settings.setSetting("benchmark_history", history)
    
    async def get_benchmark_history(self) -> Dict[str, Any]:
        """Get last 20 benchmark results.
        
        Includes comparison with previous result for each entry if available.
        
        Returns:
            Dictionary with success status and list of benchmark results
            
        Requirements: 7.5
        """
        history = self.settings.getSetting("benchmark_history") or []
        
        # Add comparisons to each result (except the first)
        results_with_comparison = []
        
        for i, entry in enumerate(history):
            result_dict = {
                "score": entry["score"],
                "duration": entry["duration"],
                "cores_used": entry["cores_used"],
                "timestamp": entry["timestamp"],
                "comparison": None
            }
            
            # Add comparison with previous result if available
            if i > 0 and self.benchmark_runner:
                from ..tuning.benchmark import BenchmarkResult
                
                prev_entry = history[i - 1]
                prev_result = BenchmarkResult(
                    score=prev_entry["score"],
                    duration=prev_entry["duration"],
                    cores_used=prev_entry["cores_used"],
                    timestamp=prev_entry["timestamp"]
                )
                
                current_result = BenchmarkResult(
                    score=entry["score"],
                    duration=entry["duration"],
                    cores_used=entry["cores_used"],
                    timestamp=entry["timestamp"]
                )
                
                result_dict["comparison"] = self.benchmark_runner.compare_results(
                    prev_result,
                    current_result
                )
            
            results_with_comparison.append(result_dict)
        
        return {
            "success": True,
            "history": results_with_comparison,
            "count": len(results_with_comparison)
        }
    
    def _is_operation_running(self) -> bool:
        """Check if any long-running operation is active.
        
        Returns:
            True if autotune, binning, or benchmark is running
        """
        # Check autotune
        if self.autotune_engine and self.autotune_engine.is_running():
            return True
        
        # Check binning
        if self.binning_engine and self.binning_engine.is_running():
            return True
        
        # Check benchmark task
        if self._benchmark_task and not self._benchmark_task.done():
            return True
        
        return False

    # ==================== Fan Control ====================
    # Requirements: Fan Control Integration (Phase 4)
    
    async def get_fan_config(self) -> Dict[str, Any]:
        """Get current fan control configuration.
        
        Returns:
            Dictionary with fan config settings
        """
        from ..dynamic.config import FanConfig
        
        fan_data = self.settings.getSetting("fan_config") or {}
        fan_config = FanConfig.from_dict(fan_data)
        
        return {
            "success": True,
            "config": fan_config.to_dict()
        }
    
    async def set_fan_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update fan control configuration.
        
        Args:
            config: Dictionary with fan config fields:
                - enabled: Whether fan control is enabled
                - mode: Fan control mode (default, custom, fixed)
                - curve: List of {temp_c, speed_percent} points
                - zero_rpm_enabled: Allow fan to stop completely
                - hysteresis_temp: Temperature hysteresis in °C
                
        Returns:
            Dictionary with success status and updated config
        """
        from ..dynamic.config import FanConfig, FanCurvePoint
        
        try:
            # Get current config
            current_data = self.settings.getSetting("fan_config") or {}
            current_config = FanConfig.from_dict(current_data)
            
            # Update fields
            if "enabled" in config:
                current_config.enabled = config["enabled"]
            
            if "mode" in config:
                mode = config["mode"]
                if mode not in ("default", "custom", "fixed"):
                    return {"success": False, "error": f"Invalid mode: {mode}"}
                current_config.mode = mode
            
            if "curve" in config:
                curve_data = config["curve"]
                if not isinstance(curve_data, list):
                    return {"success": False, "error": "curve must be a list"}
                current_config.curve = [FanCurvePoint.from_dict(p) for p in curve_data]
            
            if "zero_rpm_enabled" in config:
                current_config.zero_rpm_enabled = config["zero_rpm_enabled"]
            
            if "hysteresis_temp" in config:
                hysteresis = config["hysteresis_temp"]
                if not (1 <= hysteresis <= 10):
                    return {"success": False, "error": f"hysteresis_temp must be 1-10, got {hysteresis}"}
                current_config.hysteresis_temp = hysteresis
            
            # Validate
            errors = current_config.validate()
            if errors:
                return {"success": False, "error": "; ".join(errors)}
            
            # Persist
            self.settings.setSetting("fan_config", current_config.to_dict())
            
            logger.info(f"Updated fan config: enabled={current_config.enabled}, mode={current_config.mode}")
            return {"success": True, "config": current_config.to_dict()}
            
        except Exception as e:
            logger.error(f"Failed to update fan config: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_fan_curve(self, points: List[Dict[str, int]]) -> Dict[str, Any]:
        """Set custom fan curve points.
        
        Args:
            points: List of {temp_c, speed_percent} dictionaries
                   Must have at least 2 points with increasing temperatures
                   
        Returns:
            Dictionary with success status
        """
        from ..dynamic.config import FanConfig, FanCurvePoint
        
        try:
            if not isinstance(points, list) or len(points) < 2:
                return {"success": False, "error": "Fan curve requires at least 2 points"}
            
            # Parse and validate points
            curve = []
            prev_temp = -1
            
            for i, p in enumerate(points):
                temp_c = p.get("temp_c", 0)
                speed_percent = p.get("speed_percent", 0)
                
                if not (0 <= temp_c <= 100):
                    return {"success": False, "error": f"Point {i}: temp_c must be 0-100"}
                if not (0 <= speed_percent <= 100):
                    return {"success": False, "error": f"Point {i}: speed_percent must be 0-100"}
                if temp_c <= prev_temp:
                    return {"success": False, "error": f"Point {i}: temperatures must be strictly increasing"}
                
                curve.append(FanCurvePoint(temp_c=temp_c, speed_percent=speed_percent))
                prev_temp = temp_c
            
            # Update config
            current_data = self.settings.getSetting("fan_config") or {}
            current_config = FanConfig.from_dict(current_data)
            current_config.curve = curve
            current_config.mode = "custom"  # Auto-switch to custom mode
            
            # Persist
            self.settings.setSetting("fan_config", current_config.to_dict())
            
            logger.info(f"Set fan curve with {len(curve)} points")
            return {"success": True, "curve": [p.to_dict() for p in curve]}
            
        except Exception as e:
            logger.error(f"Failed to set fan curve: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_fan_mode(self, mode: str) -> Dict[str, Any]:
        """Set fan control mode.
        
        Args:
            mode: Fan mode - "default" (BIOS), "custom" (curve), or "fixed"
            
        Returns:
            Dictionary with success status
        """
        from ..dynamic.config import FanConfig
        
        if mode not in ("default", "custom", "fixed"):
            return {"success": False, "error": f"Invalid mode: {mode}. Must be default, custom, or fixed"}
        
        try:
            current_data = self.settings.getSetting("fan_config") or {}
            current_config = FanConfig.from_dict(current_data)
            current_config.mode = mode
            
            # Persist
            self.settings.setSetting("fan_config", current_config.to_dict())
            
            logger.info(f"Set fan mode to: {mode}")
            return {"success": True, "mode": mode}
            
        except Exception as e:
            logger.error(f"Failed to set fan mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def enable_fan_control(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable fan control.
        
        Args:
            enabled: Whether to enable fan control
            
        Returns:
            Dictionary with success status
        """
        from ..dynamic.config import FanConfig
        
        try:
            current_data = self.settings.getSetting("fan_config") or {}
            current_config = FanConfig.from_dict(current_data)
            current_config.enabled = enabled
            
            # Persist
            self.settings.setSetting("fan_config", current_config.to_dict())
            
            logger.info(f"Fan control {'enabled' if enabled else 'disabled'}")
            return {"success": True, "enabled": enabled}
            
        except Exception as e:
            logger.error(f"Failed to toggle fan control: {e}")
            return {"success": False, "error": str(e)}
