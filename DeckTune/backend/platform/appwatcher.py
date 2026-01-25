"""Steam AppID watcher for automatic profile switching.

This module monitors Steam's active application and triggers profile switches
when the user launches different games. It uses multiple detection methods
to reliably identify the currently running game.

Feature: decktune-3.0-automation
Validates: Requirements 4.1, 4.6

# AppID Detection Strategy

The watcher uses multiple methods to detect the active Steam AppID:

1. **Primary Method**: Parse Steam's appmanifest files
   - Location: ~/.steam/steam/steamapps/appmanifest_*.acf
   - Look for "StateFlags" field indicating running state
   
2. **Fallback Method**: Scan /proc for steam processes
   - Look for processes with -applaunch <appid> argument
   - Parse command line from /proc/<pid>/cmdline

# Polling and Debouncing

- Polls every 2 seconds (configurable)
- Debounces app changes: waits 5 seconds before applying profile
- This prevents rapid switching when games are starting/stopping

# Usage Example

```python
from backend.platform.appwatcher import AppWatcher
from backend.dynamic.profile_manager import ProfileManager

# Initialize watcher
watcher = AppWatcher(profile_manager, poll_interval=2.0)

# Start monitoring
await watcher.start()

# Stop monitoring
await watcher.stop()
```
"""

import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from ..dynamic.profile_manager import ProfileManager

logger = logging.getLogger(__name__)


