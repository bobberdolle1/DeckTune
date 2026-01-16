/**
 * SetupWizard component for DeckTune first-run experience.
 * 
 * Feature: decktune-3.1-reliability-ux, Setup Wizard
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
 * 
 * Provides a guided setup process for new users:
 * - Step 1: Welcome with introduction
 * - Step 2: Explanation of undervolting benefits/risks
 * - Step 3: Goal selection with estimates
 * - Step 4: Confirmation and completion
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  Focusable,
  ConfirmModal,
  showModal,
} from "@decky/ui";
import {
  FaLeaf,
  FaBalanceScale,
  FaBatteryFull,
  FaRocket,
  FaCheck,
  FaTimes,
  FaArrowRight,
  FaArrowLeft,
  FaInfoCircle,
  FaExclamationTriangle,
  FaBolt,
  FaThermometerHalf,
} from "react-icons/fa";
import { useDeckTune, usePlatformInfo } from "../context";

// ============================================================================
// Types and Interfaces
// Requirements: 5.3, 5.4
// ============================================================================

/**
 * Wizard step type.
 * Requirements: 5.1, 5.2, 5.3
 */
export type WizardStep = 'welcome' | 'explanation' | 'goal' | 'confirm' | 'complete';

/**
 * Goal type for wizard selection.
 * Requirements: 5.3
 */
export type SetupGoal = 'quiet' | 'balanced' | 'battery' | 'performance';

/**
 * Wizard state interface.
 * Requirements: 5.3, 5.4
 */
export interface WizardState {
  step: WizardStep;
  selectedGoal: SetupGoal | null;
}

/**
 * Goal estimate interface with battery and temperature improvements.
 * Requirements: 5.4
 */
export interface GoalEstimate {
  batteryImprovement: string;
  tempReduction: string;
  description: string;
}

/**
 * Wizard settings stored in backend.
 * Requirements: 5.5, 5.6
 */
export interface WizardSettings {
  first_run_complete: boolean;
  wizard_goal: SetupGoal | null;
  wizard_completed_at: string | null;
}

// ============================================================================
// Constants
// Requirements: 5.4
// ============================================================================

/**
 * Goal estimates for each preset goal.
 * Requirements: 5.4
 * 
 * These estimates are based on typical Steam Deck undervolting results.
 * Actual results vary based on silicon quality and workload.
 */
export const GOAL_ESTIMATES: Record<SetupGoal, GoalEstimate> = {
  quiet: {
    batteryImprovement: "+10-15%",
    tempReduction: "-8-12°C",
    description: "Prioritizes lower temperatures and quieter fan operation. Best for casual gaming and media consumption.",
  },
  balanced: {
    batteryImprovement: "+15-20%",
    tempReduction: "-5-8°C",
    description: "Good balance between performance, battery life, and thermals. Recommended for most users.",
  },
  battery: {
    batteryImprovement: "+20-30%",
    tempReduction: "-3-5°C",
    description: "Maximizes battery life with aggressive power savings. Ideal for long gaming sessions away from power.",
  },
  performance: {
    batteryImprovement: "+5-10%",
    tempReduction: "-2-4°C",
    description: "Finds the most aggressive stable undervolt for maximum efficiency. For users who want every bit of optimization.",
  },
};

/**
 * Goal display information.
 * Requirements: 5.3
 */
export const GOAL_INFO: Record<SetupGoal, { label: string; icon: FC; color: string }> = {
  quiet: {
    label: "Quiet/Cool",
    icon: FaLeaf,
    color: "#4caf50",
  },
  balanced: {
    label: "Balanced",
    icon: FaBalanceScale,
    color: "#2196f3",
  },
  battery: {
    label: "Max Battery",
    icon: FaBatteryFull,
    color: "#ff9800",
  },
  performance: {
    label: "Max Performance",
    icon: FaRocket,
    color: "#f44336",
  },
};


// ============================================================================
// Props Interfaces
// ============================================================================

