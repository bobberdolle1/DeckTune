/**
 * API class for DeckTune frontend state management.
 * 
 * Feature: decktune, Frontend State Management
 * Requirements: Frontend integration, State management
 * 
 * This class manages frontend state and provides RPC methods for
 * communicating with the Python backend.
 */

import { call, addEventListener, removeEventListener } from "@decky/api";
import {
  State,
  PlatformInfo,
  AutotuneProgress,
  AutotuneResult,
  TestResult,
  TestHistoryEntry,
  Preset,
  Settings,
  DynamicSettings,
  DynamicStatus,
  ServerEvent,
  StatusString,
  BinningConfig,
  BinningState,
  BinningResult,
  BinningProgress,
  GameProfile,
  BenchmarkResult,
  Session,
  SessionComparison,
} from "./types";

// Simple EventEmitter implementation
type EventHandler = (...args: any[]) => void;

class SimpleEventEmitter {
  private events: Map<string, EventHandler[]> = new Map();

  on(event: string, handler: EventHandler): void {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event)!.push(handler);
  }

  emit(event: string, ...args: any[]): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(...args));
    }
  }

  removeListener(event: string, handler: EventHandler): void {
    const handlers = this.events.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }
}

// Decky Frontend Library types
declare const DFL: any;
declare const SteamClient: any;
declare const appStore: any;

let apiInstance: Api | null = null;

/**
 * Get or create the singleton Api instance.
 */
export const getApiInstance = (initialState: State): Api => {
  if (!apiInstance) {
    apiInstance = new Api(initialState);
  }
  return apiInstance;
};

/**
 * Main API class for DeckTune frontend.
 * 
 * Extends SimpleEventEmitter to provide state change notifications.
 * Implements all RPC methods for backend communication.
 */
export class Api extends SimpleEventEmitter {
  private state: State;
  private registeredListeners: any[] = [];

  constructor(initialState: State) {
    super();
    this.state = initialState;
  }

  /**
   * Update state and emit change event.
   */
  setState(newState: Partial<State>): void {
    this.state = { ...this.state, ...newState };
    this.emit("state_change", this.state);
  }

  /**
   * Get current state.
   */
  getState(): State {
    return this.state;
  }


  /**
   * Initialize the API and register event listeners.
   */
  async init(): Promise<void> {
    await call("init");
    await this.fetchConfig();
    await this.fetchPlatformInfo();
    await this.fetchTestHistory();

    // Register Steam client listeners (with fallbacks for API changes)
    try {
      if (SteamClient?.GameSessions?.RegisterForAppLifetimeNotifications) {
        this.registeredListeners.push(
          SteamClient.GameSessions.RegisterForAppLifetimeNotifications(
            this.onAppLifetimeNotification.bind(this)
          )
        );
      }
    } catch (e) {
      console.warn("DeckTune: Failed to register app lifetime listener:", e);
    }

    try {
      if (SteamClient?.System?.RegisterForOnResumeFromSuspend) {
        this.registeredListeners.push(
          SteamClient.System.RegisterForOnResumeFromSuspend(
            this.onResumeFromSuspend.bind(this)
          )
        );
      }
    } catch (e) {
      console.warn("DeckTune: Failed to register suspend listener:", e);
    }

    // Register backend event listeners
    addEventListener("tuning_progress", this.onTuningProgress.bind(this));
    addEventListener("tuning_complete", this.onTuningComplete.bind(this));
    addEventListener("test_complete", this.onTestComplete.bind(this));
    addEventListener("update_status", this.onStatusUpdate.bind(this));
    addEventListener("dynamic_status", this.onDynamicStatus.bind(this));
    addEventListener("binning_progress", this.onBinningProgress.bind(this));
    addEventListener("binning_complete", this.onBinningComplete.bind(this));
    addEventListener("binning_error", this.onBinningError.bind(this));
    addEventListener("profile_changed", this.onProfileChanged.bind(this));
    addEventListener("telemetry_sample", this.onTelemetrySample.bind(this));

    if (this.state.settings.isRunAutomatically && DFL.Router.MainRunningApp) {
      return await this.handleMainRunningApp();
    }

    if (this.state.settings.runAtStartup) {
      return await this.applyUndervolt(
        this.state.cores,
        this.state.settings.timeoutApply
      );
    }

    await this.disableUndervolt();
  }

  /**
   * Fetch configuration from backend.
   */
  async fetchConfig(): Promise<void> {
    const config = (await call("fetch_config")) as any;
    this.setState({
      dynamicSettings: config.dynamicSettings,
      globalCores: config.cores,
      cores: config.cores,
      settings: config.settings,
      presets: config.presets,
      status: config.status,
    });
  }

