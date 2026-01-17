/**
 * ExpertMode component for DeckTune.
 * 
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 4.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 2.1, 2.2, 2.3, 2.5, 2.6
 * 
 * Provides detailed manual controls and diagnostics for power users:
 * - Manual tab: Per-core sliders, Apply/Test/Disable buttons, live metrics
 * - Presets tab: Preset list with edit/delete/export, import
 * - Tests tab: Test selection, run button, history
 * - Diagnostics tab: System info, logs, export
 * - Panic Disable button: Always visible emergency reset (Requirement 4.5)
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  SliderField,
  DropdownItem,
  ProgressBarWithInfo,
  Focusable,
  TextField,
  ToggleField,
} from "@decky/ui";
import {
  FaSlidersH,
  FaList,
  FaVial,
  FaInfoCircle,
  FaPlay,
  FaBan,
  FaCheck,
  FaTimes,
  FaDownload,
  FaUpload,
  FaTrash,
  FaEdit,
  FaSpinner,
  FaThermometerHalf,
  FaMicrochip,
  FaExclamationTriangle,
  FaExclamationCircle,
  FaRocket,
  FaFan,
} from "react-icons/fa";
import { useDeckTune, usePlatformInfo, useTests, useBinaries, useProfiles } from "../context";
import { Preset, TestHistoryEntry, TestResult, GameProfile } from "../api/types";
import { LoadGraph } from "./LoadGraph";
import { PresetsTabNew } from "./PresetsTabNew";
import { FanTab } from "./FanTab";

/**
 * Compact styles for QAM (310px width).
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 2.1
 */
const QAM_STYLES = {
  container: {
    maxWidth: "310px",
    padding: "8px",
  },
  tabNav: {
    display: "flex",
    gap: "4px",
    padding: "4px",
  },
  tabButton: {
    flex: 1,
    padding: "6px 4px",
    fontSize: "10px",
    minWidth: "0",
  },
  slider: {
    marginBottom: "8px",
  },
  metricsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "6px",
  },
  button: {
    padding: "8px 12px",
    fontSize: "12px",
  },
  buttonContainer: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "6px",
  },
  compactRow: {
    marginBottom: "6px",
  },
};

/**
 * Tab type for Expert Mode navigation.
 * Requirements: 7.1
 */
export type ExpertTab = "manual" | "presets" | "tests" | "fan" | "diagnostics";

interface TabConfig {
  id: ExpertTab;
  label: string;
  icon: FC;
}

const TABS: TabConfig[] = [
  { id: "manual", label: "Manual", icon: FaSlidersH },
  { id: "presets", label: "Presets", icon: FaList },
  { id: "tests", label: "Tests", icon: FaVial },
  { id: "fan", label: "Fan", icon: FaFan },
  { id: "diagnostics", label: "Diagnostics", icon: FaInfoCircle },
];

/**
 * Props for ExpertMode component.
 */
interface ExpertModeProps {
  initialTab?: ExpertTab;
}

/**
 * Panic Disable Button component - always visible emergency reset.
 * Requirements: 4.5
 * 
 * Features:
 * - Always visible red button
 * - Immediate reset to 0 on click
 */
const PanicDisableButton: FC = () => {
  const { api } = useDeckTune();
  const [isPanicking, setIsPanicking] = useState(false);

  const handlePanicDisable = async () => {
    setIsPanicking(true);
    try {
      await api.panicDisable();
    } finally {
      setIsPanicking(false);
    }
  };

  return (
    <PanelSectionRow>
      <ButtonItem
        layout="below"
        onClick={handlePanicDisable}
        disabled={isPanicking}
        style={{
          backgroundColor: "#b71c1c",
          borderRadius: "8px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            color: "#fff",
            fontWeight: "bold",
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" />
              <span>Disabling...</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle />
              <span>PANIC DISABLE</span>
            </>
          )}
        </div>
      </ButtonItem>
    </PanelSectionRow>
  );
};

/**
 * ExpertMode component - detailed controls for power users.
 * Requirements: 4.5, 7.1
 */
