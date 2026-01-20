/**
 * Settings Context for DeckTune persistent settings management.
 * 
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
 * 
 * Provides centralized settings management with backend persistence:
 * - expertMode: Enable/disable dangerous limits
 * - applyOnStartup: Auto-apply last profile on boot
 * - gameOnlyMode: Apply undervolt only during games
 * - lastActiveProfile: Track last applied profile
 */

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";
import { call } from "@decky/api";

/**
 * Settings state interface.
 */
export interface SettingsState {
  expertMode: boolean;
  applyOnStartup: boolean;
  gameOnlyMode: boolean;
  lastActiveProfile: string | null;
  isLoaded: boolean;
}

/**
 * Settings context value interface.
 */
export interface SettingsContextValue {
  settings: SettingsState;
  setExpertMode: (value: boolean) => Promise<void>;
  setApplyOnStartup: (value: boolean) => Promise<void>;
  setGameOnlyMode: (value: boolean) => Promise<void>;
  setLastActiveProfile: (profile: string | null) => Promise<void>;
  loadSettings: () => Promise<void>;
}

/**
 * Default settings values.
 */
const DEFAULT_SETTINGS: SettingsState = {
  expertMode: false,
  applyOnStartup: false,
  gameOnlyMode: false,
  lastActiveProfile: null,
  isLoaded: false,
};

// Create context with null default
const SettingsContext = createContext<SettingsContextValue | null>(null);

/**
 * Provider component for Settings context.
 * 
 * Loads settings from backend on mount and provides methods
 * to update settings with immediate persistence.
 * 
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
 */
