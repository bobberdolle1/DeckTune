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
 * 
 * v3.1.19: Complete focus system refactor with FocusableButton
 */

import { useState, useEffect, FC, useCallback } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  SliderField,
  Focusable,
} from "@decky/ui";
import { call } from "@decky/api";
import {
  FaSlidersH,
  FaList,
  FaVial,
  FaInfoCircle,
  FaBan,
  FaCheck,
  FaTimes,
  FaDownload,
  FaSpinner,
  FaExclamationTriangle,
  FaFan,
  FaChartLine,
} from "react-icons/fa";
import { useDeckTune, usePlatformInfo } from "../context";
import { useSettings } from "../context/SettingsContext";
import { PresetsTabNew } from "./PresetsTabNew";
import { TestsTabNew } from "./TestsTabNew";
import { FanTab } from "./FanTab";
import { FocusableButton } from "./FocusableButton";
import { DynamicManualMode } from "./DynamicManualMode";

/**
 * Tab type for Expert Mode navigation.
 * Requirements: 7.1, 10.1
 */
export type ExpertTab = "manual" | "presets" | "tests" | "fan" | "diagnostics" | "dynamic-manual";

interface TabConfig {
  id: ExpertTab;
  label: string;
  icon: FC;
}

const TABS: TabConfig[] = [
  { id: "manual", label: "Manual", icon: FaSlidersH },
  { id: "dynamic-manual", label: "Dynamic", icon: FaChartLine },
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
 * Panic Disable Button component - compact emergency reset.
 * Requirements: 4.5
 * 
 * Features:
 * - Compact red button with white focus outline
 * - Immediate reset to 0 on click
 * - Uses FocusableButton for custom focus
 */
const PanicDisableButton: FC = () => {
  const { api } = useDeckTune();
  const [isPanicking, setIsPanicking] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

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
      <Focusable
        onActivate={handlePanicDisable}
        onGamepadFocus={() => setIsFocused(true)}
        onGamepadBlur={() => setIsFocused(false)}
        style={{
          padding: 0,
          margin: 0,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            padding: "12px 16px",
            backgroundColor: "#b71c1c",
            borderRadius: "8px",
            color: "#fff",
            fontWeight: "bold",
            fontSize: "12px",
            border: isFocused && !isPanicking ? "3px solid #fff" : "3px solid transparent",
            boxShadow: isFocused && !isPanicking ? "0 0 12px rgba(255, 255, 255, 0.6)" : "none",
            transform: isFocused && !isPanicking ? "scale(1.05)" : "scale(1)",
            transition: "all 0.2s ease",
            cursor: isPanicking ? "not-allowed" : "pointer",
            opacity: isPanicking ? 0.5 : 1,
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" style={{ fontSize: "12px" }} />
              <span>Disabling...</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle style={{ fontSize: "12px" }} />
              <span>PANIC DISABLE</span>
            </>
          )}
        </div>
      </Focusable>
    </PanelSectionRow>
  );
};

/**
 * ExpertMode component - detailed controls for power users.
 * Requirements: 4.5, 7.1, 10.1, 10.2, 10.3, 10.4, 10.5
 */
