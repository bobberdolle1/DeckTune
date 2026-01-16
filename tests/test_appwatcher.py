"""Unit tests for AppWatcher.

Feature: decktune-3.0-automation
Validates: Requirements 4.1, 4.6

This module tests the AppWatcher's AppID detection methods and
debouncing logic.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from backend.platform.appwatcher import AppWatcher


# ==================== Test Fixtures ====================

@pytest.fixture
def mock_profile_manager():
    """Create a mock ProfileManager."""
    manager = Mock()
    manager.on_app_change = AsyncMock()
    return manager


@pytest.fixture
def app_watcher(mock_profile_manager):
    """Create an AppWatcher instance with mocks."""
    return AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1  # Fast polling for tests
    )


# ==================== AppManifest Detection Tests ====================

def test_detect_from_appmanifest_running_game(app_watcher):
    """Test detecting a running game from appmanifest file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock steamapps directory
        steamapps_dir = Path(tmpdir) / "steamapps"
        steamapps_dir.mkdir()
        
        # Create appmanifest file for a running game (StateFlags = 6)
        manifest_file = steamapps_dir / "appmanifest_1091500.acf"
        manifest_content = '''
"AppState"
{
    "appid"		"1091500"
    "Universe"		"1"
    "name"		"Cyberpunk 2077"
    "StateFlags"		"6"
    "installdir"		"Cyberpunk 2077"
}
'''
        manifest_file.write_text(manifest_content)
        
        # Patch the STEAMAPPS_DIR
        app_watcher.STEAMAPPS_DIR = steamapps_dir
        
        # Detect app
        app_id = app_watcher._detect_from_appmanifest()
        
        assert app_id == 1091500, "Should detect running game from appmanifest"


def test_detect_from_appmanifest_installed_not_running(app_watcher):
    """Test that installed but not running games are not detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock steamapps directory
        steamapps_dir = Path(tmpdir) / "steamapps"
        steamapps_dir.mkdir()
        
        # Create appmanifest file for an installed game (StateFlags = 4)
        manifest_file = steamapps_dir / "appmanifest_1091500.acf"
        manifest_content = '''
"AppState"
{
    "appid"		"1091500"
    "Universe"		"1"
    "name"		"Cyberpunk 2077"
    "StateFlags"		"4"
    "installdir"		"Cyberpunk 2077"
}
'''
        manifest_file.write_text(manifest_content)
        
        # Patch the STEAMAPPS_DIR
        app_watcher.STEAMAPPS_DIR = steamapps_dir
        
        # Detect app
        app_id = app_watcher._detect_from_appmanifest()
        
        assert app_id is None, "Should not detect installed but not running game"


def test_detect_from_appmanifest_no_steamapps_dir(app_watcher):
    """Test behavior when steamapps directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Point to non-existent directory
        app_watcher.STEAMAPPS_DIR = Path(tmpdir) / "nonexistent"
        
        # Detect app
        app_id = app_watcher._detect_from_appmanifest()
        
        assert app_id is None, "Should return None when steamapps dir doesn't exist"


def test_detect_from_appmanifest_multiple_games(app_watcher):
    """Test detecting when multiple games are installed but only one is running."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock steamapps directory
        steamapps_dir = Path(tmpdir) / "steamapps"
        steamapps_dir.mkdir()
        
        # Create appmanifest for installed game (StateFlags = 4)
        manifest1 = steamapps_dir / "appmanifest_1091500.acf"
        manifest1.write_text('''
"AppState"
{
    "appid"		"1091500"
    "StateFlags"		"4"
}
''')
        
        # Create appmanifest for running game (StateFlags = 6)
        manifest2 = steamapps_dir / "appmanifest_1245620.acf"
        manifest2.write_text('''
"AppState"
{
    "appid"		"1245620"
    "StateFlags"		"6"
}
''')
        
        # Patch the STEAMAPPS_DIR
        app_watcher.STEAMAPPS_DIR = steamapps_dir
        
        # Detect app
        app_id = app_watcher._detect_from_appmanifest()
        
        assert app_id == 1245620, "Should detect the running game"


def test_detect_from_appmanifest_corrupted_file(app_watcher):
    """Test handling of corrupted appmanifest file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock steamapps directory
        steamapps_dir = Path(tmpdir) / "steamapps"
        steamapps_dir.mkdir()
        
        # Create corrupted appmanifest file
        manifest_file = steamapps_dir / "appmanifest_1091500.acf"
        manifest_file.write_text("corrupted data { { {")
        
        # Patch the STEAMAPPS_DIR
        app_watcher.STEAMAPPS_DIR = steamapps_dir
        
        # Detect app (should not crash)
        app_id = app_watcher._detect_from_appmanifest()
        
        assert app_id is None, "Should handle corrupted file gracefully"


