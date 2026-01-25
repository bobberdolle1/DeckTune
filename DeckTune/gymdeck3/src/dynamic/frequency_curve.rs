//! Frequency-based voltage curve data structures and algorithms.
//!
//! This module provides data structures for managing frequency-dependent voltage curves
//! used in the frequency-based voltage wizard. It implements linear interpolation,
//! boundary clamping, and validation logic.
//!
//! Requirements: 1.5, 2.2, 2.4

use serde::{Deserialize, Serialize};

/// Single point in a frequency-voltage curve.
///
/// Represents a tested frequency with its associated stable voltage offset.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FrequencyPoint {
    /// CPU frequency in MHz
    pub frequency_mhz: u32,
    
    /// Voltage offset in mV (negative values, e.g., -30)
    pub voltage_mv: i32,
    
    /// Whether this voltage was stable at this frequency
    pub stable: bool,
    
    /// Duration in seconds that this point was tested
    pub test_duration: u32,
    
    /// Unix timestamp when this point was tested
    pub timestamp: f64,
}

impl FrequencyPoint {
    /// Create a new frequency point.
    pub fn new(
        frequency_mhz: u32,
        voltage_mv: i32,
        stable: bool,
        test_duration: u32,
        timestamp: f64,
    ) -> Self {
        Self {
            frequency_mhz,
            voltage_mv,
            stable,
            test_duration,
            timestamp,
        }
    }
}

/// Complete frequency-voltage curve for a CPU core.
///
/// Contains a collection of frequency points and provides interpolation
/// and validation functionality.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FrequencyCurve {
    /// CPU core identifier
    pub core_id: usize,
    
    /// List of frequency-voltage points (must be sorted by frequency)
    pub points: Vec<FrequencyPoint>,
    
    /// Unix timestamp when curve was created
    pub created_at: f64,
    
    /// Configuration used to generate this curve
    #[serde(default)]
    pub wizard_config: serde_json::Value,
}

impl FrequencyCurve {
    /// Create a new frequency curve.
    pub fn new(
        core_id: usize,
        points: Vec<FrequencyPoint>,
        created_at: f64,
        wizard_config: serde_json::Value,
    ) -> Self {
        Self {
            core_id,
            points,
            created_at,
            wizard_config,
        }
    }
    
    /// Calculate voltage offset for given frequency using linear interpolation.
    ///
    /// Uses linear interpolation between surrounding frequency points.
    /// For frequencies outside the tested range, clamps to boundary values.
    ///
    /// # Arguments
    ///
    /// * `freq_mhz` - Target frequency in MHz
    ///
    /// # Returns
    ///
    /// Voltage offset in mV (negative value)
    ///
    /// # Errors
    ///
    /// Returns an error if the curve has no points.
    ///
    /// # Requirements
    ///
    /// - 1.5: Interpolate voltage values for frequencies between tested points
    /// - 2.2: Calculate appropriate voltage offset using linear interpolation
    /// - 2.4: Clamp voltage to nearest boundary value for out-of-range frequencies
    pub fn get_voltage_at_frequency(&self, freq_mhz: u32) -> Result<i32, String> {
        if self.points.is_empty() {
            return Err("Cannot interpolate voltage from empty curve".to_string());
        }
        
        // Handle single point case
        if self.points.len() == 1 {
            return Ok(self.points[0].voltage_mv);
        }
        
        // Boundary clamping: frequency below minimum
        if freq_mhz <= self.points[0].frequency_mhz {
            return Ok(self.points[0].voltage_mv);
        }
        
        // Boundary clamping: frequency above maximum
        let last_idx = self.points.len() - 1;
        if freq_mhz >= self.points[last_idx].frequency_mhz {
            return Ok(self.points[last_idx].voltage_mv);
        }
        
        // Find surrounding points for interpolation
        for i in 0..self.points.len() - 1 {
            let p1 = &self.points[i];
            let p2 = &self.points[i + 1];
            
            if p1.frequency_mhz <= freq_mhz && freq_mhz <= p2.frequency_mhz {
                // Linear interpolation: v = v1 + (v2 - v1) * (f - f1) / (f2 - f1)
                let freq_range = p2.frequency_mhz as i64 - p1.frequency_mhz as i64;
                let voltage_range = p2.voltage_mv as i64 - p1.voltage_mv as i64;
                let freq_offset = freq_mhz as i64 - p1.frequency_mhz as i64;
                
                // Handle case where two points have same frequency (shouldn't happen with validation)
                if freq_range == 0 {
                    return Ok(p1.voltage_mv);
                }
                
                let interpolated_voltage = p1.voltage_mv as i64 + (voltage_range * freq_offset) / freq_range;
                return Ok(interpolated_voltage as i32);
            }
        }
        
        // Should never reach here if points are sorted
        Err(format!("Failed to interpolate voltage for frequency {} MHz", freq_mhz))
    }
    
