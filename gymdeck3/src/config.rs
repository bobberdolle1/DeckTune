//! Configuration structures and validation for gymdeck3
//!
//! This module defines the command-line interface and configuration structures
//! for gymdeck3. It handles parsing CLI arguments, validating configuration
//! values, and providing type-safe access to settings.
//!
//! # Configuration Flow
//!
//! 1. CLI arguments are parsed using clap into the `Args` struct
//! 2. Each argument is validated using custom validators
//! 3. The validated configuration is used to initialize gymdeck3 components
//!
//! # Validation Rules
//!
//! - Sample interval: 10ms - 5000ms (10,000 - 5,000,000 microseconds)
//! - Hysteresis: 1% - 20%
//! - Undervolt values: Must be negative or zero (0 = disabled)
//! - Core bounds: max_mv must be more negative than min_mv

use clap::{Parser, ValueEnum};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Dynamic undervolt controller for Steam Deck
#[derive(Parser, Debug, Clone)]
#[command(name = "gymdeck3")]
#[command(author = "DeckTune")]
#[command(version = "0.1.0")]
#[command(about = "Dynamic undervolt controller daemon", long_about = None)]
pub struct Args {
    /// Adaptation strategy
    #[arg(value_enum)]
    pub strategy: Strategy,

    /// Sample interval in microseconds (10000-5000000, i.e., 10ms-5000ms)
    #[arg(value_parser = validate_sample_interval)]
    pub sample_interval_us: u64,

    /// Per-core configuration in format N:MIN:MAX:THRESHOLD
    /// Example: --core 0:-20:-35:50.0
    #[arg(long = "core", value_parser = parse_core_config)]
    pub cores: Vec<CoreConfig>,

    /// Hysteresis margin percentage (1-20)
    #[arg(long, default_value = "5.0", value_parser = validate_hysteresis)]
    pub hysteresis: f32,

    /// Path to ryzenadj binary
    #[arg(long = "ryzenadj-path", default_value = "ryzenadj")]
    pub ryzenadj_path: PathBuf,

    /// Status output interval in milliseconds
    #[arg(long = "status-interval", default_value = "1000")]
    pub status_interval_ms: u64,

    /// Enable verbose debug logging to stderr
    #[arg(long, short)]
    pub verbose: bool,

    // ==================== Fan Control Options ====================

    /// Enable fan control
    #[arg(long = "fan-control")]
    pub fan_control: bool,

    /// Fan control mode
    #[arg(long = "fan-mode", value_enum, default_value = "default")]
    pub fan_mode: FanControlMode,

    /// Fan curve points in format TEMP:SPEED (can be specified multiple times)
    /// Example: --fan-curve 40:20 --fan-curve 60:50 --fan-curve 80:100
    #[arg(long = "fan-curve", value_parser = parse_fan_curve_point)]
    pub fan_curve: Vec<FanCurvePointConfig>,

    /// Enable Zero RPM mode (fan stops below 45°C)
    #[arg(long = "fan-zero-rpm")]
    pub fan_zero_rpm: bool,

    /// Fan temperature hysteresis in °C (1-10)
    #[arg(long = "fan-hysteresis", default_value = "2", value_parser = validate_fan_hysteresis)]
    pub fan_hysteresis: i32,
}

/// Fan control mode
#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum FanControlMode {
    /// BIOS/EC automatic control (default)
    #[default]
    Default,
    /// Custom curve control
    Custom,
    /// Fixed speed (use with --fan-curve for single point)
    Fixed,
}

impl std::fmt::Display for FanControlMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FanControlMode::Default => write!(f, "default"),
            FanControlMode::Custom => write!(f, "custom"),
            FanControlMode::Fixed => write!(f, "fixed"),
        }
    }
}

/// Fan curve point configuration
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub struct FanCurvePointConfig {
    /// Temperature in Celsius
    pub temp_c: i32,
    /// Fan speed percentage (0-100)
    pub speed_percent: u8,
}

