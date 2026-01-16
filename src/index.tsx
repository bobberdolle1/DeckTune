/**
 * DeckTune - Main plugin entry point for Decky Loader.
 * 
 * This file registers the plugin with Decky Loader and provides
 * the main UI component that appears in the Quick Access Menu.
 * 
 * Requirements: 5.1, 5.6 - First-run detection and wizard trigger
 */

import {
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  staticClasses,
} from "@decky/ui";
import { definePlugin, addEventListener, removeEventListener } from "@decky/api";
import { useState, useEffect, FC } from "react";
import { FaCog, FaMagic, FaWrench } from "react-icons/fa";

import { DeckTuneProvider, useDeckTune, initialState } from "./context";
import { WizardMode } from "./components/WizardMode";
import { ExpertMode } from "./components/ExpertMode";
import { SetupWizard } from "./components/SetupWizard";
import { getApiInstance } from "./api";

/**
 * Main content component with mode switching and first-run detection.
 * 
 * Requirements:
 * - 5.1: Display welcome wizard on first run
 * - 5.6: Allow re-running wizard from settings
 */
const DeckTuneContent: FC = () => {
  const [mode, setMode] = useState<"wizard" | "expert">("wizard");
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null);
  const { state, api } = useDeckTune();

  // Check first-run status on mount
  // Requirements: 5.1
  useEffect(() => {
    const checkFirstRun = async () => {
      try {
        const firstRunComplete = await api.getSetting('first_run_complete');
        const isNew = firstRunComplete !== true;
        setIsFirstRun(isNew);
        if (isNew) {
          setShowSetupWizard(true);
        }
      } catch (e) {
        // If setting doesn't exist, treat as first run
        setIsFirstRun(true);
        setShowSetupWizard(true);
      }
    };
    
    checkFirstRun();
  }, [api]);

  /**
   * Handle setup wizard completion.
   * Requirements: 5.5
   */
  const handleSetupComplete = (goal: string) => {
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  /**
   * Handle setup wizard cancellation.
   * Requirements: 5.7
   */
  const handleSetupCancel = () => {
    setShowSetupWizard(false);
  };

  /**
   * Handle setup wizard skip.
   * Requirements: 5.7
   */
  const handleSetupSkip = () => {
    setShowSetupWizard(false);
    setIsFirstRun(false);
  };

  /**
   * Re-run setup wizard.
   * Requirements: 5.6
   */
  const handleRunSetupWizard = () => {
    setShowSetupWizard(true);
  };

  // Show setup wizard for first-run or when manually triggered
  // Requirements: 5.1, 5.6
  if (showSetupWizard) {
    return (
      <SetupWizard
        onComplete={handleSetupComplete}
        onCancel={handleSetupCancel}
        onSkip={handleSetupSkip}
      />
    );
  }

  // Loading state while checking first-run
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
      {/* Mode Toggle */}
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

        {/* Status indicator */}
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

        {/* Run Setup Wizard button - Requirements: 5.6 */}
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

      {/* Mode Content */}
      {mode === "wizard" ? <WizardMode /> : <ExpertMode />}
    </>
  );
};

/**
 * Main plugin component wrapped with context provider.
 */
const DeckTunePlugin: FC = () => {
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

    // Register server event listener
    const handleServerEvent = (event: any) => {
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

  return (
    <DeckTuneProvider>
      <DeckTuneContent />
    </DeckTuneProvider>
  );
};

/**
 * Plugin definition for Decky Loader.
 */
export default definePlugin(() => {
  console.log("DeckTune plugin loaded");

  return {
    // The name shown in various decky menus
    name: "DeckTune",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>DeckTune</div>,
    // The content of your plugin's menu
    content: <DeckTunePlugin />,
    // The icon displayed in the plugin list
    icon: <FaMagic />,
    // The function triggered when your plugin unloads
    onDismount() {
      console.log("DeckTune plugin unloaded");
    },
  };
});
