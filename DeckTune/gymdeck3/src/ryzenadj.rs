//! Ryzenadj subprocess wrapper for applying undervolt values
//!
//! This module provides a wrapper around the ryzenadj binary for applying
//! undervolt values to AMD APU cores. It handles subprocess execution,
//! error tracking, and consecutive failure detection.

use std::path::PathBuf;
use std::process::Stdio;
use tokio::process::Command;

/// Maximum number of consecutive failures before exit
pub const MAX_CONSECUTIVE_FAILURES: u32 = 5;

/// Error types for ryzenadj operations
#[derive(Debug, Clone, PartialEq)]
pub enum RyzenadjError {
    /// Binary not found at specified path
    BinaryNotFound(String),
    /// Command execution failed
    ExecutionFailed(String),
    /// Command returned non-zero exit code
    NonZeroExit { code: i32, stderr: String },
    /// Maximum consecutive failures reached
    MaxFailuresReached(u32),
}

impl std::fmt::Display for RyzenadjError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RyzenadjError::BinaryNotFound(path) => {
                write!(f, "ryzenadj binary not found at: {}", path)
            }
            RyzenadjError::ExecutionFailed(msg) => {
                write!(f, "ryzenadj execution failed: {}", msg)
            }
            RyzenadjError::NonZeroExit { code, stderr } => {
                write!(f, "ryzenadj exited with code {}: {}", code, stderr)
            }
            RyzenadjError::MaxFailuresReached(count) => {
                write!(f, "ryzenadj failed {} consecutive times", count)
            }
        }
    }
}

impl std::error::Error for RyzenadjError {}

/// Result of a ryzenadj apply operation
#[derive(Debug, Clone, PartialEq)]
pub struct ApplyResult {
    /// Whether the operation succeeded
    pub success: bool,
    /// Current consecutive failure count (0 if success)
    pub consecutive_failures: u32,
}

/// Executor for ryzenadj subprocess calls
#[derive(Debug)]
pub struct RyzenadjExecutor {
    /// Path to the ryzenadj binary
    binary_path: PathBuf,
    /// Count of consecutive failures
    consecutive_failures: u32,
    /// Maximum allowed consecutive failures
    max_failures: u32,
}

impl RyzenadjExecutor {
    /// Create a new RyzenadjExecutor with the specified binary path
    ///
    /// # Arguments
    /// * `binary_path` - Path to the ryzenadj binary
    pub fn new(binary_path: &str) -> Self {
        Self {
            binary_path: PathBuf::from(binary_path),
            consecutive_failures: 0,
            max_failures: MAX_CONSECUTIVE_FAILURES,
        }
    }

    /// Create a new RyzenadjExecutor with custom max failures (for testing)
    ///
    /// # Arguments
    /// * `binary_path` - Path to the ryzenadj binary
    /// * `max_failures` - Maximum consecutive failures before error
    pub fn with_max_failures(binary_path: &str, max_failures: u32) -> Self {
        Self {
            binary_path: PathBuf::from(binary_path),
            consecutive_failures: 0,
            max_failures,
        }
    }

    /// Get the current consecutive failure count
    pub fn consecutive_failures(&self) -> u32 {
        self.consecutive_failures
    }

    /// Get the maximum allowed consecutive failures
    pub fn max_failures(&self) -> u32 {
        self.max_failures
    }

    /// Get the binary path
    pub fn binary_path(&self) -> &PathBuf {
        &self.binary_path
    }

    /// Reset the consecutive failure counter
    pub fn reset_failures(&mut self) {
        self.consecutive_failures = 0;
    }

    /// Record a failure and check if max failures reached
    ///
    /// # Returns
    /// * `Ok(count)` - Current failure count if under max
    /// * `Err(MaxFailuresReached)` - If max failures reached
    fn record_failure(&mut self) -> Result<u32, RyzenadjError> {
        self.consecutive_failures += 1;
        if self.consecutive_failures >= self.max_failures {
            Err(RyzenadjError::MaxFailuresReached(self.consecutive_failures))
        } else {
            Ok(self.consecutive_failures)
        }
    }

