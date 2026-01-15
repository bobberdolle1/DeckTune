/**
 * React context for DeckTune state management.
 * 
 * Feature: decktune, Frontend State Management
 * Requirements: State management
 * 
 * Provides state properties:
 * - autotuneProgress, autotuneResult
 * - testHistory, currentTest
 * - platformInfo
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { getApiInstance, Api, State, PlatformInfo, AutotuneProgress, AutotuneResult, TestHistoryEntry } from "../api";

// Declare SP_REACT for Decky environment
declare const SP_REACT: typeof import("react");

/**
 * Context value interface with state and API methods.
 */
interface DeckTuneContextValue {
  // State properties
  state: State;
  api: Api;
  
  // Convenience accessors for new state properties
  autotuneProgress: AutotuneProgress | null;
  autotuneResult: AutotuneResult | null;
  testHistory: TestHistoryEntry[];
  currentTest: string | null;
  platformInfo: PlatformInfo | null;
  isAutotuning: boolean;
  isTestRunning: boolean;
}

/**
 * Initial state with all required properties.
 * Requirements: State management
 */
export const initialState: State = {
  // Core state
  cores: [5, 5, 5, 5],
  globalCores: [],
  status: "disabled",
  
  // Platform info
  platformInfo: null,
  
  // Running app info
  runningAppName: null,
  runningAppId: null,
  
  // Presets
  presets: [],
  currentPreset: null,
  
  // Settings
  settings: {
    isGlobal: false,
    runAtStartup: false,
    isRunAutomatically: false,
    timeoutApply: 15,
  },
  dynamicSettings: {
    strategy: "DEFAULT",
    sample_interval: 50000,
    cores: [
      { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
      { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
      { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
      { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
    ],
  },
  
  // Dynamic mode
  gymdeckRunning: false,
  isDynamic: false,
  
  // Autotune state (new properties)
  autotuneProgress: null,
  autotuneResult: null,
  isAutotuning: false,
  
  // Test state (new properties)
  testHistory: [],
  currentTest: null,
  isTestRunning: false,
};

// Create context with null default
const DeckTuneContext = createContext<DeckTuneContextValue | null>(null);

/**
 * Provider component for DeckTune context.
 */
export const DeckTuneProvider = ({ children }: { children: ReactNode }) => {
  const api = getApiInstance(initialState);
  const [state, setState] = useState<State>(api.getState());

  useEffect(() => {
    const handleStateChange = (newState: State) => {
      setState((prev) => ({ ...prev, ...newState }));
    };

    api.on("state_change", handleStateChange);

    return () => {
      api.removeListener("state_change", handleStateChange);
    };
  }, [api]);

  const contextValue: DeckTuneContextValue = {
    state,
    api,
    
    // Convenience accessors for new state properties
    autotuneProgress: state.autotuneProgress,
    autotuneResult: state.autotuneResult,
    testHistory: state.testHistory,
    currentTest: state.currentTest,
    platformInfo: state.platformInfo,
    isAutotuning: state.isAutotuning,
    isTestRunning: state.isTestRunning,
  };

  return (
    <DeckTuneContext.Provider value={contextValue}>
      {children}
    </DeckTuneContext.Provider>
  );
};

/**
 * Hook to access DeckTune context.
 * @throws Error if used outside of DeckTuneProvider
 */
export const useDeckTune = (): DeckTuneContextValue => {
  const context = useContext(DeckTuneContext);
  if (!context) {
    throw new Error("useDeckTune must be used within a DeckTuneProvider");
  }
  return context;
};

/**
 * Hook to access just the API instance.
 */
export const useApi = (): Api => {
  const { api } = useDeckTune();
  return api;
};

/**
 * Hook to access autotune state.
 */
export const useAutotune = () => {
  const { autotuneProgress, autotuneResult, isAutotuning, api } = useDeckTune();
  return {
    progress: autotuneProgress,
    result: autotuneResult,
    isRunning: isAutotuning,
    start: (mode: "quick" | "thorough") => api.startAutotune(mode),
    stop: () => api.stopAutotune(),
  };
};

/**
 * Hook to access test state.
 */
export const useTests = () => {
  const { testHistory, currentTest, isTestRunning, api } = useDeckTune();
  return {
    history: testHistory,
    currentTest,
    isRunning: isTestRunning,
    runTest: (testName: string) => api.runTest(testName),
    getHistory: () => api.getTestHistory(),
  };
};

/**
 * Hook to access platform info.
 */
export const usePlatformInfo = () => {
  const { platformInfo, api } = useDeckTune();
  return {
    info: platformInfo,
    refresh: () => api.fetchPlatformInfo(),
  };
};

export default DeckTuneContext;
