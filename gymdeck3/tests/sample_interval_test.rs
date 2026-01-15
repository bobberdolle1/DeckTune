//! Property-based tests for Sample Interval Validation
//!
//! **Feature: dynamic-mode-refactor, Property 2: Sample Interval Validation**
//! **Validates: Requirements 2.3**

use proptest::prelude::*;

use gymdeck3::{
    validate_sample_interval_ms,
    MIN_SAMPLE_INTERVAL_MS,
    MAX_SAMPLE_INTERVAL_MS,
    LoadMonitor,
};

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// Property 2: Sample Interval Validation
    ///
    /// For any sample interval value, if it is in range [10, 5000] milliseconds
    /// it SHALL be accepted, otherwise it SHALL be rejected with an error.
    ///
    /// **Validates: Requirements 2.3**
    #[test]
    fn prop_valid_sample_interval_accepted(
        interval in MIN_SAMPLE_INTERVAL_MS..=MAX_SAMPLE_INTERVAL_MS
    ) {
        // Any value in [10, 5000] should be accepted
        let result = validate_sample_interval_ms(interval);
        prop_assert!(
            result.is_ok(),
            "Valid interval {} ms should be accepted, got error: {:?}",
            interval,
            result.err()
        );
        
        // The returned value should be the same as input
        prop_assert_eq!(
            result.unwrap(),
            interval,
            "Returned interval should match input"
        );
    }

    /// Property: Values below minimum are rejected
    #[test]
    fn prop_below_minimum_rejected(
        interval in 0u64..MIN_SAMPLE_INTERVAL_MS
    ) {
        let result = validate_sample_interval_ms(interval);
        prop_assert!(
            result.is_err(),
            "Interval {} ms below minimum {} should be rejected",
            interval,
            MIN_SAMPLE_INTERVAL_MS
        );
    }

    /// Property: Values above maximum are rejected
    #[test]
    fn prop_above_maximum_rejected(
        interval in (MAX_SAMPLE_INTERVAL_MS + 1)..=u64::MAX
    ) {
        let result = validate_sample_interval_ms(interval);
        prop_assert!(
            result.is_err(),
            "Interval {} ms above maximum {} should be rejected",
            interval,
            MAX_SAMPLE_INTERVAL_MS
        );
    }

    /// Property: LoadMonitor accepts valid intervals
    #[test]
    fn prop_load_monitor_accepts_valid_interval(
        interval in MIN_SAMPLE_INTERVAL_MS..=MAX_SAMPLE_INTERVAL_MS
    ) {
        // LoadMonitor should accept valid intervals
        // (using a non-existent path to avoid actual file I/O)
        let result = LoadMonitor::with_path(interval, "/nonexistent".to_string());
        prop_assert!(
            result.is_ok(),
            "LoadMonitor should accept valid interval {} ms",
            interval
        );
    }

    /// Property: LoadMonitor rejects invalid intervals
    #[test]
    fn prop_load_monitor_rejects_invalid_interval(
        interval in prop::sample::select(vec![
            0u64, 1, 5, 9,  // Below minimum
            5001, 6000, 10000, u64::MAX  // Above maximum
        ])
    ) {
        let result = LoadMonitor::with_path(interval, "/nonexistent".to_string());
        prop_assert!(
            result.is_err(),
            "LoadMonitor should reject invalid interval {} ms",
            interval
        );
    }
}

/// Boundary tests for sample interval validation
#[cfg(test)]
mod boundary_tests {
    use super::*;

    #[test]
    fn test_exact_minimum_boundary() {
        // Exactly at minimum should be accepted
        assert!(validate_sample_interval_ms(MIN_SAMPLE_INTERVAL_MS).is_ok());
        // One below minimum should be rejected
        assert!(validate_sample_interval_ms(MIN_SAMPLE_INTERVAL_MS - 1).is_err());
    }

    #[test]
    fn test_exact_maximum_boundary() {
        // Exactly at maximum should be accepted
        assert!(validate_sample_interval_ms(MAX_SAMPLE_INTERVAL_MS).is_ok());
        // One above maximum should be rejected
        assert!(validate_sample_interval_ms(MAX_SAMPLE_INTERVAL_MS + 1).is_err());
    }

    #[test]
    fn test_constants_match_requirements() {
        // Requirements 2.3 specifies 10ms-5000ms range
        assert_eq!(MIN_SAMPLE_INTERVAL_MS, 10, "Minimum should be 10ms per Requirements 2.3");
        assert_eq!(MAX_SAMPLE_INTERVAL_MS, 5000, "Maximum should be 5000ms per Requirements 2.3");
    }
}
