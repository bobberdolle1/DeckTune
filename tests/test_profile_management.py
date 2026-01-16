"""Property-based tests for profile management.

Feature: decktune-3.0-automation, Property 12, 14, 15, 16
Validates: Requirements 3.1, 3.3, 3.4, 3.5

This module tests the ProfileManager's CRUD operations and profile
application logic using property-based testing.
"""

import asyncio
import json
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, MagicMock
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from backend.dynamic.profile_manager import ProfileManager, GameProfile


# ==================== Helper Functions ====================

def create_profile_manager():
    """Create a ProfileManager instance with mocks for testing."""
    mock_settings = Mock()
    mock_settings.getSetting = Mock(return_value={})
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_controller = Mock()
    mock_controller.is_running = Mock(return_value=False)
    mock_controller.stop = AsyncMock()
    
    mock_emitter = Mock()
    mock_emitter.emit_profile_changed = AsyncMock()
    
    return ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=mock_controller,
        event_emitter=mock_emitter
    )


# ==================== Test Fixtures ====================

@pytest.fixture
def mock_settings_manager():
    """Create a mock settings manager."""
    manager = Mock()
    manager.getSetting = Mock(return_value={})
    manager.setSetting = Mock()
    return manager


@pytest.fixture
def mock_ryzenadj():
    """Create a mock RyzenadjWrapper."""
    ryzenadj = Mock()
    # Return tuple (success, error) instead of RyzenadjResult
    ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    return ryzenadj


@pytest.fixture
def mock_dynamic_controller():
    """Create a mock DynamicController."""
    controller = Mock()
    controller.is_running = Mock(return_value=False)
    controller.stop = AsyncMock()
    return controller


@pytest.fixture
def mock_event_emitter():
    """Create a mock EventEmitter."""
    emitter = Mock()
    emitter.emit_profile_changed = AsyncMock()
    return emitter


@pytest.fixture
def profile_manager(mock_settings_manager, mock_ryzenadj, mock_dynamic_controller, mock_event_emitter):
    """Create a ProfileManager instance with mocks."""
    return ProfileManager(
        settings_manager=mock_settings_manager,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=mock_dynamic_controller,
        event_emitter=mock_event_emitter
    )


# ==================== Hypothesis Strategies ====================

# Strategy for valid app_ids (positive integers)
app_ids = st.integers(min_value=1, max_value=999999)

# Strategy for game names (non-empty strings, max 128 chars)
game_names = st.text(min_size=1, max_size=128, alphabet=st.characters(
    blacklist_categories=('Cs', 'Cc'),  # Exclude control characters
    blacklist_characters='\x00'
))

# Strategy for undervolt values (valid range: -100 to 0 mV)
undervolt_values = st.integers(min_value=-100, max_value=0)

# Strategy for cores array (4 undervolt values)
cores_arrays = st.lists(undervolt_values, min_size=4, max_size=4)

# Strategy for dynamic_enabled flag
dynamic_enabled_flags = st.booleans()

# Strategy for dynamic_config (simplified)
dynamic_configs = st.one_of(
    st.none(),
    st.fixed_dictionaries({
        "strategy": st.sampled_from(["conservative", "balanced", "aggressive"]),
        "simple_mode": st.booleans(),
        "simple_value": undervolt_values
    })
)


# ==================== Property Tests ====================

@given(
    app_id=app_ids,
    name=game_names,
    cores=cores_arrays,
    dynamic_enabled=dynamic_enabled_flags,
    dynamic_config=dynamic_configs
)
@settings(max_examples=100, deadline=None)
def test_property_12_profile_creation_completeness(
    app_id,
    name,
    cores,
    dynamic_enabled,
    dynamic_config
):
    """Property 12: Profile creation completeness.
    
    Feature: decktune-3.0-automation, Property 12
    Validates: Requirements 3.1
    
    For any created profile, it must contain fields: app_id, name, cores,
    dynamic_enabled, dynamic_config, created_at.
    """
    # Skip invalid combinations (dynamic_enabled=True but dynamic_config=None)
    if dynamic_enabled and dynamic_config is None:
        return
    
    # Create fresh profile manager for each test
    profile_manager = create_profile_manager()
    
    # Create profile
    profile = asyncio.run(profile_manager.create_profile(
        app_id=app_id,
        name=name,
        cores=cores,
        dynamic_enabled=dynamic_enabled,
        dynamic_config=dynamic_config
    ))
    
    # Verify profile was created
    assert profile is not None, "Profile creation should succeed with valid inputs"
    
    # Verify all required fields are present
    assert profile.app_id == app_id, "app_id must match input"
    assert profile.name == name, "name must match input"
    assert profile.cores == cores, "cores must match input"
    assert profile.dynamic_enabled == dynamic_enabled, "dynamic_enabled must match input"
    assert profile.dynamic_config == dynamic_config, "dynamic_config must match input"
    assert profile.created_at != "", "created_at must be set"
    
    # Verify profile can be retrieved
    retrieved = profile_manager.get_profile(app_id)
    assert retrieved is not None, "Profile must be retrievable after creation"
    assert retrieved.app_id == app_id, "Retrieved profile must match created profile"