/**
 * Props for SetupWizard component.
 */
export interface SetupWizardProps {
  onComplete?: (goal: SetupGoal) => void;
  onCancel?: () => void;
  onSkip?: () => void;
}

// ============================================================================
// Sub-components
// ============================================================================

/**
 * Step indicator showing wizard progress.
 */
interface StepIndicatorProps {
  currentStep: WizardStep;
}

const STEP_ORDER: WizardStep[] = ['welcome', 'explanation', 'goal', 'confirm'];

const StepIndicator: FC<StepIndicatorProps> = ({ currentStep }) => {
  const steps = [
    { id: 'welcome', label: 'Welcome' },
    { id: 'explanation', label: 'Learn' },
    { id: 'goal', label: 'Goal' },
    { id: 'confirm', label: 'Confirm' },
  ];

  const currentIndex = STEP_ORDER.indexOf(currentStep);

  return (
    <Focusable
      style={{
        display: "flex",
        justifyContent: "center",
        gap: "8px",
        marginBottom: "16px",
      }}
    >
      {steps.map((s, index) => (
        <div
          key={s.id}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          <div
            style={{
              width: "24px",
              height: "24px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: currentIndex >= index ? "#1a9fff" : "#3d4450",
              color: currentIndex >= index ? "#fff" : "#8b929a",
              fontWeight: "bold",
              fontSize: "12px",
            }}
          >
            {currentIndex > index ? <FaCheck size={10} /> : index + 1}
          </div>
          <span
            style={{
              color: currentIndex >= index ? "#fff" : "#8b929a",
              fontSize: "10px",
              display: index < steps.length - 1 ? "none" : "inline",
            }}
          >
            {s.label}
          </span>
          {index < steps.length - 1 && (
            <div
              style={{
                width: "16px",
                height: "2px",
                backgroundColor: currentIndex > index ? "#1a9fff" : "#3d4450",
              }}
            />
          )}
        </div>
      ))}
    </Focusable>
  );
};

/**
 * Welcome step component.
 * Requirements: 5.1
 */
interface WelcomeStepProps {
  onNext: () => void;
  onSkip: () => void;
}

const WelcomeStep: FC<WelcomeStepProps> = ({ onNext, onSkip }) => {
  return (
    <>
      <PanelSectionRow>
        <div
          style={{
            textAlign: "center",
            padding: "16px",
          }}
        >
          <FaBolt
            style={{
              fontSize: "48px",
              color: "#1a9fff",
              marginBottom: "16px",
            }}
          />
          <div
            style={{
              fontSize: "18px",
              fontWeight: "bold",
              marginBottom: "8px",
            }}
          >
            Welcome to DeckTune!
          </div>
          <div
            style={{
              fontSize: "13px",
              color: "#8b929a",
              lineHeight: "1.5",
            }}
          >
            Let's set up your Steam Deck for optimal performance and battery life.
            This wizard will guide you through the process.
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onNext}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              color: "#1a9fff",
            }}
          >
            <span>Get Started</span>
            <FaArrowRight />
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onSkip}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              color: "#8b929a",
              fontSize: "12px",
            }}
          >
            <span>Skip Setup</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};

/**
 * Explanation step component.
 * Requirements: 5.2
 */
