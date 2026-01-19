# DeckTune v3.1.26 Release Notes

## 🎉 Major Feature: Settings Management System

This release introduces a comprehensive settings management system with persistent storage and advanced automation features.

### ✨ New Features

#### Header Bar Navigation
- Compact icon-based navigation (20px icons)
- Quick access to Fan Control and Settings
- Right-aligned layout optimized for Steam Deck
- Full gamepad support with D-pad navigation

#### Settings Menu
- Centralized modal for global plugin configuration
- Expert Mode toggle with safety confirmation dialog
- Auto-save on all changes
- WCAG AA accessibility compliant
- Backdrop dismiss and close button

#### Apply on Startup
- Automatically apply your last profile when Steam Deck boots
- No need to manually apply settings after each reboot
- Graceful handling when no previous profile exists
- Detailed logging for troubleshooting

#### Game Only Mode
- Apply undervolt only during games
- Automatic reset to default (0mV) in Steam menu
- Monitors Steam game launches and exits
- Transitions within 2 seconds
- Perfect for users who want performance during gaming but stability in menus

#### Persistent Settings
- All settings survive plugin reloads and system reboots
- Backend storage with atomic writes and backup
- Graceful error handling with fallback to defaults
- Settings stored at: `~/homebrew/settings/decktune/settings.json`

#### Manual Tab Cleanup
- Removed Expert Mode toggle (moved to Settings Menu)
- Added "Startup Behavior" section with Apply on Startup and Game Only Mode toggles
- Cleaner, more focused interface for undervolt controls

### 🔧 Technical Details

#### Backend Components
- **SettingsManager** (`backend/core/settings_manager.py`)
  - Atomic write operations with backup
  - JSON serialization for all values
  - RPC methods: `save_setting()`, `get_setting()`, `load_all_settings()`

- **GameStateMonitor** (`backend/core/game_state_monitor.py`)
  - Steam event subscription for game launches/exits
  - Polling fallback (2-second interval)
  - RPC methods: `enable_game_only_mode()`, `disable_game_only_mode()`

- **GameOnlyMode** (`backend/core/game_only_mode.py`)
  - Profile application on game start
  - Undervolt reset on game exit
  - Integration with GameStateMonitor and SettingsManager

#### Frontend Components
- **SettingsContext** (`src/context/SettingsContext.tsx`)
  - React Context API for unified settings access
  - State: expertMode, applyOnStartup, gameOnlyMode, lastActiveProfile
  - `useSettings()` hook for component access

- **HeaderBar** (`src/components/HeaderBar.tsx`)
  - Compact icon buttons with gamepad support
  - ARIA labels for accessibility

- **SettingsMenu** (`src/components/SettingsMenu.tsx`)
  - Modal overlay with Expert Mode toggle
  - Warning dialog with explicit confirmation
  - Auto-save functionality

### 🧪 Testing

- **91 comprehensive tests** covering all functionality
- **10 property-based tests** for correctness verification:
  1. Settings persistence round-trip
  2. Expert Mode confirmation requirement
  3. Game state transition triggers
  4. Startup profile application
  5. Settings context synchronization
  6. Storage failure resilience
  7. Game Only Mode monitoring lifecycle
  8. Header navigation exclusivity
  9. Manual tab control exclusivity
  10. Settings menu state isolation

- **Integration tests** for full workflows
- **Manual testing materials** prepared (checklist, guide, accessibility checker)

### 📋 Requirements Validated

✅ Requirement 1: Header bar with compact navigation  
✅ Requirement 2: Dedicated Settings menu  
✅ Requirement 3: Settings persistence across reloads  
✅ Requirement 4: Apply on Startup functionality  
✅ Requirement 5: Game Only Mode with automatic switching  
✅ Requirement 6: Backend game state monitoring  
✅ Requirement 7: Manual tab focused on undervolt controls  
✅ Requirement 8: Fan Control accessible only via header  
✅ Requirement 9: Logical settings organization  
✅ Requirement 10: Centralized settings management  

### 🎯 Use Cases

#### For Casual Users
- Enable "Apply on Startup" to never worry about applying settings again
- Use "Game Only Mode" for automatic performance boost during gaming

#### For Power Users
- Fine-tune settings per game with automatic profile switching
- Expert Mode with safety confirmation for advanced undervolting
- Full control over startup behavior and game-specific settings

#### For Safety-Conscious Users
- Game Only Mode ensures stability in Steam menu
- Expert Mode requires explicit confirmation
- All settings can be easily reset via Settings Menu

### 📦 Installation

#### Quick Install
```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

#### Manual Install
1. Download `DeckTune-v3.1.26.zip` from releases
2. Enable Developer Mode in Decky Loader settings
3. Install from zip file in Decky Loader

### 🔄 Upgrade from Previous Versions

Settings from previous versions will be automatically migrated. No manual action required.

### 🐛 Known Issues

None at this time. Please report any issues on GitHub.

### 🙏 Acknowledgements

- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — plugin framework
- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj) — AMD APU control utility
- All contributors and testers

### 📄 License

GPL-3.0 License — see [LICENSE](LICENSE)

---

**Full Changelog**: https://github.com/bobberdolle1/DeckTune/blob/main/CHANGELOG.md
