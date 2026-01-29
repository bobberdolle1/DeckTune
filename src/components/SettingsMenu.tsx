/**
 * SettingsMenu component for DeckTune.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 * 
 * Provides centralized settings management interface:
 * - Expert Mode toggle with confirmation dialog
 * - Binning Settings (test duration, step size, start value)
 * - Update Management (check for updates, install)
 * - Modal overlay with backdrop dismiss
 * - Gamepad navigation support
 * - Accessibility compliant (WCAG AA)
 */

import { FC, useState, useEffect } from "react";
import { PanelSection, PanelSectionRow, Focusable, SliderField } from "@decky/ui";
import { FaTimes, FaExclamationTriangle, FaCheck, FaDownload, FaSync } from "react-icons/fa";
import { call } from "@decky/api";
import { useSettings } from "../context/SettingsContext";
import { FocusableButton } from "./FocusableButton";

// Add CSS animation for spinner
const spinKeyframes = `
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
`;

// Inject keyframes into document
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = spinKeyframes;
  document.head.appendChild(style);
}

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

  // Update state
  const [updateInfo, setUpdateInfo] = useState<{
    checking: boolean;
    available: boolean;
    currentVersion: string;
    latestVersion?: string;
    releaseNotes?: string;
    downloadUrl?: string;
    error?: string;
  }>({
    checking: false,
    available: false,
    currentVersion: "3.4.0",
  });
  const [installing, setInstalling] = useState(false);
  const [updateProgress, setUpdateProgress] = useState<{
    stage: string;
    progress: number;
    message: string;
    eta_seconds: number;
  }>({
    stage: "idle",
    progress: 0,
    message: "",
    eta_seconds: 0,
  });

  // Poll update status when installing
  useEffect(() => {
    if (!installing) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await call("get_update_status") as {
          in_progress: boolean;
          stage: string;
          progress: number;
          message: string;
          eta_seconds: number;
        };

        setUpdateProgress({
          stage: status.stage,
          progress: status.progress,
          message: status.message,
          eta_seconds: status.eta_seconds,
        });

        // Stop polling if complete or error
        if (status.stage === "complete" || status.stage === "error") {
          setInstalling(false);
          clearInterval(pollInterval);
          
          if (status.stage === "complete") {
            // Plugin will reload automatically
          }
        }
      } catch (err) {
        console.error("Failed to get update status:", err);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [installing]);

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

  const checkForUpdates = async () => {
    setUpdateInfo({ ...updateInfo, checking: true, error: undefined });
    
    try {
      const response = await call("check_for_updates") as {
        success: boolean;
        update_available?: boolean;
        current_version?: string;
        latest_version?: string;
        release_notes?: string;
        download_url?: string;
        error?: string;
      };
      
      if (response.success) {
        setUpdateInfo({
          checking: false,
          available: response.update_available || false,
          currentVersion: response.current_version || "3.4.0",
          latestVersion: response.latest_version,
          releaseNotes: response.release_notes,
          downloadUrl: response.download_url,
        });
      } else {
        setUpdateInfo({
          ...updateInfo,
          checking: false,
          error: response.error || "Failed to check for updates",
        });
      }
    } catch (err) {
      console.error("Failed to check for updates:", err);
      setUpdateInfo({
        ...updateInfo,
        checking: false,
        error: "Network error checking for updates",
      });
    }
  };

  const installUpdate = async () => {
    if (!updateInfo.downloadUrl) return;
    
    setInstalling(true);
    
    try {
      const response = await call("install_update", updateInfo.downloadUrl) as {
        success: boolean;
        message?: string;
        error?: string;
      };
      
      if (response.success) {
        // Update started in background - start polling
        setInstalling(true);
        setUpdateProgress({
          stage: "starting",
          progress: 0,
          message: "Starting update...",
          eta_seconds: 0,
        });
      } else {
        alert(`Failed to install update: ${response.error}`);
        setInstalling(false);
      }
    } catch (err) {
      console.error("Failed to install update:", err);
      alert("Failed to install update");
      setInstalling(false);
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
            
            {/* Update Management Section */}
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
                  Plugin Updates
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "12px",
                    lineHeight: "1.4",
                  }}
                >
                  Check for and install DeckTune updates from GitHub
                </div>

                {/* Current Version */}
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "8px",
                  }}
                >
                  Current Version: <strong style={{ color: "#fff" }}>{updateInfo.currentVersion}</strong>
                </div>

                {/* Check for Updates Button */}
                <FocusableButton
                  onClick={checkForUpdates}
                  disabled={updateInfo.checking || installing}
                  style={{ width: "100%", marginBottom: "8px" }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "8px",
                      padding: "10px 12px",
                      backgroundColor: updateInfo.checking ? "#3d4450" : "#1a9fff",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: "bold",
                      opacity: updateInfo.checking || installing ? 0.6 : 1,
                    }}
                  >
                    <FaSync
                      size={12}
                      aria-hidden="true"
                      style={{
                        animation: updateInfo.checking ? "spin 1s linear infinite" : "none",
                      }}
                    />
                    <span>{updateInfo.checking ? "Checking..." : "Check for Updates"}</span>
                  </div>
                </FocusableButton>

                {/* Update Available */}
                {updateInfo.available && updateInfo.latestVersion && (
                  <div
                    style={{
                      padding: "12px",
                      backgroundColor: "#1a4d2e",
                      borderRadius: "4px",
                      marginBottom: "8px",
                      border: "1px solid #4caf50",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "11px",
                        fontWeight: "bold",
                        color: "#4caf50",
                        marginBottom: "8px",
                      }}
                    >
                      ✓ Update Available: v{updateInfo.latestVersion}
                    </div>
                    
                    {updateInfo.releaseNotes && (
                      <div
                        style={{
                          fontSize: "9px",
                          color: "#8b929a",
                          marginBottom: "8px",
                          maxHeight: "60px",
                          overflowY: "auto",
                          lineHeight: "1.3",
                        }}
                      >
                        {updateInfo.releaseNotes.split('\n').slice(0, 3).join('\n')}
                      </div>
                    )}

                    <FocusableButton
                      onClick={installUpdate}
                      disabled={installing}
                      style={{ width: "100%" }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "8px",
                          padding: "8px",
                          backgroundColor: installing ? "#3d4450" : "#4caf50",
                          borderRadius: "4px",
                          fontSize: "10px",
                          fontWeight: "bold",
                          opacity: installing ? 0.6 : 1,
                        }}
                      >
                        <FaDownload size={10} aria-hidden="true" />
                        <span>{installing ? "Installing..." : "Install Update"}</span>
                      </div>
                    </FocusableButton>

                    {/* Installation Progress */}
                    {installing && (
                      <div style={{ marginTop: "12px" }}>
                        {/* Progress Bar */}
                        <div
                          style={{
                            width: "100%",
                            height: "8px",
                            backgroundColor: "#3d4450",
                            borderRadius: "4px",
                            overflow: "hidden",
                            marginBottom: "8px",
                          }}
                        >
                          <div
                            style={{
                              width: `${updateProgress.progress}%`,
                              height: "100%",
                              backgroundColor: "#4caf50",
                              transition: "width 0.3s ease",
                            }}
                          />
                        </div>

                        {/* Progress Info */}
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            fontSize: "9px",
                            color: "#8b929a",
                          }}
                        >
                          <span>{updateProgress.message}</span>
                          <span>{updateProgress.progress}%</span>
                        </div>

                        {/* ETA */}
                        {updateProgress.eta_seconds > 0 && (
                          <div
                            style={{
                              fontSize: "9px",
                              color: "#8b929a",
                              textAlign: "center",
                              marginTop: "4px",
                            }}
                          >
                            ETA: {Math.ceil(updateProgress.eta_seconds / 60)} min
                          </div>
                        )}

                        {/* Stage Indicator */}
                        <div
                          style={{
                            fontSize: "9px",
                            color: "#1a9fff",
                            textAlign: "center",
                            marginTop: "8px",
                            fontWeight: "bold",
                          }}
                        >
                          {updateProgress.stage === "downloading" && "⬇ Downloading..."}
                          {updateProgress.stage === "extracting" && "📦 Extracting..."}
                          {updateProgress.stage === "installing" && "⚙️ Installing..."}
                          {updateProgress.stage === "finalizing" && "✓ Finalizing..."}
                          {updateProgress.stage === "complete" && "✓ Complete! Reloading..."}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* No Update Available */}
                {!updateInfo.available && !updateInfo.checking && updateInfo.latestVersion && (
                  <div>
                    <div
                      style={{
                        fontSize: "10px",
                        color: "#4caf50",
                        textAlign: "center",
                        padding: "8px",
                        marginBottom: "8px",
                      }}
                    >
                      ✓ You're running the latest version
                    </div>

                    {/* Force Reinstall Button */}
                    <FocusableButton
                      onClick={async () => {
                        if (confirm("Reinstall current version? This will redownload and reinstall all plugin files.")) {
                          await installUpdate();
                        }
                      }}
                      disabled={installing}
                      style={{ width: "100%" }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "8px",
                          padding: "8px",
                          backgroundColor: installing ? "#3d4450" : "#3d4450",
                          borderRadius: "4px",
                          fontSize: "10px",
                          fontWeight: "bold",
                          opacity: installing ? 0.6 : 1,
                        }}
                      >
                        <FaSync size={10} aria-hidden="true" />
                        <span>{installing ? "Reinstalling..." : "Force Reinstall"}</span>
                      </div>
                    </FocusableButton>
                  </div>
                )}

                {/* Error */}
                {updateInfo.error && (
                  <div
                    style={{
                      fontSize: "9px",
                      color: "#f44336",
                      textAlign: "center",
                      padding: "8px",
                      backgroundColor: "rgba(244, 67, 54, 0.1)",
                      borderRadius: "4px",
                    }}
                  >
                    {updateInfo.error}
                  </div>
                )}
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
                      
                      // Call backend reset_config
                      await call("reset_config");
                      
                      // Reload page
                      window.location.reload();
                    } catch (err) {
                      console.error("Failed to reset settings:", err);
                      alert(`Failed to reset settings: ${err}`);
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
