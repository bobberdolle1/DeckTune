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
//! - **Fan control**: Temperature-based fan curve with safety overrides
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
//! │  │ FanController│  │  Watchdog    │  │  OutputWriter    │  │
//! │  │ (hwmon sysfs)│  │  (10s timer) │  │  (JSON stdout)   │  │
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
//!   --status-interval 1000 \
//!   --fan-control --fan-mode custom \
//!   --fan-curve 40:20 --fan-curve 60:50 --fan-curve 80:100
//! ```
//!
//! # Signal Handling
//!
//! - **SIGTERM/SIGINT**: Graceful shutdown (resets values to 0, returns fan to BIOS)
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
//! - `7`: Fan control initialization failed
//! - `101`: Panic (after resetting values)
//!
//! # Requirements
//!
//! - Linux with /proc/stat (SteamOS 3.x)
//! - Root privileges (for ryzenadj and fan control)
//! - ryzenadj binary in PATH or specified via --ryzenadj-path

mod config;
mod load_monitor;
mod strategy;
mod output;
mod hysteresis;
mod interpolation;
mod ryzenadj;
mod watchdog;
mod safety;
pub mod fan;

#[cfg(unix)]
mod signals;

use clap::Parser;
use config::{Args, FanControlMode, validate_args};
use output::{OutputWriter, FanStatusOutput};
use fan::{FanController, FanCurve, FanCurvePoint, FanControllerConfig, FanSafetyLimits};
#[cfg(unix)]
use signals::{SignalHandler, SignalState, graceful_shutdown, install_panic_hook};
use safety::check_root_or_exit;

/// Initialize fan controller from CLI arguments
#[cfg(unix)]
fn init_fan_controller(args: &Args, verbose: bool) -> Option<FanController> {
    if !args.fan_control {
        return None;
    }

    if verbose {
        eprintln!("Initializing fan controller...");
        eprintln!("  Mode: {}", args.fan_mode);
        eprintln!("  Zero RPM: {}", args.fan_zero_rpm);
        eprintln!("  Hysteresis: {}°C", args.fan_hysteresis);
        eprintln!("  Curve points: {}", args.fan_curve.len());
    }

    // Try to create fan controller
    let mut controller = match FanController::new() {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Warning: Failed to initialize fan controller: {}", e);
            eprintln!("Fan control will be disabled.");
            return None;
        }
    };

    // Set up configuration
    let mut config = FanControllerConfig::default();
    config.hysteresis_temp = args.fan_hysteresis;
    
    // Configure safety limits with zero RPM setting
    config.safety_limits = FanSafetyLimits {
        allow_zero_rpm: args.fan_zero_rpm,
        ..Default::default()
    };
    
    controller.set_config(config);

    // Set up fan curve based on mode
    match args.fan_mode {
        FanControlMode::Default => {
            // Use default curve, don't enable manual control
            if verbose {
                eprintln!("Fan mode: default (BIOS control)");
            }
            return Some(controller);
        }
        FanControlMode::Custom => {
            // Build curve from CLI arguments
            if args.fan_curve.len() >= 2 {
                let points: Vec<FanCurvePoint> = args.fan_curve
                    .iter()
                    .map(|p| FanCurvePoint::new(p.temp_c, p.speed_percent))
                    .collect();
                
                match FanCurve::new(points) {
                    Ok(curve) => {
                        if verbose {
                            eprintln!("Fan curve set with {} points", curve.len());
                        }
                        controller.set_curve(curve);
                    }
                    Err(e) => {
                        eprintln!("Warning: Invalid fan curve: {}", e);
                        eprintln!("Using default curve.");
                    }
                }
            } else if verbose {
                eprintln!("Warning: Custom mode requires at least 2 curve points, using default");
            }
        }
        FanControlMode::Fixed => {
            // Fixed mode: use first curve point as fixed speed
            if let Some(point) = args.fan_curve.first() {
                // Create a flat curve at the fixed speed
                let points = vec![
                    FanCurvePoint::new(0, point.speed_percent),
                    FanCurvePoint::new(100, point.speed_percent),
                ];
                if let Ok(curve) = FanCurve::new(points) {
                    controller.set_curve(curve);
                    if verbose {
                        eprintln!("Fan fixed at {}%", point.speed_percent);
                    }
                }
            }
        }
    }

    // Enable manual control for custom/fixed modes
    if args.fan_mode != FanControlMode::Default {
        if let Err(e) = controller.enable() {
            eprintln!("Warning: Failed to enable fan control: {}", e);
            return None;
        }
        if verbose {
            eprintln!("Fan manual control enabled");
        }
    }

    Some(controller)
}

