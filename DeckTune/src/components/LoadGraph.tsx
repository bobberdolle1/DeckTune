/**
 * LoadGraph component for displaying real-time CPU load and undervolt values.
 * 
 * Feature: decktune-3.0-automation
 * Requirements: 6.3, 6.4
 * 
 * Displays per-core CPU load percentages and applied undervolt values.
 * Shows historical data with dual Y-axes and profile change markers.
 * Implements 60-second rolling window with 1-second resolution.
 */

import { FC, useEffect, useState, useRef } from "react";
import { FaMicrochip } from "react-icons/fa";

interface LoadGraphProps {
  /** Current per-core load values (0-100%) */
  load: number[];
  /** Current per-core undervolt values (mV) */
  values: number[];
  /** Whether dynamic mode is currently active */
  isActive: boolean;
  /** Active profile name (if any) */
  activeProfile?: string;
}

/**
 * Extended graph data point with undervolt values and profile info.
 * Requirements: 6.3
 */
interface GraphDataPoint {
  timestamp: number;
  load: number[];
  values: number[];
  profile?: string;
}

const MAX_HISTORY_POINTS = 60; // Keep 60 data points (1 minute at 1Hz)
const GRAPH_HEIGHT = 120;
const GRAPH_WIDTH = 300;
const MARGIN_LEFT = 35;
const MARGIN_RIGHT = 35;

/**
 * Get color for a specific core (load lines).
 */
const getCoreColor = (coreIndex: number): string => {
  const colors = ["#1a9fff", "#4caf50", "#ff9800", "#f44336"];
  return colors[coreIndex] || "#8b929a";
};

/**
 * Get color for undervolt value lines (orange tones).
 */
const getValueColor = (coreIndex: number): string => {
  const colors = ["#ff9800", "#ffb74d", "#ffa726", "#ff8a65"];
  return colors[coreIndex] || "#ff9800";
};

/**
 * LoadGraph component - displays real-time CPU load and undervolt values.
 * Requirements: 6.3, 6.4
 */
