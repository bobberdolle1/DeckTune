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
 * Dynamic mode status from gymdeck3.
 * Requirements: 15.1
 */
export interface DynamicStatus {
  running: boolean;
  load: number[];       // Per-core CPU load percentages (0-100)
  values: number[];     // Per-core applied undervolt values (mV)
  strategy: string;     // Current strategy name
  uptime_ms: number;    // Time since gymdeck3 started
  error?: string;       // Error message if any
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
  
  // Game Profiles (new in v3.0)
  gameProfiles: GameProfile[];
  activeProfile: GameProfile | null;
  
  // Settings
  settings: Settings;
  dynamicSettings: DynamicSettings;
  
  // Dynamic mode
  gymdeckRunning: boolean;
  isDynamic: boolean;
  dynamicStatus: DynamicStatus | null;
  
  // Autotune state
  autotuneProgress: AutotuneProgress | null;
  autotuneResult: AutotuneResult | null;
  isAutotuning: boolean;
  
  // Binning state
  binningProgress: BinningProgress | null;
  binningResult: BinningResult | null;
  isBinning: boolean;
  binningConfig: BinningConfig | null;
  
  // Test state
  testHistory: TestHistoryEntry[];
  currentTest: string | null;
  isTestRunning: boolean;
  
  // Benchmark state (new in v3.0)
  benchmarkHistory: BenchmarkResult[];
  isBenchmarkRunning: boolean;
  lastBenchmarkResult: BenchmarkResult | null;
  
  // Telemetry state (new in v3.1)
  // Requirements: 2.1, 2.2, 2.3, 2.4
  telemetrySamples: TelemetrySample[];
  
  // Binary availability (for SteamOS compatibility warnings)
  missingBinaries: string[];
  
  // Frequency wizard state (new in v3.2)
  frequencyModeEnabled: boolean;
  frequencyCurves: Record<number, FrequencyCurve>; // Keyed by core_id
  frequencyWizardProgress: FrequencyWizardProgress | null;
  isFrequencyWizardRunning: boolean;
}

/**
 * Server event types.
 */
export interface ServerEvent {
  type: "update_status" | "tuning_progress" | "tuning_complete" | "test_complete";
  data: any;
}

/**
 * Binning configuration for silicon limit discovery.
 */
export interface BinningConfig {
  start_value: number;      // Starting undervolt (mV), default -10
  step_size: number;        // Step increment (mV), default 5
  test_duration: number;    // Test duration per iteration (seconds), default 60
  max_iterations: number;   // Safety limit, default 20
  consecutive_fail_limit: number;  // Abort after N consecutive failures, default 3
}

/**
 * Binning state for crash recovery.
 */
export interface BinningState {
  active: boolean;          // Is binning currently running?
  current_value: number;    // Value being tested
  last_stable: number;      // Last value that passed
  iteration: number;        // Current iteration number
  failed_values: number[];  // Values that failed
  timestamp: string;        // ISO timestamp
}

/**
 * Binning result after completion.
 */
export interface BinningResult {
  max_stable: number;       // Maximum stable value found
  recommended: number;      // Recommended value (max_stable + 5mV safety margin)
  iterations: number;       // Number of iterations run
  duration: number;         // Total time in seconds
  aborted: boolean;         // True if aborted early
}

/**
 * Binning progress event data.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
 */
export interface BinningProgress {
  current_value: number;    // Value being tested
  iteration: number;        // Current iteration number
  last_stable: number;      // Last successful value
  eta: number;              // Estimated time remaining in seconds
  max_iterations: number;   // Maximum number of iterations
  percent_complete: number; // Progress percentage (0-100)
}

/**
 * Game profile configuration for per-game settings.
 * Requirements: 3.1
 */
export interface GameProfile {
  app_id: number;           // Steam AppID
  name: string;             // Game name (from Steam)
  cores: number[];          // Undervolt values [core0, core1, core2, core3]
  dynamic_enabled: boolean; // Use dynamic mode?
  dynamic_config: DynamicSettings | null;  // Dynamic mode settings
  created_at: string;       // ISO timestamp
  last_used: string | null; // Last time profile was applied
}

/**
 * Profile import result.
 */
export interface ProfileImportResult {
  success: boolean;
  imported_count: number;
  conflicts: number[];      // AppIDs that conflicted
  error?: string;
}

/**
 * Benchmark result from stress-ng execution.
 * Requirements: 7.1, 7.2, 7.5
 */
export interface BenchmarkResult {
  score: number;            // Operations per second (bogo ops/s)
  duration: number;         // Actual test duration in seconds
  cores_used: number[];     // Undervolt values during test [core0, core1, core2, core3]
  timestamp: string;        // ISO timestamp
}

/**
 * Benchmark comparison result.
 * Requirements: 7.3
 */
export interface BenchmarkComparison {
  score_diff: number;       // Difference in scores (current - baseline)
  percent_change: number;   // Percentage change ((current - baseline) / baseline * 100)
  improvement: boolean;     // True if current score is better than baseline
}

