//! Custom adaptation strategy with user-defined load-to-undervolt curves

use super::{AdaptationStrategy, CoreBounds, clamp_to_bounds};

/// Custom strategy with user-defined curve points
///
/// This strategy allows users to define their own load-to-undervolt
/// mapping using a series of (load%, undervolt_mv) points. Values
/// between points are linearly interpolated.
pub struct CustomStrategy {
    /// Curve points sorted by load percentage
    /// Each point is (load%, undervolt_mv)
    curve: Vec<(f32, i32)>,
}

impl CustomStrategy {
    /// Create a new CustomStrategy with the given curve points
    ///
    /// # Arguments
    /// * `curve` - Vector of (load%, undervolt_mv) points
    ///
    /// # Notes
    /// - Points will be sorted by load percentage
    /// - At least one point is required
    /// - If only one point is provided, that value is used for all loads
    pub fn new(mut curve: Vec<(f32, i32)>) -> Self {
        // Sort by load percentage
        curve.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
        
        // Ensure at least one point exists
        if curve.is_empty() {
            curve.push((0.0, 0)); // Default: no undervolt
        }
        
        CustomStrategy { curve }
    }

    /// Get the curve points
    pub fn curve(&self) -> &[(f32, i32)] {
        &self.curve
    }

    /// Interpolate the undervolt value for a given load
    fn interpolate(&self, load: f32) -> i32 {
        let load = load.clamp(0.0, 100.0);
        
        // Handle single point case
        if self.curve.len() == 1 {
            return self.curve[0].1;
        }

        // Find the two points to interpolate between
        let mut lower_idx = 0;
        let mut upper_idx = self.curve.len() - 1;

        for (i, &(point_load, _)) in self.curve.iter().enumerate() {
            if point_load <= load {
                lower_idx = i;
            }
            if point_load >= load && i < upper_idx {
                upper_idx = i;
                break;
            }
        }

        // If load is below first point, use first point value
        if load <= self.curve[0].0 {
            return self.curve[0].1;
        }

        // If load is above last point, use last point value
        if load >= self.curve[self.curve.len() - 1].0 {
            return self.curve[self.curve.len() - 1].1;
        }

        // Linear interpolation between the two points
        let (load1, val1) = self.curve[lower_idx];
        let (load2, val2) = self.curve[upper_idx];

        if (load2 - load1).abs() < f32::EPSILON {
            return val1;
        }

        let t = (load - load1) / (load2 - load1);
        let interpolated = val1 as f32 + (val2 - val1) as f32 * t;
        interpolated.round() as i32
    }
}

impl AdaptationStrategy for CustomStrategy {
    fn calculate_target(&self, load: f32, bounds: &CoreBounds) -> i32 {
        let target = self.interpolate(load);
        clamp_to_bounds(target, bounds)
    }

    fn ramp_time_ms(&self) -> u64 {
        // Custom strategy uses balanced ramp time by default
        2000
    }

    fn name(&self) -> &'static str {
        "custom"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_custom_name() {
        let strategy = CustomStrategy::new(vec![(0.0, -30), (100.0, -10)]);
        assert_eq!(strategy.name(), "custom");
    }

    #[test]
    fn test_custom_ramp_time() {
        let strategy = CustomStrategy::new(vec![(0.0, -30), (100.0, -10)]);
        assert_eq!(strategy.ramp_time_ms(), 2000);
    }

    #[test]
    fn test_custom_single_point() {
        let strategy = CustomStrategy::new(vec![(50.0, -25)]);
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        // Single point should return that value for all loads
        assert_eq!(strategy.calculate_target(0.0, &bounds), -25);
        assert_eq!(strategy.calculate_target(50.0, &bounds), -25);
        assert_eq!(strategy.calculate_target(100.0, &bounds), -25);
    }

    #[test]
    fn test_custom_two_points_linear() {
        let strategy = CustomStrategy::new(vec![(0.0, -30), (100.0, -10)]);
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };

        // Endpoints
        assert_eq!(strategy.calculate_target(0.0, &bounds), -30);
        assert_eq!(strategy.calculate_target(100.0, &bounds), -10);

        // Midpoint should be -20
        assert_eq!(strategy.calculate_target(50.0, &bounds), -20);

        // 25% should be -25
        assert_eq!(strategy.calculate_target(25.0, &bounds), -25);
    }

    #[test]
    fn test_custom_multiple_points() {
        let strategy = CustomStrategy::new(vec![
            (0.0, -35),
            (30.0, -30),
            (70.0, -25),
            (100.0, -20),
        ]);
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };

        // Exact points
        assert_eq!(strategy.calculate_target(0.0, &bounds), -35);
        assert_eq!(strategy.calculate_target(30.0, &bounds), -30);
        assert_eq!(strategy.calculate_target(70.0, &bounds), -25);
        assert_eq!(strategy.calculate_target(100.0, &bounds), -20);

        // Interpolated: 50% is between 30% and 70%
        // t = (50-30)/(70-30) = 0.5
        // value = -30 + (-25 - -30) * 0.5 = -30 + 2.5 = -27.5 ≈ -28
        let mid = strategy.calculate_target(50.0, &bounds);
        assert!(mid >= -28 && mid <= -27);
    }

    #[test]
    fn test_custom_respects_bounds() {
        // Curve that goes outside typical bounds
        let strategy = CustomStrategy::new(vec![(0.0, -50), (100.0, -5)]);
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        // At 0% load, curve says -50 but should be clamped to -35
        assert_eq!(strategy.calculate_target(0.0, &bounds), -35);

        // At 100% load, curve says -5 but should be clamped to -20
        assert_eq!(strategy.calculate_target(100.0, &bounds), -20);
    }

    #[test]
    fn test_custom_unsorted_input() {
        // Points provided out of order should still work
        let strategy = CustomStrategy::new(vec![
            (100.0, -10),
            (0.0, -30),
            (50.0, -20),
        ]);
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };

        assert_eq!(strategy.calculate_target(0.0, &bounds), -30);
        assert_eq!(strategy.calculate_target(50.0, &bounds), -20);
        assert_eq!(strategy.calculate_target(100.0, &bounds), -10);
    }

    #[test]
    fn test_custom_empty_curve() {
        // Empty curve should default to no undervolt
        let strategy = CustomStrategy::new(vec![]);
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };

        assert_eq!(strategy.calculate_target(50.0, &bounds), 0);
    }

    #[test]
    fn test_custom_extrapolation_clamped() {
        let strategy = CustomStrategy::new(vec![(20.0, -30), (80.0, -20)]);
        let bounds = CoreBounds {
            min_mv: 0,
            max_mv: -100,
            threshold: 50.0,
        };

        // Below first point: use first point value
        assert_eq!(strategy.calculate_target(0.0, &bounds), -30);
        assert_eq!(strategy.calculate_target(10.0, &bounds), -30);

        // Above last point: use last point value
        assert_eq!(strategy.calculate_target(90.0, &bounds), -20);
        assert_eq!(strategy.calculate_target(100.0, &bounds), -20);
    }
}