/// Get fan status for JSON output
fn get_fan_status(controller: &FanController, mode: &FanControlMode) -> Option<FanStatusOutput> {
    match controller.status() {
        Ok(status) => Some(FanStatusOutput::new(
            status.temp_c,
            status.pwm,
            status.speed_percent,
            &mode.to_string(),
            status.rpm,
            status.safety_override_active,
        )),
        Err(_) => None,
    }
}

#[cfg(unix)]
#[tokio::main]
async fn main() {
    let args = Args::parse();

    if let Err(e) = validate_args(&args) {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }

    // Check if running as root (required for ryzenadj and fan control)
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
        eprintln!("  Fan control: {}", args.fan_control);
    }

    // Set up signal handling
    let signal_state = SignalState::new();
    let signal_handler = SignalHandler::new(signal_state.clone());
    
    if let Err(e) = signal_handler.start().await {
        eprintln!("Warning: Failed to register signal handlers: {}", e);
    }

    // Initialize fan controller if enabled
    let mut fan_controller = init_fan_controller(&args, args.verbose);
    let fan_mode = args.fan_mode;

    // Create output writer
    let mut output_writer = OutputWriter::new(args.status_interval_ms);

    // Main loop placeholder - will be implemented in subsequent tasks
    if args.verbose {
        eprintln!("gymdeck3 initialized successfully, entering main loop...");
    }

    // Tick counter for fan updates (update fan every 500ms = 5 ticks at 100ms)
    let mut tick_count: u64 = 0;
    let fan_update_interval = 5; // Update fan every 5 ticks

    // Simple main loop that checks for signals
    loop {
        tick_count += 1;

        // Check for shutdown signal
        if signal_state.is_shutdown_requested() {
            if args.verbose {
                eprintln!("Shutdown requested, cleaning up...");
            }
            
            // Disable fan control (returns to BIOS)
            if let Some(ref mut fc) = fan_controller {
                if let Err(e) = fc.disable() {
                    eprintln!("Warning: Failed to disable fan control: {}", e);
                }
                if args.verbose {
                    eprintln!("Fan control returned to BIOS");
                }
            }
            
            let exit_code = graceful_shutdown(
                num_cores,
                &args.ryzenadj_path.display().to_string(),
                args.verbose,
            ).await;
            std::process::exit(exit_code);
        }

        // Update fan controller (every 500ms)
        if tick_count % fan_update_interval == 0 {
            if let Some(ref mut fc) = fan_controller {
                if fc.is_active() {
                    if let Err(e) = fc.update() {
                        if args.verbose {
                            eprintln!("Fan update error: {}", e);
                        }
                    }
                }
            }
        }

        // Check for force status signal (SIGUSR1)
        if signal_state.take_force_status() {
            // Force output status regardless of interval
            let load = vec![0.0; num_cores];
            let values = vec![0; num_cores];
            
            // Get fan status if available
            let fan_status = fan_controller.as_ref()
                .and_then(|fc| get_fan_status(fc, &fan_mode));
            
            if let Some(fan) = fan_status {
                let status = output::StatusOutput::with_fan(
                    load, values, args.strategy, output_writer.uptime_ms(), fan
                );
                if let Err(e) = status.to_json().map(|j| println!("{}", j)) {
                    eprintln!("Error writing status: {}", e);
                }
            } else if let Err(e) = output_writer.write_status(load, values, args.strategy) {
                eprintln!("Error writing status: {}", e);
            }
        }

        // Sleep briefly to avoid busy-waiting
        // This will be replaced with actual sampling logic in subsequent tasks
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

// Non-Unix stub (Windows compilation check)
#[cfg(not(unix))]
fn main() {
    eprintln!("gymdeck3 requires Unix (Linux/SteamOS) to run.");
    eprintln!("This binary is for Steam Deck only.");
    std::process::exit(1);
}