export const ExpertMode: FC<ExpertModeProps> = ({ initialTab = "manual" }) => {
  const [activeTab, setActiveTab] = useState<ExpertTab>(initialTab);

  // NUCLEAR CACHE BUST - v3.1.19-20260118-2230
  useEffect(() => {
    const buildId = "v3.1.19-20260118-2230-FOCUSABLE-BUTTON";
    console.log(`[DeckTune CACHE BUST] ${buildId} - FocusableButton refactor complete`);
    (window as any).__DECKTUNE_BUILD_ID__ = buildId;
    (window as any).__DECKTUNE_EXPERT_MODE_VERSION__ = "FOCUSABLE_BUTTON_V1";
  }, []);

  /**
   * Handle tab change with persistence.
   * Requirements: 10.5
   */
  const handleTabChange = useCallback(async (tab: ExpertTab) => {
    setActiveTab(tab);
    
    // Persist selected tab to settings
    try {
      await call("save_setting", "expert_mode_selected_tab", tab);
      console.log("[ExpertMode] Selected tab persisted:", tab);
    } catch (error) {
      console.error("[ExpertMode] Failed to persist selected tab:", error);
    }
  }, []);

  // Load persisted tab on mount
  useEffect(() => {
    const loadPersistedTab = async () => {
      try {
        const response = await call("load_setting", "expert_mode_selected_tab") as { success: boolean; value?: string };
        if (response.success && response.value) {
          setActiveTab(response.value as ExpertTab);
          console.log("[ExpertMode] Loaded persisted tab:", response.value);
        }
      } catch (error) {
        console.error("[ExpertMode] Failed to load persisted tab:", error);
      }
    };
    
    loadPersistedTab();
  }, []);

  return (
    <PanelSection title="Expert Mode">
      {/* Panic Disable Button - Always visible at top (Requirement 4.5) */}
      <PanicDisableButton />

      {/* Tab Navigation - always first in focus order */}
      <PanelSectionRow>
        <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />
      </PanelSectionRow>

      {/* Tab Content - key forces remount on tab change to reset focus */}
      <div key={activeTab}>
        {activeTab === "manual" && <ManualTab />}
        {activeTab === "dynamic-manual" && <DynamicManualMode />}
        {activeTab === "presets" && <PresetsTabNew />}
        {activeTab === "tests" && <TestsTabNew />}
        {activeTab === "fan" && <FanTab />}
        {activeTab === "diagnostics" && <DiagnosticsTab />}
      </div>
    </PanelSection>
  );
};

