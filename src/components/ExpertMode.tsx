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
      {activeTab === "presets" && <PresetsTab />}
      {activeTab === "tests" && <TestsTab />}
      {activeTab === "fan" && <FanTab />}
      {activeTab === "diagnostics" && <DiagnosticsTab />}
    </PanelSection>
  );
};

/**
 * Tab navigation component with compact display for QAM.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 2.3
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
        justifyContent: "space-around",
        marginBottom: "12px",
        backgroundColor: "#23262e",
        borderRadius: "6px",
        padding: "3px",
        gap: "2px",
      }}
    >
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "2px",
              padding: "6px 2px",
              backgroundColor: isActive ? "#1a9fff" : "transparent",
              border: "none",
              borderRadius: "4px",
              color: isActive ? "#fff" : "#8b929a",
              cursor: "pointer",
              transition: "all 0.2s ease",
              minWidth: "0",
            }}
          >
            <Icon style={{ fontSize: "14px" }} />
            {/* Hide label on very compact displays, show only icon */}
            <span style={{ fontSize: "9px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "100%" }}>
              {tab.label}
            </span>
          </button>
        );
      })}
    </Focusable>
  );
};


/**
 * Manual tab component.
 * Requirements: 5.4, 7.2, 13.3-13.6, 14.1, 14.2
 * 
 * Features:
 * - Expert Overclocker Mode toggle with warning (Requirements 13.3-13.6)
 * - Simple Mode toggle (Requirements 14.1, 14.2)
 * - Per-core sliders with current values
 * - Apply, Test, Disable buttons
 * - Live temperature and frequency display
 * - "Tune for this game" button (Requirement 5.4)
 */
