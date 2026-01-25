/**
 * DynamicManualMode component for per-core dynamic voltage control.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 1.5, 4.1, 5.1, 5.2, 5.3, 5.4
 * 
 * Provides granular per-core dynamic voltage configuration with:
 * - Simple Mode: Unified controls for all cores
 * - Expert Mode: Per-core configuration
 * - Real-time voltage curve visualization
 * - Live metrics monitoring (500ms polling)
 * - Configuration persistence (localStorage + backend)
 * - Safety validation and error handling
 */

import React, { FC, useState, useEffect, useCallback, useRef } from "react";
import {
  PanelSection,
  PanelSectionRow,
  Focusable,
} from "@decky/ui";
import { FaPlay, FaStop, FaSpinner, FaExclamationTriangle, FaUndo } from "react-icons/fa";
import { useApi } from "../context";
import {
  DynamicConfig,
  CoreConfig,
  CoreMetrics,
  ValidationError,
  ConnectionStatus,
} from "../types/DynamicMode";
import { FocusableButton } from "./FocusableButton";
import { CoreTabs } from "./CoreTabs";
import { VoltageSliders } from "./VoltageSliders";
import { withRetry, DEFAULT_RETRY_CONFIG } from "../utils/rpcRetry";
import { 
  loadLKG, 
  saveLKG, 
  StabilityTracker,
  isStableEnoughForLKG 
} from "../utils/lkgStorage";

/**
 * Safe default configuration values.
 * Requirements: 7.5
 */
const SAFE_DEFAULTS: Omit<CoreConfig, 'core_id'> = {
  min_mv: -30,
  max_mv: -15,
  threshold: 50,
};

/**
 * Create default configuration for all cores.
 */
const createDefaultConfig = (): DynamicConfig => ({
  mode: 'simple',
  cores: [0, 1, 2, 3].map(core_id => ({
    core_id,
    ...SAFE_DEFAULTS,
  })),
  version: 1,
});

/**
 * DynamicManualMode error boundary wrapper.
 * Requirements: Error handling
 * 
 * Catches React errors and provides recovery options:
 * - Retry: Attempt to re-render the component
 * - Restore LKG: Load Last Known Good configuration
 * - Reset: Reset to safe defaults
 */
class DynamicModeErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[DynamicManualMode] Error caught by boundary:', error, errorInfo);
    
    // Log to backend for diagnostics
    try {
      // TODO: Send error report to backend
      console.error('[DynamicManualMode] Error details:', {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      });
    } catch (e) {
      console.error('[DynamicManualMode] Failed to log error:', e);
    }
  }
  
  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };
  
  handleRestoreLKG = () => {
    try {
      const lkg = loadLKG();
      if (lkg) {
        // Save LKG config to localStorage for component to load
        localStorage.setItem('dynamicMode', JSON.stringify(lkg.config));
        console.log('[DynamicManualMode] Restored Last Known Good config');
      }
    } catch (e) {
      console.error('[DynamicManualMode] Failed to restore LKG:', e);
    }
    
    this.setState({ hasError: false, error: null });
  };
  
  handleReset = () => {
    try {
      // Clear localStorage to force safe defaults
      localStorage.removeItem('dynamicMode');
      console.log('[DynamicManualMode] Reset to safe defaults');
    } catch (e) {
      console.error('[DynamicManualMode] Failed to reset:', e);
    }
    
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <PanelSection title="Dynamic Manual Mode">
          <PanelSectionRow>
            <div style={{
              padding: '16px',
              backgroundColor: '#b71c1c',
              borderRadius: '8px',
              color: '#fff',
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                fontWeight: 'bold', 
                marginBottom: '8px' 
              }}>
                <FaExclamationTriangle />
                <span>Error Loading Dynamic Mode</span>
              </div>
              <div style={{ fontSize: '12px', marginBottom: '12px' }}>
                {this.state.error?.message || 'Unknown error'}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <FocusableButton
                  onClick={this.handleRetry}
                  style={{ width: '100%' }}
                >
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#1a9fff',
                    borderRadius: '6px',
                    textAlign: 'center',
                    fontWeight: 'bold',
                    fontSize: '11px',
                  }}>
                    Retry
                  </div>
                </FocusableButton>
                <FocusableButton
                  onClick={this.handleRestoreLKG}
                  style={{ width: '100%' }}
                >
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#ff9800',
                    borderRadius: '6px',
                    textAlign: 'center',
                    fontWeight: 'bold',
                    fontSize: '11px',
                  }}>
                    Restore Last Stable
                  </div>
                </FocusableButton>
                <FocusableButton
                  onClick={this.handleReset}
                  style={{ width: '100%' }}
                >
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#3d4450',
                    borderRadius: '6px',
                    textAlign: 'center',
                    fontWeight: 'bold',
                    fontSize: '11px',
                  }}>
                    Reset to Defaults
                  </div>
                </FocusableButton>
              </div>
            </div>
          </PanelSectionRow>
        </PanelSection>
      );
    }

    return this.props.children;
  }
}

