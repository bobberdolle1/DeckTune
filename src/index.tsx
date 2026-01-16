/**
 * DeckTune - Main plugin entry point for Decky Loader.
 */

import { definePlugin } from "@decky/api";
import { FaMagic } from "react-icons/fa";

import { DeckTuneProvider } from "./context";
import { DeckTuneApp } from "./components/DeckTuneApp";

export default definePlugin(() => {
  console.log("DeckTune plugin loaded");

  return {
    name: "DeckTune",
    content: (
      <DeckTuneProvider>
        <DeckTuneApp />
      </DeckTuneProvider>
    ),
    icon: <FaMagic />,
    onDismount() {
      console.log("DeckTune plugin unloaded");
    },
  };
});