interface ExplanationStepProps {
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const ExplanationStep: FC<ExplanationStepProps> = ({ onNext, onBack, onSkip }) => {
  return (
    <>
      <PanelSectionRow>
        <div
          style={{
            padding: "12px",
            backgroundColor: "#1a3a5c",
            borderRadius: "8px",
            marginBottom: "12px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "8px",
            }}
          >
            <FaInfoCircle style={{ color: "#1a9fff" }} />
            <span style={{ fontWeight: "bold" }}>What is Undervolting?</span>
          </div>
          <div
            style={{
              fontSize: "12px",
              color: "#b0bec5",
              lineHeight: "1.5",
            }}
          >
            Undervolting reduces the voltage supplied to your CPU while maintaining
            the same performance. This results in lower temperatures, quieter fans,
            and longer battery life.
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            gap: "8px",
            marginBottom: "12px",
          }}
        >
          <div
            style={{
              flex: 1,
              padding: "12px",
              backgroundColor: "#1b5e20",
              borderRadius: "8px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                marginBottom: "6px",
              }}
            >
              <FaCheck style={{ color: "#4caf50" }} />
              <span style={{ fontWeight: "bold", fontSize: "12px" }}>Benefits</span>
            </div>
            <ul
              style={{
                fontSize: "10px",
                color: "#a5d6a7",
                margin: 0,
                paddingLeft: "16px",
                lineHeight: "1.6",
              }}
            >
              <li>Lower temperatures</li>
              <li>Quieter fan operation</li>
              <li>Extended battery life</li>
              <li>Same performance</li>
            </ul>
          </div>

          <div
            style={{
              flex: 1,
              padding: "12px",
              backgroundColor: "#5c4813",
              borderRadius: "8px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                marginBottom: "6px",
              }}
            >
              <FaExclamationTriangle style={{ color: "#ff9800" }} />
              <span style={{ fontWeight: "bold", fontSize: "12px" }}>Risks</span>
            </div>
            <ul
              style={{
                fontSize: "10px",
                color: "#ffe0b2",
                margin: 0,
                paddingLeft: "16px",
                lineHeight: "1.6",
              }}
            >
              <li>System instability if too aggressive</li>
              <li>Requires testing</li>
              <li>Results vary by chip</li>
            </ul>
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            padding: "10px",
            backgroundColor: "#23262e",
            borderRadius: "6px",
            fontSize: "11px",
            color: "#8b929a",
            textAlign: "center",
          }}
        >
          <FaCheck style={{ color: "#4caf50", marginRight: "6px" }} />
          DeckTune includes automatic safety features and crash recovery.
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
          <ButtonItem layout="below" onClick={onBack} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              <FaArrowLeft />
              <span>Back</span>
            </div>
          </ButtonItem>
          <ButtonItem layout="below" onClick={onNext} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                color: "#1a9fff",
              }}
            >
              <span>Next</span>
              <FaArrowRight />
            </div>
          </ButtonItem>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onSkip}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#8b929a",
              fontSize: "12px",
            }}
          >
            <span>Skip Setup</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};


/**
 * Goal selection step component.
 * Requirements: 5.3, 5.4
 */