  /**
   * Fetch platform information from backend.
   * Requirements: Frontend integration
   */
  async fetchPlatformInfo(): Promise<PlatformInfo> {
    const platformInfo = (await call("get_platform_info")) as PlatformInfo;
    this.setState({ platformInfo });
    return platformInfo;
  }

  /**
   * Fetch test history from backend.
   * Requirements: Frontend integration
   */
  async fetchTestHistory(): Promise<TestHistoryEntry[]> {
    const testHistory = (await call("get_test_history")) as TestHistoryEntry[];
    this.setState({ testHistory });
    return testHistory;
  }

  // ==================== Event Handlers ====================

  /**
   * Handle tuning progress events from backend.
   */
  private onTuningProgress(progress: AutotuneProgress): void {
    this.setState({ autotuneProgress: progress });
  }

  /**
   * Handle tuning complete events from backend.
   */
  private onTuningComplete(result: AutotuneResult): void {
    this.setState({
      autotuneResult: result,
      autotuneProgress: null,
      isAutotuning: false,
    });
  }

  /**
   * Handle test complete events from backend.
   */
  private onTestComplete(result: TestResult): void {
    this.setState({ currentTest: null, isTestRunning: false });
    // Refresh test history
    this.fetchTestHistory();
  }

  /**
   * Handle status update events from backend.
   */
  private onStatusUpdate(status: StatusString): void {
    this.setState({ status });
  }

  /**
   * Handle dynamic status update events from backend.
   * Requirements: 15.1
   */
  private onDynamicStatus(status: DynamicStatus): void {
    this.setState({ dynamicStatus: status });
  }

  /**
   * Handle binning progress events from backend.
   * Requirements: 8.1, 8.2
   */
  private onBinningProgress(progress: BinningProgress): void {
    this.setState({ binningProgress: progress });
  }

  /**
   * Handle binning complete events from backend.
   * Requirements: 8.3, 8.4
   */
  private onBinningComplete(result: BinningResult): void {
    this.setState({
      binningResult: result,
      binningProgress: null,
      isBinning: false,
    });
  }

  /**
   * Handle binning error events from backend.
   * Requirements: 8.3
   */
  private onBinningError(error: { message: string }): void {
    this.setState({
      isBinning: false,
      binningProgress: null,
    });
    // Error will be shown in UI via result or status
  }

  /**
   * Handle profile change events from backend.
   * Requirements: 4.4
   * 
   * Updates state with active profile name and shows notification.
   */
  private onProfileChanged(data: { profile_name: string; app_id: number | null }): void {
    // Update active profile in state
    if (data.app_id !== null) {
      // Find the profile in our local state
      const profile = this.state.gameProfiles?.find(p => p.app_id === data.app_id);
      if (profile) {
        this.setState({ activeProfile: profile });
      }
    } else {
      // Global default - clear active profile
      this.setState({ activeProfile: null });
    }
    
    // Show notification via Decky toast (if available)
    if (typeof DFL !== 'undefined' && DFL.Toaster) {
      DFL.Toaster.toast({
        title: "Profile Switched",
        body: `Now using: ${data.profile_name}`,
        duration: 3000,
      });
    }
  }

  /**
   * Handle telemetry sample events from backend.
   * Requirements: 2.1, 2.2, 2.3, 2.4
   * 
   * Feature: decktune-3.1-reliability-ux
   * Adds new telemetry sample to state, maintaining 60-second window.
   */
  private onTelemetrySample(sample: {
    timestamp: number;
    temperature_c: number;
    power_w: number;
    load_percent: number;
  }): void {
    const MAX_SAMPLES = 60; // Keep 60 seconds of data at 1Hz
    const now = Date.now() / 1000;
    const cutoffTime = now - 60;
    
    // Filter old samples and add new one
    const currentSamples = this.state.telemetrySamples || [];
    const filteredSamples = currentSamples.filter(s => s.timestamp >= cutoffTime);
    const newSamples = [...filteredSamples, sample].slice(-MAX_SAMPLES);
    
    this.setState({ telemetrySamples: newSamples });
  }

  /**
   * Handle app lifetime notifications from Steam.
   * Requirements: 5.2, 5.3
   * 
   * Detects game launch via SteamClient and applies preset with timeout.
   * Shows status: "Using preset for <GameName>"
   */
  async onAppLifetimeNotification(app: any): Promise<void> {
    const gameId = app.unAppID;
    const gameInfo = appStore.GetAppOverviewByGameID(gameId);

    if (app.bRunning) {
      // Game is starting
      if (!this.state.settings.isRunAutomatically) return;
      await this.handleMainRunningApp(gameId, gameInfo.display_name);
    } else {
      // Game is closing - revert to global settings
      this.setState({ 
        runningAppName: null, 
        runningAppId: null,
        cores: this.state.globalCores,
        currentPreset: null,
      });
      
      if (this.state.settings.isGlobal && this.state.status !== "disabled") {
        await this.applyUndervolt(this.state.globalCores);
        this.setState({ status: "Global" });
      } else {
        await this.disableUndervolt();
      }
    }
  }