/// Adaptation strategy for dynamic undervolt control
///
/// Each strategy has different responsiveness characteristics:
/// - **Conservative**: Slow, gradual changes (5s ramp) - prioritizes stability
/// - **Balanced**: Moderate responsiveness (2s ramp) - good for most users
/// - **Aggressive**: Fast adaptation (500ms ramp) - prioritizes responsiveness
/// - **Custom**: User-defined load-to-undervolt curve
#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Strategy {
    /// Conservative strategy with 5 second ramp time
    Conservative,
    /// Balanced strategy with 2 second ramp time (default)
    Balanced,
    /// Aggressive strategy with 500ms ramp time
    Aggressive,
    /// Custom strategy with user-defined curve
    Custom,
}

impl std::fmt::Display for Strategy {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Strategy::Conservative => write!(f, "conservative"),
            Strategy::Balanced => write!(f, "balanced"),
            Strategy::Aggressive => write!(f, "aggressive"),
            Strategy::Custom => write!(f, "custom"),
        }
    }
}

/// Per-core configuration for dynamic undervolt control
///
/// Defines the undervolt bounds and threshold for a single CPU core.
///
/// # Undervolt Value Semantics
///
/// - `min_mv`: Less aggressive undervolt (closer to 0, e.g., -20mV)
/// - `max_mv`: More aggressive undervolt (more negative, e.g., -35mV)
/// - Higher CPU load → use min_mv (safer, less aggressive)
/// - Lower CPU load → use max_mv (more aggressive, better efficiency)
///
/// # Example
///
/// ```
/// # use gymdeck3::CoreConfig;
/// let config = CoreConfig {
///     core_id: 0,
///     min_mv: -20,    // Safe value for high load
///     max_mv: -35,    // Aggressive value for low load
///     threshold: 50.0, // Load threshold for strategy decisions
/// };
/// ```
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct CoreConfig {
    /// Core ID (0-based index)
    pub core_id: usize,
    /// Minimum (less aggressive) undervolt value in millivolts
    pub min_mv: i32,
    /// Maximum (more aggressive) undervolt value in millivolts
    pub max_mv: i32,
    /// Load threshold percentage for strategy switching (0.0 - 100.0)
    pub threshold: f32,
}

/// Validate sample interval is within 10ms-5000ms (10000-5000000 microseconds)
pub fn validate_sample_interval(s: &str) -> Result<u64, String> {
    let val: u64 = s
        .parse()
        .map_err(|_| format!("'{}' is not a valid number", s))?;
    
    if val < 10_000 {
        return Err(format!(
            "Sample interval {} us is too small (minimum: 10000 us / 10ms)",
            val
        ));
    }
    if val > 5_000_000 {
        return Err(format!(
            "Sample interval {} us is too large (maximum: 5000000 us / 5000ms)",
            val
        ));
    }
    Ok(val)
}

/// Validate sample interval from u64 value directly
pub fn validate_sample_interval_value(val: u64) -> Result<u64, String> {
    if val < 10_000 {
        return Err(format!(
            "Sample interval {} us is too small (minimum: 10000 us / 10ms)",
            val
        ));
    }
    if val > 5_000_000 {
        return Err(format!(
            "Sample interval {} us is too large (maximum: 5000000 us / 5000ms)",
            val
        ));
    }
    Ok(val)
}

/// Validate hysteresis is within 1-20%
pub fn validate_hysteresis(s: &str) -> Result<f32, String> {
    let val: f32 = s
        .parse()
        .map_err(|_| format!("'{}' is not a valid number", s))?;
    
    validate_hysteresis_value(val)
}

/// Validate hysteresis from f32 value directly
pub fn validate_hysteresis_value(val: f32) -> Result<f32, String> {
    if val < 1.0 {
        return Err(format!(
            "Hysteresis {}% is too small (minimum: 1%)",
            val
        ));
    }
    if val > 20.0 {
        return Err(format!(
            "Hysteresis {}% is too large (maximum: 20%)",
            val
        ));
    }
    Ok(val)
}

