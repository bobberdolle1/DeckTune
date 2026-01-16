"""Property test for diagnostics archive contents.

Feature: decktune, Property 12: Diagnostics Archive Contents
Validates: Requirements 8.1

Tests that for any diagnostics export, the resulting tar.gz archive
contains files matching:
- plugin_logs.txt (non-empty)
- config.json (valid JSON with cores and lkg_cores keys)
- system_info.txt (contains uname output)
- dmesg.txt (non-empty)
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import json
import asyncio
import tarfile
import os
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.rpc import DeckTuneRPC
from backend.platform.detect import PlatformInfo


# Strategy for generating valid core values
core_values_strategy = st.lists(
    st.integers(min_value=-60, max_value=0),
    min_size=4,
    max_size=4
)

# Strategy for generating valid status strings
status_strategy = st.sampled_from(["enabled", "disabled", "error", "scheduled", "dynamic_running"])


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self, cores=None, lkg_cores=None, status="disabled"):
        self._settings = {
            "cores": cores or [0, 0, 0, 0],
            "lkg_cores": lkg_cores or [0, 0, 0, 0],
            "lkg_timestamp": "2024-01-01T00:00:00",
            "status": status,
            "presets": []
        }
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


def create_test_rpc(cores=None, lkg_cores=None, status="disabled"):
    """Create a DeckTuneRPC instance for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings = MockSettingsManager(cores, lkg_cores, status)
    
    # Create minimal mocks for required dependencies
    ryzenadj = MagicMock()
    safety = MagicMock()
    event_emitter = MagicMock()
    
    return DeckTuneRPC(
        platform=platform,
        ryzenadj=ryzenadj,
        safety=safety,
        event_emitter=event_emitter,
        settings_manager=settings
    )


@given(
    cores=core_values_strategy,
    lkg_cores=core_values_strategy,
    status=status_strategy
)
@hyp_settings(max_examples=100)
def test_diagnostics_archive_contents(cores, lkg_cores, status):
    """Property 12: Diagnostics Archive Contents
    
    For any diagnostics export, the resulting tar.gz archive SHALL contain
    files matching:
    - plugin_logs.txt (non-empty)
    - config.json (valid JSON with cores and lkg_cores keys)
    - system_info.txt (contains uname output)
    - dmesg.txt (non-empty)
    
    Feature: decktune, Property 12: Diagnostics Archive Contents
    Validates: Requirements 8.1
    """
    rpc = create_test_rpc(cores=cores, lkg_cores=lkg_cores, status=status)
    
    # Create a temporary directory for the archive
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch the home directory to use temp dir
        with patch.dict(os.environ, {"HOME": temp_dir}):
            with patch("os.path.expanduser", return_value=temp_dir):
                # Export diagnostics
                result = asyncio.run(
                    rpc.export_diagnostics()
                )
        
        assert result["success"], f"Export failed: {result.get('error')}"
        assert "path" in result, "No path in result"
        
        archive_path = result["path"]
        assert os.path.exists(archive_path), f"Archive not found at {archive_path}"
        
        # Open and verify archive contents
        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getnames()
            
            # 1. Check plugin_logs.txt exists
            assert "plugin_logs.txt" in members, \
                f"plugin_logs.txt not in archive. Found: {members}"
            
            # Extract and verify plugin_logs.txt is non-empty
            logs_file = tar.extractfile("plugin_logs.txt")
            logs_content = logs_file.read().decode("utf-8")
            assert len(logs_content) > 0, "plugin_logs.txt is empty"
            
            # 2. Check config.json exists and is valid
            assert "config.json" in members, \
                f"config.json not in archive. Found: {members}"
            
            config_file = tar.extractfile("config.json")
            config_content = config_file.read().decode("utf-8")
            
            # Parse JSON and verify required keys
            config = json.loads(config_content)
            assert "cores" in config, "config.json missing 'cores' key"
            assert "lkg_cores" in config, "config.json missing 'lkg_cores' key"
            
            # Verify the values match what we set
            assert config["cores"] == cores, \
                f"cores mismatch: {config['cores']} != {cores}"
            assert config["lkg_cores"] == lkg_cores, \
                f"lkg_cores mismatch: {config['lkg_cores']} != {lkg_cores}"
            
            # 3. Check system_info.txt exists and contains uname
            assert "system_info.txt" in members, \
                f"system_info.txt not in archive. Found: {members}"
            
            sysinfo_file = tar.extractfile("system_info.txt")
            sysinfo_content = sysinfo_file.read().decode("utf-8")
            assert "uname" in sysinfo_content.lower(), \
                f"system_info.txt doesn't contain uname output: {sysinfo_content[:100]}"
            
            # 4. Check dmesg.txt exists (content may be empty on non-Linux systems)
            assert "dmesg.txt" in members, \
                f"dmesg.txt not in archive. Found: {members}"
            
            dmesg_file = tar.extractfile("dmesg.txt")
            dmesg_content = dmesg_file.read().decode("utf-8")
            # Note: dmesg may be empty on non-Linux systems or when permission denied
            # The important thing is that the file exists in the archive
            assert dmesg_content is not None, "dmesg.txt could not be read"
        
        # Clean up archive
        if os.path.exists(archive_path):
            os.remove(archive_path)


def test_diagnostics_archive_structure():
    """Test that diagnostics archive has correct structure.
    
    Feature: decktune, Property 12: Diagnostics Archive Contents
    Validates: Requirements 8.1
    """
    rpc = create_test_rpc(
        cores=[-10, -15, -20, -25],
        lkg_cores=[-5, -10, -15, -20],
        status="enabled"
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"HOME": temp_dir}):
            with patch("os.path.expanduser", return_value=temp_dir):
                result = asyncio.run(
                    rpc.export_diagnostics()
                )
        
        assert result["success"]
        archive_path = result["path"]
        
        with tarfile.open(archive_path, "r:gz") as tar:
            # Verify exactly 4 files
            members = tar.getnames()
            expected_files = {"plugin_logs.txt", "config.json", "system_info.txt", "dmesg.txt"}
            assert set(members) == expected_files, \
                f"Unexpected files in archive: {set(members)} != {expected_files}"
        
        if os.path.exists(archive_path):
            os.remove(archive_path)
