"""Property tests for platform cache validity.

**Feature: decktune-3.1-reliability-ux, Property 4: Platform cache validity**
**Validates: Requirements 3.3**

Property 4: Platform cache validity
For any cached platform data, if the cache age exceeds 30 days, is_valid() 
SHALL return False and fresh detection SHALL be performed.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from backend.platform.cache import CachedPlatform, PlatformCache


# Strategy for valid model names
model_strategy = st.sampled_from(["Jupiter", "Galileo", "Unknown"])

# Strategy for valid variant names
variant_strategy = st.sampled_from(["LCD", "OLED", "UNKNOWN"])

# Strategy for valid safe limits
safe_limit_strategy = st.sampled_from([-30, -35, -25])


@st.composite
def cached_platform_with_age(draw, min_days: int = 0, max_days: int = 60):
    """Generate a CachedPlatform with a specific age range."""
    model = draw(model_strategy)
    variant = draw(variant_strategy)
    safe_limit = draw(safe_limit_strategy)
    age_days = draw(st.integers(min_value=min_days, max_value=max_days))
    
    cached_at = (datetime.now() - timedelta(days=age_days)).isoformat()
    
    return CachedPlatform(
        model=model,
        variant=variant,
        safe_limit=safe_limit,
        cached_at=cached_at
    ), age_days


class TestPlatformCacheValidity:
    """Property 4: Platform cache validity
    
    For any cached platform data, if the cache age exceeds 30 days, is_valid() 
    SHALL return False and fresh detection SHALL be performed.
    
    **Feature: decktune-3.1-reliability-ux, Property 4: Platform cache validity**
    **Validates: Requirements 3.3**
    """

    @given(data=cached_platform_with_age(min_days=31, max_days=365))
    @settings(max_examples=100)
    def test_cache_older_than_30_days_is_invalid(self, data):
        """Cache older than 30 days returns is_valid() = False."""
        cached_platform, age_days = data
        
        cache = PlatformCache()
        cache._cached = cached_platform
        
        assert not cache.is_valid(), \
            f"Cache aged {age_days} days should be invalid (> 30 days)"

    @given(data=cached_platform_with_age(min_days=0, max_days=29))
    @settings(max_examples=100)
    def test_cache_within_30_days_is_valid(self, data):
        """Cache within 30 days returns is_valid() = True."""
        cached_platform, age_days = data
        
        cache = PlatformCache()
        cache._cached = cached_platform
        
        assert cache.is_valid(), \
            f"Cache aged {age_days} days should be valid (<= 30 days)"

    def test_cache_exactly_30_days_is_valid(self):
        """Cache exactly 30 days old is still valid (boundary condition)."""
        # Use 29 days and 23 hours to ensure we're within the 30-day window
        # even with test execution time
        cached_at = (datetime.now() - timedelta(days=29, hours=23)).isoformat()
        cached_platform = CachedPlatform(
            model="Jupiter",
            variant="LCD",
            safe_limit=-30,
            cached_at=cached_at
        )
        
        cache = PlatformCache()
        cache._cached = cached_platform
        
        assert cache.is_valid(), "Cache within 30 days should be valid"

    def test_cache_31_days_is_invalid(self):
        """Cache 31 days old is invalid (boundary condition)."""
        cached_at = (datetime.now() - timedelta(days=31)).isoformat()
        cached_platform = CachedPlatform(
            model="Jupiter",
            variant="LCD",
            safe_limit=-30,
            cached_at=cached_at
        )
        
        cache = PlatformCache()
        cache._cached = cached_platform
        
        assert not cache.is_valid(), "Cache 31 days old should be invalid"

    def test_empty_cache_is_invalid(self):
        """Empty cache (no cached data) returns is_valid() = False."""
        cache = PlatformCache()
        
        assert not cache.is_valid(), "Empty cache should be invalid"

    def test_cache_ttl_is_30_days(self):
        """Cache TTL is 30 days."""
        assert PlatformCache.CACHE_TTL_DAYS == 30, \
            f"Cache TTL should be 30 days, got {PlatformCache.CACHE_TTL_DAYS}"
