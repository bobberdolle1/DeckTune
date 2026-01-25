//! Fan controller with curve interpolation, hysteresis, and smoothing
//!
//! Main control logic for fan speed management. Combines:
//! - Temperature-based fan curve with linear interpolation
//! - Hysteresis to prevent rapid speed changes on small temp fluctuations
//! - Moving average smoothing for gradual transitions
//! - PWM smoothing for gradual fan speed transitions
//! - Safety overrides for critical temperatures

use std::collections::VecDeque;

use super::hwmon::{HwmonDevice, HwmonError, FanMode};
use super::safety::{FanSafetyLimits, SafetyOverride, apply_safety_override, check_safety_override};
use super::smoother::{PWMSmoother, DEFAULT_RAMP_TIME_SEC};

/// Default temperature hysteresis in °C
pub const DEFAULT_HYSTERESIS_TEMP: i32 = 2;

/// Default number of samples for moving average smoothing
pub const DEFAULT_SMOOTHING_SAMPLES: usize = 5;

/// Minimum PWM value
pub const MIN_PWM: u8 = 0;

/// Maximum PWM value
pub const MAX_PWM: u8 = 255;

/// A point on the fan curve (temperature -> speed)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FanCurvePoint {
    /// Temperature in Celsius
    pub temp_c: i32,
    /// Fan speed percentage (0-100)
    pub speed_percent: u8,
}

impl FanCurvePoint {
    pub fn new(temp_c: i32, speed_percent: u8) -> Self {
        FanCurvePoint {
            temp_c,
            speed_percent: speed_percent.min(100),
        }
    }
}

/// Fan curve definition with interpolation
#[derive(Debug, Clone)]
pub struct FanCurve {
    /// Sorted points (by temperature)
    points: Vec<FanCurvePoint>,
}

impl FanCurve {
    /// Create a new fan curve from points
    ///
    /// Points will be sorted by temperature. At least 2 points required.
    ///
    /// # Errors
    /// Returns error if fewer than 2 points provided
    pub fn new(mut points: Vec<FanCurvePoint>) -> Result<Self, String> {
        if points.len() < 2 {
            return Err("Fan curve requires at least 2 points".to_string());
        }

        // Sort by temperature
        points.sort_by_key(|p| p.temp_c);

        Ok(FanCurve { points })
    }

    /// Create curve from (temp, speed%) tuples
    pub fn from_tuples(tuples: Vec<(i32, u8)>) -> Result<Self, String> {
        let points = tuples
            .into_iter()
            .map(|(t, s)| FanCurvePoint::new(t, s))
            .collect();
        Self::new(points)
    }

    /// Get the number of points in the curve
    pub fn len(&self) -> usize {
        self.points.len()
    }

    /// Check if curve is empty
    pub fn is_empty(&self) -> bool {
        self.points.is_empty()
    }

    /// Get all points (sorted by temperature)
    pub fn points(&self) -> &[FanCurvePoint] {
        &self.points
    }

    /// Calculate fan speed for a given temperature using linear interpolation
    ///
    /// - Below lowest point: returns lowest point's speed
    /// - Above highest point: returns highest point's speed
    /// - Between points: linear interpolation
    pub fn calculate_speed(&self, temp_c: i32) -> u8 {
        if self.points.is_empty() {
            return 50; // Fallback
        }

        // Below lowest point
        if temp_c <= self.points[0].temp_c {
            return self.points[0].speed_percent;
        }

        // Above highest point
        let last = &self.points[self.points.len() - 1];
        if temp_c >= last.temp_c {
            return last.speed_percent;
        }

        // Find surrounding points and interpolate
        for i in 0..self.points.len() - 1 {
            let p1 = &self.points[i];
            let p2 = &self.points[i + 1];

            if temp_c >= p1.temp_c && temp_c <= p2.temp_c {
                return Self::interpolate(temp_c, p1, p2);
            }
        }

        // Shouldn't reach here, but fallback
        50
    }

    /// Linear interpolation between two points
    fn interpolate(temp_c: i32, p1: &FanCurvePoint, p2: &FanCurvePoint) -> u8 {
        let temp_range = p2.temp_c - p1.temp_c;
        if temp_range == 0 {
            return p1.speed_percent;
        }

        let speed_range = p2.speed_percent as i32 - p1.speed_percent as i32;
        let temp_offset = temp_c - p1.temp_c;

        let speed = p1.speed_percent as i32 + (speed_range * temp_offset) / temp_range;
        speed.clamp(0, 100) as u8
    }

