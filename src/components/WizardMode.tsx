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
  ToggleField,
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
import { FrequencyWizard } from "./FrequencyWizard";

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
            Testing: <strong>{crashInfo?.currentOffset ?? 0}mV</strong>
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
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: "400px", overflowY: "auto" }}>
      <PanelSectionRow>
        <div style={{ fontSize: "11px", color: "#ccc", marginBottom: "6px" }}>
          Find optimal undervolt through systematic testing.
        </div>
      </PanelSectionRow>

      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "9px", color: "#8b929a", padding: "6px", backgroundColor: "#1a1d24", borderRadius: "4px" }}>
            {platformInfo.variant} • Limit: {platformInfo.safe_limit}mV
          </div>
        </PanelSectionRow>
      )}

      {/* CRITICAL FIX: Vertical Button Layout */}
      <PanelSectionRow>
        <div style={{ marginBottom: "4px" }}>
          <div style={{ fontSize: "10px", color: "#8b929a", marginBottom: "4px", fontWeight: "bold" }}>
            Aggressiveness
          </div>
          <Focusable style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <ButtonItem
              layout="below"
              onClick={() => setAggressiveness("safe")}
              style={{
                width: "100%",
                backgroundColor: aggressiveness === "safe" ? "#1a9fff" : "#3d4450",
                border: aggressiveness === "safe" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "32px",
                padding: "4px",
              }}
            >
              <div style={{ fontSize: "9px", textAlign: "center", color: aggressiveness === "safe" ? "#fff" : "#8b929a" }}>
                <div style={{ fontWeight: "bold" }}>Safe (2mV steps)</div>
              </div>
            </ButtonItem>
            <ButtonItem
              layout="below"
              onClick={() => setAggressiveness("balanced")}
              style={{
                width: "100%",
                backgroundColor: aggressiveness === "balanced" ? "#1a9fff" : "#3d4450",
                border: aggressiveness === "balanced" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "32px",
                padding: "4px",
              }}
            >
              <div style={{ fontSize: "9px", textAlign: "center", color: aggressiveness === "balanced" ? "#fff" : "#8b929a" }}>
                <div style={{ fontWeight: "bold" }}>Balanced (5mV steps)</div>
              </div>
            </ButtonItem>
            <ButtonItem
              layout="below"
              onClick={() => setAggressiveness("aggressive")}
              style={{
                width: "100%",
                backgroundColor: aggressiveness === "aggressive" ? "#1a9fff" : "#3d4450",
                border: aggressiveness === "aggressive" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "32px",
                padding: "4px",
              }}
            >
              <div style={{ fontSize: "9px", textAlign: "center", color: aggressiveness === "aggressive" ? "#fff" : "#8b929a" }}>
                <div style={{ fontWeight: "bold" }}>Aggressive (10mV steps)</div>
              </div>
            </ButtonItem>
          </Focusable>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ marginBottom: "4px" }}>
          <div style={{ fontSize: "10px", color: "#8b929a", marginBottom: "4px", fontWeight: "bold" }}>
            Test Duration
          </div>
          <Focusable style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <ButtonItem
              layout="below"
              onClick={() => setTestDuration("short")}
              style={{
                width: "100%",
                backgroundColor: testDuration === "short" ? "#1a9fff" : "#3d4450",
                border: testDuration === "short" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "32px",
                padding: "4px",
              }}
            >
              <div style={{ fontSize: "9px", textAlign: "center", color: testDuration === "short" ? "#fff" : "#8b929a" }}>
                <div style={{ fontWeight: "bold" }}>Short (30s per test)</div>
              </div>
            </ButtonItem>
            <ButtonItem
              layout="below"
              onClick={() => setTestDuration("long")}
              style={{
                width: "100%",
                backgroundColor: testDuration === "long" ? "#1a9fff" : "#3d4450",
                border: testDuration === "long" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "32px",
                padding: "4px",
              }}
            >
              <div style={{ fontSize: "9px", textAlign: "center", color: testDuration === "long" ? "#fff" : "#8b929a" }}>
                <div style={{ fontWeight: "bold" }}>Long (120s per test)</div>
              </div>
            </ButtonItem>
          </Focusable>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "9px", color: "#8b929a", textAlign: "center", padding: "3px" }}>
          Est. time: ~{getEstimatedTime()} min
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleRunBenchmark} disabled={isBenchmarking}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", fontSize: "10px" }}>
            {isBenchmarking ? <FaSpinner className="spin" size={10} /> : <FaChartLine size={10} />}
            <span>{isBenchmarking ? "Running..." : "Benchmark"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {isBenchmarking && (
        <PanelSectionRow>
          <ProgressBarWithInfo
            label="Benchmark"
            description="Testing..."
            nProgress={50}
            sOperationText="Wait..."
          />
        </PanelSectionRow>
      )}

      {benchmarkResult && (
        <PanelSectionRow>
          <div style={{ fontSize: "9px", color: "#4caf50", padding: "6px", backgroundColor: "#1a1d24", borderRadius: "4px" }}>
            <div>Score: {benchmarkResult.score} ops/sec</div>
            <div>Temp: {benchmarkResult.max_temp}°C • Freq: {benchmarkResult.max_freq} MHz</div>
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleStart}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", fontSize: "11px" }}>
            <FaPlay size={10} />
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
          description={`Testing ${progress?.currentOffset ?? 0}mV`}
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
            <div>Last Stable: {progress?.liveMetrics?.last_stable ?? 0}mV</div>
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

// ==================== Enhanced Interactive Curve Chart ====================

const EnhancedCurveChart: FC<{ data: any[] }> = ({ data }) => {
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  if (!data || data.length === 0) return null;

  const width = 320;
  const height = 180;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };

  const offsets = data.map((d) => d.offset);
  const temps = data.map((d) => d.temp);

  const xMin = Math.min(...offsets);
  const xMax = Math.max(...offsets);
  const yMin = 0;
  const yMax = Math.max(...temps, 100);

  const xScale = (x: number) =>
    padding.left + ((x - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);

  const yScale = (y: number) =>
    height - padding.bottom - ((y - yMin) / (yMax - yMin)) * (height - padding.top - padding.bottom);

  const handlePointHover = (index: number, event: React.MouseEvent) => {
    setHoveredPoint(index);
    const rect = (event.currentTarget as SVGElement).getBoundingClientRect();
    setTooltipPos({ x: event.clientX - rect.left, y: event.clientY - rect.top });
  };

  return (
    <div style={{ position: "relative" }}>
      <svg width={width} height={height} style={{ backgroundColor: "#0d0f12", borderRadius: "4px" }}>
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((temp) => (
          <g key={temp}>
            <line
              x1={padding.left}
              y1={yScale(temp)}
              x2={width - padding.right}
              y2={yScale(temp)}
              stroke="#2a2d34"
              strokeWidth={1}
              strokeDasharray="2,2"
            />
            <text x={padding.left - 5} y={yScale(temp) + 3} fontSize="9" fill="#5a5d64" textAnchor="end">
              {temp}°C
            </text>
          </g>
        ))}

        {/* Axes */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="#3d4450"
          strokeWidth={2}
        />
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="#3d4450"
          strokeWidth={2}
        />

        {/* Data line with gradient */}
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4caf50" />
            <stop offset="50%" stopColor="#1a9fff" />
            <stop offset="100%" stopColor="#f44336" />
          </linearGradient>
        </defs>

        <polyline
          points={data.map((d) => `${xScale(d.offset)},${yScale(d.temp)}`).join(" ")}
          fill="none"
          stroke="url(#lineGradient)"
          strokeWidth={2}
        />

        {/* Data points with hover */}
        {data.map((point, i) => {
          const color =
            point.result === "pass" ? "#4caf50" :
            point.result === "fail" ? "#ff9800" :
            "#f44336";
          
          return (
            <g key={i}>
              <circle
                cx={xScale(point.offset)}
                cy={yScale(point.temp)}
                r={hoveredPoint === i ? 6 : 4}
                fill={color}
                stroke="#fff"
                strokeWidth={hoveredPoint === i ? 2 : 1}
                style={{ cursor: "pointer", transition: "all 0.2s" }}
                onMouseEnter={(e) => handlePointHover(i, e)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
            </g>
          );
        })}

        {/* Axis labels */}
        <text
          x={width / 2}
          y={height - 5}
          fontSize="11"
          fill="#8b929a"
          textAnchor="middle"
          fontWeight="bold"
        >
          Voltage Offset (mV)
        </text>
        <text
          x={15}
          y={height / 2}
          fontSize="11"
          fill="#8b929a"
          textAnchor="middle"
          fontWeight="bold"
          transform={`rotate(-90, 15, ${height / 2})`}
        >
          Temperature (°C)
        </text>

        {/* Legend */}
        <g transform={`translate(${width - 100}, 15)`}>
          <circle cx={0} cy={0} r={3} fill="#4caf50" />
          <text x={8} y={3} fontSize="9" fill="#8b929a">Pass</text>
          
          <circle cx={0} cy={12} r={3} fill="#ff9800" />
          <text x={8} y={15} fontSize="9" fill="#8b929a">Fail</text>
          
          <circle cx={0} cy={24} r={3} fill="#f44336" />
          <text x={8} y={27} fontSize="9" fill="#8b929a">Crash</text>
        </g>
      </svg>

      {/* Tooltip */}
      {hoveredPoint !== null && (
        <div
          style={{
            position: "absolute",
            left: tooltipPos.x + 10,
            top: tooltipPos.y - 40,
            backgroundColor: "#1a1d24",
            border: "1px solid #3d4450",
            borderRadius: "4px",
            padding: "6px 10px",
            fontSize: "10px",
            color: "#fff",
            pointerEvents: "none",
            zIndex: 1000,
            boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
          }}
        >
          <div><strong>{data[hoveredPoint].offset}mV</strong></div>
          <div>Temp: {data[hoveredPoint].temp}°C</div>
          <div style={{ 
            color: data[hoveredPoint].result === "pass" ? "#4caf50" : 
                   data[hoveredPoint].result === "fail" ? "#ff9800" : "#f44336" 
          }}>
            {data[hoveredPoint].result.toUpperCase()}
          </div>
        </div>
      )}
    </div>
  );
};

// ==================== Results Screen ====================

const ResultsScreen: FC<{
  result: any;
  onApply: (applyOnStartup: boolean, gameOnlyMode: boolean) => void;
  onStartOver: () => void;
}> = ({ result, onApply, onStartOver }) => {
  const cpuOffset = result?.offsets?.cpu || 0;
  const [isApplying, setIsApplying] = useState(false);
  const [applyOnStartup, setApplyOnStartup] = useState(false);
  const [gameOnlyMode, setGameOnlyMode] = useState(false);

  const handleApply = async () => {
    setIsApplying(true);
    try {
      await onApply(applyOnStartup, gameOnlyMode);
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
          <EnhancedCurveChart data={result?.curveData || []} />
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

      {/* CRITICAL FIX #3: Apply on Startup and Game Only Mode options */}
      <PanelSectionRow>
        <ToggleField
          label="Apply on Startup"
          description="Automatically apply this preset when DeckTune starts"
          checked={applyOnStartup}
          onChange={setApplyOnStartup}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Game Only Mode"
          description="Only apply when a game is running"
          checked={gameOnlyMode}
          onChange={setGameOnlyMode}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleApply} disabled={isApplying}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: isApplying ? "#8b929a" : "#4caf50" }}>
            {isApplying ? <FaSpinner className="spin" size={12} /> : <FaCheck size={12} />}
            <span>{isApplying ? "Applying..." : "Apply & Save as Wizard Preset"}</span>
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

// ==================== Wizard History View (Inline) ====================

const WizardHistoryView: FC<{ onClose: () => void }> = ({ onClose }) => {
  const [presets, setPresets] = useState<any[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadPresets = async () => {
    setIsLoading(true);
    try {
      const result = await call("get_wizard_presets");
      setPresets(result || []);
    } catch (err) {
      console.error("Failed to load wizard presets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPresets();
  }, []);

  const handleApply = async (preset: any) => {
    try {
      await call("apply_wizard_result", preset.id, true, preset.apply_on_startup, preset.game_only_mode);
      console.log("Applied wizard preset:", preset.id);
    } catch (err) {
      console.error("Failed to apply preset:", err);
    }
  };

  const handleDelete = async (presetId: string) => {
    try {
      await call("delete_wizard_preset", presetId);
      console.log("Deleted wizard preset:", presetId);
      setSelectedPreset(null);
      await loadPresets();
    } catch (err) {
      console.error("Failed to delete preset:", err);
    }
  };

  const handleUpdateOptions = async (presetId: string, applyOnStartup: boolean, gameOnlyMode: boolean) => {
    try {
      await call("update_wizard_preset_options", presetId, applyOnStartup, gameOnlyMode);
      console.log("Updated wizard preset options:", presetId);
      await loadPresets();
    } catch (err) {
      console.error("Failed to update preset options:", err);
    }
  };

  if (isLoading) {
    return (
      <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "20px" }}>
            <FaSpinner className="spin" style={{ fontSize: "24px", color: "#1a9fff" }} />
            <div style={{ fontSize: "12px", color: "#8b929a", marginTop: "10px" }}>
              Loading presets...
            </div>
          </div>
        </PanelSectionRow>
      </Focusable>
    );
  }

  if (selectedPreset) {
    const cpuOffset = selectedPreset.offsets?.cpu || 0;
    const [applyOnStartup, setApplyOnStartup] = useState(selectedPreset.apply_on_startup);
    const [gameOnlyMode, setGameOnlyMode] = useState(selectedPreset.game_only_mode);

    return (
      <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => setSelectedPreset(null)}>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <FaHistory size={10} />
              <span>Back to List</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>

        <PanelSectionRow>
          <ChipGradeBadge grade={selectedPreset.chip_grade} />
        </PanelSectionRow>

        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "10px" }}>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: "#1a9fff" }}>
              {cpuOffset}mV
            </div>
            <div style={{ fontSize: "10px", color: "#8b929a" }}>
              {new Date(selectedPreset.timestamp).toLocaleString()}
            </div>
          </div>
        </PanelSectionRow>

        <PanelSectionRow>
          <ToggleField
            label="Apply on Startup"
            checked={applyOnStartup}
            onChange={(val) => {
              setApplyOnStartup(val);
              handleUpdateOptions(selectedPreset.id, val, gameOnlyMode);
            }}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <ToggleField
            label="Game Only Mode"
            checked={gameOnlyMode}
            onChange={(val) => {
              setGameOnlyMode(val);
              handleUpdateOptions(selectedPreset.id, applyOnStartup, val);
            }}
          />
        </PanelSectionRow>

        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => handleApply(selectedPreset)}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#4caf50" }}>
              <FaCheck size={12} />
              <span>Apply Preset</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>

        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => handleDelete(selectedPreset.id)}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#f44336" }}>
              <FaTimes size={12} />
              <span>Delete Preset</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      </Focusable>
    );
  }

  if (presets.length === 0) {
    return (
      <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "20px", color: "#8b929a", fontSize: "12px" }}>
            No wizard presets found. Run the wizard to create your first preset.
          </div>
        </PanelSectionRow>
      </Focusable>
    );
  }

  return (
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {presets.map((preset: any) => {
        const cpuOffset = preset.offsets?.cpu || 0;
        const date = new Date(preset.timestamp).toLocaleDateString();

        return (
          <PanelSectionRow key={preset.id}>
            <ButtonItem layout="below" onClick={() => setSelectedPreset(preset)}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{ fontSize: "16px" }}>
                    {preset.chip_grade === "Platinum" && <FaTrophy style={{ color: "#e5e4e2" }} />}
                    {preset.chip_grade === "Gold" && <FaMedal style={{ color: "#ffd700" }} />}
                    {preset.chip_grade === "Silver" && <FaAward style={{ color: "#c0c0c0" }} />}
                    {preset.chip_grade === "Bronze" && <FaCertificate style={{ color: "#cd7f32" }} />}
                  </div>
                  <div>
                    <div style={{ fontSize: "11px", fontWeight: "bold" }}>
                      {preset.chip_grade} • {cpuOffset}mV
                    </div>
                    <div style={{ fontSize: "9px", color: "#8b929a" }}>
                      {date}
                    </div>
                  </div>
                </div>
              </div>
            </ButtonItem>
          </PanelSectionRow>
        );
      })}
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
  const [showHistory, setShowHistory] = useState(false);
  const [wizardType, setWizardType] = useState<"load" | "frequency">("load");

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

  const handleApply = async (applyOnStartup: boolean, gameOnlyMode: boolean) => {
    if (!localResult) return;
    try {
      await applyResult(localResult.id, true, applyOnStartup, gameOnlyMode);
      console.log(`Applied wizard result with options: startup=${applyOnStartup}, gameOnly=${gameOnlyMode}`);
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

      {/* Wizard Type Selector - FIXED: Vertical layout */}
      {!isRunning && !localResult && !showHistory && (
        <PanelSectionRow>
          <Focusable style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
            <ButtonItem
              layout="below"
              onClick={() => setWizardType("load")}
              style={{
                width: "100%",
                backgroundColor: wizardType === "load" ? "#1a9fff" : "#3d4450",
                border: wizardType === "load" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "40px",
              }}
            >
              <div style={{ 
                fontSize: "11px", 
                fontWeight: "bold",
                color: wizardType === "load" ? "#fff" : "#8b929a"
              }}>
                Load-Based Wizard
              </div>
            </ButtonItem>
            <ButtonItem
              layout="below"
              onClick={() => setWizardType("frequency")}
              style={{
                width: "100%",
                backgroundColor: wizardType === "frequency" ? "#1a9fff" : "#3d4450",
                border: wizardType === "frequency" ? "2px solid #1a9fff" : "2px solid transparent",
                minHeight: "40px",
              }}
            >
              <div style={{ 
                fontSize: "11px", 
                fontWeight: "bold",
                color: wizardType === "frequency" ? "#fff" : "#8b929a"
              }}>
                Frequency-Based Wizard
              </div>
            </ButtonItem>
          </Focusable>
        </PanelSectionRow>
      )}

      {/* History Toggle Button */}
      {!isRunning && !localResult && wizardType === "load" && (
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => setShowHistory(!showHistory)}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" }}>
              <FaHistory size={12} />
              <span>{showHistory ? "Back to Wizard" : "View History"}</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      )}

      {showCrashModal && dirtyExit?.crashInfo && (
        <CrashRecoveryModal
          crashInfo={dirtyExit.crashInfo}
          onDismiss={() => setShowCrashModal(false)}
        />
      )}

      {wizardType === "load" && (
        <>
          {!isRunning && !localResult && !showHistory && (
            <ConfigurationScreen onStart={handleStart} platformInfo={platformInfo} />
          )}

          {!isRunning && !localResult && showHistory && (
            <WizardHistoryView onClose={() => setShowHistory(false)} />
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
        </>
      )}

      {wizardType === "frequency" && (
        <FrequencyWizard />
      )}
    </PanelSection>
  );
};
