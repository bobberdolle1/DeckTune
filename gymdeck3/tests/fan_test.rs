//! Property-based tests for fan control module
//!
//! Tests fan curve interpolation, safety overrides, and hysteresis behavior.

use proptest::prelude::*;

// Import from the library's public re-exports
use gymdeck3::fan::{
    FanCurve, FanSafetyLimits, SafetyOverride,
    CRITICAL_TEMP_C, HIGH_TEMP_C, ZERO_RPM_MAX_TEMP_C,
    check_safety_override, apply_safety_override, is_zero_rpm_safe,
};

// ============================================================================
// Fan Curve Tests
// ============================================================================

proptest! {
    /// Property: Fan curve speed is always in [0, 100] range
    #[test]
    fn prop_curve_speed_in_range(temp in -50i32..150i32) {
        let curve = FanCurve::default();
        let speed = curve.calculate_speed(temp);
        prop_assert!(speed <= 100, "Speed {} exceeds 100%", speed);
    }

    /// Property: Higher temperature never results in lower fan speed
    #[test]
    fn prop_curve_monotonic(
        temp1 in 0i32..100i32,
        temp2 in 0i32..100i32,
    ) {
        let curve = FanCurve::default();
        let (low_temp, high_temp) = if temp1 <= temp2 { (temp1, temp2) } else { (temp2, temp1) };
        
        let speed_low = curve.calculate_speed(low_temp);
        let speed_high = curve.calculate_speed(high_temp);
        
        prop_assert!(
            speed_high >= speed_low,
            "Higher temp {} gave lower speed {} vs {} at {}°C",
            high_temp, speed_high, speed_low, low_temp
        );
    }

    /// Property: Speed at curve points matches exactly
    #[test]
    fn prop_curve_exact_at_points(
        t1 in 30i32..50i32,
        s1 in 0u8..50u8,
        t2 in 60i32..90i32,
        s2 in 50u8..100u8,
    ) {
        // Ensure t1 < t2 and s1 <= s2 for monotonic curve
        let (t1, t2) = (t1.min(t2 - 10), t2);
        let (s1, s2) = (s1.min(s2), s2);
        
        let curve = FanCurve::from_tuples(vec![(t1, s1), (t2, s2)]).unwrap();
        
        prop_assert_eq!(curve.calculate_speed(t1), s1);
        prop_assert_eq!(curve.calculate_speed(t2), s2);
    }

    /// Property: Interpolation is linear between points
    #[test]
    fn prop_curve_linear_interpolation(
        t1 in 30i32..50i32,
        t2 in 60i32..90i32,
    ) {
        let curve = FanCurve::from_tuples(vec![(40, 20), (80, 100)]).unwrap();
        
        // Midpoint should be average of endpoints
        let mid_temp = 60; // Midpoint of 40-80
        let mid_speed = curve.calculate_speed(mid_temp);
        
        // Expected: 20 + (100-20) * (60-40) / (80-40) = 20 + 80 * 0.5 = 60
        prop_assert_eq!(mid_speed, 60);
    }
}

// ============================================================================
// Safety Override Tests
// ============================================================================

proptest! {
    /// Property: Critical temperature always forces 100% PWM
    #[test]
    fn prop_critical_temp_forces_max(temp in CRITICAL_TEMP_C..150i32) {
        let limits = FanSafetyLimits::default();
        let result = check_safety_override(temp, &limits);
        prop_assert_eq!(result, SafetyOverride::ForcePwm(255));
    }

    /// Property: High temperature enforces minimum PWM
    #[test]
    fn prop_high_temp_enforces_minimum(temp in HIGH_TEMP_C..(CRITICAL_TEMP_C)) {
        let limits = FanSafetyLimits::default();
        let result = check_safety_override(temp, &limits);
        prop_assert!(matches!(result, SafetyOverride::MinimumPwm(_)));
    }

    /// Property: Normal temperature has no override
    #[test]
    fn prop_normal_temp_no_override(temp in 0i32..HIGH_TEMP_C) {
        let limits = FanSafetyLimits::default();
        let result = check_safety_override(temp, &limits);
        prop_assert_eq!(result, SafetyOverride::None);
    }

    /// Property: Safety override never decreases PWM
    #[test]
    fn prop_safety_never_decreases_pwm(
        calculated_pwm in 0u8..=255u8,
        temp in 0i32..100i32,
    ) {
        let limits = FanSafetyLimits::default();
        let safe_pwm = apply_safety_override(calculated_pwm, temp, &limits);
        
        // Safety should never decrease PWM (except zero RPM edge case)
        if calculated_pwm > 0 || temp >= ZERO_RPM_MAX_TEMP_C {
            prop_assert!(
                safe_pwm >= calculated_pwm,
                "Safety decreased PWM from {} to {} at {}°C",
                calculated_pwm, safe_pwm, temp
            );
        }
    }

    /// Property: Zero RPM only allowed at low temps with flag enabled
    #[test]
    fn prop_zero_rpm_safety(temp in 0i32..100i32) {
        let limits_disabled = FanSafetyLimits::default();
        let limits_enabled = FanSafetyLimits::default().with_zero_rpm();
        
        // With zero RPM disabled, should never be safe
        prop_assert!(!is_zero_rpm_safe(temp, &limits_disabled));
        
        // With zero RPM enabled, only safe below threshold
        if temp <= ZERO_RPM_MAX_TEMP_C {
            prop_assert!(is_zero_rpm_safe(temp, &limits_enabled));
        } else {
            prop_assert!(!is_zero_rpm_safe(temp, &limits_enabled));
        }
    }
}

