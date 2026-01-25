//! Property-based tests for JSON output format
//!
//! **Feature: dynamic-mode-refactor**
//!
//! These tests verify the correctness properties of the JSON output
//! as defined in the design document.

use proptest::prelude::*;
use gymdeck3::{
    Strategy,
    StatusOutput,
    TransitionOutput,
    ErrorOutput,
    validate_status_output,
};

/// Generate valid load values (0.0 to 100.0)
fn arb_load() -> impl proptest::strategy::Strategy<Value = f32> {
    0.0f32..=100.0f32
}

/// Generate valid undervolt values (-100 to 0)
fn arb_undervolt() -> impl proptest::strategy::Strategy<Value = i32> {
    -100i32..=0i32
}

/// Generate valid uptime values
fn arb_uptime() -> impl proptest::strategy::Strategy<Value = u64> {
    0u64..=u64::MAX / 2
}

/// Generate a vector of load values (1-8 cores)
fn arb_load_vec() -> impl proptest::strategy::Strategy<Value = Vec<f32>> {
    proptest::collection::vec(arb_load(), 1..=8)
}

/// Generate a vector of undervolt values (1-8 cores)
fn arb_values_vec() -> impl proptest::strategy::Strategy<Value = Vec<i32>> {
    proptest::collection::vec(arb_undervolt(), 1..=8)
}

/// Generate any strategy type
fn arb_strategy() -> impl proptest::strategy::Strategy<Value = Strategy> {
    prop_oneof![
        Just(Strategy::Conservative),
        Just(Strategy::Balanced),
        Just(Strategy::Aggressive),
        Just(Strategy::Custom),
    ]
}

