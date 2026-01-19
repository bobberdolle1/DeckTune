/**
 * WizardMode component for DeckTune.
 * 
 * Feature: decktune, Frontend UI Components - Wizard Mode
 * Requirements: 4.5, 6.1, 6.2, 6.3, 6.4, 6.5
 * 
 * Provides a 3-step wizard interface for beginner users:
 * - Step 1: Goal selection (Quiet/Cool, Balanced, Max Battery, Max Performance)
 * - Step 2: Autotune progress with phase, core, ETA
 * - Step 3: Results display with per-core values and Apply & Save
 * - Panic Disable button: Always visible emergency reset (Requirement 4.5)
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  ProgressBarWithInfo,
  Focusable,
  SliderField,
} from "@decky/ui";
import { FaLeaf, FaBalanceScale, FaBatteryFull, FaRocket, FaCheck, FaTimes, FaSpinner, FaExclamationTriangle, FaExclamationCircle, FaMicrochip, FaCog, FaVial } from "react-icons/fa";
import { useAutotune, usePlatformInfo, useDeckTune, useBinaries, useBinning } from "../context";
import { AutotuneProgress, AutotuneResult, Preset, BinningConfig } from "../api/types";

/**
 * Wizard goal options for Step 1.
 * Requirements: 6.2
 */
export type WizardGoal = "quiet_cool" | "balanced" | "max_battery" | "max_performance";

interface GoalOption {
  id: WizardGoal;
  label: string;
  description: string;
  icon: FC;
  mode: "quick" | "thorough";
}

const GOAL_OPTIONS: GoalOption[] = [
  {
    id: "quiet_cool",
    label: "Quiet/Cool",
    description: "Lower temperatures and fan noise",
    icon: FaLeaf,
    mode: "quick",
  },
  {
    id: "balanced",
    label: "Balanced",
    description: "Good balance of performance and efficiency",
    icon: FaBalanceScale,
    mode: "quick",
  },
  {
    id: "max_battery",
    label: "Max Battery",
    description: "Maximize battery life",
    icon: FaBatteryFull,
    mode: "thorough",
  },
  {
    id: "max_performance",
    label: "Max Performance",
    description: "Find the most aggressive stable undervolt",
    icon: FaRocket,
    mode: "thorough",
  },
];

/**
 * Wizard step type.
 */
type WizardStep = 1 | 2 | 3;

/**
 * Props for WizardMode component.
 */
interface WizardModeProps {
  onComplete?: (result: AutotuneResult) => void;
  onCancel?: () => void;
}

/**
 * Panic Disable Button component - always visible emergency reset.
 * Requirements: 4.5
 * 
 * Features:
 * - Always visible red button
 * - Immediate reset to 0 on click
 */
