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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..core.safety import SafetyManager
    from ..core.blackbox import BlackBox
    from ..core.fan_control import FanControlService
    from ..core.settings_manager import SettingsManager
    from ..core.game_state_monitor import GameStateMonitor
    from ..platform.detect import PlatformInfo
    from ..tuning.autotune import AutotuneEngine, AutotuneConfig
    from ..tuning.runner import TestRunner
    from ..tuning.binning import BinningEngine
    from ..tuning.benchmark import BenchmarkRunner
    from ..tuning.iron_seeker import IronSeekerEngine
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
        benchmark_runner: Optional["BenchmarkRunner"] = None,
        iron_seeker_engine: Optional["IronSeekerEngine"] = None,
        blackbox: Optional["BlackBox"] = None
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
            iron_seeker_engine: Optional IronSeekerEngine for per-core tuning
            blackbox: Optional BlackBox for system metrics recording
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
        self.iron_seeker_engine = iron_seeker_engine
        self.blackbox = blackbox
        self.fan_control_service = None  # Will be set via set_fan_control_service()
        
        self._delay_task: Optional[asyncio.Task] = None
        self._autotune_task: Optional[asyncio.Task] = None
        self._binning_task: Optional[asyncio.Task] = None
        self._benchmark_task: Optional[asyncio.Task] = None
        self._iron_seeker_task: Optional[asyncio.Task] = None
    
    def set_blackbox(self, blackbox: "BlackBox") -> None:
        """Set the BlackBox recorder.
        
        Args:
            blackbox: BlackBox instance
        """
        self.blackbox = blackbox
    
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
    
    def set_iron_seeker_engine(self, engine: "IronSeekerEngine") -> None:
        """Set the Iron Seeker engine.
        
        Args:
            engine: IronSeekerEngine instance
        """
        self.iron_seeker_engine = engine
    
    def set_fan_control_service(self, service: "FanControlService") -> None:
        """Set the fan control service.
        
        Args:
            service: FanControlService instance
        """
        self.fan_control_service = service
    
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
    
    async def redetect_platform(self) -> Dict[str, Any]:
        """Force fresh platform detection, clearing any cached data.
        
        Clears the platform cache and performs fresh DMI detection.
        Updates the internal platform reference with the new detection result.
        
        Returns:
            Dictionary with model, variant, safe_limit, and detected status
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 3.4
        """
        from ..platform.detect import redetect_platform as _redetect
        
        logger.info("Manual platform re-detection requested")
        
        # Perform fresh detection
        new_platform = _redetect()
        
        # Update internal reference
        self.platform = new_platform
        
        logger.info(f"Platform re-detected: {new_platform.model} ({new_platform.variant})")
        
        return {
            "model": new_platform.model,
            "variant": new_platform.variant,
            "safe_limit": new_platform.safe_limit,
            "detected": new_platform.detected
        }
    
    # ==================== Undervolt Control ====================
    
    async def apply_undervolt(
        self,
        cores: List[int],
        timeout: int = 0
    ) -> Dict[str, Any]:
        """Apply undervolt values with optional delay and detailed diagnostics.
        
        Respects Game Only Mode setting - if enabled, values are saved but only
        applied when a game is running.
        
        Args:
            cores: List of 4 undervolt values (positive values will be negated)
            timeout: Delay in seconds before applying (0 for immediate)
            
        Returns:
            Dictionary with success status, applied cores, and diagnostics on error
            
        Feature: decktune-critical-fixes
        Validates: Requirements 1.2, 1.5, 5.1, 5.2
        """
        logger.info(f"Applying undervolt with values: {cores}, timeout: {timeout}")
        
        # Cancel any pending delay task
        self._cancel_delay_task()
        
        # Check ryzenadj availability before proceeding
        diagnostics = await self.ryzenadj.diagnose()
        
        if not diagnostics.get("binary_exists"):
            error_msg = "ryzenadj binary not found. Please ensure ryzenadj is installed in bin/"
            logger.error(error_msg)
            await self.event_emitter.emit_status("error")
            return {
                "success": False,
                "error": error_msg,
                "diagnostics": diagnostics
            }
        
        if not diagnostics.get("binary_executable"):
            error_msg = "ryzenadj binary is not executable. Please check file permissions."
            logger.error(error_msg)
            await self.event_emitter.emit_status("error")
            return {
                "success": False,
                "error": error_msg,
                "diagnostics": diagnostics
            }
        
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
        
        logger.debug(f"Applying clamped values: {clamped_cores} (original: {cores})")
        
        # CRITICAL FIX: Check if Game Only Mode is enabled
        game_only_mode_enabled = False
        game_is_running = False
        
        if hasattr(self, '_settings_manager') and self._settings_manager:
            game_only_mode_enabled = self._settings_manager.get_setting("game_only_mode", False)
            logger.debug(f"Game Only Mode enabled: {game_only_mode_enabled}")
        
        if game_only_mode_enabled and hasattr(self, '_game_only_mode_controller'):
            status = self._game_only_mode_controller.get_status()
            game_is_running = status.get("game_running", False)
            logger.debug(f"Game running: {game_is_running}")
        
        # Save values to settings first (always save, regardless of game state)
        self.settings.setSetting("cores", clamped_cores)
        self.settings.setSetting("lkg_cores", clamped_cores)
        self.settings.setSetting("lkg_timestamp", datetime.now().isoformat())
        
        # Determine if we should apply now or defer to GameOnlyModeController
        should_apply_now = True
        deferred_reason = None
        
        if game_only_mode_enabled:
            if game_is_running:
                # Game is running, apply immediately
                logger.info("Game Only Mode enabled and game is running - applying immediately")
                should_apply_now = True
            else:
                # No game running, defer application
                logger.info("Game Only Mode enabled but no game running - values saved, will apply on next game start")
                should_apply_now = False
                deferred_reason = "Game Only Mode enabled - values will apply when game starts"
        
        if should_apply_now:
            # Apply values via ryzenadj
            success, error = await self.ryzenadj.apply_values_async(clamped_cores)
            
            if success:
                self.settings.setSetting("status", "enabled")
                await self.event_emitter.emit_status("enabled")
                logger.info(f"Undervolt applied successfully: {clamped_cores}")
                return {
                    "success": True,
                    "cores": clamped_cores,
                    "commands_executed": self.ryzenadj.get_last_commands(),
                    "game_only_mode": game_only_mode_enabled,
                    "applied_immediately": True
                }
            else:
                await self.event_emitter.emit_status("error")
                logger.error(f"Failed to apply undervolt: {error}")
                
                # Return detailed diagnostics on failure
                return {
                    "success": False,
                    "error": error,
                    "diagnostics": diagnostics,
                    "commands_executed": self.ryzenadj.get_last_commands()
                }
        else:
            # Values saved but not applied (deferred to game start)
            self.settings.setSetting("status", "deferred")
            await self.event_emitter.emit_status("deferred")
            logger.info(f"Undervolt values saved but not applied: {clamped_cores}")
            return {
                "success": True,
                "cores": clamped_cores,
                "game_only_mode": True,
                "applied_immediately": False,
                "deferred_reason": deferred_reason
            }
    
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
            
            with open(export_path, 'w', encoding='utf-8') as f:
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
        
        with open(path, 'w', encoding='utf-8') as f:
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
        
        with open(path, 'w', encoding='utf-8') as f:
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
        
        with open(path, 'w', encoding='utf-8') as f:
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
        
        with open(path, 'w', encoding='utf-8') as f:
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
            True if autotune, binning, benchmark, Iron Seeker, or frequency wizard is running
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
        
        # Check Iron Seeker
        if self.iron_seeker_engine and self.iron_seeker_engine.is_running():
            return True
        
        # Check frequency wizard
        if hasattr(self, '_frequency_wizard_task') and self._frequency_wizard_task and not self._frequency_wizard_task.done():
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

    # ==================== Fan Control Curves ====================
    # Requirements: 1.1, 3.1, 6.1, 6.2, 6.3
    
    async def fan_apply_preset(self, preset_name: str) -> Dict[str, Any]:
        """Apply a predefined fan curve preset.
        
        Args:
            preset_name: Name of the preset ("stock", "silent", or "turbo")
            
        Returns:
            Dictionary with success status
            
        Requirements: 1.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        logger.info(f"Applying fan preset: {preset_name}")
        
        success = self.fan_control_service.apply_preset(preset_name)
        
        if success:
            return {"success": True, "preset": preset_name}
        else:
            return {"success": False, "error": f"Unknown preset: {preset_name}"}
    
    async def fan_create_custom(self, name: str, points: List[Dict[str, int]]) -> Dict[str, Any]:
        """Create a custom fan curve.
        
        Args:
            name: Name for the custom curve
            points: List of dictionaries with "temp" and "speed" keys
            
        Returns:
            Dictionary with success status
            
        Requirements: 3.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        logger.info(f"Creating custom fan curve: {name} with {len(points)} points")
        
        try:
            # Import FanPoint from fan_control module
            from ..core.fan_control import FanPoint
            
            # Convert dict points to FanPoint objects
            fan_points = []
            for point in points:
                temp = point.get("temp")
                speed = point.get("speed")
                
                if temp is None or speed is None:
                    return {"success": False, "error": "Each point must have 'temp' and 'speed' keys"}
                
                fan_points.append(FanPoint(temp=temp, speed=speed))
            
            # Create the custom curve
            success = self.fan_control_service.create_custom_curve(name, fan_points)
            
            if success:
                return {"success": True, "name": name, "points": len(fan_points)}
            else:
                return {"success": False, "error": "Failed to create custom curve (validation error)"}
                
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Failed to create custom curve: {e}")
            return {"success": False, "error": str(e)}
    
    async def fan_load_custom(self, name: str) -> Dict[str, Any]:
        """Load and activate a custom fan curve.
        
        Args:
            name: Name of the custom curve to load
            
        Returns:
            Dictionary with success status
            
        Requirements: 3.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        logger.info(f"Loading custom fan curve: {name}")
        
        success = self.fan_control_service.load_custom_curve(name)
        
        if success:
            return {"success": True, "name": name}
        else:
            return {"success": False, "error": f"Custom curve '{name}' not found"}
    
    async def fan_delete_custom(self, name: str) -> Dict[str, Any]:
        """Delete a custom fan curve.
        
        Args:
            name: Name of the custom curve to delete
            
        Returns:
            Dictionary with success status
            
        Requirements: 3.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        logger.info(f"Deleting custom fan curve: {name}")
        
        success = self.fan_control_service.delete_custom_curve(name)
        
        if success:
            return {"success": True, "name": name}
        else:
            return {"success": False, "error": f"Custom curve '{name}' not found"}
    
    async def fan_list_presets(self) -> Dict[str, Any]:
        """Get list of available fan curve presets.
        
        Returns:
            Dictionary with success status and list of preset names
            
        Requirements: 1.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        presets = self.fan_control_service.get_available_presets()
        
        return {
            "success": True,
            "presets": presets
        }
    
    async def fan_list_custom(self) -> Dict[str, Any]:
        """Get list of custom fan curves.
        
        Returns:
            Dictionary with success status and list of custom curve names
            
        Requirements: 3.1
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        custom_curves = self.fan_control_service.list_custom_curves()
        
        return {
            "success": True,
            "custom_curves": custom_curves
        }
    
    async def fan_get_status(self) -> Dict[str, Any]:
        """Get current fan control status.
        
        Returns:
            Dictionary with current temperature, fan speeds, and active curve info
            
        Requirements: 6.1, 6.2, 6.3
        """
        if not hasattr(self, 'fan_control_service') or self.fan_control_service is None:
            return {"success": False, "error": "Fan control service not initialized"}
        
        status = self.fan_control_service.get_current_status()
        
        return {
            "success": True,
            **status
        }

    # ==================== Iron Seeker ====================
    # Requirements: 1.1, 3.5, 5.1, 5.2, 5.3, 3.4
    
    async def start_iron_seeker(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start Iron Seeker per-core undervolt optimization.
        
        Iron Seeker tests each CPU core independently to find optimal
        undervolt values, accounting for silicon lottery variations.
        
        Args:
            config: Optional configuration dictionary with:
                - step_size: Step increment in mV (1-20, default 5)
                - test_duration: Test duration per iteration in seconds (10-300, default 60)
                - safety_margin: Safety margin to add to results in mV (0-20, default 5)
                - vdroop_pulse_ms: Pulse duration for Vdroop test in ms (default 100)
                
        Returns:
            Dictionary with success status or error if already running
            
        Requirements: 1.1, 7.1, 7.2, 7.3
        """
        if self.iron_seeker_engine is None:
            return {"success": False, "error": "Iron Seeker engine not configured"}
        
        if self.iron_seeker_engine.is_running():
            return {"success": False, "error": "Iron Seeker already running"}
        
        # Check if other operations are running
        if self._is_operation_running():
            return {
                "success": False,
                "error": "Another operation is running. Please wait for it to complete."
            }
        
        # Import here to avoid circular imports
        from ..tuning.iron_seeker import IronSeekerConfig
        
        # Parse configuration
        try:
            if config:
                iron_seeker_config = IronSeekerConfig(
                    step_size=config.get("step_size", 5),
                    test_duration=config.get("test_duration", 60),
                    safety_margin=config.get("safety_margin", 5),
                    vdroop_pulse_ms=config.get("vdroop_pulse_ms", 100)
                )
            else:
                iron_seeker_config = IronSeekerConfig()
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid Iron Seeker config: {e}")
            return {"success": False, "error": f"Invalid config: {e}"}
        
        logger.info(f"Starting Iron Seeker with config: step_size={iron_seeker_config.step_size}, "
                   f"test_duration={iron_seeker_config.test_duration}, "
                   f"safety_margin={iron_seeker_config.safety_margin}")
        
        # Get current undervolt values as initial values
        initial_values = self.settings.getSetting("cores") or [0, 0, 0, 0]
        
        # Run Iron Seeker in background task
        self._iron_seeker_task = asyncio.create_task(
            self._run_iron_seeker(iron_seeker_config, initial_values)
        )
        
        return {
            "success": True,
            "config": {
                "step_size": iron_seeker_config.step_size,
                "test_duration": iron_seeker_config.test_duration,
                "safety_margin": iron_seeker_config.safety_margin,
                "vdroop_pulse_ms": iron_seeker_config.vdroop_pulse_ms
            }
        }
    
    async def _run_iron_seeker(
        self,
        config: "IronSeekerConfig",
        initial_values: List[int]
    ) -> None:
        """Run Iron Seeker and handle completion.
        
        Args:
            config: IronSeekerConfig instance
            initial_values: Initial undervolt values before Iron Seeker
        """
        from ..tuning.iron_seeker import IronSeekerStoredResult
        
        try:
            result = await self.iron_seeker_engine.start(config, initial_values)
            
            # If not aborted, save results
            if not result.aborted and result.cores:
                # Create stored result format
                stored_result = IronSeekerStoredResult.from_result(result)
                
                # Save to settings via safety manager
                self.safety.save_iron_seeker_results(stored_result)
                
                # Also update current cores to recommended values
                recommended_values = [c.recommended for c in result.cores]
                self.settings.setSetting("cores", recommended_values)
                self.settings.setSetting("status", "enabled")
                
                logger.info(f"Iron Seeker completed: recommended values = {recommended_values}")
            else:
                logger.info("Iron Seeker was aborted or produced no results")
                
        except asyncio.CancelledError:
            logger.info("Iron Seeker task cancelled")
            await self.event_emitter.emit_status("disabled")
        except Exception as e:
            logger.exception(f"Iron Seeker error: {e}")
            await self.event_emitter.emit_status("error")
        finally:
            self._iron_seeker_task = None
    
    async def cancel_iron_seeker(self) -> Dict[str, Any]:
        """Cancel running Iron Seeker session.
        
        Cancels the Iron Seeker process, restores previous undervolt values,
        and clears the state file.
        
        Returns:
            Dictionary with success status
            
        Requirements: 3.5
        """
        if self.iron_seeker_engine is None:
            return {"success": False, "error": "Iron Seeker engine not configured"}
        
        if not self.iron_seeker_engine.is_running():
            return {"success": False, "error": "Iron Seeker not running"}
        
        logger.info("Cancelling Iron Seeker")
        self.iron_seeker_engine.cancel()
        
        # Cancel the background task if it exists
        if self._iron_seeker_task and not self._iron_seeker_task.done():
            self._iron_seeker_task.cancel()
            try:
                await self._iron_seeker_task
            except asyncio.CancelledError:
                pass
            self._iron_seeker_task = None
        
        return {"success": True}
    
    async def get_iron_seeker_status(self) -> Dict[str, Any]:
        """Get current Iron Seeker status.
        
        Returns status information including:
        - Whether Iron Seeker is running
        - Current state if running (core, value, progress)
        - Last results if available
        
        Returns:
            Dictionary with status information
            
        Requirements: 1.1
        """
        if self.iron_seeker_engine is None:
            return {"success": False, "error": "Iron Seeker engine not configured"}
        
        is_running = self.iron_seeker_engine.is_running()
        
        result = {
            "success": True,
            "running": is_running
        }
        
        # If running, include current state from safety manager
        if is_running:
            state = self.safety.load_iron_seeker_state()
            if state:
                result["current_core"] = state.current_core
                result["current_value"] = state.current_value
                result["core_results"] = state.core_results
        
        # Include last saved results if available
        stored_results = self.safety.load_iron_seeker_results()
        if stored_results:
            result["last_results"] = stored_results.to_dict()
        
        return result

    # ==================== Frequency Wizard ====================
    # Feature: frequency-based-wizard
    # Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    
    async def start_frequency_wizard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start frequency wizard session.
        
        Initiates automated frequency curve generation for a CPU core.
        The wizard tests voltage stability across a range of frequencies
        to create an optimal frequency-voltage curve.
        
        Args:
            config: Dictionary with wizard configuration:
                - core_id: CPU core ID to test (default: 0)
                - freq_start: Starting frequency in MHz (400-3500, default: 400)
                - freq_end: Ending frequency in MHz (must be > freq_start, default: 3500)
                - freq_step: Frequency step size in MHz (50-500, default: 100)
                - test_duration: Test duration per frequency in seconds (10-120, default: 30)
                - voltage_start: Starting voltage offset in mV (-100 to 0, default: -30)
                - voltage_step: Voltage step size in mV (1-10, default: 2)
                - safety_margin: Safety margin to add in mV (0-20, default: 5)
                - adaptive_step: Enable adaptive stepping (default: True)
                - preset: Optional preset name ("quick", "balanced", "thorough")
                
        Returns:
            Dictionary with success status, session_id, and estimated_duration:
            {
                "success": bool,
                "session_id": str,
                "estimated_duration": int  # seconds
            }
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.1
        """
        logger.info("=" * 80)
        logger.info("FREQUENCY WIZARD START REQUEST")
        logger.info("=" * 80)
        logger.info(f"Received config: {config}")
        
        # Check if other operations are running
        logger.info("Checking if other operations are running...")
        if self._is_operation_running():
            logger.warning("Another operation is already running - blocking frequency wizard start")
            logger.info(f"  - Autotune running: {self.autotune_engine and self.autotune_engine.is_running()}")
            logger.info(f"  - Binning running: {self.binning_engine and self.binning_engine.is_running()}")
            logger.info(f"  - Benchmark running: {self._benchmark_task and not self._benchmark_task.done()}")
            logger.info(f"  - Iron Seeker running: {self.iron_seeker_engine and self.iron_seeker_engine.is_running()}")
            logger.info(f"  - Frequency Wizard running: {hasattr(self, '_frequency_wizard_task') and self._frequency_wizard_task and not self._frequency_wizard_task.done()}")
            return {
                "success": False,
                "error": "Another operation is running. Please wait for it to complete."
            }
        logger.info("No other operations running - proceeding")
        
        # Check if test_runner is available
        logger.info(f"Checking test_runner availability: {self.test_runner is not None}")
        if not self.test_runner:
            logger.error("TestRunner not initialized - cannot start frequency wizard")
            logger.error("This usually means the plugin failed to initialize properly")
            return {
                "success": False,
                "error": "Test runner not initialized. Please restart the plugin."
            }
        logger.info("TestRunner is available")
        
        # Import here to avoid circular imports
        logger.info("Importing frequency wizard modules...")
        from ..tuning.frequency_wizard import FrequencyWizardConfig, FrequencyWizard
        from ..platform.cpufreq import CPUFreqController
        from pathlib import Path
        import uuid
        logger.info("Modules imported successfully")
        
        try:
            # Extract core_id
            core_id = config.get("core_id", 0)
            logger.info(f"Target core_id: {core_id}")
            
            # Check for preset
            preset = config.get("preset")
            logger.info(f"Preset specified: {preset}")
            
            if preset:
                logger.info(f"Loading preset configuration: {preset}")
                if preset == "quick":
                    wizard_config = FrequencyWizardConfig.quick_preset()
                elif preset == "balanced":
                    wizard_config = FrequencyWizardConfig.balanced_preset()
                elif preset == "thorough":
                    wizard_config = FrequencyWizardConfig.thorough_preset()
                else:
                    logger.error(f"Unknown preset: {preset}")
                    return {"success": False, "error": f"Unknown preset: {preset}"}
                logger.info(f"Preset loaded: {wizard_config}")
            else:
                # Create config from parameters
                logger.info("Creating custom configuration from parameters")
                wizard_config = FrequencyWizardConfig(
                    freq_start=config.get("freq_start", 400),
                    freq_end=config.get("freq_end", 3500),
                    freq_step=config.get("freq_step", 100),
                    test_duration=config.get("test_duration", 30),
                    voltage_start=config.get("voltage_start", -30),
                    voltage_step=config.get("voltage_step", 2),
                    safety_margin=config.get("safety_margin", 5),
                    adaptive_step=config.get("adaptive_step", True)
                )
                logger.info(f"Custom config created: {wizard_config}")
            
            # Validate configuration
            logger.info("Validating wizard configuration...")
            try:
                wizard_config.validate()
                logger.info("Configuration validation passed")
            except Exception as validation_error:
                logger.error(f"Configuration validation failed: {validation_error}")
                raise
            
            # Create CPUFreq controller
            logger.info("Creating CPUFreq controller...")
            try:
                cpufreq_controller = CPUFreqController()
                logger.info("CPUFreq controller created successfully")
            except Exception as cpufreq_error:
                logger.error(f"Failed to create CPUFreq controller: {cpufreq_error}")
                raise
            
            # Create save path for intermediate results
            save_dir = Path.home() / ".decktune" / "frequency_wizard"
            logger.info(f"Creating save directory: {save_dir}")
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f"wizard_core{core_id}_intermediate.json"
            logger.info(f"Intermediate results will be saved to: {save_path}")
            
            # Create wizard instance
            session_id = str(uuid.uuid4())
            logger.info(f"Creating wizard instance with session_id: {session_id}")
            try:
                wizard = FrequencyWizard(
                    config=wizard_config,
                    cpufreq_controller=cpufreq_controller,
                    test_runner=self.test_runner,
                    progress_callback=self._frequency_wizard_progress_callback,
                    save_path=save_path
                )
                logger.info("Wizard instance created successfully")
            except Exception as wizard_error:
                logger.error(f"Failed to create wizard instance: {wizard_error}")
                raise
            
            # Store wizard instance
            if not hasattr(self, '_frequency_wizards'):
                self._frequency_wizards = {}
                logger.info("Initialized _frequency_wizards dictionary")
            self._frequency_wizards[session_id] = wizard
            logger.info(f"Wizard instance stored with session_id: {session_id}")
            
            # Calculate estimated duration
            num_frequencies = len(wizard._calculate_frequency_points())
            # Rough estimate: test_duration * num_frequencies * avg_binary_search_iterations
            estimated_duration = wizard_config.test_duration * num_frequencies * 6
            logger.info(f"Estimated duration: {estimated_duration}s ({num_frequencies} frequency points)")
            
            # Start wizard in background task
            logger.info("Starting wizard background task...")
            self._frequency_wizard_task = asyncio.create_task(
                self._run_frequency_wizard(session_id, wizard, core_id)
            )
            logger.info("Background task created and started")
            
            logger.info("=" * 80)
            logger.info("FREQUENCY WIZARD STARTED SUCCESSFULLY")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"Core ID: {core_id}")
            logger.info(f"Estimated Duration: {estimated_duration}s")
            logger.info("=" * 80)
            
            logger.info(
                f"Started frequency wizard: session_id={session_id}, core={core_id}, "
                f"estimated_duration={estimated_duration}s"
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "estimated_duration": estimated_duration
            }
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("FREQUENCY WIZARD START FAILED")
            logger.error("=" * 80)
            logger.exception(f"Exception during frequency wizard start: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            logger.error("=" * 80)
            return {"success": False, "error": str(e)}
    
    async def _run_frequency_wizard(
        self,
        session_id: str,
        wizard: "FrequencyWizard",
        core_id: int
    ) -> None:
        """Run frequency wizard and handle completion.
        
        Args:
            session_id: Wizard session ID
            wizard: FrequencyWizard instance
            core_id: CPU core ID
        """
        logger.info("=" * 80)
        logger.info(f"FREQUENCY WIZARD EXECUTION STARTED")
        logger.info(f"Session ID: {session_id}, Core ID: {core_id}")
        logger.info("=" * 80)
        
        try:
            logger.info("Calling wizard.run()...")
            curve = await wizard.run(core_id)
            logger.info(f"Wizard.run() completed successfully")
            logger.info(f"Generated curve: {curve}")
            
            # Save curve to settings
            logger.info("Saving curve to settings...")
            curves = self.settings.getSetting("frequency_curves") or {}
            logger.info(f"Existing curves: {list(curves.keys())}")
            curves[str(core_id)] = curve.to_dict()
            self.settings.setSetting("frequency_curves", curves)
            logger.info(f"Curve saved for core {core_id}")
            
            # Emit completion event
            logger.info("Emitting completion event...")
            await self.event_emitter.emit_status("frequency_wizard_complete")
            logger.info("Completion event emitted")
            
            logger.info("=" * 80)
            logger.info(f"FREQUENCY WIZARD COMPLETED SUCCESSFULLY")
            logger.info(f"Session ID: {session_id}, Core ID: {core_id}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"FREQUENCY WIZARD EXECUTION FAILED")
            logger.error(f"Session ID: {session_id}, Core ID: {core_id}")
            logger.error("=" * 80)
            logger.exception(f"Exception during wizard execution: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            logger.error("=" * 80)
            await self.event_emitter.emit_status("error")
        finally:
            # Clean up wizard instance
            if hasattr(self, '_frequency_wizards') and session_id in self._frequency_wizards:
                del self._frequency_wizards[session_id]
    
    def _frequency_wizard_progress_callback(self, progress: "WizardProgress") -> None:
        """Callback for frequency wizard progress updates.
        
        Args:
            progress: WizardProgress instance
        """
        logger.debug(f"Progress callback: {progress.progress_percent:.1f}% - "
                    f"Freq: {progress.current_frequency}MHz, "
                    f"Voltage: {progress.current_voltage}mV, "
                    f"Completed: {progress.completed_points}/{progress.total_points}")
        
        # Store latest progress
        if not hasattr(self, '_frequency_wizard_progress'):
            self._frequency_wizard_progress = {}
            logger.debug("Initialized _frequency_wizard_progress dictionary")
        
        # Find session_id for this wizard (there should only be one active)
        if hasattr(self, '_frequency_wizards'):
            for session_id in self._frequency_wizards:
                self._frequency_wizard_progress[session_id] = progress
                logger.debug(f"Stored progress for session {session_id}")
                break
        else:
            logger.warning("No active frequency wizards found in progress callback")
    
    async def get_frequency_wizard_progress(self) -> Dict[str, Any]:
        """Get current frequency wizard progress.
        
        Returns progress information including current frequency being tested,
        current voltage, progress percentage, and estimated time remaining.
        
        Returns:
            Dictionary with progress information:
            {
                "running": bool,
                "current_frequency": int,  # MHz
                "current_voltage": int,  # mV
                "progress_percent": float,  # 0-100
                "estimated_remaining": int,  # seconds
                "completed_points": int,
                "total_points": int
            }
            
        Feature: frequency-based-wizard, Property 13: RPC response completeness
        Validates: Requirements 11.2
        """
        if not hasattr(self, '_frequency_wizard_progress') or not self._frequency_wizard_progress:
            return {
                "running": False,
                "current_frequency": 0,
                "current_voltage": 0,
                "progress_percent": 0.0,
                "estimated_remaining": 0,
                "completed_points": 0,
                "total_points": 0
            }
        
        # Get latest progress (should only be one active session)
        progress = next(iter(self._frequency_wizard_progress.values()))
        
        return progress.to_dict()
    
    async def cancel_frequency_wizard(self) -> Dict[str, Any]:
        """Cancel running frequency wizard.
        
        Stops the wizard and restores original CPU governor and voltage settings
        within 2 seconds.
        
        Returns:
            Dictionary with success status
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.3
        """
        if not hasattr(self, '_frequency_wizards') or not self._frequency_wizards:
            return {"success": False, "error": "No frequency wizard running"}
        
        try:
            # Cancel all active wizards
            for wizard in self._frequency_wizards.values():
                wizard.cancel()
            
            # Wait for task to complete (with timeout)
            if hasattr(self, '_frequency_wizard_task') and self._frequency_wizard_task:
                try:
                    await asyncio.wait_for(self._frequency_wizard_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Frequency wizard cancellation timed out")
                    self._frequency_wizard_task.cancel()
            
            logger.info("Frequency wizard cancelled")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to cancel frequency wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_frequency_curve(self, core_id: int) -> Dict[str, Any]:
        """Get saved frequency curve for a CPU core.
        
        Retrieves the complete frequency-voltage curve data for the specified
        core, including all frequency points with voltages and stability status.
        
        Args:
            core_id: CPU core ID (0-based)
            
        Returns:
            Dictionary with success status and curve data:
            {
                "success": bool,
                "curve": {
                    "core_id": int,
                    "points": [{"frequency_mhz": int, "voltage_mv": int, "stable": bool, ...}],
                    "created_at": float,
                    "wizard_config": {...}
                }
            }
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.4
        """
        try:
            curves = self.settings.getSetting("frequency_curves") or {}
            curve_data = curves.get(str(core_id))
            
            if not curve_data:
                return {
                    "success": False,
                    "error": f"No frequency curve found for core {core_id}"
                }
            
            return {
                "success": True,
                "curve": curve_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get frequency curve: {e}")
            return {"success": False, "error": str(e)}
    
    async def apply_frequency_curve(self, curves: Dict[str, Any]) -> Dict[str, Any]:
        """Apply frequency curves to CPU cores.
        
        Validates and activates the provided frequency curves. The curves will
        be used by the frequency-based voltage controller to adjust voltage
        based on current CPU frequency.
        
        Args:
            curves: Dictionary mapping core IDs to curve data:
                {
                    "0": {"core_id": 0, "points": [...], ...},
                    "1": {"core_id": 1, "points": [...], ...}
                }
                
        Returns:
            Dictionary with success status
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.5
        """
        try:
            from ..tuning.frequency_curve import FrequencyCurve
            
            # Validate all curves
            for core_id_str, curve_data in curves.items():
                try:
                    curve = FrequencyCurve.from_dict(curve_data)
                    curve.validate()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Invalid curve for core {core_id_str}: {e}"
                    }
            
            # Save curves to settings
            self.settings.setSetting("frequency_curves", curves)
            
            logger.info(f"Applied frequency curves for {len(curves)} cores")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to apply frequency curves: {e}")
            return {"success": False, "error": str(e)}
    
    async def enable_frequency_mode(self) -> Dict[str, Any]:
        """Enable frequency-based voltage control.
        
        Activates the frequency voltage controller which adjusts CPU voltage
        based on current frequency using the loaded frequency curves.
        
        Returns:
            Dictionary with success status
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.6
        """
        try:
            # Set frequency mode flag
            self.settings.setSetting("frequency_mode_enabled", True)
            
            # TODO: Activate frequency controller in Rust dynamic controller
            # This will be implemented when integrating with gymdeck3
            
            logger.info("Frequency-based mode enabled")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to enable frequency mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def disable_frequency_mode(self) -> Dict[str, Any]:
        """Disable frequency-based voltage control.
        
        Deactivates the frequency voltage controller and returns to the
        previous voltage control mode (load-based or manual).
        
        Returns:
            Dictionary with success status
            
        Feature: frequency-based-wizard
        Validates: Requirements 11.7
        """
        try:
            # Clear frequency mode flag
            self.settings.setSetting("frequency_mode_enabled", False)
            
            # TODO: Deactivate frequency controller in Rust dynamic controller
            # This will be implemented when integrating with gymdeck3
            
            logger.info("Frequency-based mode disabled")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to disable frequency mode: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Context Profile Management ====================
    # Requirements: 1.1
    
    async def create_contextual_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contextual game profile.
        
        Contextual profiles can have the same app_id but different conditions,
        allowing multiple profiles per game for different contexts (battery level,
        power mode, temperature).
        
        Args:
            profile_data: Dictionary with profile fields:
                - app_id: Steam AppID (required)
                - name: Profile name (required)
                - cores: Undervolt values [core0, core1, core2, core3] (required)
                - dynamic_enabled: Whether dynamic mode is enabled (optional, default False)
                - dynamic_config: Dynamic mode configuration (optional)
                - conditions: Context conditions dictionary (optional):
                    - battery_threshold: Profile active when battery <= threshold (0-100)
                    - power_mode: Profile active when power mode matches ("ac", "battery", or None)
                    - temp_threshold: Profile active when temp >= threshold (0-100°C)
                
        Returns:
            Dictionary with success status and created profile
            
        Requirements: 1.1
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
            conditions_data = profile_data.get("conditions", {})
            
            # Create ContextCondition from conditions data
            from ..dynamic.context import ContextCondition
            conditions = ContextCondition(
                battery_threshold=conditions_data.get("battery_threshold"),
                power_mode=conditions_data.get("power_mode"),
                temp_threshold=conditions_data.get("temp_threshold"),
            )
            
            # Create contextual profile
            profile = await self.profile_manager.create_contextual_profile(
                app_id=app_id,
                name=name,
                cores=cores,
                conditions=conditions,
                dynamic_enabled=dynamic_enabled,
                dynamic_config=dynamic_config
            )
            
            if profile:
                logger.info(f"Created contextual profile '{name}' (app_id: {app_id})")
                return {
                    "success": True,
                    "profile": profile.to_dict()
                }
            else:
                return {"success": False, "error": "Failed to create contextual profile (invalid data)"}
                
        except Exception as e:
            logger.error(f"Failed to create contextual profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_contextual_profile(
        self,
        profile_name: str,
        app_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing contextual profile.
        
        Args:
            profile_name: Name of the profile to update
            app_id: Steam AppID of the profile
            updates: Dictionary with fields to update:
                - name: New profile name
                - cores: New undervolt values
                - dynamic_enabled: Whether dynamic mode is enabled
                - dynamic_config: Dynamic mode configuration
                - conditions: New context conditions dictionary
            
        Returns:
            Dictionary with success status
            
        Requirements: 1.1
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            # Convert conditions dict to ContextCondition if provided
            if "conditions" in updates:
                from ..dynamic.context import ContextCondition
                conditions_data = updates["conditions"]
                updates["conditions"] = ContextCondition(
                    battery_threshold=conditions_data.get("battery_threshold"),
                    power_mode=conditions_data.get("power_mode"),
                    temp_threshold=conditions_data.get("temp_threshold"),
                )
            
            success = await self.profile_manager.update_contextual_profile(
                profile_name=profile_name,
                app_id=app_id,
                **updates
            )
            
            if success:
                logger.info(f"Updated contextual profile '{profile_name}' for app_id {app_id}")
                return {"success": True}
            else:
                return {"success": False, "error": f"Profile '{profile_name}' for app_id {app_id} not found"}
                
        except Exception as e:
            logger.error(f"Failed to update contextual profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_contextual_profile(
        self,
        profile_name: str,
        app_id: int
    ) -> Dict[str, Any]:
        """Delete a contextual profile.
        
        Args:
            profile_name: Name of the profile to delete
            app_id: Steam AppID of the profile
            
        Returns:
            Dictionary with success status
            
        Requirements: 1.1
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            success = await self.profile_manager.delete_contextual_profile(
                profile_name=profile_name,
                app_id=app_id
            )
            
            if success:
                logger.info(f"Deleted contextual profile '{profile_name}' for app_id {app_id}")
                return {"success": True}
            else:
                return {"success": False, "error": f"Profile '{profile_name}' for app_id {app_id} not found"}
                
        except Exception as e:
            logger.error(f"Failed to delete contextual profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_contextual_profiles(
        self,
        app_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get contextual profiles, optionally filtered by app_id.
        
        Args:
            app_id: Optional Steam AppID to filter by (None for all profiles)
            
        Returns:
            Dictionary with success status and list of profiles
            
        Requirements: 1.1
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            profiles = self.profile_manager.get_contextual_profiles(app_id)
            profiles_list = [profile.to_dict() for profile in profiles]
            
            return {
                "success": True,
                "profiles": profiles_list,
                "count": len(profiles_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to get contextual profiles: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_context(self) -> Dict[str, Any]:
        """Get current system context (battery, power mode, temperature).
        
        Reads the current system state used for contextual profile matching.
        
        Returns:
            Dictionary with success status and context data:
            - battery_percent: Current battery level (0-100)
            - power_mode: Current power mode ("ac" or "battery")
            - temperature_c: Current CPU temperature in Celsius
            
        Requirements: 1.1
        """
        try:
            from ..dynamic.context import SystemContext
            
            context = await SystemContext.read_current()
            
            return {
                "success": True,
                "context": context.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system context: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_active_profile(self) -> Dict[str, Any]:
        """Get the currently active contextual profile.
        
        Returns the profile that is currently applied based on the
        current app and system context.
        
        Returns:
            Dictionary with success status and active profile (or None if global default)
            
        Requirements: 1.1
        """
        if not self.profile_manager:
            return {"success": False, "error": "ProfileManager not initialized"}
        
        try:
            active_profile = self.profile_manager.get_active_profile()
            
            if active_profile:
                return {
                    "success": True,
                    "profile": active_profile.to_dict(),
                    "is_global_default": False
                }
            else:
                # Return global default info
                global_default = self.profile_manager.get_global_default()
                return {
                    "success": True,
                    "profile": {
                        "name": "Global Default",
                        "app_id": None,
                        "cores": global_default.get("cores", [0, 0, 0, 0]),
                        "dynamic_enabled": global_default.get("dynamic_enabled", False),
                        "dynamic_config": global_default.get("dynamic_config"),
                        "conditions": {}
                    },
                    "is_global_default": True
                }
            
        except Exception as e:
            logger.error(f"Failed to get active profile: {e}")
            return {"success": False, "error": str(e)}

    # ==================== BlackBox Recording ====================
    # Requirements: 3.3
    
    async def list_blackbox_recordings(self) -> Dict[str, Any]:
        """List available BlackBox recordings.
        
        Returns the last 5 BlackBox recordings with timestamps and reasons.
        Recordings are created when crashes or instability events are detected.
        
        Returns:
            Dictionary with success status and list of recordings:
            - recordings: List of dicts with filename, timestamp, reason
            - count: Number of recordings
            
        Requirements: 3.3
        """
        if not self.blackbox:
            return {"success": False, "error": "BlackBox not initialized"}
        
        try:
            recordings = self.blackbox.list_recordings()
            
            return {
                "success": True,
                "recordings": recordings,
                "count": len(recordings)
            }
            
        except Exception as e:
            logger.error(f"Failed to list BlackBox recordings: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_blackbox_recording(self, filename: str) -> Dict[str, Any]:
        """Get a specific BlackBox recording by filename.
        
        Loads and returns the full recording data including all metric samples.
        
        Args:
            filename: Name of the recording file (e.g., "blackbox_20260116_123045.json")
            
        Returns:
            Dictionary with success status and recording data:
            - timestamp: ISO timestamp when recording was saved
            - reason: Reason for the recording (e.g., "watchdog_timeout")
            - duration_sec: Duration of recorded data in seconds
            - samples: List of metric samples with:
                - timestamp: Unix timestamp
                - temperature_c: CPU temperature
                - cpu_load_percent: CPU load percentage
                - undervolt_values: Per-core undervolt values
                - fan_speed_rpm: Fan speed
                - fan_pwm: Fan PWM value
            
        Requirements: 3.3
        """
        if not self.blackbox:
            return {"success": False, "error": "BlackBox not initialized"}
        
        if not filename:
            return {"success": False, "error": "filename is required"}
        
        try:
            recording = self.blackbox.load_recording(filename)
            
            if recording is None:
                return {"success": False, "error": f"Recording '{filename}' not found"}
            
            return {
                "success": True,
                "recording": recording.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get BlackBox recording: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Acoustic Fan Profiles ====================
    # Requirements: 4.4
    
    async def get_acoustic_profile(self) -> Dict[str, Any]:
        """Get current acoustic fan profile.
        
        Returns the currently selected acoustic profile (Silent, Balanced,
        MaxCooling, or Custom).
        
        Returns:
            Dictionary with success status and profile info:
            - profile: Current profile name ("silent", "balanced", "max_cooling", "custom")
            - description: Human-readable description of the profile
            
        Requirements: 4.4
        """
        try:
            # Get acoustic profile from settings
            acoustic_data = self.settings.getSetting("acoustic_profile") or {}
            profile = acoustic_data.get("profile", "balanced")
            
            # Profile descriptions
            descriptions = {
                "silent": "Prioritizes low noise (max 3000 RPM until 85°C)",
                "balanced": "Balances noise and cooling (linear 30-70°C → 1500-4500 RPM)",
                "max_cooling": "Maximum cooling performance (max RPM at 60°C+)",
                "custom": "User-defined fan curve"
            }
            
            return {
                "success": True,
                "profile": profile,
                "description": descriptions.get(profile, "Unknown profile")
            }
            
        except Exception as e:
            logger.error(f"Failed to get acoustic profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_acoustic_profile(self, profile: str) -> Dict[str, Any]:
        """Set acoustic fan profile.
        
        Changes the fan curve to match the selected acoustic profile.
        The selection is persisted and restored on boot.
        
        Args:
            profile: Profile name - one of:
                - "silent": Low noise priority (max 3000 RPM until 85°C)
                - "balanced": Balance noise and cooling
                - "max_cooling": Maximum cooling (max RPM at 60°C+)
                - "custom": Use custom fan curve
                
        Returns:
            Dictionary with success status
            
        Requirements: 4.4
        """
        valid_profiles = ["silent", "balanced", "max_cooling", "custom"]
        
        if profile not in valid_profiles:
            return {
                "success": False,
                "error": f"Invalid profile: {profile}. Must be one of: {', '.join(valid_profiles)}"
            }
        
        try:
            # Get current acoustic settings
            acoustic_data = self.settings.getSetting("acoustic_profile") or {}
            
            # Update profile
            acoustic_data["profile"] = profile
            
            # Persist
            self.settings.setSetting("acoustic_profile", acoustic_data)
            
            logger.info(f"Set acoustic profile to: {profile}")
            return {"success": True, "profile": profile}
            
        except Exception as e:
            logger.error(f"Failed to set acoustic profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_pwm_smoothing_config(self) -> Dict[str, Any]:
        """Get PWM smoothing configuration.
        
        Returns the current PWM smoothing settings that control how
        fan speed changes are interpolated.
        
        Returns:
            Dictionary with success status and config:
            - enabled: Whether PWM smoothing is enabled
            - ramp_time_sec: Time to ramp from 0 to 100% (default 2.0)
            
        Requirements: 5.1
        """
        try:
            # Get PWM smoothing config from settings
            smoothing_data = self.settings.getSetting("pwm_smoothing") or {}
            
            return {
                "success": True,
                "config": {
                    "enabled": smoothing_data.get("enabled", True),
                    "ramp_time_sec": smoothing_data.get("ramp_time_sec", 2.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get PWM smoothing config: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_pwm_smoothing_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set PWM smoothing configuration.
        
        Configures how fan speed changes are interpolated to prevent
        sudden RPM jumps.
        
        Args:
            config: Dictionary with config fields:
                - enabled: Whether PWM smoothing is enabled (optional)
                - ramp_time_sec: Time to ramp from 0 to 100% in seconds (optional, 0.5-10.0)
                
        Returns:
            Dictionary with success status and updated config
            
        Requirements: 5.1
        """
        try:
            # Get current config
            smoothing_data = self.settings.getSetting("pwm_smoothing") or {}
            
            # Update fields
            if "enabled" in config:
                smoothing_data["enabled"] = bool(config["enabled"])
            
            if "ramp_time_sec" in config:
                ramp_time = float(config["ramp_time_sec"])
                if not (0.5 <= ramp_time <= 10.0):
                    return {
                        "success": False,
                        "error": f"ramp_time_sec must be between 0.5 and 10.0, got {ramp_time}"
                    }
                smoothing_data["ramp_time_sec"] = ramp_time
            
            # Persist
            self.settings.setSetting("pwm_smoothing", smoothing_data)
            
            logger.info(f"Updated PWM smoothing config: enabled={smoothing_data.get('enabled', True)}, "
                       f"ramp_time_sec={smoothing_data.get('ramp_time_sec', 2.0)}")
            
            return {
                "success": True,
                "config": {
                    "enabled": smoothing_data.get("enabled", True),
                    "ramp_time_sec": smoothing_data.get("ramp_time_sec", 2.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to set PWM smoothing config: {e}")
            return {"success": False, "error": str(e)}


    # ==================== Crash Metrics (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 1.2
    
    async def get_crash_metrics(self) -> Dict[str, Any]:
        """Get crash recovery metrics.
        
        Returns crash recovery statistics including total count,
        last crash date, and history of crash events.
        
        Returns:
            Dictionary with success status and CrashMetrics data:
            - total_count: Total number of crash recoveries
            - last_crash_date: ISO 8601 timestamp of last crash
            - history: List of CrashRecord objects
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 1.2
        """
        try:
            from ..core.crash_metrics import CrashMetricsManager
            
            # Get or create crash metrics manager
            if not hasattr(self, '_crash_metrics_manager'):
                self._crash_metrics_manager = CrashMetricsManager(self.settings)
            
            metrics = self._crash_metrics_manager.get_metrics()
            
            return {
                "success": True,
                "metrics": metrics.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get crash metrics: {e}")
            return {"success": False, "error": str(e)}
    
    def set_crash_metrics_manager(self, manager) -> None:
        """Set the crash metrics manager.
        
        Args:
            manager: CrashMetricsManager instance
        """
        self._crash_metrics_manager = manager
    
    # ==================== Telemetry (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 2.3, 2.4
    
    async def get_telemetry(self, seconds: int = 60) -> Dict[str, Any]:
        """Get recent telemetry samples.
        
        Returns temperature, power, and load data for the specified
        time window.
        
        Args:
            seconds: Number of seconds of data to retrieve (default 60)
            
        Returns:
            Dictionary with success status and telemetry samples:
            - samples: List of TelemetrySample objects
            - count: Number of samples returned
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 2.3, 2.4
        """
        try:
            from ..core.telemetry import TelemetryManager
            
            # Get or create telemetry manager
            if not hasattr(self, '_telemetry_manager'):
                self._telemetry_manager = TelemetryManager()
            
            samples = self._telemetry_manager.get_recent(seconds)
            
            return {
                "success": True,
                "samples": [s.to_dict() for s in samples],
                "count": len(samples)
            }
            
        except Exception as e:
            logger.error(f"Failed to get telemetry: {e}")
            return {"success": False, "error": str(e)}
    
    def set_telemetry_manager(self, manager) -> None:
        """Set the telemetry manager.
        
        Args:
            manager: TelemetryManager instance
        """
        self._telemetry_manager = manager
    
    # ==================== Session History (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 8.4, 8.5, 8.6
    
    async def get_session_history(self, limit: int = 30) -> Dict[str, Any]:
        """Get session history.
        
        Returns recent gaming sessions with metrics.
        
        Args:
            limit: Maximum number of sessions to return (default 30)
            
        Returns:
            Dictionary with success status and session list:
            - sessions: List of Session objects
            - count: Number of sessions returned
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.4
        """
        try:
            from ..core.session_manager import SessionManager
            
            # Get or create session manager
            if not hasattr(self, '_session_manager'):
                self._session_manager = SessionManager(self.settings)
            
            sessions = self._session_manager.get_history(limit)
            
            return {
                "success": True,
                "sessions": [s.to_dict() for s in sessions],
                "count": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific session by ID.
        
        Returns detailed session information including metrics and samples.
        
        Args:
            session_id: UUID of the session to retrieve
            
        Returns:
            Dictionary with success status and session data
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.5
        """
        try:
            from ..core.session_manager import SessionManager
            
            # Get or create session manager
            if not hasattr(self, '_session_manager'):
                self._session_manager = SessionManager(self.settings)
            
            session = self._session_manager.get_session(session_id)
            
            if session is None:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            
            return {
                "success": True,
                "session": session.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return {"success": False, "error": str(e)}
    
    async def compare_sessions(self, id1: str, id2: str) -> Dict[str, Any]:
        """Compare two sessions.
        
        Returns side-by-side metric comparison with differences.
        The diff values are calculated as (session1 - session2).
        
        Args:
            id1: UUID of first session
            id2: UUID of second session
            
        Returns:
            Dictionary with success status and comparison data:
            - session1: First session data
            - session2: Second session data
            - diff: Metric differences (session1 - session2)
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.6
        """
        try:
            from ..core.session_manager import SessionManager
            
            # Get or create session manager
            if not hasattr(self, '_session_manager'):
                self._session_manager = SessionManager(self.settings)
            
            comparison = self._session_manager.compare_sessions(id1, id2)
            
            if comparison is None:
                return {
                    "success": False,
                    "error": "One or both sessions not found or have no metrics"
                }
            
            return {
                "success": True,
                **comparison
            }
            
        except Exception as e:
            logger.error(f"Failed to compare sessions: {e}")
            return {"success": False, "error": str(e)}
    
    def set_session_manager(self, manager) -> None:
        """Set the session manager.
        
        Args:
            manager: SessionManager instance
        """
        self._session_manager = manager
    
    # ==================== Wizard (v3.1) ====================
    # Feature: decktune-3.1-reliability-ux
    # Requirements: 5.5, 5.6
    
    async def get_wizard_state(self) -> Dict[str, Any]:
        """Get wizard settings state.
        
        Returns the current wizard settings including whether first run
        is complete and the selected goal.
        
        Returns:
            Dictionary with success status and wizard settings:
            - first_run_complete: Whether first run wizard is complete
            - wizard_goal: Selected goal (quiet, balanced, battery, performance)
            - wizard_completed_at: ISO 8601 timestamp of completion
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.5, 5.6
        """
        try:
            first_run_complete = self.settings.getSetting("first_run_complete") or False
            wizard_goal = self.settings.getSetting("wizard_goal")
            wizard_completed_at = self.settings.getSetting("wizard_completed_at")
            
            return {
                "success": True,
                "wizard_state": {
                    "first_run_complete": first_run_complete,
                    "wizard_goal": wizard_goal,
                    "wizard_completed_at": wizard_completed_at
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get wizard state: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_wizard(self, goal: str) -> Dict[str, Any]:
        """Complete the setup wizard with selected goal.
        
        Saves the user's goal preference and marks first run as complete.
        
        Args:
            goal: Selected goal - one of: quiet, balanced, battery, performance
            
        Returns:
            Dictionary with success status
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.5
        """
        valid_goals = ["quiet", "balanced", "battery", "performance"]
        
        if goal not in valid_goals:
            return {
                "success": False,
                "error": f"Invalid goal: {goal}. Must be one of: {', '.join(valid_goals)}"
            }
        
        try:
            from datetime import datetime
            
            self.settings.setSetting("wizard_goal", goal)
            self.settings.setSetting("wizard_completed_at", datetime.now().isoformat())
            self.settings.setSetting("first_run_complete", True)
            
            logger.info(f"Wizard completed with goal: {goal}")
            
            return {
                "success": True,
                "goal": goal
            }
            
        except Exception as e:
            logger.error(f"Failed to complete wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def reset_wizard(self) -> Dict[str, Any]:
        """Reset wizard state to allow re-running.
        
        Clears first_run_complete flag so wizard will show again.
        Does not clear the previously selected goal.
        
        Returns:
            Dictionary with success status
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 5.6
        """
        try:
            self.settings.setSetting("first_run_complete", False)
            
            logger.info("Wizard state reset - will show on next load")
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to reset wizard: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Settings Management ====================
    # Feature: ui-refactor-settings
    # Requirements: 3.1, 3.2, 3.3, 10.3, 10.4
    
    async def save_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """Save a single setting to persistent storage.
        
        Saves critical plugin settings (Expert Mode, Apply on Startup,
        Game Only Mode, last active profile) to backend storage.
        
        Args:
            key: Setting key
            value: Setting value (must be JSON-serializable)
            
        Returns:
            Dictionary with success status
            
        Feature: ui-refactor-settings
        Validates: Requirements 3.1, 10.3
        """
        if not hasattr(self, '_settings_manager'):
            return {"success": False, "error": "Settings manager not initialized"}
        
        try:
            success = self._settings_manager.save_setting(key, value)
            
            if success:
                logger.debug(f"Saved setting: {key}")
                return {"success": True}
            else:
                return {"success": False, "error": "Failed to save setting"}
                
        except Exception as e:
            logger.error(f"Failed to save setting '{key}': {e}")
            return {"success": False, "error": str(e)}
    
    async def get_setting(self, key: str, default: Any = None) -> Dict[str, Any]:
        """Retrieve a setting from storage.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Dictionary with success status and value
            
        Feature: ui-refactor-settings
        Validates: Requirements 3.2, 10.3
        """
        if not hasattr(self, '_settings_manager'):
            return {"success": False, "error": "Settings manager not initialized"}
        
        try:
            value = self._settings_manager.get_setting(key, default)
            
            return {
                "success": True,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Failed to get setting '{key}': {e}")
            return {"success": False, "error": str(e)}
    
    async def load_setting(self, key: str, default: Any = None) -> Dict[str, Any]:
        """Alias for get_setting for consistency with frontend naming.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Dictionary with success status and value
            
        Feature: manual-dynamic-mode
        Validates: Requirements 10.5
        """
        return await self.get_setting(key, default)
    
    async def load_all_settings(self) -> Dict[str, Any]:
        """Load all settings from storage.
        
        Returns all persisted settings including Expert Mode,
        Apply on Startup, Game Only Mode, and last active profile.
        
        Returns:
            Dictionary with success status and all settings
            
        Feature: ui-refactor-settings
        Validates: Requirements 3.2, 10.4
        """
        if not hasattr(self, '_settings_manager'):
            return {"success": False, "error": "Settings manager not initialized"}
        
        try:
            settings = self._settings_manager.load_all_settings()
            
            return {
                "success": True,
                "settings": settings
            }
            
        except Exception as e:
            logger.error(f"Failed to load all settings: {e}")
            return {"success": False, "error": str(e)}
    
    def set_settings_manager(self, manager: "SettingsManager") -> None:
        """Set the settings manager.
        
        Args:
            manager: SettingsManager instance
        """
        self._settings_manager = manager

    # ==================== Game State Monitor ====================
    # Feature: ui-refactor-settings
    # Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    
    async def start_monitoring(self) -> Dict[str, Any]:
        """Start game state monitoring for Game Only Mode.
        
        Starts monitoring Steam game launches and exits.
        Invokes callbacks when game state changes are detected.
        
        Returns:
            Dictionary with success status
            
        Feature: ui-refactor-settings
        Validates: Requirements 6.1, 6.4
        """
        if not hasattr(self, '_game_state_monitor'):
            return {"success": False, "error": "Game state monitor not initialized"}
        
        try:
            success = await self._game_state_monitor.start_monitoring()
            
            if success:
                logger.info("Game state monitoring started")
                return {"success": True}
            else:
                return {"success": False, "error": "Failed to start monitoring"}
                
        except Exception as e:
            logger.error(f"Failed to start game state monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop game state monitoring.
        
        Stops monitoring Steam game launches and exits.
        
        Returns:
            Dictionary with success status
            
        Feature: ui-refactor-settings
        Validates: Requirements 6.5
        """
        if not hasattr(self, '_game_state_monitor'):
            return {"success": False, "error": "Game state monitor not initialized"}
        
        try:
            await self._game_state_monitor.stop_monitoring()
            logger.info("Game state monitoring stopped")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to stop game state monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_game_running(self) -> Dict[str, Any]:
        """Check if a game is currently running.
        
        Returns:
            Dictionary with success status and game running state
            
        Feature: ui-refactor-settings
        Validates: Requirements 6.1
        """
        if not hasattr(self, '_game_state_monitor'):
            return {"success": False, "error": "Game state monitor not initialized"}
        
        try:
            is_running = self._game_state_monitor.is_game_running()
            app_id = self._game_state_monitor.get_current_app_id()
            
            return {
                "success": True,
                "is_game_running": is_running,
                "app_id": app_id
            }
            
        except Exception as e:
            logger.error(f"Failed to check game running state: {e}")
            return {"success": False, "error": str(e)}
    
    def set_game_state_monitor(self, monitor: "GameStateMonitor") -> None:
        """Set the game state monitor.
        
        Args:
            monitor: GameStateMonitor instance
        """
        self._game_state_monitor = monitor
    
    # ==================== Game Only Mode ====================
    # Feature: ui-refactor-settings
    # Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    
    async def enable_game_only_mode(self) -> Dict[str, Any]:
        """Enable Game Only Mode.
        
        Starts game state monitoring and configures callbacks for
        automatic profile application on game start and reset on game exit.
        
        Returns:
            Dictionary with success status
            
        Feature: ui-refactor-settings
        Validates: Requirements 5.1, 5.2, 5.5
        """
        if not hasattr(self, '_game_only_mode_controller'):
            return {"success": False, "error": "Game Only Mode controller not initialized"}
        
        try:
            success = await self._game_only_mode_controller.enable()
            
            if success:
                # Save setting
                if hasattr(self, '_settings_manager'):
                    self._settings_manager.save_setting("game_only_mode", True)
                
                logger.info("Game Only Mode enabled")
                return {"success": True}
            else:
                return {"success": False, "error": "Failed to enable Game Only Mode"}
                
        except Exception as e:
            logger.error(f"Failed to enable Game Only Mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def disable_game_only_mode(self) -> Dict[str, Any]:
        """Disable Game Only Mode.
        
        Stops game state monitoring and resets undervolt to default.
        
        Returns:
            Dictionary with success status
            
        Feature: ui-refactor-settings
        Validates: Requirements 5.3, 5.5
        """
        if not hasattr(self, '_game_only_mode_controller'):
            return {"success": False, "error": "Game Only Mode controller not initialized"}
        
        try:
            success = await self._game_only_mode_controller.disable()
            
            if success:
                # Save setting
                if hasattr(self, '_settings_manager'):
                    self._settings_manager.save_setting("game_only_mode", False)
                
                logger.info("Game Only Mode disabled")
                return {"success": True}
            else:
                return {"success": False, "error": "Failed to disable Game Only Mode"}
                
        except Exception as e:
            logger.error(f"Failed to disable Game Only Mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_game_only_mode_status(self) -> Dict[str, Any]:
        """Get current Game Only Mode status.
        
        Returns:
            Dictionary with success status and Game Only Mode state
            
        Feature: ui-refactor-settings
        Validates: Requirements 5.5
        """
        if not hasattr(self, '_game_only_mode_controller'):
            return {"success": False, "error": "Game Only Mode controller not initialized"}
        
        try:
            status = self._game_only_mode_controller.get_status()
            
            return {
                "success": True,
                **status
            }
            
        except Exception as e:
            logger.error(f"Failed to get Game Only Mode status: {e}")
            return {"success": False, "error": str(e)}
    
    def set_game_only_mode_controller(self, controller) -> None:
        """Set the Game Only Mode controller.
        
        Args:
            controller: GameOnlyModeController instance
        """
        self._game_only_mode_controller = controller
    
    # ==================== Wizard Mode ====================
    # Feature: Wizard Mode Refactoring
    
    def set_wizard_session(self, session) -> None:
        """Set the wizard session instance.
        
        Args:
            session: WizardSession instance
        """
        from ..tuning.wizard_session import WizardSession
        self._wizard_session: Optional[WizardSession] = session
        self._wizard_task: Optional[asyncio.Task] = None
    
    async def start_wizard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start wizard session.
        
        Args:
            config: Dictionary containing:
                - target_domains: List of domains to test ["cpu", "gpu", "soc"]
                - aggressiveness: "safe", "balanced", or "aggressive"
                - test_duration: "short" or "long"
                - safety_limits: Dict of domain -> limit (mV)
        
        Returns:
            Dictionary with success status and session_id
        """
        logger.info(f"[RPC] start_wizard called with config: {config}")
        
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            logger.error("[RPC] Wizard not initialized")
            return {"success": False, "error": "Wizard not initialized"}
        
        if self._wizard_session.is_running():
            logger.warning("[RPC] Wizard is already running")
            return {"success": False, "error": "Wizard is already running"}
        
        try:
            from ..tuning.wizard_session import WizardConfig, AggressivenessLevel, TestDuration
            
            logger.info("[RPC] Parsing wizard config...")
            
            # Parse config
            wizard_config = WizardConfig(
                target_domains=config.get("target_domains", ["cpu"]),
                aggressiveness=AggressivenessLevel(config.get("aggressiveness", "balanced")),
                test_duration=TestDuration(config.get("test_duration", "short")),
                safety_limits=config.get("safety_limits", {"cpu": self.platform.safe_limit})
            )
            
            logger.info(f"[RPC] Starting wizard with config: {wizard_config}")
            
            # Start wizard in background task
            self._wizard_task = asyncio.create_task(
                self._wizard_session.start(wizard_config)
            )
            
            logger.info(f"[RPC] Wizard started with session_id: {self._wizard_session._session_id}")
            
            return {
                "success": True,
                "session_id": self._wizard_session._session_id
            }
            
        except ValueError as e:
            logger.error(f"[RPC] Invalid wizard config: {e}", exc_info=True)
            return {"success": False, "error": f"Invalid configuration: {str(e)}"}
        except Exception as e:
            logger.error(f"[RPC] Failed to start wizard: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def cancel_wizard(self) -> Dict[str, Any]:
        """Cancel running wizard session.
        
        Returns:
            Dictionary with success status
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        if not self._wizard_session.is_running():
            return {"success": False, "error": "No wizard running"}
        
        try:
            self._wizard_session.cancel()
            
            # Wait for task to complete cancellation
            if self._wizard_task:
                try:
                    await asyncio.wait_for(self._wizard_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Wizard cancellation timed out")
                except asyncio.CancelledError:
                    pass
            
            logger.info("Wizard cancelled")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to cancel wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_wizard_status(self) -> Dict[str, Any]:
        """Get current wizard status.
        
        Returns:
            Dictionary with running status and state
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"running": False, "state": "idle"}
        
        return {
            "running": self._wizard_session.is_running(),
            "state": self._wizard_session.get_state().value
        }
    
    async def check_wizard_dirty_exit(self) -> Dict[str, Any]:
        """Check for dirty exit from previous wizard session.
        
        Returns:
            Dictionary with dirty_exit flag and crash_info if applicable
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"dirty_exit": False}
        
        try:
            crash_info = self._wizard_session.check_dirty_exit()
            
            if crash_info:
                logger.warning(f"Wizard dirty exit detected: {crash_info}")
                return {
                    "dirty_exit": True,
                    "crash_info": crash_info
                }
            
            return {"dirty_exit": False}
            
        except Exception as e:
            logger.error(f"Failed to check wizard dirty exit: {e}")
            return {"dirty_exit": False, "error": str(e)}
    
    async def get_wizard_results_history(self) -> List[Dict[str, Any]]:
        """Get history of wizard results.
        
        Returns:
            List of wizard result dictionaries
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return []
        
        try:
            from dataclasses import asdict
            results = self._wizard_session.get_results_history()
            return [asdict(r) for r in results]
            
        except Exception as e:
            logger.error(f"Failed to get wizard results history: {e}")
            return []
    
    async def apply_wizard_result(
        self,
        result_id: str,
        save_as_preset: bool = True,
        apply_on_startup: bool = False,
        game_only_mode: bool = False
    ) -> Dict[str, Any]:
        """Apply a wizard result and save as wizard preset with gymdeck3 integration.
        
        CRITICAL FIX #2 & #3: Save as wizard preset with dynamic config and apply options.
        
        Args:
            result_id: UUID of the wizard result to apply
            save_as_preset: Whether to save as a wizard preset
            apply_on_startup: Whether to apply on startup
            game_only_mode: Whether to enable only during games
        
        Returns:
            Dictionary with success status and preset_id if saved
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        try:
            # Find result
            results = self._wizard_session.get_results_history()
            result = next((r for r in results if r.id == result_id), None)
            
            if not result:
                return {"success": False, "error": "Result not found"}
            
            # CRITICAL FIX #1: Use DynamicController if available and dynamic_config exists
            cpu_offset = result.offsets.get("cpu", 0)
            
            if result.dynamic_config and hasattr(self, 'dynamic_controller') and self.dynamic_controller:
                # Start dynamic mode with wizard config
                from ..dynamic.config import DynamicConfig, CoreConfig
                
                dynamic_config = DynamicConfig(
                    strategy=result.dynamic_config.get("strategy", "balanced"),
                    simple_mode=result.dynamic_config.get("simple_mode", True),
                    simple_value=result.dynamic_config.get("simple_value", cpu_offset),
                    cores=[
                        CoreConfig(**core_dict) for core_dict in result.dynamic_config.get("cores", [])
                    ]
                )
                
                success = await self.dynamic_controller.start(dynamic_config)
                if not success:
                    return {"success": False, "error": "Failed to start dynamic mode"}
                
                await self.event_emitter.emit_status("dynamic_running")
                logger.info(f"Started dynamic mode with wizard config: {cpu_offset}mV")
            else:
                # Fallback to static ryzenadj
                values = [cpu_offset, cpu_offset, cpu_offset, cpu_offset]
                success, error = await self.ryzenadj.apply_values_async(values)
                if not success:
                    return {"success": False, "error": error}
                
                await self.event_emitter.emit_status("enabled")
                logger.info(f"Applied static wizard values: {cpu_offset}mV")
            
            # CRITICAL FIX #2: Save as wizard preset with full metadata
            preset_id = None
            if save_as_preset:
                preset_id = self._wizard_session.save_as_wizard_preset(
                    result,
                    apply_on_startup=apply_on_startup,
                    game_only_mode=game_only_mode
                )
                logger.info(f"Saved wizard preset: {preset_id}")
            
            # CRITICAL FIX: Auto-persist apply_on_startup setting to prevent values from resetting on plugin close
            if apply_on_startup and hasattr(self, 'settings_manager') and self.settings_manager:
                self.settings_manager.save_setting("apply_on_startup", True)
                self.settings_manager.save_setting("last_active_profile", preset_id)
                logger.info(f"Enabled apply_on_startup and set last_active_profile to {preset_id}")
            
            return {
                "success": True,
                "preset_id": preset_id,
                "dynamic_enabled": result.dynamic_config is not None,
                "apply_on_startup": apply_on_startup,
                "game_only_mode": game_only_mode
            }
            
        except Exception as e:
            logger.error(f"Failed to apply wizard result: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def run_wizard_benchmark(self, duration: int = 10) -> Dict[str, Any]:
        """Run performance benchmark for wizard mode.
        
        Executes a CPU-intensive benchmark and returns performance metrics.
        
        Args:
            duration: Benchmark duration in seconds (default 10)
            
        Returns:
            Dictionary with score, max_temp, max_freq, and duration
        """
        if not self.test_runner:
            return {"success": False, "error": "Test runner not initialized"}
        
        try:
            logger.info(f"Running wizard benchmark for {duration}s")
            
            # CRITICAL FIX #6: Pass progress callback for real-time updates
            progress_updates = []
            
            def progress_callback(percent: int):
                progress_updates.append(percent)
                # Emit progress event to frontend
                asyncio.create_task(
                    self.event_emitter._emit_event("wizard_benchmark_progress", {
                        "progress": percent,
                        "duration": duration
                    })
                )
            
            result = await self.test_runner.run_benchmark_with_progress(
                duration=duration,
                progress_callback=progress_callback
            )
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            logger.info(f"Benchmark completed: score={result['score']}, "
                       f"max_temp={result['max_temp']}°C")
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    # ==================== CRITICAL FIX #2: Wizard Preset Management ====================
    
    async def get_wizard_presets(self) -> List[Dict[str, Any]]:
        """Get all wizard presets with full metadata.
        
        Returns:
            List of wizard preset dictionaries
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return []
        
        try:
            return self._wizard_session.get_wizard_presets()
        except Exception as e:
            logger.error(f"Failed to get wizard presets: {e}")
            return []
    
    async def get_wizard_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific wizard preset by ID.
        
        Args:
            preset_id: Preset ID
            
        Returns:
            Preset dictionary or None if not found
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return None
        
        try:
            return self._wizard_session.get_wizard_preset(preset_id)
        except Exception as e:
            logger.error(f"Failed to get wizard preset: {e}")
            return None
    
    async def delete_wizard_preset(self, preset_id: str) -> Dict[str, Any]:
        """Delete a wizard preset.
        
        Args:
            preset_id: Preset ID to delete
            
        Returns:
            Dictionary with success status
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        try:
            success = self._wizard_session.delete_wizard_preset(preset_id)
            return {"success": success}
        except Exception as e:
            logger.error(f"Failed to delete wizard preset: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_wizard_preset_options(
        self,
        preset_id: str,
        apply_on_startup: Optional[bool] = None,
        game_only_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update wizard preset options (apply on startup, game only mode).
        
        CRITICAL FIX #3: Enable Apply on Startup and Game Only Mode for wizard presets.
        
        Args:
            preset_id: Preset ID
            apply_on_startup: Whether to apply on startup (None = no change)
            game_only_mode: Whether to enable only during games (None = no change)
            
        Returns:
            Dictionary with success status
        """
        if not hasattr(self, '_wizard_session') or not self._wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        try:
            success = self._wizard_session.update_wizard_preset_options(
                preset_id,
                apply_on_startup=apply_on_startup,
                game_only_mode=game_only_mode
            )
            return {"success": success}
        except Exception as e:
            logger.error(f"Failed to update wizard preset options: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Manual Dynamic Mode ====================
    # Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    
    def set_dynamic_mode_rpc(self, dynamic_rpc: "DynamicModeRPC") -> None:
        """Set the dynamic mode RPC handler.
        
        Args:
            dynamic_rpc: DynamicModeRPC instance
        """
        self.dynamic_mode_rpc = dynamic_rpc
    
    async def get_dynamic_config(self) -> Dict[str, Any]:
        """Get current dynamic mode configuration for all cores.
        
        Returns:
            Dictionary with success status and configuration data
            
        Validates: Requirements 9.1
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.get_dynamic_config()
    
    async def set_dynamic_core_config(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> Dict[str, Any]:
        """Update configuration for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            min_mv: Minimum undervolt value in mV (-100 to 0)
            max_mv: Maximum undervolt value in mV (-100 to 0)
            threshold: Load threshold percentage (0-100)
            
        Returns:
            Dictionary with success status and any validation errors
            
        Validates: Requirements 9.2
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.set_dynamic_core_config(
            core_id, min_mv, max_mv, threshold
        )
    
    async def get_dynamic_curve_data(self, core_id: int) -> Dict[str, Any]:
        """Get voltage curve data for visualization.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            Dictionary with success status and curve points
            
        Validates: Requirements 9.3
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.get_dynamic_curve_data(core_id)
    
    async def start_dynamic_mode(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start dynamic voltage adjustment with the provided configuration.
        
        Args:
            config: Configuration dictionary with mode and cores data
            
        Returns:
            Dictionary with success status
            
        Validates: Requirements 9.5, 5.1
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.start_dynamic_mode(config)
    
    async def stop_dynamic_mode(self) -> Dict[str, Any]:
        """Stop dynamic voltage adjustment.
        
        Returns:
            Dictionary with success status
            
        Validates: Requirements 5.3
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.stop_dynamic_mode()
    
    async def get_core_metrics(self, core_id: int) -> Dict[str, Any]:
        """Get current metrics for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            Dictionary with success status and metrics
            
        Validates: Requirements 9.4
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.get_core_metrics(core_id)
    
    async def set_all_cores_config(
        self,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> Dict[str, Any]:
        """Update configuration for all cores (Simple Mode).
        
        Args:
            min_mv: Minimum undervolt value in mV
            max_mv: Maximum undervolt value in mV
            threshold: Load threshold percentage
            
        Returns:
            Dictionary with success status
            
        Validates: Requirements 4.2, 4.3, 7.1
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.set_all_cores_config(min_mv, max_mv, threshold)
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get platform-specific voltage limits.
        
        Returns:
            Dictionary with success status and limits
            
        Validates: Requirements 7.2, 7.3
        """
        if not hasattr(self, 'dynamic_mode_rpc') or not self.dynamic_mode_rpc:
            return {"success": False, "error": "Dynamic mode not initialized"}
        
        return await self.dynamic_mode_rpc.get_platform_limits()