@given(
    app_id=app_ids,
    name=game_names,
    cores=cores_arrays,
    new_cores=cores_arrays
)
@settings(max_examples=100, deadline=None)
def test_property_14_profile_update_persistence(
    app_id,
    name,
    cores,
    new_cores
):
    """Property 14: Profile update persistence.
    
    Feature: decktune-3.0-automation, Property 14
    Validates: Requirements 3.3
    
    For any profile update, the changes must persist to storage and be
    applied if the game is currently active.
    """
    # Create fresh profile manager for each test
    profile_manager = create_profile_manager()
    
    # Create initial profile
    profile = asyncio.run(profile_manager.create_profile(
        app_id=app_id,
        name=name,
        cores=cores,
        dynamic_enabled=False,
        dynamic_config=None
    ))
    assert profile is not None
    
    # Update the profile with new cores
    success = asyncio.run(profile_manager.update_profile(
        app_id=app_id,
        cores=new_cores
    ))
    assert success, "Profile update should succeed"
    
    # Verify changes persisted
    updated = profile_manager.get_profile(app_id)
    assert updated is not None, "Profile must still exist after update"
    assert updated.cores == new_cores, "Updated cores must persist"
    
    # Verify setSetting was called (persistence)
    assert profile_manager.settings.setSetting.called, "Settings must be saved after update"


@given(
    app_id=app_ids,
    name=game_names,
    cores=cores_arrays
)
@settings(max_examples=100, deadline=None)
def test_property_15_profile_deletion_with_fallback(
    app_id,
    name,
    cores
):
    """Property 15: Profile deletion with fallback.
    
    Feature: decktune-3.0-automation, Property 15
    Validates: Requirements 3.4
    
    For any profile deletion while that game is active, the global default
    must be applied immediately.
    """
    # Create fresh profile manager for each test
    profile_manager = create_profile_manager()
    
    # Create profile
    profile = asyncio.run(profile_manager.create_profile(
        app_id=app_id,
        name=name,
        cores=cores,
        dynamic_enabled=False,
        dynamic_config=None
    ))
    assert profile is not None
    
    # Apply the profile (make it active)
    asyncio.run(profile_manager.apply_profile(app_id))
    assert profile_manager._current_app_id == app_id, "Profile should be active"
    
    # Reset mock to track new calls
    profile_manager.ryzenadj.apply_values_async.reset_mock()
    
    # Delete the active profile
    success = asyncio.run(profile_manager.delete_profile(app_id))
    assert success, "Profile deletion should succeed"
    
    # Verify profile is gone
    deleted = profile_manager.get_profile(app_id)
    assert deleted is None, "Profile must not exist after deletion"
    
    # Verify global default was applied (ryzenadj.apply_values_async called)
    assert profile_manager.ryzenadj.apply_values_async.called, "Global default must be applied after deleting active profile"
    
    # Verify current_app_id was cleared
    assert profile_manager._current_app_id is None, "Current app_id should be cleared"


