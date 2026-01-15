//! Internal watchdog timer for gymdeck3
//!
//! Monitors the main loop and resets undervolt values if it stalls for too long.
//! This ensures safety even if the daemon hangs or deadlocks.
//!
//! Requirements: 9.4

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::watch;

/// Default watchdog timeout in seconds
pub const DEFAULT_WATCHDOG_TIMEOUT_SECS: u64 = 10;

/// Watchdog state shared between the main loop and watchdog task
#[derive(Debug, Clone)]
pub struct WatchdogState {
    /// Last heartbeat timestamp (milliseconds since start)
    last_heartbeat_ms: Arc<AtomicU64>,
    /// Start time for calculating elapsed time
    start_time: Instant,
}

impl Default for WatchdogState {
    fn default() -> Self {
        Self::new()
    }
}

impl WatchdogState {
    /// Create a new watchdog state
    pub fn new() -> Self {
        Self {
            last_heartbeat_ms: Arc::new(AtomicU64::new(0)),
            start_time: Instant::now(),
        }
    }

    /// Record a heartbeat from the main loop
    ///
    /// This should be called regularly from the main loop to indicate
    /// that the daemon is still functioning properly.
    pub fn heartbeat(&self) {
        let elapsed_ms = self.start_time.elapsed().as_millis() as u64;
        self.last_heartbeat_ms.store(elapsed_ms, Ordering::SeqCst);
    }

    /// Get the time since the last heartbeat in milliseconds
    pub fn time_since_heartbeat_ms(&self) -> u64 {
        let current_ms = self.start_time.elapsed().as_millis() as u64;
        let last_ms = self.last_heartbeat_ms.load(Ordering::SeqCst);
        current_ms.saturating_sub(last_ms)
    }

    /// Check if the watchdog has timed out
    ///
    /// # Arguments
    /// * `timeout_ms` - Timeout threshold in milliseconds
    ///
    /// # Returns
    /// true if the time since last heartbeat exceeds the timeout
    pub fn is_timed_out(&self, timeout_ms: u64) -> bool {
        self.time_since_heartbeat_ms() > timeout_ms
    }
}

/// Watchdog controller that monitors the main loop and triggers reset on stall
pub struct Watchdog {
    state: WatchdogState,
    timeout_secs: u64,
    num_cores: usize,
    ryzenadj_path: String,
    /// Channel to signal watchdog timeout
    timeout_tx: watch::Sender<bool>,
    timeout_rx: watch::Receiver<bool>,
}

impl Watchdog {
    /// Create a new watchdog with the specified configuration
    ///
    /// # Arguments
    /// * `timeout_secs` - Timeout in seconds before triggering reset
    /// * `num_cores` - Number of CPU cores to reset
    /// * `ryzenadj_path` - Path to ryzenadj binary
    pub fn new(timeout_secs: u64, num_cores: usize, ryzenadj_path: String) -> Self {
        let (timeout_tx, timeout_rx) = watch::channel(false);
        Self {
            state: WatchdogState::new(),
            timeout_secs,
            num_cores,
            ryzenadj_path,
            timeout_tx,
            timeout_rx,
        }
    }

    /// Get a clone of the watchdog state for use in the main loop
    pub fn state(&self) -> WatchdogState {
        self.state.clone()
    }

    /// Get a receiver for timeout notifications
    pub fn timeout_receiver(&self) -> watch::Receiver<bool> {
        self.timeout_rx.clone()
    }

    /// Get the timeout in seconds
    pub fn timeout_secs(&self) -> u64 {
        self.timeout_secs
    }

    /// Start the watchdog monitoring task
    ///
    /// This spawns a background task that periodically checks for heartbeats.
    /// If no heartbeat is received within the timeout period, it resets
    /// undervolt values and signals a timeout.
    ///
    /// # Arguments
    /// * `verbose` - Whether to log verbose output
    pub async fn start(&self, verbose: bool) {
        let state = self.state.clone();
        let timeout_ms = self.timeout_secs * 1000;
        let num_cores = self.num_cores;
        let ryzenadj_path = self.ryzenadj_path.clone();
        let timeout_tx = self.timeout_tx.clone();

        // Initial heartbeat
        state.heartbeat();

        tokio::spawn(async move {
            let check_interval = Duration::from_millis(1000); // Check every second

            loop {
                tokio::time::sleep(check_interval).await;

                if state.is_timed_out(timeout_ms) {
                    eprintln!(
                        "WATCHDOG: Main loop stalled for >{}s, resetting values...",
                        timeout_ms / 1000
                    );

                    // Reset values to safe state
                    if let Err(e) = reset_values_sync(&ryzenadj_path, num_cores) {
                        eprintln!("WATCHDOG: Failed to reset values: {}", e);
                    } else if verbose {
                        eprintln!("WATCHDOG: Values reset to 0");
                    }

                    // Signal timeout
                    let _ = timeout_tx.send(true);

                    // Exit with watchdog timeout code
                    std::process::exit(5);
                }
            }
        });
    }
}

