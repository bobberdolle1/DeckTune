/**
 * LoadGraph component for displaying real-time CPU load.
 * 
 * Feature: dynamic-mode-refactor
 * Requirements: 15.1
 * 
 * Displays per-core CPU load percentages when dynamic mode is active.
 * Shows historical data with a simple line graph visualization.
 */

import { FC, useEffect, useState, useRef } from "react";
import { FaMicrochip } from "react-icons/fa";

interface LoadGraphProps {
  /** Current per-core load values (0-100%) */
  load: number[];
  /** Whether dynamic mode is currently active */
  isActive: boolean;
}

interface LoadHistory {
  timestamp: number;
  values: number[];
}

const MAX_HISTORY_POINTS = 60; // Keep 60 data points (1 minute at 1Hz)
const GRAPH_HEIGHT = 100;
const GRAPH_WIDTH = 300;

/**
 * Get color for a specific core.
 */
const getCoreColor = (coreIndex: number): string => {
  const colors = ["#1a9fff", "#4caf50", "#ff9800", "#f44336"];
  return colors[coreIndex] || "#8b929a";
};

/**
 * LoadGraph component - displays real-time CPU load graph.
 * Requirements: 15.1
 */
export const LoadGraph: FC<LoadGraphProps> = ({ load, isActive }) => {
  const [history, setHistory] = useState<LoadHistory[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Update history when load changes
  useEffect(() => {
    if (!isActive || load.length !== 4) {
      // Clear history when not active
      setHistory([]);
      return;
    }

    setHistory((prev) => {
      const newHistory = [
        ...prev,
        {
          timestamp: Date.now(),
          values: [...load],
        },
      ];

      // Keep only the last MAX_HISTORY_POINTS
      if (newHistory.length > MAX_HISTORY_POINTS) {
        return newHistory.slice(-MAX_HISTORY_POINTS);
      }

      return newHistory;
    });
  }, [load, isActive]);

  // Draw the graph on canvas
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
      ctx.moveTo(0, y);
      ctx.lineTo(GRAPH_WIDTH, y);
      ctx.stroke();
    }

    // Draw load lines for each core
    const pointSpacing = GRAPH_WIDTH / (MAX_HISTORY_POINTS - 1);

    for (let coreIndex = 0; coreIndex < 4; coreIndex++) {
      ctx.strokeStyle = getCoreColor(coreIndex);
      ctx.lineWidth = 2;
      ctx.beginPath();

      let firstPoint = true;

      history.forEach((point, index) => {
        const x = index * pointSpacing;
        const loadValue = point.values[coreIndex] || 0;
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
  }, [history]);

  if (!isActive) {
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
          CPU Load (Real-time)
        </span>
      </div>

      {/* Current load values */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "8px",
          marginBottom: "12px",
        }}
      >
        {load.map((value, index) => (
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
            <div
              style={{
                fontSize: "16px",
                fontWeight: "bold",
                color: getCoreColor(index),
              }}
            >
              {value.toFixed(1)}%
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

        {/* Y-axis labels */}
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
                color: "#8b929a",
                lineHeight: "1",
              }}
            >
              {value}%
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "16px",
          marginTop: "8px",
          fontSize: "11px",
        }}
      >
        {[0, 1, 2, 3].map((index) => (
          <div
            key={index}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <div
              style={{
                width: "12px",
                height: "3px",
                backgroundColor: getCoreColor(index),
                borderRadius: "2px",
              }}
            />
            <span style={{ color: "#8b929a" }}>Core {index}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadGraph;
