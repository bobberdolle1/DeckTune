# DeckTune v3.1.29 Release Notes

## Critical Fixes - Wizard Mode & UI

### 🔧 Backend Fixes

**1. Fixed "testing undefined mV" infinite loop**
- `_current_offset` now properly initialized as `None` instead of `0`
- Progress emission handles `None` offset during initialization
- Prevents confusing "testing 0mV" messages before wizard starts

**2. Fixed wizard cancellation not working**
- Added cancellation checks inside core test loop
- Added cancellation checks inside per-core iteration
- Wizard now responds immediately to cancel button

**3. Fixed wizard state not persisting after restart**
- Added localStorage persistence for wizard setup completion
- Key: `decktune_wizard_setup_complete`
- Prevents wizard setup from showing again after completion

### 🎮 UI/UX Fixes

**4. Fixed gamepad focus on Expert/Wizard mode buttons**
- Added `.mode-button-focusable` CSS class
- Gamepad focus now shows blue outline with glow effect
- Proper focus-within and gpfocus support

**5. Replaced dropdown with button grid in wizard config**
- Aggressiveness: 3 buttons (Safe/Balanced/Aggressive)
- Test Duration: 2 buttons (Short/Long)
- Fully gamepad-navigable
- Visual feedback for selected option

**6. Added Reset Settings button**
- Located in Settings menu
- Clears all localStorage state
- Resets binning config to defaults
- Disables expert mode
- Reloads page after reset

**7. Settings menu now gamepad-accessible**
- All controls are Focusable
- Proper navigation flow
- Modal doesn't block gamepad input

### 📊 Technical Details

**Backend Changes:**
- `backend/tuning/wizard_session.py`:
  - `_current_offset: Optional[int] = None`
  - Enhanced `_emit_progress()` with None handling
  - Added 3 cancellation checkpoints in test loop

**Frontend Changes:**
- `src/components/DeckTuneApp.tsx`:
  - localStorage wizard setup persistence
  - Gamepad focus CSS for mode buttons
  
- `src/components/WizardMode.tsx`:
  - Removed Dropdown/Field imports
  - Button grid for aggressiveness/duration
  - Improved visual hierarchy

- `src/components/SettingsMenu.tsx`:
  - Reset Settings button with confirmation
  - Clears localStorage and resets all configs

### 🎯 User Impact

**Before:**
- Wizard showed "testing undefinedmV" infinitely
- Cancel button didn't work
- Setup wizard appeared every restart
- Couldn't select wizard presets with gamepad
- No way to reset settings

**After:**
- Clean initialization with proper offset display
- Cancel works immediately
- Setup state persists across restarts
- Full gamepad navigation support
- One-click settings reset

### 🔍 Testing Recommendations

1. Start wizard → verify no "undefined mV"
2. Cancel during test → verify immediate stop
3. Complete wizard → restart plugin → verify no setup screen
4. Navigate with gamepad → verify all buttons focusable
5. Settings → Reset → verify clean state

---

**Build:** v3.1.29  
**Date:** 2026-01-20  
**Commit:** Critical wizard fixes + gamepad UX improvements
