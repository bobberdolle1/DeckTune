//! gymdeck3 - Dynamic undervolt controller for Steam Deck
//!
//! # Overview
//!
//! gymdeck3 is a standalone Rust daemon that provides dynamic CPU undervolt
//! control for Steam Deck. It monitors CPU load in real-time and adjusts
//! undervolt values based on the selected adaptation strategy.
//!
//! # Features
//!
//! - **Real-time load monitoring**: Reads CPU statistics from /proc/stat
//! - **Multiple strategies**: Conservative, Balanced, Aggressive, and Custom
//! - **Hysteresis control**: Prevents value hunting around thresholds
//! - **Smooth transitions**: Linear interpolation with configurable step size
//! - **Safety features**: Watchdog, panic hook, graceful shutdown
//! - **JSON output**: NDJSON status updates for frontend integration
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                         gymdeck3                             │
//! │                                                              │
//! │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
//! │  │ LoadMonitor  │─►│  Adaptation  │─►│  Hysteresis      │  │
//! │  │ /proc/stat   │  │  Strategy    │  │  Controller      │  │
//! │  └──────────────┘  └──────────────┘  └────────┬─────────┘  │
//! │                                                │             │
//! │                                                ▼             │
//! │                                       ┌──────────────────┐  │
//! │                                       │  Interpolator    │  │
//! │                                       │  (smooth ramp)   │  │
//! │                                       └────────┬─────────┘  │
//! │                                                │             │
//! │                                                ▼             │
//! │                                       ┌──────────────────┐  │
//! │                                       │ RyzenadjExecutor │  │
//! │                                       │  (apply values)  │  │
//! │                                       └──────────────────┘  │
//! │                                                              │
//! │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
//! │  │ SignalHandler│  │  Watchdog    │  │  OutputWriter    │  │
//! │  │ TERM/USR1    │  │  (10s timer) │  │  (JSON stdout)   │  │
//! │  └──────────────┘  └──────────────┘  └──────────────────┘  │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Usage
//!
//! ```bash
//! # Start with balanced strategy, 100ms sampling
//! gymdeck3 balanced 100000 \
//!   --core 0:-20:-35:50.0 \
//!   --core 1:-20:-35:50.0 \
//!   --core 2:-20:-35:50.0 \
//!   --core 3:-20:-35:50.0 \
//!   --hysteresis 5.0 \
//!   --ryzenadj-path /usr/bin/ryzenadj \
//!   --status-interval 1000
//! ```
//!
//! # Signal Handling
//!
//! - **SIGTERM/SIGINT**: Graceful shutdown (resets values to 0)
//! - **SIGUSR1**: Force immediate status output
//!
//! # Exit Codes
//!
//! - `0`: Normal exit
//! - `1`: Invalid arguments
//! - `2`: /proc/stat unavailable
//! - `3`: ryzenadj binary not found
//! - `4`: ryzenadj failed 5 consecutive times
//! - `5`: Watchdog timeout (main loop stalled)
//! - `6`: Not running as root
//! - `101`: Panic (after resetting values)
//!
//! # Requirements
//!
//! - Linux with /proc/stat (SteamOS 3.x)
//! - Root privileges (for ryzenadj)
//! - ryzenadj binary in PATH or specified via --ryzenadj-path

mod config;
mod load_monitor;
mod strategy;
mod output;
mod signals;
mod hysteresis;
mod interpolation;
mod ryzenadj;
mod watchdog;
mod safety;

use clap::Parser;
use config::{Args, validate_args};
use output::OutputWriter;
use signals::{SignalHandler, SignalState, graceful_shutdown, install_panic_hook};
use safety::check_root_or_exit;

#[tokio::main]
async fn main() {
    let args = Args::parse();

    if let Err(e) = validate_args(&args) {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }

    // Check if running as root (required for ryzenadj)
    if let Err(exit_code) = check_root_or_exit(args.verbose) {
        std::process::exit(exit_code);
    }

    // Install panic hook to reset values on panic
    let num_cores = if args.cores.is_empty() { 4 } else { args.cores.len() };
    install_panic_hook(num_cores, args.ryzenadj_path.display().to_string());

    if args.verbose {
        eprintln!("gymdeck3 starting with configuration:");
        eprintln!("  Strategy: {}", args.strategy);
        eprintln!("  Sample interval: {} us", args.sample_interval_us);
        eprintln!("  Hysteresis: {}%", args.hysteresis);
        eprintln!("  Ryzenadj path: {:?}", args.ryzenadj_path);
        eprintln!("  Status interval: {} ms", args.status_interval_ms);
        eprintln!("  Cores: {:?}", args.cores);
    }

    // Set up signal handling
    let signal_state = SignalState::new();
    let signal_handler = SignalHandler::new(signal_state.clone());
    
    if let Err(e) = signal_handler.start().await {
        eprintln!("Warning: Failed to register signal handlers: {}", e);
    }

    // Create output writer
    let mut output_writer = OutputWriter::new(args.status_interval_ms);

    // Main loop placeholder - will be implemented in subsequent tasks
    if args.verbose {
        eprintln!("gymdeck3 initialized successfully, entering main loop...");
    }

    // Simple main loop that checks for signals
    loop {
        // Check for shutdown signal
        if signal_state.is_shutdown_requested() {
            if args.verbose {
                eprintln!("Shutdown requested, cleaning up...");
            }
            let exit_code = graceful_shutdown(
                num_cores,
                &args.ryzenadj_path.display().to_string(),
                args.verbose,
            ).await;
            std::process::exit(exit_code);
        }

        // Check for force status signal (SIGUSR1)
        if signal_state.take_force_status() {
            // Force output status regardless of interval
            // Using placeholder values until main loop is fully implemented
            let load = vec![0.0; num_cores];
            let values = vec![0; num_cores];
            if let Err(e) = output_writer.write_status(load, values, args.strategy) {
                eprintln!("Error writing status: {}", e);
            }
        }

        // Sleep briefly to avoid busy-waiting
        // This will be replaced with actual sampling logic in subsequent tasks
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}
