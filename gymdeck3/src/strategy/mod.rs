//! Adaptation strategies for dynamic undervolt control
//!
//! This module provides different strategies for calculating undervolt targets
//! based on CPU load. Each strategy has different responsiveness characteristics
//! and is suitable for different use cases.
//!
//! # Strategy Comparison
//!
//! | Strategy      | Ramp Time | Use Case                          |
//! |---------------|-----------|-----------------------------------|
//! | Conservative  | 5000ms    | Maximum stability, minimal risk   |
//! | Balanced      | 2000ms    | Good for most users (default)     |
//! | Aggressive    | 500ms     | Fast response, gaming             |
//! | Custom        | 2000ms    | User-defined load-to-UV curve     |
//!
//! # Load-to-Undervolt Mapping
//!
//! All strategies follow the same principle:
//! - **Low load** (0-30%) → More aggressive undervolt (max_mv, e.g., -35mV)
//! - **Medium load** (30-70%) → Moderate undervolt (interpolated)
//! - **High load** (70-100%) → Safer undervolt (min_mv, e.g., -20mV)
//!
//! This ensures system stability under heavy load while maximizing efficiency
//! during light workloads.
//!
//! # Example Usage
//!
//! ```rust
//! use gymdeck3::strategy::{create_strategy, CoreBounds, AdaptationStrategy};
//! use gymdeck3::Strategy;
//!
//! // Create a balanced strategy
//! let strategy = create_strategy(Strategy::Balanced, None);
//!
//! // Define bounds for a core
//! let bounds = CoreBounds {
//!     min_mv: -20,    // Safe value for high load
//!     max_mv: -35,    // Aggressive value for low load
//!     threshold: 50.0,
//! };
//!
//! // Calculate target for 75% load (high load → safer value)
//! let target = strategy.calculate_target(75.0, &bounds);
//! assert!(target > -30); // Should be closer to min_mv (-20)
//!
//! // Calculate target for 25% load (low load → aggressive value)
//! let target = strategy.calculate_target(25.0, &bounds);
//! assert!(target < -30); // Should be closer to max_mv (-35)
//! ```
//!
//! # Custom Strategy
//!
//! The custom strategy allows users to define their own load-to-undervolt
//! mapping using a series of points:
//!
//! ```rust
//! use gymdeck3::strategy::{create_strategy, CustomStrategy, AdaptationStrategy, CoreBounds};
//! use gymdeck3::Strategy;
//!
//! // Define custom curve: (load%, undervolt_mv)
//! let curve = vec![
//!     (0.0, -35),    // 0% load → -35mV
//!     (30.0, -30),   // 30% load → -30mV
//!     (70.0, -25),   // 70% load → -25mV
//!     (100.0, -20),  // 100% load → -20mV
//! ];
//!
//! let strategy = create_strategy(Strategy::Custom, Some(curve));
//! let bounds = CoreBounds { min_mv: 0, max_mv: -100, threshold: 50.0 };
//!
//! // Values between points are linearly interpolated
//! let target = strategy.calculate_target(50.0, &bounds);
//! // 50% is between 30% and 70%, so target is between -30 and -25
//! assert!(target >= -30 && target <= -25);
//! ```

mod conservative;
mod balanced;
mod aggressive;
mod custom;

pub use conservative::ConservativeStrategy;
pub use balanced::BalancedStrategy;
pub use aggressive::AggressiveStrategy;
pub use custom::CustomStrategy;

use crate::config::{CoreConfig, Strategy};

