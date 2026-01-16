# DeckTune Technology Stack

## Architecture

Three main components:

1. **Python Backend** (`backend/`, `main.py`): Core logic, RPC API, safety management
2. **TypeScript Frontend** (`src/`): React UI for Decky Loader
3. **Rust Daemon** (`gymdeck3/`): High-performance dynamic mode controller

## Tech Stack

### Backend (Python)
- **Runtime**: Python 3.x (SteamOS system Python)
- **Dependencies**: Standard library only (asyncio, subprocess, json, dataclasses, pathlib)
- **Framework**: Decky Loader plugin API
- **External Tools**: ryzenadj (AMD APU control), stress-ng, memtester

### Frontend (TypeScript/React)
- **Language**: TypeScript 5.3+ (strict mode)
- **Framework**: React 18 (provided by Decky Loader)
- **UI Library**: `@decky/ui` (Steam Deck UI components)
- **Build Tool**: Rollup 4.x with `@decky/rollup`
- **Target**: ES2020, ESNext modules

### Dynamic Mode Daemon (Rust)
- **Language**: Rust 2021 edition
- **Runtime**: Tokio async runtime
- **CLI**: clap 4.x with derive macros
- **Serialization**: serde + serde_json
- **Testing**: proptest (property-based testing)
- **Target**: `x86_64-unknown-linux-musl` (static linking)
- **Optimization**: Size-optimized (`-Oz`), LTO enabled, stripped

## Common Commands

### Frontend
```bash
npm install          # Install dependencies
npm run build        # Production build
npm run watch        # Development build with watch
```
Output: `dist/index.js`

### Rust (gymdeck3)
```bash
cd gymdeck3
rustup target add x86_64-unknown-linux-musl  # One-time setup
cargo build                                   # Dev build
cargo build --release --target x86_64-unknown-linux-musl  # Production
cargo test                                    # Run tests
```
Output: `target/x86_64-unknown-linux-musl/release/gymdeck3` (< 5MB static binary)

### Python Testing
```bash
pip install -r requirements-test.txt  # Install test deps
pytest tests/ -v                      # Run all tests
pytest tests/test_safety_clamp.py -v  # Run specific test
```

## Key Libraries

### Python
- **decky**: Decky Loader plugin API (logging, settings, events)
- **hypothesis**: Property-based testing framework

### TypeScript
- **@decky/api**: Decky API (addEventListener, callPluginMethod)
- **@decky/ui**: Steam Deck UI components (PanelSection, ButtonItem, etc.)

### Rust
- **tokio**: Async runtime with signal handling
- **clap**: CLI argument parsing
- **proptest**: Property-based testing

### External Binaries
- **ryzenadj**: AMD APU control utility (in `bin/`)
- **stress-ng**: CPU stress testing (system package)
- **memtester**: Memory stress testing (system package)
