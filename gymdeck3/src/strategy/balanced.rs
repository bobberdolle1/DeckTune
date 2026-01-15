//! Balanced adaptation strategy with moderate responsiveness (2s ramp)

use super::{AdaptationStrategy, CoreBounds, clamp_to_bounds, lerp};

/// Balanced strategy with 2 second ramp time
///
/// This strategy provides a balance between responsiveness and stability.
/// It adapts faster than conservative but slower than aggressive,
/// making it suitable for most users.
pub struct BalancedStrategy;

impl BalancedStrategy {
    pub fn new() -> Self {
        BalancedStrategy
    }
}

impl Default for BalancedStrategy {
    fn default() -> Self {
        Self::new()
    }
}

impl AdaptationStrategy for BalancedStrategy {
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
        2000 // 2 seconds
    }

    fn name(&self) -> &'static str {
        "balanced"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_balanced_ramp_time() {
        let strategy = BalancedStrategy::new();
        assert_eq!(strategy.ramp_time_ms(), 2000);
    }

    #[test]
    fn test_balanced_name() {
        let strategy = BalancedStrategy::new();
        assert_eq!(strategy.name(), "balanced");
    }

    #[test]
    fn test_balanced_calculate_target() {
        let strategy = BalancedStrategy::new();
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
    fn test_balanced_respects_bounds() {
        let strategy = BalancedStrategy::new();
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
