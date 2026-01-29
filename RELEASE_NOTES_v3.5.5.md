# 🔧 DeckTune v3.5.5 - Frequency Wizard Critical Fix

## Fixed

### 🐛 Frequency Wizard Execution
- **CPUFreqController Instance Mismatch** — Fixed frequency wizard failing immediately with "CPUFreqController required" error
  - Root cause: RPC was creating new CPUFreqController instead of using TestRunner's instance
  - TestRunner's `run_frequency_locked_test()` checked its own `_cpufreq_controller` which was different
  - Solution: Reuse CPUFreqController from TestRunner instead of creating new instances
  - All frequency tests now execute correctly with proper frequency locking

## Installation

Download and install via Decky Loader Developer Mode:

1. Download `DeckTune-v3.5.5.zip`
2. Open Decky Loader Settings → Developer Mode
3. Install from ZIP

Or use the in-app updater from Settings menu!

---

**Full Changelog**: https://github.com/bobberdolle1/DeckTune/compare/v3.5.0...v3.5.5
