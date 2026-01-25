//! CPU load monitoring from /proc/stat
//!
//! Provides zero-copy parsing of CPU statistics and calculation of
//! per-core and average utilization percentages.

use std::fs;
use std::io;
use std::time::{Duration, Instant};

/// Statistics for a single CPU core (or total)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct CoreStats {
    pub user: u64,
    pub nice: u64,
    pub system: u64,
    pub idle: u64,
    pub iowait: u64,
    pub irq: u64,
    pub softirq: u64,
    pub steal: u64,
}

impl CoreStats {
    /// Total CPU time (all fields combined)
    pub fn total(&self) -> u64 {
        self.user + self.nice + self.system + self.idle + self.iowait + self.irq + self.softirq + self.steal
    }

    /// Active (non-idle) CPU time
    pub fn active(&self) -> u64 {
        self.user + self.nice + self.system + self.irq + self.softirq + self.steal
    }

    /// Idle CPU time (idle + iowait)
    pub fn idle_time(&self) -> u64 {
        self.idle + self.iowait
    }
}

/// Snapshot of CPU statistics at a point in time
#[derive(Debug, Clone)]
pub struct CpuStats {
    pub total: CoreStats,
    pub per_core: Vec<CoreStats>,
    pub timestamp: Instant,
}

/// Result of a load sample calculation
#[derive(Debug, Clone)]
pub struct LoadSample {
    /// Average load across all cores (0.0 - 100.0)
    pub average: f32,
    /// Per-core load percentages (0.0 - 100.0 each)
    pub per_core: Vec<f32>,
    /// Timestamp in milliseconds since monitor start
    pub timestamp_ms: u64,
}

/// Error types for LoadMonitor operations
#[derive(Debug)]
pub enum LoadMonitorError {
    IoError(io::Error),
    ParseError(String),
    NoPreviousSample,
    InvalidSampleInterval(String),
}

impl std::fmt::Display for LoadMonitorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LoadMonitorError::IoError(e) => write!(f, "I/O error: {}", e),
            LoadMonitorError::ParseError(s) => write!(f, "Parse error: {}", s),
            LoadMonitorError::NoPreviousSample => write!(f, "No previous sample available"),
            LoadMonitorError::InvalidSampleInterval(s) => write!(f, "Invalid sample interval: {}", s),
        }
    }
}

impl std::error::Error for LoadMonitorError {}

impl From<io::Error> for LoadMonitorError {
    fn from(e: io::Error) -> Self {
        LoadMonitorError::IoError(e)
    }
}

/// Validate sample interval is within the allowed range (10-5000ms)
///
/// # Arguments
/// * `interval_ms` - Sample interval in milliseconds
///
/// # Returns
/// * `Ok(interval_ms)` if valid
/// * `Err(LoadMonitorError::InvalidSampleInterval)` if outside range [10, 5000]
pub fn validate_sample_interval_ms(interval_ms: u64) -> Result<u64, LoadMonitorError> {
    if interval_ms < MIN_SAMPLE_INTERVAL_MS {
        return Err(LoadMonitorError::InvalidSampleInterval(format!(
            "{} ms is too small (minimum: {} ms)",
            interval_ms, MIN_SAMPLE_INTERVAL_MS
        )));
    }
    if interval_ms > MAX_SAMPLE_INTERVAL_MS {
        return Err(LoadMonitorError::InvalidSampleInterval(format!(
            "{} ms is too large (maximum: {} ms)",
            interval_ms, MAX_SAMPLE_INTERVAL_MS
        )));
    }
    Ok(interval_ms)
}

/// CPU load monitor that reads from /proc/stat
pub struct LoadMonitor {
    prev_stats: Option<CpuStats>,
    sample_interval: Duration,
    start_time: Instant,
    proc_stat_path: String,
}


/// Minimum sample interval in milliseconds
pub const MIN_SAMPLE_INTERVAL_MS: u64 = 10;
/// Maximum sample interval in milliseconds
pub const MAX_SAMPLE_INTERVAL_MS: u64 = 5000;

