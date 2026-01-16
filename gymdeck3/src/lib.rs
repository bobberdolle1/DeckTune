//! gymdeck3 library exports for testing and external use
//!
//! This module provides public exports of all gymdeck3 components for use
//! in tests and potential external integrations. All core functionality is
//! exposed through well-defined interfaces.
//!
//! # Module Organization
//!
//! - **config**: CLI argument parsing and validation
//! - **load_monitor**: CPU load monitoring from /proc/stat
//! - **strategy**: Adaptation strategies (conservative, balanced, aggressive, custom)
//! - **hysteresis**: Dead-band logic for stable value transitions
//! - **interpolation**: Smooth value ramping with linear stepping
//! - **ryzenadj**: Subprocess wrapper for applying undervolt values
//! - **output**: JSON status output formatting (NDJSON)
//! - **signals**: Signal handling (SIGTERM, SIGUSR1)
//! - **watchdog**: Internal watchdog timer for safety
//! - **safety**: Root check and value validation
//! - **fan**: Fan control via hwmon sysfs (temperature curves, hysteresis, safety)
//!
//! # Testing
//!
//! All modules are designed to be testable in isolation:
//!
//! ```rust
//! use gymdeck3::{LoadMonitor, ConservativeStrategy, AdaptationStrategy, CoreBounds};
//!
//! // Test load monitoring with mock data
//! let monitor = LoadMonitor::with_path(100, "/path/to/mock/stat".to_string())?;
//!
//! // Test strategy calculations
//! let strategy = ConservativeStrategy::new();
//! let bounds = CoreBounds { min_mv: -20, max_mv: -35, threshold: 50.0 };
//! let target = strategy.calculate_target(75.0, &bounds);
//! assert!(target >= bounds.max_mv && target <= bounds.min_mv);
//! # Ok::<(), Box<dyn std::error::Error>>(())
//! ```
//!
//! # Property-Based Testing
//!
//! The library is designed with property-based testing in mind. Key properties:
//!
//! - Load values are always in [0.0, 100.0]
//! - Undervolt targets respect configured bounds
//! - Higher load → safer (less negative) undervolt
//! - Hysteresis prevents rapid value changes
//! - Interpolation produces linear sequences

mod config;
mod load_monitor;
mod hysteresis;
mod interpolation;
mod ryzenadj;
mod output;
#[cfg(unix)]
mod signals;
mod watchdog;
mod safety;
pub mod strategy;
pub mod fan;

pub use config::{
    Args,
    Strategy,
    CoreConfig,
    FanControlMode,
    FanCurvePointConfig,
    validate_sample_interval,
    validate_sample_interval_value,
    validate_hysteresis,
    validate_hysteresis_value,
    parse_core_config,
    validate_core_config_values,
    validate_args,
    parse_fan_curve_point,
    validate_fan_curve_point,
    validate_fan_hysteresis,
    parse_acoustic_profile,
};

pub use load_monitor::{
    LoadMonitor,
    LoadMonitorError,
    LoadSample,
    CpuStats,
    CoreStats,
    validate_sample_interval_ms,
    MIN_SAMPLE_INTERVAL_MS,
    MAX_SAMPLE_INTERVAL_MS,
};

pub use strategy::{
    AdaptationStrategy,
    CoreBounds,
    ConservativeStrategy,
    BalancedStrategy,
    AggressiveStrategy,
    CustomStrategy,
    create_strategy,
    clamp_to_bounds,
    lerp,
};

pub use hysteresis::{
    HysteresisController,
    validate_hysteresis_margin,
    MIN_HYSTERESIS_PERCENT,
    MAX_HYSTERESIS_PERCENT,
};

pub use interpolation::{
    Interpolator,
    DEFAULT_STEP_SIZE_MV,
};

pub use ryzenadj::{
    RyzenadjExecutor,
    RyzenadjError,
    ApplyResult,
    simulate_failure_sequence,
    MAX_CONSECUTIVE_FAILURES,
};

pub use output::{
    StatusOutput,
    FanStatusOutput,
    TransitionOutput,
    ErrorOutput,
    OutputWriter,
    validate_status_output,
};

pub use watchdog::{
    WatchdogState,
    Watchdog,
    check_timeout,
    DEFAULT_WATCHDOG_TIMEOUT_SECS,
};

#[cfg(unix)]
pub use signals::{
    SignalState,
    SignalHandler,
    graceful_shutdown,
    install_panic_hook,
};

pub use safety::{
    is_root,
    check_root_or_exit,
    clamp_value,
    is_value_in_bounds,
    clamp_all_values,
    all_values_in_bounds,
    EXIT_CODE_NOT_ROOT,
};

// Fan control module re-exports
pub use fan::{
    FanController,
    FanCurve,
    FanCurvePoint,
    FanControllerConfig,
    FanStatus,
    FanMode,
    FanSafetyLimits,
    HwmonDevice,
    HwmonError,
    find_steam_deck_hwmon,
    CRITICAL_TEMP_C,
    HIGH_TEMP_C,
    ZERO_RPM_MAX_TEMP_C,
    AcousticProfile,
};
