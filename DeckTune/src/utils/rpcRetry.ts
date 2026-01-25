/**
 * RPC retry utility with exponential backoff.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: Error handling with retry logic
 * 
 * Provides automatic retry logic for RPC calls with exponential backoff
 * to handle transient network errors and connection issues.
 */

import { RPCRetryConfig } from '../types/DynamicMode';

/**
 * Default retry configuration.
 * - 3 retry attempts
 * - 500ms initial delay
 * - 2x backoff multiplier (500ms, 1000ms, 2000ms)
 * - 5000ms maximum delay
 */
export const DEFAULT_RETRY_CONFIG: RPCRetryConfig = {
  maxRetries: 3,
  initialDelay: 500,
  backoffMultiplier: 2,
  maxDelay: 5000,
};

/**
 * Sleep for a specified duration.
 * 
 * @param ms - Duration in milliseconds
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Calculate delay for a retry attempt using exponential backoff.
 * 
 * @param attempt - Current attempt number (0-indexed)
 * @param config - Retry configuration
 * @returns Delay in milliseconds
 */
const calculateDelay = (attempt: number, config: RPCRetryConfig): number => {
  const delay = config.initialDelay * Math.pow(config.backoffMultiplier, attempt);
  return Math.min(delay, config.maxDelay);
};

/**
 * Determine if an error is retryable.
 * 
 * Retryable errors include:
 * - Network errors (connection lost, timeout)
 * - Temporary server errors (503, 504)
 * - RPC errors marked as recoverable
 * 
 * Non-retryable errors include:
 * - Validation errors (400)
 * - Permission errors (403)
 * - Not found errors (404)
 * - Hardware errors
 * 
 * @param error - Error object
 * @returns True if error is retryable
 */
const isRetryableError = (error: any): boolean => {
  // Network errors
  if (error.message?.includes('network') || 
      error.message?.includes('timeout') ||
      error.message?.includes('connection')) {
    return true;
  }
  
  // RPC errors with recoverable flag
  if (error.recoverable === true) {
    return true;
  }
  
  // HTTP status codes
  if (error.status) {
    // Retry on 503 (Service Unavailable) and 504 (Gateway Timeout)
    if (error.status === 503 || error.status === 504) {
      return true;
    }
    
    // Don't retry on client errors (4xx) or hardware errors
    if (error.status >= 400 && error.status < 500) {
      return false;
    }
  }
  
  // Hardware errors are not retryable
  if (error.code === 'HARDWARE_ERROR' || error.message?.includes('hardware')) {
    return false;
  }
  
  // Default to retryable for unknown errors
  return true;
};

/**
 * Execute an RPC call with automatic retry logic.
 * 
 * Retries the operation up to maxRetries times with exponential backoff
 * if the error is retryable. Logs retry attempts for debugging.
 * 
 * @param operation - Async function to execute
 * @param config - Retry configuration (optional, uses defaults)
 * @param operationName - Name for logging (optional)
 * @returns Promise resolving to operation result
 * @throws Last error if all retries fail
 * 
 * @example
 * ```typescript
 * const result = await withRetry(
 *   () => api.callPluginMethod('get_dynamic_config', {}),
 *   undefined,
 *   'get_dynamic_config'
 * );
 * ```
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  config: RPCRetryConfig = DEFAULT_RETRY_CONFIG,
  operationName: string = 'RPC call'
): Promise<T> {
  let lastError: any;
  
  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      // Execute the operation
      const result = await operation();
      
      // Log successful retry
      if (attempt > 0) {
        console.log(`[RPCRetry] ${operationName} succeeded on attempt ${attempt + 1}`);
      }
      
      return result;
    } catch (error) {
      lastError = error;
      
      // Check if we should retry
      const shouldRetry = attempt < config.maxRetries && isRetryableError(error);
      
      if (shouldRetry) {
        const delay = calculateDelay(attempt, config);
        console.warn(
          `[RPCRetry] ${operationName} failed (attempt ${attempt + 1}/${config.maxRetries + 1}), ` +
          `retrying in ${delay}ms:`,
          error
        );
        
        await sleep(delay);
      } else {
        // No more retries or non-retryable error
        if (attempt >= config.maxRetries) {
          console.error(
            `[RPCRetry] ${operationName} failed after ${config.maxRetries + 1} attempts:`,
            error
          );
        } else {
          console.error(
            `[RPCRetry] ${operationName} failed with non-retryable error:`,
            error
          );
        }
        
        throw error;
      }
    }
  }
  
  // Should never reach here, but TypeScript needs it
  throw lastError;
}

/**
 * Create a retry wrapper for an API object.
 * 
 * Returns a proxy that automatically wraps all method calls with retry logic.
 * 
 * @param api - API object to wrap
 * @param config - Retry configuration (optional)
 * @returns Proxied API object with retry logic
 * 
 * @example
 * ```typescript
 * const apiWithRetry = createRetryWrapper(api);
 * const result = await apiWithRetry.callPluginMethod('get_dynamic_config', {});
 * ```
 */
export function createRetryWrapper<T extends object>(
  api: T,
  config: RPCRetryConfig = DEFAULT_RETRY_CONFIG
): T {
  return new Proxy(api, {
    get(target, prop) {
      const original = (target as any)[prop];
      
      // Only wrap functions
      if (typeof original !== 'function') {
        return original;
      }
      
      // Return wrapped function with retry logic
      return function(this: any, ...args: any[]) {
        return withRetry(
          () => original.apply(target, args),
          config,
          `${String(prop)}`
        );
      };
    }
  });
}
