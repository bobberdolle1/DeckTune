/**
 * API class for DeckTune frontend state management.
 * 
 * Feature: decktune, Frontend State Management
 * Requirements: Frontend integration, State management
 * 
 * This class manages frontend state and provides RPC methods for
 * communicating with the Python backend.
 */

import EventEmitter from "eventemitter3";
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
  ServerEvent,
  StatusString,
} from "./types";

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
 * Extends EventEmitter to provide state change notifications.
 * Implements all RPC methods for backend communication.
 */
export class Api extends EventEmitter {
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

    // Register Steam client listeners
    this.registeredListeners.push(
      SteamClient.GameSessions.RegisterForAppLifetimeNotifications(
        this.onAppLifetimeNotification.bind(this)
      )
    );
    this.registeredListeners.push(
      SteamClient.System.RegisterForOnResumeFromSuspend(
        this.onResumeFromSuspend.bind(this)
      )
    );

    // Register backend event listeners
    addEventListener("tuning_progress", this.onTuningProgress.bind(this));
    addEventListener("tuning_complete", this.onTuningComplete.bind(this));
    addEventListener("test_complete", this.onTestComplete.bind(this));
    addEventListener("update_status", this.onStatusUpdate.bind(this));

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
    this.setState({ gymdeckRunning: false, status: "disabled" });
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
  }
}

export default Api;
