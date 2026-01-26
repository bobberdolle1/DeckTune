# 🚀 DeckTune v3.4.0 - In-App Update System

## New Features

### 🔄 In-App Update System
- **One-Click Updates** — Check and install updates directly from Settings menu
- **GitHub Integration** — Automatic version checking against latest releases
- **Real-Time Progress** — Live progress bar with ETA and stage indicators
- **Smart Installation** — Preserves user data and settings during updates
- **Automatic Reload** — Plugin reloads automatically after successful installation
- **Release Notes Preview** — View changelog before installing updates

### Update Stages
1. **Download** (0-40%) — Fetching release from GitHub
2. **Extract** (45-55%) — Unpacking archive
3. **Install** (60-90%) — Copying files and restoring permissions
4. **Finalize** (92-95%) — Cleanup and verification
5. **Complete** (100%) — Ready to reload

## Technical Implementation

### Backend
- `UpdateManager` class with async download/install pipeline
- GitHub API integration for release metadata
- Progress tracking with stage-based percentage calculation
- Backup creation and rollback support
- Binary permissions restoration (ryzenadj, gymdeck3, stress-ng, memtester)

### Frontend
- Progress polling with 1-second intervals
- Stage-based UI updates with descriptive messages
- Error handling with user-friendly notifications
- Settings preservation across updates

## Installation

Download and install via Decky Loader Developer Mode:
1. Download `DeckTune-v3.4.0.zip`
2. Open Decky Loader Settings → Developer Mode
3. Install from ZIP

Or use the new in-app updater if you're on v3.3.4+!

---

**Full Changelog**: https://github.com/bobberdolle1/DeckTune/compare/v3.3.4...v3.4.0
