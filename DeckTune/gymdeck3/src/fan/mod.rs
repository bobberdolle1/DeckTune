//! Fan control module for Steam Deck
//!
//! Provides low-level fan control via hwmon sysfs interface with:
//! - Automatic hwmon device discovery (jupiter/galileo)
//! - Temperature-based fan curve with linear interpolation
//! - Hysteresis to prevent rapid speed changes
//! - Smoothing (moving average) for gradual transitions
//! - Safety overrides (90°C+ forces 100% PWM)
//! - Fail-safe: Drop trait returns control to BIOS
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                      Fan Control Module                      │
//! │                                                              │
//! │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
//! │  │   HwmonDevice │  │  FanCurve    │  │  FanController   │  │
//! │  │   (sysfs I/O) │  │  (points)    │  │  (main logic)    │  │
//! │  └──────────────┘  └──────────────┘  └──────────────────┘  │
//! │         │                  │                  │             │
//! │         │                  │                  ▼             │
//! │         │                  │         ┌──────────────────┐  │
//! │         │                  └────────►│  Interpolation   │  │
//! │         │                            │  + Hysteresis    │  │
//! │         │                            └────────┬─────────┘  │
//! │         │                                     │             │
//! │         │                                     ▼             │
//! │         │                            ┌──────────────────┐  │
//! │         └───────────────────────────►│  Safety Check    │  │
//! │                                       │  (90°C override) │  │
//! │                                       └──────────────────┘  │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Usage
//!
//! ```rust,ignore
//! use gymdeck3::fan::{FanController, FanCurve, FanMode};
//!
//! // Create curve with temperature -> speed% points
//! let curve = FanCurve::new(vec![
//!     (40, 0),    // 40°C -> 0% (Zero RPM)
//!     (50, 30),   // 50°C -> 30%
//!     (70, 60),   // 70°C -> 60%
//!     (85, 100),  // 85°C -> 100%
//! ])?;
//!
//! // Create controller
//! let mut controller = FanController::new()?;
//! controller.set_curve(curve);
//! controller.set_mode(FanMode::Custom)?;
//!
//! // In main loop (called every tick)
//! controller.update()?;
//! ```
//!
//! # Safety
//!
//! - Temperature >= 90°C always forces 100% PWM regardless of curve
//! - Drop trait automatically returns control to BIOS (pwm1_enable = 2)
//! - All sysfs writes are atomic and validated

mod hwmon;
mod controller;
mod safety;
mod acoustic;
mod smoother;

pub use hwmon::{
    HwmonDevice,
    HwmonError,
    FanMode,
    find_steam_deck_hwmon,
    HWMON_PATH,
};

pub use controller::{
    FanController,
    FanCurve,
    FanCurvePoint,
    FanControllerConfig,
    FanStatus,
    DEFAULT_HYSTERESIS_TEMP,
    DEFAULT_SMOOTHING_SAMPLES,
    MIN_PWM,
    MAX_PWM,
};

pub use safety::{
    FanSafetyLimits,
    SafetyOverride,
    CRITICAL_TEMP_C,
    HIGH_TEMP_C,
    ZERO_RPM_MAX_TEMP_C,
    check_safety_override,
    apply_safety_override,
    is_zero_rpm_safe,
};

pub use acoustic::AcousticProfile;

pub use smoother::{
    PWMSmoother,
    DEFAULT_RAMP_TIME_SEC,
};
