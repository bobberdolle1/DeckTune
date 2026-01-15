"""Property tests for platform detection mapping.

Feature: decktune, Property 1: Platform Detection Mapping
Validates: Requirements 1.2, 1.3, 1.4
"""

from hypothesis import given, strategies as st, settings

from backend.platform.detect import _map_product_name_to_platform, PlatformInfo


# Strategy for generating product name strings containing "Jupiter"
jupiter_strings = st.text(min_size=0, max_size=50).map(
    lambda s: s[:25] + "Jupiter" + s[25:] if len(s) >= 25 else "Jupiter" + s
)

# Strategy for generating product name strings containing "Galileo"
galileo_strings = st.text(min_size=0, max_size=50).map(
    lambda s: s[:25] + "Galileo" + s[25:] if len(s) >= 25 else "Galileo" + s
)

# Strategy for strings that don't contain Jupiter or Galileo
unknown_strings = st.text(min_size=0, max_size=100).filter(
    lambda s: "Jupiter" not in s and "Galileo" not in s
)


class TestPlatformDetectionMapping:
    """Property 1: Platform Detection Mapping
    
    For any device product name string, the Platform_Detector SHALL correctly map:
    - Strings containing "Jupiter" → LCD variant with safe_limit = -30
    - Strings containing "Galileo" → OLED variant with safe_limit = -35
    - All other strings → UNKNOWN variant with safe_limit = -25
    
    Validates: Requirements 1.2, 1.3, 1.4
    """

    @given(product_name=jupiter_strings)
    @settings(max_examples=100)
    def test_jupiter_maps_to_lcd(self, product_name: str):
        """Strings containing 'Jupiter' map to LCD with safe_limit -30."""
        result = _map_product_name_to_platform(product_name)
        
        assert result.model == "Jupiter"
        assert result.variant == "LCD"
        assert result.safe_limit == -30
        assert result.detected is True

    @given(product_name=galileo_strings)
    @settings(max_examples=100)
    def test_galileo_maps_to_oled(self, product_name: str):
        """Strings containing 'Galileo' map to OLED with safe_limit -35."""
        result = _map_product_name_to_platform(product_name)
        
        assert result.model == "Galileo"
        assert result.variant == "OLED"
        assert result.safe_limit == -35
        assert result.detected is True

    @given(product_name=unknown_strings)
    @settings(max_examples=100)
    def test_unknown_maps_to_conservative(self, product_name: str):
        """Strings without Jupiter/Galileo map to UNKNOWN with safe_limit -25."""
        result = _map_product_name_to_platform(product_name)
        
        assert result.model == "Unknown"
        assert result.variant == "UNKNOWN"
        assert result.safe_limit == -25
        assert result.detected is False

    def test_none_maps_to_unknown(self):
        """None input maps to UNKNOWN with safe_limit -25."""
        result = _map_product_name_to_platform(None)
        
        assert result.model == "Unknown"
        assert result.variant == "UNKNOWN"
        assert result.safe_limit == -25
        assert result.detected is False
