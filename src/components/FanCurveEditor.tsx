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
} from "@decky/ui";
import { FaFan, FaPlus, FaTrash, FaUndo } from "react-icons/fa";

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

// Graph dimensions
const GRAPH_WIDTH = 280;
const GRAPH_HEIGHT = 160;
const MARGIN = { top: 20, right: 30, bottom: 30, left: 40 };
const INNER_WIDTH = GRAPH_WIDTH - MARGIN.left - MARGIN.right;
const INNER_HEIGHT = GRAPH_HEIGHT - MARGIN.top - MARGIN.bottom;

// Temperature and speed ranges
const TEMP_MIN = 30;
const TEMP_MAX = 95;
const SPEED_MIN = 0;
const SPEED_MAX = 100;

// Point interaction
const POINT_RADIUS = 8;
const POINT_HIT_RADIUS = 15;

/** Default fan curve */
const DEFAULT_CURVE: FanCurvePoint[] = [
  { temp_c: 40, speed_percent: 20 },
  { temp_c: 50, speed_percent: 30 },
  { temp_c: 60, speed_percent: 45 },
  { temp_c: 70, speed_percent: 60 },
  { temp_c: 80, speed_percent: 80 },
  { temp_c: 85, speed_percent: 100 },
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
    { data: "default", label: "Default (BIOS)" },
    { data: "custom", label: "Custom Curve" },
    { data: "fixed", label: "Fixed Speed" },
  ];

  // Sort curve for display
  const sortedCurve = [...config.curve].sort((a, b) => a.temp_c - b.temp_c);

  return (
    <PanelSection title="Fan Control">
      {/* Enable toggle */}
      <PanelSectionRow>
        <ToggleField
          label="Enable Fan Control"
          description="Take manual control of the fan"
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
              label="Fan Mode"
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
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "8px 12px",
                backgroundColor: "#23262e",
                borderRadius: "8px",
                fontSize: "13px",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <FaFan style={{ 
                    color: status.safety_override ? "#f44336" : "#4caf50",
                    animation: status.speed_percent > 0 ? "spin 1s linear infinite" : "none",
                  }} />
                  <span>{status.temp_c}°C</span>
                </div>
                <div style={{ color: "#8b929a" }}>
                  {status.speed_percent}% {status.rpm ? `(${status.rpm} RPM)` : ""}
                </div>
                {status.safety_override && (
                  <span style={{ color: "#f44336", fontSize: "11px" }}>
                    Safety Override
                  </span>
                )}
              </div>
            </PanelSectionRow>
          )}

          {/* Fan curve graph (only for custom mode) */}
          {config.mode === "custom" && (
            <PanelSectionRow>
              <div style={{
                backgroundColor: "#1a1d23",
                borderRadius: "8px",
                padding: "8px",
              }}>
                <svg
                  ref={svgRef}
                  width={GRAPH_WIDTH}
                  height={GRAPH_HEIGHT}
                  style={{ cursor: draggingIndex !== null ? "grabbing" : "crosshair" }}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                  onClick={handleGraphClick}
                >
                  {/* Grid lines */}
                  <g stroke="#3d4450" strokeWidth="1">
                    {/* Horizontal grid (speed) */}
                    {[0, 25, 50, 75, 100].map(speed => (
                      <line
                        key={`h-${speed}`}
                        x1={MARGIN.left}
                        y1={speedToY(speed)}
                        x2={MARGIN.left + INNER_WIDTH}
                        y2={speedToY(speed)}
                      />
                    ))}
                    {/* Vertical grid (temperature) */}
                    {[40, 50, 60, 70, 80, 90].map(temp => (
                      <line
                        key={`v-${temp}`}
                        x1={tempToX(temp)}
                        y1={MARGIN.top}
                        x2={tempToX(temp)}
                        y2={MARGIN.top + INNER_HEIGHT}
                      />
                    ))}
                  </g>

                  {/* Axis labels */}
                  <g fill="#8b929a" fontSize="10">
                    {/* Y-axis (speed) */}
                    {[0, 50, 100].map(speed => (
                      <text
                        key={`y-${speed}`}
                        x={MARGIN.left - 5}
                        y={speedToY(speed) + 3}
                        textAnchor="end"
                      >
                        {speed}%
                      </text>
                    ))}
                    {/* X-axis (temperature) */}
                    {[40, 60, 80].map(temp => (
                      <text
                        key={`x-${temp}`}
                        x={tempToX(temp)}
                        y={MARGIN.top + INNER_HEIGHT + 15}
                        textAnchor="middle"
                      >
                        {temp}°C
                      </text>
                    ))}
                  </g>

                  {/* Safety zone (85°C+) */}
                  <rect
                    x={tempToX(85)}
                    y={MARGIN.top}
                    width={MARGIN.left + INNER_WIDTH - tempToX(85)}
                    height={INNER_HEIGHT}
                    fill="rgba(244, 67, 54, 0.1)"
                  />

                  {/* Current temperature indicator */}
                  {status && (
                    <line
                      x1={tempToX(status.temp_c)}
                      y1={MARGIN.top}
                      x2={tempToX(status.temp_c)}
                      y2={MARGIN.top + INNER_HEIGHT}
                      stroke="#4caf50"
                      strokeWidth="2"
                      strokeDasharray="4,4"
                    />
                  )}

                  {/* Curve path */}
                  <path
                    d={generateCurvePath(sortedCurve)}
                    fill="none"
                    stroke="#1a9fff"
                    strokeWidth="2"
                  />

                  {/* Curve fill */}
                  <path
                    d={`${generateCurvePath(sortedCurve)} L ${MARGIN.left + INNER_WIDTH} ${MARGIN.top + INNER_HEIGHT} L ${MARGIN.left} ${MARGIN.top + INNER_HEIGHT} Z`}
                    fill="rgba(26, 159, 255, 0.1)"
                  />

                  {/* Draggable points */}
                  {sortedCurve.map((point, index) => (
                    <g key={index}>
                      {/* Hit area (larger, invisible) */}
                      <circle
                        cx={tempToX(point.temp_c)}
                        cy={speedToY(point.speed_percent)}
                        r={POINT_HIT_RADIUS}
                        fill="transparent"
                        style={{ cursor: "grab" }}
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
                      {/* Visible point */}
                      <circle
                        cx={tempToX(point.temp_c)}
                        cy={speedToY(point.speed_percent)}
                        r={POINT_RADIUS}
                        fill="#1a9fff"
                        stroke="#fff"
                        strokeWidth="2"
                        style={{ pointerEvents: "none" }}
                      />
                      {/* Point label */}
                      <text
                        x={tempToX(point.temp_c)}
                        y={speedToY(point.speed_percent) - 12}
                        fill="#fff"
                        fontSize="9"
                        textAnchor="middle"
                        style={{ pointerEvents: "none" }}
                      >
                        {point.temp_c}°/{point.speed_percent}%
                      </text>
                    </g>
                  ))}
                </svg>

                {/* Instructions */}
                <div style={{
                  fontSize: "10px",
                  color: "#8b929a",
                  textAlign: "center",
                  marginTop: "4px",
                }}>
                  Click to add point • Drag to move • Double-click to remove
                </div>
              </div>
            </PanelSectionRow>
          )}

          {/* Fixed speed slider (only for fixed mode) */}
          {config.mode === "fixed" && (
            <PanelSectionRow>
              <SliderField
                label="Fixed Fan Speed"
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
              label="Zero RPM Mode"
              description="Allow fan to stop below 45°C (risky!)"
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
              label="Temperature Hysteresis"
              description="Prevents rapid speed changes"
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
