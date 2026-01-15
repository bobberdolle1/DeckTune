/**
 * DeckTune - Main plugin entry point for Decky Loader.
 * 
 * This file registers the plugin with Decky Loader and provides
 * the main UI component that appears in the Quick Access Menu.
 */

import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  staticClasses,
} from "@decky/ui";
import { addEventListener, removeEventListener } from "@decky/api";
import { useState, useEffect, FC } from "react";
import { FaCog, FaMagic } from "react-icons/fa";

import { DeckTuneProvider, useDeckTune, initialState } from "./context";
import { WizardMode } from "./components/WizardMode";
import { ExpertMode } from "./components/ExpertMode";
import { getApiInstance } from "./api";

/**
 * Main content component with mode switching.
 */
const DeckTuneContent: FC = () => {
  const [mode, setMode] = useState<"wizard" | "expert">("wizard");
  const { state } = useDeckTune();

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
    // Plugin title shown in Decky menu
    title: <div className={staticClasses.Title}>DeckTune</div>,
    
    // Main plugin content
    content: <DeckTunePlugin />,
    
    // Plugin icon (shown in Quick Access Menu)
    icon: <FaMagic />,
    
    // Called when plugin is unloaded
    onDismount() {
      console.log("DeckTune plugin unloaded");
    },
  };
});
