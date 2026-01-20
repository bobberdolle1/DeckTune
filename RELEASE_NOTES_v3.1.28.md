# DeckTune v3.1.28 - Wizard Mode Critical Fix

## 🔧 Critical Fixes

### Wizard Mode Complete Rewrite
**Problem**: Wizard returned fake success (-50mV for all cores) without proper validation.

**Solution**: Production-grade hardware validation system:

#### Backend Validation (wizard_session.py)
- ✅ Voltage verification via hwmon sensors
- ✅ Real-time MCE/WHEA hardware error detection
- ✅ 60-second verification pass with automatic rollback
- ✅ Parallel dmesg monitoring during stress tests
- ✅ Tests now properly FAIL when detecting instability

#### Enhanced Test Runner (runner.py)
- ✅ `monitor_dmesg_realtime()` - Real-time hardware error detection
- ✅ `read_voltage_sensors()` - Verify voltage application
- ✅ `run_per_core_test()` - Per-core stress testing with taskset
- ✅ `run_benchmark_with_progress()` - Real CPU benchmark

#### Frontend Improvements (WizardMode.tsx)
- ✅ "Run Benchmark" now functional with real metrics
- ✅ "Apply & Save as Preset" automatic (no manual steps)
- ✅ Benchmark results display (score, temp, freq)
- ✅ Proper gamepad navigation via Focusable components

#### Settings Fix (SettingsContext.tsx)
- ✅ Expert Mode toggle calls proper RPC methods
- ✅ Confirmation handling for enable/disable

## 🎯 Impact

**Before**: Wizard always returned -50mV regardless of actual stability
**After**: Wizard properly validates stability and fails when detecting:
- Hardware errors (MCE/WHEA)
- Voltage application failures
- Instability during 60s verification pass

## 📋 Testing Required

1. Run wizard on actual Steam Deck hardware
2. Verify tests fail at aggressive undervolt values
3. Confirm hardware errors are detected
4. Validate benchmark returns real metrics
5. Check presets are saved correctly with chip grade

## 🔍 Technical Details

### Validation Chain
```
1. Apply voltage offset
2. Verify via sensors (hwmon)
3. Run stress test (30s or 120s)
4. Monitor dmesg for MCE/WHEA in parallel
5. Check system metrics
6. Run 60s verification pass
7. Rollback if unstable (+5mV safety margin)
8. Retry verification with safer values
9. Fallback to -10mV if still unstable
```

### Files Modified
- `backend/tuning/runner.py` - 4 new methods (200+ lines)
- `backend/tuning/wizard_session.py` - Enhanced validation (150+ lines)
- `backend/api/rpc.py` - Benchmark RPC method (40 lines)
- `main.py` - Exposed benchmark (5 lines)
- `src/components/WizardMode.tsx` - UI fixes (80 lines)
- `src/context/SettingsContext.tsx` - Expert Mode fix (15 lines)

## ⚠️ Breaking Changes
None - fully backward compatible

## 🚀 Deployment
Standard Decky Loader installation via developer mode or plugin store.
