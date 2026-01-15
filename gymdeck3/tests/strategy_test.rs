//! Property-based tests for adaptation strategies
//!
//! **Feature: dynamic-mode-refactor**
//!
//! These tests verify the correctness properties of the adaptation strategies
//! as defined in the design document.

use proptest::prelude::*;
use proptest::strategy::Strategy as PropStrategy;
use gymdeck3::{
    Strategy as StrategyEnum,
    CoreBounds,
    AdaptationStrategy,
    ConservativeStrategy,
    BalancedStrategy,
    AggressiveStrategy,
    CustomStrategy,
    create_strategy,
};

/// Generate valid CoreBounds where max_mv <= min_mv (both negative or zero)
fn arb_core_bounds() -> impl PropStrategy<Value = CoreBounds> {
    // min_mv: -100 to 0 (less aggressive)
    // max_mv: must be <= min_mv (more aggressive, more negative)
    (-100i32..=0i32).prop_flat_map(|min_mv| {
        (-100i32..=min_mv).prop_map(move |max_mv| {
            CoreBounds {
                min_mv,
                max_mv,
                threshold: 50.0,
            }
        })
    })
}

/// Generate valid load values (0.0 to 100.0)
fn arb_load() -> impl PropStrategy<Value = f32> {
    0.0f32..=100.0f32
}

/// Generate two different load values where l1 < l2
fn arb_two_loads() -> impl PropStrategy<Value = (f32, f32)> {
    (0.0f32..100.0f32).prop_flat_map(|l1| {
        (l1 + 0.01f32..=100.0f32).prop_map(move |l2| (l1, l2))
    })
}

