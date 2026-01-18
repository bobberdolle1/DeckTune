/**
 * FanCurveEditor component for visual fan curve editing.
 * 
 * Feature: Fan Control Integration (Phase 4)
 * 
 * Provides an interactive SVG graph for editing fan curve points.
 * Supports drag-and-drop point manipulation, add/remove points,
 * and real-time preview of the curve.
 */

import { useState, useRef, useCallback, useEffect, FC } from "react";
import { 
  PanelSection, 
  PanelSectionRow, 
  ButtonItem, 
  ToggleField,
  SliderField,
  DropdownItem,
  Focusable,
} from "@decky/ui";
import { FaFan, FaPlus, FaTrash, FaUndo, FaExclamationTriangle } from "react-icons/fa";
import { useTranslation, Translations } from "../i18n/translations";

/** Fan curve point (temperature -> speed) */
export interface FanCurvePoint {
  temp_c: number;
  speed_percent: number;
}

/** Fan configuration */
export interface FanConfig {
  enabled: boolean;
  mode: "default" | "custom" | "fixed";
  curve: FanCurvePoint[];
  zero_rpm_enabled: boolean;
  hysteresis_temp: number;
}

/** Fan status from backend */
export interface FanStatus {
  temp_c: number;
  pwm: number;
  speed_percent: number;
  mode: string;
  rpm?: number;
  safety_override: boolean;
}

interface FanCurveEditorProps {
  /** Current fan configuration */
  config: FanConfig;
  /** Current fan status (optional, for live display) */
  status?: FanStatus;
  /** Callback when configuration changes */
  onConfigChange: (config: FanConfig) => void;
  /** Callback to save configuration to backend */
  onSave: (config: FanConfig) => Promise<void>;
  /** Whether the component is in loading state */
  isLoading?: boolean;
}

// Graph dimensions - увеличен для лучшей видимости
const GRAPH_WIDTH = 300;
const GRAPH_HEIGHT = 200;
const MARGIN = { top: 25, right: 35, bottom: 35, left: 45 };
const INNER_WIDTH = GRAPH_WIDTH - MARGIN.left - MARGIN.right;
const INNER_HEIGHT = GRAPH_HEIGHT - MARGIN.top - MARGIN.bottom;

// Temperature and speed ranges
const TEMP_MIN = 30;
const TEMP_MAX = 95;
const SPEED_MIN = 0;
const SPEED_MAX = 100;

// Point interaction
const POINT_RADIUS = 7;
const POINT_HIT_RADIUS = 16;

// Temperature zones for visual feedback
const TEMP_SAFE = 70;
const TEMP_WARNING = 80;
const TEMP_DANGER = 85;

/** Default fan curve */
const DEFAULT_CURVE: FanCurvePoint[] = [
  { temp_c: 40, speed_percent: 20 },
  { temp_c: 50, speed_percent: 30 },
  { temp_c: 60, speed_percent: 45 },
  { temp_c: 70, speed_percent: 60 },
  { temp_c: 80, speed_percent: 80 },
  { temp_c: 85, speed_percent: 100 },
];

/** Fan curve presets */
interface FanCurvePreset {
  id: string;
  name: string;
  descriptionKey: keyof Translations;
  icon: string;
  curve: FanCurvePoint[];
}

/**
 * Get fan presets with translated descriptions
 */
