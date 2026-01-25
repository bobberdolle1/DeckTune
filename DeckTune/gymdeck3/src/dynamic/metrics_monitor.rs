//! Metrics monitor for per-core CPU metrics
//!
//! Provides real-time monitoring of CPU load, voltage, frequency, and temperature
//! for individual cores.
//!
//! Requirements: 5.5, 9.5

use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

/// Metrics for a single CPU core
#[derive(Debug, Clone, PartialEq)]
pub struct CoreMetrics {
    /// Core ID (0-based index)
    pub core_id: usize,
    /// CPU load percentage (0.0-100.0)
    pub load: f32,
    /// Current voltage offset in mV
    pub voltage: i32,
    /// Current frequency in MHz
    pub frequency: u32,
    /// Current temperature in Celsius
    pub temperature: f32,
    /// Unix timestamp in milliseconds
    pub timestamp: u64,
}

/// Errors from metrics monitor operations
#[derive(Debug)]
pub enum MetricsError {
    /// Invalid core ID
    InvalidCoreId(usize),
    /// I/O error reading from sysfs
    IoError(std::io::Error),
    /// Parse error reading sysfs values
    ParseError(String),
    /// Required sysfs file not found
    FileNotFound(String),
}

impl std::fmt::Display for MetricsError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MetricsError::InvalidCoreId(id) => {
                write!(f, "Invalid core ID: {}", id)
            }
            MetricsError::IoError(e) => {
                write!(f, "I/O error: {}", e)
            }
            MetricsError::ParseError(msg) => {
                write!(f, "Parse error: {}", msg)
            }
            MetricsError::FileNotFound(path) => {
                write!(f, "File not found: {}", path)
            }
        }
    }
}

impl std::error::Error for MetricsError {}

impl From<std::io::Error> for MetricsError {
    fn from(e: std::io::Error) -> Self {
        MetricsError::IoError(e)
    }
}

/// Metrics monitor for CPU cores
///
/// Polls CPU metrics from sysfs and /proc interfaces.
pub struct MetricsMonitor {
    /// Number of CPU cores
    num_cores: usize,
    /// Base path for CPU sysfs (for testing)
    sysfs_base: PathBuf,
    /// Path to /proc/stat (for testing)
    proc_stat_path: PathBuf,
    /// Path to hwmon for temperature (for testing)
    hwmon_path: PathBuf,
    /// Previous CPU stats for load calculation
    prev_stats: Vec<CpuTimeStats>,
}

/// CPU time statistics for load calculation
#[derive(Debug, Clone, Default)]
struct CpuTimeStats {
    total: u64,
    idle: u64,
}

impl MetricsMonitor {
    /// Create a new MetricsMonitor
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores to monitor
    pub fn new(num_cores: usize) -> Self {
        Self {
            num_cores,
            sysfs_base: PathBuf::from("/sys/devices/system/cpu"),
            proc_stat_path: PathBuf::from("/proc/stat"),
            hwmon_path: PathBuf::from("/sys/class/hwmon"),
            prev_stats: vec![CpuTimeStats::default(); num_cores],
        }
    }
    
    /// Create a MetricsMonitor with custom paths (for testing)
    ///
    /// # Arguments
    /// * `num_cores` - Number of CPU cores
    /// * `sysfs_base` - Base path for CPU sysfs
    /// * `proc_stat_path` - Path to /proc/stat
    /// * `hwmon_path` - Path to hwmon directory
    pub fn with_paths(
        num_cores: usize,
        sysfs_base: PathBuf,
        proc_stat_path: PathBuf,
        hwmon_path: PathBuf,
    ) -> Self {
        Self {
            num_cores,
            sysfs_base,
            proc_stat_path,
            hwmon_path,
            prev_stats: vec![CpuTimeStats::default(); num_cores],
        }
    }
    
