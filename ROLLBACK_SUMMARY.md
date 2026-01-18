# Rollback to v3.1.13 - Summary

## Date: 2026-01-18

## Reason for Rollback
User reported that v3.5.0 UI improvements were not rendering properly on Steam Deck despite:
- Files being deployed correctly (MD5 hash verified)
- Code loading (test banner appeared)
- Multiple deployment attempts

The following features from v3.5.0 were not visible on Steam Deck:
- Fan Tab: Interactive SVG curve editor with presets
- Dynamic Mode: Load → Undervolt curve visualization
- Localization system (EN/RU)
- Enhanced gamepad navigation

## Rollback Details

### Commit Information
- **Target Commit**: `a75ebc69c76420539d3874b47cbfeaa193636784`
- **Version**: v3.1.13
- **Date**: 2026-01-17

### Rollback Command
```bash
git reset --hard a75ebc6
```

### Deployment Process
1. Built frontend: `npm run build`
2. Created release: `.\scripts\build-release.ps1`
3. Copied to Steam Deck: `scp -r release/DeckTune deck@192.168.0.163:~/Downloads/`
4. Installed on Steam Deck:
   ```bash
   sudo rm -rf ~/homebrew/plugins/DeckTune
   sudo mv ~/Downloads/DeckTune ~/homebrew/plugins/
   sudo chmod +x ~/homebrew/plugins/DeckTune/bin/*
   sudo chmod +x ~/homebrew/plugins/DeckTune/install.sh
   sudo systemctl restart plugin_loader
   ```

### Verification
- ✅ All binaries executable (gymdeck3, ryzenadj, stress-ng, memtester)
- ✅ Version confirmed: 3.1.13
- ✅ Plugin loader restarted successfully

## What Was Lost in Rollback

### v3.5.0 Features (Not in v3.1.13)
- **Localization System**: Full EN/RU translation support
- **Fan Tab Enhancements**: Interactive SVG curve editor with 7 presets
- **Dynamic Mode Visualization**: Real-time load/voltage curve graph
- **Enhanced Gamepad Navigation**: Improved focus management across all tabs
- **UI Optimizations**: Various layout improvements for QAM

### What Remains in v3.1.13
- ✅ All core functionality (autotune, dynamic mode, safety system)
- ✅ Silicon binning
- ✅ Per-game profiles
- ✅ Fan control (basic)
- ✅ Expert mode with extended limits
- ✅ Crash recovery metrics
- ✅ Real-time telemetry
- ✅ Session history
- ✅ Setup wizard

## Next Steps

### Investigation Required
1. **Why didn't v3.5.0 UI render on Steam Deck?**
   - Possible React/Decky Loader compatibility issue
   - Possible SVG rendering issue in Steam Deck's browser
   - Possible CSS/layout issue specific to QAM environment

2. **Testing Approach**
   - Test v3.5.0 components individually
   - Check browser console for errors on Steam Deck
   - Verify Decky Loader version compatibility
   - Test with minimal component changes

### Recommendations
1. Keep v3.1.13 as stable baseline
2. Create feature branch for v3.5.0 improvements
3. Test each major UI change on actual Steam Deck before merging
4. Consider alternative approaches for UI enhancements that work in QAM environment

## Files Changed
- All project files reverted to commit a75ebc6
- No localization files (`src/i18n/`) in v3.1.13
- No enhanced visualization components in v3.1.13

## Status
✅ **COMPLETE** - v3.1.13 successfully deployed to Steam Deck
