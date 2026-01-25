# 🎯 DeckTune v3.3.0 — Frequency-Based Voltage Wizard

**Release Date**: January 25, 2026

---

## 🌟 Headline Feature: Frequency-Based Voltage Curves

DeckTune 3.3.0 introduces **Frequency-Based Voltage Wizard** — a revolutionary approach to CPU undervolting that maps specific frequencies to optimal voltage offsets. Unlike traditional load-based methods, frequency-based mode provides surgical precision across the entire CPU frequency spectrum (400-3500 MHz).

### Why Frequency-Based?

**Traditional Load-Based Mode:**
- Adjusts voltage based on CPU utilization percentage (0-100%)
- Simple but imprecise — same load can occur at different frequencies
- Good for consistent workloads

**New Frequency-Based Mode:**
- Maps voltage to actual CPU frequency (400-3500 MHz)
- Precise control at every frequency point
- Optimal efficiency across full frequency spectrum
- Perfect for gaming and mixed workloads

---

## ✨ Key Features

### 🧙 Automated Curve Generation
- **Binary Search Algorithm** — Efficiently discovers maximum stable voltage at each frequency
- **Configurable Testing** — Frequency range (400-3500 MHz), step size (50-500 MHz), test duration (10-120s)
- **Quick Presets** — Conservative (~10 min), Balanced (~15 min), Aggressive (~30 min)
- **Smart Optimization** — Adaptive step size skips redundant tests in stable regions

### 📊 Real-Time Visualization
- **Interactive Charts** — Frequency-voltage relationship with Recharts
- **Live Operating Point** — Current frequency and voltage highlighted
- **Stable/Failed Points** — Visual distinction between successful and failed tests
- **Interpolated Curve** — Smooth line showing voltage across full spectrum
- **Hover Tooltips** — Exact frequency and voltage values

### 🛡️ Safety Features
- **Temperature Monitoring** — Aborts if CPU exceeds 85°C
- **Timeout Detection** — Detects frozen tests (duration + 30s)
- **Consecutive Failure Skip** — Skips frequency after 3 failures
- **Verification Tests** — Validates curve at 3-5 random frequencies
- **State Restoration** — Cancellation restores original settings
- **Boundary Clamping** — Safe voltage for out-of-range frequencies

### 🎮 Profile Integration
- **Game Profiles** — Save frequency curves for automatic per-game switching
- **Export/Import** — Share curves with other users
- **Fallback Support** — Profiles without curves use load-based mode
- **Seamless Switching** — Toggle between load-based and frequency-based anytime

---

## 🚀 Performance

| Preset | Frequency Step | Test Duration | Total Time | Precision |
|--------|---------------|---------------|------------|-----------|
| **Conservative** | 200 MHz | 20s | ~10 min | Good |
| **Balanced** | 100 MHz | 30s | ~15 min | Better |
| **Aggressive** | 50 MHz | 60s | ~30 min | Best |

**Runtime Overhead**: < 1% CPU for frequency monitoring

---

## 📖 How to Use

### Quick Start (Balanced Preset)
1. Open DeckTune → Expert Mode → Frequency Wizard
2. Click "Balanced" preset button
3. Click "Start Wizard" and wait ~15 minutes
4. Review curve on interactive chart
5. Click "Apply Curve" to activate

### Custom Configuration
```
Frequency Range: 400-3500 MHz
Step Size: 100 MHz (31 test points)
Test Duration: 30 seconds per frequency
Voltage Start: -30 mV
Voltage Step: 2 mV
Safety Margin: 5 mV
```

### Example Results
```
400 MHz  → -45 mV  (aggressive at low freq)
800 MHz  → -40 mV
1200 MHz → -35 mV
1600 MHz → -30 mV
2000 MHz → -25 mV
2400 MHz → -20 mV
2800 MHz → -15 mV
3200 MHz → -10 mV  (conservative at high freq)
3500 MHz → -5 mV
```

---

## 🔧 Technical Implementation

