"""Property test for dynamic mode configuration persistence.

Feature: manual-dynamic-mode, Property 11: Backend settings persistence round-trip
Validates: Requirements 6.2

Tests that for any valid DynamicManualConfig, persisting to backend settings
and then loading SHALL produce an equivalent configuration.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.settings_manager import SettingsManager
from backend.dynamic.manual_manager import DynamicManager, DynamicManualConfig, CoreConfig


# Strategy for generating valid voltage values (-100 to 0 mV)
voltage_strategy = st.integers(min_value=-100, max_value=0)

# Strategy for generating valid threshold values (0 to 100%)
threshold_strategy = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

# Strategy for generating valid core IDs (0-3)
core_id_strategy = st.integers(min_value=0, max_value=3)

# Strategy for generating valid mode values
mode_strategy = st.sampled_from(["simple", "expert"])


def core_config_strategy(core_id: int) -> st.SearchStrategy[CoreConfig]:
    """Generate a valid CoreConfig for a specific core ID.
    
    Args:
        core_id: The core ID to use
        
    Returns:
        Strategy that generates CoreConfig instances
    """
    return st.builds(
        CoreConfig,
        core_id=st.just(core_id),
        min_mv=voltage_strategy,
        max_mv=voltage_strategy,
        threshold=threshold_strategy
    )


# Strategy for generating a complete DynamicManualConfig
@st.composite
def dynamic_config_strategy(draw):
    """Generate a valid DynamicManualConfig.
    
    Ensures that we have exactly 4 cores (0-3) with valid configurations.
    """
    mode = draw(mode_strategy)
    
    # Generate configs for all 4 cores
    cores = [
        draw(core_config_strategy(0)),
        draw(core_config_strategy(1)),
        draw(core_config_strategy(2)),
        draw(core_config_strategy(3))
    ]
    
    return DynamicManualConfig(
        mode=mode,
        cores=cores,
        version=1
    )


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_property_11_backend_settings_persistence_roundtrip(config):
    """**Feature: manual-dynamic-mode, Property 11: Backend settings persistence round-trip**
    
    For any valid DynamicManualConfig, persisting to backend settings
    and then loading SHALL produce an equivalent configuration.
    
    Validates: Requirements 6.2
    """
    # Create a temporary directory for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings manager with temp directory
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Create dynamic manager and set the config
        manager = DynamicManager()
        manager.config = config
        
        # Save configuration
        save_success = manager.save_config(settings_manager)
        assert save_success, "Failed to save configuration"
        
        # Create a new manager instance (simulating fresh load)
        manager2 = DynamicManager()
        
        # Load configuration
        load_success = manager2.load_config(settings_manager)
        assert load_success, "Failed to load configuration"
        
        # Verify the loaded config matches the original
        loaded_config = manager2.config
        
        # Check mode
        assert loaded_config.mode == config.mode, \
            f"Mode mismatch: {loaded_config.mode} != {config.mode}"
        
        # Check version
        assert loaded_config.version == config.version, \
            f"Version mismatch: {loaded_config.version} != {config.version}"
        
        # Check all cores
        assert len(loaded_config.cores) == len(config.cores), \
            f"Core count mismatch: {len(loaded_config.cores)} != {len(config.cores)}"
        
        for i in range(4):
            original_core = config.cores[i]
            loaded_core = loaded_config.cores[i]
            
            assert loaded_core.core_id == original_core.core_id, \
                f"Core {i} ID mismatch: {loaded_core.core_id} != {original_core.core_id}"
            
            assert loaded_core.min_mv == original_core.min_mv, \
                f"Core {i} min_mv mismatch: {loaded_core.min_mv} != {original_core.min_mv}"
            
            assert loaded_core.max_mv == original_core.max_mv, \
                f"Core {i} max_mv mismatch: {loaded_core.max_mv} != {original_core.max_mv}"
            
            # Handle float comparison with tolerance for threshold
            assert abs(loaded_core.threshold - original_core.threshold) < 1e-9, \
                f"Core {i} threshold mismatch: {loaded_core.threshold} != {original_core.threshold}"


@given(config=dynamic_config_strategy())
@hyp_settings(max_examples=100)
def test_persistence_across_multiple_instances(config):
    """Test that configuration persists across multiple manager instances.
    
    Feature: manual-dynamic-mode, Property 11: Backend settings persistence round-trip
    Validates: Requirements 6.2
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # First instance: save config
        manager1 = DynamicManager()
        manager1.config = config
        save_success = manager1.save_config(settings_manager)
        assert save_success, "Failed to save configuration"
        
        # Second instance: load config
        manager2 = DynamicManager()
        load_success = manager2.load_config(settings_manager)
        assert load_success, "Failed to load configuration"
        
        # Third instance: verify config still there
        manager3 = DynamicManager()
        load_success = manager3.load_config(settings_manager)
        assert load_success, "Failed to load configuration on third instance"
        
        # All instances should have the same config
        for i in range(4):
            assert manager2.config.cores[i].min_mv == manager3.config.cores[i].min_mv, \
                f"Core {i} min_mv changed between instances"
            assert manager2.config.cores[i].max_mv == manager3.config.cores[i].max_mv, \
                f"Core {i} max_mv changed between instances"
            assert abs(manager2.config.cores[i].threshold - manager3.config.cores[i].threshold) < 1e-9, \
                f"Core {i} threshold changed between instances"