/// Bounds for undervolt calculation on a single core
///
/// Defines the safe operating range for undervolt values on a CPU core.
///
/// # Semantics
///
/// - `min_mv`: Less aggressive undervolt (closer to 0, e.g., -20mV)
///   - Used when CPU load is HIGH (system under stress)
///   - Prioritizes stability over efficiency
///
/// - `max_mv`: More aggressive undervolt (more negative, e.g., -35mV)
///   - Used when CPU load is LOW (system idle or light work)
///   - Prioritizes efficiency over absolute stability
///
/// - `threshold`: Load percentage threshold for strategy-specific decisions
///   - Not used by all strategies
///   - Typically around 50% for balanced operation
///
/// # Important Note
///
/// The naming can be counterintuitive: `max_mv` is MORE NEGATIVE than `min_mv`.
/// This is because more negative values represent more aggressive undervolting.
///
/// Valid range: `max_mv <= value <= min_mv` (e.g., -35 <= value <= -20)
///
/// # Example
///
/// ```rust
/// use gymdeck3::strategy::CoreBounds;
///
/// let bounds = CoreBounds {
///     min_mv: -20,    // Safe value (high load)
///     max_mv: -35,    // Aggressive value (low load)
///     threshold: 50.0,
/// };
///
/// // Verify bounds are valid
/// assert!(bounds.max_mv <= bounds.min_mv);
/// assert!(bounds.threshold >= 0.0 && bounds.threshold <= 100.0);
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct CoreBounds {
    /// Less aggressive undervolt value (closer to 0, e.g., -20)
    pub min_mv: i32,
    /// More aggressive undervolt value (more negative, e.g., -35)
    pub max_mv: i32,
    /// Load threshold for strategy decisions
    pub threshold: f32,
}

impl From<&CoreConfig> for CoreBounds {
    fn from(config: &CoreConfig) -> Self {
        CoreBounds {
            min_mv: config.min_mv,
            max_mv: config.max_mv,
            threshold: config.threshold,
        }
    }
}

/// Trait for adaptation strategies that calculate undervolt targets based on load
///
/// All strategies must implement this trait to be usable by gymdeck3.
/// The trait ensures consistent behavior across different strategy types.
///
/// # Implementation Requirements
///
/// 1. **Monotonicity**: Higher load must produce safer (less negative) values
/// 2. **Bounds respect**: Returned values must be within the provided bounds
/// 3. **Thread safety**: Implementations must be Send + Sync
///
/// # Example Implementation
///
/// ```rust
/// use gymdeck3::strategy::{AdaptationStrategy, CoreBounds, lerp, clamp_to_bounds};
///
/// struct MyStrategy;
///
/// impl AdaptationStrategy for MyStrategy {
///     fn calculate_target(&self, load: f32, bounds: &CoreBounds) -> i32 {
///         let load = load.clamp(0.0, 100.0);
///         let t = load / 100.0;
///         let target = lerp(bounds.max_mv, bounds.min_mv, t);
///         clamp_to_bounds(target, bounds)
///     }
///
///     fn ramp_time_ms(&self) -> u64 {
///         2000 // 2 second ramp
///     }
///
///     fn name(&self) -> &'static str {
///         "my_strategy"
///     }
/// }
/// ```
pub trait AdaptationStrategy: Send + Sync {
    /// Calculate the target undervolt value for a given load
    ///
    /// # Arguments
    /// * `load` - CPU load percentage (0.0 - 100.0)
    /// * `bounds` - The min/max undervolt bounds for this core
    ///
    /// # Returns
    /// Target undervolt value in millivolts (negative or zero)
    ///
    /// # Guarantees
    /// - Return value MUST be within [bounds.max_mv, bounds.min_mv]
    /// - Higher load MUST produce less negative (safer) values
    fn calculate_target(&self, load: f32, bounds: &CoreBounds) -> i32;

    /// Get the ramp time in milliseconds for this strategy
    ///
    /// This determines how quickly values transition from one target to another.
    /// Longer ramp times provide more stability but slower response.
    fn ramp_time_ms(&self) -> u64;

    /// Get the strategy name
    ///
    /// Used for logging and status output. Should be lowercase and match
    /// the Strategy enum variant name.
    fn name(&self) -> &'static str;
}