### Backend (Python)
- **`backend/platform/cpufreq.py`** — CPU frequency control via userspace governor
- **`backend/tuning/frequency_curve.py`** — Curve data model with interpolation
- **`backend/tuning/frequency_wizard.py`** — Automated testing with binary search
- **`backend/api/rpc.py`** — 6 new RPC methods for wizard control
- **`backend/core/settings_manager.py`** — Curve persistence in settings.json
- **`backend/dynamic/profile_manager.py`** — Profile integration

### Rust (gymdeck3)
- **`gymdeck3/src/dynamic/frequency_curve.rs`** — Curve storage and interpolation
- **`gymdeck3/src/dynamic/frequency_controller.rs`** — Voltage controller
- **`gymdeck3/src/dynamic/metrics_monitor.rs`** — Frequency telemetry

### Frontend (TypeScript/React)
- **`src/components/FrequencyWizard.tsx`** — Main wizard UI (650+ lines)
- **`src/components/FrequencyCurveChart.tsx`** — Curve visualization (280+ lines)
- **`src/api/Api.ts`** — API client methods
- **`src/components/DeckTuneApp.tsx`** — Mode integration

---

## 🧪 Testing

**25 Property-Based Tests** (100+ iterations each):
- Configuration validation completeness
- Curve serialization round-trip
- Interpolation correctness
- Boundary clamping
- Wizard frequency coverage
- Mode switching consistency
- Cancellation state restoration
- Failure recovery with safety margin
- Profile curve preservation
- Temperature safety abort
- Timeout detection
- Consecutive failure skip
- Visualization data integrity
- Verification test execution
- Adaptive step optimization

**Test Coverage:**
- Python: 25 property-based tests + unit tests (hypothesis)
- Rust: 2 property-based tests (proptest)
- Frontend: Component tests for UI and visualization
- Integration: End-to-end wizard flow tests

---

## 📚 Documentation

- **[Frequency Wizard Guide](docs/FREQUENCY_WIZARD_GUIDE.md)** — Complete user guide with screenshots
- **[Frequency Wizard API](docs/FREQUENCY_WIZARD_API.md)** — API reference for developers
- **[README.md](README.md)** — Updated with FAQ and troubleshooting

---

## 🔄 When to Use Each Mode

### Use Frequency-Based Mode When:
- Gaming with varying CPU frequencies
- Mixed workloads (browsing, video, gaming)
- Per-game optimization needed
- Maximum efficiency across full spectrum desired

### Use Load-Based Mode When:
- Consistent workloads (video playback, idle)
- Quick setup needed
- General-purpose usage
- Simpler configuration preferred

---

## ⚙️ Requirements

- **Root Access** — Required for cpufreq userspace governor
- **Linux Kernel 4.0+** — With cpufreq support
- **AMD Ryzen Processor** — For ryzenadj compatibility
- **Temperature Sensors** — Accessible via hwmon

---

## 🐛 Troubleshooting

### Permission Errors
```bash
# Check available governors
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors

# Ensure root access for DeckTune
```

### Wizard Takes Too Long
- Use Conservative preset (200 MHz step, 20s duration)
- Enable adaptive step size
- Reduce frequency range (e.g., 800-3000 MHz)

### System Instability
- Increase safety margin (10-15 mV)
- Use longer test duration (60s)
- Reduce voltage aggressiveness (start at -20 mV)

### Curve Doesn't Improve Efficiency
- Verify frequency-based mode is enabled
- Check CPU frequency varies during workload
- Compare with load-based mode using benchmarks
- Some workloads may benefit more from load-based

---

## 🎉 What's Next?

DeckTune 3.3.0 represents a major leap in precision undervolting. The Frequency-Based Voltage Wizard provides unprecedented control over CPU voltage across the entire frequency spectrum, enabling optimal efficiency for every workload.

**Try it now:**
1. Update to v3.3.0
2. Open Expert Mode → Frequency Wizard
3. Run Balanced preset
4. Enjoy better efficiency and battery life!

---

## 📦 Installation

### Quick Install
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

### Manual Install
1. Download `DeckTune-v3.3.0.zip` from [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Transfer to Steam Deck
3. Enable Developer Mode in Decky Loader
4. Install from zip

---

## 🙏 Acknowledgments

Special thanks to the Steam Deck community for testing and feedback during development.

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
**Previous Release**: [v3.2.0](RELEASE_NOTES_v3.2.0.md)
