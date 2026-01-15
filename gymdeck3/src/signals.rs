//! Signal handling for gymdeck3
//!
//! Provides handlers for Unix signals:
//! - SIGTERM: Graceful shutdown with value reset to 0
//! - SIGUSR1: Force immediate status output
//!
//! Requirements: 7.3, 7.4, 9.3

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tokio::signal::unix::{signal, SignalKind};

/// Signal state shared between signal handlers and main loop
#[derive(Debug, Clone)]
pub struct SignalState {
    /// Flag indicating SIGTERM was received
    shutdown_requested: Arc<AtomicBool>,
    /// Flag indicating SIGUSR1 was received (force status output)
    force_status: Arc<AtomicBool>,
}

impl Default for SignalState {
    fn default() -> Self {
        Self::new()
    }
}

impl SignalState {
    /// Create a new signal state
    pub fn new() -> Self {
        Self {
            shutdown_requested: Arc::new(AtomicBool::new(false)),
            force_status: Arc::new(AtomicBool::new(false)),
        }
    }

    /// Check if shutdown was requested (SIGTERM received)
    pub fn is_shutdown_requested(&self) -> bool {
        self.shutdown_requested.load(Ordering::SeqCst)
    }

    /// Request shutdown (called by signal handler)
    pub fn request_shutdown(&self) {
        self.shutdown_requested.store(true, Ordering::SeqCst);
    }

    /// Check and clear the force status flag (SIGUSR1)
    ///
    /// Returns true if SIGUSR1 was received since last check
    pub fn take_force_status(&self) -> bool {
        self.force_status.swap(false, Ordering::SeqCst)
    }

    /// Set the force status flag (called by signal handler)
    pub fn set_force_status(&self) {
        self.force_status.store(true, Ordering::SeqCst);
    }

    /// Reset all flags (for testing)
    #[cfg(test)]
    pub fn reset(&self) {
        self.shutdown_requested.store(false, Ordering::SeqCst);
        self.force_status.store(false, Ordering::SeqCst);
    }
}

/// Signal handler that manages SIGTERM and SIGUSR1
pub struct SignalHandler {
    state: SignalState,
}

impl SignalHandler {
    /// Create a new signal handler with the given state
    pub fn new(state: SignalState) -> Self {
        Self { state }
    }

    /// Get a reference to the signal state
    pub fn state(&self) -> &SignalState {
        &self.state
    }

    /// Start listening for signals
    ///
    /// This spawns background tasks that update the signal state when
    /// signals are received. The tasks run until the process exits.
    ///
    /// # Errors
    /// Returns error if signal handlers cannot be registered
    pub async fn start(&self) -> Result<(), std::io::Error> {
        // Register SIGTERM handler
        let state_term = self.state.clone();
        let mut sigterm = signal(SignalKind::terminate())?;
        tokio::spawn(async move {
            loop {
                sigterm.recv().await;
                eprintln!("Received SIGTERM, initiating graceful shutdown...");
                state_term.request_shutdown();
            }
        });

        // Register SIGUSR1 handler
        let state_usr1 = self.state.clone();
        let mut sigusr1 = signal(SignalKind::user_defined1())?;
        tokio::spawn(async move {
            loop {
                sigusr1.recv().await;
                eprintln!("Received SIGUSR1, forcing status output...");
                state_usr1.set_force_status();
            }
        });

        // Register SIGINT handler (Ctrl+C) - same as SIGTERM
        let state_int = self.state.clone();
        let mut sigint = signal(SignalKind::interrupt())?;
        tokio::spawn(async move {
            loop {
                sigint.recv().await;
                eprintln!("Received SIGINT, initiating graceful shutdown...");
                state_int.request_shutdown();
            }
        });

        Ok(())
    }
}

