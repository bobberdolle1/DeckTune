"""RPC handlers for Decky frontend communication.

Feature: decktune, API and Events Module
Validates: All RPC endpoints

This module provides the RPC interface for frontend communication,
including platform info, undervolt control, autotune, tests, presets,
and diagnostics methods.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ryzenadj import RyzenadjWrapper
    from ..core.safety import SafetyManager
    from ..platform.detect import PlatformInfo
    from ..tuning.autotune import AutotuneEngine, AutotuneConfig
    from ..tuning.runner import TestRunner
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
        test_runner: Optional["TestRunner"] = None
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
        """
        self.platform = platform
        self.ryzenadj = ryzenadj
        self.safety = safety
        self.event_emitter = event_emitter
        self.settings = settings_manager
        self.autotune_engine = autotune_engine
        self.test_runner = test_runner
        
        self._delay_task: Optional[asyncio.Task] = None
        self._autotune_task: Optional[asyncio.Task] = None
    
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
    
    # ==================== Tests ====================
    
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
