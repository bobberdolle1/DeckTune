/**
 * Refactored WizardMode component for DeckTune.
 * 
 * Feature: Wizard Mode Refactoring
 * 
 * Complete redesign with:
 * - Configuration screen with aggressiveness/duration settings
 * - Real-time progress with ETA/OTA/heartbeat
 * - Results screen with curve visualization and chip grading
 * - Crash recovery modal
 * - Results history browser
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  ProgressBarWithInfo,
  Focusable,
  Field,
  ToggleField,
  Dropdown,
} from "@decky/ui";
import { call } from "@decky/api";
import {
  FaExclamationTriangle,
  FaSpinner,
  FaCheck,
  FaTimes,
  FaCog,
  FaTrophy,
  FaMedal,
  FaAward,
  FaCertificate,
  FaChartLine,
  FaHistory,
  FaPlay,
  FaStop,
} from "react-icons/fa";
import { useDeckTune, useWizard, usePlatformInfo } from "../context";
import { WizardConfig } from "../context/WizardContext";

// ==================== Panic Disable Button ====================

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
          borderRadius: "4px",
          minHeight: "30px",
          padding: "4px 6px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "4px",
            color: "#fff",
            fontWeight: "bold",
            fontSize: "11px",
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" size={10} />
              <span>Disabling...</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle size={10} />
              <span>PANIC DISABLE</span>
            </>
          )}
        </div>
      </ButtonItem>
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
    </PanelSectionRow>
  );
};

// ==================== Crash Recovery Modal ====================

const CrashRecoveryModal: FC<{ crashInfo: any; onDismiss: () => void }> = ({ crashInfo, onDismiss }) => {
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          backgroundColor: "#1a1d24",
          borderRadius: "8px",
          padding: "20px",
          maxWidth: "400px",
          border: "2px solid #ff9800",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" }}>
          <FaExclamationTriangle style={{ color: "#ff9800", fontSize: "24px" }} />
          <h3 style={{ margin: 0, color: "#fff" }}>Crash Detected</h3>
        </div>
        
        <p style={{ fontSize: "13px", color: "#ccc", marginBottom: "15px" }}>
          The system crashed during wizard testing. This is normal when pushing limits.
        </p>
        
        <div style={{ backgroundColor: "#2a2d34", padding: "10px", borderRadius: "4px", marginBottom: "15px" }}>
          <div style={{ fontSize: "11px", color: "#8b929a", marginBottom: "5px" }}>Crash Details:</div>
          <div style={{ fontSize: "12px", color: "#fff" }}>
            Testing: <strong>{crashInfo?.currentOffset}mV</strong>
          </div>
          <div style={{ fontSize: "12px", color: "#4caf50" }}>
            Last Stable: <strong>{crashInfo?.lastStable}mV</strong>
          </div>
        </div>
        
        <ButtonItem layout="below" onClick={onDismiss}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" }}>
            <FaCheck size={12} />
            <span>Continue</span>
          </div>
        </ButtonItem>
      </div>
    </div>
  );
};

// ==================== Configuration Screen ====================

const ConfigurationScreen: FC<{
  onStart: (config: WizardConfig) => void;
  platformInfo: any;
}> = ({ onStart, platformInfo }) => {
  const [aggressiveness, setAggressiveness] = useState<"safe" | "balanced" | "aggressive">("balanced");
  const [testDuration, setTestDuration] = useState<"short" | "long">("short");
  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState<any>(null);

  const handleStart = () => {
    const config: WizardConfig = {
      targetDomains: ["cpu"],
      aggressiveness,
      testDuration,
      safetyLimits: {
        cpu: platformInfo?.safe_limit || -100,
      },
    };
    onStart(config);
  };

  const handleRunBenchmark = async () => {
    setIsBenchmarking(true);
    setBenchmarkResult(null);
    try {
      const result = await call("run_wizard_benchmark", 10);
      if (result?.success) {
        setBenchmarkResult(result);
      }
    } catch (err) {
      console.error("Benchmark failed:", err);
    } finally {
      setIsBenchmarking(false);
    }
  };

  const getEstimatedTime = () => {
    const base = testDuration === "short" ? 5 : 15;
    const multiplier = aggressiveness === "safe" ? 2 : aggressiveness === "aggressive" ? 0.5 : 1;
    return Math.round(base * multiplier);
  };

  return (
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <PanelSectionRow>
        <div style={{ fontSize: "13px", color: "#ccc", marginBottom: "10px" }}>
          Automatically find the optimal undervolt for your chip through systematic testing.
        </div>
      </PanelSectionRow>

      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "10px", color: "#8b929a", padding: "8px", backgroundColor: "#1a1d24", borderRadius: "4px" }}>
            {platformInfo.variant} ({platformInfo.model}) • Safety Limit: {platformInfo.safe_limit}mV
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <Field label="Aggressiveness">
          <Dropdown
            rgOptions={[
              { label: "Safe (2mV steps, +10mV margin)", data: "safe" },
              { label: "Balanced (5mV steps, +5mV margin)", data: "balanced" },
              { label: "Aggressive (10mV steps, +2mV margin)", data: "aggressive" },
            ]}
            selectedOption={aggressiveness}
            onChange={(option) => setAggressiveness(option.data)}
          />
        </Field>
      </PanelSectionRow>

      <PanelSectionRow>
        <Field label="Test Duration">
          <Dropdown
            rgOptions={[
              { label: "Short (30s per test)", data: "short" },
              { label: "Long (120s per test)", data: "long" },
            ]}
            selectedOption={testDuration}
            onChange={(option) => setTestDuration(option.data)}
          />
        </Field>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "11px", color: "#8b929a", textAlign: "center", padding: "5px" }}>
          Estimated time: ~{getEstimatedTime()} minutes
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleRunBenchmark} disabled={isBenchmarking}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" }}>
            {isBenchmarking ? <FaSpinner className="spin" size={12} /> : <FaChartLine size={12} />}
            <span>{isBenchmarking ? "Running..." : "Run Benchmark"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {benchmarkResult && (
        <PanelSectionRow>
          <div style={{ fontSize: "10px", color: "#4caf50", padding: "8px", backgroundColor: "#1a1d24", borderRadius: "4px" }}>
            <div>Score: {benchmarkResult.score} ops/sec</div>
            <div>Max Temp: {benchmarkResult.max_temp}°C</div>
            <div>Max Freq: {benchmarkResult.max_freq} MHz</div>
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleStart}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" }}>
            <FaPlay size={12} />
            <span>Start Wizard</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </Focusable>
  );
};

// ==================== Progress Screen ====================

const ProgressScreen: FC<{
  progress: any;
  onCancel: () => void;
}> = ({ progress, onCancel }) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const formatOTA = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <PanelSectionRow>
        <div style={{ textAlign: "center", marginBottom: "15px" }}>
          <FaSpinner
            style={{
              animation: "spin 1s linear infinite",
              fontSize: "32px",
              color: "#1a9fff",
            }}
          />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ProgressBarWithInfo
          label={progress?.currentStage || "Initializing..."}
          description={`Testing ${progress?.currentOffset}mV`}
          nProgress={progress?.progressPercent || 0}
          sOperationText={`ETA: ${formatTime(progress?.etaSeconds || 0)}`}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "11px",
            color: "#8b929a",
            padding: "8px",
            backgroundColor: "#1a1d24",
            borderRadius: "4px",
          }}
        >
          <div>
            <div>Elapsed: {formatOTA(progress?.otaSeconds || 0)}</div>
            <div>Iterations: {progress?.liveMetrics?.iterations || 0}</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div>Last Stable: {progress?.liveMetrics?.last_stable || 0}mV</div>
            <div style={{ color: "#4caf50" }}>● Active</div>
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onCancel}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#f44336" }}>
            <FaStop size={12} />
            <span>Cancel</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </Focusable>
  );
};

// ==================== Chip Grade Badge ====================

const ChipGradeBadge: FC<{ grade: string }> = ({ grade }) => {
  const getGradeConfig = () => {
    switch (grade) {
      case "Platinum":
        return { icon: FaTrophy, color: "#e5e4e2", glow: "#e5e4e2" };
      case "Gold":
        return { icon: FaMedal, color: "#ffd700", glow: "#ffd700" };
      case "Silver":
        return { icon: FaAward, color: "#c0c0c0", glow: "#c0c0c0" };
      default:
        return { icon: FaCertificate, color: "#cd7f32", glow: "#cd7f32" };
    }
  };

  const config = getGradeConfig();
  const Icon = config.icon;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
        padding: "15px",
        backgroundColor: "#1a1d24",
        borderRadius: "8px",
        border: `2px solid ${config.color}`,
        boxShadow: `0 0 15px ${config.glow}`,
      }}
    >
      <Icon style={{ fontSize: "32px", color: config.color }} />
      <div>
        <div style={{ fontSize: "18px", fontWeight: "bold", color: config.color }}>
          {grade}
        </div>
        <div style={{ fontSize: "11px", color: "#8b929a" }}>Chip Quality</div>
      </div>
    </div>
  );
};

// ==================== Simple Curve Chart ====================

const SimpleCurveChart: FC<{ data: any[] }> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const width = 280;
  const height = 120;
  const padding = 25;

  const offsets = data.map((d) => d.offset);
  const temps = data.map((d) => d.temp);

  const xMin = Math.min(...offsets);
  const xMax = Math.max(...offsets);
  const yMin = 0;
  const yMax = Math.max(...temps, 100);

  const xScale = (x: number) =>
    padding + ((x - xMin) / (xMax - xMin)) * (width - 2 * padding);

  const yScale = (y: number) =>
    height - padding - ((y - yMin) / (yMax - yMin)) * (height - 2 * padding);

  return (
    <svg width={width} height={height} style={{ backgroundColor: "#0d0f12", borderRadius: "4px" }}>
      {/* Grid lines */}
      <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#3d4450" strokeWidth={1} />
      <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#3d4450" strokeWidth={1} />

      {/* Data line */}
      <polyline
        points={data.map((d) => `${xScale(d.offset)},${yScale(d.temp)}`).join(" ")}
        fill="none"
        stroke="#1a9fff"
        strokeWidth={2}
      />

      {/* Data points */}
      {data.map((point, i) => (
        <circle
          key={i}
          cx={xScale(point.offset)}
          cy={yScale(point.temp)}
          r={3}
          fill={
            point.result === "pass" ? "#4caf50" :
            point.result === "fail" ? "#f44336" :
            "#ff9800"
          }
        />
      ))}

      {/* Axis labels */}
      <text x={width / 2} y={height - 5} fontSize="9" fill="#8b929a" textAnchor="middle">
        Offset (mV)
      </text>
      <text x={10} y={height / 2} fontSize="9" fill="#8b929a" textAnchor="middle" transform={`rotate(-90, 10, ${height / 2})`}>
        Temp (°C)
      </text>
    </svg>
  );
};

