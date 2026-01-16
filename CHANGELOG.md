# Changelog

All notable changes to DeckTune will be documented in this file.

## [3.0.0] - 2026-01-16

### Major Changes - Intelligent Automation Features

DeckTune 3.0 transforms the plugin from a manual tuning tool into an intelligent, adaptive system with comprehensive automation features.

#### Context-Aware Profile System (NEW!)
- **Multi-condition profile activation** — profiles activate based on game + battery level + power mode + temperature
- **Automatic context detection** — monitors battery level, AC/battery mode, and CPU temperature
- **Smart profile selection** — most specific matching profile wins (more conditions = higher priority)
- **Seamless transitions** — automatic re-evaluation when context changes (battery threshold crossed, charger plugged/unplugged)
- **Fallback chain** — graceful degradation: context match → app-only match → global default

**Implementation:**
- New `ContextCondition` and `SystemContext` dataclasses in `backend/dynamic/context.py`
- New `ContextMatcher` class for intelligent profile selection
- Extended `ContextualProfile` with conditions field
- Context monitoring in `ProfileManager` with threshold detection
- 5 property-based tests validating context matching correctness

#### Progressive Recovery System (NEW!)
- **Smart rollback** — attempts to reduce undervolt by 5mV before full rollback
- **Stability verification** — waits for 2 heartbeat cycles to confirm recovery
- **Escalation logic** — proceeds to full LKG rollback if instability persists
- **LKG auto-update** — successful recovery updates Last Known Good values
- **Event notifications** — frontend receives recovery status updates

**Implementation:**
- New `ProgressiveRecovery` class in `backend/core/safety.py`
- `RecoveryState` dataclass tracking recovery stages (initial → reduced → rollback)
- Integration with `Watchdog` for automatic trigger on instability
- 4 property-based tests validating recovery behavior

#### BlackBox Recorder (NEW!)
- **Ring buffer metrics** — maintains last 30 seconds of system metrics (60 samples at 500ms)
- **Crash persistence** — automatically saves buffer to timestamped JSON on instability detection
- **Post-mortem analysis** — includes temperature, CPU load, undervolt values, fan speed/PWM
- **Recording management** — stores last 5 recordings, accessible via RPC
- **FIFO behavior** — oldest samples automatically discarded when buffer full

**Implementation:**
- New `BlackBox` class in `backend/core/blackbox.py`
- `MetricSample` dataclass with all required fields
- Storage path: `/tmp/decktune_blackbox/`
- RPC methods: `list_blackbox_recordings()`, `get_blackbox_recording()`
- 2 property-based tests validating FIFO and persistence

#### Acoustic Fan Profiles (NEW!)
- **Silent profile** — prioritizes low noise (max 60% / ~3000 RPM until 85°C)
- **Balanced profile** — linear curve 30-70°C → 30-90% for noise/cooling balance
- **Max Cooling profile** — aggressive curve (100% at 60°C+)
- **Custom profile** — user-defined curves via FanCurveEditor
- **Safety override** — 90°C+ always forces 100% regardless of profile

**Implementation:**
- New `AcousticProfile` enum in `gymdeck3/src/fan/acoustic.rs`
- Profile-specific `FanCurve` generation
- CLI argument: `--acoustic-profile <silent|balanced|max_cooling|custom>`
- Property-based tests for each profile's behavior

#### PWM Smoothing (NEW!)
- **Gradual transitions** — interpolates fan speed over configurable ramp time (default 2s)
- **Linear interpolation** — smooth PWM changes between current and target
- **Rate limiting** — configurable max RPM change per second (default 1000 RPM/s)
- **Asymmetric rates** — decrease rate is 50% of increase rate to prevent thermal spikes
- **Emergency bypass** — 90°C+ immediately sets max PWM, skipping smoothing

