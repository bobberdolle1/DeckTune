//! Conservative adaptation strategy with slow, gradual changes (5s ramp)

use super::{AdaptationStrategy, CoreBounds, clamp_to_bounds, lerp};

/// Conservative strategy with 5 second ramp time
///
/// This strategy provides slow, gradual changes to undervolt values,
/// prioritizing stability over responsiveness. Ideal for users who
/// want minimal risk of instability.
pub struct ConservativeStrategy;

impl ConservativeStrategy {
    pub fn new() -> Self {
        ConservativeStrategy
    }
}

impl Default for ConservativeStrategy {
    fn default() -> Self {
        Self::new()
    }
}

impl AdaptationStrategy for ConservativeStrategy {
    fn calculate_target(&self, load: f32, bounds: &CoreBounds) -> i32 {
        // Clamp load to valid range
        let load = load.clamp(0.0, 100.0);
        
        // Higher load → safer (less negative) undervolt
        // Lower load → more aggressive (more negative) undervolt
        // Linear interpolation: 0% load → max_mv, 100% load → min_mv
        let t = load / 100.0;
        let target = lerp(bounds.max_mv, bounds.min_mv, t);
        
        clamp_to_bounds(target, bounds)
    }

    fn ramp_time_ms(&self) -> u64 {
        5000 // 5 seconds
    }

    fn name(&self) -> &'static str {
        "conservative"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_conservative_ramp_time() {
        let strategy = ConservativeStrategy::new();
        assert_eq!(strategy.ramp_time_ms(), 5000);
    }

    #[test]
    fn test_conservative_name() {
        let strategy = ConservativeStrategy::new();
        assert_eq!(strategy.name(), "conservative");
    }

    #[test]
    fn test_conservative_calculate_target() {
        let strategy = ConservativeStrategy::new();
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        // 0% load → most aggressive (max_mv)
        assert_eq!(strategy.calculate_target(0.0, &bounds), -35);
        
        // 100% load → least aggressive (min_mv)
        assert_eq!(strategy.calculate_target(100.0, &bounds), -20);
        
        // 50% load → midpoint
        let mid = strategy.calculate_target(50.0, &bounds);
        assert!(mid > -35 && mid < -20);
    }

    #[test]
    fn test_conservative_respects_bounds() {
        let strategy = ConservativeStrategy::new();
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };

        for load in [0.0, 25.0, 50.0, 75.0, 100.0] {
            let target = strategy.calculate_target(load, &bounds);
            assert!(target >= bounds.max_mv, "target {} should be >= max_mv {}", target, bounds.max_mv);
            assert!(target <= bounds.min_mv, "target {} should be <= min_mv {}", target, bounds.min_mv);
        }
    }
}
