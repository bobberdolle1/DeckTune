/**
 * Last Known Good (LKG) configuration storage utility.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 7.4 - LKG configuration storage and recovery
 * 
 * Manages storage and retrieval of stable configurations for error recovery.
 * A configuration is marked as "stable" after running successfully for 30 seconds.
 */

import { DynamicConfig, LastKnownGoodConfig } from '../types/DynamicMode';

/**
 * Storage key for LKG configuration in localStorage.
 */
const LKG_STORAGE_KEY = 'dynamicMode_lkg';

/**
 * Minimum duration (in seconds) a configuration must be stable before
 * being marked as Last Known Good.
 */
const STABILITY_THRESHOLD_SECONDS = 30;

/**
 * Save a configuration as Last Known Good.
 * 
 * Stores the configuration with timestamp and stability duration.
 * This should be called after a configuration has been running
 * successfully for at least STABILITY_THRESHOLD_SECONDS.
 * 
 * @param config - Configuration to save as LKG
 * @param stableDuration - Duration in seconds the config has been stable
 * @returns True if saved successfully
 * 
 * Requirements: 7.4
 */
export function saveLKG(config: DynamicConfig, stableDuration: number): boolean {
  try {
    const lkg: LastKnownGoodConfig = {
      config,
      timestamp: Date.now(),
      stable_duration: stableDuration,
    };
    
    localStorage.setItem(LKG_STORAGE_KEY, JSON.stringify(lkg));
    console.log(`[LKG] Saved Last Known Good config (stable for ${stableDuration}s)`);
    return true;
  } catch (error) {
    console.error('[LKG] Failed to save Last Known Good config:', error);
    return false;
  }
}

/**
 * Load the Last Known Good configuration.
 * 
 * Retrieves the most recently saved stable configuration.
 * Returns null if no LKG configuration exists or if loading fails.
 * 
 * @returns Last Known Good configuration or null
 * 
 * Requirements: 7.4
 */
export function loadLKG(): LastKnownGoodConfig | null {
  try {
    const stored = localStorage.getItem(LKG_STORAGE_KEY);
    if (!stored) {
      console.log('[LKG] No Last Known Good config found');
      return null;
    }
    
    const lkg = JSON.parse(stored) as LastKnownGoodConfig;
    
    // Validate structure
    if (!lkg.config || !lkg.timestamp || typeof lkg.stable_duration !== 'number') {
      console.warn('[LKG] Invalid Last Known Good config structure');
      return null;
    }
    
    console.log(
      `[LKG] Loaded Last Known Good config from ${new Date(lkg.timestamp).toLocaleString()} ` +
      `(stable for ${lkg.stable_duration}s)`
    );
    return lkg;
  } catch (error) {
    console.error('[LKG] Failed to load Last Known Good config:', error);
    return null;
  }
}

/**
 * Clear the Last Known Good configuration.
 * 
 * Removes the stored LKG configuration from localStorage.
 * This might be called when resetting to factory defaults.
 * 
 * @returns True if cleared successfully
 */
export function clearLKG(): boolean {
  try {
    localStorage.removeItem(LKG_STORAGE_KEY);
    console.log('[LKG] Cleared Last Known Good config');
    return true;
  } catch (error) {
    console.error('[LKG] Failed to clear Last Known Good config:', error);
    return false;
  }
}

/**
 * Check if a configuration has been stable long enough to be marked as LKG.
 * 
 * @param stableDuration - Duration in seconds the config has been stable
 * @returns True if duration meets the stability threshold
 */
export function isStableEnoughForLKG(stableDuration: number): boolean {
  return stableDuration >= STABILITY_THRESHOLD_SECONDS;
}

/**
 * Get the age of the Last Known Good configuration in milliseconds.
 * 
 * @returns Age in milliseconds, or null if no LKG exists
 */
export function getLKGAge(): number | null {
  const lkg = loadLKG();
  if (!lkg) {
    return null;
  }
  
  return Date.now() - lkg.timestamp;
}

/**
 * Check if the Last Known Good configuration is recent enough to be useful.
 * 
 * An LKG is considered stale if it's older than 7 days.
 * 
 * @returns True if LKG exists and is not stale
 */
export function isLKGFresh(): boolean {
  const age = getLKGAge();
  if (age === null) {
    return false;
  }
  
  const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;
  return age < SEVEN_DAYS_MS;
}

/**
 * Stability tracker for monitoring configuration stability.
 * 
 * Tracks how long a configuration has been running without errors
 * and automatically saves it as LKG when it reaches the stability threshold.
 */
export class StabilityTracker {
  private startTime: number | null = null;
  private config: DynamicConfig | null = null;
  private checkInterval: NodeJS.Timeout | null = null;
  
  /**
   * Start tracking stability for a configuration.
   * 
   * @param config - Configuration to track
   */
  start(config: DynamicConfig): void {
    this.stop(); // Stop any existing tracking
    
    this.config = config;
    this.startTime = Date.now();
    
    console.log('[LKG] Started stability tracking');
    
    // Check stability every 5 seconds
    this.checkInterval = setInterval(() => {
      this.checkStability();
    }, 5000);
  }
  
  /**
   * Stop tracking stability.
   */
  stop(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    
    this.startTime = null;
    this.config = null;
    
    console.log('[LKG] Stopped stability tracking');
  }
  
  /**
   * Check if configuration has been stable long enough and save as LKG.
   */
  private checkStability(): void {
    if (!this.startTime || !this.config) {
      return;
    }
    
    const stableDuration = (Date.now() - this.startTime) / 1000;
    
    if (isStableEnoughForLKG(stableDuration)) {
      // Save as LKG
      saveLKG(this.config, stableDuration);
      
      // Stop tracking - we've saved it
      this.stop();
    }
  }
  
  /**
   * Get current stability duration in seconds.
   * 
   * @returns Duration in seconds, or 0 if not tracking
   */
  getStabilityDuration(): number {
    if (!this.startTime) {
      return 0;
    }
    
    return (Date.now() - this.startTime) / 1000;
  }
}