export const ExpertMode: FC<ExpertModeProps> = ({ initialTab = "manual" }) => {
  const [activeTab, setActiveTab] = useState<ExpertTab>(initialTab);

  return (
    <PanelSection title="Expert Mode">
      {/* Panic Disable Button - Always visible at top (Requirement 4.5) */}
      <PanicDisableButton />

      {/* Tab Navigation */}
      <PanelSectionRow>
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      </PanelSectionRow>

      {/* Tab Content */}
      {activeTab === "manual" && <ManualTab />}
      {activeTab === "presets" && <PresetsTabNew />}
      {activeTab === "tests" && <TestsTab />}
      {activeTab === "fan" && <FanTab />}
      {activeTab === "diagnostics" && <DiagnosticsTab />}
    </PanelSection>
  );
};

/**
 * Tab navigation component with compact display for QAM.
 * Ultra-compact tabs that fit in 310px width.
 */
interface TabNavigationProps {
  activeTab: ExpertTab;
  onTabChange: (tab: ExpertTab) => void;
}

const TabNavigation: FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <Focusable
      style={{
        display: "flex",
        marginBottom: "8px",
        backgroundColor: "#23262e",
        borderRadius: "4px",
        padding: "2px",
        gap: "2px",
      }}
      flow-children="horizontal"
    >
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <Focusable
            key={tab.id}
            className={`expert-tab ${isActive ? "active" : ""}`}
            focusClassName="gpfocus"
            onActivate={() => onTabChange(tab.id)}
            onClick={() => onTabChange(tab.id)}
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1px",
              padding: "4px 2px",
              borderRadius: "3px",
              cursor: "pointer",
              transition: "all 0.2s ease",
              backgroundColor: isActive ? "#1a9fff" : "transparent",
              color: isActive ? "#fff" : "#8b929a",
            }}
          >
            <Icon size={11} />
            <span style={{ fontSize: "8px", fontWeight: isActive ? "600" : "400" }}>
              {tab.label}
            </span>
          </Focusable>
        );
      })}
    </Focusable>
  );
};


/**
 * Manual tab component - vertical mode switcher.
 * Simplified interface with Simple/Expert mode selection.
 */