/// Parse core configuration from string format: N:MIN:MAX:THRESHOLD
/// Example: "0:-20:-35:50.0"
pub fn parse_core_config(s: &str) -> Result<CoreConfig, String> {
    let parts: Vec<&str> = s.split(':').collect();
    if parts.len() != 4 {
        return Err(format!(
            "Invalid core config '{}'. Expected format: N:MIN:MAX:THRESHOLD (e.g., 0:-20:-35:50.0)",
            s
        ));
    }

    let core_id: usize = parts[0]
        .parse()
        .map_err(|_| format!("Invalid core ID '{}': must be a non-negative integer", parts[0]))?;

    let min_mv: i32 = parts[1]
        .parse()
        .map_err(|_| format!("Invalid min_mv '{}': must be an integer", parts[1]))?;

    let max_mv: i32 = parts[2]
        .parse()
        .map_err(|_| format!("Invalid max_mv '{}': must be an integer", parts[2]))?;

    let threshold: f32 = parts[3]
        .parse()
        .map_err(|_| format!("Invalid threshold '{}': must be a float", parts[3]))?;

    validate_core_config_values(core_id, min_mv, max_mv, threshold)
}

/// Validate core configuration values directly
pub fn validate_core_config_values(
    core_id: usize,
    min_mv: i32,
    max_mv: i32,
    threshold: f32,
) -> Result<CoreConfig, String> {
    // Validate undervolt values (should be negative or zero)
    if min_mv > 0 {
        return Err(format!(
            "min_mv {} must be <= 0 (undervolt values are negative)",
            min_mv
        ));
    }
    if max_mv > 0 {
        return Err(format!(
            "max_mv {} must be <= 0 (undervolt values are negative)",
            max_mv
        ));
    }

    // max_mv should be more negative (more aggressive) than min_mv
    if max_mv > min_mv {
        return Err(format!(
            "max_mv ({}) must be <= min_mv ({}) (max is more aggressive/negative)",
            max_mv, min_mv
        ));
    }

    // Validate threshold is in valid range
    if !(0.0..=100.0).contains(&threshold) {
        return Err(format!(
            "Threshold {} must be between 0.0 and 100.0",
            threshold
        ));
    }

    Ok(CoreConfig {
        core_id,
        min_mv,
        max_mv,
        threshold,
    })
}

/// Validate the complete Args configuration
pub fn validate_args(args: &Args) -> Result<(), String> {
    // Check for duplicate core IDs
    let mut seen_cores = std::collections::HashSet::new();
    for core in &args.cores {
        if !seen_cores.insert(core.core_id) {
            return Err(format!("Duplicate core ID: {}", core.core_id));
        }
    }

    // Validate ryzenadj path exists (basic check)
    if args.ryzenadj_path.as_os_str().is_empty() {
        return Err("ryzenadj-path cannot be empty".to_string());
    }

    // Validate fan curve if fan control is enabled
    if args.fan_control && args.fan_mode == FanControlMode::Custom {
        if args.fan_curve.len() < 2 {
            return Err("Fan curve requires at least 2 points".to_string());
        }
    }

    Ok(())
}

/// Parse fan curve point from string format: TEMP:SPEED
/// Example: "60:50" means 60°C -> 50% speed
pub fn parse_fan_curve_point(s: &str) -> Result<FanCurvePointConfig, String> {
    let parts: Vec<&str> = s.split(':').collect();
    if parts.len() != 2 {
        return Err(format!(
            "Invalid fan curve point '{}'. Expected format: TEMP:SPEED (e.g., 60:50)",
            s
        ));
    }

    let temp_c: i32 = parts[0]
        .parse()
        .map_err(|_| format!("Invalid temperature '{}': must be an integer", parts[0]))?;

    let speed_percent: u8 = parts[1]
        .parse()
        .map_err(|_| format!("Invalid speed '{}': must be 0-100", parts[1]))?;

    validate_fan_curve_point(temp_c, speed_percent)
}

/// Validate fan curve point values
pub fn validate_fan_curve_point(temp_c: i32, speed_percent: u8) -> Result<FanCurvePointConfig, String> {
    if temp_c < 0 || temp_c > 100 {
        return Err(format!(
            "Temperature {} must be between 0 and 100°C",
            temp_c
        ));
    }

    if speed_percent > 100 {
        return Err(format!(
            "Speed {} must be between 0 and 100%",
            speed_percent
        ));
    }

    Ok(FanCurvePointConfig {
        temp_c,
        speed_percent,
    })
}