class AppWatcher:
    """Monitors Steam's active application for automatic profile switching.
    
    Polls Steam's state files and process list to detect when the user
    launches or exits games, then triggers profile switches via ProfileManager.
    
    Requirements: 4.1, 4.6
    """
    
    # Default polling interval in seconds
    DEFAULT_POLL_INTERVAL = 2.0
    
    # Debounce delay in seconds (wait before applying profile)
    DEBOUNCE_DELAY = 5.0
    
    # Steam paths
    STEAM_ROOT = Path.home() / ".steam" / "steam"
    STEAMAPPS_DIR = STEAM_ROOT / "steamapps"
    
    def __init__(
        self,
        profile_manager: "ProfileManager",
        poll_interval: float = DEFAULT_POLL_INTERVAL
    ):
        """Initialize the AppWatcher.
        
        Args:
            profile_manager: ProfileManager instance for applying profiles
            poll_interval: How often to check for app changes (seconds)
            
        Requirements: 4.1
        """
        self.profile_manager = profile_manager
        self.poll_interval = poll_interval
        
        # State tracking
        self._running = False
        self._current_app_id: Optional[int] = None
        self._poll_task: Optional[asyncio.Task] = None
        self._last_change_time: Optional[datetime] = None
        
        logger.info(f"AppWatcher initialized with poll_interval={poll_interval}s")
    
    def is_running(self) -> bool:
        """Check if the watcher is currently active.
        
        Returns:
            True if watcher is running, False otherwise
        """
        return self._running
    
    def get_current_app_id(self) -> Optional[int]:
        """Get the currently detected AppID.
        
        Returns:
            Current AppID if a game is running, None otherwise
        """
        return self._current_app_id

    
    # ==================== AppID Detection Methods ====================
    
    def _get_active_app_id(self) -> Optional[int]:
        """Get the currently running Steam AppID.
        
        Tries multiple detection methods in order of preference:
        1. Parse appmanifest files for running games
        2. Scan /proc for steam processes with -applaunch argument
        
        Returns:
            AppID as integer if a game is running, None otherwise
            
        Requirements: 4.1, 4.6
        """
        # Try method 1: Parse appmanifest files
        app_id = self._detect_from_appmanifest()
        if app_id is not None:
            return app_id
        
        # Try method 2: Scan /proc for steam processes
        app_id = self._detect_from_proc()
        if app_id is not None:
            return app_id
        
        # No game detected
        return None
    
    def _detect_from_appmanifest(self) -> Optional[int]:
        """Detect running game from Steam's appmanifest files.
        
        Parses ~/.steam/steam/steamapps/appmanifest_*.acf files to find
        games with StateFlags indicating they are running.
        
        StateFlags values:
        - 4 = Installed
        - 6 = Running (4 + 2)
        
        Returns:
            AppID if a running game is found, None otherwise
        """
        try:
            if not self.STEAMAPPS_DIR.exists():
                logger.debug(f"Steam apps directory not found: {self.STEAMAPPS_DIR}")
                return None
            
            # Find all appmanifest files
            manifest_files = list(self.STEAMAPPS_DIR.glob("appmanifest_*.acf"))
            
            for manifest_file in manifest_files:
                try:
                    # Extract AppID from filename (appmanifest_<appid>.acf)
                    filename = manifest_file.name
                    match = re.match(r"appmanifest_(\d+)\.acf", filename)
                    if not match:
                        continue
                    
                    app_id = int(match.group(1))
                    
                    # Read and parse the manifest file
                    with open(manifest_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Look for StateFlags field
                    # Format: "StateFlags"		"6"
                    state_match = re.search(r'"StateFlags"\s+"(\d+)"', content)
                    if state_match:
                        state_flags = int(state_match.group(1))
                        
                        # Check if game is running (StateFlags & 2 == 2)
                        if state_flags & 2:
                            logger.debug(f"Detected running game from appmanifest: {app_id}")
                            return app_id
                
                except Exception as e:
                    logger.debug(f"Error parsing {manifest_file}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error detecting from appmanifest: {e}")
            return None
    
    def _detect_from_proc(self) -> Optional[int]:
        """Detect running game from /proc filesystem.
        
        Scans /proc for steam processes with -applaunch <appid> argument.
        
        Returns:
            AppID if a steam game process is found, None otherwise
        """
        try:
            # Iterate through /proc directories
            proc_dir = Path("/proc")
            if not proc_dir.exists():
                return None
            
            for pid_dir in proc_dir.iterdir():
                # Skip non-numeric directories
                if not pid_dir.name.isdigit():
                    continue
                
                try:
                    # Read command line
                    cmdline_file = pid_dir / "cmdline"
                    if not cmdline_file.exists():
                        continue
                    
                    with open(cmdline_file, 'rb') as f:
                        cmdline_bytes = f.read()
                    
                    # Command line arguments are null-separated
                    cmdline = cmdline_bytes.decode('utf-8', errors='ignore')
                    args = cmdline.split('\x00')
                    
                    # Look for steam process with -applaunch argument
                    # Example: /path/to/steam -applaunch 1091500
                    if 'steam' in args[0].lower():
                        for i, arg in enumerate(args):
                            if arg == '-applaunch' and i + 1 < len(args):
                                try:
                                    app_id = int(args[i + 1])
                                    logger.debug(f"Detected running game from /proc: {app_id}")
                                    return app_id
                                except ValueError:
                                    continue
                
                except (PermissionError, FileNotFoundError):
                    # Skip processes we can't read
                    continue
                except Exception as e:
                    logger.debug(f"Error reading /proc/{pid_dir.name}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error detecting from /proc: {e}")
            return None

    
    # ==================== Polling Loop ====================
    
    async def _poll_loop(self) -> None:
        """Main polling loop that monitors for app changes.
        
        Polls every poll_interval seconds and detects app changes.
        Implements debouncing to wait DEBOUNCE_DELAY seconds before
        applying a profile after an app change is detected.
        
        Requirements: 4.1
        """
        logger.info("AppWatcher polling loop started")
        
        # Track pending app change for debouncing
        pending_app_id: Optional[int] = None
        pending_since: Optional[datetime] = None
        
        while self._running:
            try:
                # Detect current app
                detected_app_id = self._get_active_app_id()
                
                # Check if app has changed
                if detected_app_id != self._current_app_id:
                    # App change detected
                    logger.info(f"App change detected: {self._current_app_id} -> {detected_app_id}")
                    
                    # Start debounce timer
                    pending_app_id = detected_app_id
                    pending_since = datetime.now(timezone.utc)
                    self._last_change_time = pending_since
                
                # Check if we have a pending change that's ready to apply
                if pending_app_id is not None and pending_since is not None:
                    elapsed = (datetime.now(timezone.utc) - pending_since).total_seconds()
                    
                    if elapsed >= self.DEBOUNCE_DELAY:
                        # Debounce period has elapsed, apply the profile
                        logger.info(f"Debounce period elapsed, applying profile for app_id: {pending_app_id}")
                        
                        # Update current app_id
                        self._current_app_id = pending_app_id
                        
                        # Trigger profile change
                        await self.profile_manager.on_app_change(pending_app_id)
                        
                        # Clear pending change
                        pending_app_id = None
                        pending_since = None
                
                # Sleep until next poll
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                logger.info("AppWatcher polling loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in AppWatcher polling loop: {e}")
                # Continue polling despite errors
                await asyncio.sleep(self.poll_interval)
        
        logger.info("AppWatcher polling loop stopped")

    
    # ==================== Lifecycle Methods ====================
    
    async def start(self) -> None:
        """Start monitoring Steam apps.
        
        Detects the currently running app and applies the appropriate profile,
        then starts the polling loop.
        
        Requirements: 4.6
        """
        if self._running:
            logger.warning("AppWatcher is already running")
            return
        
        logger.info("Starting AppWatcher")
        self._running = True
        
        # Detect current app and apply profile immediately
        try:
            current_app_id = self._get_active_app_id()
            self._current_app_id = current_app_id
            
            if current_app_id is not None:
                logger.info(f"Detected app on startup: {current_app_id}")
                await self.profile_manager.on_app_change(current_app_id)
            else:
                logger.info("No app detected on startup, applying global default")
                await self.profile_manager.on_app_change(None)
        except Exception as e:
            logger.error(f"Error detecting app on startup: {e}")
        
        # Start polling loop
        self._poll_task = asyncio.create_task(self._poll_loop())
        logger.info("AppWatcher started successfully")
    
    async def stop(self) -> None:
        """Stop monitoring Steam apps.
        
        Cancels the polling loop and cleans up resources.
        """
        if not self._running:
            logger.warning("AppWatcher is not running")
            return
        
        logger.info("Stopping AppWatcher")
        self._running = False
        
        # Cancel polling task
        if self._poll_task is not None:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None
        
        logger.info("AppWatcher stopped successfully")