    /// Convert speed percentage to PWM value (0-255)
    pub fn speed_to_pwm(speed_percent: u8) -> u8 {
        ((speed_percent.min(100) as u16 * 255) / 100) as u8
    }

    /// Convert PWM value to speed percentage
    pub fn pwm_to_speed(pwm: u8) -> u8 {
        ((pwm as u16 * 100) / 255) as u8
    }
}

impl Default for FanCurve {
    /// Default curve: quiet at low temps, aggressive at high temps
    fn default() -> Self {
        FanCurve::from_tuples(vec![
            (40, 20),  // 40°C -> 20%
            (50, 30),  // 50°C -> 30%
            (60, 45),  // 60°C -> 45%
            (70, 60),  // 70°C -> 60%
            (80, 80),  // 80°C -> 80%
            (85, 100), // 85°C -> 100%
        ])
        .expect("Default curve is valid")
    }
}

/// Fan controller configuration
#[derive(Debug, Clone)]
pub struct FanControllerConfig {
    /// Temperature hysteresis in °C
    pub hysteresis_temp: i32,
    /// Number of samples for moving average
    pub smoothing_samples: usize,
    /// Safety limits
    pub safety_limits: FanSafetyLimits,
    /// Minimum PWM change to actually write (reduces sysfs spam)
    pub min_pwm_change: u8,
    /// Enable PWM smoothing for gradual transitions
    pub pwm_smoothing_enabled: bool,
    /// PWM smoothing ramp time in seconds (0 to 255 PWM)
    pub pwm_ramp_time_sec: f32,
}

impl Default for FanControllerConfig {
    fn default() -> Self {
        FanControllerConfig {
            hysteresis_temp: DEFAULT_HYSTERESIS_TEMP,
            smoothing_samples: DEFAULT_SMOOTHING_SAMPLES,
            safety_limits: FanSafetyLimits::default(),
            min_pwm_change: 3, // Don't write for changes < 3 PWM (~1%)
            pwm_smoothing_enabled: true,
            pwm_ramp_time_sec: DEFAULT_RAMP_TIME_SEC,
        }
    }
}

/// Current fan status
#[derive(Debug, Clone)]
pub struct FanStatus {
    /// Current temperature in °C
    pub temp_c: i32,
    /// Current PWM value (0-255)
    pub pwm: u8,
    /// Current speed percentage (0-100)
    pub speed_percent: u8,
    /// Current fan mode
    pub mode: FanMode,
    /// Fan RPM if available
    pub rpm: Option<u32>,
    /// Whether safety override is active
    pub safety_override_active: bool,
}

/// Main fan controller
pub struct FanController {
    /// Hwmon device handle
    device: HwmonDevice,
    /// Fan curve
    curve: FanCurve,
    /// Configuration
    config: FanControllerConfig,
    /// Temperature history for smoothing
    temp_history: VecDeque<i32>,
    /// Last stable temperature (for hysteresis)
    last_stable_temp: Option<i32>,
    /// Last written PWM value
    last_pwm: u8,
    /// Whether controller is active (in manual mode)
    active: bool,
    /// PWM smoother for gradual transitions
    pwm_smoother: PWMSmoother,
}

impl FanController {
    /// Create a new fan controller
    ///
    /// Automatically finds the Steam Deck hwmon device.
    pub fn new() -> Result<Self, HwmonError> {
        let device = super::hwmon::find_steam_deck_hwmon()?;
        Ok(Self::with_device(device))
    }

    /// Create controller with a specific device (for testing)
    pub fn with_device(device: HwmonDevice) -> Self {
        FanController {
            device,
            curve: FanCurve::default(),
            config: FanControllerConfig::default(),
            temp_history: VecDeque::with_capacity(DEFAULT_SMOOTHING_SAMPLES),
            last_stable_temp: None,
            last_pwm: 0,
            active: false,
            pwm_smoother: PWMSmoother::default(),
        }
    }

    /// Set the fan curve
    pub fn set_curve(&mut self, curve: FanCurve) {
        self.curve = curve;
    }

    /// Set configuration
    pub fn set_config(&mut self, config: FanControllerConfig) {
        // Resize history buffer if needed
        while self.temp_history.len() > config.smoothing_samples {
            self.temp_history.pop_front();
        }
        // Update PWM smoother if ramp time changed
        if (config.pwm_ramp_time_sec - self.config.pwm_ramp_time_sec).abs() > 0.01 {
            self.pwm_smoother = PWMSmoother::new(config.pwm_ramp_time_sec);
        }
        self.config = config;
    }

