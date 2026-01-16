import { definePlugin } from "@decky/api";
import { PanelSection, PanelSectionRow } from "@decky/ui";
import { FaMagic } from "react-icons/fa";

export default definePlugin(() => {
  return {
    name: "DeckTune",
    content: (
      <PanelSection title="DeckTune">
        <PanelSectionRow>
          <div>Hello from DeckTune!</div>
        </PanelSectionRow>
      </PanelSection>
    ),
    icon: <FaMagic />,
    onDismount() {
      console.log("DeckTune unloaded");
    },
  };
});
