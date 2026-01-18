# DeckTune Branch Strategy

## Main Branch: v3.1.13 (Stable)

**Branch**: `main`  
**Commit**: `a75ebc6`  
**Version**: 3.1.13  
**Status**: ✅ **STABLE - PRODUCTION READY**

This is the most stable and tested version of DeckTune. All core features work correctly on Steam Deck hardware.

### Why v3.1.13 is Main
- ✅ All features tested and working on actual Steam Deck
- ✅ UI renders correctly in Decky Loader QAM
- ✅ Gamepad navigation works properly
- ✅ No rendering issues or compatibility problems
- ✅ Clean, focused interface

### Core Features (v3.1.13)
- Auto platform detection with caching
- Autotune with binary search
- Dynamic mode (gymdeck3 Rust daemon)
- Fan control (basic)
- Safety system with watchdog
- Per-game profiles with auto-switching
- Silicon binning
- Expert mode with extended limits (-100mV)
- Built-in stress tests
- Real-time telemetry graphs
- Crash recovery metrics
- Session history tracking
- Setup wizard

## Experimental Branch: v3.5.0

**Branch**: `v3.5.0-experimental`  
**Commit**: `5cb6768`  
**Version**: 3.5.0  
**Status**: ⚠️ **EXPERIMENTAL - NOT WORKING ON HARDWARE**

This branch contains UI enhancements that don't render properly on Steam Deck.

### What Was Added in v3.5.0
- 🌐 Full localization system (EN/RU)
- 📊 Enhanced Fan Tab with interactive SVG curve editor
- 📈 Dynamic Mode visualization with load/voltage curves
- 🎮 Improved gamepad navigation
- 🎨 Various UI optimizations

### Known Issues
- ❌ UI components don't render on Steam Deck (despite code loading)
- ❌ Fan Tab visualization not visible
- ❌ Dynamic Mode graph not visible
- ❌ Localization not working on hardware
- ⚠️ Suspected React/Decky Loader compatibility issue

### Investigation Needed
1. Why do SVG components not render in QAM?
2. Is there a Decky Loader version incompatibility?
3. Are there browser/CSS issues specific to Steam Deck?
4. Do we need alternative approaches for visualization?

## Development Workflow

### For Stable Features
```bash
git checkout main
# Make changes
# Test on Steam Deck
git commit -m "feature: description"
git push origin main
```

### For Experimental Features
```bash
git checkout v3.5.0-experimental
# Make changes
# Test locally first
git commit -m "experiment: description"
git push origin v3.5.0-experimental
```

### Merging Experimental → Main
Only merge when:
1. ✅ Feature tested on actual Steam Deck hardware
2. ✅ UI renders correctly in QAM
3. ✅ Gamepad navigation works
4. ✅ No performance issues
5. ✅ No compatibility problems

## Deployment

### Production (Steam Deck)
Always deploy from `main` branch:
```bash
git checkout main
npm run build
.\scripts\build-release.ps1
# Deploy to Steam Deck
```

### Testing (Local)
Can test experimental branch locally:
```bash
git checkout v3.5.0-experimental
npm run build
# Test in local Decky environment
```

## Version History

| Version | Branch | Status | Notes |
|---------|--------|--------|-------|
| 3.1.13 | main | ✅ Stable | Current production version |
| 3.5.0 | v3.5.0-experimental | ⚠️ Broken | UI doesn't render on hardware |
| 3.1.12 | (tag) | ✅ Stable | Previous stable version |

## Recommendations

1. **Always test on hardware** before merging to main
2. **Keep main stable** - it's what users rely on
3. **Use experimental branch** for risky UI changes
4. **Document issues** when features don't work on hardware
5. **Consider alternatives** if approach doesn't work on Steam Deck

## Contact

If you find issues with main branch, report them immediately.  
If you want to help fix v3.5.0 experimental, check the branch and investigate rendering issues.