    /// Get metrics for a specific core
    ///
    /// # Arguments
    /// * `core_id` - Core identifier (0-based)
    ///
    /// # Returns
    /// * `Ok(CoreMetrics)` if successful
    /// * `Err(MetricsError)` if error occurs
    pub fn get_core_metrics(&mut self, core_id: usize) -> Result<CoreMetrics, MetricsError> {
        if core_id >= self.num_cores {
            return Err(MetricsError::InvalidCoreId(core_id));
        }
        
        let load = self.get_cpu_load(core_id)?;
        let voltage = self.get_voltage(core_id)?;
        let frequency = self.get_frequency(core_id)?;
        let temperature = self.get_temperature(core_id)?;
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        
        Ok(CoreMetrics {
            core_id,
            load,
            voltage,
            frequency,
            temperature,
            timestamp,
        })
    }
    
    /// Get CPU load for a specific core
    ///
    /// Reads from /proc/stat and calculates load percentage based on
    /// the difference from the previous sample.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(f32)` - Load percentage (0.0-100.0)
    /// * `Err(MetricsError)` if error occurs
    pub fn get_cpu_load(&mut self, core_id: usize) -> Result<f32, MetricsError> {
        if core_id >= self.num_cores {
            return Err(MetricsError::InvalidCoreId(core_id));
        }
        
        // Read /proc/stat
        let content = fs::read_to_string(&self.proc_stat_path)?;
        
        // Find the line for this core (cpu0, cpu1, etc.)
        let cpu_line = format!("cpu{} ", core_id);
        let line = content
            .lines()
            .find(|l| l.starts_with(&cpu_line))
            .ok_or_else(|| {
                MetricsError::ParseError(format!("Core {} not found in /proc/stat", core_id))
            })?;
        
        // Parse CPU time values
        // Format: cpu0 user nice system idle iowait irq softirq steal guest guest_nice
        let values: Vec<u64> = line
            .split_whitespace()
            .skip(1) // Skip "cpu0"
            .filter_map(|s| s.parse().ok())
            .collect();
        
        if values.len() < 4 {
            return Err(MetricsError::ParseError(format!(
                "Invalid /proc/stat format for core {}",
                core_id
            )));
        }
        
        // Calculate total and idle time
        let total: u64 = values.iter().sum();
        let idle = values[3]; // idle is the 4th field
        
        // Calculate load percentage
        let prev = &self.prev_stats[core_id];
        let load = if prev.total > 0 {
            let total_delta = total.saturating_sub(prev.total);
            let idle_delta = idle.saturating_sub(prev.idle);
            
            if total_delta > 0 {
                let active_delta = total_delta.saturating_sub(idle_delta);
                (active_delta as f32 / total_delta as f32) * 100.0
            } else {
                0.0
            }
        } else {
            0.0 // First sample, no previous data
        };
        
        // Update previous stats
        self.prev_stats[core_id] = CpuTimeStats { total, idle };
        
        Ok(load.max(0.0).min(100.0))
    }
    
    /// Get current voltage offset for a core
    ///
    /// Reads from sysfs voltage interface.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(i32)` - Voltage offset in mV
    /// * `Err(MetricsError)` if error occurs
    pub fn get_voltage(&self, core_id: usize) -> Result<i32, MetricsError> {
        if core_id >= self.num_cores {
            return Err(MetricsError::InvalidCoreId(core_id));
        }
        
        // Try to read voltage from sysfs
        // Path: /sys/devices/system/cpu/cpu{N}/cpufreq/voltage_offset
        let voltage_path = self.sysfs_base
            .join(format!("cpu{}", core_id))
            .join("cpufreq")
            .join("voltage_offset");
        
        if voltage_path.exists() {
            let content = fs::read_to_string(&voltage_path)?;
            content
                .trim()
                .parse()
                .map_err(|_| {
                    MetricsError::ParseError(format!("Invalid voltage value: {}", content.trim()))
                })
        } else {
            // If voltage file doesn't exist, return 0 (no offset)
            Ok(0)
        }
    }
    
