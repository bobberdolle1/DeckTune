# DeckTune v3.5.0 Release Notes

## 🎯 Frequency Wizard Preset Management

Complete preset system for managing frequency wizard results with chip grading and automation.

### New Features

#### Preset Management UI
- **Chip Quality Grading** — Visual badges showing silicon quality:
  - 🏆 **Platinum**: Exceptional chip (avg < -30mV, min < -40mV)
  - 🥇 **Gold**: Excellent chip (avg < -25mV, min < -35mV)
  - 🥈 **Silver**: Good chip (avg < -20mV, min < -30mV)
  - 🥉 **Bronze**: Average chip (avg < -15mV)
  - ⭐ **Standard**: Below average chip

#### Automation Toggles
- **Apply on Startup** — Automatically apply preset when DeckTune plugin starts
- **Game Only Mode** — Apply preset only when a game is running
- Both toggles are fully functional and integrated with backend logic

#### Preset Actions
- **Apply** — Activate frequency curves and enable frequency mode
- **Show Details** — Expand to view per-core statistics:
  - Average voltage per core
  - Minimum voltage per core
  - Number of stable frequency points
- **Delete** — Remove preset with confirmation modal

### Location
Navigate to: **Wizard Mode → Frequency-Based Wizard → Frequency Wizard Presets**

---

## 🔧 Critical Wizard Fixes

### Regular Wizard Algorithm
**Fixed**: Per-core testing now works correctly
- **Before**: Tested all cores at each voltage level (inefficient, incorrect)
- **After**: Tests each core individually to its limit, then final verification

### Crash Recovery
**Added**: Full crash detection and recovery system
- Saves progress after each successful test
- Detects crashes on restart
- Offers to continue from last completed core
- Handles multiple crashes gracefully

### Stress Test Optimization
**Added**: Gradual load decrease to prevent crashes
- Test phases: 100% → 90% → 80% CPU load
- Prevents crashes from sudden load spikes
- Uses stress-ng `--cpu-load` parameter

---

## 🚀 Frequency Wizard Improvements

### Automatic Per-Core Testing
**Fixed**: Frequency wizard now tests all 4 cores automatically
- **Before**: Required 4 separate runs (one per core)
- **After**: Single run tests all cores sequentially
- Generates complete frequency curves for entire CPU
- Collects per-core statistics automatically

### Start Button
**Fixed**: Start button now works correctly
- Added missing `checkFrequencyWizardCrash()` API method
- Proper error handling and state management

---

## 📋 Technical Details

### Backend Changes
- Added `game_only_mode` field to frequency wizard preset structure
- Updated `update_frequency_wizard_preset()` to support `game_only_mode`
- Startup logic checks frequency wizard presets with `apply_on_startup`
- Game-only logic checks frequency wizard presets with `game_only_mode`
- Modified `_run_step_down_search()` for correct per-core algorithm
- Added `_set_crash_flag()` and `_persist_state()` for crash recovery
- Added gradual load decrease to `run_per_core_test()`

### Frontend Changes
- Created `FrequencyWizardPresets.tsx` component (Decky UI compliant)
- Integrated into `WizardMode.tsx` under Frequency Wizard section
- Added `checkFrequencyWizardCrash()` method to `Api.ts`
- Fixed `FrequencyWizard.tsx` start button handler
- All components fit properly in QAM menu (no overflow)

---

## 🎮 Usage Guide

### Creating a Preset
1. Navigate to **Wizard Mode → Frequency-Based Wizard**
2. Click **Start** to run the wizard
3. Wait for all 4 cores to complete testing
4. Preset is automatically created with chip grade

### Managing Presets
1. Navigate to **Frequency Wizard Presets** section
2. View chip grade and creation date
3. Toggle **Apply on Startup** or **Game Only Mode** as needed
4. Click **Apply** to activate the preset
5. Click **Show** to view per-core statistics
6. Click **Delete** to remove the preset

### Automation
- **Apply on Startup**: Preset applies when DeckTune starts
- **Game Only Mode**: Preset applies only when a game launches
- Priority: Wizard presets → Frequency wizard presets → Game profiles

---

## 🐛 Known Issues
- Frequency wizard game_only_mode requires gymdeck3 integration (not yet implemented)
- TypeScript diagnostic errors for JSX elements (false positives, build succeeds)

---

## 📦 Installation

Download and install via Decky Loader Developer Mode:

1. Download `DeckTune-v3.5.0.zip`
2. Open Decky Loader Settings → Developer Mode
3. Install from ZIP

Or use the in-app updater from Settings menu!

---

## 🔗 Links
- [GitHub Repository](https://github.com/yourusername/DeckTune)
- [Documentation](https://github.com/yourusername/DeckTune/tree/main/docs)
- [Issue Tracker](https://github.com/yourusername/DeckTune/issues)
