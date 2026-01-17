/**
 * ErrorBoundary component for DeckTune.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 * 
 * Catches React render errors and displays a fallback UI instead of crashing.
 */

import React, { Component, ErrorInfo, ReactNode } from "react";
import { PanelSection, PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaExclamationTriangle, FaRedo } from "react-icons/fa";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary component that catches render errors.
 * 
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 */
export class DeckTuneErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("DeckTune render error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <PanelSection title="DeckTune">
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
              <FaExclamationTriangle
                style={{ color: "#f44336", fontSize: "32px" }}
              />
              <div
                style={{
                  color: "#ffcdd2",
                  textAlign: "center",
                  fontSize: "14px",
                }}
              >
                Произошла ошибка рендеринга
              </div>
              <div
                style={{
                  color: "#ef9a9a",
                  textAlign: "center",
                  fontSize: "11px",
                  maxWidth: "280px",
                  wordBreak: "break-word",
                }}
              >
                {this.state.error?.message || "Unknown error"}
              </div>
            </div>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem
              layout="below"
              onClick={this.handleReset}
              style={{ marginTop: "8px" }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                }}
              >
                <FaRedo />
                <span>Попробовать снова</span>
              </div>
            </ButtonItem>
          </PanelSectionRow>
        </PanelSection>
      );
    }

    return this.props.children;
  }
}

export default DeckTuneErrorBoundary;
