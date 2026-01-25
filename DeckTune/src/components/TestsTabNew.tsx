/**
 * Redesigned Tests tab - compact and gamepad-friendly.
 * 
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 7.4
 * 
 * Two sections:
 * 1. Run Tests - test selection and execution with progress
 * 2. Test History - last 10 test results
 */

import { useState, useEffect, FC } from "react";
import {
  PanelSectionRow,
  Focusable,
} from "@decky/ui";
import {
  FaPlay,
  FaHistory,
  FaSpinner,
  FaCheck,
  FaTimes,
  FaExclamationCircle,
} from "react-icons/fa";
import { useTests, useBinaries } from "../context";
import { FocusableButton } from "./FocusableButton";

/**
 * Available test options with compact labels and estimated durations.
 */
const TEST_OPTIONS = [
  { value: "cpu_quick", label: "CPU Quick", duration: "30s", durationSeconds: 30, icon: "⚡" },
  { value: "cpu_long", label: "CPU Long", duration: "5m", durationSeconds: 300, icon: "🔥" },
  { value: "ram_quick", label: "RAM Quick", duration: "2m", durationSeconds: 120, icon: "💾" },
  { value: "ram_thorough", label: "RAM Thorough", duration: "15m", durationSeconds: 900, icon: "🧠" },
  { value: "combo", label: "Combo Stress", duration: "5m", durationSeconds: 300, icon: "💪" },
  { value: "cpu_loop", label: "CPU Loop", duration: "∞", durationSeconds: 0, icon: "🔁" },
];

export const TestsTabNew: FC = () => {
  const { history, currentTest, isRunning, runTest } = useTests();
  const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();
  const [activeSection, setActiveSection] = useState<"run" | "history">("run");

  // NUCLEAR CACHE BUST - v3.1.19-20260118-2230
  useEffect(() => {
    const buildId = "v3.1.19-20260118-2230-FOCUSABLE-BUTTON";
    console.log(`[DeckTune CACHE BUST] ${buildId} - TestsTabNew with FocusableButton`);
    (window as any).__DECKTUNE_BUILD_ID__ = buildId;
    (window as any).__DECKTUNE_TESTS_TAB_VERSION__ = "FOCUSABLE_BUTTON";
  }, []);

  // Check binaries on mount
  useEffect(() => {
    checkBinaries();
  }, []);

  return (
    <>
      {/* Section switcher */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            gap: "4px",
            marginBottom: "12px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            padding: "2px",
          }}
          flow-children="horizontal"
        >
          <FocusableButton
            onClick={() => setActiveSection("run")}
            style={{ flex: 1 }}
          >
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center", 
              gap: "4px", 
              padding: "6px", 
              fontSize: "10px",
              backgroundColor: activeSection === "run" ? "#1a9fff" : "transparent",
              borderRadius: "4px",
              color: activeSection === "run" ? "#fff" : "#8b929a",
            }}>
              <FaPlay style={{ fontSize: "10px" }} />
              <span>Run Tests</span>
            </div>
          </FocusableButton>
          
          <FocusableButton
            onClick={() => setActiveSection("history")}
            style={{ flex: 1 }}
          >
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center", 
              gap: "4px", 
              padding: "6px", 
              fontSize: "10px",
              backgroundColor: activeSection === "history" ? "#1a9fff" : "transparent",
              borderRadius: "4px",
              color: activeSection === "history" ? "#fff" : "#8b929a",
            }}>
              <FaHistory style={{ fontSize: "10px" }} />
              <span>History</span>
            </div>
          </FocusableButton>
        </Focusable>
      </PanelSectionRow>

      {/* Content */}
      {activeSection === "run" ? (
        <RunTestsSection 
          isRunning={isRunning} 
          currentTest={currentTest} 
          runTest={runTest} 
          hasMissing={hasMissing} 
          missingBinaries={missingBinaries} 
        />
      ) : (
        <TestHistorySection history={history} />
      )}

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
    </>
  );
};

/**
 * Run Tests Section with progress tracking and error display
 */
interface RunTestsSectionProps {
  isRunning: boolean;
  currentTest: string | null;
  runTest: (testName: string) => Promise<any>;
  hasMissing: boolean;
  missingBinaries: string[];
}

