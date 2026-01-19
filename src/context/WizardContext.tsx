/**
 * Wizard Mode Context for DeckTune.
 * 
 * Feature: Wizard Mode Refactoring
 * 
 * Provides state management and API integration for the wizard workflow:
 * - Configuration and session management
 * - Real-time progress tracking
 * - Results history and visualization
 * - Crash recovery detection
 */

import { createContext, useContext, useState, useEffect, FC, ReactNode, useCallback } from "react";
import { call, addEventListener, removeEventListener } from "@decky/api";

// ==================== Types ====================

export interface WizardConfig {
  targetDomains: string[];
  aggressiveness: "safe" | "balanced" | "aggressive";
  testDuration: "short" | "long";
  safetyLimits: Record<string, number>;
}

export interface WizardProgress {
  state: string;
  currentStage: string;
  currentOffset: number;
  progressPercent: number;
  etaSeconds: number;
  otaSeconds: number;
  heartbeat: number;
  liveMetrics: Record<string, any>;
}

export interface CurveDataPoint {
  offset: number;
  result: "pass" | "fail" | "crash";
  temp: number;
  timestamp: string;
}

export interface WizardResult {
  id: string;
  name: string;
  timestamp: string;
  chipGrade: string;
  offsets: Record<string, number>;
  curveData: CurveDataPoint[];
  duration: number;
  iterations: number;
}

export interface CrashInfo {
  sessionId: string;
  timestamp: string;
  currentOffset: number;
  lastStable: number;
}

// ==================== Context ====================

interface WizardContextType {
  // State
  isRunning: boolean;
  progress: WizardProgress | null;
  result: WizardResult | null;
  resultsHistory: WizardResult[];
  dirtyExit: { detected: boolean; crashInfo: CrashInfo | null } | null;
  error: string | null;
  
  // Actions
  startWizard: (config: WizardConfig) => Promise<void>;
  cancelWizard: () => Promise<void>;
  applyResult: (resultId: string, saveAsPreset: boolean) => Promise<void>;
  checkDirtyExit: () => Promise<void>;
  loadResultsHistory: () => Promise<void>;
  clearError: () => void;
}

const WizardContext = createContext<WizardContextType | undefined>(undefined);

// ==================== Provider ====================

export const WizardProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState<WizardProgress | null>(null);
  const [result, setResult] = useState<WizardResult | null>(null);
  const [resultsHistory, setResultsHistory] = useState<WizardResult[]>([]);
  const [dirtyExit, setDirtyExit] = useState<{ detected: boolean; crashInfo: CrashInfo | null } | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // ==================== Server Event Listener ====================
  
  useEffect(() => {
    const handleServerEvent = (data: any) => {
      if (!data || !data.type) return;
      
      switch (data.type) {
        case "wizard_progress":
          setProgress(data.data);
          setIsRunning(true);
          setError(null);
          break;
          
        case "wizard_complete":
          setResult(data.data);
          setIsRunning(false);
          setProgress(null);
          loadResultsHistory();
          break;
          
        case "wizard_error":
          setError(data.data?.error || "Unknown wizard error");
          setIsRunning(false);
          setProgress(null);
          break;
      }
    };
    
    addEventListener("server_event", handleServerEvent);
    return () => removeEventListener("server_event", handleServerEvent);
  }, []);
  
  // ==================== Actions ====================
  
  const startWizard = useCallback(async (config: WizardConfig) => {
    try {
      setError(null);
      setResult(null);
      
      const response = await call("start_wizard", config) as { success: boolean; error?: string; session_id?: string };
      
      if (response?.success) {
        setIsRunning(true);
      } else {
        const errorMsg = response?.error || "Failed to start wizard";
        setError(errorMsg);
        throw new Error(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to start wizard";
      setError(errorMsg);
      throw err;
    }
  }, []);
  
  const cancelWizard = useCallback(async () => {
    try {
      const response = await call("cancel_wizard") as { success: boolean; error?: string };
      
      if (response?.success) {
        setIsRunning(false);
        setProgress(null);
      } else {
        const errorMsg = response?.error || "Failed to cancel wizard";
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to cancel wizard";
      setError(errorMsg);
    }
  }, []);
  
  const applyResult = useCallback(async (resultId: string, saveAsPreset: boolean) => {
    try {
      setError(null);
      
      const response = await call("apply_wizard_result", resultId, saveAsPreset) as { success: boolean; error?: string };
      
      if (!response?.success) {
        const errorMsg = response?.error || "Failed to apply wizard result";
        setError(errorMsg);
        throw new Error(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to apply wizard result";
      setError(errorMsg);
      throw err;
    }
  }, []);
  
  const checkDirtyExit = useCallback(async () => {
    try {
      const response = await call("check_wizard_dirty_exit") as { dirty_exit: boolean; crash_info?: CrashInfo };
      
      if (response?.dirty_exit) {
        setDirtyExit({
          detected: true,
          crashInfo: response.crash_info || null
        });
      } else {
        setDirtyExit({ detected: false, crashInfo: null });
      }
    } catch (err) {
      console.error("Failed to check wizard dirty exit:", err);
      setDirtyExit({ detected: false, crashInfo: null });
    }
  }, []);
  
  const loadResultsHistory = useCallback(async () => {
    try {
      const response = await call("get_wizard_results_history") as WizardResult[];
      
      if (Array.isArray(response)) {
        setResultsHistory(response);
      }
    } catch (err) {
      console.error("Failed to load wizard results history:", err);
    }
  }, []);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  // ==================== Initialization ====================
  
  useEffect(() => {
    checkDirtyExit();
    loadResultsHistory();
  }, [checkDirtyExit, loadResultsHistory]);
  
  // ==================== Context Value ====================
  
  const value: WizardContextType = {
    isRunning,
    progress,
    result,
    resultsHistory,
    dirtyExit,
    error,
    startWizard,
    cancelWizard,
    applyResult,
    checkDirtyExit,
    loadResultsHistory,
    clearError
  };
  
  return (
    <WizardContext.Provider value={value}>
      {children}
    </WizardContext.Provider>
  );
};

// ==================== Hook ====================

export const useWizard = (): WizardContextType => {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error("useWizard must be used within WizardProvider");
  }
  return context;
};
