import { definePlugin } from "@decky/api";
import { FaMagic } from "react-icons/fa";
import { FC } from "react";

import { DeckTuneApp } from "./components/DeckTuneApp";
import { DeckTuneProvider, useDeckTune } from "./context";
import { DeckTuneErrorBoundary } from "./components/ErrorBoundary";

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
          <DeckTuneTitleView />
        </DeckTuneProvider>
      </DeckTuneErrorBoundary>
    ),
    content: (
      <DeckTuneErrorBoundary>
        <DeckTuneProvider>
          <DeckTuneApp />
        </DeckTuneProvider>
      </DeckTuneErrorBoundary>
    ),
    icon: <FaMagic />,
    onDismount() {
      console.log("DeckTune unloaded");
    },
  };
});
