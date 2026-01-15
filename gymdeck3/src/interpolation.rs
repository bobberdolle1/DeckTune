//! Interpolation engine for smooth undervolt value transitions
//!
//! This module implements linear stepping between undervolt values to prevent
//! sudden voltage jumps that could cause system instability. Values transition
//! gradually with configurable step size (default 1mV per tick).

use serde::{Deserialize, Serialize};

/// Default step size in millivolts for interpolation
pub const DEFAULT_STEP_SIZE_MV: i32 = 1;

/// Per-core interpolation state
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
struct CoreInterpolationState {
    /// Current interpolated value
    current: i32,
    /// Target value to reach
    target: i32,
}

impl CoreInterpolationState {
    fn new() -> Self {
        CoreInterpolationState {
            current: 0,
            target: 0,
        }
    }

    /// Check if this core is currently transitioning
    fn is_transitioning(&self) -> bool {
        self.current != self.target
    }

    /// Perform one step of interpolation toward target
    /// Returns the new current value
    fn tick(&mut self, step_size: i32) -> i32 {
        if self.current == self.target {
            return self.current;
        }

        let diff = self.target - self.current;
        let step = if diff.abs() <= step_size {
            diff
        } else if diff > 0 {
            step_size
        } else {
            -step_size
        };

        self.current += step;
        self.current
    }

    /// Force immediate transition to a value
    fn force_immediate(&mut self, value: i32) {
        self.current = value;
        self.target = value;
    }

    /// Set new target value
    fn set_target(&mut self, target: i32) {
        self.target = target;
    }
}

/// Interpolator for smooth value transitions across multiple cores
///
/// Provides gradual transitions between undervolt values using linear
/// interpolation with configurable step size. Each tick moves values
/// closer to their targets by the step amount.
#[derive(Debug, Clone)]
pub struct Interpolator {
    /// Per-core interpolation state
    states: Vec<CoreInterpolationState>,
    /// Step size in millivolts (positive value)
    step_size_mv: i32,
}

impl Interpolator {
    /// Create a new interpolator for the specified number of cores
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores to track
    ///
    /// # Returns
    /// New Interpolator with default step size (1mV)
    pub fn new(num_cores: usize) -> Self {
        Interpolator {
            states: (0..num_cores).map(|_| CoreInterpolationState::new()).collect(),
            step_size_mv: DEFAULT_STEP_SIZE_MV,
        }
    }

    /// Create a new interpolator with custom step size
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores to track
    /// * `step_size_mv` - Step size in millivolts (must be positive)
    ///
    /// # Panics
    /// Panics if step_size_mv is not positive
    pub fn with_step_size(num_cores: usize, step_size_mv: i32) -> Self {
        assert!(step_size_mv > 0, "Step size must be positive");
        Interpolator {
            states: (0..num_cores).map(|_| CoreInterpolationState::new()).collect(),
            step_size_mv,
        }
    }

    /// Get the number of cores being tracked
    pub fn num_cores(&self) -> usize {
        self.states.len()
    }

    /// Get the configured step size
    pub fn step_size(&self) -> i32 {
        self.step_size_mv
    }

    /// Set target values for all cores
    ///
    /// # Arguments
    /// * `targets` - Vector of target values, one per core
    ///
    /// # Panics
    /// Panics if targets length doesn't match num_cores
    pub fn set_targets(&mut self, targets: Vec<i32>) {
        assert_eq!(
            targets.len(),
            self.states.len(),
            "Targets length must match number of cores"
        );
        for (state, target) in self.states.iter_mut().zip(targets.into_iter()) {
            state.set_target(target);
        }
    }

    /// Set target value for a specific core
    ///
    /// # Arguments
    /// * `core_idx` - Core index (0-based)
    /// * `target` - Target undervolt value
    ///
    /// # Panics
    /// Panics if core_idx is out of bounds
    pub fn set_target(&mut self, core_idx: usize, target: i32) {
        self.states[core_idx].set_target(target);
    }

    /// Perform one interpolation tick for all cores
    ///
    /// Each core's current value moves one step closer to its target.
    /// If the distance to target is less than step size, the value
    /// jumps directly to target.
    ///
    /// # Returns
    /// Vector of current values after the tick (values to apply)
    pub fn tick(&mut self) -> Vec<i32> {
        self.states
            .iter_mut()
            .map(|state| state.tick(self.step_size_mv))
            .collect()
    }

    /// Force immediate transition to specified values (emergency reset)
    ///
    /// Bypasses gradual interpolation and sets both current and target
    /// to the specified values immediately. Use for emergency resets
    /// (e.g., SIGTERM handling).
    ///
    /// # Arguments
    /// * `values` - Vector of values to set immediately
    ///
    /// # Panics
    /// Panics if values length doesn't match num_cores
    pub fn force_immediate(&mut self, values: Vec<i32>) {
        assert_eq!(
            values.len(),
            self.states.len(),
            "Values length must match number of cores"
        );
        for (state, value) in self.states.iter_mut().zip(values.into_iter()) {
            state.force_immediate(value);
        }
    }

    /// Force immediate transition to zero for all cores
    ///
    /// Convenience method for emergency reset to safe values.
    pub fn force_reset_to_zero(&mut self) {
        for state in &mut self.states {
            state.force_immediate(0);
        }
    }