/// Validate fan hysteresis is within 1-10°C
pub fn validate_fan_hysteresis(s: &str) -> Result<i32, String> {
    let val: i32 = s
        .parse()
        .map_err(|_| format!("'{}' is not a valid number", s))?;

    if val < 1 {
        return Err(format!(
            "Fan hysteresis {}°C is too small (minimum: 1°C)",
            val
        ));
    }
    if val > 10 {
        return Err(format!(
            "Fan hysteresis {}°C is too large (maximum: 10°C)",
            val
        ));
    }
    Ok(val)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_core_config_valid() {
        let config = parse_core_config("0:-20:-35:50.0").unwrap();
        assert_eq!(config.core_id, 0);
        assert_eq!(config.min_mv, -20);
        assert_eq!(config.max_mv, -35);
        assert_eq!(config.threshold, 50.0);
    }

    #[test]
    fn test_parse_core_config_invalid_format() {
        assert!(parse_core_config("0:-20:-35").is_err());
        assert!(parse_core_config("invalid").is_err());
    }

    #[test]
    fn test_parse_core_config_invalid_values() {
        // Positive undervolt values
        assert!(parse_core_config("0:20:-35:50.0").is_err());
        // max_mv > min_mv
        assert!(parse_core_config("0:-35:-20:50.0").is_err());
        // Invalid threshold
        assert!(parse_core_config("0:-20:-35:150.0").is_err());
    }

    #[test]
    fn test_validate_sample_interval() {
        assert!(validate_sample_interval("10000").is_ok());
        assert!(validate_sample_interval("5000000").is_ok());
        assert!(validate_sample_interval("100000").is_ok());
        
        assert!(validate_sample_interval("9999").is_err());
        assert!(validate_sample_interval("5000001").is_err());
        assert!(validate_sample_interval("invalid").is_err());
    }

    #[test]
    fn test_validate_hysteresis() {
        assert!(validate_hysteresis("1.0").is_ok());
        assert!(validate_hysteresis("20.0").is_ok());
        assert!(validate_hysteresis("5.5").is_ok());
        
        assert!(validate_hysteresis("0.5").is_err());
        assert!(validate_hysteresis("21.0").is_err());
        assert!(validate_hysteresis("invalid").is_err());
    }

    #[test]
    fn test_strategy_display() {
        assert_eq!(Strategy::Conservative.to_string(), "conservative");
        assert_eq!(Strategy::Balanced.to_string(), "balanced");
        assert_eq!(Strategy::Aggressive.to_string(), "aggressive");
        assert_eq!(Strategy::Custom.to_string(), "custom");
    }

    // ==================== Fan Config Tests ====================

    #[test]
    fn test_parse_fan_curve_point_valid() {
        let point = parse_fan_curve_point("60:50").unwrap();
        assert_eq!(point.temp_c, 60);
        assert_eq!(point.speed_percent, 50);

        let point = parse_fan_curve_point("40:0").unwrap();
        assert_eq!(point.temp_c, 40);
        assert_eq!(point.speed_percent, 0);

        let point = parse_fan_curve_point("85:100").unwrap();
        assert_eq!(point.temp_c, 85);
        assert_eq!(point.speed_percent, 100);
    }

    #[test]
    fn test_parse_fan_curve_point_invalid() {
        // Wrong format
        assert!(parse_fan_curve_point("60").is_err());
        assert!(parse_fan_curve_point("60:50:30").is_err());
        assert!(parse_fan_curve_point("invalid").is_err());

        // Invalid values
        assert!(parse_fan_curve_point("-10:50").is_err()); // Negative temp
        assert!(parse_fan_curve_point("110:50").is_err()); // Temp > 100
        assert!(parse_fan_curve_point("60:150").is_err()); // Speed > 100
    }

    #[test]
    fn test_validate_fan_hysteresis() {
        assert!(validate_fan_hysteresis("1").is_ok());
        assert!(validate_fan_hysteresis("5").is_ok());
        assert!(validate_fan_hysteresis("10").is_ok());

        assert!(validate_fan_hysteresis("0").is_err());
        assert!(validate_fan_hysteresis("11").is_err());
        assert!(validate_fan_hysteresis("invalid").is_err());
    }

    #[test]
    fn test_fan_control_mode_display() {
        assert_eq!(FanControlMode::Default.to_string(), "default");
        assert_eq!(FanControlMode::Custom.to_string(), "custom");
        assert_eq!(FanControlMode::Fixed.to_string(), "fixed");
    }
}