const getFanPresets = (t: Translations): FanCurvePreset[] => [
  {
    id: "stock",
    name: t.stock,
    descriptionKey: "stockDescription",
    icon: "🏭",
    curve: [
      { temp_c: 40, speed_percent: 20 },
      { temp_c: 50, speed_percent: 30 },
      { temp_c: 60, speed_percent: 45 },
      { temp_c: 70, speed_percent: 60 },
      { temp_c: 80, speed_percent: 80 },
      { temp_c: 85, speed_percent: 100 },
    ],
  },
  {
    id: "silent",
    name: t.silent,
    descriptionKey: "silentDescription",
    icon: "🔇",
    curve: [
      { temp_c: 45, speed_percent: 15 },
      { temp_c: 55, speed_percent: 25 },
      { temp_c: 65, speed_percent: 35 },
      { temp_c: 75, speed_percent: 50 },
      { temp_c: 82, speed_percent: 70 },
      { temp_c: 88, speed_percent: 100 },
    ],
  },
  {
    id: "balanced",
    name: t.balanced,
    descriptionKey: "balancedDescription",
    icon: "⚖️",
    curve: [
      { temp_c: 40, speed_percent: 20 },
      { temp_c: 50, speed_percent: 30 },
      { temp_c: 60, speed_percent: 45 },
      { temp_c: 70, speed_percent: 60 },
      { temp_c: 80, speed_percent: 80 },
      { temp_c: 85, speed_percent: 100 },
    ],
  },
  {
    id: "cool",
    name: t.cool,
    descriptionKey: "coolDescription",
    icon: "❄️",
    curve: [
      { temp_c: 35, speed_percent: 25 },
      { temp_c: 45, speed_percent: 40 },
      { temp_c: 55, speed_percent: 55 },
      { temp_c: 65, speed_percent: 70 },
      { temp_c: 75, speed_percent: 85 },
      { temp_c: 80, speed_percent: 100 },
    ],
  },
  {
    id: "aggressive",
    name: t.aggressive,
    descriptionKey: "aggressiveDescription",
    icon: "🌪️",
    curve: [
      { temp_c: 30, speed_percent: 30 },
      { temp_c: 40, speed_percent: 50 },
      { temp_c: 50, speed_percent: 65 },
      { temp_c: 60, speed_percent: 80 },
      { temp_c: 70, speed_percent: 90 },
      { temp_c: 75, speed_percent: 100 },
    ],
  },
  {
    id: "gaming",
    name: t.gaming,
    descriptionKey: "gamingDescription",
    icon: "🎮",
    curve: [
      { temp_c: 40, speed_percent: 25 },
      { temp_c: 55, speed_percent: 40 },
      { temp_c: 65, speed_percent: 55 },
      { temp_c: 72, speed_percent: 70 },
      { temp_c: 78, speed_percent: 85 },
      { temp_c: 83, speed_percent: 100 },
    ],
  },
  {
    id: "eco",
    name: t.eco,
    descriptionKey: "ecoDescription",
    icon: "🌱",
    curve: [
      { temp_c: 50, speed_percent: 20 },
      { temp_c: 60, speed_percent: 30 },
      { temp_c: 70, speed_percent: 45 },
      { temp_c: 78, speed_percent: 60 },
      { temp_c: 85, speed_percent: 80 },
      { temp_c: 90, speed_percent: 100 },
    ],
  },
];

/**
 * Convert temperature to X coordinate
 */
const tempToX = (temp: number): number => {
  const normalized = (temp - TEMP_MIN) / (TEMP_MAX - TEMP_MIN);
  return MARGIN.left + normalized * INNER_WIDTH;
};

/**
 * Convert speed to Y coordinate (inverted - 0% at bottom)
 */
const speedToY = (speed: number): number => {
  const normalized = (speed - SPEED_MIN) / (SPEED_MAX - SPEED_MIN);
  return MARGIN.top + INNER_HEIGHT - normalized * INNER_HEIGHT;
};

/**
 * Convert X coordinate to temperature
 */
const xToTemp = (x: number): number => {
  const normalized = (x - MARGIN.left) / INNER_WIDTH;
  return Math.round(TEMP_MIN + normalized * (TEMP_MAX - TEMP_MIN));
};

/**
 * Convert Y coordinate to speed
 */
const yToSpeed = (y: number): number => {
  const normalized = 1 - (y - MARGIN.top) / INNER_HEIGHT;
  return Math.round(SPEED_MIN + normalized * (SPEED_MAX - SPEED_MIN));
};

/**
 * Clamp value to range
 */
const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value));
};

/**
 * Generate SVG path for the curve
 */
const generateCurvePath = (points: FanCurvePoint[]): string => {
  if (points.length === 0) return "";
  
  const sorted = [...points].sort((a, b) => a.temp_c - b.temp_c);
  
  // Start from left edge at first point's speed
  let path = `M ${MARGIN.left} ${speedToY(sorted[0].speed_percent)}`;
  path += ` L ${tempToX(sorted[0].temp_c)} ${speedToY(sorted[0].speed_percent)}`;
  
  // Connect all points
  for (let i = 1; i < sorted.length; i++) {
    path += ` L ${tempToX(sorted[i].temp_c)} ${speedToY(sorted[i].speed_percent)}`;
  }
  
  // Extend to right edge at last point's speed
  const lastPoint = sorted[sorted.length - 1];
  path += ` L ${MARGIN.left + INNER_WIDTH} ${speedToY(lastPoint.speed_percent)}`;
  
  return path;
};

/**
 * FanCurveEditor component
 */
