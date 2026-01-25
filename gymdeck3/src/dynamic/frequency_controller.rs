//! Frequency-based voltage controller for per-core dynamic voltage adjustment
//!
//! Implements the FrequencyVoltageController that manages frequency-dependent
//! voltage curves and applies voltage offsets based on real-time CPU frequency.
//!
//! Requirements: 2.1, 2.2, 2.3

use std::collections::HashMap;
use std::fs;
use std::io;
use std::path::PathBuf;
use std::time::{Duration, Instant};
use crate::dynamic::frequency_curve::FrequencyCurve;

/// Cache entry for frequency readings
#[derive(Debug, Clone)]
struct FrequencyCache {
    /// Cached frequency value in MHz
    frequency: u32,
    /// Timestamp when this value was cached
    timestamp: Instant,
}

/// Frequency-based voltage controller
///
/// Manages frequency-dependent voltage curves for multiple CPU cores and applies
/// voltage offsets via ryzenadj based on real-time CPU frequency monitoring.
pub struct FrequencyVoltageController {
    /// Per-core frequency curves
    curves: HashMap<usize, FrequencyCurve>,
    
    /// Last applied voltage for each core (to avoid redundant applications)
    last_voltages: HashMap<usize, i32>,
    
    /// Cached frequency readings per core
    frequency_cache: HashMap<usize, FrequencyCache>,
    
    /// Cache TTL in milliseconds (default: 10ms)
    cache_ttl_ms: u64,
    
    /// Base path for CPU sysfs (for testing)
    sysfs_base: PathBuf,
}

/// Errors from frequency voltage controller operations
#[derive(Debug)]
pub enum FrequencyControllerError {
    /// Invalid core ID
    InvalidCoreId(usize),
    
    /// No curve loaded for core
    NoCurveLoaded(usize),
    
    /// I/O error reading from sysfs
    IoError(io::Error),
    
    /// Parse error reading sysfs values
    ParseError(String),
    
    /// Curve validation error
    InvalidCurve(String),
}

impl std::fmt::Display for FrequencyControllerError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FrequencyControllerError::InvalidCoreId(id) => {
                write!(f, "Invalid core ID: {}", id)
            }
            FrequencyControllerError::NoCurveLoaded(id) => {
                write!(f, "No frequency curve loaded for core {}", id)
            }
            FrequencyControllerError::IoError(e) => {
                write!(f, "I/O error: {}", e)
            }
            FrequencyControllerError::ParseError(msg) => {
                write!(f, "Parse error: {}", msg)
            }
            FrequencyControllerError::InvalidCurve(msg) => {
                write!(f, "Invalid curve: {}", msg)
            }
        }
    }
}

impl std::error::Error for FrequencyControllerError {}

impl From<io::Error> for FrequencyControllerError {
    fn from(e: io::Error) -> Self {
        FrequencyControllerError::IoError(e)
    }
}

impl FrequencyVoltageController {
    /// Create a new FrequencyVoltageController
    ///
    /// # Returns
    /// New controller with default configuration
    pub fn new() -> Self {
        Self {
            curves: HashMap::new(),
            last_voltages: HashMap::new(),
            frequency_cache: HashMap::new(),
            cache_ttl_ms: 10, // 10ms cache TTL as per requirements
            sysfs_base: PathBuf::from("/sys/devices/system/cpu"),
        }
    }
    
    /// Create a FrequencyVoltageController with custom sysfs base path (for testing)
    ///
    /// # Arguments
    /// * `sysfs_base` - Base path for CPU sysfs
    pub fn with_sysfs_base(sysfs_base: PathBuf) -> Self {
        Self {
            curves: HashMap::new(),
            last_voltages: HashMap::new(),
            frequency_cache: HashMap::new(),
            cache_ttl_ms: 10,
            sysfs_base,
        }
    }
    
    /// Set cache TTL in milliseconds (for testing)
    ///
    /// # Arguments
    /// * `ttl_ms` - Cache time-to-live in milliseconds
    pub fn set_cache_ttl(&mut self, ttl_ms: u64) {
        self.cache_ttl_ms = ttl_ms;
    }
    
    /// Load a frequency curve for a specific core
    ///
    /// Validates the curve before loading.
    ///
    /// # Arguments
    /// * `curve` - Frequency curve to load
    ///
    /// # Returns
    /// * `Ok(())` if successful
    /// * `Err(FrequencyControllerError)` if validation fails
    ///
    /// # Requirements
    /// - 2.1: Monitor current CPU frequency
    /// - 2.2: Calculate appropriate voltage offset from frequency curve
    pub fn load_curve(&mut self, curve: FrequencyCurve) -> Result<(), FrequencyControllerError> {
        // Validate curve before loading
        curve.validate()
            .map_err(|e| FrequencyControllerError::InvalidCurve(e))?;
        
        let core_id = curve.core_id;
        self.curves.insert(core_id, curve);
        
        // Clear cached values for this core
        self.last_voltages.remove(&core_id);
        self.frequency_cache.remove(&core_id);
        
        Ok(())
    }
    