def test_load_with_no_saved_config():
    """Test that loading with no saved config returns safe defaults."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Create manager and try to load (should get defaults)
        manager = DynamicManager()
        load_success = manager.load_config(settings_manager)
        
        # Should return False (no saved config)
        assert not load_success, "Should return False when no config exists"
        
        # Should have safe defaults
        assert manager.config.mode == "expert"
        assert len(manager.config.cores) == 4
        
        # Check default values
        for i in range(4):
            assert manager.config.cores[i].core_id == i
            assert manager.config.cores[i].min_mv == -30
            assert manager.config.cores[i].max_mv == -15
            assert manager.config.cores[i].threshold == 50.0


def test_migration_preserves_data():
    """Test that config migration preserves all data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Create a config with version 1
        config = DynamicManualConfig(
            mode="simple",
            cores=[
                CoreConfig(core_id=0, min_mv=-50, max_mv=-25, threshold=60.0),
                CoreConfig(core_id=1, min_mv=-40, max_mv=-20, threshold=55.0),
                CoreConfig(core_id=2, min_mv=-35, max_mv=-18, threshold=52.0),
                CoreConfig(core_id=3, min_mv=-45, max_mv=-22, threshold=58.0)
            ],
            version=1
        )
        
        # Save config
        manager = DynamicManager()
        manager.config = config
        manager.save_config(settings_manager)
        
        # Load config (should trigger migration check)
        manager2 = DynamicManager()
        manager2.load_config(settings_manager)
        
        # Verify all data preserved
        assert manager2.config.mode == "simple"
        assert manager2.config.cores[0].min_mv == -50
        assert manager2.config.cores[1].max_mv == -20
        assert manager2.config.cores[2].threshold == 52.0
        assert manager2.config.version == 1


@given(
    config=dynamic_config_strategy(),
    core_id=core_id_strategy,
    new_min=voltage_strategy,
    new_max=voltage_strategy,
    new_threshold=threshold_strategy
)
@hyp_settings(max_examples=100)
def test_update_preserves_other_cores(config, core_id, new_min, new_max, new_threshold):
    """Test that updating one core doesn't affect others.
    
    Feature: manual-dynamic-mode, Property 11: Backend settings persistence round-trip
    Validates: Requirements 6.2
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_manager = SettingsManager(storage_dir=Path(temp_dir))
        
        # Save initial config
        manager = DynamicManager()
        manager.config = config
        manager.save_config(settings_manager)
        
        # Update one core
        manager.set_core_config(core_id, new_min, new_max, new_threshold)
        manager.save_config(settings_manager)
        
        # Load config
        manager2 = DynamicManager()
        manager2.load_config(settings_manager)
        
        # Verify the updated core has new values
        assert manager2.config.cores[core_id].min_mv == new_min
        assert manager2.config.cores[core_id].max_mv == new_max
        assert abs(manager2.config.cores[core_id].threshold - new_threshold) < 1e-9
        
        # Verify other cores unchanged
        for i in range(4):
            if i != core_id:
                assert manager2.config.cores[i].min_mv == config.cores[i].min_mv, \
                    f"Core {i} min_mv changed unexpectedly"
                assert manager2.config.cores[i].max_mv == config.cores[i].max_mv, \
                    f"Core {i} max_mv changed unexpectedly"
                assert abs(manager2.config.cores[i].threshold - config.cores[i].threshold) < 1e-9, \
                    f"Core {i} threshold changed unexpectedly"
