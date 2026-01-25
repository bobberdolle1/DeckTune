"""Game Only Mode Controller.

Feature: ui-refactor-settings
Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5

This module implements Game Only Mode logic that applies undervolting
only when games are running and resets to default when returning to
the Steam menu.
"""

import asyncio
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state_monitor import GameStateMonitor
    from .ryzenadj import RyzenadjWrapper
    from .settings_manager import SettingsManager
    from ..api.events import EventEmitter

logger = logging.getLogger(__name__)


class GameOnlyModeController:
    """Controls Game Only Mode behavior.
    
    Manages the lifecycle of Game Only Mode, coordinating between
    the game state monitor and undervolt application/reset.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    def __init__(
        self,
        game_state_monitor: "GameStateMonitor",
        ryzenadj: "RyzenadjWrapper",
        settings_manager: "SettingsManager",
        event_emitter: "EventEmitter"
    ):
        """Initialize the Game Only Mode controller.
        
        Args:
            game_state_monitor: GameStateMonitor instance for detecting game state
            ryzenadj: RyzenadjWrapper for applying/resetting undervolt
            settings_manager: SettingsManager for accessing saved profile
            event_emitter: EventEmitter for status updates
        """
        self.monitor = game_state_monitor
        self.ryzenadj = ryzenadj
        self.settings = settings_manager
        self.event_emitter = event_emitter
        
        self._enabled = False
        self._last_profile = None
        
        logger.info("GameOnlyModeController initialized")
    
    def is_enabled(self) -> bool:
        """Check if Game Only Mode is currently enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self._enabled
    
    async def enable(self) -> bool:
        """Enable Game Only Mode.
        
        Starts game state monitoring and sets up callbacks for
        profile application on game start and reset on game exit.
        
        Returns:
            True if enabled successfully, False otherwise
            
        Requirements: 5.5, 6.1
        """
        if self._enabled:
            logger.warning("Game Only Mode is already enabled")
            return True
        
        logger.info("Enabling Game Only Mode")
        
        try:
            # Start game state monitoring
            success = await self.monitor.start_monitoring()
            
            if not success:
                logger.error("Failed to start game state monitoring")
                return False
            
            self._enabled = True
            logger.info("Game Only Mode enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable Game Only Mode: {e}")
            return False
    
    async def disable(self) -> bool:
        """Disable Game Only Mode.
        
        Stops game state monitoring and resets undervolt to default.
        
        Returns:
            True if disabled successfully, False otherwise
            
        Requirements: 5.3, 6.5
        """
        if not self._enabled:
            logger.warning("Game Only Mode is not enabled")
            return True
        
        logger.info("Disabling Game Only Mode")
        
        try:
            # Stop game state monitoring
            await self.monitor.stop_monitoring()
            
            # Reset undervolt to default (Requirement 5.3)
            await self._reset_undervolt()
            
            self._enabled = False
            self._last_profile = None
            logger.info("Game Only Mode disabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable Game Only Mode: {e}")
            return False
    
    async def on_game_start(self, app_id: int) -> None:
        """Handle game start event.
        
        Applies the saved undervolt profile when a game starts.
        Implements 2-second timeout requirement.
        
        Args:
            app_id: Steam AppID of the game that started
            
        Requirements: 5.1, 5.4
        """
        if not self._enabled:
            return
        
        logger.info(f"Game started (app_id: {app_id}), applying profile")
        
        try:
            # Create task with 2-second timeout (Requirement 5.4)
            await asyncio.wait_for(
                self._apply_profile(),
                timeout=2.0
            )
            
        except asyncio.TimeoutError:
            logger.error("Profile application timed out after 2 seconds")
            await self.event_emitter.emit_status("error")
        except Exception as e:
            logger.error(f"Error applying profile on game start: {e}")
            await self.event_emitter.emit_status("error")
    
    async def on_game_exit(self) -> None:
        """Handle game exit event.
        
        Resets undervolt to default (0) when a game exits.
        Implements 2-second timeout requirement.
        
        Requirements: 5.2, 5.4
        """
        if not self._enabled:
            return
        
        logger.info("Game exited, resetting undervolt to default")
        
        try:
            # Create task with 2-second timeout (Requirement 5.4)
            await asyncio.wait_for(
                self._reset_undervolt(),
                timeout=2.0
            )
            
        except asyncio.TimeoutError:
            logger.error("Undervolt reset timed out after 2 seconds")
            await self.event_emitter.emit_status("error")
        except Exception as e:
            logger.error(f"Error resetting undervolt on game exit: {e}")
            await self.event_emitter.emit_status("error")
    
    async def _apply_profile(self) -> None:
        """Apply the saved undervolt profile.
        
        Loads the last active profile from settings and applies it.
        Handles errors gracefully.
        
        Requirements: 5.1
        """
        try:
            # Get last active profile from settings
            last_profile = self.settings.get_setting("cores")
            
            if not last_profile or last_profile == [0, 0, 0, 0]:
                logger.info("No active profile to apply, skipping")
                return
            
            # Apply the profile
            logger.debug(f"Applying profile: {last_profile}")
            success, error = await self.ryzenadj.apply_values_async(last_profile)
            
            if success:
                self._last_profile = last_profile
                await self.event_emitter.emit_status("enabled")
                logger.info(f"Profile applied successfully: {last_profile}")
            else:
                logger.error(f"Failed to apply profile: {error}")
                await self.event_emitter.emit_status("error")
                
        except Exception as e:
            logger.error(f"Error in _apply_profile: {e}")
            raise
    
    async def _reset_undervolt(self) -> None:
        """Reset undervolt to default (all cores to 0).
        
        Handles errors gracefully.
        
        Requirements: 5.2
        """
        try:
            logger.debug("Resetting undervolt to default [0, 0, 0, 0]")
            success, error = await self.ryzenadj.disable_async()
            
            if success:
                self._last_profile = None
                await self.event_emitter.emit_status("disabled")
                logger.info("Undervolt reset to default successfully")
            else:
                logger.error(f"Failed to reset undervolt: {error}")
                await self.event_emitter.emit_status("error")
                
        except Exception as e:
            logger.error(f"Error in _reset_undervolt: {e}")
            raise
    
    def get_status(self) -> dict:
        """Get current Game Only Mode status.
        
        Returns:
            Dictionary with enabled status and last applied profile
        """
        return {
            "enabled": self._enabled,
            "monitoring": self.monitor.is_running() if self.monitor else False,
            "game_running": self.monitor.is_game_running() if self.monitor else False,
            "last_profile": self._last_profile
        }