    /// Remove curve for a specific core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    pub fn remove_curve(&mut self, core_id: usize) {
        self.curves.remove(&core_id);
        self.last_voltages.remove(&core_id);
        self.frequency_cache.remove(&core_id);
    }
    
    /// Check if a curve is loaded for a core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// `true` if curve is loaded, `false` otherwise
    pub fn has_curve(&self, core_id: usize) -> bool {
        self.curves.contains_key(&core_id)
    }
    
    /// Get the curve for a specific core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Some(&FrequencyCurve)` if curve exists
    /// * `None` if no curve loaded
    pub fn get_curve(&self, core_id: usize) -> Option<&FrequencyCurve> {
        self.curves.get(&core_id)
    }
    
    /// Read current frequency for a core from sysfs
    ///
    /// Uses caching to reduce sysfs access overhead. Cached values are valid
    /// for cache_ttl_ms milliseconds.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(u32)` - Frequency in MHz
    /// * `Err(FrequencyControllerError)` if read fails
    ///
    /// # Requirements
    /// - 2.1: Monitor current CPU frequency at intervals of 10-50 milliseconds
    /// - 12.3: Cache frequency reading for 10 milliseconds to reduce sysfs access
    pub fn read_current_frequency(&mut self, core_id: usize) -> Result<u32, FrequencyControllerError> {
        // Check cache first
        if let Some(cached) = self.frequency_cache.get(&core_id) {
            let age = cached.timestamp.elapsed();
            if age < Duration::from_millis(self.cache_ttl_ms) {
                return Ok(cached.frequency);
            }
        }
        
        // Cache miss or expired, read from sysfs
        let freq_path = self.sysfs_base
            .join(format!("cpu{}", core_id))
            .join("cpufreq")
            .join("scaling_cur_freq");
        
        let content = fs::read_to_string(&freq_path)?;
        let freq_khz: u32 = content
            .trim()
            .parse()
            .map_err(|_| {
                FrequencyControllerError::ParseError(
                    format!("Invalid frequency value: {}", content.trim())
                )
            })?;
        
        // Convert kHz to MHz
        let freq_mhz = freq_khz / 1000;
        
        // Update cache
        self.frequency_cache.insert(core_id, FrequencyCache {
            frequency: freq_mhz,
            timestamp: Instant::now(),
        });
        
        Ok(freq_mhz)
    }
    
    /// Calculate voltage for a core based on current frequency
    ///
    /// Reads the current frequency and interpolates the voltage from the curve.
    /// Returns None if voltage hasn't changed since last call (to avoid redundant applications).
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(Some(i32))` - New voltage to apply (in mV)
    /// * `Ok(None)` - Voltage unchanged, no need to apply
    /// * `Err(FrequencyControllerError)` if error occurs
    ///
    /// # Requirements
    /// - 2.2: Calculate appropriate voltage offset from frequency curve using linear interpolation
    /// - 2.3: Apply offset through ryzenadj within 50 milliseconds
    pub fn calculate_voltage_for_current_frequency(
        &mut self,
        core_id: usize,
    ) -> Result<Option<i32>, FrequencyControllerError> {
        // Check if curve is loaded
        if !self.curves.contains_key(&core_id) {
            return Err(FrequencyControllerError::NoCurveLoaded(core_id));
        }
        
        // Read current frequency
        let freq_mhz = self.read_current_frequency(core_id)?;
        
        // Calculate voltage from curve (now we can borrow curve after mutable borrow is done)
        let curve = self.curves.get(&core_id).unwrap(); // Safe because we checked above
        let voltage = curve.get_voltage_at_frequency(freq_mhz)
            .map_err(|e| FrequencyControllerError::InvalidCurve(e))?;
        
        // Check if voltage has changed
        if let Some(&last_voltage) = self.last_voltages.get(&core_id) {
            if last_voltage == voltage {
                return Ok(None); // No change, skip application
            }
        }
        
        // Update last voltage
        self.last_voltages.insert(core_id, voltage);
        
        Ok(Some(voltage))
    }
    
    /// Get the last applied voltage for a core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Some(i32)` - Last applied voltage in mV
    /// * `None` if no voltage has been applied yet
    pub fn get_last_voltage(&self, core_id: usize) -> Option<i32> {
        self.last_voltages.get(&core_id).copied()
    }
    
    /// Clear all cached data
    ///
    /// Clears frequency cache and last voltage tracking.
    /// Useful when resetting the controller state.
    pub fn clear_cache(&mut self) {
        self.frequency_cache.clear();
        self.last_voltages.clear();
    }
    
    /// Get all loaded core IDs
    ///
    /// # Returns
    /// Vector of core IDs that have curves loaded
    pub fn get_loaded_cores(&self) -> Vec<usize> {
        let mut cores: Vec<usize> = self.curves.keys().copied().collect();
        cores.sort_unstable();
        cores
    }
}

