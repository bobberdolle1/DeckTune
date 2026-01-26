# 🎯 DeckTune v3.3.2 — Frequency Wizard Integration & UI Fixes

**Release Date**: January 26, 2026

---

## 🌟 Major Changes

### Frequency Wizard Integration
The Frequency-Based Voltage Wizard has been **integrated into Wizard Mode** for better UI organization and navigation flow.

**What Changed:**
- ❌ Removed from top-level navigation menu (no more separate "Frequency-Based" mode)
- ✅ Added as sub-mode within Wizard Mode
- ✅ New toggle: **"Load-Based Wizard"** ↔ **"Frequency-Based Wizard"**
- ✅ Cleaner, more intuitive navigation

**How to Access:**
1. Open DeckTune
2. Select **Wizard Mode**
3. Toggle between **Load-Based** and **Frequency-Based** wizards
4. Configure and run your preferred wizard

---

## 🐛 Bug Fixes

### Frequency Wizard UI Fixes
Fixed multiple critical UI/UX issues that prevented proper usage:

**Layout & Display:**
- ✅ Fixed preset cards overflowing plugin boundaries
  - Added `maxWidth: 100%` and `overflow: hidden` to prevent horizontal scrolling
  - Preset cards now properly fit within Decky Loader's QAM interface
- ✅ Fixed frequency range always visible
  - Now only shown in **Manual Config** mode
  - Cleaner UI when using Quick Presets

**Gamepad Navigation:**
- ✅ Fixed gamepad focus not appearing on quick presets
  - Added proper focus styles with blue outline
  - Improved Focusable structure for Steam Deck controller
  - D-pad navigation now works correctly

**User Experience:**
- ✅ Added **"Quick Presets"** / **"Manual Config"** toggle
  - Quick Presets: One-click Conservative/Balanced/Aggressive configurations
  - Manual Config: Full control over all parameters
  - Better organization and less overwhelming for new users

### Frequency Wizard Backend Fixes
Enhanced reliability and debugging capabilities:

**Operation Conflict Prevention:**
- ✅ Added `_frequency_wizard_task` to `_is_operation_running()` check
  - Prevents wizard from starting during autotune/binning/benchmark
  - Clear error messages when operations conflict
  - Improved stability

**Error Handling:**
- ✅ Added test_runner availability check
  - Detects if stress testing tools are missing
  - Provides clear error message with installation instructions
  - Prevents cryptic failures

**Comprehensive Logging:**
- ✅ Extensive debug logging throughout wizard lifecycle:
  - Operation status checks (autotune, binning, benchmark, iron seeker)
  - Config validation and preset loading
  - CPUFreq controller initialization
  - Wizard instance creation
  - Background task execution with progress tracking
  - Full exception handling with stack traces
  - Progress callbacks with frequency/voltage/completion metrics
- ✅ Visual separators (80-char lines) for easy log parsing
- ✅ Step-by-step execution tracking

### Settings Menu Fixes (v3.3.1)
Fixed non-functional settings in Expert Mode:

**Settings Accessibility:**
- ✅ Moved **"Apply on Startup"** and **"Game Only Mode"** to main Settings menu
  - Previously hidden in Expert Mode → Manual tab
  - Now accessible via header gear icon (⚙️)
  - Centralized location alongside Expert Mode toggle
- ✅ Removed redundant Focusable wrappers that blocked gamepad input
- ✅ Fixed property access patterns to use correct context structure
- ✅ Settings now properly save and apply

---

## 📊 Frequency Wizard Quick Reference

### Quick Presets

| Preset | Frequency Step | Test Duration | Total Time | Use Case |
|--------|---------------|---------------|------------|----------|
| **Conservative** | 200 MHz | 20s | ~10 min | Safe, thorough testing |
| **Balanced** | 100 MHz | 30s | ~15 min | Good balance (recommended) |
| **Aggressive** | 50 MHz | 60s | ~30 min | Maximum precision |

### When to Use Frequency-Based vs Load-Based

**Frequency-Based Wizard:**
- ✅ Gaming with varying CPU frequencies
- ✅ Mixed workloads (browsing, video, gaming)
- ✅ Per-game optimization
- ✅ Maximum efficiency across full spectrum

**Load-Based Wizard:**
- ✅ Consistent workloads (video playback, idle)
- ✅ Quick setup needed
- ✅ General-purpose usage
- ✅ Simpler configuration

---

## 🔧 Technical Details

### UI Improvements
- Preset cards: `maxWidth: 100%`, `overflow: hidden`, `word-wrap: break-word`
- Focus styles: `outline: 3px solid #1a9fff`, `box-shadow: 0 0 15px rgba(26, 159, 255, 0.6)`
- Conditional rendering: Frequency range only in Manual Config mode
- Toggle component: Quick Presets ↔ Manual Config

### Backend Improvements
- Operation conflict detection: `_is_operation_running()` includes frequency wizard
- Test runner validation: Checks for stress-ng/stress availability
- Logging levels: DEBUG for all wizard operations
- Exception handling: Full traceback capture with error type identification
- Progress tracking: Real-time frequency/voltage/percentage updates

---

## 📦 Installation

### Quick Install
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

### Manual Install (Developer Mode)
1. Download `DeckTune-v3.3.2.zip` from [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Transfer to Steam Deck
3. Enable **Developer Mode** in Decky Loader settings
4. Install from zip file

---

## 🆙 Upgrading from v3.3.0/v3.3.1

**Breaking Changes:** None

**UI Changes:**
- Frequency-Based mode moved into Wizard Mode
- Access via toggle instead of top-level navigation
- All functionality preserved

**Settings Changes:**
- "Apply on Startup" and "Game Only Mode" moved to Settings menu
- More accessible location (header gear icon)

---

## 🐛 Known Issues

None reported for v3.3.2.

---

## 📝 Changelog

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)

**Previous Releases:**
- [v3.3.1](RELEASE_NOTES_v3.3.1.md) - Settings Menu Fixes
- [v3.3.0](RELEASE_NOTES_v3.3.0.md) - Frequency-Based Voltage Wizard

---

## 🙏 Acknowledgments

Thanks to the Steam Deck community for bug reports and testing feedback!

---

**Enjoy better undervolting with DeckTune v3.3.2!** 🎮⚡
