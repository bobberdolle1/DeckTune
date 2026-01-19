# DeckTune v3.1.27 Release Notes

## 🎯 Wizard Mode Refactoring

Complete redesign of the automated undervolt discovery system with transparent progress tracking, crash recovery, and chip quality grading.

## ✨ New Features

### Wizard Mode Overhaul
- **Step-down algorithm**: Systematic testing from -10mV until failure with configurable step sizes
- **Crash recovery**: Automatic dirty exit detection with rollback to last stable values
- **Chip quality grading**: Bronze/Silver/Gold/Platinum tiers based on silicon lottery results
- **Real-time progress**: Live ETA, OTA (elapsed time), heartbeat indicator, and test metrics
- **Curve visualization**: SVG chart showing voltage offset vs temperature progression
- **Results history**: Persistent storage of all wizard sessions with replay capability

### Configuration Options
- **Aggressiveness levels**:
  - Safe: 2mV steps, +10mV safety margin (~15-20 minutes)
  - Balanced: 5mV steps, +5mV safety margin (~5-10 minutes)
  - Aggressive: 10mV steps, +2mV safety margin (~3-5 minutes)
- **Test duration**: Short (30s) or Long (120s) per iteration
- **Platform detection**: Automatic safety limits (LCD: -100mV, OLED: -80mV)

### User Experience
- **Configuration screen**: Simple dropdown selections with estimated completion time
- **Progress screen**: Real-time updates with current stage, offset being tested, and live metrics
- **Results screen**: Chip grade badge, recommended offset, curve visualization, and apply/save actions
- **Crash recovery modal**: Automatic detection on next boot with crash details and last stable value
- **Panic disable**: Always-visible emergency reset button

## 🔧 Technical Implementation

### Backend
- `WizardSession` class with full state machine (IDLE → RUNNING → FINISHED/CRASHED)
- Crash flag system with atomic file operations
- State persistence to `~/homebrew/settings/decktune/`
- 6 new RPC endpoints for wizard control
- 3 new event emitters for real-time updates

### Frontend
- `WizardContext` with React Context API
- Complete component refactor with modular screens
- SVG-based curve visualization
- Type-safe API integration

## 📊 Chip Grading Scale

- **Platinum** (≥-51mV): Top 1-5% silicon quality
- **Gold** (-36 to -50mV): Top 20% silicon quality
- **Silver** (-21 to -35mV): Top 40% silicon quality
- **Bronze** (-10 to -20mV): Bottom 60% silicon quality

## 🛡️ Safety Features

- Platform-specific hard limits enforced
- 3 consecutive failure stop condition
- Automatic safety margins based on aggressiveness
- Watchdog heartbeat monitoring
- Crash recovery with automatic rollback
- User confirmation required for aggressive settings

## 🔄 Migration Notes

- Existing wizard functionality replaced with new system
- Old autotune/binning modes remain available
- No breaking changes to existing presets or profiles
- Wizard results stored separately from manual configurations

## 📦 Installation

Install via Decky Loader plugin store or manual ZIP installation in developer mode.

## 🐛 Known Issues

None reported.

## 🙏 Credits

Developed by the DeckTune team for the Steam Deck community.
