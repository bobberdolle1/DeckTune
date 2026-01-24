/**
 * HeaderBar component for DeckTune.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 * 
 * Provides compact navigation to Fan Control and Settings:
 * - Fan Control icon button (FaFan)
 * - Settings icon button (FaCog)
 * - Compact display with 20px icons
 * - Gamepad navigation support via FocusableButton
 */

import { FC } from "react";
import { FaFan, FaCog } from "react-icons/fa";
import { FocusableButton } from "./FocusableButton";

/**
 * Props for HeaderBar component.
 */
export interface HeaderBarProps {
  onFanControlClick: () => void;
  onSettingsClick: () => void;
  version?: string;
}

/**
 * HeaderBar component - compact navigation for Fan Control and Settings.
 * 
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 * 
 * Features:
 * - Positioned at top of DeckTuneApp
 * - Two icon buttons: Fan Control (FaFan) and Settings (FaCog)
 * - Icons sized at 20px for compact display (Requirement 1.5)
 * - Gamepad navigation support via FocusableButton
 * - Hover and focus states for accessibility
 */
export const HeaderBar: FC<HeaderBarProps> = ({
  onFanControlClick,
  onSettingsClick,
  version,
}) => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "8px",
        padding: "8px 12px",
        backgroundColor: "rgba(26, 29, 35, 0.5)",
        borderRadius: "8px",
        marginBottom: "12px",
      }}
      role="navigation"
      aria-label="Quick navigation"
    >
      {/* Version Display */}
      {version && (
        <div
          style={{
            fontSize: "10px",
            color: "#5a5d64",
            fontFamily: "monospace",
          }}
        >
          v{version}
        </div>
      )}
      
      <div style={{ display: "flex", gap: "8px" }}>
      {/* Fan Control Icon Button - Requirements: 1.2 */}
      <FocusableButton
        onClick={onFanControlClick}
        style={{ padding: 0 }}
        aria-label="Open Fan Control"
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "36px",
            height: "36px",
            backgroundColor: "rgba(61, 68, 80, 0.5)",
            borderRadius: "6px",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
        >
          <FaFan
            size={20}
            color="#8b929a"
            aria-hidden="true"
            style={{ transition: "color 0.2s ease" }}
          />
        </div>
      </FocusableButton>

      {/* Settings Icon Button - Requirements: 1.3 */}
      <FocusableButton
        onClick={onSettingsClick}
        style={{ padding: 0 }}
        aria-label="Open Settings"
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "36px",
            height: "36px",
            backgroundColor: "rgba(61, 68, 80, 0.5)",
            borderRadius: "6px",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
        >
          <FaCog
            size={20}
            color="#8b929a"
            aria-hidden="true"
            style={{ transition: "color 0.2s ease" }}
          />
        </div>
      </FocusableButton>
      </div>
    </div>
  );
};

export default HeaderBar;
