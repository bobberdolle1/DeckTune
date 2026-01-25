"""
Frequency-based voltage curve data model.

This module provides data structures and algorithms for managing frequency-dependent
voltage curves used in the frequency-based voltage wizard.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json
from pathlib import Path


@dataclass
class FrequencyPoint:
    """Single point in frequency-voltage curve.
    
    Attributes:
        frequency_mhz: CPU frequency in MHz
        voltage_mv: Voltage offset in mV (negative values, e.g., -30)
        stable: Whether this voltage was stable at this frequency
        test_duration: Duration in seconds that this point was tested
        timestamp: Unix timestamp when this point was tested
    """
    frequency_mhz: int
    voltage_mv: int
    stable: bool
    test_duration: int
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrequencyPoint':
        """Create FrequencyPoint from dictionary."""
        return cls(
            frequency_mhz=data['frequency_mhz'],
            voltage_mv=data['voltage_mv'],
            stable=data['stable'],
            test_duration=data['test_duration'],
            timestamp=data['timestamp']
        )


@dataclass
class FrequencyCurve:
    """Complete frequency-voltage curve for a CPU core.
    
    Attributes:
        core_id: CPU core identifier
        points: List of frequency-voltage points (must be sorted by frequency)
        created_at: Unix timestamp when curve was created
        wizard_config: Configuration used to generate this curve
    """
    core_id: int
    points: List[FrequencyPoint]
    created_at: float
    wizard_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_voltage_for_frequency(self, freq_mhz: int) -> int:
        """Calculate voltage offset for given frequency using linear interpolation.
        
        Uses linear interpolation between surrounding frequency points.
        For frequencies outside the tested range, clamps to boundary values.
        
        Args:
            freq_mhz: Target frequency in MHz
            
        Returns:
            Voltage offset in mV (negative value)
            
        Raises:
            ValueError: If curve has no points
        """
        if not self.points:
            raise ValueError("Cannot interpolate voltage from empty curve")
        
        # Handle single point case
        if len(self.points) == 1:
            return self.points[0].voltage_mv
        
        # Boundary clamping: frequency below minimum
        if freq_mhz <= self.points[0].frequency_mhz:
            return self.points[0].voltage_mv
        
        # Boundary clamping: frequency above maximum
        if freq_mhz >= self.points[-1].frequency_mhz:
            return self.points[-1].voltage_mv
        
        # Find surrounding points for interpolation
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            if p1.frequency_mhz <= freq_mhz <= p2.frequency_mhz:
                # Linear interpolation: v = v1 + (v2 - v1) * (f - f1) / (f2 - f1)
                freq_range = p2.frequency_mhz - p1.frequency_mhz
                voltage_range = p2.voltage_mv - p1.voltage_mv
                freq_offset = freq_mhz - p1.frequency_mhz
                
                # Handle case where two points have same frequency (shouldn't happen with validation)
                if freq_range == 0:
                    return p1.voltage_mv
                
                interpolated_voltage = p1.voltage_mv + (voltage_range * freq_offset) // freq_range
                return interpolated_voltage
        
        # Should never reach here if points are sorted
        raise ValueError(f"Failed to interpolate voltage for frequency {freq_mhz} MHz")
    
    def validate(self) -> bool:
        """Validate curve integrity.
        
        Checks:
        - Points are sorted by frequency in ascending order
        - All voltages are in valid range [-100, 0] mV
        - No duplicate frequencies
        
        Returns:
            True if curve is valid
            
        Raises:
            ValueError: If validation fails, with descriptive error message
        """
        if not self.points:
            raise ValueError("Curve has no points")
        
        # Check voltage range
        for point in self.points:
            if not (-100 <= point.voltage_mv <= 0):
                raise ValueError(
                    f"Voltage {point.voltage_mv} mV at {point.frequency_mhz} MHz "
                    f"is outside valid range [-100, 0] mV"
                )
        
        # Check sorted order and no duplicates
        for i in range(len(self.points) - 1):
            curr_freq = self.points[i].frequency_mhz
            next_freq = self.points[i + 1].frequency_mhz
            
            if curr_freq >= next_freq:
                if curr_freq == next_freq:
                    raise ValueError(
                        f"Duplicate frequency {curr_freq} MHz found in curve"
                    )
                else:
                    raise ValueError(
                        f"Frequencies not in ascending order: "
                        f"{curr_freq} MHz followed by {next_freq} MHz"
                    )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize curve to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            'core_id': self.core_id,
            'points': [point.to_dict() for point in self.points],
            'created_at': self.created_at,
            'wizard_config': self.wizard_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrequencyCurve':
        """Deserialize curve from dictionary.
        
        Args:
            data: Dictionary containing curve data
            
        Returns:
            FrequencyCurve instance
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If curve validation fails
        """
        points = [FrequencyPoint.from_dict(p) for p in data['points']]
        
        curve = cls(
            core_id=data['core_id'],
            points=points,
            created_at=data['created_at'],
            wizard_config=data.get('wizard_config', {})
        )
        
        # Validate after deserialization
        curve.validate()
        
        return curve
    
    def to_json(self) -> str:
        """Serialize curve to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FrequencyCurve':
        """Deserialize curve from JSON string.
        
        Args:
            json_str: JSON string containing curve data
            
        Returns:
            FrequencyCurve instance
            
        Raises:
            json.JSONDecodeError: If JSON is malformed
            ValueError: If curve validation fails
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: Path) -> None:
        """Save curve to JSON file.
        
        Args:
            filepath: Path to output file
        """
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'FrequencyCurve':
        """Load curve from JSON file.
        
        Args:
            filepath: Path to input file
            
        Returns:
            FrequencyCurve instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is malformed
            ValueError: If curve validation fails
        """
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