    /// Record a success and reset failure counter
    fn record_success(&mut self) {
        self.consecutive_failures = 0;
    }

    /// Build the ryzenadj command arguments for applying undervolt values
    ///
    /// # Arguments
    /// * `values` - Slice of undervolt values in mV for each core
    ///
    /// # Returns
    /// Vector of command arguments
    fn build_args(&self, values: &[i32]) -> Vec<String> {
        let mut args = Vec::new();
        
        // ryzenadj uses --set-coall for setting all cores at once
        // or individual core settings with --set-coper-N
        // For batching, we use --set-coall with the average or
        // individual per-core settings
        
        // Using per-core undervolt settings
        for (core_idx, &value) in values.iter().enumerate() {
            // ryzenadj expects positive values for undervolt offset
            // Convert our negative mV to the format ryzenadj expects
            let abs_value = value.abs();
            args.push(format!("--set-coper-{}", core_idx));
            args.push(format!("{}", abs_value));
        }
        
        args
    }

    /// Apply undervolt values to all cores
    ///
    /// # Arguments
    /// * `values` - Slice of undervolt values in mV for each core
    ///
    /// # Returns
    /// * `Ok(ApplyResult)` - Result with success status and failure count
    /// * `Err(RyzenadjError)` - If max failures reached or critical error
    pub async fn apply(&mut self, values: &[i32]) -> Result<ApplyResult, RyzenadjError> {
        let args = self.build_args(values);
        
        match self.execute_command(&args).await {
            Ok(()) => {
                self.record_success();
                Ok(ApplyResult {
                    success: true,
                    consecutive_failures: 0,
                })
            }
            Err(e) => {
                // Record failure and check if we've hit the limit
                match self.record_failure() {
                    Ok(count) => {
                        // Under the limit, return result with failure info
                        eprintln!("ryzenadj failed (attempt {}): {}", count, e);
                        Ok(ApplyResult {
                            success: false,
                            consecutive_failures: count,
                        })
                    }
                    Err(max_err) => {
                        // Hit the limit, propagate the error
                        Err(max_err)
                    }
                }
            }
        }
    }

    /// Reset all undervolt values to zero (safe state)
    ///
    /// This is called during shutdown or panic recovery
    pub async fn reset_to_zero(&mut self, num_cores: usize) -> Result<(), RyzenadjError> {
        let values: Vec<i32> = vec![0; num_cores];
        let args = self.build_args(&values);
        
        // For reset, we don't track failures - just try once
        self.execute_command(&args).await
    }

