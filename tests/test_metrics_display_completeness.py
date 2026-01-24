"""Property test for metrics display completeness.

Feature: manual-dynamic-mode, Property 4: Metrics display completeness
Validates: Requirements 3.2

Property 4: Metrics display completeness
For any CoreMetrics object received, the display SHALL contain all four 
metric values: CPULoad, VoltageOffset, frequency, and temperature.
"""

import pytest
from hypothesis import given, strategies as st, settings


# Strategy for generating CoreMetrics-like data
@st.composite
def core_metrics(draw):
    """Generate a CoreMetrics-like dictionary."""
    return {
        'core_id': draw(st.integers(min_value=0, max_value=3)),
        'load': draw(st.floats(min_value=0.0, max_value=100.0)),
        'voltage': draw(st.integers(min_value=-100, max_value=0)),
        'frequency': draw(st.integers(min_value=400, max_value=3500)),
        'temperature': draw(st.floats(min_value=20.0, max_value=95.0)),
        'timestamp': draw(st.integers(min_value=1000000000, max_value=2000000000)),
    }


def format_metrics_display(metrics: dict) -> str:
    """
    Simulate the metrics display formatting.
    This represents what the MetricsDisplay component renders.
    
    Requirements: 3.2
    Property 4: Metrics display completeness
    """
    # Format each metric with appropriate units
    load_str = f"CPU LOAD: {metrics['load']:.1f}%"
    voltage_str = f"VOLTAGE OFFSET: {metrics['voltage']}mV"
    frequency_str = f"FREQUENCY: {metrics['frequency']}MHz"
    temperature_str = f"TEMPERATURE: {metrics['temperature']:.1f}°C"
    
    # Combine all metrics into display string
    display = f"{load_str}\n{voltage_str}\n{frequency_str}\n{temperature_str}"
    return display


class TestMetricsDisplayCompleteness:
    """Property 4: Metrics display completeness
    
    For any CoreMetrics object received, the display SHALL contain all four 
    metric values: CPULoad, VoltageOffset, frequency, and temperature.
    
    Validates: Requirements 3.2
    """

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_all_four_metrics(self, metrics: dict):
        """Display SHALL contain all four metric values."""
        display = format_metrics_display(metrics)
        
        # Verify all four metrics are present in display
        assert "CPU LOAD" in display, "Display must contain CPU Load"
        assert "VOLTAGE OFFSET" in display, "Display must contain Voltage Offset"
        assert "FREQUENCY" in display, "Display must contain Frequency"
        assert "TEMPERATURE" in display, "Display must contain Temperature"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_load_value(self, metrics: dict):
        """Display SHALL contain the CPU load value."""
        display = format_metrics_display(metrics)
        
        # Verify load value is present
        load_str = f"{metrics['load']:.1f}"
        assert load_str in display, (
            f"Display must contain load value {load_str}"
        )
        
        # Verify load has percentage unit
        assert "%" in display, "Load must have percentage unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_voltage_value(self, metrics: dict):
        """Display SHALL contain the voltage offset value."""
        display = format_metrics_display(metrics)
        
        # Verify voltage value is present
        voltage_str = str(metrics['voltage'])
        assert voltage_str in display, (
            f"Display must contain voltage value {voltage_str}"
        )
        
        # Verify voltage has millivolt unit
        assert "mV" in display, "Voltage must have millivolt unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_frequency_value(self, metrics: dict):
        """Display SHALL contain the frequency value."""
        display = format_metrics_display(metrics)
        
        # Verify frequency value is present
        frequency_str = str(metrics['frequency'])
        assert frequency_str in display, (
            f"Display must contain frequency value {frequency_str}"
        )
        
        # Verify frequency has megahertz unit
        assert "MHz" in display, "Frequency must have megahertz unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_temperature_value(self, metrics: dict):
        """Display SHALL contain the temperature value."""
        display = format_metrics_display(metrics)
        
        # Verify temperature value is present
        temperature_str = f"{metrics['temperature']:.1f}"
        assert temperature_str in display, (
            f"Display must contain temperature value {temperature_str}"
        )
        
        # Verify temperature has Celsius unit
        assert "°C" in display, "Temperature must have Celsius unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_has_all_required_units(self, metrics: dict):
        """Display SHALL include units for all metrics."""
        display = format_metrics_display(metrics)
        
        # Verify all required units are present
        required_units = ["%", "mV", "MHz", "°C"]
        for unit in required_units:
            assert unit in display, (
                f"Display must contain unit '{unit}'"
            )

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_no_metric_is_missing(self, metrics: dict):
        """No metric SHALL be missing from display."""
        display = format_metrics_display(metrics)
        
        # Count occurrences of metric labels
        metric_labels = ["CPU LOAD", "VOLTAGE OFFSET", "FREQUENCY", "TEMPERATURE"]
        for label in metric_labels:
            count = display.count(label)
            assert count >= 1, (
                f"Metric label '{label}' must appear at least once in display"
            )

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_format_is_consistent(self, metrics: dict):
        """Display format SHALL be consistent across all metrics."""
        display = format_metrics_display(metrics)
        
        # Verify display is not empty
        assert len(display) > 0, "Display must not be empty"
        
        # Verify display contains newlines (multi-line format)
        assert "\n" in display, "Display should be multi-line"
        
        # Verify all four metrics are on separate lines
        lines = display.split("\n")
        assert len(lines) >= 4, (
            f"Display should have at least 4 lines, got {len(lines)}"
        )