const ManualTab: FC = () => {
  const { state, api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const [mode, setMode] = useState<"simple" | "expert">("simple");
  const [showExpertWarning, setShowExpertWarning] = useState<boolean>(false);
  const [pendingExpertToggle, setPendingExpertToggle] = useState<boolean>(false);

  /**
   * Handle mode selection.
   */
  const handleModeSelect = (selectedMode: "simple" | "expert") => {
    if (selectedMode === "expert") {
      // Show warning before switching to expert
      setPendingExpertToggle(true);
      setShowExpertWarning(true);
    } else {
      setMode(selectedMode);
    }
  };

  /**
   * Confirm expert mode activation.
   */
  const handleExpertModeConfirm = () => {
    setMode("expert");
    setShowExpertWarning(false);
    setPendingExpertToggle(false);
  };

  /**
   * Cancel expert mode activation.
   */
  const handleExpertModeCancel = () => {
    setShowExpertWarning(false);
    setPendingExpertToggle(false);
  };

  return (
    <>
      {/* Expert Mode Warning Dialog with gamepad support */}
      {showExpertWarning && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.9)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
          }}
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
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <FaExclamationTriangle style={{ color: "#ff6b6b", fontSize: "20px" }} />
              <div style={{ fontSize: "14px", fontWeight: "bold", color: "#ff6b6b" }}>
                Expert Undervolter Mode
              </div>
            </div>

            <div style={{ fontSize: "11px", lineHeight: "1.5", marginBottom: "12px", color: "#e0e0e0" }}>
              <p style={{ marginBottom: "8px" }}>
                <strong>⚠️ WARNING:</strong> Expert mode removes safety limits.
              </p>
              <p style={{ marginBottom: "8px", color: "#ff9800" }}>
                <strong>Risks:</strong> System instability, crashes, data loss, hardware damage.
              </p>
              <p style={{ color: "#f44336", fontWeight: "bold", fontSize: "10px" }}>
                Use at your own risk!
              </p>
            </div>

            <Focusable style={{ display: "flex", gap: "8px" }} flow-children="horizontal">
              <Focusable
                style={{ flex: 1 }}
                focusClassName="gpfocus"
                onActivate={handleExpertModeConfirm}
                onClick={handleExpertModeConfirm}
              >
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  gap: "4px",
                  padding: "8px",
                  backgroundColor: "#b71c1c",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "10px",
                  fontWeight: "bold"
                }}>
                  <FaCheck size={10} />
                  <span>I Understand</span>
                </div>
              </Focusable>

              <Focusable
                style={{ flex: 1 }}
                focusClassName="gpfocus"
                onActivate={handleExpertModeCancel}
                onClick={handleExpertModeCancel}
              >
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  gap: "4px",
                  padding: "8px",
                  backgroundColor: "#3d4450",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "10px",
                  fontWeight: "bold"
                }}>
                  <FaTimes size={10} />
                  <span>Cancel</span>
                </div>
              </Focusable>
            </Focusable>
          </div>
        </div>
      )}

      {/* Platform info */}
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "10px", color: "#8b929a", marginBottom: "6px", padding: "2px 0" }}>
            {platformInfo.variant} ({platformInfo.model}) • Limit: {platformInfo.safe_limit}mV
          </div>
        </PanelSectionRow>
      )}

      {/* Mode Switcher - Vertical like WizardMode */}
      <PanelSectionRow>
        <div style={{ fontSize: "11px", marginBottom: "6px", fontWeight: "bold" }}>
          Select Tuning Mode:
        </div>
      </PanelSectionRow>

      {/* Simple Mode Button */}
      <PanelSectionRow>
        <Focusable
          focusClassName="gpfocus"
          onActivate={() => handleModeSelect("simple")}
          onClick={() => handleModeSelect("simple")}
        >
          <div style={{
            padding: "10px",
            backgroundColor: mode === "simple" ? "#1a9fff" : "#23262e",
            borderRadius: "6px",
            cursor: "pointer",
            border: mode === "simple" ? "2px solid #1a9fff" : "2px solid transparent",
            transition: "all 0.2s ease"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <FaSlidersH size={12} style={{ color: mode === "simple" ? "#fff" : "#1a9fff" }} />
              <span style={{ fontSize: "12px", fontWeight: "bold", color: mode === "simple" ? "#fff" : "#e0e0e0" }}>
                Simple Mode
              </span>
            </div>
            <div style={{ fontSize: "9px", color: mode === "simple" ? "#e0e0e0" : "#8b929a" }}>
              Safe limits • Easy controls • Recommended
            </div>
          </div>
        </Focusable>
      </PanelSectionRow>

      {/* Expert Mode Button */}
      <PanelSectionRow>
        <Focusable
          focusClassName="gpfocus"
          onActivate={() => handleModeSelect("expert")}
          onClick={() => handleModeSelect("expert")}
        >
          <div style={{
            padding: "10px",
            backgroundColor: mode === "expert" ? "#b71c1c" : "#23262e",
            borderRadius: "6px",
            cursor: "pointer",
            border: mode === "expert" ? "2px solid #ff6b6b" : "2px solid transparent",
            transition: "all 0.2s ease"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <FaExclamationTriangle size={12} style={{ color: mode === "expert" ? "#fff" : "#ff6b6b" }} />
              <span style={{ fontSize: "12px", fontWeight: "bold", color: mode === "expert" ? "#fff" : "#e0e0e0" }}>
                Expert Undervolter Mode
              </span>
            </div>
            <div style={{ fontSize: "9px", color: mode === "expert" ? "#ffb74d" : "#8b929a" }}>
              No limits • Advanced • Use at your own risk
            </div>
          </div>
        </Focusable>
      </PanelSectionRow>

      {/* Mode description */}
      <PanelSectionRow>
        <div style={{
          padding: "8px",
          backgroundColor: mode === "expert" ? "#5c1313" : "#1a3a5c",
          borderRadius: "6px",
          marginTop: "8px",
          border: mode === "expert" ? "1px solid #ff6b6b" : "1px solid #1a9fff"
        }}>
          <div style={{ fontSize: "10px", lineHeight: "1.4" }}>
            {mode === "simple" ? (
              <>
                <strong>Simple Mode:</strong> Safe undervolt range with platform-specific limits. 
                Perfect for most users.
              </>
            ) : (
              <>
                <strong style={{ color: "#ff6b6b" }}>Expert Mode:</strong> Extended range up to -100mV. 
                <span style={{ color: "#ff9800" }}> May cause instability!</span>
              </>
            )}
          </div>
        </div>
      </PanelSectionRow>

      {/* Current status */}
      <PanelSectionRow>
        <div style={{
          marginTop: "12px",
          padding: "6px",
          backgroundColor: "#23262e",
          borderRadius: "4px",
          fontSize: "10px",
          textAlign: "center",
          color: "#8b929a"
        }}>
          Active Mode: <span style={{ color: mode === "expert" ? "#ff6b6b" : "#1a9fff", fontWeight: "bold" }}>
            {mode === "simple" ? "Simple" : "Expert Undervolter"}
          </span>
        </div>
      </PanelSectionRow>

      <style>
        {`
          .gpfocus {
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.8) !important;
            transform: scale(1.02);
          }
        `}
      </style>
    </>
  );
};


/**
 * Presets tab component - now uses PresetsTabNew with profile management.
 * Requirements: 3.2, 5.1, 5.4, 7.3, 9.1, 9.2
 */
const PresetsTab: FC = PresetsTabNew;


/**
 * Available test options.
 */
const TEST_OPTIONS = [
  { value: "cpu_quick", label: "CPU Quick (30s)" },
  { value: "cpu_long", label: "CPU Long (5m)" },
  { value: "ram_quick", label: "RAM Quick (2m)" },
  { value: "ram_thorough", label: "RAM Thorough (15m)" },
  { value: "combo", label: "Combo Stress (5m)" },
];

/**
 * Tests tab component.
 * Requirements: 7.4
 * 
 * Features:
 * - Test selection dropdown
 * - Run test button with progress
 * - Last 10 test results history
 * - Warning banner if binaries missing
 */
const TestsTab: FC = () => {
  const { history, currentTest, isRunning, runTest } = useTests();
  const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();
  const [selectedTest, setSelectedTest] = useState<string>("cpu_quick");

  // Check binaries on mount
  useEffect(() => {
    checkBinaries();
  }, []);

  /**
   * Handle run test button click.
   */
  const handleRunTest = async () => {
    await runTest(selectedTest);
  };

  /**
   * Format duration for display.
   */
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  /**
   * Format timestamp for display.
   */
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  /**
   * Get test label from value.
   */
  const getTestLabel = (value: string): string => {
    return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
  };

  return (
    <>
      {/* Missing Binaries Warning */}
      {hasMissing && (
        <PanelSectionRow>
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "10px",
              padding: "12px",
              backgroundColor: "#5c4813",
              borderRadius: "8px",
              marginBottom: "12px",
              border: "1px solid #ff9800",
            }}
          >
            <FaExclamationCircle style={{ color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" }} />
            <div>
              <div style={{ fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" }}>
                Missing Components
              </div>
              <div style={{ fontSize: "12px", color: "#ffe0b2" }}>
                Required tools not found: <strong>{missingBinaries.join(", ")}</strong>
              </div>
              <div style={{ fontSize: "11px", color: "#ffcc80", marginTop: "4px" }}>
                Stress tests are unavailable until binaries are installed.
              </div>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Test selection */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Run Stress Test
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <DropdownItem
          label="Select Test"
          menuLabel="Select Test"
          rgOptions={TEST_OPTIONS.map((t, idx) => ({
            data: idx,
            label: t.label,
          }))}
          selectedOption={TEST_OPTIONS.findIndex(t => t.value === selectedTest)}
          onChange={(option: any) => {
            const test = TEST_OPTIONS[option.data];
            if (test) setSelectedTest(test.value);
          }}
          disabled={hasMissing}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleRunTest}
          disabled={isRunning || hasMissing}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", opacity: hasMissing ? 0.5 : 1 }}>
            {isRunning ? (
              <>
                <FaSpinner className="spin" />
                <span>Running {getTestLabel(currentTest || selectedTest)}...</span>
              </>
            ) : (
              <>
                <FaPlay />
                <span>Run Test</span>
              </>
            )}
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Running test indicator */}
      {isRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#1a3a5c",
              borderRadius: "8px",
              marginTop: "8px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <FaSpinner className="spin" style={{ color: "#1a9fff" }} />
              <span>Test in progress...</span>
            </div>
            <div style={{ fontSize: "12px", color: "#8b929a" }}>
              Running: {getTestLabel(currentTest || selectedTest)}
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Test history */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          Test History (Last 10)
        </div>
      </PanelSectionRow>

      {history.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px" }}>
            No tests run yet.
          </div>
        </PanelSectionRow>
      ) : (
        history.slice(0, 10).map((entry, index) => (
          <PanelSectionRow key={index}>
            <Focusable
              style={{
                padding: "10px",
                backgroundColor: "#23262e",
                borderRadius: "6px",
                marginBottom: "6px",
                borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
              }}
              focusClassName="gpfocus"
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  {entry.passed ? (
                    <FaCheck style={{ color: "#4caf50" }} />
                  ) : (
                    <FaTimes style={{ color: "#f44336" }} />
                  )}
                  <span style={{ fontWeight: "bold", fontSize: "13px" }}>
                    {getTestLabel(entry.test_name)}
                  </span>
                </div>
                <span style={{ fontSize: "11px", color: "#8b929a" }}>
                  {formatDuration(entry.duration)}
                </span>
              </div>
              <div style={{ fontSize: "11px", color: "#8b929a", marginTop: "4px" }}>
                {formatTimestamp(entry.timestamp)}
              </div>
              <div style={{ fontSize: "10px", color: "#8b929a", marginTop: "2px" }}>
                Cores: [{entry.cores_tested.join(", ")}]
              </div>
            </Focusable>
          </PanelSectionRow>
        ))
      )}

      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .gpfocus {
            border: 2px solid #1a9fff !important;
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
          }
        `}
      </style>
    </>
  );
};


/**
 * Diagnostics tab component.
 * Requirements: 7.5, 8.1, 8.2
 * 
 * Features:
 * - System info display (platform, SteamOS version)
 * - Log viewer
 * - Export Diagnostics button
 */
const DiagnosticsTab: FC = () => {
  const { api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<{ success: boolean; path?: string; error?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch system info on mount
  useEffect(() => {
    const fetchSystemInfo = async () => {
      setIsLoading(true);
      try {
        const info = await api.getSystemInfo();
        setSystemInfo(info);
      } catch (e) {
        console.error("Failed to fetch system info:", e);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSystemInfo();
  }, [api]);

  /**
   * Handle export diagnostics button click.
   */
  const handleExportDiagnostics = async () => {
    setIsExporting(true);
    setExportResult(null);
    try {
      const result = await api.exportDiagnostics();
      setExportResult(result);
    } catch (e) {
      setExportResult({ success: false, error: "Export failed" });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <>
      {/* System Info Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          System Information
        </div>
      </PanelSectionRow>

      {isLoading ? (
        <PanelSectionRow>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#8b929a" }}>
            <FaSpinner className="spin" />
            <span>Loading system info...</span>
          </div>
        </PanelSectionRow>
      ) : (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
            }}
          >
            {/* Platform info */}
            <InfoRow label="Platform" value={platformInfo ? `${platformInfo.variant} (${platformInfo.model})` : "Unknown"} />
            <InfoRow label="Safe Limit" value={platformInfo ? `${platformInfo.safe_limit} mV` : "Unknown"} />
            <InfoRow label="Detection" value={platformInfo?.detected ? "Successful" : "Failed"} />
            
            {/* System info from backend */}
            {systemInfo && (
              <>
                <div style={{ borderTop: "1px solid #3d4450", margin: "8px 0" }} />
                <InfoRow label="SteamOS Version" value={systemInfo.steamos_version || "Unknown"} />
                <InfoRow label="Kernel" value={systemInfo.kernel || "Unknown"} />
                <InfoRow label="Hostname" value={systemInfo.hostname || "Unknown"} />
                {systemInfo.uptime && (
                  <InfoRow label="Uptime" value={formatUptime(systemInfo.uptime)} />
                )}
              </>
            )}
          </div>
        </PanelSectionRow>
      )}

      {/* Current Config Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          Current Configuration
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            padding: "12px",
            backgroundColor: "#23262e",
            borderRadius: "8px",
          }}
        >
          {systemInfo?.config ? (
            <>
              <InfoRow label="Active Cores" value={`[${systemInfo.config.cores?.join(", ") || "0, 0, 0, 0"}]`} />
              <InfoRow label="LKG Cores" value={`[${systemInfo.config.lkg_cores?.join(", ") || "0, 0, 0, 0"}]`} />
              <InfoRow label="Status" value={systemInfo.config.status || "Unknown"} />
              <InfoRow label="Presets Count" value={String(systemInfo.config.presets_count || 0)} />
            </>
          ) : (
            <div style={{ color: "#8b929a" }}>Configuration not available</div>
          )}
        </div>
      </PanelSectionRow>

      {/* Log Viewer Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          Recent Logs
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            padding: "8px",
            backgroundColor: "#1a1d23",
            borderRadius: "8px",
            maxHeight: "150px",
            overflowY: "auto",
            fontFamily: "monospace",
            fontSize: "10px",
            color: "#8b929a",
          }}
        >
          {systemInfo?.logs ? (
            systemInfo.logs.split("\n").slice(-20).map((line: string, index: number) => (
              <div key={index} style={{ marginBottom: "2px" }}>
                {line}
              </div>
            ))
          ) : (
            <div>No logs available</div>
          )}
        </div>
      </PanelSectionRow>

      {/* Export Diagnostics Button */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleExportDiagnostics}
          disabled={isExporting}
          style={{ marginTop: "16px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
            {isExporting ? (
              <>
                <FaSpinner className="spin" />
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <FaDownload />
                <span>Export Diagnostics</span>
              </>
            )}
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Export result */}
      {exportResult && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: exportResult.success ? "#1b5e20" : "#b71c1c",
              borderRadius: "8px",
              marginTop: "8px",
            }}
          >
            {exportResult.success ? (
              <>
                <div style={{ fontWeight: "bold", marginBottom: "4px" }}>
                  <FaCheck style={{ marginRight: "8px" }} />
                  Export Successful
                </div>
                <div style={{ fontSize: "12px", wordBreak: "break-all" }}>
                  Saved to: {exportResult.path}
                </div>
              </>
            ) : (
              <>
                <div style={{ fontWeight: "bold" }}>
                  <FaTimes style={{ marginRight: "8px" }} />
                  Export Failed
                </div>
                <div style={{ fontSize: "12px" }}>
                  {exportResult.error}
                </div>
              </>
            )}
          </div>
        </PanelSectionRow>
      )}

      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </>
  );
};

/**
 * Helper component for displaying info rows.
 */
interface InfoRowProps {
  label: string;
  value: string;
}

const InfoRow: FC<InfoRowProps> = ({ label, value }) => (
  <div
    style={{
      display: "flex",
      justifyContent: "space-between",
      marginBottom: "6px",
      fontSize: "12px",
    }}
  >
    <span style={{ color: "#8b929a" }}>{label}:</span>
    <span style={{ color: "#fff" }}>{value}</span>
  </div>
);

/**
 * Format uptime seconds to human readable string.
 */
const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  
  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (mins > 0) parts.push(`${mins}m`);
  
  return parts.length > 0 ? parts.join(" ") : "< 1m";
};

// Global styles for ExpertMode
const expertModeStyles = `
  .expert-tab.gpfocus {
    border: 2px solid #1a9fff;
    box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
  }
  .expert-tab:hover {
    background-color: rgba(26, 159, 255, 0.2);
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleId = 'expert-mode-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = expertModeStyles;
    document.head.appendChild(style);
  }
}

export default ExpertMode;