  /**
   * Handle resume from suspend.
   */
  async onResumeFromSuspend(): Promise<void> {
    if (this.state.status === "enabled" || this.state.status.startsWith("Using preset for")) {
      await this.applyUndervolt(this.state.cores, 5);
    }
  }

  /**
   * Handle main running app detection.
   * Requirements: 5.2, 5.3
   * 
   * Applies preset for the running game and updates status.
   */
  async handleMainRunningApp(id?: number, label?: string): Promise<void> {
    if (DFL.Router.MainRunningApp || (id && label)) {
      const appName = label || DFL.Router.MainRunningApp?.display_name || null;
      const appId = id || Number(DFL.Router.MainRunningApp?.appid) || null;
      
      this.setState({
        runningAppName: appName,
        runningAppId: appId,
      });
      
      await this.applyUndervoltBasedOnPreset(appId, appName);
    } else {
      this.setState({ cores: this.state.globalCores });
    }
  }

  /**
   * Apply undervolt based on current preset.
   * Requirements: 5.2, 5.3
   * 
   * Finds preset for the running game and applies it with timeout.
   * Updates status to "Using preset for <GameName>" or "Global".
   */
  async applyUndervoltBasedOnPreset(appId?: number | null, appName?: string | null): Promise<void> {
    const targetAppId = appId ?? this.state.runningAppId;
    const targetAppName = appName ?? this.state.runningAppName;
    
    const preset = this.state.presets.find(
      (p) => p.app_id === targetAppId
    );
    
    if (preset) {
      // Found a preset for this game
      this.setState({ 
        cores: preset.value, 
        currentPreset: preset,
      });
      
      const timeout = preset.use_timeout ? preset.timeout : 0;
      await this.applyUndervolt(preset.value, timeout);
      
      // Update status to show which preset is being used (Requirement 5.3)
      const statusString = `Using preset for ${preset.label || targetAppName || 'Unknown'}` as StatusString;
      this.setState({ status: statusString });
    } else if (this.state.settings.isGlobal) {
      // No preset, but global mode is enabled - use global values
      this.setState({ 
        cores: this.state.globalCores,
        currentPreset: null,
      });
      await this.applyUndervolt(this.state.globalCores);
      this.setState({ status: "Global" });
    } else {
      // No preset and global mode disabled
      this.setState({ 
        currentPreset: null,
        status: "Disabled",
      });
    }
  }


  // ==================== Undervolt Control ====================

  /**
   * Apply undervolt values.
   */
  async applyUndervolt(core_values: number[], timeout: number = 0): Promise<void> {
    this.setState({ cores: core_values });
    await call("apply_undervolt", core_values, timeout);
  }

  /**
   * Disable undervolt (reset to 0).
   */
  async disableUndervolt(): Promise<void> {
    await call("disable_undervolt");
  }

  /**
   * Panic disable - emergency reset.
   */
  async panicDisable(): Promise<void> {
    await call("panic_disable");
    this.setState({
      status: "disabled",
      isAutotuning: false,
      autotuneProgress: null,
    });
  }

  // ==================== Dynamic Mode ====================

  /**
   * Enable gymdeck dynamic mode.
   */
  async enableGymdeck(): Promise<void> {
    await call("start_gymdeck", this.state.dynamicSettings);
    this.setState({ gymdeckRunning: true, status: "DYNAMIC RUNNING" });
  }

  /**
   * Disable gymdeck dynamic mode.
   */
  async disableGymdeck(): Promise<void> {
    await call("stop_gymdeck");
    this.setState({ gymdeckRunning: false, status: "disabled", dynamicStatus: null });
  }

  /**
   * Get current dynamic mode status.
   * Requirements: 15.1
   */
  async getDynamicStatus(): Promise<DynamicStatus | null> {
    const result = await call("get_dynamic_status") as any;
    
    if (result.running && result.load) {
      const status: DynamicStatus = {
        running: result.running,
        load: result.load,
        values: result.values,
        strategy: result.strategy,
        uptime_ms: result.uptime_ms,
        error: result.error,
      };
      this.setState({ dynamicStatus: status });
      return status;
    }
    
    this.setState({ dynamicStatus: null });
    return null;
  }

