"""Property tests for CPUFreq frequency reading cache consistency.

Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
Validates: Requirements 12.3

Property 23: Frequency reading cache consistency
For any sequence of frequency reads within a 10-millisecond window, all reads 
SHALL return the same cached value without additional sysfs access.

This test validates the caching logic in CPUFreqController to ensure:
- Multiple reads within the cache TTL return the same value
- Cache entries expire after the TTL
- Cache can be explicitly cleared
- Cache is per-core (different cores have independent caches)
"""

import pytest
import time
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch

from backend.platform.cpufreq import CPUFreqController, FrequencyCache


# Strategies for testing
core_id_strategy = st.integers(min_value=0, max_value=7)
frequency_mhz_strategy = st.integers(min_value=400, max_value=3500)
read_count_strategy = st.integers(min_value=2, max_value=10)


class TestFrequencyReadingCacheConsistency:
    """Property 23: Frequency reading cache consistency
    
    For any sequence of frequency reads within a 10-millisecond window, 
    all reads SHALL return the same cached value without additional sysfs access.
    
    Validates: Requirements 12.3
    """

    @given(
        core_id=core_id_strategy,
        frequency_mhz=frequency_mhz_strategy,
        read_count=read_count_strategy
    )
    @settings(max_examples=100)
    def test_multiple_reads_within_ttl_return_same_value(
        self, 
        core_id: int, 
        frequency_mhz: int,
        read_count: int
    ):
        """Multiple frequency reads within cache TTL SHALL return same value.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure
            base_path = Path(tmpdir)
            cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
            cpufreq_path.mkdir(parents=True)
            
            freq_file = cpufreq_path / "scaling_cur_freq"
            freq_khz = frequency_mhz * 1000
            freq_file.write_text(str(freq_khz))
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # First read should populate cache
            first_read = controller.get_current_frequency(core_id, use_cache=True)
            assert first_read == frequency_mhz
            
            # Change the underlying file (simulating frequency change)
            new_freq_mhz = frequency_mhz + 100
            freq_file.write_text(str(new_freq_mhz * 1000))
            
            # Subsequent reads within TTL should return cached value
            # Don't add delays - just read multiple times immediately
            for _ in range(read_count - 1):
                cached_read = controller.get_current_frequency(core_id, use_cache=True)
                assert cached_read == first_read, (
                    f"Read within cache TTL should return cached value {first_read}, "
                    f"but got {cached_read}"
                )

    @given(
        core_id=core_id_strategy,
        frequency_mhz=frequency_mhz_strategy
    )
    @settings(max_examples=100)
    def test_cache_expires_after_ttl(self, core_id: int, frequency_mhz: int):
        """Cache entry SHALL expire after TTL and return fresh value.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure
            base_path = Path(tmpdir)
            cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
            cpufreq_path.mkdir(parents=True)
            
            freq_file = cpufreq_path / "scaling_cur_freq"
            freq_khz = frequency_mhz * 1000
            freq_file.write_text(str(freq_khz))
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # First read
            first_read = controller.get_current_frequency(core_id, use_cache=True)
            assert first_read == frequency_mhz
            
            # Wait for cache to expire (TTL is 10ms)
            time.sleep(0.015)  # 15ms > 10ms TTL
            
            # Change the underlying file
            new_freq_mhz = frequency_mhz + 200
            freq_file.write_text(str(new_freq_mhz * 1000))
            
            # Read after TTL should get fresh value
            second_read = controller.get_current_frequency(core_id, use_cache=True)
            assert second_read == new_freq_mhz, (
                f"Read after cache TTL should return fresh value {new_freq_mhz}, "
                f"but got {second_read}"
            )

    @given(
        core_id=core_id_strategy,
        frequency_mhz=frequency_mhz_strategy
    )
    @settings(max_examples=100)
    def test_cache_disabled_always_reads_fresh(self, core_id: int, frequency_mhz: int):
        """Reads with cache disabled SHALL always return fresh values.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure
            base_path = Path(tmpdir)
            cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
            cpufreq_path.mkdir(parents=True)
            
            freq_file = cpufreq_path / "scaling_cur_freq"
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # First read with cache disabled
            freq_file.write_text(str(frequency_mhz * 1000))
            first_read = controller.get_current_frequency(core_id, use_cache=False)
            assert first_read == frequency_mhz
            
            # Change frequency
            new_freq_mhz = frequency_mhz + 100
            freq_file.write_text(str(new_freq_mhz * 1000))
            
            # Second read with cache disabled should get new value immediately
            second_read = controller.get_current_frequency(core_id, use_cache=False)
            assert second_read == new_freq_mhz, (
                f"Read with cache disabled should return fresh value {new_freq_mhz}, "
                f"but got {second_read}"
            )

    @given(
        core_id_1=core_id_strategy,
        core_id_2=core_id_strategy,
        freq_1=frequency_mhz_strategy,
        freq_2=frequency_mhz_strategy
    )
    @settings(max_examples=100)
    def test_cache_is_per_core_independent(
        self, 
        core_id_1: int, 
        core_id_2: int,
        freq_1: int,
        freq_2: int
    ):
        """Cache entries SHALL be independent per core.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        # Skip if same core
        if core_id_1 == core_id_2:
            return
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure for both cores
            base_path = Path(tmpdir)
            
            for core_id, freq_mhz in [(core_id_1, freq_1), (core_id_2, freq_2)]:
                cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
                cpufreq_path.mkdir(parents=True)
                freq_file = cpufreq_path / "scaling_cur_freq"
                freq_file.write_text(str(freq_mhz * 1000))
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # Read both cores
            read_1 = controller.get_current_frequency(core_id_1, use_cache=True)
            read_2 = controller.get_current_frequency(core_id_2, use_cache=True)
            
            assert read_1 == freq_1
            assert read_2 == freq_2
            
            # Change core 1 frequency
            new_freq_1 = freq_1 + 100
            freq_file_1 = base_path / f"cpu{core_id_1}" / "cpufreq" / "scaling_cur_freq"
            freq_file_1.write_text(str(new_freq_1 * 1000))
            
            # Wait for core 1 cache to expire
            time.sleep(0.015)
            
            # Core 1 should get new value, core 2 should still be cached
            read_1_new = controller.get_current_frequency(core_id_1, use_cache=True)
            read_2_cached = controller.get_current_frequency(core_id_2, use_cache=True)
            
            assert read_1_new == new_freq_1, (
                f"Core {core_id_1} should read new value {new_freq_1}, got {read_1_new}"
            )
            assert read_2_cached == freq_2, (
                f"Core {core_id_2} cache should be independent, expected {freq_2}, got {read_2_cached}"
            )

    @given(
        core_id=core_id_strategy,
        frequency_mhz=frequency_mhz_strategy
    )
    @settings(max_examples=100)
    def test_clear_cache_forces_fresh_read(self, core_id: int, frequency_mhz: int):
        """Clearing cache SHALL force next read to be fresh.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure
            base_path = Path(tmpdir)
            cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
            cpufreq_path.mkdir(parents=True)
            
            freq_file = cpufreq_path / "scaling_cur_freq"
            freq_file.write_text(str(frequency_mhz * 1000))
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # First read to populate cache
            first_read = controller.get_current_frequency(core_id, use_cache=True)
            assert first_read == frequency_mhz
            
            # Change frequency
            new_freq_mhz = frequency_mhz + 150
            freq_file.write_text(str(new_freq_mhz * 1000))
            
            # Clear cache
            controller.clear_cache()
            
            # Next read should get fresh value even within TTL
            fresh_read = controller.get_current_frequency(core_id, use_cache=True)
            assert fresh_read == new_freq_mhz, (
                f"Read after cache clear should return fresh value {new_freq_mhz}, "
                f"but got {fresh_read}"
            )

    @given(
        core_id=core_id_strategy,
        frequency_mhz=frequency_mhz_strategy
    )
    @settings(max_examples=100)
    def test_lock_frequency_invalidates_cache(self, core_id: int, frequency_mhz: int):
        """Locking frequency SHALL invalidate cache for that core.
        
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 12.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock sysfs structure
            base_path = Path(tmpdir)
            cpufreq_path = base_path / f"cpu{core_id}" / "cpufreq"
            cpufreq_path.mkdir(parents=True)
            
            # Create necessary files
            freq_file = cpufreq_path / "scaling_cur_freq"
            freq_file.write_text(str(frequency_mhz * 1000))
            
            gov_file = cpufreq_path / "scaling_governor"
            gov_file.write_text("schedutil")
            
            avail_gov_file = cpufreq_path / "scaling_available_governors"
            avail_gov_file.write_text("schedutil userspace performance")
            
            setspeed_file = cpufreq_path / "scaling_setspeed"
            setspeed_file.write_text(str(frequency_mhz * 1000))
            
            # Create controller
            controller = CPUFreqController(base_path=str(base_path))
            
            # First read to populate cache
            first_read = controller.get_current_frequency(core_id, use_cache=True)
            assert first_read == frequency_mhz
            
            # Lock frequency (this should invalidate cache)
            new_freq_mhz = frequency_mhz + 200
            freq_file.write_text(str(new_freq_mhz * 1000))
            controller.lock_frequency(core_id, new_freq_mhz)
            
            # Next read should get fresh value
            fresh_read = controller.get_current_frequency(core_id, use_cache=True)
            assert fresh_read == new_freq_mhz, (
                f"Read after lock_frequency should return fresh value {new_freq_mhz}, "
                f"but got {fresh_read}"
            )


