//! Property-based tests for CLI argument validation
//! 
//! **Feature: dynamic-mode-refactor, Property 11: CLI Argument Validation**
//! **Validates: Requirements 8.1-8.8**
//!
//! For any CLI arguments, valid combinations SHALL be accepted and produce correct Config,
//! invalid combinations SHALL cause exit with code 1 and usage message.

use proptest::prelude::*;
use proptest::strategy::Strategy as PropStrategy;

// Import specific items to avoid naming conflicts
use gymdeck3::{
    validate_sample_interval_value,
    validate_hysteresis_value,
    validate_core_config_values,
    parse_core_config,
};

/// Strategy for generating valid sample intervals (10000-5000000 us)
fn valid_sample_interval() -> impl PropStrategy<Value = u64> {
    10_000u64..=5_000_000u64
}

/// Strategy for generating invalid sample intervals (outside valid range)
fn invalid_sample_interval() -> impl PropStrategy<Value = u64> {
    prop_oneof![
        0u64..10_000u64,           // Too small
        5_000_001u64..10_000_000u64 // Too large
    ]
}

/// Strategy for generating valid hysteresis values (1.0-20.0%)
fn valid_hysteresis() -> impl PropStrategy<Value = f32> {
    1.0f32..=20.0f32
}

/// Strategy for generating invalid hysteresis values
fn invalid_hysteresis() -> impl PropStrategy<Value = f32> {
    prop_oneof![
        0.0f32..1.0f32,    // Too small (but not negative to avoid NaN issues)
        20.1f32..100.0f32  // Too large
    ]
}

/// Strategy for generating valid undervolt values (negative or zero)
fn valid_undervolt() -> impl PropStrategy<Value = i32> {
    -100i32..=0i32
}

/// Strategy for generating valid threshold values (0.0-100.0)
fn valid_threshold() -> impl PropStrategy<Value = f32> {
    0.0f32..=100.0f32
}

/// Strategy for generating invalid threshold values
fn invalid_threshold() -> impl PropStrategy<Value = f32> {
    prop_oneof![
        -100.0f32..-0.1f32,  // Negative
        100.1f32..200.0f32   // Too large
    ]
}