  // ==================== Autotune Methods ====================
  // Requirements: Frontend integration

  /**
   * Start autotune process.
   * @param mode - "quick" or "thorough"
   */
  async startAutotune(mode: "quick" | "thorough" = "quick"): Promise<{ success: boolean; error?: string }> {
    const result = (await call("start_autotune", mode)) as { success: boolean; error?: string };
    
    if (result.success) {
      this.setState({
        isAutotuning: true,
        autotuneProgress: null,
        autotuneResult: null,
      });
    }
    
    return result;
  }

  /**
   * Stop running autotune.
   */
  async stopAutotune(): Promise<{ success: boolean; error?: string }> {
    const result = (await call("stop_autotune")) as { success: boolean; error?: string };
    
    if (result.success) {
      this.setState({
        isAutotuning: false,
        autotuneProgress: null,
      });
    }
    
    return result;
  }

  // ==================== Binning Methods ====================
  // Requirements: 8.1, 8.2, 8.3, 8.4, 10.1

  /**
   * Start silicon binning process.
   * Requirements: 8.1
   * 
   * @param config - Optional binning configuration
   * @returns Promise with success status
   */
  async startBinning(config?: Partial<BinningConfig>): Promise<{ success: boolean; error?: string }> {
    const result = (await call("start_binning", config || {})) as { success: boolean; error?: string };
    
    if (result.success) {
      this.setState({
        isBinning: true,
        binningProgress: null,
        binningResult: null,
      });
    }
    
    return result;
  }

  /**
   * Stop running binning process.
   * Requirements: 8.1
   * 
   * @returns Promise with success status
   */
  async stopBinning(): Promise<{ success: boolean; error?: string }> {
    const result = (await call("stop_binning")) as { success: boolean; error?: string };
    
    if (result.success) {
      this.setState({
        isBinning: false,
        binningProgress: null,
      });
    }
    
    return result;
  }

  /**
   * Get current binning status.
   * Requirements: 8.1
   * 
   * @returns Current binning state or null
   */
  async getBinningStatus(): Promise<BinningState | null> {
    return (await call("get_binning_status")) as BinningState | null;
  }

  /**
   * Get binning configuration.
   * Requirements: 10.1
   * 
   * @returns Current binning configuration
   */
  async getBinningConfig(): Promise<BinningConfig> {
    const config = (await call("get_binning_config")) as BinningConfig;
    this.setState({ binningConfig: config });
    return config;
  }

  /**
   * Update binning configuration.
   * Requirements: 10.1, 10.2, 10.3, 10.4
   * 
   * @param config - Partial configuration to update
   * @returns Promise with success status
   */
  async updateBinningConfig(config: Partial<BinningConfig>): Promise<{ success: boolean; error?: string }> {
    const result = (await call("update_binning_config", config)) as { success: boolean; error?: string };
    
    if (result.success) {
      // Refresh config from backend
      await this.getBinningConfig();
    }
    
    return result;
  }

  /**
   * Tune for current game - run autotune and save as game preset.
   * Requirements: 5.4
   * 
   * @param mode - "quick" or "thorough" autotune mode
   * @returns Promise with success status and the created preset
   */
  async tuneForCurrentGame(mode: "quick" | "thorough" = "quick"): Promise<{ 
    success: boolean; 
    error?: string; 
    preset?: Preset;
  }> {
    // Check if a game is currently running
    if (!this.state.runningAppId || !this.state.runningAppName) {
      return { success: false, error: "No game is currently running" };
    }

    const appId = this.state.runningAppId;
    const appName = this.state.runningAppName;

    // Start autotune
    const startResult = await this.startAutotune(mode);
    if (!startResult.success) {
      return { success: false, error: startResult.error };
    }

    // Wait for autotune to complete by watching state changes
    return new Promise((resolve) => {
      const checkComplete = () => {
        const state = this.getState();
        
        if (state.autotuneResult) {
          // Autotune completed - save as preset
          const result = state.autotuneResult;
          
          if (result.stable) {
            // Create and save preset for this game
            const preset: Preset = {
              app_id: appId,
              label: appName,
              value: result.cores,
              timeout: 0,
              use_timeout: false,
              created_at: new Date().toISOString(),
              tested: true, // Marked as tested since autotune validates stability
            };

            // Save the preset
            this.saveAndApply(result.cores, true, preset).then(() => {
              resolve({ success: true, preset });
            }).catch((error) => {
              resolve({ success: false, error: String(error) });
            });
          } else {
            resolve({ 
              success: false, 
              error: "Autotune did not find stable values for all cores" 
            });
          }
          
          // Remove listener
          this.removeListener("state_change", checkComplete);
        } else if (!state.isAutotuning && !state.autotuneResult) {
          // Autotune was cancelled or failed
          resolve({ success: false, error: "Autotune was cancelled or failed" });
          this.removeListener("state_change", checkComplete);
        }
      };

      // Listen for state changes
      this.on("state_change", checkComplete);
    });
  }

