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
  const [mode, setMode] = useState<"wizard" | "expert">("wizard");
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null);
  const { state, api } = useDeckTune();

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
        <PanelSectionRow>
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "8px",
              marginBottom: "8px",
            }}
          >
            <ButtonItem
              layout="below"
              onClick={() => setMode("wizard")}
            >
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                gap: "6px",
                color: mode === "wizard" ? "#1a9fff" : "#8b929a"
              }}>
                <FaMagic />
                <span>Wizard</span>
              </div>
            </ButtonItem>
            <ButtonItem
              layout="below"
              onClick={() => setMode("expert")}
            >
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                gap: "6px",
                color: mode === "expert" ? "#1a9fff" : "#8b929a"
              }}>
                <FaCog />
                <span>Expert</span>
              </div>
            </ButtonItem>
          </div>
        </PanelSectionRow>

        <PanelSectionRow>
          <div
            style={{
              textAlign: "center",
              fontSize: "12px",
              color: "#8b929a",
              padding: "4px 8px",
              backgroundColor: "#23262e",
              borderRadius: "4px",
            }}
          >
            Status: <span style={{ 
              color: state.status === "enabled" || state.status === "DYNAMIC RUNNING" 
                ? "#4caf50" 
                : state.status === "error" 
                  ? "#f44336" 
                  : "#8b929a" 
            }}>
              {state.status}
            </span>
          </div>
        </PanelSectionRow>

        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleRunSetupWizard}
          >
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center", 
              gap: "6px",
              color: "#8b929a",
              fontSize: "11px"
            }}>
              <FaWrench />
              <span>Run Setup Wizard</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>

      {mode === "wizard" ? <WizardMode /> : <ExpertMode />}
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
