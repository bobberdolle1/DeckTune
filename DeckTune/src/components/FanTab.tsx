/**
 * FanTab component for fan control in Expert Mode.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 * 
 * Provides fan curve editing and control through the FanCurveEditor component.
 */

import { useState, useEffect, FC } from "react";
import { PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaSpinner, FaExclamationTriangle } from "react-icons/fa";
import { useDeckTune } from "../context";
import { FanCurveEditor, FanConfig, FanStatus } from "./FanCurveEditor";

/**
 * FanTab component for Expert Mode.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 */
export const FanTab: FC = () => {
  const { api } = useDeckTune();
  const [config, setConfig] = useState<FanConfig | null>(null);
  const [status, setStatus] = useState<FanStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Load fan configuration on mount
  useEffect(() => {
    const loadFanConfig = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await api.getFanConfig();
        if (result.success && result.config) {
          setConfig(result.config);
        } else {
          setError(result.error || "Failed to load fan configuration");
        }
      } catch (e) {
        setError(`Error loading fan config: ${e}`);
      } finally {
        setIsLoading(false);
      }
    };

    loadFanConfig();
  }, [api]);

  // Poll fan status periodically
  useEffect(() => {
    if (!config?.enabled) return;

    const pollStatus = async () => {
      try {
        const result = await api.getFanStatus();
        if (result.success && result.status) {
          setStatus(result.status);
        }
      } catch (e) {
        console.error("Error polling fan status:", e);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [api, config?.enabled]);

  const handleConfigChange = (newConfig: FanConfig) => {
    setConfig(newConfig);
  };

  const handleSave = async (newConfig: FanConfig) => {
    setIsSaving(true);
    setError(null);
    try {
      const result = await api.setFanConfig(newConfig);
      if (result.success) {
        setConfig(newConfig);
      } else {
        setError(result.error || "Failed to save fan configuration");
      }
    } catch (e) {
      setError(`Error saving fan config: ${e}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            padding: "24px",
            color: "#8b929a",
          }}
        >
          <FaSpinner className="spin" />
          <span>Загрузка конфигурации вентилятора...</span>
        </div>
        <style>
          {`
            .spin {
              animation: spin 1s linear infinite;
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}
        </style>
      </PanelSectionRow>
    );
  }

  // Error state
  if (error && !config) {
    return (
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "12px",
            padding: "16px",
            backgroundColor: "#5c1313",
            borderRadius: "8px",
            border: "1px solid #f44336",
          }}
        >
          <FaExclamationTriangle style={{ color: "#f44336", fontSize: "24px" }} />
          <div style={{ color: "#ffcdd2", textAlign: "center", fontSize: "12px" }}>
            {error}
          </div>
          <ButtonItem
            layout="below"
            onClick={() => window.location.reload()}
          >
            Попробовать снова
          </ButtonItem>
        </div>
      </PanelSectionRow>
    );
  }

  // No config available
  if (!config) {
    return (
      <PanelSectionRow>
        <div
          style={{
            textAlign: "center",
            padding: "24px",
            color: "#8b929a",
          }}
        >
          Конфигурация вентилятора недоступна
        </div>
      </PanelSectionRow>
    );
  }

  return (
    <>
      {/* Error banner */}
      {error && (
        <PanelSectionRow>
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "#5c1313",
              borderRadius: "6px",
              marginBottom: "8px",
              fontSize: "11px",
              color: "#ffcdd2",
              border: "1px solid #f44336",
            }}
          >
            {error}
          </div>
        </PanelSectionRow>
      )}

      {/* Fan Curve Editor */}
      <FanCurveEditor
        config={config}
        status={status || undefined}
        onConfigChange={handleConfigChange}
        onSave={handleSave}
        isLoading={isSaving}
      />
    </>
  );
};

export default FanTab;