const RunTestsSection: FC<RunTestsSectionProps> = ({ 
  isRunning, 
  currentTest, 
  runTest, 
  hasMissing, 
  missingBinaries 
}) => {
  const [progress, setProgress] = useState(0);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [estimatedDuration, setEstimatedDuration] = useState(0);
  const [testResult, setTestResult] = useState<{ passed: boolean; error?: string } | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Progress tracking
  useEffect(() => {
    if (!isRunning || !currentTest) {
      setProgress(0);
      setStartTime(null);
      setElapsedTime(0);
      return;
    }

    // Set start time and estimated duration
    const testOption = TEST_OPTIONS.find(t => t.value === currentTest);
    if (testOption && !startTime) {
      setStartTime(Date.now());
      setEstimatedDuration(testOption.durationSeconds);
      setTestResult(null);
    }

    // Update progress every second
    const interval = setInterval(() => {
      if (startTime) {
        const elapsed = (Date.now() - startTime) / 1000;
        setElapsedTime(Math.floor(elapsed));
        
        if (estimatedDuration > 0) {
          const newProgress = Math.min((elapsed / estimatedDuration) * 100, 99);
          setProgress(newProgress);
        } else {
          // Loop test - show elapsed time only
          setProgress(0);
        }
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, currentTest, startTime, estimatedDuration]);

  const handleRunTest = async (testValue: string) => {
    if (isRunning) return;
    setProgress(0);
    setStartTime(null);
    setTestResult(null);
    
    try {
      const result = await runTest(testValue);
      setProgress(100);
      setTestResult({ passed: result?.passed ?? true });
    } catch (error: any) {
      setTestResult({ passed: false, error: error?.message || "Test failed" });
    }
  };

  const getTestLabel = (value: string): string => {
    return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const getRemainingTime = (): string => {
    if (!startTime || !estimatedDuration) return "";
    const remaining = Math.max(0, estimatedDuration - elapsedTime);
    return formatTime(remaining) + " left";
  };

  const isLoopTest = currentTest && TEST_OPTIONS.find(t => t.value === currentTest)?.durationSeconds === 0;

  return (
    <>
      {/* Missing Binaries Warning */}
      {hasMissing && (
        <PanelSectionRow>
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "8px",
              padding: "10px",
              backgroundColor: "#5c4813",
              borderRadius: "6px",
              marginBottom: "12px",
              border: "1px solid #ff9800",
            }}
          >
            <FaExclamationCircle style={{ color: "#ff9800", fontSize: "14px", flexShrink: 0, marginTop: "1px" }} />
            <div>
              <div style={{ fontWeight: "bold", color: "#ffb74d", marginBottom: "3px", fontSize: "10px" }}>
                Missing Components
              </div>
              <div style={{ fontSize: "9px", color: "#ffe0b2" }}>
                Required: <strong>{missingBinaries.join(", ")}</strong>
              </div>
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* Test result banner */}
      {testResult && !isRunning && (
        <PanelSectionRow>
          <div
            style={{
              padding: "10px",
              backgroundColor: testResult.passed ? "#1b5e20" : "#5c1313",
              borderRadius: "6px",
              marginBottom: "12px",
              border: `1px solid ${testResult.passed ? "#4caf50" : "#f44336"}`,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: testResult.error ? "4px" : "0" }}>
              {testResult.passed ? (
                <FaCheck style={{ color: "#4caf50", fontSize: "12px" }} />
              ) : (
                <FaTimes style={{ color: "#f44336", fontSize: "12px" }} />
              )}
              <span style={{ fontSize: "10px", fontWeight: "bold" }}>
                {testResult.passed ? "Test Passed!" : "Test Failed"}
              </span>
            </div>
            {testResult.error && (
              <div style={{ fontSize: "9px", color: "#ffcdd2", marginTop: "4px" }}>
                {testResult.error}
              </div>
            )}
          </div>
        </PanelSectionRow>
      )}

      {/* Running test with progress */}
      {isRunning && currentTest && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#1a3a5c",
              borderRadius: "6px",
              marginBottom: "12px",
              border: "1px solid #1a9fff",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <FaSpinner className="spin" style={{ color: "#1a9fff", fontSize: "12px" }} />
                <span style={{ fontSize: "10px", fontWeight: "bold" }}>
                  {getTestLabel(currentTest)}
                </span>
              </div>
              <span style={{ fontSize: "9px", color: "#8b929a" }}>
                {isLoopTest ? `${formatTime(elapsedTime)} elapsed` : getRemainingTime()}
              </span>
            </div>
            
            {/* Progress bar - only for non-loop tests */}
            {!isLoopTest && (
              <div>
                <div style={{ 
                  width: "100%", 
                  height: "6px", 
                  backgroundColor: "#23262e", 
                  borderRadius: "3px",
                  overflow: "hidden"
                }}>
                  <div style={{
                    width: `${progress}%`,
                    height: "100%",
                    backgroundColor: "#1a9fff",
                    transition: "width 0.3s ease",
                    borderRadius: "3px"
                  }} />
                </div>
                <div style={{ fontSize: "8px", color: "#8b929a", marginTop: "4px", textAlign: "center" }}>
                  {Math.round(progress)}%
                </div>
              </div>
            )}
            
            {/* Info for loop tests */}
            {isLoopTest && (
              <div style={{ fontSize: "9px", color: "#8b929a", textAlign: "center", marginTop: "4px" }}>
                Running until manually stopped (restart plugin to cancel)
              </div>
            )}
          </div>
        </PanelSectionRow>
      )}

      {/* Test options grid */}
      {!isRunning && (
        <PanelSectionRow>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "6px",
            }}
          >
            {TEST_OPTIONS.map((test) => (
              <FocusableButton
                key={test.value}
                onClick={() => !hasMissing && handleRunTest(test.value)}
                disabled={hasMissing}
              >
                <div
                  style={{
                    padding: "10px 8px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", marginBottom: "4px" }}>
                    <span style={{ fontSize: "14px" }}>{test.icon}</span>
                    <span style={{ fontSize: "10px", fontWeight: "bold" }}>{test.label}</span>
                  </div>
                  <div style={{ fontSize: "8px", color: "#8b929a" }}>
                    {test.durationSeconds === 0 ? "Until cancelled" : `Duration: ${test.duration}`}
                  </div>
                </div>
              </FocusableButton>
            ))}
          </div>
        </PanelSectionRow>
      )}
    </>
  );
};