export const LoadGraph: FC<LoadGraphProps> = ({ load, values, isActive, activeProfile }) => {
  const [history, setHistory] = useState<GraphDataPoint[]>([]);
  const [previousProfile, setPreviousProfile] = useState<string | undefined>(activeProfile);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const updateIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Update history at 1-second intervals (Requirements: 6.3)
  useEffect(() => {
    if (!isActive || load.length !== 4 || values.length !== 4) {
      // Clear history when not active
      setHistory([]);
      setPreviousProfile(undefined);
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
        updateIntervalRef.current = null;
      }
      return;
    }

    // Detect profile change
    const profileChanged = activeProfile !== previousProfile && previousProfile !== undefined;
    
    // Add new data point
    const addDataPoint = () => {
      setHistory((prev) => {
        const newPoint: GraphDataPoint = {
          timestamp: Date.now(),
          load: [...load],
          values: [...values],
          profile: profileChanged ? activeProfile : undefined,
        };

        const newHistory = [...prev, newPoint];

        // Keep only the last MAX_HISTORY_POINTS (60-second rolling window)
        if (newHistory.length > MAX_HISTORY_POINTS) {
          return newHistory.slice(-MAX_HISTORY_POINTS);
        }

        return newHistory;
      });

      if (profileChanged) {
        setPreviousProfile(activeProfile);
      }
    };

    // Add initial point immediately
    addDataPoint();

    // Set up 1-second interval
    updateIntervalRef.current = setInterval(addDataPoint, 1000);

    return () => {
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
      }
    };
  }, [load, values, isActive, activeProfile, previousProfile]);

  // Draw the graph on canvas with dual Y-axes (Requirements: 6.3, 6.4)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || history.length === 0) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    // Clear canvas
    ctx.clearRect(0, 0, GRAPH_WIDTH, GRAPH_HEIGHT);

    // Draw background grid
    ctx.strokeStyle = "#3d4450";
    ctx.lineWidth = 1;

    // Horizontal grid lines (every 25%)
    for (let i = 0; i <= 4; i++) {
      const y = (i * GRAPH_HEIGHT) / 4;
      ctx.beginPath();
      ctx.moveTo(MARGIN_LEFT, y);
      ctx.lineTo(GRAPH_WIDTH - MARGIN_RIGHT, y);
      ctx.stroke();
    }

    // Calculate graph area
    const graphWidth = GRAPH_WIDTH - MARGIN_LEFT - MARGIN_RIGHT;
    const pointSpacing = graphWidth / (MAX_HISTORY_POINTS - 1);

    // Draw profile change markers (Requirements: 6.3)
    history.forEach((point, index) => {
      if (point.profile) {
        const x = MARGIN_LEFT + index * pointSpacing;
        
        // Draw vertical line
        ctx.strokeStyle = "#4caf50";
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 3]);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, GRAPH_HEIGHT);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw label
        ctx.fillStyle = "#4caf50";
        ctx.font = "9px sans-serif";
        ctx.save();
        ctx.translate(x + 2, GRAPH_HEIGHT - 5);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(point.profile || "Profile", 0, 0);
        ctx.restore();
      }
    });

    // Draw load lines for each core (blue tones, left Y-axis)
    for (let coreIndex = 0; coreIndex < 4; coreIndex++) {
      ctx.strokeStyle = getCoreColor(coreIndex);
      ctx.lineWidth = 2;
      ctx.beginPath();

      let firstPoint = true;

      history.forEach((point, index) => {
        const x = MARGIN_LEFT + index * pointSpacing;
        const loadValue = point.load[coreIndex] || 0;
        // Invert Y axis (0% at bottom, 100% at top)
        const y = GRAPH_HEIGHT - (loadValue / 100) * GRAPH_HEIGHT;

        if (firstPoint) {
          ctx.moveTo(x, y);
          firstPoint = false;
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();
    }

    // Draw undervolt value lines (orange tones, right Y-axis)
    // Requirements: 6.3, 6.4
    const minValue = -50; // Minimum expected undervolt value
    const maxValue = 0;   // Maximum expected undervolt value
    const valueRange = maxValue - minValue;

    for (let coreIndex = 0; coreIndex < 4; coreIndex++) {
      ctx.strokeStyle = getValueColor(coreIndex);
      ctx.lineWidth = 1.5;
      ctx.setLineDash([3, 2]);
      ctx.beginPath();

      let firstPoint = true;

      history.forEach((point, index) => {
        const x = MARGIN_LEFT + index * pointSpacing;
        const value = point.values[coreIndex] || 0;
        // Map value to graph height (0mV at top, -50mV at bottom)
        const normalizedValue = (value - minValue) / valueRange;
        const y = GRAPH_HEIGHT - normalizedValue * GRAPH_HEIGHT;

        if (firstPoint) {
          ctx.moveTo(x, y);
          firstPoint = false;
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();
      ctx.setLineDash([]);
    }

    // If dynamic mode is inactive, draw static line (Requirements: 6.4)
    if (!isActive && values.length === 4) {
      const avgValue = values.reduce((sum, v) => sum + v, 0) / values.length;
      const normalizedValue = (avgValue - minValue) / valueRange;
      const y = GRAPH_HEIGHT - normalizedValue * GRAPH_HEIGHT;

      ctx.strokeStyle = "#ff9800";
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(MARGIN_LEFT, y);
      ctx.lineTo(GRAPH_WIDTH - MARGIN_RIGHT, y);
      ctx.stroke();
    }
  }, [history, isActive, values]);

  if (!isActive && values.length === 0) {
    return null;
  }

  return (
    <div
      style={{
        padding: "12px",
        backgroundColor: "#23262e",
        borderRadius: "8px",
        marginBottom: "16px",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "12px",
        }}
      >
        <FaMicrochip style={{ color: "#1a9fff" }} />
        <span style={{ fontWeight: "bold", fontSize: "14px" }}>
          {isActive ? "CPU Load & Undervolt (Real-time)" : "Undervolt Values (Manual Mode)"}
        </span>
      </div>

      {/* Current load and values */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "8px",
          marginBottom: "12px",
        }}
      >
        {load.map((loadValue, index) => (
          <div
            key={index}
            style={{
              padding: "6px",
              backgroundColor: "#1a1d23",
              borderRadius: "4px",
              textAlign: "center",
              borderLeft: `3px solid ${getCoreColor(index)}`,
            }}
          >
            <div style={{ fontSize: "10px", color: "#8b929a" }}>
              Core {index}
            </div>
            {isActive && (
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: "bold",
                  color: getCoreColor(index),
                }}
              >
                {loadValue.toFixed(1)}%
              </div>
            )}
            <div
              style={{
                fontSize: isActive ? "11px" : "16px",
                fontWeight: isActive ? "normal" : "bold",
                color: getValueColor(index),
              }}
            >
              {values[index] || 0}mV
            </div>
          </div>
        ))}
      </div>

      {/* Graph canvas */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: `${GRAPH_HEIGHT}px`,
          backgroundColor: "#1a1d23",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <canvas
          ref={canvasRef}
          width={GRAPH_WIDTH}
          height={GRAPH_HEIGHT}
          style={{
            width: "100%",
            height: "100%",
          }}
        />

        {/* Left Y-axis labels (CPU Load %) */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "2px 4px",
            pointerEvents: "none",
          }}
        >
          {[100, 75, 50, 25, 0].map((value) => (
            <div
              key={value}
              style={{
                fontSize: "9px",
                color: "#1a9fff",
                lineHeight: "1",
              }}
            >
              {value}%
            </div>
          ))}
        </div>

        {/* Right Y-axis labels (Undervolt mV) */}
        <div
          style={{
            position: "absolute",
            top: 0,
            right: 0,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "2px 4px",
            pointerEvents: "none",
          }}
        >
          {[0, -12, -25, -37, -50].map((value) => (
            <div
              key={value}
              style={{
                fontSize: "9px",
                color: "#ff9800",
                lineHeight: "1",
                textAlign: "right",
              }}
            >
              {value}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "12px",
          marginTop: "8px",
          fontSize: "10px",
          flexWrap: "wrap",
        }}
      >
        {isActive && (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <div
                style={{
                  width: "16px",
                  height: "3px",
                  backgroundColor: "#1a9fff",
                  borderRadius: "2px",
                }}
              />
              <span style={{ color: "#8b929a" }}>Load (solid)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <div
                style={{
                  width: "16px",
                  height: "2px",
                  background: "repeating-linear-gradient(to right, #ff9800 0, #ff9800 3px, transparent 3px, transparent 5px)",
                  borderRadius: "2px",
                }}
              />
              <span style={{ color: "#8b929a" }}>Undervolt (dashed)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <div
                style={{
                  width: "3px",
                  height: "16px",
                  background: "repeating-linear-gradient(to bottom, #4caf50 0, #4caf50 5px, transparent 5px, transparent 8px)",
                  borderRadius: "2px",
                }}
              />
              <span style={{ color: "#8b929a" }}>Profile change</span>
            </div>
          </>
        )}
        {!isActive && (
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <div
              style={{
                width: "16px",
                height: "3px",
                backgroundColor: "#ff9800",
                borderRadius: "2px",
              }}
            />
            <span style={{ color: "#8b929a" }}>Manual undervolt</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadGraph;
