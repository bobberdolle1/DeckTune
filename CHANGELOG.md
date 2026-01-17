# Changelog

All notable changes to DeckTune will be documented in this file.

## [3.1.15] - 2026-01-18

### Added
- **Dynamic Mode Complete Overhaul** 🚀
  - Real-time LoadGraph visualization when active
  - Compact status card with 🟢 АКТИВЕН / ⚫ ВЫКЛ indicator
  - Start/Stop buttons for easy control
  - Collapsible settings panel (Settings button)
  - Improved configuration: strategy, simple mode, interval, hysteresis
  - "How it works" info box with current settings
  - Smooth animations and gradients
- **One-Click Package Installation** 📦
  - Install button for stress-ng and memtester
  - Automatic installation via `sudo pacman -S`
  - Progress indicator and result feedback
  - Auto-refresh after successful installation
  - Available in both Wizard and Expert modes
- **Improved Missing Packages Warning** ℹ️
  - Changed from warning (orange) to info (blue)
  - Clear explanation: "Optional Packages"
  - Shows what works without them (autotune, benchmarks)
  - Install button instead of manual command
  - Bilingual interface (Russian/English)

### Changed
- **Manual Tab Redesign**
  - Platform info in compact card
  - Control mode selection with icons and bilingual labels
  - Current values display for all cores
  - Buttons with gradients and dual-language text
  - Dynamic mode fully integrated into mode selection
- **Missing Packages Messaging**
  - From "Missing System Packages" to "Optional Packages"
  - Emphasis on what works (✅) vs what requires packages (⚠️)
  - Less alarming, more informative

### Improved
- **Dynamic Mode UX**
  - Settings no longer "overflow" - contained in card
  - Better visual hierarchy with collapsible sections
  - Clearer status indication
  - Easier to understand and configure
- **Documentation**
  - Added `.kiro/steering/dynamic-mode-improvements.md`
  - Added `.kiro/steering/optional-packages.md`
  - Updated `.kiro/steering/tech.md` with package info

### Technical
- **Backend API**
  - `install_binaries()` - install stress-ng and memtester
  - Uses plugin's root privileges
  - Returns installation status and errors
- **Frontend API**
  - `installBinaries()` - call backend installation
  - InstallBinariesButton component (WizardMode)
  - InstallBinariesButtonExpert component (ExpertMode)

## [3.1.14] - 2026-01-17

### Added
- **Dynamic Mode Settings UI** - Inline configuration panel in Manual tab
  - Strategy selection (Conservative/Balanced/Aggressive)
  - Simple Mode toggle for unified control
  - Value slider with real-time preview
  - Expandable panel with "Dynamic Settings" button
  - Settings persist and apply on next Dynamic mode start
- **Language Persistence** - Language selection now saved in localStorage
  - Fixes issue where language reset on QAM close/reopen
  - Syncs between localStorage and backend settings
  - Automatic restore on plugin load
- **RPC Methods for Dynamic Config**
  - `get_dynamic_config()` - retrieve current configuration
  - `save_dynamic_config(config)` - save with validation
- **API Methods**
  - `getDynamicConfig()` - fetch dynamic configuration
  - `saveDynamicConfig(config)` - save dynamic configuration
  - `enableGymdeck()` - start gymdeck3 with current settings
  - `disableGymdeck()` - stop gymdeck3

### Changed
- **Settings Tab Complete Redesign**
  - Modern card-based UI with gradients and shadows
  - 🌐 Language Card (blue) with save indicator
  - 🧪 Expert Mode Card (red when active) with pulsing animation
  - ℹ️ Info Card (green) with structured information
  - Smooth animations: fadeIn, slideUp, fadeInUp, slideDown, pulse
  - Icon badges in circles with color coding
  - Improved modal dialog with better visual hierarchy
- **Dynamic Settings Location**
  - Moved from separate tab to inline panel in Manual tab
  - Appears when Dynamic mode is selected
  - More intuitive workflow: select mode → configure → save
  - Compact design optimized for QAM (310px width)

### Improved
- **Gamepad Navigation**
  - All interactive elements use Focusable components
  - Full D-Pad and analog stick support
  - A button to activate, B button to go back
  - Visual focus indicators with glow effects
  - Proper focus flow for all new components
- **UI Consistency**
  - Unified color scheme across all components
  - Consistent spacing and typography
  - Responsive layouts with flex containers
  - Better visual feedback for all interactions

### Documentation
- Added `FIXES_SUMMARY.md` - Detailed technical documentation (EN)
- Added `FIXES_RU.md` - User guide in Russian
- Added `SETTINGS_IMPROVEMENTS.md` - Settings redesign details
- Updated README.md with new UI features and Dynamic Mode configuration