/**
 * RPC response types.
 */
export interface RpcResponse<T = any> {
  success: boolean;
  error?: string;
  data?: T;
}

/**
 * Fan curve point (temperature -> speed).
 * Requirements: Fan Control Integration
 */
export interface FanCurvePoint {
  temp_c: number;
  speed_percent: number;
}

/**
 * Fan control configuration.
 * Requirements: Fan Control Integration
 */
export interface FanConfig {
  enabled: boolean;
  mode: "default" | "custom" | "fixed";
  curve: FanCurvePoint[];
  zero_rpm_enabled: boolean;
  hysteresis_temp: number;
}

/**
 * Fan status from gymdeck3.
 * Requirements: Fan Control Integration
 */
export interface FanStatus {
  temp_c: number;
  pwm: number;
  speed_percent: number;
  mode: string;
  rpm?: number;
  safety_override: boolean;
}

/**
 * Telemetry sample for real-time monitoring.
 * Requirements: 2.1, 2.2
 */
export interface TelemetrySample {
  timestamp: number;       // Unix timestamp
  temperature_c: number;   // CPU temperature in Celsius
  power_w: number;         // Power consumption in Watts
  load_percent: number;    // CPU load percentage (0-100)
}


/**
 * Session metrics calculated after session completion.
 * Requirements: 8.3
 */
export interface SessionMetrics {
  duration_sec: number;              // Total session duration in seconds
  avg_temperature_c: number;         // Average CPU temperature
  min_temperature_c: number;         // Minimum CPU temperature
  max_temperature_c: number;         // Maximum CPU temperature
  avg_power_w: number;               // Average power consumption
  estimated_battery_saved_wh: number; // Estimated battery savings
  undervolt_values: number[];        // Undervolt values used during session
}

/**
 * Telemetry sample data stored in session.
 * Requirements: 8.5
 */
export interface SessionTelemetrySample {
  timestamp: number;       // Unix timestamp
  temperature_c: number;   // CPU temperature
  power_w: number;         // Power consumption
}

/**
 * Gaming session record with metrics.
 * Requirements: 8.1, 8.3, 8.4, 8.5
 */
export interface Session {
  id: string;                        // UUID
  start_time: string;                // ISO 8601 format
  end_time: string | null;           // ISO 8601 format, null if active
  game_name: string | null;          // Game name
  app_id: number | null;             // Steam app ID
  metrics: SessionMetrics | null;    // Calculated metrics (null if active)
  samples: SessionTelemetrySample[]; // Raw telemetry data for graphs
}

/**
 * Session comparison result with metric differences.
 * Requirements: 8.6
 */
export interface SessionComparison {
  session1: Session;
  session2: Session;
  diff: {
    duration_sec: number;
    avg_temperature_c: number;
    min_temperature_c: number;
    max_temperature_c: number;
    avg_power_w: number;
    estimated_battery_saved_wh: number;
  };
}

/**
 * Frequency point in a frequency-voltage curve.
 * Requirements: 1.3
 */
export interface FrequencyPoint {
  frequency_mhz: number;    // CPU frequency in MHz
  voltage_mv: number;       // Voltage offset in mV (negative)
  stable: boolean;          // Whether this point passed stability test
  test_duration: number;    // Duration tested in seconds
  timestamp: number;        // Unix timestamp when tested
}

/**
 * Frequency-voltage curve for a CPU core.
 * Requirements: 1.3, 1.5, 2.2
 */
export interface FrequencyCurve {
  core_id: number;          // CPU core ID
  points: FrequencyPoint[]; // Frequency-voltage points
  created_at: number;       // Unix timestamp
  wizard_config: FrequencyWizardConfig; // Configuration used to generate
}

/**
 * Frequency wizard configuration.
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
 */
export interface FrequencyWizardConfig {
  freq_start: number;       // Starting frequency in MHz (400-3500)
  freq_end: number;         // Ending frequency in MHz (> freq_start)
  freq_step: number;        // Frequency step in MHz (50-500)
  test_duration: number;    // Test duration per frequency in seconds (10-120)
  voltage_start: number;    // Starting voltage offset in mV (-100 to 0)
  voltage_step: number;     // Voltage step in mV (1-10)
  safety_margin: number;    // Safety margin in mV (0-20)
}

/**
 * Frequency wizard progress data.
 * Requirements: 4.1, 4.2, 4.3, 4.4
 */
export interface FrequencyWizardProgress {
  running: boolean;         // Is wizard currently running?
  current_frequency: number; // Current frequency being tested (MHz)
  current_voltage: number;  // Current voltage being tested (mV)
  progress_percent: number; // Progress percentage (0-100)
  estimated_remaining: number; // Estimated time remaining in seconds
  completed_points: number; // Number of frequency points completed
  total_points: number;     // Total number of frequency points to test
}