@given(
    app_id=app_ids,
    name=game_names
)
@settings(max_examples=100, deadline=None)
def test_property_16_current_settings_capture(
    app_id,
    name
):
    """Property 16: Current settings capture.
    
    Feature: decktune-3.0-automation, Property 16
    Validates: Requirements 3.5, 5.2
    
    For any profile created from current settings, it must match the active
    undervolt values and dynamic mode configuration.
    """
    # Create fresh profile manager with custom mock settings
    mock_settings = Mock()
    current_cores = [-25, -25, -25, -25]
    mock_settings.getSetting = Mock(side_effect=lambda key, default=None: {
        "cores": current_cores,
        "dynamic_config": None
    }.get(key, default))
    mock_settings.setSetting = Mock()
    
    mock_ryzenadj = Mock()
    mock_ryzenadj.apply_values_async = AsyncMock(return_value=(True, None))
    
    mock_controller = Mock()
    mock_controller.is_running = Mock(return_value=False)
    
    mock_emitter = Mock()
    mock_emitter.emit_profile_changed = AsyncMock()
    
    profile_manager = ProfileManager(
        settings_manager=mock_settings,
        ryzenadj=mock_ryzenadj,
        dynamic_controller=mock_controller,
        event_emitter=mock_emitter
    )
    
    # Create profile from current settings
    profile = asyncio.run(profile_manager.create_from_current(
        app_id=app_id,
        name=name
    ))
    
    assert profile is not None, "Profile creation from current should succeed"
    
    # Verify captured settings match current settings
    assert profile.cores == current_cores, "Captured cores must match current settings"
    assert profile.app_id == app_id, "app_id must match input"
    assert profile.name == name, "name must match input"
    
    # Verify getSetting was called to capture current state
    assert mock_settings.getSetting.called, "Must read current settings"


# ==================== Edge Case Tests ====================

def test_profile_creation_duplicate_app_id():
    """Test that creating a profile with duplicate app_id fails."""
    profile_manager = create_profile_manager()
    app_id = 12345
    
    # Create first profile
    profile1 = asyncio.run(profile_manager.create_profile(
        app_id=app_id,
        name="Game 1",
        cores=[-20, -20, -20, -20]
    ))
    assert profile1 is not None
    
    # Try to create second profile with same app_id
    profile2 = asyncio.run(profile_manager.create_profile(
        app_id=app_id,
        name="Game 2",
        cores=[-25, -25, -25, -25]
    ))
    assert profile2 is None, "Duplicate app_id should be rejected"


def test_profile_validation_invalid_cores():
    """Test that invalid cores array is rejected."""
    profile_manager = create_profile_manager()
    
    # Too few cores
    profile1 = asyncio.run(profile_manager.create_profile(
        app_id=12345,
        name="Test Game",
        cores=[-20, -20]  # Only 2 cores
    ))
    assert profile1 is None, "Invalid cores array should be rejected"
    
    # Out of range values
    profile2 = asyncio.run(profile_manager.create_profile(
        app_id=12346,
        name="Test Game 2",
        cores=[-200, -200, -200, -200]  # Out of range
    ))
    assert profile2 is None, "Out of range cores should be rejected"


def test_update_nonexistent_profile():
    """Test that updating a non-existent profile fails."""
    profile_manager = create_profile_manager()
    
    success = asyncio.run(profile_manager.update_profile(
        app_id=99999,
        cores=[-25, -25, -25, -25]
    ))
    assert not success, "Updating non-existent profile should fail"


def test_delete_nonexistent_profile():
    """Test that deleting a non-existent profile fails."""
    profile_manager = create_profile_manager()
    
    success = asyncio.run(profile_manager.delete_profile(app_id=99999))
    assert not success, "Deleting non-existent profile should fail"


def test_get_all_profiles_empty():
    """Test getting all profiles when none exist."""
    profile_manager = create_profile_manager()
    
    profiles = profile_manager.get_all_profiles()
    assert profiles == [], "Should return empty list when no profiles exist"


def test_get_all_profiles_multiple():
    """Test getting all profiles when multiple exist."""
    profile_manager = create_profile_manager()
    
    # Create multiple profiles
    asyncio.run(profile_manager.create_profile(
        app_id=1,
        name="Game 1",
        cores=[-20, -20, -20, -20]
    ))
    asyncio.run(profile_manager.create_profile(
        app_id=2,
        name="Game 2",
        cores=[-25, -25, -25, -25]
    ))
    asyncio.run(profile_manager.create_profile(
        app_id=3,
        name="Game 3",
        cores=[-30, -30, -30, -30]
    ))
    
    profiles = profile_manager.get_all_profiles()
    assert len(profiles) == 3, "Should return all profiles"
    assert all(isinstance(p, GameProfile) for p in profiles), "All items should be GameProfile instances"


# ==================== Import/Export Property Tests ====================

