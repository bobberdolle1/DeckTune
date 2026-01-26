/**
 * SettingsMenu component for DeckTune.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 * 
 * Provides centralized settings management interface:
 * - Expert Mode toggle with confirmation dialog
 * - Binning Settings (test duration, step size, start value)
 * - Modal overlay with backdrop dismiss
 * - Gamepad navigation support
 * - Accessibility compliant (WCAG AA)
 */

import { FC, useState, useEffect } from "react";
import { PanelSection, PanelSectionRow, Focusable } from "@decky/ui";
import { FaTimes, FaExclamationTriangle, FaCheck } from "react-icons/fa";
import { call } from "@decky/api";
import { useSettings } from "../context/SettingsContext";
import { FocusableButton } from "./FocusableButton";

/**
 * Props for SettingsMenu component.
 */
export interface SettingsMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Props for Expert Mode Warning Dialog.
 */
interface ExpertWarningDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Expert Mode Warning Dialog component.
 * 
 * Requirements: 2.3, 2.4, 9.3
 * 
 * Displays warning about risks and requires explicit confirmation
 * before enabling Expert Mode.
 */
const ExpertWarningDialog: FC<ExpertWarningDialogProps> = ({
  isOpen,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        zIndex: 10000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="expert-warning-title"
      aria-describedby="expert-warning-description"
    >
      <div
        style={{
          backgroundColor: "#1a1d23",
          borderRadius: "8px",
          padding: "16px",
          maxWidth: "400px",
          border: "2px solid #ff6b6b",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "12px",
          }}
        >
          <FaExclamationTriangle
            style={{ color: "#ff6b6b", fontSize: "20px" }}
            aria-hidden="true"
          />
          <div
            id="expert-warning-title"
            style={{
              fontSize: "14px",
              fontWeight: "bold",
              color: "#ff6b6b",
            }}
          >
            Expert Undervolter Mode
          </div>
        </div>

        <div
          id="expert-warning-description"
          style={{
            fontSize: "11px",
            lineHeight: "1.5",
            marginBottom: "12px",
            color: "#e0e0e0",
          }}
        >
          <p style={{ marginBottom: "8px" }}>
            <strong>⚠️ WARNING:</strong> Expert mode removes safety limits.
          </p>
          <p style={{ marginBottom: "8px", color: "#ff9800" }}>
            <strong>Risks:</strong> System instability, crashes, data loss,
            hardware damage.
          </p>
          <p style={{ color: "#f44336", fontWeight: "bold", fontSize: "10px" }}>
            Use at your own risk!
          </p>
        </div>

        <Focusable
          style={{ display: "flex", gap: "8px" }}
          flow-children="horizontal"
        >
          <FocusableButton onClick={onConfirm} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "8px",
                backgroundColor: "#b71c1c",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "bold",
              }}
            >
              <FaCheck size={10} aria-hidden="true" />
              <span>I Understand</span>
            </div>
          </FocusableButton>

          <FocusableButton onClick={onCancel} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "8px",
                backgroundColor: "#3d4450",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "bold",
              }}
            >
              <FaTimes size={10} aria-hidden="true" />
              <span>Cancel</span>
            </div>
          </FocusableButton>
        </Focusable>
      </div>
    </div>
  );
};

/**
 * SettingsMenu component - centralized settings management.
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 * 
 * Features:
 * - Modal overlay with backdrop dismiss
 * - Expert Mode toggle with confirmation
 * - Binning Settings (test duration, step size, start value)
 * - Auto-save on changes (Requirement 9.4)
 * - Gamepad navigation support
 * - WCAG AA compliant
 */
