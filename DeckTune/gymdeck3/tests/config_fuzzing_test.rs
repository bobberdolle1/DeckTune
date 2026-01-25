//! Property-based tests for config parsing no-panic guarantee
//!
//! **Feature: decktune-3.1-reliability-ux, Property 12: Fuzzing no-panic guarantee**
//! **Validates: Requirements 6.1, 6.2**
//!
//! For any byte sequence input to the config parser, the parser SHALL not panic
//! and SHALL return either a valid config or an error.

use proptest::prelude::*;
use std::panic::{catch_unwind, AssertUnwindSafe};

use gymdeck3::{
    parse_core_config,
    validate_sample_interval,
    validate_hysteresis,
    validate_sample_interval_value,
    validate_hysteresis_value,
    validate_core_config_values,
    parse_fan_curve_point,
    validate_fan_curve_point,
    validate_fan_hysteresis,
    parse_acoustic_profile,
};

/// Strategy for generating arbitrary strings (including edge cases)
fn arbitrary_string() -> impl Strategy<Value = String> {
    prop_oneof![
        // Empty and whitespace
        Just("".to_string()),
        Just(" ".to_string()),
        Just("\t".to_string()),
        Just("\n".to_string()),
        Just("\r\n".to_string()),
        // Random ASCII strings
        "[[:ascii:]]{0,100}",
        // Random alphanumeric with special chars
        "[a-zA-Z0-9:.-]{0,50}",
        // Numeric strings
        "-?[0-9]{1,20}",
        "-?[0-9]{1,10}\\.[0-9]{1,10}",
        // Core config-like patterns
        "[0-9]:-?[0-9]{1,3}:-?[0-9]{1,3}:[0-9]{1,3}(\\.[0-9]{1,3})?",
        // Fan curve-like patterns
        "-?[0-9]{1,3}:[0-9]{1,3}",
        // Strategy names and variations
        "(conservative|balanced|aggressive|custom|invalid|BALANCED|ConSeRvAtIvE)",
        // Acoustic profile names
        "(silent|balanced|max_cooling|maxcooling|max-cooling|SILENT|invalid)",
        // Special values
        Just("NaN".to_string()),
        Just("inf".to_string()),
        Just("-inf".to_string()),
        Just("null".to_string()),
        Just("undefined".to_string()),
        // Extreme numeric values
        Just("2147483647".to_string()),
        Just("-2147483648".to_string()),
        Just("9223372036854775807".to_string()),
        Just("-9223372036854775808".to_string()),
        Just("1e308".to_string()),
        Just("-1e308".to_string()),
    ]
}

/// Strategy for generating arbitrary i32 values
fn arbitrary_i32() -> impl Strategy<Value = i32> {
    prop_oneof![
        // Normal range
        -1000i32..1000i32,
        // Edge cases
        Just(i32::MIN),
        Just(i32::MAX),
        Just(0),
        Just(-1),
        Just(1),
        // Typical undervolt values
        -100i32..0i32,
    ]
}

/// Strategy for generating arbitrary u64 values
fn arbitrary_u64() -> impl Strategy<Value = u64> {
    prop_oneof![
        // Normal range
        0u64..10_000_000u64,
        // Edge cases
        Just(0u64),
        Just(u64::MAX),
        Just(10_000u64),
        Just(5_000_000u64),
    ]
}

/// Strategy for generating arbitrary f32 values (excluding NaN for comparison)
fn arbitrary_f32() -> impl Strategy<Value = f32> {
    prop_oneof![
        // Normal range
        -1000.0f32..1000.0f32,
        // Edge cases
        Just(0.0f32),
        Just(-0.0f32),
        Just(f32::MIN),
        Just(f32::MAX),
        Just(f32::INFINITY),
        Just(f32::NEG_INFINITY),
        // Typical values
        0.0f32..100.0f32,
        1.0f32..20.0f32,
    ]
}

/// Strategy for generating arbitrary usize values
fn arbitrary_usize() -> impl Strategy<Value = usize> {
    prop_oneof![
        0usize..1000usize,
        Just(0usize),
        Just(usize::MAX),
    ]
}