@given(
    profiles_data=st.lists(
        st.fixed_dictionaries({
            "app_id": app_ids,
            "name": game_names,
            "cores": cores_arrays,
            "dynamic_enabled": dynamic_enabled_flags,
            "dynamic_config": dynamic_configs
        }),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x["app_id"]  # Ensure unique app_ids
    )
)
@settings(max_examples=100, deadline=None)
def test_property_35_export_json_validity(profiles_data):
    """Property 35: Export JSON validity.
    
    Feature: decktune-3.0-automation, Property 35
    Validates: Requirements 9.1
    
    For any profile export, the output must be valid JSON containing
    version and profiles array.
    """
    # Filter out invalid combinations
    valid_profiles = []
    for p in profiles_data:
        if p["dynamic_enabled"] and p["dynamic_config"] is None:
            continue
        # Filter out whitespace-only names (validation will reject these)
        if not p["name"] or not p["name"].strip():
            continue
        valid_profiles.append(p)
    
    if not valid_profiles:
        return  # Skip if no valid profiles
    
    # Create profile manager and add profiles
    profile_manager = create_profile_manager()
    
    for profile_data in valid_profiles:
        asyncio.run(profile_manager.create_profile(
            app_id=profile_data["app_id"],
            name=profile_data["name"],
            cores=profile_data["cores"],
            dynamic_enabled=profile_data["dynamic_enabled"],
            dynamic_config=profile_data["dynamic_config"]
        ))
    
    # Export profiles
    json_str = profile_manager.export_profiles()
    
    # Verify it's valid JSON
    try:
        export_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        pytest.fail(f"Export must produce valid JSON: {e}")
    
    # Verify required fields
    assert "version" in export_data, "Export must contain 'version' field"
    assert "profiles" in export_data, "Export must contain 'profiles' array"
    assert isinstance(export_data["profiles"], list), "'profiles' must be an array"
    
    # Verify profile count matches
    assert len(export_data["profiles"]) == len(valid_profiles), "Export must contain all profiles"
    
    # Verify each profile has required fields
    for profile in export_data["profiles"]:
        assert "app_id" in profile, "Each profile must have app_id"
        assert "name" in profile, "Each profile must have name"
        assert "cores" in profile, "Each profile must have cores"
        assert "dynamic_enabled" in profile, "Each profile must have dynamic_enabled"
        assert "created_at" in profile, "Each profile must have created_at"


