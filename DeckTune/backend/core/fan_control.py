"""Fan Control system with customizable fan curves.

This module provides fan control functionality through predefined presets
and custom curves, using linear interpolation for smooth temperature-based
fan speed adjustments.
"""

import bisect
import os
import glob
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class FanPoint:
    """Immutable temperature-to-speed mapping point.
    
    Attributes:
        temp: Temperature in Celsius (0-120)
        speed: Fan speed percentage (0-100)
    """
    temp: int
    speed: int
    
    def __post_init__(self):
        """Validate temperature and speed ranges."""
        if not 0 <= self.temp <= 120:
            raise ValueError(f"Temperature {self.temp} out of range [0, 120]")
        if not 0 <= self.speed <= 100:
            raise ValueError(f"Speed {self.speed} out of range [0, 100]")


@dataclass
class FanCurve:
    """Represents a complete fan curve configuration.
    
    Attributes:
        name: Name of the curve
        points: List of FanPoint objects defining the curve
        is_preset: Whether this is a predefined preset curve
    """
    name: str
    points: list[FanPoint]
    is_preset: bool = False
    
    def __post_init__(self):
        """Validate point count and sort points by temperature."""
        if len(self.points) < 3:
            raise ValueError(f"Curve must have at least 3 points, got {len(self.points)}")
        if len(self.points) > 10:
            raise ValueError(f"Curve cannot have more than 10 points, got {len(self.points)}")
        
        # Sort points by temperature using object.__setattr__ since dataclass is mutable
        object.__setattr__(self, 'points', sorted(self.points, key=lambda p: p.temp))


def calculate_fan_speed(current_temp: float, curve_points: list[FanPoint]) -> int:
    """Calculate fan speed using linear interpolation.
    
    This function implements linear interpolation between curve points to determine
    the appropriate fan speed for a given temperature. It handles edge cases where
    the temperature is outside the defined curve range.
    
    Args:
        current_temp: Current temperature in Celsius
        curve_points: List of FanPoint objects (will be sorted by temperature)
    
    Returns:
        Fan speed percentage (0-100) as an integer
    
    Examples:
        >>> points = [FanPoint(40, 0), FanPoint(60, 50), FanPoint(80, 100)]
        >>> calculate_fan_speed(50.0, points)
        25
        >>> calculate_fan_speed(30.0, points)  # Below minimum
        0
        >>> calculate_fan_speed(90.0, points)  # Above maximum
        100
    """
    # Ensure points are sorted by temperature
    sorted_points = sorted(curve_points, key=lambda p: p.temp)
    temps = [p.temp for p in sorted_points]
    
    # Edge case: temperature below minimum point
    if current_temp <= temps[0]:
        return sorted_points[0].speed
    
    # Edge case: temperature above maximum point
    if current_temp >= temps[-1]:
        return sorted_points[-1].speed
    
    # Edge case: temperature exactly on a point
    # bisect_right will give us the index after the exact match
    idx = bisect.bisect_right(temps, current_temp)
    
    # Check if we're exactly on a point (within floating point precision)
    if idx > 0 and abs(temps[idx - 1] - current_temp) < 1e-9:
        return sorted_points[idx - 1].speed
    
    # Linear interpolation between two points
    p1, p2 = sorted_points[idx - 1], sorted_points[idx]
    
    # Linear interpolation formula: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    ratio = (current_temp - p1.temp) / (p2.temp - p1.temp)
    speed = p1.speed + (p2.speed - p1.speed) * ratio
    
    return int(round(speed))



