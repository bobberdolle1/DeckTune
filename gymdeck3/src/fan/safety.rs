//! Fan safety limits and overrides
//!
//! Provides hard safety limits that cannot be bypassed by user configuration.
//! These ensure the Steam Deck doesn't overheat even with misconfigured curves.

/// Critical temperature threshold (°C) - forces 100% fan immediately
pub const CRITICAL_TEMP_C: i32 = 90;

/// High temperature threshold (°C) - minimum 80% fan
pub const HIGH_TEMP_C: i32 = 85;

/// Maximum temperature for Zero RPM mode (°C)
pub const ZERO_RPM_MAX_TEMP_C: i32 = 45;

/// Minimum PWM value (0 = fan off)
pub const MIN_SAFE_PWM: u8 = 0;

/// Maximum PWM value (255 = full speed)
pub const MAX_SAFE_PWM: u8 = 255;

/// Safety limits configuration
#[derive(Debug, Clone, Copy)]
pub struct FanSafetyLimits {
    /// Temperature that forces 100% fan (°C)
    pub critical_temp: i32,
    /// Temperature that forces minimum 80% fan (°C)
    pub high_temp: i32,
    /// Maximum temp for zero RPM mode (°C)
    pub zero_rpm_max_temp: i32,
    /// Whether zero RPM mode is allowed
    pub allow_zero_rpm: bool,
}

impl Default for FanSafetyLimits {
    fn default() -> Self {
        FanSafetyLimits {
            critical_temp: CRITICAL_TEMP_C,
            high_temp: HIGH_TEMP_C,
            zero_rpm_max_temp: ZERO_RPM_MAX_TEMP_C,
            allow_zero_rpm: false, // Disabled by default for safety
        }
    }
}

impl FanSafetyLimits {
    /// Create limits with zero RPM enabled
    pub fn with_zero_rpm(mut self) -> Self {
        self.allow_zero_rpm = true;
        self
    }

    /// Create limits with custom critical temperature
    pub fn with_critical_temp(mut self, temp: i32) -> Self {
        // Don't allow critical temp below 85°C
        self.critical_temp = temp.max(85);
        self
    }
}

/// Result of safety check
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SafetyOverride {
    /// No override needed, use calculated PWM
    None,
    /// Force specific PWM value due to safety
    ForcePwm(u8),
    /// Force specific minimum PWM (can go higher)
    MinimumPwm(u8),
}

/// Check if safety override is needed based on temperature
///
/// # Arguments
/// * `temp_c` - Current temperature in Celsius
/// * `limits` - Safety limits configuration
///
/// # Returns
/// SafetyOverride indicating if/how to override the calculated PWM
pub fn check_safety_override(temp_c: i32, limits: &FanSafetyLimits) -> SafetyOverride {
    if temp_c >= limits.critical_temp {
        // Critical: force 100% immediately
        SafetyOverride::ForcePwm(255)
    } else if temp_c >= limits.high_temp {
        // High: minimum 80% (204/255)
        SafetyOverride::MinimumPwm(204)
    } else {
        SafetyOverride::None
    }
}

/// Check if zero RPM is safe at current temperature
///
/// # Arguments
/// * `temp_c` - Current temperature in Celsius
/// * `limits` - Safety limits configuration
///
/// # Returns
/// true if zero RPM is allowed at this temperature
pub fn is_zero_rpm_safe(temp_c: i32, limits: &FanSafetyLimits) -> bool {
    limits.allow_zero_rpm && temp_c <= limits.zero_rpm_max_temp
}

/// Apply safety override to a calculated PWM value
///
/// # Arguments
/// * `calculated_pwm` - PWM value from fan curve
/// * `temp_c` - Current temperature in Celsius
/// * `limits` - Safety limits configuration
///
/// # Returns
/// Final PWM value after applying safety overrides
pub fn apply_safety_override(calculated_pwm: u8, temp_c: i32, limits: &FanSafetyLimits) -> u8 {
    match check_safety_override(temp_c, limits) {
        SafetyOverride::ForcePwm(pwm) => pwm,
        SafetyOverride::MinimumPwm(min_pwm) => calculated_pwm.max(min_pwm),
        SafetyOverride::None => {
            // Check zero RPM safety
            if calculated_pwm == 0 && !is_zero_rpm_safe(temp_c, limits) {
                // Force minimum spin to prevent overheating
                30 // ~12% - barely spinning but moving air
            } else {
                calculated_pwm
            }
        }
    }
}

