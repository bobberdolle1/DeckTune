"""Property test for preset round-trip serialization.

Feature: decktune, Property 9: Preset Round-Trip Serialization
Validates: Requirements 5.5

Tests that for any valid Preset object P, export_presets() followed by
import_presets() produces a preset list containing an equivalent preset
(same app_id, label, value, timeout, use_timeout).
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import json
import asyncio
from unittest.mock import MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.rpc import DeckTuneRPC
from backend.platform.detect import PlatformInfo


# Strategy for generating valid preset values
preset_value_strategy = st.lists(
    st.integers(min_value=-60, max_value=0),
    min_size=4,
    max_size=4
)

# Strategy for generating valid presets
preset_strategy = st.fixed_dictionaries({
    "app_id": st.integers(min_value=1, max_value=1000000),
    "label": st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'S'),
        whitelist_characters=' -_'
    )),
    "value": preset_value_strategy,
    "timeout": st.integers(min_value=0, max_value=300),
    "use_timeout": st.booleans()
})


class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {}
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


def create_test_rpc():
    """Create a DeckTuneRPC instance for testing."""
    platform = PlatformInfo(
        model="Jupiter",
        variant="LCD",
        safe_limit=-30,
        detected=True
    )
    
    settings = MockSettingsManager()
    
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


@given(preset=preset_strategy)
@hyp_settings(max_examples=100)
def test_preset_roundtrip_serialization(preset):
    """Property 9: Preset Round-Trip Serialization
    
    For any valid Preset object P, export_presets() followed by
    import_presets() SHALL produce a preset list containing an
    equivalent preset (same app_id, label, value, timeout, use_timeout).
    
    Feature: decktune, Property 9: Preset Round-Trip Serialization
    Validates: Requirements 5.5
    """
    rpc = create_test_rpc()
    
    # Save the preset
    asyncio.run(
        rpc.save_preset(preset)
    )
    
    # Export presets
    exported_json = asyncio.run(
        rpc.export_presets()
    )
    
    # Create a new RPC instance (simulating import to fresh state)
    rpc2 = create_test_rpc()
    
    # Import presets
    result = asyncio.run(
        rpc2.import_presets(exported_json)
    )
    
    assert result["success"], f"Import failed: {result.get('error')}"
    
    # Get imported presets
    imported_presets = asyncio.run(
        rpc2.get_presets()
    )
    
    # Find the preset with matching app_id
    matching_preset = None
    for p in imported_presets:
        if p.get("app_id") == preset["app_id"]:
            matching_preset = p
            break
    
    assert matching_preset is not None, \
        f"Preset with app_id {preset['app_id']} not found after import"
    
    # Verify all key fields match
    assert matching_preset["app_id"] == preset["app_id"], \
        f"app_id mismatch: {matching_preset['app_id']} != {preset['app_id']}"
    
    assert matching_preset["label"] == preset["label"], \
        f"label mismatch: {matching_preset['label']} != {preset['label']}"
    
    assert matching_preset["value"] == preset["value"], \
        f"value mismatch: {matching_preset['value']} != {preset['value']}"
    
    assert matching_preset["timeout"] == preset["timeout"], \
        f"timeout mismatch: {matching_preset['timeout']} != {preset['timeout']}"
    
    assert matching_preset["use_timeout"] == preset["use_timeout"], \
        f"use_timeout mismatch: {matching_preset['use_timeout']} != {preset['use_timeout']}"


@given(presets=st.lists(preset_strategy, min_size=1, max_size=5, unique_by=lambda p: p["app_id"]))
@hyp_settings(max_examples=100)
def test_multiple_presets_roundtrip(presets):
    """Test round-trip with multiple presets.
    
    Feature: decktune, Property 9: Preset Round-Trip Serialization
    Validates: Requirements 5.5
    """
    rpc = create_test_rpc()
    
    # Save all presets
    for preset in presets:
        asyncio.run(
            rpc.save_preset(preset)
        )
    
    # Export presets
    exported_json = asyncio.run(
        rpc.export_presets()
    )
    
    # Create a new RPC instance
    rpc2 = create_test_rpc()
    
    # Import presets
    result = asyncio.run(
        rpc2.import_presets(exported_json)
    )
    
    assert result["success"], f"Import failed: {result.get('error')}"
    assert result["imported_count"] == len(presets), \
        f"Expected {len(presets)} imports, got {result['imported_count']}"
    
    # Get imported presets
    imported_presets = asyncio.run(
        rpc2.get_presets()
    )
    
    # Verify all presets were imported
    imported_app_ids = {p["app_id"] for p in imported_presets}
    original_app_ids = {p["app_id"] for p in presets}
    
    assert imported_app_ids == original_app_ids, \
        f"App IDs mismatch: {imported_app_ids} != {original_app_ids}"