def apply_safety_override(temp: float, calculated_speed: int) -> int:
    """Apply safety overrides to prevent hardware damage.
    
    This function implements emergency temperature handling by overriding
    the calculated fan speed when temperatures reach critical levels.
    
    Args:
        temp: Current temperature in Celsius
        calculated_speed: Speed calculated from the fan curve
    
    Returns:
        Final speed with safety overrides applied (0-100)
    
    Safety Rules:
        - Temperature >= 95°C: Force 100% fan speed (critical override)
        - Temperature >= 90°C: Minimum 80% fan speed (warning boost)
        - Temperature < 90°C: Use calculated speed (normal operation)
    
    Examples:
        >>> apply_safety_override(96.0, 50)
        100
        >>> apply_safety_override(92.0, 50)
        80
        >>> apply_safety_override(85.0, 50)
        50
    """
    # Critical temperature override: force maximum cooling
    if temp >= 95.0:
        return 100
    
    # Warning temperature boost: ensure minimum cooling
    if temp >= 90.0:
        return max(calculated_speed, 80)
    
    # Normal operation: use calculated speed
    return calculated_speed



# Preset fan curve definitions
PRESET_STOCK = FanCurve(
    name="stock",
    points=[
        FanPoint(40, 0),
        FanPoint(60, 40),
        FanPoint(75, 70),
        FanPoint(85, 100)
    ],
    is_preset=True
)

PRESET_SILENT = FanCurve(
    name="silent",
    points=[
        FanPoint(50, 0),
        FanPoint(70, 30),
        FanPoint(85, 60),
        FanPoint(95, 100)
    ],
    is_preset=True
)

PRESET_TURBO = FanCurve(
    name="turbo",
    points=[
        FanPoint(30, 20),
        FanPoint(50, 60),
        FanPoint(65, 80),
        FanPoint(80, 100)
    ],
    is_preset=True
)

PRESETS = {
    "stock": PRESET_STOCK,
    "silent": PRESET_SILENT,
    "turbo": PRESET_TURBO
}


