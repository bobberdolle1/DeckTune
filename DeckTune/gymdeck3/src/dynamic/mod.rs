//! Dynamic voltage control module
//!
//! Provides per-core dynamic voltage adjustment based on CPU load.
//! This module implements the backend for DeckTune's Manual Dynamic Mode.
//!
//! Requirements: 5.5, 9.5

pub mod voltage_controller;
pub mod metrics_monitor;
pub mod frequency_curve;
pub mod frequency_controller;

pub use voltage_controller::{VoltageController, CoreConfig, VoltageControllerError};
pub use metrics_monitor::{MetricsMonitor, CoreMetrics, MetricsError};
pub use frequency_curve::{FrequencyCurve, FrequencyPoint};
pub use frequency_controller::{FrequencyVoltageController, FrequencyControllerError};