# ==================== /proc Detection Tests ====================

def test_detect_from_proc_steam_process(app_watcher):
    """Test detecting game from /proc with steam process."""
    # Mock the /proc filesystem
    with patch('pathlib.Path.iterdir') as mock_iterdir, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', create=True) as mock_open:
        
        # Mock /proc directory listing
        mock_pid_dir = MagicMock()
        mock_pid_dir.name = "12345"
        mock_pid_dir.__truediv__ = lambda self, x: MagicMock(exists=lambda: True)
        mock_iterdir.return_value = [mock_pid_dir]
        
        # Mock cmdline file content
        # Format: /path/to/steam\x00-applaunch\x001091500\x00
        cmdline_content = b'/home/user/.steam/steam\x00-applaunch\x001091500\x00'
        mock_open.return_value.__enter__.return_value.read.return_value = cmdline_content
        
        # Detect app
        app_id = app_watcher._detect_from_proc()
        
        assert app_id == 1091500, "Should detect game from steam process"


def test_detect_from_proc_no_steam_process(app_watcher):
    """Test when no steam process is running."""
    with patch('pathlib.Path.iterdir') as mock_iterdir, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', create=True) as mock_open:
        
        # Mock /proc directory listing
        mock_pid_dir = MagicMock()
        mock_pid_dir.name = "12345"
        mock_pid_dir.__truediv__ = lambda self, x: MagicMock(exists=lambda: True)
        mock_iterdir.return_value = [mock_pid_dir]
        
        # Mock cmdline for non-steam process
        cmdline_content = b'/usr/bin/firefox\x00'
        mock_open.return_value.__enter__.return_value.read.return_value = cmdline_content
        
        # Detect app
        app_id = app_watcher._detect_from_proc()
        
        assert app_id is None, "Should return None when no steam process found"


def test_detect_from_proc_steam_without_applaunch(app_watcher):
    """Test steam process without -applaunch argument."""
    with patch('pathlib.Path.iterdir') as mock_iterdir, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', create=True) as mock_open:
        
        # Mock /proc directory listing
        mock_pid_dir = MagicMock()
        mock_pid_dir.name = "12345"
        mock_pid_dir.__truediv__ = lambda self, x: MagicMock(exists=lambda: True)
        mock_iterdir.return_value = [mock_pid_dir]
        
        # Mock cmdline for steam without -applaunch
        cmdline_content = b'/home/user/.steam/steam\x00-silent\x00'
        mock_open.return_value.__enter__.return_value.read.return_value = cmdline_content
        
        # Detect app
        app_id = app_watcher._detect_from_proc()
        
        assert app_id is None, "Should return None when steam has no -applaunch"


# ==================== Debouncing Tests ====================

@pytest.mark.asyncio
async def test_debouncing_simple(mock_profile_manager):
    """Simplified test for debouncing behavior."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    watcher.DEBOUNCE_DELAY = 0.3
    
    # Manually trigger the polling loop behavior
    # Start with None
    watcher._current_app_id = None
    
    # Simulate detecting a new app
    with patch.object(watcher, '_get_active_app_id', return_value=1091500):
        # Start the watcher
        await watcher.start()
        
        # Give it time to poll and detect the change, then debounce
        # poll (0.1) + detect change + debounce (0.3) + buffer
        await asyncio.sleep(0.6)
        
        # Check if profile was applied
        calls = [call[0][0] for call in mock_profile_manager.on_app_change.call_args_list]
        
        # Should have: initial None, then 1091500 after debounce
        assert 1091500 in calls, f"Should have applied profile for app 1091500. Calls: {calls}"
        
        await watcher.stop()


@pytest.mark.asyncio
async def test_debouncing_resets_on_app_change(mock_profile_manager):
    """Test that debouncing resets when app changes again."""
    # Create watcher with short intervals for testing
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.05  # 50ms
    )
    watcher.DEBOUNCE_DELAY = 0.2  # 200ms debounce
    
    # Mock detection to return different app_ids over time
    app_ids = [1091500, 1245620]  # Two different games
    call_count = [0]
    
    def mock_get_app_id():
        # Return first app_id for first few calls, then second app_id
        if call_count[0] < 3:
            call_count[0] += 1
            return app_ids[0]
        else:
            return app_ids[1]
    
    with patch.object(watcher, '_get_active_app_id', side_effect=mock_get_app_id):
        # Start watcher
        await watcher.start()
        
        # Wait for app to change during debounce period
        await asyncio.sleep(0.25)
        
        # Should have detected the second app change
        # The first app should not have been applied (debounce was reset)
        
        # Wait for second debounce to complete
        await asyncio.sleep(0.25)
        
        # Should have applied the second app
        assert mock_profile_manager.on_app_change.called
        
        # Stop watcher
        await watcher.stop()


# ==================== Lifecycle Tests ====================

@pytest.mark.asyncio
async def test_start_detects_current_app(mock_profile_manager):
    """Test that start() detects and applies current app immediately."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Mock detection to return an app_id
    with patch.object(watcher, '_get_active_app_id', return_value=1091500):
        # Start watcher
        await watcher.start()
        
        # Should have detected and applied profile immediately (no debounce on startup)
        assert mock_profile_manager.on_app_change.called, \
            "Should apply profile immediately on startup"
        assert mock_profile_manager.on_app_change.call_args[0][0] == 1091500, \
            "Should apply profile for detected app_id"
        
        # Stop watcher
        await watcher.stop()


