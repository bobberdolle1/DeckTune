# DeckTune v3.5.6 Release Notes

## 🐛 Critical Fixes

### Wizard Cancellation
- **Fixed: Cancel doesn't stop stress-ng process**
  - Added `cancel_current_test()` method to TestRunner
  - Wizard cancellation now properly kills running stress-ng processes
  - Both regular wizard and frequency wizard call process termination on cancel
  - Prevents CPU load persisting after wizard cancellation

### Regular Wizard
- **Fixed: Verification test infinite loop**
  - Changed verification from `cpu_long` (5 minutes) to new `cpu_verify` (60 seconds)
  - Added cancellation check before starting verification
  - Verification now completes in stated 60 seconds instead of appearing to hang
  - "Running 60s verification test" message now accurate

### Frequency Wizard
- **Fixed: Progress bar and ETA not updating**
  - Added real-time event emission in progress callback
  - Progress updates now emit `frequency_wizard_progress` events
  - Frontend receives live updates instead of polling
  - ETA and current frequency display now work correctly

- **Fixed: Preset not created after completion**
  - Fixed `self.config` → `wizard.config` typo in preset creation
  - Presets now properly saved after wizard completion
  - Completion event emitted with preset information

- **Fixed: Cannot restart wizard without reboot**
  - Proper cleanup of wizard instances after completion/cancellation
  - Session management improved to allow immediate restart

### UI
- **Removed version display from main menu**
  - Cleaned up HeaderBar component
  - Version only visible in Settings menu

## 🔧 Technical Changes

### backend/tuning/runner.py
- Added `cancel_current_test()` method for process termination
- Added `cpu_verify` test case (60s duration)
- Improved process cleanup on cancellation

### backend/tuning/wizard_session.py
- Updated `cancel()` to call `cancel_current_test()`
- Changed verification test from `cpu_long` to `cpu_verify`
- Added cancellation check before verification start

### backend/tuning/frequency_wizard.py
- Updated `cancel()` to kill running tests
- Improved cancellation handling

### backend/api/rpc.py
- Added event emission in `_frequency_wizard_progress_callback()`
- Fixed preset creation config reference
- Real-time progress updates via events

### src/components/HeaderBar.tsx
- Removed version prop and display
- Simplified component interface

## 📝 Notes

This release addresses all critical issues reported in testing:
- Wizard cancellation now works immediately
- Verification tests complete in reasonable time
- Frequency wizard shows accurate progress
- Presets are created successfully
- Wizards can be restarted without system reboot

---

**Installation**: Update via Decky Loader plugin store or manual installation from GitHub releases.