/**
 * Test History Section
 */
interface TestHistorySectionProps {
  history: any[];
}

const TestHistorySection: FC<TestHistorySectionProps> = ({ history }) => {
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    } catch {
      return timestamp;
    }
  };

  const getTestLabel = (value: string): string => {
    return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
  };

  const getTestIcon = (value: string): string => {
    return TEST_OPTIONS.find((t) => t.value === value)?.icon || "🔧";
  };

  return (
    <>
      {history.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "24px", fontSize: "11px" }}>
            No tests run yet.
            <div style={{ marginTop: "4px", fontSize: "9px" }}>
              Switch to "Run Tests" to start!
            </div>
          </div>
        </PanelSectionRow>
      ) : (
        history.slice(0, 10).map((entry, index) => (
          <PanelSectionRow key={index}>
            <Focusable
              focusClassName="gpfocus"
              style={{
                marginBottom: "6px",
              }}
            >
              <div
                style={{
                  padding: "8px 10px",
                  backgroundColor: "#23262e",
                  borderRadius: "6px",
                  borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ fontSize: "12px" }}>{getTestIcon(entry.test_name)}</span>
                    {entry.passed ? (
                      <FaCheck style={{ color: "#4caf50", fontSize: "10px" }} />
                    ) : (
                      <FaTimes style={{ color: "#f44336", fontSize: "10px" }} />
                    )}
                    <span style={{ fontWeight: "bold", fontSize: "10px" }}>
                      {getTestLabel(entry.test_name)}
                    </span>
                  </div>
                  <span style={{ fontSize: "9px", color: "#8b929a" }}>
                    {formatDuration(entry.duration)}
                  </span>
                </div>
                <div style={{ fontSize: "8px", color: "#8b929a", marginBottom: "2px" }}>
                  {formatTimestamp(entry.timestamp)}
                </div>
                <div style={{ fontSize: "8px", color: "#8b929a" }}>
                  Cores: [{entry.cores_tested.join(", ")}]
                </div>
              </div>
            </Focusable>
          </PanelSectionRow>
        ))
      )}
    </>
  );
};

export default TestsTabNew;
