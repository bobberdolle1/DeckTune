//! Property-based tests for LoadMonitor
//!
//! **Feature: dynamic-mode-refactor, Property 1: Load Calculation Correctness**
//! **Validates: Requirements 2.2, 2.5**

use proptest::prelude::*;
use std::time::Instant;

use gymdeck3::{CoreStats, CpuStats, LoadMonitor};

proptest! {
    #![proptest_config(ProptestConfig::with_cases(100))]

    /// Property 1: Load Calculation Correctness
    ///
    /// For any two consecutive valid /proc/stat snapshots, the calculated CPU load
    /// percentage for each core SHALL be in range [0.0, 100.0], and the average load
    /// SHALL equal the arithmetic mean of per-core loads.
    ///
    /// **Validates: Requirements 2.2, 2.5**
    #[test]
    fn prop_load_in_valid_range_and_average_is_mean(
        num_cores in 1usize..=8usize,
        // Deltas for each potential core (we'll use first num_cores)
        user_deltas in prop::collection::vec(0u64..100_000u64, 8),
        system_deltas in prop::collection::vec(0u64..50_000u64, 8),
        idle_deltas in prop::collection::vec(1u64..1_000_000u64, 8), // At least 1 to avoid div by zero
    ) {
        // Create previous stats (all zeros for simplicity)
        let prev_cores: Vec<CoreStats> = (0..num_cores)
            .map(|_| CoreStats::default())
            .collect();

        // Create current stats with the generated deltas
        let current_cores: Vec<CoreStats> = (0..num_cores)
            .map(|i| CoreStats {
                user: user_deltas[i],
                nice: 0,
                system: system_deltas[i],
                idle: idle_deltas[i],
                iowait: 0,
                irq: 0,
                softirq: 0,
                steal: 0,
            })
            .collect();

        let prev = CpuStats {
            total: CoreStats::default(),
            per_core: prev_cores,
            timestamp: Instant::now(),
        };

        let current = CpuStats {
            total: CoreStats::default(),
            per_core: current_cores,
            timestamp: Instant::now(),
        };

        let sample = LoadMonitor::calculate_load(&prev, &current, Instant::now());

        // Property 1a: All per-core loads are in [0.0, 100.0]
        for (i, &load) in sample.per_core.iter().enumerate() {
            prop_assert!(
                load >= 0.0 && load <= 100.0,
                "Core {} load {} is out of range [0.0, 100.0]",
                i,
                load
            );
        }

        // Property 1b: Average load is in [0.0, 100.0]
        prop_assert!(
            sample.average >= 0.0 && sample.average <= 100.0,
            "Average load {} is out of range [0.0, 100.0]",
            sample.average
        );

        // Property 1c: Average equals arithmetic mean of per-core loads
        if !sample.per_core.is_empty() {
            let expected_avg = sample.per_core.iter().sum::<f32>() / sample.per_core.len() as f32;
            prop_assert!(
                (sample.average - expected_avg).abs() < 0.001,
                "Average {} does not equal mean of per-core loads {}",
                sample.average,
                expected_avg
            );
        }
    }

    /// Property: Load calculation handles edge case of zero total delta
    #[test]
    fn prop_zero_delta_returns_zero_load(
        num_cores in 1usize..=4usize,
        base_values in prop::collection::vec(0u64..1_000_000u64, 8),
    ) {
        // Same stats for prev and current = zero delta = zero load
        let cores: Vec<CoreStats> = (0..num_cores)
            .map(|i| CoreStats {
                user: base_values[i],
                nice: base_values[(i + 1) % 8],
                system: base_values[(i + 2) % 8],
                idle: base_values[(i + 3) % 8],
                iowait: 0,
                irq: 0,
                softirq: 0,
                steal: 0,
            })
            .collect();

        let stats = CpuStats {
            total: CoreStats::default(),
            per_core: cores,
            timestamp: Instant::now(),
        };

        let sample = LoadMonitor::calculate_load(&stats, &stats, Instant::now());

        // When there's no change, load should be 0
        for &load in &sample.per_core {
            prop_assert!(
                load == 0.0,
                "Expected 0.0 load for zero delta, got {}",
                load
            );
        }
        prop_assert!(
            sample.average == 0.0,
            "Expected 0.0 average for zero delta, got {}",
            sample.average
        );
    }

    /// Property: Load calculation is monotonic with respect to active time ratio
    /// More active time (relative to total) should result in higher load
    #[test]
    fn prop_load_increases_with_active_ratio(
        idle1 in 100u64..1_000_000u64,
        idle2 in 100u64..1_000_000u64,
        active in 1u64..100_000u64,
    ) {
        // Two scenarios with same active time but different idle times
        let prev = CoreStats::default();

        let current1 = CoreStats {
            user: active,
            nice: 0,
            system: 0,
            idle: idle1,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let current2 = CoreStats {
            user: active,
            nice: 0,
            system: 0,
            idle: idle2,
            iowait: 0,
            irq: 0,
            softirq: 0,
            steal: 0,
        };

        let prev_stats = CpuStats {
            total: prev.clone(),
            per_core: vec![prev],
            timestamp: Instant::now(),
        };

        let current_stats1 = CpuStats {
            total: current1.clone(),
            per_core: vec![current1],
            timestamp: Instant::now(),
        };

        let current_stats2 = CpuStats {
            total: current2.clone(),
            per_core: vec![current2],
            timestamp: Instant::now(),
        };

        let sample1 = LoadMonitor::calculate_load(&prev_stats, &current_stats1, Instant::now());
        let sample2 = LoadMonitor::calculate_load(&prev_stats, &current_stats2, Instant::now());

        // More idle time = lower load
        // So if idle1 > idle2, then load1 < load2
        if idle1 > idle2 {
            prop_assert!(
                sample1.average <= sample2.average + 0.01, // Small epsilon for float comparison
                "More idle time should result in lower load: idle1={}, idle2={}, load1={}, load2={}",
                idle1, idle2, sample1.average, sample2.average
            );
        } else if idle2 > idle1 {
            prop_assert!(
                sample2.average <= sample1.average + 0.01,
                "More idle time should result in lower load: idle1={}, idle2={}, load1={}, load2={}",
                idle1, idle2, sample1.average, sample2.average
            );
        }
    }
}
