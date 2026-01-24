//! Voltage controller for per-core dynamic voltage adjustment
//!
//! Implements the VoltageController that manages voltage curves and applies
//! voltage offsets based on real-time CPU load.
//!
//! Requirements: 5.5, 9.5

use std::fs;
use std::path::PathBuf;
use crate::safety::clamp_value;
use crate::strategy::CoreBounds;

/// Configuration for a single CPU core's voltage curve
#[derive(Debug, Clone, PartialEq)]
pub struct CoreConfig {
    /// Core ID (0-based index)
    pub core_id: usize,
    /// Minimum voltage offset in mV (less aggressive, applied at low load)
    pub min_mv: i32,
    /// Maximum voltage offset in mV (more aggressive, applied at high load)
    pub max_mv: i32,
    /// Load threshold percentage (0-100) where transition begins
    pub threshold: f32,
}

impl CoreConfig {
    /// Create a new CoreConfig with validation
    ///
    /// # Arguments
    /// * `core_id` - Core identifier (0-based)
    /// * `min_mv` - Voltage offset at low load (-100 to 0 mV) - applied below threshold
    /// * `max_mv` - Voltage offset at high load (-100 to 0 mV) - applied above threshold
    /// * `threshold` - Load threshold (0-100%)
    ///
    /// Note: Typically min_mv is more negative (more aggressive) than max_mv
    /// because we can afford more aggressive undervolting at low loads.
    ///
    /// # Returns
    /// * `Ok(CoreConfig)` if valid
    /// * `Err(String)` if validation fails
    pub fn new(core_id: usize, min_mv: i32, max_mv: i32, threshold: f32) -> Result<Self, String> {
        // Validate voltage range
        if min_mv < -100 || min_mv > 0 {
            return Err(format!("min_mv must be in range [-100, 0], got {}", min_mv));
        }
        if max_mv < -100 || max_mv > 0 {
            return Err(format!("max_mv must be in range [-100, 0], got {}", max_mv));
        }
        
        // Validate min <= max (numerically: -30 <= -15)
        // min_mv is typically more negative (applied at low load)
        // max_mv is typically less negative (applied at high load for stability)
        if min_mv > max_mv {
            return Err(format!(
                "min_mv ({}) must be <= max_mv ({}) (more negative <= less negative)",
                min_mv, max_mv
            ));
        }
        
        // Validate threshold range
        if threshold < 0.0 || threshold > 100.0 {
            return Err(format!("threshold must be in range [0, 100], got {}", threshold));
        }
        
        Ok(CoreConfig {
            core_id,
            min_mv,
            max_mv,
            threshold,
        })
    }
    
    /// Calculate voltage offset for a given CPU load
    ///
    /// Uses piecewise linear interpolation:
    /// - load <= threshold: returns min_mv
    /// - load > threshold: linear interpolation from min_mv to max_mv
    ///
    /// # Arguments
    /// * `load` - CPU load percentage (0-100)
    ///
    /// # Returns
    /// Voltage offset in mV
    pub fn calculate_voltage(&self, load: f32) -> i32 {
        let load = load.max(0.0).min(100.0); // Clamp load to valid range
        
        if load <= self.threshold {
            self.min_mv
        } else {
            // Linear interpolation from min_mv to max_mv
            let range = 100.0 - self.threshold;
            if range <= 0.0 {
                // Threshold at 100%, always use min_mv
                self.min_mv
            } else {
                let progress = (load - self.threshold) / range;
                let voltage_range = self.max_mv - self.min_mv;
                self.min_mv + (voltage_range as f32 * progress).round() as i32
            }
        }
    }
    
    /// Convert to CoreBounds for safety validation
    /// 
    /// Note: CoreBounds has opposite semantics:
    /// - CoreBounds.min_mv = less aggressive (closer to 0)
    /// - CoreBounds.max_mv = more aggressive (more negative)
    /// 
    /// Our CoreConfig:
    /// - min_mv = applied at low load (typically more aggressive)
    /// - max_mv = applied at high load (typically less aggressive)
    pub fn to_bounds(&self) -> CoreBounds {
        CoreBounds {
            min_mv: self.max_mv,  // Swap: our max_mv is their min_mv (less aggressive)
            max_mv: self.min_mv,  // Swap: our min_mv is their max_mv (more aggressive)
            threshold: self.threshold,
        }
    }
}