**Implementation:**
- New `PWMSmoother` struct in `gymdeck3/src/fan/smoother.rs`
- Configurable `ramp_time_sec` parameter
- `force_immediate()` method for emergency bypass
- Integration with `FanController` update loop
- 4 property-based tests validating smoothing behavior

#### Iron Seeker - Per-Core Curve Optimizer (NEW!)
- **Per-core undervolt discovery** — tests each CPU core individually, accounting for silicon lottery
- **Vdroop stress testing** — pulsating load pattern (100ms load/100ms idle) for detecting transient instability
- **Quality tier classification** — Gold (≤-35mV), Silver (-34 to -20mV), Bronze (>-20mV) ratings per core
- **Crash recovery** — automatic state persistence and boot recovery after system crash
- **Configurable parameters**: step size (1-20mV), test duration (10-300s), safety margin (0-20mV)
- **Progress tracking** with real-time updates, ETA calculation, and per-core results
- **Preset integration** — save discovered values as presets with quality tier metadata

**Implementation:**
- New `IronSeekerEngine` class in `backend/tuning/iron_seeker.py`:
  - `IronSeekerConfig`: Configuration with validation and clamping
  - `CoreResult`: Per-core results with quality tier
  - `IronSeekerResult`: Complete session results
  - `IronSeekerState`: Persistent state for crash recovery
  - `QualityTier`: Enum with Gold/Silver/Bronze classification
- New `VdroopTester` class in `backend/tuning/vdroop.py`:
  - Pulsating load generation using stress-ng with AVX2 workload
  - MCE (Machine Check Exception) detection via dmesg
  - Process failure and timeout detection
- Extended `SafetyManager` for Iron Seeker state management:
  - `create_iron_seeker_state()`, `load_iron_seeker_state()`, `clear_iron_seeker_state()`
  - Boot recovery integration
- RPC methods: `start_iron_seeker()`, `cancel_iron_seeker()`, `get_iron_seeker_status()`
- Events: `iron_seeker_progress`, `iron_seeker_core_complete`, `iron_seeker_complete`, `iron_seeker_recovery`
- 22 property-based tests validating all correctness properties

#### Low-Level Fan Control (NEW!)
- **Direct hwmon sysfs control** via Rust daemon (gymdeck3)
- **Custom fan curves** with visual SVG editor and drag-and-drop points
- **Temperature-based interpolation** with smooth transitions
- **Hysteresis control** prevents rapid speed changes (1-10°C configurable)
- **Safety overrides**: 90°C+ forces 100% PWM, 85°C+ enforces minimum 80%
- **Zero RPM mode** allows fan to stop below 45°C (optional, with warning)
- **Fail-safe Drop trait** returns control to BIOS on daemon exit/crash
- **Three modes**: Default (BIOS), Custom (curve), Fixed (constant speed)

**Implementation:**
- New `fan/` module in gymdeck3 Rust daemon:
  - `hwmon.rs`: Low-level sysfs I/O for `/sys/class/hwmon`
  - `controller.rs`: Curve calculation, smoothing, hysteresis
  - `safety.rs`: Hard limits and Drop trait for BIOS fallback
- Python backend integration:
  - `FanConfig`, `FanCurvePoint`, `FanStatus` dataclasses
  - `DynamicConfig.fan_config` field with validation
  - RPC methods: `get_fan_config()`, `set_fan_config()`, `set_fan_curve()`, `set_fan_mode()`, `enable_fan_control()`
- Frontend `FanCurveEditor.tsx` component:
  - Interactive SVG graph with drag-and-drop points
  - Click to add, drag to move, double-click to remove
  - Live temperature/RPM display
  - Safety override indicator
- CLI arguments: `--fan-control`, `--fan-mode`, `--fan-curve`, `--fan-zero-rpm`, `--fan-hysteresis`

#### Automated Silicon Binning
- **Automatic limit discovery** through iterative stress testing
- **Crash recovery** with persistent state management
- **Safety guarantees** with boot recovery and rollback
- **Configurable parameters**: test duration (30-300s), step size (1-10mV), start value (0 to -20mV)
- **Smart recommendations** with 5mV safety margin
- **Progress tracking** with real-time updates and ETA
- **Cancellation support** with instant rollback to previous values