interface GoalStepProps {
  selectedGoal: SetupGoal | null;
  onSelectGoal: (goal: SetupGoal) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const GoalStep: FC<GoalStepProps> = ({
  selectedGoal,
  onSelectGoal,
  onNext,
  onBack,
  onSkip,
}) => {
  const goals: SetupGoal[] = ['quiet', 'balanced', 'battery', 'performance'];

  return (
    <>
      <PanelSectionRow>
        <div
          style={{
            fontSize: "14px",
            fontWeight: "bold",
            marginBottom: "8px",
          }}
        >
          Choose Your Goal
        </div>
        <div
          style={{
            fontSize: "11px",
            color: "#8b929a",
            marginBottom: "12px",
          }}
        >
          Select what matters most to you. You can change this later.
        </div>
      </PanelSectionRow>

      {goals.map((goal) => {
        const info = GOAL_INFO[goal];
        const estimate = GOAL_ESTIMATES[goal];
        const Icon = info.icon;
        const isSelected = selectedGoal === goal;

        return (
          <PanelSectionRow key={goal}>
            <ButtonItem
              layout="below"
              onClick={() => onSelectGoal(goal)}
              style={{
                border: isSelected ? `2px solid ${info.color}` : "2px solid transparent",
                borderRadius: "8px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "12px",
                  padding: "4px",
                }}
              >
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "8px",
                    backgroundColor: isSelected ? info.color : "#3d4450",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <Icon style={{ color: "#fff", fontSize: "16px" }} />
                </div>
                <div style={{ flex: 1, textAlign: "left" }}>
                  <div
                    style={{
                      fontWeight: "bold",
                      fontSize: "13px",
                      color: isSelected ? info.color : "#fff",
                    }}
                  >
                    {info.label}
                  </div>
                  <div
                    style={{
                      fontSize: "10px",
                      color: "#8b929a",
                      marginTop: "2px",
                    }}
                  >
                    {estimate.description.split('.')[0]}.
                  </div>
                </div>
                {isSelected && (
                  <FaCheck style={{ color: info.color, fontSize: "14px" }} />
                )}
              </div>
            </ButtonItem>
          </PanelSectionRow>
        );
      })}

      {/* Show estimates when goal is selected - Requirements: 5.4 */}
      {selectedGoal && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginTop: "8px",
            }}
          >
            <div
              style={{
                fontSize: "12px",
                fontWeight: "bold",
                marginBottom: "8px",
                color: GOAL_INFO[selectedGoal].color,
              }}
            >
              Estimated Improvements
            </div>
            <div
              style={{
                display: "flex",
                gap: "16px",
              }}
            >
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    marginBottom: "4px",
                  }}
                >
                  <FaBatteryFull style={{ color: "#4caf50", fontSize: "12px" }} />
                  <span style={{ fontSize: "10px", color: "#8b929a" }}>Battery</span>
                </div>
                <div
                  style={{
                    fontSize: "16px",
                    fontWeight: "bold",
                    color: "#4caf50",
                  }}
                >
                  {GOAL_ESTIMATES[selectedGoal].batteryImprovement}
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    marginBottom: "4px",
                  }}
                >
                  <FaThermometerHalf style={{ color: "#2196f3", fontSize: "12px" }} />
                  <span style={{ fontSize: "10px", color: "#8b929a" }}>Temperature</span>
                </div>
                <div
                  style={{
                    fontSize: "16px",
                    fontWeight: "bold",
                    color: "#2196f3",
                  }}
                >
                  {GOAL_ESTIMATES[selectedGoal].tempReduction}
                </div>
              </div>
            </div>
            <div
              style={{
                fontSize: "9px",
                color: "#666",
                marginTop: "8px",
                fontStyle: "italic",
              }}
            >
              * Actual results vary based on silicon quality and workload
            </div>
          </div>
        </PanelSectionRow>
      )}

      <PanelSectionRow>
        <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
          <ButtonItem layout="below" onClick={onBack} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              <FaArrowLeft />
              <span>Back</span>
            </div>
          </ButtonItem>
          <ButtonItem
            layout="below"
            onClick={onNext}
            disabled={!selectedGoal}
            style={{ flex: 1 }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                color: selectedGoal ? "#1a9fff" : "#8b929a",
                opacity: selectedGoal ? 1 : 0.5,
              }}
            >
              <span>Next</span>
              <FaArrowRight />
            </div>
          </ButtonItem>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onSkip}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#8b929a",
              fontSize: "12px",
            }}
          >
            <span>Skip Setup</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
};

/**
 * Confirmation step component.
 * Requirements: 5.5
 */
interface ConfirmStepProps {
  selectedGoal: SetupGoal;
  onConfirm: () => void;
  onBack: () => void;
  onCancel: () => void;
  isLoading: boolean;
}