  // ==================== Test Methods ====================
  // Requirements: Frontend integration

  /**
   * Check availability of required stress test binaries.
   * Call this on mount to show warnings if binaries are missing.
   * 
   * @returns Object with binary status and list of missing binaries
   */
  async checkBinaries(): Promise<{
    success: boolean;
    binaries: Record<string, boolean>;
    missing: string[];
    all_available: boolean;
  }> {
    return (await call("check_binaries")) as {
      success: boolean;
      binaries: Record<string, boolean>;
      missing: string[];
      all_available: boolean;
    };
  }

  /**
   * Install missing stress test binaries using pacman.
   * Executes: sudo pacman -S --noconfirm stress-ng memtester
   * 
   * @returns Object with installation result
   */
  async installBinaries(): Promise<{
    success: boolean;
    message?: string;
    installed?: string[];
    error?: string;
  }> {
    return (await call("install_binaries")) as {
      success: boolean;
      message?: string;
      installed?: string[];
      error?: string;
    };
  }

  /**
   * Run a specific stress test.
   * @param testName - Name of test (cpu_quick, cpu_long, ram_quick, ram_thorough, combo)
   */
  async runTest(testName: string): Promise<TestResult> {
    this.setState({ currentTest: testName, isTestRunning: true });
    
    const result = (await call("run_test", testName)) as TestResult;
    
    this.setState({ currentTest: null, isTestRunning: false });
    
    // Refresh test history after test completes
    await this.fetchTestHistory();
    
    return result;
  }

  /**
   * Get test history (last 10 results).
   */
  async getTestHistory(): Promise<TestHistoryEntry[]> {
    return await this.fetchTestHistory();
  }

  // ==================== Diagnostics Methods ====================
  // Requirements: Frontend integration

  /**
   * Export diagnostics archive.
   * @returns Path to the created archive
   */
  async exportDiagnostics(): Promise<{ success: boolean; path?: string; error?: string }> {
    return (await call("export_diagnostics")) as { success: boolean; path?: string; error?: string };
  }

  /**
   * Get system information for diagnostics tab.
   */
  async getSystemInfo(): Promise<any> {
    return await call("get_system_info");
  }


  // ==================== Preset Management ====================

  /**
   * Save and apply undervolt values.
   */
  async saveAndApply(
    core_values: number[],
    use_as_preset: boolean,
    presetSettings?: Partial<Preset>
  ): Promise<void> {
    if (use_as_preset) {
      const presetIndex = this.state.presets.findIndex(
        (p) => p.app_id === this.state.runningAppId
      );
      let preset: Preset;
      const presets = [...this.state.presets];

      if (presetIndex !== -1) {
        presets[presetIndex] = {
          ...presets[presetIndex],
          ...presetSettings,
          value: core_values,
        };
        preset = presets[presetIndex];
      } else {
        preset = {
          ...presetSettings,
          app_id: this.state.runningAppId!,
          value: core_values,
          label: this.state.runningAppName || "",
          timeout: presetSettings?.timeout || 0,
          use_timeout: presetSettings?.use_timeout || false,
        };
        presets.push(preset);
      }

      this.setState({ presets, currentPreset: preset });
      await call("save_preset", preset);
    } else {
      this.setState({ cores: core_values, globalCores: core_values });
    }

    await this.applyUndervolt(core_values);

    if (!use_as_preset) {
      await call("save_setting", "cores", core_values);
    }
  }

  /**
   * Save settings.
   */
  async saveSettings(settings: Settings): Promise<void> {
    await call("save_settings", settings);
    this.setState({ settings });
  }

  /**
   * Save a single setting value.
   */
  async saveSetting(key: string, value: any): Promise<void> {
    await call("save_setting", key, value);
  }

  /**
   * Get a single setting value.
   */
  async getSetting(key: string): Promise<any> {
    return await call("get_setting", key);
  }

  /**
   * Reset configuration to defaults.
   */
  async resetConfig(): Promise<void> {
    const result = (await call("reset_config")) as any;
    this.setState({
      globalCores: result.cores,
      cores: result.cores,
      settings: result.settings,
      status: "disabled",
      currentPreset: null,
    });
    await this.disableUndervolt();
  }

