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
  FaSave,
  FaUndo,
} from "react-icons/fa";
import { useDeckTune, usePlatformInfo, useTests, useBinaries, useProfiles } from "../context";
import { Preset, TestHistoryEntry, TestResult, GameProfile } from "../api/types";
import { LoadGraph } from "./LoadGraph";
import { DynamicModeVisualization } from "./DynamicModeVisualization";
import { PresetsTabNew } from "./PresetsTabNew";
import { FanTab } from "./FanTab";
import { useTranslation, Translations } from "../i18n/translations";

/**
 * Install Binaries Button component for ExpertMode.
 * Allows one-click installation of stress-ng and memtester.
 */
interface InstallBinariesButtonExpertProps {
  onInstalled: () => void;
}

const InstallBinariesButtonExpert: FC<InstallBinariesButtonExpertProps> = ({ onInstalled }) => {
  const { api } = useDeckTune();
  const { t } = useTranslation();
  const [isInstalling, setIsInstalling] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message?: string; error?: string } | null>(null);

  const handleInstall = async () => {
    setIsInstalling(true);
    setResult(null);
    
    try {
      const installResult = await api.installBinaries();
      setResult(installResult);
      
      if (installResult.success) {
        // Wait a bit then refresh binary status
        setTimeout(() => {
          onInstalled();
        }, 1000);
      }
    } catch (e) {
      setResult({ success: false, error: String(e) });
    } finally {
      setIsInstalling(false);
    }
  };

  return (
    <div>
      <Focusable
        onActivate={handleInstall}
        onClick={handleInstall}
      >
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "6px",
          padding: "8px",
          background: isInstalling 
            ? "linear-gradient(135deg, #2e7d32 0%, #388e3c 100%)"
            : "linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "10px",
          fontWeight: "bold",
          marginTop: "6px",
          opacity: isInstalling ? 0.7 : 1
        }}>
          {isInstalling ? <FaSpinner className="spin" /> : <FaDownload />}
          <span>{isInstalling ? t.installing : t.install}</span>
        </div>
      </Focusable>

      {/* Result message */}
      {result && (
        <div style={{
          marginTop: "6px",
          padding: "6px",
          backgroundColor: result.success ? "#1b5e20" : "#b71c1c",
          borderRadius: "4px",
          fontSize: "9px",
          color: "#fff"
        }}>
          {result.success ? (
            <>
              <FaCheck style={{ marginRight: "4px" }} />
              {result.message || t.exportSuccessful}
            </>
          ) : (
            <>
              <FaTimes style={{ marginRight: "4px" }} />
              {result.error || t.exportFailed}
            </>
          )}
        </div>
      )}

      <style>{`
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

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
  labelKey: keyof Pick<Translations, 'manualTab' | 'presetsTab' | 'testsTab' | 'fanTab' | 'diagnosticsTab'>;
  icon: FC;
}

const TABS: TabConfig[] = [
  { id: "manual", labelKey: "manualTab", icon: FaSlidersH },
  { id: "presets", labelKey: "presetsTab", icon: FaList },
  { id: "tests", labelKey: "testsTab", icon: FaVial },
  { id: "fan", labelKey: "fanTab", icon: FaFan },
  { id: "diagnostics", labelKey: "diagnosticsTab", icon: FaInfoCircle },
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
  const { t } = useTranslation();
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
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            color: "#fff",
            fontWeight: "bold",
            backgroundColor: "#b71c1c",
            borderRadius: "8px",
            padding: "12px"
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" />
              <span>{t.disabling}</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle />
              <span>{t.panicDisable}</span>
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
      <div style={{ display: activeTab === "manual" ? "block" : "none", flex: 1, minHeight: 0 }}>
        <ManualTab />
      </div>
      <div style={{ display: activeTab === "presets" ? "block" : "none", flex: 1, minHeight: 0 }}>
        <PresetsTabNew />
      </div>
      <div style={{ display: activeTab === "tests" ? "block" : "none", flex: 1, minHeight: 0 }}>
        <TestsTab />
      </div>
      <div style={{ display: activeTab === "fan" ? "block" : "none", flex: 1, minHeight: 0 }}>
        <FanTab />
      </div>
      <div style={{ display: activeTab === "diagnostics" ? "block" : "none", flex: 1, minHeight: 0 }}>
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
  const { t } = useTranslation();
  
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
            <Icon />
            <span style={{ fontSize: "8px", fontWeight: isActive ? "600" : "400" }}>
              {t[tab.labelKey]}
            </span>
          </Focusable>
        );
      })}
    </Focusable>
  );
};


/**
 * Inline Dynamic Settings component - improved with graph and better controls.
 * Shows comprehensive dynamic mode configuration with real-time monitoring.
 */
const DynamicSettingsInline: FC = () => {
  const { state, api } = useDeckTune();
  const { t } = useTranslation();
  const [strategy, setStrategy] = useState<string>("balanced");
  const [simpleMode, setSimpleMode] = useState<boolean>(false);
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [sampleInterval, setSampleInterval] = useState<number>(100);
  const [hysteresis, setHysteresis] = useState<number>(5);
  const [isSaving, setIsSaving] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Get expert mode from settings
  const expertMode = state.settings.expertMode || false;
  const minLimit = expertMode ? -100 : -35;
  
  // Check if dynamic mode is running
  const isDynamicRunning = state.status === "DYNAMIC RUNNING" || state.gymdeckRunning;

  // Load config on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await api.getDynamicConfig();
        if (config) {
          setStrategy(config.strategy || "balanced");
          setSimpleMode(config.simple_mode || false);
          setSimpleValue(config.simple_value || -25);
          setSampleInterval(config.sample_interval_ms || 100);
          setHysteresis(config.hysteresis_percent || 5);
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
        sample_interval_ms: sampleInterval,
        hysteresis_percent: hysteresis,
        expert_mode: expertMode,
      };
      await api.saveDynamicConfig(config);
    } catch (e) {
      console.error("Failed to save dynamic config:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleStart = async () => {
    setIsStarting(true);
    try {
      await api.enableGymdeck();
    } finally {
      setIsStarting(false);
    }
  };

  const handleStop = async () => {
    setIsStopping(true);
    try {
      await api.disableGymdeck();
    } finally {
      setIsStopping(false);
    }
  };

  return (
    <div style={{ marginBottom: "12px" }}>
      {/* Dynamic Mode Status Card */}
      <PanelSectionRow>
        <div style={{
          padding: "12px",
          background: isDynamicRunning 
            ? "linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%)"
            : "linear-gradient(135deg, #1a2a3a 0%, #1a1d23 100%)",
          borderRadius: "8px",
          border: isDynamicRunning 
            ? "1px solid rgba(76, 175, 80, 0.5)"
            : "1px solid rgba(26, 159, 255, 0.3)",
          marginBottom: "8px"
        }}>
          {/* Status Header */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "8px"
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}>
              <FaRocket style={{ 
                color: isDynamicRunning ? "#81c784" : "#1a9fff",
                fontSize: "14px"
              }} />
              <span style={{
                fontSize: "12px",
                fontWeight: "bold",
                color: isDynamicRunning ? "#a5d6a7" : "#1a9fff"
              }}>
                {t.dynamicModeTitle}
              </span>
            </div>
            <div style={{
              padding: "4px 8px",
              backgroundColor: isDynamicRunning ? "#4caf50" : "#3d4450",
              borderRadius: "4px",
              fontSize: "9px",
              fontWeight: "bold",
              color: "#fff"
            }}>
              {isDynamicRunning ? `🟢 ${t.active}` : `⚫ ${t.off}`}
            </div>
          </div>

          {/* Description */}
          <div style={{
            fontSize: "9px",
            color: isDynamicRunning ? "#c8e6c9" : "#8b929a",
            marginBottom: "12px",
            lineHeight: "1.4"
          }}>
            {isDynamicRunning 
              ? t.dynamicModeDescriptionActive
              : t.dynamicModeDescription
            }
          </div>

          {/* Control Buttons */}
          <Focusable style={{ display: "flex", gap: "6px" }} flow-children="horizontal">
            {!isDynamicRunning ? (
              <Focusable
                style={{ flex: 1 }}
                onActivate={handleStart}
                onClick={handleStart}
              >
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  padding: "10px",
                  background: "linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "11px",
                  fontWeight: "bold",
                  opacity: isStarting ? 0.6 : 1
                }}>
                  {isStarting ? <FaSpinner className="spin" size={11} /> : <FaPlay size={11} />}
                  <span>{t.start}</span>
                </div>
              </Focusable>
            ) : (
              <Focusable
                style={{ flex: 1 }}
                onActivate={handleStop}
                onClick={handleStop}
              >
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  padding: "10px",
                  backgroundColor: "#f44336",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "11px",
                  fontWeight: "bold",
                  opacity: isStopping ? 0.6 : 1
                }}>
                  {isStopping ? <FaSpinner className="spin" size={11} /> : <FaBan size={11} />}
                  <span>{t.stop}</span>
                </div>
              </Focusable>
            )}

            <Focusable
              style={{ flex: 1 }}
              onActivate={() => setShowSettings(!showSettings)}
              onClick={() => setShowSettings(!showSettings)}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "6px",
                padding: "10px",
                backgroundColor: showSettings ? "#1a9fff" : "#3d4450",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "11px",
                fontWeight: "bold"
              }}>
                <FaCog size={11} />
                <span>{t.settings}</span>
              </div>
            </Focusable>
          </Focusable>
        </div>
      </PanelSectionRow>

      {/* Real-time Visualization (only when running) */}
      {isDynamicRunning && (
        <PanelSectionRow>
          <DynamicModeVisualization
            strategy={strategy}
            load={[0, 0, 0, 0]} // TODO: Get real load data from backend
            values={state.cores}
            isActive={true}
            simpleMode={simpleMode}
            simpleValue={simpleValue}
          />
        </PanelSectionRow>
      )}

      {/* Configuration Panel (collapsible) */}
      {showSettings && (
        <PanelSectionRow>
          <div style={{
            padding: "12px",
            background: "linear-gradient(135deg, #1a2a3a 0%, #1a1d23 100%)",
            borderRadius: "8px",
            border: "1px solid rgba(26, 159, 255, 0.3)",
            animation: "slideDown 0.3s ease-out"
          }}>
            {/* Strategy Selection */}
            <div style={{ marginBottom: "12px" }}>
              <div style={{ fontSize: "10px", fontWeight: "bold", marginBottom: "6px", color: "#e0e0e0" }}>
                {t.strategy}
              </div>
              <Focusable style={{ display: "flex", gap: "4px" }} flow-children="horizontal">
                {[
                  { id: "conservative", label: t.conservative },
                  { id: "balanced", label: t.balanced },
                  { id: "aggressive", label: t.aggressive }
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
                      transition: "all 0.2s ease"
                    }}>
                      <div>{strategy === s.id ? "✓ " : ""}{s.label}</div>
                    </div>
                  </Focusable>
                ))}
              </Focusable>
            </div>

            {/* Simple Mode Toggle */}
            <div style={{ marginBottom: "12px" }}>
              <ToggleField
                label={t.simpleModeDynamic}
                description={t.simpleModeDescription}
                checked={simpleMode}
                onChange={setSimpleMode}
                bottomSeparator="none"
              />
            </div>

            {/* Simple Value Slider (only if Simple Mode enabled) */}
            {simpleMode && (
              <div style={{ marginBottom: "12px" }}>
                <SliderField
                  label={t.undervoltValue}
                  value={simpleValue}
                  min={minLimit}
                  max={0}
                  step={1}
                  showValue={true}
                  onChange={(value: number) => setSimpleValue(value)}
                  valueSuffix=" mV"
                  bottomSeparator="none"
                />
                <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px" }}>
                  {t.simpleModeDescription}
                </div>
              </div>
            )}

            {/* Sample Interval */}
            <div style={{ marginBottom: "12px" }}>
              <SliderField
                label={t.sampleInterval}
                value={sampleInterval}
                min={50}
                max={500}
                step={10}
                showValue={true}
                onChange={(value: number) => setSampleInterval(value)}
                valueSuffix=" ms"
                bottomSeparator="none"
              />
              <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px" }}>
                {t.sampleIntervalDescription}
              </div>
            </div>

            {/* Hysteresis */}
            <div style={{ marginBottom: "12px" }}>
              <SliderField
                label={t.hysteresis}
                value={hysteresis}
                min={1}
                max={20}
                step={1}
                showValue={true}
                onChange={(value: number) => setHysteresis(value)}
                valueSuffix=" %"
                bottomSeparator="none"
              />
              <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px" }}>
                {t.hysteresisDescription}
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
                transition: "all 0.2s ease"
              }}>
                {isSaving ? <FaSpinner className="spin" size={11} /> : <FaCheck size={11} />}
                <span>{isSaving ? t.saving : t.save}</span>
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
              <div style={{ fontWeight: "bold", color: "#1a9fff", marginBottom: "4px" }}>ℹ️ {t.howItWorks}</div>
              • {t.sampleIntervalDescription}: {sampleInterval}ms<br/>
              • {t.strategy}: {strategy}<br/>
              • {t.hysteresis}: {hysteresis}%<br/>
            </div>
          </div>
        </PanelSectionRow>
      )}

      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};


/**
 * Manual tab component with simple/per-core/dynamic modes.
 * Improved layout with better dynamic mode integration.
 */
const ManualTab: FC = () => {
  const { state, api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  const { t } = useTranslation();
  const [coreValues, setCoreValues] = useState<number[]>([...state.cores]);
  const [controlMode, setControlMode] = useState<"single" | "percore" | "dynamic">("single");
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  const [isApplying, setIsApplying] = useState(false);

  // Get expert mode from settings
  const expertMode = state.settings.expertMode || false;
  const safeLimit = platformInfo?.safe_limit ?? -30;
  const currentMinLimit = expertMode ? -100 : safeLimit;

  // Check if dynamic mode is running
  const isDynamicRunning = state.status === "DYNAMIC RUNNING" || state.gymdeckRunning;

  // Sync with state.cores
  useEffect(() => {
    setCoreValues([...state.cores]);
    const avg = Math.round(state.cores.reduce((sum, val) => sum + val, 0) / 4);
    setSimpleValue(avg);
  }, [state.cores]);

  // Auto-detect control mode based on state
  useEffect(() => {
    if (isDynamicRunning && controlMode !== "dynamic") {
      setControlMode("dynamic");
    }
  }, [isDynamicRunning]);

  /**
   * Handle control mode change.
   */
  const handleControlModeChange = (mode: "single" | "percore" | "dynamic") => {
    setControlMode(mode);
    // Don't auto-start/stop dynamic mode here - let user control it via buttons
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
          <div style={{ 
            fontSize: "10px", 
            color: "#8b929a", 
            marginBottom: "8px",
            padding: "6px 8px",
            backgroundColor: "#23262e",
            borderRadius: "4px"
          }}>
            <div style={{ marginBottom: "2px" }}>
              <strong style={{ color: "#1a9fff" }}>{platformInfo.variant}</strong> ({platformInfo.model})
            </div>
            <div>
              Лимит / Limit: <strong style={{ color: expertMode ? "#ff9800" : "#4caf50" }}>
                {expertMode ? "-100mV (Expert)" : `${platformInfo.safe_limit}mV`}
              </strong>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Control Mode Selection */}
      <PanelSectionRow>
        <div style={{ fontSize: "11px", fontWeight: "bold", marginBottom: "6px", color: "#e0e0e0" }}>
          {t.controlMode}
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <Focusable style={{ display: "flex", gap: "4px", marginBottom: "12px" }} flow-children="horizontal">
          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("single")}
            onClick={() => handleControlModeChange("single")}
          >
            <div style={{
              padding: "10px 6px",
              backgroundColor: controlMode === "single" ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: controlMode === "single" ? "2px solid #1a9fff" : "2px solid transparent"
            }}>
              <div>{controlMode === "single" ? "✓" : ""}</div>
              <div style={{ fontSize: "9px", marginTop: "2px" }}>{t.single}</div>
            </div>
          </Focusable>

          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("percore")}
            onClick={() => handleControlModeChange("percore")}
          >
            <div style={{
              padding: "10px 6px",
              backgroundColor: controlMode === "percore" ? "#1a9fff" : "#3d4450",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: controlMode === "percore" ? "2px solid #1a9fff" : "2px solid transparent"
            }}>
              <div>{controlMode === "percore" ? "✓" : ""}</div>
              <div style={{ fontSize: "9px", marginTop: "2px" }}>{t.perCore}</div>
            </div>
          </Focusable>

          <Focusable
            style={{ flex: 1 }}
            onActivate={() => handleControlModeChange("dynamic")}
            onClick={() => handleControlModeChange("dynamic")}
          >
            <div style={{
              padding: "10px 6px",
              backgroundColor: controlMode === "dynamic" ? "#4caf50" : "#3d4450",
              color: controlMode === "dynamic" ? "#fff" : "#e0e0e0",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "bold",
              textAlign: "center",
              transition: "all 0.2s ease",
              border: controlMode === "dynamic" ? "2px solid #4caf50" : "2px solid transparent"
            }}>
              <div>{controlMode === "dynamic" ? "✓" : ""}</div>
              <div style={{ fontSize: "9px", marginTop: "2px" }}>{t.dynamic}</div>
            </div>
          </Focusable>
        </Focusable>
      </PanelSectionRow>

      {/* Dynamic Mode Panel (when selected) */}
      {controlMode === "dynamic" && (
        <DynamicSettingsInline />
      )}

      {/* Manual Controls (Single and Per-Core modes) */}
      {controlMode !== "dynamic" && (
        <>
          {/* Current Values Display */}
          <PanelSectionRow>
            <div style={{
              padding: "8px",
              backgroundColor: "#23262e",
              borderRadius: "6px",
              marginBottom: "8px"
            }}>
              <div style={{ fontSize: "9px", color: "#8b929a", marginBottom: "4px" }}>
                {t.currentValues}
              </div>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "4px"
              }}>
                {state.cores.map((value, index) => (
                  <div key={index} style={{
                    padding: "4px",
                    backgroundColor: "#1a1d23",
                    borderRadius: "4px",
                    textAlign: "center",
                    fontSize: "11px",
                    fontWeight: "bold",
                    color: value < 0 ? "#4caf50" : "#8b929a"
                  }}>
                    C{index}: {value}mV
                  </div>
                ))}
              </div>
            </div>
          </PanelSectionRow>

          {/* Sliders */}
          {controlMode === "single" ? (
            /* Single Mode: One slider for all cores */
            <PanelSectionRow>
              <SliderField
                label={t.allCores}
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
                  label={`${t.core} ${core}`}
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
            <Focusable style={{ display: "flex", gap: "6px", marginTop: "12px" }} flow-children="horizontal">
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
                  background: "linear-gradient(135deg, #1a9fff 0%, #1976d2 100%)",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "11px",
                  fontWeight: "bold",
                  opacity: isApplying ? 0.6 : 1,
                  transition: "all 0.2s ease"
                }}>
                  {isApplying ? <FaSpinner className="spin" size={11} /> : <FaCheck size={11} />}
                  <span>{t.apply}</span>
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
                  transition: "all 0.2s ease"
                }}>
                  <FaBan size={11} />
                  <span>{t.disable}</span>
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
                  transition: "all 0.2s ease"
                }}>
                  <FaTimes size={11} />
                  <span>{t.reset}</span>
                </div>
              </Focusable>
            </Focusable>
          </PanelSectionRow>
        </>
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
  const { t } = useTranslation();
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
              gap: "8px",
              padding: "10px",
              backgroundColor: "#1a3a5c",
              borderRadius: "6px",
              marginBottom: "10px",
              border: "1px solid #1a9fff",
            }}
          >
            <FaExclamationCircle style={{ color: "#1a9fff", fontSize: "16px", flexShrink: 0, marginTop: "1px" }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: "bold", color: "#64b5f6", marginBottom: "4px", fontSize: "11px" }}>
                ℹ️ {t.optionalPackages}
              </div>
              <div style={{ fontSize: "10px", color: "#bbdefb", marginBottom: "4px" }}>
                {t.notInstalled} <strong>{missingBinaries.join(", ")}</strong>
              </div>
              <div style={{ fontSize: "9px", color: "#90caf9", marginBottom: "6px" }}>
                {t.packagesNeeded}<br/>
                {t.otherFeaturesWork}
              </div>
              
              {/* Install Button */}
              <InstallBinariesButtonExpert onInstalled={checkBinaries} />
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Test selection */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          {t.runStressTest}
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <DropdownItem
          label={t.selectTest}
          menuLabel={t.selectTest}
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
                <span>{t.running} {getTestLabel(currentTest || selectedTest)}...</span>
              </>
            ) : (
              <>
                <FaPlay />
                <span>{t.runTest}</span>
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
              <span>{t.testInProgress}</span>
            </div>
            <div style={{ fontSize: "12px", color: "#8b929a" }}>
              {t.running}: {getTestLabel(currentTest || selectedTest)}
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Test history */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          {t.testHistory}
        </div>
      </PanelSectionRow>

      {history.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px" }}>
            {t.noTests}
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
  const { t } = useTranslation();
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
          {t.systemInformation}
        </div>
      </PanelSectionRow>

      {isLoading ? (
        <PanelSectionRow>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#8b929a" }}>
            <FaSpinner className="spin" />
            <span>{t.loading}</span>
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
            <InfoRow label={t.platform} value={platformInfo ? `${platformInfo.variant} (${platformInfo.model})` : "Unknown"} />
            <InfoRow label={t.safeLimit} value={platformInfo ? `${platformInfo.safe_limit} mV` : "Unknown"} />
            <InfoRow label={t.detection} value={platformInfo?.detected ? t.successful : t.failed} />
            
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
          {t.currentConfiguration}
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
              <InfoRow label={t.activeCores} value={`[${systemInfo.config.cores?.join(", ") || "0, 0, 0, 0"}]`} />
              <InfoRow label={t.lkgCores} value={`[${systemInfo.config.lkg_cores?.join(", ") || "0, 0, 0, 0"}]`} />
              <InfoRow label={t.status} value={systemInfo.config.status || "Unknown"} />
              <InfoRow label={t.presetsCount} value={String(systemInfo.config.presets_count || 0)} />
            </>
          ) : (
            <div style={{ color: "#8b929a" }}>Configuration not available</div>
          )}
        </div>
      </PanelSectionRow>

      {/* Log Viewer Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          {t.recentLogs}
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
            <div>{t.noLogs}</div>
          )}
        </div>
      </PanelSectionRow>

      {/* Export Diagnostics Button */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleExportDiagnostics}
          disabled={isExporting}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", marginTop: "16px" }}>
            {isExporting ? (
              <>
                <FaSpinner className="spin" />
                <span>{t.exporting}</span>
              </>
            ) : (
              <>
                <FaDownload />
                <span>{t.exportDiagnostics}</span>
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
                  {t.exportSuccessful}
                </div>
                <div style={{ fontSize: "12px", wordBreak: "break-all" }}>
                  {t.savedTo} {exportResult.path}
                </div>
              </>
            ) : (
              <>
                <div style={{ fontWeight: "bold" }}>
                  <FaTimes style={{ marginRight: "8px" }} />
                  {t.exportFailed}
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