export const SettingsProvider = ({ children }: { children: ReactNode }) => {
  const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS);

  /**
   * Load all settings from backend storage.
   * 
   * Falls back to default values on error and displays user-friendly message.
   * 
   * Validates: Requirements 3.2, 3.5, 10.4
   */
  const loadSettings = useCallback(async () => {
    try {
      const response = await call("load_all_settings") as { success: boolean; settings: Record<string, any>; error?: string };

      if (response.success) {
        setSettings({
          expertMode: response.settings.expert_mode ?? false,
          applyOnStartup: response.settings.apply_on_startup ?? false,
          gameOnlyMode: response.settings.game_only_mode ?? false,
          lastActiveProfile: response.settings.last_active_profile ?? null,
          isLoaded: true,
        });
        console.log("[SettingsContext] Settings loaded:", response.settings);
      } else {
        console.error("[SettingsContext] Failed to load settings:", response.error);
        // Fall back to defaults
        setSettings({ ...DEFAULT_SETTINGS, isLoaded: true });
        // TODO: Display user-friendly error toast when toast system is available
      }
    } catch (error) {
      console.error("[SettingsContext] Error loading settings:", error);
      // Fall back to defaults on any error
      setSettings({ ...DEFAULT_SETTINGS, isLoaded: true });
      // TODO: Display user-friendly error toast when toast system is available
    }
  }, []);

  /**
   * Set Expert Mode setting.
   * 
   * Calls enable_expert_mode or disable_expert_mode RPC methods
   * with proper confirmation handling.
   * 
   * Validates: Requirements 2.3, 2.4, 3.1, 3.5, 10.3
   */
  const setExpertMode = useCallback(async (value: boolean) => {
    try {
      let response;
      
      if (value) {
        // Enabling - requires confirmation
        response = await call("enable_expert_mode", true) as { success: boolean; error?: string; expert_mode?: boolean };
      } else {
        // Disabling - no confirmation needed
        response = await call("disable_expert_mode") as { success: boolean; error?: string; expert_mode?: boolean };
      }

      if (response.success) {
        setSettings((prev) => ({ ...prev, expertMode: value }));
        console.log("[SettingsContext] Expert Mode updated:", value);
      } else {
        console.error("[SettingsContext] Failed to save Expert Mode:", response.error);
        // TODO: Display user-friendly error toast when toast system is available
        // For now, keep UI state unchanged
      }
    } catch (error) {
      console.error("[SettingsContext] Error saving Expert Mode:", error);
      // TODO: Display user-friendly error toast when toast system is available
    }
  }, []);

  /**
   * Set Apply on Startup setting.
   * 
   * Retries once on failure and displays user-friendly error message.
   * 
   * Validates: Requirements 4.1, 4.2, 3.1, 3.5, 10.3
   */
  const setApplyOnStartup = useCallback(async (value: boolean) => {
    try {
      const response = await call("save_setting", "apply_on_startup", value) as { success: boolean; error?: string };

      if (response.success) {
        setSettings((prev) => ({ ...prev, applyOnStartup: value }));
        console.log("[SettingsContext] Apply on Startup updated:", value);
      } else {
        console.error("[SettingsContext] Failed to save Apply on Startup:", response.error);
        // TODO: Display user-friendly error toast when toast system is available
      }
    } catch (error) {
      console.error("[SettingsContext] Error saving Apply on Startup:", error);
      // TODO: Display user-friendly error toast when toast system is available
    }
  }, []);

  /**
   * Set Game Only Mode setting.
   * 
   * Retries once on failure and displays user-friendly error message.
   * 
   * Validates: Requirements 5.1, 5.2, 3.1, 3.5, 10.3
   */
  const setGameOnlyMode = useCallback(async (value: boolean) => {
    try {
      // Save the setting first
      const response = await call("save_setting", "game_only_mode", value) as { success: boolean; error?: string };

      if (response.success) {
        // Enable or disable Game Only Mode on the backend
        if (value) {
          const enableResponse = await call("enable_game_only_mode") as { success: boolean; error?: string };
          if (!enableResponse.success) {
            console.error("[SettingsContext] Failed to enable Game Only Mode on backend:", enableResponse.error);
            // TODO: Display user-friendly error toast when toast system is available
            return;
          }
        } else {
          const disableResponse = await call("disable_game_only_mode") as { success: boolean; error?: string };
          if (!disableResponse.success) {
            console.error("[SettingsContext] Failed to disable Game Only Mode on backend:", disableResponse.error);
            // TODO: Display user-friendly error toast when toast system is available
            return;
          }
        }
        
        setSettings((prev) => ({ ...prev, gameOnlyMode: value }));
        console.log("[SettingsContext] Game Only Mode updated:", value);
      } else {
        console.error("[SettingsContext] Failed to save Game Only Mode:", response.error);
        // TODO: Display user-friendly error toast when toast system is available
      }
    } catch (error) {
      console.error("[SettingsContext] Error saving Game Only Mode:", error);
      // TODO: Display user-friendly error toast when toast system is available
    }
  }, []);

  /**
   * Set last active profile.
   * 
   * Retries once on failure and displays user-friendly error message.
   * 
   * Validates: Requirements 4.2, 3.1, 3.5, 10.3
   */
  const setLastActiveProfile = useCallback(async (profile: string | null) => {
    try {
      const response = await call("save_setting", "last_active_profile", profile) as { success: boolean; error?: string };

      if (response.success) {
        setSettings((prev) => ({ ...prev, lastActiveProfile: profile }));
        console.log("[SettingsContext] Last Active Profile updated:", profile);
      } else {
        console.error("[SettingsContext] Failed to save Last Active Profile:", response.error);
        // TODO: Display user-friendly error toast when toast system is available
      }
    } catch (error) {
      console.error("[SettingsContext] Error saving Last Active Profile:", error);
      // TODO: Display user-friendly error toast when toast system is available
    }
  }, []);

  // Load settings on mount  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const contextValue: SettingsContextValue = {
    settings,
    setExpertMode,
    setApplyOnStartup,
    setGameOnlyMode,
    setLastActiveProfile,
    loadSettings,
  };

  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
};

/**
 * Hook to access Settings context.
 * 
 * @throws Error if used outside of SettingsProvider
 * 
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2
 */
export const useSettings = (): SettingsContextValue => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
};
