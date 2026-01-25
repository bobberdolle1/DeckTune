//! Property-based tests for ryzenadj executor
//!
//! **Feature: dynamic-mode-refactor**
//!
//! These tests verify the correctness properties of the ryzenadj executor
//! as defined in the design document.

use proptest::prelude::*;
use gymdeck3::{
    simulate_failure_sequence,
    MAX_CONSECUTIVE_FAILURES,
};

/// Generate a sequence of success/failure results
fn arb_result_sequence(max_len: usize) -> impl Strategy<Value = Vec<bool>> {
    prop::collection::vec(any::<bool>(), 0..=max_len)
}

/// Generate a valid max_failures value (1 to 10)
fn arb_max_failures() -> impl Strategy<Value = u32> {
    1u32..=10u32
}

// =============================================================================
// Property 9: Consecutive Failure Exit
// **Validates: Requirements 6.5**
//
// For any sequence of ryzenadj calls, if exactly N consecutive calls fail
// (where N = max_failures), the system SHALL exit. If any call succeeds,
// the failure counter SHALL reset.
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// If exactly max_failures consecutive failures occur, the system should exit
    #[test]
    fn prop_consecutive_failures_trigger_exit(
        max_failures in arb_max_failures(),
    ) {
        // Create a sequence of exactly max_failures consecutive failures
        let results: Vec<bool> = vec![false; max_failures as usize];
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(
            outcome.is_err(),
            "Expected exit after {} consecutive failures, but got Ok({:?})",
            max_failures, outcome
        );
        
        if let Err(count) = outcome {
            prop_assert_eq!(
                count, max_failures,
                "Exit should occur at exactly {} failures, got {}",
                max_failures, count
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// If fewer than max_failures consecutive failures occur, system should not exit
    #[test]
    fn prop_under_limit_no_exit(
        max_failures in 2u32..=10u32,
        num_failures in 1u32..10u32,
    ) {
        // Ensure we're under the limit
        let actual_failures = num_failures.min(max_failures - 1);
        let results: Vec<bool> = vec![false; actual_failures as usize];
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(
            outcome.is_ok(),
            "Should not exit with {} failures when max is {}",
            actual_failures, max_failures
        );
        
        if let Ok(count) = outcome {
            prop_assert_eq!(
                count, actual_failures,
                "Final failure count should be {}, got {}",
                actual_failures, count
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// A success resets the failure counter
    #[test]
    fn prop_success_resets_counter(
        max_failures in arb_max_failures(),
        failures_before in 1u32..10u32,
    ) {
        // Ensure failures_before is less than max_failures
        let actual_failures = failures_before.min(max_failures - 1);
        
        // Sequence: some failures, then success
        let mut results: Vec<bool> = vec![false; actual_failures as usize];
        results.push(true); // Success resets counter
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(
            outcome.is_ok(),
            "Success should reset counter, preventing exit"
        );
        
        if let Ok(count) = outcome {
            prop_assert_eq!(
                count, 0,
                "Counter should be 0 after success, got {}",
                count
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// Success in the middle of failures resets the counter
    #[test]
    fn prop_success_in_middle_resets(
        max_failures in 3u32..=10u32,
        failures_before in 1u32..5u32,
        failures_after in 1u32..5u32,
    ) {
        // Ensure we don't hit the limit in either segment
        let actual_before = failures_before.min(max_failures - 1);
        let actual_after = failures_after.min(max_failures - 1);
        
        // Sequence: failures, success, failures
        let mut results: Vec<bool> = vec![false; actual_before as usize];
        results.push(true); // Success resets counter
        results.extend(vec![false; actual_after as usize]);
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(
            outcome.is_ok(),
            "Should not exit when success resets counter in middle"
        );
        
        if let Ok(count) = outcome {
            prop_assert_eq!(
                count, actual_after,
                "Counter should be {} after final failures, got {}",
                actual_after, count
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// All successes result in zero failure count
    #[test]
    fn prop_all_success_zero_count(
        max_failures in arb_max_failures(),
        num_successes in 1usize..20usize,
    ) {
        let results: Vec<bool> = vec![true; num_successes];
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(outcome.is_ok());
        prop_assert_eq!(outcome.unwrap(), 0);
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// Empty sequence results in zero failure count
    #[test]
    fn prop_empty_sequence_zero_count(
        max_failures in arb_max_failures(),
    ) {
        let results: Vec<bool> = vec![];
        
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        prop_assert!(outcome.is_ok());
        prop_assert_eq!(outcome.unwrap(), 0);
    }

    /// **Feature: dynamic-mode-refactor, Property 9: Consecutive Failure Exit**
    /// **Validates: Requirements 6.5**
    ///
    /// Random sequences behave correctly
    #[test]
    fn prop_random_sequence_correctness(
        max_failures in 2u32..=10u32,
        results in arb_result_sequence(30),
    ) {
        let outcome = simulate_failure_sequence(&results, max_failures);
        
        // Manually verify the outcome
        let mut consecutive = 0u32;
        let mut expected_exit = false;
        let mut exit_count = 0u32;
        
        for &success in &results {
            if success {
                consecutive = 0;
            } else {
                consecutive += 1;
                if consecutive >= max_failures {
                    expected_exit = true;
                    exit_count = consecutive;
                    break;
                }
            }
        }
        
        if expected_exit {
            prop_assert!(
                outcome.is_err(),
                "Expected exit at {} failures, but got Ok({:?})",
                exit_count, outcome
            );
            prop_assert_eq!(outcome.unwrap_err(), exit_count);
        } else {
            prop_assert!(
                outcome.is_ok(),
                "Did not expect exit, but got Err({:?})",
                outcome
            );
            prop_assert_eq!(outcome.unwrap(), consecutive);
        }
    }
}

// =============================================================================
// Additional boundary and edge case tests
// =============================================================================

#[cfg(test)]
mod boundary_tests {
    use super::*;

    #[test]
    fn test_default_max_failures_is_five() {
        assert_eq!(MAX_CONSECUTIVE_FAILURES, 5);
    }

    #[test]
    fn test_exactly_five_failures_exits() {
        let results = vec![false, false, false, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Err(5));
    }

    #[test]
    fn test_four_failures_no_exit() {
        let results = vec![false, false, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(4));
    }

    #[test]
    fn test_success_after_four_failures_resets() {
        let results = vec![false, false, false, false, true];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(0));
    }

    #[test]
    fn test_five_failures_after_success_exits() {
        let results = vec![true, false, false, false, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Err(5));
    }

    #[test]
    fn test_alternating_success_failure_no_exit() {
        // Alternating pattern never accumulates consecutive failures
        let results = vec![false, true, false, true, false, true, false, true];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(0)); // Ends with success
    }

    #[test]
    fn test_alternating_ending_with_failure() {
        let results = vec![true, false, true, false, true, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(1)); // Only 1 consecutive failure at end
    }

    #[test]
    fn test_max_failures_of_one() {
        // Edge case: max_failures = 1 means first failure exits
        let results = vec![false];
        let outcome = simulate_failure_sequence(&results, 1);
        assert_eq!(outcome, Err(1));
    }

    #[test]
    fn test_success_before_single_failure_limit() {
        let results = vec![true, false];
        let outcome = simulate_failure_sequence(&results, 1);
        assert_eq!(outcome, Err(1));
    }

    #[test]
    fn test_long_sequence_with_reset() {
        // 4 failures, success, 4 failures, success, 5 failures -> exit
        let results = vec![
            false, false, false, false, // 4 failures
            true,                        // reset
            false, false, false, false, // 4 failures
            true,                        // reset
            false, false, false, false, false, // 5 failures -> exit
        ];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Err(5));
    }

    #[test]
    fn test_long_sequence_without_exit() {
        // 4 failures, success, 4 failures, success, 4 failures
        let results = vec![
            false, false, false, false, // 4 failures
            true,                        // reset
            false, false, false, false, // 4 failures
            true,                        // reset
            false, false, false, false, // 4 failures
        ];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(4));
    }
}
