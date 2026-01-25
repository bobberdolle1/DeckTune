//! Property-based tests for frequency curve interpolation and validation
//!
//! **Feature: frequency-based-wizard**
//!
//! These tests verify the correctness properties of the frequency curve
//! as defined in the design document.

use proptest::prelude::*;
use gymdeck3::dynamic::{FrequencyCurve, FrequencyPoint};

/// Generate valid frequency values (400-3500 MHz)
fn arb_frequency() -> impl Strategy<Value = u32> {
    400u32..=3500u32
}

/// Generate valid voltage offset values (-100 to 0 mV)
fn arb_voltage() -> impl Strategy<Value = i32> {
    -100i32..=0i32
}

/// Generate a sorted list of unique frequencies
fn arb_sorted_frequencies(min_count: usize, max_count: usize) -> impl Strategy<Value = Vec<u32>> {
    prop::collection::vec(arb_frequency(), min_count..=max_count)
        .prop_map(|mut freqs| {
            freqs.sort_unstable();
            freqs.dedup();
            freqs
        })
        .prop_filter("Need at least min_count unique frequencies", move |v| v.len() >= min_count)
}

/// Generate a valid frequency curve with random points
fn arb_frequency_curve() -> impl Strategy<Value = FrequencyCurve> {
    (
        0usize..=7usize, // core_id
        arb_sorted_frequencies(2, 10), // frequencies
        0.0f64..1e10f64, // created_at
    ).prop_flat_map(|(core_id, freqs, created_at)| {
        let num_points = freqs.len();
        prop::collection::vec(arb_voltage(), num_points..=num_points)
            .prop_map(move |voltages| {
                let points: Vec<FrequencyPoint> = freqs.iter().zip(voltages.iter())
                    .map(|(&freq, &volt)| {
                        FrequencyPoint::new(freq, volt, true, 30, created_at)
                    })
                    .collect();
                
                FrequencyCurve::new(
                    core_id,
                    points,
                    created_at,
                    serde_json::json!({"test": true}),
                )
            })
    })
}

