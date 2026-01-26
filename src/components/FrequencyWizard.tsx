/**
 * FrequencyWizard - Frequency-based voltage curve generation UI.
 * 
 * Feature: frequency-based-wizard
 * Requirements: 3.1-3.7, 4.1-4.4, 5.1-5.6, 6.3, 6.5
 * 
 * Provides configuration form, progress monitoring, and curve visualization
 * for the frequency-based voltage wizard.
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  SliderField,
  Focusable,
  ProgressBarWithInfo,
} from "@decky/ui";
import {
  FaPlay,
  FaStop,
  FaCheck,
  FaExclamationTriangle,
  FaSpinner,
  FaBolt,
  FaBalanceScale,
  FaShieldAlt,
} from "react-icons/fa";
import { useDeckTune } from "../context";
import { FrequencyWizardConfig } from "../api/types";
import { FrequencyCurveChart } from "./FrequencyCurveChart";

/**
 * Quick preset configurations for common use cases.
 * Requirements: 3.7, 12.5
 */
interface QuickPreset {
  name: string;
  icon: any;
  description: string;
  config: FrequencyWizardConfig;
}

const QUICK_PRESETS: QuickPreset[] = [
  {
    name: "Conservative",
    icon: FaShieldAlt,
    description: "Safe settings, longer testing (~30 min)",
    config: {
      freq_start: 400,
      freq_end: 3500,
      freq_step: 200,
      test_duration: 30,
      voltage_start: -20,
      voltage_step: 2,
      safety_margin: 10,
    },
  },
  {
    name: "Balanced",
    icon: FaBalanceScale,
    description: "Balanced speed and thoroughness (~15 min)",
    config: {
      freq_start: 400,
      freq_end: 3500,
      freq_step: 200,
      test_duration: 20,
      voltage_start: -30,
      voltage_step: 2,
      safety_margin: 5,
    },
  },
  {
    name: "Aggressive",
    icon: FaBolt,
    description: "Fast testing, less margin (~10 min)",
    config: {
      freq_start: 400,
      freq_end: 3500,
      freq_step: 250,
      test_duration: 15,
      voltage_start: -40,
      voltage_step: 3,
      safety_margin: 3,
    },
  },
];

/**
 * Validation errors for configuration.
 * Requirements: 3.2-3.7
 */
interface ValidationErrors {
  freq_start?: string;
  freq_end?: string;
  freq_step?: string;
  test_duration?: string;
  voltage_start?: string;
  voltage_step?: string;
  safety_margin?: string;
}

/**
 * Validate wizard configuration.
 * Requirements: 3.2-3.7
 */
const validateConfig = (config: FrequencyWizardConfig): ValidationErrors => {
  const errors: ValidationErrors = {};

  // Requirement 3.2: Frequency range validation
  if (config.freq_start < 400 || config.freq_start > 3500) {
    errors.freq_start = "Start frequency must be between 400-3500 MHz";
  }
  if (config.freq_end <= config.freq_start) {
    errors.freq_end = "End frequency must be greater than start frequency";
  }
  if (config.freq_end > 3500) {
    errors.freq_end = "End frequency must not exceed 3500 MHz";
  }

  // Requirement 3.3: Frequency step validation
  if (config.freq_step < 50 || config.freq_step > 500) {
    errors.freq_step = "Frequency step must be between 50-500 MHz";
  }

  // Requirement 3.4: Test duration validation
  if (config.test_duration < 10 || config.test_duration > 120) {
    errors.test_duration = "Test duration must be between 10-120 seconds";
  }

  // Requirement 3.5: Voltage parameters validation
  if (config.voltage_start < -100 || config.voltage_start > 0) {
    errors.voltage_start = "Starting voltage must be between -100 and 0 mV";
  }
  if (config.voltage_step < 1 || config.voltage_step > 10) {
    errors.voltage_step = "Voltage step must be between 1-10 mV";
  }

  // Requirement 3.6: Safety margin validation
  if (config.safety_margin < 0 || config.safety_margin > 20) {
    errors.safety_margin = "Safety margin must be between 0-20 mV";
  }

  return errors;
};

/**
 * Main FrequencyWizard component.
 * Requirements: 3.1-3.7, 4.1-4.4, 6.3, 6.5
 */