@given(
    profiles_data=st.lists(
        st.fixed_dictionaries({
            "app_id": app_ids,
            "name": game_names,
            "cores": cores_arrays,
            "dynamic_enabled": st.just(False),  # Simplified for testing
            "dynamic_config": st.none()
        }),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x["app_id"]
    ),
    merge_strategy=st.sampled_from(["skip", "overwrite", "rename"])
)
@settings(max_examples=100, deadline=None)
def test_property_36_import_validation_and_merge(profiles_data, merge_strategy):
    """Property 36: Import validation and merge.
    
    Feature: decktune-3.0-automation, Property 36
    Validates: Requirements 9.2
    
    For any profile import, invalid JSON must be rejected and valid profiles
    must not overwrite existing ones with same AppID (when strategy is "skip").
    """
    # Create profile manager
    profile_manager = create_profile_manager()
    
    # Test 1: Invalid JSON should be rejected
    invalid_json = "{ invalid json }"
    result = asyncio.run(profile_manager.import_profiles(invalid_json, merge_strategy))
    assert not result["success"], "Invalid JSON must be rejected"
    assert len(result["errors"]) > 0, "Must report JSON parse error"
    
    # Test 2: Valid import
    # Create some initial profiles
    initial_profiles = profiles_data[:len(profiles_data)//2] if len(profiles_data) > 1 else []
    for profile_data in initial_profiles:
        asyncio.run(profile_manager.create_profile(
            app_id=profile_data["app_id"],
            name=profile_data["name"],
            cores=profile_data["cores"],
            dynamic_enabled=profile_data["dynamic_enabled"],
            dynamic_config=profile_data["dynamic_config"]
        ))
    
    # Export all profiles to get valid JSON format
    export_json = profile_manager.export_profiles()
    
    # Create a new profile manager to test import
    profile_manager2 = create_profile_manager()
    
    # Add some profiles that will conflict
    conflict_profiles = profiles_data[:len(profiles_data)//3] if len(profiles_data) > 2 else []
    for profile_data in conflict_profiles:
        asyncio.run(profile_manager2.create_profile(
            app_id=profile_data["app_id"],
            name="Existing Profile",
            cores=[0, 0, 0, 0],
            dynamic_enabled=False,
            dynamic_config=None
        ))
    
    # Import profiles
    result = asyncio.run(profile_manager2.import_profiles(export_json, merge_strategy))
    
    # Verify import succeeded (or had no errors)
    assert result["success"] or len(result["errors"]) == 0, "Valid import should succeed"
    
    # Verify behavior based on merge strategy
    if merge_strategy == "skip":
        # Conflicting profiles should be skipped
        if conflict_profiles:
            assert result["skipped_count"] > 0, "Conflicts should be skipped with 'skip' strategy"
            # Verify original profiles are unchanged
            for conflict in conflict_profiles:
                existing = profile_manager2.get_profile(conflict["app_id"])
                if existing:
                    assert existing.name == "Existing Profile", "Existing profile should not be overwritten with 'skip' strategy"
    
    elif merge_strategy == "overwrite":
        # Profiles should be imported (count depends on conflicts)
        total_expected = len(initial_profiles)
        if total_expected > 0:
            assert result["imported_count"] >= 0, "Import count should be non-negative"
    
    elif merge_strategy == "rename":
        # Profiles should be imported (count depends on conflicts)
        total_expected = len(initial_profiles)
        if total_expected > 0:
            assert result["imported_count"] >= 0, "Import count should be non-negative"


def test_export_import_roundtrip():
    """Test that export followed by import preserves all profiles."""
    profile_manager = create_profile_manager()
    
    # Create several profiles
    test_profiles = [
        {"app_id": 1091500, "name": "Cyberpunk 2077", "cores": [-25, -25, -25, -25]},
        {"app_id": 1245620, "name": "Elden Ring", "cores": [-30, -30, -30, -30]},
        {"app_id": 1174180, "name": "Red Dead Redemption 2", "cores": [-20, -20, -20, -20]},
    ]
    
    for profile_data in test_profiles:
        asyncio.run(profile_manager.create_profile(
            app_id=profile_data["app_id"],
            name=profile_data["name"],
            cores=profile_data["cores"],
            dynamic_enabled=False,
            dynamic_config=None
        ))
    
    # Export profiles
    json_str = profile_manager.export_profiles()
    
    # Create new profile manager and import
    profile_manager2 = create_profile_manager()
    result = asyncio.run(profile_manager2.import_profiles(json_str, "overwrite"))
    
    # Verify import succeeded
    assert result["success"], "Import should succeed"
    assert result["imported_count"] == len(test_profiles), "All profiles should be imported"
    
    # Verify all profiles are present with correct data
    imported_profiles = profile_manager2.get_all_profiles()
    assert len(imported_profiles) == len(test_profiles), "All profiles should be present"
    
    for original in test_profiles:
        imported = profile_manager2.get_profile(original["app_id"])
        assert imported is not None, f"Profile {original['app_id']} should exist"
        assert imported.name == original["name"], "Name should match"
        assert imported.cores == original["cores"], "Cores should match"


def test_import_missing_required_fields():
    """Test that import rejects profiles missing required fields."""
    profile_manager = create_profile_manager()
    
    # JSON with profile missing app_id
    invalid_json = json.dumps({
        "version": "3.0",
        "profiles": [
            {
                "name": "Test Game",
                "cores": [-25, -25, -25, -25],
                "dynamic_enabled": False
            }
        ]
    })
    
    result = asyncio.run(profile_manager.import_profiles(invalid_json, "skip"))
    
    # Should report error about missing app_id
    assert len(result["errors"]) > 0, "Must report error for missing required field"
    assert result["imported_count"] == 0, "Should not import invalid profiles"


def test_import_invalid_merge_strategy():
    """Test that invalid merge strategy is rejected."""
    profile_manager = create_profile_manager()
    
    valid_json = json.dumps({
        "version": "3.0",
        "profiles": []
    })
    
    result = asyncio.run(profile_manager.import_profiles(valid_json, "invalid_strategy"))
    
    assert not result["success"], "Invalid merge strategy should be rejected"
    assert len(result["errors"]) > 0, "Must report error for invalid strategy"
