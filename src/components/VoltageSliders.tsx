/**
 * VoltageSliders component for dynamic voltage configuration.
 * 
 * Feature: manual-dynamic-mode
 * Requirements: 1.2, 1.3, 1.4, 5.2, 5.4
 * 
 * Provides three sliders for configuring voltage curves:
 * - MinimalValue: Voltage offset at low CPU load (-100 to 0 mV)
 * - MaximumValue: Voltage offset at high CPU load (-100 to 0 mV)
 * - Threshold: CPU load percentage where transition occurs (0 to 100%)
 * 
 * Property 1: Slider value clamping
 * All slider values are clamped to their valid ranges.
 * 
 * UI Polish:
 * - Tooltips for each control explaining their purpose
 * - Smooth transitions for focus indicators
 * - Responsive layout for different screen sizes
 */

import { FC, useState } from "react";
import { PanelSectionRow, SliderField } from "@decky/ui";
import { CoreConfig, ValidationError } from "../types/DynamicMode";
import { FaInfoCircle } from "react-icons/fa";

/**
 * Props for VoltageSliders component.
 */
export interface VoltageSlidersProps {
  /** Core identifier (0-3) */
  coreId: number;
  
  /** Current core configuration */
  config: CoreConfig;
  
  /** Callback when a field value changes */
  onChange: (field: 'min_mv' | 'max_mv' | 'threshold', value: number) => void;
  
  /** Whether sliders are disabled */
  disabled?: boolean;
  
  /** Validation errors to display */
  validationErrors?: ValidationError[];
  
  /** Currently focused slider for gamepad navigation */
  focusedSlider?: 'min' | 'max' | 'threshold' | null;
  
  /** Callback when slider receives focus */
  onSliderFocus?: (slider: 'min' | 'max' | 'threshold') => void;
}

/**
 * Clamp a value to a specified range.
 * Property 1: Slider value clamping
 * 
 * @param value - Value to clamp
 * @param min - Minimum allowed value
 * @param max - Maximum allowed value
 * @returns Clamped value within [min, max]
 */
const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value));
};

/**
 * VoltageSliders component.
 * Requirements: 1.2, 1.3, 1.4, 8.3, 8.5
 * UI Polish: Tooltips, smooth transitions, responsive layout
 */
