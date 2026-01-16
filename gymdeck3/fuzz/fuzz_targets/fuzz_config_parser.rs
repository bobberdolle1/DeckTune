//! Fuzz target for config string parsing
//!
//! **Feature: decktune-3.1-reliability-ux, Property 12: Fuzzing no-panic guarantee**
//! **Validates: Requirements 6.1, 6.2**
//!
//! Tests that the config parser handles arbitrary byte sequences without panicking.

#![no_main]

use libfuzzer_sys::fuzz_target;
use gymdeck3::{
    parse_core_config,
    validate_sample_interval,
    validate_hysteresis,
    parse_fan_curve_point,
    validate_fan_hysteresis,
    parse_acoustic_profile,
};

fuzz_target!(|data: &[u8]| {
    // Try to interpret the bytes as a UTF-8 string
    if let Ok(s) = std::str::from_utf8(data) {
        // Fuzz core config parsing - should not panic
        let _ = parse_core_config(s);
        
        // Fuzz sample interval validation - should not panic
        let _ = validate_sample_interval(s);
        
        // Fuzz hysteresis validation - should not panic
        let _ = validate_hysteresis(s);
        
        // Fuzz fan curve point parsing - should not panic
        let _ = parse_fan_curve_point(s);
        
        // Fuzz fan hysteresis validation - should not panic
        let _ = validate_fan_hysteresis(s);
        
        // Fuzz acoustic profile parsing - should not panic
        let _ = parse_acoustic_profile(s);
    }
});