  /**
   * Delete a preset.
   */
  async deletePreset(app_id: number): Promise<void> {
    const presets = [...this.state.presets];
    const presetIndex = presets.findIndex((p) => p.app_id === app_id);
    if (presetIndex !== -1) {
      presets.splice(presetIndex, 1);
    }
    this.setState({ presets });
    await call("delete_preset", app_id);
  }

  /**
   * Update a preset.
   */
  async updatePreset(preset: Preset): Promise<void> {
    const presets = [...this.state.presets];
    const presetIndex = presets.findIndex((p) => p.app_id === preset.app_id);
    if (presetIndex !== -1) {
      presets[presetIndex] = preset;
    }
    this.setState({ presets });
    await call("update_preset", preset);

    if (preset.app_id === this.state.runningAppId) {
      if (this.state.settings.isRunAutomatically) {
        await this.applyUndervolt(preset.value);
      }
    }
  }

  /**
   * Export all presets as JSON.
   */
  async exportPresets(): Promise<string> {
    return (await call("export_presets")) as string;
  }

  /**
   * Import presets from JSON.
   */
  async importPresets(jsonData: string): Promise<{ success: boolean; imported_count?: number; error?: string }> {
    const result = (await call("import_presets", jsonData)) as { success: boolean; imported_count?: number; error?: string };
    
    if (result.success) {
      // Refresh presets from backend
      await this.fetchConfig();
    }
    
    return result;
  }

  // ==================== Expert Mode Methods ====================
  // Requirements: 13.1-13.6

  /**
   * Enable Expert Overclocker Mode.
   * Requires explicit user confirmation of risks.
   * 
   * @param confirmed - User has confirmed understanding of risks
   * @returns Object with success status and expert mode state
   */
  async enableExpertMode(confirmed: boolean = false): Promise<{
    success: boolean;
    expert_mode: boolean;
    confirmed: boolean;
    message?: string;
    error?: string;
  }> {
    const result = await call("enable_expert_mode", confirmed) as {
      success: boolean;
      expert_mode: boolean;
      confirmed: boolean;
      message?: string;
      error?: string;
    };
    
    if (result.success) {
      // Update state to reflect expert mode is active
      this.emit("expert_mode_changed", { enabled: true });
    }
    
    return result;
  }

  /**
   * Disable Expert Overclocker Mode.
   * Returns to safe platform limits.
   * 
   * @returns Object with success status
   */
  async disableExpertMode(): Promise<{
    success: boolean;
    expert_mode: boolean;
    message?: string;
  }> {
    const result = await call("disable_expert_mode") as {
      success: boolean;
      expert_mode: boolean;
      message?: string;
    };
    
    if (result.success) {
      // Update state to reflect expert mode is disabled
      this.emit("expert_mode_changed", { enabled: false });
    }
    
    return result;
  }

  /**
   * Get current Expert Mode status.
   * 
   * @returns Object with expert mode state and limits
   */
  async getExpertModeStatus(): Promise<{
    expert_mode: boolean;
    confirmed: boolean;
    active: boolean;
    min_limit: number;
    max_limit: number;
  }> {
    return await call("get_expert_mode_status") as {
      expert_mode: boolean;
      confirmed: boolean;
      active: boolean;
      min_limit: number;
      max_limit: number;
    };
  }

  // ==================== Profile Management Methods ====================
  // Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 9.1, 9.2

  /**
   * Create a new game profile.
   * Requirements: 3.1, 5.1
   * 
   * @param profile - Profile data to create
   * @returns Promise with success status
   */
  async createProfile(profile: Omit<GameProfile, 'created_at' | 'last_used'>): Promise<{
    success: boolean;
    profile?: GameProfile;
    error?: string;
  }> {
    const result = await call("create_profile", profile) as {
      success: boolean;
      profile?: GameProfile;
      error?: string;
    };
    
    if (result.success && result.profile) {
      // Add to local state
      const profiles = [...(this.state.gameProfiles || []), result.profile];
      this.setState({ gameProfiles: profiles });
    }
    
    return result;
  }

  /**
   * Get all game profiles.
   * Requirements: 3.2
   * 
   * @returns Array of all game profiles
   */
  async getProfiles(): Promise<GameProfile[]> {
    const profiles = await call("get_profiles") as GameProfile[];
    this.setState({ gameProfiles: profiles });
    return profiles;
  }

