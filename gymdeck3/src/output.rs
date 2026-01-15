//! JSON output formatting for gymdeck3 status
//!
//! Provides NDJSON (newline-delimited JSON) output for status updates,
//! transitions, and error messages.

use serde::{Deserialize, Serialize};
use std::io::{self, Write};
use std::time::Instant;

use crate::config::Strategy;

/// Status output message containing current state
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct StatusOutput {
    /// Message type identifier
    #[serde(rename = "type")]
    pub msg_type: String,
    /// Per-core CPU load percentages
    pub load: Vec<f32>,
    /// Per-core applied undervolt values in mV
    pub values: Vec<i32>,
    /// Current adaptation strategy name
    pub strategy: String,
    /// Uptime in milliseconds since daemon start
    pub uptime_ms: u64,
}

impl StatusOutput {
    /// Create a new status output message
    pub fn new(
        load: Vec<f32>,
        values: Vec<i32>,
        strategy: Strategy,
        uptime_ms: u64,
    ) -> Self {
        Self {
            msg_type: "status".to_string(),
            load,
            values,
            strategy: strategy.to_string(),
            uptime_ms,
        }
    }

    /// Serialize to JSON string
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }
}

/// Transition output message for value changes
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TransitionOutput {
    /// Message type identifier
    #[serde(rename = "type")]
    pub msg_type: String,
    /// Previous undervolt values
    pub from: Vec<i32>,
    /// Target undervolt values
    pub to: Vec<i32>,
    /// Transition progress (0.0 - 1.0)
    pub progress: f32,
}

impl TransitionOutput {
    /// Create a new transition output message
    pub fn new(from: Vec<i32>, to: Vec<i32>, progress: f32) -> Self {
        Self {
            msg_type: "transition".to_string(),
            from,
            to,
            progress: progress.clamp(0.0, 1.0),
        }
    }

    /// Serialize to JSON string
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }
}

/// Error output message
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ErrorOutput {
    /// Message type identifier
    #[serde(rename = "type")]
    pub msg_type: String,
    /// Error code for programmatic handling
    pub code: String,
    /// Human-readable error message
    pub message: String,
}

impl ErrorOutput {
    /// Create a new error output message
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            msg_type: "error".to_string(),
            code: code.into(),
            message: message.into(),
        }
    }

    /// Serialize to JSON string
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }
}

/// Output writer for NDJSON status messages
pub struct OutputWriter {
    start_time: Instant,
    output_interval_ms: u64,
    last_output: Option<Instant>,
}

impl OutputWriter {
    /// Create a new output writer with configurable interval
    ///
    /// # Arguments
    /// * `output_interval_ms` - Minimum interval between status outputs in milliseconds
    pub fn new(output_interval_ms: u64) -> Self {
        Self {
            start_time: Instant::now(),
            output_interval_ms,
            last_output: None,
        }
    }

    /// Get uptime in milliseconds since writer creation
    pub fn uptime_ms(&self) -> u64 {
        self.start_time.elapsed().as_millis() as u64
    }

    /// Check if enough time has passed for next output
    pub fn should_output(&self) -> bool {
        match self.last_output {
            Some(last) => last.elapsed().as_millis() as u64 >= self.output_interval_ms,
            None => true,
        }
    }

    /// Write status output to stdout if interval has elapsed
    ///
    /// Returns true if output was written, false if skipped due to interval
    pub fn write_status_if_due(
        &mut self,
        load: Vec<f32>,
        values: Vec<i32>,
        strategy: Strategy,
    ) -> io::Result<bool> {
        if !self.should_output() {
            return Ok(false);
        }

        self.write_status(load, values, strategy)?;
        Ok(true)
    }

    /// Force write status output regardless of interval
    pub fn write_status(
        &mut self,
        load: Vec<f32>,
        values: Vec<i32>,
        strategy: Strategy,
    ) -> io::Result<()> {
        let status = StatusOutput::new(load, values, strategy, self.uptime_ms());
        self.write_json(&status)?;
        self.last_output = Some(Instant::now());
        Ok(())
    }

    /// Write transition output
    pub fn write_transition(
        &mut self,
        from: Vec<i32>,
        to: Vec<i32>,
        progress: f32,
    ) -> io::Result<()> {
        let transition = TransitionOutput::new(from, to, progress);
        self.write_json(&transition)
    }

    /// Write error output
    pub fn write_error(&mut self, code: &str, message: &str) -> io::Result<()> {
        let error = ErrorOutput::new(code, message);
        self.write_json(&error)
    }

    /// Write any serializable value as NDJSON line
    fn write_json<T: Serialize>(&self, value: &T) -> io::Result<()> {
        let json = serde_json::to_string(value)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
        
        let stdout = io::stdout();
        let mut handle = stdout.lock();
        writeln!(handle, "{}", json)?;
        handle.flush()
    }
}

