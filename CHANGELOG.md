# Changelog

## [3.5.5] - 2026-01-29

### Fixed
- **Frequency Wizard — Steam Deck Compatibility**
  - Fixed userspace governor unavailable error on Steam Deck
  - Implemented fallback using performance governor with frequency limits
  - Progress bar and ETA now work correctly during testing
  - Tests no longer fail immediately on Steam Deck hardware
- **Core System — Path Import Error**
  - Fixed `NameError: name 'Path' is not defined` in update manager
  - Added missing `from pathlib import Path` import to main.py
- **UI Components — Focusable Errors**
  - Fixed TypeScript errors in FrequencyWizardPresets component
  - Corrected nested Focusable structure
  - Removed invalid flow-children prop

### Technical Details
- Backend: `cpufreq.lock_frequency()` auto-detects available governors
- Backend: `cpufreq.unlock_frequency()` restores frequency limits
- Backend: Added CPUFreqError import to runner.py
- Frontend: Fixed Focusable component structure in FrequencyWizardPresets

## [3.5.0] - 2026-01-29

### Added
- **Frequency Wizard Preset Management** — Complete preset system for frequency wizard results
  - Chip quality grading with visual badges (Platinum/Gold/Silver/Bronze/Standard)
  - Apply on Startup toggle — automatically apply preset when plugin starts
  - Game Only Mode toggle — apply preset only when a game is running
  - Per-core statistics display with expandable details (avg/min voltage, stable points)
  - Apply/Delete actions with confirmation modals
  - Integrated into Wizard Mode under Frequency Wizard section

### Fixed
- **Regular Wizard Algorithm** — Fixed per-core testing to test each core individually to its limit
  - Previous: tested all cores at each voltage level (all at -30mV, then all at -32mV)
  - Correct: Core 0 to limit → Core 1 to limit → Core 2 to limit → Core 3 to limit → Final verification
- **Wizard Crash Recovery** — Added full crash detection and recovery for regular wizard
  - Saves per-core progress after each successful test
  - Detects crashes on restart and offers to continue from last completed core
  - Handles multiple crashes gracefully
- **Stress Test Load** — Added gradual load decrease to prevent crashes
  - Test phases: 100% → 90% → 80% CPU load
  - Uses stress-ng `--cpu-load` parameter
  - For tests <20s, uses standard 100% load
- **Frequency Wizard Start Button** — Fixed non-functional start button (missing API method)
- **Frequency Wizard Per-Core Testing** — Automatically tests all 4 cores sequentially
  - Generates complete frequency curves for entire CPU
  - Collects per-core statistics (avg_voltage, min_voltage, max_voltage, stable_points)
  - Saves intermediate results after each core

### Technical Details
- Backend: Added `game_only_mode` field to frequency wizard preset structure
- Backend: Updated `update_frequency_wizard_preset()` to allow `game_only_mode` updates
- Backend: Startup logic checks frequency wizard presets with `apply_on_startup`
- Backend: Game-only logic checks frequency wizard presets with `game_only_mode`
- Frontend: FrequencyWizardPresets component follows Decky UI standards (QAM compliant)
- Frontend: All toggles are functional (not placeholders)

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