/// Validate that a PWM value is within safe bounds
pub fn validate_pwm(pwm: u8) -> u8 {
    pwm.clamp(MIN_SAFE_PWM, MAX_SAFE_PWM)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_limits() {
        let limits = FanSafetyLimits::default();
        assert_eq!(limits.critical_temp, 90);
        assert_eq!(limits.high_temp, 85);
        assert_eq!(limits.zero_rpm_max_temp, 45);
        assert!(!limits.allow_zero_rpm);
    }

    #[test]
    fn test_safety_override_critical() {
        let limits = FanSafetyLimits::default();

        // At critical temp
        assert_eq!(
            check_safety_override(90, &limits),
            SafetyOverride::ForcePwm(255)
        );

        // Above critical temp
        assert_eq!(
            check_safety_override(95, &limits),
            SafetyOverride::ForcePwm(255)
        );
    }

    #[test]
    fn test_safety_override_high() {
        let limits = FanSafetyLimits::default();

        // At high temp
        assert_eq!(
            check_safety_override(85, &limits),
            SafetyOverride::MinimumPwm(204)
        );

        // Between high and critical
        assert_eq!(
            check_safety_override(87, &limits),
            SafetyOverride::MinimumPwm(204)
        );
    }

    #[test]
    fn test_safety_override_none() {
        let limits = FanSafetyLimits::default();

        // Normal temps
        assert_eq!(check_safety_override(50, &limits), SafetyOverride::None);
        assert_eq!(check_safety_override(70, &limits), SafetyOverride::None);
        assert_eq!(check_safety_override(84, &limits), SafetyOverride::None);
    }

    #[test]
    fn test_zero_rpm_safety() {
        let limits_disabled = FanSafetyLimits::default();
        let limits_enabled = FanSafetyLimits::default().with_zero_rpm();

        // Zero RPM disabled
        assert!(!is_zero_rpm_safe(40, &limits_disabled));
        assert!(!is_zero_rpm_safe(30, &limits_disabled));

        // Zero RPM enabled, below threshold
        assert!(is_zero_rpm_safe(40, &limits_enabled));
        assert!(is_zero_rpm_safe(45, &limits_enabled));

        // Zero RPM enabled, above threshold
        assert!(!is_zero_rpm_safe(46, &limits_enabled));
        assert!(!is_zero_rpm_safe(50, &limits_enabled));
    }

    #[test]
    fn test_apply_safety_override() {
        let limits = FanSafetyLimits::default();

        // Critical temp forces 255
        assert_eq!(apply_safety_override(100, 90, &limits), 255);
        assert_eq!(apply_safety_override(0, 95, &limits), 255);

        // High temp enforces minimum
        assert_eq!(apply_safety_override(100, 85, &limits), 204); // 100 < 204, use 204
        assert_eq!(apply_safety_override(220, 85, &limits), 220); // 220 > 204, keep 220

        // Normal temp, no override
        assert_eq!(apply_safety_override(150, 70, &limits), 150);

        // Zero PWM without zero_rpm enabled gets minimum spin
        assert_eq!(apply_safety_override(0, 50, &limits), 30);
    }

    #[test]
    fn test_apply_safety_with_zero_rpm() {
        let limits = FanSafetyLimits::default().with_zero_rpm();

        // Zero PWM allowed at low temp
        assert_eq!(apply_safety_override(0, 40, &limits), 0);

        // Zero PWM not allowed at higher temp
        assert_eq!(apply_safety_override(0, 50, &limits), 30);
    }

    #[test]
    fn test_custom_critical_temp() {
        // Can't set below 85
        let limits = FanSafetyLimits::default().with_critical_temp(80);
        assert_eq!(limits.critical_temp, 85);

        // Can set above 85
        let limits = FanSafetyLimits::default().with_critical_temp(95);
        assert_eq!(limits.critical_temp, 95);
    }

    #[test]
    fn test_validate_pwm() {
        assert_eq!(validate_pwm(0), 0);
        assert_eq!(validate_pwm(127), 127);
        assert_eq!(validate_pwm(255), 255);
    }
}
