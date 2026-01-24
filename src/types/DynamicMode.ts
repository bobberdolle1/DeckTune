/**
 * Type definitions for Dynamic Manual Mode feature.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 1.1, 1.2, 1.3, 1.4
 */

/**
 * Core configuration for dynamic voltage control.
 * Defines the voltage curve parameters for a single CPU core.
 * 
 * Requirements: 1.1, 1.2, 1.3, 1.4
 */
export interface CoreConfig {
  /** Core identifier (0-3 for typical AMD APU) */
  core_id: number;
  
  /** Minimum voltage offset in millivolts (range: -100 to 0) */
  min_mv: number;
  
  /** Maximum voltage offset in millivolts (range: -100 to 0) */
  max_mv: number;
  
  /** CPU load threshold percentage where voltage transitions occur (range: 0 to 100) */
  threshold: number;
}

/**
 * Complete dynamic mode configuration.
 * Contains settings for all cores and operational mode.
 * 
 * Requirements: 1.1, 4.1
 */
export interface DynamicConfig {
  /** Configuration mode: 'simple' applies same settings to all cores, 'expert' allows per-core config */
  mode: 'simple' | 'expert';
  
  /** Array of per-core configurations (length: 4 for typical AMD APU) */
  cores: CoreConfig[];
  
  /** Configuration version for migration compatibility */
  version: number;
}

/**
 * Real-time metrics for a single CPU core.
 * Updated every 500ms when dynamic mode is active.
 * 
 * Requirements: 3.1, 3.2, 3.3
 */
export interface CoreMetrics {
  /** Core identifier (0-3) */
  core_id: number;
  
  /** CPU load percentage (0-100) */
  load: number;
  
  /** Current voltage offset in millivolts */
  voltage: number;
  
  /** CPU frequency in megahertz */
  frequency: number;
  
  /** Core temperature in Celsius */
  temperature: number;
  
  /** Unix timestamp when metrics were captured */
  timestamp: number;
}

/**
 * Single point on the voltage curve for visualization.
 * Represents the voltage offset at a specific CPU load.
 * 
 * Requirements: 2.1, 2.4, 2.5
 */
export interface CurvePoint {
  /** CPU load percentage (0-100) */
  load: number;
  
  /** Voltage offset in millivolts (-100 to 0) */
  voltage: number;
}

/**
 * RPC request to retrieve current dynamic mode configuration.
 * 
 * Requirements: 9.1
 */
export interface GetDynamicConfigRequest {
  method: 'get_dynamic_config';
  params: Record<string, never>; // No parameters
}

/**
 * RPC response containing dynamic mode configuration.
 * 
 * Requirements: 9.1
 */
export interface GetDynamicConfigResponse {
  success: boolean;
  data?: DynamicConfig;
  error?: string;
}

/**
 * RPC request to update configuration for a specific core.
 * 
 * Requirements: 9.2
 */
export interface SetDynamicCoreConfigRequest {
  method: 'set_dynamic_core_config';
  params: {
    core_id: number;
    min_mv: number;
    max_mv: number;
    threshold: number;
  };
}

/**
 * RPC response for core configuration update.
 * 
 * Requirements: 9.2
 */
export interface SetDynamicCoreConfigResponse {
  success: boolean;
  error?: string;
}

/**
 * RPC request to retrieve voltage curve data for visualization.
 * 
 * Requirements: 9.3
 */
export interface GetDynamicCurveDataRequest {
  method: 'get_dynamic_curve_data';
  params: {
    core_id: number;
  };
}

/**
 * RPC response containing voltage curve points.
 * 
 * Requirements: 9.3
 */
export interface GetDynamicCurveDataResponse {
  success: boolean;
  data?: CurvePoint[];
  error?: string;
}

/**
 * RPC request to start dynamic voltage mode.
 * 
 * Requirements: 5.1, 9.5
 */
export interface StartDynamicModeRequest {
  method: 'start_dynamic_mode';
  params: {
    config: DynamicConfig;
  };
}

/**
 * RPC response for starting dynamic mode.
 * 
 * Requirements: 5.1, 9.5
 */
export interface StartDynamicModeResponse {
  success: boolean;
  error?: string;
}

/**
 * RPC request to stop dynamic voltage mode.
 * 
 * Requirements: 5.3
 */
export interface StopDynamicModeRequest {
  method: 'stop_dynamic_mode';
  params: Record<string, never>; // No parameters
}

/**
 * RPC response for stopping dynamic mode.
 * 
 * Requirements: 5.3
 */
export interface StopDynamicModeResponse {
  success: boolean;
  error?: string;
}

/**
 * RPC request to retrieve real-time metrics for a core.
 * 
 * Requirements: 3.1, 9.4
 */
export interface GetCoreMetricsRequest {
  method: 'get_core_metrics';
  params: {
    core_id: number;
  };
}

/**
 * RPC response containing core metrics.
 * 
 * Requirements: 3.2, 9.4
 */
