//! Safety features for gymdeck3
//!
//! Provides safety checks and value validation to ensure safe operation.
//!
//! Requirements: 9.1, 9.5

use crate::strategy::CoreBounds;

/// Exit code for permission denied (not running as root)
pub const EXIT_CODE_NOT_ROOT: i32 = 6;

/// Check if the current process is running as root
///
/// Returns true if running as root (UID 0), false otherwise.
///
/// # Platform Support
/// This function only works on Unix-like systems. On other platforms,
/// it will always return false.
#[cfg(unix)]
pub fn is_root() -> bool {
    // SAFETY: getuid() is always safe to call
    unsafe { libc::getuid() == 0 }
}

#[cfg(not(unix))]
pub fn is_root() -> bool {
    false
}

/// Check if running as root and exit with error if not
///
/// This should be called early in main() to ensure the daemon
/// has the necessary permissions to modify CPU voltage.
///
/// # Arguments
/// * `verbose` - Whether to print verbose output
///
/// # Returns
/// Ok(()) if running as root, Err with exit code if not
pub fn check_root_or_exit(verbose: bool) -> Result<(), i32> {
    if is_root() {
        if verbose {
            eprintln!("Running as root (UID 0)");
        }
        Ok(())
    } else {
        eprintln!("Error: gymdeck3 must be run as root (sudo) to modify CPU voltage.");
        eprintln!("Please run with: sudo gymdeck3 ...");
        Err(EXIT_CODE_NOT_ROOT)
    }
}

/// Validate and clamp an undervolt value against bounds
///
/// Ensures the value is within the safe range defined by CoreBounds.
/// Values outside the range are clamped to the nearest bound.
///
/// # Arguments
/// * `value` - The undervolt value to validate (in mV, negative or zero)
/// * `bounds` - The bounds to validate against
///
/// # Returns
/// The clamped value within bounds
pub fn clamp_value(value: i32, bounds: &CoreBounds) -> i32 {
    // max_mv is more negative (more aggressive), min_mv is less negative (safer)
    // So valid range is [max_mv, min_mv]
    value.max(bounds.max_mv).min(bounds.min_mv)
}

/// Validate an undervolt value against bounds
///
/// Returns true if the value is within bounds, false otherwise.
///
/// # Arguments
/// * `value` - The undervolt value to validate (in mV, negative or zero)
/// * `bounds` - The bounds to validate against
pub fn is_value_in_bounds(value: i32, bounds: &CoreBounds) -> bool {
    value >= bounds.max_mv && value <= bounds.min_mv
}

/// Validate all values against their respective bounds
///
/// # Arguments
/// * `values` - Slice of undervolt values
/// * `bounds` - Slice of bounds for each core
///
/// # Returns
/// Vec of clamped values
pub fn clamp_all_values(values: &[i32], bounds: &[CoreBounds]) -> Vec<i32> {
    values
        .iter()
        .zip(bounds.iter())
        .map(|(&v, b)| clamp_value(v, b))
        .collect()
}

/// Check if all values are within their bounds
///
/// # Arguments
/// * `values` - Slice of undervolt values
/// * `bounds` - Slice of bounds for each core
///
/// # Returns
/// true if all values are within bounds
pub fn all_values_in_bounds(values: &[i32], bounds: &[CoreBounds]) -> bool {
    values
        .iter()
        .zip(bounds.iter())
        .all(|(&v, b)| is_value_in_bounds(v, b))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_bounds() -> CoreBounds {
        CoreBounds {
            min_mv: -20,
            max_mv: -35,
            threshold: 50.0,
        }
    }

    #[test]
    fn test_clamp_value_within_bounds() {
        let bounds = test_bounds();
        assert_eq!(clamp_value(-25, &bounds), -25);
        assert_eq!(clamp_value(-20, &bounds), -20);
        assert_eq!(clamp_value(-35, &bounds), -35);
    }

    #[test]
    fn test_clamp_value_too_aggressive() {
        let bounds = test_bounds();
        // Value more negative than max_mv should be clamped to max_mv
        assert_eq!(clamp_value(-40, &bounds), -35);
        assert_eq!(clamp_value(-100, &bounds), -35);
    }

    #[test]
    fn test_clamp_value_too_conservative() {
        let bounds = test_bounds();
        // Value less negative than min_mv should be clamped to min_mv
        assert_eq!(clamp_value(-10, &bounds), -20);
        assert_eq!(clamp_value(0, &bounds), -20);
        assert_eq!(clamp_value(10, &bounds), -20);
    }

    #[test]
    fn test_is_value_in_bounds() {
        let bounds = test_bounds();
        assert!(is_value_in_bounds(-25, &bounds));
        assert!(is_value_in_bounds(-20, &bounds));
        assert!(is_value_in_bounds(-35, &bounds));
        assert!(!is_value_in_bounds(-10, &bounds));
        assert!(!is_value_in_bounds(-40, &bounds));
    }

    #[test]
    fn test_clamp_all_values() {
        let bounds = vec![
            CoreBounds { min_mv: -20, max_mv: -35, threshold: 50.0 },
            CoreBounds { min_mv: -25, max_mv: -40, threshold: 50.0 },
        ];
        let values = vec![-10, -50];
        let clamped = clamp_all_values(&values, &bounds);
        assert_eq!(clamped, vec![-20, -40]);
    }

    #[test]
    fn test_all_values_in_bounds() {
        let bounds = vec![
            CoreBounds { min_mv: -20, max_mv: -35, threshold: 50.0 },
            CoreBounds { min_mv: -25, max_mv: -40, threshold: 50.0 },
        ];
        
        assert!(all_values_in_bounds(&[-25, -30], &bounds));
        assert!(!all_values_in_bounds(&[-10, -30], &bounds));
        assert!(!all_values_in_bounds(&[-25, -50], &bounds));
    }

    #[test]
    #[cfg(unix)]
    fn test_is_root_returns_bool() {
        // Just verify it returns a boolean without crashing
        let _ = is_root();
    }

    #[test]
    fn test_check_root_or_exit_format() {
        // Test that the function exists and returns the expected type
        // We can't actually test root check without being root
        let result = check_root_or_exit(false);
        // Result should be Ok if root, Err(EXIT_CODE_NOT_ROOT) if not
        match result {
            Ok(()) => {
                // Running as root
            }
            Err(code) => {
                assert_eq!(code, EXIT_CODE_NOT_ROOT);
            }
        }
    }
}