/// Strategy for generating valid core configs
fn valid_core_config() -> impl PropStrategy<Value = (usize, i32, i32, f32)> {
    (
        0usize..8usize,           // core_id (0-7 for typical CPUs)
        valid_undervolt(),        // min_mv
        valid_undervolt(),        // max_mv  
        valid_threshold(),        // threshold
    ).prop_filter("max_mv must be <= min_mv", |(_, min_mv, max_mv, _)| {
        *max_mv <= *min_mv
    })
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// Property: Valid sample intervals in range [10000, 5000000] SHALL be accepted
    #[test]
    fn prop_valid_sample_interval_accepted(val in valid_sample_interval()) {
        let result = validate_sample_interval_value(val);
        prop_assert!(result.is_ok(), "Valid sample interval {} should be accepted", val);
        prop_assert_eq!(result.unwrap(), val);
    }

    /// Property: Invalid sample intervals outside range SHALL be rejected
    #[test]
    fn prop_invalid_sample_interval_rejected(val in invalid_sample_interval()) {
        let result = validate_sample_interval_value(val);
        prop_assert!(result.is_err(), "Invalid sample interval {} should be rejected", val);
    }

    /// Property: Valid hysteresis values in range [1.0, 20.0] SHALL be accepted
    #[test]
    fn prop_valid_hysteresis_accepted(val in valid_hysteresis()) {
        let result = validate_hysteresis_value(val);
        prop_assert!(result.is_ok(), "Valid hysteresis {}% should be accepted", val);
        prop_assert!((result.unwrap() - val).abs() < f32::EPSILON);
    }

    /// Property: Invalid hysteresis values outside range SHALL be rejected
    #[test]
    fn prop_invalid_hysteresis_rejected(val in invalid_hysteresis()) {
        let result = validate_hysteresis_value(val);
        prop_assert!(result.is_err(), "Invalid hysteresis {}% should be rejected", val);
    }

    /// Property: Valid core configurations SHALL be accepted
    #[test]
    fn prop_valid_core_config_accepted((core_id, min_mv, max_mv, threshold) in valid_core_config()) {
        let result = validate_core_config_values(core_id, min_mv, max_mv, threshold);
        prop_assert!(
            result.is_ok(),
            "Valid core config (id={}, min={}, max={}, thresh={}) should be accepted",
            core_id, min_mv, max_mv, threshold
        );
        
        let config = result.unwrap();
        prop_assert_eq!(config.core_id, core_id);
        prop_assert_eq!(config.min_mv, min_mv);
        prop_assert_eq!(config.max_mv, max_mv);
        prop_assert!((config.threshold - threshold).abs() < f32::EPSILON);
    }

    /// Property: Core configs with positive undervolt values SHALL be rejected
    #[test]
    fn prop_positive_undervolt_rejected(
        core_id in 0usize..8usize,
        positive_mv in 1i32..100i32,
        threshold in valid_threshold()
    ) {
        // Test positive min_mv
        let result = validate_core_config_values(core_id, positive_mv, -30, threshold);
        prop_assert!(result.is_err(), "Positive min_mv {} should be rejected", positive_mv);
        
        // Test positive max_mv
        let result = validate_core_config_values(core_id, -20, positive_mv, threshold);
        prop_assert!(result.is_err(), "Positive max_mv {} should be rejected", positive_mv);
    }

    /// Property: Core configs with max_mv > min_mv SHALL be rejected
    #[test]
    fn prop_invalid_mv_order_rejected(
        core_id in 0usize..8usize,
        min_mv in -50i32..=-10i32,
        threshold in valid_threshold()
    ) {
        // max_mv should be more negative than min_mv, so max_mv > min_mv is invalid
        let max_mv = min_mv + 5; // This makes max_mv > min_mv (less negative)
        if max_mv <= 0 {
            let result = validate_core_config_values(core_id, min_mv, max_mv, threshold);
            prop_assert!(
                result.is_err(),
                "max_mv ({}) > min_mv ({}) should be rejected",
                max_mv, min_mv
            );
        }
    }

    /// Property: Core configs with invalid threshold SHALL be rejected
    #[test]
    fn prop_invalid_threshold_rejected(
        core_id in 0usize..8usize,
        min_mv in valid_undervolt(),
        threshold in invalid_threshold()
    ) {
        let max_mv = min_mv - 10; // Ensure max_mv <= min_mv
        let result = validate_core_config_values(core_id, min_mv, max_mv.max(-100), threshold);
        prop_assert!(
            result.is_err(),
            "Invalid threshold {} should be rejected",
            threshold
        );
    }

    /// Property: Core config string parsing produces correct values
    #[test]
    fn prop_core_config_string_parsing((core_id, min_mv, max_mv, threshold) in valid_core_config()) {
        let config_str = format!("{}:{}:{}:{}", core_id, min_mv, max_mv, threshold);
        let result = parse_core_config(&config_str);
        
        prop_assert!(
            result.is_ok(),
            "Valid config string '{}' should parse successfully",
            config_str
        );
        
        let config = result.unwrap();
        prop_assert_eq!(config.core_id, core_id);
        prop_assert_eq!(config.min_mv, min_mv);
        prop_assert_eq!(config.max_mv, max_mv);
        // Allow small floating point differences
        prop_assert!(
            (config.threshold - threshold).abs() < 0.001,
            "Threshold mismatch: {} vs {}",
            config.threshold, threshold
        );
    }

    /// Property: Malformed core config strings SHALL be rejected
    #[test]
    fn prop_malformed_core_config_rejected(
        parts in prop::collection::vec("[a-zA-Z0-9.-]+", 0..3)
    ) {
        // Generate strings with wrong number of parts (not 4)
        let config_str = parts.join(":");
        let result = parse_core_config(&config_str);
        prop_assert!(
            result.is_err(),
            "Malformed config string '{}' with {} parts should be rejected",
            config_str, parts.len()
        );
    }
}

#[cfg(test)]
mod boundary_tests {
    use super::*;

    /// Test exact boundary values for sample interval
    #[test]
    fn test_sample_interval_boundaries() {
        // Exact minimum
        assert!(validate_sample_interval_value(10_000).is_ok());
        // Just below minimum
        assert!(validate_sample_interval_value(9_999).is_err());
        // Exact maximum
        assert!(validate_sample_interval_value(5_000_000).is_ok());
        // Just above maximum
        assert!(validate_sample_interval_value(5_000_001).is_err());
    }

    /// Test exact boundary values for hysteresis
    #[test]
    fn test_hysteresis_boundaries() {
        // Exact minimum
        assert!(validate_hysteresis_value(1.0).is_ok());
        // Just below minimum
        assert!(validate_hysteresis_value(0.99).is_err());
        // Exact maximum
        assert!(validate_hysteresis_value(20.0).is_ok());
        // Just above maximum
        assert!(validate_hysteresis_value(20.01).is_err());
    }

    /// Test exact boundary values for threshold
    #[test]
    fn test_threshold_boundaries() {
        // Exact minimum
        assert!(validate_core_config_values(0, -20, -30, 0.0).is_ok());
        // Exact maximum
        assert!(validate_core_config_values(0, -20, -30, 100.0).is_ok());
        // Just below minimum
        assert!(validate_core_config_values(0, -20, -30, -0.1).is_err());
        // Just above maximum
        assert!(validate_core_config_values(0, -20, -30, 100.1).is_err());
    }

    /// Test undervolt value boundaries
    #[test]
    fn test_undervolt_boundaries() {
        // Zero is valid
        assert!(validate_core_config_values(0, 0, -30, 50.0).is_ok());
        assert!(validate_core_config_values(0, -20, 0, 50.0).is_err()); // max > min
        // Positive is invalid
        assert!(validate_core_config_values(0, 1, -30, 50.0).is_err());
        assert!(validate_core_config_values(0, -20, 1, 50.0).is_err());
    }
}
