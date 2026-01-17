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
  FaCog,
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
 * 
 * Tabs: ManualTab, PresetsTabNew, TestsTab, FanTab, DiagnosticsTab, SettingsTab
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
      <div style={{ display: activeTab === "manual" ? "block" : "none" }}>
        <ManualTab />
      </div>
      <div style={{ display: activeTab === "presets" ? "block" : "none" }}>
        <PresetsTabNew />
      </div>
      <div style={{ display: activeTab === "tests" ? "block" : "none" }}>
        <TestsTab />
      </div>
      <div style={{ display: activeTab === "fan" ? "block" : "none" }}>
        <FanTab />
      </div>
      <div style={{ display: activeTab === "diagnostics" ? "block" : "none" }}>
        <DiagnosticsTab />
      </div>
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
 * Inline Dynamic Settings component - expanded version with more settings.
 * Shows comprehensive dynamic mode configuration.
 */
const DynamicSettingsInline: FC = () => {
  const { state, api } = useDeckTune();
  const [strategy, setStrategy] = useState<string>("balanced");
  const [simpleMode, setSimpleMode] = useState<boolean>(false);
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [updateInterval, setUpdateInterval] = useState<number>(1000);
  const [loadThreshold, setLoadThreshold] = useState<number>(50);
  const [isSaving, setIsSaving] = useState(false);

  // Get expert mode from settings
  const expertMode = state.settings.expertMode || false;
  const minLimit = expertMode ? -100 : -35;

  // Load config on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await api.getDynamicConfig();
        if (config) {
          setStrategy(config.strategy || "balanced");
          setSimpleMode(config.simple_mode || false);
          setSimpleValue(config.simple_value || -25);
          setUpdateInterval(config.update_interval || 1000);
          setLoadThreshold(config.load_threshold || 50);
        }
      } catch (e) {
        console.error("Failed to load dynamic config:", e);
      }
    };
    loadConfig();
  }, [api]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const config = {
        strategy,
        simple_mode: simpleMode,
        simple_value: simpleValue,
        update_interval: updateInterval,
        load_threshold: loadThreshold,
        expert_mode: expertMode,
      };
      await api.saveDynamicConfig(config);
    } catch (e) {
      console.error("Failed to save dynamic config:", e);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <PanelSectionRow>
      <div style={{
        padding: "12px",
        background: "linear-gradient(135deg, #1a2a3a 0%, #1a1d23 100%)",
        borderRadius: "8px",
        border: "1px solid rgba(26, 159, 255, 0.3)",
        animation: "slideDown 0.3s ease-out"
      }}>
        {/* Header */}
        <div style={{
          fontSize: "11px",
          fontWeight: "bold",
          color: "#1a9fff",
          marginBottom: "12px",
          paddingBottom: "8px",
          borderBottom: "1px solid rgba(26, 159, 255, 0.2)"
        }}>
          ⚙️ Dynamic Mode Configuration
        </div>

        {/* Strategy Selection */}
        <div style={{ marginBottom: "12px" }}>
          <div style={{ fontSize: "10px", fontWeight: "bold", marginBottom: "6px", color: "#e0e0e0" }}>
            Strategy
          </div>
          <Focusable style={{ display: "flex", gap: "4px" }} flow-children="horizontal">
            {[
              { id: "conservative", label: "Conservative", desc: "Safe" },
              { id: "balanced", label: "Balanced", desc: "Default" },
              { id: "aggressive", label: "Aggressive", desc: "Max" }
            ].map((s) => (
              <Focusable
                key={s.id}
                style={{ flex: 1 }}
                onActivate={() => setStrategy(s.id)}
                onClick={() => setStrategy(s.id)}
              >
                <div style={{
                  padding: "8px 4px",
                  backgroundColor: strategy === s.id ? "#1a9fff" : "#3d4450",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "9px",
                  fontWeight: "bold",
                  textAlign: "center",
                  transition: "all 0.2s ease",
                  border: "none",
                  outline: "none"
                }}>
                  <div>{strategy === s.id ? "✓ " : ""}{s.label}</div>
                  <div style={{ fontSize: "7px", opacity: 0.7, marginTop: "2px" }}>{s.desc}</div>
                </div>
              </Focusable>
            ))}
          </Focusable>
        </div>

        {/* Simple Mode Toggle */}
        <div style={{ marginBottom: "12px" }}>
          <ToggleField
            label="Simple Mode"
            description="Use one value for all cores"
            checked={simpleMode}
            onChange={setSimpleMode}
            bottomSeparator="none"
          />
        </div>

        {/* Simple Value Slider (only if Simple Mode enabled) */}
        {simpleMode && (
          <div style={{ marginBottom: "12px" }}>
            <SliderField
              label="Undervolt Value"
              value={simpleValue}
              min={minLimit}
              max={0}
              step={1}
              showValue={true}
              onChange={(value: number) => setSimpleValue(value)}
              valueSuffix=" mV"
              bottomSeparator="none"
            />
          </div>
        )}

        {/* Update Interval Slider */}
        <div style={{ marginBottom: "12px" }}>
          <SliderField
            label="Update Interval"
            value={updateInterval}
            min={500}
            max={5000}
            step={100}
            showValue={true}
            onChange={(value: number) => setUpdateInterval(value)}
            valueSuffix=" ms"
            bottomSeparator="none"
          />
          <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px" }}>
            How often to check CPU load and adjust voltage
          </div>
        </div>

        {/* Load Threshold Slider */}
        <div style={{ marginBottom: "12px" }}>
          <SliderField
            label="Load Threshold"
            value={loadThreshold}
            min={10}
            max={90}
            step={5}
            showValue={true}
            onChange={(value: number) => setLoadThreshold(value)}
            valueSuffix="%"
            bottomSeparator="none"
          />
          <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px" }}>
            CPU load % to trigger voltage adjustment
          </div>
        </div>

        {/* Save Button */}
        <Focusable
          onActivate={handleSave}
          onClick={handleSave}
        >
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
            padding: "10px",
            background: isSaving 
              ? "linear-gradient(135deg, #2e7d32 0%, #388e3c 100%)"
              : "linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "11px",
            fontWeight: "bold",
            border: "none",
            outline: "none",
            transition: "all 0.2s ease"
          }}>
            {isSaving ? <FaSpinner className="spin" size={11} /> : <FaCheck size={11} />}
            <span>{isSaving ? "Saving..." : "Save Configuration"}</span>
          </div>
        </Focusable>

        {/* Info Box */}
        <div style={{
          marginTop: "10px",
          padding: "8px",
          backgroundColor: "rgba(26, 159, 255, 0.1)",
          borderRadius: "6px",
          fontSize: "8px",
          color: "#8b929a",
          lineHeight: "1.5",
          border: "1px solid rgba(26, 159, 255, 0.2)"
        }}>
          <div style={{ fontWeight: "bold", color: "#1a9fff", marginBottom: "4px" }}>ℹ️ How it works:</div>
          • Monitors CPU load every {updateInterval}ms<br/>
          • Adjusts voltage based on {strategy} strategy<br/>
          • Triggers when load {'>'} {loadThreshold}%<br/>
          • Restart Dynamic mode to apply changes
        </div>
      </div>
    </PanelSectionRow>
  );
};


