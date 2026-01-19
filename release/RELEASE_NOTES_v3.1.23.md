# DeckTune v3.1.23 - Hotfix Release

**Release Date**: January 19, 2026

## 🔧 Critical Hotfix

This is a hotfix release that resolves a critical issue with Silicon Binning diagnostics introduced by ryzenadj's exit code behavior.

### What's Fixed

**ryzenadj Exit Code Handling**
- Fixed false-positive diagnostic failures in Silicon Binning
- ryzenadj binary returns exit code 255 even on successful execution (this is normal behavior)
- Modified `diagnose()` method to validate success by checking stdout content instead of exit code
- Now checks for "CPU Family" or "STAPM" in output to confirm ryzenadj is working
- Silicon Binning diagnostics now work correctly

### Technical Details

The ryzenadj binary has an unusual behavior where it returns exit code 255 (`exit_group(-1)`) even when executing successfully. This was causing the `diagnose()` method to incorrectly report failures during Silicon Binning initialization.

**Before**: Checked `returncode == 0` → Always failed
**After**: Checks if stdout contains valid data → Works correctly

### Testing

Added `test_binning_api.py` - a comprehensive test script that:
- Verifies platform detection
- Tests ryzenadj initialization  
- Validates diagnostics (same checks as binning)
- Tests undervolt application and reset
- Useful for troubleshooting binning issues

Run it with: `sudo python test_binning_api.py`

## 📦 Installation

### New Installation
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/download/v3.1.23/DeckTune-v3.1.23.zip -o DeckTune.zip
sudo unzip -o DeckTune.zip -d /home/deck/homebrew/plugins/
sudo systemctl restart plugin_loader
```

### Update from v3.1.22
```bash
cd /home/deck/homebrew/plugins/DeckTune
sudo git pull
sudo systemctl restart plugin_loader
```

Or download and extract the zip file manually.

## ✅ Verification

After installation, verify binning works:

1. Open DeckTune in Gaming Mode
2. Go to Expert Mode → Silicon Binning
3. Click "Start Binning"
4. Should start without "ryzenadj test command failed" error

Or run the test script:
```bash
cd /home/deck/homebrew/plugins/DeckTune
sudo python test_binning_api.py
```

Expected output: "RESULT: ALL TESTS PASSED ✓"

## 🔗 Links

- [Full Changelog](https://github.com/bobberdolle1/DeckTune/blob/main/CHANGELOG.md)
- [GitHub Repository](https://github.com/bobberdolle1/DeckTune)
- [Report Issues](https://github.com/bobberdolle1/DeckTune/issues)

## 📝 Notes

- This release only affects Silicon Binning diagnostics
- No changes to undervolt application logic
- No changes to Wizard Mode or other features
- Safe to update from v3.1.22

---

**Previous Release**: [v3.1.22](https://github.com/bobberdolle1/DeckTune/releases/tag/v3.1.22) - Silicon Binning NOPASSWD fix