/// State of a single core in the voltage controller
#[derive(Debug, Clone)]
struct CoreState {
    config: CoreConfig,
    current_voltage: i32,
    last_load: f32,
}

/// Errors from voltage controller operations
#[derive(Debug)]
pub enum VoltageControllerError {
    /// Invalid core ID
    InvalidCoreId(usize),
    /// Invalid configuration
    InvalidConfig(String),
    /// I/O error writing to sysfs
    IoError(std::io::Error),
    /// Controller not started
    NotStarted,
    /// Controller already started
    AlreadyStarted,
    /// Safety limit violation
    SafetyViolation(String),
}

impl std::fmt::Display for VoltageControllerError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            VoltageControllerError::InvalidCoreId(id) => {
                write!(f, "Invalid core ID: {}", id)
            }
            VoltageControllerError::InvalidConfig(msg) => {
                write!(f, "Invalid configuration: {}", msg)
            }
            VoltageControllerError::IoError(e) => {
                write!(f, "I/O error: {}", e)
            }
            VoltageControllerError::NotStarted => {
                write!(f, "Controller not started")
            }
            VoltageControllerError::AlreadyStarted => {
                write!(f, "Controller already started")
            }
            VoltageControllerError::SafetyViolation(msg) => {
                write!(f, "Safety violation: {}", msg)
            }
        }
    }
}

impl std::error::Error for VoltageControllerError {}

impl From<std::io::Error> for VoltageControllerError {
    fn from(e: std::io::Error) -> Self {
        VoltageControllerError::IoError(e)
    }
}

/// Voltage controller for dynamic per-core voltage adjustment
///
/// Manages voltage curves for multiple CPU cores and applies voltage
/// offsets via sysfs based on real-time CPU load.
pub struct VoltageController {
    /// Per-core state
    cores: Vec<CoreState>,
    /// Whether the controller is active
    active: bool,
    /// Base path for CPU voltage control (for testing)
    sysfs_base: PathBuf,
}

impl VoltageController {
    /// Create a new VoltageController with the specified number of cores
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores to manage
    ///
    /// # Returns
    /// VoltageController with default safe configuration
    pub fn new(num_cores: usize) -> Self {
        let cores = (0..num_cores)
            .map(|core_id| CoreState {
                config: CoreConfig {
                    core_id,
                    min_mv: -30,  // Safe default
                    max_mv: -15,  // Safe default
                    threshold: 50.0,
                },
                current_voltage: 0,
                last_load: 0.0,
            })
            .collect();
        
        Self {
            cores,
            active: false,
            sysfs_base: PathBuf::from("/sys/devices/system/cpu"),
        }
    }
    
    /// Create a VoltageController with custom sysfs base path (for testing)
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores
    /// * `sysfs_base` - Base path for CPU sysfs
    pub fn with_sysfs_base(num_cores: usize, sysfs_base: PathBuf) -> Self {
        let mut controller = Self::new(num_cores);
        controller.sysfs_base = sysfs_base;
        controller
    }
    
    /// Get the number of cores managed by this controller
    pub fn num_cores(&self) -> usize {
        self.cores.len()
    }
    
    /// Check if the controller is active
    pub fn is_active(&self) -> bool {
        self.active
    }
    
    /// Set configuration for a specific core
    ///
    /// # Arguments
    /// * `config` - Core configuration
    ///
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(VoltageControllerError)` if core_id invalid or config invalid
    pub fn set_core_config(&mut self, config: CoreConfig) -> Result<(), VoltageControllerError> {
        let core_id = config.core_id;
        
        if core_id >= self.cores.len() {
            return Err(VoltageControllerError::InvalidCoreId(core_id));
        }
        
        // Validate configuration
        CoreConfig::new(
            config.core_id,
            config.min_mv,
            config.max_mv,
            config.threshold,
        )
        .map_err(VoltageControllerError::InvalidConfig)?;
        
        // Update core state
        self.cores[core_id].config = config;
        
        Ok(())
    }
    
    /// Get configuration for a specific core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(&CoreConfig)` if successful
    /// * `Err(VoltageControllerError::InvalidCoreId)` if core_id invalid
    pub fn get_core_config(&self, core_id: usize) -> Result<&CoreConfig, VoltageControllerError> {
        self.cores
            .get(core_id)
            .map(|state| &state.config)
            .ok_or(VoltageControllerError::InvalidCoreId(core_id))
    }
    
