# DeckTune v3.5.7 Release Notes

**Release Date:** January 29, 2026

## 🐛 Bug Fixes

### Wizard Completion & Results
- **Fixed chip grading calculation** — Gold tier now correctly awarded at -45mV (was incorrectly showing Bronze)
- **Auto-preset creation** — Wizard now automatically creates presets after completion
- **Results screen display** — Fixed data formatting and display issues
- **Preset tracking** — Added preset_id to completion event for frontend tracking

### Progress Bar Accuracy
- **Fixed progress calculation** — Corrected from 10 to 28 iterations for accurate percentage
- **Real-time updates** — Progress bar now shows accurate percentage during per-core testing
- **Debug logging** — Added progress update logging for troubleshooting

### Process Cleanup
- **Orphaned process termination** — Added `pkill -9 stress-ng` to kill lingering processes
- **CPU load persistence fix** — CPU load no longer persists after wizard completion
- **Cleanup guarantee** — Cleanup runs in wizard finally block

### Event Emission Errors
- **Fixed EventEmitter signature error** — Resolved 613+ occurrences in logs
- **Method signature correction** — Changed `emit_status(event, data)` to `_emit_event(event, data)`
- **Error-free progress events** — Progress events now emit without errors

### Data Serialization
- **Fixed asdict() TypeError** — Resolved curve_data serialization issues
- **Type checking** — Added type checking for dict vs dataclass instances
- **Preset generation stability** — Preset generation no longer crashes

## 🔧 Technical Details

### Backend Changes
- Enhanced `_calculate_chip_grade()` with logging
- Fixed `_emit_progress()` iteration estimate (28 iterations)
- Added type checking in `save_as_wizard_preset()`
- Enhanced `cancel_current_test()` with pkill
- Improved error handling in event emission

### Frontend Changes
- Added snake_case to camelCase conversion in WizardContext
- Improved preset tracking with preset_id

## 📦 Installation

Download `DeckTune-v3.5.7.zip` and install via Decky Loader.

## 🔄 Upgrading from v3.5.6

This is a bug fix release. All settings and presets will be preserved.

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

**Note:** This release focuses on stability improvements for the Frequency Wizard feature, fixing critical issues with progress tracking, process cleanup, and preset generation.