// ==================== Results Screen ====================

const ResultsScreen: FC<{
  result: any;
  onApply: () => void;
  onStartOver: () => void;
}> = ({ result, onApply, onStartOver }) => {
  const cpuOffset = result?.offsets?.cpu || 0;
  const [isApplying, setIsApplying] = useState(false);

  const handleApply = async () => {
    setIsApplying(true);
    try {
      await onApply();
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <PanelSectionRow>
        <ChipGradeBadge grade={result?.chipGrade || "Bronze"} />
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ textAlign: "center", padding: "10px" }}>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#1a9fff" }}>
            {cpuOffset}mV
          </div>
          <div style={{ fontSize: "11px", color: "#8b929a" }}>Recommended Undervolt</div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <SimpleCurveChart data={result?.curveData || []} />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontSize: "10px",
            color: "#8b929a",
            padding: "8px",
            backgroundColor: "#1a1d24",
            borderRadius: "4px",
          }}
        >
          <div>Duration: {Math.round(result?.duration || 0)}s</div>
          <div>Iterations: {result?.iterations || 0}</div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleApply} disabled={isApplying}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: isApplying ? "#8b929a" : "#4caf50" }}>
            {isApplying ? <FaSpinner className="spin" size={12} /> : <FaCheck size={12} />}
            <span>{isApplying ? "Applying..." : "Apply & Save as Preset"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onStartOver}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" }}>
            <FaHistory size={12} />
            <span>Start Over</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </Focusable>
  );
};