const ConfirmStep: FC<ConfirmStepProps> = ({
  selectedGoal,
  onConfirm,
  onBack,
  onCancel,
  isLoading,
}) => {
  const info = GOAL_INFO[selectedGoal];
  const estimate = GOAL_ESTIMATES[selectedGoal];
  const Icon = info.icon;

  return (
    <>
      <PanelSectionRow>
        <div
          style={{
            textAlign: "center",
            padding: "16px",
          }}
        >
          <div
            style={{
              width: "64px",
              height: "64px",
              borderRadius: "50%",
              backgroundColor: info.color,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
            }}
          >
            <Icon style={{ color: "#fff", fontSize: "28px" }} />
          </div>
          <div
            style={{
              fontSize: "16px",
              fontWeight: "bold",
              marginBottom: "8px",
            }}
          >
            Ready to Start!
          </div>
          <div
            style={{
              fontSize: "12px",
              color: "#8b929a",
            }}
          >
            You've selected <strong style={{ color: info.color }}>{info.label}</strong>
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            padding: "12px",
            backgroundColor: "#23262e",
            borderRadius: "8px",
          }}
        >
          <div style={{ fontSize: "11px", color: "#8b929a", marginBottom: "8px" }}>
            What happens next:
          </div>
          <ul
            style={{
              fontSize: "11px",
              color: "#b0bec5",
              margin: 0,
              paddingLeft: "20px",
              lineHeight: "1.8",
            }}
          >
            <li>Your preferences will be saved</li>
            <li>DeckTune will be configured for your goal</li>
            <li>You can run autotune to find optimal values</li>
            <li>Settings can be changed anytime in Expert mode</li>
          </ul>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onConfirm}
          disabled={isLoading}
          style={{ marginTop: "12px" }}
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
            <span>{isLoading ? "Saving..." : "Complete Setup"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", gap: "8px" }}>
          <ButtonItem layout="below" onClick={onBack} disabled={isLoading} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              <FaArrowLeft />
              <span>Back</span>
            </div>
          </ButtonItem>
          <ButtonItem layout="below" onClick={onCancel} disabled={isLoading} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                color: "#ff6b6b",
              }}
            >
              <FaTimes />
              <span>Cancel</span>
            </div>
          </ButtonItem>
        </div>
      </PanelSectionRow>
    </>
  );
};


// ============================================================================
// Main Component
// Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
// ============================================================================

/**
 * SetupWizard component - guided first-run experience.
 * 
 * Requirements:
 * - 5.1: Display welcome wizard on first run
 * - 5.2: Explain undervolting benefits/risks
 * - 5.3: Offer preset goals with explanations
 * - 5.4: Show estimated improvements for selected goal
 * - 5.5: Save preferences on completion
 * - 5.6: Allow re-running wizard from settings
 * - 5.7: Allow skip/cancel without applying changes
 */
