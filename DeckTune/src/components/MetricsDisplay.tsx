/**
 * MetricsDisplay component for real-time core metrics visualization.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 3.2, 3.3, 3.4
 * 
 * Displays real-time metrics for a CPU core:
 * - CPU Load (percentage)
 * - Voltage Offset (millivolts)
 * - Frequency (megahertz)
 * - Temperature (Celsius)
 * 
 * Includes time-series graph with FIFO buffer (max 60 points).
 * Updates every 500ms when dynamic mode is active.
 */

import React, { FC, useState, useEffect, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { CoreMetrics } from "../types/DynamicMode";

/**
 * Props for MetricsDisplay component.
 * Requirements: 3.2
 */
interface MetricsDisplayProps {
  /** Current metrics for the core */
  metrics: CoreMetrics;
}

/**
 * Historical data point for time-series graph.
 */
interface HistoricalDataPoint {
  timestamp: number;
  load: number;
  voltage: number;
  frequency: number;
  temperature: number;
}

/**
 * Maximum number of data points in the FIFO buffer.
 * Requirements: 3.4
 */
const MAX_DATA_POINTS = 60;

/**
 * MetricsDisplay component.
 * Requirements: 3.2, 3.3, 3.4
 * 
 * Property 4: Metrics display completeness
 * For any CoreMetrics object received, the display SHALL contain all four 
 * metric values: CPULoad, VoltageOffset, frequency, and temperature.
 * 
 * Property 5: Metrics buffer FIFO limit
 * For any sequence of CoreMetrics updates, the real-time metrics graph buffer 
 * SHALL never exceed 60 data points, removing the oldest point when the limit 
 * is reached.
 */
export const MetricsDisplay: FC<MetricsDisplayProps> = ({ metrics }) => {
  // Historical data buffer with FIFO behavior
  // Requirements: 3.3, 3.4
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  
  /**
   * Update historical data buffer when new metrics arrive.
   * Implements FIFO: removes oldest point when buffer exceeds 60 points.
   * Requirements: 3.3, 3.4
   * 
   * Property 5: Metrics buffer FIFO limit
   */
  useEffect(() => {
    setHistoricalData((prev) => {
      const newPoint: HistoricalDataPoint = {
        timestamp: metrics.timestamp,
        load: metrics.load,
        voltage: metrics.voltage,
        frequency: metrics.frequency,
        temperature: metrics.temperature,
      };
      
      // Add new point
      const updated = [...prev, newPoint];
      
      // Remove oldest point if buffer exceeds limit
      // Requirements: 3.4
      if (updated.length > MAX_DATA_POINTS) {
        return updated.slice(updated.length - MAX_DATA_POINTS);
      }
      
      return updated;
    });
  }, [metrics]);
  
  /**
   * Format timestamp for display (relative time in seconds).
   */
  const formatTimestamp = (timestamp: number): string => {
    if (historicalData.length === 0) return "0s";
    const firstTimestamp = historicalData[0].timestamp;
    const elapsed = Math.floor((timestamp - firstTimestamp) / 1000);
    return `${elapsed}s`;
  };
  
  /**
   * Custom tooltip for the time-series graph.
   */
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: "#1a1d24",
            border: "1px solid #3d4450",
            borderRadius: "4px",
            padding: "8px 12px",
            fontSize: "10px",
            color: "#fff",
          }}
        >
          <div style={{ marginBottom: "4px", fontWeight: "bold" }}>
            {formatTimestamp(data.timestamp)}
          </div>
          <div style={{ color: "#4caf50" }}>Load: {data.load.toFixed(1)}%</div>
          <div style={{ color: "#1a9fff" }}>Voltage: {data.voltage}mV</div>
          <div style={{ color: "#ff9800" }}>Freq: {data.frequency}MHz</div>
          <div style={{ color: "#f44336" }}>Temp: {data.temperature.toFixed(1)}°C</div>
        </div>
      );
    }
    return null;
  };
  
  return (
    <div style={{ width: "100%", maxWidth: "100%" }}>
      {/* Current Metrics Grid - Compact for QAM */}
      {/* Requirements: 3.2 */}
      {/* Property 4: Metrics display completeness */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "6px",
          marginBottom: "12px",
        }}
      >
        {/* CPU Load */}
        <div
          style={{
            padding: "8px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            border: "1px solid #2a2d34",
            transition: "all 0.3s ease",
          }}
        >
          <div
            style={{
              fontSize: "9px",
              color: "#8b929a",
              marginBottom: "2px",
              fontWeight: "bold",
            }}
          >
            CPU LOAD
          </div>
          <div
            style={{
              fontSize: "16px",
              color: "#4caf50",
              fontWeight: "bold",
              transition: "color 0.3s ease",
            }}
          >
            {metrics.load.toFixed(1)}
            <span style={{ fontSize: "10px", marginLeft: "2px" }}>%</span>
          </div>
        </div>
        
        {/* Voltage Offset */}
        <div
          style={{
            padding: "8px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            border: "1px solid #2a2d34",
            transition: "all 0.3s ease",
          }}
        >
          <div
            style={{
              fontSize: "9px",
              color: "#8b929a",
              marginBottom: "2px",
              fontWeight: "bold",
            }}
          >
            VOLTAGE
          </div>
          <div
            style={{
              fontSize: "16px",
              color: "#1a9fff",
              fontWeight: "bold",
              transition: "color 0.3s ease",
            }}
          >
            {metrics.voltage}
            <span style={{ fontSize: "10px", marginLeft: "2px" }}>mV</span>
          </div>
        </div>
        
        {/* Frequency */}
        <div
          style={{
            padding: "8px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            border: "1px solid #2a2d34",
            transition: "all 0.3s ease",
          }}
        >
          <div
            style={{
              fontSize: "9px",
              color: "#8b929a",
              marginBottom: "2px",
              fontWeight: "bold",
            }}
          >
            FREQUENCY
          </div>
          <div
            style={{
              fontSize: "16px",
              color: "#ff9800",
              fontWeight: "bold",
              transition: "color 0.3s ease",
            }}
          >
            {metrics.frequency}
            <span style={{ fontSize: "10px", marginLeft: "2px" }}>MHz</span>
          </div>
        </div>
        
        {/* Temperature */}
        <div
          style={{
            padding: "8px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            border: "1px solid #2a2d34",
            transition: "all 0.3s ease",
          }}
        >
          <div
            style={{
              fontSize: "9px",
              color: "#8b929a",
              marginBottom: "2px",
              fontWeight: "bold",
            }}
          >
            TEMP
          </div>
          <div
            style={{
              fontSize: "16px",
              color: "#f44336",
              fontWeight: "bold",
              transition: "color 0.3s ease",
            }}
          >
            {metrics.temperature.toFixed(1)}
            <span style={{ fontSize: "10px", marginLeft: "2px" }}>°C</span>
          </div>
        </div>
      </div>
      
      {/* Time-Series Graph - Compact for QAM */}
      {/* Requirements: 3.3, 3.4 */}
      {/* UI Polish: Smooth transitions for graph updates */}
      {historicalData.length > 0 && (
        <div
          style={{
            backgroundColor: "#0d0f12",
            borderRadius: "4px",
            border: "1px solid #2a2d34",
            padding: "8px",
            transition: "opacity 0.3s ease",
          }}
        >
          <div
            style={{
              fontSize: "9px",
              color: "#8b929a",
              marginBottom: "6px",
              fontWeight: "bold",
            }}
          >
            HISTORY ({historicalData.length}/{MAX_DATA_POINTS})
          </div>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart
              data={historicalData}
              margin={{ top: 5, right: 5, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2d34" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatTimestamp}
                stroke="#5a5d64"
                style={{ fontSize: "8px" }}
                tick={{ fill: "#5a5d64" }}
              />
              <YAxis
                yAxisId="left"
                stroke="#5a5d64"
                style={{ fontSize: "8px" }}
                tick={{ fill: "#5a5d64" }}
                width={35}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#5a5d64"
                style={{ fontSize: "8px" }}
                tick={{ fill: "#5a5d64" }}
                width={35}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: "8px" }}
                iconType="line"
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="load"
                stroke="#4caf50"
                strokeWidth={1.5}
                dot={false}
                name="Load"
                animationDuration={300}
                animationEasing="ease-in-out"
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="voltage"
                stroke="#1a9fff"
                strokeWidth={1.5}
                dot={false}
                name="Volt"
                animationDuration={300}
                animationEasing="ease-in-out"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="frequency"
                stroke="#ff9800"
                strokeWidth={1.5}
                dot={false}
                name="Freq"
                animationDuration={300}
                animationEasing="ease-in-out"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="temperature"
                stroke="#f44336"
                strokeWidth={1.5}
                dot={false}
                name="Temp"
                animationDuration={300}
                animationEasing="ease-in-out"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      
      {/* No data message - Compact */}
      {historicalData.length === 0 && (
        <div
          style={{
            padding: "16px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            textAlign: "center",
            color: "#8b929a",
            fontSize: "10px",
            animation: "fadeIn 0.5s ease",
          }}
        >
          Waiting for metrics...
        </div>
      )}
      
      {/* CSS Animations */}
      <style>
        {`
          @keyframes fadeIn {
            from {
              opacity: 0;
            }
            to {
              opacity: 1;
            }
          }
        `}
      </style>
    </div>
  );
};

export default MetricsDisplay;
