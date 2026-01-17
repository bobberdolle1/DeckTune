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
import { SetupWizard } from "./SetupWizard";
import { getApiInstance } from "../api";

/**
 * Main content component with mode switching and first-run detection.
 */
const DeckTuneContent: FC = () => {
  // Load saved mode from localStorage, default to wizard
  const [mode, setMode] = useState<"wizard" | "expert">(() => {
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
            Loading...
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <>
      <PanelSection>
        {/* Mode switcher - vertical layout for better gamepad navigation */}
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={() => setMode("wizard")}
            style={{ 
              minHeight: "32px", 
              padding: "4px 8px",
              backgroundColor: mode === "wizard" ? "#1a9fff" : "transparent",
              marginBottom: "4px"
            }}
          >
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "space-between",
              fontSize: "11px",
              color: mode === "wizard" ? "#fff" : "#8b929a"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <FaMagic size={10} />
                <span>Wizard Mode</span>
              </div>
              {mode === "wizard" && (
                <div style={{
                  fontSize: "9px",
                  color: state.status === "enabled" || state.status === "DYNAMIC RUNNING" 
                    ? "#4caf50" 
                    : state.status === "error" 
                      ? "#f44336" 
                      : "#8b929a",
                  padding: "2px 4px",
                  backgroundColor: "rgba(0,0,0,0.3)",
                  borderRadius: "2px",
                }}>
                  {state.status === "DYNAMIC RUNNING" ? "DYN" : state.status === "enabled" ? "ON" : state.status === "error" ? "ERR" : "OFF"}
                </div>
              )}
            </div>
          </ButtonItem>
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={() => setMode("expert")}
            style={{ 
              minHeight: "32px", 
              padding: "4px 8px",
              backgroundColor: mode === "expert" ? "#1a9fff" : "transparent"
            }}
          >
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "space-between",
              fontSize: "11px",
              color: mode === "expert" ? "#fff" : "#8b929a"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <FaCog size={10} />
                <span>Expert Mode</span>
              </div>
              {mode === "expert" && (
                <div style={{
                  fontSize: "9px",
                  color: state.status === "enabled" || state.status === "DYNAMIC RUNNING" 
                    ? "#4caf50" 
                    : state.status === "error" 
                      ? "#f44336" 
                      : "#8b929a",
                  padding: "2px 4px",
                  backgroundColor: "rgba(0,0,0,0.3)",
                  borderRadius: "2px",
                }}>
                  {state.status === "DYNAMIC RUNNING" ? "DYN" : state.status === "enabled" ? "ON" : state.status === "error" ? "ERR" : "OFF"}
                </div>
              )}
            </div>
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>

      {mode === "wizard" ? <WizardMode onRunSetup={handleRunSetupWizard} /> : <ExpertMode onRunSetup={handleRunSetupWizard} />}
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