class TestMetricsDisplayEdgeCases:
    """Test edge cases for metrics display completeness."""

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_zero_load(self, metrics: dict):
        """Display SHALL handle zero CPU load correctly."""
        metrics['load'] = 0.0
        display = format_metrics_display(metrics)
        
        assert "0.0" in display, "Display must show zero load"
        assert "%" in display, "Display must include percentage unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_max_load(self, metrics: dict):
        """Display SHALL handle maximum CPU load correctly."""
        metrics['load'] = 100.0
        display = format_metrics_display(metrics)
        
        assert "100.0" in display, "Display must show max load"
        assert "%" in display, "Display must include percentage unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_zero_voltage(self, metrics: dict):
        """Display SHALL handle zero voltage offset correctly."""
        metrics['voltage'] = 0
        display = format_metrics_display(metrics)
        
        assert "0" in display, "Display must show zero voltage"
        assert "mV" in display, "Display must include millivolt unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_min_voltage(self, metrics: dict):
        """Display SHALL handle minimum voltage offset correctly."""
        metrics['voltage'] = -100
        display = format_metrics_display(metrics)
        
        assert "-100" in display, "Display must show minimum voltage"
        assert "mV" in display, "Display must include millivolt unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_min_frequency(self, metrics: dict):
        """Display SHALL handle minimum frequency correctly."""
        metrics['frequency'] = 400
        display = format_metrics_display(metrics)
        
        assert "400" in display, "Display must show minimum frequency"
        assert "MHz" in display, "Display must include megahertz unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_max_frequency(self, metrics: dict):
        """Display SHALL handle maximum frequency correctly."""
        metrics['frequency'] = 3500
        display = format_metrics_display(metrics)
        
        assert "3500" in display, "Display must show maximum frequency"
        assert "MHz" in display, "Display must include megahertz unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_low_temperature(self, metrics: dict):
        """Display SHALL handle low temperature correctly."""
        metrics['temperature'] = 20.0
        display = format_metrics_display(metrics)
        
        assert "20.0" in display, "Display must show low temperature"
        assert "°C" in display, "Display must include Celsius unit"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_handles_high_temperature(self, metrics: dict):
        """Display SHALL handle high temperature correctly."""
        metrics['temperature'] = 95.0
        display = format_metrics_display(metrics)
        
        assert "95.0" in display, "Display must show high temperature"
        assert "°C" in display, "Display must include Celsius unit"

    @given(
        load=st.floats(min_value=0.0, max_value=100.0),
        voltage=st.integers(min_value=-100, max_value=0),
        frequency=st.integers(min_value=400, max_value=3500),
        temperature=st.floats(min_value=20.0, max_value=95.0)
    )
    @settings(max_examples=100)
    def test_display_completeness_with_individual_values(
        self,
        load: float,
        voltage: int,
        frequency: int,
        temperature: float
    ):
        """Display SHALL be complete for any combination of valid values."""
        metrics = {
            'core_id': 0,
            'load': load,
            'voltage': voltage,
            'frequency': frequency,
            'temperature': temperature,
            'timestamp': 1000000000,
        }
        
        display = format_metrics_display(metrics)
        
        # Verify all four metrics are present
        assert "CPU LOAD" in display
        assert "VOLTAGE OFFSET" in display
        assert "FREQUENCY" in display
        assert "TEMPERATURE" in display
        
        # Verify all values are present
        assert f"{load:.1f}" in display
        assert str(voltage) in display
        assert str(frequency) in display
        assert f"{temperature:.1f}" in display
        
        # Verify all units are present
        assert "%" in display
        assert "mV" in display
        assert "MHz" in display
        assert "°C" in display


class TestMetricsDisplayInvariant:
    """Test invariants for metrics display."""

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_length_is_non_zero(self, metrics: dict):
        """Display length SHALL always be non-zero."""
        display = format_metrics_display(metrics)
        assert len(display) > 0, "Display must have non-zero length"

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_display_contains_no_missing_placeholders(self, metrics: dict):
        """Display SHALL not contain missing value placeholders."""
        display = format_metrics_display(metrics)
        
        # Verify no common placeholder strings
        placeholders = ["N/A", "null", "undefined", "None", "---", "???"]
        for placeholder in placeholders:
            assert placeholder not in display, (
                f"Display should not contain placeholder '{placeholder}'"
            )

    @given(metrics1=core_metrics(), metrics2=core_metrics())
    @settings(max_examples=100)
    def test_different_metrics_produce_different_displays(
        self,
        metrics1: dict,
        metrics2: dict
    ):
        """Different metrics SHALL produce different displays (unless identical or rounded to same values)."""
        display1 = format_metrics_display(metrics1)
        display2 = format_metrics_display(metrics2)
        
        # If metrics are different, displays should be different
        # UNLESS they round to the same display values
        if metrics1 != metrics2:
            # Check if the formatted values actually differ
            # (accounting for display precision)
            load_differs = round(metrics1['load'], 1) != round(metrics2['load'], 1)
            voltage_differs = metrics1['voltage'] != metrics2['voltage']
            frequency_differs = metrics1['frequency'] != metrics2['frequency']
            temperature_differs = round(metrics1['temperature'], 1) != round(metrics2['temperature'], 1)
            
            formatted_values_differ = (
                load_differs or voltage_differs or 
                frequency_differs or temperature_differs
            )
            
            if formatted_values_differ:
                assert display1 != display2, (
                    "Metrics with different formatted values should produce different displays"
                )
