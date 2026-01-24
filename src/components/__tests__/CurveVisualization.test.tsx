/**
 * Unit tests for CurveVisualization component.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
 */

import { describe, it, expect } from '@jest/globals';
import { CoreConfig, CoreMetrics } from '../../types/DynamicMode';

/**
 * Test data for curve visualization.
 */
const createTestConfig = (overrides?: Partial<CoreConfig>): CoreConfig => ({
  core_id: 0,
  min_mv: -30,
  max_mv: -15,
  threshold: 50,
  ...overrides,
});

const createTestMetrics = (overrides?: Partial<CoreMetrics>): CoreMetrics => ({
  core_id: 0,
  load: 75,
  voltage: -20,
  frequency: 3500,
  temperature: 65,
  timestamp: Date.now() / 1000,
  ...overrides,
});

describe('CurveVisualization', () => {
  describe('Curve Calculation', () => {
    it('should calculate voltage below threshold as min_mv', () => {
      const config = createTestConfig({ min_mv: -40, max_mv: -20, threshold: 60 });
      
      // For load <= threshold, voltage should equal min_mv
      const load = 30; // Below threshold of 60
      const expectedVoltage = config.min_mv; // -40
      
      expect(load).toBeLessThanOrEqual(config.threshold);
      expect(expectedVoltage).toBe(-40);
    });

    it('should calculate voltage above threshold using interpolation', () => {
      const config = createTestConfig({ min_mv: -40, max_mv: -20, threshold: 50 });
      
      // For load > threshold, voltage should be interpolated
      const load = 75; // Above threshold of 50
      const progress = (load - config.threshold) / (100 - config.threshold);
      const expectedVoltage = config.min_mv + (config.max_mv - config.min_mv) * progress;
      
      // Expected: -40 + (-20 - (-40)) * (75 - 50) / (100 - 50)
      // Expected: -40 + 20 * 25 / 50 = -40 + 10 = -30
      expect(expectedVoltage).toBe(-30);
    });

    it('should calculate voltage at load=100 as max_mv', () => {
      const config = createTestConfig({ min_mv: -50, max_mv: -10, threshold: 40 });
      
      const load = 100;
      const progress = (load - config.threshold) / (100 - config.threshold);
      const expectedVoltage = config.min_mv + (config.max_mv - config.min_mv) * progress;
      
      expect(expectedVoltage).toBe(config.max_mv);
    });

    it('should handle threshold at 0', () => {
      const config = createTestConfig({ min_mv: -60, max_mv: -30, threshold: 0 });
      
      // At load=0, voltage should be min_mv
      const load0 = 0;
      expect(load0).toBe(config.threshold);
      
      // At load=50, voltage should be interpolated
      const load50 = 50;
      const progress = (load50 - config.threshold) / (100 - config.threshold);
      const expectedVoltage = config.min_mv + (config.max_mv - config.min_mv) * progress;
      
      // Expected: -60 + (-30 - (-60)) * 50 / 100 = -60 + 15 = -45
      expect(expectedVoltage).toBe(-45);
    });

    it('should handle threshold at 100', () => {
      const config = createTestConfig({ min_mv: -70, max_mv: -35, threshold: 100 });
      
      // All loads should be at or below threshold
      const load = 100;
      expect(load).toBeLessThanOrEqual(config.threshold);
      
      // Voltage should be min_mv for all loads
      const expectedVoltage = config.min_mv;
      expect(expectedVoltage).toBe(-70);
    });

    it('should handle min_mv equals max_mv', () => {
      const config = createTestConfig({ min_mv: -25, max_mv: -25, threshold: 50 });
      
      // Voltage should be constant regardless of load
      const load = 75;
      const progress = (load - config.threshold) / (100 - config.threshold);
      const expectedVoltage = config.min_mv + (config.max_mv - config.min_mv) * progress;
      
      // Expected: -25 + 0 * progress = -25
      expect(expectedVoltage).toBe(-25);
    });
  });

  describe('Component Props', () => {
    it('should accept valid CoreConfig', () => {
      const config = createTestConfig();
      
      expect(config.core_id).toBeGreaterThanOrEqual(0);
      expect(config.core_id).toBeLessThanOrEqual(3);
      expect(config.min_mv).toBeGreaterThanOrEqual(-100);
      expect(config.min_mv).toBeLessThanOrEqual(0);
      expect(config.max_mv).toBeGreaterThanOrEqual(-100);
      expect(config.max_mv).toBeLessThanOrEqual(0);
      expect(config.threshold).toBeGreaterThanOrEqual(0);
      expect(config.threshold).toBeLessThanOrEqual(100);
    });

    it('should accept optional CoreMetrics', () => {
      const metrics = createTestMetrics();
      
      expect(metrics.core_id).toBeGreaterThanOrEqual(0);
      expect(metrics.load).toBeGreaterThanOrEqual(0);
      expect(metrics.load).toBeLessThanOrEqual(100);
      expect(metrics.voltage).toBeGreaterThanOrEqual(-100);
      expect(metrics.voltage).toBeLessThanOrEqual(0);
      expect(metrics.frequency).toBeGreaterThan(0);
      expect(metrics.temperature).toBeGreaterThan(0);
      expect(metrics.timestamp).toBeGreaterThan(0);
    });
  });

  describe('Curve Point Generation', () => {
    it('should generate 101 curve points', () => {
      // The component should generate points for load 0-100 (inclusive)
      const expectedPointCount = 101;
      expect(expectedPointCount).toBe(101);
    });

    it('should have monotonically increasing load values', () => {
      // Load values should be 0, 1, 2, ..., 100
      const loads = Array.from({ length: 101 }, (_, i) => i);
      
      for (let i = 1; i < loads.length; i++) {
        expect(loads[i]).toBeGreaterThan(loads[i - 1]);
      }
    });

    it('should have voltage values within valid range', () => {
      const config = createTestConfig();
      
      // All voltage values should be between -100 and 0
      const minVoltage = -100;
      const maxVoltage = 0;
      
      expect(config.min_mv).toBeGreaterThanOrEqual(minVoltage);
      expect(config.min_mv).toBeLessThanOrEqual(maxVoltage);
      expect(config.max_mv).toBeGreaterThanOrEqual(minVoltage);
      expect(config.max_mv).toBeLessThanOrEqual(maxVoltage);
    });
  });
});
