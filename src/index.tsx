import { definePlugin } from "@decky/api";
import { FaMagic } from "react-icons/fa";

import { DeckTuneApp } from "./components/DeckTuneApp";
import { DeckTuneProvider } from "./context";

export default definePlugin(() => {
  return {
    name: "DeckTune",
    content: (
      <DeckTuneProvider>
        <DeckTuneApp />
      </DeckTuneProvider>
    ),
    icon: <FaMagic />,
    onDismount() {
      console.log("DeckTune unloaded");
    },
  };
});
