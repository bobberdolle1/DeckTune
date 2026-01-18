/**
 * DynamicModeVisualization component for Expert Mode.
 * 
 * Displays real-time visualization of dynamic undervolt adaptation:
 * - Load vs Undervolt curve for each strategy
 * - Current operating point
 * - Per-core load and undervolt values
 * - Compact design optimized for QAM (310px width)
 */

import { FC } from "react";
import { FaMicrochip, FaBolt } from "react-icons/fa";

interface DynamicModeVisualizationProps {
  /** Current strategy: conservative, balanced, aggressive */
  strategy: string;
  /** Current per-core load values (0-100%) */
  load: number[];
  /** Current per-core undervolt values (mV) */
  values: number[];
  /** Whether dynamic mode is running */
  isActive: boolean;
  /** Simple mode enabled */
  simpleMode: boolean;
  /** Simple mode value */
  simpleValue: number;
}

// Graph dimensions optimized for QAM
const GRAPH_WIDTH = 280;
const GRAPH_HEIGHT = 140;
const MARGIN = { top: 20, right: 25, bottom: 25, left: 35 };
const INNER_WIDTH = GRAPH_WIDTH - MARGIN.left - MARGIN.right;
const INNER_HEIGHT = GRAPH_HEIGHT - MARGIN.top - MARGIN.bottom;

// Load and undervolt ranges
const LOAD_MIN = 0;
const LOAD_MAX = 100;
const VOLT_MIN = -100;
const VOLT_MAX = 0;

/**
 * Strategy curve definitions (load% -> undervolt mV)
 */
const STRATEGY_CURVES = {
  conservative: [
    { load: 0, volt: -30 },
    { load: 20, volt: -25 },
    { load: 40, volt: -20 },
    { load: 60, volt: -15 },
    { load: 80, volt: -10 },
    { load: 100, volt: -5 },
  ],
  balanced: [
    { load: 0, volt: -35 },
    { load: 20, volt: -30 },
    { load: 40, volt: -25 },
    { load: 60, volt: -20 },
    { load: 80, volt: -12 },
    { load: 100, volt: -5 },
  ],
  aggressive: [
    { load: 0, volt: -45 },
    { load: 20, volt: -38 },
    { load: 40, volt: -30 },
    { load: 60, volt: -22 },
    { load: 80, volt: -15 },
    { load: 100, volt: -8 },
  ],
};

/**
 * Convert load to X coordinate
 */
const loadToX = (load: number): number => {
  const normalized = (load - LOAD_MIN) / (LOAD_MAX - LOAD_MIN);
  return MARGIN.left + normalized * INNER_WIDTH;
};

/**
 * Convert undervolt to Y coordinate (inverted - more negative at bottom)
 */
const voltToY = (volt: number): number => {
  const normalized = (volt - VOLT_MIN) / (VOLT_MAX - VOLT_MIN);
  return MARGIN.top + INNER_HEIGHT - normalized * INNER_HEIGHT;
};

/**
 * Generate SVG path for strategy curve
 */
const generateCurvePath = (strategy: string): string => {
  const curve = STRATEGY_CURVES[strategy as keyof typeof STRATEGY_CURVES] || STRATEGY_CURVES.balanced;
  
  let path = `M ${loadToX(curve[0].load)} ${voltToY(curve[0].volt)}`;
  
  for (let i = 1; i < curve.length; i++) {
    path += ` L ${loadToX(curve[i].load)} ${voltToY(curve[i].volt)}`;
  }
  
  return path;
};

/**
 * Get strategy color
 */
const getStrategyColor = (strategy: string): string => {
  switch (strategy) {
    case "conservative": return "#4caf50";
    case "balanced": return "#1a9fff";
    case "aggressive": return "#ff9800";
    default: return "#1a9fff";
  }
};

/**
 * Get core color
 */
const getCoreColor = (coreIndex: number): string => {
  const colors = ["#1a9fff", "#4caf50", "#ff9800", "#f44336"];
  return colors[coreIndex] || "#8b929a";
};

