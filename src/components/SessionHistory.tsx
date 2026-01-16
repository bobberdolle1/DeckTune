/**
 * SessionHistory component for displaying gaming session history.
 * 
 * Feature: decktune-3.1-reliability-ux
 * Requirements: 8.4, 8.5, 8.6
 * 
 * Displays last 30 sessions in list view with key metrics:
 * - Duration, average temperature, power, battery saved
 */

import React, { FC, useState, useEffect, useCallback } from "react";
import {
  FaHistory,
  FaClock,
  FaThermometerHalf,
  FaBolt,
  FaBatteryFull,
  FaGamepad,
  FaChevronRight,
  FaExchangeAlt,
  FaSpinner,
} from "react-icons/fa";
import { Session, SessionMetrics } from "../api/types";
import { useDeckTune } from "../context";

/**
 * Format duration in seconds to human-readable string.
 */
const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    return `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
};

/**
 * Format ISO date string to readable format.
 */
const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return `Today ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } else if (diffDays === 1) {
    return `Yesterday ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
};

/**
 * Props for SessionHistory component.
 */
interface SessionHistoryProps {
  /** Callback when a session is selected for detail view */
  onSelectSession?: (session: Session) => void;
  /** Callback when compare mode is activated with two sessions */
  onCompare?: (session1: Session, session2: Session) => void;
}

/**
 * SessionHistory component - displays last 30 sessions in list view.
 * 
 * Requirements:
 * - 8.4: Display the last 30 sessions with key metrics in a list view
 */
export const SessionHistory: FC<SessionHistoryProps> = ({
  onSelectSession,
  onCompare,
}) => {
  const { api } = useDeckTune();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState<Session | null>(null);

  /**
   * Load session history from backend.
   * Requirements: 8.4
   */
  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const history = await api.getSessionHistory(30);
      setSessions(history || []);
    } catch (e) {
      setError("Failed to load session history");
      console.error("Failed to load sessions:", e);
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  /**
   * Handle session click - either select for detail or compare.
   */
  const handleSessionClick = (session: Session) => {
    if (compareMode) {
      if (selectedForCompare === null) {
        setSelectedForCompare(session);
      } else if (selectedForCompare.id !== session.id) {
        // Trigger comparison
        if (onCompare) {
          onCompare(selectedForCompare, session);
        }
        setCompareMode(false);
        setSelectedForCompare(null);
      }
    } else if (onSelectSession) {
      onSelectSession(session);
    }
  };

  /**
   * Toggle compare mode.
   */
  const toggleCompareMode = () => {
    setCompareMode(!compareMode);
    setSelectedForCompare(null);
  };

  /**
   * Cancel compare mode.
   */
  const cancelCompare = () => {
    setCompareMode(false);
    setSelectedForCompare(null);
  };

  if (loading) {
    return (
      <div style={{ 
        padding: "24px", 
        textAlign: "center", 
        color: "#8b929a" 
      }}>
        <FaSpinner className="spin" style={{ fontSize: "24px", marginBottom: "8px" }} />
        <div>Loading session history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: "24px", 
        textAlign: "center", 
        color: "#f44336" 
      }}>
        <div>{error}</div>
        <button
          onClick={loadSessions}
          style={{
            marginTop: "12px",
            padding: "8px 16px",
            backgroundColor: "#1a9fff",
            border: "none",
            borderRadius: "4px",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div style={{ 
        padding: "24px", 
        textAlign: "center", 
        color: "#8b929a" 
      }}>
        <FaHistory style={{ fontSize: "32px", marginBottom: "12px", opacity: 0.5 }} />
        <div>No session history yet</div>
        <div style={{ fontSize: "12px", marginTop: "8px" }}>
          Sessions will appear here after using Dynamic Mode
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "8px 0" }}>
      {/* Header with compare button */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "12px",
        padding: "0 4px",
      }}>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "8px",
          fontSize: "14px",
          fontWeight: "bold",
        }}>
          <FaHistory style={{ color: "#1a9fff" }} />
          <span>Session History ({sessions.length})</span>
        </div>
        
        {sessions.length >= 2 && (
          <button
            onClick={compareMode ? cancelCompare : toggleCompareMode}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 12px",
              backgroundColor: compareMode ? "#f44336" : "#23262e",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              fontSize: "12px",
            }}
          >
            <FaExchangeAlt />
            <span>{compareMode ? "Cancel" : "Compare"}</span>
          </button>
        )}
      </div>

      {/* Compare mode instructions */}
      {compareMode && (
        <div style={{
          padding: "10px 12px",
          backgroundColor: "#1a9fff20",
          borderRadius: "6px",
          marginBottom: "12px",
          fontSize: "12px",
          color: "#1a9fff",
          border: "1px solid #1a9fff40",
        }}>
          {selectedForCompare 
            ? `Selected: ${selectedForCompare.game_name || "Unknown Game"} - Now select another session to compare`
            : "Select the first session to compare"
          }
        </div>
      )}

      {/* Session list */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {sessions.map((session) => (
          <SessionListItem
            key={session.id}
            session={session}
            onClick={() => handleSessionClick(session)}
            isSelected={selectedForCompare?.id === session.id}
            compareMode={compareMode}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * Props for SessionListItem component.
 */
interface SessionListItemProps {
  session: Session;
  onClick: () => void;
  isSelected: boolean;
  compareMode: boolean;
}

/**
 * Individual session list item.
 * Requirements: 8.4 - Show key metrics: duration, avg temp, power, battery saved
 */
const SessionListItem: FC<SessionListItemProps> = ({
  session,
  onClick,
  isSelected,
  compareMode,
}) => {
  const metrics = session.metrics;
  
  return (
    <button
      onClick={onClick}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        padding: "12px",
        backgroundColor: isSelected ? "#1a9fff30" : "#23262e",
        border: isSelected ? "2px solid #1a9fff" : "2px solid transparent",
        borderRadius: "8px",
        cursor: "pointer",
        textAlign: "left",
        width: "100%",
        transition: "all 0.2s ease",
      }}
    >
      {/* Top row: Game name and date */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "8px",
          flex: 1,
          minWidth: 0,
        }}>
          <FaGamepad style={{ color: "#1a9fff", flexShrink: 0 }} />
          <span style={{ 
            fontWeight: "bold", 
            fontSize: "13px",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}>
            {session.game_name || "Unknown Game"}
          </span>
        </div>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "4px",
          color: "#8b929a",
          fontSize: "11px",
          flexShrink: 0,
        }}>
          <span>{formatDate(session.start_time)}</span>
          {!compareMode && <FaChevronRight style={{ fontSize: "10px" }} />}
        </div>
      </div>

      {/* Metrics row */}
      {metrics && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "8px",
        }}>
          {/* Duration */}
          <MetricBadge
            icon={FaClock}
            value={formatDuration(metrics.duration_sec)}
            label="Duration"
            color="#8b929a"
          />
          
          {/* Avg Temperature */}
          <MetricBadge
            icon={FaThermometerHalf}
            value={`${metrics.avg_temperature_c.toFixed(1)}°C`}
            label="Avg Temp"
            color="#ff9800"
          />
          
          {/* Avg Power */}
          <MetricBadge
            icon={FaBolt}
            value={`${metrics.avg_power_w.toFixed(1)}W`}
            label="Avg Power"
            color="#ffeb3b"
          />
          
          {/* Battery Saved */}
          <MetricBadge
            icon={FaBatteryFull}
            value={`${metrics.estimated_battery_saved_wh.toFixed(2)}Wh`}
            label="Saved"
            color="#4caf50"
          />
        </div>
      )}

      {/* No metrics message for active sessions */}
      {!metrics && (
        <div style={{
          fontSize: "11px",
          color: "#8b929a",
          fontStyle: "italic",
        }}>
          Session in progress...
        </div>
      )}
    </button>
  );
};

/**
 * Props for MetricBadge component.
 */
interface MetricBadgeProps {
  icon: FC<{ style?: React.CSSProperties }>;
  value: string;
  label: string;
  color: string;
}

/**
 * Small metric badge for session list items.
 */
const MetricBadge: FC<MetricBadgeProps> = ({ icon: Icon, value, label, color }) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "2px",
    }}>
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "4px",
        color,
      }}>
        <span style={{ fontSize: "10px" }}><Icon /></span>
        <span style={{ fontSize: "11px", fontWeight: "bold" }}>{value}</span>
      </div>
      <span style={{ fontSize: "9px", color: "#8b929a" }}>{label}</span>
    </div>
  );
};

export default SessionHistory;