/// Factory function to create an adaptation strategy from the Strategy enum
///
/// # Arguments
/// * `strategy` - The strategy type to create
/// * `custom_curve` - Optional custom curve points for CustomStrategy
///
/// # Returns
/// A boxed trait object implementing AdaptationStrategy
pub fn create_strategy(
    strategy: Strategy,
    custom_curve: Option<Vec<(f32, i32)>>,
) -> Box<dyn AdaptationStrategy> {
    match strategy {
        Strategy::Conservative => Box::new(ConservativeStrategy::new()),
        Strategy::Balanced => Box::new(BalancedStrategy::new()),
        Strategy::Aggressive => Box::new(AggressiveStrategy::new()),
        Strategy::Custom => {
            let curve = custom_curve.unwrap_or_else(|| {
                // Default curve if none provided: linear from max to min
                vec![(0.0, -35), (100.0, 0)]
            });
            Box::new(CustomStrategy::new(curve))
        }
    }
}

/// Clamp a value to the bounds defined by min_mv and max_mv
/// Note: max_mv is more negative (more aggressive) than min_mv
#[inline]
pub fn clamp_to_bounds(value: i32, bounds: &CoreBounds) -> i32 {
    // max_mv <= value <= min_mv (since max_mv is more negative)
    value.max(bounds.max_mv).min(bounds.min_mv)
}

/// Linear interpolation between two values
#[inline]
pub fn lerp(a: i32, b: i32, t: f32) -> i32 {
    let t = t.clamp(0.0, 1.0);
    (a as f32 + (b - a) as f32 * t).round() as i32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_core_bounds_from_config() {
        let config = CoreConfig {
            core_id: 0,
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };
        let bounds: CoreBounds = (&config).into();
        assert_eq!(bounds.min_mv, -20);
        assert_eq!(bounds.max_mv, -35);
        assert_eq!(bounds.threshold, 50.0);
    }

    #[test]
    fn test_clamp_to_bounds() {
        let bounds = CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        };
        
        // Value within bounds
        assert_eq!(clamp_to_bounds(-25, &bounds), -25);
        
        // Value too aggressive (more negative than max_mv)
        assert_eq!(clamp_to_bounds(-40, &bounds), -35);
        
        // Value too conservative (less negative than min_mv)
        assert_eq!(clamp_to_bounds(-10, &bounds), -20);
        
        // Edge cases
        assert_eq!(clamp_to_bounds(-20, &bounds), -20);
        assert_eq!(clamp_to_bounds(-35, &bounds), -35);
    }

    #[test]
    fn test_lerp() {
        assert_eq!(lerp(-35, -20, 0.0), -35);
        assert_eq!(lerp(-35, -20, 1.0), -20);
        assert_eq!(lerp(-35, -20, 0.5), -28); // midpoint
        
        // Clamping
        assert_eq!(lerp(-35, -20, -0.5), -35);
        assert_eq!(lerp(-35, -20, 1.5), -20);
    }

    #[test]
    fn test_create_strategy_conservative() {
        let strategy = create_strategy(Strategy::Conservative, None);
        assert_eq!(strategy.name(), "conservative");
        assert_eq!(strategy.ramp_time_ms(), 5000);
    }

    #[test]
    fn test_create_strategy_balanced() {
        let strategy = create_strategy(Strategy::Balanced, None);
        assert_eq!(strategy.name(), "balanced");
        assert_eq!(strategy.ramp_time_ms(), 2000);
    }

    #[test]
    fn test_create_strategy_aggressive() {
        let strategy = create_strategy(Strategy::Aggressive, None);
        assert_eq!(strategy.name(), "aggressive");
        assert_eq!(strategy.ramp_time_ms(), 500);
    }

    #[test]
    fn test_create_strategy_custom() {
        let curve = vec![(0.0, -30), (50.0, -20), (100.0, -10)];
        let strategy = create_strategy(Strategy::Custom, Some(curve));
        assert_eq!(strategy.name(), "custom");
    }
}
