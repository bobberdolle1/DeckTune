//! Acoustic fan profiles for Steam Deck
//!
//! Provides preset fan curves optimized for different use cases:
//! - **Silent**: Prioritizes low noise, max ~3000 RPM until 85°C
//! - **Balanced**: Linear curve balancing noise and cooling
//! - **MaxCooling**: Aggressive cooling, max RPM at 60°C+
//! - **Custom**: User-defined curve
//!
//! All profiles respect safety overrides (90°C+ forces 100% fan).

use serde::{Deserialize, Serialize};
use super::controller::FanCurve;

/// Acoustic fan profile presets
///
/// Each profile defines a fan curve optimized for a specific use case.
/// Safety overrides (90°C+ = 100% fan) apply regardless of profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum AcousticProfile {
    /// Silent profile: prioritizes low noise
    /// - Max ~60% (3000 RPM) until 85°C
    /// - Zero RPM until 40°C
    /// - Gradual ramp to minimize noise
    Silent,
    
    /// Balanced profile: balances noise and cooling
    /// - Linear 30-70°C → 30%-90%
    /// - Good for general gaming
    #[default]
    Balanced,
    
    /// Max Cooling profile: aggressive cooling
    /// - 100% fan at 60°C+
    /// - Prioritizes thermals over noise
    MaxCooling,
    
    /// Custom profile: user-defined curve
    /// - Uses the curve set via set_curve()
    Custom,
}

impl AcousticProfile {
    /// Get the fan curve for this profile
    ///
    /// Returns a FanCurve configured for the profile's characteristics.
    /// Custom profile returns a default curve (should be overridden).
    pub fn curve(&self) -> FanCurve {
        match self {
            AcousticProfile::Silent => {
                // Silent: prioritize low RPM
                // Max 60% (~3000 RPM) until 85°C
                // Safety override kicks in at 90°C
                FanCurve::from_tuples(vec![
                    (40, 0),    // Zero RPM until 40°C
                    (60, 20),   // 20% at 60°C
                    (75, 40),   // 40% at 75°C
                    (85, 60),   // 60% at 85°C (max ~3000 RPM)
                    (90, 100),  // 100% at 90°C (safety)
                ])
                .expect("Silent curve is valid")
            }
            AcousticProfile::Balanced => {
                // Balanced: linear 30-70°C → 30%-90%
                FanCurve::from_tuples(vec![
                    (30, 30),   // 30% at 30°C (~1500 RPM)
                    (50, 50),   // 50% at 50°C
                    (70, 90),   // 90% at 70°C (~4500 RPM)
                    (80, 100),  // 100% at 80°C
                ])
                .expect("Balanced curve is valid")
            }
            AcousticProfile::MaxCooling => {
                // Max Cooling: aggressive, 100% at 60°C+
                FanCurve::from_tuples(vec![
                    (40, 50),   // 50% at 40°C
                    (60, 100),  // 100% at 60°C (max RPM)
                ])
                .expect("MaxCooling curve is valid")
            }
            AcousticProfile::Custom => {
                // Custom: return default, should be overridden
                FanCurve::default()
            }
        }
    }
    
    /// Get the profile name as a string
    pub fn name(&self) -> &'static str {
        match self {
            AcousticProfile::Silent => "silent",
            AcousticProfile::Balanced => "balanced",
            AcousticProfile::MaxCooling => "max_cooling",
            AcousticProfile::Custom => "custom",
        }
    }
    
    /// Parse profile from string
    pub fn from_name(name: &str) -> Option<Self> {
        match name.to_lowercase().as_str() {
            "silent" => Some(AcousticProfile::Silent),
            "balanced" => Some(AcousticProfile::Balanced),
            "max_cooling" | "maxcooling" | "max-cooling" => Some(AcousticProfile::MaxCooling),
            "custom" => Some(AcousticProfile::Custom),
            _ => None,
        }
    }
    
    /// Get all available profiles (excluding Custom)
    pub fn presets() -> &'static [AcousticProfile] {
        &[
            AcousticProfile::Silent,
            AcousticProfile::Balanced,
            AcousticProfile::MaxCooling,
        ]
    }
}

impl std::fmt::Display for AcousticProfile {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_silent_profile_curve() {
        let curve = AcousticProfile::Silent.curve();
        assert!(curve.len() >= 2);
        
        // Should be 0% at 40°C
        assert_eq!(curve.calculate_speed(40), 0);
        
        // Should be max 60% at 85°C
        assert_eq!(curve.calculate_speed(85), 60);
    }

    #[test]
    fn test_balanced_profile_curve() {
        let curve = AcousticProfile::Balanced.curve();
        assert!(curve.len() >= 2);
        
        // Should be 30% at 30°C
        assert_eq!(curve.calculate_speed(30), 30);
        
        // Should be 90% at 70°C
        assert_eq!(curve.calculate_speed(70), 90);
    }

    #[test]
    fn test_max_cooling_profile_curve() {
        let curve = AcousticProfile::MaxCooling.curve();
        assert!(curve.len() >= 2);
        
        // Should be 100% at 60°C+
        assert_eq!(curve.calculate_speed(60), 100);
        assert_eq!(curve.calculate_speed(80), 100);
    }

    #[test]
    fn test_profile_name_roundtrip() {
        for profile in AcousticProfile::presets() {
            let name = profile.name();
            let parsed = AcousticProfile::from_name(name);
            assert_eq!(parsed, Some(*profile));
        }
    }

    #[test]
    fn test_profile_from_name_variants() {
        assert_eq!(AcousticProfile::from_name("max_cooling"), Some(AcousticProfile::MaxCooling));
        assert_eq!(AcousticProfile::from_name("maxcooling"), Some(AcousticProfile::MaxCooling));
        assert_eq!(AcousticProfile::from_name("max-cooling"), Some(AcousticProfile::MaxCooling));
        assert_eq!(AcousticProfile::from_name("SILENT"), Some(AcousticProfile::Silent));
        assert_eq!(AcousticProfile::from_name("invalid"), None);
    }

    #[test]
    fn test_default_profile() {
        assert_eq!(AcousticProfile::default(), AcousticProfile::Balanced);
    }
}
