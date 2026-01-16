# DeckTune Project Structure

## Top-Level Organization

```
DeckTune/
├── backend/              # Python backend modules
├── src/                  # TypeScript frontend
├── gymdeck3/             # Rust dynamic mode daemon
├── tests/                # Python integration tests
├── bin/                  # Compiled binaries (ryzenadj, gymdeck3)
├── dist/                 # Build output (index.js)
├── main.py               # Plugin entry point (RPC router)
├── plugin.json           # Decky plugin metadata
├── package.json          # NPM configuration
└── requirements*.txt     # Python dependencies
```

## Backend Structure (`backend/`)

```
backend/
├── core/                 # Core functionality
│   ├── ryzenadj.py      # Wrapper for ryzenadj CLI
│   ├── safety.py        # Safety manager (LKG, rollback, clamping)
│   ├── crash_metrics.py # Crash recovery metrics and history (v3.1)
│   ├── telemetry.py     # Real-time telemetry buffer (v3.1)
│   └── session_manager.py # Gaming session tracking (v3.1)
├── platform/             # Platform detection
│   ├── detect.py        # DMI-based model detection
│   ├── cache.py         # Platform detection cache (v3.1)
│   ├── caps.py          # Platform capabilities and limits
│   └── appwatcher.py    # Steam app detection for auto-switching
├── tuning/               # Autotune and testing
│   ├── autotune.py      # Autotune engine (binary search)
│   ├── runner.py        # Test runner (stress-ng, memtester)
│   ├── binning.py       # Silicon binning engine
│   └── benchmark.py     # Performance benchmarking
├── dynamic/              # Dynamic mode (gymdeck3 integration)
│   ├── controller.py    # Gymdeck3 process controller
│   ├── config.py        # Dynamic mode configuration
│   ├── profiles.py      # Preset profiles
│   ├── profile_manager.py # Per-game profile management
│   └── migration.py     # Settings format migration
├── api/                  # RPC and events
│   ├── rpc.py           # RPC method handlers
│   ├── events.py        # Event emitter to frontend
│   └── stream.py        # Server-sent events manager (v3.1)
└── watchdog.py           # Heartbeat monitoring and rollback
```

## Frontend Structure (`src/`)

```
src/
├── api/                  # Backend communication
│   ├── Api.ts           # API client (callPluginMethod wrapper)
│   ├── types.ts         # TypeScript type definitions
│   └── index.ts
├── components/           # UI components
│   ├── WizardMode.tsx   # Simplified mode for beginners
│   ├── ExpertMode.tsx   # Advanced mode (tabs: Manual, Presets, Tests, Diagnostics)
│   ├── LoadGraph.tsx    # Real-time load visualization
│   ├── FanCurveEditor.tsx # Fan curve SVG editor with drag-and-drop
│   ├── PresetsTabNew.tsx # Preset management UI
│   ├── SetupWizard.tsx  # First-run setup wizard (v3.1)
│   ├── TelemetryGraph.tsx # Temperature/power graphs (v3.1)
│   └── SessionHistory.tsx # Session history and comparison (v3.1)
├── context/              # State management
│   └── DeckTuneContext.tsx  # React Context + reducer
└── index.tsx             # Plugin entry point (Decky registration)
```

## Rust Daemon Structure (`gymdeck3/`)

```
gymdeck3/
├── src/
│   ├── main.rs              # Entry point, CLI, signal handling
│   ├── config.rs            # CLI argument parsing
│   ├── load_monitor.rs      # /proc/stat CPU load monitoring
│   ├── strategy/            # Adaptation strategies (conservative, balanced, aggressive)
│   ├── hysteresis.rs        # Dead-band controller
│   ├── interpolation.rs     # Smooth value transitions
│   ├── ryzenadj.rs          # Ryzenadj subprocess executor
│   ├── output.rs            # NDJSON status writer
│   ├── watchdog.rs          # Timeout monitor
│   ├── safety.rs            # Root check, panic hook
│   └── fan/                 # Fan control module (v3.0)
│       ├── mod.rs           # Public interface
│       ├── hwmon.rs         # Low-level sysfs I/O (/sys/class/hwmon)
│       ├── controller.rs    # Curve calculation, smoothing, hysteresis
│       └── safety.rs        # Hard limits (90°C+ override), Drop trait
└── tests/                   # Property-based tests
```

## Naming Conventions

- **Python**: snake_case (files, functions, variables), PascalCase (classes)
- **TypeScript**: PascalCase (components, types), camelCase (functions, variables)
- **Rust**: snake_case (files, functions, modules), PascalCase (types, traits, enums)

## Key Entry Points

- `main.py`: Plugin class with RPC methods, delegates to `backend/api/rpc.py`
- `src/index.tsx`: Decky plugin registration, wraps app in `DeckTuneProvider`
- `gymdeck3/src/main.rs`: CLI daemon entry point