    /// Enable manual fan control
    pub fn enable(&mut self) -> Result<(), HwmonError> {
        self.device.set_mode(FanMode::Manual)?;
        self.active = true;
        Ok(())
    }

    /// Disable manual control, return to BIOS
    pub fn disable(&mut self) -> Result<(), HwmonError> {
        self.device.set_mode(FanMode::Auto)?;
        self.active = false;
        self.temp_history.clear();
        self.last_stable_temp = None;
        self.pwm_smoother.reset();
        Ok(())
    }

    /// Check if controller is active
    pub fn is_active(&self) -> bool {
        self.active
    }

    /// Get current status
    pub fn status(&self) -> Result<FanStatus, HwmonError> {
        let temp_c = self.device.read_temp_c()?;
        let pwm = self.device.read_pwm()?;
        let mode = self.device.read_mode()?;
        let rpm = self.device.read_rpm();

        let safety_override = check_safety_override(temp_c, &self.config.safety_limits);

        Ok(FanStatus {
            temp_c,
            pwm,
            speed_percent: FanCurve::pwm_to_speed(pwm),
            mode,
            rpm,
            safety_override_active: safety_override != SafetyOverride::None,
        })
    }

    /// Main update tick - read temp, calculate speed, apply
    ///
    /// Should be called periodically (e.g., every 500ms).
    /// Returns the applied PWM value.
    pub fn update(&mut self) -> Result<u8, HwmonError> {
        if !self.active {
            return Ok(self.last_pwm);
        }

        // Read current temperature
        let raw_temp = self.device.read_temp_c()?;

        // Add to history for smoothing
        self.temp_history.push_back(raw_temp);
        while self.temp_history.len() > self.config.smoothing_samples {
            self.temp_history.pop_front();
        }

        // Calculate smoothed temperature (moving average)
        let smoothed_temp = if self.temp_history.is_empty() {
            raw_temp
        } else {
            let sum: i32 = self.temp_history.iter().sum();
            sum / self.temp_history.len() as i32
        };

        // Apply hysteresis
        let effective_temp = self.apply_hysteresis(smoothed_temp);

        // Calculate target speed from curve
        let target_speed = self.curve.calculate_speed(effective_temp);
        let target_pwm = FanCurve::speed_to_pwm(target_speed);

        // Apply safety overrides
        let safe_pwm = apply_safety_override(target_pwm, raw_temp, &self.config.safety_limits);

        // Check if safety override is active (critical temperature)
        let safety_override = check_safety_override(raw_temp, &self.config.safety_limits);
        let is_critical = matches!(safety_override, SafetyOverride::ForcePwm(_));

        // Apply PWM smoothing if enabled and not in critical state
        let final_pwm = if self.config.pwm_smoothing_enabled && !is_critical {
            self.pwm_smoother.set_target(safe_pwm);
            self.pwm_smoother.update()
        } else if is_critical {
            // Bypass smoothing for emergency - force immediate max PWM
            self.pwm_smoother.force_immediate(safe_pwm);
            safe_pwm
        } else {
            safe_pwm
        };

        // Only write if change is significant (reduces sysfs spam)
        let pwm_diff = (final_pwm as i16 - self.last_pwm as i16).unsigned_abs() as u8;
        if pwm_diff >= self.config.min_pwm_change || final_pwm == 0 || final_pwm == 255 {
            self.device.set_pwm(final_pwm)?;
            self.last_pwm = final_pwm;
        }

        Ok(self.last_pwm)
    }

    /// Apply hysteresis to temperature
    ///
    /// Only updates the "stable" temperature if change exceeds hysteresis threshold.
    fn apply_hysteresis(&mut self, temp: i32) -> i32 {
        match self.last_stable_temp {
            Some(last) => {
                let diff = (temp - last).abs();
                if diff >= self.config.hysteresis_temp {
                    self.last_stable_temp = Some(temp);
                    temp
                } else {
                    last
                }
            }
            None => {
                self.last_stable_temp = Some(temp);
                temp
            }
        }
    }