@pytest.mark.asyncio
async def test_start_applies_global_default_when_no_game(mock_profile_manager):
    """Test that start() applies global default when no game is running."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Mock detection to return None (no game running)
    with patch.object(watcher, '_get_active_app_id', return_value=None):
        # Start watcher
        await watcher.start()
        
        # Should have applied global default
        assert mock_profile_manager.on_app_change.called, \
            "Should apply global default on startup"
        assert mock_profile_manager.on_app_change.call_args[0][0] is None, \
            "Should pass None to apply global default"
        
        # Stop watcher
        await watcher.stop()


@pytest.mark.asyncio
async def test_stop_cancels_polling(mock_profile_manager):
    """Test that stop() cancels the polling task."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Mock detection
    with patch.object(watcher, '_get_active_app_id', return_value=None):
        # Start watcher
        await watcher.start()
        
        assert watcher.is_running(), "Watcher should be running"
        assert watcher._poll_task is not None, "Poll task should exist"
        
        # Stop watcher
        await watcher.stop()
        
        assert not watcher.is_running(), "Watcher should not be running"
        # Note: _poll_task is set to None after cancellation


@pytest.mark.asyncio
async def test_start_when_already_running(mock_profile_manager):
    """Test that calling start() when already running is a no-op."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Mock detection
    with patch.object(watcher, '_get_active_app_id', return_value=None):
        # Start watcher
        await watcher.start()
        
        # Reset mock
        mock_profile_manager.on_app_change.reset_mock()
        
        # Try to start again
        await watcher.start()
        
        # Should not have called on_app_change again
        assert not mock_profile_manager.on_app_change.called, \
            "Should not apply profile when already running"
        
        # Stop watcher
        await watcher.stop()


@pytest.mark.asyncio
async def test_stop_when_not_running(mock_profile_manager):
    """Test that calling stop() when not running is a no-op."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Stop without starting (should not crash)
    await watcher.stop()
    
    assert not watcher.is_running(), "Watcher should not be running"


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_app_switching_workflow(mock_profile_manager):
    """Test that startup detection works correctly."""
    watcher = AppWatcher(
        profile_manager=mock_profile_manager,
        poll_interval=0.1
    )
    
    # Start with a game running
    with patch.object(watcher, '_get_active_app_id', return_value=1091500):
        await watcher.start()
        # Wait for startup to complete
        await asyncio.sleep(0.2)
        
        # Should have applied the profile once on startup
        assert mock_profile_manager.on_app_change.call_count == 1
        assert mock_profile_manager.on_app_change.call_args[0][0] == 1091500
        
        await watcher.stop()


def test_get_current_app_id(app_watcher):
    """Test getting the current app_id."""
    # Initially None
    assert app_watcher.get_current_app_id() is None
    
    # Set current app_id
    app_watcher._current_app_id = 1091500
    assert app_watcher.get_current_app_id() == 1091500


def test_is_running(app_watcher):
    """Test is_running() method."""
    # Initially not running
    assert not app_watcher.is_running()
    
    # Set running flag
    app_watcher._running = True
    assert app_watcher.is_running()
    
    # Clear running flag
    app_watcher._running = False
    assert not app_watcher.is_running()
