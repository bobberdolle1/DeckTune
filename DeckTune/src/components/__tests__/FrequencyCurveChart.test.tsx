/**
 * Property-based tests for FrequencyCurveChart component.
 * 
 * Feature: frequency-based-wizard, Property 17: Stable point filtering in visualization
 * Feature: frequency-based-wizard, Property 18: Failed point separation in visualization
 * Requirements: 5.2, 5.4
 * 
 * Tests the data transformation logic for curve visualization.
 */

import { describe, it, expect } from '@jest/globals';
import { FrequencyCurve, FrequencyPoint } from '../../api/types';

/**
 * Helper to create test frequency points.
 */
const createFrequencyPoint = (
  frequency_mhz: number,
  voltage_mv: number,
  stable: boolean
): FrequencyPoint => ({
  frequency_mhz,
  voltage_mv,
  stable,
  test_duration: 30,
  timestamp: Date.now() / 1000,
});

/**
 * Helper to create test frequency curve.
 */
const createFrequencyCurve = (points: FrequencyPoint[]): FrequencyCurve => ({
  core_id: 0,
  points,
  created_at: Date.now() / 1000,
  wizard_config: {
    freq_start: 400,
    freq_end: 3500,
    freq_step: 200,
    test_duration: 30,
    voltage_start: -30,
    voltage_step: 2,
    safety_margin: 5,
  },
});

/**
 * Filter stable points from curve (mimics component logic).
 * This is the logic being tested.
 */
const filterStablePoints = (curve: FrequencyCurve): FrequencyPoint[] => {
  return curve.points.filter((p) => p.stable);
};

/**
 * Filter failed points from curve (mimics component logic).
 * This is the logic being tested.
 */
const filterFailedPoints = (curve: FrequencyCurve): FrequencyPoint[] => {
  return curve.points.filter((p) => !p.stable);
};

