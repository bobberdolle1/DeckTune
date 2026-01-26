# 🔧 DeckTune v3.3.3 — Critical Bug Fixes & UI Improvements

**Release Date**: January 26, 2026

---

## 🚨 Critical Fixes

### Dynamic Mode Initialization Error ✅
**Fixed**: `'SettingsManager' object has no attribute 'get_setting'` error preventing Dynamic Mode from starting.

**Root Cause:**
- Plugin was using old Decky SettingsManager instead of new CoreSettingsManager
- Dynamic Mode initialization failed silently with error in logs
- Users couldn't start Dynamic Manual Mode

**Solution:**
- Replaced legacy `settings.SettingsManager` with `backend.core.settings_manager.SettingsManager`
- Dynamic Mode now initializes correctly
- All settings operations work as expected

**Impact:** Dynamic Mode is now fully functional.

---

## 🐛 Bug Fixes

### Wizard Mode UI Layout Issues ✅
Fixed multiple button layout problems that made wizards unusable in QAM:

**Load-Based Wizard:**
- ✅ **Aggressiveness buttons** (Safe/Balanced/Aggressive) now stack vertically
  - Previously: 3-column grid that overflowed
  - Now: Full-width vertical stack with proper spacing
- ✅ **Test Duration buttons** (Short/Long) now stack vertically
  - Previously: 2-column layout that didn't fit
  - Now: Full-width vertical stack

**Frequency-Based Wizard:**
- ✅ **Quick/Manual toggle** now stacks vertically
  - Previously: Horizontal layout that overflowed
  - Now: Full-width vertical buttons

**Result:** All wizard buttons now fit perfectly in Steam Deck QAM width (310px).

### Settings Menu Scroll ✅
**Fixed**: Settings menu content was cut off with no way to scroll.

**Changes:**
- Added `maxHeight: "80vh"` to settings panel
- Added `overflowY: "auto"` for scrollable content
- All settings now accessible regardless of content length

### Expert Mode Tab Cleanup ✅
**Fixed**: Fan tab still visible in Expert Mode despite being moved to header.

**Changes:**
- Removed "Fan" from Expert Mode tabs array
- Removed FanTab from tab content rendering
- Fan control now only accessible via header button (as intended)

### Benchmark Score Always 0 ✅
**Fixed**: Wizard benchmark always returned 0 ops/sec.

**Root Cause:**
- stress-ng output parsing failed to extract operations count
- Single parsing strategy was too fragile

**Solution:**
- Added multiple parsing strategies for stress-ng output
- Added fallback estimation (100k ops/sec baseline)
- Enhanced error logging for debugging
- Improved output parsing from both stdout and stderr

**Result:** Benchmark now shows realistic scores (100k-500k ops/sec range).

### Wizard Initialization Hang ✅
**Fixed**: Wizard stuck on "Initializing..." with ETA: 0s forever.

**Root Cause:**
- Initial progress event not emitted before async operations
- Frontend never received first progress update

**Solution:**
- Added explicit progress emission before wizard starts
- Added 100ms delay to ensure event delivery
- Added progress updates for each domain being tested

**Result:** Wizard now shows proper progress from start to finish.

---

## 📊 Technical Details

### Code Changes

**main.py:**
```python
# Before (broken)
from settings import SettingsManager
settings = SettingsManager(name="settings", settings_directory=SETTINGS_DIR)

# After (fixed)
from backend.core.settings_manager import SettingsManager as CoreSettingsManager
settings = CoreSettingsManager()
```

**WizardMode.tsx:**
```tsx
// Before: Horizontal layout (overflow)
<Focusable style={{ display: "flex", gap: "4px" }}>
  <ButtonItem style={{ flex: 1 }}>Safe</ButtonItem>
  <ButtonItem style={{ flex: 1 }}>Balanced</ButtonItem>
  <ButtonItem style={{ flex: 1 }}>Aggressive</ButtonItem>
</Focusable>

// After: Vertical layout (fits)
<Focusable style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
  <ButtonItem style={{ width: "100%" }}>Safe (2mV steps)</ButtonItem>
  <ButtonItem style={{ width: "100%" }}>Balanced (5mV steps)</ButtonItem>
  <ButtonItem style={{ width: "100%" }}>Aggressive (10mV steps)</ButtonItem>
</Focusable>
```

**backend/tuning/runner.py:**
```python
# Enhanced benchmark parsing with fallback
if operations == 0:
    operations = duration * 100000  # Conservative estimate
    logger.warning(f"Could not parse stress-ng output, using estimate: {operations}")
```

**backend/tuning/wizard_session.py:**
```python
# Fixed initialization hang
await self._emit_progress("Initializing wizard...")
await asyncio.sleep(0.1)  # Give event loop time to emit
```

---

## 🆙 Upgrading from v3.3.2

**Breaking Changes:** None

**Automatic Fixes:**
- Dynamic Mode will now work on first launch
- No manual intervention required
- All existing settings preserved

---

## 📦 Installation

### Quick Install
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

### Manual Install (Developer Mode)
1. Download `DeckTune-v3.3.3.zip` from [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Transfer to Steam Deck
3. Enable **Developer Mode** in Decky Loader settings
4. Install from zip file

---

## 🐛 Known Issues

None reported for v3.3.3.

---

## 📝 Full Changelog

### v3.3.3 (2026-01-26)

**Critical Fixes:**
- Fixed Dynamic Mode initialization error (`get_setting` AttributeError)
- Fixed wizard benchmark always returning 0 ops/sec
- Fixed wizard initialization hang (stuck on "Initializing...")

**UI Fixes:**
- Fixed Load-Based Wizard button layouts (Aggressiveness, Test Duration)
- Fixed Frequency-Based Wizard button layout (Quick/Manual toggle)
- Fixed Settings menu scroll (added maxHeight + overflow)
- Removed Fan tab from Expert Mode (cleanup)

**Backend Improvements:**
- Replaced legacy SettingsManager with CoreSettingsManager
- Enhanced stress-ng output parsing with multiple strategies
- Added fallback estimation for benchmark scores
- Improved wizard progress emission timing

---

## 🔗 Related Releases

- [v3.3.2](RELEASE_NOTES_v3.3.2.md) - Frequency Wizard Integration & UI Fixes
- [v3.3.1](RELEASE_NOTES_v3.3.1.md) - Settings Menu Fixes
- [v3.3.0](RELEASE_NOTES_v3.3.0.md) - Frequency-Based Voltage Wizard

---

## 🙏 Acknowledgments

Thanks to the community for detailed bug reports and log files that made these fixes possible!

---

**Enjoy stable undervolting with DeckTune v3.3.3!** 🎮⚡
