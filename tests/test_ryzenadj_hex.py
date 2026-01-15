"""Property tests for hex calculation formula.

Feature: decktune, Property 13: Hex Calculation Formula
Validates: Requirements 9.1

Property 13: Hex Calculation Formula
For any core in [0,1,2,3] and value in [-60, 0], calculate_hex(core, value) 
SHALL return a string equal to hex((core * 0x100000) + (value & 0xFFFFF)).upper()
"""

from hypothesis import given, strategies as st, settings

from backend.core.ryzenadj import RyzenadjWrapper


# Strategy for core indices (0-3)
core_index = st.integers(min_value=0, max_value=3)

# Strategy for undervolt values (-60 to 0)
undervolt_value = st.integers(min_value=-60, max_value=0)


class TestHexCalculationFormula:
    """Property 13: Hex Calculation Formula
    
    For any core in [0,1,2,3] and value in [-60, 0], calculate_hex(core, value) 
    SHALL return a string equal to hex((core * 0x100000) + (value & 0xFFFFF)).upper()
    
    Validates: Requirements 9.1
    """

    @given(core=core_index, value=undervolt_value)
    @settings(max_examples=100)
    def test_hex_calculation_matches_formula(self, core: int, value: int):
        """calculate_hex output matches the formula specification."""
        result = RyzenadjWrapper.calculate_hex(core, value)
        
        # Expected formula: (core * 0x100000) + (value & 0xFFFFF)
        expected_value = (core * 0x100000) + (value & 0xFFFFF)
        expected = hex(expected_value).upper()
        
        assert result == expected, (
            f"For core={core}, value={value}: "
            f"got {result}, expected {expected}"
        )

    @given(core=core_index, value=undervolt_value)
    @settings(max_examples=100)
    def test_hex_output_is_uppercase(self, core: int, value: int):
        """calculate_hex output is uppercase."""
        result = RyzenadjWrapper.calculate_hex(core, value)
        
        # Check that the result is uppercase (0X prefix and hex digits)
        assert result == result.upper(), f"Result {result} is not uppercase"

    @given(core=core_index, value=undervolt_value)
    @settings(max_examples=100)
    def test_hex_output_starts_with_0x(self, core: int, value: int):
        """calculate_hex output starts with 0X prefix."""
        result = RyzenadjWrapper.calculate_hex(core, value)
        
        assert result.startswith("0X"), f"Result {result} does not start with 0X"

    @given(core=core_index, value=undervolt_value)
    @settings(max_examples=100)
    def test_core_offset_encoded_correctly(self, core: int, value: int):
        """Core index is correctly encoded in the upper bits."""
        result = RyzenadjWrapper.calculate_hex(core, value)
        result_int = int(result, 16)
        
        # Extract core from result (upper bits)
        extracted_core = result_int >> 20  # Divide by 0x100000
        
        assert extracted_core == core, (
            f"Core extraction failed: got {extracted_core}, expected {core}"
        )

    def test_known_values(self):
        """Test with known expected values for verification."""
        # Core 0, value 0 -> 0x0
        assert RyzenadjWrapper.calculate_hex(0, 0) == "0X0"
        
        # Core 1, value 0 -> 0x100000
        assert RyzenadjWrapper.calculate_hex(1, 0) == "0X100000"
        
        # Core 2, value 0 -> 0x200000
        assert RyzenadjWrapper.calculate_hex(2, 0) == "0X200000"
        
        # Core 3, value 0 -> 0x300000
        assert RyzenadjWrapper.calculate_hex(3, 0) == "0X300000"
        
        # Core 0, value -1 -> 0xFFFFF (two's complement mask)
        assert RyzenadjWrapper.calculate_hex(0, -1) == "0XFFFFF"
        
        # Core 1, value -1 -> 0x1FFFFF
        assert RyzenadjWrapper.calculate_hex(1, -1) == "0X1FFFFF"