// ============================================================================
// PWM Conversion Tests
// ============================================================================

proptest! {
    /// Property: Speed to PWM conversion is in valid range
    #[test]
    fn prop_speed_to_pwm_range(speed in 0u8..=100u8) {
        let pwm = FanCurve::speed_to_pwm(speed);
        prop_assert!(pwm <= 255);
    }

    /// Property: PWM to speed conversion is in valid range
    #[test]
    fn prop_pwm_to_speed_range(pwm in 0u8..=255u8) {
        let speed = FanCurve::pwm_to_speed(pwm);
        prop_assert!(speed <= 100);
    }

    /// Property: Conversion roundtrip is approximately identity
    #[test]
    fn prop_conversion_roundtrip(speed in 0u8..=100u8) {
        let pwm = FanCurve::speed_to_pwm(speed);
        let back = FanCurve::pwm_to_speed(pwm);
        
        // Allow ±1% error due to integer rounding
        let diff = (speed as i16 - back as i16).abs();
        prop_assert!(diff <= 1, "Roundtrip error: {} -> {} -> {} (diff {})", speed, pwm, back, diff);
    }
}

// ============================================================================
// Unit Tests
// ============================================================================

#[test]
fn test_fan_curve_requires_two_points() {
    assert!(FanCurve::from_tuples(vec![]).is_err());
    assert!(FanCurve::from_tuples(vec![(40, 20)]).is_err());
    assert!(FanCurve::from_tuples(vec![(40, 20), (80, 100)]).is_ok());
}

#[test]
fn test_fan_curve_sorts_points() {
    let curve = FanCurve::from_tuples(vec![(80, 100), (40, 20), (60, 50)]).unwrap();
    let points = curve.points();
    
    assert_eq!(points[0].temp_c, 40);
    assert_eq!(points[1].temp_c, 60);
    assert_eq!(points[2].temp_c, 80);
}

#[test]
fn test_fan_curve_clamps_below_min() {
    let curve = FanCurve::from_tuples(vec![(40, 20), (80, 100)]).unwrap();
    assert_eq!(curve.calculate_speed(0), 20);
    assert_eq!(curve.calculate_speed(-10), 20);
}

#[test]
fn test_fan_curve_clamps_above_max() {
    let curve = FanCurve::from_tuples(vec![(40, 20), (80, 100)]).unwrap();
    assert_eq!(curve.calculate_speed(100), 100);
    assert_eq!(curve.calculate_speed(150), 100);
}

#[test]
fn test_safety_limits_builder() {
    let limits = FanSafetyLimits::default()
        .with_zero_rpm()
        .with_critical_temp(95);
    
    assert!(limits.allow_zero_rpm);
    assert_eq!(limits.critical_temp, 95);
}

#[test]
fn test_safety_limits_min_critical_temp() {
    // Can't set critical temp below 85
    let limits = FanSafetyLimits::default().with_critical_temp(70);
    assert_eq!(limits.critical_temp, 85);
}

#[test]
fn test_default_curve_behavior() {
    let curve = FanCurve::default();
    
    // Should be quiet at idle temps
    assert!(curve.calculate_speed(40) <= 30);
    
    // Should ramp up at gaming temps
    assert!(curve.calculate_speed(70) >= 50);
    
    // Should be max at thermal limit
    assert!(curve.calculate_speed(85) >= 90);
}
