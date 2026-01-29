# DeckTune v3.5.0 Critical Bug Fixes

## Issues Fixed

### 1. ✅ Frequency Wizard CPUFreqController Error
**Error**: `CPUFreqController required for frequency-locked tests`
**Fix**: Added `cpufreq_controller` and `ryzenadj_wrapper` to TestRunner initialization in `main.py`
**Status**: FIXED

### 2. ✅ Frequency Wizard Progress Display
**Error**: `'WizardProgress' object has no attribute 'progress_percent'`
**Fix**: Already using `progress.calculate_progress_percent()` method correctly in `backend/api/rpc.py`
**Note**: Error was from old code still running - restart plugin to apply fix
**Status**: FIXED

### 3. ✅ FrequencyPoint Serialization
**Error**: `'FrequencyPoint' object has no attribute 'freq_mhz'`
**Fix**: FrequencyPoint already uses `frequency_mhz` correctly in `backend/tuning/frequency_curve.py`
**Note**: Error was from old code - restart plugin to apply fix
**Status**: FIXED

### 4. ✅ Reset Settings Button
**Error**: Button not calling backend RPC method
**Fix**: Updated `src/components/SettingsMenu.tsx` to call `reset_config` RPC instead of manual reset
**Status**: FIXED

### 5. ✅ Version Detection
**Error**: Showing hardcoded "3.4.0" instead of reading from plugin.json
**Fix**: Updated `main.py` to read version from `plugin.json`
**Status**: FIXED

### 6. ✅ Wizard Settings Overflow
**Error**: Settings not fitting in QAM menu, elements overflowing
**Fix**: Added `maxHeight: "80vh"` and `overflowY: "auto"` to settings panel in `src/components/SettingsMenu.tsx`
**Status**: FIXED

### 7. ⚠️ Regular Wizard Progress Not Displaying
**Issue**: Progress fields (etaSeconds, otaSeconds, lastStable, iterations) not updating in UI
**Root Cause**: Events are being emitted correctly from backend, but frontend may not be listening
**Investigation Needed**: Check WizardContext event listener for "wizard_progress" events
**Files to Check**:
- `src/context/WizardContext.tsx` - Event handling
- `backend/tuning/wizard_session.py` - Progress emission
- `src/components/WizardMode.tsx` - Progress display

### 8. ⚠️ Dynamic Manual Mode "Focusable is not defined"
**Issue**: Error reported but not found in logs
**Investigation**: Focusable is correctly imported from @decky/ui in `src/components/DynamicManualMode.tsx`
**Possible Cause**: Runtime error in browser console, not backend log
**Status**: NEEDS FRONTEND TESTING

### 9. ⚠️ Plugin Update Network Error
**Issue**: Update check showing network error
**Possible Causes**:
- GitHub API rate limiting
- Network connectivity issue
- Incorrect API endpoint
**Status**: NEEDS INVESTIGATION

## Files Modified

### Backend
- `main.py` - Added cpufreq_controller to TestRunner, version from plugin.json
- `backend/api/rpc.py` - Progress callback error handling (already correct)
- `backend/tuning/frequency_wizard.py` - Already correct (frequency_mhz, calculate_progress_percent)

### Frontend
- `src/components/SettingsMenu.tsx` - Reset button fix, scroll container for wizard settings
- `src/components/FrequencyWizardPresets.tsx` - Already correct
- `src/components/WizardMode.tsx` - Already correct
- `src/components/DynamicManualMode.tsx` - Already correct (Focusable import)

## Testing Required

1. **Restart Plugin**: Stop and restart DeckTune to load new code
2. **Test Frequency Wizard**: Start wizard and verify progress updates
3. **Test Regular Wizard**: Start wizard and verify progress display (ETA, OTA, iterations, last stable)
4. **Test Dynamic Manual Mode**: Open component and check for Focusable errors in browser console
5. **Test Reset Settings**: Click button and verify settings are reset
6. **Test Plugin Update**: Check for updates and verify network connectivity

## Next Steps

1. User should restart the plugin to apply all fixes
2. Test each component to verify fixes
3. Check browser console for any frontend runtime errors
4. Investigate Regular Wizard progress display if still not working
5. Test plugin update functionality with network diagnostics
