//! Fuzz target for core config value validation
//!
//! **Feature: decktune-3.1-reliability-ux, Property 12: Fuzzing no-panic guarantee**
//! **Validates: Requirements 6.1, 6.2**
//!
//! Tests that core config validation handles arbitrary values without panicking.

#![no_main]

use libfuzzer_sys::fuzz_target;
use arbitrary::Arbitrary;
use gymdeck3::validate_core_config_values;

#[derive(Debug, Arbitrary)]
struct FuzzCoreConfig {
    core_id: usize,
    min_mv: i32,
    max_mv: i32,
    threshold: f32,
}

fuzz_target!(|config: FuzzCoreConfig| {
    // Validate core config with arbitrary values - should not panic
    // It should return Ok or Err, never panic
    let _ = validate_core_config_values(
        config.core_id,
        config.min_mv,
        config.max_mv,
        config.threshold,
    );
});
