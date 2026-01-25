# 🎉 DeckTune v3.2.0 Release Summary

## ✅ Release Complete!

**Version**: v3.2.0  
**Release Date**: January 24, 2026  
**GitHub Release**: https://github.com/bobberdolle1/DeckTune/releases/tag/v3.2.0

---

## 📦 What Was Released

### 1. Dynamic Manual Mode Feature
- ✅ Per-core voltage curve control (4 cores)
- ✅ Simple Mode (all cores) and Expert Mode (per-core)
- ✅ Real-time voltage curve visualization
- ✅ Live metrics monitoring (500ms polling)
- ✅ Time-series graphs with 60-point FIFO buffer
- ✅ QAM-optimized UI (fits ~400px width)
- ✅ Full gamepad navigation support
- ✅ Multi-layer safety validation
- ✅ Last Known Good (LKG) backup system
- ✅ Configuration persistence (localStorage + backend)

### 2. Documentation
- ✅ [User Guide](docs/DYNAMIC_MANUAL_MODE_GUIDE.md) - Complete usage instructions
- ✅ [API Reference](docs/DYNAMIC_MANUAL_MODE_API.md) - RPC methods documentation
- ✅ [Troubleshooting Guide](docs/DYNAMIC_MANUAL_MODE_TROUBLESHOOTING.md) - Common issues
- ✅ [QAM Optimization](docs/QAM_OPTIMIZATION.md) - UI design principles
- ✅ Updated README.md with new feature section
- ✅ Updated CHANGELOG.md with detailed release notes

### 3. Testing
- ✅ 25 correctness properties with property-based testing
- ✅ 100+ iterations per property
- ✅ 9 integration tests for end-to-end workflows
- ✅ Round-trip testing for persistence
- ✅ Curve calculation verification
- ✅ Validation and clamping tests

### 4. UI Optimizations for QAM
- ✅ CurveVisualization: 340x160px responsive SVG
- ✅ MetricsDisplay: Compact grid (8px padding, 16px fonts)
- ✅ CoreTabs: Reduced spacing (4px gaps, 10px fonts)
- ✅ All components fit without horizontal scrolling
- ✅ Optimized for 7" screen (1280x800)

---

## 🚀 Installation Instructions

### Quick Install (Recommended)
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

### Manual Install
1. Download `DeckTune-v3.2.0.zip` from [GitHub Releases](https://github.com/bobberdolle1/DeckTune/releases/tag/v3.2.0)
2. Transfer to Steam Deck
3. Open Decky Loader → Settings → Developer Mode
4. Click "Install from ZIP"
5. Select `DeckTune-v3.2.0.zip`
6. Restart Decky Loader

---

## 📊 Release Statistics

- **Files Changed**: 58 files
- **Lines Added**: 16,706 insertions
- **Lines Removed**: 876 deletions
- **New Components**: 5 React components
- **New Backend Modules**: 4 Python modules
- **New Tests**: 12 test files
- **Documentation Pages**: 4 new guides
- **ZIP Size**: 5.11 MB

---

## 🎯 Key Features

### Per-Core Voltage Curves
Each CPU core can have its own voltage curve defined by:
- **MinimalValue**: Conservative voltage at low load (-100 to 0 mV)
- **MaximumValue**: Aggressive voltage at high load (-100 to 0 mV)
- **Threshold**: Load percentage where transition occurs (0-100%)

### Real-Time Visualization
- Live voltage curve graphs with threshold markers
- Current operating point indicator
- Per-core metrics (load, voltage, frequency, temperature)
- Time-series graphs with 30 seconds of history

### Safety Features
- Multi-layer validation (frontend, backend, hardware)
- Platform-specific voltage limits
- Dangerous configuration warnings
- Last Known Good (LKG) automatic backup
- Automatic rollback on errors

### Gamepad Navigation
- D-pad Up/Down: Switch cores
- D-pad Left/Right: Navigate controls
- L1/R1: Adjust sliders
- A button: Activate buttons
- Visual focus indicators

---

## 📝 Git Commit

```
commit 9d4f89d
Author: bobberdolle1
Date: January 24, 2026

Release v3.2.0 - Dynamic Manual Mode with QAM Optimization

58 files changed, 16706 insertions(+), 876 deletions(-)
```

---

## 🔗 Links

- **GitHub Release**: https://github.com/bobberdolle1/DeckTune/releases/tag/v3.2.0
- **Download ZIP**: https://github.com/bobberdolle1/DeckTune/releases/download/v3.2.0/DeckTune-v3.2.0.zip
- **Repository**: https://github.com/bobberdolle1/DeckTune
- **Issues**: https://github.com/bobberdolle1/DeckTune/issues

---

## 🎮 Next Steps

1. **Install the plugin** using one of the methods above
2. **Read the User Guide** at [docs/DYNAMIC_MANUAL_MODE_GUIDE.md](docs/DYNAMIC_MANUAL_MODE_GUIDE.md)
3. **Try Simple Mode** first with safe defaults (-30mV / -15mV / 50%)
4. **Monitor metrics** to ensure stability
5. **Fine-tune** in Expert Mode for optimal performance

---

## 🙏 Thank You!

Thank you to the Decky Loader team and the Steam Deck community for making this possible!

**Enjoy Dynamic Manual Mode! 🎮⚡**