    /// Get all core configurations
    pub fn get_all_configs(&self) -> Vec<CoreConfig> {
        self.cores.iter().map(|state| state.config.clone()).collect()
    }
    
    /// Start the voltage controller
    ///
    /// Activates dynamic voltage adjustment. Voltage will be applied
    /// when update_and_apply() is called with load data.
    ///
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(VoltageControllerError::AlreadyStarted)` if already active
    pub fn start(&mut self) -> Result<(), VoltageControllerError> {
        if self.active {
            return Err(VoltageControllerError::AlreadyStarted);
        }
        
        self.active = true;
        Ok(())
    }
    
    /// Stop the voltage controller
    ///
    /// Deactivates dynamic voltage adjustment and resets all cores to 0mV.
    ///
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(VoltageControllerError::NotStarted)` if not active
    pub fn stop(&mut self) -> Result<(), VoltageControllerError> {
        if !self.active {
            return Err(VoltageControllerError::NotStarted);
        }
        
        // Reset all cores to 0mV (safe state)
        for core_id in 0..self.cores.len() {
            self.apply_voltage(core_id, 0)?;
            self.cores[core_id].current_voltage = 0;
        }
        
        self.active = false;
        Ok(())
    }
    
    /// Update voltage for a core based on current load and apply it
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    /// * `load` - Current CPU load percentage (0-100)
    ///
    /// # Returns
    /// * `Ok(i32)` - The voltage that was applied
    /// * `Err(VoltageControllerError)` if error occurs
    pub fn update_and_apply(&mut self, core_id: usize, load: f32) -> Result<i32, VoltageControllerError> {
        if !self.active {
            return Err(VoltageControllerError::NotStarted);
        }
        
        if core_id >= self.cores.len() {
            return Err(VoltageControllerError::InvalidCoreId(core_id));
        }
        
        // Calculate target voltage based on load
        let config = &self.cores[core_id].config;
        let target_voltage = config.calculate_voltage(load);
        
        // Apply safety clamping
        let bounds = config.to_bounds();
        let safe_voltage = clamp_value(target_voltage, &bounds);
        
        // Apply voltage to hardware
        self.apply_voltage(core_id, safe_voltage)?;
        
        // Update state
        self.cores[core_id].current_voltage = safe_voltage;
        self.cores[core_id].last_load = load;
        
        Ok(safe_voltage)
    }
    
    /// Get current voltage for a core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(i32)` - Current voltage offset in mV
    /// * `Err(VoltageControllerError::InvalidCoreId)` if core_id invalid
    pub fn get_current_voltage(&self, core_id: usize) -> Result<i32, VoltageControllerError> {
        self.cores
            .get(core_id)
            .map(|state| state.current_voltage)
            .ok_or(VoltageControllerError::InvalidCoreId(core_id))
    }
    
