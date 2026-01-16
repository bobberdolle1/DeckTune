//! Low-level hwmon sysfs interface for fan control
//!
//! Provides direct access to Steam Deck fan hardware via /sys/class/hwmon.
//! Automatically discovers the correct hwmon device by name (jupiter/galileo).

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

/// Base path for hwmon devices
pub const HWMON_PATH: &str = "/sys/class/hwmon";

/// Fan control mode
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FanMode {
    /// BIOS/EC automatic control (pwm1_enable = 2)
    Auto,
    /// Manual PWM control (pwm1_enable = 1)
    Manual,
}

impl FanMode {
    /// Get the sysfs value for this mode
    pub fn as_sysfs_value(&self) -> u8 {
        match self {
            FanMode::Auto => 2,
            FanMode::Manual => 1,
        }
    }

    /// Parse from sysfs value
    pub fn from_sysfs_value(value: u8) -> Option<Self> {
        match value {
            1 => Some(FanMode::Manual),
            2 => Some(FanMode::Auto),
            _ => None,
        }
    }
}

/// Errors from hwmon operations
#[derive(Debug)]
pub enum HwmonError {
    /// Device not found
    DeviceNotFound(String),
    /// I/O error reading/writing sysfs
    IoError(io::Error),
    /// Invalid value read from sysfs
    ParseError(String),
    /// Permission denied (not root)
    PermissionDenied,
    /// Device doesn't support required features
    UnsupportedDevice(String),
}

impl std::fmt::Display for HwmonError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            HwmonError::DeviceNotFound(s) => write!(f, "Hwmon device not found: {}", s),
            HwmonError::IoError(e) => write!(f, "I/O error: {}", e),
            HwmonError::ParseError(s) => write!(f, "Parse error: {}", s),
            HwmonError::PermissionDenied => write!(f, "Permission denied (run as root)"),
            HwmonError::UnsupportedDevice(s) => write!(f, "Unsupported device: {}", s),
        }
    }
}

impl std::error::Error for HwmonError {}

impl From<io::Error> for HwmonError {
    fn from(e: io::Error) -> Self {
        if e.kind() == io::ErrorKind::PermissionDenied {
            HwmonError::PermissionDenied
        } else {
            HwmonError::IoError(e)
        }
    }
}

/// Steam Deck hwmon device handle
///
/// Provides safe access to fan control via sysfs. Implements Drop
/// to return control to BIOS on cleanup.
#[derive(Debug)]
pub struct HwmonDevice {
    /// Path to hwmon device (e.g., /sys/class/hwmon/hwmon5)
    path: PathBuf,
    /// Device name (jupiter or galileo)
    name: String,
    /// Whether we took manual control (for Drop)
    took_control: bool,
}

impl HwmonDevice {
    /// Open an hwmon device by path
    ///
    /// # Arguments
    /// * `path` - Path to hwmon device directory
    ///
    /// # Errors
    /// Returns error if device doesn't exist or lacks required files
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self, HwmonError> {
        let path = path.as_ref().to_path_buf();

        // Read device name
        let name_path = path.join("name");
        let name = fs::read_to_string(&name_path)
            .map_err(|_| HwmonError::DeviceNotFound(format!("No name file at {:?}", name_path)))?
            .trim()
            .to_string();

        // Verify required files exist
        let required_files = ["pwm1", "pwm1_enable", "temp1_input"];
        for file in &required_files {
            let file_path = path.join(file);
            if !file_path.exists() {
                return Err(HwmonError::UnsupportedDevice(format!(
                    "Missing required file: {}",
                    file
                )));
            }
        }

        Ok(HwmonDevice {
            path,
            name,
            took_control: false,
        })
    }

    /// Get device name
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get device path
    pub fn path(&self) -> &Path {
        &self.path
    }

    /// Check if this is a Steam Deck fan controller
    pub fn is_steam_deck(&self) -> bool {
        self.name == "jupiter" || self.name == "galileo"
    }

    /// Read current temperature in millidegrees Celsius
    ///
    /// # Returns
    /// Temperature in millidegrees (e.g., 45000 = 45°C)
    pub fn read_temp_raw(&self) -> Result<i32, HwmonError> {
        let content = fs::read_to_string(self.path.join("temp1_input"))?;
        content
            .trim()
            .parse()
            .map_err(|_| HwmonError::ParseError(format!("Invalid temp value: {}", content.trim())))
    }

    /// Read current temperature in degrees Celsius
    pub fn read_temp_c(&self) -> Result<i32, HwmonError> {
        Ok(self.read_temp_raw()? / 1000)
    }

    /// Read current PWM value (0-255)
    pub fn read_pwm(&self) -> Result<u8, HwmonError> {
        let content = fs::read_to_string(self.path.join("pwm1"))?;
        let value: u16 = content
            .trim()
            .parse()
            .map_err(|_| HwmonError::ParseError(format!("Invalid PWM value: {}", content.trim())))?;

        // Clamp to u8 range (should already be 0-255)
        Ok(value.min(255) as u8)
    }

    /// Read current fan mode
    pub fn read_mode(&self) -> Result<FanMode, HwmonError> {
        let content = fs::read_to_string(self.path.join("pwm1_enable"))?;
        let value: u8 = content
            .trim()
            .parse()
            .map_err(|_| HwmonError::ParseError(format!("Invalid mode value: {}", content.trim())))?;

        FanMode::from_sysfs_value(value)
            .ok_or_else(|| HwmonError::ParseError(format!("Unknown fan mode: {}", value)))
    }

