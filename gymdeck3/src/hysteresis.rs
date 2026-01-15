//! Hysteresis controller for stable undervolt value transitions
//!
//! This module implements dead-band logic to prevent frequent value changes
//! when CPU load fluctuates around threshold values. Each core maintains
//! independent hysteresis state.

use serde::{Deserialize, Serialize};

/// Minimum hysteresis margin percentage
pub const MIN_HYSTERESIS_PERCENT: f32 = 1.0;
/// Maximum hysteresis margin percentage
pub const MAX_HYSTERESIS_PERCENT: f32 = 20.0;

/// Per-core hysteresis state
#[derive(Debug, Clone, Serialize, Deserialize)]
struct HysteresisState {
    /// Last stable load value that caused an output change
    last_stable_load: Option<f32>,
    /// Last output undervolt value
    last_output: i32,
    /// Whether currently in dead-band (suppressing changes)
    in_dead_band: bool,
}

impl HysteresisState {
    fn new() -> Self {
        HysteresisState {
            last_stable_load: None, // No baseline yet
            last_output: 0,
            in_dead_band: false,
        }
    }

    fn reset(&mut self) {
        self.last_stable_load = None;
        self.last_output = 0;
        self.in_dead_band = false;
    }
}

/// Hysteresis controller that prevents value hunting around thresholds
///
/// When load fluctuates within ±margin% of the last stable value,
/// the output remains unchanged. This prevents rapid value changes
/// that could cause instability.
#[derive(Debug, Clone)]
pub struct HysteresisController {
    /// Hysteresis margin as percentage (1.0 - 20.0)
    margin_percent: f32,
    /// Per-core state tracking
    per_core_state: Vec<HysteresisState>,
}

impl HysteresisController {
    /// Create a new hysteresis controller
    ///
    /// # Arguments
    /// * `margin_percent` - Dead-band margin (1.0 - 20.0%)
    /// * `num_cores` - Number of CPU cores to track
    ///
    /// # Panics
    /// Panics if margin_percent is outside valid range
    pub fn new(margin_percent: f32, num_cores: usize) -> Self {
        assert!(
            (MIN_HYSTERESIS_PERCENT..=MAX_HYSTERESIS_PERCENT).contains(&margin_percent),
            "Hysteresis margin must be between {}% and {}%",
            MIN_HYSTERESIS_PERCENT,
            MAX_HYSTERESIS_PERCENT
        );

        HysteresisController {
            margin_percent,
            per_core_state: (0..num_cores).map(|_| HysteresisState::new()).collect(),
        }
    }

    /// Get the configured margin percentage
    pub fn margin_percent(&self) -> f32 {
        self.margin_percent
    }

    /// Get the number of cores being tracked
    pub fn num_cores(&self) -> usize {
        self.per_core_state.len()
    }

    /// Process a load value and raw target for a specific core
    ///
    /// Returns the filtered output value, which may be the same as the
    /// previous output if the load is within the dead-band.
    ///
    /// # Arguments
    /// * `core_idx` - Core index (0-based)
    /// * `load` - Current CPU load percentage (0.0 - 100.0)
    /// * `raw_target` - Raw undervolt target from strategy
    ///
    /// # Returns
    /// Filtered undervolt value (may be unchanged if in dead-band)
    ///
    /// # Panics
    /// Panics if core_idx is out of bounds
    pub fn process(&mut self, core_idx: usize, load: f32, raw_target: i32) -> i32 {
        let state = &mut self.per_core_state[core_idx];
        
        // If no baseline established yet, set it and return raw target
        let last_stable = match state.last_stable_load {
            Some(l) => l,
            None => {
                state.last_stable_load = Some(load);
                state.last_output = raw_target;
                state.in_dead_band = false;
                return raw_target;
            }
        };
        
        // Calculate dead-band boundaries
        let lower_bound = last_stable - self.margin_percent;
        let upper_bound = last_stable + self.margin_percent;
        
        // Check if load is within dead-band
        if load >= lower_bound && load <= upper_bound {
            // Within dead-band: keep previous output
            state.in_dead_band = true;
            state.last_output
        } else {
            // Outside dead-band: update to new value
            state.in_dead_band = false;
            state.last_stable_load = Some(load);
            state.last_output = raw_target;
            raw_target
        }
    }

    /// Check if a specific core is currently in dead-band
    pub fn is_in_dead_band(&self, core_idx: usize) -> bool {
        self.per_core_state[core_idx].in_dead_band
    }

    /// Get the last stable load for a specific core
    /// Returns None if no baseline has been established yet
    pub fn last_stable_load(&self, core_idx: usize) -> Option<f32> {
        self.per_core_state[core_idx].last_stable_load
    }

    /// Get the last output value for a specific core
    pub fn last_output(&self, core_idx: usize) -> i32 {
        self.per_core_state[core_idx].last_output
    }

    /// Reset all per-core state
    pub fn reset(&mut self) {
        for state in &mut self.per_core_state {
            state.reset();
        }
    }

    /// Reset state for a specific core
    pub fn reset_core(&mut self, core_idx: usize) {
        self.per_core_state[core_idx].reset();
    }
}