class TestFrequencyCacheDataclass:
    """Test FrequencyCache dataclass behavior."""
    
    @given(
        frequency_mhz=frequency_mhz_strategy,
        ttl_ms=st.floats(min_value=10.0, max_value=100.0)
    )
    @settings(max_examples=100)
    def test_cache_entry_valid_within_ttl(self, frequency_mhz: int, ttl_ms: float):
        """Cache entry SHALL be valid within its TTL."""
        cache = FrequencyCache(
            frequency_mhz=frequency_mhz,
            timestamp=time.time(),
            ttl_ms=ttl_ms
        )
        
        assert cache.is_valid(), "Cache entry should be valid immediately after creation"
        
        # Wait less than TTL (use a smaller fraction to avoid timing issues)
        time.sleep(ttl_ms / 4000)  # Quarter of the TTL in seconds
        assert cache.is_valid(), f"Cache entry should be valid within TTL ({ttl_ms}ms)"
    
    @given(
        frequency_mhz=frequency_mhz_strategy,
        ttl_ms=st.floats(min_value=5.0, max_value=20.0)
    )
    @settings(max_examples=100)
    def test_cache_entry_invalid_after_ttl(self, frequency_mhz: int, ttl_ms: float):
        """Cache entry SHALL be invalid after its TTL expires."""
        cache = FrequencyCache(
            frequency_mhz=frequency_mhz,
            timestamp=time.time(),
            ttl_ms=ttl_ms
        )
        
        # Wait longer than TTL
        time.sleep((ttl_ms + 5) / 1000)  # TTL + 5ms in seconds
        assert not cache.is_valid(), (
            f"Cache entry should be invalid after TTL ({ttl_ms}ms) expires"
        )