export interface GetCoreMetricsResponse {
  success: boolean;
  data?: CoreMetrics;
  error?: string;
}

/**
 * Union type of all dynamic mode RPC requests.
 */
export type DynamicModeRPCRequest =
  | GetDynamicConfigRequest
  | SetDynamicCoreConfigRequest
  | GetDynamicCurveDataRequest
  | StartDynamicModeRequest
  | StopDynamicModeRequest
  | GetCoreMetricsRequest;

/**
 * Union type of all dynamic mode RPC responses.
 */
export type DynamicModeRPCResponse =
  | GetDynamicConfigResponse
  | SetDynamicCoreConfigResponse
  | GetDynamicCurveDataResponse
  | StartDynamicModeResponse
  | StopDynamicModeResponse
  | GetCoreMetricsResponse;

/**
 * Validation error for configuration issues.
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4
 */
export interface ValidationError {
  /** Field that failed validation */
  field: 'min_mv' | 'max_mv' | 'threshold' | 'config';
  
  /** Human-readable error message */
  message: string;
  
  /** Error code for programmatic handling */
  code: ValidationErrorCode;
  
  /** Core ID if error is specific to a core */
  core_id?: number;
}

/**
 * Validation error codes for different failure types.
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4
 */
export enum ValidationErrorCode {
  /** Minimum voltage is greater than maximum voltage */
  MIN_GREATER_THAN_MAX = 'MIN_GREATER_THAN_MAX',
  
  /** Voltage value is below platform minimum limit */
  BELOW_PLATFORM_MIN = 'BELOW_PLATFORM_MIN',
  
  /** Voltage value is above 0mV */
  ABOVE_ZERO = 'ABOVE_ZERO',
  
  /** Threshold is outside valid range (0-100) */
  INVALID_THRESHOLD = 'INVALID_THRESHOLD',
  
  /** Configuration exceeds platform safety limits */
  EXCEEDS_SAFETY_LIMIT = 'EXCEEDS_SAFETY_LIMIT',
  
  /** Invalid core ID */
  INVALID_CORE_ID = 'INVALID_CORE_ID',
  
  /** Generic validation failure */
  VALIDATION_FAILED = 'VALIDATION_FAILED',
}

/**
 * Result of configuration validation.
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4
 */
export interface ValidationResult {
  /** Whether the configuration is valid */
  valid: boolean;
  
  /** Array of validation errors (empty if valid) */
  errors: ValidationError[];
  
  /** Array of non-blocking warnings */
  warnings?: string[];
}

/**
 * Platform-specific voltage limits.
 * 
 * Requirements: 7.2, 7.3
 */
export interface PlatformLimits {
  /** Minimum allowed voltage offset in millivolts */
  min_voltage_mv: number;
  
  /** Maximum allowed voltage offset in millivolts (always 0) */
  max_voltage_mv: number;
  
  /** Number of CPU cores */
  core_count: number;
  
  /** Platform model identifier */
  model: string;
}

/**
 * Safe default configuration values.
 * 
 * Requirements: 7.5
 */
export interface SafeDefaults {
  /** Default minimum voltage offset (-30mV) */
  min_mv: number;
  
  /** Default maximum voltage offset (-15mV) */
  max_mv: number;
  
  /** Default threshold (50%) */
  threshold: number;
}

/**
 * Last Known Good (LKG) configuration for recovery.
 * 
 * Requirements: 7.4
 */
export interface LastKnownGoodConfig {
  /** Configuration that was stable */
  config: DynamicConfig;
  
  /** Timestamp when configuration was marked as stable */
  timestamp: number;
  
  /** Duration in seconds that configuration was stable */
  stable_duration: number;
}

/**
 * RPC retry configuration.
 * 
 * Requirements: Error handling with retry logic
 */
export interface RPCRetryConfig {
  /** Maximum number of retry attempts */
  maxRetries: number;
  
  /** Initial delay in milliseconds */
  initialDelay: number;
  
  /** Backoff multiplier for exponential backoff */
  backoffMultiplier: number;
  
  /** Maximum delay in milliseconds */
  maxDelay: number;
}

/**
 * Connection status for error banners.
 * 
 * Requirements: Error banners for connection issues
 */
export enum ConnectionStatus {
  /** Connected and operational */
  CONNECTED = 'CONNECTED',
  
  /** Attempting to reconnect */
  RECONNECTING = 'RECONNECTING',
  
  /** Connection lost */
  DISCONNECTED = 'DISCONNECTED',
  
  /** Hardware error detected */
  HARDWARE_ERROR = 'HARDWARE_ERROR',
}

/**
 * RPC error response structure.
 * 
 * Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
 */
export interface RPCError {
  /** Error code for programmatic handling */
  code: string;
  
  /** Human-readable error message */
  message: string;
  
  /** Whether the error is recoverable with retry */
  recoverable: boolean;
  
  /** Additional error details */
  details?: Record<string, any>;
}