  /**
   * Update an existing game profile.
   * Requirements: 3.3
   * 
   * @param appId - Steam AppID of the profile to update
   * @param updates - Partial profile data to update
   * @returns Promise with success status
   */
  async updateProfile(appId: number, updates: Partial<GameProfile>): Promise<{
    success: boolean;
    profile?: GameProfile;
    error?: string;
  }> {
    const result = await call("update_profile", appId, updates) as {
      success: boolean;
      profile?: GameProfile;
      error?: string;
    };
    
    if (result.success && result.profile) {
      // Update local state
      const profiles = [...(this.state.gameProfiles || [])];
      const index = profiles.findIndex(p => p.app_id === appId);
      if (index !== -1) {
        profiles[index] = result.profile;
        this.setState({ gameProfiles: profiles });
      }
    }
    
    return result;
  }

  /**
   * Delete a game profile.
   * Requirements: 3.4
   * 
   * @param appId - Steam AppID of the profile to delete
   * @returns Promise with success status
   */
  async deleteProfile(appId: number): Promise<{
    success: boolean;
    error?: string;
  }> {
    const result = await call("delete_profile", appId) as {
      success: boolean;
      error?: string;
    };
    
    if (result.success) {
      // Remove from local state
      const profiles = (this.state.gameProfiles || []).filter(p => p.app_id !== appId);
      this.setState({ gameProfiles: profiles });
      
      // If this was the active profile, clear it
      if (this.state.activeProfile?.app_id === appId) {
        this.setState({ activeProfile: null });
      }
    }
    
    return result;
  }

  /**
   * Create a profile for the currently running game.
   * Requirements: 5.1, 5.2, 5.3, 5.4
   * 
   * Automatically populates app_id and game name from the running game.
   * Captures current undervolt and dynamic mode settings.
   * 
   * @returns Promise with success status and created profile
   */
  async createProfileForCurrentGame(): Promise<{
    success: boolean;
    profile?: GameProfile;
    error?: string;
  }> {
    if (!this.state.runningAppId || !this.state.runningAppName) {
      return {
        success: false,
        error: "No game is currently running"
      };
    }
    
    const result = await call("create_profile_for_current_game") as {
      success: boolean;
      profile?: GameProfile;
      error?: string;
    };
    
    if (result.success && result.profile) {
      // Add to local state
      const profiles = [...(this.state.gameProfiles || []), result.profile];
      this.setState({ 
        gameProfiles: profiles,
        activeProfile: result.profile
      });
    }
    
    return result;
  }

  /**
   * Export all game profiles as JSON.
   * Requirements: 9.1
   * 
   * @returns JSON string containing all profiles
   */
  async exportGameProfiles(): Promise<{
    success: boolean;
    json?: string;
    path?: string;
    error?: string;
  }> {
    return await call("export_profiles") as {
      success: boolean;
      json?: string;
      path?: string;
      error?: string;
    };
  }

  /**
   * Import game profiles from JSON.
   * Requirements: 9.2, 9.3, 9.4
   * 
   * @param jsonData - JSON string containing profiles to import
   * @param mergeStrategy - How to handle conflicts: "skip", "overwrite", "rename"
   * @returns Promise with import result
   */
  async importGameProfiles(jsonData: string, mergeStrategy: "skip" | "overwrite" | "rename" = "skip"): Promise<{
    success: boolean;
    imported_count: number;
    conflicts: number[];
    error?: string;
  }> {
    const result = await call("import_profiles", jsonData, mergeStrategy) as {
      success: boolean;
      imported_count: number;
      conflicts: number[];
      error?: string;
    };
    
    if (result.success) {
      // Refresh profiles from backend
      await this.getProfiles();
    }
    
    return result;
  }

  // ==================== Benchmark Methods ====================
  // Requirements: 7.1, 7.3, 7.5

  /**
   * Run a 10-second benchmark using stress-ng.
   * Requirements: 7.1, 7.4
   * 
   * Blocks other operations during execution.
   * 
   * @returns Promise with benchmark result
   */
  async runBenchmark(): Promise<{
    success: boolean;
    result?: BenchmarkResult;
    error?: string;
  }> {
    // Set running state before starting
    this.setState({ isBenchmarkRunning: true });
    
    const response = await call("run_benchmark") as {
      success: boolean;
      result?: BenchmarkResult;
      error?: string;
    };
    
    if (response.success && response.result) {
      // Update state with new result
      this.setState({
        isBenchmarkRunning: false,
        lastBenchmarkResult: response.result,
      });
      
      // Refresh benchmark history
      await this.getBenchmarkHistory();
    } else {
      // Clear running state on error
      this.setState({ isBenchmarkRunning: false });
    }
    
    return response;
  }

  /**
   * Get benchmark history (last 20 results).
   * Requirements: 7.5
   * 
   * @returns Array of benchmark results with comparisons
   */
  async getBenchmarkHistory(): Promise<BenchmarkResult[]> {
    const history = await call("get_benchmark_history") as BenchmarkResult[];
    this.setState({ benchmarkHistory: history });
    return history;
  }