// =============================================================================
// Property 10: JSON Output Format
// **Validates: Requirements 7.1, 7.2, 7.6**
//
// For any status output line, it SHALL be valid JSON containing at minimum:
// "type", "load" (array), "values" (array), "strategy" (string), "uptime_ms" (number).
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// **Feature: dynamic-mode-refactor, Property 10: JSON Output Format**
    /// **Validates: Requirements 7.1, 7.2, 7.6**
    ///
    /// StatusOutput serialization produces valid JSON with all required fields
    #[test]
    fn prop_status_output_contains_required_fields(
        load in arb_load_vec(),
        values in arb_values_vec(),
        strategy in arb_strategy(),
        uptime_ms in arb_uptime(),
    ) {
        let status = StatusOutput::new(load.clone(), values.clone(), strategy, uptime_ms);
        let json = status.to_json().expect("Serialization should succeed");
        
        // Verify it's valid JSON by parsing
        let parsed: serde_json::Value = serde_json::from_str(&json)
            .expect("Should be valid JSON");
        
        // Verify required fields exist
        prop_assert!(parsed.get("type").is_some(), "Missing 'type' field");
        prop_assert!(parsed.get("load").is_some(), "Missing 'load' field");
        prop_assert!(parsed.get("values").is_some(), "Missing 'values' field");
        prop_assert!(parsed.get("strategy").is_some(), "Missing 'strategy' field");
        prop_assert!(parsed.get("uptime_ms").is_some(), "Missing 'uptime_ms' field");
        
        // Verify field types
        prop_assert!(parsed["type"].is_string(), "'type' should be string");
        prop_assert!(parsed["load"].is_array(), "'load' should be array");
        prop_assert!(parsed["values"].is_array(), "'values' should be array");
        prop_assert!(parsed["strategy"].is_string(), "'strategy' should be string");
        prop_assert!(parsed["uptime_ms"].is_number(), "'uptime_ms' should be number");
        
        // Verify type value
        prop_assert_eq!(parsed["type"].as_str().unwrap(), "status");
    }

    /// **Feature: dynamic-mode-refactor, Property 10: JSON Output Format**
    /// **Validates: Requirements 7.1, 7.2, 7.6**
    ///
    /// StatusOutput round-trip: serialize then deserialize preserves data
    #[test]
    fn prop_status_output_roundtrip(
        load in arb_load_vec(),
        values in arb_values_vec(),
        strategy in arb_strategy(),
        uptime_ms in arb_uptime(),
    ) {
        let original = StatusOutput::new(load.clone(), values.clone(), strategy, uptime_ms);
        let json = original.to_json().expect("Serialization should succeed");
        let deserialized: StatusOutput = serde_json::from_str(&json)
            .expect("Deserialization should succeed");
        
        prop_assert_eq!(original.msg_type, deserialized.msg_type);
        prop_assert_eq!(original.strategy, deserialized.strategy);
        prop_assert_eq!(original.uptime_ms, deserialized.uptime_ms);
        prop_assert_eq!(original.values, deserialized.values);
        
        // Compare load values with floating point tolerance
        prop_assert_eq!(original.load.len(), deserialized.load.len());
        for (orig, deser) in original.load.iter().zip(deserialized.load.iter()) {
            prop_assert!(
                (orig - deser).abs() < 0.001,
                "Load mismatch: {} vs {}",
                orig, deser
            );
        }
    }

    /// **Feature: dynamic-mode-refactor, Property 10: JSON Output Format**
    /// **Validates: Requirements 7.1, 7.2, 7.6**
    ///
    /// StatusOutput validation accepts valid outputs
    #[test]
    fn prop_status_output_validation_accepts_valid(
        load in proptest::collection::vec(arb_load(), 1..=8),
        values in proptest::collection::vec(arb_undervolt(), 1..=8),
        strategy in arb_strategy(),
        uptime_ms in arb_uptime(),
    ) {
        let status = StatusOutput::new(load, values, strategy, uptime_ms);
        let json = status.to_json().expect("Serialization should succeed");
        
        let result = validate_status_output(&json);
        prop_assert!(
            result.is_ok(),
            "Valid status should pass validation: {:?}",
            result.err()
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 10: JSON Output Format**
    /// **Validates: Requirements 7.1, 7.2, 7.6**
    ///
    /// JSON output is newline-free (NDJSON compatible)
    #[test]
    fn prop_status_output_no_newlines(
        load in arb_load_vec(),
        values in arb_values_vec(),
        strategy in arb_strategy(),
        uptime_ms in arb_uptime(),
    ) {
        let status = StatusOutput::new(load, values, strategy, uptime_ms);
        let json = status.to_json().expect("Serialization should succeed");
        
        prop_assert!(
            !json.contains('\n'),
            "JSON output should not contain newlines for NDJSON format"
        );
        prop_assert!(
            !json.contains('\r'),
            "JSON output should not contain carriage returns"
        );
    }

    /// **Feature: dynamic-mode-refactor, Property 10: JSON Output Format**
    /// **Validates: Requirements 7.1, 7.2, 7.6**
    ///
    /// Strategy names serialize correctly
    #[test]
    fn prop_strategy_serialization(strategy in arb_strategy()) {
        let status = StatusOutput::new(vec![50.0], vec![-25], strategy, 1000);
        let json = status.to_json().expect("Serialization should succeed");
        
        let expected_name = match strategy {
            Strategy::Conservative => "conservative",
            Strategy::Balanced => "balanced",
            Strategy::Aggressive => "aggressive",
            Strategy::Custom => "custom",
        };
        
        prop_assert!(
            json.contains(&format!("\"strategy\":\"{}\"", expected_name)),
            "Strategy '{}' not found in JSON: {}",
            expected_name, json
        );
    }
}

// =============================================================================
// Additional output format tests
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// TransitionOutput serialization produces valid JSON
    #[test]
    fn prop_transition_output_valid_json(
        from in arb_values_vec(),
        to in arb_values_vec(),
        progress in 0.0f32..=1.0f32,
    ) {
        let transition = TransitionOutput::new(from.clone(), to.clone(), progress);
        let json = transition.to_json().expect("Serialization should succeed");
        
        let parsed: serde_json::Value = serde_json::from_str(&json)
            .expect("Should be valid JSON");
        
        prop_assert_eq!(parsed["type"].as_str().unwrap(), "transition");
        prop_assert!(parsed["from"].is_array());
        prop_assert!(parsed["to"].is_array());
        prop_assert!(parsed["progress"].is_number());
    }

    /// TransitionOutput progress is clamped to [0, 1]
    #[test]
    fn prop_transition_progress_clamped(
        from in arb_values_vec(),
        to in arb_values_vec(),
        progress in -10.0f32..=10.0f32,
    ) {
        let transition = TransitionOutput::new(from, to, progress);
        
        prop_assert!(
            transition.progress >= 0.0 && transition.progress <= 1.0,
            "Progress {} should be clamped to [0, 1]",
            transition.progress
        );
    }

    /// ErrorOutput serialization produces valid JSON
    #[test]
    fn prop_error_output_valid_json(
        code in "[a-z_]{1,20}",
        message in ".{1,100}",
    ) {
        let error = ErrorOutput::new(&code, &message);
        let json = error.to_json().expect("Serialization should succeed");
        
        let parsed: serde_json::Value = serde_json::from_str(&json)
            .expect("Should be valid JSON");
        
        prop_assert_eq!(parsed["type"].as_str().unwrap(), "error");
        prop_assert!(parsed["code"].is_string());
        prop_assert!(parsed["message"].is_string());
    }
}

// =============================================================================
// Validation rejection tests
// =============================================================================

#[cfg(test)]
mod validation_tests {
    use super::*;

    #[test]
    fn test_validation_rejects_wrong_type() {
        let json = r#"{"type":"error","load":[50.0],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Expected type 'status'"));
    }

    #[test]
    fn test_validation_rejects_empty_load() {
        let json = r#"{"type":"status","load":[],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("load array cannot be empty"));
    }

    #[test]
    fn test_validation_rejects_empty_values() {
        let json = r#"{"type":"status","load":[50.0],"values":[],"strategy":"balanced","uptime_ms":1000}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("values array cannot be empty"));
    }

    #[test]
    fn test_validation_rejects_invalid_load_range() {
        let json = r#"{"type":"status","load":[150.0],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("out of range"));
    }

    #[test]
    fn test_validation_rejects_negative_load() {
        let json = r#"{"type":"status","load":[-10.0],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("out of range"));
    }

    #[test]
    fn test_validation_rejects_invalid_json() {
        let json = "not valid json";
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Invalid JSON"));
    }

    #[test]
    fn test_validation_accepts_boundary_load_values() {
        // Test 0.0 load
        let json = r#"{"type":"status","load":[0.0],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        assert!(validate_status_output(json).is_ok());

        // Test 100.0 load
        let json = r#"{"type":"status","load":[100.0],"values":[-25],"strategy":"balanced","uptime_ms":1000}"#;
        assert!(validate_status_output(json).is_ok());
    }
}
