/**
 * DeckTuneApp - Main application component.
 */

import {
  PanelSection,
  PanelSectionRow,
  ButtonItem,
} from "@decky/ui";
import { addEventListener, removeEventListener } from "@decky/api";
import { useState, useEffect, FC } from "react";
import { FaCog, FaMagic, FaWrench } from "react-icons/fa";

import { useDeckTune, initialState } from "../context";
import { WizardMode } from "./WizardMode";
import { ExpertMode } from "./ExpertMode";
import { SettingsTab } from "./SettingsTab";
import { SetupWizard } from "./SetupWizard";
import { getApiInstance } from "../api";

/**
 * Main content component with mode switching and first-run detection.
 */
const DeckTuneContent: FC = () => {
  // Load saved mode from localStorage, default to wizard
  const [mode, setMode] = useState<"wizard" | "expert" | "settings">(() => {
    try {
      const saved = localStorage.getItem('decktune_ui_mode');
      return (saved === "expert" || saved === "wizard") ? saved : "wizard";
    } catch {
      return "wizard";
    }
  });
  
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null);
  const { state, api } = useDeckTune();

  // Save mode to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('decktune_ui_mode', mode);
    } catch (e) {
      console.error("Failed to save UI mode:", e);
    }
  }, [mode]);

  useEffect(() => {
    const checkFirstRun = async () => {
      try {
        const firstRunComplete = await api.getSetting('first_run_complete');
        const isNew = firstRunComplete !== true;
        setIsFirstRun(isNew);
        if (isNew) {
          setShowSetupWizard(true);
        }
      } catch {
        setIsFirstRun(true);
        setShowSetupWizard(true);
      }
    };
    
    checkFirstRun();
  }, [api]);

  const handleSetupComplete = () => {
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  const handleSetupCancel = () => {
    setShowSetupWizard(false);
  };

  const handleSetupSkip = () => {
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  const handleRunSetupWizard = () => {
    setShowSetupWizard(true);
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
        `}
      </style>

      <PanelSection>
        {/* Mode switcher with animations */}
        <PanelSectionRow>
          <div className="fade-in">
            <ButtonItem
              layout="below"
              onClick={() => setMode("wizard")}
              className={`mode-button ${mode === "wizard" ? "active" : ""}`}
              style={{ 
                minHeight: "40px", 
                padding: "8px 12px",
                backgroundColor: mode === "wizard" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                marginBottom: "6px",
                borderRadius: "8px",
                border: mode === "wizard" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
              }}
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
            </ButtonItem>
          </div>
        </PanelSectionRow>
        
        <PanelSectionRow>
          <div className="fade-in" style={{ animationDelay: "0.1s" }}>
            <ButtonItem
              layout="below"
              onClick={() => setMode("expert")}
              className={`mode-button ${mode === "expert" ? "active" : ""}`}
              style={{ 
                minHeight: "40px", 
                padding: "8px 12px",
                backgroundColor: mode === "expert" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                borderRadius: "8px",
                border: mode === "expert" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
              }}
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
            </ButtonItem>
          </div>
        </PanelSectionRow>
        
        <PanelSectionRow>
          <div className="fade-in" style={{ animationDelay: "0.2s" }}>
            <ButtonItem
              layout="below"
              onClick={() => setMode("settings")}
              className={`mode-button ${mode === "settings" ? "active" : ""}`}
              style={{ 
                minHeight: "40px", 
                padding: "8px 12px",
                backgroundColor: mode === "settings" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                borderRadius: "8px",
                border: mode === "settings" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
              }}
            >
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center",
                fontSize: "12px",
                fontWeight: mode === "settings" ? "bold" : "normal",
                color: mode === "settings" ? "#fff" : "#8b929a"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <FaCog size={14} style={{ 
                    filter: mode === "settings" ? "drop-shadow(0 0 4px rgba(255,255,255,0.5))" : "none"
                  }} />
                  <span>Settings</span>
                </div>
              </div>
            </ButtonItem>
          </div>
        </PanelSectionRow>
      </PanelSection>

      <div className="fade-in" style={{ animationDelay: "0.3s" }}>
        {mode === "wizard" && <WizardMode onRunSetup={handleRunSetupWizard} />}
        {mode === "expert" && <ExpertMode onRunSetup={handleRunSetupWizard} />}
        {mode === "settings" && <SettingsTab />}
      </div>
    </>
  );
};

/**
 * Main app component with initialization.
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
      api.handleServerEvent(event);
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

  return <DeckTuneContent />;
};