export const SettingsMenu: FC<SettingsMenuProps> = ({ isOpen, onClose }) => {
  const settings = useSettings();
  const [showExpertWarning, setShowExpertWarning] = useState(false);
  
  // Binning config state
  const [binningConfig, setBinningConfig] = useState({
    test_duration: 60,
    step_size: 5,
    start_value: -10,
  });
  const [binningLoaded, setBinningLoaded] = useState(false);

  // Load binning config on mount
  useEffect(() => {
    if (isOpen && !binningLoaded) {
      loadBinningConfig();
    }
  }, [isOpen]);

  const loadBinningConfig = async () => {
    try {
      const response = await call("get_binning_config") as { success: boolean; config: any };
      if (response.success && response.config) {
        setBinningConfig({
          test_duration: response.config.test_duration || 60,
          step_size: response.config.step_size || 5,
          start_value: response.config.start_value || -10,
        });
        setBinningLoaded(true);
      }
    } catch (err) {
      console.error("Failed to load binning config:", err);
    }
  };

  const updateBinningConfig = async (updates: Partial<typeof binningConfig>) => {
    const newConfig = { ...binningConfig, ...updates };
    setBinningConfig(newConfig);
    
    try {
      await call("update_binning_config", newConfig);
    } catch (err) {
      console.error("Failed to update binning config:", err);
    }
  };

  if (!isOpen) return null;

  /**
   * Handle Expert Mode toggle.
   * 
   * Requirements: 2.3, 2.4
   * Shows confirmation dialog when enabling, directly disables when turning off.
   */
  const handleExpertModeToggle = () => {
    if (!settings.settings.expertMode) {
      // Enabling - show warning dialog
      setShowExpertWarning(true);
    } else {
      // Disabling - no confirmation needed
      settings.setExpertMode(false);
    }
  };

  /**
   * Handle Expert Mode confirmation.
   * 
   * Requirements: 2.4, 9.4
   */
  const handleExpertModeConfirm = async () => {
    await settings.setExpertMode(true);
    setShowExpertWarning(false);
  };

  /**
   * Handle Expert Mode cancellation.
   * 
   * Requirements: 2.4
   */
  const handleExpertModeCancel = () => {
    setShowExpertWarning(false);
  };

  /**
   * Handle backdrop click to close menu.
   * 
   * Requirements: 2.1, 9.5
   */
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <>
      {/* Modal backdrop - Requirements: 2.1, 9.5 */}
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.85)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "20px",
        }}
        onClick={handleBackdropClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-menu-title"
      >
        {/* Settings panel - FIXED: Added scroll */}
        <div
          style={{
            backgroundColor: "#1a1d23",
            borderRadius: "8px",
            padding: "16px",
            maxWidth: "400px",
            width: "100%",
            maxHeight: "80vh",
            overflowY: "auto",
            border: "1px solid #3d4450",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header with close button - Requirements: 2.1 */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "16px",
            }}
          >
            <h2
              id="settings-menu-title"
              style={{
                fontSize: "16px",
                fontWeight: "bold",
                color: "#fff",
                margin: 0,
              }}
            >
              Settings
            </h2>

            <FocusableButton onClick={onClose}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "32px",
                  height: "32px",
                  backgroundColor: "#3d4450",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
                aria-label="Close settings"
              >
                <FaTimes size={14} color="#fff" aria-hidden="true" />
              </div>
            </FocusableButton>
          </div>

          {/* Settings content */}
          <PanelSection>
            {/* Expert Mode section - Requirements: 2.2, 9.1, 9.2 */}
            <PanelSectionRow>
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    color: "#fff",
                    marginBottom: "8px",
                  }}
                >
                  Expert Mode
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "8px",
                    lineHeight: "1.4",
                  }}
                >
                  Removes safety limits for advanced undervolting. Use with
                  caution.
                </div>

                <FocusableButton
                  onClick={handleExpertModeToggle}
                  style={{ width: "100%" }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 12px",
                      backgroundColor: settings.settings.expertMode
                        ? "#b71c1c"
                        : "#3d4450",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: "bold",
                    }}
                    role="switch"
                    aria-checked={settings.settings.expertMode}
                    aria-label="Expert Mode toggle"
                  >
                    <span>
                      {settings.settings.expertMode ? "⚠ Expert Mode" : "Expert Mode"}
                    </span>
                    <span style={{ fontSize: "10px", color: "#8b929a" }}>
                      {settings.settings.expertMode ? "ON" : "OFF"}
                    </span>
                  </div>
                </FocusableButton>
              </div>
            </PanelSectionRow>

            {/* Apply on Startup section */}
            <PanelSectionRow>
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    color: "#fff",
                    marginBottom: "8px",
                  }}
                >
                  Apply on Startup
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "8px",
                    lineHeight: "1.4",
                  }}
                >
                  Automatically apply last profile when Steam Deck boots
                </div>

                <FocusableButton
                  onClick={() => settings.setApplyOnStartup(!settings.settings.applyOnStartup)}
                  style={{ width: "100%" }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 12px",
                      backgroundColor: settings.settings.applyOnStartup
                        ? "#1a9fff"
                        : "#3d4450",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: "bold",
                    }}
                    role="switch"
                    aria-checked={settings.settings.applyOnStartup}
                    aria-label="Apply on Startup toggle"
                  >
                    <span>
                      {settings.settings.applyOnStartup ? "✓ Apply on Startup" : "Apply on Startup"}
                    </span>
                    <span style={{ fontSize: "10px", color: "#8b929a" }}>
                      {settings.settings.applyOnStartup ? "ON" : "OFF"}
                    </span>
                  </div>
                </FocusableButton>
              </div>
            </PanelSectionRow>

            {/* Game Only Mode section */}
            <PanelSectionRow>
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    color: "#fff",
                    marginBottom: "8px",
                  }}
                >
                  Game Only Mode
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "8px",
                    lineHeight: "1.4",
                  }}
                >
                  Apply undervolt only when games are running, reset in Steam menu
                </div>

                <FocusableButton
                  onClick={() => settings.setGameOnlyMode(!settings.settings.gameOnlyMode)}
                  style={{ width: "100%" }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 12px",
                      backgroundColor: settings.settings.gameOnlyMode
                        ? "#1a9fff"
                        : "#3d4450",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: "bold",
                    }}
                    role="switch"
                    aria-checked={settings.settings.gameOnlyMode}
                    aria-label="Game Only Mode toggle"
                  >
                    <span>
                      {settings.settings.gameOnlyMode ? "✓ Game Only Mode" : "Game Only Mode"}
                    </span>
                    <span style={{ fontSize: "10px", color: "#8b929a" }}>
                      {settings.settings.gameOnlyMode ? "ON" : "OFF"}
                    </span>
                  </div>
                </FocusableButton>
              </div>
            </PanelSectionRow>

            {/* Binning Settings section */}
            {/* Wizard Settings section - FIXED: Gamepad navigation with D-pad/stick */}
            <PanelSectionRow>
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    color: "#fff",
                    marginBottom: "8px",
                  }}
                >
                  Wizard Settings
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "12px",
                    lineHeight: "1.4",
                  }}
                >
                  Advanced configuration for Wizard Mode testing algorithm.
                </div>

                <Focusable style={{ display: "flex", flexDirection: "column", gap: "12px" }} flow-children="vertical">
                  <SliderField
                    label="Test Duration"
                    value={binningConfig.test_duration}
                    min={30}
                    max={300}
                    step={10}
                    onChange={(value) => updateBinningConfig({ test_duration: value })}
                    showValue={true}
                    valueSuffix=" sec"
                    bottomSeparator="none"
                  />

                  <SliderField
                    label="Step Size"
                    value={binningConfig.step_size}
                    min={1}
                    max={10}
                    step={1}
                    onChange={(value) => updateBinningConfig({ step_size: value })}
                    showValue={true}
                    valueSuffix=" mV"
                    bottomSeparator="none"
                  />

                  <SliderField
                    label="Start Value"
                    value={Math.abs(binningConfig.start_value)}
                    min={5}
                    max={20}
                    step={5}
                    onChange={(value) => updateBinningConfig({ start_value: -value })}
                    showValue={true}
                    valueSuffix=" mV"
                    bottomSeparator="none"
                  />
                </Focusable>
              </div>
            </PanelSectionRow>

            {/* Visual feedback for saved state - Requirements: 9.5 */}
            <PanelSectionRow>
              <div
                style={{
                  fontSize: "9px",
                  color: "#4caf50",
                  textAlign: "center",
                  padding: "4px",
                }}
              >
                ✓ Changes saved automatically
              </div>
            </PanelSectionRow>
            
            {/* CRITICAL FIX: Reset Settings Button */}
            <PanelSectionRow>
              <FocusableButton
                onClick={async () => {
                  if (confirm("Reset all settings to defaults? This will clear wizard setup state and all configurations.")) {
                    try {
                      // Clear localStorage
                      localStorage.removeItem('decktune_wizard_setup_complete');
                      localStorage.removeItem('decktune_ui_mode');
                      localStorage.removeItem('decktune_last_mode');
                      
                      // Reset binning config
                      await call("update_binning_config", {
                        test_duration: 60,
                        step_size: 5,
                        start_value: -10,
                      });
                      
                      // Reset expert mode
                      await settings.setExpertMode(false);
                      
                      // Reload page
                      window.location.reload();
                    } catch (err) {
                      console.error("Failed to reset settings:", err);
                    }
                  }
                }}
                style={{
                  width: "100%",
                  padding: "10px",
                  backgroundColor: "#f44336",
                  borderRadius: "4px",
                  color: "#fff",
                  fontWeight: "bold",
                  fontSize: "12px",
                  textAlign: "center",
                  cursor: "pointer",
                }}
              >
                Reset All Settings
              </FocusableButton>
            </PanelSectionRow>
          </PanelSection>
        </div>
      </div>

      {/* Expert Mode Warning Dialog - Requirements: 2.3, 2.4 */}
      <ExpertWarningDialog
        isOpen={showExpertWarning}
        onConfirm={handleExpertModeConfirm}
        onCancel={handleExpertModeCancel}
      />
    </>
  );
};

export default SettingsMenu;