/// Validate status output contains all required fields
pub fn validate_status_output(json_str: &str) -> Result<StatusOutput, String> {
    let output: StatusOutput = serde_json::from_str(json_str)
        .map_err(|e| format!("Invalid JSON: {}", e))?;

    // Validate required fields
    if output.msg_type != "status" {
        return Err(format!("Expected type 'status', got '{}'", output.msg_type));
    }

    if output.load.is_empty() {
        return Err("load array cannot be empty".to_string());
    }

    if output.values.is_empty() {
        return Err("values array cannot be empty".to_string());
    }

    if output.strategy.is_empty() {
        return Err("strategy cannot be empty".to_string());
    }

    // Validate load values are in valid range
    for (i, &load) in output.load.iter().enumerate() {
        if !(0.0..=100.0).contains(&load) {
            return Err(format!("load[{}] = {} is out of range [0, 100]", i, load));
        }
    }

    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_status_output_serialization() {
        let status = StatusOutput::new(
            vec![45.2, 52.1, 38.7, 41.0],
            vec![-28, -25, -30, -29],
            Strategy::Balanced,
            12500,
        );

        let json = status.to_json().unwrap();
        assert!(json.contains("\"type\":\"status\""));
        assert!(json.contains("\"load\":[45.2,52.1,38.7,41.0]"));
        assert!(json.contains("\"values\":[-28,-25,-30,-29]"));
        assert!(json.contains("\"strategy\":\"balanced\""));
        assert!(json.contains("\"uptime_ms\":12500"));
    }

    #[test]
    fn test_status_output_deserialization() {
        let json = r#"{"type":"status","load":[45.2,52.1],"values":[-28,-25],"strategy":"balanced","uptime_ms":12500}"#;
        let status: StatusOutput = serde_json::from_str(json).unwrap();

        assert_eq!(status.msg_type, "status");
        assert_eq!(status.load, vec![45.2, 52.1]);
        assert_eq!(status.values, vec![-28, -25]);
        assert_eq!(status.strategy, "balanced");
        assert_eq!(status.uptime_ms, 12500);
    }

    #[test]
    fn test_transition_output_serialization() {
        let transition = TransitionOutput::new(
            vec![-25, -25],
            vec![-30, -30],
            0.5,
        );

        let json = transition.to_json().unwrap();
        assert!(json.contains("\"type\":\"transition\""));
        assert!(json.contains("\"from\":[-25,-25]"));
        assert!(json.contains("\"to\":[-30,-30]"));
        assert!(json.contains("\"progress\":0.5"));
    }

    #[test]
    fn test_transition_progress_clamped() {
        let transition = TransitionOutput::new(vec![], vec![], 1.5);
        assert_eq!(transition.progress, 1.0);

        let transition = TransitionOutput::new(vec![], vec![], -0.5);
        assert_eq!(transition.progress, 0.0);
    }

    #[test]
    fn test_error_output_serialization() {
        let error = ErrorOutput::new("ryzenadj_failed", "Command returned exit code 1");

        let json = error.to_json().unwrap();
        assert!(json.contains("\"type\":\"error\""));
        assert!(json.contains("\"code\":\"ryzenadj_failed\""));
        assert!(json.contains("\"message\":\"Command returned exit code 1\""));
    }

    #[test]
    fn test_validate_status_output_valid() {
        let json = r#"{"type":"status","load":[45.2,52.1],"values":[-28,-25],"strategy":"balanced","uptime_ms":12500}"#;
        let result = validate_status_output(json);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_status_output_invalid_type() {
        let json = r#"{"type":"error","load":[45.2],"values":[-28],"strategy":"balanced","uptime_ms":12500}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Expected type 'status'"));
    }

    #[test]
    fn test_validate_status_output_empty_load() {
        let json = r#"{"type":"status","load":[],"values":[-28],"strategy":"balanced","uptime_ms":12500}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("load array cannot be empty"));
    }

    #[test]
    fn test_validate_status_output_invalid_load_range() {
        let json = r#"{"type":"status","load":[150.0],"values":[-28],"strategy":"balanced","uptime_ms":12500}"#;
        let result = validate_status_output(json);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("out of range"));
    }

    #[test]
    fn test_output_writer_interval() {
        let writer = OutputWriter::new(1000);
        assert!(writer.should_output()); // First output always allowed
    }

    #[test]
    fn test_all_strategies_serialize() {
        for strategy in [Strategy::Conservative, Strategy::Balanced, Strategy::Aggressive, Strategy::Custom] {
            let status = StatusOutput::new(vec![50.0], vec![-25], strategy, 1000);
            let json = status.to_json().unwrap();
            assert!(json.contains("\"type\":\"status\""));
        }
    }
}
