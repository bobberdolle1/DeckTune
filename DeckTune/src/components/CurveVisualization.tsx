/**
 * CurveVisualization component for displaying voltage curves.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
 * 
 * Renders an interactive voltage curve graph showing:
 * - Voltage offset vs CPU load relationship
 * - Threshold marker indicating transition point
 * - Current operating point (if metrics available)
 * - Grid lines, axis labels, and legend
 * 
 * Updates within 100ms of configuration changes.
 */

import React, { FC, useState, useMemo } from "react";
import { CoreConfig, CoreMetrics, CurvePoint } from "../types/DynamicMode";

/**
 * Props for CurveVisualization component.
 * Requirements: 2.1, 2.2
 */
interface CurveVisualizationProps {
  /** Core configuration defining the voltage curve */
  config: CoreConfig;
  
  /** Optional current metrics to display operating point */
  currentMetrics?: CoreMetrics;
}

/**
 * Calculate voltage curve points based on configuration.
 * Implements piecewise linear interpolation.
 * 
 * Requirements: 2.4, 2.5
 * 
 * Formula:
 * - voltage(load) = min_mv if load <= threshold
 * - voltage(load) = min_mv + (max_mv - min_mv) * (load - threshold) / (100 - threshold) if load > threshold
 * 
 * @param config Core configuration
 * @returns Array of 101 curve points (load 0-100)
 */
const calculateCurvePoints = (config: CoreConfig): CurvePoint[] => {
  const points: CurvePoint[] = [];
  const { min_mv, max_mv, threshold } = config;
  
  for (let load = 0; load <= 100; load++) {
    let voltage: number;
    
    if (load <= threshold) {
      // Below threshold: constant at min_mv
      // Requirements: 2.4
      voltage = min_mv;
    } else {
      // Above threshold: linear interpolation
      // Requirements: 2.5
      voltage = min_mv + (max_mv - min_mv) * (load - threshold) / (100 - threshold);
    }
    
    points.push({ load, voltage });
  }
  
  return points;
};

/**
 * CurveVisualization component.
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
 */