class HwmonInterface:
    """Abstraction for hwmon hardware access.
    
    This class provides an interface to Linux hwmon subsystem for reading
    temperature sensors and controlling PWM fan speed.
    
    Attributes:
        hwmon_path: Base path to hwmon devices (default: /sys/class/hwmon)
        temp_sensor_path: Path to temperature sensor file (discovered)
        pwm_control_path: Path to PWM control file (discovered)
    """
    
    def __init__(self, hwmon_path: str = "/sys/class/hwmon"):
        """Initialize hwmon interface and discover devices.
        
        Args:
            hwmon_path: Base path to hwmon devices
        """
        self.hwmon_path = hwmon_path
        self.temp_sensor_path: Optional[str] = None
        self.pwm_control_path: Optional[str] = None
        self._discover_devices()
    
    def _discover_devices(self) -> None:
        """Discover temperature sensor and PWM control paths.
        
        Scans the hwmon directory structure to locate available temperature
        sensors and PWM control interfaces.
        """
        self.temp_sensor_path = self._find_temp_sensor()
        self.pwm_control_path = self._find_pwm_control()
    
    def _find_temp_sensor(self) -> Optional[str]:
        """Locate temperature sensor in hwmon filesystem.
        
        Searches for temp*_input files in hwmon devices. Prioritizes
        sensors labeled as CPU or package temperature.
        
        Returns:
            Path to temperature sensor file, or None if not found
        """
        if not os.path.exists(self.hwmon_path):
            return None
        
        # Search all hwmon devices
        hwmon_devices = glob.glob(os.path.join(self.hwmon_path, "hwmon*"))
        
        for device in sorted(hwmon_devices):
            # Look for temperature input files
            temp_files = glob.glob(os.path.join(device, "temp*_input"))
            
            for temp_file in sorted(temp_files):
                # Check if this sensor has a label
                label_file = temp_file.replace("_input", "_label")
                if os.path.exists(label_file):
                    try:
                        with open(label_file, 'r') as f:
                            label = f.read().strip().lower()
                            # Prioritize CPU/package sensors
                            if 'cpu' in label or 'package' in label or 'tctl' in label:
                                return temp_file
                    except (OSError, PermissionError):
                        continue
                
                # If no label or not CPU, still consider it as fallback
                # Verify we can read it
                try:
                    with open(temp_file, 'r') as f:
                        f.read()
                    # Return first readable sensor as fallback
                    if self.temp_sensor_path is None:
                        return temp_file
                except (OSError, PermissionError):
                    continue
        
        return None
    
    def _find_pwm_control(self) -> Optional[str]:
        """Locate PWM control interface in hwmon filesystem.
        
        Searches for pwm* files in hwmon devices that support manual control.
        
        Returns:
            Path to PWM control file, or None if not found
        """
        if not os.path.exists(self.hwmon_path):
            return None
        
        # Search all hwmon devices
        hwmon_devices = glob.glob(os.path.join(self.hwmon_path, "hwmon*"))
        
        for device in sorted(hwmon_devices):
            # Look for PWM control files (pwm1, pwm2, etc.)
            pwm_files = glob.glob(os.path.join(device, "pwm[0-9]"))
            
            for pwm_file in sorted(pwm_files):
                # Check if PWM enable file exists (for manual control)
                pwm_enable_file = pwm_file + "_enable"
                
                # Verify we can write to the PWM file
                try:
                    # Try to read current value first
                    with open(pwm_file, 'r') as f:
                        f.read()
                    
                    # Check if we have write permission (without actually writing)
                    if os.access(pwm_file, os.W_OK):
                        return pwm_file
                except (OSError, PermissionError):
                    continue
        
        return None
    
    def read_temperature(self) -> Optional[float]:
        """Read current temperature from hwmon sensor.
        
        Reads temperature from the discovered sensor. hwmon reports
        temperature in millidegrees Celsius.
        
        Returns:
            Temperature in Celsius, or None on failure
        """
        if self.temp_sensor_path is None:
            return None
        
        try:
            with open(self.temp_sensor_path, 'r') as f:
                # hwmon reports temperature in millidegrees Celsius
                millidegrees = int(f.read().strip())
                return millidegrees / 1000.0
        except (OSError, PermissionError, ValueError, FileNotFoundError):
            return None
    
    def write_pwm(self, speed_percent: int) -> bool:
        """Write fan speed to PWM interface.
        
        Converts speed percentage to PWM value and writes to hwmon.
        PWM values range from 0-255, where 0 is off and 255 is maximum.
        
        Args:
            speed_percent: Fan speed percentage (0-100)
        
        Returns:
            True if write succeeded, False otherwise
        """
        if self.pwm_control_path is None:
            return False
        
        if not 0 <= speed_percent <= 100:
            return False
        
        # Convert percentage (0-100) to PWM value (0-255)
        pwm_value = int(round(speed_percent * 255 / 100))
        
        try:
            with open(self.pwm_control_path, 'w') as f:
                f.write(str(pwm_value))
            return True
        except (OSError, PermissionError):
            return False
    
    def read_current_pwm(self) -> Optional[int]:
        """Read current PWM value from hwmon.
        
        Reads the current PWM value and converts it to percentage.
        
        Returns:
            Current fan speed percentage (0-100), or None on failure
        """
        if self.pwm_control_path is None:
            return None
        
        try:
            with open(self.pwm_control_path, 'r') as f:
                pwm_value = int(f.read().strip())
                # Convert PWM value (0-255) to percentage (0-100)
                return int(round(pwm_value * 100 / 255))
        except (OSError, PermissionError, ValueError, FileNotFoundError):
            return None
    
    def is_available(self) -> bool:
        """Check if hardware interface is available.
        
        Returns:
            True if both temperature sensor and PWM control are available
        """
        return self.temp_sensor_path is not None and self.pwm_control_path is not None