const PanicDisableButton: FC = () => {
  const { api } = useDeckTune();
  const [isPanicking, setIsPanicking] = useState(false);

  const handlePanicDisable = async () => {
    setIsPanicking(true);
    try {
      await api.panicDisable();
    } finally {
      setIsPanicking(false);
    }
  };

  return (
    <PanelSectionRow>
      <ButtonItem
        layout="below"
        onClick={handlePanicDisable}
        disabled={isPanicking}
        style={{
          backgroundColor: "#b71c1c",
          borderRadius: "4px",
          minHeight: "30px",
          padding: "4px 6px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "4px",
            color: "#fff",
            fontWeight: "bold",
            fontSize: "11px",
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" size={10} />
              <span>Disabling...</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle size={10} />
              <span>PANIC DISABLE</span>
            </>
          )}
        </div>
      </ButtonItem>
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
};

/**
 * WizardMode component - 3-step wizard for beginner users.
 * Requirements: 4.5, 5.4, 6.1, 8.1
 */
export const WizardMode: FC<WizardModeProps> = ({ onComplete, onCancel }) => {
  const [step, setStep] = useState<WizardStep>(1);
  const [selectedGoal, setSelectedGoal] = useState<WizardGoal | null>(null);
  const { progress, result, isRunning, start, stop } = useAutotune();
  const { progress: binningProgress, result: binningResult, isRunning: isBinningRunning, start: startBinning, stop: stopBinning } = useBinning();
  const { info: platformInfo } = usePlatformInfo();
  const { api, state } = useDeckTune();
  const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();

  // Check binaries on mount
  useEffect(() => {
    checkBinaries();
  }, []);

  // Handle autotune completion - move to step 3
  useEffect(() => {
    if (result && step === 2) {
      setStep(3);
    }
  }, [result, step]);

  // Handle binning completion - move to step 3
  useEffect(() => {
    if (binningResult && step === 2) {
      setStep(3);
    }
  }, [binningResult, step]);

  /**
   * Handle goal selection and start autotune.
   * Requirements: 6.2, 6.3
   */
  const handleGoalSelect = async (goal: WizardGoal) => {
    setSelectedGoal(goal);
    const goalOption = GOAL_OPTIONS.find((g) => g.id === goal);
    if (goalOption) {
      setStep(2);
      await start(goalOption.mode);
    }
  };

  /**
   * Handle binning button click.
   * Requirements: 8.1
   */
  const handleBinningClick = async () => {
    setSelectedGoal(null);
    setStep(2);
    await startBinning();
  };

  /**
   * Handle benchmark button click.
   * Requirements: 7.1, 7.4
   */
  const handleBenchmarkClick = async () => {
    await api.runBenchmark();
  };

  /**
   * Handle cancel button click.
   * Requirements: 6.3, 8.1
   */
  const handleCancel = async () => {
    if (isRunning) {
      await stop();
    }
    if (isBinningRunning) {
      await stopBinning();
    }
    setStep(1);
    setSelectedGoal(null);
    onCancel?.();
  };

  /**
   * Handle Apply & Save button click.
   * Requirements: 5.4, 6.4
   * 
   * If a game is running, saves the result as a game-specific preset.
   */
  const handleApplyAndSave = async () => {
    if (result) {
      // Check if a game is running - save as game preset (Requirement 5.4)
      if (state.runningAppId && state.runningAppName) {
        const preset: Preset = {
          app_id: state.runningAppId,
          label: state.runningAppName,
          value: result.cores,
          timeout: 0,
          use_timeout: false,
          created_at: new Date().toISOString(),
          tested: true,
        };
        
        await api.saveAndApply(result.cores, true, preset);
      } else {
        // No game running - apply as global values
        await api.applyUndervolt(result.cores);
      }
      
      onComplete?.(result);
    }
  };

  /**
   * Handle Apply Recommended button click for binning results.
   * Requirements: 8.4
   */
  const handleApplyBinningResult = async () => {
    if (binningResult) {
      // Apply the recommended value (max_stable + 5mV safety margin)
      const cores = [binningResult.recommended, binningResult.recommended, binningResult.recommended, binningResult.recommended];
      
      // Check if a game is running - save as game preset
      if (state.runningAppId && state.runningAppName) {
        const preset: Preset = {
          app_id: state.runningAppId,
          label: state.runningAppName,
          value: cores,
          timeout: 0,
          use_timeout: false,
          created_at: new Date().toISOString(),
          tested: true,
        };
        
        await api.saveAndApply(cores, true, preset);
      } else {
        // No game running - apply as global values
        await api.applyUndervolt(cores);
      }
    }
  };

  /**
   * Reset wizard to start over.
   */
  const handleStartOver = () => {
    setStep(1);
    setSelectedGoal(null);
  };

  return (
    <PanelSection title="DeckTune Wizard">
      {/* Panic Disable Button - Always visible at top (Requirement 4.5) */}
      <PanicDisableButton />

      {/* Missing Binaries Warning */}
      {hasMissing && (
        <PanelSectionRow>
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "10px",
              padding: "12px",
              backgroundColor: "#5c4813",
              borderRadius: "8px",
              marginBottom: "12px",
              border: "1px solid #ff9800",
            }}
          >
            <FaExclamationCircle style={{ color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" }} />
            <div>
              <div style={{ fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" }}>
                Missing Components
              </div>
              <div style={{ fontSize: "12px", color: "#ffe0b2" }}>
                Required tools not found: <strong>{missingBinaries.join(", ")}</strong>
              </div>
              <div style={{ fontSize: "11px", color: "#ffcc80", marginTop: "4px" }}>
                Autotune and stress tests are unavailable. Please reinstall the plugin or add missing binaries to bin/ folder.
              </div>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Step indicator */}
      <PanelSectionRow>
        <StepIndicator currentStep={step} />
      </PanelSectionRow>

      {/* Step 1: Goal Selection */}
      {step === 1 && (
        <GoalSelectionStep
          onSelect={handleGoalSelect}
          onBinningClick={handleBinningClick}
          onBenchmarkClick={handleBenchmarkClick}
          platformInfo={platformInfo}
          disabled={hasMissing}
          isBinningRunning={isBinningRunning}
        />
      )}

      {/* Step 2: Autotune or Binning Progress */}
      {step === 2 && !isBinningRunning && (
        <AutotuneProgressStep
          progress={progress}
          isRunning={isRunning}
          onCancel={handleCancel}
          selectedGoal={selectedGoal}
        />
      )}

      {/* Step 2: Binning Progress */}
      {step === 2 && isBinningRunning && (
        <BinningProgressStep
          progress={binningProgress}
          isRunning={isBinningRunning}
          onCancel={handleCancel}
        />
      )}

      {/* Step 3: Results Display */}
      {step === 3 && result && !binningResult && (
        <ResultsStep
          result={result}
          platformInfo={platformInfo}
          onApplyAndSave={handleApplyAndSave}
          onStartOver={handleStartOver}
        />
      )}

      {/* Step 3: Binning Results Display */}
      {step === 3 && binningResult && (
        <BinningResultsStep
          result={binningResult}
          platformInfo={platformInfo}
          onApplyRecommended={handleApplyBinningResult}
          onStartOver={handleStartOver}
        />
      )}
    </PanelSection>
  );
};


/**
 * Step indicator component showing current wizard progress.
 */
interface StepIndicatorProps {
  currentStep: WizardStep;
}

const StepIndicator: FC<StepIndicatorProps> = ({ currentStep }) => {
  const steps = [
    { num: 1, label: "Goal" },
    { num: 2, label: "Tuning" },
    { num: 3, label: "Results" },
  ];

  return (
    <Focusable style={{ display: "flex", justifyContent: "center", gap: "8px", marginBottom: "8px", padding: "2px 0" }}>
      {steps.map((s, index) => (
        <div
          key={s.num}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          <div
            style={{
              width: "22px",
              height: "22px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: currentStep >= s.num ? "#1a9fff" : "#3d4450",
              color: currentStep >= s.num ? "#fff" : "#8b929a",
              fontWeight: "bold",
              fontSize: "11px",
            }}
          >
            {currentStep > s.num ? <FaCheck size={9} /> : s.num}
          </div>
          <span
            style={{
              color: currentStep >= s.num ? "#fff" : "#8b929a",
              fontSize: "10px",
            }}
          >
            {s.label}
          </span>
          {index < steps.length - 1 && (
            <div
              style={{
                width: "16px",
                height: "2px",
                backgroundColor: currentStep > s.num ? "#1a9fff" : "#3d4450",
                marginLeft: "4px",
              }}
            />
          )}
        </div>
      ))}
    </Focusable>
  );
};

/**
 * Compact Binning Configuration Panel - inline expandable settings.
 * Requirements: 10.1, 10.2, 10.3, 10.4
 */
interface BinningConfigPanelProps {
  config: BinningConfig | null;
  onSave: (config: Partial<BinningConfig>) => Promise<void>;
  isExpanded: boolean;
  onToggle: () => void;
}

const BinningConfigPanel: FC<BinningConfigPanelProps> = ({ config, onSave, isExpanded, onToggle }) => {
  const [testDuration, setTestDuration] = useState(config?.test_duration || 60);
  const [stepSize, setStepSize] = useState(config?.step_size || 5);
  const [startValue, setStartValue] = useState(config?.start_value || -10);

  // Default values
  const DEFAULT_TEST_DURATION = 60;
  const DEFAULT_STEP_SIZE = 5;
  const DEFAULT_START_VALUE = -10;

  // Update local state when config changes
  useEffect(() => {
    if (config) {
      setTestDuration(config.test_duration || DEFAULT_TEST_DURATION);
      setStepSize(config.step_size || DEFAULT_STEP_SIZE);
      setStartValue(config.start_value || DEFAULT_START_VALUE);
    }
  }, [config]);

  const handleSave = async () => {
    await onSave({
      test_duration: testDuration,
      step_size: stepSize,
      start_value: startValue,
    });
  };

  const handleReset = () => {
    setTestDuration(DEFAULT_TEST_DURATION);
    setStepSize(DEFAULT_STEP_SIZE);
    setStartValue(DEFAULT_START_VALUE);
  };

  if (!isExpanded) return null;

  return (
    <div
      style={{
        padding: "4px",
        backgroundColor: "#1a1d24",
        borderRadius: "4px",
        marginTop: "4px",
        border: "1px solid #3d4450",
        maxWidth: "100%",
        overflow: "hidden",
      }}
    >
      <div style={{ fontSize: "9px", fontWeight: "bold", marginBottom: "4px", color: "#8b929a" }}>
        Advanced Settings
      </div>

      {/* Sliders container - ultra compact */}
      <div style={{ maxWidth: "100%", paddingRight: "2px" }}>
        {/* Test Duration */}
        <div style={{ marginBottom: "2px" }}>
          <div style={{ fontSize: "8px", color: "#8b929a", marginBottom: "1px" }}>
            Test Duration: {testDuration}s
          </div>
          <SliderField
            label=""
            description=""
            value={testDuration}
            min={30}
            max={300}
            step={10}
            onChange={(value: number) => setTestDuration(value)}
            showValue={false}
            bottomSeparator="none"
          />
        </div>

        {/* Step Size */}
        <div style={{ marginBottom: "2px" }}>
          <div style={{ fontSize: "8px", color: "#8b929a", marginBottom: "1px" }}>
            Step Size: {stepSize}mV
          </div>
          <SliderField
            label=""
            description=""
            value={stepSize}
            min={1}
            max={10}
            step={1}
            onChange={(value: number) => setStepSize(value)}
            showValue={false}
            bottomSeparator="none"
          />
        </div>

        {/* Starting Value */}
        <div style={{ marginBottom: "2px" }}>
          <div style={{ fontSize: "8px", color: "#8b929a", marginBottom: "1px" }}>
            Start Value: {startValue}mV
          </div>
          <SliderField
            label=""
            description=""
            value={startValue}
            min={-20}
            max={0}
            step={1}
            onChange={(value: number) => setStartValue(value)}
            showValue={false}
            bottomSeparator="none"
          />
        </div>
      </div>

      {/* Action buttons - vertical layout */}
      <div style={{ display: "flex", flexDirection: "column", gap: "2px", marginTop: "4px" }}>
        {/* Save button */}
        <ButtonItem
          layout="below"
          onClick={handleSave}
          style={{ minHeight: "24px", padding: "2px 4px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "3px", color: "#4caf50", fontSize: "9px" }}>
            <FaCheck style={{ fontSize: "8px" }} />
            <span>Save</span>
          </div>
        </ButtonItem>

        {/* Reset to Defaults button */}
        <ButtonItem
          layout="below"
          onClick={handleReset}
          style={{ minHeight: "24px", padding: "2px 4px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "3px", color: "#ff9800", fontSize: "9px" }}>
            <FaTimes style={{ fontSize: "8px" }} />
            <span>Reset</span>
          </div>
        </ButtonItem>
      </div>
    </div>
  );
};

/**
 * Step 1: Goal Selection component.
 * Requirements: 5.4, 6.2, 8.1, 10.1
 */
interface GoalSelectionStepProps {
  onSelect: (goal: WizardGoal) => void;
  onBinningClick: () => void;
  onBenchmarkClick: () => void;
  platformInfo: { model: string; variant: string; safe_limit: number } | null;
  disabled?: boolean;
  isBinningRunning?: boolean;
}

const GoalSelectionStep: FC<GoalSelectionStepProps> = ({ onSelect, onBinningClick, onBenchmarkClick, platformInfo, disabled = false, isBinningRunning = false }) => {
  const { state } = useDeckTune();
  const { config, getConfig, updateConfig } = useBinning();
  const [showConfig, setShowConfig] = useState(false);
  const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;

  // Load config on mount
  useEffect(() => {
    getConfig();
  }, []);

  const handleConfigToggle = () => {
    setShowConfig(!showConfig);
  };

  const handleConfigSave = async (newConfig: Partial<BinningConfig>) => {
    await updateConfig(newConfig);
    setShowConfig(false);
  };

  return (
    <>
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "10px", color: "#8b929a", marginBottom: "4px", padding: "2px 0" }}>
            {platformInfo.variant} ({platformInfo.model}) • Limit: {platformInfo.safe_limit}mV
          </div>
        </PanelSectionRow>
      )}
      
      {/* Show current game info if running (Requirement 5.4) */}
      {isGameRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "4px 6px",
              backgroundColor: "#1a3a5c",
              borderRadius: "4px",
              marginBottom: "6px",
              fontSize: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <FaRocket style={{ color: "#1a9fff", fontSize: "9px" }} />
              <span>
                Running: <strong>{state.runningAppName}</strong>
              </span>
            </div>
            <div style={{ fontSize: "9px", color: "#8b929a", marginTop: "2px" }}>
              Tuning will be saved as preset for this game
            </div>
          </div>
        </PanelSectionRow>
      )}
      
      {/* Binning Button - Requirements: 8.1 */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onBinningClick}
          disabled={disabled || isBinningRunning}
          description="Auto-discover max stable undervolt"
          style={{ minHeight: "32px", padding: "4px 6px" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "4px", opacity: (disabled || isBinningRunning) ? 0.5 : 1, fontSize: "11px" }}>
            <FaMicrochip style={{ color: "#ff9800", fontSize: "10px" }} />
            <span>Find Max Undervolt</span>
            <span style={{ fontSize: "9px", color: "#8b929a", marginLeft: "auto" }}>
              ~5-15m
            </span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Binning Settings Button */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleConfigToggle}
          disabled={disabled || isBinningRunning}
          style={{ marginTop: "4px", minHeight: "28px", padding: "2px 4px" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "4px", opacity: (disabled || isBinningRunning) ? 0.5 : 1, fontSize: "10px", color: "#8b929a" }}>
            <FaCog style={{ fontSize: "9px" }} />
            <span>{showConfig ? "Hide Settings" : "Binning Settings"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Inline Config Panel */}
      <PanelSectionRow>
        <BinningConfigPanel
          config={config}
          onSave={handleConfigSave}
          isExpanded={showConfig}
          onToggle={handleConfigToggle}
        />
      </PanelSectionRow>
      
      {/* Run Benchmark button - Requirements: 7.1, 7.4 */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onBenchmarkClick}
          disabled={disabled || isBinningRunning || state.isBenchmarkRunning}
          description="Run 10-sec performance benchmark"
          style={{ marginTop: "4px", minHeight: "32px", padding: "4px 6px" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "4px", opacity: (disabled || isBinningRunning || state.isBenchmarkRunning) ? 0.5 : 1, fontSize: "11px" }}>
            {state.isBenchmarkRunning ? (
              <>
                <FaSpinner className="spin" style={{ color: "#4caf50", fontSize: "10px" }} />
                <span>Running...</span>
              </>
            ) : (
              <>
                <FaVial style={{ color: "#4caf50", fontSize: "10px" }} />
                <span>Run Benchmark</span>
              </>
            )}
            <span style={{ fontSize: "9px", color: "#8b929a", marginLeft: "auto" }}>
              10s
            </span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Benchmark Progress - Requirements: 7.4 */}
      {state.isBenchmarkRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "6px",
              backgroundColor: "#1b5e20",
              borderRadius: "4px",
              marginTop: "4px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "4px", marginBottom: "4px", fontSize: "10px" }}>
              <FaSpinner className="spin" style={{ color: "#4caf50", fontSize: "9px" }} />
              <span style={{ fontWeight: "bold" }}>Running benchmark...</span>
            </div>
            <div style={{ fontSize: "9px", color: "#a5d6a7", textAlign: "center" }}>
              Testing performance (~10 seconds)
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Benchmark Result Display - Requirements: 7.3, 7.5 */}
      {state.lastBenchmarkResult && !state.isBenchmarkRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "6px",
              backgroundColor: "#1b5e20",
              borderRadius: "4px",
              marginTop: "4px",
              borderLeft: "3px solid #4caf50",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px", fontSize: "10px" }}>
              <span style={{ fontWeight: "bold" }}>Benchmark Complete</span>
              <FaCheck style={{ color: "#4caf50", fontSize: "9px" }} />
            </div>
            
            {/* Score */}
            <div style={{ marginBottom: "4px" }}>
              <div style={{ fontSize: "9px", color: "#a5d6a7" }}>Score</div>
              <div style={{ fontSize: "14px", fontWeight: "bold", color: "#4caf50" }}>
                {state.lastBenchmarkResult.score.toFixed(2)} bogo ops/s
              </div>
            </div>

            {/* Comparison with previous run */}
            {state.benchmarkHistory && state.benchmarkHistory.length > 1 && (() => {
              const current = state.benchmarkHistory[0];
              const previous = state.benchmarkHistory[1];
              const scoreDiff = current.score - previous.score;
              const percentChange = ((scoreDiff / previous.score) * 100);
              const improvement = scoreDiff > 0;
              
              return (
                <div style={{ marginTop: "4px", paddingTop: "4px", borderTop: "1px solid #2e7d32" }}>
                  <div style={{ fontSize: "9px", color: "#a5d6a7", marginBottom: "2px" }}>
                    vs Previous
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    {improvement ? (
                      <FaCheck style={{ color: "#4caf50", fontSize: "9px" }} />
                    ) : (
                      <FaTimes style={{ color: "#ff6b6b", fontSize: "9px" }} />
                    )}
                    <span style={{ fontSize: "10px", color: improvement ? "#4caf50" : "#ff6b6b", fontWeight: "bold" }}>
                      {improvement ? "+" : ""}{percentChange.toFixed(2)}%
                    </span>
                    <span style={{ fontSize: "9px", color: "#a5d6a7" }}>
                      {improvement ? "improvement" : "degradation"}
                    </span>
                  </div>
                </div>
              );
            })()}
          </div>
        </PanelSectionRow>
      )}
      
      <PanelSectionRow>
        <div style={{ fontSize: "11px", marginBottom: "6px", marginTop: "6px" }}>
          Or select your tuning goal:
        </div>
      </PanelSectionRow>
      {GOAL_OPTIONS.map((goal) => {
        const Icon = goal.icon;
        return (
          <PanelSectionRow key={goal.id}>
            <ButtonItem
              layout="below"
              onClick={() => onSelect(goal.id)}
              description={goal.description}
              disabled={disabled || isBinningRunning}
              style={{ minHeight: "32px", padding: "4px 6px" }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "4px", opacity: (disabled || isBinningRunning) ? 0.5 : 1, fontSize: "11px" }}>
                <Icon size={10} />
                <span>{goal.label}</span>
                <span style={{ fontSize: "9px", color: "#8b929a", marginLeft: "auto" }}>
                  {goal.mode === "thorough" ? "~10m" : "~3m"}
                </span>
              </div>
            </ButtonItem>
          </PanelSectionRow>
        );
      })}
    </>
  );
};