    /// Execute the ryzenadj command with given arguments
    async fn execute_command(&self, args: &[String]) -> Result<(), RyzenadjError> {
        let output = Command::new(&self.binary_path)
            .args(args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .await
            .map_err(|e| {
                if e.kind() == std::io::ErrorKind::NotFound {
                    RyzenadjError::BinaryNotFound(self.binary_path.display().to_string())
                } else {
                    RyzenadjError::ExecutionFailed(e.to_string())
                }
            })?;

        if output.status.success() {
            Ok(())
        } else {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            let code = output.status.code().unwrap_or(-1);
            Err(RyzenadjError::NonZeroExit { code, stderr })
        }
    }
}


/// Simulate a sequence of apply results for testing consecutive failure logic
///
/// # Arguments
/// * `results` - Sequence of success (true) or failure (false) results
/// * `max_failures` - Maximum consecutive failures allowed
///
/// # Returns
/// * `Ok(final_count)` - Final consecutive failure count if no max reached
/// * `Err(count)` - The count at which max failures was reached
pub fn simulate_failure_sequence(results: &[bool], max_failures: u32) -> Result<u32, u32> {
    let mut consecutive_failures: u32 = 0;
    
    for &success in results {
        if success {
            consecutive_failures = 0;
        } else {
            consecutive_failures += 1;
            if consecutive_failures >= max_failures {
                return Err(consecutive_failures);
            }
        }
    }
    
    Ok(consecutive_failures)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_executor_new() {
        let executor = RyzenadjExecutor::new("/usr/bin/ryzenadj");
        assert_eq!(executor.binary_path(), &PathBuf::from("/usr/bin/ryzenadj"));
        assert_eq!(executor.consecutive_failures(), 0);
        assert_eq!(executor.max_failures(), MAX_CONSECUTIVE_FAILURES);
    }

    #[test]
    fn test_executor_with_max_failures() {
        let executor = RyzenadjExecutor::with_max_failures("/usr/bin/ryzenadj", 3);
        assert_eq!(executor.max_failures(), 3);
    }

    #[test]
    fn test_build_args_single_core() {
        let executor = RyzenadjExecutor::new("ryzenadj");
        let args = executor.build_args(&[-25]);
        assert_eq!(args, vec!["--set-coper-0", "25"]);
    }

    #[test]
    fn test_build_args_multiple_cores() {
        let executor = RyzenadjExecutor::new("ryzenadj");
        let args = executor.build_args(&[-20, -25, -30, -35]);
        assert_eq!(args, vec![
            "--set-coper-0", "20",
            "--set-coper-1", "25",
            "--set-coper-2", "30",
            "--set-coper-3", "35",
        ]);
    }

    #[test]
    fn test_build_args_zero_values() {
        let executor = RyzenadjExecutor::new("ryzenadj");
        let args = executor.build_args(&[0, 0, 0, 0]);
        assert_eq!(args, vec![
            "--set-coper-0", "0",
            "--set-coper-1", "0",
            "--set-coper-2", "0",
            "--set-coper-3", "0",
        ]);
    }

    #[test]
    fn test_record_failure_under_limit() {
        let mut executor = RyzenadjExecutor::with_max_failures("ryzenadj", 5);
        
        // First 4 failures should be OK
        for i in 1..5 {
            let result = executor.record_failure();
            assert!(result.is_ok());
            assert_eq!(result.unwrap(), i);
        }
    }

    #[test]
    fn test_record_failure_at_limit() {
        let mut executor = RyzenadjExecutor::with_max_failures("ryzenadj", 5);
        
        // First 4 failures
        for _ in 0..4 {
            let _ = executor.record_failure();
        }
        
        // 5th failure should trigger error
        let result = executor.record_failure();
        assert!(result.is_err());
        match result {
            Err(RyzenadjError::MaxFailuresReached(count)) => {
                assert_eq!(count, 5);
            }
            _ => panic!("Expected MaxFailuresReached error"),
        }
    }

    #[test]
    fn test_record_success_resets_counter() {
        let mut executor = RyzenadjExecutor::with_max_failures("ryzenadj", 5);
        
        // Add some failures
        let _ = executor.record_failure();
        let _ = executor.record_failure();
        assert_eq!(executor.consecutive_failures(), 2);
        
        // Success should reset
        executor.record_success();
        assert_eq!(executor.consecutive_failures(), 0);
    }

    #[test]
    fn test_simulate_failure_sequence_all_success() {
        let results = vec![true, true, true, true, true];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(0));
    }

    #[test]
    fn test_simulate_failure_sequence_mixed() {
        // Fail, fail, success, fail, fail
        let results = vec![false, false, true, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(2)); // 2 consecutive failures at end
    }

    #[test]
    fn test_simulate_failure_sequence_hits_limit() {
        // 5 consecutive failures
        let results = vec![true, false, false, false, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Err(5));
    }

    #[test]
    fn test_simulate_failure_sequence_reset_before_limit() {
        // 4 failures, success, 4 failures - should not hit limit
        let results = vec![false, false, false, false, true, false, false, false, false];
        let outcome = simulate_failure_sequence(&results, 5);
        assert_eq!(outcome, Ok(4));
    }

    #[test]
    fn test_error_display() {
        let err = RyzenadjError::BinaryNotFound("/path/to/ryzenadj".to_string());
        assert!(err.to_string().contains("/path/to/ryzenadj"));

        let err = RyzenadjError::MaxFailuresReached(5);
        assert!(err.to_string().contains("5"));

        let err = RyzenadjError::NonZeroExit {
            code: 1,
            stderr: "error message".to_string(),
        };
        assert!(err.to_string().contains("1"));
        assert!(err.to_string().contains("error message"));
    }
}
