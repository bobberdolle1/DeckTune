# QAM Optimization Guide

## Overview

This document describes the optimizations made to ensure DeckTune's Dynamic Manual Mode fits properly within Decky Loader's Quick Access Menu (QAM).

## QAM Constraints

- **Width**: ~400px maximum (with padding)
- **Height**: Scrollable, but should minimize vertical space
- **Font sizes**: Must be readable on 7" screen (1280x800)
- **Touch targets**: Minimum 44x44px for gamepad/touch interaction

## Optimizations Applied

### 1. CurveVisualization Component

**Changes:**
- Reduced chart dimensions: 340x160px (was 320x180px)
- Made SVG responsive with `viewBox` and `preserveAspectRatio`
- Reduced padding: 15px (was 20px)
- Smaller fonts: 9px for labels (was 11px)
- Compact tooltip positioning to prevent overflow

**Result:** Chart fits QAM width and scales properly

### 2. MetricsDisplay Component

**Changes:**
- Reduced grid padding: 8px (was 12px)
- Smaller font sizes:
  - Labels: 9px (was 10px)
  - Values: 16px (was 20px)
  - Units: 10px (was 12px)
- Compact graph height: 140px (was 180px)
- Reduced margins: 6px gaps (was 8px)
- Shorter labels: "TEMP" instead of "TEMPERATURE"
- Narrower Y-axis: 35px width
- Thinner lines: 1.5px (was 2px)

**Result:** Metrics display is compact and readable

### 3. CoreTabs Component

**Changes:**
- Reduced padding: 8px vertical, 6px horizontal (was 10px/8px)
- Smaller gaps: 4px (was 6px)
- Smaller font: 10px (was 11px)
- Smaller indicator dot: 5px (was 6px)
- Reduced border radius: 4px (was 6px)

**Result:** Core tabs are compact but still touch-friendly

### 4. VoltageSliders Component

**Already optimized:**
- Uses Decky's `SliderField` component (responsive)
- Compact tooltips with 11px font
- Minimal padding and margins

## Testing Checklist

- [ ] Test on actual Steam Deck hardware
- [ ] Verify all text is readable
- [ ] Check touch targets are accessible
- [ ] Ensure no horizontal scrolling
- [ ] Verify gamepad navigation works
- [ ] Test with different QAM sizes (docked/undocked)

## Responsive Design Principles

1. **Use relative units**: `%`, `fr`, `flex` instead of fixed `px`
2. **SVG viewBox**: Makes charts scale properly
3. **Max-width**: Prevent overflow with `maxWidth: "100%"`
4. **Compact spacing**: Reduce padding/margins for QAM
5. **Readable fonts**: Minimum 9px for labels, 10px for values

## Future Improvements

1. **Dynamic font scaling**: Adjust based on container width
2. **Collapsible sections**: Hide less important info by default
3. **Horizontal scrolling**: For very wide content (avoid if possible)
4. **Lazy loading**: Load graphs only when visible

## References

- Decky Loader QAM specs: ~400px width
- Steam Deck screen: 1280x800 (7 inches)
- Minimum touch target: 44x44px (Apple HIG)
- Readable font size: 9-11px for UI labels
