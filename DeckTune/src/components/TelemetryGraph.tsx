/**
 * TelemetryGraph component for displaying real-time temperature and power data.
 * 
 * Feature: decktune-3.1-reliability-ux
 * Requirements: 2.3, 2.4, 2.6
 * 
 * Displays scrolling line graphs showing the last 60 seconds of telemetry data.
 * Supports temperature (°C) and power (W) data types with hover tooltips.
 */

import { useState, useRef, useCallback, MouseEvent, FC } from "react";
import { FaThermometerHalf, FaBolt } from "react-icons/fa";
import { TelemetrySample } from "../api/types";

/**
 * Props for the TelemetryGraph component.
 */
interface TelemetryGraphProps {
  /** Array of telemetry samples to display */
  data: TelemetrySample[];
  /** Type of data to display: temperature or power */
  type: "temperature" | "power";
  /** Width of the graph in pixels (default: 300) */
  width?: number;
  /** Height of the graph in pixels (default: 100) */
  height?: number;
}

/**
 * Tooltip state for hover display.
 */
interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  value: number;
  timestamp: number;
}

// Graph constants
const DEFAULT_WIDTH = 300;
const DEFAULT_HEIGHT = 100;
const MARGIN_LEFT = 35;
const MARGIN_RIGHT = 10;
const MARGIN_TOP = 5;
const MARGIN_BOTTOM = 20;
const MAX_DISPLAY_SECONDS = 60;

/**
 * Format timestamp for tooltip display.
 */
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString([], { 
    hour: "2-digit", 
    minute: "2-digit", 
    second: "2-digit" 
  });
};

/**
 * Get the value from a sample based on graph type.
 */
const getValue = (sample: TelemetrySample, type: "temperature" | "power"): number => {
  return type === "temperature" ? sample.temperature_c : sample.power_w;
};

/**
 * Get display configuration based on graph type.
 */
const getTypeConfig = (type: "temperature" | "power") => {
  if (type === "temperature") {
    return {
      label: "Temperature",
      unit: "°C",
      color: "#f44336",
      icon: FaThermometerHalf,
      minValue: 30,
      maxValue: 100,
      gridLines: [40, 55, 70, 85],
    };
  }
  return {
    label: "Power",
    unit: "W",
    color: "#ff9800",
    icon: FaBolt,
    minValue: 0,
    maxValue: 30,
    gridLines: [5, 10, 15, 20, 25],
  };
};

/**
 * TelemetryGraph component - displays real-time scrolling line graph.
 * 
 * Requirements:
 * - 2.3: Display scrolling line graph showing last 60 seconds of temperature data
 * - 2.4: Display scrolling line graph showing last 60 seconds of power data
 * - 2.6: Display exact value and timestamp on hover
 */
