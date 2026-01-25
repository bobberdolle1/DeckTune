/**
 * FanControl component for fan curve management.
 * 
 * Feature: fan-control-curves
 * Requirements: 4.1, 4.2, 4.3
 * 
 * Provides UI for:
 * - Preset selection (Stock, Silent, Turbo)
 * - Custom curve creation and management
 * - Real-time status display
 * - Navigation back to admin panel
 */

import { useState, useEffect, FC } from "react";
import {
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  Focusable,
  TextField,
  ModalRoot,
  ModalHeader,
  ModalBody,
  ModalFooter,
  showModal,
  closeModal,
} from "@decky/ui";
import { FaArrowLeft, FaSpinner, FaExclamationTriangle, FaPlus, FaTrash } from "react-icons/fa";
import { call } from "@decky/api";

// Fan curve point interface
interface FanPoint {
  temp: number;
  speed: number;
}

// Fan status from backend
interface FanStatus {
  current_temp: number;
  current_speed: number;
  target_speed: number;
  active_curve: string;
  curve_type: "preset" | "custom";
  monitoring_active: boolean;
  hwmon_available: boolean;
  last_update: string;
}

interface FanControlProps {
  onBack: () => void;
}

/**
 * FanControl component
 * Requirements: 4.1, 4.2, 4.3
 */
