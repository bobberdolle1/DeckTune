# 🔧 DeckTune v3.3.4 - Settings API Migration

## Critical Fixes

### 🐛 Settings Manager API Migration
- **Fixed**: Replaced all legacy Decky `getSetting/setSetting` calls with CoreSettingsManager API (`get_setting/save_setting`)
- **Impact**: Resolves plugin initialization failures and "SettingsManager object has no attribute getSetting" errors
- **Scope**: Updated across entire backend codebase:
  - `main.py` - Plugin initialization
  - `backend/api/rpc.py` - All RPC endpoints
  - `backend/core/safety.py` - LKG and crash recovery
  - `backend/core/session_manager.py` - Session persistence
  - `backend/core/crash_metrics.py` - Crash tracking
  - `backend/dynamic/profile_manager.py` - Profile storage

### 🛠️ Exception Handling
- **Fixed**: NameError in wizard initialization exception handler
- **Details**: Moved crash_info emission inside try block to prevent undefined variable access

## Technical Details

This release completes the migration from Decky Loader's legacy settings API to the new CoreSettingsManager implementation. All settings operations now use the unified API with proper error handling and type safety.

## Installation

Download and install via Decky Loader Developer Mode:
1. Download `DeckTune-v3.3.4.zip`
2. Open Decky Loader Settings → Developer Mode
3. Install from ZIP

---

**Full Changelog**: https://github.com/bobberdolle1/DeckTune/compare/v3.3.3...v3.3.4
