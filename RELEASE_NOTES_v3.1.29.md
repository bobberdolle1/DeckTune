# DeckTune v3.1.29 - Wizard Mode Complete Implementation

## 🎯 Major Features

### Wizard Mode Full Rewrite
Complete implementation of automated undervolt discovery with gymdeck3 integration.

#### Core Features
- ✅ **Per-core testing** - Individual core validation with taskset
- ✅ **Dynamic undervolt** - gymdeck3 integration for adaptive voltage
- ✅ **Hardware validation** - Real-time MCE/WHEA error detection
- ✅ **Crash recovery** - Automatic rollback with dirty exit detection
- ✅ **Chip grading** - Bronze/Silver/Gold/Platinum quality tiers
- ✅ **Curve visualization** - Interactive SVG chart with pass/fail/crash indicators
- ✅ **Progress tracking** - Real-time ETA/OTA with heartbeat
- ✅ **Wizard presets** - Dedicated preset system with full metadata
- ✅ **History browser** - View, compare, and manage all wizard runs
- ✅ **Apply options** - Apply on Startup and Game Only Mode integration

#### Backend Implementation

**wizard_session.py**:
- Per-core stress testing with `_test_offset_per_core()`
- Dynamic undervolt integration via `DynamicController`
- 60-second verification pass with automatic rollback
- Comprehensive hardware error monitoring
- Chip quality grading algorithm
- Curve data collection for visualization

**runner.py**:
- `run_per_core_test()` - Core-specific stress testing
- `monitor_dmesg_realtime()` - Hardware error detection
- `read_voltage_sensors()` - Voltage verification
- `run_benchmark_with_progress()` - Real-time benchmark metrics

**rpc.py**:
- `start_wizard()` - Launch wizard session
- `cancel_wizard()` - Cancel running session
- `apply_wizard_result()` - Apply with dynamic preset creation
- `run_wizard_benchmark()` - Performance benchmarking
- `get_wizard_results_history()` - Retrieve all runs

#### Frontend Implementation

**WizardMode.tsx**:
- Configuration screen with aggressiveness/duration settings
- Real-time progress with ETA/OTA display
- Results screen with chip grade badge
- Curve visualization with pass/fail indicators
- Benchmark integration with progress bar

**WizardHistory.tsx**:
- Complete history of all wizard runs
- Detailed view with curve data
- Apply/Delete actions
- Chip grade filtering
- Timestamp sorting

**SettingsMenu.tsx**:
- Binning Settings (test duration, step size, start value)
- Expert Mode toggle with confirmation
- Persistent configuration storage

**FocusableButton.tsx**:
- Fixed mouse click handling
- Gamepad navigation support
- Visual focus indicators

### Settings & Persistence

**All settings persist across restarts**:
- Wizard configuration (aggressiveness, duration)
- Binning settings (test_duration, step_size, start_value)
- Expert Mode state
- Apply on Startup preference
- Game Only Mode preference
- Wizard results history (last 20 runs)

### UI/UX Improvements

**Gamepad Navigation**:
- D-pad up/down for Wizard/Expert mode switching
- Focusable components throughout
- Proper focus indicators

**Visual Feedback**:
- Real-time progress bars
- Chip grade badges with glow effects
- Color-coded curve points (green/red/orange)
- Status indicators (ON/OFF/DYN)

**Error Handling**:
- Crash recovery modal with details
- Hardware error detection alerts
- Graceful fallbacks on failures

## 🔧 Technical Details

### Validation Chain
```
1. Apply voltage offset (per-core or all cores)
2. Verify via hwmon sensors
3. Run stress test (30s or 120s)
4. Monitor dmesg for MCE/WHEA in parallel
5. Check system metrics (temp, freq)
6. Record curve data point
7. Run 60s verification pass
8. Rollback if unstable (+5mV safety margin)
9. Create dynamic preset with gymdeck3 config
```

### Chip Grading Scale
- **Platinum**: ≥ -51mV (Top 1-5%)
- **Gold**: -36 to -50mV (Top 20%)
- **Silver**: -21 to -35mV (Top 40%)
- **Bronze**: -10 to -20mV (Bottom 60%)

### Aggressiveness Levels
- **Safe**: 2mV steps, +10mV margin, ~15-20 min
- **Balanced**: 5mV steps, +5mV margin, ~5-10 min
- **Aggressive**: 10mV steps, +2mV margin, ~3-5 min

## 📋 Files Modified

### Backend
- `backend/tuning/wizard_session.py` - Complete rewrite (800+ lines)
- `backend/tuning/runner.py` - Added 4 new methods (200+ lines)
- `backend/api/rpc.py` - Wizard RPC methods (150+ lines)
- `backend/api/events.py` - Wizard events (30 lines)
- `main.py` - Wizard initialization (50 lines)

### Frontend
- `src/components/WizardMode.tsx` - Complete redesign (600+ lines)
- `src/components/WizardHistory.tsx` - New component (400+ lines)
- `src/components/SettingsMenu.tsx` - Binning settings (100+ lines)
- `src/components/FocusableButton.tsx` - Click fix (5 lines)
- `src/context/WizardContext.tsx` - State management (200+ lines)
- `src/context/SettingsContext.tsx` - Settings persistence (50 lines)

## ⚠️ Breaking Changes
None - fully backward compatible

## 🚀 Installation
1. Download `DeckTune-v3.1.29.zip`
2. Open Decky Loader in Developer Mode
3. Install from ZIP
4. Restart Steam

## 🧪 Testing Checklist
- [x] Per-core testing validates individual cores
- [x] Hardware errors detected (MCE/WHEA)
- [x] Dynamic presets created with gymdeck3
- [x] Crash recovery works after system crash
- [x] Benchmark shows real metrics with progress
- [x] Settings persist after restart
- [x] Gamepad navigation functional
- [x] Expert Mode toggle works
- [x] Apply on Startup works
- [x] Game Only Mode works
- [x] Wizard history browsable
- [x] Curve visualization accurate

## 📝 Known Limitations
- GPU/SOC domain testing not yet implemented (CPU only)
- Curve chart is basic SVG (no zoom/pan)
- Maximum 20 wizard results stored

## 🎯 Next Steps
- GPU/SOC domain support
- Enhanced curve visualization (recharts)
- Export/import wizard results
- Comparison view for multiple runs
