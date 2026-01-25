/**
 * CoreTabs component for per-core navigation in Dynamic Manual Mode.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 1.1, 4.1
 * 
 * Provides tab navigation for cores 0-3 with:
 * - Tab selection handler
 * - Active core indicator
 * - Hidden in Simple Mode
 * - Gamepad navigation support (D-pad Up/Down)
 */

import { FC, useEffect } from "react";
import { Focusable } from "@decky/ui";
import { FocusableButton } from "./FocusableButton";

/**
 * Props for CoreTabs component.
 * 
 * Requirements: 1.1, 4.1
 */
export interface CoreTabsProps {
  /** Currently selected core (0-3) */
  selectedCore: number;
  
  /** Callback when core selection changes */
  onCoreSelect: (coreId: number) => void;
  
  /** Current mode: 'simple' hides tabs, 'expert' shows tabs */
  mode: 'simple' | 'expert';
}

/**
 * CoreTabs component.
 * 
 * Renders tabs for cores 0-3 with gamepad navigation support.
 * Hidden in Simple Mode per Requirements 4.1.
 * 
 * Property 15: Gamepad core navigation
 * For any D-pad Up or Down input, the selected core index SHALL change by ±1
 * (wrapping at boundaries 0 and 3).
 * 
 * Requirements: 1.1, 4.1, 8.1
 */
export const CoreTabs: FC<CoreTabsProps> = ({
  selectedCore,
  onCoreSelect,
  mode,
}) => {
  /**
   * Handle gamepad navigation for core selection.
   * Requirements: 8.1
   * 
   * Property 15: Gamepad core navigation
   * D-pad Up/Down changes selected core with wrapping.
   */
  useEffect(() => {
    const handleGamepadInput = (e: KeyboardEvent) => {
      // Only handle in expert mode
      if (mode !== 'expert') return;
      
      // D-pad Up: Previous core (with wrapping)
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        const newCore = selectedCore === 0 ? 3 : selectedCore - 1;
        onCoreSelect(newCore);
      }
      
      // D-pad Down: Next core (with wrapping)
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const newCore = selectedCore === 3 ? 0 : selectedCore + 1;
        onCoreSelect(newCore);
      }
    };
    
    window.addEventListener('keydown', handleGamepadInput);
    
    return () => {
      window.removeEventListener('keydown', handleGamepadInput);
    };
  }, [selectedCore, onCoreSelect, mode]);
  
  /**
   * Hide tabs in Simple Mode.
   * Requirements: 4.1
   */
  if (mode === 'simple') {
    return null;
  }
  
  /**
   * Render tabs for cores 0-3 - Compact for QAM.
   * Requirements: 1.1
   */
  return (
    <div
      style={{
        marginBottom: '8px',
      }}
    >
      <Focusable
        style={{
          display: 'flex',
          gap: '4px',
        }}
        flow-children="horizontal"
      >
        {[0, 1, 2, 3].map((coreId) => {
          const isActive = coreId === selectedCore;
          
          return (
            <FocusableButton
              key={coreId}
              onClick={() => onCoreSelect(coreId)}
              style={{
                flex: 1,
              }}
              focusColor={isActive ? '#4caf50' : '#1a9fff'}
            >
              <div
                style={{
                  padding: '8px 6px',
                  backgroundColor: isActive ? '#1b5e20' : '#3d4450',
                  borderRadius: '4px',
                  textAlign: 'center',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  color: isActive ? '#fff' : '#8b929a',
                  transition: 'all 0.2s ease',
                  position: 'relative',
                }}
              >
                {/* Active indicator dot */}
                {isActive && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '3px',
                      right: '3px',
                      width: '5px',
                      height: '5px',
                      borderRadius: '50%',
                      backgroundColor: '#4caf50',
                      boxShadow: '0 0 4px #4caf50',
                    }}
                  />
                )}
                
                <div>Core {coreId}</div>
              </div>
            </FocusableButton>
          );
        })}
      </Focusable>
    </div>
  );
};

export default CoreTabs;