    /// Get current frequency for a core
    ///
    /// Reads from sysfs cpufreq interface.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(u32)` - Frequency in MHz
    /// * `Err(MetricsError)` if error occurs
    pub fn get_frequency(&self, core_id: usize) -> Result<u32, MetricsError> {
        if core_id >= self.num_cores {
            return Err(MetricsError::InvalidCoreId(core_id));
        }
        
        // Read current frequency from sysfs
        // Path: /sys/devices/system/cpu/cpu{N}/cpufreq/scaling_cur_freq
        let freq_path = self.sysfs_base
            .join(format!("cpu{}", core_id))
            .join("cpufreq")
            .join("scaling_cur_freq");
        
        if freq_path.exists() {
            let content = fs::read_to_string(&freq_path)?;
            let freq_khz: u32 = content
                .trim()
                .parse()
                .map_err(|_| {
                    MetricsError::ParseError(format!("Invalid frequency value: {}", content.trim()))
                })?;
            
            // Convert kHz to MHz
            Ok(freq_khz / 1000)
        } else {
            // If frequency file doesn't exist, return 0
            Ok(0)
        }
    }
    
    /// Get current temperature for a core
    ///
    /// Reads from hwmon interface. Note: On many systems, temperature is
    /// per-package rather than per-core.
    ///
    /// # Arguments
    /// * `core_id` - Core identifier
    ///
    /// # Returns
    /// * `Ok(f32)` - Temperature in Celsius
    /// * `Err(MetricsError)` if error occurs
    pub fn get_temperature(&self, core_id: usize) -> Result<f32, MetricsError> {
        if core_id >= self.num_cores {
            return Err(MetricsError::InvalidCoreId(core_id));
        }
        
        // Try to read temperature from hwmon
        // First, try per-core temperature: temp{N+2}_input (temp1 is usually package)
        let temp_index = core_id + 2;
        let temp_path = self.hwmon_path
            .join("hwmon0")
            .join(format!("temp{}_input", temp_index));
        
        if temp_path.exists() {
            let content = fs::read_to_string(&temp_path)?;
            let temp_millidegrees: i32 = content
                .trim()
                .parse()
                .map_err(|_| {
                    MetricsError::ParseError(format!("Invalid temperature value: {}", content.trim()))
                })?;
            
            // Convert millidegrees to degrees
            Ok(temp_millidegrees as f32 / 1000.0)
        } else {
            // Fall back to package temperature (temp1_input)
            let package_temp_path = self.hwmon_path
                .join("hwmon0")
                .join("temp1_input");
            
            if package_temp_path.exists() {
                let content = fs::read_to_string(&package_temp_path)?;
                let temp_millidegrees: i32 = content
                    .trim()
                    .parse()
                    .map_err(|_| {
                        MetricsError::ParseError(format!(
                            "Invalid temperature value: {}",
                            content.trim()
                        ))
                    })?;
                
                Ok(temp_millidegrees as f32 / 1000.0)
            } else {
                // If no temperature available, return 0
                Ok(0.0)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;
    
    fn create_mock_sysfs(temp_dir: &TempDir, num_cores: usize) -> (PathBuf, PathBuf, PathBuf) {
        let sysfs_base = temp_dir.path().join("sys/devices/system/cpu");
        let proc_stat_path = temp_dir.path().join("proc/stat");
        let hwmon_path = temp_dir.path().join("sys/class/hwmon");
        
        // Create CPU directories
        for i in 0..num_cores {
            let cpu_dir = sysfs_base.join(format!("cpu{}", i)).join("cpufreq");
            fs::create_dir_all(&cpu_dir).unwrap();
            
            // Create mock files
            fs::write(cpu_dir.join("scaling_cur_freq"), "2800000").unwrap(); // 2800 MHz
            fs::write(cpu_dir.join("voltage_offset"), "-25").unwrap();
        }
        
        // Create hwmon directory
        let hwmon0 = hwmon_path.join("hwmon0");
        fs::create_dir_all(&hwmon0).unwrap();
        fs::write(hwmon0.join("temp1_input"), "45000").unwrap(); // 45°C
        
        // Create /proc/stat
        fs::create_dir_all(proc_stat_path.parent().unwrap()).unwrap();
        let mut stat_content = String::from("cpu  100 0 50 850 0 0 0 0 0 0\n");
        for i in 0..num_cores {
            stat_content.push_str(&format!("cpu{} 100 0 50 850 0 0 0 0 0 0\n", i));
        }
        fs::write(&proc_stat_path, stat_content).unwrap();
        
        (sysfs_base, proc_stat_path, hwmon_path)
    }
    
    #[test]
    fn test_metrics_monitor_new() {
        let monitor = MetricsMonitor::new(4);
        assert_eq!(monitor.num_cores, 4);
    }
    
    #[test]
    fn test_get_frequency() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path, hwmon_path);
        
        let freq = monitor.get_frequency(0);
        assert!(freq.is_ok());
        assert_eq!(freq.unwrap(), 2800); // 2800 MHz
    }
    
    #[test]
    fn test_get_voltage() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path, hwmon_path);
        
