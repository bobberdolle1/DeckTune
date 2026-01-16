"""Property tests for platform cache corruption resilience.

**Feature: decktune-3.1-reliability-ux, Property 5: Platform cache corruption resilience**
**Validates: Requirements 3.5**

Property 5: Platform cache corruption resilience
For any corrupted or malformed cache file, loading SHALL return None and not 
raise an exception, allowing fallback to fresh detection.
"""

import pytest
import tempfile
from hypothesis import given, strategies as st, settings
from pathlib import Path

from backend.platform.cache import PlatformCache


# Strategy for arbitrary byte sequences (corrupted data)
corrupted_bytes = st.binary(min_size=0, max_size=1000)

# Strategy for arbitrary text (malformed JSON)
malformed_text = st.text(min_size=0, max_size=500)

# Strategy for partial/incomplete JSON
partial_json = st.sampled_from([
    "{",
    '{"model":',
    '{"model": "Jupiter"',
    '{"model": "Jupiter",',
    '{"model": "Jupiter", "variant":',
    '{"model": "Jupiter", "variant": "LCD"',
    '{"model": "Jupiter", "variant": "LCD",',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit":',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30,',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30, "cached_at":',
    "}",
    "}{",
    "[]",
    "null",
    "true",
    "false",
    "123",
    '"string"',
])

# Strategy for JSON with missing required fields
missing_fields_json = st.sampled_from([
    '{}',
    '{"model": "Jupiter"}',
    '{"variant": "LCD"}',
    '{"safe_limit": -30}',
    '{"cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD"}',
    '{"model": "Jupiter", "safe_limit": -30}',
    '{"model": "Jupiter", "cached_at": "2025-01-01T00:00:00"}',
    '{"variant": "LCD", "safe_limit": -30}',
    '{"variant": "LCD", "cached_at": "2025-01-01T00:00:00"}',
    '{"safe_limit": -30, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30}',
])

# Strategy for JSON with invalid field types
invalid_types_json = st.sampled_from([
    '{"model": 123, "variant": "LCD", "safe_limit": -30, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": 456, "safe_limit": -30, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": "not_a_number", "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30, "cached_at": 12345}',
    '{"model": null, "variant": "LCD", "safe_limit": -30, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": null, "safe_limit": -30, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": null, "cached_at": "2025-01-01T00:00:00"}',
    '{"model": "Jupiter", "variant": "LCD", "safe_limit": -30, "cached_at": null}',
])


class TestPlatformCacheCorruptionResilience:
    """Property 5: Platform cache corruption resilience
    
    For any corrupted or malformed cache file, loading SHALL return None and not 
    raise an exception, allowing fallback to fresh detection.
    
    **Feature: decktune-3.1-reliability-ux, Property 5: Platform cache corruption resilience**
    **Validates: Requirements 3.5**
    """

    @given(data=corrupted_bytes)
    @settings(max_examples=100)
    def test_arbitrary_bytes_do_not_crash(self, data: bytes):
        """Arbitrary byte sequences do not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Write corrupted data
            cache_file.write_bytes(data)
            
            # Load should not raise and should return None
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"Corrupted cache should return None, got {result}"

    @given(data=malformed_text)
    @settings(max_examples=100)
    def test_malformed_text_does_not_crash(self, data: str):
        """Malformed text does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Write malformed text
            cache_file.write_text(data, encoding='utf-8')
            
            # Load should not raise and should return None
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"Malformed cache should return None, got {result}"

    @given(data=partial_json)
    @settings(max_examples=100)
    def test_partial_json_does_not_crash(self, data: str):
        """Partial/incomplete JSON does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Write partial JSON
            cache_file.write_text(data, encoding='utf-8')
            
            # Load should not raise and should return None
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"Partial JSON cache should return None, got {result}"

    @given(data=missing_fields_json)
    @settings(max_examples=100)
    def test_missing_fields_does_not_crash(self, data: str):
        """JSON with missing required fields does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Write JSON with missing fields
            cache_file.write_text(data, encoding='utf-8')
            
            # Load should not raise and should return None
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"JSON with missing fields should return None, got {result}"

    @given(data=invalid_types_json)
    @settings(max_examples=100)
    def test_invalid_types_does_not_crash(self, data: str):
        """JSON with invalid field types does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Write JSON with invalid types
            cache_file.write_text(data, encoding='utf-8')
            
            # Load should not raise and should return None
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"JSON with invalid types should return None, got {result}"

    def test_missing_file_does_not_crash(self):
        """Missing cache file does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Don't create any file
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"Missing cache file should return None, got {result}"

    def test_empty_file_does_not_crash(self):
        """Empty cache file does not cause exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / PlatformCache.CACHE_FILE
            
            # Create empty file
            cache_file.write_text("", encoding='utf-8')
            
            cache = PlatformCache(cache_dir=cache_dir)
            result = cache.load()
            
            assert result is None, \
                f"Empty cache file should return None, got {result}"