## [3.1.13] - 2026-01-17

### Fixed
- **Critical**: Fixed "unexpected token export" and "plugin export is not a function" errors
  - Changed Rollup output format to simple IIFE (Immediately Invoked Function Expression)
  - Plugin now loads correctly in Decky Loader without JavaScript errors
- **Critical**: Fixed ryzenadj binary path resolution
  - Changed from relative path to absolute path using PLUGIN_DIR
  - Resolves "ryzenadj binary not found" error on plugin initialization
- **Critical**: Fixed missing Fan Control API methods
  - Added `getFanConfig()`, `setFanConfig()`, `getFanStatus()` to API client
  - Fan tab now works without "api.getFanConfig is not a function" error
- **Critical**: Fixed profiles.map error in Presets tab
  - Added null safety check for profiles array: `(profiles || []).map()`
  - Fixed condition check: `(!profiles || profiles.length === 0)` for proper undefined handling
  - Prevents "profiles.map is not a function" crash
  - ErrorBoundary now allows recovery without being stuck
- **Build system**: Added PowerShell build script (`scripts/build-release.ps1`) for Windows

### Changed
- **Increased safe limits** for better performance (Requirement 5.1)
  - LCD (Jupiter): -30mV → -50mV safe limit, -40mV → -70mV absolute limit
  - OLED (Galileo): -35mV → -60mV safe limit, -50mV → -80mV absolute limit
  - Previous limits were too conservative, Steam Deck can handle more
  - Clear platform cache to apply: `rm -f ~/.local/share/decky/settings/decktune_platform_cache.json`

### UI Optimization
- **Vertical mode switcher** for better gamepad navigation
  - Wizard/Expert buttons now stacked vertically instead of horizontal
  - Status indicator integrated into active mode button
  - Better focus navigation with gamepad