    /// Check if any core is currently transitioning
    pub fn is_transitioning(&self) -> bool {
        self.states.iter().any(|s| s.is_transitioning())
    }

    /// Check if a specific core is transitioning
    ///
    /// # Panics
    /// Panics if core_idx is out of bounds
    pub fn is_core_transitioning(&self, core_idx: usize) -> bool {
        self.states[core_idx].is_transitioning()
    }

    /// Get current values for all cores
    pub fn current_values(&self) -> Vec<i32> {
        self.states.iter().map(|s| s.current).collect()
    }

    /// Get target values for all cores
    pub fn target_values(&self) -> Vec<i32> {
        self.states.iter().map(|s| s.target).collect()
    }

    /// Get current value for a specific core
    ///
    /// # Panics
    /// Panics if core_idx is out of bounds
    pub fn current_value(&self, core_idx: usize) -> i32 {
        self.states[core_idx].current
    }

    /// Get target value for a specific core
    ///
    /// # Panics
    /// Panics if core_idx is out of bounds
    pub fn target_value(&self, core_idx: usize) -> i32 {
        self.states[core_idx].target
    }

    /// Calculate remaining distance to target for a specific core
    pub fn remaining_distance(&self, core_idx: usize) -> i32 {
        (self.states[core_idx].target - self.states[core_idx].current).abs()
    }

    /// Calculate total remaining distance across all cores
    pub fn total_remaining_distance(&self) -> i32 {
        self.states
            .iter()
            .map(|s| (s.target - s.current).abs())
            .sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_interpolator() {
        let interp = Interpolator::new(4);
        assert_eq!(interp.num_cores(), 4);
        assert_eq!(interp.step_size(), DEFAULT_STEP_SIZE_MV);
        assert!(!interp.is_transitioning());
    }

    #[test]
    fn test_with_step_size() {
        let interp = Interpolator::with_step_size(4, 5);
        assert_eq!(interp.step_size(), 5);
    }

    #[test]
    #[should_panic(expected = "Step size must be positive")]
    fn test_invalid_step_size() {
        Interpolator::with_step_size(4, 0);
    }

    #[test]
    fn test_set_targets() {
        let mut interp = Interpolator::new(4);
        interp.set_targets(vec![-10, -20, -30, -40]);
        
        assert_eq!(interp.target_values(), vec![-10, -20, -30, -40]);
        assert!(interp.is_transitioning());
    }

    #[test]
    fn test_tick_single_step() {
        let mut interp = Interpolator::new(1);
        interp.set_target(0, -5);
        
        // Each tick should move 1mV toward target
        let values = interp.tick();
        assert_eq!(values, vec![-1]);
        
        let values = interp.tick();
        assert_eq!(values, vec![-2]);
    }

    #[test]
    fn test_tick_reaches_target() {
        let mut interp = Interpolator::new(1);
        interp.set_target(0, -3);
        
        interp.tick(); // -1
        interp.tick(); // -2
        let values = interp.tick(); // -3
        
        assert_eq!(values, vec![-3]);
        assert!(!interp.is_transitioning());
    }

    #[test]
    fn test_tick_positive_direction() {
        let mut interp = Interpolator::new(1);
        interp.force_immediate(vec![-10]);
        interp.set_target(0, -5);
        
        // Should move toward -5 (positive direction)
        let values = interp.tick();
        assert_eq!(values, vec![-9]);
    }

    #[test]
    fn test_force_immediate() {
        let mut interp = Interpolator::new(2);
        interp.set_targets(vec![-20, -30]);
        
        // Force immediate should bypass interpolation
        interp.force_immediate(vec![-20, -30]);
        
        assert_eq!(interp.current_values(), vec![-20, -30]);
        assert!(!interp.is_transitioning());
    }

    #[test]
    fn test_force_reset_to_zero() {
        let mut interp = Interpolator::new(2);
        interp.force_immediate(vec![-20, -30]);
        
        interp.force_reset_to_zero();
        
        assert_eq!(interp.current_values(), vec![0, 0]);
        assert_eq!(interp.target_values(), vec![0, 0]);
        assert!(!interp.is_transitioning());
    }

    #[test]
    fn test_remaining_distance() {
        let mut interp = Interpolator::new(2);
        interp.set_targets(vec![-10, -20]);
        
        assert_eq!(interp.remaining_distance(0), 10);
        assert_eq!(interp.remaining_distance(1), 20);
        assert_eq!(interp.total_remaining_distance(), 30);
    }

    #[test]
    fn test_custom_step_size() {
        let mut interp = Interpolator::with_step_size(1, 5);
        interp.set_target(0, -12);
        
        let values = interp.tick();
        assert_eq!(values, vec![-5]);
        
        let values = interp.tick();
        assert_eq!(values, vec![-10]);
        
        // Last step should be 2 (less than step size)
        let values = interp.tick();
        assert_eq!(values, vec![-12]);
    }

    #[test]
    fn test_multiple_cores_independent() {
        let mut interp = Interpolator::new(2);
        interp.set_targets(vec![-2, -5]);
        
        // Tick once
        let values = interp.tick();
        assert_eq!(values, vec![-1, -1]);
        
        // Tick again
        let values = interp.tick();
        assert_eq!(values, vec![-2, -2]);
        
        // Core 0 should be done, core 1 continues
        assert!(!interp.is_core_transitioning(0));
        assert!(interp.is_core_transitioning(1));
    }
}