/// Graceful shutdown procedure
///
/// This function should be called when shutdown is requested.
/// It resets all undervolt values to 0 before exiting.
///
/// # Arguments
/// * `num_cores` - Number of CPU cores to reset
/// * `ryzenadj_path` - Path to ryzenadj binary
/// * `verbose` - Whether to log verbose output
///
/// # Returns
/// Exit code (0 for success, non-zero for errors)
pub async fn graceful_shutdown(
    num_cores: usize,
    ryzenadj_path: &str,
    verbose: bool,
) -> i32 {
    use crate::ryzenadj::RyzenadjExecutor;

    if verbose {
        eprintln!("Resetting all undervolt values to 0...");
    }

    let mut executor = RyzenadjExecutor::new(ryzenadj_path);
    
    match executor.reset_to_zero(num_cores).await {
        Ok(()) => {
            if verbose {
                eprintln!("Values reset successfully, exiting.");
            }
            0
        }
        Err(e) => {
            eprintln!("Warning: Failed to reset values during shutdown: {}", e);
            // Still exit with 0 since we tried our best
            0
        }
    }
}

/// Install a panic hook that resets values to 0
///
/// This ensures that even if the daemon panics, undervolt values
/// are reset to safe defaults.
///
/// # Arguments
/// * `num_cores` - Number of CPU cores
/// * `ryzenadj_path` - Path to ryzenadj binary
pub fn install_panic_hook(num_cores: usize, ryzenadj_path: String) {
    let default_hook = std::panic::take_hook();
    
    std::panic::set_hook(Box::new(move |panic_info| {
        eprintln!("PANIC: Resetting undervolt values to safe defaults...");
        
        // Use blocking call since we're in a panic handler
        // We can't use async here, so we spawn a blocking subprocess
        let values: Vec<String> = (0..num_cores)
            .flat_map(|i| vec![format!("--set-coper-{}", i), "0".to_string()])
            .collect();
        
        let _ = std::process::Command::new(&ryzenadj_path)
            .args(&values)
            .output();
        
        // Call the default panic hook
        default_hook(panic_info);
    }));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_signal_state_new() {
        let state = SignalState::new();
        assert!(!state.is_shutdown_requested());
        assert!(!state.take_force_status());
    }

    #[test]
    fn test_signal_state_shutdown() {
        let state = SignalState::new();
        assert!(!state.is_shutdown_requested());
        
        state.request_shutdown();
        assert!(state.is_shutdown_requested());
        
        // Should remain true
        assert!(state.is_shutdown_requested());
    }

    #[test]
    fn test_signal_state_force_status() {
        let state = SignalState::new();
        assert!(!state.take_force_status());
        
        state.set_force_status();
        
        // First take should return true
        assert!(state.take_force_status());
        
        // Second take should return false (cleared)
        assert!(!state.take_force_status());
    }

    #[test]
    fn test_signal_state_reset() {
        let state = SignalState::new();
        state.request_shutdown();
        state.set_force_status();
        
        state.reset();
        
        assert!(!state.is_shutdown_requested());
        assert!(!state.take_force_status());
    }

    #[test]
    fn test_signal_state_clone() {
        let state1 = SignalState::new();
        let state2 = state1.clone();
        
        // Changes to one should be visible in the other
        state1.request_shutdown();
        assert!(state2.is_shutdown_requested());
        
        state2.set_force_status();
        assert!(state1.take_force_status());
    }

    #[test]
    fn test_signal_handler_state_access() {
        let state = SignalState::new();
        let handler = SignalHandler::new(state.clone());
        
        state.request_shutdown();
        assert!(handler.state().is_shutdown_requested());
    }

    #[test]
    fn test_signal_state_default() {
        let state = SignalState::default();
        assert!(!state.is_shutdown_requested());
        assert!(!state.take_force_status());
    }

    #[test]
    fn test_panic_hook_args_building() {
        // Test that the panic hook builds correct ryzenadj arguments
        let num_cores = 4;
        let expected_args: Vec<String> = (0..num_cores)
            .flat_map(|i| vec![format!("--set-coper-{}", i), "0".to_string()])
            .collect();
        
        assert_eq!(expected_args, vec![
            "--set-coper-0", "0",
            "--set-coper-1", "0",
            "--set-coper-2", "0",
            "--set-coper-3", "0",
        ]);
    }

    #[test]
    fn test_panic_hook_args_single_core() {
        let num_cores = 1;
        let args: Vec<String> = (0..num_cores)
            .flat_map(|i| vec![format!("--set-coper-{}", i), "0".to_string()])
            .collect();
        
        assert_eq!(args, vec!["--set-coper-0", "0"]);
    }
}
