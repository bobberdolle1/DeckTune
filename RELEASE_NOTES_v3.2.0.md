# 🎮 DeckTune v3.2.0 - Dynamic Manual Mode Release

## 🚀 Major New Feature: Dynamic Manual Mode

We're excited to announce **Dynamic Manual Mode** - a complete per-core voltage curve control system with real-time visualization, designed specifically for Steam Deck's Quick Access Menu!

### ✨ What's New

#### Per-Core Voltage Curves
- **Independent Control**: Configure unique voltage curves for each CPU core (0-3)
- **Three Parameters**:
  - 🔽 **MinimalValue**: Conservative voltage at low CPU load (-100 to 0 mV)
  - 🔼 **MaximumValue**: Aggressive voltage at high CPU load (-100 to 0 mV)
  - 📊 **Threshold**: CPU load percentage where transition occurs (0-100%)

#### Two Modes for Every User
- **🎯 Simple Mode**: Apply identical settings to all cores - perfect for beginners
- **⚙️ Expert Mode**: Fine-tune each core individually - for power users

#### Real-Time Visualization
- **📈 Live Voltage Curves**: See your voltage curve in real-time with threshold markers
- **📊 Metrics Dashboard**: Monitor load, voltage, frequency, and temperature per core
- **📉 Time-Series Graphs**: Last 60 data points (30 seconds) with smooth animations
- **🎯 Current Operating Point**: See exactly where your CPU is on the curve

#### QAM-Optimized Interface
- **📱 Compact Design**: Fits perfectly in Decky Loader's Quick Access Menu (~400px width)
- **📐 Responsive Charts**: SVG graphics scale beautifully
- **🎨 Clean Layout**: Optimized fonts and spacing for 7" screen
- **🚫 No Scrolling**: Everything fits without horizontal scrolling

#### Full Gamepad Support
- **🎮 D-pad Up/Down**: Switch between cores
- **🎮 D-pad Left/Right**: Navigate controls
- **🎮 L1/R1**: Adjust slider values
- **🎮 A button**: Activate buttons
- **👁️ Visual Feedback**: Clear focus indicators for gamepad navigation

#### Safety First
- **✅ Multi-Layer Validation**: Frontend, backend, and hardware checks
- **🛡️ Platform Limits**: Hardware-specific voltage limits enforced
- **⚠️ Dangerous Config Warnings**: Alerts for voltages below -50mV
- **💾 Last Known Good (LKG)**: Automatic backup after 30s of stable operation
- **🔄 Automatic Rollback**: Recovery from unstable configurations
- **🚦 Status Indicator**: Visual Active/Inactive state

### 📚 Comprehensive Documentation

We've created extensive documentation to help you get started:

- **[📖 User Guide](docs/DYNAMIC_MANUAL_MODE_GUIDE.md)** - Complete usage instructions with examples
- **[🔧 API Reference](docs/DYNAMIC_MANUAL_MODE_API.md)** - RPC methods and data structures
- **[🔍 Troubleshooting](docs/DYNAMIC_MANUAL_MODE_TROUBLESHOOTING.md)** - Common issues and solutions
- **[🎨 QAM Optimization](docs/QAM_OPTIMIZATION.md)** - UI design principles

### 🎯 Quick Start

1. Open DeckTune in Decky Loader
2. Navigate to **Expert Mode** → **Dynamic Manual** tab
3. Choose **Simple Mode** (all cores) or **Expert Mode** (per-core)
4. Adjust voltage curve parameters:
   - Start with safe defaults: -30mV / -15mV / 50%
   - Or try presets: Battery Saver, Balanced, Performance
5. Click **Apply** to save configuration
6. Click **Start** to activate dynamic voltage control
7. Monitor real-time metrics and graphs

### 🔧 Technical Highlights

- **Frontend**: TypeScript/React with Recharts for visualization
- **Backend**: Python with comprehensive validation and error handling
- **Testing**: 25 correctness properties with 100+ iterations each
- **Performance**: 500ms polling, 60-point FIFO buffer, smooth animations
- **Integration**: Seamless integration with existing Expert Mode

### 📦 Installation

#### Quick Install (Recommended)
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

#### Manual Install
1. Download `DeckTune-v3.2.0.zip` from [Releases](https://github.com/bobberdolle1/DeckTune/releases/tag/v3.2.0)
2. Transfer to your Steam Deck
3. Enable Developer Mode in Decky Loader settings
4. Install the plugin from the archive

### 🐛 Bug Fixes & Improvements

- **QAM Optimization**: All UI components now fit perfectly in Quick Access Menu
- **Responsive Charts**: SVG graphics scale properly without overflow
- **Compact Metrics**: Reduced padding and font sizes for better fit
- **Smooth Animations**: 300ms transitions for graph updates
- **Error Handling**: Comprehensive error boundaries and recovery

### 🙏 Acknowledgments

Special thanks to the Decky Loader team and the Steam Deck community for their continued support!

### 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**Enjoy Dynamic Manual Mode! 🎮⚡**

If you encounter any issues, please check our [Troubleshooting Guide](docs/DYNAMIC_MANUAL_MODE_TROUBLESHOOTING.md) or open an issue on GitHub.
