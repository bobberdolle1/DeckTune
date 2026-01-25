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
import { getApiInstance, Api, State, PlatformInfo, AutotuneProgress, AutotuneResult, TestHistoryEntry, BinningProgress, BinningResult, BinningConfig, GameProfile } from "../api";

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
  
  // Game Profiles (new in v3.0)
  gameProfiles: [],
  activeProfile: null,
  
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
  dynamicStatus: null,
  
  // Autotune state (new properties)
  autotuneProgress: null,
  autotuneResult: null,
  isAutotuning: false,
  
  // Binning state
  binningProgress: null,
  binningResult: null,
  isBinning: false,
  binningConfig: null,
  
  // Test state (new properties)
  testHistory: [],
  currentTest: null,
  isTestRunning: false,
  
  // Benchmark state (new in v3.0)
  benchmarkHistory: [],
  isBenchmarkRunning: false,
  lastBenchmarkResult: null,
  
  // Telemetry state (new in v3.1)
  // Requirements: 2.1, 2.2, 2.3, 2.4
  telemetrySamples: [],
  
  // Binary availability
  missingBinaries: [],
  
  // Frequency wizard state (new in v3.2)
  frequencyModeEnabled: false,
  frequencyCurves: {},
  frequencyWizardProgress: null,
  isFrequencyWizardRunning: false,
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

/**
 * Hook to check binary availability.
 * Returns missing binaries list and a function to refresh.
 */
export const useBinaries = () => {
  const { state, api } = useDeckTune();
  
  const checkBinaries = async () => {
    const result = await api.checkBinaries();
    if (result.success) {
      api.setState({ missingBinaries: result.missing });
    }
    return result;
  };
  
  return {
    missing: state.missingBinaries,
    hasMissing: state.missingBinaries.length > 0,
    check: checkBinaries,
  };
};

/**
 * Hook to access binning state.
 * Requirements: 8.1, 8.2, 8.3, 8.4
 */
export const useBinning = () => {
  const { state, api } = useDeckTune();
  return {
    progress: state.binningProgress,
    result: state.binningResult,
    isRunning: state.isBinning,
    config: state.binningConfig,
    start: (config?: Partial<BinningConfig>) => api.startBinning(config),
    stop: () => api.stopBinning(),
    getConfig: () => api.getBinningConfig(),
    updateConfig: (config: Partial<BinningConfig>) => api.updateBinningConfig(config),
  };
};

/**
 * Hook to access profile management.
 * Requirements: 3.1, 3.2, 3.3, 3.4, 5.1
 */
export const useProfiles = () => {
  const { state, api } = useDeckTune();
  return {
    profiles: state.gameProfiles || [],
    activeProfile: state.activeProfile,
    runningAppId: state.runningAppId,
    runningAppName: state.runningAppName,
    createProfile: (profile: Omit<GameProfile, 'created_at' | 'last_used'>) => api.createProfile(profile),
    getProfiles: () => api.getProfiles(),
    updateProfile: (appId: number, updates: Partial<GameProfile>) => api.updateProfile(appId, updates),
    deleteProfile: (appId: number) => api.deleteProfile(appId),
    createProfileForCurrentGame: () => api.createProfileForCurrentGame(),
    exportProfiles: () => api.exportGameProfiles(),
    importProfiles: (jsonData: string, strategy: "skip" | "overwrite" | "rename") => api.importGameProfiles(jsonData, strategy),
  };
};

/**
 * Hook to access telemetry data for real-time graphs.
 * Requirements: 2.3, 2.4
 * Feature: decktune-3.1-reliability-ux
 */
export const useTelemetry = () => {
  const { state } = useDeckTune();
  return {
    samples: state.telemetrySamples || [],
    hasData: (state.telemetrySamples || []).length > 0,
  };
};

/**
 * Hook to access frequency wizard state and methods.
 * Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
 */
export const useFrequencyWizard = () => {
  const { state, api } = useDeckTune();
  return {
    isRunning: state.isFrequencyWizardRunning,
    progress: state.frequencyWizardProgress,
    curves: state.frequencyCurves,
    modeEnabled: state.frequencyModeEnabled,
    startWizard: (config: any) => api.startFrequencyWizard(config),
    getProgress: () => api.getFrequencyWizardProgress(),
    cancelWizard: () => api.cancelFrequencyWizard(),
    getCurve: (coreId: number) => api.getFrequencyCurve(coreId),
    applyCurves: (curves: Record<number, any>) => api.applyFrequencyCurve(curves),
    enableMode: () => api.enableFrequencyMode(),
    disableMode: () => api.disableFrequencyMode(),
  };
};

export default DeckTuneContext;