/// Reset all undervolt values to zero synchronously
///
/// This is used by the watchdog when it detects a stall.
/// Uses blocking I/O since we may be in a situation where async is not working.
fn reset_values_sync(ryzenadj_path: &str, num_cores: usize) -> Result<(), String> {
    let args: Vec<String> = (0..num_cores)
        .flat_map(|i| vec![format!("--set-coper-{}", i), "0".to_string()])
        .collect();

    let output = std::process::Command::new(ryzenadj_path)
        .args(&args)
        .output()
        .map_err(|e| format!("Failed to execute ryzenadj: {}", e))?;

    if output.status.success() {
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!(
            "ryzenadj exited with code {:?}: {}",
            output.status.code(),
            stderr
        ))
    }
}

/// Check if the watchdog timeout has been exceeded
///
/// Utility function for testing watchdog logic without spawning tasks.
///
/// # Arguments
/// * `last_heartbeat_ms` - Time of last heartbeat in milliseconds since start
/// * `current_time_ms` - Current time in milliseconds since start
/// * `timeout_ms` - Timeout threshold in milliseconds
///
/// # Returns
/// true if timeout exceeded
pub fn check_timeout(last_heartbeat_ms: u64, current_time_ms: u64, timeout_ms: u64) -> bool {
    current_time_ms.saturating_sub(last_heartbeat_ms) > timeout_ms
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_watchdog_state_new() {
        let state = WatchdogState::new();
        // Initially, time since heartbeat should be very small (just created)
        assert!(state.time_since_heartbeat_ms() < 100);
    }

    #[test]
    fn test_watchdog_state_heartbeat() {
        let state = WatchdogState::new();
        
        // Wait a bit
        std::thread::sleep(Duration::from_millis(50));
        
        // Record heartbeat
        state.heartbeat();
        
        // Time since heartbeat should be very small
        assert!(state.time_since_heartbeat_ms() < 50);
    }

    #[test]
    fn test_watchdog_state_timeout_check() {
        let state = WatchdogState::new();
        state.heartbeat();
        
        // Should not be timed out immediately
        assert!(!state.is_timed_out(1000));
        
        // Wait and check again
        std::thread::sleep(Duration::from_millis(100));
        
        // Should be timed out with very short timeout
        assert!(state.is_timed_out(50));
        
        // Should not be timed out with longer timeout
        assert!(!state.is_timed_out(200));
    }

    #[test]
    fn test_check_timeout_function() {
        // No timeout
        assert!(!check_timeout(0, 5000, 10000));
        
        // Exactly at timeout (not exceeded)
        assert!(!check_timeout(0, 10000, 10000));
        
        // Timeout exceeded
        assert!(check_timeout(0, 10001, 10000));
        
        // With offset
        assert!(!check_timeout(5000, 10000, 10000));
        assert!(check_timeout(5000, 15001, 10000));
    }

    #[test]
    fn test_watchdog_new() {
        let watchdog = Watchdog::new(10, 4, "/usr/bin/ryzenadj".to_string());
        assert_eq!(watchdog.timeout_secs(), 10);
    }

    #[test]
    fn test_watchdog_state_clone() {
        let state1 = WatchdogState::new();
        let state2 = state1.clone();
        
        // Heartbeat on one should be visible on the other
        state1.heartbeat();
        
        // Both should have similar time since heartbeat
        let diff = state1.time_since_heartbeat_ms().abs_diff(state2.time_since_heartbeat_ms());
        assert!(diff < 10);
    }

    #[test]
    fn test_watchdog_state_default() {
        let state = WatchdogState::default();
        assert!(state.time_since_heartbeat_ms() < 100);
    }
}