impl Default for FrequencyVoltageController {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::dynamic::frequency_curve::FrequencyPoint;
    use std::fs;
    use tempfile::TempDir;
    
    fn create_test_curve(core_id: usize) -> FrequencyCurve {
        let points = vec![
            FrequencyPoint::new(400, -50, true, 30, 1706198430.0),
            FrequencyPoint::new(800, -40, true, 30, 1706198460.0),
            FrequencyPoint::new(1200, -30, true, 30, 1706198490.0),
            FrequencyPoint::new(1600, -20, true, 30, 1706198520.0),
        ];
        
        FrequencyCurve::new(
            core_id,
            points,
            1706198400.0,
            serde_json::json!({"freq_step": 400}),
        )
    }
    
    fn create_mock_sysfs(temp_dir: &TempDir, num_cores: usize) -> PathBuf {
        let sysfs_base = temp_dir.path().join("sys/devices/system/cpu");
        
        for i in 0..num_cores {
            let cpu_dir = sysfs_base.join(format!("cpu{}", i)).join("cpufreq");
            fs::create_dir_all(&cpu_dir).unwrap();
            
            // Create mock frequency file (in kHz)
            fs::write(cpu_dir.join("scaling_cur_freq"), "1200000").unwrap(); // 1200 MHz
        }
        
        sysfs_base
    }
    
    #[test]
    fn test_controller_new() {
        let controller = FrequencyVoltageController::new();
        assert_eq!(controller.curves.len(), 0);
        assert_eq!(controller.cache_ttl_ms, 10);
    }
    
    #[test]
    fn test_load_curve() {
        let mut controller = FrequencyVoltageController::new();
        let curve = create_test_curve(0);
        
        let result = controller.load_curve(curve);
        assert!(result.is_ok());
        assert!(controller.has_curve(0));
    }
    
    #[test]
    fn test_load_invalid_curve() {
        let mut controller = FrequencyVoltageController::new();
        
        // Create invalid curve (voltage out of range)
        let points = vec![
            FrequencyPoint::new(400, -150, true, 30, 0.0), // Invalid voltage
        ];
        let curve = FrequencyCurve::new(0, points, 0.0, serde_json::json!({}));
        
        let result = controller.load_curve(curve);
        assert!(result.is_err());
        match result {
            Err(FrequencyControllerError::InvalidCurve(_)) => {},
            _ => panic!("Expected InvalidCurve error"),
        }
    }
    
    #[test]
    fn test_remove_curve() {
        let mut controller = FrequencyVoltageController::new();
        let curve = create_test_curve(0);
        
        controller.load_curve(curve).unwrap();
        assert!(controller.has_curve(0));
        
        controller.remove_curve(0);
        assert!(!controller.has_curve(0));
    }
    
