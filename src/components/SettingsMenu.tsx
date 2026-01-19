/**
 * SettingsMenu component for DeckTune.
 * 
 * Feature: ui-refactor-settings
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 * 
 * Provides centralized settings management interface:
 * - Expert Mode toggle with confirmation dialog
 * - Modal overlay with backdrop dismiss
 * - Gamepad navigation support
 * - Accessibility compliant (WCAG AA)
 */

import { FC, useState } from "react";
import { PanelSection, PanelSectionRow, Focusable } from "@decky/ui";
import { FaTimes, FaExclamationTriangle, FaCheck } from "react-icons/fa";
import { useSettings } from "../context/SettingsContext";
import { FocusableButton } from "./FocusableButton";

/**
 * Props for SettingsMenu component.
 */
export interface SettingsMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Props for Expert Mode Warning Dialog.
 */
interface ExpertWarningDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Expert Mode Warning Dialog component.
 * 
 * Requirements: 2.3, 2.4, 9.3
 * 
 * Displays warning about risks and requires explicit confirmation
 * before enabling Expert Mode.
 */
const ExpertWarningDialog: FC<ExpertWarningDialogProps> = ({
  isOpen,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        zIndex: 10000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="expert-warning-title"
      aria-describedby="expert-warning-description"
    >
      <div
        style={{
          backgroundColor: "#1a1d23",
          borderRadius: "8px",
          padding: "16px",
          maxWidth: "400px",
          border: "2px solid #ff6b6b",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "12px",
          }}
        >
          <FaExclamationTriangle
            style={{ color: "#ff6b6b", fontSize: "20px" }}
            aria-hidden="true"
          />
          <div
            id="expert-warning-title"
            style={{
              fontSize: "14px",
              fontWeight: "bold",
              color: "#ff6b6b",
            }}
          >
            Expert Undervolter Mode
          </div>
        </div>

        <div
          id="expert-warning-description"
          style={{
            fontSize: "11px",
            lineHeight: "1.5",
            marginBottom: "12px",
            color: "#e0e0e0",
          }}
        >
          <p style={{ marginBottom: "8px" }}>
            <strong>⚠️ WARNING:</strong> Expert mode removes safety limits.
          </p>
          <p style={{ marginBottom: "8px", color: "#ff9800" }}>
            <strong>Risks:</strong> System instability, crashes, data loss,
            hardware damage.
          </p>
          <p style={{ color: "#f44336", fontWeight: "bold", fontSize: "10px" }}>
            Use at your own risk!
          </p>
        </div>

        <Focusable
          style={{ display: "flex", gap: "8px" }}
          flow-children="horizontal"
        >
          <FocusableButton onClick={onConfirm} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "8px",
                backgroundColor: "#b71c1c",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "bold",
              }}
            >
              <FaCheck size={10} aria-hidden="true" />
              <span>I Understand</span>
            </div>
          </FocusableButton>

          <FocusableButton onClick={onCancel} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "8px",
                backgroundColor: "#3d4450",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "bold",
              }}
            >
              <FaTimes size={10} aria-hidden="true" />
              <span>Cancel</span>
            </div>
          </FocusableButton>
        </Focusable>
      </div>
    </div>
  );
};

/**
 * SettingsMenu component - centralized settings management.
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 * 
 * Features:
 * - Modal overlay with backdrop dismiss
 * - Expert Mode toggle with confirmation
 * - Auto-save on changes (Requirement 9.4)
 * - Gamepad navigation support
 * - WCAG AA compliant
 */
export const SettingsMenu: FC<SettingsMenuProps> = ({ isOpen, onClose }) => {
  const { settings, setExpertMode } = useSettings();
  const [showExpertWarning, setShowExpertWarning] = useState(false);

  if (!isOpen) return null;

  /**
   * Handle Expert Mode toggle.
   * 
   * Requirements: 2.3, 2.4
   * Shows confirmation dialog when enabling, directly disables when turning off.
   */
  const handleExpertModeToggle = () => {
    if (!settings.expertMode) {
      // Enabling - show warning dialog
      setShowExpertWarning(true);
    } else {
      // Disabling - no confirmation needed
      setExpertMode(false);
    }
  };

  /**
   * Handle Expert Mode confirmation.
   * 
   * Requirements: 2.4, 9.4
   */
  const handleExpertModeConfirm = async () => {
    await setExpertMode(true);
    setShowExpertWarning(false);
  };

  /**
   * Handle Expert Mode cancellation.
   * 
   * Requirements: 2.4
   */
  const handleExpertModeCancel = () => {
    setShowExpertWarning(false);
  };

  /**
   * Handle backdrop click to close menu.
   * 
   * Requirements: 2.1, 9.5
   */
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <>
      {/* Modal backdrop - Requirements: 2.1, 9.5 */}
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.85)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "20px",
        }}
        onClick={handleBackdropClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-menu-title"
      >
        {/* Settings panel */}
        <div
          style={{
            backgroundColor: "#1a1d23",
            borderRadius: "8px",
            padding: "16px",
            maxWidth: "400px",
            width: "100%",
            border: "1px solid #3d4450",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header with close button - Requirements: 2.1 */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "16px",
            }}
          >
            <h2
              id="settings-menu-title"
              style={{
                fontSize: "16px",
                fontWeight: "bold",
                color: "#fff",
                margin: 0,
              }}
            >
              Settings
            </h2>

            <FocusableButton onClick={onClose}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "32px",
                  height: "32px",
                  backgroundColor: "#3d4450",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
                aria-label="Close settings"
              >
                <FaTimes size={14} color="#fff" aria-hidden="true" />
              </div>
            </FocusableButton>
          </div>

          {/* Settings content */}
          <PanelSection>
            {/* Expert Mode section - Requirements: 2.2, 9.1, 9.2 */}
            <PanelSectionRow>
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    color: "#fff",
                    marginBottom: "8px",
                  }}
                >
                  Expert Mode
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#8b929a",
                    marginBottom: "8px",
                    lineHeight: "1.4",
                  }}
                >
                  Removes safety limits for advanced undervolting. Use with
                  caution.
                </div>

                <FocusableButton
                  onClick={handleExpertModeToggle}
                  style={{ width: "100%" }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 12px",
                      backgroundColor: settings.expertMode
                        ? "#b71c1c"
                        : "#3d4450",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: "bold",
                    }}
                    role="switch"
                    aria-checked={settings.expertMode}
                    aria-label="Expert Mode toggle"
                  >
                    <span>
                      {settings.expertMode ? "⚠ Expert Mode" : "Expert Mode"}
                    </span>
                    <span style={{ fontSize: "10px", color: "#8b929a" }}>
                      {settings.expertMode ? "ON" : "OFF"}
                    </span>
                  </div>
                </FocusableButton>
              </div>
            </PanelSectionRow>

            {/* Visual feedback for saved state - Requirements: 9.5 */}
            <PanelSectionRow>
              <div
                style={{
                  fontSize: "9px",
                  color: "#4caf50",
                  textAlign: "center",
                  padding: "4px",
                }}
              >
                ✓ Changes saved automatically
              </div>
            </PanelSectionRow>
          </PanelSection>
        </div>
      </div>

      {/* Expert Mode Warning Dialog - Requirements: 2.3, 2.4 */}
      <ExpertWarningDialog
        isOpen={showExpertWarning}
        onConfirm={handleExpertModeConfirm}
        onCancel={handleExpertModeCancel}
      />
    </>
  );
};

export default SettingsMenu;