export const VoltageSliders: FC<VoltageSlidersProps> = ({
  coreId,
  config,
  onChange,
  disabled = false,
  validationErrors = [],
  focusedSlider = null,
  onSliderFocus,
}) => {
  // Tooltip visibility state
  const [showMinTooltip, setShowMinTooltip] = useState(false);
  const [showMaxTooltip, setShowMaxTooltip] = useState(false);
  const [showThresholdTooltip, setShowThresholdTooltip] = useState(false);
  
  /**
   * Handle MinimalValue slider change.
   * Requirements: 1.2
   * Property 1: Slider value clamping - values are clamped to -100 to 0 mV
   */
  const handleMinChange = (value: number) => {
    const clamped = clamp(Math.round(value), -100, 0);
    onChange('min_mv', clamped);
  };
  
  /**
   * Handle MaximumValue slider change.
   * Requirements: 1.3
   * Property 1: Slider value clamping - values are clamped to -100 to 0 mV
   */
  const handleMaxChange = (value: number) => {
    const clamped = clamp(Math.round(value), -100, 0);
    onChange('max_mv', clamped);
  };
  
  /**
   * Handle Threshold slider change.
   * Requirements: 1.4
   * Property 1: Slider value clamping - values are clamped to 0 to 100%
   */
  const handleThresholdChange = (value: number) => {
    const clamped = clamp(Math.round(value), 0, 100);
    onChange('threshold', clamped);
  };
  
  /**
   * Get validation errors for a specific field.
   */
  const getFieldErrors = (field: 'min_mv' | 'max_mv' | 'threshold'): string[] => {
    return validationErrors
      .filter(err => err.field === field && (err.core_id === undefined || err.core_id === coreId))
      .map(err => err.message);
  };
  
  const minErrors = getFieldErrors('min_mv');
  const maxErrors = getFieldErrors('max_mv');
  const thresholdErrors = getFieldErrors('threshold');
  
  /**
   * Tooltip component for displaying help text.
   */
  const Tooltip: FC<{ text: string; visible: boolean }> = ({ text, visible }) => {
    if (!visible) return null;
    
    return (
      <div style={{
        position: 'absolute',
        top: '-60px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: '#1a1f2c',
        border: '2px solid #1a9fff',
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '11px',
        color: '#fff',
        whiteSpace: 'nowrap',
        zIndex: 1000,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
        animation: 'tooltipFadeIn 0.2s ease',
      }}>
        {text}
        <div style={{
          position: 'absolute',
          bottom: '-8px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: 0,
          height: 0,
          borderLeft: '8px solid transparent',
          borderRight: '8px solid transparent',
          borderTop: '8px solid #1a9fff',
        }} />
      </div>
    );
  };
  
  return (
    <>
      {/* MinimalValue Slider */}
      <PanelSectionRow>
        <div style={{ position: 'relative' }}>
          <div
            onClick={() => onSliderFocus?.('min')}
            onMouseEnter={() => setShowMinTooltip(true)}
            onMouseLeave={() => setShowMinTooltip(false)}
            style={{
              border: focusedSlider === 'min' ? '3px solid #1a9fff' : '3px solid transparent',
              borderRadius: '8px',
              boxShadow: focusedSlider === 'min' ? '0 0 12px #1a9fff99' : 'none',
              padding: '4px',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <SliderField
                  label="Min"
                  value={config.min_mv}
                  min={-100}
                  max={0}
                  step={1}
                  onChange={handleMinChange}
                  disabled={disabled}
                  showValue={true}
                  valueSuffix=" mV"
                />
              </div>
              <FaInfoCircle 
                style={{ 
                  color: '#8b929a', 
                  fontSize: '14px',
                  flexShrink: 0,
                  opacity: 0.7,
                  transition: 'opacity 0.2s ease',
                }} 
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  setShowMinTooltip(true);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.7';
                  setShowMinTooltip(false);
                }}
              />
            </div>
          </div>
          <Tooltip 
            text="Conservative voltage offset applied when CPU load is below threshold" 
            visible={showMinTooltip} 
          />
        </div>
        {minErrors.length > 0 && (
          <div style={{
            marginTop: '4px',
            padding: '6px 8px',
            backgroundColor: '#5c1313',
            borderRadius: '4px',
            fontSize: '10px',
            color: '#ff9800',
            animation: 'errorFadeIn 0.3s ease',
          }}>
            {minErrors.map((err, idx) => (
              <div key={idx}>{err}</div>
            ))}
          </div>
        )}
      </PanelSectionRow>
      
      {/* MaximumValue Slider */}
      <PanelSectionRow>
        <div style={{ position: 'relative' }}>
          <div
            onClick={() => onSliderFocus?.('max')}
            onMouseEnter={() => setShowMaxTooltip(true)}
            onMouseLeave={() => setShowMaxTooltip(false)}
            style={{
              border: focusedSlider === 'max' ? '3px solid #1a9fff' : '3px solid transparent',
              borderRadius: '8px',
              boxShadow: focusedSlider === 'max' ? '0 0 12px #1a9fff99' : 'none',
              padding: '4px',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <SliderField
                  label="Max"
                  value={config.max_mv}
                  min={-100}
                  max={0}
                  step={1}
                  onChange={handleMaxChange}
                  disabled={disabled}
                  showValue={true}
                  valueSuffix=" mV"
                />
              </div>
              <FaInfoCircle 
                style={{ 
                  color: '#8b929a', 
                  fontSize: '14px',
                  flexShrink: 0,
                  opacity: 0.7,
                  transition: 'opacity 0.2s ease',
                }} 
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  setShowMaxTooltip(true);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.7';
                  setShowMaxTooltip(false);
                }}
              />
            </div>
          </div>
          <Tooltip 
            text="Aggressive voltage offset applied when CPU load is above threshold" 
            visible={showMaxTooltip} 
          />
        </div>
        {maxErrors.length > 0 && (
          <div style={{
            marginTop: '4px',
            padding: '6px 8px',
            backgroundColor: '#5c1313',
            borderRadius: '4px',
            fontSize: '10px',
            color: '#ff9800',
            animation: 'errorFadeIn 0.3s ease',
          }}>
            {maxErrors.map((err, idx) => (
              <div key={idx}>{err}</div>
            ))}
          </div>
        )}
      </PanelSectionRow>
      
      {/* Threshold Slider */}
      <PanelSectionRow>
        <div style={{ position: 'relative' }}>
          <div
            onClick={() => onSliderFocus?.('threshold')}
            onMouseEnter={() => setShowThresholdTooltip(true)}
            onMouseLeave={() => setShowThresholdTooltip(false)}
            style={{
              border: focusedSlider === 'threshold' ? '3px solid #1a9fff' : '3px solid transparent',
              borderRadius: '8px',
              boxShadow: focusedSlider === 'threshold' ? '0 0 12px #1a9fff99' : 'none',
              padding: '4px',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <SliderField
                  label="Threshold"
                  value={config.threshold}
                  min={0}
                  max={100}
                  step={1}
                  onChange={handleThresholdChange}
                  disabled={disabled}
                  showValue={true}
                  valueSuffix="%"
                />
              </div>
              <FaInfoCircle 
                style={{ 
                  color: '#8b929a', 
                  fontSize: '14px',
                  flexShrink: 0,
                  opacity: 0.7,
                  transition: 'opacity 0.2s ease',
                }} 
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  setShowThresholdTooltip(true);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.7';
                  setShowThresholdTooltip(false);
                }}
              />
            </div>
          </div>
          <Tooltip 
            text="CPU load percentage where voltage transitions from minimal to maximum" 
            visible={showThresholdTooltip} 
          />
        </div>
        {thresholdErrors.length > 0 && (
          <div style={{
            marginTop: '4px',
            padding: '6px 8px',
            backgroundColor: '#5c1313',
            borderRadius: '4px',
            fontSize: '10px',
            color: '#ff9800',
            animation: 'errorFadeIn 0.3s ease',
          }}>
            {thresholdErrors.map((err, idx) => (
              <div key={idx}>{err}</div>
            ))}
          </div>
        )}
      </PanelSectionRow>
      
      {/* CSS Animations */}
      <style>
        {`
          @keyframes tooltipFadeIn {
            from {
              opacity: 0;
              transform: translateX(-50%) translateY(-5px);
            }
            to {
              opacity: 1;
              transform: translateX(-50%) translateY(0);
            }
          }
          
          @keyframes errorFadeIn {
            from {
              opacity: 0;
              transform: translateY(-5px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}
      </style>
    </>
  );
};

export default VoltageSliders;