// =============================================================================
// Property 3: Frequency curve interpolation correctness
// **Validates: Requirements 1.5, 2.2**
//
// For any frequency curve with at least two points, and any frequency value
// between the minimum and maximum tested frequencies, the interpolated voltage
// should be mathematically correct using linear interpolation between the
// surrounding points.
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness**
    /// **Validates: Requirements 1.5, 2.2**
    ///
    /// Interpolated voltage should match manual linear interpolation calculation
    #[test]
    fn prop_interpolation_matches_linear_formula(
        curve in arb_frequency_curve(),
    ) {
        // Skip if curve has less than 2 points
        prop_assume!(curve.points.len() >= 2);
        
        // Test interpolation at midpoint between each consecutive pair
        for i in 0..curve.points.len() - 1 {
            let p1 = &curve.points[i];
            let p2 = &curve.points[i + 1];
            
            // Calculate midpoint frequency
            let mid_freq = (p1.frequency_mhz + p2.frequency_mhz) / 2;
            
            // Skip if frequencies are too close (would be same after division)
            if mid_freq == p1.frequency_mhz || mid_freq == p2.frequency_mhz {
                continue;
            }
            
            // Get interpolated voltage from curve
            let interpolated = curve.get_voltage_at_frequency(mid_freq).unwrap();
            
            // Calculate expected voltage using linear interpolation formula
            // v = v1 + (v2 - v1) * (f - f1) / (f2 - f1)
            let freq_range = p2.frequency_mhz as i64 - p1.frequency_mhz as i64;
            let voltage_range = p2.voltage_mv as i64 - p1.voltage_mv as i64;
            let freq_offset = mid_freq as i64 - p1.frequency_mhz as i64;
            let expected = p1.voltage_mv as i64 + (voltage_range * freq_offset) / freq_range;
            
            prop_assert_eq!(
                interpolated as i64, expected,
                "Interpolation mismatch at {} MHz between {} MHz ({} mV) and {} MHz ({} mV)",
                mid_freq, p1.frequency_mhz, p1.voltage_mv, p2.frequency_mhz, p2.voltage_mv
            );
        }
    }

    /// **Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness**
    /// **Validates: Requirements 1.5, 2.2**
    ///
    /// Interpolation at exact frequency points should return exact voltage
    #[test]
    fn prop_interpolation_exact_at_points(
        curve in arb_frequency_curve(),
    ) {
        for point in &curve.points {
            let voltage = curve.get_voltage_at_frequency(point.frequency_mhz).unwrap();
            prop_assert_eq!(
                voltage, point.voltage_mv,
                "Voltage at exact frequency {} MHz should be {} mV, got {} mV",
                point.frequency_mhz, point.voltage_mv, voltage
            );
        }
    }

    /// **Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness**
    /// **Validates: Requirements 1.5, 2.2**
    ///
    /// Interpolated values should be monotonic if curve is monotonic
    #[test]
    fn prop_interpolation_preserves_monotonicity(
        curve in arb_frequency_curve(),
    ) {
        prop_assume!(curve.points.len() >= 2);
        
        // Check if curve is monotonic (all increasing or all decreasing)
        let mut is_increasing = true;
        let mut is_decreasing = true;
        
        for i in 0..curve.points.len() - 1 {
            let v1 = curve.points[i].voltage_mv;
            let v2 = curve.points[i + 1].voltage_mv;
            if v1 > v2 { is_increasing = false; }
            if v1 < v2 { is_decreasing = false; }
        }
        
        let is_monotonic = is_increasing || is_decreasing;
        prop_assume!(is_monotonic);
        
        // Sample interpolated values and verify monotonicity
        let min_freq = curve.points.first().unwrap().frequency_mhz;
        let max_freq = curve.points.last().unwrap().frequency_mhz;
        
        if max_freq > min_freq + 100 {
            let step = (max_freq - min_freq) / 10;
            let mut prev_voltage = curve.get_voltage_at_frequency(min_freq).unwrap();
            
            for i in 1..=10 {
                let freq = min_freq + i * step;
                let voltage = curve.get_voltage_at_frequency(freq).unwrap();
                
                if is_increasing {
                    prop_assert!(
                        voltage >= prev_voltage,
                        "Monotonicity violated: voltage decreased from {} to {} at freq {}",
                        prev_voltage, voltage, freq
                    );
                } else {
                    prop_assert!(
                        voltage <= prev_voltage,
                        "Monotonicity violated: voltage increased from {} to {} at freq {}",
                        prev_voltage, voltage, freq
                    );
                }
                
                prev_voltage = voltage;
            }
        }
    }

    /// **Feature: frequency-based-wizard, Property 3: Frequency curve interpolation correctness**
    /// **Validates: Requirements 1.5, 2.2**
    ///
    /// Interpolation should be bounded by surrounding point voltages
    #[test]
    fn prop_interpolation_bounded_by_neighbors(
        curve in arb_frequency_curve(),
    ) {
        prop_assume!(curve.points.len() >= 2);
        
        // Test multiple frequencies between each pair of points
        for i in 0..curve.points.len() - 1 {
            let p1 = &curve.points[i];
            let p2 = &curve.points[i + 1];
            
            let freq_range = p2.frequency_mhz - p1.frequency_mhz;
            if freq_range <= 2 {
                continue; // Skip if range too small
            }
            
            // Test at 25%, 50%, 75% between points
            for fraction in [1, 2, 3].iter() {
                let test_freq = p1.frequency_mhz + (freq_range * fraction) / 4;
                let voltage = curve.get_voltage_at_frequency(test_freq).unwrap();
                
                let min_v = p1.voltage_mv.min(p2.voltage_mv);
                let max_v = p1.voltage_mv.max(p2.voltage_mv);
                
                prop_assert!(
                    voltage >= min_v && voltage <= max_v,
                    "Interpolated voltage {} at {} MHz is outside bounds [{}, {}]",
                    voltage, test_freq, min_v, max_v
                );
            }
        }
    }
}