/**
 * Step 2: Autotune Progress component.
 * Requirements: 6.3
 */
interface AutotuneProgressStepProps {
  progress: AutotuneProgress | null;
  isRunning: boolean;
  onCancel: () => void;
  selectedGoal: WizardGoal | null;
}

const AutotuneProgressStep: FC<AutotuneProgressStepProps> = ({
  progress,
  isRunning,
  onCancel,
  selectedGoal,
}) => {
  const goalLabel = GOAL_OPTIONS.find((g) => g.id === selectedGoal)?.label || "Unknown";
  
  // Calculate progress percentage
  const calculateProgress = (): number => {
    if (!progress) return 0;
    // Phase A: cores 0-3 (0-50%), Phase B: cores 0-3 (50-100%)
    const phaseOffset = progress.phase === "B" ? 50 : 0;
    const coreProgress = (progress.core / 4) * 50;
    return Math.min(phaseOffset + coreProgress, 100);
  };

  // Format ETA
  const formatEta = (seconds: number): string => {
    if (seconds <= 0) return "Almost done...";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
      return `${mins}m ${secs}s remaining`;
    }
    return `${secs}s remaining`;
  };

  return (
    <>
      <PanelSectionRow>
        <div style={{ textAlign: "center", marginBottom: "16px" }}>
          <FaSpinner
            style={{
              animation: "spin 1s linear infinite",
              fontSize: "24px",
              color: "#1a9fff",
            }}
          />
          <style>
            {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
          </style>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Tuning for: {goalLabel}
        </div>
      </PanelSectionRow>

      {progress && (
        <>
          <PanelSectionRow>
            <ProgressBarWithInfo
              label={`Phase ${progress.phase} - Core ${progress.core}`}
              description={`Testing value: ${progress.value}`}
              nProgress={calculateProgress()}
              sOperationText={formatEta(progress.eta)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "12px",
                color: "#8b929a",
                marginTop: "8px",
              }}
            >
              <span>Phase: {progress.phase === "A" ? "Coarse Search" : "Fine Tuning"}</span>
              <span>Core: {progress.core + 1}/4</span>
            </div>
          </PanelSectionRow>
        </>
      )}

      {!progress && isRunning && (
        <PanelSectionRow>
          <div style={{ textAlign: "center", color: "#8b929a" }}>
            Initializing autotune...
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onCancel}
          style={{ marginTop: "16px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" }}>
            <FaTimes />
            <span>Cancel</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};


/**
 * Step 3: Results Display component.
 * Requirements: 6.4, 6.5
 */
interface ResultsStepProps {
  result: AutotuneResult;
  platformInfo: { model: string; variant: string; safe_limit: number } | null;
  onApplyAndSave: () => void;
  onStartOver: () => void;
}

const ResultsStep: FC<ResultsStepProps> = ({
  result,
  platformInfo,
  onApplyAndSave,
  onStartOver,
}) => {
  /**
   * Get color indicator based on value and stability.
   * Requirements: 6.5
   * - Green: stable/applied
   * - Yellow: moderate undervolt
   * - Red: aggressive undervolt near limit
   */
  const getValueColor = (value: number): string => {
    if (!platformInfo) return "#8b929a";
    const limit = platformInfo.safe_limit;
    const ratio = Math.abs(value) / Math.abs(limit);
    
    if (ratio < 0.5) return "#4caf50"; // Green - conservative
    if (ratio < 0.8) return "#ff9800"; // Yellow - moderate
    return "#f44336"; // Red - aggressive
  };

  /**
   * Get status label for value.
   */
  const getValueStatus = (value: number): string => {
    if (!platformInfo) return "";
    const limit = platformInfo.safe_limit;
    const ratio = Math.abs(value) / Math.abs(limit);
    
    if (ratio < 0.5) return "Conservative";
    if (ratio < 0.8) return "Moderate";
    return "Aggressive";
  };

  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <>
      {/* Status banner */}
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            padding: "12px",
            backgroundColor: result.stable ? "#1b5e20" : "#b71c1c",
            borderRadius: "8px",
            marginBottom: "16px",
          }}
        >
          {result.stable ? <FaCheck /> : <FaTimes />}
          <span style={{ fontWeight: "bold" }}>
            {result.stable ? "Tuning Complete!" : "Tuning Incomplete"}
          </span>
        </div>
      </PanelSectionRow>

      {/* Summary stats */}
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            fontSize: "12px",
            color: "#8b929a",
            marginBottom: "16px",
          }}
        >
          <span>Duration: {formatDuration(result.duration)}</span>
          <span>Tests: {result.tests_run}</span>
        </div>
      </PanelSectionRow>

      {/* Per-core values display */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Optimal Values Found:
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <Focusable
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "8px",
          }}
        >
          {result.cores.map((value, index) => (
            <div
              key={index}
              style={{
                padding: "12px",
                backgroundColor: "#23262e",
                borderRadius: "8px",
                borderLeft: `4px solid ${getValueColor(value)}`,
              }}
            >
              <div style={{ fontSize: "12px", color: "#8b929a" }}>
                Core {index}
              </div>
              <div
                style={{
                  fontSize: "20px",
                  fontWeight: "bold",
                  color: getValueColor(value),
                }}
              >
                {value}
              </div>
              <div style={{ fontSize: "10px", color: "#8b929a" }}>
                {getValueStatus(value)}
              </div>
            </div>
          ))}
        </Focusable>
      </PanelSectionRow>

      {/* Color legend */}
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "16px",
            fontSize: "10px",
            color: "#8b929a",
            marginTop: "8px",
          }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4caf50" }} />
            Conservative
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#ff9800" }} />
            Moderate
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#f44336" }} />
            Aggressive
          </span>
        </div>
      </PanelSectionRow>

      {/* Action buttons */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onApplyAndSave}
          style={{ marginTop: "16px" }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              color: "#4caf50",
            }}
          >
            <FaCheck />
            <span>Apply & Save</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onStartOver}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
            <span>Start Over</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};

