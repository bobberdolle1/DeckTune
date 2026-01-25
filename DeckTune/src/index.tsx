import { definePlugin } from "@decky/api";
import { FaMagic } from "react-icons/fa";
import { FC, useEffect } from "react";

import { DeckTuneApp } from "./components/DeckTuneApp";
import { DeckTuneProvider, useDeckTune, WizardProvider } from "./context";
import { DeckTuneErrorBoundary } from "./components/ErrorBoundary";

// NUCLEAR CACHE BUST - Force new module evaluation
const BUILD_TIMESTAMP = "20260118-2115";
const BUILD_VERSION = "v3.1.16-INLINE-FOCUS";
console.log(`[DeckTune CACHE BUST] Plugin index.tsx loaded - ${BUILD_VERSION} - ${BUILD_TIMESTAMP}`);
(window as any).__DECKTUNE_BUILD_TIMESTAMP__ = BUILD_TIMESTAMP;
(window as any).__DECKTUNE_BUILD_VERSION__ = BUILD_VERSION;

// Inject global CSS to disable ALL default focus styles
if (typeof document !== 'undefined') {
  const styleId = 'decktune-no-default-focus';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      /* Disable ALL default Decky UI focus styles */
      .decktune-plugin * {
        outline: none !important;
      }
      
      .decktune-plugin *:focus,
      .decktune-plugin *:focus-visible,
      .decktune-plugin .gpfocus {
        outline: none !important;
        box-shadow: none !important;
      }
      
      /* Disable focus ring on all Focusable components */
      .decktune-plugin [class*="Focusable"]:focus {
        outline: none !important;
      }
    `;
    document.head.appendChild(style);
    console.log('[DeckTune] Global focus styles disabled');
  }
}

/**
 * Title view component that shows status badge in plugin list.
 */
const DeckTuneTitleView: FC = () => {
  const { state } = useDeckTune();
  
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
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <span>DeckTune</span>
      <div style={{
        fontSize: "9px",
        fontWeight: "bold",
        color: "#fff",
        padding: "2px 6px",
        backgroundColor: getStatusColor(),
        borderRadius: "4px",
        boxShadow: `0 0 8px ${getStatusColor()}`,
        animation: state.status === "enabled" || state.status === "DYNAMIC RUNNING" ? "pulse 2s ease-in-out infinite" : "none"
      }}>
        {getStatusText()}
      </div>
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `}
      </style>
    </div>
  );
};

/**
 * DeckTune plugin entry point.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 */
export default definePlugin(() => {
  return {
    name: "DeckTune",
    titleView: (
      <DeckTuneErrorBoundary>
        <DeckTuneProvider>
          <WizardProvider>
            <DeckTuneTitleView />
          </WizardProvider>
        </DeckTuneProvider>
      </DeckTuneErrorBoundary>
    ),
    content: (
      <DeckTuneErrorBoundary>
        <DeckTuneProvider>
          <WizardProvider>
            <div className="decktune-plugin">
              <DeckTuneApp />
            </div>
          </WizardProvider>
        </DeckTuneProvider>
      </DeckTuneErrorBoundary>
    ),
    icon: <FaMagic />,
    onDismount() {
      console.log("DeckTune unloaded");
    },
  };
});
