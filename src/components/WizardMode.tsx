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
} from "@decky/ui";
import { FaLeaf, FaBalanceScale, FaBatteryFull, FaRocket, FaCheck, FaTimes, FaSpinner, FaExclamationTriangle } from "react-icons/fa";
import { useAutotune, usePlatformInfo, useDeckTune } from "../context";
import { AutotuneProgress, AutotuneResult, Preset } from "../api/types";

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
          borderRadius: "8px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            color: "#fff",
            fontWeight: "bold",
          }}
        >
          {isPanicking ? (
            <>
              <FaSpinner className="spin" />
              <span>Disabling...</span>
            </>
          ) : (
            <>
              <FaExclamationTriangle />
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
 * Requirements: 4.5, 5.4, 6.1
 */
export const WizardMode: FC<WizardModeProps> = ({ onComplete, onCancel }) => {
  const [step, setStep] = useState<WizardStep>(1);
  const [selectedGoal, setSelectedGoal] = useState<WizardGoal | null>(null);
  const { progress, result, isRunning, start, stop } = useAutotune();
  const { info: platformInfo } = usePlatformInfo();
  const { api, state } = useDeckTune();

  // Handle autotune completion - move to step 3
  useEffect(() => {
    if (result && step === 2) {
      setStep(3);
    }
  }, [result, step]);

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
   * Handle cancel button click.
   * Requirements: 6.3
   */
  const handleCancel = async () => {
    if (isRunning) {
      await stop();
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

      {/* Step indicator */}
      <PanelSectionRow>
        <StepIndicator currentStep={step} />
      </PanelSectionRow>

      {/* Step 1: Goal Selection */}
      {step === 1 && (
        <GoalSelectionStep
          onSelect={handleGoalSelect}
          platformInfo={platformInfo}
        />
      )}

      {/* Step 2: Autotune Progress */}
      {step === 2 && (
        <AutotuneProgressStep
          progress={progress}
          isRunning={isRunning}
          onCancel={handleCancel}
          selectedGoal={selectedGoal}
        />
      )}

      {/* Step 3: Results Display */}
      {step === 3 && result && (
        <ResultsStep
          result={result}
          platformInfo={platformInfo}
          onApplyAndSave={handleApplyAndSave}
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
    <Focusable style={{ display: "flex", justifyContent: "center", gap: "16px", marginBottom: "16px" }}>
      {steps.map((s, index) => (
        <div
          key={s.num}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <div
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: currentStep >= s.num ? "#1a9fff" : "#3d4450",
              color: currentStep >= s.num ? "#fff" : "#8b929a",
              fontWeight: "bold",
              fontSize: "14px",
            }}
          >
            {currentStep > s.num ? <FaCheck size={12} /> : s.num}
          </div>
          <span
            style={{
              color: currentStep >= s.num ? "#fff" : "#8b929a",
              fontSize: "12px",
            }}
          >
            {s.label}
          </span>
          {index < steps.length - 1 && (
            <div
              style={{
                width: "24px",
                height: "2px",
                backgroundColor: currentStep > s.num ? "#1a9fff" : "#3d4450",
                marginLeft: "8px",
              }}
            />
          )}
        </div>
      ))}
    </Focusable>
  );
};

/**
 * Step 1: Goal Selection component.
 * Requirements: 5.4, 6.2
 */
interface GoalSelectionStepProps {
  onSelect: (goal: WizardGoal) => void;
  platformInfo: { model: string; variant: string; safe_limit: number } | null;
}

const GoalSelectionStep: FC<GoalSelectionStepProps> = ({ onSelect, platformInfo }) => {
  const { state } = useDeckTune();
  const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;

  return (
    <>
      {platformInfo && (
        <PanelSectionRow>
          <div style={{ fontSize: "12px", color: "#8b929a", marginBottom: "8px" }}>
            Detected: {platformInfo.variant} ({platformInfo.model}) • Safe limit: {platformInfo.safe_limit}
          </div>
        </PanelSectionRow>
      )}
      
      {/* Show current game info if running (Requirement 5.4) */}
      {isGameRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "#1a3a5c",
              borderRadius: "6px",
              marginBottom: "12px",
              fontSize: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaRocket style={{ color: "#1a9fff" }} />
              <span>
                Running: <strong>{state.runningAppName}</strong>
              </span>
            </div>
            <div style={{ fontSize: "10px", color: "#8b929a", marginTop: "4px" }}>
              Tuning will be saved as a preset for this game
            </div>
          </div>
        </PanelSectionRow>
      )}
      
      <PanelSectionRow>
        <div style={{ fontSize: "14px", marginBottom: "12px" }}>
          Select your tuning goal:
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
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Icon />
                <span>{goal.label}</span>
                <span style={{ fontSize: "10px", color: "#8b929a", marginLeft: "auto" }}>
                  {goal.mode === "thorough" ? "~10 min" : "~3 min"}
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

export default WizardMode;