impl LoadMonitor {
    /// Create a new LoadMonitor with the specified sample interval
    ///
    /// # Arguments
    /// * `sample_interval_ms` - Sample interval in milliseconds (10-5000)
    ///
    /// # Errors
    /// Returns error if sample_interval_ms is outside the valid range [10, 5000]
    pub fn new(sample_interval_ms: u64) -> Result<Self, LoadMonitorError> {
        Self::with_path(sample_interval_ms, "/proc/stat".to_string())
    }

    /// Create a new LoadMonitor with a custom /proc/stat path (for testing)
    ///
    /// # Arguments
    /// * `sample_interval_ms` - Sample interval in milliseconds (10-5000)
    /// * `proc_stat_path` - Path to the proc stat file (usually "/proc/stat")
    ///
    /// # Errors
    /// Returns error if sample_interval_ms is outside the valid range [10, 5000]
    pub fn with_path(sample_interval_ms: u64, proc_stat_path: String) -> Result<Self, LoadMonitorError> {
        validate_sample_interval_ms(sample_interval_ms)?;
        
        Ok(Self {
            prev_stats: None,
            sample_interval: Duration::from_millis(sample_interval_ms),
            start_time: Instant::now(),
            proc_stat_path,
        })
    }

    /// Get the configured sample interval
    pub fn sample_interval(&self) -> Duration {
        self.sample_interval
    }

    /// Read and parse current CPU statistics from /proc/stat
    fn read_stats(&self) -> Result<CpuStats, LoadMonitorError> {
        let content = fs::read_to_string(&self.proc_stat_path)?;
        Self::parse_proc_stat(&content)
    }

    /// Parse /proc/stat content into CpuStats
    ///
    /// Zero-copy parsing: we iterate over lines without allocating intermediate strings
    pub fn parse_proc_stat(content: &str) -> Result<CpuStats, LoadMonitorError> {
        let mut total: Option<CoreStats> = None;
        let mut per_core: Vec<CoreStats> = Vec::new();

        for line in content.lines() {
            if line.starts_with("cpu") {
                let stats = Self::parse_cpu_line(line)?;
                if line.starts_with("cpu ") {
                    // Total CPU line (note the space after "cpu")
                    total = Some(stats);
                } else if line.chars().nth(3).map_or(false, |c| c.is_ascii_digit()) {
                    // Per-core line (cpu0, cpu1, etc.)
                    per_core.push(stats);
                }
            }
        }

        let total = total.ok_or_else(|| {
            LoadMonitorError::ParseError("Missing total CPU line in /proc/stat".to_string())
        })?;

        Ok(CpuStats {
            total,
            per_core,
            timestamp: Instant::now(),
        })
    }

    /// Parse a single CPU line from /proc/stat
    ///
    /// Format: cpu[N] user nice system idle iowait irq softirq steal [guest] [guest_nice]
    fn parse_cpu_line(line: &str) -> Result<CoreStats, LoadMonitorError> {
        let mut parts = line.split_whitespace();
        
        // Skip the "cpu" or "cpuN" label
        parts.next();

        let parse_field = |parts: &mut std::str::SplitWhitespace, name: &str| -> Result<u64, LoadMonitorError> {
            parts
                .next()
                .ok_or_else(|| LoadMonitorError::ParseError(format!("Missing {} field", name)))?
                .parse()
                .map_err(|_| LoadMonitorError::ParseError(format!("Invalid {} value", name)))
        };

        let user = parse_field(&mut parts, "user")?;
        let nice = parse_field(&mut parts, "nice")?;
        let system = parse_field(&mut parts, "system")?;
        let idle = parse_field(&mut parts, "idle")?;
        let iowait = parse_field(&mut parts, "iowait").unwrap_or(0);
        let irq = parse_field(&mut parts, "irq").unwrap_or(0);
        let softirq = parse_field(&mut parts, "softirq").unwrap_or(0);
        let steal = parse_field(&mut parts, "steal").unwrap_or(0);

        Ok(CoreStats {
            user,
            nice,
            system,
            idle,
            iowait,
            irq,
            softirq,
            steal,
        })
    }

