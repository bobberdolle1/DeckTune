/**
 * FrequencyCurveChart - Visualization component for frequency-voltage curves.
 * 
 * Feature: frequency-based-wizard
 * Requirements: 5.1-5.6
 * 
 * Displays frequency-voltage curve with stable/failed points and interpolated line.
 * Highlights current operating point when frequency mode is active.
 */

import { FC, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Scatter,
  ComposedChart,
  TooltipProps,
} from "recharts";
import { FrequencyCurve, FrequencyPoint } from "../api/types";

/**
 * Props for FrequencyCurveChart component.
 * Requirements: 5.1, 5.6
 */
export interface FrequencyCurveChartProps {
  curve: FrequencyCurve;
  currentFrequency?: number; // Current operating frequency (MHz)
  width?: number;
  height?: number;
}

/**
 * Custom tooltip for displaying point details.
 * Requirements: 5.5
 */
const CustomTooltip: FC<TooltipProps<number, string>> = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div
      style={{
        background: "rgba(30, 30, 30, 0.95)",
        border: "1px solid #1a9fff",
        borderRadius: "6px",
        padding: "10px",
        fontSize: "11px",
      }}
    >
      <div style={{ color: "#fff", fontWeight: "bold", marginBottom: "6px" }}>
        Frequency Point
      </div>
      <div style={{ color: "#8b929a", marginBottom: "3px" }}>
        Frequency: <span style={{ color: "#fff" }}>{data.frequency_mhz} MHz</span>
      </div>
      <div style={{ color: "#8b929a", marginBottom: "3px" }}>
        Voltage: <span style={{ color: "#fff" }}>{data.voltage_mv} mV</span>
      </div>
      {data.stable !== undefined && (
        <div style={{ color: "#8b929a" }}>
          Status:{" "}
          <span style={{ color: data.stable ? "#4caf50" : "#f44336" }}>
            {data.stable ? "Stable" : "Failed"}
          </span>
        </div>
      )}
      {data.isCurrent && (
        <div style={{ color: "#1a9fff", fontWeight: "bold", marginTop: "6px" }}>
          ⚡ Current Operating Point
        </div>
      )}
    </div>
  );
};

/**
 * Main FrequencyCurveChart component.
 * Requirements: 5.1-5.6
 */