export const FanControl: FC<FanControlProps> = ({ onBack }) => {
  const [status, setStatus] = useState<FanStatus | null>(null);
  const [presets, setPresets] = useState<string[]>([]);
  const [customCurves, setCustomCurves] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isApplying, setIsApplying] = useState(false);
  const [showCustomEditor, setShowCustomEditor] = useState(false);
  const [customCurveName, setCustomCurveName] = useState("");
  const [customPoints, setCustomPoints] = useState<FanPoint[]>([
    { temp: 40, speed: 20 },
    { temp: 60, speed: 50 },
    { temp: 80, speed: 100 },
  ]);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Poll status every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const loadInitialData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Load presets
      const presetsResult = await call<{ success: boolean; presets?: string[]; error?: string }>(
        "fan_list_presets"
      );
      
      if (presetsResult.success && presetsResult.presets) {
        setPresets(presetsResult.presets);
      }

      // Load custom curves
      const customResult = await call<{ success: boolean; curves?: string[]; error?: string }>(
        "fan_list_custom"
      );
      
      if (customResult.success && customResult.curves) {
        setCustomCurves(customResult.curves);
      }

      // Load status
      await loadStatus();
    } catch (e) {
      setError(`Failed to load fan control data: ${e}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStatus = async () => {
    try {
      const result = await call<{ success: boolean; status?: FanStatus; error?: string }>(
        "fan_get_status"
      );
      
      if (result.success && result.status) {
        setStatus(result.status);
      }
    } catch (e) {
      console.error("Failed to load fan status:", e);
    }
  };

  const applyPreset = async (presetName: string) => {
    setIsApplying(true);
    setError(null);
    
    try {
      const result = await call<{ success: boolean; error?: string }>(
        "fan_apply_preset",
        presetName
      );
      
      if (!result.success) {
        setError(result.error || "Failed to apply preset");
      } else {
        await loadStatus();
      }
    } catch (e) {
      setError(`Error applying preset: ${e}`);
    } finally {
      setIsApplying(false);
    }
  };

  const loadCustomCurve = async (curveName: string) => {
    setIsApplying(true);
    setError(null);
    
    try {
      const result = await call<{ success: boolean; error?: string }>(
        "fan_load_custom",
        curveName
      );
      
      if (!result.success) {
        setError(result.error || "Failed to load custom curve");
      } else {
        await loadStatus();
      }
    } catch (e) {
      setError(`Error loading custom curve: ${e}`);
    } finally {
      setIsApplying(false);
    }
  };

  const deleteCustomCurve = async (curveName: string) => {
    setError(null);
    
    try {
      const result = await call<{ success: boolean; error?: string }>(
        "fan_delete_custom",
        curveName
      );
      
      if (!result.success) {
        setError(result.error || "Failed to delete custom curve");
      } else {
        // Refresh custom curves list
        const customResult = await call<{ success: boolean; curves?: string[]; error?: string }>(
          "fan_list_custom"
        );
        
        if (customResult.success && customResult.curves) {
          setCustomCurves(customResult.curves);
        }
      }
    } catch (e) {
      setError(`Error deleting custom curve: ${e}`);
    }
  };

  const validatePoints = (points: FanPoint[]): string | null => {
    // Check point count (3-10)
    if (points.length < 3) {
      return "Curve must have at least 3 points";
    }
    if (points.length > 10) {
      return "Curve cannot have more than 10 points";
    }

    // Check each point
    for (const point of points) {
      if (point.temp < 0 || point.temp > 120) {
        return `Temperature ${point.temp}°C is out of range [0, 120]`;
      }
      if (point.speed < 0 || point.speed > 100) {
        return `Speed ${point.speed}% is out of range [0, 100]`;
      }
    }

    return null;
  };

  const addPoint = () => {
    if (customPoints.length >= 10) {
      setValidationError("Cannot add more than 10 points");
      return;
    }

    // Add a new point between the last two points
    const lastPoint = customPoints[customPoints.length - 1];
    const secondLastPoint = customPoints[customPoints.length - 2];
    const newTemp = Math.round((lastPoint.temp + secondLastPoint.temp) / 2);
    const newSpeed = Math.round((lastPoint.speed + secondLastPoint.speed) / 2);

    setCustomPoints([...customPoints, { temp: newTemp, speed: newSpeed }]);
    setValidationError(null);
  };

  const removePoint = (index: number) => {
    if (customPoints.length <= 3) {
      setValidationError("Curve must have at least 3 points");
      return;
    }

    const newPoints = customPoints.filter((_, i) => i !== index);
    setCustomPoints(newPoints);
    setValidationError(null);
  };

  const updatePoint = (index: number, field: "temp" | "speed", value: string) => {
    const numValue = parseInt(value, 10);
    if (isNaN(numValue)) return;

    const newPoints = [...customPoints];
    newPoints[index] = { ...newPoints[index], [field]: numValue };
    setCustomPoints(newPoints);

    // Validate
    const error = validatePoints(newPoints);
    setValidationError(error);
  };

  const saveCustomCurve = async () => {
    // Validate curve name
    if (!customCurveName.trim()) {
      setValidationError("Please enter a curve name");
      return;
    }

    // Validate points
    const error = validatePoints(customPoints);
    if (error) {
      setValidationError(error);
      return;
    }

    setIsApplying(true);
    setValidationError(null);

    try {
      const result = await call<{ success: boolean; error?: string }>(
        "fan_create_custom",
        customCurveName.trim(),
        customPoints
      );

      if (!result.success) {
        setValidationError(result.error || "Failed to create custom curve");
      } else {
        // Refresh custom curves list
        const customResult = await call<{ success: boolean; curves?: string[]; error?: string }>(
          "fan_list_custom"
        );

        if (customResult.success && customResult.curves) {
          setCustomCurves(customResult.curves);
        }

        // Close editor
        setShowCustomEditor(false);
        setCustomCurveName("");
        setCustomPoints([
          { temp: 40, speed: 20 },
          { temp: 60, speed: 50 },
          { temp: 80, speed: 100 },
        ]);
      }
    } catch (e) {
      setValidationError(`Error creating custom curve: ${e}`);
    } finally {
      setIsApplying(false);
    }
  };

  const openCustomEditor = () => {
    setShowCustomEditor(true);
    setValidationError(null);
    setCustomCurveName("");
    setCustomPoints([
      { temp: 40, speed: 20 },
      { temp: 60, speed: 50 },
      { temp: 80, speed: 100 },
    ]);
  };

  // Loading state
  if (isLoading) {
    return (
      <PanelSection title="Fan Control">
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
            <span>Loading fan control...</span>
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
      </PanelSection>
    );
  }

  return (
    <>
      <PanelSection>
        {/* Back button - Requirements: 8.4 */}
        <PanelSectionRow>
          <Focusable>
            <ButtonItem
              layout="below"
              onClick={onBack}
              style={{
                minHeight: "40px",
                padding: "8px 12px",
                backgroundColor: "rgba(61, 68, 80, 0.5)",
                borderRadius: "8px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <FaArrowLeft size={14} />
                <span>Back to Main View</span>
              </div>
            </ButtonItem>
          </Focusable>
        </PanelSectionRow>

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
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <FaExclamationTriangle />
              {error}
            </div>
          </PanelSectionRow>
        )}

        {/* Hardware unavailable warning */}
        {status && !status.hwmon_available && (
          <PanelSectionRow>
            <div
              style={{
                padding: "8px 12px",
                backgroundColor: "#5c4813",
                borderRadius: "6px",
                marginBottom: "8px",
                fontSize: "11px",
                color: "#fff3cd",
                border: "1px solid #ff9800",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <FaExclamationTriangle />
              Hardware interface unavailable - fan control disabled
            </div>
          </PanelSectionRow>
        )}
      </PanelSection>

      {/* Status Display - will be implemented in subtask 9.3 */}
      {status && (
        <PanelSection title="Current Status">
          <PanelSectionRow>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 12px",
                backgroundColor: "#23262e",
                borderRadius: "8px",
                fontSize: "13px",
              }}
            >
              <div>
                <div style={{ color: "#8b929a", fontSize: "11px" }}>Temperature</div>
                <div style={{ fontWeight: "bold" }}>{status.current_temp.toFixed(1)}°C</div>
              </div>
              <div>
                <div style={{ color: "#8b929a", fontSize: "11px" }}>Current Speed</div>
                <div style={{ fontWeight: "bold" }}>{status.current_speed}%</div>
              </div>
              <div>
                <div style={{ color: "#8b929a", fontSize: "11px" }}>Target Speed</div>
                <div style={{ fontWeight: "bold" }}>{status.target_speed}%</div>
              </div>
            </div>
          </PanelSectionRow>
          <PanelSectionRow>
            <div
              style={{
                padding: "6px 12px",
                backgroundColor: "#1a1d23",
                borderRadius: "6px",
                fontSize: "11px",
                color: "#8b929a",
                textAlign: "center",
              }}
            >
              Active: {status.active_curve} ({status.curve_type})
            </div>
          </PanelSectionRow>
        </PanelSection>
      )}

      {/* Preset Selection - will be implemented in subtask 9.2 */}
      <PanelSection title="Presets">
        {presets.map((preset) => (
          <PanelSectionRow key={preset}>
            <Focusable>
              <ButtonItem
                layout="below"
                onClick={() => applyPreset(preset)}
                disabled={isApplying || (status && !status.hwmon_available)}
                style={{
                  minHeight: "40px",
                  padding: "8px 12px",
                  backgroundColor:
                    status?.active_curve === preset && status?.curve_type === "preset"
                      ? "#1a9fff"
                      : "rgba(61, 68, 80, 0.5)",
                  borderRadius: "8px",
                  border:
                    status?.active_curve === preset && status?.curve_type === "preset"
                      ? "2px solid rgba(26, 159, 255, 0.5)"
                      : "2px solid transparent",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <span style={{ textTransform: "capitalize" }}>{preset}</span>
                  {status?.active_curve === preset && status?.curve_type === "preset" && (
                    <span style={{ fontSize: "11px", color: "#4caf50" }}>● Active</span>
                  )}
                </div>
              </ButtonItem>
            </Focusable>
          </PanelSectionRow>
        ))}
      </PanelSection>

      {/* Custom Curves - will be implemented in subtask 9.4 */}
      <PanelSection title="Custom Curves">
        {customCurves.length === 0 ? (
          <PanelSectionRow>
            <div
              style={{
                textAlign: "center",
                padding: "16px",
                color: "#8b929a",
                fontSize: "12px",
              }}
            >
              No custom curves created yet
            </div>
          </PanelSectionRow>
        ) : (
          customCurves.map((curve) => (
            <PanelSectionRow key={curve}>
              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  alignItems: "center",
                }}
              >
                <Focusable style={{ flex: 1 }}>
                  <ButtonItem
                    layout="below"
                    onClick={() => loadCustomCurve(curve)}
                    disabled={isApplying || (status && !status.hwmon_available)}
                    style={{
                      minHeight: "40px",
                      padding: "8px 12px",
                      backgroundColor:
                        status?.active_curve === curve && status?.curve_type === "custom"
                          ? "#1a9fff"
                          : "rgba(61, 68, 80, 0.5)",
                      borderRadius: "8px",
                      border:
                        status?.active_curve === curve && status?.curve_type === "custom"
                          ? "2px solid rgba(26, 159, 255, 0.5)"
                          : "2px solid transparent",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>{curve}</span>
                      {status?.active_curve === curve && status?.curve_type === "custom" && (
                        <span style={{ fontSize: "11px", color: "#4caf50" }}>● Active</span>
                      )}
                    </div>
                  </ButtonItem>
                </Focusable>
                <Focusable>
                  <ButtonItem
                    layout="below"
                    onClick={() => deleteCustomCurve(curve)}
                    disabled={isApplying}
                    style={{
                      minHeight: "40px",
                      padding: "8px 12px",
                      backgroundColor: "#5c1313",
                      borderRadius: "8px",
                      border: "1px solid #f44336",
                    }}
                  >
                    Delete
                  </ButtonItem>
                </Focusable>
              </div>
            </PanelSectionRow>
          ))
        )}
        
        <PanelSectionRow>
          <Focusable>
            <ButtonItem
              layout="below"
              onClick={openCustomEditor}
              disabled={status && !status.hwmon_available}
              style={{
                minHeight: "40px",
                padding: "8px 12px",
                backgroundColor: "rgba(26, 159, 255, 0.2)",
                borderRadius: "8px",
                border: "1px solid #1a9fff",
              }}
            >
              Edit Curve
            </ButtonItem>
          </Focusable>
        </PanelSectionRow>
      </PanelSection>

      {/* Custom Curve Editor Modal */}
      {showCustomEditor && (
        <ModalRoot onCancel={() => setShowCustomEditor(false)}>
          <ModalHeader>Create Custom Fan Curve</ModalHeader>
          <ModalBody>
            <div style={{ padding: "16px" }}>
              {/* Curve name input */}
              <div style={{ marginBottom: "16px" }}>
                <div style={{ marginBottom: "8px", fontSize: "13px", color: "#8b929a" }}>
                  Curve Name
                </div>
                <TextField
                  value={customCurveName}
                  onChange={(e) => setCustomCurveName(e.target.value)}
                  placeholder="Enter curve name"
                  style={{
                    width: "100%",
                    padding: "8px",
                    backgroundColor: "#23262e",
                    border: "1px solid #3d4450",
                    borderRadius: "4px",
                    color: "#fff",
                  }}
                />
              </div>

              {/* Points editor */}
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{
                    marginBottom: "8px",
                    fontSize: "13px",
                    color: "#8b929a",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>Curve Points (3-10)</span>
                  <ButtonItem
                    layout="below"
                    onClick={addPoint}
                    disabled={customPoints.length >= 10}
                    style={{
                      padding: "4px 8px",
                      fontSize: "11px",
                      backgroundColor: "rgba(76, 175, 80, 0.2)",
                      border: "1px solid #4caf50",
                      borderRadius: "4px",
                    }}
                  >
                    <FaPlus size={10} style={{ marginRight: "4px" }} />
                    Add Point
                  </ButtonItem>
                </div>

                {customPoints.map((point, index) => (
                  <div
                    key={index}
                    style={{
                      display: "flex",
                      gap: "8px",
                      marginBottom: "8px",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "11px", color: "#8b929a", marginBottom: "4px" }}>
                        Temp (°C)
                      </div>
                      <TextField
                        value={point.temp.toString()}
                        onChange={(e) => updatePoint(index, "temp", e.target.value)}
                        type="number"
                        min={0}
                        max={120}
                        style={{
                          width: "100%",
                          padding: "6px",
                          backgroundColor: "#23262e",
                          border: "1px solid #3d4450",
                          borderRadius: "4px",
                          color: "#fff",
                        }}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "11px", color: "#8b929a", marginBottom: "4px" }}>
                        Speed (%)
                      </div>
                      <TextField
                        value={point.speed.toString()}
                        onChange={(e) => updatePoint(index, "speed", e.target.value)}
                        type="number"
                        min={0}
                        max={100}
                        style={{
                          width: "100%",
                          padding: "6px",
                          backgroundColor: "#23262e",
                          border: "1px solid #3d4450",
                          borderRadius: "4px",
                          color: "#fff",
                        }}
                      />
                    </div>
                    <ButtonItem
                      layout="below"
                      onClick={() => removePoint(index)}
                      disabled={customPoints.length <= 3}
                      style={{
                        padding: "6px 8px",
                        marginTop: "16px",
                        backgroundColor: "rgba(244, 67, 54, 0.2)",
                        border: "1px solid #f44336",
                        borderRadius: "4px",
                      }}
                    >
                      <FaTrash size={12} />
                    </ButtonItem>
                  </div>
                ))}
              </div>

              {/* Validation error */}
              {validationError && (
                <div
                  style={{
                    padding: "8px 12px",
                    backgroundColor: "#5c1313",
                    borderRadius: "6px",
                    marginBottom: "8px",
                    fontSize: "11px",
                    color: "#ffcdd2",
                    border: "1px solid #f44336",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <FaExclamationTriangle />
                  {validationError}
                </div>
              )}
            </div>
          </ModalBody>
          <ModalFooter>
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
              <ButtonItem
                layout="below"
                onClick={() => setShowCustomEditor(false)}
                disabled={isApplying}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "rgba(61, 68, 80, 0.5)",
                  borderRadius: "4px",
                }}
              >
                Cancel
              </ButtonItem>
              <ButtonItem
                layout="below"
                onClick={saveCustomCurve}
                disabled={isApplying || !!validationError || !customCurveName.trim()}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#1a9fff",
                  borderRadius: "4px",
                }}
              >
                {isApplying ? "Saving..." : "Save Curve"}
              </ButtonItem>
            </div>
          </ModalFooter>
        </ModalRoot>
      )}
    </>
  );
};

export default FanControl;