- **Expert Mode improvements**
  - Tab navigation: Converted from HTML buttons to Focusable components for gamepad support
  - Tabs now navigable with D-pad left/right and activatable with A button
  - Added visual focus indicator: blue border (2px) and glow effect when tab is focused
  - Active tab: blue background (#1a9fff)
  - Focused tab: blue border with shadow for clear visibility
  - Reduced tab sizes: 12px icons, 8px labels, 4px padding
  - Panic button: Compact size (30px height, 11px font, 10px icons)
- **Expert Mode Manual tab improvements**
  - Toggle labels: "Expert Undervolter" (was "Expert Mode"), "All Cores Same" (was "Simple Mode")
  - Vertical layout for toggles instead of horizontal to prevent text wrapping
  - Compact Expert Mode warning dialog (400px max width, 10px fonts)
  - Dialog now uses vertical button layout with proper gamepad navigation
  - Fixed bug: Added `pendingExpertToggle` state to properly manage toggle during confirmation
  - Toggle now shows ON only when: `expertModeActive || pendingExpertToggle`
  - Toggle disabled during pending confirmation to prevent double-clicks
  - Fixed bug: Wrapped dialog buttons in Focusable container with `flow-children="vertical"`
  - Added `noFocusRing={false}` to outer Focusable for proper focus management
  - Dialog buttons now fully navigable with D-pad up/down and activatable with A button
  - Changed "Overclocker" to "Undervolter" throughout
  - Fixed: Removed leftover `setShowExpertWarning` references, now uses `showModal` with `ConfirmModal`
  - Dialog now properly captures gamepad focus using native Decky UI components
- **UI State Persistence**
  - Mode selection (Wizard/Expert) now persists across QAM close/reopen using localStorage
  - Expert Mode active tab now persists across QAM close/reopen using localStorage
  - No more reset to initial screen when reopening QAM
- **Presets Tab Complete Redesign**
  - Split into two sections: Game Profiles (auto-switching) and Global Presets (manual)
  - Ultra-compact card design: 8-11px fonts, minimal padding
  - Game Profiles: Quick-create button, active indicator, dynamic mode badge
  - Global Presets: Apply button, save current values, tested indicator
  - All actions use ConfirmModal for safety
  - Full gamepad navigation with visual focus indicators
  - Removed bloated import/export UI - kept only essential functions
- **Expert Mode Manual tab cleanup**
  - Action buttons (Apply/Test/Disable) now vertical layout for better fit
  - Removed "Tune for this game" button (available in Wizard mode)
  - Removed "Run Benchmark" button and history (available in Tests tab)
  - Cleaner, more focused interface
- **Aggressive size reduction** for Decky menu (310px width)
  - Reduced all font sizes: 8-11px (was 12-16px)
  - Minimized padding/margins: 2-4px (was 8-16px)
  - Smaller icons: 9-10px (was 12-16px)
  - Compact button heights: 28-32px (was 36-48px)
- **Tab navigation** with Focusable for gamepad support
  - All tabs now navigable with gamepad D-pad
  - Proper focus states and onActivate handlers
- **Panic button**: Reduced size while maintaining visibility (30px height, 11px font)
- **Step indicators**: Smaller circles (22px) and tighter spacing (8px gaps)
- **Binning/Benchmark cards**: Compact padding (4-6px), smaller fonts (9-11px)
- **Goal selection buttons**: Reduced height and spacing for better fit
- **Binning settings**: Ultra-compact inline expandable panel
  - Settings now expand/collapse directly in the interface
  - No more oversized ConfirmModal that doesn't fit in Decky menu
  - Custom compact labels (8px font) instead of SliderField labels to save space
  - Vertical button layout: Save button above Reset button
  - Minimal padding (4px panel, 2px gaps) and smaller fonts (9px buttons, 8px labels)
  - Added "Reset to Defaults" button to restore default values (60s, 5mV, -10mV)
  - Fixed slider overflow with constrained container width
  - Fully navigable with gamepad

### Platform Detection
- **Cache cleared**: Platform detection cache reset to pick up new safe limits
  - LCD (Jupiter): -50mV safe limit (was -30mV)
  - OLED (Galileo): -60mV safe limit (was -35mV)
  - Requires plugin restart to see updated limits

### Installation Note
After installing the plugin, run this command on Steam Deck to make binaries executable:
```bash
sudo chmod +x ~/homebrew/plugins/DeckTune/bin/*
```

### Notes
- All features from v3.1.12 are included (extended limits -50mV LCD / -60mV OLED, binning progress, QAM optimization)
- Windows zip doesn't preserve executable permissions - manual chmod required after installation
- Binary permissions issue resolved: stress-ng, memtester, ryzenadj, gymdeck3 now executable
- Manual tab now focused on core functionality only - tests and benchmarks moved to dedicated tabs

## [3.1.12] - 2026-01-17

### Fixed
- **Undervolt functionality** — improved diagnostics and error handling
  - Added `diagnose()` method to RyzenadjWrapper for comprehensive availability checks
  - Enhanced `apply_values_async()` with detailed logging and validation
  - Improved error handling in RPC `apply_undervolt` with diagnostics check before applying
- **Extended undervolt limits** — increased safe limits for better performance
  - LCD (Jupiter): safe_limit = -50mV (was -30mV), absolute_limit = -70mV
  - OLED (Galileo): safe_limit = -60mV (was -35mV), absolute_limit = -80mV
  - Unknown: safe_limit = -30mV (was -25mV), absolute_limit = -40mV
- **Binning improvements** — enhanced reliability and diagnostics
  - Added ryzenadj availability check in `BinningEngine.start()`
  - Improved `_run_iteration` with detailed diagnostics and logging
  - Better error messages when ryzenadj is unavailable
- **Binning progress bar** — new visual progress indicator
  - Added `max_iterations` and `percent_complete` to binning progress events
  - New `BinningProgress` component with progress bar, ETA, and iteration tracking
  - Integrated into WizardMode for better user feedback
- **QAM UI optimization** — improved layout for Quick Access Menu
  - Compact styles with max-width: 310px for QAM compatibility
  - Icon-only tab navigation to save space
  - Flex-wrap for buttons to prevent overflow
  - 2x2 grid layout for core metrics
- **Rendering error fixes** — improved error handling in UI
  - New `ErrorBoundary` component wrapping DeckTuneApp
  - Graceful error recovery with fallback UI
  - Better error logging for debugging
- **Fan control restoration** — re-enabled fan control tab
  - New `FanTab` component with fan curve editor integration
  - Added Fan tab to Expert Mode navigation
  - Property tests for fan curve application and temperature safety

### Testing
- **9 new property-based tests** covering all critical fixes
  - Property 1: Hex calculation correctness (extended to -100mV range)
  - Property 2: Status invariant after undervolt application
  - Property 3: Binning sequence correctness
  - Property 4: Binning result invariant
  - Property 5: Binning state persistence
  - Property 6: Expert Mode extended range validation
  - Property 7: Binning progress event completeness
  - Property 8: Fan curve application
  - Property 9: Fan temperature safety override
- **All 504 tests passing** including new property tests
- **Updated test mocks** to include new `diagnose()` method

### Technical
- Enhanced `RyzenadjWrapper` with comprehensive diagnostics
- Updated platform limits in `caps.py` and `detect.py`
- Improved event emission in `events.py` with progress tracking
- New React components: `BinningProgress`, `ErrorBoundary`, `FanTab`
- Updated TypeScript interfaces for binning progress data

## [3.1.8] - 2026-01-16

### Fixed
- **Decky Loader compatibility** — fixed manifest treeshaking issue
  - Custom rollup plugin to inject full manifest with `moduleSideEffects: 'no-treeshake'`
  - Full plugin.json manifest now embedded in bundle (was only `{"name":"DeckTune"}`)
  - This fixes the "Unexpected token 'export'" error in Decky Loader

### Technical
- Custom `manifestPlugin()` in rollup.config.js to prevent treeshaking of manifest properties
- Manifest now includes: name, author, version, api_version, flags, publish (tags, description, image)

## [3.1.7] - 2026-01-16

### Fixed
- **Decky Loader compatibility** — reverted to standard ESM format with @decky/rollup
  - Standard `@decky/rollup` config generates correct ESM output
  - Output format: `export { index as default }` (official Decky format)
  - Minimal test build to isolate and verify plugin loading

## [3.1.6] - 2026-01-16

### Fixed
- **Decky Loader compatibility** — switched to IIFE bundle format instead of ESM
  - Custom rollup config with `format: "iife"` for proper Decky Loader loading
  - Simplified index.tsx structure to match working plugins
  - Created separate DeckTuneApp component for cleaner architecture

## [3.1.5] - 2026-01-16

### Fixed
- **Decky Loader compatibility** — fixed plugin loading error "Unexpected token 'export'"
  - Changed JSX transform from `react` to `react-jsx` (matches official Decky template)
  - Fixed `definePlugin` import source (now from `@decky/api`)
  - Fixed plugin return format with `name` and `titleView` fields
  - Updated dependencies to match official decky-plugin-template versions
- **Python 3.9 compatibility** — fixed `asyncio.Lock()` initialization in `backend/api/stream.py`
- **Rust field name** — fixed `zero_rpm_enabled` → `allow_zero_rpm` in gymdeck3

### Technical
- Updated `@decky/rollup` to 1.0.2
- Updated `@decky/ui` to 4.11.0
- Updated `@decky/api` to 1.1.3
- Updated TypeScript to 5.6.2
- Updated React types to 19.1.1

## [3.1.0] - 2026-01-16

### Reliability & UX Improvements

DeckTune 3.1 focuses on reliability improvements, performance optimizations, and UX enhancements for a more polished user experience.

#### Crash Recovery Metrics (NEW!)
- **Persistent crash counter** — tracks how many times crash recovery has saved your system
- **Detailed crash history** — stores last 50 crash events with timestamps, crashed values, restored values, and recovery reason
- **Diagnostics integration** — complete crash history included in diagnostics export
- **FIFO management** — oldest entries automatically removed when limit reached

**Implementation:**
- New `CrashMetricsManager` class in `backend/core/crash_metrics.py`
- `CrashRecord` and `CrashMetrics` dataclasses with serialization
- Integration with `SafetyManager.check_boot_recovery()`
- RPC method: `get_crash_metrics()`
- 2 property-based tests validating FIFO limit and record completeness

#### Real-Time Telemetry Graphs (NEW!)
- **Live temperature graph** — scrolling line graph showing last 60 seconds of CPU temperature
- **Live power graph** — scrolling line graph showing last 60 seconds of power consumption
- **Hover tooltips** — exact value and timestamp on hover
- **Circular buffer** — stores up to 300 samples (5 minutes) at 1Hz
- **SSE integration** — real-time updates via server-sent events

**Implementation:**
- New `TelemetryManager` class in `backend/core/telemetry.py`
- `TelemetrySample` dataclass with timestamp, temperature, power, load
- New `TelemetryGraph.tsx` React component with SVG rendering
- RPC method: `get_telemetry(seconds)`
- 1 property-based test validating circular buffer behavior

#### Platform Detection Caching (NEW!)
- **Faster startup** — cached platform data eliminates DMI read on every launch
- **30-day TTL** — cache automatically expires and refreshes
- **Corruption resilience** — graceful fallback to fresh detection on invalid cache
- **Manual re-detection** — RPC method to force fresh detection

**Implementation:**
- New `PlatformCache` class in `backend/platform/cache.py`
- `CachedPlatform` dataclass with model, variant, safe_limit, cached_at
- Integration with `detect_platform()` function
- RPC method: `redetect_platform()`
- 2 property-based tests validating cache validity and corruption resilience

#### Streaming Status Updates (NEW!)
- **Server-sent events** — replaces polling for real-time status updates
- **< 100ms latency** — status updates forwarded to frontend within 100ms
- **Automatic reconnection** — resumes streaming without page reload
- **Buffer management** — up to 10 updates buffered during delivery failures
- **Smart filtering** — no events emitted when gymdeck3 is not running

**Implementation:**
- New `StatusStreamManager` class in `backend/api/stream.py`
- Subscriber management with asyncio.Queue
- Integration with `DynamicController` event emission
- 2 property-based tests validating buffer limit and no-events-when-stopped

#### Setup Wizard (NEW!)
- **First-run detection** — automatically shows wizard for new users
- **Step-by-step guidance** — welcome, explanation, goal selection, confirmation
- **Goal estimates** — shows estimated battery improvement and temperature reduction
- **Skip/cancel support** — exit at any step without applying changes
- **Re-run option** — "Run Setup Wizard" available in settings

**Implementation:**
- New `SetupWizard.tsx` React component with multi-step UI
- `WizardState` TypeScript interface for state management
- `GOAL_ESTIMATES` constant with battery/temp estimates per goal
- RPC methods: `get_wizard_state()`, `complete_wizard()`, `reset_wizard()`
- 2 property-based tests validating cancellation safety and goal estimates

#### Session History with Metrics (NEW!)
- **Automatic session tracking** — creates session record when gymdeck3 starts
- **Comprehensive metrics** — duration, avg/min/max temperature, avg power, estimated battery savings
- **Session history** — view last 30 sessions with key metrics
- **Session comparison** — side-by-side comparison of any two sessions
- **Archival system** — sessions beyond 100 moved to archive file
- **Diagnostics integration** — session history included in export

**Implementation:**
- New `SessionManager` class in `backend/core/session_manager.py`
- `Session` and `SessionMetrics` dataclasses with UUID generation
- New `SessionHistory.tsx`, `SessionDetail.tsx`, `SessionComparison.tsx` components
- RPC methods: `get_session_history()`, `get_session()`, `compare_sessions()`
- 3 property-based tests validating history limit, metrics calculation, and comparison symmetry

#### Rust Config Fuzzing Infrastructure (NEW!)
- **No-panic guarantee** — config parser handles arbitrary byte sequences without crashing
- **Graceful error handling** — invalid inputs return descriptive error messages
- **Fuzzing dictionary** — includes all config field names for targeted fuzzing
- **Code coverage** — fuzzing reports coverage percentage for config module

**Implementation:**
- New `tests/config_fuzzing_test.rs` with proptest-based fuzzing
- Fuzzing dictionary at `gymdeck3/fuzz/dict/config.dict`
- 1 property-based test validating no-panic guarantee

#### Frontend-Backend Integration Tests (NEW!)
- **RPC contract tests** — verify all methods return expected response shapes
- **Event payload tests** — verify event structure matches TypeScript types
- **Error response tests** — verify error responses include code and message
- **Schema compliance** — all responses validated against expected schemas

**Implementation:**
- New `tests/test_rpc_contract.py` with comprehensive contract tests
- New `tests/test_rpc_response_schema.py` for schema validation
- New `tests/test_rpc_error_response.py` for error structure validation
- 3 property-based tests validating RPC response schema, error structure, and contract compliance

### Testing & Quality
- **15 new correctness properties** covering all v3.1 features
- **507 Python tests** passing (including all property-based tests)
- **319 Rust tests** passing (including config fuzzing)
- **Comprehensive coverage** of crash metrics, telemetry, caching, sessions, streaming, wizard, and RPC contracts

### API Changes
- **New RPC methods** (backward compatible):
  - Crash Metrics: `get_crash_metrics()`
  - Telemetry: `get_telemetry(seconds)`
  - Platform: `redetect_platform()`
  - Sessions: `get_session_history(limit)`, `get_session(id)`, `compare_sessions(id1, id2)`
  - Wizard: `get_wizard_state()`, `complete_wizard(goal)`, `reset_wizard()`
- **New events**:
  - `telemetry_sample`: Real-time telemetry data
  - `session_started`: Session creation notification
  - `session_ended`: Session completion with metrics

### Breaking Changes
- **None** — All changes are backward compatible
- Existing settings and presets are preserved
- No migration required

### Technical Improvements
- Server-sent events for real-time updates (replaces polling)
- Platform detection caching for faster startup
- Circular buffers for efficient memory usage
- Comprehensive error handling for all new features
- Type-safe TypeScript interfaces for all new data structures

---

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
