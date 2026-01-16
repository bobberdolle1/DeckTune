//! Fuzz target for fan curve point validation
//!
//! **Feature: decktune-3.1-reliability-ux, Property 12: Fuzzing no-panic guarantee**
//! **Validates: Requirements 6.1, 6.2**
//!
//! Tests that fan curve validation handles arbitrary values without panicking.

#![no_main]

use libfuzzer_sys::fuzz_target;
use arbitrary::Arbitrary;
use gymdeck3::validate_fan_curve_point;

#[derive(Debug, Arbitrary)]
struct FuzzFanCurvePoint {
    temp_c: i32,
    speed_percent: u8,
}

fuzz_target!(|point: FuzzFanCurvePoint| {
    // Validate fan curve point with arbitrary values - should not panic
    // It should return Ok or Err, never panic
    let _ = validate_fan_curve_point(point.temp_c, point.speed_percent);
});
