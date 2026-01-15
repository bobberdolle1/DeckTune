/**
 * ExpertMode component for DeckTune.
 * 
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 4.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2
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
  FaRocket,
} from "react-icons/fa";
import { useDeckTune, usePlatformInfo, useTests } from "../context";
import { Preset, TestHistoryEntry, TestResult } from "../api/types";

/**
 * Tab type for Expert Mode navigation.
 * Requirements: 7.1
 */
export type ExpertTab = "manual" | "presets" | "tests" | "diagnostics";

interface TabConfig {
  id: ExpertTab;
  label: string;
  icon: FC;
}

const TABS: TabConfig[] = [
  { id: "manual", label: "Manual", icon: FaSlidersH },
  { id: "presets", label: "Presets", icon: FaList },
  { id: "tests", label: "Tests", icon: FaVial },
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
      {activeTab === "diagnostics" && <DiagnosticsTab />}
    </PanelSection>
  );
};

/**
 * Tab navigation component.
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
        marginBottom: "16px",
        backgroundColor: "#23262e",
        borderRadius: "8px",
        padding: "4px",
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
              gap: "4px",
              padding: "8px 4px",
              backgroundColor: isActive ? "#1a9fff" : "transparent",
              border: "none",
              borderRadius: "6px",
              color: isActive ? "#fff" : "#8b929a",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            <Icon />
            <span style={{ fontSize: "10px" }}>{tab.label}</span>
          </button>
        );
      })}
    </Focusable>
  );
};


/**
 * Manual tab component.
 * Requirements: 5.4, 7.2
 * 
 * Features:
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
  const [systemMetrics, setSystemMetrics] = useState<{
    temps: number[];
    freqs: number[];
  } | null>(null);

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

  const safeLimit = platformInfo?.safe_limit ?? -30;

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
      {/* Platform info */}
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "12px", color: "#8b929a", marginBottom: "8px" }}>
            {platformInfo.variant} ({platformInfo.model}) • Safe limit: {safeLimit}
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
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Undervolt Values
        </div>
      </PanelSectionRow>

      {[0, 1, 2, 3].map((core) => (
        <PanelSectionRow key={core}>
          <SliderField
            label={`Core ${core}`}
            value={coreValues[core]}
            min={safeLimit}
            max={0}
            step={1}
            showValue={true}
            onChange={(value: number) => handleCoreChange(core, value)}
            valueSuffix=""
            description={
              <span style={{ color: getValueColor(coreValues[core]) }}>
                {coreValues[core] === 0 ? "Disabled" : `${coreValues[core]} mV`}
              </span>
            }
          />
        </PanelSectionRow>
      ))}

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
        `}
      </style>
    </>
  );
};


/**
 * Presets tab component.
 * Requirements: 7.3
 * 
 * Features:
 * - Preset list with edit/delete/export
 * - Import preset button
 */
const PresetsTab: FC = () => {
  const { state, api } = useDeckTune();
  const [editingPreset, setEditingPreset] = useState<Preset | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [importJson, setImportJson] = useState("");
  const [importError, setImportError] = useState<string | null>(null);

  /**
   * Handle preset deletion.
   */
  const handleDelete = async (appId: number) => {
    await api.deletePreset(appId);
  };

  /**
   * Handle preset export (single preset).
   */
  const handleExportSingle = async (preset: Preset) => {
    const json = JSON.stringify([preset], null, 2);
    // In a real implementation, this would trigger a file download
    console.log("Export preset:", json);
    // For now, copy to clipboard simulation
    alert(`Preset exported:\n${json}`);
  };

  /**
   * Handle export all presets.
   */
  const handleExportAll = async () => {
    const json = await api.exportPresets();
    console.log("Export all presets:", json);
    alert(`All presets exported:\n${json}`);
  };

  /**
   * Handle import presets.
   */
  const handleImport = async () => {
    setImportError(null);
    try {
      const result = await api.importPresets(importJson);
      if (result.success) {
        setIsImporting(false);
        setImportJson("");
        alert(`Successfully imported ${result.imported_count} preset(s)`);
      } else {
        setImportError(result.error || "Import failed");
      }
    } catch (e) {
      setImportError("Invalid JSON format");
    }
  };

  /**
   * Handle preset edit save.
   */
  const handleSaveEdit = async () => {
    if (editingPreset) {
      await api.updatePreset(editingPreset);
      setEditingPreset(null);
    }
  };

  /**
   * Format core values for display.
   */
  const formatCoreValues = (values: number[]): string => {
    return values.map((v, i) => `C${i}:${v}`).join(" ");
  };

  return (
    <>
      {/* Header with export all and import buttons */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "16px",
          }}
        >
          <ButtonItem layout="below" onClick={handleExportAll}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaDownload />
              <span>Export All</span>
            </div>
          </ButtonItem>

          <ButtonItem layout="below" onClick={() => setIsImporting(true)}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaUpload />
              <span>Import</span>
            </div>
          </ButtonItem>
        </Focusable>
      </PanelSectionRow>

      {/* Import dialog */}
      {isImporting && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Import Presets
            </div>
            <TextField
              label="JSON Data"
              value={importJson}
              onChange={(e: any) => setImportJson(e.target.value)}
              style={{ marginBottom: "8px" }}
            />
            {importError && (
              <div style={{ color: "#f44336", fontSize: "12px", marginBottom: "8px" }}>
                {importError}
              </div>
            )}
            <Focusable style={{ display: "flex", gap: "8px" }}>
              <ButtonItem layout="below" onClick={handleImport}>
                <span>Import</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => { setIsImporting(false); setImportJson(""); setImportError(null); }}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Edit dialog */}
      {editingPreset && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Edit Preset: {editingPreset.label}
            </div>
            <TextField
              label="Label"
              value={editingPreset.label}
              onChange={(e: any) => setEditingPreset({ ...editingPreset, label: e.target.value })}
              style={{ marginBottom: "8px" }}
            />
            <ToggleField
              label="Use Timeout"
              checked={editingPreset.use_timeout}
              onChange={(checked: boolean) => setEditingPreset({ ...editingPreset, use_timeout: checked })}
            />
            {editingPreset.use_timeout && (
              <SliderField
                label="Timeout (seconds)"
                value={editingPreset.timeout}
                min={0}
                max={60}
                step={5}
                showValue={true}
                onChange={(value: number) => setEditingPreset({ ...editingPreset, timeout: value })}
              />
            )}
            <Focusable style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <ButtonItem layout="below" onClick={handleSaveEdit}>
                <span>Save</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => setEditingPreset(null)}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Preset list */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Saved Presets ({state.presets.length})
        </div>
      </PanelSectionRow>

      {state.presets.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px" }}>
            No presets saved yet. Use "Tune for this game" or save from Manual tab.
          </div>
        </PanelSectionRow>
      ) : (
        state.presets.map((preset) => (
          <PanelSectionRow key={preset.app_id}>
            <div
              style={{
                padding: "12px",
                backgroundColor: "#23262e",
                borderRadius: "8px",
                marginBottom: "8px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: "bold", fontSize: "14px" }}>{preset.label}</div>
                  <div style={{ fontSize: "12px", color: "#8b929a" }}>
                    {formatCoreValues(preset.value)}
                  </div>
                  {preset.use_timeout && (
                    <div style={{ fontSize: "10px", color: "#ff9800" }}>
                      Timeout: {preset.timeout}s
                    </div>
                  )}
                  {preset.tested && (
                    <div style={{ fontSize: "10px", color: "#4caf50" }}>
                      ✓ Tested
                    </div>
                  )}
                </div>
                <Focusable style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => setEditingPreset(preset)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#1a9fff",
                      cursor: "pointer",
                    }}
                  >
                    <FaEdit />
                  </button>
                  <button
                    onClick={() => handleExportSingle(preset)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#8b929a",
                      cursor: "pointer",
                    }}
                  >
                    <FaDownload />
                  </button>
                  <button
                    onClick={() => handleDelete(preset.app_id)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#f44336",
                      cursor: "pointer",
                    }}
                  >
                    <FaTrash />
                  </button>
                </Focusable>
              </div>
            </div>
          </PanelSectionRow>
        ))
      )}
    </>
  );
};


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
 */
const TestsTab: FC = () => {
  const { history, currentTest, isRunning, runTest } = useTests();
  const [selectedTest, setSelectedTest] = useState<string>("cpu_quick");

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
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleRunTest}
          disabled={isRunning}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
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