/**
 * Tab navigation component with compact display for QAM.
 * Ultra-compact tabs that fit in 310px width.
 * 
 * Fixed: Uses FocusableButton for proper focus management.
 * Key prop on parent forces focus reset when tab changes.
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
          <FocusableButton
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            focusColor={isActive ? "#1a9fff" : "#666"}
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1px",
              padding: "4px 2px",
              borderRadius: "3px",
              backgroundColor: isActive ? "#1a9fff" : "transparent",
              color: isActive ? "#fff" : "#8b929a",
            }}
          >
            <Icon />
            <span style={{ fontSize: "8px", fontWeight: isActive ? "600" : "400" }}>
              {tab.label}
            </span>
          </FocusableButton>
        );
      })}
    </Focusable>
  );
};


/**
 * Manual tab component with simple/per-core modes.
 * 
 * Feature: ui-refactor-settings
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 */
const ManualTab: FC = () => {
  const { state, api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const { settings, setApplyOnStartup, setGameOnlyMode } = useSettings();
  const [coreValues, setCoreValues] = useState<number[]>([...state.cores]);
  const [simpleMode, setSimpleMode] = useState<boolean>(true);
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [isApplying, setIsApplying] = useState(false);

  const safeLimit = platformInfo?.safe_limit ?? -30;
  const currentMinLimit = settings.expertMode ? -100 : safeLimit;

  // Sync with state.cores
  useEffect(() => {
    setCoreValues([...state.cores]);
    const avg = Math.round(state.cores.reduce((sum, val) => sum + val, 0) / 4);
    setSimpleValue(avg);
  }, [state.cores]);

  /**
   * Handle simple mode toggle.
   */
  const handleSimpleModeToggle = () => {
    if (!simpleMode) {
      // Switching to simple: use average
      const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
      setSimpleValue(avg);
    } else {
      // Switching to per-core: copy simple value to all cores
      setCoreValues([simpleValue, simpleValue, simpleValue, simpleValue]);
    }
    setSimpleMode(!simpleMode);
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
            {platformInfo.variant} ({platformInfo.model}) • Limit: {platformInfo.safe_limit}mV
          </div>
        </PanelSectionRow>
      )}

      {/* Startup Behavior Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "12px", fontWeight: "bold", marginBottom: "8px", marginTop: "4px" }}>
          Startup Behavior
        </div>
      </PanelSectionRow>

      {/* Apply on Startup Toggle */}
      <PanelSectionRow>
        <Focusable style={{ marginBottom: "8px" }}>
          <FocusableButton
            onClick={() => setApplyOnStartup(!settings.applyOnStartup)}
            style={{ width: "100%" }}
          >
            <div style={{
              padding: "10px",
              backgroundColor: settings.applyOnStartup ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              display: "flex",
              flexDirection: "column",
              gap: "4px",
            }}>
              <div style={{
                fontSize: "11px",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}>
                {settings.applyOnStartup ? "✓" : "○"} Apply on Startup
              </div>
              <div style={{
                fontSize: "9px",
                color: settings.applyOnStartup ? "#e0e0e0" : "#8b929a",
                lineHeight: "1.3",
              }}>
                Automatically apply last profile when Steam Deck boots
              </div>
            </div>
          </FocusableButton>
        </Focusable>
      </PanelSectionRow>

      {/* Game Only Mode Toggle */}
      <PanelSectionRow>
        <Focusable style={{ marginBottom: "12px" }}>
          <FocusableButton
            onClick={() => setGameOnlyMode(!settings.gameOnlyMode)}
            style={{ width: "100%" }}
          >
            <div style={{
              padding: "10px",
              backgroundColor: settings.gameOnlyMode ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              display: "flex",
              flexDirection: "column",
              gap: "4px",
            }}>
              <div style={{
                fontSize: "11px",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}>
                {settings.gameOnlyMode ? "✓" : "○"} Game Only Mode
              </div>
              <div style={{
                fontSize: "9px",
                color: settings.gameOnlyMode ? "#e0e0e0" : "#8b929a",
                lineHeight: "1.3",
              }}>
                Apply undervolt only when games are running, reset in Steam menu
              </div>
            </div>
          </FocusableButton>
        </Focusable>
      </PanelSectionRow>

      {/* Mode toggle */}
      <PanelSectionRow>
        <Focusable style={{ marginBottom: "8px" }}>
          {/* Simple Mode Toggle */}
          <FocusableButton
            onClick={handleSimpleModeToggle}
            style={{ width: "100%" }}
          >
            <div style={{
              padding: "6px",
              backgroundColor: simpleMode ? "#1a9fff" : "#3d4450",
              borderRadius: "4px",
              fontSize: "9px",
              fontWeight: "bold",
              textAlign: "center",
            }}>
              {simpleMode ? "✓ Simple Mode" : "Per-Core Mode"}
            </div>
          </FocusableButton>
        </Focusable>
      </PanelSectionRow>

      {/* Expert Mode Active Warning */}
      {settings.expertMode && (
        <PanelSectionRow>
          <div style={{
            padding: "6px",
            backgroundColor: "#5c1313",
            borderRadius: "4px",
            border: "1px solid #ff6b6b",
            marginBottom: "8px"
          }}>
            <div style={{ fontSize: "9px", color: "#ff9800", display: "flex", alignItems: "center", gap: "4px" }}>
              <FaExclamationTriangle size={9} />
              <span>Expert mode active • Range: -100mV</span>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Sliders */}
      {simpleMode ? (
        /* Simple Mode: Single slider for all cores */
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

      {/* Action buttons */}
      <PanelSectionRow>
        <Focusable style={{ display: "flex", gap: "6px", marginTop: "8px" }} flow-children="horizontal">
          <FocusableButton
            onClick={handleApply}
            disabled={isApplying}
            style={{ flex: 1 }}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              padding: "8px",
              backgroundColor: "#1a9fff",
              borderRadius: "6px",
              fontSize: "10px",
              fontWeight: "bold",
            }}>
              {isApplying ? <FaSpinner className="spin" size={10} /> : <FaCheck size={10} />}
              <span>Apply</span>
            </div>
          </FocusableButton>

          <FocusableButton
            onClick={handleDisable}
            style={{ flex: 1 }}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              padding: "8px",
              backgroundColor: "#3d4450",
              borderRadius: "6px",
              fontSize: "10px",
              fontWeight: "bold"
            }}>
              <FaBan size={10} />
              <span>Disable</span>
            </div>
          </FocusableButton>

          <FocusableButton
            onClick={handleReset}
            style={{ flex: 1 }}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              padding: "8px",
              backgroundColor: "#5c4813",
              borderRadius: "6px",
              fontSize: "10px",
              fontWeight: "bold",
              color: "#ff9800"
            }}>
              <FaTimes size={10} />
              <span>Reset</span>
            </div>
          </FocusableButton>
        </Focusable>
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
        <div style={{ marginTop: "16px" }}>
          <ButtonItem
            layout="below"
            onClick={handleExportDiagnostics}
            disabled={isExporting}
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
        </div>
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