**Implementation:**
- New `BinningEngine` class in `backend/tuning/binning.py`
- State persistence to `/tmp/decktune_binning_state.json`
- Extended `SafetyManager` for binning state management
- RPC methods: `start_binning()`, `stop_binning()`, `get_binning_status()`, `get_binning_config()`, `update_binning_config()`
- UI integration in Wizard Mode with progress display and result summary

#### Per-Game Profiles with Automatic Switching
- **Automatic profile switching** based on running Steam game
- **Quick-create** profiles from current settings while game is running
- **Global default** fallback for games without specific profiles
- **Import/Export** functionality for sharing and backup
- **Seamless transitions** within 500ms on game launch
- **AppID detection** via Steam appmanifest files and process scanning

**Implementation:**
- New `ProfileManager` class in `backend/dynamic/profile_manager.py`
- New `AppWatcher` class in `backend/platform/appwatcher.py` for game detection
- Profile storage in Decky settings with version metadata
- RPC methods: `create_profile()`, `get_profiles()`, `update_profile()`, `delete_profile()`, `create_profile_for_current_game()`, `export_profiles()`, `import_profiles()`
- UI integration in Expert Mode Presets tab with profile list and management

#### Built-in Benchmarking System
- **Quick 10-second benchmarks** using stress-ng matrix operations
- **Automatic comparison** with previous results
- **History tracking** of last 20 benchmark runs
- **Performance metrics** with score, duration, and undervolt values
- **Before/after testing** to measure tuning impact

**Implementation:**
- New `BenchmarkRunner` class in `backend/tuning/benchmark.py`
- Benchmark history storage in Decky settings
- RPC methods: `run_benchmark()`, `get_benchmark_history()`
- UI integration in both Wizard and Expert modes

#### Enhanced Visualization
- **Dual Y-axes** for CPU load and undervolt values
- **60-second rolling window** with 1-second resolution
- **Profile change markers** showing when profiles switch
- **Static line display** for manual mode
- **Real-time updates** with smooth animations

**Implementation:**
- Extended `LoadGraph` component in `src/components/LoadGraph.tsx`
- New `GraphDataPoint` interface with profile tracking
- Event listeners for profile changes and binning progress

### Testing & Quality
- **Property-based testing** for new features
  - 44 new correctness properties (hypothesis)
  - Comprehensive coverage of binning, profiles, and benchmarking
- **Integration tests** for complete workflows
  - Binning crash recovery scenarios
  - Profile auto-switching on game launch
  - Benchmark before/after comparisons

### API Changes
- **New RPC methods** (backward compatible):
  - Binning: `start_binning()`, `stop_binning()`, `get_binning_status()`, `get_binning_config()`, `update_binning_config()`
  - Profiles: `create_profile()`, `get_profiles()`, `update_profile()`, `delete_profile()`, `create_profile_for_current_game()`, `export_profiles()`, `import_profiles()`
  - Benchmarking: `run_benchmark()`, `get_benchmark_history()`
- **New events**:
  - `binning_progress`: Real-time binning updates
  - `binning_complete`: Binning completion with results
  - `profile_changed`: Profile switch notifications

### Breaking Changes
- **None** - All changes are backward compatible
- Existing presets and settings are preserved
- No migration required

### Migration Notes
- **Automatic migration** from v2.x settings format
- **Profile storage** uses new format but old presets remain accessible
- **Binning state** is ephemeral and doesn't affect existing configurations
- **Benchmark history** starts fresh (no historical data migration)

### Technical Improvements
- Modular architecture with clear separation of concerns
- Comprehensive error handling for all new features
- Persistent state management for crash recovery
- Event-driven UI updates for responsive feedback
- Type-safe TypeScript interfaces for all new data structures