const ManualTab: FC = () => {
  const { state, api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const [coreValues, setCoreValues] = useState<number[]>([...state.cores]);
  const [isApplying, setIsApplying] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isTuning, setIsTuning] = useState(false);
  const [simpleMode, setSimpleMode] = useState<boolean>(false);
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [systemMetrics, setSystemMetrics] = useState<{
    temps: number[];
    freqs: number[];
  } | null>(null);
  
  // Expert Mode state (Requirements 13.3-13.6)
  const [expertMode, setExpertMode] = useState<boolean>(false);
  const [expertModeActive, setExpertModeActive] = useState<boolean>(false);
  const [showExpertWarning, setShowExpertWarning] = useState<boolean>(false);
  const [isTogglingExpert, setIsTogglingExpert] = useState(false);

  // Fetch system metrics periodically
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const info = await api.getSystemInfo();
        if (info.temps && info.freqs) {
          setSystemMetrics({ temps: info.temps, freqs: info.freqs });
        }
      } catch (e) {
        // Ignore errors
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, [api]);

  // Load expert mode status on mount (Requirements 13.3-13.6)
  useEffect(() => {
    const loadExpertMode = async () => {
      try {
        const status = await api.getExpertModeStatus();
        setExpertMode(status.expert_mode);
        setExpertModeActive(status.active);
      } catch (e) {
        // Ignore errors, use default (false)
      }
    };
    loadExpertMode();

    // Listen for expert mode changes
    const handleExpertModeChange = (data: { enabled: boolean }) => {
      setExpertMode(data.enabled);
      setExpertModeActive(data.enabled);
    };
    api.on("expert_mode_changed", handleExpertModeChange);

    return () => {
      api.removeListener("expert_mode_changed", handleExpertModeChange);
    };
  }, [api]);

  // Initialize simpleValue from current cores (average) and load saved preference
  useEffect(() => {
    if (coreValues.length === 4) {
      const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
      setSimpleValue(avg);
    }
    
    // Load saved simple_mode preference
    const loadSimpleMode = async () => {
      try {
        const saved = await api.getSetting("simple_mode");
        if (saved !== null && saved !== undefined) {
          setSimpleMode(saved);
        }
      } catch (e) {
        // Ignore errors, use default (false)
      }
    };
    loadSimpleMode();
  }, []);

  const safeLimit = platformInfo?.safe_limit ?? -30;
  
  // Determine current limit based on expert mode (Requirements 13.2, 13.6)
  const currentMinLimit = expertModeActive ? -100 : safeLimit;

  /**
   * Handle Expert Mode toggle.
   * Requirements: 13.3, 13.4, 13.5
   */
  const handleExpertModeToggle = async (enabled: boolean) => {
    if (enabled) {
      // Show warning dialog (Requirement 13.3)
      setShowExpertWarning(true);
    } else {
      // Disable expert mode
      setIsTogglingExpert(true);
      try {
        const result = await api.disableExpertMode();
        if (result.success) {
          setExpertMode(false);
          setExpertModeActive(false);
        }
      } finally {
        setIsTogglingExpert(false);
      }
    }
  };

  /**
   * Confirm expert mode activation.
   * Requirements: 13.4
   */
  const handleExpertModeConfirm = async () => {
    setIsTogglingExpert(true);
    try {
      const result = await api.enableExpertMode(true);
      if (result.success) {
        setExpertMode(true);
        setExpertModeActive(true);
        setShowExpertWarning(false);
      } else {
        // Show error if confirmation failed
        alert(result.error || "Failed to enable expert mode");
      }
    } finally {
      setIsTogglingExpert(false);
    }
  };

  /**
   * Cancel expert mode activation.
   */
  const handleExpertModeCancel = () => {
    setShowExpertWarning(false);
  };

  /**
   * Handle Simple Mode toggle.
   * Requirements: 14.4, 14.5
   */
  const handleSimpleModeToggle = (enabled: boolean) => {
    if (enabled) {
      // Switching to Simple Mode: use average of current values (Requirement 14.4)
      const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
      setSimpleValue(avg);
    } else {
      // Switching to per-core mode: copy current simple value to all cores (Requirement 14.5)
      setCoreValues([simpleValue, simpleValue, simpleValue, simpleValue]);
    }
    setSimpleMode(enabled);
    // Save preference
    api.saveSetting("simple_mode", enabled);
  };

  /**
   * Handle simple slider value change.
   * Requirements: 14.3
   */
  const handleSimpleValueChange = (value: number) => {
    setSimpleValue(value);
    // Apply same value to all cores (Requirement 14.3)
    setCoreValues([value, value, value, value]);
  };

  /**
   * Handle slider value change for a specific core.
   */
  const handleCoreChange = (core: number, value: number) => {
    const newValues = [...coreValues];
    newValues[core] = value;
    setCoreValues(newValues);
  };

  /**
   * Apply current values.
   */
  const handleApply = async () => {
    setIsApplying(true);
    try {
      await api.applyUndervolt(coreValues);
    } finally {
      setIsApplying(false);
    }
  };

  /**
   * Run quick test with current values.
   */
  const handleTest = async () => {
    setIsTesting(true);
    try {
      await api.applyUndervolt(coreValues);
      await api.runTest("cpu_quick");
    } finally {
      setIsTesting(false);
    }
  };

  /**
   * Disable undervolt (reset to 0).
   */
  const handleDisable = async () => {
    await api.disableUndervolt();
    setCoreValues([0, 0, 0, 0]);
  };

  /**
   * Tune for current game - run autotune and save as preset.
   * Requirements: 5.4
   */
  const handleTuneForGame = async () => {
    if (!state.runningAppId || !state.runningAppName) {
      return;
    }
    
    setIsTuning(true);
    try {
      const result = await api.tuneForCurrentGame("quick");
      if (result.success && result.preset) {
        setCoreValues(result.preset.value);
      }
    } finally {
      setIsTuning(false);
    }
  };

  /**
   * Run benchmark - 10 second stress test.
   * Requirements: 7.1, 7.4
   */
  const handleRunBenchmark = async () => {
    try {
      await api.runBenchmark();
    } catch (e) {
      console.error("Benchmark failed:", e);
    }
  };

  /**
   * Get color for value indicator.
   */
  const getValueColor = (value: number): string => {
    const ratio = Math.abs(value) / Math.abs(safeLimit);
    if (ratio < 0.5) return "#4caf50";
    if (ratio < 0.8) return "#ff9800";
    return "#f44336";
  };

  // Check if a game is currently running
  const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;

  return (
    <>
      {/* Expert Mode Warning Dialog - Requirements: 13.3, 13.4 */}
      {showExpertWarning && (
        <PanelSectionRow>
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
          >
            <div
              style={{
                backgroundColor: "#1a1d23",
                borderRadius: "12px",
                padding: "24px",
                maxWidth: "500px",
                border: "2px solid #ff6b6b",
                boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <FaExclamationTriangle style={{ color: "#ff6b6b", fontSize: "32px" }} />
                <div style={{ fontSize: "20px", fontWeight: "bold", color: "#ff6b6b" }}>
                  Expert Overclocker Mode
                </div>
              </div>

              <div style={{ fontSize: "14px", lineHeight: "1.6", marginBottom: "20px", color: "#e0e0e0" }}>
                <p style={{ marginBottom: "12px" }}>
                  <strong>⚠️ WARNING:</strong> You are about to enable Expert Overclocker Mode, which removes all safety limits.
                </p>
                <p style={{ marginBottom: "12px" }}>
                  This mode allows undervolt values up to <strong>-100mV</strong>, far beyond the safe limits for your device.
                </p>
                <p style={{ marginBottom: "12px", color: "#ff9800" }}>
                  <strong>Risks include:</strong>
                </p>
                <ul style={{ marginLeft: "20px", marginBottom: "12px", color: "#ffb74d" }}>
                  <li>System instability and crashes</li>
                  <li>Data loss from unexpected shutdowns</li>
                  <li>Potential hardware damage</li>
                  <li>Voiding of warranty</li>
                </ul>
                <p style={{ color: "#f44336", fontWeight: "bold" }}>
                  Use at your own risk. The developers are not responsible for any damage.
                </p>
              </div>

              <Focusable style={{ display: "flex", gap: "12px" }}>
                <ButtonItem
                  layout="below"
                  onClick={handleExpertModeConfirm}
                  disabled={isTogglingExpert}
                  style={{
                    flex: 1,
                    backgroundColor: "#b71c1c",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    {isTogglingExpert ? (
                      <>
                        <FaSpinner className="spin" />
                        <span>Enabling...</span>
                      </>
                    ) : (
                      <>
                        <FaCheck />
                        <span>I Understand, Enable</span>
                      </>
                    )}
                  </div>
                </ButtonItem>

                <ButtonItem
                  layout="below"
                  onClick={handleExpertModeCancel}
                  disabled={isTogglingExpert}
                  style={{ flex: 1 }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    <FaTimes />
                    <span>Cancel</span>
                  </div>
                </ButtonItem>
              </Focusable>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Platform info */}
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "12px", color: "#8b929a", marginBottom: "8px" }}>
            {platformInfo.variant} ({platformInfo.model}) • Safe limit: {safeLimit}
          </div>
        </PanelSectionRow>
      )}

      {/* Real-time Load Graph - Requirements: 15.1 */}
      {state.dynamicStatus && state.dynamicStatus.running && (
        <PanelSectionRow>
          <LoadGraph
            load={state.dynamicStatus.load}
            isActive={state.dynamicStatus.running}
          />
        </PanelSectionRow>
      )}

      {/* Expert Mode Active Indicator - Requirements: 13.6 */}
      {expertModeActive && (
        <PanelSectionRow>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "12px",
              backgroundColor: "#5c1313",
              borderRadius: "8px",
              marginBottom: "12px",
              border: "2px solid #ff6b6b",
              animation: "pulse 2s ease-in-out infinite",
            }}
          >
            <FaExclamationTriangle style={{ color: "#ff6b6b", fontSize: "20px", flexShrink: 0 }} />
            <div>
              <div style={{ fontWeight: "bold", color: "#ff6b6b", marginBottom: "2px" }}>
                Expert Overclocker Mode Active
              </div>
              <div style={{ fontSize: "11px", color: "#ffb74d" }}>
                Extended range enabled: 0 to -100mV • Use with extreme caution
              </div>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Live metrics display */}
      {systemMetrics && (
        <PanelSectionRow>
          <Focusable
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "8px",
              marginBottom: "16px",
            }}
          >
            {[0, 1, 2, 3].map((core) => (
              <div
                key={core}
                style={{
                  padding: "8px",
                  backgroundColor: "#23262e",
                  borderRadius: "6px",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: "10px", color: "#8b929a" }}>Core {core}</div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", marginTop: "4px" }}>
                  <FaThermometerHalf style={{ color: "#ff9800", fontSize: "10px" }} />
                  <span style={{ fontSize: "12px" }}>
                    {systemMetrics.temps[core] ?? "--"}°C
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" }}>
                  <FaMicrochip style={{ color: "#1a9fff", fontSize: "10px" }} />
                  <span style={{ fontSize: "12px" }}>
                    {systemMetrics.freqs[core] ? `${(systemMetrics.freqs[core] / 1000).toFixed(1)}GHz` : "--"}
                  </span>
                </div>
              </div>
            ))}
          </Focusable>
        </PanelSectionRow>
      )}

      {/* Per-core sliders */}
      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <div style={{ fontSize: "14px", fontWeight: "bold" }}>
            Undervolt Values
          </div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            {/* Expert Mode Toggle - Requirements: 13.3-13.6 */}
            <ToggleField
              label="Expert Mode"
              description="Remove safety limits (-100mV)"
              checked={expertMode}
              onChange={handleExpertModeToggle}
              disabled={isTogglingExpert}
            />
            {/* Simple Mode Toggle - Requirements: 14.1, 14.2 */}
            <ToggleField
              label="Simple Mode"
              description="Control all cores with one slider"
              checked={simpleMode}
              onChange={handleSimpleModeToggle}
            />
          </div>
        </div>
      </PanelSectionRow>

      {simpleMode ? (
        /* Simple Mode: Single slider for all cores - Requirements: 14.2, 14.3 */
        <PanelSectionRow>
          <SliderField
            label="All Cores"
            value={simpleValue}
            min={currentMinLimit}
            max={0}
            step={1}
            showValue={true}
            onChange={handleSimpleValueChange}
            valueSuffix=""
            description={
              <span style={{ color: getValueColor(simpleValue) }}>
                {simpleValue === 0 ? "Disabled" : `${simpleValue} mV (applies to all 4 cores)`}
                {expertModeActive && simpleValue < safeLimit && (
                  <span style={{ color: "#ff6b6b", marginLeft: "8px" }}>⚠️ EXPERT</span>
                )}
              </span>
            }
          />
        </PanelSectionRow>
      ) : (
        /* Per-core mode: Individual sliders */
        [0, 1, 2, 3].map((core) => (
          <PanelSectionRow key={core}>
            <SliderField
              label={`Core ${core}`}
              value={coreValues[core]}
              min={currentMinLimit}
              max={0}
              step={1}
              showValue={true}
              onChange={(value: number) => handleCoreChange(core, value)}
              valueSuffix=""
              description={
                <span style={{ color: getValueColor(coreValues[core]) }}>
                  {coreValues[core] === 0 ? "Disabled" : `${coreValues[core]} mV`}
                  {expertModeActive && coreValues[core] < safeLimit && (
                    <span style={{ color: "#ff6b6b", marginLeft: "8px" }}>⚠️ EXPERT</span>
                  )}
                </span>
              }
            />
          </PanelSectionRow>
        ))
      )}

      {/* Action buttons */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            gap: "8px",
            marginTop: "16px",
          }}
        >
          <ButtonItem
            layout="below"
            onClick={handleApply}
            disabled={isApplying || isTesting || isTuning}
            style={{ flex: 1 }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              {isApplying ? <FaSpinner className="spin" /> : <FaCheck />}
              <span>Apply</span>
            </div>
          </ButtonItem>

          <ButtonItem
            layout="below"
            onClick={handleTest}
            disabled={isApplying || isTesting || isTuning}
            style={{ flex: 1 }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              {isTesting ? <FaSpinner className="spin" /> : <FaVial />}
              <span>Test</span>
            </div>
          </ButtonItem>

          <ButtonItem
            layout="below"
            onClick={handleDisable}
            disabled={isApplying || isTesting || isTuning}
            style={{ flex: 1 }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" }}>
              <FaBan />
              <span>Disable</span>
            </div>
          </ButtonItem>
        </Focusable>
      </PanelSectionRow>

      {/* Tune for this game button - Requirements: 5.4 */}
      {isGameRunning && (
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleTuneForGame}
            disabled={isApplying || isTesting || isTuning}
            style={{ marginTop: "8px" }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#1a9fff" }}>
              {isTuning ? (
                <>
                  <FaSpinner className="spin" />
                  <span>Tuning for {state.runningAppName}...</span>
                </>
              ) : (
                <>
                  <FaRocket />
                  <span>Tune for {state.runningAppName}</span>
                </>
              )}
            </div>
          </ButtonItem>
        </PanelSectionRow>
      )}

      {/* Run Benchmark button - Requirements: 7.1, 7.4 */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleRunBenchmark}
          disabled={isApplying || isTesting || isTuning || state.isBenchmarkRunning}
          style={{ marginTop: "8px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff9800" }}>
            {state.isBenchmarkRunning ? (
              <>
                <FaSpinner className="spin" />
                <span>Running Benchmark...</span>
              </>
            ) : (
              <>
                <FaVial />
                <span>Run Benchmark</span>
              </>
            )}
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Benchmark Progress - Requirements: 7.4 */}
      {state.isBenchmarkRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginTop: "8px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <FaSpinner className="spin" style={{ color: "#ff9800" }} />
              <span style={{ fontWeight: "bold" }}>Running benchmark...</span>
            </div>
            <ProgressBarWithInfo
              label="Benchmark Progress"
              description="Testing performance with stress-ng"
              nProgress={50}
              sOperationText="~10 seconds"
            />
            <div style={{ fontSize: "11px", color: "#8b929a", marginTop: "8px", textAlign: "center" }}>
              All tuning controls are disabled during benchmark
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Benchmark Result Display - Requirements: 7.3, 7.5 */}
      {state.lastBenchmarkResult && !state.isBenchmarkRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#1b5e20",
              borderRadius: "8px",
              marginTop: "8px",
              borderLeft: "4px solid #4caf50",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <span style={{ fontWeight: "bold", fontSize: "14px" }}>Latest Benchmark</span>
              <FaCheck style={{ color: "#4caf50" }} />
            </div>
            
            {/* Score */}
            <div style={{ marginBottom: "8px" }}>
              <div style={{ fontSize: "11px", color: "#a5d6a7" }}>Score</div>
              <div style={{ fontSize: "20px", fontWeight: "bold", color: "#4caf50" }}>
                {state.lastBenchmarkResult.score.toFixed(2)} bogo ops/s
              </div>
            </div>

            {/* Undervolt values used */}
            <div style={{ marginBottom: "8px" }}>
              <div style={{ fontSize: "11px", color: "#a5d6a7", marginBottom: "4px" }}>Undervolt Values Used</div>
              <div style={{ fontSize: "12px", color: "#c8e6c9" }}>
                [{state.lastBenchmarkResult.cores_used.join(", ")}] mV
              </div>
            </div>

            {/* Comparison with previous run */}
            {state.benchmarkHistory && state.benchmarkHistory.length > 1 && (() => {
              const current = state.benchmarkHistory[0];
              const previous = state.benchmarkHistory[1];
              const scoreDiff = current.score - previous.score;
              const percentChange = ((scoreDiff / previous.score) * 100);
              const improvement = scoreDiff > 0;
              
              return (
                <div style={{ marginTop: "8px", paddingTop: "8px", borderTop: "1px solid #2e7d32" }}>
                  <div style={{ fontSize: "11px", color: "#a5d6a7", marginBottom: "4px" }}>
                    Comparison with Previous Run
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {improvement ? (
                      <FaCheck style={{ color: "#4caf50" }} />
                    ) : (
                      <FaTimes style={{ color: "#ff6b6b" }} />
                    )}
                    <span style={{ fontSize: "13px", color: improvement ? "#4caf50" : "#ff6b6b", fontWeight: "bold" }}>
                      {improvement ? "+" : ""}{percentChange.toFixed(2)}%
                    </span>
                    <span style={{ fontSize: "11px", color: "#a5d6a7" }}>
                      ({improvement ? "+" : ""}{scoreDiff.toFixed(2)} bogo ops/s)
                    </span>
                  </div>
                </div>
              );
            })()}

            {/* Timestamp */}
            <div style={{ fontSize: "10px", color: "#81c784", marginTop: "8px" }}>
              {new Date(state.lastBenchmarkResult.timestamp).toLocaleString()}
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Benchmark History - Requirements: 7.5 */}
      {state.benchmarkHistory && state.benchmarkHistory.length > 0 && (
        <>
          <PanelSectionRow>
            <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
              Benchmark History (Last 10)
            </div>
          </PanelSectionRow>

          {state.benchmarkHistory.slice(0, 10).map((result, index) => (
            <PanelSectionRow key={index}>
              <div
                style={{
                  padding: "10px",
                  backgroundColor: "#23262e",
                  borderRadius: "6px",
                  marginBottom: "6px",
                  borderLeft: `3px solid #4caf50`,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ fontWeight: "bold", fontSize: "13px", color: "#4caf50" }}>
                      {result.score.toFixed(2)} bogo ops/s
                    </div>
                    <div style={{ fontSize: "10px", color: "#8b929a", marginTop: "2px" }}>
                      Cores: [{result.cores_used.join(", ")}] mV
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "11px", color: "#8b929a" }}>
                      {new Date(result.timestamp).toLocaleDateString()}
                    </div>
                    <div style={{ fontSize: "10px", color: "#8b929a" }}>
                      {new Date(result.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            </PanelSectionRow>
          ))}
        </>
      )}

      {/* Current status */}
      <PanelSectionRow>
        <div
          style={{
            marginTop: "12px",
            padding: "8px",
            backgroundColor: "#23262e",
            borderRadius: "6px",
            fontSize: "12px",
            textAlign: "center",
          }}
        >
          Status: <span style={{ color: state.status === "enabled" ? "#4caf50" : "#8b929a" }}>{state.status}</span>
        </div>
      </PanelSectionRow>

      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
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
          rgOptions={TEST_OPTIONS.map((t) => ({
            data: t.value,
            label: t.label,
          }))}
          selectedOption={selectedTest}
          onChange={(option: any) => setSelectedTest(option.data)}
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
            <div
              style={{
                padding: "10px",
                backgroundColor: "#23262e",
                borderRadius: "6px",
                marginBottom: "6px",
                borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
              }}
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
            </div>
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

export default ExpertMode;
