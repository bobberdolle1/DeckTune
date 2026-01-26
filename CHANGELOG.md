# Changelog

## [3.4.0] - 2026-01-26

### Added
- **In-App Update System** — Check and install updates directly from Settings
  - GitHub releases integration with version comparison
  - Real-time progress tracking with ETA
  - Progress bar with stage indicators (downloading, extracting, installing)
  - Automatic plugin reload after installation
  - User data preservation during updates
  - Release notes preview before installation

### Technical Details
- Backend: `UpdateManager` with async download/install pipeline
- Frontend: Progress polling with 1-second intervals
- Stages: Download (0-40%), Extract (45-55%), Install (60-90%), Finalize (92-95%), Complete (100%)
- Safety: Backup creation, settings preservation, binary permissions restoration

## [3.3.4] - 2026-01-26

### Fixed
- **Reset All Settings** — Fixed non-functional reset button (missing await)
- **Wizard Settings Sliders** — Replaced HTML range inputs with gamepad-friendly SliderField
- **Slider Overflow** — Added overflowX: hidden to prevent layout issues in FrequencyWizard and DynamicManualMode
- **QAM Layout** — Fixed multiple controls not fitting in 310px QAM width
  - Settings menu: Added scroll container (maxHeight 80vh)
  - Wizard Mode: Vertical layout for mode selectors
  - Expert Mode: Added scroll container, removed redundant tabs
- **Dynamic Mode Init** — Fixed SettingsManager import error on plugin load
- **Frequency Wizard RPC** — Added missing frontend-facing RPC wrappers
- **Benchmark Parsing** — Enhanced stress-ng output parsing with fallback estimation
- **Wizard Progress** — Fixed initialization hang with explicit progress emission

## [3.3.2] - 2026-01-26

### Changed
- **Frequency Wizard Integration** — Moved into Wizard Mode as sub-mode (Load-Based/Frequency-Based toggle)

### Fixed
- **Frequency Wizard UI** — Fixed preset card overflow, gamepad focus, mode visibility
- **Frequency Wizard Backend** — Added test_runner checks, operation conflict prevention, comprehensive logging

## [3.3.0] - 2026-01-25

### Added
- **Frequency-Based Voltage Wizard** — Complete frequency-dependent voltage curve system
  - Automated curve generation with binary search (400-3500 MHz)
  - Quick presets: Conservative (20s), Balanced (30s), Aggressive (60s)
  - Real-time visualization with interactive charts
  - Linear interpolation between tested points
  - Profile integration with export/import
  - Safety: temperature monitoring, timeout detection, verification tests
  - Optimization: adaptive step size, frequency cache, intermediate persistence

**When to use:**
- Frequency-Based: Gaming, mixed workloads with varying CPU frequencies
- Load-Based: Consistent workloads, simpler setup

## [3.2.0] - 2026-01-24

### Added
- **Dynamic Manual Mode** — Per-core voltage curve control with real-time visualization
  - Simple Mode: Unified settings for all cores
  - Expert Mode: Per-core configuration
  - Real-time metrics: load, voltage, frequency, temperature (500ms polling)
  - Time-series graphs: 60-point FIFO buffer (30 seconds)
  - QAM optimized: compact design for 400px width
  - Safety: multi-layer validation, LKG backup, automatic rollback
  - Gamepad navigation: D-pad, L1/R1, visual focus indicators

## [3.1.31] - 2026-01-24

### Fixed
- **Wizard Mode** — Resolved low undervolt values and persistence issues
  - Starting point: -30mV (was -10mV)
  - Search algorithm: stops after failure instead of continuing
  - Safety margin: adds margin for conservative values (was subtracting)
  - Auto-persistence: enables apply_on_startup automatically
- **Expert Mode** — Game Only Mode integration with deferred application

## [3.1.28] - 2026-01-20

### Fixed
- **Wizard Mode Validation** — Complete rewrite with hardware verification
  - Voltage verification via hwmon sensors
  - Real-time MCE/WHEA monitoring via dmesg
  - 60-second verification pass with automatic rollback
  - Real CPU benchmark with progress and metrics
  - Apply & Save: automatic preset creation
- **Expert Mode Toggle** — Fixed to call proper enable/disable RPC methods
- **Gamepad Navigation** — Proper Focusable wrapping for left stick/DPAD

## [3.1.27] - 2026-01-20

### Added
- **Wizard Mode Refactoring** — Complete redesign of automated undervolt discovery
  - Step-down algorithm: iterative testing from -10mV until failure
  - Crash recovery: dirty exit detection with automatic rollback
  - Chip quality grading: Bronze/Silver/Gold/Platinum tiers
  - Real-time progress: ETA, OTA, heartbeat, live metrics
  - Curve visualization: SVG chart showing test progression
  - Configurable aggressiveness: Safe (2mV), Balanced (5mV), Aggressive (10mV)
  - Safety margins: automatic +10/+5/+2mV based on aggressiveness
  - Results history: persistent storage with replay capability

## [3.1.26] - 2026-01-19

### Added
- **Settings Management System** — Centralized settings with persistent storage
  - Header Bar: compact icon-based navigation (Fan Control, Settings)
  - Settings Menu: modal with Expert Mode confirmation dialog
  - Apply on Startup: auto-apply last profile on boot
  - Game Only Mode: apply undervolt only during games
  - Backend storage: `~/homebrew/settings/decktune/settings.json`
  - Game state monitor: tracks Steam launches/exits
  - Settings Context: React Context API for unified access

## [3.1.24] - 2026-01-19

### Added
- **Fan Control** — Custom fan curves with hardware interface
  - Custom curves: 3-10 temperature/speed points
  - Presets: Stock, Silent, Turbo
  - Linear interpolation for smooth transitions
  - Real-time monitoring: temperature, fan speed, target speed
  - Safety overrides: 100% at ≥95°C, minimum 80% at ≥90°C
  - Zero RPM safety enforcement
  - Configuration persistence across reboots

## [3.1.0] - 2026-01-16

### Added
- **Crash Recovery Metrics** — Persistent crash counter with detailed history
- **Real-Time Telemetry** — Live temperature/power graphs with 60s scrolling
- **Platform Detection Caching** — 30-day TTL for faster startup
- **Streaming Status Updates** — Server-sent events replace polling (<100ms latency)
- **Setup Wizard** — First-run guidance with goal selection
- **Session History** — Automatic tracking with metrics (duration, temp, power, battery savings)
- **Rust Config Fuzzing** — No-panic guarantee for config parser

## [3.0.0] - 2026-01-16

### Added
- **Context-Aware Profiles** — Multi-condition activation (game + battery + power + temp)
- **Progressive Recovery** — Smart rollback with 5mV reduction before full LKG
- **Adaptive Strategies** — Dynamic load-based adjustment (Conservative/Balanced/Aggressive)
- **Hysteresis Control** — Prevents value hunting with configurable dead-band
- **Smooth Transitions** — Linear interpolation with 1mV steps
- **Watchdog System** — 10s timeout with automatic reset
- **Profile Import/Export** — JSON format with conflict resolution
- **Diagnostics Export** — One-click system info and logs