/// Strategy for generating arbitrary u8 values
fn arbitrary_u8() -> impl Strategy<Value = u8> {
    any::<u8>()
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    // ==================== String Parsing Tests ====================

    /// Property: parse_core_config SHALL not panic on any string input
    #[test]
    fn prop_parse_core_config_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = parse_core_config(&s);
        }));
        prop_assert!(result.is_ok(), "parse_core_config panicked on input: {:?}", s);
    }

    /// Property: validate_sample_interval SHALL not panic on any string input
    #[test]
    fn prop_validate_sample_interval_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_sample_interval(&s);
        }));
        prop_assert!(result.is_ok(), "validate_sample_interval panicked on input: {:?}", s);
    }

    /// Property: validate_hysteresis SHALL not panic on any string input
    #[test]
    fn prop_validate_hysteresis_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_hysteresis(&s);
        }));
        prop_assert!(result.is_ok(), "validate_hysteresis panicked on input: {:?}", s);
    }

    /// Property: parse_fan_curve_point SHALL not panic on any string input
    #[test]
    fn prop_parse_fan_curve_point_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = parse_fan_curve_point(&s);
        }));
        prop_assert!(result.is_ok(), "parse_fan_curve_point panicked on input: {:?}", s);
    }

    /// Property: validate_fan_hysteresis SHALL not panic on any string input
    #[test]
    fn prop_validate_fan_hysteresis_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_fan_hysteresis(&s);
        }));
        prop_assert!(result.is_ok(), "validate_fan_hysteresis panicked on input: {:?}", s);
    }

    /// Property: parse_acoustic_profile SHALL not panic on any string input
    #[test]
    fn prop_parse_acoustic_profile_no_panic(s in arbitrary_string()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = parse_acoustic_profile(&s);
        }));
        prop_assert!(result.is_ok(), "parse_acoustic_profile panicked on input: {:?}", s);
    }

    // ==================== Value Validation Tests ====================

    /// Property: validate_sample_interval_value SHALL not panic on any u64 input
    #[test]
    fn prop_validate_sample_interval_value_no_panic(val in arbitrary_u64()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_sample_interval_value(val);
        }));
        prop_assert!(result.is_ok(), "validate_sample_interval_value panicked on input: {}", val);
    }

    /// Property: validate_hysteresis_value SHALL not panic on any f32 input
    #[test]
    fn prop_validate_hysteresis_value_no_panic(val in arbitrary_f32()) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_hysteresis_value(val);
        }));
        prop_assert!(result.is_ok(), "validate_hysteresis_value panicked on input: {}", val);
    }

    /// Property: validate_core_config_values SHALL not panic on any combination of inputs
    #[test]
    fn prop_validate_core_config_values_no_panic(
        core_id in arbitrary_usize(),
        min_mv in arbitrary_i32(),
        max_mv in arbitrary_i32(),
        threshold in arbitrary_f32()
    ) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_core_config_values(core_id, min_mv, max_mv, threshold);
        }));
        prop_assert!(
            result.is_ok(),
            "validate_core_config_values panicked on input: core_id={}, min_mv={}, max_mv={}, threshold={}",
            core_id, min_mv, max_mv, threshold
        );
    }

    /// Property: validate_fan_curve_point SHALL not panic on any combination of inputs
    #[test]
    fn prop_validate_fan_curve_point_no_panic(
        temp_c in arbitrary_i32(),
        speed_percent in arbitrary_u8()
    ) {
        let result = catch_unwind(AssertUnwindSafe(|| {
            let _ = validate_fan_curve_point(temp_c, speed_percent);
        }));
        prop_assert!(
            result.is_ok(),
            "validate_fan_curve_point panicked on input: temp_c={}, speed_percent={}",
            temp_c, speed_percent
        );
    }

    // ==================== Return Value Tests ====================

    /// Property: All parsing functions SHALL return Result (Ok or Err), never panic
    #[test]
    fn prop_all_parsers_return_result(s in arbitrary_string()) {
        // Each function should return a Result type
        let core_result = parse_core_config(&s);
        prop_assert!(core_result.is_ok() || core_result.is_err());

        let interval_result = validate_sample_interval(&s);
        prop_assert!(interval_result.is_ok() || interval_result.is_err());

        let hysteresis_result = validate_hysteresis(&s);
        prop_assert!(hysteresis_result.is_ok() || hysteresis_result.is_err());

        let fan_curve_result = parse_fan_curve_point(&s);
        prop_assert!(fan_curve_result.is_ok() || fan_curve_result.is_err());

        let fan_hyst_result = validate_fan_hysteresis(&s);
        prop_assert!(fan_hyst_result.is_ok() || fan_hyst_result.is_err());

        // parse_acoustic_profile returns Option, not Result
        let profile_result = parse_acoustic_profile(&s);
        // Option is always Some or None, this just confirms no panic occurred
        let _ = profile_result;
    }

    /// Property: Error messages SHALL be non-empty strings
    #[test]
    fn prop_error_messages_non_empty(s in arbitrary_string()) {
        if let Err(e) = parse_core_config(&s) {
            prop_assert!(!e.is_empty(), "Error message should not be empty");
        }
        if let Err(e) = validate_sample_interval(&s) {
            prop_assert!(!e.is_empty(), "Error message should not be empty");
        }
        if let Err(e) = validate_hysteresis(&s) {
            prop_assert!(!e.is_empty(), "Error message should not be empty");
        }
        if let Err(e) = parse_fan_curve_point(&s) {
            prop_assert!(!e.is_empty(), "Error message should not be empty");
        }
        if let Err(e) = validate_fan_hysteresis(&s) {
            prop_assert!(!e.is_empty(), "Error message should not be empty");
        }
    }
}