    /// Take a sample and calculate CPU load since last sample
    ///
    /// Returns LoadSample with per-core and average utilization percentages.
    /// First call will store stats and return an error (no previous sample).
    pub fn sample(&mut self) -> Result<LoadSample, LoadMonitorError> {
        let current = self.read_stats()?;
        
        let result = match &self.prev_stats {
            Some(prev) => {
                let sample = Self::calculate_load(prev, &current, self.start_time);
                Ok(sample)
            }
            None => Err(LoadMonitorError::NoPreviousSample),
        };

        self.prev_stats = Some(current);
        result
    }

    /// Calculate load percentages from two consecutive stat snapshots
    pub fn calculate_load(prev: &CpuStats, current: &CpuStats, start_time: Instant) -> LoadSample {
        let per_core: Vec<f32> = prev
            .per_core
            .iter()
            .zip(current.per_core.iter())
            .map(|(p, c)| Self::calculate_core_load(p, c))
            .collect();

        let average = if per_core.is_empty() {
            Self::calculate_core_load(&prev.total, &current.total)
        } else {
            per_core.iter().sum::<f32>() / per_core.len() as f32
        };

        LoadSample {
            average,
            per_core,
            timestamp_ms: start_time.elapsed().as_millis() as u64,
        }
    }

    /// Calculate load percentage for a single core between two samples
    fn calculate_core_load(prev: &CoreStats, current: &CoreStats) -> f32 {
        let total_delta = current.total().saturating_sub(prev.total());
        let idle_delta = current.idle_time().saturating_sub(prev.idle_time());

        if total_delta == 0 {
            return 0.0;
        }

        let active_delta = total_delta.saturating_sub(idle_delta);
        let load = (active_delta as f64 / total_delta as f64) * 100.0;
        
        // Clamp to valid range
        load.clamp(0.0, 100.0) as f32
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE_PROC_STAT: &str = r#"cpu  10132153 290696 3084719 46828483 16683 0 25195 0 0 0
cpu0 1393280 32966 572056 13343292 6130 0 17875 0 0 0
cpu1 1335535 34218 506820 13496949 3908 0 3556 0 0 0
cpu2 1339767 33239 502039 13496407 3742 0 1829 0 0 0
cpu3 1340270 33232 502039 13496407 3742 0 1829 0 0 0
intr 620315706 0 0 0 0 0 0 0 0 1 79 0 0 156 0 0 0
"#;

    #[test]
    fn test_parse_proc_stat() {
        let stats = LoadMonitor::parse_proc_stat(SAMPLE_PROC_STAT).unwrap();
        
        assert_eq!(stats.per_core.len(), 4);
        assert_eq!(stats.total.user, 10132153);
        assert_eq!(stats.total.nice, 290696);
        assert_eq!(stats.total.system, 3084719);
        assert_eq!(stats.total.idle, 46828483);
    }

    #[test]
    fn test_parse_cpu_line() {
        let line = "cpu0 1393280 32966 572056 13343292 6130 0 17875 0 0 0";
        let stats = LoadMonitor::parse_cpu_line(line).unwrap();
        
        assert_eq!(stats.user, 1393280);
        assert_eq!(stats.nice, 32966);
        assert_eq!(stats.system, 572056);
        assert_eq!(stats.idle, 13343292);
        assert_eq!(stats.iowait, 6130);
        assert_eq!(stats.irq, 0);
        assert_eq!(stats.softirq, 17875);
        assert_eq!(stats.steal, 0);
    }

    #[test]
    fn test_core_stats_calculations() {
        let stats = CoreStats {
            user: 100,
            nice: 10,
            system: 50,
            idle: 800,
            iowait: 20,
            irq: 5,
            softirq: 10,
            steal: 5,
        };

        assert_eq!(stats.total(), 1000);
        assert_eq!(stats.active(), 180); // user + nice + system + irq + softirq + steal
        assert_eq!(stats.idle_time(), 820); // idle + iowait
    }

    #[test]
    fn test_calculate_core_load() {
        let prev = CoreStats {
            user: 100,
            nice: 0,
            system: 0,
            idle: 900,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let current = CoreStats {
            user: 200,
            nice: 0,
            system: 0,
            idle: 1800,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        // Delta: 100 active, 900 idle = 1000 total
        // Load = 100/1000 = 10%
        let load = LoadMonitor::calculate_core_load(&prev, &current);
        assert!((load - 10.0).abs() < 0.01);
    }

    #[test]
    fn test_calculate_load_average() {
        let prev = CpuStats {
            total: CoreStats::default(),
            per_core: vec![
                CoreStats { user: 0, nice: 0, system: 0, idle: 100, iowait: 0, irq: 0, softirq: 0, steal: 0 },
                CoreStats { user: 0, nice: 0, system: 0, idle: 100, iowait: 0, irq: 0, softirq: 0, steal: 0 },
            ],
            timestamp: Instant::now(),
        };

        let current = CpuStats {
            total: CoreStats::default(),
            per_core: vec![
                CoreStats { user: 50, nice: 0, system: 0, idle: 150, iowait: 0, irq: 0, softirq: 0, steal: 0 },
                CoreStats { user: 30, nice: 0, system: 0, idle: 170, iowait: 0, irq: 0, softirq: 0, steal: 0 },
            ],
            timestamp: Instant::now(),
        };

        let sample = LoadMonitor::calculate_load(&prev, &current, Instant::now());
        
        // Core 0: 50 active / 100 total = 50%
        // Core 1: 30 active / 100 total = 30%
        // Average: 40%
        assert!((sample.per_core[0] - 50.0).abs() < 0.01);
        assert!((sample.per_core[1] - 30.0).abs() < 0.01);
        assert!((sample.average - 40.0).abs() < 0.01);
    }

    #[test]
    fn test_load_clamped_to_valid_range() {
        // Test that load is always in [0, 100] range
        let prev = CoreStats {
            user: 1000,
            nice: 0,
            system: 0,
            idle: 0,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let current = CoreStats {
            user: 2000,
            nice: 0,
            system: 0,
            idle: 0,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let load = LoadMonitor::calculate_core_load(&prev, &current);
        assert!(load >= 0.0 && load <= 100.0);
    }

    #[test]
    fn test_zero_delta_returns_zero_load() {
        let stats = CoreStats {
            user: 100,
            nice: 0,
            system: 0,
            idle: 900,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let load = LoadMonitor::calculate_core_load(&stats, &stats);
        assert_eq!(load, 0.0);
    }

    #[test]
    fn test_validate_sample_interval_valid() {
        // Minimum valid
        assert!(validate_sample_interval_ms(10).is_ok());
        // Maximum valid
        assert!(validate_sample_interval_ms(5000).is_ok());
        // Middle value
        assert!(validate_sample_interval_ms(100).is_ok());
        assert!(validate_sample_interval_ms(1000).is_ok());
    }

    #[test]
    fn test_validate_sample_interval_too_small() {
        assert!(validate_sample_interval_ms(9).is_err());
        assert!(validate_sample_interval_ms(0).is_err());
        assert!(validate_sample_interval_ms(1).is_err());
    }

    #[test]
    fn test_validate_sample_interval_too_large() {
        assert!(validate_sample_interval_ms(5001).is_err());
        assert!(validate_sample_interval_ms(10000).is_err());
        assert!(validate_sample_interval_ms(u64::MAX).is_err());
    }

    #[test]
    fn test_load_monitor_rejects_invalid_interval() {
        // Too small
        assert!(LoadMonitor::with_path(5, "/proc/stat".to_string()).is_err());
        // Too large
        assert!(LoadMonitor::with_path(6000, "/proc/stat".to_string()).is_err());
    }

    #[test]
    fn test_load_monitor_accepts_valid_interval() {
        // Note: This will fail on non-Linux systems due to /proc/stat not existing,
        // but the validation itself should pass
        let result = LoadMonitor::with_path(100, "/nonexistent".to_string());
        // The constructor should succeed (validation passes), 
        // only actual sampling would fail
        assert!(result.is_ok());
    }
}