export const FrequencyWizard: FC = () => {
  const { state, api } = useDeckTune();
  
  // Configuration mode: "preset" or "manual"
  const [configMode, setConfigMode] = useState<"preset" | "manual">("preset");
  
  // Configuration state - Requirements: 3.1
  const [config, setConfig] = useState<FrequencyWizardConfig>({
    freq_start: 400,
    freq_end: 3500,
    freq_step: 200,
    test_duration: 20,
    voltage_start: -30,
    voltage_step: 2,
    safety_margin: 5,
  });

  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [showErrors, setShowErrors] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Poll for progress updates - Requirements: 4.1-4.4
  useEffect(() => {
    if (!state.isFrequencyWizardRunning) return;

    const interval = setInterval(async () => {
      try {
        await api.getFrequencyWizardProgress();
      } catch (err) {
        console.error("Failed to fetch wizard progress:", err);
      }
    }, 1000); // Poll every second

    return () => clearInterval(interval);
  }, [state.isFrequencyWizardRunning, api]);

  // Validate configuration on change - Requirements: 3.7
  useEffect(() => {
    const errors = validateConfig(config);
    setValidationErrors(errors);
  }, [config]);

  /**
   * Apply a quick preset configuration.
   * Requirements: 3.7, 12.5
   */
  const handlePresetClick = (preset: QuickPreset) => {
    setConfig(preset.config);
    setConfigMode("preset");
    setShowErrors(false);
    setError(null);
  };

  /**
   * Start the frequency wizard.
   * Requirements: 6.3
   */
  const handleStart = async () => {
    console.log("[FrequencyWizard] Start button clicked");
    
    // Validate configuration - Requirement 3.7
    const errors = validateConfig(config);
    if (Object.keys(errors).length > 0) {
      console.error("[FrequencyWizard] Validation errors:", errors);
      setShowErrors(true);
      return;
    }

    setIsStarting(true);
    setError(null);
    
    console.log("[FrequencyWizard] Starting wizard with config:", config);

    try {
      const result = await api.startFrequencyWizard(config);
      
      console.log("[FrequencyWizard] Start result:", result);
      
      if (!result.success) {
        const errorMsg = result.error || "Failed to start wizard";
        console.error("[FrequencyWizard] Start failed:", errorMsg);
        setError(errorMsg);
      } else {
        console.log("[FrequencyWizard] Wizard started successfully");
      }
    } catch (err) {
      const errorMsg = String(err);
      console.error("[FrequencyWizard] Exception during start:", errorMsg);
      setError(errorMsg);
    } finally {
      setIsStarting(false);
    }
  };

  /**
   * Cancel the running wizard with confirmation.
   * Requirements: 6.5
   */
  const handleCancelClick = () => {
    setShowCancelConfirm(true);
  };

  const handleCancelConfirm = async () => {
    setShowCancelConfirm(false);
    setIsCancelling(true);
    setError(null);

    try {
      const result = await api.cancelFrequencyWizard();
      
      if (!result.success) {
        setError(result.error || "Failed to cancel wizard");
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setIsCancelling(false);
    }
  };

  const handleCancelDismiss = () => {
    setShowCancelConfirm(false);
  };

  /**
   * Apply the generated frequency curve and enable frequency mode.
   * Requirements: 6.3
   */
  const handleApply = async () => {
    if (!state.frequencyCurves || Object.keys(state.frequencyCurves).length === 0) {
      setError("No frequency curves available to apply");
      return;
    }

    setIsApplying(true);
    setError(null);

    try {
      // First, apply the frequency curves
      const applyResult = await api.applyFrequencyCurve(state.frequencyCurves);
      
      if (!applyResult.success) {
        setError(applyResult.error || "Failed to apply frequency curves");
        return;
      }

      // Then, enable frequency mode
      const enableResult = await api.enableFrequencyMode();
      
      if (!enableResult.success) {
        setError(enableResult.error || "Failed to enable frequency mode");
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setIsApplying(false);
    }
  };

  /**
   * Format time in seconds to human-readable string.
   */
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const isRunning = state.isFrequencyWizardRunning;
  const progress = state.frequencyWizardProgress;
  const hasErrors = Object.keys(validationErrors).length > 0;

  return (
    <>
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
          }
          
          .preset-card {
            background: rgba(61, 68, 80, 0.5);
            border-radius: 8px;
            padding: 12px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            cursor: pointer;
            max-width: 100%;
            overflow: hidden;
          }
          
          .preset-card:hover {
            border-color: #1a9fff;
            background: rgba(61, 68, 80, 0.8);
          }
          
          .preset-card.active {
            border-color: #1a9fff;
            background: rgba(26, 159, 255, 0.2);
          }
          
          .preset-card:focus-within,
          .preset-card.gpfocus {
            outline: 3px solid #1a9fff !important;
            outline-offset: 2px;
            box-shadow: 0 0 15px rgba(26, 159, 255, 0.6) !important;
          }
          
          .error-text {
            color: #f44336;
            font-size: 11px;
            margin-top: 4px;
          }
          
          .warning-banner {
            background: rgba(255, 152, 0, 0.1);
            border: 1px solid #ff9800;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
          }
          
          .info-banner {
            background: rgba(26, 159, 255, 0.1);
            border: 1px solid #1a9fff;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
          }
          
          .progress-container {
            background: rgba(61, 68, 80, 0.5);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
          }
          
          .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(139, 146, 154, 0.2);
          }
          
          .stat-row:last-child {
            border-bottom: none;
          }
          
          .stat-label {
            color: #8b929a;
            font-size: 11px;
          }
          
          .stat-value {
            color: #fff;
            font-size: 12px;
            font-weight: bold;
          }
        `}
      </style>

      <PanelSection title="Frequency-Based Voltage Wizard">
        {/* Warning banner when not running */}
        {!isRunning && (
          <PanelSectionRow>
            <div className="warning-banner">
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <FaExclamationTriangle style={{ color: "#ff9800", fontSize: "14px" }} />
                <span style={{ color: "#fff", fontSize: "12px", fontWeight: "bold" }}>
                  Advanced Feature
                </span>
              </div>
              <p style={{ fontSize: "11px", color: "#ccc", margin: 0 }}>
                This wizard will test CPU stability at different frequencies and voltages.
                The process may take 10-30 minutes depending on settings.
              </p>
            </div>
          </PanelSectionRow>
        )}

        {/* Error display */}
        {error && (
          <PanelSectionRow>
            <div style={{
              background: "rgba(244, 67, 54, 0.1)",
              border: "1px solid #f44336",
              borderRadius: "6px",
              padding: "10px",
              marginBottom: "12px",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <FaExclamationTriangle style={{ color: "#f44336", fontSize: "14px" }} />
                <span style={{ color: "#f44336", fontSize: "11px" }}>{error}</span>
              </div>
            </div>
          </PanelSectionRow>
        )}

        {/* Progress display - Requirements: 4.1-4.4 */}
        {isRunning && progress && (
          <>
            <PanelSectionRow>
              <div className="progress-container">
                <div style={{ marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <FaSpinner style={{ animation: "spin 1s linear infinite", color: "#1a9fff" }} />
                    <span style={{ color: "#fff", fontSize: "13px", fontWeight: "bold" }}>
                      Testing in Progress
                    </span>
                  </div>
                  
                  <ProgressBarWithInfo
                    nProgress={progress.progress_percent / 100}
                    sOperationText={`${Math.round(progress.progress_percent)}%`}
                  />
                </div>

                {/* Current test info - Requirements: 4.1, 4.2 */}
                <div className="stat-row">
                  <span className="stat-label">Current Frequency:</span>
                  <span className="stat-value">{progress.current_frequency} MHz</span>
                </div>
                
                <div className="stat-row">
                  <span className="stat-label">Current Voltage:</span>
                  <span className="stat-value">{progress.current_voltage} mV</span>
                </div>

                {/* Progress stats - Requirements: 4.3, 4.4 */}
                <div className="stat-row">
                  <span className="stat-label">Completed Points:</span>
                  <span className="stat-value">
                    {progress.completed_points} / {progress.total_points}
                  </span>
                </div>

                <div className="stat-row">
                  <span className="stat-label">Estimated Remaining:</span>
                  <span className="stat-value">{formatTime(progress.estimated_remaining)}</span>
                </div>
              </div>
            </PanelSectionRow>

            {/* Cancel button with confirmation - Requirement: 6.5 */}
            <PanelSectionRow>
              {!showCancelConfirm ? (
                <ButtonItem
                  layout="below"
                  onClick={handleCancelClick}
                  disabled={isCancelling}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    <FaStop />
                    <span>Cancel Wizard</span>
                  </div>
                </ButtonItem>
              ) : (
                <>
                  <div style={{
                    background: "rgba(255, 152, 0, 0.1)",
                    border: "1px solid #ff9800",
                    borderRadius: "6px",
                    padding: "10px",
                    marginBottom: "8px",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                      <FaExclamationTriangle style={{ color: "#ff9800", fontSize: "14px" }} />
                      <span style={{ color: "#fff", fontSize: "12px", fontWeight: "bold" }}>
                        Confirm Cancellation
                      </span>
                    </div>
                    <p style={{ fontSize: "11px", color: "#ccc", margin: 0 }}>
                      Are you sure you want to cancel the wizard? Progress will be lost and
                      settings will be restored to their original state.
                    </p>
                  </div>
                  
                  <Focusable style={{ display: "flex", gap: "8px" }}>
                    <ButtonItem
                      layout="below"
                      onClick={handleCancelConfirm}
                      disabled={isCancelling}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                        {isCancelling ? (
                          <>
                            <FaSpinner style={{ animation: "spin 1s linear infinite" }} />
                            <span>Cancelling...</span>
                          </>
                        ) : (
                          <>
                            <FaCheck />
                            <span>Yes, Cancel</span>
                          </>
                        )}
                      </div>
                    </ButtonItem>
                    
                    <ButtonItem
                      layout="below"
                      onClick={handleCancelDismiss}
                      disabled={isCancelling}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                        <FaStop />
                        <span>No, Continue</span>
                      </div>
                    </ButtonItem>
                  </Focusable>
                </>
              )}
            </PanelSectionRow>
          </>
        )}

        {/* Configuration form - Requirements: 3.1-3.7 */}
        {!isRunning && (
          <>
            {/* Mode Toggle: Preset vs Manual - FIXED: Vertical layout */}
            <PanelSectionRow>
              <Focusable style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
                <ButtonItem
                  layout="below"
                  onClick={() => setConfigMode("preset")}
                  style={{
                    width: "100%",
                    backgroundColor: configMode === "preset" ? "#1a9fff" : "#3d4450",
                    border: configMode === "preset" ? "2px solid #1a9fff" : "2px solid transparent",
                    minHeight: "36px",
                  }}
                >
                  <div style={{ 
                    fontSize: "11px", 
                    fontWeight: "bold",
                    color: configMode === "preset" ? "#fff" : "#8b929a"
                  }}>
                    Quick Presets
                  </div>
                </ButtonItem>
                <ButtonItem
                  layout="below"
                  onClick={() => setConfigMode("manual")}
                  style={{
                    width: "100%",
                    backgroundColor: configMode === "manual" ? "#1a9fff" : "#3d4450",
                    border: configMode === "manual" ? "2px solid #1a9fff" : "2px solid transparent",
                    minHeight: "36px",
                  }}
                >
                  <div style={{ 
                    fontSize: "11px", 
                    fontWeight: "bold",
                    color: configMode === "manual" ? "#fff" : "#8b929a"
                  }}>
                    Manual Config
                  </div>
                </ButtonItem>
              </Focusable>
            </PanelSectionRow>

            {/* Quick presets - Requirements: 3.7, 12.5 */}
            {configMode === "preset" && (
              <PanelSectionRow>
                <div style={{ marginBottom: "8px" }}>
                  <span style={{ color: "#8b929a", fontSize: "11px", fontWeight: "bold" }}>
                    Select Preset
                  </span>
                </div>
                <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px", maxWidth: "100%" }}>
                  {QUICK_PRESETS.map((preset) => {
                    const Icon = preset.icon;
                    const isActive = JSON.stringify(config) === JSON.stringify(preset.config);
                    
                    return (
                      <Focusable
                        key={preset.name}
                        className={`preset-card ${isActive ? "active" : ""}`}
                        onActivate={() => handlePresetClick(preset)}
                        onClick={() => handlePresetClick(preset)}
                        style={{ width: "100%" }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "10px", width: "100%" }}>
                          <Icon style={{ fontSize: "20px", color: isActive ? "#1a9fff" : "#8b929a", flexShrink: 0 }} />
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ 
                              fontSize: "12px", 
                              fontWeight: "bold", 
                              color: isActive ? "#1a9fff" : "#fff",
                              marginBottom: "2px",
                            }}>
                              {preset.name}
                            </div>
                            <div style={{ fontSize: "10px", color: "#8b929a", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                              {preset.description}
                            </div>
                          </div>
                          {isActive && (
                            <FaCheck style={{ color: "#1a9fff", fontSize: "14px", flexShrink: 0 }} />
                          )}
                        </div>
                      </Focusable>
                    );
                  })}
                </Focusable>
              </PanelSectionRow>
            )}

            {/* Frequency range configuration - Requirements: 3.1, 3.2 */}
            {configMode === "manual" && (
              <PanelSection title="Frequency Range">
              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Start"
                    value={config.freq_start}
                    min={400}
                    max={3500}
                    step={50}
                    onChange={(value) => setConfig({ ...config, freq_start: value })}
                    showValue={true}
                    valueSuffix=" MHz"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.freq_start && (
                  <div className="error-text">{validationErrors.freq_start}</div>
                )}
              </PanelSectionRow>

              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="End"
                    value={config.freq_end}
                    min={400}
                    max={3500}
                    step={50}
                    onChange={(value) => setConfig({ ...config, freq_end: value })}
                    showValue={true}
                    valueSuffix=" MHz"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.freq_end && (
                  <div className="error-text">{validationErrors.freq_end}</div>
                )}
              </PanelSectionRow>

              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Step"
                    value={config.freq_step}
                    min={50}
                    max={500}
                    step={10}
                    onChange={(value) => setConfig({ ...config, freq_step: value })}
                    showValue={true}
                    valueSuffix=" MHz"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.freq_step && (
                  <div className="error-text">{validationErrors.freq_step}</div>
                )}
              </PanelSectionRow>
            </PanelSection>
            )}

            {/* Test duration - Requirements: 3.1, 3.4 */}
            {configMode === "manual" && (
            <PanelSection title="Test Settings">
              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Duration"
                    value={config.test_duration}
                    min={10}
                    max={120}
                    step={5}
                    onChange={(value) => setConfig({ ...config, test_duration: value })}
                    showValue={true}
                    valueSuffix=" sec"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.test_duration && (
                  <div className="error-text">{validationErrors.test_duration}</div>
                )}
              </PanelSectionRow>
            </PanelSection>
            )}

            {/* Voltage parameters - Requirements: 3.1, 3.5 */}
            {configMode === "manual" && (
            <PanelSection title="Voltage Settings">
              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Start"
                    value={config.voltage_start}
                    min={-100}
                    max={0}
                    step={1}
                    onChange={(value) => setConfig({ ...config, voltage_start: value })}
                    showValue={true}
                    valueSuffix=" mV"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.voltage_start && (
                  <div className="error-text">{validationErrors.voltage_start}</div>
                )}
              </PanelSectionRow>

              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Step"
                    value={config.voltage_step}
                    min={1}
                    max={10}
                    step={1}
                    onChange={(value) => setConfig({ ...config, voltage_step: value })}
                    showValue={true}
                    valueSuffix=" mV"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.voltage_step && (
                  <div className="error-text">{validationErrors.voltage_step}</div>
                )}
              </PanelSectionRow>

              <PanelSectionRow>
                <Focusable>
                  <SliderField
                    label="Safety"
                    value={config.safety_margin}
                    min={0}
                    max={20}
                    step={1}
                    onChange={(value) => setConfig({ ...config, safety_margin: value })}
                    showValue={true}
                    valueSuffix=" mV"
                    bottomSeparator="none"
                  />
                </Focusable>
                {showErrors && validationErrors.safety_margin && (
                  <div className="error-text">{validationErrors.safety_margin}</div>
                )}
              </PanelSectionRow>
            </PanelSection>
            )}

            {/* Start button - Requirement: 6.3 */}
            <PanelSectionRow>
              <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <ButtonItem
                  layout="below"
                  onClick={handleStart}
                  disabled={isStarting || hasErrors}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    {isStarting ? (
                      <>
                        <FaSpinner style={{ animation: "spin 1s linear infinite" }} />
                        <span>Starting...</span>
                      </>
                    ) : (
                      <>
                        <FaPlay />
                        <span>Start Wizard</span>
                      </>
                    )}
                  </div>
                </ButtonItem>
                
                {/* Reset button for manual config */}
                {configMode === "manual" && (
                  <ButtonItem
                    layout="below"
                    onClick={() => {
                      setConfig({
                        freq_start: 400,
                        freq_end: 3500,
                        freq_step: 200,
                        test_duration: 20,
                        voltage_start: -30,
                        voltage_step: 2,
                        safety_margin: 5,
                      });
                      setShowErrors(false);
                      setError(null);
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                      <FaStop />
                      <span>Reset to Defaults</span>
                    </div>
                  </ButtonItem>
                )}
              </Focusable>
              
              {/* Validation error summary - Requirement: 3.7 */}
              {showErrors && hasErrors && (
                <div style={{ marginTop: "8px" }}>
                  <div style={{
                    background: "rgba(244, 67, 54, 0.1)",
                    border: "1px solid #f44336",
                    borderRadius: "6px",
                    padding: "8px",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
                      <FaExclamationTriangle style={{ color: "#f44336", fontSize: "12px" }} />
                      <span style={{ color: "#f44336", fontSize: "11px", fontWeight: "bold" }}>
                        Configuration Errors
                      </span>
                    </div>
                    <div style={{ fontSize: "10px", color: "#f44336" }}>
                      Please fix the validation errors above before starting.
                    </div>
                  </div>
                </div>
              )}
            </PanelSectionRow>
          </>
        )}

        {/* Curve visualization - Requirements: 5.1-5.6 */}
        {!isRunning && state.frequencyCurves && Object.keys(state.frequencyCurves).length > 0 && (
          <PanelSection title="Generated Frequency Curves">
            <PanelSectionRow>
              <div className="info-banner">
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <FaCheck style={{ color: "#4caf50", fontSize: "14px" }} />
                  <span style={{ color: "#fff", fontSize: "12px", fontWeight: "bold" }}>
                    Wizard Complete
                  </span>
                </div>
                <p style={{ fontSize: "11px", color: "#ccc", margin: 0 }}>
                  Frequency curves have been generated and saved. The chart below shows the
                  voltage-frequency relationship for Core 0.
                </p>
              </div>
            </PanelSectionRow>

            {/* Display curve for core 0 */}
            {state.frequencyCurves[0] && (
              <PanelSectionRow>
                <div style={{
                  background: "rgba(61, 68, 80, 0.5)",
                  borderRadius: "8px",
                  padding: "16px",
                  marginBottom: "12px",
                }}>
                  <div style={{ marginBottom: "12px" }}>
                    <span style={{ color: "#8b929a", fontSize: "11px", fontWeight: "bold" }}>
                      Core 0 Frequency Curve
                    </span>
                  </div>
                  <FrequencyCurveChart
                    curve={state.frequencyCurves[0]}
                    height={300}
                  />
                  <div style={{ marginTop: "12px", fontSize: "10px", color: "#8b929a" }}>
                    <div style={{ marginBottom: "4px" }}>
                      • <span style={{ color: "#4caf50" }}>Green circles</span>: Stable frequency points
                    </div>
                    {state.frequencyCurves[0].points.some(p => !p.stable) && (
                      <div style={{ marginBottom: "4px" }}>
                        • <span style={{ color: "#f44336" }}>Red crosses</span>: Failed frequency points
                      </div>
                    )}
                    <div style={{ marginBottom: "4px" }}>
                      • <span style={{ color: "#1a9fff" }}>Blue line</span>: Interpolated voltage curve
                    </div>
                  </div>
                </div>
              </PanelSectionRow>
            )}

            {/* Apply curve button - Requirement: 6.3 */}
            {!state.frequencyModeEnabled && (
              <PanelSectionRow>
                <ButtonItem
                  layout="below"
                  onClick={handleApply}
                  disabled={isApplying}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    {isApplying ? (
                      <>
                        <FaSpinner style={{ animation: "spin 1s linear infinite" }} />
                        <span>Applying...</span>
                      </>
                    ) : (
                      <>
                        <FaBolt />
                        <span>Apply Curve & Enable Frequency Mode</span>
                      </>
                    )}
                  </div>
                </ButtonItem>
              </PanelSectionRow>
            )}

            {state.frequencyModeEnabled && (
              <PanelSectionRow>
                <div style={{
                  background: "rgba(76, 175, 80, 0.1)",
                  border: "1px solid #4caf50",
                  borderRadius: "6px",
                  padding: "10px",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <FaCheck style={{ color: "#4caf50", fontSize: "14px" }} />
                    <span style={{ color: "#4caf50", fontSize: "11px", fontWeight: "bold" }}>
                      Frequency Mode Active
                    </span>
                  </div>
                  <p style={{ fontSize: "10px", color: "#ccc", margin: "6px 0 0 0" }}>
                    Voltage is being adjusted automatically based on CPU frequency.
                  </p>
                </div>
              </PanelSectionRow>
            )}
          </PanelSection>
        )}
      </PanelSection>
    </>
  );
};

export default FrequencyWizard;