/**
 * Manual tab component with simple/per-core/dynamic modes.
 */
const ManualTab: FC = () => {
  const { state, api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const [coreValues, setCoreValues] = useState<number[]>([...state.cores]);
  const [controlMode, setControlMode] = useState<"single" | "percore" | "dynamic">("single");
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [isApplying, setIsApplying] = useState(false);

  // Get expert mode from settings
  const expertMode = state.settings.expertMode || false;
  const safeLimit = platformInfo?.safe_limit ?? -30;
  const currentMinLimit = expertMode ? -100 : safeLimit;

  // Sync with state.cores
  useEffect(() => {
    setCoreValues([...state.cores]);
    const avg = Math.round(state.cores.reduce((sum, val) => sum + val, 0) / 4);
    setSimpleValue(avg);
  }, [state.cores]);

  /**
   * Handle control mode change.
   */
  const handleControlModeChange = (mode: "single" | "percore" | "dynamic") => {
    if (mode === "dynamic") {
      // Start gymdeck3
      api.enableGymdeck();
    } else {
      // Stop gymdeck3 if running
      if (state.gymdeckRunning) {
        api.disableGymdeck();
      }
    }
    setControlMode(mode);
  };

  /**
   * Handle simple slider change.
   */
  const handleSimpleValueChange = (value: number) => {
    setSimpleValue(value);
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
   * Disable undervolt (reset to 0 on backend, but keep UI values).
   */
  const handleDisable = async () => {
    await api.disableUndervolt();
    // Don't reset UI values - user can re-enable with same values
  };

  /**
   * Reset UI values to 0.
   */
  const handleReset = () => {
    setCoreValues([0, 0, 0, 0]);
    setSimpleValue(0);
  };

  return (
    <>
      {/* Platform info */}
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "10px", color: "#8b929a", marginBottom: "6px" }}>
            {platformInfo.variant} ({platformInfo.model}) • Limit: {expertMode ? "-100mV (Expert)" : `${platformInfo.safe_limit}mV`}
          </div>
        </PanelSectionRow>
      )}

      {/* Control Mode Selection */}
      <PanelSectionRow>
        <div style={{ fontSize: "11px", fontWeight: "bold", marginBottom: "6px" }}>Control Mode</div>
      </PanelSectionRow>
      <PanelSectionRow>
        <Focusable style={{ display: "flex", gap: "4px", marginBottom: "8px" }} flow-children="horizontal">
          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("single")}
            onClick={() => handleControlModeChange("single")}
          >
            <div style={{
              padding: "8px 6px",
              backgroundColor: controlMode === "single" ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: "none",
              outline: "none"
            }}>
              {controlMode === "single" ? "✓ Single" : "Single"}
            </div>
          </Focusable>

          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("percore")}
            onClick={() => handleControlModeChange("percore")}
          >
            <div style={{
              padding: "8px 6px",
              backgroundColor: controlMode === "percore" ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: "none",
              outline: "none"
            }}>
              {controlMode === "percore" ? "✓ Per-Core" : "Per-Core"}
            </div>
          </Focusable>

          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("dynamic")}
            onClick={() => handleControlModeChange("dynamic")}
          >
            <div style={{
              padding: "8px 6px",
              backgroundColor: controlMode === "dynamic" ? "#4caf50" : "#3d4450",
              color: controlMode === "dynamic" ? "#fff" : "#e0e0e0",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: "none",
              outline: "none"
            }}>
              {controlMode === "dynamic" ? "✓ Dynamic" : "Dynamic"}
            </div>
          </Focusable>
        </Focusable>
      </PanelSectionRow>

      {/* Dynamic Mode Status */}
      {controlMode === "dynamic" && state.gymdeckRunning && (
        <PanelSectionRow>
          <div style={{
            padding: "8px",
            backgroundColor: "#1b5e20",
            borderRadius: "4px",
            border: "1px solid #4caf50",
            marginBottom: "8px"
          }}>
            <div style={{ fontSize: "9px", color: "#81c784", fontWeight: "bold", marginBottom: "4px" }}>
              🚀 Dynamic Mode Active
            </div>
            <div style={{ fontSize: "8px", color: "#a5d6a7" }}>
              Real-time load-based adjustment via gymdeck3
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Dynamic Mode Settings (always visible when Dynamic is selected) */}
      {controlMode === "dynamic" && (
        <DynamicSettingsInline />
      )}

      {/* Sliders (only for Single and Per-Core modes) */}
      {controlMode !== "dynamic" && (
        <>
          {controlMode === "single" ? (
            /* Single Mode: One slider for all cores */
            <PanelSectionRow>
              <SliderField
                label="All Cores"
                value={simpleValue}
                min={currentMinLimit}
                max={0}
                step={1}
                showValue={true}
                onChange={handleSimpleValueChange}
                valueSuffix=" mV"
                bottomSeparator="none"
              />
            </PanelSectionRow>
          ) : (
            /* Per-core sliders */
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
                  valueSuffix=" mV"
                  bottomSeparator="none"
                />
              </PanelSectionRow>
            ))
          )}
        </>
      )}

      {/* Action buttons (only for Single and Per-Core modes) */}
      {controlMode !== "dynamic" && (
        <PanelSectionRow>
          <Focusable style={{ display: "flex", gap: "6px", marginTop: "8px" }} flow-children="horizontal">
            <Focusable
              style={{ flex: 1 }}
              onActivate={handleApply}
              onClick={handleApply}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "10px 8px",
                backgroundColor: "#1a9fff",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "11px",
                fontWeight: "bold",
                opacity: isApplying ? 0.5 : 1,
                border: "none",
                outline: "none"
              }}>
                {isApplying ? <FaSpinner className="spin" size={11} /> : <FaCheck size={11} />}
                <span>Apply</span>
              </div>
            </Focusable>

            <Focusable
              style={{ flex: 1 }}
              onActivate={handleDisable}
              onClick={handleDisable}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "10px 8px",
                backgroundColor: "#3d4450",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "11px",
                fontWeight: "bold",
                border: "none",
                outline: "none"
              }}>
                <FaBan size={11} />
                <span>Disable</span>
              </div>
            </Focusable>

            <Focusable
              style={{ flex: 1 }}
              onActivate={handleReset}
              onClick={handleReset}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "4px",
                padding: "10px 8px",
                backgroundColor: "#5c4813",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "11px",
                fontWeight: "bold",
                color: "#ff9800",
                border: "none",
                outline: "none"
              }}>
                <FaTimes size={11} />
                <span>Reset</span>
              </div>
            </Focusable>
          </Focusable>
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
  .expert-tab {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
  }
  
  .expert-tab::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #1a9fff, transparent);
    transition: all 0.3s ease;
    transform: translateX(-50%);
  }
  
  .expert-tab.active::after {
    width: 80%;
  }
  
  .expert-tab.gpfocus {
    border: 2px solid #1a9fff;
    box-shadow: 0 0 15px rgba(26, 159, 255, 0.6);
    transform: scale(1.05);
  }
  
  .expert-tab:hover {
    background-color: rgba(26, 159, 255, 0.2);
    transform: translateY(-2px);
  }
  
  .expert-tab.active {
    box-shadow: 0 4px 12px rgba(26, 159, 255, 0.4);
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes buttonPulse {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(26, 159, 255, 0.7);
    }
    50% {
      box-shadow: 0 0 0 10px rgba(26, 159, 255, 0);
    }
  }
  
  .animated-button {
    animation: slideIn 0.3s ease-out;
    transition: all 0.2s ease;
  }
  
  .animated-button:active {
    transform: scale(0.95);
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