// =============================================================================
// Property 3: Load-to-Undervolt Monotonicity
// **Validates: Requirements 3.5, 3.6**
//
// For any adaptation strategy and any two load values L1 < L2, the calculated
// undervolt target T1 for L1 SHALL be more aggressive (more negative) than or
// equal to T2 for L2. In other words: higher load → safer (less negative) undervolt.
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 3: Load-to-Undervolt Monotonicity**
    /// **Validates: Requirements 3.5, 3.6**
    ///
    /// For ConservativeStrategy: higher load should result in less aggressive undervolt
    #[test]
    fn prop_conservative_monotonicity(
        (l1, l2) in arb_two_loads(),
        bounds in arb_core_bounds()
    ) {
        let strategy = ConservativeStrategy::new();
        let t1 = strategy.calculate_target(l1, &bounds);
        let t2 = strategy.calculate_target(l2, &bounds);
        
        // l1 < l2 implies t1 <= t2 (t1 is more negative or equal)
        // Since more negative = more aggressive, and higher load = safer
        prop_assert!(
            t1 <= t2,
            "Monotonicity violated: load {} -> {} but undervolt {} -> {} (should be non-increasing)",
            l1, l2, t1, t2
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 3: Load-to-Undervolt Monotonicity**
    /// **Validates: Requirements 3.5, 3.6**
    ///
    /// For BalancedStrategy: higher load should result in less aggressive undervolt
    #[test]
    fn prop_balanced_monotonicity(
        (l1, l2) in arb_two_loads(),
        bounds in arb_core_bounds()
    ) {
        let strategy = BalancedStrategy::new();
        let t1 = strategy.calculate_target(l1, &bounds);
        let t2 = strategy.calculate_target(l2, &bounds);
        
        prop_assert!(
            t1 <= t2,
            "Monotonicity violated: load {} -> {} but undervolt {} -> {} (should be non-increasing)",
            l1, l2, t1, t2
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 3: Load-to-Undervolt Monotonicity**
    /// **Validates: Requirements 3.5, 3.6**
    ///
    /// For AggressiveStrategy: higher load should result in less aggressive undervolt
    #[test]
    fn prop_aggressive_monotonicity(
        (l1, l2) in arb_two_loads(),
        bounds in arb_core_bounds()
    ) {
        let strategy = AggressiveStrategy::new();
        let t1 = strategy.calculate_target(l1, &bounds);
        let t2 = strategy.calculate_target(l2, &bounds);
        
        prop_assert!(
            t1 <= t2,
            "Monotonicity violated: load {} -> {} but undervolt {} -> {} (should be non-increasing)",
            l1, l2, t1, t2
        );
    }
}

// =============================================================================
// Property 4: Strategy Respects Limits
// **Validates: Requirements 3.7**
//
// For any adaptation strategy, any load value, and any CoreBounds configuration,
// the calculated undervolt target SHALL be within [max_mv, min_mv].
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 4: Strategy Respects Limits**
    /// **Validates: Requirements 3.7**
    ///
    /// ConservativeStrategy output must be within bounds
    #[test]
    fn prop_conservative_respects_limits(
        load in arb_load(),
        bounds in arb_core_bounds()
    ) {
        let strategy = ConservativeStrategy::new();
        let target = strategy.calculate_target(load, &bounds);
        
        prop_assert!(
            target >= bounds.max_mv && target <= bounds.min_mv,
            "Target {} outside bounds [{}, {}] for load {}",
            target, bounds.max_mv, bounds.min_mv, load
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 4: Strategy Respects Limits**
    /// **Validates: Requirements 3.7**
    ///
    /// BalancedStrategy output must be within bounds
    #[test]
    fn prop_balanced_respects_limits(
        load in arb_load(),
        bounds in arb_core_bounds()
    ) {
        let strategy = BalancedStrategy::new();
        let target = strategy.calculate_target(load, &bounds);
        
        prop_assert!(
            target >= bounds.max_mv && target <= bounds.min_mv,
            "Target {} outside bounds [{}, {}] for load {}",
            target, bounds.max_mv, bounds.min_mv, load
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 4: Strategy Respects Limits**
    /// **Validates: Requirements 3.7**
    ///
    /// AggressiveStrategy output must be within bounds
    #[test]
    fn prop_aggressive_respects_limits(
        load in arb_load(),
        bounds in arb_core_bounds()
    ) {
        let strategy = AggressiveStrategy::new();
        let target = strategy.calculate_target(load, &bounds);
        
        prop_assert!(
            target >= bounds.max_mv && target <= bounds.min_mv,
            "Target {} outside bounds [{}, {}] for load {}",
            target, bounds.max_mv, bounds.min_mv, load
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 4: Strategy Respects Limits**
    /// **Validates: Requirements 3.7**
    ///
    /// CustomStrategy output must be within bounds regardless of curve values
    #[test]
    fn prop_custom_respects_limits(
        load in arb_load(),
        bounds in arb_core_bounds(),
        // Generate curve with potentially out-of-bounds values
        curve_val1 in -150i32..50i32,
        curve_val2 in -150i32..50i32,
    ) {
        let curve = vec![(0.0, curve_val1), (100.0, curve_val2)];
        let strategy = CustomStrategy::new(curve);
        let target = strategy.calculate_target(load, &bounds);
        
        prop_assert!(
            target >= bounds.max_mv && target <= bounds.min_mv,
            "Target {} outside bounds [{}, {}] for load {} with curve [{}, {}]",
            target, bounds.max_mv, bounds.min_mv, load, curve_val1, curve_val2
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 4: Strategy Respects Limits**
    /// **Validates: Requirements 3.7**
    ///
    /// Factory-created strategies must respect limits
    #[test]
    fn prop_factory_strategies_respect_limits(
        load in arb_load(),
        bounds in arb_core_bounds(),
        strategy_type in prop_oneof![
            Just(StrategyEnum::Conservative),
            Just(StrategyEnum::Balanced),
            Just(StrategyEnum::Aggressive),
        ]
    ) {
        let strategy = create_strategy(strategy_type, None);
        let target = strategy.calculate_target(load, &bounds);
        
        prop_assert!(
            target >= bounds.max_mv && target <= bounds.min_mv,
            "Target {} outside bounds [{}, {}] for load {} with strategy {:?}",
            target, bounds.max_mv, bounds.min_mv, load, strategy_type
        );
    }
}

// =============================================================================
// Property 5: Custom Curve Interpolation
// **Validates: Requirements 3.4**
//
// For any custom strategy with defined curve points, and any load value, the
// calculated undervolt SHALL be the linear interpolation between the two nearest
// curve points (or clamped to endpoint values).
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 5: Custom Curve Interpolation**
    /// **Validates: Requirements 3.4**
    ///
    /// Custom curve interpolation should produce values between adjacent points
    #[test]
    fn prop_custom_curve_interpolation_between_points(
        // Generate two points with different loads
        load1 in 0.0f32..50.0f32,
        load2 in 50.0f32..=100.0f32,
        val1 in -100i32..0i32,
        val2 in -100i32..0i32,
        // Test load between the two points
        t in 0.0f32..=1.0f32,
    ) {
        let curve = vec![(load1, val1), (load2, val2)];
        let strategy = CustomStrategy::new(curve);
        
        // Wide bounds to not interfere with interpolation
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };
        
        // Test at interpolated load
        let test_load = load1 + (load2 - load1) * t;
        let result = strategy.calculate_target(test_load, &bounds);
        
        // Result should be between val1 and val2 (inclusive, accounting for rounding)
        let min_val = val1.min(val2);
        let max_val = val1.max(val2);
        
        prop_assert!(
            result >= min_val && result <= max_val,
            "Interpolated value {} not between {} and {} for load {} (t={})",
            result, min_val, max_val, test_load, t
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 5: Custom Curve Interpolation**
    /// **Validates: Requirements 3.4**
    ///
    /// Custom curve should return exact values at defined points
    #[test]
    fn prop_custom_curve_exact_at_points(
        load_point in 0.0f32..=100.0f32,
        val in -100i32..0i32,
    ) {
        // Create curve with a single point
        let curve = vec![(load_point, val)];
        let strategy = CustomStrategy::new(curve);
        
        // Wide bounds
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };
        
        // At the exact point, should return the exact value
        let result = strategy.calculate_target(load_point, &bounds);
        
        prop_assert_eq!(
            result, val,
            "At exact curve point load={}, expected {} but got {}",
            load_point, val, result
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 5: Custom Curve Interpolation**
    /// **Validates: Requirements 3.4**
    ///
    /// Custom curve should clamp to endpoint values outside the curve range
    #[test]
    fn prop_custom_curve_clamps_outside_range(
        // Curve defined between 20% and 80%
        val_low in -100i32..0i32,
        val_high in -100i32..0i32,
    ) {
        let curve = vec![(20.0, val_low), (80.0, val_high)];
        let strategy = CustomStrategy::new(curve);
        
        // Wide bounds
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };
        
        // Below curve range should return first point value
        let result_below = strategy.calculate_target(0.0, &bounds);
        prop_assert_eq!(
            result_below, val_low,
            "Below range: expected {} but got {}",
            val_low, result_below
        );
        
        // Above curve range should return last point value
        let result_above = strategy.calculate_target(100.0, &bounds);
        prop_assert_eq!(
            result_above, val_high,
            "Above range: expected {} but got {}",
            val_high, result_above
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 5: Custom Curve Interpolation**
    /// **Validates: Requirements 3.4**
    ///
    /// Linear interpolation midpoint property
    #[test]
    fn prop_custom_curve_linear_midpoint(
        val1 in -100i32..0i32,
        val2 in -100i32..0i32,
    ) {
        let curve = vec![(0.0, val1), (100.0, val2)];
        let strategy = CustomStrategy::new(curve);
        
        // Wide bounds
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };
        
        // At 50% load, should be exactly midpoint (with rounding)
        let result = strategy.calculate_target(50.0, &bounds);
        let expected = ((val1 as f32 + val2 as f32) / 2.0).round() as i32;
        
        prop_assert_eq!(
            result, expected,
            "Midpoint: expected {} but got {} for curve [{}, {}]",
            expected, result, val1, val2
        );
    }
}

// =============================================================================
// Additional boundary tests
// =============================================================================

#[cfg(test)]
mod boundary_tests {
    use super::*;

    #[test]
    fn test_all_strategies_same_at_extremes() {
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        let strategies: Vec<Box<dyn AdaptationStrategy>> = vec![
            Box::new(ConservativeStrategy::new()),
            Box::new(BalancedStrategy::new()),
            Box::new(AggressiveStrategy::new()),
        ];

        // At 0% load, all should return max_mv (most aggressive)
        for strategy in &strategies {
            assert_eq!(
                strategy.calculate_target(0.0, &bounds),
                bounds.max_mv,
                "{} at 0% load",
                strategy.name()
            );
        }

        // At 100% load, all should return min_mv (least aggressive)
        for strategy in &strategies {
            assert_eq!(
                strategy.calculate_target(100.0, &bounds),
                bounds.min_mv,
                "{} at 100% load",
                strategy.name()
            );
        }
    }

    #[test]
    fn test_ramp_times_are_distinct() {
        let conservative = ConservativeStrategy::new();
        let balanced = BalancedStrategy::new();
        let aggressive = AggressiveStrategy::new();

        assert_eq!(conservative.ramp_time_ms(), 5000);
        assert_eq!(balanced.ramp_time_ms(), 2000);
        assert_eq!(aggressive.ramp_time_ms(), 500);

        // Verify ordering: conservative > balanced > aggressive
        assert!(conservative.ramp_time_ms() > balanced.ramp_time_ms());
        assert!(balanced.ramp_time_ms() > aggressive.ramp_time_ms());
    }

    #[test]
    fn test_custom_with_monotonic_curve() {
        // Monotonically increasing curve (more aggressive at low load)
        let curve = vec![
            (0.0, -35),
            (25.0, -30),
            (50.0, -25),
            (75.0, -22),
            (100.0, -20),
        ];
        let strategy = CustomStrategy::new(curve);
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        // Verify monotonicity
        let mut prev_target = strategy.calculate_target(0.0, &bounds);
        for load in (1..=100).step_by(5) {
            let target = strategy.calculate_target(load as f32, &bounds);
            assert!(
                target >= prev_target,
                "Monotonicity violated at load {}: {} -> {}",
                load,
                prev_target,
                target
            );
            prev_target = target;
        }
    }
}
