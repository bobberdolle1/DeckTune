/**
 * DeckTuneApp - Main application component.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.3, 8.4, 8.5
 */

import {
  PanelSection,
  PanelSectionRow,
  Focusable,
} from "@decky/ui";
import { addEventListener, removeEventListener } from "@decky/api";
import { useState, useEffect, FC } from "react";
import { FaCog, FaMagic } from "react-icons/fa";

import { useDeckTune, initialState } from "../context";
import { SettingsProvider } from "../context/SettingsContext";
import { WizardMode } from "./WizardMode";
import { ExpertMode } from "./ExpertMode";
import { SetupWizard } from "./SetupWizard";
import { FanControl } from "./FanControl";
import { HeaderBar } from "./HeaderBar";
import { SettingsMenu } from "./SettingsMenu";
import { getApiInstance } from "../api";

/**
 * Main content component with mode switching and first-run detection.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.3, 8.4, 8.5
 * 
 * CRITICAL FIX: Wizard setup state persistence
 */
const DeckTuneContent: FC = () => {
  // Load saved mode from localStorage, default to wizard
  // Requirements: 8.1, 8.2 - Fan Control accessed only via header, not in mode list
  const [mode, setMode] = useState<"wizard" | "expert" | "fan">(() => {
    try {
      const saved = localStorage.getItem('decktune_ui_mode');
      return (saved === "expert" || saved === "wizard" || saved === "fan") ? saved : "wizard";
    } catch {
      return "wizard";
    }
  });
  
  // Settings Menu visibility state - Requirements: 1.3
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  
  // CRITICAL FIX: Persist wizard setup state
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null);
  const { state, api } = useDeckTune();

  // Save mode to localStorage whenever it changes
  // Requirements: 8.5 - Preserve mode state when navigating to/from Fan Control
  useEffect(() => {
    try {
      localStorage.setItem('decktune_ui_mode', mode);
      // Save last non-fan mode for back navigation
      if (mode !== "fan") {
        localStorage.setItem('decktune_last_mode', mode);
      }
    } catch (e) {
      console.error("Failed to save UI mode:", e);
    }
  }, [mode]);

  useEffect(() => {
    const checkFirstRun = async () => {
      try {
        // CRITICAL FIX: Check localStorage first for wizard setup completion
        const wizardSetupComplete = localStorage.getItem('decktune_wizard_setup_complete');
        if (wizardSetupComplete === 'true') {
          setIsFirstRun(false);
          setShowSetupWizard(false);
          return;
        }
        
        const firstRunComplete = await api.getSetting('first_run_complete');
        const isNew = firstRunComplete !== true;
        setIsFirstRun(isNew);
        if (isNew) {
          setShowSetupWizard(true);
        }
      } catch {
        // Check localStorage fallback
        const wizardSetupComplete = localStorage.getItem('decktune_wizard_setup_complete');
        if (wizardSetupComplete === 'true') {
          setIsFirstRun(false);
          setShowSetupWizard(false);
        } else {
          setIsFirstRun(true);
          setShowSetupWizard(true);
        }
      }
    };
    
    checkFirstRun();
  }, [api]);

  const handleSetupComplete = () => {
    // CRITICAL FIX: Persist wizard setup completion
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  const handleSetupCancel = () => {
    setShowSetupWizard(false);
  };

  const handleSetupSkip = () => {
    // CRITICAL FIX: Persist skip state
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  /**
   * Handle Fan Control navigation from header.
   * Requirements: 1.2, 8.3, 8.5
   */
  const handleFanControlClick = () => {
    setMode("fan");
  };

  /**
   * Handle Settings navigation from header.
   * Requirements: 1.3
   */
  const handleSettingsClick = () => {
    setShowSettingsMenu(true);
  };

  /**
   * Handle back navigation from Fan Control.
   * Requirements: 8.4, 8.5 - Preserve previously selected mode
   */
  const handleFanControlBack = () => {
    // Return to the last non-fan mode (wizard or expert)
    const lastMode = localStorage.getItem('decktune_last_mode');
    if (lastMode === "expert" || lastMode === "wizard") {
      setMode(lastMode);
    } else {
      setMode("wizard");
    }
  };

  if (showSetupWizard) {
    return (
      <SetupWizard
        onComplete={handleSetupComplete}
        onCancel={handleSetupCancel}
        onSkip={handleSetupSkip}
      />
    );
  }

  if (isFirstRun === null) {
    return (
      <PanelSection title="DeckTune">
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "16px", color: "#8b929a" }}>
            <div className="loading-spinner" />
            Loading...
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  const getStatusColor = () => {
    if (state.status === "enabled" || state.status === "DYNAMIC RUNNING") return "#4caf50";
    if (state.status === "error") return "#f44336";
    return "#8b929a";
  };

  const getStatusText = () => {
    if (state.status === "DYNAMIC RUNNING") return "DYN";
    if (state.status === "enabled") return "ON";
    if (state.status === "error") return "ERR";
    return "OFF";
  };

  return (
    <>
      {/* Animated gradient background */}
      <style>
        {`
          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
          }
          
          @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(26, 159, 255, 0.3); }
            50% { box-shadow: 0 0 20px rgba(26, 159, 255, 0.6); }
          }
          
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          
          .mode-button {
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          }
          
          .mode-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
          }
          
          .mode-button:hover::before {
            left: 100%;
          }
          
          .mode-button.active {
            background: linear-gradient(135deg, #1a9fff 0%, #0d7fd8 100%);
            animation: glow 2s ease-in-out infinite;
          }
          
          .status-badge {
            animation: pulse 2s ease-in-out infinite;
          }
          
          .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(139, 146, 154, 0.3);
            border-top-color: #1a9fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 8px;
          }
          
          .fade-in {
            animation: fadeInUp 0.5s ease-out;
          }
          
          /* CRITICAL FIX: Gamepad focus highlight for mode buttons */
          .mode-button-focusable:focus-within,
          .mode-button-focusable.gpfocus {
            outline: 3px solid #1a9fff !important;
            outline-offset: 2px;
            box-shadow: 0 0 15px rgba(26, 159, 255, 0.6) !important;
          }
        `}
      </style>

      {/* Header Bar - Requirements: 1.1, 1.2, 1.3, 1.4 */}
      <HeaderBar
        onFanControlClick={handleFanControlClick}
        onSettingsClick={handleSettingsClick}
      />

      {/* Settings Menu - Requirements: 1.3, 2.1 */}
      <SettingsMenu
        isOpen={showSettingsMenu}
        onClose={() => setShowSettingsMenu(false)}
      />

      <PanelSection>
        {/* Mode switcher with animations - Requirements: 8.1, 8.2 */}
        {/* Large Fan Control button removed per Requirements 8.1, 8.2 */}
        <PanelSectionRow>
          <Focusable style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <Focusable
              className="fade-in mode-button-focusable"
              style={{ 
                minHeight: "40px", 
                padding: "8px 12px",
                backgroundColor: mode === "wizard" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                borderRadius: "8px",
                border: mode === "wizard" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
                position: "relative",
                overflow: "hidden",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                cursor: "pointer",
              }}
              onActivate={() => setMode("wizard")}
              onClick={() => setMode("wizard")}
            >
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between",
                fontSize: "12px",
                fontWeight: mode === "wizard" ? "bold" : "normal",
                color: mode === "wizard" ? "#fff" : "#8b929a"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <FaMagic size={14} style={{ 
                    filter: mode === "wizard" ? "drop-shadow(0 0 4px rgba(255,255,255,0.5))" : "none" 
                  }} />
                  <span>Wizard Mode</span>
                </div>
                {mode === "wizard" && (
                  <div className="status-badge" style={{
                    fontSize: "9px",
                    color: "#fff",
                    padding: "3px 6px",
                    backgroundColor: getStatusColor(),
                    borderRadius: "4px",
                    fontWeight: "bold",
                    boxShadow: `0 0 10px ${getStatusColor()}`,
                  }}>
                    {getStatusText()}
                  </div>
                )}
              </div>
            </Focusable>
            
            <Focusable
              className="fade-in mode-button-focusable"
              style={{ 
                minHeight: "40px", 
                padding: "8px 12px",
                backgroundColor: mode === "expert" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                borderRadius: "8px",
                border: mode === "expert" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
                position: "relative",
                overflow: "hidden",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                cursor: "pointer",
                animationDelay: "0.1s"
              }}
              onActivate={() => setMode("expert")}
              onClick={() => setMode("expert")}
            >
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between",
                fontSize: "12px",
                fontWeight: mode === "expert" ? "bold" : "normal",
                color: mode === "expert" ? "#fff" : "#8b929a"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <FaCog size={14} style={{ 
                    filter: mode === "expert" ? "drop-shadow(0 0 4px rgba(255,255,255,0.5))" : "none",
                    animation: mode === "expert" ? "spin 3s linear infinite" : "none"
                  }} />
                  <span>Expert Mode</span>
                </div>
                {mode === "expert" && (
                  <div className="status-badge" style={{
                    fontSize: "9px",
                    color: "#fff",
                    padding: "3px 6px",
                    backgroundColor: getStatusColor(),
                    borderRadius: "4px",
                    fontWeight: "bold",
                    boxShadow: `0 0 10px ${getStatusColor()}`,
                  }}>
                    {getStatusText()}
                  </div>
                )}
              </div>
            </Focusable>
          </Focusable>
        </PanelSectionRow>
      </PanelSection>

      <div className="fade-in" style={{ animationDelay: "0.3s" }}>
        {mode === "wizard" ? (
          <WizardMode />
        ) : mode === "expert" ? (
          <ExpertMode />
        ) : (
          <FanControl onBack={handleFanControlBack} />
        )}
      </div>
    </>
  );
};

/**
 * Main app component with initialization.
 * Wrapped with SettingsProvider for persistent settings management.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 10.1, 10.5
 */
export const DeckTuneApp: FC = () => {
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initPlugin = async () => {
      try {
        const api = getApiInstance(initialState);
        await api.init();
        setInitialized(true);
      } catch (e) {
        console.error("DeckTune init error:", e);
        setError(String(e));
      }
    };

    initPlugin();

    const handleServerEvent = (event: unknown) => {
      const api = getApiInstance(initialState);
      api.handleServerEvent(event as any);
    };

    addEventListener("server_event", handleServerEvent);

    return () => {
      removeEventListener("server_event", handleServerEvent);
      const api = getApiInstance(initialState);
      api.destroy();
    };
  }, []);

  if (error) {
    return (
      <PanelSection title="DeckTune">
        <PanelSectionRow>
          <div style={{ color: "#f44336", textAlign: "center", padding: "16px" }}>
            Failed to initialize: {error}
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  if (!initialized) {
    return (
      <PanelSection title="DeckTune">
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "16px", color: "#8b929a" }}>
            Loading...
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  // Wrap content with SettingsProvider - Requirements: 10.1, 10.5
  return (
    <SettingsProvider>
      <DeckTuneContent />
    </SettingsProvider>
  );
};
