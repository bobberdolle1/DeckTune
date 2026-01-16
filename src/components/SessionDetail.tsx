/**
 * SessionDetail component for displaying detailed session metrics.
 * 
 * Feature: decktune-3.1-reliability-ux
 * Requirements: 8.5
 * 
 * Displays detailed metrics including:
 * - Temperature and power graphs
 * - Undervolt values used during session
 * - Full session statistics
 */

import { useMemo, FC } from "react";
import {
  FaArrowLeft,
  FaClock,
  FaThermometerHalf,
  FaBolt,
  FaBatteryFull,
  FaGamepad,
  FaMicrochip,
  FaCalendarAlt,
} from "react-icons/fa";
import { Session, SessionTelemetrySample } from "../api/types";
import { TelemetryGraph } from "./TelemetryGraph";

/**
 * Format duration in seconds to human-readable string.
 */
const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
};

/**
 * Format ISO date string to readable format.
 */
const formatDateTime = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Props for SessionDetail component.
 */
interface SessionDetailProps {
  /** Session to display */
  session: Session;
  /** Callback to go back to list view */
  onBack: () => void;
}

/**
 * SessionDetail component - displays detailed metrics for a session.
 * 
 * Requirements:
 * - 8.5: Display detailed metrics including temperature graph, power graph, and undervolt values used
 */
