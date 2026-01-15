//! Property-based tests for hysteresis controller
//!
//! **Feature: dynamic-mode-refactor**
//!
//! These tests verify the correctness properties of the hysteresis controller
//! as defined in the design document.

use proptest::prelude::*;
use gymdeck3::{
    HysteresisController,
    MIN_HYSTERESIS_PERCENT,
    MAX_HYSTERESIS_PERCENT,
};

/// Generate valid hysteresis margin (1.0 - 20.0%)
fn arb_hysteresis_margin() -> impl Strategy<Value = f32> {
    (MIN_HYSTERESIS_PERCENT..=MAX_HYSTERESIS_PERCENT)
}

/// Generate valid load values (0.0 to 100.0)
fn arb_load() -> impl Strategy<Value = f32> {
    0.0f32..=100.0f32
}

/// Generate valid undervolt values (-100 to 0)
fn arb_undervolt() -> impl Strategy<Value = i32> {
    -100i32..=0i32
}

/// Generate number of cores (1 to 8)
fn arb_num_cores() -> impl Strategy<Value = usize> {
    1usize..=8usize
}

/// Generate a load fluctuation within a margin
fn arb_load_fluctuation_within_margin(base_load: f32, margin: f32) -> impl Strategy<Value = f32> {
    let lower = (base_load - margin).max(0.0);
    let upper = (base_load + margin).min(100.0);
    lower..=upper
}

