"""Property-based tests for frequency wizard configuration validation.

Feature: frequency-based-wizard, Property 1: Configuration validation completeness
Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
"""

import pytest
from hypothesis import given, strategies as st

from backend.tuning.frequency_wizard import FrequencyWizardConfig, ConfigurationError


class TestConfigurationValidation:
    """Test configuration validation completeness.
    
    Property 1: For any wizard configuration with parameters outside valid ranges,
    the validation function should reject the configuration and prevent wizard execution.
    """
    
    @given(
        freq_start=st.one_of(
            st.integers(max_value=399),  # Below minimum
            st.integers(min_value=3501)  # Above maximum
        )
    )
    def test_freq_start_out_of_range_rejected(self, freq_start):
        """Test that freq_start outside [400, 3500] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=3500,
            freq_step=100
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "freq_start" in str(exc_info.value).lower()
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3500),
        freq_end_offset=st.integers(max_value=0)  # End <= start
    )
    def test_freq_end_not_greater_than_start_rejected(self, freq_start, freq_end_offset):
        """Test that freq_end <= freq_start is rejected."""
        freq_end = freq_start + freq_end_offset
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=100
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "freq_end" in str(exc_info.value).lower()
    
    @given(
        freq_step=st.one_of(
            st.integers(max_value=49),  # Below minimum
            st.integers(min_value=501)  # Above maximum
        )
    )
    def test_freq_step_out_of_range_rejected(self, freq_step):
        """Test that freq_step outside [50, 500] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=3500,
            freq_step=freq_step
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "freq_step" in str(exc_info.value).lower()
    
    @given(
        test_duration=st.one_of(
            st.integers(max_value=9),  # Below minimum
            st.integers(min_value=121)  # Above maximum
        )
    )
    def test_test_duration_out_of_range_rejected(self, test_duration):
        """Test that test_duration outside [10, 120] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=3500,
            freq_step=100,
            test_duration=test_duration
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "test_duration" in str(exc_info.value).lower()
    
    @given(
        voltage_start=st.one_of(
            st.integers(max_value=-101),  # Below minimum
            st.integers(min_value=1)  # Above maximum
        )
    )
    def test_voltage_start_out_of_range_rejected(self, voltage_start):
        """Test that voltage_start outside [-100, 0] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=3500,
            freq_step=100,
            voltage_start=voltage_start
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "voltage_start" in str(exc_info.value).lower()
    
    @given(
        voltage_step=st.one_of(
            st.integers(max_value=0),  # Below minimum
            st.integers(min_value=11)  # Above maximum
        )
    )
    def test_voltage_step_out_of_range_rejected(self, voltage_step):
        """Test that voltage_step outside [1, 10] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=3500,
            freq_step=100,
            voltage_step=voltage_step
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "voltage_step" in str(exc_info.value).lower()
    
    @given(
        safety_margin=st.one_of(
            st.integers(max_value=-1),  # Below minimum
            st.integers(min_value=21)  # Above maximum
        )
    )
    def test_safety_margin_out_of_range_rejected(self, safety_margin):
        """Test that safety_margin outside [0, 20] is rejected."""
        config = FrequencyWizardConfig(
            freq_start=400,
            freq_end=3500,
            freq_step=100,
            safety_margin=safety_margin
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "safety_margin" in str(exc_info.value).lower()
    
    @given(
        freq_start=st.integers(min_value=400, max_value=3500),
        freq_end=st.integers(min_value=401, max_value=3500),
        freq_step=st.integers(min_value=50, max_value=500),
        test_duration=st.integers(min_value=10, max_value=120),
        voltage_start=st.integers(min_value=-100, max_value=0),
        voltage_step=st.integers(min_value=1, max_value=10),
        safety_margin=st.integers(min_value=0, max_value=20)
    )
    def test_valid_configuration_accepted(
        self,
        freq_start,
        freq_end,
        freq_step,
        test_duration,
        voltage_start,
        voltage_step,
        safety_margin
    ):
        """Test that all valid configurations are accepted."""
        # Ensure freq_end > freq_start
        if freq_end <= freq_start:
            freq_end = freq_start + 100
        
        config = FrequencyWizardConfig(
            freq_start=freq_start,
            freq_end=freq_end,
            freq_step=freq_step,
            test_duration=test_duration,
            voltage_start=voltage_start,
            voltage_step=voltage_step,
            safety_margin=safety_margin
        )
        
        # Should not raise
        config.validate()
    
    def test_multiple_errors_reported(self):
        """Test that multiple validation errors are reported together."""
        config = FrequencyWizardConfig(
            freq_start=100,  # Invalid: < 400
            freq_end=100,  # Invalid: <= freq_start
            freq_step=1000,  # Invalid: > 500
            test_duration=200,  # Invalid: > 120
            voltage_start=10,  # Invalid: > 0
            voltage_step=20,  # Invalid: > 10
            safety_margin=50  # Invalid: > 20
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        error_msg = str(exc_info.value).lower()
        
        # All errors should be reported
        assert "freq_start" in error_msg
        assert "freq_end" in error_msg
        assert "freq_step" in error_msg
        assert "test_duration" in error_msg
        assert "voltage_start" in error_msg
        assert "voltage_step" in error_msg
        assert "safety_margin" in error_msg
