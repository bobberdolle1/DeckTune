/**
 * BinningProgress component for displaying binning progress.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
 */

import { FC } from "react";
import { ProgressBarWithInfo } from "@decky/ui";
import { BinningProgress as BinningProgressData } from "../api/types";

/**
 * Format ETA in human-readable format.
 */
function formatEta(seconds: number): string {
  if (seconds <= 0) return "Завершение...";
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (minutes > 0) {
    return `~${minutes}м ${remainingSeconds}с`;
  }
  return `~${remainingSeconds}с`;
}

/**
 * Styles for the BinningProgress component.
 */
const styles = {
  container: {
    padding: "8px",
    backgroundColor: "rgba(0, 0, 0, 0.2)",
    borderRadius: "4px",
    marginBottom: "8px",
  },
  status: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "4px",
    marginTop: "8px",
    fontSize: "12px",
  },
  statusRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  label: {
    color: "rgba(255, 255, 255, 0.7)",
  },
  value: {
    fontWeight: "bold" as const,
    color: "#fff",
  },
  highlight: {
    color: "#4caf50",
    fontWeight: "bold" as const,
  },
};

interface BinningProgressProps {
  progress: BinningProgressData | null;
  isRunning: boolean;
}

/**
 * BinningProgress component displays the progress of silicon binning.
 * 
 * Shows:
 * - Progress bar with percentage
 * - Current iteration / max iterations
 * - Current value being tested
 * - Last stable value found
 * - Estimated time remaining (ETA)
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
 */
export const BinningProgressComponent: FC<BinningProgressProps> = ({ 
  progress, 
  isRunning 
}) => {
  if (!isRunning || !progress) {
    return null;
  }

  const { 
    current_value, 
    iteration, 
    last_stable, 
    eta, 
    max_iterations,
    percent_complete 
  } = progress;

  return (
    <div style={styles.container}>
      {/* Progress bar */}
      <ProgressBarWithInfo
        label={`Итерация ${iteration}/${max_iterations}`}
        description={`Тестируется: ${current_value}mV`}
        nProgress={percent_complete / 100}
        sOperationText={formatEta(eta)}
      />
      
      {/* Status details */}
      <div style={styles.status}>
        <div style={styles.statusRow}>
          <span style={styles.label}>Текущее значение:</span>
          <span style={styles.value}>{current_value}mV</span>
        </div>
        <div style={styles.statusRow}>
          <span style={styles.label}>Последнее стабильное:</span>
          <span style={styles.highlight}>{last_stable}mV</span>
        </div>
        <div style={styles.statusRow}>
          <span style={styles.label}>Осталось:</span>
          <span style={styles.value}>{formatEta(eta)}</span>
        </div>
        <div style={styles.statusRow}>
          <span style={styles.label}>Прогресс:</span>
          <span style={styles.value}>{percent_complete.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
};

export default BinningProgressComponent;