// =============================================================================
// Property 4: Frequency curve boundary clamping
// **Validates: Requirements 2.4**
//
// For any frequency curve, frequencies below the minimum tested frequency
// should return the minimum voltage, and frequencies above the maximum tested
// frequency should return the maximum voltage.
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping**
    /// **Validates: Requirements 2.4**
    ///
    /// Frequencies below minimum should clamp to minimum voltage
    #[test]
    fn prop_clamp_below_minimum(
        curve in arb_frequency_curve(),
        offset in 1u32..=500u32,
    ) {
        let min_freq = curve.points.first().unwrap().frequency_mhz;
        let min_voltage = curve.points.first().unwrap().voltage_mv;
        
        // Test frequency below minimum (but not below absolute minimum of 400)
        let test_freq = if min_freq > offset { min_freq - offset } else { 400 };
        
        let voltage = curve.get_voltage_at_frequency(test_freq).unwrap();
        
        prop_assert_eq!(
            voltage, min_voltage,
            "Frequency {} MHz below minimum {} MHz should return minimum voltage {} mV, got {} mV",
            test_freq, min_freq, min_voltage, voltage
        );
    }

    /// **Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping**
    /// **Validates: Requirements 2.4**
    ///
    /// Frequencies above maximum should clamp to maximum voltage
    #[test]
    fn prop_clamp_above_maximum(
        curve in arb_frequency_curve(),
        offset in 1u32..=500u32,
    ) {
        let max_freq = curve.points.last().unwrap().frequency_mhz;
        let max_voltage = curve.points.last().unwrap().voltage_mv;
        
        // Test frequency above maximum (but not above absolute maximum of 3500)
        let test_freq = if max_freq + offset <= 3500 { max_freq + offset } else { 3500 };
        
        let voltage = curve.get_voltage_at_frequency(test_freq).unwrap();
        
        prop_assert_eq!(
            voltage, max_voltage,
            "Frequency {} MHz above maximum {} MHz should return maximum voltage {} mV, got {} mV",
            test_freq, max_freq, max_voltage, voltage
        );
    }

    /// **Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping**
    /// **Validates: Requirements 2.4**
    ///
    /// Boundary clamping should be consistent for all out-of-range values
    #[test]
    fn prop_clamp_consistency(
        curve in arb_frequency_curve(),
    ) {
        let min_freq = curve.points.first().unwrap().frequency_mhz;
        let max_freq = curve.points.last().unwrap().frequency_mhz;
        let min_voltage = curve.points.first().unwrap().voltage_mv;
        let max_voltage = curve.points.last().unwrap().voltage_mv;
        
        // Test multiple frequencies below minimum
        for test_freq in [400, min_freq.saturating_sub(100), min_freq.saturating_sub(1)] {
            if test_freq < min_freq {
                let voltage = curve.get_voltage_at_frequency(test_freq).unwrap();
                prop_assert_eq!(
                    voltage, min_voltage,
                    "All frequencies below minimum should return same voltage"
                );
            }
        }
        
        // Test multiple frequencies above maximum
        for test_freq in [max_freq + 1, max_freq + 100, 3500] {
            if test_freq > max_freq && test_freq <= 3500 {
                let voltage = curve.get_voltage_at_frequency(test_freq).unwrap();
                prop_assert_eq!(
                    voltage, max_voltage,
                    "All frequencies above maximum should return same voltage"
                );
            }
        }
    }

    /// **Feature: frequency-based-wizard, Property 4: Frequency curve boundary clamping**
    /// **Validates: Requirements 2.4**
    ///
    /// Single-point curves should return same voltage for all frequencies
    #[test]
    fn prop_single_point_clamps_everywhere(
        core_id in 0usize..=7usize,
        freq in arb_frequency(),
        voltage in arb_voltage(),
        test_freq in arb_frequency(),
    ) {
        let point = FrequencyPoint::new(freq, voltage, true, 30, 0.0);
        let curve = FrequencyCurve::new(
            core_id,
            vec![point],
            0.0,
            serde_json::json!({}),
        );
        
        let result = curve.get_voltage_at_frequency(test_freq).unwrap();
        
        prop_assert_eq!(
            result, voltage,
            "Single-point curve should return same voltage {} mV for any frequency, got {} mV at {} MHz",
            voltage, result, test_freq
        );
    }
}