        let voltage = monitor.get_voltage(0);
        assert!(voltage.is_ok());
        assert_eq!(voltage.unwrap(), -25);
    }
    
    #[test]
    fn test_get_temperature() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path, hwmon_path);
        
        let temp = monitor.get_temperature(0);
        assert!(temp.is_ok());
        assert_eq!(temp.unwrap(), 45.0);
    }
    
    #[test]
    fn test_get_cpu_load() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let mut monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path.clone(), hwmon_path);
        
        // First call should return 0 (no previous data)
        let load = monitor.get_cpu_load(0);
        assert!(load.is_ok());
        assert_eq!(load.unwrap(), 0.0);
        
        // Update /proc/stat with new values
        let mut stat_content = String::from("cpu  200 0 100 1700 0 0 0 0 0 0\n");
        for i in 0..4 {
            stat_content.push_str(&format!("cpu{} 200 0 100 1700 0 0 0 0 0 0\n", i));
        }
        fs::write(&proc_stat_path, stat_content).unwrap();
        
        // Second call should calculate load
        let load = monitor.get_cpu_load(0);
        assert!(load.is_ok());
        let load_val = load.unwrap();
        assert!(load_val >= 0.0 && load_val <= 100.0);
    }
    
    #[test]
    fn test_get_core_metrics() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let mut monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path, hwmon_path);
        
        let metrics = monitor.get_core_metrics(0);
        assert!(metrics.is_ok());
        
        let metrics = metrics.unwrap();
        assert_eq!(metrics.core_id, 0);
        assert!(metrics.load >= 0.0 && metrics.load <= 100.0);
        assert_eq!(metrics.voltage, -25);
        assert_eq!(metrics.frequency, 2800);
        assert_eq!(metrics.temperature, 45.0);
        assert!(metrics.timestamp > 0);
    }
    
    #[test]
    fn test_get_core_metrics_invalid_id() {
        let temp_dir = TempDir::new().unwrap();
        let (sysfs_base, proc_stat_path, hwmon_path) = create_mock_sysfs(&temp_dir, 4);
        
        let mut monitor = MetricsMonitor::with_paths(4, sysfs_base, proc_stat_path, hwmon_path);
        
        let metrics = monitor.get_core_metrics(10);
        assert!(metrics.is_err());
        match metrics {
            Err(MetricsError::InvalidCoreId(id)) => assert_eq!(id, 10),
            _ => panic!("Expected InvalidCoreId error"),
        }
    }
    
    #[test]
    fn test_metrics_error_display() {
        let err = MetricsError::InvalidCoreId(5);
        assert!(err.to_string().contains("5"));
        
        let err = MetricsError::ParseError("test error".to_string());
        assert!(err.to_string().contains("test error"));
        
        let err = MetricsError::FileNotFound("/path/to/file".to_string());
        assert!(err.to_string().contains("/path/to/file"));
    }
}