/**
 * DynamicModeVisualization component
 */
export const DynamicModeVisualization: FC<DynamicModeVisualizationProps> = ({
  strategy,
  load,
  values,
  isActive,
  simpleMode,
  simpleValue,
}) => {
  const strategyColor = getStrategyColor(strategy);
  const avgLoad = load.length > 0 ? load.reduce((sum, l) => sum + l, 0) / load.length : 0;
  const avgVolt = values.length > 0 ? values.reduce((sum, v) => sum + v, 0) / values.length : 0;

  return (
    <div style={{
      background: "linear-gradient(135deg, #1a1d23 0%, #23262e 100%)",
      borderRadius: "10px",
      padding: "10px",
      border: "1px solid rgba(26, 159, 255, 0.2)",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
    }}>
      {/* Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "8px",
      }}>
        <div style={{
          fontSize: "11px",
          fontWeight: "bold",
          color: "#e0e0e0",
          display: "flex",
          alignItems: "center",
          gap: "6px",
        }}>
          <FaBolt style={{ color: strategyColor }} />
          <span>Load → Undervolt Curve</span>
        </div>
        <div style={{
          fontSize: "9px",
          color: strategyColor,
          fontWeight: "bold",
          textTransform: "capitalize",
        }}>
          {strategy}
        </div>
      </div>

      {/* Graph */}
      <svg
        width={GRAPH_WIDTH}
        height={GRAPH_HEIGHT}
        style={{ display: "block" }}
      >
        {/* Definitions */}
        <defs>
          <linearGradient id="curveGradientDynamic" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={strategyColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor={strategyColor} stopOpacity="0.05" />
          </linearGradient>
          <filter id="glowDynamic">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Grid */}
        <g stroke="#3d4450" strokeWidth="1" opacity="0.5">
          {/* Horizontal grid (undervolt) */}
          {[0, -25, -50, -75, -100].map(volt => (
            <line
              key={`h-${volt}`}
              x1={MARGIN.left}
              y1={voltToY(volt)}
              x2={MARGIN.left + INNER_WIDTH}
              y2={voltToY(volt)}
              strokeDasharray={volt === 0 ? "none" : "2,2"}
            />
          ))}
          {/* Vertical grid (load) */}
          {[0, 25, 50, 75, 100].map(load => (
            <line
              key={`v-${load}`}
              x1={loadToX(load)}
              y1={MARGIN.top}
              x2={loadToX(load)}
              y2={MARGIN.top + INNER_HEIGHT}
              strokeDasharray="2,2"
            />
          ))}
        </g>

        {/* Axis labels */}
        <g fill="#b0b0b0" fontSize="9" fontWeight="500">
          {/* Y-axis (undervolt) */}
          {[0, -25, -50, -75, -100].map(volt => (
            <text
              key={`y-${volt}`}
              x={MARGIN.left - 5}
              y={voltToY(volt) + 3}
              textAnchor="end"
            >
              {volt}
            </text>
          ))}
          {/* X-axis (load) */}
          {[0, 25, 50, 75, 100].map(load => (
            <text
              key={`x-${load}`}
              x={loadToX(load)}
              y={MARGIN.top + INNER_HEIGHT + 15}
              textAnchor="middle"
            >
              {load}%
            </text>
          ))}
        </g>

        {/* Axis titles */}
        <g fill="#8b929a" fontSize="9" fontWeight="600">
          <text
            x={10}
            y={MARGIN.top + INNER_HEIGHT / 2}
            textAnchor="middle"
            transform={`rotate(-90, 10, ${MARGIN.top + INNER_HEIGHT / 2})`}
          >
            mV
          </text>
          <text
            x={MARGIN.left + INNER_WIDTH / 2}
            y={GRAPH_HEIGHT - 5}
            textAnchor="middle"
          >
            CPU Load (%)
          </text>
        </g>

        {/* Strategy curve fill */}
        <path
          d={`${generateCurvePath(strategy)} L ${loadToX(100)} ${voltToY(VOLT_MIN)} L ${loadToX(0)} ${voltToY(VOLT_MIN)} Z`}
          fill="url(#curveGradientDynamic)"
        />

        {/* Strategy curve line */}
        <path
          d={generateCurvePath(strategy)}
          fill="none"
          stroke={strategyColor}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#glowDynamic)"
        />

        {/* Current operating point (if active) */}
        {isActive && load.length > 0 && values.length > 0 && (
          <g>
            {/* Average point */}
            <circle
              cx={loadToX(avgLoad)}
              cy={voltToY(avgVolt)}
              r="6"
              fill={strategyColor}
              stroke="#fff"
              strokeWidth="2"
              filter="url(#glowDynamic)"
            >
              <animate
                attributeName="r"
                values="6;8;6"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>

            {/* Per-core points (smaller) */}
            {!simpleMode && load.map((coreLoad, idx) => (
              <circle
                key={idx}
                cx={loadToX(coreLoad)}
                cy={voltToY(values[idx])}
                r="3"
                fill={getCoreColor(idx)}
                stroke="#fff"
                strokeWidth="1"
                opacity="0.8"
              />
            ))}

            {/* Label */}
            <rect
              x={loadToX(avgLoad) - 30}
              y={voltToY(avgVolt) - 20}
              width="60"
              height="14"
              rx="3"
              fill="rgba(0, 0, 0, 0.8)"
            />
            <text
              x={loadToX(avgLoad)}
              y={voltToY(avgVolt) - 10}
              fill="#fff"
              fontSize="9"
              fontWeight="bold"
              textAnchor="middle"
            >
              {Math.round(avgLoad)}% / {Math.round(avgVolt)}mV
            </text>
          </g>
        )}
      </svg>

      {/* Per-core metrics (compact) */}
      {isActive && load.length > 0 && values.length > 0 && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "4px",
          marginTop: "8px",
        }}>
          {load.map((coreLoad, idx) => (
            <div
              key={idx}
              style={{
                padding: "6px 4px",
                backgroundColor: "rgba(0, 0, 0, 0.3)",
                borderRadius: "6px",
                border: `1px solid ${getCoreColor(idx)}`,
                textAlign: "center",
              }}
            >
              <div style={{
                fontSize: "8px",
                color: "#8b929a",
                marginBottom: "2px",
              }}>
                C{idx}
              </div>
              <div style={{
                fontSize: "10px",
                fontWeight: "bold",
                color: getCoreColor(idx),
              }}>
                {Math.round(coreLoad)}%
              </div>
              <div style={{
                fontSize: "9px",
                color: "#e0e0e0",
              }}>
                {values[idx]}mV
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Simple mode indicator */}
      {simpleMode && (
        <div style={{
          marginTop: "8px",
          padding: "6px",
          backgroundColor: "rgba(26, 159, 255, 0.1)",
          borderRadius: "6px",
          fontSize: "9px",
          color: "#1a9fff",
          textAlign: "center",
          border: "1px solid rgba(26, 159, 255, 0.2)",
        }}>
          Simple Mode: {simpleValue}mV for all cores at low load
        </div>
      )}

      {/* Strategy description */}
      <div style={{
        marginTop: "8px",
        padding: "6px",
        backgroundColor: "rgba(0, 0, 0, 0.2)",
        borderRadius: "6px",
        fontSize: "8px",
        color: "#8b929a",
        lineHeight: "1.4",
      }}>
        <strong style={{ color: strategyColor }}>
          {strategy === "conservative" && "Conservative: "}
          {strategy === "balanced" && "Balanced: "}
          {strategy === "aggressive" && "Aggressive: "}
        </strong>
        {strategy === "conservative" && "Безопасная адаптация, меньше андервольт при нагрузке"}
        {strategy === "balanced" && "Оптимальный баланс производительности и стабильности"}
        {strategy === "aggressive" && "Максимальный андервольт, быстрая адаптация"}
      </div>
    </div>
  );
};

export default DynamicModeVisualization;
