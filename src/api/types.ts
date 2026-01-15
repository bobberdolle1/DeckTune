/**
 * Type definitions for DeckTune frontend state management.
 * 
 * Feature: decktune, Frontend State Management
 * Requirements: Frontend integration, State management
 */

/**
 * Platform information from backend detection.
 */
export interface PlatformInfo {
  model: string;        // "Jupiter" or "Galileo"
  variant: string;      // "LCD" or "OLED"
  safe_limit: number;   // Maximum safe undervolt (-30 or -35)
  detected: boolean;    // True if successfully detected
}

/**
 * Autotune progress event data.
 */
export interface AutotuneProgress {
  phase: string;        // "A" or "B"
  core: number;         // 0-3
  value: number;        // Current undervolt value being tested
  eta: number;          // Estimated time remaining in seconds
}

/**
 * Autotune result after completion.
 */
export interface AutotuneResult {
  cores: number[];      // Final values per core [4 values]
  duration: number;     // Total time in seconds
  tests_run: number;    // Number of tests executed
  stable: boolean;      // All cores found stable values
}

/**
 * Test result from stress test execution.
 */
export interface TestResult {
  passed: boolean;
  duration: number;
  logs: string;
  error?: string;
}

/**
 * Test history entry stored in settings.
 */
export interface TestHistoryEntry {
  test_name: string;
  passed: boolean;
  duration: number;
  timestamp: string;
  cores_tested: number[];
}

/**
 * Preset configuration for per-game settings.
 */
export interface Preset {
  app_id: number;
  label: string;
  value: number[];      // [core0, core1, core2, core3]
  timeout: number;
  use_timeout: boolean;
  created_at?: string;
  tested?: boolean;
}

/**
 * Dynamic mode core configuration.
 */
export interface DynamicCoreConfig {
  maximum_value: number;
  minimum_value: number;
  threshold: number;
  manual_points: Array<{ load: number; value: number }>;
}

/**
 * Dynamic mode settings.
 */
export interface DynamicSettings {
  strategy: "DEFAULT" | "AGGRESSIVE" | "MANUAL";
  sample_interval: number;
  cores: DynamicCoreConfig[];
}

/**
 * User settings configuration.
 */
export interface Settings {
  isGlobal: boolean;
  runAtStartup: boolean;
  isRunAutomatically: boolean;
  timeoutApply: number;
}

/**
 * Status string type.
 * Validates: Requirements 5.3
 */
export type StatusString = 
  | "enabled" 
  | "disabled" 
  | "error" 
  | "scheduled" 
  | "DYNAMIC RUNNING"
  | `Using preset for ${string}`
  | "Global"
  | "Disabled";

/**
 * Complete application state.
 */
export interface State {
  // Core state
  cores: number[];
  globalCores: number[];
  status: StatusString;
  
  // Platform info
  platformInfo: PlatformInfo | null;
  
  // Running app info
  runningAppName: string | null;
  runningAppId: number | null;
  
  // Presets
  presets: Preset[];
  currentPreset: Preset | null;
  
  // Settings
  settings: Settings;
  dynamicSettings: DynamicSettings;
  
  // Dynamic mode
  gymdeckRunning: boolean;
  isDynamic: boolean;
  
  // Autotune state
  autotuneProgress: AutotuneProgress | null;
  autotuneResult: AutotuneResult | null;
  isAutotuning: boolean;
  
  // Test state
  testHistory: TestHistoryEntry[];
  currentTest: string | null;
  isTestRunning: boolean;
  
  // Binary availability (for SteamOS compatibility warnings)
  missingBinaries: string[];
}

/**
 * Server event types.
 */
export interface ServerEvent {
  type: "update_status" | "tuning_progress" | "tuning_complete" | "test_complete";
  data: any;
}

/**
 * RPC response types.
 */
export interface RpcResponse<T = any> {
  success: boolean;
  error?: string;
  data?: T;
}