export const SessionDetail: FC<SessionDetailProps> = ({ session, onBack }) => {
  const metrics = session.metrics;

  /**
   * Convert session samples to TelemetrySample format for graphs.
   */
  const telemetrySamples = useMemo(() => {
    return session.samples.map((sample: SessionTelemetrySample) => ({
      timestamp: sample.timestamp,
      temperature_c: sample.temperature_c,
      power_w: sample.power_w,
      load_percent: 0, // Not stored in session samples
    }));
  }, [session.samples]);

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
        <div style={{ flex: 1 }}>
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "8px",
            fontSize: "16px",
            fontWeight: "bold",
          }}>
            <FaGamepad style={{ color: "#1a9fff" }} />
            <span>{session.game_name || "Unknown Game"}</span>
          </div>
          <div style={{ 
            fontSize: "11px", 
            color: "#8b929a",
            marginTop: "2px",
          }}>
            {formatDateTime(session.start_time)}
          </div>
        </div>
      </div>

      {/* Session info card */}
      <div style={{
        backgroundColor: "#23262e",
        borderRadius: "8px",
        padding: "12px",
        marginBottom: "12px",
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "12px",
        }}>
          {/* Start time */}
          <InfoRow
            icon={FaCalendarAlt}
            label="Started"
            value={formatDateTime(session.start_time)}
            color="#8b929a"
          />
          
          {/* End time */}
          {session.end_time && (
            <InfoRow
              icon={FaCalendarAlt}
              label="Ended"
              value={formatDateTime(session.end_time)}
              color="#8b929a"
            />
          )}
          
          {/* Duration */}
          {metrics && (
            <InfoRow
              icon={FaClock}
              label="Duration"
              value={formatDuration(metrics.duration_sec)}
              color="#1a9fff"
            />
          )}
          
          {/* App ID */}
          {session.app_id && (
            <InfoRow
              icon={FaGamepad}
              label="App ID"
              value={String(session.app_id)}
              color="#8b929a"
            />
          )}
        </div>
      </div>

      {/* Metrics section */}
      {metrics && (
        <>
          {/* Temperature metrics */}
          <div style={{
            backgroundColor: "#23262e",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "12px",
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "12px",
              fontSize: "13px",
              fontWeight: "bold",
            }}>
              <FaThermometerHalf style={{ color: "#ff9800" }} />
              <span>Temperature</span>
            </div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "8px",
            }}>
              <MetricCard
                label="Average"
                value={`${metrics.avg_temperature_c.toFixed(1)}°C`}
                color="#ff9800"
              />
              <MetricCard
                label="Minimum"
                value={`${metrics.min_temperature_c.toFixed(1)}°C`}
                color="#4caf50"
              />
              <MetricCard
                label="Maximum"
                value={`${metrics.max_temperature_c.toFixed(1)}°C`}
                color="#f44336"
              />
            </div>
          </div>

          {/* Power metrics */}
          <div style={{
            backgroundColor: "#23262e",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "12px",
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "12px",
              fontSize: "13px",
              fontWeight: "bold",
            }}>
              <FaBolt style={{ color: "#ffeb3b" }} />
              <span>Power</span>
            </div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "8px",
            }}>
              <MetricCard
                label="Average Power"
                value={`${metrics.avg_power_w.toFixed(1)}W`}
                color="#ffeb3b"
              />
              <MetricCard
                label="Battery Saved"
                value={`${metrics.estimated_battery_saved_wh.toFixed(2)}Wh`}
                color="#4caf50"
                icon={FaBatteryFull}
              />
            </div>
          </div>

          {/* Undervolt values - Requirements: 8.5 */}
          <div style={{
            backgroundColor: "#23262e",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "12px",
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "12px",
              fontSize: "13px",
              fontWeight: "bold",
            }}>
              <FaMicrochip style={{ color: "#1a9fff" }} />
              <span>Undervolt Values</span>
            </div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "8px",
            }}>
              {metrics.undervolt_values.map((value, index) => (
                <div
                  key={index}
                  style={{
                    backgroundColor: "#1a1d23",
                    borderRadius: "6px",
                    padding: "8px",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontSize: "10px", color: "#8b929a" }}>
                    Core {index}
                  </div>
                  <div style={{
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: value === 0 ? "#8b929a" : "#1a9fff",
                  }}>
                    {value === 0 ? "Off" : `${value}mV`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Telemetry graphs - Requirements: 8.5 */}
      {telemetrySamples.length > 0 && (
        <div style={{ marginBottom: "12px" }}>
          <div style={{
            fontSize: "13px",
            fontWeight: "bold",
            marginBottom: "8px",
            padding: "0 4px",
          }}>
            Session Telemetry
          </div>
          <TelemetryGraph
            data={telemetrySamples}
            type="temperature"
            width={300}
            height={100}
          />
          <TelemetryGraph
            data={telemetrySamples}
            type="power"
            width={300}
            height={100}
          />
        </div>
      )}

      {/* No telemetry data message */}
      {telemetrySamples.length === 0 && (
        <div style={{
          padding: "24px",
          textAlign: "center",
          color: "#8b929a",
          backgroundColor: "#23262e",
          borderRadius: "8px",
        }}>
          No telemetry data available for this session
        </div>
      )}
    </div>
  );
};

/**
 * Props for InfoRow component.
 */
interface InfoRowProps {
  icon: FC;
  label: string;
  value: string;
  color: string;
}

/**
 * Info row for session details.
 */
const InfoRow: FC<InfoRowProps> = ({ icon: Icon, label, value, color }) => {
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "8px",
    }}>
      <span style={{ color, fontSize: "12px" }}><Icon /></span>
      <div>
        <div style={{ fontSize: "10px", color: "#8b929a" }}>{label}</div>
        <div style={{ fontSize: "12px" }}>{value}</div>
      </div>
    </div>
  );
};

/**
 * Props for MetricCard component.
 */
interface MetricCardProps {
  label: string;
  value: string;
  color: string;
  icon?: FC;
}

/**
 * Metric card for displaying a single metric.
 */
const MetricCard: FC<MetricCardProps> = ({ label, value, color, icon: Icon }) => {
  return (
    <div style={{
      backgroundColor: "#1a1d23",
      borderRadius: "6px",
      padding: "10px",
      textAlign: "center",
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
        justifyContent: "center",
        gap: "4px",
      }}>
        {Icon && <span style={{ color, fontSize: "12px" }}><Icon /></span>}
        <span style={{
          fontSize: "16px",
          fontWeight: "bold",
          color,
        }}>
          {value}
        </span>
      </div>
    </div>
  );
};

export default SessionDetail;