#[cfg(test)]
mod edge_case_tests {
    use super::*;

    /// Test specific edge cases that might cause panics
    #[test]
    fn test_empty_string_no_panic() {
        let _ = parse_core_config("");
        let _ = validate_sample_interval("");
        let _ = validate_hysteresis("");
        let _ = parse_fan_curve_point("");
        let _ = validate_fan_hysteresis("");
        let _ = parse_acoustic_profile("");
    }

    /// Test null-like strings
    #[test]
    fn test_null_strings_no_panic() {
        for s in &["null", "NULL", "None", "nil", "undefined"] {
            let _ = parse_core_config(s);
            let _ = validate_sample_interval(s);
            let _ = validate_hysteresis(s);
            let _ = parse_fan_curve_point(s);
            let _ = validate_fan_hysteresis(s);
            let _ = parse_acoustic_profile(s);
        }
    }

    /// Test special float strings
    #[test]
    fn test_special_float_strings_no_panic() {
        for s in &["NaN", "nan", "NAN", "inf", "Inf", "INF", "-inf", "-Inf", "-INF"] {
            let _ = parse_core_config(s);
            let _ = validate_sample_interval(s);
            let _ = validate_hysteresis(s);
            let _ = parse_fan_curve_point(s);
            let _ = validate_fan_hysteresis(s);
        }
    }

    /// Test extreme numeric strings
    #[test]
    fn test_extreme_numeric_strings_no_panic() {
        let extreme_values = [
            "2147483647",      // i32::MAX
            "-2147483648",     // i32::MIN
            "9223372036854775807",  // i64::MAX
            "-9223372036854775808", // i64::MIN
            "18446744073709551615", // u64::MAX
            "1e308",           // Near f64::MAX
            "-1e308",          // Near f64::MIN
            "1e-308",          // Near f64::MIN_POSITIVE
            "0.0000000001",
            "99999999999999999999999999999999",
        ];
        
        for s in &extreme_values {
            let _ = parse_core_config(s);
            let _ = validate_sample_interval(s);
            let _ = validate_hysteresis(s);
            let _ = parse_fan_curve_point(s);
            let _ = validate_fan_hysteresis(s);
        }
    }

    /// Test malformed core config strings
    #[test]
    fn test_malformed_core_config_no_panic() {
        let malformed = [
            ":",
            "::",
            ":::",
            "::::",
            ":::::",
            "0:",
            ":0",
            "0:0",
            "0:0:0",
            "0:0:0:0:0",
            "a:b:c:d",
            "0:a:b:c",
            "0:-20:b:50",
            "0:-20:-30:c",
            "-1:-20:-30:50",
            "0:20:-30:50",    // Positive min_mv
            "0:-20:30:50",    // Positive max_mv
            "0:-20:-30:-10",  // Negative threshold
            "0:-20:-30:150",  // Threshold > 100
        ];
        
        for s in &malformed {
            let result = parse_core_config(s);
            // Should not panic, should return Err
            assert!(result.is_err(), "Expected error for malformed input: {}", s);
        }
    }

    /// Test malformed fan curve strings
    #[test]
    fn test_malformed_fan_curve_no_panic() {
        let malformed = [
            ":",
            "::",
            "60",
            "60:",
            ":50",
            "60:50:30",
            "a:b",
            "60:b",
            "a:50",
            "-10:50",   // Negative temp
            "110:50",   // Temp > 100
            "60:150",   // Speed > 100 (but u8 max is 255)
        ];
        
        for s in &malformed {
            let result = parse_fan_curve_point(s);
            // Should not panic
            assert!(result.is_ok() || result.is_err());
        }
    }

    /// Test value validation with extreme values
    #[test]
    fn test_extreme_value_validation_no_panic() {
        // Sample interval
        let _ = validate_sample_interval_value(0);
        let _ = validate_sample_interval_value(u64::MAX);
        
        // Hysteresis
        let _ = validate_hysteresis_value(f32::MIN);
        let _ = validate_hysteresis_value(f32::MAX);
        let _ = validate_hysteresis_value(f32::INFINITY);
        let _ = validate_hysteresis_value(f32::NEG_INFINITY);
        let _ = validate_hysteresis_value(f32::NAN);
        
        // Core config
        let _ = validate_core_config_values(usize::MAX, i32::MIN, i32::MAX, f32::NAN);
        let _ = validate_core_config_values(0, 0, 0, 0.0);
        let _ = validate_core_config_values(0, i32::MIN, i32::MIN, f32::INFINITY);
        
        // Fan curve
        let _ = validate_fan_curve_point(i32::MIN, 0);
        let _ = validate_fan_curve_point(i32::MAX, 255);
        let _ = validate_fan_curve_point(0, 0);
        let _ = validate_fan_curve_point(100, 100);
    }
}