export const SetupWizard: FC<SetupWizardProps> = ({
  onComplete,
  onCancel,
  onSkip,
}) => {
  const { api } = useDeckTune();
  const { info: platformInfo } = usePlatformInfo();
  
  const [wizardState, setWizardState] = useState<WizardState>({
    step: 'welcome',
    selectedGoal: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Navigate to next step.
   */
  const goToNextStep = () => {
    const stepOrder: WizardStep[] = ['welcome', 'explanation', 'goal', 'confirm'];
    const currentIndex = stepOrder.indexOf(wizardState.step);
    if (currentIndex < stepOrder.length - 1) {
      setWizardState((prev) => ({
        ...prev,
        step: stepOrder[currentIndex + 1],
      }));
    }
  };

  /**
   * Navigate to previous step.
   */
  const goToPreviousStep = () => {
    const stepOrder: WizardStep[] = ['welcome', 'explanation', 'goal', 'confirm'];
    const currentIndex = stepOrder.indexOf(wizardState.step);
    if (currentIndex > 0) {
      setWizardState((prev) => ({
        ...prev,
        step: stepOrder[currentIndex - 1],
      }));
    }
  };

  /**
   * Handle goal selection.
   * Requirements: 5.3
   */
  const handleSelectGoal = (goal: SetupGoal) => {
    setWizardState((prev) => ({
      ...prev,
      selectedGoal: goal,
    }));
  };

  /**
   * Handle wizard completion.
   * Requirements: 5.5
   * 
   * Saves preferences and marks first_run_complete.
   */
  const handleComplete = async () => {
    if (!wizardState.selectedGoal) return;

    setIsLoading(true);
    setError(null);

    try {
      // Save wizard settings via RPC
      await api.saveSetting('wizard_goal', wizardState.selectedGoal);
      await api.saveSetting('wizard_completed_at', new Date().toISOString());
      await api.saveSetting('first_run_complete', true);

      setWizardState((prev) => ({
        ...prev,
        step: 'complete',
      }));

      onComplete?.(wizardState.selectedGoal);
    } catch (e) {
      setError(String(e));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle wizard cancellation.
   * Requirements: 5.7
   * 
   * Does not modify any settings or apply any values.
   */
  const handleCancel = () => {
    // Reset state without saving anything
    setWizardState({
      step: 'welcome',
      selectedGoal: null,
    });
    onCancel?.();
  };

  /**
   * Handle wizard skip.
   * Requirements: 5.7
   * 
   * Marks first_run_complete but doesn't apply any settings.
   */
  const handleSkip = async () => {
    try {
      // Only mark as complete, don't save any goal
      await api.saveSetting('first_run_complete', true);
      onSkip?.();
    } catch (e) {
      // Silently fail - user can still use the plugin
      onSkip?.();
    }
  };

  return (
    <PanelSection title="Setup Wizard">
      {/* Platform info */}
      {platformInfo && (
        <PanelSectionRow>
          <div
            style={{
              fontSize: "10px",
              color: "#8b929a",
              textAlign: "center",
              marginBottom: "8px",
            }}
          >
            Detected: {platformInfo.variant} ({platformInfo.model})
          </div>
        </PanelSectionRow>
      )}

      {/* Step indicator */}
      {wizardState.step !== 'complete' && (
        <PanelSectionRow>
          <StepIndicator currentStep={wizardState.step} />
        </PanelSectionRow>
      )}

      {/* Error display */}
      {error && (
        <PanelSectionRow>
          <div
            style={{
              padding: "8px",
              backgroundColor: "#b71c1c",
              borderRadius: "4px",
              fontSize: "11px",
              color: "#fff",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        </PanelSectionRow>
      )}

      {/* Step content */}
      {wizardState.step === 'welcome' && (
        <WelcomeStep onNext={goToNextStep} onSkip={handleSkip} />
      )}

      {wizardState.step === 'explanation' && (
        <ExplanationStep
          onNext={goToNextStep}
          onBack={goToPreviousStep}
          onSkip={handleSkip}
        />
      )}

      {wizardState.step === 'goal' && (
        <GoalStep
          selectedGoal={wizardState.selectedGoal}
          onSelectGoal={handleSelectGoal}
          onNext={goToNextStep}
          onBack={goToPreviousStep}
          onSkip={handleSkip}
        />
      )}

      {wizardState.step === 'confirm' && wizardState.selectedGoal && (
        <ConfirmStep
          selectedGoal={wizardState.selectedGoal}
          onConfirm={handleComplete}
          onBack={goToPreviousStep}
          onCancel={handleCancel}
          isLoading={isLoading}
        />
      )}

      {/* Completion screen */}
      {wizardState.step === 'complete' && (
        <>
          <PanelSectionRow>
            <div
              style={{
                textAlign: "center",
                padding: "24px",
              }}
            >
              <div
                style={{
                  width: "64px",
                  height: "64px",
                  borderRadius: "50%",
                  backgroundColor: "#4caf50",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 16px",
                }}
              >
                <FaCheck style={{ color: "#fff", fontSize: "28px" }} />
              </div>
              <div
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  marginBottom: "8px",
                }}
              >
                Setup Complete!
              </div>
              <div
                style={{
                  fontSize: "12px",
                  color: "#8b929a",
                }}
              >
                DeckTune is ready to use. Head to Wizard mode to run autotune
                and find your optimal undervolt values.
              </div>
            </div>
          </PanelSectionRow>
        </>
      )}
    </PanelSection>
  );
};

export default SetupWizard;