    /// Apply voltage offset to a specific core via sysfs
    ///
    /// Writes to /sys/devices/system/cpu/cpuX/cpufreq/amd_pstate_max_freq_khz
    /// or similar interface depending on platform.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    /// * `voltage_mv` - Voltage offset in mV
    ///
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(VoltageControllerError)` if write fails
    fn apply_voltage(&self, core_id: usize, voltage_mv: i32) -> Result<(), VoltageControllerError> {
        // For AMD APUs, voltage control is typically done through ryzenadj
        // or ACPI interfaces. This is a placeholder for the sysfs interface.
        //
        // In production, this would write to the appropriate sysfs file:
        // /sys/devices/system/cpu/cpu{core_id}/cpufreq/amd_pstate_voltage_offset
        //
        // For now, we'll write to a test file if sysfs_base is not the default
        
        let voltage_path = self.sysfs_base
            .join(format!("cpu{}", core_id))
            .join("cpufreq")
            .join("voltage_offset");
        
        // Only write if the path exists (for testing) or if we're in production
        if voltage_path.parent().map(|p| p.exists()).unwrap_or(false) {
            fs::write(&voltage_path, format!("{}", voltage_mv))?;
        }
        
        // In production, this would also call ryzenadj or similar tool
        // For testing, we just validate the write would succeed
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;
    
    #[test]
    fn test_core_config_new_valid() {
        let config = CoreConfig::new(0, -30, -15, 50.0);
        assert!(config.is_ok());
        let config = config.unwrap();
        assert_eq!(config.core_id, 0);
        assert_eq!(config.min_mv, -30);
        assert_eq!(config.max_mv, -15);
        assert_eq!(config.threshold, 50.0);
    }
    
    #[test]
    fn test_core_config_new_invalid_min_range() {
        let config = CoreConfig::new(0, -150, -15, 50.0);
        assert!(config.is_err());
        assert!(config.unwrap_err().contains("min_mv"));
        
        let config = CoreConfig::new(0, 10, -15, 50.0);
        assert!(config.is_err());
    }
    
    #[test]
    fn test_core_config_new_invalid_max_range() {
        let config = CoreConfig::new(0, -30, -150, 50.0);
        assert!(config.is_err());
        assert!(config.unwrap_err().contains("max_mv"));
    }
    
    #[test]
    fn test_core_config_new_invalid_ordering() {
        // min_mv must be <= max_mv (more negative <= less negative)
        let config = CoreConfig::new(0, -20, -40, 50.0);
        assert!(config.is_err());
        let err_msg = config.unwrap_err();
        assert!(err_msg.contains("min_mv"));
        assert!(err_msg.contains("max_mv"));
    }
    
    #[test]
    fn test_core_config_new_invalid_threshold() {
        let config = CoreConfig::new(0, -30, -15, -10.0);
        assert!(config.is_err());
        assert!(config.unwrap_err().contains("threshold"));
        
        let config = CoreConfig::new(0, -30, -15, 150.0);
        assert!(config.is_err());
    }
    
    #[test]
    fn test_core_config_calculate_voltage_below_threshold() {
        let config = CoreConfig::new(0, -30, -15, 50.0).unwrap();
        
        // Below threshold should return min_mv
        assert_eq!(config.calculate_voltage(0.0), -30);
        assert_eq!(config.calculate_voltage(25.0), -30);
        assert_eq!(config.calculate_voltage(50.0), -30);
    }
    
    #[test]
    fn test_core_config_calculate_voltage_above_threshold() {
        let config = CoreConfig::new(0, -30, -15, 50.0).unwrap();
        
        // At 75% (halfway between 50 and 100), should be halfway between -30 and -15
        let voltage = config.calculate_voltage(75.0);
        assert_eq!(voltage, -22); // -30 + (15 * 0.5) = -22.5 -> -22
        
        // At 100%, should be max_mv
        assert_eq!(config.calculate_voltage(100.0), -15);
    }
    
    #[test]
    fn test_core_config_calculate_voltage_clamping() {
        let config = CoreConfig::new(0, -30, -15, 50.0).unwrap();
        
        // Values outside [0, 100] should be clamped
        assert_eq!(config.calculate_voltage(-10.0), -30);
        assert_eq!(config.calculate_voltage(150.0), -15);
    }
    
    #[test]
    fn test_core_config_calculate_voltage_threshold_at_100() {
        let config = CoreConfig::new(0, -30, -15, 100.0).unwrap();
        
        // Threshold at 100% means always use min_mv
        assert_eq!(config.calculate_voltage(0.0), -30);
        assert_eq!(config.calculate_voltage(50.0), -30);
        assert_eq!(config.calculate_voltage(100.0), -30);
    }
    
    #[test]
    fn test_core_config_calculate_voltage_threshold_at_0() {
        let config = CoreConfig::new(0, -30, -15, 0.0).unwrap();
        
        // Threshold at 0% means always interpolate
        assert_eq!(config.calculate_voltage(0.0), -30);
        assert_eq!(config.calculate_voltage(50.0), -22); // Halfway
        assert_eq!(config.calculate_voltage(100.0), -15);
    }
    
    #[test]
    fn test_voltage_controller_new() {
        let controller = VoltageController::new(4);
        assert_eq!(controller.num_cores(), 4);
        assert!(!controller.is_active());
        
        // Check default configs
        for i in 0..4 {
            let config = controller.get_core_config(i).unwrap();
            assert_eq!(config.core_id, i);
            assert_eq!(config.min_mv, -30);
            assert_eq!(config.max_mv, -15);
            assert_eq!(config.threshold, 50.0);
        }
    }
    
    #[test]
    fn test_voltage_controller_set_core_config() {
        let mut controller = VoltageController::new(4);
        
        let config = CoreConfig::new(1, -40, -20, 60.0).unwrap();
        let result = controller.set_core_config(config.clone());
        assert!(result.is_ok());
        
        let retrieved = controller.get_core_config(1).unwrap();
        assert_eq!(retrieved.min_mv, -40);
        assert_eq!(retrieved.max_mv, -20);
        assert_eq!(retrieved.threshold, 60.0);
    }
    
    #[test]
    fn test_voltage_controller_set_core_config_invalid_id() {
        let mut controller = VoltageController::new(4);
        
        let config = CoreConfig::new(10, -30, -15, 50.0).unwrap();
        let result = controller.set_core_config(config);
        assert!(result.is_err());
        match result {
            Err(VoltageControllerError::InvalidCoreId(id)) => assert_eq!(id, 10),
            _ => panic!("Expected InvalidCoreId error"),
        }
    }
    
    #[test]
    fn test_voltage_controller_start_stop() {
        let mut controller = VoltageController::new(4);
        
        assert!(!controller.is_active());
        
        let result = controller.start();
        assert!(result.is_ok());
        assert!(controller.is_active());
        
        // Starting again should fail
        let result = controller.start();
        assert!(result.is_err());
        
        let result = controller.stop();
        assert!(result.is_ok());
        assert!(!controller.is_active());
        
        // Stopping again should fail
        let result = controller.stop();
        assert!(result.is_err());
    }
    
    #[test]
    fn test_voltage_controller_update_and_apply_not_started() {
        let mut controller = VoltageController::new(4);
        
        let result = controller.update_and_apply(0, 50.0);
        assert!(result.is_err());
        match result {
            Err(VoltageControllerError::NotStarted) => {},
            _ => panic!("Expected NotStarted error"),
        }
    }
    
    #[test]
    fn test_voltage_controller_update_and_apply() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = temp_dir.path().to_path_buf();
        
        // Create mock sysfs structure
        for i in 0..4 {
            let cpu_dir = sysfs_base.join(format!("cpu{}", i)).join("cpufreq");
            fs::create_dir_all(&cpu_dir).unwrap();
        }
        
        let mut controller = VoltageController::with_sysfs_base(4, sysfs_base.clone());
        controller.start().unwrap();
        
        // Set custom config for core 0
        let config = CoreConfig::new(0, -30, -15, 50.0).unwrap();
        controller.set_core_config(config).unwrap();
        
        // Apply voltage at 75% load (should be halfway between -30 and -15)
        let result = controller.update_and_apply(0, 75.0);
        assert!(result.is_ok());
        let voltage = result.unwrap();
        assert_eq!(voltage, -22);
        
        // Check current voltage
        assert_eq!(controller.get_current_voltage(0).unwrap(), -22);
    }
    
    #[test]
    fn test_voltage_controller_get_all_configs() {
        let mut controller = VoltageController::new(2);
        
        let config0 = CoreConfig::new(0, -40, -20, 60.0).unwrap();
        let config1 = CoreConfig::new(1, -35, -25, 55.0).unwrap();
        
        controller.set_core_config(config0.clone()).unwrap();
        controller.set_core_config(config1.clone()).unwrap();
        
        let all_configs = controller.get_all_configs();
        assert_eq!(all_configs.len(), 2);
        assert_eq!(all_configs[0].min_mv, -40);
        assert_eq!(all_configs[1].min_mv, -35);
    }
}