export const TelemetryGraph: FC<TelemetryGraphProps> = ({
  data,
  type,
  width = DEFAULT_WIDTH,
  height = DEFAULT_HEIGHT,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    x: 0,
    y: 0,
    value: 0,
    timestamp: 0,
  });

  const config = getTypeConfig(type);
  const Icon = config.icon;

  // Calculate graph dimensions
  const graphWidth = width - MARGIN_LEFT - MARGIN_RIGHT;
  const graphHeight = height - MARGIN_TOP - MARGIN_BOTTOM;

  // Filter data to last 60 seconds
  const now = Date.now() / 1000;
  const cutoffTime = now - MAX_DISPLAY_SECONDS;
  const filteredData = data.filter((sample) => sample.timestamp >= cutoffTime);

  // Calculate min/max values for dynamic scaling
  const values = filteredData.map((s) => getValue(s, type));
  const dataMin = values.length > 0 ? Math.min(...values) : config.minValue;
  const dataMax = values.length > 0 ? Math.max(...values) : config.maxValue;
  
  // Add padding to the range
  const range = dataMax - dataMin || 10;
  const minValue = Math.max(config.minValue, Math.floor(dataMin - range * 0.1));
  const maxValue = Math.min(config.maxValue, Math.ceil(dataMax + range * 0.1));
  const valueRange = maxValue - minValue || 1;

  /**
   * Convert a value to Y coordinate.
   */
  const valueToY = useCallback(
    (value: number): number => {
      const normalized = (value - minValue) / valueRange;
      return MARGIN_TOP + graphHeight - normalized * graphHeight;
    },
    [minValue, valueRange, graphHeight]
  );

  /**
   * Convert a timestamp to X coordinate.
   */
  const timeToX = useCallback(
    (timestamp: number): number => {
      const elapsed = now - timestamp;
      const normalized = 1 - elapsed / MAX_DISPLAY_SECONDS;
      return MARGIN_LEFT + normalized * graphWidth;
    },
    [now, graphWidth]
  );

  /**
   * Generate SVG path for the data line.
   */
  const generatePath = (): string => {
    if (filteredData.length === 0) return "";

    const points = filteredData.map((sample) => {
      const x = timeToX(sample.timestamp);
      const y = valueToY(getValue(sample, type));
      return `${x},${y}`;
    });

    return `M ${points.join(" L ")}`;
  };

  /**
   * Handle mouse move for tooltip.
   * Requirements: 2.6
   */
  const handleMouseMove = useCallback(
    (event: MouseEvent<SVGSVGElement>) => {
      if (filteredData.length === 0) return;

      const svg = svgRef.current;
      if (!svg) return;

      const rect = svg.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;

      // Find the closest data point
      let closestSample: TelemetrySample | null = null;
      let closestDistance = Infinity;

      filteredData.forEach((sample) => {
        const x = timeToX(sample.timestamp);
        const distance = Math.abs(x - mouseX);
        if (distance < closestDistance) {
          closestDistance = distance;
          closestSample = sample;
        }
      });

      if (closestSample && closestDistance < 20) {
        const x = timeToX((closestSample as TelemetrySample).timestamp);
        const value = getValue(closestSample as TelemetrySample, type);
        const y = valueToY(value);

        setTooltip({
          visible: true,
          x,
          y,
          value,
          timestamp: (closestSample as TelemetrySample).timestamp,
        });
      } else {
        setTooltip((prev) => ({ ...prev, visible: false }));
      }
    },
    [filteredData, timeToX, valueToY, type]
  );

  /**
   * Handle mouse leave to hide tooltip.
   */
  const handleMouseLeave = useCallback(() => {
    setTooltip((prev) => ({ ...prev, visible: false }));
  }, []);

  // Get current value for display
  const currentValue =
    filteredData.length > 0
      ? getValue(filteredData[filteredData.length - 1], type)
      : null;

  return (
    <div
      style={{
        backgroundColor: "#23262e",
        borderRadius: "8px",
        padding: "12px",
        marginBottom: "8px",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "8px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Icon style={{ color: config.color }} />
          <span style={{ fontWeight: "bold", fontSize: "13px" }}>
            {config.label}
          </span>
        </div>
        {currentValue !== null && (
          <span
            style={{
              fontSize: "16px",
              fontWeight: "bold",
              color: config.color,
            }}
          >
            {currentValue.toFixed(1)}
            {config.unit}
          </span>
        )}
      </div>

      {/* Graph */}
      <div
        style={{
          position: "relative",
          backgroundColor: "#1a1d23",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <svg
          ref={svgRef}
          width={width}
          height={height}
          style={{ display: "block", width: "100%", height: "auto" }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          {/* Grid lines */}
          {config.gridLines
            .filter((v) => v >= minValue && v <= maxValue)
            .map((value) => {
              const y = valueToY(value);
              return (
                <g key={value}>
                  <line
                    x1={MARGIN_LEFT}
                    y1={y}
                    x2={width - MARGIN_RIGHT}
                    y2={y}
                    stroke="#3d4450"
                    strokeWidth={1}
                  />
                  <text
                    x={MARGIN_LEFT - 4}
                    y={y + 3}
                    fill="#8b929a"
                    fontSize="9"
                    textAnchor="end"
                  >
                    {value}
                  </text>
                </g>
              );
            })}

          {/* Y-axis labels (min/max) */}
          <text
            x={MARGIN_LEFT - 4}
            y={MARGIN_TOP + 8}
            fill="#8b929a"
            fontSize="9"
            textAnchor="end"
          >
            {maxValue}
          </text>
          <text
            x={MARGIN_LEFT - 4}
            y={height - MARGIN_BOTTOM - 2}
            fill="#8b929a"
            fontSize="9"
            textAnchor="end"
          >
            {minValue}
          </text>

          {/* X-axis labels */}
          <text
            x={MARGIN_LEFT}
            y={height - 4}
            fill="#8b929a"
            fontSize="9"
            textAnchor="start"
          >
            -60s
          </text>
          <text
            x={MARGIN_LEFT + graphWidth / 2}
            y={height - 4}
            fill="#8b929a"
            fontSize="9"
            textAnchor="middle"
          >
            -30s
          </text>
          <text
            x={width - MARGIN_RIGHT}
            y={height - 4}
            fill="#8b929a"
            fontSize="9"
            textAnchor="end"
          >
            now
          </text>

          {/* Data line */}
          {filteredData.length > 1 && (
            <path
              d={generatePath()}
              fill="none"
              stroke={config.color}
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Data points (only show if few points) */}
          {filteredData.length > 0 && filteredData.length <= 10 && (
            <>
              {filteredData.map((sample, index) => (
                <circle
                  key={index}
                  cx={timeToX(sample.timestamp)}
                  cy={valueToY(getValue(sample, type))}
                  r={3}
                  fill={config.color}
                />
              ))}
            </>
          )}

          {/* Tooltip indicator */}
          {tooltip.visible && (
            <>
              {/* Vertical line */}
              <line
                x1={tooltip.x}
                y1={MARGIN_TOP}
                x2={tooltip.x}
                y2={height - MARGIN_BOTTOM}
                stroke="#8b929a"
                strokeWidth={1}
                strokeDasharray="3,3"
              />
              {/* Point highlight */}
              <circle
                cx={tooltip.x}
                cy={tooltip.y}
                r={5}
                fill={config.color}
                stroke="#fff"
                strokeWidth={2}
              />
            </>
          )}

          {/* No data message */}
          {filteredData.length === 0 && (
            <text
              x={width / 2}
              y={height / 2}
              fill="#8b929a"
              fontSize="12"
              textAnchor="middle"
            >
              No data available
            </text>
          )}
        </svg>

        {/* Tooltip box - Requirements: 2.6 */}
        {tooltip.visible && (
          <div
            style={{
              position: "absolute",
              left: Math.min(tooltip.x + 10, width - 100),
              top: Math.max(tooltip.y - 40, 5),
              backgroundColor: "rgba(0, 0, 0, 0.85)",
              color: "#fff",
              padding: "6px 10px",
              borderRadius: "4px",
              fontSize: "11px",
              pointerEvents: "none",
              zIndex: 10,
              whiteSpace: "nowrap",
            }}
          >
            <div style={{ fontWeight: "bold", color: config.color }}>
              {tooltip.value.toFixed(1)}
              {config.unit}
            </div>
            <div style={{ color: "#8b929a", fontSize: "10px" }}>
              {formatTime(tooltip.timestamp)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TelemetryGraph;