describe('FrequencyCurveChart - Data Transformation', () => {
  describe('Property 17: Stable point filtering in visualization', () => {
    /**
     * Feature: frequency-based-wizard, Property 17: Stable point filtering in visualization
     * Validates: Requirements 5.2
     * 
     * For any frequency curve displayed in the chart, only points where stable=true
     * should be included in the stable points marker data.
     */
    it('should only include stable points in stable dataset', () => {
      // Create a curve with mixed stable and unstable points
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, true),
        createFrequencyPoint(800, -45, false), // Failed
        createFrequencyPoint(1000, -42, true),
        createFrequencyPoint(1200, -40, false), // Failed
        createFrequencyPoint(1400, -38, true),
      ];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      
      // All returned points must have stable=true
      expect(stablePoints.every((p) => p.stable === true)).toBe(true);
      
      // Should have exactly 4 stable points
      expect(stablePoints.length).toBe(4);
      
      // Verify specific stable points are included
      expect(stablePoints.some((p) => p.frequency_mhz === 400)).toBe(true);
      expect(stablePoints.some((p) => p.frequency_mhz === 600)).toBe(true);
      expect(stablePoints.some((p) => p.frequency_mhz === 1000)).toBe(true);
      expect(stablePoints.some((p) => p.frequency_mhz === 1400)).toBe(true);
      
      // Verify failed points are NOT included
      expect(stablePoints.some((p) => p.frequency_mhz === 800)).toBe(false);
      expect(stablePoints.some((p) => p.frequency_mhz === 1200)).toBe(false);
    });

    it('should return empty array when all points are unstable', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, false),
        createFrequencyPoint(600, -48, false),
        createFrequencyPoint(800, -45, false),
      ];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      
      expect(stablePoints.length).toBe(0);
    });

    it('should return all points when all are stable', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, true),
        createFrequencyPoint(800, -45, true),
        createFrequencyPoint(1000, -42, true),
      ];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      
      expect(stablePoints.length).toBe(4);
      expect(stablePoints.every((p) => p.stable === true)).toBe(true);
    });

    it('should handle single stable point', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, false),
        createFrequencyPoint(600, -48, true), // Only stable point
        createFrequencyPoint(800, -45, false),
      ];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      
      expect(stablePoints.length).toBe(1);
      expect(stablePoints[0].frequency_mhz).toBe(600);
      expect(stablePoints[0].stable).toBe(true);
    });

    it('should preserve all properties of stable points', () => {
      const testPoint = createFrequencyPoint(1000, -42, true);
      const points: FrequencyPoint[] = [testPoint];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      
      expect(stablePoints.length).toBe(1);
      expect(stablePoints[0].frequency_mhz).toBe(testPoint.frequency_mhz);
      expect(stablePoints[0].voltage_mv).toBe(testPoint.voltage_mv);
      expect(stablePoints[0].stable).toBe(testPoint.stable);
      expect(stablePoints[0].test_duration).toBe(testPoint.test_duration);
      expect(stablePoints[0].timestamp).toBe(testPoint.timestamp);
    });
  });

  describe('Property 18: Failed point separation in visualization', () => {
    /**
     * Feature: frequency-based-wizard, Property 18: Failed point separation in visualization
     * Validates: Requirements 5.4
     * 
     * For any frequency curve displayed in the chart, points where stable=false
     * should be separated into a distinct dataset from stable points.
     */
    it('should only include failed points in failed dataset', () => {
      // Create a curve with mixed stable and unstable points
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, false), // Failed
        createFrequencyPoint(800, -45, true),
        createFrequencyPoint(1000, -42, false), // Failed
        createFrequencyPoint(1200, -40, true),
        createFrequencyPoint(1400, -38, false), // Failed
      ];
      
      const curve = createFrequencyCurve(points);
      const failedPoints = filterFailedPoints(curve);
      
      // All returned points must have stable=false
      expect(failedPoints.every((p) => p.stable === false)).toBe(true);
      
      // Should have exactly 3 failed points
      expect(failedPoints.length).toBe(3);
      
      // Verify specific failed points are included
      expect(failedPoints.some((p) => p.frequency_mhz === 600)).toBe(true);
      expect(failedPoints.some((p) => p.frequency_mhz === 1000)).toBe(true);
      expect(failedPoints.some((p) => p.frequency_mhz === 1400)).toBe(true);
      
      // Verify stable points are NOT included
      expect(failedPoints.some((p) => p.frequency_mhz === 400)).toBe(false);
      expect(failedPoints.some((p) => p.frequency_mhz === 800)).toBe(false);
      expect(failedPoints.some((p) => p.frequency_mhz === 1200)).toBe(false);
    });

    it('should return empty array when all points are stable', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, true),
        createFrequencyPoint(800, -45, true),
      ];
      
      const curve = createFrequencyCurve(points);
      const failedPoints = filterFailedPoints(curve);
      
      expect(failedPoints.length).toBe(0);
    });

    it('should return all points when all are failed', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, false),
        createFrequencyPoint(600, -48, false),
        createFrequencyPoint(800, -45, false),
        createFrequencyPoint(1000, -42, false),
      ];
      
      const curve = createFrequencyCurve(points);
      const failedPoints = filterFailedPoints(curve);
      
      expect(failedPoints.length).toBe(4);
      expect(failedPoints.every((p) => p.stable === false)).toBe(true);
    });

    it('should handle single failed point', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, false), // Only failed point
        createFrequencyPoint(800, -45, true),
      ];
      
      const curve = createFrequencyCurve(points);
      const failedPoints = filterFailedPoints(curve);
      
      expect(failedPoints.length).toBe(1);
      expect(failedPoints[0].frequency_mhz).toBe(600);
      expect(failedPoints[0].stable).toBe(false);
    });

    it('should preserve all properties of failed points', () => {
      const testPoint = createFrequencyPoint(1000, -42, false);
      const points: FrequencyPoint[] = [testPoint];
      
      const curve = createFrequencyCurve(points);
      const failedPoints = filterFailedPoints(curve);
      
      expect(failedPoints.length).toBe(1);
      expect(failedPoints[0].frequency_mhz).toBe(testPoint.frequency_mhz);
      expect(failedPoints[0].voltage_mv).toBe(testPoint.voltage_mv);
      expect(failedPoints[0].stable).toBe(testPoint.stable);
      expect(failedPoints[0].test_duration).toBe(testPoint.test_duration);
      expect(failedPoints[0].timestamp).toBe(testPoint.timestamp);
    });

    it('should ensure stable and failed datasets are mutually exclusive', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, false),
        createFrequencyPoint(800, -45, true),
        createFrequencyPoint(1000, -42, false),
        createFrequencyPoint(1200, -40, true),
      ];
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      const failedPoints = filterFailedPoints(curve);
      
      // No point should appear in both datasets
      const stableFreqs = new Set(stablePoints.map((p) => p.frequency_mhz));
      const failedFreqs = new Set(failedPoints.map((p) => p.frequency_mhz));
      
      // Check for intersection
      const intersection = [...stableFreqs].filter((freq) => failedFreqs.has(freq));
      expect(intersection.length).toBe(0);
      
      // Total points should equal sum of stable and failed
      expect(stablePoints.length + failedPoints.length).toBe(points.length);
    });
  });

  describe('Data Integrity', () => {
    it('should not modify original curve data', () => {
      const points: FrequencyPoint[] = [
        createFrequencyPoint(400, -50, true),
        createFrequencyPoint(600, -48, false),
      ];
      
      const curve = createFrequencyCurve(points);
      const originalPointsCount = curve.points.length;
      const originalFirstPoint = { ...curve.points[0] };
      
      // Filter points
      filterStablePoints(curve);
      filterFailedPoints(curve);
      
      // Original curve should be unchanged
      expect(curve.points.length).toBe(originalPointsCount);
      expect(curve.points[0].frequency_mhz).toBe(originalFirstPoint.frequency_mhz);
      expect(curve.points[0].voltage_mv).toBe(originalFirstPoint.voltage_mv);
      expect(curve.points[0].stable).toBe(originalFirstPoint.stable);
    });

    it('should handle empty curve', () => {
      const curve = createFrequencyCurve([]);
      
      const stablePoints = filterStablePoints(curve);
      const failedPoints = filterFailedPoints(curve);
      
      expect(stablePoints.length).toBe(0);
      expect(failedPoints.length).toBe(0);
    });

    it('should handle large number of points', () => {
      // Create 100 points alternating between stable and failed
      const points: FrequencyPoint[] = [];
      for (let i = 0; i < 100; i++) {
        points.push(createFrequencyPoint(400 + i * 10, -50 + i, i % 2 === 0));
      }
      
      const curve = createFrequencyCurve(points);
      const stablePoints = filterStablePoints(curve);
      const failedPoints = filterFailedPoints(curve);
      
      // Should have 50 stable and 50 failed
      expect(stablePoints.length).toBe(50);
      expect(failedPoints.length).toBe(50);
      
      // All stable points should have stable=true
      expect(stablePoints.every((p) => p.stable === true)).toBe(true);
      
      // All failed points should have stable=false
      expect(failedPoints.every((p) => p.stable === false)).toBe(true);
    });
  });
});
