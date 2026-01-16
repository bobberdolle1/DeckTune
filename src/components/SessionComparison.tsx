/**
 * SessionComparison component for comparing two gaming sessions.
 * 
 * Feature: decktune-3.1-reliability-ux
 * Requirements: 8.6
 * 
 * Allows selecting two sessions and displays side-by-side metric comparison
 * with diff values showing improvement or regression.
 */

import React, { FC, useState, useEffect, useCallback } from "react";
import {
  FaArrowLeft,
  FaExchangeAlt,
  FaClock,
  FaThermometerHalf,
  FaBolt,
  FaBatteryFull,
  FaGamepad,
  FaArrowUp,
  FaArrowDown,
  FaMinus,
  FaSpinner,
} from "react-icons/fa";
import { Session, SessionComparison as SessionComparisonType } from "../api/types";
import { useDeckTune } from "../context";

/**
 * Format duration in seconds to human-readable string.
 */
const formatDuration = (seconds: number): string => {
  const hours = Math.floor(Math.abs(seconds) / 3600);
  const minutes = Math.floor((Math.abs(seconds) % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

/**
 * Format ISO date string to short format.
 */
const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
};

/**
 * Props for SessionComparison component.
 */
interface SessionComparisonProps {
  /** First session to compare */
  session1: Session;
  /** Second session to compare */
  session2: Session;
  /** Callback to go back to list view */
  onBack: () => void;
}

/**
 * SessionComparison component - displays side-by-side metric comparison.
 * 
 * Requirements:
 * - 8.6: Allow selecting two sessions and display side-by-side metric comparison
 */
export const SessionComparisonView: FC<SessionComparisonProps> = ({
  session1,
  session2,
  onBack,
}) => {
  const { api } = useDeckTune();
  const [comparison, setComparison] = useState<SessionComparisonType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load comparison data from backend.
   * Requirements: 8.6
   */
  const loadComparison = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.compareSessions(session1.id, session2.id);
      if (result) {
        setComparison(result);
      } else {
        setError("Failed to compare sessions");
      }
    } catch (e) {
      setError("Failed to load comparison");
      console.error("Failed to compare sessions:", e);
    } finally {
      setLoading(false);
    }
  }, [api, session1.id, session2.id]);

  useEffect(() => {
    loadComparison();
  }, [loadComparison]);

  if (loading) {
    return (
      <div style={{ 
        padding: "24px", 
        textAlign: "center", 
        color: "#8b929a" 
      }}>
        <FaSpinner className="spin" style={{ fontSize: "24px", marginBottom: "8px" }} />
        <div>Loading comparison...</div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div style={{ 
        padding: "24px", 
        textAlign: "center", 
        color: "#f44336" 
      }}>
        <div>{error || "Failed to load comparison"}</div>
        <button
          onClick={onBack}
          style={{
            marginTop: "12px",
            padding: "8px 16px",
            backgroundColor: "#23262e",
            border: "none",
            borderRadius: "4px",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Go Back
        </button>
      </div>
    );
  }

  const m1 = session1.metrics;
  const m2 = session2.metrics;
  const diff = comparison.diff;

  return (
    <div style={{ padding: "8px 0" }}>
      {/* Header with back button */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        marginBottom: "16px",
      }}>
        <button
          onClick={onBack}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "32px",
            height: "32px",
            backgroundColor: "#23262e",
            border: "none",
            borderRadius: "6px",
            color: "#8b929a",
            cursor: "pointer",
          }}
        >
          <FaArrowLeft />
        </button>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "8px",
          fontSize: "14px",
          fontWeight: "bold",
        }}>
          <FaExchangeAlt style={{ color: "#1a9fff" }} />
          <span>Session Comparison</span>
        </div>
      </div>

      {/* Session headers */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "8px",
        marginBottom: "12px",
      }}>
        <SessionHeader session={session1} label="Session 1" />
        <SessionHeader session={session2} label="Session 2" />
      </div>

      {/* Comparison metrics */}
      {m1 && m2 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {/* Duration */}
          <ComparisonRow
            icon={FaClock}
            label="Duration"
            value1={formatDuration(m1.duration_sec)}
            value2={formatDuration(m2.duration_sec)}
            diff={diff.duration_sec}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${formatDuration(d)}`}
            higherIsBetter={true}
            color="#8b929a"
          />

          {/* Average Temperature */}
          <ComparisonRow
            icon={FaThermometerHalf}
            label="Avg Temperature"
            value1={`${m1.avg_temperature_c.toFixed(1)}°C`}
            value2={`${m2.avg_temperature_c.toFixed(1)}°C`}
            diff={diff.avg_temperature_c}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${d.toFixed(1)}°C`}
            higherIsBetter={false}
            color="#ff9800"
          />

          {/* Min Temperature */}
          <ComparisonRow
            icon={FaThermometerHalf}
            label="Min Temperature"
            value1={`${m1.min_temperature_c.toFixed(1)}°C`}
            value2={`${m2.min_temperature_c.toFixed(1)}°C`}
            diff={diff.min_temperature_c}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${d.toFixed(1)}°C`}
            higherIsBetter={false}
            color="#4caf50"
          />

          {/* Max Temperature */}
          <ComparisonRow
            icon={FaThermometerHalf}
            label="Max Temperature"
            value1={`${m1.max_temperature_c.toFixed(1)}°C`}
            value2={`${m2.max_temperature_c.toFixed(1)}°C`}
            diff={diff.max_temperature_c}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${d.toFixed(1)}°C`}
            higherIsBetter={false}
            color="#f44336"
          />

          {/* Average Power */}
          <ComparisonRow
            icon={FaBolt}
            label="Avg Power"
            value1={`${m1.avg_power_w.toFixed(1)}W`}
            value2={`${m2.avg_power_w.toFixed(1)}W`}
            diff={diff.avg_power_w}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${d.toFixed(1)}W`}
            higherIsBetter={false}
            color="#ffeb3b"
          />

          {/* Battery Saved */}
          <ComparisonRow
            icon={FaBatteryFull}
            label="Battery Saved"
            value1={`${m1.estimated_battery_saved_wh.toFixed(2)}Wh`}
            value2={`${m2.estimated_battery_saved_wh.toFixed(2)}Wh`}
            diff={diff.estimated_battery_saved_wh}
            formatDiff={(d) => `${d > 0 ? "+" : ""}${d.toFixed(2)}Wh`}
            higherIsBetter={true}
            color="#4caf50"
          />
        </div>
      )}

      {/* No metrics message */}
      {(!m1 || !m2) && (
        <div style={{
          padding: "24px",
          textAlign: "center",
          color: "#8b929a",
          backgroundColor: "#23262e",
          borderRadius: "8px",
        }}>
          One or both sessions have no metrics data
        </div>
      )}
    </div>
  );
};

/**
 * Props for SessionHeader component.
 */
interface SessionHeaderProps {
  session: Session;
  label: string;
}

/**
 * Session header card for comparison view.
 */
const SessionHeader: FC<SessionHeaderProps> = ({ session, label }) => {
  return (
    <div style={{
      backgroundColor: "#23262e",
      borderRadius: "8px",
      padding: "10px",
    }}>
      <div style={{ 
        fontSize: "10px", 
        color: "#8b929a",
        marginBottom: "4px",
      }}>
        {label}
      </div>
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "6px",
        marginBottom: "4px",
      }}>
        <FaGamepad style={{ color: "#1a9fff", fontSize: "12px" }} />
        <span style={{ 
          fontSize: "12px", 
          fontWeight: "bold",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}>
          {session.game_name || "Unknown"}
        </span>
      </div>
      <div style={{ fontSize: "10px", color: "#8b929a" }}>
        {formatDate(session.start_time)}
      </div>
    </div>
  );
};

/**
 * Props for ComparisonRow component.
 */
interface ComparisonRowProps {
  icon: FC;
  label: string;
  value1: string;
  value2: string;
  diff: number;
  formatDiff: (diff: number) => string;
  higherIsBetter: boolean;
  color: string;
}

/**
 * Comparison row showing values side-by-side with diff indicator.
 */
const ComparisonRow: FC<ComparisonRowProps> = ({
  icon: Icon,
  label,
  value1,
  value2,
  diff,
  formatDiff,
  higherIsBetter,
  color,
}) => {
  // Determine if the diff is good, bad, or neutral
  const isImprovement = higherIsBetter ? diff > 0 : diff < 0;
  const isRegression = higherIsBetter ? diff < 0 : diff > 0;
  const isNeutral = Math.abs(diff) < 0.01;

  const getDiffColor = () => {
    if (isNeutral) return "#8b929a";
    if (isImprovement) return "#4caf50";
    return "#f44336";
  };

  const getDiffIcon = () => {
    if (isNeutral) return FaMinus;
    if (isImprovement) return FaArrowUp;
    return FaArrowDown;
  };

  const DiffIcon = getDiffIcon();

  return (
    <div style={{
      backgroundColor: "#23262e",
      borderRadius: "8px",
      padding: "10px 12px",
    }}>
      {/* Label row */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "6px",
        marginBottom: "8px",
      }}>
        <span style={{ color, fontSize: "12px" }}><Icon /></span>
        <span style={{ fontSize: "12px", color: "#8b929a" }}>{label}</span>
      </div>

      {/* Values row */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr auto 1fr",
        gap: "8px",
        alignItems: "center",
      }}>
        {/* Session 1 value */}
        <div style={{
          fontSize: "14px",
          fontWeight: "bold",
          textAlign: "center",
        }}>
          {value1}
        </div>

        {/* Diff indicator */}
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "2px",
          padding: "4px 8px",
          backgroundColor: "#1a1d23",
          borderRadius: "4px",
          minWidth: "70px",
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
            color: getDiffColor(),
            fontSize: "11px",
            fontWeight: "bold",
          }}>
            <DiffIcon style={{ fontSize: "10px" }} />
            <span>{formatDiff(diff)}</span>
          </div>
        </div>

        {/* Session 2 value */}
        <div style={{
          fontSize: "14px",
          fontWeight: "bold",
          textAlign: "center",
        }}>
          {value2}
        </div>
      </div>
    </div>
  );
};

export default SessionComparisonView;