// =============================================================================
// Additional validation and edge case tests
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// Validation should accept valid curves
    #[test]
    fn prop_validation_accepts_valid_curves(
        curve in arb_frequency_curve(),
    ) {
        prop_assert!(curve.validate().is_ok());
    }

    /// Validation should reject curves with voltages out of range
    #[test]
    fn prop_validation_rejects_invalid_voltages(
        core_id in 0usize..=7usize,
        freq in arb_frequency(),
        invalid_voltage in prop::sample::select(vec![-150, -101, 1, 10, 100]),
    ) {
        let point = FrequencyPoint::new(freq, invalid_voltage, true, 30, 0.0);
        let curve = FrequencyCurve::new(
            core_id,
            vec![point],
            0.0,
            serde_json::json!({}),
        );
        
        prop_assert!(curve.validate().is_err());
    }

    /// Serialization round-trip should preserve curve data
    #[test]
    fn prop_serialization_roundtrip(
        curve in arb_frequency_curve(),
    ) {
        let json = serde_json::to_string(&curve).unwrap();
        let deserialized: FrequencyCurve = serde_json::from_str(&json).unwrap();
        
        prop_assert_eq!(curve.core_id, deserialized.core_id);
        prop_assert_eq!(curve.points.len(), deserialized.points.len());
        
        // Floating point timestamps may have minor precision differences
        // Use relative tolerance for large values
        let timestamp_diff = (curve.created_at - deserialized.created_at).abs();
        let relative_tolerance = curve.created_at.abs() * 1e-9 + 1e-6;
        prop_assert!(
            timestamp_diff < relative_tolerance,
            "Timestamp difference {} exceeds tolerance {}",
            timestamp_diff, relative_tolerance
        );
        
        for (orig, deser) in curve.points.iter().zip(deserialized.points.iter()) {
            prop_assert_eq!(orig.frequency_mhz, deser.frequency_mhz);
            prop_assert_eq!(orig.voltage_mv, deser.voltage_mv);
            prop_assert_eq!(orig.stable, deser.stable);
            prop_assert_eq!(orig.test_duration, deser.test_duration);
            
            // Check timestamp with relative tolerance
            let point_timestamp_diff = (orig.timestamp - deser.timestamp).abs();
            let point_relative_tolerance = orig.timestamp.abs() * 1e-9 + 1e-6;
            prop_assert!(
                point_timestamp_diff < point_relative_tolerance,
                "Point timestamp difference {} exceeds tolerance {}",
                point_timestamp_diff, point_relative_tolerance
            );
        }
    }
}

#[cfg(test)]
mod edge_case_tests {
    use super::*;

    #[test]
    fn test_empty_curve_error() {
        let curve = FrequencyCurve::new(0, vec![], 0.0, serde_json::json!({}));
        assert!(curve.get_voltage_at_frequency(1000).is_err());
        assert!(curve.validate().is_err());
    }

    #[test]
    fn test_unsorted_frequencies_validation() {
        let points = vec![
            FrequencyPoint::new(800, -40, true, 30, 0.0),
            FrequencyPoint::new(400, -50, true, 30, 0.0), // Out of order
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }

    #[test]
    fn test_duplicate_frequencies_validation() {
        let points = vec![
            FrequencyPoint::new(400, -50, true, 30, 0.0),
            FrequencyPoint::new(400, -40, true, 30, 0.0), // Duplicate
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        assert!(curve.validate().is_err());
    }

    #[test]
    fn test_interpolation_with_identical_voltages() {
        let points = vec![
            FrequencyPoint::new(400, -30, true, 30, 0.0),
            FrequencyPoint::new(800, -30, true, 30, 0.0),
            FrequencyPoint::new(1200, -30, true, 30, 0.0),
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        
        // All interpolated values should be -30
        assert_eq!(curve.get_voltage_at_frequency(600).unwrap(), -30);
        assert_eq!(curve.get_voltage_at_frequency(1000).unwrap(), -30);
    }

    #[test]
    fn test_interpolation_steep_gradient() {
        let points = vec![
            FrequencyPoint::new(400, -100, true, 30, 0.0),
            FrequencyPoint::new(500, 0, true, 30, 0.0),
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        
        // Midpoint should be -50
        assert_eq!(curve.get_voltage_at_frequency(450).unwrap(), -50);
    }

    #[test]
    fn test_boundary_at_exact_min_max() {
        let points = vec![
            FrequencyPoint::new(400, -50, true, 30, 0.0),
            FrequencyPoint::new(1600, -20, true, 30, 0.0),
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        
        // Exact boundaries should return exact voltages
        assert_eq!(curve.get_voltage_at_frequency(400).unwrap(), -50);
        assert_eq!(curve.get_voltage_at_frequency(1600).unwrap(), -20);
    }
}