### Documentation
- Updated README with new feature sections
- Added user guides for binning, profiles, and benchmarking
- Updated architecture diagrams
- Comprehensive inline code documentation

## [2.0.0] - 2026-01-15

### Major Changes - Dynamic Mode Refactor (gymdeck3)

#### New Rust Daemon (gymdeck3)
- **Complete rewrite** of dynamic mode in Rust for memory safety and performance
- **Static binary** (905KB) with zero runtime dependencies
- **Advanced load monitoring** from /proc/stat with per-core tracking
- **Adaptive strategies**: Conservative (5s ramp), Balanced (2s ramp), Aggressive (500ms ramp), Custom
- **Hysteresis control** prevents value hunting with configurable dead-band (1-20%)
- **Smooth transitions** with 1mV linear interpolation
- **Safety features**: watchdog, panic hook, automatic rollback, signal handling
- **JSON IPC protocol** (NDJSON) for status updates

#### Python Integration
- **DynamicController** manages gymdeck3 subprocess lifecycle
- **DynamicConfig** with validation and serialization
- **Profile management** with default profiles (Battery Saver, Balanced, Performance, Silent)
- **Settings migration** from old gymdeck2 format with automatic conversion
- **Event system** for real-time frontend updates

#### UI Enhancements
- **Expert Overclocker Mode** removes safety limits (-100mV range) with warning dialog
- **Simple Mode** single slider controls all cores simultaneously
- **Real-time load graph** displays CPU load when dynamic mode active
- **Profile switching** quick access to saved configurations

#### Testing & Quality
- **Property-based testing** for correctness verification
  - 8 Rust properties (proptest) - 244 tests
  - 7 Python properties (hypothesis) - 127 tests
- **Manual integration tests** comprehensive end-to-end validation
- **100% test coverage** for critical components

### Removed
- **gymdeck2** (C daemon) replaced by gymdeck3 (Rust)

### Technical Improvements
- Rust 1.70+ with musl static linking
- Comprehensive inline documentation
- Updated README with gymdeck3 build instructions
- Improved error handling and diagnostics

## [1.0.0] - 2026-01-15

### Added
- **Autotune Engine** — automatic discovery of optimal undervolt values
  - Quick mode: fast search with step 5 and 30-second tests
  - Thorough mode: precise search with binary refinement and 2-minute tests
- **Platform Detection** — automatic Steam Deck model detection
  - LCD (Jupiter): limit -30
  - OLED (Galileo): limit -35
  - Unknown: conservative limit -25
- **Safety System** — multi-level protection system
  - Watchdog with heartbeat monitoring
  - Automatic rollback on freeze
  - Boot recovery on reboot during tuning
  - LKG (Last Known Good) persistence
  - Panic Disable button
- **Stress Test Suite** — built-in stress tests
  - CPU Quick/Long (stress-ng)
  - RAM Quick/Thorough (memtester)
  - Combo (CPU + RAM)
- **Preset Management** — preset management
  - Global and per-game presets
  - Auto-apply on game launch
  - Export/import to JSON
- **Wizard Mode** — simple interface for beginners
  - 3-step setup wizard
  - Goal selection (Quiet, Balanced, Max Battery, Max Performance)
- **Expert Mode** — advanced interface
  - Manual: per-core value adjustment
  - Presets: preset management
  - Tests: run tests manually
  - Diagnostics: logs and export
- **Diagnostics Export** — one-click diagnostics export
  - Plugin logs
  - Configuration and LKG
  - System information
  - dmesg
- **Dynamic Mode** — integration with gymdeck3
  - Automatic adjustment based on load
  - Strategies: Default, Aggressive, Manual

### Technical
- Modular backend architecture (core, platform, tuning, api)
- Property-based testing with hypothesis (16 properties, 91 tests)
- TypeScript/React frontend with Decky UI
- Python 3.10+ backend with type hints

## [0.x] - Previous Versions

Based on [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt)