class FanControlService:
    """Core fan control service with configuration persistence.
    
    This service manages fan control operations including preset management,
    custom curve handling, and persistent configuration storage.
    
    Attributes:
        hwmon: Hardware interface for temperature and PWM control
        config_path: Path to configuration file
        active_curve: Currently active fan curve
        custom_curves: Dictionary of user-defined custom curves
    """
    
    # Configuration file schema version
    CONFIG_VERSION = 1
    
    def __init__(self, hwmon_interface: HwmonInterface, config_path: Optional[str] = None):
        """Initialize fan control service.
        
        Args:
            hwmon_interface: Hardware interface for fan control
            config_path: Path to configuration file (default: ~/.config/decktune/fan_control.json)
        """
        self.hwmon = hwmon_interface
        
        # Set default config path if not provided
        if config_path is None:
            config_dir = Path.home() / ".config" / "decktune"
            self.config_path = str(config_dir / "fan_control.json")
        else:
            self.config_path = config_path
        
        self.active_curve: Optional[FanCurve] = None
        self.active_curve_type: str = "preset"  # "preset" or "custom"
        self.custom_curves: dict[str, FanCurve] = {}
        
        # Monitoring thread attributes
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._monitoring_active = False
        self._last_applied_speed: Optional[int] = None
        self._current_temp: Optional[float] = None
        self._target_speed: Optional[int] = None
        self._consecutive_failures = 0
        self._last_update: Optional[datetime] = None
        
        # Load configuration on initialization
        self._load_config()
    
    def _save_config(self) -> bool:
        """Save current configuration to JSON file.
        
        Serializes the active curve and custom curves to persistent storage.
        Creates the configuration directory if it doesn't exist.
        
        Returns:
            True if save succeeded, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Build configuration dictionary
            config = {
                "version": self.CONFIG_VERSION,
                "active_curve": self.active_curve.name if self.active_curve else "stock",
                "active_curve_type": self.active_curve_type,
                "custom_curves": {},
                "last_applied": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Serialize custom curves
            for name, curve in self.custom_curves.items():
                config["custom_curves"][name] = {
                    "name": curve.name,
                    "points": [
                        {"temp": point.temp, "speed": point.speed}
                        for point in curve.points
                    ]
                }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = self.config_path + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Set proper permissions (0600 - owner read/write only)
            os.chmod(temp_path, 0o600)
            
            # Atomic rename
            os.replace(temp_path, self.config_path)
            
            return True
            
        except (OSError, IOError, PermissionError) as e:
            # Log error but don't crash
            print(f"Error saving fan control configuration: {e}")
            return False
    
    def _load_config(self) -> None:
        """Load configuration from JSON file.
        
        Reads and parses the configuration file, loading the active curve
        and custom curves. Falls back to Stock preset if file is missing
        or corrupted.
        """
        # Default to Stock preset
        self.active_curve = PRESET_STOCK
        self.active_curve_type = "preset"
        self.custom_curves = {}
        
        # Check if config file exists
        if not os.path.exists(self.config_path):
            # No config file, use defaults
            return
        
        try:
            # Read and parse JSON
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate configuration structure
            if not isinstance(config, dict):
                raise ValueError("Invalid configuration format")
            
            if "version" not in config or "active_curve" not in config:
                raise ValueError("Missing required configuration fields")
            
            # Load custom curves
            if "custom_curves" in config and isinstance(config["custom_curves"], dict):
                for curve_name, curve_data in config["custom_curves"].items():
                    try:
                        # Parse curve points
                        points = [
                            FanPoint(temp=pt["temp"], speed=pt["speed"])
                            for pt in curve_data["points"]
                        ]
                        
                        # Create FanCurve object
                        curve = FanCurve(
                            name=curve_data["name"],
                            points=points,
                            is_preset=False
                        )
                        
                        self.custom_curves[curve_name] = curve
                        
                    except (KeyError, ValueError, TypeError) as e:
                        # Skip invalid custom curve
                        print(f"Skipping invalid custom curve '{curve_name}': {e}")
                        continue
            
            # Load active curve
            active_curve_name = config["active_curve"]
            active_curve_type = config.get("active_curve_type", "preset")
            
            if active_curve_type == "preset":
                # Load preset curve
                if active_curve_name in PRESETS:
                    self.active_curve = PRESETS[active_curve_name]
                    self.active_curve_type = "preset"
                else:
                    # Unknown preset, fall back to Stock
                    print(f"Unknown preset '{active_curve_name}', using Stock")
                    self.active_curve = PRESET_STOCK
                    self.active_curve_type = "preset"
            
            elif active_curve_type == "custom":
                # Load custom curve
                if active_curve_name in self.custom_curves:
                    self.active_curve = self.custom_curves[active_curve_name]
                    self.active_curve_type = "custom"
                else:
                    # Custom curve not found, fall back to Stock
                    print(f"Custom curve '{active_curve_name}' not found, using Stock")
                    self.active_curve = PRESET_STOCK
                    self.active_curve_type = "preset"
            
            else:
                # Unknown curve type, fall back to Stock
                print(f"Unknown curve type '{active_curve_type}', using Stock")
                self.active_curve = PRESET_STOCK
                self.active_curve_type = "preset"
        
        except (OSError, IOError, json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            # Corrupted or invalid config file, fall back to Stock preset
            print(f"Error loading fan control configuration: {e}")
            print("Falling back to Stock preset")
            self.active_curve = PRESET_STOCK
            self.active_curve_type = "preset"
            self.custom_curves = {}
    
    # Preset Management Methods
    
    def apply_preset(self, preset_name: str) -> bool:
        """Load and activate a predefined preset curve.
        
        Args:
            preset_name: Name of the preset ("stock", "silent", or "turbo")
        
        Returns:
            True if preset was applied successfully, False otherwise
        """
        if preset_name not in PRESETS:
            return False
        
        self.active_curve = PRESETS[preset_name]
        self.active_curve_type = "preset"
        
        # Persist the selection
        return self._save_config()
    
    def get_available_presets(self) -> list[str]:
        """Get list of available preset names.
        
        Returns:
            List of preset names
        """
        return list(PRESETS.keys())
    
    # Custom Curve Management Methods
    
    def create_custom_curve(self, name: str, points: list[FanPoint]) -> bool:
        """Create and save a custom fan curve.
        
        Validates the curve and adds it to the custom curves collection.
        
        Args:
            name: Name for the custom curve
            points: List of FanPoint objects defining the curve
        
        Returns:
            True if curve was created successfully, False otherwise
        """
        try:
            # Create FanCurve object (this validates point count and sorts)
            curve = FanCurve(name=name, points=points, is_preset=False)
            
            # Add to custom curves
            self.custom_curves[name] = curve
            
            # Persist to configuration
            return self._save_config()
            
        except (ValueError, TypeError) as e:
            print(f"Error creating custom curve '{name}': {e}")
            return False
    
    def load_custom_curve(self, name: str) -> bool:
        """Load and activate a custom curve.
        
        Args:
            name: Name of the custom curve to load
        
        Returns:
            True if curve was loaded successfully, False otherwise
        """
        if name not in self.custom_curves:
            return False
        
        self.active_curve = self.custom_curves[name]
        self.active_curve_type = "custom"
        
        # Persist the selection
        return self._save_config()
    
    def delete_custom_curve(self, name: str) -> bool:
        """Delete a custom curve.
        
        If the deleted curve is currently active, falls back to Stock preset.
        
        Args:
            name: Name of the custom curve to delete
        
        Returns:
            True if curve was deleted successfully, False otherwise
        """
        if name not in self.custom_curves:
            return False
        
        # Remove from custom curves
        del self.custom_curves[name]
        
        # If this was the active curve, fall back to Stock preset
        if self.active_curve_type == "custom" and self.active_curve and self.active_curve.name == name:
            self.active_curve = PRESET_STOCK
            self.active_curve_type = "preset"
        
        # Persist changes
        return self._save_config()
    
    def list_custom_curves(self) -> list[str]:
        """Get list of custom curve names.
        
        Returns:
            List of custom curve names
        """
        return list(self.custom_curves.keys())
    
    # Monitoring and Control Methods
    
    def start_monitoring(self) -> None:
        """Start the background monitoring thread.
        
        Starts a daemon thread that continuously monitors temperature
        and adjusts fan speed according to the active curve.
        """
        if self._monitoring_active:
            return
        
        self.stop_event.clear()
        self._monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop the background monitoring thread gracefully.
        
        Signals the monitoring thread to stop and waits for it to finish.
        """
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop that adjusts fan speed based on temperature.
        
        Runs continuously until stop_event is set. Reads temperature every second,
        calculates target speed, applies safety overrides, and updates fan speed
        if it changed by 2% or more.
        
        Implements exponential backoff on exceptions to prevent tight error loops.
        """
        backoff_delay = 1.0  # Start with 1 second
        max_backoff = 30.0   # Maximum 30 seconds
        
        while not self.stop_event.is_set():
            try:
                # Read current temperature
                temp = self.hwmon.read_temperature()
                
                if temp is None:
                    # Temperature read failed, wait and retry
                    time.sleep(1.0)
                    continue
                
                self._current_temp = temp
                
                # Calculate target speed using active curve
                if self.active_curve is None:
                    # No active curve, wait and retry
                    time.sleep(1.0)
                    continue
                
                calculated_speed = calculate_fan_speed(temp, self.active_curve.points)
                
                # Apply safety overrides
                target_speed = apply_safety_override(temp, calculated_speed)
                self._target_speed = target_speed
                
                # Apply fan speed if changed by >= 2% or first application
                if self._last_applied_speed is None or abs(target_speed - self._last_applied_speed) >= 2:
                    success = self._apply_fan_speed(target_speed)
                    
                    if success:
                        # Reset backoff on success
                        backoff_delay = 1.0
                    else:
                        # Increment backoff on failure
                        backoff_delay = min(backoff_delay * 2, max_backoff)
                
                # Update timestamp
                self._last_update = datetime.now(timezone.utc)
                
                # Wait 1 second before next iteration
                self.stop_event.wait(1.0)
                
            except Exception as e:
                # Catch any unexpected exceptions to prevent thread crash
                print(f"Error in fan control monitoring loop: {e}")
                
                # Exponential backoff
                self.stop_event.wait(backoff_delay)
                backoff_delay = min(backoff_delay * 2, max_backoff)
    
    def _apply_fan_speed(self, speed: int) -> bool:
        """Apply fan speed to hardware.
        
        Writes the speed to the PWM interface and tracks consecutive failures.
        Disables automatic control after 3 consecutive failures.
        
        Args:
            speed: Target fan speed percentage (0-100)
        
        Returns:
            True if speed was applied successfully, False otherwise
        """
        success = self.hwmon.write_pwm(speed)
        
        if success:
            self._last_applied_speed = speed
            self._consecutive_failures = 0
            return True
        else:
            self._consecutive_failures += 1
            
            # Disable automatic control after 3 failures
            if self._consecutive_failures >= 3:
                print(f"Fan control disabled after {self._consecutive_failures} consecutive failures")
                self._monitoring_active = False
                self.stop_event.set()
            
            return False
    
    def get_current_status(self) -> dict:
        """Get current fan control status.
        
        Returns a dictionary containing current temperature, fan speeds,
        active curve information, and system status.
        
        Returns:
            Dictionary with status information:
                - current_temp: Current temperature in Celsius (or None)
                - current_speed: Current fan speed percentage (or None)
                - target_speed: Calculated target speed (or None)
                - active_curve: Name of active curve (or None)
                - curve_type: Type of active curve ("preset" or "custom")
                - monitoring_active: Whether monitoring is running
                - hwmon_available: Whether hardware interface is available
                - last_update: ISO timestamp of last update (or None)
        """
        # Read current PWM speed
        current_speed = self.hwmon.read_current_pwm()
        
        return {
            "current_temp": self._current_temp,
            "current_speed": current_speed,
            "target_speed": self._target_speed,
            "active_curve": self.active_curve.name if self.active_curve else None,
            "curve_type": self.active_curve_type,
            "monitoring_active": self._monitoring_active,
            "hwmon_available": self.hwmon.is_available(),
            "last_update": self._last_update.isoformat().replace('+00:00', 'Z') if self._last_update else None
        }