    #[test]
    fn test_get_curve() {
        let mut controller = FrequencyVoltageController::new();
        let curve = create_test_curve(0);
        
        controller.load_curve(curve.clone()).unwrap();
        
        let retrieved = controller.get_curve(0);
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().core_id, 0);
    }
    
    #[test]
    fn test_read_current_frequency() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        
        let freq = controller.read_current_frequency(0);
        assert!(freq.is_ok());
        assert_eq!(freq.unwrap(), 1200); // 1200 MHz
    }
    
    #[test]
    fn test_read_current_frequency_caching() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base.clone());
        
        // First read should hit sysfs
        let freq1 = controller.read_current_frequency(0).unwrap();
        assert_eq!(freq1, 1200);
        
        // Update the file
        let freq_path = sysfs_base.join("cpu0/cpufreq/scaling_cur_freq");
        fs::write(&freq_path, "1600000").unwrap(); // Change to 1600 MHz
        
        // Second read within cache TTL should return cached value
        let freq2 = controller.read_current_frequency(0).unwrap();
        assert_eq!(freq2, 1200); // Still cached value
        
        // Wait for cache to expire
        std::thread::sleep(Duration::from_millis(15));
        
        // Third read should hit sysfs again
        let freq3 = controller.read_current_frequency(0).unwrap();
        assert_eq!(freq3, 1600); // New value
    }
    
    #[test]
    fn test_calculate_voltage_for_current_frequency() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // Calculate voltage for 1200 MHz (should be -30 mV from curve)
        let voltage = controller.calculate_voltage_for_current_frequency(0);
        assert!(voltage.is_ok());
        assert_eq!(voltage.unwrap(), Some(-30));
    }
    
    #[test]
    fn test_calculate_voltage_no_change() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // First calculation
        let voltage1 = controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert_eq!(voltage1, Some(-30));
        
        // Second calculation (frequency unchanged, should return None)
        let voltage2 = controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert_eq!(voltage2, None);
    }
    
    #[test]
    fn test_calculate_voltage_no_curve() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        
        // Try to calculate without loading curve
        let result = controller.calculate_voltage_for_current_frequency(0);
        assert!(result.is_err());
        match result {
            Err(FrequencyControllerError::NoCurveLoaded(id)) => assert_eq!(id, 0),
            _ => panic!("Expected NoCurveLoaded error"),
        }
    }
    
    #[test]
    fn test_get_last_voltage() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // No voltage applied yet
        assert_eq!(controller.get_last_voltage(0), None);
        
        // Calculate voltage
        controller.calculate_voltage_for_current_frequency(0).unwrap();
        
        // Should have last voltage now
        assert_eq!(controller.get_last_voltage(0), Some(-30));
    }
    
    #[test]
    fn test_clear_cache() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // Calculate voltage to populate cache
        controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert!(controller.get_last_voltage(0).is_some());
        
        // Clear cache
        controller.clear_cache();
        assert_eq!(controller.get_last_voltage(0), None);
    }
    
    #[test]
    fn test_get_loaded_cores() {
        let mut controller = FrequencyVoltageController::new();
        
        controller.load_curve(create_test_curve(0)).unwrap();
        controller.load_curve(create_test_curve(2)).unwrap();
        controller.load_curve(create_test_curve(1)).unwrap();
        
        let cores = controller.get_loaded_cores();
        assert_eq!(cores, vec![0, 1, 2]); // Should be sorted
    }
    
    #[test]
    fn test_interpolation_between_points() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        // Set frequency to 600 MHz (between 400 and 800)
        let freq_path = sysfs_base.join("cpu0/cpufreq/scaling_cur_freq");
        fs::write(&freq_path, "600000").unwrap();
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // Calculate voltage for 600 MHz
        // Should interpolate between 400 MHz (-50 mV) and 800 MHz (-40 mV)
        // At 600 MHz (halfway), should be -45 mV
        let voltage = controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert_eq!(voltage, Some(-45));
    }
    
    #[test]
    fn test_boundary_clamping_below() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        // Set frequency below minimum (200 MHz < 400 MHz)
        let freq_path = sysfs_base.join("cpu0/cpufreq/scaling_cur_freq");
        fs::write(&freq_path, "200000").unwrap();
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // Should clamp to minimum voltage (-50 mV)
        let voltage = controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert_eq!(voltage, Some(-50));
    }
    
    #[test]
    fn test_boundary_clamping_above() {
        let temp_dir = TempDir::new().unwrap();
        let sysfs_base = create_mock_sysfs(&temp_dir, 4);
        
        // Set frequency above maximum (2000 MHz > 1600 MHz)
        let freq_path = sysfs_base.join("cpu0/cpufreq/scaling_cur_freq");
        fs::write(&freq_path, "2000000").unwrap();
        
        let mut controller = FrequencyVoltageController::with_sysfs_base(sysfs_base);
        let curve = create_test_curve(0);
        controller.load_curve(curve).unwrap();
        
        // Should clamp to maximum voltage (-20 mV)
        let voltage = controller.calculate_voltage_for_current_frequency(0).unwrap();
        assert_eq!(voltage, Some(-20));
    }
    
    #[test]
    fn test_error_display() {
        let err = FrequencyControllerError::InvalidCoreId(5);
        assert!(err.to_string().contains("5"));
        
        let err = FrequencyControllerError::NoCurveLoaded(3);
        assert!(err.to_string().contains("3"));
        
        let err = FrequencyControllerError::ParseError("test error".to_string());
        assert!(err.to_string().contains("test error"));
        
        let err = FrequencyControllerError::InvalidCurve("invalid".to_string());
        assert!(err.to_string().contains("invalid"));
    }
}