  // ==================== Session History Methods ====================
  // Requirements: 8.4, 8.5, 8.6

  /**
   * Get session history.
   * Requirements: 8.4
   * 
   * @param limit - Maximum number of sessions to return (default 30)
   * @returns Array of sessions, most recent first
   */
  async getSessionHistory(limit: number = 30): Promise<Session[]> {
    const sessions = await call("get_session_history", limit) as Session[];
    return sessions || [];
  }

  /**
   * Get a specific session by ID.
   * Requirements: 8.5
   * 
   * @param sessionId - UUID of the session to retrieve
   * @returns Session if found, null otherwise
   */
  async getSession(sessionId: string): Promise<Session | null> {
    return await call("get_session", sessionId) as Session | null;
  }

  /**
   * Compare two sessions and return metric differences.
   * Requirements: 8.6
   * 
   * @param id1 - ID of first session
   * @param id2 - ID of second session
   * @returns Comparison result with diff values
   */
  async compareSessions(id1: string, id2: string): Promise<SessionComparison | null> {
    return await call("compare_sessions", id1, id2) as SessionComparison | null;
  }

  // ==================== Fan Control Methods ====================

  /**
   * Get current fan control configuration.
   * 
   * @returns Fan configuration with enabled status and curve points
   */
  async getFanConfig(): Promise<{
    success: boolean;
    config?: any;
    error?: string;
  }> {
    return await call("get_fan_config") as any;
  }

  /**
   * Set fan control configuration.
   * 
   * @param config - Fan configuration to apply
   * @returns Success status
   */
  async setFanConfig(config: any): Promise<{
    success: boolean;
    error?: string;
  }> {
    return await call("set_fan_config", config) as any;
  }

  /**
   * Get current fan status (RPM, temperature).
   * 
   * @returns Current fan status
   */
  async getFanStatus(): Promise<{
    success: boolean;
    status?: any;
    error?: string;
  }> {
    return await call("get_fan_status") as any;
  }

  // ==================== Dynamic Mode Configuration ====================

  /**
   * Get dynamic mode configuration.
   * 
   * @returns Current dynamic configuration
   */
  async getDynamicConfig(): Promise<any> {
    return await call("get_dynamic_config") as any;
  }

  /**
   * Save dynamic mode configuration.
   * 
   * @param config - Dynamic configuration to save
   * @returns Success status
   */
  async saveDynamicConfig(config: any): Promise<{
    success: boolean;
    error?: string;
  }> {
    return await call("save_dynamic_config", config) as any;
  }

  /**
   * Enable gymdeck3 dynamic mode.
   * 
   * @returns Success status
   */
  async enableGymdeck(): Promise<{
    success: boolean;
    error?: string;
  }> {
    const dynamicSettings = this.state.dynamicSettings;
    return await call("start_gymdeck", dynamicSettings) as any;
  }

  /**
   * Disable gymdeck3 dynamic mode.
   * 
   * @returns Success status
   */
  async disableGymdeck(): Promise<{
    success: boolean;
    error?: string;
  }> {
    return await call("stop_gymdeck") as any;
  }

  // ==================== Server Events ====================

  /**
   * Handle server events.
   */
  handleServerEvent({ type, data }: ServerEvent): void {
    switch (type) {
      case "update_status":
        this.setState({ status: data });
        break;
      case "tuning_progress":
        this.onTuningProgress(data);
        break;
      case "tuning_complete":
        this.onTuningComplete(data);
        break;
      case "test_complete":
        this.onTestComplete(data);
        break;
    }
  }

  // ==================== Cleanup ====================

  /**
   * Cleanup and unregister listeners.
   */
  destroy(): void {
    this.registeredListeners.forEach((listener) => {
      listener.unregister();
    });
    
    removeEventListener("tuning_progress", this.onTuningProgress.bind(this));
    removeEventListener("tuning_complete", this.onTuningComplete.bind(this));
    removeEventListener("test_complete", this.onTestComplete.bind(this));
    removeEventListener("update_status", this.onStatusUpdate.bind(this));
    removeEventListener("dynamic_status", this.onDynamicStatus.bind(this));
    removeEventListener("binning_progress", this.onBinningProgress.bind(this));
    removeEventListener("binning_complete", this.onBinningComplete.bind(this));
    removeEventListener("binning_error", this.onBinningError.bind(this));
    removeEventListener("profile_changed", this.onProfileChanged.bind(this));
    removeEventListener("telemetry_sample", this.onTelemetrySample.bind(this));
  }
}

export default Api;
