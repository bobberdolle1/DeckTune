"""Update manager for DeckTune plugin.

Handles checking for updates from GitHub releases and installing them.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


class UpdateManager:
    """Manages plugin updates from GitHub releases."""
    
    GITHUB_API_URL = "https://api.github.com/repos/bobberdolle1/DeckTune/releases/latest"
    GITHUB_RELEASE_URL = "https://github.com/bobberdolle1/DeckTune/releases/download/{tag}/DeckTune-{tag}.zip"
    
    def __init__(self, plugin_dir: str, current_version: str, event_emitter=None):
        """Initialize update manager.
        
        Args:
            plugin_dir: Path to plugin directory
            current_version: Current plugin version (e.g., "3.3.4")
            event_emitter: Optional event emitter for progress updates
        """
        self.plugin_dir = Path(plugin_dir)
        self.current_version = current_version
        self.event_emitter = event_emitter
        self._update_task: Optional[asyncio.Task] = None
        self._update_progress = {
            "stage": "idle",
            "progress": 0,
            "message": "",
            "eta_seconds": 0
        }
    
    def _parse_version(self, version: str) -> tuple:
        """Parse version string to tuple for comparison.
        
        Args:
            version: Version string (e.g., "v3.3.4" or "3.3.4")
            
        Returns:
            Tuple of integers (major, minor, patch)
        """
        # Remove 'v' prefix if present
        version = version.lstrip('v')
        
        try:
            parts = version.split('.')
            return tuple(int(p) for p in parts[:3])
        except (ValueError, IndexError):
            logger.warning(f"Failed to parse version: {version}")
            return (0, 0, 0)
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check for available updates from GitHub.
        
        Returns:
            Dictionary with:
                - success: bool
                - update_available: bool
                - current_version: str
                - latest_version: str (if available)
                - release_notes: str (if available)
                - download_url: str (if available)
                - error: str (if failed)
        """
        try:
            # Fetch latest release info from GitHub API
            request = Request(
                self.GITHUB_API_URL,
                headers={'User-Agent': 'DeckTune-Plugin'}
            )
            
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            latest_tag = data.get('tag_name', '')
            latest_version = latest_tag.lstrip('v')
            release_notes = data.get('body', 'No release notes available.')
            
            # Compare versions
            current_tuple = self._parse_version(self.current_version)
            latest_tuple = self._parse_version(latest_version)
            
            update_available = latest_tuple > current_tuple
            
            # Construct download URL
            download_url = self.GITHUB_RELEASE_URL.format(tag=latest_tag)
            
            logger.info(
                f"Update check: current={self.current_version}, "
                f"latest={latest_version}, available={update_available}"
            )
            
            return {
                "success": True,
                "update_available": update_available,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "release_notes": release_notes,
                "download_url": download_url
            }
            
        except HTTPError as e:
            logger.error(f"HTTP error checking for updates: {e.code} {e.reason}")
            return {
                "success": False,
                "error": f"HTTP error: {e.code} {e.reason}",
                "current_version": self.current_version
            }
        except URLError as e:
            logger.error(f"Network error checking for updates: {e.reason}")
            return {
                "success": False,
                "error": f"Network error: {e.reason}",
                "current_version": self.current_version
            }
        except Exception as e:
            logger.error(f"Error checking for updates: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "current_version": self.current_version
            }
    
    async def _emit_progress(self, stage: str, progress: int, message: str, eta_seconds: int = 0):
        """Emit progress update event.
        
        Args:
            stage: Current stage (downloading, extracting, installing, complete)
            progress: Progress percentage (0-100)
            message: Status message
            eta_seconds: Estimated time remaining in seconds
        """
        self._update_progress = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "eta_seconds": eta_seconds
        }
        
        if self.event_emitter:
            await self.event_emitter.emit("update_progress", self._update_progress)
    
    async def install_update(self, download_url: str) -> Dict[str, Any]:
        """Download and install update.
        
        Args:
            download_url: URL to download the update zip file
            
        Returns:
            Dictionary with:
                - success: bool
                - message: str
                - error: str (if failed)
        """
        if self._update_task and not self._update_task.done():
            return {
                "success": False,
                "error": "Update already in progress"
            }
        
        # Reset progress
        await self._emit_progress("starting", 0, "Initializing update...")
        
        # Run update in background task
        self._update_task = asyncio.create_task(
            self._install_update_async(download_url)
        )
        
        return {
            "success": True,
            "message": "Update started in background"
        }
    
    async def _install_update_async(self, download_url: str) -> None:
        """Async task to download and install update.
        
        Args:
            download_url: URL to download the update zip file
        """
        temp_dir = None
        
        try:
            logger.info(f"Starting update download from: {download_url}")
            await self._emit_progress("downloading", 5, "Starting download...")
            
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="decktune_update_"))
            zip_path = temp_dir / "update.zip"
            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()
            
            # Download update zip with progress tracking
            request = Request(
                download_url,
                headers={'User-Agent': 'DeckTune-Plugin'}
            )
            
            await self._emit_progress("downloading", 10, "Downloading update...")
            
            with urlopen(request, timeout=120) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(zip_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = 10 + int((downloaded / total_size) * 30)
                            await self._emit_progress(
                                "downloading",
                                progress,
                                f"Downloaded {downloaded // 1024} KB / {total_size // 1024} KB"
                            )
            
            logger.info(f"Downloaded update to: {zip_path}")
            await self._emit_progress("extracting", 45, "Extracting files...")
            
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted update to: {extract_dir}")
            await self._emit_progress("extracting", 55, "Files extracted")
            
            # Find the plugin directory in extracted files
            # Structure should be: extracted/DeckTune/...
            plugin_content_dir = extract_dir / "DeckTune"
            
            if not plugin_content_dir.exists():
                # Try to find any directory
                subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
                if subdirs:
                    plugin_content_dir = subdirs[0]
                else:
                    raise Exception("Could not find plugin content in update archive")
            
            logger.info(f"Plugin content directory: {plugin_content_dir}")
            await self._emit_progress("installing", 60, "Creating backup...")
            
            # Backup current plugin (optional, for safety)
            backup_dir = self.plugin_dir.parent / f"DeckTune_backup_{self.current_version}"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            logger.info(f"Creating backup at: {backup_dir}")
            shutil.copytree(self.plugin_dir, backup_dir)
            
            await self._emit_progress("installing", 70, "Installing files...")
            
            # Copy new files over existing plugin directory
            # We need to preserve settings and user data
            logger.info("Installing update files...")
            
            total_items = len(list(plugin_content_dir.iterdir()))
            processed = 0
            
            for item in plugin_content_dir.iterdir():
                dest = self.plugin_dir / item.name
                
                # Skip settings directory to preserve user data
                if item.name in ['.kiro', 'settings']:
                    logger.info(f"Skipping user data: {item.name}")
                    processed += 1
                    continue
                
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    if dest.exists():
                        dest.unlink()
                    shutil.copy2(item, dest)
                
                processed += 1
                progress = 70 + int((processed / total_items) * 20)
                await self._emit_progress("installing", progress, f"Installing {item.name}...")
            
            logger.info("Update installed successfully")
            await self._emit_progress("finalizing", 92, "Setting permissions...")
            
            # Set executable permissions on binaries
            bin_dir = self.plugin_dir / "bin"
            if bin_dir.exists():
                for binary in bin_dir.iterdir():
                    if binary.is_file():
                        os.chmod(binary, 0o755)
                        logger.info(f"Set executable permission: {binary}")
            
            await self._emit_progress("complete", 95, "Update complete, reloading plugin...")
            logger.info("Update completed successfully - reloading plugin")
            
            # Wait a moment for UI to show completion
            await asyncio.sleep(2)
            
            # Trigger plugin reload via systemctl
            try:
                subprocess.run(
                    ["systemctl", "restart", "plugin_loader"],
                    timeout=5,
                    check=False
                )
                logger.info("Plugin reload triggered")
            except Exception as e:
                logger.warning(f"Could not trigger plugin reload: {e}")
            
            await self._emit_progress("complete", 100, "Plugin reloading...")
            
        except Exception as e:
            logger.error(f"Failed to install update: {e}", exc_info=True)
            await self._emit_progress("error", 0, f"Update failed: {str(e)}")
            
        finally:
            # Cleanup temporary directory
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary files")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def is_update_in_progress(self) -> bool:
        """Check if update is currently in progress.
        
        Returns:
            True if update task is running
        """
        return self._update_task is not None and not self._update_task.done()
    
    async def get_update_status(self) -> Dict[str, Any]:
        """Get current update status.
        
        Returns:
            Dictionary with:
                - in_progress: bool
                - stage: str
                - progress: int (0-100)
                - message: str
                - eta_seconds: int
        """
        in_progress = self.is_update_in_progress()
        
        return {
            "in_progress": in_progress,
            "stage": self._update_progress["stage"],
            "progress": self._update_progress["progress"],
            "message": self._update_progress["message"],
            "eta_seconds": self._update_progress["eta_seconds"]
        }