// =============================================================================
// Property 6: Hysteresis Dead-Band Stability
// **Validates: Requirements 4.1, 4.2**
//
// For any hysteresis controller with margin M%, if load fluctuates within ±M%
// of the last stable value, the output undervolt SHALL remain unchanged.
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 6: Hysteresis Dead-Band Stability**
    /// **Validates: Requirements 4.1, 4.2**
    ///
    /// When load fluctuates within the dead-band, output should remain unchanged
    #[test]
    fn prop_deadband_stability_single_fluctuation(
        margin in arb_hysteresis_margin(),
        initial_load in 10.0f32..90.0f32, // Avoid edge cases at 0 and 100
        initial_target in arb_undervolt(),
        fluctuation_offset in -1.0f32..=1.0f32, // Normalized offset within margin
    ) {
        let mut controller = HysteresisController::new(margin, 1);
        
        // Establish baseline
        let first_output = controller.process(0, initial_load, initial_target);
        prop_assert_eq!(first_output, initial_target);
        
        // Calculate fluctuating load within dead-band
        // Scale the offset to be within margin
        let fluctuating_load = initial_load + (fluctuation_offset * margin * 0.99);
        let fluctuating_load = fluctuating_load.clamp(0.0, 100.0);
        
        // New target that would be different
        let new_target = initial_target.saturating_add(5).min(0);
        
        // Process with fluctuating load
        let output = controller.process(0, fluctuating_load, new_target);
        
        // Output should remain unchanged (dead-band stability)
        prop_assert_eq!(
            output, initial_target,
            "Dead-band violated: margin={}%, initial_load={}, fluctuating_load={}, \
             expected output={}, got={}",
            margin, initial_load, fluctuating_load, initial_target, output
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 6: Hysteresis Dead-Band Stability**
    /// **Validates: Requirements 4.1, 4.2**
    ///
    /// Multiple fluctuations within dead-band should all maintain the same output
    #[test]
    fn prop_deadband_stability_multiple_fluctuations(
        margin in arb_hysteresis_margin(),
        initial_load in 20.0f32..80.0f32,
        initial_target in arb_undervolt(),
        num_fluctuations in 2usize..10usize,
    ) {
        let mut controller = HysteresisController::new(margin, 1);
        
        // Establish baseline
        let first_output = controller.process(0, initial_load, initial_target);
        prop_assert_eq!(first_output, initial_target);
        
        // Generate multiple fluctuations within dead-band
        for i in 0..num_fluctuations {
            // Alternate between positive and negative offsets within margin
            let offset = if i % 2 == 0 { margin * 0.5 } else { -margin * 0.5 };
            let fluctuating_load = (initial_load + offset).clamp(0.0, 100.0);
            
            // Different target each time
            let new_target = initial_target.saturating_add(i as i32).min(0);
            
            let output = controller.process(0, fluctuating_load, new_target);
            
            prop_assert_eq!(
                output, initial_target,
                "Dead-band violated on fluctuation {}: margin={}%, initial_load={}, \
                 fluctuating_load={}, expected={}, got={}",
                i, margin, initial_load, fluctuating_load, initial_target, output
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 6: Hysteresis Dead-Band Stability**
    /// **Validates: Requirements 4.1, 4.2**
    ///
    /// Load exactly at boundary should still be within dead-band
    #[test]
    fn prop_deadband_boundary_inclusive(
        margin in arb_hysteresis_margin(),
        initial_load in 20.0f32..80.0f32,
        initial_target in arb_undervolt(),
    ) {
        let mut controller = HysteresisController::new(margin, 1);
        
        // Establish baseline
        controller.process(0, initial_load, initial_target);
        
        // Test at exact upper boundary
        let upper_boundary = (initial_load + margin).min(100.0);
        let new_target = initial_target.saturating_add(10).min(0);
        let output_upper = controller.process(0, upper_boundary, new_target);
        
        prop_assert_eq!(
            output_upper, initial_target,
            "Upper boundary not inclusive: margin={}%, initial_load={}, boundary_load={}",
            margin, initial_load, upper_boundary
        );
        
        // Test at exact lower boundary
        let lower_boundary = (initial_load - margin).max(0.0);
        let output_lower = controller.process(0, lower_boundary, new_target);
        
        prop_assert_eq!(
            output_lower, initial_target,
            "Lower boundary not inclusive: margin={}%, initial_load={}, boundary_load={}",
            margin, initial_load, lower_boundary
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 6: Hysteresis Dead-Band Stability**
    /// **Validates: Requirements 4.1, 4.2**
    ///
    /// Load outside dead-band should update the output
    #[test]
    fn prop_outside_deadband_updates(
        margin in arb_hysteresis_margin(),
        initial_load in 20.0f32..80.0f32,
        initial_target in arb_undervolt(),
        new_target in arb_undervolt(),
    ) {
        let mut controller = HysteresisController::new(margin, 1);
        
        // Establish baseline
        controller.process(0, initial_load, initial_target);
        
        // Load outside dead-band (just beyond margin)
        let outside_load = (initial_load + margin + 0.1).min(100.0);
        
        let output = controller.process(0, outside_load, new_target);
        
        prop_assert_eq!(
            output, new_target,
            "Outside dead-band should update: margin={}%, initial_load={}, outside_load={}, \
             expected={}, got={}",
            margin, initial_load, outside_load, new_target, output
        );
    }
}

// =============================================================================
// Additional boundary and edge case tests
// =============================================================================

#[cfg(test)]
mod boundary_tests {
    use super::*;

    #[test]
    fn test_deadband_at_load_extremes() {
        // Test dead-band behavior at 0% and 100% load
        let mut controller = HysteresisController::new(5.0, 1);
        
        // At 0% load
        controller.process(0, 0.0, -30);
        let output = controller.process(0, 3.0, -25); // Within 5%
        assert_eq!(output, -30, "Dead-band should work at 0% load");
        
        // Reset and test at 100% load
        controller.reset();
        controller.process(0, 100.0, -20);
        let output = controller.process(0, 97.0, -25); // Within 5%
        assert_eq!(output, -20, "Dead-band should work at 100% load");
    }

    #[test]
    fn test_deadband_with_minimum_margin() {
        let mut controller = HysteresisController::new(MIN_HYSTERESIS_PERCENT, 1);
        
        controller.process(0, 50.0, -30);
        
        // Within 1% margin
        let output = controller.process(0, 50.5, -25);
        assert_eq!(output, -30);
        
        // Outside 1% margin
        let output = controller.process(0, 51.5, -25);
        assert_eq!(output, -25);
    }

    #[test]
    fn test_deadband_with_maximum_margin() {
        let mut controller = HysteresisController::new(MAX_HYSTERESIS_PERCENT, 1);
        
        controller.process(0, 50.0, -30);
        
        // Within 20% margin
        let output = controller.process(0, 65.0, -25);
        assert_eq!(output, -30);
        
        // Outside 20% margin
        let output = controller.process(0, 71.0, -25);
        assert_eq!(output, -25);
    }

    #[test]
    fn test_deadband_resets_after_exit() {
        let mut controller = HysteresisController::new(5.0, 1);
        
        // Establish baseline at 50%
        controller.process(0, 50.0, -30);
        
        // Exit dead-band to 60%
        controller.process(0, 60.0, -25);
        
        // Now dead-band should be centered at 60%
        // 58% is within ±5% of 60%
        let output = controller.process(0, 58.0, -20);
        assert_eq!(output, -25, "Dead-band should be re-centered after exit");
    }
}


// =============================================================================
// Property 7: Hysteresis Per-Core Independence
// **Validates: Requirements 4.5**
//
// For any multi-core configuration, changing the load on core N SHALL NOT
// affect the hysteresis state or output of core M (where N ≠ M).
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 7: Hysteresis Per-Core Independence**
    /// **Validates: Requirements 4.5**
    ///
    /// Changing load on one core should not affect other cores' outputs
    #[test]
    fn prop_per_core_independence_two_cores(
        margin in arb_hysteresis_margin(),
        load_core0 in 20.0f32..80.0f32,
        load_core1 in 20.0f32..80.0f32,
        target_core0 in arb_undervolt(),
        target_core1 in arb_undervolt(),
        new_load_core0 in 0.0f32..=100.0f32,
        new_target_core0 in arb_undervolt(),
    ) {
        let mut controller = HysteresisController::new(margin, 2);
        
        // Establish baselines for both cores
        controller.process(0, load_core0, target_core0);
        controller.process(1, load_core1, target_core1);
        
        // Record core 1's state before modifying core 0
        let core1_output_before = controller.last_output(1);
        let core1_load_before = controller.last_stable_load(1);
        let core1_deadband_before = controller.is_in_dead_band(1);
        
        // Modify core 0 (potentially exiting its dead-band)
        controller.process(0, new_load_core0, new_target_core0);
        
        // Core 1's state should be completely unchanged
        prop_assert_eq!(
            controller.last_output(1), core1_output_before,
            "Core 1 output changed when core 0 was modified"
        );
        prop_assert_eq!(
            controller.last_stable_load(1), core1_load_before,
            "Core 1 last_stable_load changed when core 0 was modified"
        );
        prop_assert_eq!(
            controller.is_in_dead_band(1), core1_deadband_before,
            "Core 1 dead-band state changed when core 0 was modified"
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 7: Hysteresis Per-Core Independence**
    /// **Validates: Requirements 4.5**
    ///
    /// Multiple cores can have independent dead-band states
    #[test]
    fn prop_per_core_independence_multiple_cores(
        margin in arb_hysteresis_margin(),
        num_cores in 2usize..=8usize,
    ) {
        let mut controller = HysteresisController::new(margin, num_cores);
        
        // Establish different baselines for each core
        let baselines: Vec<(f32, i32)> = (0..num_cores)
            .map(|i| {
                let load = 20.0 + (i as f32 * 10.0); // 20, 30, 40, ...
                let target = -20 - (i as i32 * 5);   // -20, -25, -30, ...
                (load, target)
            })
            .collect();
        
        for (i, (load, target)) in baselines.iter().enumerate() {
            controller.process(i, *load, *target);
        }
        
        // Verify each core has its own independent state
        for (i, (load, target)) in baselines.iter().enumerate() {
            prop_assert_eq!(
                controller.last_stable_load(i), Some(*load),
                "Core {} has wrong last_stable_load", i
            );
            prop_assert_eq!(
                controller.last_output(i), *target,
                "Core {} has wrong last_output", i
            );
        }
        
        // Modify only core 0 significantly (exit dead-band)
        let new_load = baselines[0].0 + margin + 5.0;
        let new_target = -50;
        controller.process(0, new_load, new_target);
        
        // Verify core 0 changed
        prop_assert_eq!(controller.last_output(0), new_target);
        prop_assert_eq!(controller.last_stable_load(0), Some(new_load));
        
        // Verify all other cores are unchanged
        for i in 1..num_cores {
            let (expected_load, expected_target) = baselines[i];
            prop_assert_eq!(
                controller.last_stable_load(i), Some(expected_load),
                "Core {} state changed when core 0 was modified", i
            );
            prop_assert_eq!(
                controller.last_output(i), expected_target,
                "Core {} output changed when core 0 was modified", i
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 7: Hysteresis Per-Core Independence**
    /// **Validates: Requirements 4.5**
    ///
    /// Resetting one core should not affect other cores
    #[test]
    fn prop_per_core_independence_reset(
        margin in arb_hysteresis_margin(),
        load_core0 in 20.0f32..80.0f32,
        load_core1 in 20.0f32..80.0f32,
        target_core0 in arb_undervolt(),
        target_core1 in arb_undervolt(),
    ) {
        let mut controller = HysteresisController::new(margin, 2);
        
        // Establish baselines for both cores
        controller.process(0, load_core0, target_core0);
        controller.process(1, load_core1, target_core1);
        
        // Reset only core 0
        controller.reset_core(0);
        
        // Core 0 should be reset
        prop_assert_eq!(controller.last_stable_load(0), None);
        prop_assert_eq!(controller.last_output(0), 0);
        
        // Core 1 should be unchanged
        prop_assert_eq!(
            controller.last_stable_load(1), Some(load_core1),
            "Core 1 last_stable_load changed when core 0 was reset"
        );
        prop_assert_eq!(
            controller.last_output(1), target_core1,
            "Core 1 output changed when core 0 was reset"
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 7: Hysteresis Per-Core Independence**
    /// **Validates: Requirements 4.5**
    ///
    /// Dead-band entry/exit on one core doesn't affect other cores
    #[test]
    fn prop_per_core_independence_deadband_transitions(
        margin in arb_hysteresis_margin(),
        load_core0 in 30.0f32..70.0f32,
        load_core1 in 30.0f32..70.0f32,
        target_core0 in arb_undervolt(),
        target_core1 in arb_undervolt(),
    ) {
        let mut controller = HysteresisController::new(margin, 2);
        
        // Establish baselines
        controller.process(0, load_core0, target_core0);
        controller.process(1, load_core1, target_core1);
        
        // Put core 0 into dead-band
        let deadband_load = load_core0 + (margin * 0.5);
        controller.process(0, deadband_load, target_core0 + 5);
        
        prop_assert!(
            controller.is_in_dead_band(0),
            "Core 0 should be in dead-band"
        );
        prop_assert!(
            !controller.is_in_dead_band(1),
            "Core 1 should not be in dead-band just because core 0 is"
        );
        
        // Now put core 1 into dead-band
        let deadband_load1 = load_core1 + (margin * 0.5);
        controller.process(1, deadband_load1, target_core1 + 5);
        
        prop_assert!(
            controller.is_in_dead_band(1),
            "Core 1 should now be in dead-band"
        );
        prop_assert!(
            controller.is_in_dead_band(0),
            "Core 0 should still be in dead-band"
        );
        
        // Exit core 0 from dead-band
        let exit_load = load_core0 + margin + 5.0;
        controller.process(0, exit_load, target_core0 - 10);
        
        prop_assert!(
            !controller.is_in_dead_band(0),
            "Core 0 should have exited dead-band"
        );
        prop_assert!(
            controller.is_in_dead_band(1),
            "Core 1 should still be in dead-band after core 0 exited"
        );
    }
}

#[cfg(test)]
mod per_core_boundary_tests {
    use super::*;

    #[test]
    fn test_four_cores_independence() {
        let mut controller = HysteresisController::new(5.0, 4);
        
        // Set up different states for each core
        controller.process(0, 20.0, -20);
        controller.process(1, 40.0, -25);
        controller.process(2, 60.0, -30);
        controller.process(3, 80.0, -35);
        
        // Verify initial states
        assert_eq!(controller.last_output(0), -20);
        assert_eq!(controller.last_output(1), -25);
        assert_eq!(controller.last_output(2), -30);
        assert_eq!(controller.last_output(3), -35);
        
        // Modify core 2 significantly
        controller.process(2, 90.0, -15);
        
        // Only core 2 should change
        assert_eq!(controller.last_output(0), -20);
        assert_eq!(controller.last_output(1), -25);
        assert_eq!(controller.last_output(2), -15); // Changed
        assert_eq!(controller.last_output(3), -35);
        
        assert_eq!(controller.last_stable_load(0), Some(20.0));
        assert_eq!(controller.last_stable_load(1), Some(40.0));
        assert_eq!(controller.last_stable_load(2), Some(90.0)); // Changed
        assert_eq!(controller.last_stable_load(3), Some(80.0));
    }

    #[test]
    fn test_interleaved_core_updates() {
        let mut controller = HysteresisController::new(5.0, 2);
        
        // Interleave updates between cores
        controller.process(0, 50.0, -30);
        controller.process(1, 50.0, -25);
        
        // Both in dead-band
        controller.process(0, 52.0, -28);
        assert_eq!(controller.last_output(0), -30); // Unchanged
        
        controller.process(1, 48.0, -27);
        assert_eq!(controller.last_output(1), -25); // Unchanged
        
        // Core 0 exits dead-band
        controller.process(0, 60.0, -20);
        assert_eq!(controller.last_output(0), -20); // Changed
        assert_eq!(controller.last_output(1), -25); // Still unchanged
        
        // Core 1 still in its original dead-band
        controller.process(1, 53.0, -22);
        assert_eq!(controller.last_output(1), -25); // Still unchanged
    }
}
