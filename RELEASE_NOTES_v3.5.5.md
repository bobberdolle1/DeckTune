# DeckTune v3.5.5 Release Notes

## 🐛 Critical Fixes

### Frequency Wizard
- **Fixed: Userspace governor unavailable on Steam Deck**
  - Frequency wizard now uses `performance` governor with min/max frequency limits as fallback
  - Tests no longer fail immediately when `userspace` governor is unavailable
  - Progress bar and ETA now function correctly during testing
  - Resolves issue where wizard completed in <1 minute with all tests failing

### Core System
- **Fixed: Path import error in main.py**
  - Added missing `from pathlib import Path` import
  - Resolves `NameError: name 'Path' is not defined` in update manager initialization

### UI Components
- **Fixed: Focusable component errors in FrequencyWizardPresets**
  - Corrected nested `Focusable` structure causing TypeScript errors
  - Removed invalid `flow-children` prop
  - Improved button focus handling

## 🔧 Technical Changes

### backend/platform/cpufreq.py
- `lock_frequency()`: Auto-detects available governors, uses fallback strategy
- `unlock_frequency()`: Restores original frequency limits before governor change
- Better error handling for unsupported governor scenarios

### backend/tuning/runner.py
- Added `CPUFreqError` import for proper exception handling
- Improved frequency locking error messages

## 📝 Notes

This release specifically addresses Steam Deck compatibility issues where the Linux kernel doesn't provide the `userspace` cpufreq governor. The frequency wizard now works correctly on all Steam Deck models (LCD/OLED).

---

**Installation**: Update via Decky Loader plugin store or manual installation from GitHub releases.
