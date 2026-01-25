/**
 * SessionHistoryContainer component - container for session history UI.
 * 
 * Feature: decktune-3.1-reliability-ux
 * Requirements: 8.4, 8.5, 8.6
 * 
 * Manages navigation between:
 * - Session list view (SessionHistory)
 * - Session detail view (SessionDetail)
 * - Session comparison view (SessionComparison)
 */

import { useState, FC } from "react";
import { Session } from "../api/types";
import { SessionHistory } from "./SessionHistory";
import { SessionDetail } from "./SessionDetail";
import { SessionComparisonView } from "./SessionComparison";

/**
 * View state for the container.
 */
type ViewState = 
  | { type: "list" }
  | { type: "detail"; session: Session }
  | { type: "compare"; session1: Session; session2: Session };

/**
 * SessionHistoryContainer component - manages session history views.
 * 
 * Requirements:
 * - 8.4: Display the last 30 sessions with key metrics in a list view
 * - 8.5: Display detailed metrics including temperature graph, power graph, and undervolt values used
 * - 8.6: Allow selecting two sessions and display side-by-side metric comparison
 */
export const SessionHistoryContainer: FC = () => {
  const [viewState, setViewState] = useState<ViewState>({ type: "list" });

  /**
   * Handle session selection for detail view.
   */
  const handleSelectSession = (session: Session) => {
    setViewState({ type: "detail", session });
  };

  /**
   * Handle session comparison.
   */
  const handleCompare = (session1: Session, session2: Session) => {
    setViewState({ type: "compare", session1, session2 });
  };

  /**
   * Go back to list view.
   */
  const handleBack = () => {
    setViewState({ type: "list" });
  };

  // Render based on current view state
  switch (viewState.type) {
    case "detail":
      return (
        <SessionDetail
          session={viewState.session}
          onBack={handleBack}
        />
      );
    
    case "compare":
      return (
        <SessionComparisonView
          session1={viewState.session1}
          session2={viewState.session2}
          onBack={handleBack}
        />
      );
    
    case "list":
    default:
      return (
        <SessionHistory
          onSelectSession={handleSelectSession}
          onCompare={handleCompare}
        />
      );
  }
};

export default SessionHistoryContainer;