/**
 * Step 2: Binning Progress component.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
 * 
 * Requirements: 8.1, 8.2
 */
interface BinningProgressStepProps {
  progress: any | null;
  isRunning: boolean;
  onCancel: () => void;
}

const BinningProgressStep: FC<BinningProgressStepProps> = ({
  progress,
  isRunning,
  onCancel,
}) => {
  // Format ETA
  const formatEta = (seconds: number): string => {
    if (seconds <= 0) return "Finishing...";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
      return `~${mins}m ${secs}s`;
    }
    return `~${secs}s`;
  };

  // Calculate progress percentage using max_iterations if available
  const calculateProgress = (): number => {
    if (!progress) return 0;
    if (progress.percent_complete !== undefined) {
      return progress.percent_complete;
    }
    // Fallback to old calculation
    const maxIterations = progress.max_iterations || 20;
    return Math.min((progress.iteration / maxIterations) * 100, 100);
  };

  return (
    <>
      <PanelSectionRow>
        <div style={{ textAlign: "center", marginBottom: "16px" }}>
          <FaSpinner
            style={{
              animation: "spin 1s linear infinite",
              fontSize: "24px",
              color: "#ff9800",
            }}
          />
          <style>
            {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
          </style>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Finding Maximum Undervolt
        </div>
      </PanelSectionRow>

      {progress && (
        <>
          <PanelSectionRow>
            <ProgressBarWithInfo
              label={`Iteration ${progress.iteration}/${progress.max_iterations || 20}`}
              description={`Testing: ${progress.current_value}mV`}
              nProgress={calculateProgress() / 100}
              sOperationText={formatEta(progress.eta)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "6px",
                fontSize: "12px",
                marginTop: "8px",
                padding: "8px",
                backgroundColor: "rgba(0, 0, 0, 0.2)",
                borderRadius: "4px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#8b929a" }}>Current Value:</span>
                <span style={{ fontWeight: "bold" }}>{progress.current_value}mV</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#8b929a" }}>Last Stable:</span>
                <span style={{ fontWeight: "bold", color: "#4caf50" }}>{progress.last_stable}mV</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#8b929a" }}>Remaining:</span>
                <span style={{ fontWeight: "bold" }}>{formatEta(progress.eta)}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#8b929a" }}>Progress:</span>
                <span style={{ fontWeight: "bold" }}>{calculateProgress().toFixed(1)}%</span>
              </div>
            </div>
          </PanelSectionRow>
        </>
      )}

      {!progress && isRunning && (
        <PanelSectionRow>
          <div style={{ textAlign: "center", color: "#8b929a" }}>
            Initializing binning...
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onCancel}
          style={{ marginTop: "16px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" }}>
            <FaTimes />
            <span>Stop</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};


/**
 * Step 3: Binning Results Display component.
 * Requirements: 8.4
 */
interface BinningResultsStepProps {
  result: any;
  platformInfo: { model: string; variant: string; safe_limit: number } | null;
  onApplyRecommended: () => void;
  onStartOver: () => void;
}

const BinningResultsStep: FC<BinningResultsStepProps> = ({
  result,
  platformInfo,
  onApplyRecommended,
  onStartOver,
}) => {
  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <>
      {/* Status banner */}
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            padding: "12px",
            backgroundColor: result.aborted ? "#b71c1c" : "#1b5e20",
            borderRadius: "8px",
            marginBottom: "16px",
          }}
        >
          {result.aborted ? <FaTimes /> : <FaCheck />}
          <span style={{ fontWeight: "bold" }}>
            {result.aborted ? "Binning Incomplete" : "Binning Complete!"}
          </span>
        </div>
      </PanelSectionRow>

      {/* Summary stats */}
      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            fontSize: "12px",
            color: "#8b929a",
            marginBottom: "16px",
          }}
        >
          <span>Duration: {formatDuration(result.duration)}</span>
          <span>Iterations: {result.iterations}</span>
        </div>
      </PanelSectionRow>

      {/* Results display */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          Discovered Values:
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          <div
            style={{
              padding: "16px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              borderLeft: `4px solid #ff9800`,
            }}
          >
            <div style={{ fontSize: "12px", color: "#8b929a" }}>
              Maximum Stable
            </div>
            <div
              style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: "#ff9800",
              }}
            >
              {result.max_stable}mV
            </div>
            <div style={{ fontSize: "10px", color: "#8b929a" }}>
              Most aggressive stable value found
            </div>
          </div>

          <div
            style={{
              padding: "16px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              borderLeft: `4px solid #4caf50`,
            }}
          >
            <div style={{ fontSize: "12px", color: "#8b929a" }}>
              Recommended (with 5mV safety margin)
            </div>
            <div
              style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: "#4caf50",
              }}
            >
              {result.recommended}mV
            </div>
            <div style={{ fontSize: "10px", color: "#8b929a" }}>
              Conservative value for daily use
            </div>
          </div>
        </Focusable>
      </PanelSectionRow>

      {/* Action buttons */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onApplyRecommended}
          style={{ marginTop: "16px" }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              color: "#4caf50",
            }}
          >
            <FaCheck />
            <span>Apply Recommended</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onStartOver}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
            <span>Start Over</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};

export default WizardMode;
