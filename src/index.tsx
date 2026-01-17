import { definePlugin } from "@decky/api";
import { FaMagic } from "react-icons/fa";

import { DeckTuneApp } from "./components/DeckTuneApp";
import { DeckTuneProvider } from "./context";
import { DeckTuneErrorBoundary } from "./components/ErrorBoundary";

/**
 * DeckTune plugin entry point.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 */
export default definePlugin(() => {
  return {
    name: "DeckTune",
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
