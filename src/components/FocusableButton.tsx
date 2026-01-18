/**
 * FocusableButton - Custom button component with gamepad focus support.
 * 
 * Replaces Decky UI's default square focus with custom rounded focus.
 * Uses inline styles to avoid CSS specificity issues.
 */

import { FC, useState, CSSProperties, ReactNode } from "react";
import { Focusable } from "@decky/ui";

export interface FocusableButtonProps {
  children: ReactNode;
  onClick?: () => void;
  onActivate?: () => void;
  style?: CSSProperties;
  focusColor?: string;
  disabled?: boolean;
  className?: string;
}

export const FocusableButton: FC<FocusableButtonProps> = ({
  children,
  onClick,
  onActivate,
  style = {},
  focusColor = "#1a9fff",
  disabled = false,
  className = "",
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleClick = () => {
    if (!disabled && onClick) onClick();
  };

  const handleActivate = () => {
    if (!disabled) {
      if (onActivate) {
        onActivate();
      } else if (onClick) {
        // Fallback to onClick if onActivate not provided
        onClick();
      }
    }
  };

  return (
    <Focusable
      onActivate={handleActivate}
      onGamepadFocus={() => setIsFocused(true)}
      onGamepadBlur={() => setIsFocused(false)}
      className={className}
      style={{
        ...style,
        // Use border instead of outline for rounded corners
        border: isFocused && !disabled ? `3px solid ${focusColor}` : "3px solid transparent",
        borderRadius: "8px", // Rounded corners
        boxShadow: isFocused && !disabled ? `0 0 12px ${focusColor}99` : "none",
        transform: isFocused && !disabled ? "scale(1.05)" : "scale(1)",
        transition: "all 0.2s ease",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        // Remove any padding/margin that might cause issues
        padding: 0,
        margin: 0,
      }}
    >
      {children}
    </Focusable>
  );
};

export default FocusableButton;