export const FrequencyCurveChart: FC<FrequencyCurveChartProps> = ({
  curve,
  currentFrequency,
  width,
  height = 300,
}) => {
  /**
   * Separate stable and failed points for visualization.
   * Requirements: 5.2, 5.4
   * 
   * Property 17: Stable point filtering in visualization
   * Property 18: Failed point separation in visualization
   */
  const { stablePoints, failedPoints, interpolatedLine, currentPoint } = useMemo(() => {
    // Filter stable points - Property 17
    const stable = curve.points.filter((p) => p.stable);
    
    // Filter failed points - Property 18
    const failed = curve.points.filter((p) => !p.stable);

    // Create interpolated line data - Requirement 5.3
    // Generate points every 50 MHz for smooth curve
    const minFreq = Math.min(...curve.points.map((p) => p.frequency_mhz));
    const maxFreq = Math.max(...curve.points.map((p) => p.frequency_mhz));
    const interpolated: Array<{ frequency_mhz: number; voltage_mv: number }> = [];

    for (let freq = minFreq; freq <= maxFreq; freq += 50) {
      const voltage = interpolateVoltage(curve.points, freq);
      interpolated.push({ frequency_mhz: freq, voltage_mv: voltage });
    }

    // Find current operating point - Requirement 5.6
    let current: (FrequencyPoint & { isCurrent: boolean }) | null = null;
    if (currentFrequency !== undefined) {
      const voltage = interpolateVoltage(curve.points, currentFrequency);
      current = {
        frequency_mhz: currentFrequency,
        voltage_mv: voltage,
        stable: true,
        test_duration: 0,
        timestamp: Date.now() / 1000,
        isCurrent: true,
      };
    }

    return {
      stablePoints: stable,
      failedPoints: failed,
      interpolatedLine: interpolated,
      currentPoint: current ? [current] : [],
    };
  }, [curve, currentFrequency]);

  return (
    <div style={{ width: "100%", height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#3d4450" />
          
          {/* X-axis: Frequency (MHz) - Requirement 5.1 */}
          <XAxis
            dataKey="frequency_mhz"
            type="number"
            domain={["dataMin", "dataMax"]}
            label={{
              value: "Frequency (MHz)",
              position: "insideBottom",
              offset: -5,
              style: { fill: "#8b929a", fontSize: "11px" },
            }}
            tick={{ fill: "#8b929a", fontSize: "10px" }}
            stroke="#8b929a"
          />
          
          {/* Y-axis: Voltage (mV) - Requirement 5.1 */}
          <YAxis
            dataKey="voltage_mv"
            type="number"
            domain={["dataMin - 5", "dataMax + 5"]}
            label={{
              value: "Voltage Offset (mV)",
              angle: -90,
              position: "insideLeft",
              style: { fill: "#8b929a", fontSize: "11px" },
            }}
            tick={{ fill: "#8b929a", fontSize: "10px" }}
            stroke="#8b929a"
          />
          
          {/* Tooltip - Requirement 5.5 */}
          <Tooltip content={<CustomTooltip />} />
          
          {/* Legend */}
          <Legend
            wrapperStyle={{ fontSize: "11px", color: "#8b929a" }}
            iconType="circle"
          />

          {/* Interpolated curve line - Requirement 5.3 */}
          <Line
            data={interpolatedLine}
            type="monotone"
            dataKey="voltage_mv"
            stroke="#1a9fff"
            strokeWidth={2}
            dot={false}
            name="Interpolated Curve"
            isAnimationActive={false}
          />

          {/* Stable points - Requirement 5.2 */}
          <Scatter
            data={stablePoints}
            dataKey="voltage_mv"
            fill="#4caf50"
            name="Stable Points"
            shape="circle"
          />

          {/* Failed points - Requirement 5.4 */}
          {failedPoints.length > 0 && (
            <Scatter
              data={failedPoints}
              dataKey="voltage_mv"
              fill="#f44336"
              name="Failed Points"
              shape="cross"
            />
          )}

          {/* Current operating point - Requirement 5.6 */}
          {currentPoint.length > 0 && (
            <Scatter
              data={currentPoint}
              dataKey="voltage_mv"
              fill="#ff9800"
              name="Current Point"
              shape="star"
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Linear interpolation for voltage at a given frequency.
 * Requirements: 1.5, 2.2
 * 
 * Implements the same interpolation logic as the backend.
 */
function interpolateVoltage(points: FrequencyPoint[], targetFreq: number): number {
  if (points.length === 0) return 0;
  if (points.length === 1) return points[0].voltage_mv;

  // Sort points by frequency
  const sorted = [...points].sort((a, b) => a.frequency_mhz - b.frequency_mhz);

  // Boundary clamping - Requirement 2.4
  if (targetFreq <= sorted[0].frequency_mhz) {
    return sorted[0].voltage_mv;
  }
  if (targetFreq >= sorted[sorted.length - 1].frequency_mhz) {
    return sorted[sorted.length - 1].voltage_mv;
  }

  // Find surrounding points for interpolation
  for (let i = 0; i < sorted.length - 1; i++) {
    const p1 = sorted[i];
    const p2 = sorted[i + 1];

    if (targetFreq >= p1.frequency_mhz && targetFreq <= p2.frequency_mhz) {
      // Linear interpolation - Requirement 1.5, 2.2
      const ratio =
        (targetFreq - p1.frequency_mhz) / (p2.frequency_mhz - p1.frequency_mhz);
      return Math.round(p1.voltage_mv + ratio * (p2.voltage_mv - p1.voltage_mv));
    }
  }

  // Fallback (should not reach here)
  return sorted[0].voltage_mv;
}

export default FrequencyCurveChart;
