"""Game State Monitor for Game Only Mode.

This module monitors Steam game launches and exits to enable Game Only Mode,
which applies undervolting only when games are running and resets to default
when returning to the Steam menu.

Feature: ui-refactor-settings
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5

# Game State Detection

The monitor uses the same detection strategy as AppWatcher:
1. Parse Steam's appmanifest files for running games
2. Scan /proc for steam processes with -applaunch argument

# Callbacks

The monitor invokes callbacks when game state changes:
- on_game_start: Called when a game launches
- on_game_exit: Called when a game exits

# Usage Example

```python
from backend.core.game_state_monitor import GameStateMonitor

async def handle_game_start(app_id: int):
    print(f"Game {app_id} started")

async def handle_game_exit():
    print("Game exited")

monitor = GameStateMonitor(
    on_game_start=handle_game_start,
    on_game_exit=handle_game_exit
)

await monitor.start_monitoring()
# ... later ...
await monitor.stop_monitoring()
```
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Callable, Awaitable
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GameStateMonitor:
    """Monitors Steam game state for Game Only Mode.
    
    Polls Steam's state files and process list to detect when games
    launch or exit, then invokes callbacks for profile application.
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    # Default polling interval in seconds
    DEFAULT_POLL_INTERVAL = 2.0
    
    # Steam paths
    STEAM_ROOT = Path.home() / ".steam" / "steam"
    STEAMAPPS_DIR = STEAM_ROOT / "steamapps"
    
    def __init__(
        self,
        on_game_start: Callable[[int], Awaitable[None]],
        on_game_exit: Callable[[], Awaitable[None]],
        poll_interval: float = DEFAULT_POLL_INTERVAL
    ):
        """Initialize the GameStateMonitor.
        
        Args:
            on_game_start: Async callback invoked when a game starts (receives app_id)
            on_game_exit: Async callback invoked when a game exits
            poll_interval: How often to check for state changes (seconds)
            
        Requirements: 6.1
        """
        self.on_game_start = on_game_start
        self.on_game_exit = on_game_exit
        self.poll_interval = poll_interval
        
        # State tracking
        self._running = False
        self._game_running = False
        self._current_app_id: Optional[int] = None
        self._poll_task: Optional[asyncio.Task] = None
        self._subscription_failed = False
        
        logger.info(f"GameStateMonitor initialized with poll_interval={poll_interval}s")
    
    def is_running(self) -> bool:
        """Check if the monitor is currently active.
        
        Returns:
            True if monitor is running, False otherwise
        """
        return self._running
    
    def is_game_running(self) -> bool:
        """Check if a game is currently running.
        
        Returns:
            True if a game is detected, False otherwise
        """
        return self._game_running
    
    def get_current_app_id(self) -> Optional[int]:
        """Get the currently detected AppID.
        
        Returns:
            Current AppID if a game is running, None otherwise
        """
        return self._current_app_id if self._game_running else None
    
    # ==================== Game Detection Methods ====================
    
    def _detect_game(self) -> Optional[int]:
        """Detect if a game is currently running.
        
        Tries multiple detection methods in order of preference:
        1. Parse appmanifest files for running games
        2. Scan /proc for steam processes with -applaunch argument
        
        Returns:
            AppID as integer if a game is running, None otherwise
            
        Requirements: 6.1, 6.2
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
        """Main polling loop that monitors for game state changes.
        
        Polls every poll_interval seconds and detects game launches/exits.
        Invokes callbacks when state changes are detected.
        
        Requirements: 6.2, 6.3
        """
        logger.info("GameStateMonitor polling loop started")
        
        while self._running:
            try:
                # Detect current game
                detected_app_id = self._detect_game()
                
                # Check for state changes
                if detected_app_id is not None and not self._game_running:
                    # Game started
                    logger.info(f"Game started: {detected_app_id}")
                    self._game_running = True
                    self._current_app_id = detected_app_id
                    
                    # Invoke callback
                    try:
                        await self.on_game_start(detected_app_id)
                    except Exception as e:
                        logger.error(f"Error in on_game_start callback: {e}")
                
                elif detected_app_id is None and self._game_running:
                    # Game exited
                    logger.info(f"Game exited: {self._current_app_id}")
                    self._game_running = False
                    self._current_app_id = None
                    
                    # Invoke callback
                    try:
                        await self.on_game_exit()
                    except Exception as e:
                        logger.error(f"Error in on_game_exit callback: {e}")
                
                elif detected_app_id is not None and self._game_running:
                    # Game is still running, update app_id if changed
                    if detected_app_id != self._current_app_id:
                        logger.info(f"Game changed: {self._current_app_id} -> {detected_app_id}")
                        old_app_id = self._current_app_id
                        self._current_app_id = detected_app_id
                        
                        # Treat as exit then start
                        try:
                            await self.on_game_exit()
                            await self.on_game_start(detected_app_id)
                        except Exception as e:
                            logger.error(f"Error in game change callbacks: {e}")
                
                # Sleep until next poll
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                logger.info("GameStateMonitor polling loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in GameStateMonitor polling loop: {e}")
                # Continue polling despite errors
                await asyncio.sleep(self.poll_interval)
        
        logger.info("GameStateMonitor polling loop stopped")
    
    # ==================== Lifecycle Methods ====================
    
    async def start_monitoring(self) -> bool:
        """Start monitoring game state.
        
        Attempts to subscribe to Steam game events (currently uses polling fallback).
        Starts the polling loop to detect game launches and exits.
        
        Returns:
            True if monitoring started successfully, False on failure
            
        Requirements: 6.1, 6.4
        """
        if self._running:
            logger.warning("GameStateMonitor is already running")
            return True
        
        logger.info("Starting GameStateMonitor")
        
        # Note: Steam event subscription is not currently implemented
        # We use polling as the primary mechanism
        # In the future, this could be enhanced with Steam's event system
        
        try:
            self._running = True
            self._subscription_failed = False
            
            # Detect initial game state
            detected_app_id = self._detect_game()
            if detected_app_id is not None:
                logger.info(f"Detected game on startup: {detected_app_id}")
                self._game_running = True
                self._current_app_id = detected_app_id
                # Don't invoke callback on startup, only on transitions
            else:
                logger.info("No game detected on startup")
                self._game_running = False
                self._current_app_id = None
            
            # Start polling loop
            self._poll_task = asyncio.create_task(self._poll_loop())
            logger.info("GameStateMonitor started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start GameStateMonitor: {e}")
            self._running = False
            self._subscription_failed = True
            return False
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring game state.
        
        Cancels the polling loop and cleans up resources.
        
        Requirements: 6.5
        """
        if not self._running:
            logger.warning("GameStateMonitor is not running")
            return
        
        logger.info("Stopping GameStateMonitor")
        self._running = False
        
        # Cancel polling task
        if self._poll_task is not None:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None
        
        # Reset state
        self._game_running = False
        self._current_app_id = None
        
        logger.info("GameStateMonitor stopped successfully")
