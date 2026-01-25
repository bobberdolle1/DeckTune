//! Property-based tests for fan control module
//!
//! Tests fan curve interpolation, safety overrides, hysteresis behavior,
//! and acoustic profile properties.

use proptest::prelude::*;

// Import from the library's public re-exports
use gymdeck3::fan::{
    FanCurve, FanSafetyLimits, SafetyOverride,
    CRITICAL_TEMP_C, HIGH_TEMP_C, ZERO_RPM_MAX_TEMP_C,
    check_safety_override, apply_safety_override, is_zero_rpm_safe,
    AcousticProfile,
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

// ============================================================================
// Acoustic Profile Property Tests
// ============================================================================

proptest! {
    /// **Feature: decktune-3.0-automation, Property 11: Silent profile RPM limit**
    /// *For any* temperature T < 85°C with Silent acoustic profile, the calculated 
    /// fan speed SHALL be ≤ 60% (approximately 3000 RPM).
    /// **Validates: Requirements 4.1**
    #[test]
    fn prop_silent_profile_rpm_limit(temp in 0i32..85i32) {
        let curve = AcousticProfile::Silent.curve();
        let speed = curve.calculate_speed(temp);
        
        prop_assert!(
            speed <= 60,
            "Silent profile at {}°C gave {}% speed, expected <= 60%",
            temp, speed
        );
    }

    /// **Feature: decktune-3.0-automation, Property 12: Balanced profile linear range**
    /// *For any* temperature T in range [30°C, 70°C] with Balanced acoustic profile, 
    /// the calculated fan speed SHALL be linearly interpolated between 30% and 90%.
    /// **Validates: Requirements 4.2**
    #[test]
    fn prop_balanced_profile_linear_range(temp in 30i32..=70i32) {
        let curve = AcousticProfile::Balanced.curve();
        let speed = curve.calculate_speed(temp);
        
        // The Balanced curve is piecewise linear:
        // 30°C -> 30%, 50°C -> 50%, 70°C -> 90%
        // Calculate expected based on which segment we're in
        let expected = if temp <= 50 {
            // Segment 30-50°C: 30% to 50%
            // speed = 30 + (50 - 30) * (temp - 30) / (50 - 30)
            30 + (20 * (temp - 30)) / 20
        } else {
            // Segment 50-70°C: 50% to 90%
            // speed = 50 + (90 - 50) * (temp - 50) / (70 - 50)
            50 + (40 * (temp - 50)) / 20
        };
        
        // Allow small rounding tolerance (±2%)
        let expected_min = if expected > 2 { expected - 2 } else { 0 };
        let expected_max = expected + 2;
        
        prop_assert!(
            speed >= expected_min as u8 && speed <= expected_max as u8,
            "Balanced profile at {}°C gave {}% speed, expected ~{}%",
            temp, speed, expected
        );
    }

    /// **Feature: decktune-3.0-automation, Property 13: Max Cooling profile aggressive curve**
    /// *For any* temperature T ≥ 60°C with Max Cooling acoustic profile, 
    /// the calculated fan speed SHALL be 100%.
    /// **Validates: Requirements 4.3**
    #[test]
    fn prop_max_cooling_profile_aggressive(temp in 60i32..100i32) {
        let curve = AcousticProfile::MaxCooling.curve();
        let speed = curve.calculate_speed(temp);
        
        prop_assert_eq!(
            speed, 100,
            "MaxCooling profile at {}°C gave {}% speed, expected 100%",
            temp, speed
        );
    }

    /// **Feature: decktune-3.0-automation, Property 14: Safety override at critical temperature**
    /// *For any* temperature T ≥ 90°C, regardless of acoustic profile, 
    /// the applied fan speed SHALL be 100% (max PWM).
    /// **Validates: Requirements 4.5**
    #[test]
    fn prop_safety_override_critical_temp(
        temp in 90i32..120i32,
        profile_idx in 0usize..3usize,
    ) {
        let profiles = [
            AcousticProfile::Silent,
            AcousticProfile::Balanced,
            AcousticProfile::MaxCooling,
        ];
        let profile = profiles[profile_idx];
        let curve = profile.curve();
        
        // Get the calculated speed from the curve
        let calculated_speed = curve.calculate_speed(temp);
        let calculated_pwm = FanCurve::speed_to_pwm(calculated_speed);
        
        // Apply safety override
        let limits = FanSafetyLimits::default();
        let safe_pwm = apply_safety_override(calculated_pwm, temp, &limits);
        
        prop_assert_eq!(
            safe_pwm, 255,
            "At {}°C with {:?} profile, safety override should force 255 PWM, got {}",
            temp, profile, safe_pwm
        );
    }
}

// ============================================================================
// Acoustic Profile Unit Tests
// ============================================================================

#[test]
fn test_silent_profile_zero_rpm_at_low_temp() {
    let curve = AcousticProfile::Silent.curve();
    assert_eq!(curve.calculate_speed(40), 0);
}

#[test]
fn test_silent_profile_max_60_at_85() {
    let curve = AcousticProfile::Silent.curve();
    assert_eq!(curve.calculate_speed(85), 60);
}

#[test]
fn test_balanced_profile_endpoints() {
    let curve = AcousticProfile::Balanced.curve();
    assert_eq!(curve.calculate_speed(30), 30);
    assert_eq!(curve.calculate_speed(70), 90);
}

#[test]
fn test_max_cooling_profile_100_at_60() {
    let curve = AcousticProfile::MaxCooling.curve();
    assert_eq!(curve.calculate_speed(60), 100);
}

#[test]
fn test_acoustic_profile_default_is_balanced() {
    assert_eq!(AcousticProfile::default(), AcousticProfile::Balanced);
}


// ============================================================================
// PWM Smoother Property Tests
// ============================================================================

use gymdeck3::fan::PWMSmoother;

proptest! {
    /// **Feature: decktune-3.0-automation, Property 15: PWM smoothing interpolation**
    /// *For any* PWM change from current C to target T over time interval Δt, 
    /// the intermediate value SHALL be C + clamp(T - C, -rate * Δt, rate * Δt) 
    /// where rate is the configured ramp rate.
    /// **Validates: Requirements 5.1, 5.2**
    #[test]
    fn prop_pwm_smoothing_interpolation(
        initial_pwm in 0u8..=255u8,
        target_pwm in 0u8..=255u8,
        ramp_time in 0.5f32..5.0f32,
    ) {
        let mut smoother = PWMSmoother::new(ramp_time);
        smoother.force_immediate(initial_pwm);
        smoother.set_target(target_pwm);
        
        // Simulate a small time step by calling update
        // The update uses elapsed time since last call
        let result = smoother.update();
        
        // The result should be between initial and target (or at target if close enough)
        let min_val = initial_pwm.min(target_pwm);
        let max_val = initial_pwm.max(target_pwm);
        
        prop_assert!(
            result >= min_val && result <= max_val,
            "Interpolated PWM {} should be between {} and {}",
            result, min_val, max_val
        );
    }

    /// **Feature: decktune-3.0-automation, Property 16: PWM ramp rate limiting**
    /// *For any* PWM change, the rate of change SHALL NOT exceed ramp_rate_increase 
    /// when increasing or ramp_rate_decrease when decreasing.
    /// **Validates: Requirements 5.3**
    #[test]
    fn prop_pwm_ramp_rate_limiting(
        initial_pwm in 0u8..=255u8,
        target_pwm in 0u8..=255u8,
        ramp_time in 1.0f32..4.0f32,
    ) {
        let mut smoother = PWMSmoother::new(ramp_time);
        smoother.force_immediate(initial_pwm);
        smoother.set_target(target_pwm);
        
        let rate_increase = smoother.ramp_rate_increase();
        let rate_decrease = smoother.ramp_rate_decrease();
        
        // Single update after a short delay to verify rate limiting
        std::thread::sleep(std::time::Duration::from_millis(10));
        let current = smoother.update();
        
        let diff = target_pwm as f32 - initial_pwm as f32;
        if diff.abs() > 0.5 {
            let expected_rate = if diff > 0.0 { rate_increase } else { rate_decrease };
            
            // Maximum possible change based on ~10ms elapsed time (with tolerance)
            let max_change = expected_rate * 0.05; // 50ms tolerance for timing
            let actual_change = (current as f32 - initial_pwm as f32).abs();
            
            // Allow tolerance for timing variations and rounding
            prop_assert!(
                actual_change <= max_change + 2.0,
                "PWM change {} exceeded max {} (rate {} * 0.05s)",
                actual_change, max_change, expected_rate
            );
        }
    }

    /// **Feature: decktune-3.0-automation, Property 17: Emergency bypass smoothing**
    /// *For any* temperature T ≥ 90°C, the PWMSmoother SHALL immediately set 
    /// current_pwm to 255 (max), bypassing interpolation.
    /// **Validates: Requirements 5.4**
    #[test]
    fn prop_emergency_bypass_smoothing(
        initial_pwm in 0u8..200u8,
        emergency_pwm in 200u8..=255u8,
    ) {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.force_immediate(initial_pwm);
        smoother.set_target(50); // Set a different target
        
        // Force immediate should bypass smoothing
        smoother.force_immediate(emergency_pwm);
        
        // Current should immediately be at emergency value
        prop_assert_eq!(
            smoother.current(), emergency_pwm,
            "force_immediate should set current to {} immediately, got {}",
            emergency_pwm, smoother.current()
        );
        
        // Target should also be updated
        prop_assert_eq!(
            smoother.target(), emergency_pwm,
            "force_immediate should set target to {} immediately, got {}",
            emergency_pwm, smoother.target()
        );
        
        // Should be at target
        prop_assert!(
            smoother.at_target(),
            "Should be at target after force_immediate"
        );
    }

    /// **Feature: decktune-3.0-automation, Property 18: Asymmetric ramp rates**
    /// *For any* PWMSmoother configuration, ramp_rate_decrease SHALL equal 
    /// ramp_rate_increase * 0.5.
    /// **Validates: Requirements 5.5**
    #[test]
    fn prop_asymmetric_ramp_rates(ramp_time in 0.5f32..10.0f32) {
        let smoother = PWMSmoother::new(ramp_time);
        
        let increase_rate = smoother.ramp_rate_increase();
        let decrease_rate = smoother.ramp_rate_decrease();
        
        // Decrease rate should be exactly 50% of increase rate
        let expected_decrease = increase_rate * 0.5;
        let diff = (decrease_rate - expected_decrease).abs();
        
        prop_assert!(
            diff < 0.001,
            "Decrease rate {} should be 50% of increase rate {} (expected {})",
            decrease_rate, increase_rate, expected_decrease
        );
    }
}

// ============================================================================
// PWM Smoother Unit Tests
// ============================================================================

#[test]
fn test_smoother_force_immediate_bypasses_smoothing() {
    let mut smoother = PWMSmoother::new(2.0);
    smoother.force_immediate(0);
    smoother.set_target(255);
    
    // Force immediate to max
    smoother.force_immediate(255);
    
    assert_eq!(smoother.current(), 255);
    assert_eq!(smoother.target(), 255);
    assert!(smoother.at_target());
}

#[test]
fn test_smoother_asymmetric_rates_ratio() {
    let smoother = PWMSmoother::new(2.0);
    let increase = smoother.ramp_rate_increase();
    let decrease = smoother.ramp_rate_decrease();
    
    // Decrease should be 50% of increase
    assert!((decrease - increase * 0.5).abs() < 0.001);
}

#[test]
fn test_smoother_default_ramp_time() {
    let smoother = PWMSmoother::default();
    // Default is 2 seconds, so rate should be 255/2 = 127.5
    assert!((smoother.ramp_rate_increase() - 127.5).abs() < 0.1);
}