    /// Validate curve integrity.
    ///
    /// Checks:
    /// - Curve has at least one point
    /// - Points are sorted by frequency in ascending order
    /// - All voltages are in valid range [-100, 0] mV
    /// - No duplicate frequencies
    ///
    /// # Returns
    ///
    /// `Ok(())` if curve is valid, `Err` with descriptive error message otherwise.
    ///
    /// # Requirements
    ///
    /// - 7.4: Validate that all voltage values are within safe range [-100, 0] mV
    /// - 7.5: Validate that frequency values are in ascending order
    pub fn validate(&self) -> Result<(), String> {
        if self.points.is_empty() {
            return Err("Curve has no points".to_string());
        }
        
        // Check voltage range
        for point in &self.points {
            if point.voltage_mv < -100 || point.voltage_mv > 0 {
                return Err(format!(
                    "Voltage {} mV at {} MHz is outside valid range [-100, 0] mV",
                    point.voltage_mv, point.frequency_mhz
                ));
            }
        }
        
        // Check sorted order and no duplicates
        for i in 0..self.points.len() - 1 {
            let curr_freq = self.points[i].frequency_mhz;
            let next_freq = self.points[i + 1].frequency_mhz;
            
            if curr_freq >= next_freq {
                if curr_freq == next_freq {
                    return Err(format!(
                        "Duplicate frequency {} MHz found in curve",
                        curr_freq
                    ));
                } else {
                    return Err(format!(
                        "Frequencies not in ascending order: {} MHz followed by {} MHz",
                        curr_freq, next_freq
                    ));
                }
            }
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    fn create_test_curve() -> FrequencyCurve {
        let points = vec![
            FrequencyPoint::new(400, -50, true, 30, 1706198430.0),
            FrequencyPoint::new(800, -40, true, 30, 1706198460.0),
            FrequencyPoint::new(1200, -30, true, 30, 1706198490.0),
            FrequencyPoint::new(1600, -20, true, 30, 1706198520.0),
        ];
        
        FrequencyCurve::new(
            0,
            points,
            1706198400.0,
            serde_json::json!({"freq_step": 400}),
        )
    }
    
    #[test]
    fn test_interpolation_exact_point() {
        let curve = create_test_curve();
        assert_eq!(curve.get_voltage_at_frequency(800).unwrap(), -40);
    }
    
    #[test]
    fn test_interpolation_between_points() {
        let curve = create_test_curve();
        // Midpoint between 400 MHz (-50 mV) and 800 MHz (-40 mV)
        // Should be -45 mV
        assert_eq!(curve.get_voltage_at_frequency(600).unwrap(), -45);
    }
    
    #[test]
    fn test_boundary_clamping_below() {
        let curve = create_test_curve();
        // Below minimum frequency should return minimum voltage
        assert_eq!(curve.get_voltage_at_frequency(200).unwrap(), -50);
    }
    
    #[test]
    fn test_boundary_clamping_above() {
        let curve = create_test_curve();
        // Above maximum frequency should return maximum voltage
        assert_eq!(curve.get_voltage_at_frequency(2000).unwrap(), -20);
    }
    
    #[test]
    fn test_empty_curve_error() {
        let curve = FrequencyCurve::new(0, vec![], 0.0, serde_json::json!({}));
        assert!(curve.get_voltage_at_frequency(1000).is_err());
    }
    
    #[test]
    fn test_single_point_curve() {
        let points = vec![FrequencyPoint::new(1000, -30, true, 30, 0.0)];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        
        assert_eq!(curve.get_voltage_at_frequency(500).unwrap(), -30);
        assert_eq!(curve.get_voltage_at_frequency(1000).unwrap(), -30);
        assert_eq!(curve.get_voltage_at_frequency(1500).unwrap(), -30);
    }
    
    #[test]
    fn test_validation_success() {
        let curve = create_test_curve();
        assert!(curve.validate().is_ok());
    }
    
    #[test]
    fn test_validation_empty_curve() {
        let curve = FrequencyCurve::new(0, vec![], 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }
    
    #[test]
    fn test_validation_voltage_out_of_range_high() {
        let points = vec![
            FrequencyPoint::new(400, 10, true, 30, 0.0), // Invalid: positive voltage
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }
    
    #[test]
    fn test_validation_voltage_out_of_range_low() {
        let points = vec![
            FrequencyPoint::new(400, -150, true, 30, 0.0), // Invalid: too negative
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }
    
    #[test]
    fn test_validation_unsorted_frequencies() {
        let points = vec![
            FrequencyPoint::new(800, -40, true, 30, 0.0),
            FrequencyPoint::new(400, -50, true, 30, 0.0), // Out of order
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }
    
    #[test]
    fn test_validation_duplicate_frequencies() {
        let points = vec![
            FrequencyPoint::new(400, -50, true, 30, 0.0),
            FrequencyPoint::new(400, -40, true, 30, 0.0), // Duplicate
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }
    
    #[test]
    fn test_serialization_roundtrip() {
        let curve = create_test_curve();
        let json = serde_json::to_string(&curve).unwrap();
        let deserialized: FrequencyCurve = serde_json::from_str(&json).unwrap();
        assert_eq!(curve, deserialized);
    }
}
