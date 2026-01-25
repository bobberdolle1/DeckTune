//! Property-based tests for interpolation engine
//!
//! **Feature: dynamic-mode-refactor**
//!
//! These tests verify the correctness properties of the interpolation engine
//! as defined in the design document.

use proptest::prelude::*;
use gymdeck3::{Interpolator, DEFAULT_STEP_SIZE_MV};

/// Generate valid undervolt values (-100 to 0)
fn arb_undervolt() -> impl Strategy<Value = i32> {
    -100i32..=0i32
}

/// Generate valid step sizes (1 to 10)
fn arb_step_size() -> impl Strategy<Value = i32> {
    1i32..=10i32
}

/// Generate number of cores (1 to 8)
fn arb_num_cores() -> impl Strategy<Value = usize> {
    1usize..=8usize
}

// =============================================================================
// Property 8: Interpolation Linearity
// **Validates: Requirements 5.1, 5.2**
//
// For any transition from value A to value B, the intermediate values produced
// by tick() SHALL form a linear sequence with step size of exactly 1mV
// (or reach target if distance < step).
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Each tick should move exactly step_size toward target (or reach target)
    #[test]
    fn prop_tick_moves_exactly_step_size(
        start in arb_undervolt(),
        target in arb_undervolt(),
        step_size in arb_step_size(),
    ) {
        let mut interp = Interpolator::with_step_size(1, step_size);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        let initial = interp.current_value(0);
        let values = interp.tick();
        let after_tick = values[0];
        
        let distance = (target - initial).abs();
        let actual_step = (after_tick - initial).abs();
        
        if distance <= step_size {
            // Should reach target directly
            prop_assert_eq!(
                after_tick, target,
                "Should reach target when distance ({}) <= step_size ({})",
                distance, step_size
            );
        } else {
            // Should move exactly step_size
            prop_assert_eq!(
                actual_step, step_size,
                "Should move exactly step_size ({}), but moved {}",
                step_size, actual_step
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Sequence of ticks should form linear progression
    #[test]
    fn prop_tick_sequence_is_linear(
        start in arb_undervolt(),
        target in arb_undervolt(),
        step_size in arb_step_size(),
    ) {
        let mut interp = Interpolator::with_step_size(1, step_size);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        let mut values: Vec<i32> = vec![start];
        
        // Collect all intermediate values until target is reached
        while interp.is_transitioning() {
            let tick_values = interp.tick();
            values.push(tick_values[0]);
            
            // Safety limit to prevent infinite loops
            if values.len() > 200 {
                break;
            }
        }
        
        // Verify linearity: each consecutive pair should differ by at most step_size
        for i in 1..values.len() {
            let diff = (values[i] - values[i-1]).abs();
            prop_assert!(
                diff <= step_size,
                "Non-linear step at index {}: {} -> {} (diff={}, step_size={})",
                i, values[i-1], values[i], diff, step_size
            );
        }
        
        // Verify final value is target
        prop_assert_eq!(
            *values.last().unwrap(), target,
            "Final value should be target"
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Direction of movement should be consistent toward target
    #[test]
    fn prop_tick_direction_toward_target(
        start in arb_undervolt(),
        target in arb_undervolt(),
        step_size in arb_step_size(),
    ) {
        // Skip if start == target (no movement needed)
        prop_assume!(start != target);
        
        let mut interp = Interpolator::with_step_size(1, step_size);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        let expected_direction = if target > start { 1 } else { -1 };
        
        let mut prev = start;
        while interp.is_transitioning() {
            let values = interp.tick();
            let current = values[0];
            
            if current != prev {
                let actual_direction = if current > prev { 1 } else { -1 };
                prop_assert_eq!(
                    actual_direction, expected_direction,
                    "Movement direction changed: prev={}, current={}, target={}",
                    prev, current, target
                );
            }
            prev = current;
            
            // Safety limit
            if (prev - start).abs() > 200 {
                break;
            }
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Default step size should be 1mV
    #[test]
    fn prop_default_step_size_is_1mv(
        start in arb_undervolt(),
        target in arb_undervolt(),
    ) {
        // Skip if start == target
        prop_assume!(start != target);
        prop_assume!((target - start).abs() > 1);
        
        let mut interp = Interpolator::new(1);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        prop_assert_eq!(interp.step_size(), DEFAULT_STEP_SIZE_MV);
        
        let values = interp.tick();
        let step = (values[0] - start).abs();
        
        prop_assert_eq!(
            step, 1,
            "Default step should be 1mV, but was {}",
            step
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Number of ticks to reach target should be ceil(distance / step_size)
    #[test]
    fn prop_tick_count_matches_distance(
        start in arb_undervolt(),
        target in arb_undervolt(),
        step_size in arb_step_size(),
    ) {
        let mut interp = Interpolator::with_step_size(1, step_size);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        let distance = (target - start).abs();
        let expected_ticks = if distance == 0 {
            0
        } else {
            (distance + step_size - 1) / step_size // ceil division
        };
        
        let mut tick_count = 0;
        while interp.is_transitioning() {
            interp.tick();
            tick_count += 1;
            
            // Safety limit
            if tick_count > 200 {
                break;
            }
        }
        
        prop_assert_eq!(
            tick_count, expected_ticks as usize,
            "Expected {} ticks for distance {} with step {}, got {}",
            expected_ticks, distance, step_size, tick_count
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 8: Interpolation Linearity**
    /// **Validates: Requirements 5.1, 5.2**
    ///
    /// Multiple cores should interpolate independently
    #[test]
    fn prop_multi_core_independent_interpolation(
        num_cores in 2usize..=4usize,
        step_size in arb_step_size(),
    ) {
        let mut interp = Interpolator::with_step_size(num_cores, step_size);
        
        // Set different start and target for each core
        let starts: Vec<i32> = (0..num_cores).map(|i| -(i as i32 * 10)).collect();
        let targets: Vec<i32> = (0..num_cores).map(|i| -(i as i32 * 10 + 20)).collect();
        
        interp.force_immediate(starts.clone());
        interp.set_targets(targets.clone());
        
        // Tick once
        let values = interp.tick();
        
        // Each core should move independently toward its target
        for i in 0..num_cores {
            let distance = (targets[i] - starts[i]).abs();
            let actual_step = (values[i] - starts[i]).abs();
            
            if distance <= step_size {
                prop_assert_eq!(
                    values[i], targets[i],
                    "Core {} should reach target", i
                );
            } else {
                prop_assert_eq!(
                    actual_step, step_size,
                    "Core {} should move exactly step_size", i
                );
            }
        }
    }
}

// =============================================================================
// Additional tests for force_immediate and edge cases
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// Force immediate should bypass interpolation completely
    #[test]
    fn prop_force_immediate_bypasses_interpolation(
        start in arb_undervolt(),
        target in arb_undervolt(),
        force_value in arb_undervolt(),
    ) {
        let mut interp = Interpolator::new(1);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        // Force immediate to a different value
        interp.force_immediate(vec![force_value]);
        
        // Both current and target should be force_value
        prop_assert_eq!(interp.current_value(0), force_value);
        prop_assert_eq!(interp.target_value(0), force_value);
        prop_assert!(!interp.is_transitioning());
    }

    /// Force reset to zero should set all values to 0
    #[test]
    fn prop_force_reset_to_zero(
        num_cores in arb_num_cores(),
    ) {
        let mut interp = Interpolator::new(num_cores);
        
        // Set various targets
        let targets: Vec<i32> = (0..num_cores).map(|i| -(i as i32 * 5 + 10)).collect();
        interp.set_targets(targets);
        
        // Tick a few times
        for _ in 0..3 {
            interp.tick();
        }
        
        // Force reset
        interp.force_reset_to_zero();
        
        // All values should be 0
        for i in 0..num_cores {
            prop_assert_eq!(interp.current_value(i), 0);
            prop_assert_eq!(interp.target_value(i), 0);
        }
        prop_assert!(!interp.is_transitioning());
    }

    /// Remaining distance should decrease with each tick
    #[test]
    fn prop_remaining_distance_decreases(
        start in arb_undervolt(),
        target in arb_undervolt(),
        step_size in arb_step_size(),
    ) {
        prop_assume!(start != target);
        
        let mut interp = Interpolator::with_step_size(1, step_size);
        interp.force_immediate(vec![start]);
        interp.set_target(0, target);
        
        let mut prev_distance = interp.remaining_distance(0);
        
        while interp.is_transitioning() {
            interp.tick();
            let current_distance = interp.remaining_distance(0);
            
            prop_assert!(
                current_distance < prev_distance,
                "Distance should decrease: prev={}, current={}",
                prev_distance, current_distance
            );
            
            prev_distance = current_distance;
            
            // Safety limit
            if prev_distance > 200 {
                break;
            }
        }
        
        prop_assert_eq!(
            interp.remaining_distance(0), 0,
            "Final distance should be 0"
        );
    }
}

#[cfg(test)]
mod edge_case_tests {
    use super::*;

    #[test]
    fn test_no_transition_when_at_target() {
        let mut interp = Interpolator::new(1);
        interp.force_immediate(vec![-30]);
        interp.set_target(0, -30);
        
        assert!(!interp.is_transitioning());
        
        let values = interp.tick();
        assert_eq!(values[0], -30);
    }

    #[test]
    fn test_transition_from_zero() {
        let mut interp = Interpolator::new(1);
        interp.set_target(0, -5);
        
        assert!(interp.is_transitioning());
        
        let mut values = vec![0];
        for _ in 0..5 {
            let tick = interp.tick();
            values.push(tick[0]);
        }
        
        assert_eq!(values, vec![0, -1, -2, -3, -4, -5]);
        assert!(!interp.is_transitioning());
    }

    #[test]
    fn test_transition_to_zero() {
        let mut interp = Interpolator::new(1);
        interp.force_immediate(vec![-5]);
        interp.set_target(0, 0);
        
        let mut values = vec![-5];
        for _ in 0..5 {
            let tick = interp.tick();
            values.push(tick[0]);
        }
        
        assert_eq!(values, vec![-5, -4, -3, -2, -1, 0]);
    }

    #[test]
    fn test_large_step_size() {
        let mut interp = Interpolator::with_step_size(1, 10);
        interp.force_immediate(vec![0]);
        interp.set_target(0, -25);
        
        let mut values = vec![0];
        while interp.is_transitioning() {
            let tick = interp.tick();
            values.push(tick[0]);
        }
        
        // 0 -> -10 -> -20 -> -25
        assert_eq!(values, vec![0, -10, -20, -25]);
    }

    #[test]
    fn test_step_larger_than_distance() {
        let mut interp = Interpolator::with_step_size(1, 10);
        interp.force_immediate(vec![0]);
        interp.set_target(0, -3);
        
        let values = interp.tick();
        assert_eq!(values[0], -3); // Should jump directly to target
        assert!(!interp.is_transitioning());
    }
}
