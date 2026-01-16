//! PWM smoothing for gradual fan speed transitions
//!
//! Provides smooth interpolation between PWM values to prevent
//! annoying sudden RPM jumps. Features:
//! - Configurable ramp time (default 2 seconds for 0-255)
//! - Asymmetric ramp rates (decrease is 50% of increase rate)
//! - Emergency bypass for critical temperatures
//! - Linear interpolation between current and target values

use std::time::Instant;

/// Default ramp time in seconds (0 to 255 PWM)
pub const DEFAULT_RAMP_TIME_SEC: f32 = 2.0;

/// PWM smoothing with configurable ramp rate
///
/// Provides gradual transitions between PWM values to eliminate
/// sudden fan speed changes that cause annoying noise.
///
/// # Example
///
/// ```rust,ignore
/// use gymdeck3::fan::PWMSmoother;
///
/// let mut smoother = PWMSmoother::new(2.0); // 2 second ramp
/// smoother.set_target(200);
///
/// // In main loop (called every tick)
/// let pwm = smoother.update();
/// // pwm gradually increases toward 200
/// ```
#[derive(Debug)]
pub struct PWMSmoother {
    /// Current PWM value (floating point for smooth interpolation)
    current_pwm: f32,
    /// Target PWM value
    target_pwm: u8,
    /// Ramp rate when increasing (PWM units per second)
    ramp_rate_increase: f32,
    /// Ramp rate when decreasing (50% of increase rate)
    ramp_rate_decrease: f32,
    /// Last update timestamp
    last_update: Instant,
}

impl PWMSmoother {
    /// Create a new PWM smoother with configurable ramp time
    ///
    /// # Arguments
    /// * `ramp_time_sec` - Time in seconds to go from 0 to 255 PWM
    ///
    /// # Example
    /// ```rust,ignore
    /// let smoother = PWMSmoother::new(2.0); // 2 seconds for full range
    /// ```
    pub fn new(ramp_time_sec: f32) -> Self {
        let ramp_time = ramp_time_sec.max(0.1); // Minimum 0.1s to avoid division issues
        let rate = 255.0 / ramp_time;
        
        PWMSmoother {
            current_pwm: 0.0,
            target_pwm: 0,
            ramp_rate_increase: rate,
            ramp_rate_decrease: rate * 0.5, // Asymmetric: decrease is 50% of increase
            last_update: Instant::now(),
        }
    }

    /// Set the target PWM value
    ///
    /// The smoother will gradually interpolate toward this value.
    pub fn set_target(&mut self, target: u8) {
        self.target_pwm = target;
    }

    /// Get the current target PWM value
    pub fn target(&self) -> u8 {
        self.target_pwm
    }

    /// Get the current (smoothed) PWM value without updating
    pub fn current(&self) -> u8 {
        self.current_pwm.round() as u8
    }

    /// Update and return the smoothed PWM value
    ///
    /// Should be called periodically (e.g., every tick).
    /// Returns the interpolated PWM value moving toward target.
    pub fn update(&mut self) -> u8 {
        let elapsed = self.last_update.elapsed().as_secs_f32();
        self.last_update = Instant::now();

        let diff = self.target_pwm as f32 - self.current_pwm;
        
        if diff.abs() < 0.5 {
            // Close enough, snap to target
            self.current_pwm = self.target_pwm as f32;
        } else {
            // Select rate based on direction
            let rate = if diff > 0.0 {
                self.ramp_rate_increase
            } else {
                self.ramp_rate_decrease
            };

            // Calculate maximum change for this time step
            let max_change = rate * elapsed;
            
            // Clamp the change to not overshoot
            let change = diff.clamp(-max_change, max_change);
            self.current_pwm = (self.current_pwm + change).clamp(0.0, 255.0);
        }

        self.current_pwm.round() as u8
    }

    /// Force immediate PWM value (bypasses smoothing)
    ///
    /// Used for emergency situations like critical temperature
    /// where we need instant response.
    pub fn force_immediate(&mut self, pwm: u8) {
        self.current_pwm = pwm as f32;
        self.target_pwm = pwm;
        self.last_update = Instant::now();
    }

    /// Get the increase ramp rate (PWM units per second)
    pub fn ramp_rate_increase(&self) -> f32 {
        self.ramp_rate_increase
    }

    /// Get the decrease ramp rate (PWM units per second)
    pub fn ramp_rate_decrease(&self) -> f32 {
        self.ramp_rate_decrease
    }

    /// Check if currently at target (no smoothing in progress)
    pub fn at_target(&self) -> bool {
        (self.current_pwm - self.target_pwm as f32).abs() < 0.5
    }

    /// Reset the smoother to initial state
    pub fn reset(&mut self) {
        self.current_pwm = 0.0;
        self.target_pwm = 0;
        self.last_update = Instant::now();
    }
}

impl Default for PWMSmoother {
    fn default() -> Self {
        Self::new(DEFAULT_RAMP_TIME_SEC)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread::sleep;
    use std::time::Duration;

    #[test]
    fn test_smoother_creation() {
        let smoother = PWMSmoother::new(2.0);
        assert_eq!(smoother.current(), 0);
        assert_eq!(smoother.target(), 0);
        assert!((smoother.ramp_rate_increase() - 127.5).abs() < 0.1);
    }

    #[test]
    fn test_smoother_default() {
        let smoother = PWMSmoother::default();
        assert_eq!(smoother.current(), 0);
        assert!((smoother.ramp_rate_increase() - 127.5).abs() < 0.1);
    }

    #[test]
    fn test_set_target() {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.set_target(200);
        assert_eq!(smoother.target(), 200);
    }

    #[test]
    fn test_force_immediate() {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.force_immediate(150);
        assert_eq!(smoother.current(), 150);
        assert_eq!(smoother.target(), 150);
        assert!(smoother.at_target());
    }

    #[test]
    fn test_asymmetric_rates() {
        let smoother = PWMSmoother::new(2.0);
        let increase = smoother.ramp_rate_increase();
        let decrease = smoother.ramp_rate_decrease();
        
        // Decrease rate should be 50% of increase rate
        assert!((decrease - increase * 0.5).abs() < 0.01);
    }

    #[test]
    fn test_at_target_initially() {
        let smoother = PWMSmoother::new(2.0);
        assert!(smoother.at_target());
    }

    #[test]
    fn test_not_at_target_after_set() {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.set_target(200);
        assert!(!smoother.at_target());
    }

    #[test]
    fn test_update_moves_toward_target() {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.set_target(255);
        
        // Wait a bit and update
        sleep(Duration::from_millis(100));
        let pwm = smoother.update();
        
        // Should have moved toward target
        assert!(pwm > 0, "PWM should increase toward target");
        assert!(pwm < 255, "PWM should not reach target instantly");
    }

    #[test]
    fn test_reset() {
        let mut smoother = PWMSmoother::new(2.0);
        smoother.force_immediate(200);
        smoother.reset();
        
        assert_eq!(smoother.current(), 0);
        assert_eq!(smoother.target(), 0);
    }

    #[test]
    fn test_minimum_ramp_time() {
        // Very small ramp time should be clamped to minimum
        let smoother = PWMSmoother::new(0.01);
        assert!(smoother.ramp_rate_increase() <= 2550.0); // 255 / 0.1
    }
}
