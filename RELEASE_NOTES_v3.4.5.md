# 🔧 DeckTune v3.4.5 - Decky Loader Compatibility Fix

## Fixed

### 🐛 Installation Issue
- **package.json Missing** — Fixed Decky Loader installation failure
  - Added `package.json` to zip root (required by Decky Loader)
  - Updated build script to include all required files
  - Verified structure matches official Decky plugin template

### 📦 Build System
- **Zip Structure** — Ensured proper Decky Loader format:
  ```
  DeckTune-v3.4.5.zip
    DeckTune/
      package.json ✅ [required]
      plugin.json ✅ [required]
      main.py ✅ [required]
      LICENSE ✅ [required]
      dist/
        index.js ✅ [required]
      backend/
      bin/
  ```

## Installation

Download and install via Decky Loader Developer Mode:

1. Download `DeckTune-v3.4.5.zip`
2. Open Decky Loader Settings → Developer Mode
3. Install from ZIP

---

**Full Changelog**: https://github.com/bobberdolle1/DeckTune/compare/v3.4.0...v3.4.5