    /// Force a specific PWM value (bypasses curve and smoothing)
    pub fn force_pwm(&mut self, pwm: u8) -> Result<(), HwmonError> {
        if self.active {
            self.pwm_smoother.force_immediate(pwm);
            self.device.set_pwm(pwm)?;
            self.last_pwm = pwm;
        }
        Ok(())
    }

    /// Get the PWM smoother (for advanced operations)
    pub fn pwm_smoother(&self) -> &PWMSmoother {
        &self.pwm_smoother
    }

    /// Get mutable PWM smoother reference
    pub fn pwm_smoother_mut(&mut self) -> &mut PWMSmoother {
        &mut self.pwm_smoother
    }

    /// Get the underlying device (for advanced operations)
    pub fn device(&self) -> &HwmonDevice {
        &self.device
    }

    /// Get mutable device reference
    pub fn device_mut(&mut self) -> &mut HwmonDevice {
        &mut self.device
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fan_curve_point() {
        let point = FanCurvePoint::new(50, 60);
        assert_eq!(point.temp_c, 50);
        assert_eq!(point.speed_percent, 60);

        // Speed clamped to 100
        let point = FanCurvePoint::new(50, 150);
        assert_eq!(point.speed_percent, 100);
    }

    #[test]
    fn test_fan_curve_creation() {
        let curve = FanCurve::from_tuples(vec![(40, 20), (80, 100)]).unwrap();
        assert_eq!(curve.len(), 2);

        // Too few points
        assert!(FanCurve::from_tuples(vec![(40, 20)]).is_err());
    }

    #[test]
    fn test_fan_curve_sorting() {
        // Points should be sorted by temperature
        let curve = FanCurve::from_tuples(vec![(80, 100), (40, 20), (60, 50)]).unwrap();
        let points = curve.points();
        assert_eq!(points[0].temp_c, 40);
        assert_eq!(points[1].temp_c, 60);
        assert_eq!(points[2].temp_c, 80);
    }

    #[test]
    fn test_fan_curve_interpolation() {
        let curve = FanCurve::from_tuples(vec![(40, 20), (80, 100)]).unwrap();

        // Below lowest point
        assert_eq!(curve.calculate_speed(30), 20);

        // At lowest point
        assert_eq!(curve.calculate_speed(40), 20);

        // Middle (linear interpolation)
        // At 60°C: 20 + (100-20) * (60-40) / (80-40) = 20 + 80 * 20/40 = 20 + 40 = 60
        assert_eq!(curve.calculate_speed(60), 60);

        // At highest point
        assert_eq!(curve.calculate_speed(80), 100);

        // Above highest point
        assert_eq!(curve.calculate_speed(90), 100);
    }

    #[test]
    fn test_fan_curve_multi_point() {
        let curve = FanCurve::from_tuples(vec![
            (40, 0),
            (50, 30),
            (70, 60),
            (85, 100),
        ])
        .unwrap();

        assert_eq!(curve.calculate_speed(40), 0);
        assert_eq!(curve.calculate_speed(45), 15); // Interpolated
        assert_eq!(curve.calculate_speed(50), 30);
        assert_eq!(curve.calculate_speed(60), 45); // Interpolated
        assert_eq!(curve.calculate_speed(70), 60);
        assert_eq!(curve.calculate_speed(85), 100);
    }

    #[test]
    fn test_speed_pwm_conversion() {
        assert_eq!(FanCurve::speed_to_pwm(0), 0);
        assert_eq!(FanCurve::speed_to_pwm(50), 127);
        assert_eq!(FanCurve::speed_to_pwm(100), 255);

        assert_eq!(FanCurve::pwm_to_speed(0), 0);
        assert_eq!(FanCurve::pwm_to_speed(127), 49); // Rounding
        assert_eq!(FanCurve::pwm_to_speed(255), 100);
    }

    #[test]
    fn test_default_curve() {
        let curve = FanCurve::default();
        assert!(curve.len() >= 2);

        // Should be quiet at low temps
        assert!(curve.calculate_speed(40) <= 30);

        // Should be aggressive at high temps
        assert!(curve.calculate_speed(85) >= 90);
    }

    #[test]
    fn test_config_defaults() {
        let config = FanControllerConfig::default();
        assert_eq!(config.hysteresis_temp, 2);
        assert_eq!(config.smoothing_samples, 5);
        assert_eq!(config.min_pwm_change, 3);
        assert!(config.pwm_smoothing_enabled);
        assert!((config.pwm_ramp_time_sec - 2.0).abs() < 0.1);
    }
}