export const CurveVisualization: FC<CurveVisualizationProps> = ({
  config,
  currentMetrics,
}) => {
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  
  // Calculate curve points
  // Memoized to update within 100ms of config changes
  // Requirements: 2.2
  const curvePoints = useMemo(() => calculateCurvePoints(config), [config]);
  
  // Chart dimensions - optimized for QAM (max width ~400px)
  const width = 340;  // Fits QAM width with padding
  const height = 160; // Compact height for QAM
  const padding = { top: 15, right: 15, bottom: 35, left: 45 };
  
  // Axis ranges
  // X-axis: CPU Load 0-100%
  // Y-axis: Voltage Offset -100 to 0 mV
  // Requirements: 2.1
  const xMin = 0;
  const xMax = 100;
  const yMin = -100;
  const yMax = 0;
  
  // Scaling functions
  const xScale = (x: number) =>
    padding.left + ((x - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
  
  const yScale = (y: number) =>
    height - padding.bottom - ((y - yMin) / (yMax - yMin)) * (height - padding.top - padding.bottom);
  
  // Handle point hover for tooltip
  const handlePointHover = (index: number, event: React.MouseEvent) => {
    setHoveredPoint(index);
    const rect = (event.currentTarget as SVGElement).getBoundingClientRect();
    setTooltipPos({ x: event.clientX - rect.left, y: event.clientY - rect.top });
  };
  
  return (
    <div style={{ width: "100%", maxWidth: "100%", overflow: "hidden" }}>
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        style={{
          backgroundColor: "#0d0f12",
          borderRadius: "4px",
          border: "1px solid #2a2d34",
          maxWidth: "100%",
        }}
      >
        {/* Grid lines - Y-axis (voltage) */}
        {/* Requirements: 2.3 */}
        {[-100, -75, -50, -25, 0].map((voltage) => (
          <g key={`y-${voltage}`}>
            <line
              x1={padding.left}
              y1={yScale(voltage)}
              x2={width - padding.right}
              y2={yScale(voltage)}
              stroke="#2a2d34"
              strokeWidth={1}
              strokeDasharray="2,2"
            />
            <text
              x={padding.left - 5}
              y={yScale(voltage) + 3}
              fontSize="9"
              fill="#5a5d64"
              textAnchor="end"
            >
              {voltage}
            </text>
          </g>
        ))}
        
        {/* Grid lines - X-axis (CPU load) */}
        {/* Requirements: 2.3 */}
        {[0, 25, 50, 75, 100].map((load) => (
          <line
            key={`x-${load}`}
            x1={xScale(load)}
            y1={padding.top}
            x2={xScale(load)}
            y2={height - padding.bottom}
            stroke="#2a2d34"
            strokeWidth={1}
            strokeDasharray="2,2"
          />
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
        
        {/* Threshold marker line */}
        {/* Requirements: 2.3 */}
        <line
          x1={xScale(config.threshold)}
          y1={padding.top}
          x2={xScale(config.threshold)}
          y2={height - padding.bottom}
          stroke="#ff9800"
          strokeWidth={2}
          strokeDasharray="4,4"
        />
        
        {/* Threshold label */}
        <text
          x={xScale(config.threshold)}
          y={padding.top - 5}
          fontSize="9"
          fill="#ff9800"
          textAnchor="middle"
          fontWeight="bold"
        >
          Threshold: {config.threshold}%
        </text>
        
        {/* Voltage curve line */}
        {/* Requirements: 2.1, 2.4, 2.5 */}
        <defs>
          <linearGradient id="voltageGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4caf50" />
            <stop offset="50%" stopColor="#1a9fff" />
            <stop offset="100%" stopColor="#9c27b0" />
          </linearGradient>
        </defs>
        
        <polyline
          points={curvePoints
            .map((point) => `${xScale(point.load)},${yScale(point.voltage)}`)
            .join(" ")}
          fill="none"
          stroke="url(#voltageGradient)"
          strokeWidth={2}
        />
        
        {/* Sample points for interaction (every 10%) */}
        {curvePoints
          .filter((_, i) => i % 10 === 0)
          .map((point, i) => (
            <circle
              key={`point-${i}`}
              cx={xScale(point.load)}
              cy={yScale(point.voltage)}
              r={hoveredPoint === i ? 5 : 3}
              fill="#1a9fff"
              stroke="#fff"
              strokeWidth={hoveredPoint === i ? 2 : 1}
              style={{ cursor: "pointer", transition: "all 0.2s" }}
              onMouseEnter={(e) => handlePointHover(i, e)}
              onMouseLeave={() => setHoveredPoint(null)}
            />
          ))}
        
        {/* Current operating point marker */}
        {/* Requirements: 2.3 */}
        {currentMetrics && (
          <g>
            <circle
              cx={xScale(currentMetrics.load)}
              cy={yScale(currentMetrics.voltage)}
              r={6}
              fill="#f44336"
              stroke="#fff"
              strokeWidth={2}
            />
            <circle
              cx={xScale(currentMetrics.load)}
              cy={yScale(currentMetrics.voltage)}
              r={10}
              fill="none"
              stroke="#f44336"
              strokeWidth={2}
              opacity={0.5}
            >
              <animate
                attributeName="r"
                from="6"
                to="12"
                dur="1s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                from="0.5"
                to="0"
                dur="1s"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        )}
        
        {/* Axis labels */}
        {/* Requirements: 2.3 */}
        <text
          x={width / 2}
          y={height - 5}
          fontSize="11"
          fill="#8b929a"
          textAnchor="middle"
          fontWeight="bold"
        >
          CPU Load (%)
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
          Voltage Offset (mV)
        </text>
        
        {/* Legend */}
        {/* Requirements: 2.3 */}
        <g transform={`translate(${width - 110}, ${height - padding.bottom + 25})`}>
          <line x1={0} y1={0} x2={15} y2={0} stroke="url(#voltageGradient)" strokeWidth={2} />
          <text x={20} y={3} fontSize="9" fill="#8b929a">Voltage Curve</text>
          
          <line x1={0} y1={12} x2={15} y2={12} stroke="#ff9800" strokeWidth={2} strokeDasharray="4,4" />
          <text x={20} y={15} fontSize="9" fill="#8b929a">Threshold</text>
          
          {currentMetrics && (
            <>
              <circle cx={7} cy={24} r={4} fill="#f44336" stroke="#fff" strokeWidth={1} />
              <text x={20} y={27} fontSize="9" fill="#8b929a">Current</text>
            </>
          )}
        </g>
      </svg>
      
      {/* Tooltip */}
      {hoveredPoint !== null && (
        <div
          style={{
            position: "absolute",
            left: Math.min(tooltipPos.x + 10, 300), // Prevent overflow
            top: tooltipPos.y - 40,
            backgroundColor: "#1a1d24",
            border: "1px solid #3d4450",
            borderRadius: "4px",
            padding: "4px 8px",
            fontSize: "9px",
            color: "#fff",
            pointerEvents: "none",
            zIndex: 1000,
            boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
            whiteSpace: "nowrap",
          }}
        >
          <div>
            <strong>Load: {curvePoints[hoveredPoint * 10].load}%</strong>
          </div>
          <div>Voltage: {curvePoints[hoveredPoint * 10].voltage.toFixed(1)}mV</div>
        </div>
      )}
    </div>
  );
};

export default CurveVisualization;