// ==================== Main Component ====================

export const WizardMode: FC = () => {
  const { info: platformInfo } = usePlatformInfo();
  const {
    isRunning,
    progress,
    result,
    dirtyExit,
    startWizard,
    cancelWizard,
    applyResult,
  } = useWizard();

  const [showCrashModal, setShowCrashModal] = useState(false);
  const [localResult, setLocalResult] = useState<any>(null);

  useEffect(() => {
    if (dirtyExit?.detected && !showCrashModal) {
      setShowCrashModal(true);
    }
  }, [dirtyExit]);

  useEffect(() => {
    if (result) {
      setLocalResult(result);
    }
  }, [result]);

  const handleStart = async (config: WizardConfig) => {
    try {
      setLocalResult(null);
      await startWizard(config);
    } catch (err) {
      console.error("Failed to start wizard:", err);
    }
  };

  const handleCancel = async () => {
    try {
      await cancelWizard();
    } catch (err) {
      console.error("Failed to cancel wizard:", err);
    }
  };

  const handleApply = async () => {
    if (!localResult) return;
    try {
      await applyResult(localResult.id, true);
    } catch (err) {
      console.error("Failed to apply result:", err);
    }
  };

  const handleStartOver = () => {
    setLocalResult(null);
  };

  return (
    <PanelSection title="Wizard Mode">
      <PanicDisableButton />

      {showCrashModal && dirtyExit?.crashInfo && (
        <CrashRecoveryModal
          crashInfo={dirtyExit.crashInfo}
          onDismiss={() => setShowCrashModal(false)}
        />
      )}

      {!isRunning && !localResult && (
        <ConfigurationScreen onStart={handleStart} platformInfo={platformInfo} />
      )}

      {isRunning && progress && (
        <ProgressScreen progress={progress} onCancel={handleCancel} />
      )}

      {!isRunning && localResult && (
        <ResultsScreen
          result={localResult}
          onApply={handleApply}
          onStartOver={handleStartOver}
        />
      )}
    </PanelSection>
  );
};