export const FanCurveEditor: FC<FanCurveEditorProps> = ({
  config,
  status,
  onConfigChange,
  onSave,
  isLoading = false,
}) => {
  const { t } = useTranslation();
  const FAN_PRESETS = getFanPresets(t);
  const svgRef = useRef<SVGSVGElement>(null);
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Handle point drag start
  const handlePointMouseDown = useCallback((index: number, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDraggingIndex(index);
  }, []);

  // Handle mouse move for dragging
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (draggingIndex === null || !svgRef.current) return;
    
    const svg = svgRef.current;
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newTemp = clamp(xToTemp(x), TEMP_MIN, TEMP_MAX);
    const newSpeed = clamp(yToSpeed(y), SPEED_MIN, SPEED_MAX);
    
    const newCurve = [...config.curve];
    newCurve[draggingIndex] = { temp_c: newTemp, speed_percent: newSpeed };
    
    onConfigChange({ ...config, curve: newCurve });
    setHasChanges(true);
  }, [draggingIndex, config, onConfigChange]);

  // Handle mouse up to stop dragging
  const handleMouseUp = useCallback(() => {
    setDraggingIndex(null);
  }, []);

  // Handle click on graph to add point
  const handleGraphClick = useCallback((e: React.MouseEvent) => {
    if (draggingIndex !== null || !svgRef.current) return;
    if (config.mode !== "custom") return;
    
    const svg = svgRef.current;
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Check if click is within graph area
    if (x < MARGIN.left || x > MARGIN.left + INNER_WIDTH) return;
    if (y < MARGIN.top || y > MARGIN.top + INNER_HEIGHT) return;
    
    // Check if click is near existing point
    const clickTemp = xToTemp(x);
    const isNearExisting = config.curve.some(p => Math.abs(p.temp_c - clickTemp) < 5);
    if (isNearExisting) return;
    
    const newPoint: FanCurvePoint = {
      temp_c: clamp(clickTemp, TEMP_MIN, TEMP_MAX),
      speed_percent: clamp(yToSpeed(y), SPEED_MIN, SPEED_MAX),
    };
    
    const newCurve = [...config.curve, newPoint].sort((a, b) => a.temp_c - b.temp_c);
    onConfigChange({ ...config, curve: newCurve });
    setHasChanges(true);
  }, [draggingIndex, config, onConfigChange]);

  // Handle point removal
  const handleRemovePoint = useCallback((index: number) => {
    if (config.curve.length <= 2) return; // Keep at least 2 points
    
    const newCurve = config.curve.filter((_, i) => i !== index);
    onConfigChange({ ...config, curve: newCurve });
    setHasChanges(true);
  }, [config, onConfigChange]);

  // Reset to default curve
  const handleReset = useCallback(() => {
    onConfigChange({ ...config, curve: [...DEFAULT_CURVE] });
    setHasChanges(true);
  }, [config, onConfigChange]);

  // Apply preset curve
  const handleApplyPreset = useCallback((presetId: string) => {
    const preset = FAN_PRESETS.find(p => p.id === presetId);
    if (preset) {
      onConfigChange({ ...config, curve: [...preset.curve] });
      setHasChanges(true);
    }
  }, [config, onConfigChange]);

  // Save configuration
  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      await onSave(config);
      setHasChanges(false);
    } finally {
      setIsSaving(false);
    }
  }, [config, onSave]);

  // Mode options for dropdown
  const modeOptions = [
    { data: "default", label: t.fanModeDefault },
    { data: "custom", label: t.fanModeCustom },
    { data: "fixed", label: t.fanModeFixed },
  ];

  // Sort curve for display
  const sortedCurve = [...config.curve].sort((a, b) => a.temp_c - b.temp_c);

  return (
    <PanelSection title="Fan Control">
      {/* Enable toggle */}
      <PanelSectionRow>
        <ToggleField
          label={t.enableFanControl}
          description={t.enableFanControlDescription}
          checked={config.enabled}
          onChange={(enabled) => {
            onConfigChange({ ...config, enabled });
            setHasChanges(true);
          }}
          disabled={isLoading}
        />
      </PanelSectionRow>

      {config.enabled && (
        <>
          {/* Mode selector */}
          <PanelSectionRow>
            <DropdownItem
              label={t.fanMode}
              rgOptions={modeOptions}
              selectedOption={config.mode}
              onChange={(option) => {
                onConfigChange({ ...config, mode: option.data as FanConfig["mode"] });
                setHasChanges(true);
              }}
              disabled={isLoading}
            />
          </PanelSectionRow>

          {/* Current status display */}
          {status && (
            <PanelSectionRow>
              <div style={{
                padding: "12px",
                background: status.safety_override 
                  ? "linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%)"
                  : "linear-gradient(135deg, #1a3a5c 0%, #1a2a3a 100%)",
                borderRadius: "10px",
                border: status.safety_override 
                  ? "2px solid #f44336"
                  : "2px solid rgba(26, 159, 255, 0.3)",
                boxShadow: status.safety_override
                  ? "0 0 20px rgba(244, 67, 54, 0.4)"
                  : "0 4px 12px rgba(0, 0, 0, 0.3)",
              }}>
                {/* Header */}
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "10px",
                }}>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}>
                    <FaFan style={{ 
                      color: status.safety_override ? "#ffcdd2" : "#4caf50",
                      fontSize: "18px",
                    }} className={status.speed_percent > 0 ? "fan-spin" : ""} />
                    <span style={{
                      fontSize: "13px",
                      fontWeight: "bold",
                      color: status.safety_override ? "#ffcdd2" : "#e0e0e0",
                    }}>
                      {t.fanStatus}
                    </span>
                  </div>
                  {status.safety_override && (
                    <div style={{
                      padding: "4px 8px",
                      backgroundColor: "rgba(255, 255, 255, 0.2)",
                      borderRadius: "4px",
                      fontSize: "9px",
                      fontWeight: "bold",
                      color: "#fff",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}>
                      <FaExclamationTriangle />
                      {t.safetyOverride}
                    </div>
                  )}
                </div>

                {/* Metrics Grid */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "10px",
                }}>
                  {/* Temperature */}
                  <div style={{
                    padding: "10px",
                    backgroundColor: "rgba(0, 0, 0, 0.3)",
                    borderRadius: "8px",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                  }}>
                    <div style={{
                      fontSize: "9px",
                      color: "#8b929a",
                      marginBottom: "4px",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px",
                    }}>
                      {t.temperature}
                    </div>
                    <div style={{
                      fontSize: "20px",
                      fontWeight: "bold",
                      color: status.temp_c >= TEMP_DANGER ? "#f44336" : 
                             status.temp_c >= TEMP_WARNING ? "#ff9800" : 
                             status.temp_c >= TEMP_SAFE ? "#ffc107" : "#4caf50",
                      display: "flex",
                      alignItems: "baseline",
                      gap: "2px",
                    }}>
                      {status.temp_c}
                      <span style={{ fontSize: "12px", opacity: 0.8 }}>°C</span>
                    </div>
                  </div>

                  {/* Fan Speed */}
                  <div style={{
                    padding: "10px",
                    backgroundColor: "rgba(0, 0, 0, 0.3)",
                    borderRadius: "8px",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                  }}>
                    <div style={{
                      fontSize: "9px",
                      color: "#8b929a",
                      marginBottom: "4px",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px",
                    }}>
                      {t.fanSpeed}
                    </div>
                    <div style={{
                      fontSize: "20px",
                      fontWeight: "bold",
                      color: "#1a9fff",
                      display: "flex",
                      alignItems: "baseline",
                      gap: "2px",
                    }}>
                      {status.speed_percent}
                      <span style={{ fontSize: "12px", opacity: 0.8 }}>%</span>
                    </div>
                  </div>

                  {/* RPM (if available) */}
                  {status.rpm !== undefined && (
                    <div style={{
                      padding: "10px",
                      backgroundColor: "rgba(0, 0, 0, 0.3)",
                      borderRadius: "8px",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                    }}>
                      <div style={{
                        fontSize: "9px",
                        color: "#8b929a",
                        marginBottom: "4px",
                        textTransform: "uppercase",
                        letterSpacing: "0.5px",
                      }}>
                        RPM
                      </div>
                      <div style={{
                        fontSize: "20px",
                        fontWeight: "bold",
                        color: "#66bb6a",
                      }}>
                        {status.rpm}
                      </div>
                    </div>
                  )}

                  {/* Mode */}
                  <div style={{
                    padding: "10px",
                    backgroundColor: "rgba(0, 0, 0, 0.3)",
                    borderRadius: "8px",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                  }}>
                    <div style={{
                      fontSize: "9px",
                      color: "#8b929a",
                      marginBottom: "4px",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px",
                    }}>
                      {t.mode}
                    </div>
                    <div style={{
                      fontSize: "13px",
                      fontWeight: "bold",
                      color: "#e0e0e0",
                    }}>
                      {status.mode}
                    </div>
                  </div>
                </div>

                {/* Safety Override Warning */}
                {status.safety_override && (
                  <div style={{
                    marginTop: "10px",
                    padding: "8px",
                    backgroundColor: "rgba(255, 255, 255, 0.1)",
                    borderRadius: "6px",
                    fontSize: "10px",
                    color: "#ffcdd2",
                    lineHeight: "1.4",
                  }}>
                    {t.safetyOverrideDescription}
                  </div>
                )}
              </div>

              <style>{`
                .fan-spin {
                  animation: fan-spin-anim ${Math.max(0.3, 2 - (status.speed_percent / 100) * 1.7)}s linear infinite;
                }
                @keyframes fan-spin-anim {
                  from { transform: rotate(0deg); }
                  to { transform: rotate(360deg); }
                }
              `}</style>
            </PanelSectionRow>
          )}

          {/* Fan curve graph (only for custom mode) */}
          {config.mode === "custom" && (
            <PanelSectionRow>
              <div style={{
                background: "linear-gradient(135deg, #1a1d23 0%, #23262e 100%)",
                borderRadius: "10px",
                padding: "12px",
                border: "1px solid rgba(26, 159, 255, 0.2)",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
              }}>
                <svg
                  ref={svgRef}
                  width={GRAPH_WIDTH}
                  height={GRAPH_HEIGHT}
                  style={{ 
                    cursor: draggingIndex !== null ? "grabbing" : "crosshair",
                    display: "block",
                  }}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                  onClick={handleGraphClick}
                >
                  {/* Definitions for gradients and effects */}
                  <defs>
                    {/* Gradient for curve fill */}
                    <linearGradient id="curveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#1a9fff" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="#1a9fff" stopOpacity="0.05" />
                    </linearGradient>
                    
                    {/* Gradient for danger zone */}
                    <linearGradient id="dangerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="rgba(244, 67, 54, 0.05)" />
                      <stop offset="100%" stopColor="rgba(244, 67, 54, 0.15)" />
                    </linearGradient>
                    
                    {/* Gradient for warning zone */}
                    <linearGradient id="warningGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="rgba(255, 152, 0, 0.03)" />
                      <stop offset="100%" stopColor="rgba(255, 152, 0, 0.08)" />
                    </linearGradient>

                    {/* Glow effect for current temp indicator */}
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>

                  {/* Background zones */}
                  <g>
                    {/* Safe zone (до 70°C) - зеленоватый */}
                    <rect
                      x={MARGIN.left}
                      y={MARGIN.top}
                      width={tempToX(TEMP_SAFE) - MARGIN.left}
                      height={INNER_HEIGHT}
                      fill="rgba(76, 175, 80, 0.03)"
                    />
                    
                    {/* Warning zone (70-80°C) - желтоватый */}
                    <rect
                      x={tempToX(TEMP_SAFE)}
                      y={MARGIN.top}
                      width={tempToX(TEMP_WARNING) - tempToX(TEMP_SAFE)}
                      height={INNER_HEIGHT}
                      fill="url(#warningGradient)"
                    />
                    
                    {/* Danger zone (80-85°C) - оранжевый */}
                    <rect
                      x={tempToX(TEMP_WARNING)}
                      y={MARGIN.top}
                      width={tempToX(TEMP_DANGER) - tempToX(TEMP_WARNING)}
                      height={INNER_HEIGHT}
                      fill="rgba(255, 152, 0, 0.08)"
                    />
                    
                    {/* Critical zone (85°C+) - красный */}
                    <rect
                      x={tempToX(TEMP_DANGER)}
                      y={MARGIN.top}
                      width={MARGIN.left + INNER_WIDTH - tempToX(TEMP_DANGER)}
                      height={INNER_HEIGHT}
                      fill="url(#dangerGradient)"
                    />
                  </g>

                  {/* Grid lines - улучшенная сетка */}
                  <g stroke="#3d4450" strokeWidth="1" opacity="0.5">
                    {/* Horizontal grid (speed) - каждые 10% */}
                    {[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map(speed => (
                      <line
                        key={`h-${speed}`}
                        x1={MARGIN.left}
                        y1={speedToY(speed)}
                        x2={MARGIN.left + INNER_WIDTH}
                        y2={speedToY(speed)}
                        strokeDasharray={speed % 25 === 0 ? "none" : "2,2"}
                        opacity={speed % 25 === 0 ? 0.6 : 0.3}
                      />
                    ))}
                    {/* Vertical grid (temperature) - каждые 5°C */}
                    {[30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95].map(temp => (
                      <line
                        key={`v-${temp}`}
                        x1={tempToX(temp)}
                        y1={MARGIN.top}
                        x2={tempToX(temp)}
                        y2={MARGIN.top + INNER_HEIGHT}
                        strokeDasharray={temp % 10 === 0 ? "none" : "2,2"}
                        opacity={temp % 10 === 0 ? 0.6 : 0.3}
                      />
                    ))}
                  </g>

                  {/* Zone boundary markers */}
                  <g>
                    {[TEMP_SAFE, TEMP_WARNING, TEMP_DANGER].map((temp, idx) => (
                      <g key={`zone-${temp}`}>
                        <line
                          x1={tempToX(temp)}
                          y1={MARGIN.top}
                          x2={tempToX(temp)}
                          y2={MARGIN.top + INNER_HEIGHT}
                          stroke={idx === 0 ? "#4caf50" : idx === 1 ? "#ff9800" : "#f44336"}
                          strokeWidth="1.5"
                          strokeDasharray="4,3"
                          opacity="0.4"
                        />
                      </g>
                    ))}
                  </g>

                  {/* Axis labels - улучшенные */}
                  <g fill="#b0b0b0" fontSize="11" fontWeight="500">
                    {/* Y-axis (speed) */}
                    {[0, 25, 50, 75, 100].map(speed => (
                      <text
                        key={`y-${speed}`}
                        x={MARGIN.left - 8}
                        y={speedToY(speed) + 4}
                        textAnchor="end"
                        fill={speed === 100 ? "#f44336" : speed === 0 ? "#4caf50" : "#b0b0b0"}
                      >
                        {speed}%
                      </text>
                    ))}
                    {/* X-axis (temperature) */}
                    {[30, 40, 50, 60, 70, 80, 90].map(temp => (
                      <text
                        key={`x-${temp}`}
                        x={tempToX(temp)}
                        y={MARGIN.top + INNER_HEIGHT + 18}
                        textAnchor="middle"
                        fill={temp >= TEMP_DANGER ? "#f44336" : temp >= TEMP_WARNING ? "#ff9800" : "#b0b0b0"}
                      >
                        {temp}°
                      </text>
                    ))}
                  </g>

                  {/* Axis titles */}
                  <g fill="#8b929a" fontSize="10" fontWeight="600">
                    {/* Y-axis title */}
                    <text
                      x={12}
                      y={MARGIN.top + INNER_HEIGHT / 2}
                      textAnchor="middle"
                      transform={`rotate(-90, 12, ${MARGIN.top + INNER_HEIGHT / 2})`}
                    >
                      Fan Speed (%)
                    </text>
                    {/* X-axis title */}
                    <text
                      x={MARGIN.left + INNER_WIDTH / 2}
                      y={GRAPH_HEIGHT - 5}
                      textAnchor="middle"
                    >
                      Temperature (°C)
                    </text>
                  </g>

                  {/* Current temperature indicator with animation */}
                  {status && (
                    <g filter="url(#glow)">
                      <line
                        x1={tempToX(status.temp_c)}
                        y1={MARGIN.top}
                        x2={tempToX(status.temp_c)}
                        y2={MARGIN.top + INNER_HEIGHT}
                        stroke="#4caf50"
                        strokeWidth="2.5"
                        strokeDasharray="5,3"
                        opacity="0.8"
                      >
                        <animate
                          attributeName="stroke-dashoffset"
                          from="0"
                          to="8"
                          dur="1s"
                          repeatCount="indefinite"
                        />
                      </line>
                      {/* Current point marker */}
                      <circle
                        cx={tempToX(status.temp_c)}
                        cy={speedToY(status.speed_percent)}
                        r="6"
                        fill="#4caf50"
                        stroke="#fff"
                        strokeWidth="2"
                      >
                        <animate
                          attributeName="r"
                          values="6;8;6"
                          dur="2s"
                          repeatCount="indefinite"
                        />
                      </circle>
                      {/* Current status label */}
                      <rect
                        x={tempToX(status.temp_c) - 35}
                        y={MARGIN.top - 18}
                        width="70"
                        height="16"
                        rx="3"
                        fill="#4caf50"
                        opacity="0.9"
                      />
                      <text
                        x={tempToX(status.temp_c)}
                        y={MARGIN.top - 7}
                        textAnchor="middle"
                        fill="#fff"
                        fontSize="10"
                        fontWeight="bold"
                      >
                        NOW: {status.temp_c}°C
                      </text>
                    </g>
                  )}

                  {/* Curve path with gradient fill */}
                  <path
                    d={`${generateCurvePath(sortedCurve)} L ${MARGIN.left + INNER_WIDTH} ${MARGIN.top + INNER_HEIGHT} L ${MARGIN.left} ${MARGIN.top + INNER_HEIGHT} Z`}
                    fill="url(#curveGradient)"
                  />

                  {/* Curve line with shadow */}
                  <path
                    d={generateCurvePath(sortedCurve)}
                    fill="none"
                    stroke="#1a9fff"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    filter="url(#glow)"
                  />

                  {/* Draggable points with enhanced visuals */}
                  {sortedCurve.map((point, index) => {
                    const isDragging = draggingIndex === config.curve.findIndex(p => 
                      p.temp_c === point.temp_c && p.speed_percent === point.speed_percent
                    );
                    return (
                      <g key={index}>
                        {/* Hit area (larger, invisible) */}
                        <circle
                          cx={tempToX(point.temp_c)}
                          cy={speedToY(point.speed_percent)}
                          r={POINT_HIT_RADIUS}
                          fill="transparent"
                          style={{ cursor: isDragging ? "grabbing" : "grab" }}
                          onMouseDown={(e) => handlePointMouseDown(
                            config.curve.findIndex(p => 
                              p.temp_c === point.temp_c && p.speed_percent === point.speed_percent
                            ),
                            e
                          )}
                          onDoubleClick={() => handleRemovePoint(
                            config.curve.findIndex(p => 
                              p.temp_c === point.temp_c && p.speed_percent === point.speed_percent
                            )
                          )}
                        />
                        {/* Outer glow ring */}
                        <circle
                          cx={tempToX(point.temp_c)}
                          cy={speedToY(point.speed_percent)}
                          r={POINT_RADIUS + 3}
                          fill="none"
                          stroke="#1a9fff"
                          strokeWidth="2"
                          opacity={isDragging ? "0.6" : "0.3"}
                          style={{ pointerEvents: "none" }}
                        />
                        {/* Visible point */}
                        <circle
                          cx={tempToX(point.temp_c)}
                          cy={speedToY(point.speed_percent)}
                          r={POINT_RADIUS}
                          fill={isDragging ? "#66bb6a" : "#1a9fff"}
                          stroke="#fff"
                          strokeWidth="2.5"
                          style={{ pointerEvents: "none" }}
                          filter="url(#glow)"
                        />
                        {/* Point label with background */}
                        <g style={{ pointerEvents: "none" }}>
                          <rect
                            x={tempToX(point.temp_c) - 28}
                            y={speedToY(point.speed_percent) - 22}
                            width="56"
                            height="14"
                            rx="3"
                            fill="rgba(0, 0, 0, 0.8)"
                          />
                          <text
                            x={tempToX(point.temp_c)}
                            y={speedToY(point.speed_percent) - 12}
                            fill="#fff"
                            fontSize="10"
                            fontWeight="bold"
                            textAnchor="middle"
                          >
                            {point.temp_c}° / {point.speed_percent}%
                          </text>
                        </g>
                      </g>
                    );
                  })}
                </svg>

                {/* Enhanced instructions with icons */}
                <div style={{
                  display: "flex",
                  justifyContent: "space-around",
                  fontSize: "9px",
                  color: "#8b929a",
                  marginTop: "8px",
                  padding: "6px",
                  backgroundColor: "rgba(26, 159, 255, 0.05)",
                  borderRadius: "6px",
                  gap: "8px",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <span style={{ color: "#1a9fff", fontSize: "12px" }}>●</span>
                    <span>Click = Add</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <span style={{ color: "#1a9fff", fontSize: "12px" }}>↔</span>
                    <span>Drag = Move</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <span style={{ color: "#f44336", fontSize: "12px" }}>✕</span>
                    <span>Double = Remove</span>
                  </div>
                </div>

                {/* Temperature zone legend */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(4, 1fr)",
                  gap: "4px",
                  marginTop: "8px",
                  fontSize: "8px",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                    <div style={{ width: "12px", height: "12px", backgroundColor: "rgba(76, 175, 80, 0.3)", borderRadius: "2px" }} />
                    <span style={{ color: "#4caf50" }}>Safe</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                    <div style={{ width: "12px", height: "12px", backgroundColor: "rgba(255, 152, 0, 0.3)", borderRadius: "2px" }} />
                    <span style={{ color: "#ff9800" }}>Warm</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                    <div style={{ width: "12px", height: "12px", backgroundColor: "rgba(255, 152, 0, 0.5)", borderRadius: "2px" }} />
                    <span style={{ color: "#ff9800" }}>Hot</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                    <div style={{ width: "12px", height: "12px", backgroundColor: "rgba(244, 67, 54, 0.3)", borderRadius: "2px" }} />
                    <span style={{ color: "#f44336" }}>Critical</span>
                  </div>
                </div>
              </div>
            </PanelSectionRow>
          )}

          {/* Fixed speed slider (only for fixed mode) */}
          {config.mode === "fixed" && (
            <PanelSectionRow>
              <SliderField
                label={t.fixedFanSpeed}
                value={config.curve[0]?.speed_percent ?? 50}
                min={0}
                max={100}
                step={5}
                showValue
                onChange={(value) => {
                  onConfigChange({
                    ...config,
                    curve: [{ temp_c: 0, speed_percent: value }],
                  });
                  setHasChanges(true);
                }}
                disabled={isLoading}
              />
            </PanelSectionRow>
          )}

          {/* Zero RPM toggle */}
          <PanelSectionRow>
            <ToggleField
              label={t.zeroRPM}
              description={t.zeroRPMDescription}
              checked={config.zero_rpm_enabled}
              onChange={(zero_rpm_enabled) => {
                onConfigChange({ ...config, zero_rpm_enabled });
                setHasChanges(true);
              }}
              disabled={isLoading}
            />
          </PanelSectionRow>

          {/* Hysteresis slider */}
          <PanelSectionRow>
            <SliderField
              label={t.temperatureHysteresis}
              description={t.temperatureHysteresisDescription}
              value={config.hysteresis_temp}
              min={1}
              max={10}
              step={1}
              showValue
              valueSuffix="°C"
              onChange={(hysteresis_temp) => {
                onConfigChange({ ...config, hysteresis_temp });
                setHasChanges(true);
              }}
              disabled={isLoading}
            />
          </PanelSectionRow>

          {/* Curve Presets (only for custom mode) */}
          {config.mode === "custom" && (
            <>
              <PanelSectionRow>
                <div style={{ 
                  fontSize: "12px", 
                  fontWeight: "bold", 
                  marginTop: "12px",
                  marginBottom: "8px",
                  color: "#e0e0e0",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}>
                  <span>⚡</span>
                  <span>{t.quickPresets}</span>
                </div>
              </PanelSectionRow>

              <PanelSectionRow>
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "6px",
                  marginBottom: "8px",
                }}>
                  {FAN_PRESETS.map((preset) => (
                    <Focusable
                      key={preset.id}
                      onActivate={() => handleApplyPreset(preset.id)}
                      onClick={() => handleApplyPreset(preset.id)}
                      style={{
                        padding: "10px 8px",
                        background: "linear-gradient(135deg, #2a2d35 0%, #23262e 100%)",
                        borderRadius: "8px",
                        cursor: "pointer",
                        border: "1px solid rgba(26, 159, 255, 0.2)",
                        transition: "all 0.2s ease",
                      }}
                      focusClassName="preset-focus"
                    >
                      <div style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "4px",
                      }}>
                        <div style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                        }}>
                          <span style={{ fontSize: "16px" }}>{preset.icon}</span>
                          <span style={{ 
                            fontSize: "11px", 
                            fontWeight: "bold",
                            color: "#e0e0e0",
                          }}>
                            {preset.name}
                          </span>
                        </div>
                        <div style={{
                          fontSize: "8px",
                          color: "#8b929a",
                          lineHeight: "1.3",
                        }}>
                          {t[preset.descriptionKey]}
                        </div>
                      </div>
                    </Focusable>
                  ))}
                </div>
              </PanelSectionRow>

              <style>{`
                .preset-focus {
                  border: 2px solid #1a9fff !important;
                  box-shadow: 0 0 12px rgba(26, 159, 255, 0.5);
                  transform: scale(1.02);
                }
                .preset-focus:hover {
                  background: linear-gradient(135deg, #1a9fff 0%, #1976d2 100%) !important;
                }
              `}</style>
            </>
          )}

          {/* Action buttons */}
          <PanelSectionRow>
            <div style={{ display: "flex", gap: "8px" }}>
              <ButtonItem
                layout="below"
                onClick={handleReset}
                disabled={isLoading || isSaving}
              >
                <FaUndo style={{ marginRight: "4px" }} />
                Reset
              </ButtonItem>
              <ButtonItem
                layout="below"
                onClick={handleSave}
                disabled={isLoading || isSaving || !hasChanges}
              >
                {isSaving ? "Saving..." : "Save"}
              </ButtonItem>
            </div>
          </PanelSectionRow>
        </>
      )}
    </PanelSection>
  );
};

export default FanCurveEditor;
