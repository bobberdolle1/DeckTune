# DeckTune v3.1.23 - Hotfix Release

**Release Date**: January 19, 2026

## 🔧 Critical Hotfixes

This hotfix release resolves critical issues with Silicon Binning diagnostics and plugin loading in Decky Loader v3.2+.

### What's Fixed

**1. ES Module Format for Decky Loader v3.2+**
- Fixed "TypeError: plugin exports is not a function" error
- Changed rollup output format from IIFE to ES module
- Decky Loader v3.2+ requires ES modules with `export default`
- Plugin now loads correctly in latest Decky version

**2. ryzenadj Exit Code Handling**
- Fixed false-positive diagnostic failures in Silicon Binning
- ryzenadj binary returns exit code 255 even on successful execution (this is normal behavior)
- Modified `diagnose()` method to validate success by checking stdout content instead of exit code
- Now checks for "CPU Family" or "STAPM" in output to confirm ryzenadj is working

**3. Binary Executable Permissions**
- Fixed "ryzenadj binary is not executable" error
- Zip archive now preserves executable permissions for Linux binaries
- Created on Linux to maintain proper file permissions
- All binaries (ryzenadj, gymdeck3, stress-ng, memtester) are now executable

### Technical Details

**ES Module Format**
- Decky Loader v3.2+ uses dynamic `import()` for plugin loading
- Requires ES module format with `export default`
- Old IIFE format `(function() { ... })()` no longer works
- New format: `export { index as default };`

**ryzenadj Exit Code**
- ryzenadj has unusual behavior: returns exit code 255 (`exit_group(-1)`) even on success
- This was causing `diagnose()` to incorrectly report failures
- **Before**: Checked `returncode == 0` → Always failed
- **After**: Checks if stdout contains valid data → Works correctly

**Binary Permissions**
- Windows zip tools don't preserve Unix executable bits
- Now building release zip on Linux (Steam Deck) to maintain permissions
- Ensures binaries work immediately after installation

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