/**
 * Main DynamicManualMode component.
 * Requirements: 1.5, 4.1, 5.1, 5.2, 5.3, 5.4, 8.1, 8.2, 8.3, 8.4, 8.5
 */
const DynamicManualModeInternal: FC = () => {
  const api = useApi();
  
  // Component state
  const [config, setConfig] = useState<DynamicConfig>(createDefaultConfig());
  const [selectedCore, setSelectedCore] = useState<number>(0);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [metrics, setMetrics] = useState<Map<number, CoreMetrics>>(new Map());
  const [showDangerWarning, setShowDangerWarning] = useState<boolean>(false);
  const [platformLimits, setPlatformLimits] = useState<{ min: number; max: number }>({ min: -100, max: 0 });
  
  // Connection status tracking
  // Requirements: Error banners for connection issues
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.CONNECTED);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  
  // LKG tracking
  // Requirements: 7.4 - Last Known Good configuration
  const stabilityTrackerRef = useRef<StabilityTracker>(new StabilityTracker());
  const [hasLKG, setHasLKG] = useState<boolean>(false);
  
  // Gamepad navigation state
  // Requirements: 8.1, 8.2, 8.3, 8.5
  const [focusedSlider, setFocusedSlider] = useState<'min' | 'max' | 'threshold' | null>(null);
  
  // Polling interval ref
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  /**
   * Load configuration and platform limits on mount.
   * Requirements: 6.1, 6.3, 6.4, 7.2, 7.3
   * 
   * Property 10: Configuration persistence round-trip
   * Loads configuration with fallback chain: localStorage → backend → safe defaults
   * 
   * Enhanced with:
   * - RPC retry logic for transient errors
   * - Connection status tracking
   * - LKG availability check
   */
  useEffect(() => {
    const loadConfig = async () => {
      setIsLoading(true);
      setConnectionStatus(ConnectionStatus.CONNECTED);
      
      try {
        // Check if LKG is available
        const lkg = loadLKG();
        setHasLKG(lkg !== null);
        
        // Load platform limits first with retry logic
        // Requirements: 7.2, 7.3
        try {
          const limitsResponse = await withRetry(
            () => api.callPluginMethod<{
              success: boolean;
              limits?: { min: number; max: number };
            }>('get_platform_limits', {}),
            DEFAULT_RETRY_CONFIG,
            'get_platform_limits'
          );
          
          if (limitsResponse.success && limitsResponse.limits) {
            setPlatformLimits(limitsResponse.limits);
            console.log('[DynamicManualMode] Platform limits:', limitsResponse.limits);
          }
        } catch (limitsError) {
          console.warn('[DynamicManualMode] Failed to load platform limits, using defaults:', limitsError);
          // Don't fail the entire load - continue with defaults
        }
        
        // Try localStorage first
        // Requirements: 6.3
        try {
          const storedConfig = localStorage.getItem('dynamicMode');
          if (storedConfig) {
            const parsed = JSON.parse(storedConfig) as DynamicConfig;
            // Validate the loaded config has required structure
            if (parsed.cores && Array.isArray(parsed.cores) && parsed.cores.length === 4) {
              setConfig(parsed);
              console.log('[DynamicManualMode] Loaded config from localStorage');
              setConnectionStatus(ConnectionStatus.CONNECTED);
              return;
            } else {
              console.warn('[DynamicManualMode] Invalid localStorage config structure, falling back');
            }
          }
        } catch (localStorageError) {
          // Handle localStorage errors gracefully
          // Requirements: 6.4
          console.warn('[DynamicManualMode] localStorage error:', localStorageError);
          // Continue to backend fallback
        }
        
        // Fallback to backend with retry logic
        // Requirements: 6.4
        try {
          const response = await withRetry(
            () => api.callPluginMethod<{ success: boolean; config?: DynamicConfig }>(
              'get_dynamic_config',
              {}
            ),
            DEFAULT_RETRY_CONFIG,
            'get_dynamic_config'
          );
          
          if (response.success && response.config) {
            setConfig(response.config);
            console.log('[DynamicManualMode] Loaded config from backend');
            setConnectionStatus(ConnectionStatus.CONNECTED);
            return;
          }
        } catch (backendError: any) {
          console.warn('[DynamicManualMode] Backend load error:', backendError);
          
          // Update connection status based on error type
          if (backendError.message?.includes('network') || 
              backendError.message?.includes('connection')) {
            setConnectionStatus(ConnectionStatus.DISCONNECTED);
            setConnectionError('Connection to backend lost');
          } else if (backendError.message?.includes('hardware')) {
            setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
            setConnectionError('Hardware error detected');
          }
          
          // Continue to safe defaults
        }
        
        // Use safe defaults if both localStorage and backend fail
        // Requirements: 6.4
        setConfig(createDefaultConfig());
        console.log('[DynamicManualMode] Using safe defaults');
      } catch (e: any) {
        console.error('[DynamicManualMode] Failed to load config:', e);
        setConfig(createDefaultConfig());
        setConnectionStatus(ConnectionStatus.DISCONNECTED);
        setConnectionError(e.message || 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadConfig();
    
    // Cleanup stability tracker on unmount
    return () => {
      stabilityTrackerRef.current.stop();
    };
  }, [api]);
  
  /**
   * Start metrics polling when active.
   * Requirements: 3.1, 3.5
   * 
   * Enhanced with:
   * - Connection error handling
   * - Automatic reconnection attempts
   */
  useEffect(() => {
    if (isActive) {
      // Start polling
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const response = await api.callPluginMethod<{
            success: boolean;
            metrics?: CoreMetrics;
            error?: string;
          }>('get_core_metrics', { core_id: selectedCore });
          
          if (response.success && response.metrics) {
            setMetrics(prev => {
              const updated = new Map(prev);
              updated.set(selectedCore, response.metrics!);
              return updated;
            });
            
            // Clear connection errors on successful poll
            if (connectionStatus !== ConnectionStatus.CONNECTED) {
              setConnectionStatus(ConnectionStatus.CONNECTED);
              setConnectionError(null);
              console.log('[DynamicManualMode] Connection restored');
            }
          } else {
            // Handle RPC error response
            if (response.error?.includes('hardware')) {
              setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
              setConnectionError(response.error);
            }
          }
        } catch (e: any) {
          console.error('[DynamicManualMode] Failed to poll metrics:', e);
          
          // Update connection status based on error
          if (e.message?.includes('network') || e.message?.includes('connection')) {
            if (connectionStatus === ConnectionStatus.CONNECTED) {
              setConnectionStatus(ConnectionStatus.RECONNECTING);
              setConnectionError('Connection lost, attempting to reconnect...');
            }
          } else if (e.message?.includes('hardware')) {
            setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
            setConnectionError('Hardware error detected');
            
            // Stop dynamic mode on hardware error
            handleStop();
          }
        }
      }, 500);
    } else {
      // Stop polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
    
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [isActive, selectedCore, api, connectionStatus]);
  
  /**
   * Validate current configuration.
   * Requirements: 7.1, 7.2, 7.3
   * 
   * Returns validation errors if configuration is invalid.
   */
  const validateConfig = useCallback((): ValidationError[] => {
    const errors: ValidationError[] = [];
    const coresToValidate = config.mode === 'simple' ? [config.cores[0]] : config.cores;
    
    for (const core of coresToValidate) {
      // Check min <= max ordering
      // Requirements: 7.1
      // Property 12: Validation min-max ordering
      if (core.min_mv > core.max_mv) {
        errors.push({
          field: 'config',
          message: `Core ${core.core_id}: Minimal Value (${core.min_mv}mV) must be ≤ Maximum Value (${core.max_mv}mV)`,
          code: 'MIN_GREATER_THAN_MAX' as any,
          core_id: core.core_id,
        });
      }
      
      // Check platform limits
      // Requirements: 7.2, 7.3
      // Property 13: Voltage lower bound clamping
      // Property 14: Voltage upper bound clamping
      if (core.min_mv < platformLimits.min) {
        errors.push({
          field: 'min_mv',
          message: `Core ${core.core_id}: Minimal Value (${core.min_mv}mV) is below platform limit (${platformLimits.min}mV)`,
          code: 'BELOW_PLATFORM_MIN' as any,
          core_id: core.core_id,
        });
      }
      
      if (core.max_mv < platformLimits.min) {
        errors.push({
          field: 'max_mv',
          message: `Core ${core.core_id}: Maximum Value (${core.max_mv}mV) is below platform limit (${platformLimits.min}mV)`,
          code: 'BELOW_PLATFORM_MIN' as any,
          core_id: core.core_id,
        });
      }
      
      if (core.min_mv > platformLimits.max) {
        errors.push({
          field: 'min_mv',
          message: `Core ${core.core_id}: Minimal Value (${core.min_mv}mV) is above 0mV`,
          code: 'ABOVE_ZERO' as any,
          core_id: core.core_id,
        });
      }
      
      if (core.max_mv > platformLimits.max) {
        errors.push({
          field: 'max_mv',
          message: `Core ${core.core_id}: Maximum Value (${core.max_mv}mV) is above 0mV`,
          code: 'ABOVE_ZERO' as any,
          core_id: core.core_id,
        });
      }
      
      // Check threshold range
      if (core.threshold < 0 || core.threshold > 100) {
        errors.push({
          field: 'threshold',
          message: `Core ${core.core_id}: Threshold (${core.threshold}%) must be between 0 and 100`,
          code: 'INVALID_THRESHOLD' as any,
          core_id: core.core_id,
        });
      }
    }
    
    return errors;
  }, [config, platformLimits]);
  
  /**
   * Check if configuration is dangerous.
   * Requirements: 7.4
   * 
   * A configuration is dangerous if any voltage is below -50mV.
   */
  const isDangerousConfig = useCallback((): boolean => {
    const DANGER_THRESHOLD = -50;
    const coresToCheck = config.mode === 'simple' ? [config.cores[0]] : config.cores;
    
    return coresToCheck.some(core => 
      core.min_mv < DANGER_THRESHOLD || core.max_mv < DANGER_THRESHOLD
    );
  }, [config]);
  
  /**
   * Reset configuration to safe defaults.
   * Requirements: 7.5
   */
  const handleResetToDefaults = useCallback(() => {
    setConfig(createDefaultConfig());
    setValidationErrors([]);
    setError(null);
    setShowDangerWarning(false);
    console.log('[DynamicManualMode] Reset to safe defaults');
  }, []);
  
  /**
   * Restore Last Known Good configuration.
   * Requirements: 7.4
   * 
   * Loads the most recent stable configuration from LKG storage.
   * This is used for error recovery when the current configuration
   * causes issues.
   */
  const handleRestoreLKG = useCallback(() => {
    const lkg = loadLKG();
    
    if (!lkg) {
      setError('No Last Known Good configuration available');
      return;
    }
    
    setConfig(lkg.config);
    setValidationErrors([]);
    setError(null);
    setShowDangerWarning(false);
    
    console.log(
      `[DynamicManualMode] Restored Last Known Good config from ` +
      `${new Date(lkg.timestamp).toLocaleString()} (stable for ${lkg.stable_duration}s)`
    );
  }, []);
  
  /**
   * Handle mode toggle (Simple/Expert).
   * Requirements: 4.1, 4.4, 4.5
   * 
   * Property 8: Mode switching configuration preservation
   * When switching modes, all core configurations are preserved.
   */
  const handleModeToggle = useCallback(() => {
    setConfig(prev => {
      const newMode = prev.mode === 'simple' ? 'expert' : 'simple';
      
      // Configuration is always preserved when switching modes
      // Requirements: 4.4
      // In Simple Mode, we display Core 0's config but all cores retain their values
      // Requirements: 4.5
      
      return { ...prev, mode: newMode };
    });
  }, []);
  
  /**
   * Handle Apply button click.
   * Requirements: 1.5, 6.1, 6.2, 4.3, 7.1, 7.4
   */
  const handleApply = useCallback(async () => {
    // Validate configuration first
    // Requirements: 7.1
    const errors = validateConfig();
    if (errors.length > 0) {
      setValidationErrors(errors);
      setError('Configuration validation failed. Please fix the errors below.');
      return;
    }
    
    // Check for dangerous configuration
    // Requirements: 7.4
    if (isDangerousConfig()) {
      setShowDangerWarning(true);
      return;
    }
    
    // Proceed with applying configuration
    await applyConfiguration();
  }, [validateConfig, isDangerousConfig]);
  
  /**
   * Apply configuration after validation passes.
   * Requirements: 1.5, 6.1, 6.2, 4.3
   * 
   * Enhanced with:
   * - RPC retry logic for transient errors
   * - Connection status tracking
   * - Hardware error handling
   */
  const applyConfiguration = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setValidationErrors([]);
    setShowDangerWarning(false);
    setConnectionStatus(ConnectionStatus.CONNECTED);
    
    try {
      if (config.mode === 'simple') {
        // In Simple Mode, apply Core 0's config to all cores
        // Requirements: 4.3
        // Property 7: Simple mode configuration uniformity
        const coreConfig = config.cores[0];
        
        const response = await withRetry(
          () => api.callPluginMethod<{
            success: boolean;
            error?: string;
            validation_errors?: string[];
          }>('set_all_cores_config', {
            min_mv: coreConfig.min_mv,
            max_mv: coreConfig.max_mv,
            threshold: coreConfig.threshold,
          }),
          DEFAULT_RETRY_CONFIG,
          'set_all_cores_config'
        );
        
        if (!response.success) {
          setError(response.error || 'Failed to apply configuration');
          if (response.validation_errors) {
            const errors: ValidationError[] = response.validation_errors.map((msg: string) => ({
              field: 'config',
              message: msg,
              code: 'VALIDATION_FAILED' as any,
            }));
            setValidationErrors(errors);
          }
          return;
        }
      } else {
        // In Expert Mode, apply configuration for each core
        for (const coreConfig of config.cores) {
          const response = await withRetry(
            () => api.callPluginMethod<{
              success: boolean;
              error?: string;
              validation_errors?: string[];
            }>('set_dynamic_core_config', {
              core_id: coreConfig.core_id,
              min_mv: coreConfig.min_mv,
              max_mv: coreConfig.max_mv,
              threshold: coreConfig.threshold,
            }),
            DEFAULT_RETRY_CONFIG,
            `set_dynamic_core_config (core ${coreConfig.core_id})`
          );
          
          if (!response.success) {
            setError(response.error || 'Failed to apply configuration');
            if (response.validation_errors) {
              const errors: ValidationError[] = response.validation_errors.map((msg: string) => ({
                field: 'config',
                message: msg,
                code: 'VALIDATION_FAILED' as any,
                core_id: coreConfig.core_id,
              }));
              setValidationErrors(errors);
            }
            return;
          }
        }
      }
      
      // Save to localStorage
      // Requirements: 6.1
      // Property 10: Configuration persistence round-trip
      try {
        localStorage.setItem('dynamicMode', JSON.stringify(config));
        console.log('[DynamicManualMode] Configuration saved to localStorage');
      } catch (localStorageError) {
        // Handle localStorage errors gracefully (e.g., quota exceeded, private browsing)
        // Requirements: 6.4
        console.warn('[DynamicManualMode] Failed to save to localStorage:', localStorageError);
        // Don't fail the entire operation - backend save already succeeded
      }
      
      console.log('[DynamicManualMode] Configuration applied successfully');
      setConnectionStatus(ConnectionStatus.CONNECTED);
    } catch (e: any) {
      console.error('[DynamicManualMode] Failed to apply config:', e);
      setError(e.message || 'Unknown error');
      
      // Update connection status based on error type
      if (e.message?.includes('network') || e.message?.includes('connection')) {
        setConnectionStatus(ConnectionStatus.DISCONNECTED);
        setConnectionError('Connection to backend lost');
      } else if (e.message?.includes('hardware')) {
        setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
        setConnectionError('Hardware error: ' + e.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, api]);
  
  /**
   * Handle Start Dynamic Mode button click.
   * Requirements: 5.1, 5.2
   * 
   * Enhanced with:
   * - RPC retry logic
   * - LKG stability tracking
   * - Connection error handling
   */
  const handleStart = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setConnectionStatus(ConnectionStatus.CONNECTED);
    
    try {
      const response = await withRetry(
        () => api.callPluginMethod<{
          success: boolean;
          error?: string;
        }>('start_dynamic_mode', { config }),
        DEFAULT_RETRY_CONFIG,
        'start_dynamic_mode'
      );
      
      if (response.success) {
        setIsActive(true);
        
        // Start stability tracking for LKG
        // Requirements: 7.4
        stabilityTrackerRef.current.start(config);
        
        console.log('[DynamicManualMode] Dynamic mode started');
        setConnectionStatus(ConnectionStatus.CONNECTED);
      } else {
        setError(response.error || 'Failed to start dynamic mode');
        
        if (response.error?.includes('hardware')) {
          setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
          setConnectionError(response.error);
        }
      }
    } catch (e: any) {
      console.error('[DynamicManualMode] Failed to start:', e);
      setError(e.message || 'Unknown error');
      
      // Update connection status
      if (e.message?.includes('network') || e.message?.includes('connection')) {
        setConnectionStatus(ConnectionStatus.DISCONNECTED);
        setConnectionError('Connection to backend lost');
      } else if (e.message?.includes('hardware')) {
        setConnectionStatus(ConnectionStatus.HARDWARE_ERROR);
        setConnectionError('Hardware error: ' + e.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, api]);
  
  /**
   * Handle Stop Dynamic Mode button click.
   * Requirements: 5.3, 5.4
   * 
   * Enhanced with:
   * - RPC retry logic
   * - LKG stability tracking stop
   * - Connection error handling
   */
  const handleStop = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await withRetry(
        () => api.callPluginMethod<{
          success: boolean;
          error?: string;
        }>('stop_dynamic_mode', {}),
        DEFAULT_RETRY_CONFIG,
        'stop_dynamic_mode'
      );
      
      if (response.success) {
        setIsActive(false);
        
        // Stop stability tracking
        // Requirements: 7.4
        const stableDuration = stabilityTrackerRef.current.getStabilityDuration();
        if (isStableEnoughForLKG(stableDuration)) {
          // Save as LKG if it was stable long enough
          saveLKG(config, stableDuration);
          setHasLKG(true);
        }
        stabilityTrackerRef.current.stop();
        
        console.log('[DynamicManualMode] Dynamic mode stopped');
        setConnectionStatus(ConnectionStatus.CONNECTED);
      } else {
        setError(response.error || 'Failed to stop dynamic mode');
      }
    } catch (e: any) {
      console.error('[DynamicManualMode] Failed to stop:', e);
      setError(e.message || 'Unknown error');
      
      // Update connection status
      if (e.message?.includes('network') || e.message?.includes('connection')) {
        setConnectionStatus(ConnectionStatus.DISCONNECTED);
        setConnectionError('Connection to backend lost');
      }
    } finally {
      setIsLoading(false);
    }
  }, [api, config]);
  
  /**
   * Update core configuration.
   */
  const updateCoreConfig = useCallback((coreId: number, updates: Partial<CoreConfig>) => {
    setConfig(prev => ({
      ...prev,
      cores: prev.cores.map(core =>
        core.core_id === coreId ? { ...core, ...updates } : core
      ),
    }));
  }, []);
  
  /**
   * Update all cores in Simple Mode.
   * Requirements: 4.2
   * Property 6: Simple mode value propagation
   */
  const updateAllCores = useCallback((updates: Partial<CoreConfig>) => {
    setConfig(prev => ({
      ...prev,
      cores: prev.cores.map(core => ({ ...core, ...updates })),
    }));
  }, []);
  
  /**
   * Handle slider changes - propagates to all cores in Simple Mode.
   * Requirements: 4.2, 8.3
   */
  const handleSliderChange = useCallback((field: 'min_mv' | 'max_mv' | 'threshold', value: number) => {
    if (config.mode === 'simple') {
      // In Simple Mode, propagate to all cores
      updateAllCores({ [field]: value });
    } else {
      // In Expert Mode, update only selected core
      updateCoreConfig(selectedCore, { [field]: value });
    }
  }, [config.mode, selectedCore, updateAllCores, updateCoreConfig]);
  
  /**
   * Handle gamepad navigation for slider adjustment and focus management.
   * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
   * 
   * Property 15: Gamepad core navigation
   * D-pad Up/Down changes selected core with wrapping (handled in CoreTabs).
   * 
   * Property 16: Gamepad focus navigation
   * D-pad Left/Right moves focus between sliders and buttons.
   * 
   * Property 17: Gamepad slider adjustment
   * L1/R1 adjusts slider value by one increment when slider has focus.
   * 
   * Property 18: Gamepad focus indicator visibility
   * Visual focus indicators are rendered for focused elements.
   */
  useEffect(() => {
    const handleGamepadInput = (e: KeyboardEvent) => {
      // D-pad Left/Right: Focus navigation between sliders
      // Requirements: 8.2
      // Property 16: Gamepad focus navigation
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        setFocusedSlider(prev => {
          if (prev === null || prev === 'min') return 'threshold';
          if (prev === 'max') return 'min';
          if (prev === 'threshold') return 'max';
          return prev;
        });
      }
      
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        setFocusedSlider(prev => {
          if (prev === null || prev === 'threshold') return 'min';
          if (prev === 'min') return 'max';
          if (prev === 'max') return 'threshold';
          return prev;
        });
      }
      
      // L1/R1: Slider adjustment when slider has focus
      // Requirements: 8.3
      // Property 17: Gamepad slider adjustment
      if ((e.key === 'PageUp' || e.key === 'PageDown') && focusedSlider) {
        e.preventDefault();
        
        const currentCore = config.mode === 'simple' ? 0 : selectedCore;
        const currentConfig = config.cores[currentCore];
        const increment = e.key === 'PageUp' ? 1 : -1; // L1 = PageUp, R1 = PageDown
        
        if (focusedSlider === 'min') {
          const newValue = Math.max(-100, Math.min(0, currentConfig.min_mv + increment));
          handleSliderChange('min_mv', newValue);
        } else if (focusedSlider === 'max') {
          const newValue = Math.max(-100, Math.min(0, currentConfig.max_mv + increment));
          handleSliderChange('max_mv', newValue);
        } else if (focusedSlider === 'threshold') {
          const newValue = Math.max(0, Math.min(100, currentConfig.threshold + increment));
          handleSliderChange('threshold', newValue);
        }
      }
    };
    
    window.addEventListener('keydown', handleGamepadInput);
    
    return () => {
      window.removeEventListener('keydown', handleGamepadInput);
    };
  }, [focusedSlider, config, selectedCore, handleSliderChange]);
  
  if (isLoading && !config.cores.length) {
    return (
      <PanelSection title="Dynamic Manual Mode">
        <PanelSectionRow>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '24px',
            color: '#8b929a',
          }}>
            <FaSpinner className="spin" />
            <span>Loading...</span>
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }
  
  // Check if Apply button should be disabled
  // Requirements: 7.1
  const hasValidationErrors = validateConfig().length > 0;
  
  return (
    <PanelSection title="Dynamic Manual Mode">
      {/* Connection Status Banner */}
      {/* Requirements: Error banners for connection issues */}
      {connectionStatus !== ConnectionStatus.CONNECTED && (
        <PanelSectionRow>
          <div style={{
            padding: '12px',
            backgroundColor: 
              connectionStatus === ConnectionStatus.HARDWARE_ERROR ? '#b71c1c' :
              connectionStatus === ConnectionStatus.DISCONNECTED ? '#d32f2f' :
              '#ff9800', // RECONNECTING
            borderRadius: '6px',
            marginBottom: '12px',
            border: '2px solid ' + (
              connectionStatus === ConnectionStatus.HARDWARE_ERROR ? '#ff5252' :
              connectionStatus === ConnectionStatus.DISCONNECTED ? '#ff5252' :
              '#ffb74d'
            ),
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              fontWeight: 'bold',
              color: '#fff',
              marginBottom: connectionError ? '6px' : '0',
            }}>
              {connectionStatus === ConnectionStatus.RECONNECTING && <FaSpinner className="spin" />}
              {connectionStatus === ConnectionStatus.HARDWARE_ERROR && <FaExclamationTriangle />}
              {connectionStatus === ConnectionStatus.DISCONNECTED && <FaExclamationTriangle />}
              <span>
                {connectionStatus === ConnectionStatus.RECONNECTING && 'Reconnecting...'}
                {connectionStatus === ConnectionStatus.HARDWARE_ERROR && 'Hardware Error'}
                {connectionStatus === ConnectionStatus.DISCONNECTED && 'Connection Lost'}
              </span>
            </div>
            {connectionError && (
              <div style={{ fontSize: '11px', color: '#fff', opacity: 0.9 }}>
                {connectionError}
              </div>
            )}
          </div>
        </PanelSectionRow>
      )}
      
      {/* Danger Warning Dialog */}
      {showDangerWarning && (
        <PanelSectionRow>
          <div style={{
            padding: '16px',
            backgroundColor: '#5c1313',
            borderRadius: '8px',
            marginBottom: '12px',
            border: '2px solid #ff9800',
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 'bold',
              color: '#ff9800',
              marginBottom: '8px',
            }}>
              ⚠️ Dangerous Configuration Warning
            </div>
            <div style={{
              fontSize: '11px',
              color: '#fff',
              marginBottom: '12px',
              lineHeight: '1.4',
            }}>
              Your configuration includes aggressive voltage offsets (below -50mV) that may cause system instability or crashes. 
              Proceed only if you understand the risks.
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <FocusableButton
                onClick={() => {
                  setShowDangerWarning(false);
                  applyConfiguration();
                }}
                style={{ flex: 1 }}
              >
                <div style={{
                  padding: '8px',
                  backgroundColor: '#ff9800',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  textAlign: 'center',
                }}>
                  Apply Anyway
                </div>
              </FocusableButton>
              <FocusableButton
                onClick={() => setShowDangerWarning(false)}
                style={{ flex: 1 }}
              >
                <div style={{
                  padding: '8px',
                  backgroundColor: '#3d4450',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  textAlign: 'center',
                }}>
                  Cancel
                </div>
              </FocusableButton>
            </div>
          </div>
        </PanelSectionRow>
      )}
      {/* Status Indicator */}
      {/* Requirements: 5.2, 5.4 */}
      {/* Property 9: Status indicator state consistency */}
      <PanelSectionRow>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          backgroundColor: isActive ? '#1b5e20' : '#3d4450',
          borderRadius: '6px',
          marginBottom: '12px',
          transition: 'background-color 0.3s ease, box-shadow 0.3s ease',
          boxShadow: isActive ? '0 0 16px rgba(76, 175, 80, 0.3)' : 'none',
        }}>
          <span style={{ 
            fontSize: '12px', 
            fontWeight: 'bold',
            transition: 'color 0.3s ease',
          }}>
            Status: {isActive ? 'Active' : 'Inactive'}
          </span>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isActive ? '#4caf50' : '#8b929a',
            boxShadow: isActive ? '0 0 8px #4caf50' : 'none',
            transition: 'all 0.3s ease',
            animation: isActive ? 'pulse 2s ease-in-out infinite' : 'none',
          }} />
        </div>
      </PanelSectionRow>
      
      {/* Error Display */}
      {error && (
        <PanelSectionRow>
          <div style={{
            padding: '12px',
            backgroundColor: '#b71c1c',
            borderRadius: '6px',
            marginBottom: '12px',
          }}>
            <div style={{ fontSize: '12px', color: '#fff' }}>
              {error}
            </div>
          </div>
        </PanelSectionRow>
      )}
      
      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <PanelSectionRow>
          <div style={{
            padding: '12px',
            backgroundColor: '#5c1313',
            borderRadius: '6px',
            marginBottom: '12px',
          }}>
            {validationErrors.map((err, idx) => (
              <div key={idx} style={{ fontSize: '11px', color: '#ff9800', marginBottom: '4px' }}>
                {err.core_id !== undefined && `Core ${err.core_id}: `}
                {err.message}
              </div>
            ))}
          </div>
        </PanelSectionRow>
      )}
      
      {/* Mode Toggle */}
      <PanelSectionRow>
        <Focusable style={{ marginBottom: '12px' }}>
          <FocusableButton
            onClick={handleModeToggle}
            style={{ width: '100%' }}
          >
            <div style={{
              padding: '8px',
              backgroundColor: config.mode === 'simple' ? '#1a9fff' : '#3d4450',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 'bold',
              textAlign: 'center',
            }}>
              {config.mode === 'simple' ? '✓ Simple Mode' : 'Expert Mode (Per-Core)'}
            </div>
          </FocusableButton>
        </Focusable>
      </PanelSectionRow>
      
      {/* Core Tabs - Hidden in Simple Mode */}
      <PanelSectionRow>
        <CoreTabs
          selectedCore={selectedCore}
          onCoreSelect={setSelectedCore}
          mode={config.mode}
        />
      </PanelSectionRow>
      
      {/* Voltage Sliders */}
      <VoltageSliders
        coreId={config.mode === 'simple' ? 0 : selectedCore}
        config={config.mode === 'simple' ? config.cores[0] : config.cores[selectedCore]}
        onChange={handleSliderChange}
        disabled={isLoading}
        validationErrors={validationErrors}
        focusedSlider={focusedSlider}
        onSliderFocus={setFocusedSlider}
      />
      
      {/* Action Buttons */}
      {/* Requirements: 1.5, 5.1, 5.3 */}
      {/* UI Polish: Tooltips for buttons */}
      <PanelSectionRow>
        <Focusable
          style={{ display: 'flex', gap: '8px', marginTop: '12px' }}
          flow-children="horizontal"
        >
          <div style={{ flex: 1, position: 'relative' }} title="Apply configuration to all cores">
            <FocusableButton
              onClick={handleApply}
              disabled={isLoading || hasValidationErrors}
              style={{ width: '100%' }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                padding: '10px',
                backgroundColor: hasValidationErrors ? '#3d4450' : '#1a9fff',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 'bold',
                opacity: hasValidationErrors ? 0.5 : 1,
                transition: 'all 0.2s ease',
              }}>
                {isLoading ? <FaSpinner className="spin" /> : null}
                <span>Apply</span>
              </div>
            </FocusableButton>
          </div>
          
          {!isActive ? (
            <div style={{ flex: 1, position: 'relative' }} title="Start dynamic voltage adjustment">
              <FocusableButton
                onClick={handleStart}
                disabled={isLoading}
                style={{ width: '100%' }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  backgroundColor: '#1b5e20',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  transition: 'all 0.2s ease',
                }}>
                  <FaPlay />
                  <span>Start</span>
                </div>
              </FocusableButton>
            </div>
          ) : (
            <div style={{ flex: 1, position: 'relative' }} title="Stop dynamic voltage adjustment">
              <FocusableButton
                onClick={handleStop}
                disabled={isLoading}
                style={{ width: '100%' }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  backgroundColor: '#b71c1c',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  transition: 'all 0.2s ease',
                }}>
                  <FaStop />
                  <span>Stop</span>
                </div>
              </FocusableButton>
            </div>
          )}
        </Focusable>
      </PanelSectionRow>
      
      {/* Reset to Safe Defaults Button */}
      {/* Requirements: 7.5, 7.4 */}
      {/* UI Polish: Tooltips for recovery buttons */}
      <PanelSectionRow>
        <Focusable 
          style={{ 
            display: 'flex', 
            gap: '8px', 
            marginTop: '8px',
            flexDirection: 'column',
          }}
        >
          {/* Restore Last Stable Button */}
          {/* Requirements: 7.4 - LKG configuration recovery */}
          {hasLKG && (
            <div style={{ position: 'relative' }} title="Restore the last known stable configuration">
              <FocusableButton
                onClick={handleRestoreLKG}
                disabled={isLoading}
                style={{ width: '100%' }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '8px',
                  backgroundColor: '#ff9800',
                  borderRadius: '6px',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  transition: 'all 0.2s ease',
                }}>
                  <FaUndo />
                  <span>Restore Last Stable</span>
                </div>
              </FocusableButton>
            </div>
          )}
          
          <div style={{ position: 'relative' }} title="Reset all cores to safe default values (-30mV/-15mV/50%)">
            <FocusableButton
              onClick={handleResetToDefaults}
              disabled={isLoading}
              style={{ width: '100%' }}
            >
              <div style={{
                padding: '8px',
                backgroundColor: '#3d4450',
                borderRadius: '6px',
                fontSize: '10px',
                fontWeight: 'bold',
                textAlign: 'center',
                transition: 'all 0.2s ease',
              }}>
                Reset to Safe Defaults
              </div>
            </FocusableButton>
          </div>
        </Focusable>
      </PanelSectionRow>
      
      <style>
        {`
          /* Spinner animation for loading states */
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          
          /* Pulse animation for active status indicator */
          @keyframes pulse {
            0%, 100% {
              opacity: 1;
              transform: scale(1);
            }
            50% {
              opacity: 0.7;
              transform: scale(1.1);
            }
          }
          
          /* Smooth fade-in for error messages */
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: translateY(-10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          /* Responsive layout adjustments */
          @media (max-width: 768px) {
            /* Adjust padding and font sizes for smaller screens */
            .dynamic-mode-container {
              padding: 8px;
            }
            
            .dynamic-mode-button {
              font-size: 10px;
              padding: 8px;
            }
            
            .dynamic-mode-status {
              font-size: 11px;
            }
          }
          
          @media (min-width: 769px) and (max-width: 1024px) {
            /* Medium screen adjustments */
            .dynamic-mode-container {
              padding: 12px;
            }
          }
          
          @media (min-width: 1025px) {
            /* Large screen adjustments */
            .dynamic-mode-container {
              padding: 16px;
              max-width: 1200px;
              margin: 0 auto;
            }
          }
          
          /* Smooth transitions for all interactive elements */
          button, .focusable-element {
            transition: all 0.2s ease;
          }
          
          button:hover, .focusable-element:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
          }
          
          button:active, .focusable-element:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          }
          
          /* Focus indicator enhancement for gamepad navigation */
          .gamepad-focus {
            outline: 3px solid #1a9fff;
            outline-offset: 2px;
            box-shadow: 0 0 12px rgba(26, 159, 255, 0.6);
            transition: all 0.2s ease;
          }
          
          /* Smooth graph update transitions */
          .recharts-wrapper {
            transition: opacity 0.3s ease;
          }
          
          .recharts-line {
            transition: stroke-dashoffset 0.5s ease;
          }
        `}
      </style>
    </PanelSection>
  );
};

/**
 * Exported component with error boundary.
 */
export const DynamicManualMode: FC = () => (
  <DynamicModeErrorBoundary>
    <DynamicManualModeInternal />
  </DynamicModeErrorBoundary>
);

export default DynamicManualMode;