/// Validate hysteresis margin value
pub fn validate_hysteresis_margin(margin: f32) -> Result<f32, String> {
    if margin < MIN_HYSTERESIS_PERCENT {
        return Err(format!(
            "Hysteresis margin {}% is too small (minimum: {}%)",
            margin, MIN_HYSTERESIS_PERCENT
        ));
    }
    if margin > MAX_HYSTERESIS_PERCENT {
        return Err(format!(
            "Hysteresis margin {}% is too large (maximum: {}%)",
            margin, MAX_HYSTERESIS_PERCENT
        ));
    }
    Ok(margin)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_controller() {
        let controller = HysteresisController::new(5.0, 4);
        assert_eq!(controller.margin_percent(), 5.0);
        assert_eq!(controller.num_cores(), 4);
    }

    #[test]
    fn test_initial_state() {
        let controller = HysteresisController::new(5.0, 4);
        for i in 0..4 {
            assert!(!controller.is_in_dead_band(i));
            assert_eq!(controller.last_stable_load(i), None);
            assert_eq!(controller.last_output(i), 0);
        }
    }

    #[test]
    fn test_process_outside_deadband() {
        let mut controller = HysteresisController::new(5.0, 1);
        
        // First call establishes baseline
        let result = controller.process(0, 30.0, -25);
        assert_eq!(result, -25);
        assert_eq!(controller.last_stable_load(0), Some(30.0));
        assert!(!controller.is_in_dead_band(0));
    }

    #[test]
    fn test_process_inside_deadband() {
        let mut controller = HysteresisController::new(5.0, 1);
        
        // Establish baseline at 50% load
        let result = controller.process(0, 50.0, -30);
        assert_eq!(result, -30);
        assert_eq!(controller.last_stable_load(0), Some(50.0));
        
        // Load within ±5% should keep previous value
        let result = controller.process(0, 52.0, -28);
        assert_eq!(result, -30); // Kept previous value
        assert!(controller.is_in_dead_band(0));
        
        // Load still within dead-band
        let result = controller.process(0, 48.0, -32);
        assert_eq!(result, -30); // Still kept previous value
        assert!(controller.is_in_dead_band(0));
    }

    #[test]
    fn test_process_exits_deadband() {
        let mut controller = HysteresisController::new(5.0, 1);
        
        // Establish baseline at 50% load
        controller.process(0, 50.0, -30);
        
        // Load outside ±5% should update
        let result = controller.process(0, 60.0, -20);
        assert_eq!(result, -20);
        assert!(!controller.is_in_dead_band(0));
        assert_eq!(controller.last_stable_load(0), Some(60.0));
    }

    #[test]
    fn test_reset() {
        let mut controller = HysteresisController::new(5.0, 2);
        
        // Modify state
        controller.process(0, 30.0, -25);
        controller.process(1, 70.0, -15);
        
        // Reset all
        controller.reset();
        
        for i in 0..2 {
            assert_eq!(controller.last_stable_load(i), None);
            assert_eq!(controller.last_output(i), 0);
            assert!(!controller.is_in_dead_band(i));
        }
    }

    #[test]
    fn test_reset_single_core() {
        let mut controller = HysteresisController::new(5.0, 2);
        
        // Modify state
        controller.process(0, 30.0, -25);
        controller.process(1, 70.0, -15);
        
        // Reset only core 0
        controller.reset_core(0);
        
        assert_eq!(controller.last_stable_load(0), None);
        assert_eq!(controller.last_output(0), 0);
        
        // Core 1 unchanged
        assert_eq!(controller.last_stable_load(1), Some(70.0));
        assert_eq!(controller.last_output(1), -15);
    }

    #[test]
    fn test_validate_hysteresis_margin() {
        assert!(validate_hysteresis_margin(1.0).is_ok());
        assert!(validate_hysteresis_margin(10.0).is_ok());
        assert!(validate_hysteresis_margin(20.0).is_ok());
        
        assert!(validate_hysteresis_margin(0.5).is_err());
        assert!(validate_hysteresis_margin(21.0).is_err());
    }

    #[test]
    #[should_panic(expected = "Hysteresis margin must be between")]
    fn test_new_controller_invalid_margin_low() {
        HysteresisController::new(0.5, 4);
    }

    #[test]
    #[should_panic(expected = "Hysteresis margin must be between")]
    fn test_new_controller_invalid_margin_high() {
        HysteresisController::new(25.0, 4);
    }

    #[test]
    fn test_boundary_values() {
        let mut controller = HysteresisController::new(5.0, 1);
        
        // Establish baseline at 50%
        let result = controller.process(0, 50.0, -30);
        assert_eq!(result, -30);
        
        // Exactly at boundary (50 + 5 = 55) - should be inside
        let result = controller.process(0, 55.0, -25);
        assert_eq!(result, -30);
        assert!(controller.is_in_dead_band(0));
        
        // Just outside boundary (55.01) - should update
        let result = controller.process(0, 55.01, -24);
        assert_eq!(result, -24);
        assert!(!controller.is_in_dead_band(0));
    }
}