    /// Set fan mode (Auto or Manual)
    ///
    /// # Safety
    /// Setting Manual mode takes control from BIOS. The Drop implementation
    /// will return control to Auto mode when this device is dropped.
    pub fn set_mode(&mut self, mode: FanMode) -> Result<(), HwmonError> {
        let value = mode.as_sysfs_value().to_string();
        fs::write(self.path.join("pwm1_enable"), &value)?;

        // Track if we took manual control
        if mode == FanMode::Manual {
            self.took_control = true;
        }

        Ok(())
    }

    /// Set PWM value (0-255)
    ///
    /// # Arguments
    /// * `pwm` - PWM duty cycle (0 = off, 255 = max)
    ///
    /// # Note
    /// Fan must be in Manual mode for this to take effect.
    pub fn set_pwm(&self, pwm: u8) -> Result<(), HwmonError> {
        let value = pwm.to_string();
        fs::write(self.path.join("pwm1"), &value)?;
        Ok(())
    }

    /// Set fan speed as percentage (0-100)
    ///
    /// Converts percentage to PWM value (0-255).
    pub fn set_speed_percent(&self, percent: u8) -> Result<(), HwmonError> {
        let percent = percent.min(100);
        let pwm = ((percent as u16 * 255) / 100) as u8;
        self.set_pwm(pwm)
    }

    /// Read fan speed as percentage (0-100)
    pub fn read_speed_percent(&self) -> Result<u8, HwmonError> {
        let pwm = self.read_pwm()?;
        Ok(((pwm as u16 * 100) / 255) as u8)
    }

    /// Read fan RPM if available
    ///
    /// # Returns
    /// Some(rpm) if fan1_input exists, None otherwise
    pub fn read_rpm(&self) -> Option<u32> {
        let rpm_path = self.path.join("fan1_input");
        if !rpm_path.exists() {
            return None;
        }

        fs::read_to_string(&rpm_path)
            .ok()
            .and_then(|s| s.trim().parse().ok())
    }

    /// Return control to BIOS (set Auto mode)
    ///
    /// Called automatically on Drop, but can be called manually.
    pub fn release_control(&mut self) -> Result<(), HwmonError> {
        if self.took_control {
            fs::write(self.path.join("pwm1_enable"), "2")?;
            self.took_control = false;
        }
        Ok(())
    }
}

impl Drop for HwmonDevice {
    fn drop(&mut self) {
        // Best-effort return to BIOS control
        if self.took_control {
            let _ = fs::write(self.path.join("pwm1_enable"), "2");
        }
    }
}

/// Find Steam Deck hwmon device (jupiter or galileo)
///
/// Iterates through /sys/class/hwmon/hwmonX directories looking for
/// a device with name "jupiter" or "galileo".
///
/// # Returns
/// HwmonDevice if found, error otherwise
pub fn find_steam_deck_hwmon() -> Result<HwmonDevice, HwmonError> {
    find_steam_deck_hwmon_in(HWMON_PATH)
}

/// Find Steam Deck hwmon device in a specific base path (for testing)
pub fn find_steam_deck_hwmon_in<P: AsRef<Path>>(base_path: P) -> Result<HwmonDevice, HwmonError> {
    let base = base_path.as_ref();

    if !base.exists() {
        return Err(HwmonError::DeviceNotFound(format!(
            "Hwmon base path doesn't exist: {:?}",
            base
        )));
    }

    let entries = fs::read_dir(base).map_err(HwmonError::IoError)?;

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        // Check if this is a hwmonX directory
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if !name.starts_with("hwmon") {
            continue;
        }

        // Try to open and check if it's Steam Deck
        if let Ok(device) = HwmonDevice::open(&path) {
            if device.is_steam_deck() {
                return Ok(device);
            }
        }
    }

    Err(HwmonError::DeviceNotFound(
        "No Steam Deck fan controller found (jupiter/galileo)".to_string(),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fan_mode_sysfs_values() {
        assert_eq!(FanMode::Auto.as_sysfs_value(), 2);
        assert_eq!(FanMode::Manual.as_sysfs_value(), 1);

        assert_eq!(FanMode::from_sysfs_value(1), Some(FanMode::Manual));
        assert_eq!(FanMode::from_sysfs_value(2), Some(FanMode::Auto));
        assert_eq!(FanMode::from_sysfs_value(0), None);
        assert_eq!(FanMode::from_sysfs_value(3), None);
    }

    #[test]
    fn test_percent_to_pwm_conversion() {
        // 0% -> 0 PWM
        assert_eq!(((0u16 * 255) / 100) as u8, 0);
        // 50% -> 127 PWM
        assert_eq!(((50u16 * 255) / 100) as u8, 127);
        // 100% -> 255 PWM
        assert_eq!(((100u16 * 255) / 100) as u8, 255);
    }

    #[test]
    fn test_pwm_to_percent_conversion() {
        // 0 PWM -> 0%
        assert_eq!(((0u16 * 100) / 255) as u8, 0);
        // 127 PWM -> 49%
        assert_eq!(((127u16 * 100) / 255) as u8, 49);
        // 255 PWM -> 100%
        assert_eq!(((255u16 * 100) / 255) as u8, 100);
    }

    #[test]
    fn test_hwmon_error_display() {
        let err = HwmonError::DeviceNotFound("test".to_string());
        assert!(err.to_string().contains("not found"));

        let err = HwmonError::PermissionDenied;
        assert!(err.to_string().contains("Permission denied"));
    }
}
