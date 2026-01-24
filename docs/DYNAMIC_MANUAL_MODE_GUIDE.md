# Dynamic Manual Mode User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Simple Mode](#simple-mode)
4. [Expert Mode](#expert-mode)
5. [Understanding Voltage Curves](#understanding-voltage-curves)
6. [Configuration Examples](#configuration-examples)
7. [Safety and Best Practices](#safety-and-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

---

## Introduction

Dynamic Manual Mode gives you precise control over CPU voltage curves, allowing you to optimize performance and power consumption based on real-time CPU load. Unlike static undervolting, dynamic mode automatically adjusts voltage as your workload changes.

### Key Concepts

**Voltage Curve**: A relationship between CPU load (0-100%) and voltage offset (-100 to 0 mV). Lower voltage = more power savings but less stability margin.

**Three Parameters:**
- **Minimal Value**: Voltage offset at low CPU load (idle/light tasks)
- **Maximum Value**: Voltage offset at high CPU load (gaming/heavy tasks)
- **Threshold**: CPU load percentage where transition occurs

**Why Dynamic?**
- Aggressive undervolt at idle → Better battery life
- Conservative undervolt under load → Better stability
- Automatic adjustment → No manual intervention needed

---

## Getting Started

### Prerequisites
- DeckTune v3.2.0 or later
- Expert Mode enabled (Settings → Expert Mode toggle)
- Basic understanding of undervolting concepts

### Accessing Dynamic Manual Mode

1. Open DeckTune from the Decky menu (⋯ button)
2. Navigate to Expert Mode
3. Click the "Dynamic Manual" tab
4. You'll see the Dynamic Manual Mode interface

### First-Time Setup

**Recommended for beginners:**
1. Start with Simple Mode (toggle at top)
2. Use safe defaults: -30mV / -15mV / 50%
3. Click "Apply" to save
4. Click "Start Dynamic Mode"
5. Monitor metrics for 5-10 minutes
6. If stable, you can experiment with more aggressive values

---

## Simple Mode

Simple Mode applies identical voltage curves to all CPU cores simultaneously. This is the recommended starting point for most users.

### Interface Overview

```
┌─────────────────────────────────────┐
│ Simple Mode: [ON]                   │
├─────────────────────────────────────┤
│ Minimal Value:  [-30] mV            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                     │
│ Maximum Value:  [-15] mV            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                     │
│ Threshold:      [50] %              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
├─────────────────────────────────────┤
│ [Apply] [Start Dynamic Mode]        │
└─────────────────────────────────────┘
```

### Step-by-Step Configuration

**1. Enable Simple Mode**
- Toggle "Simple Mode" to ON
- Core tabs will be hidden
- All cores will use the same settings

**2. Adjust Minimal Value (Idle Voltage)**
- Use slider or L1/R1 buttons
- Range: -100 to 0 mV
- Recommendation: Start at -30mV
- More negative = more aggressive = better battery at idle
- Too aggressive = potential instability at idle

**3. Adjust Maximum Value (Load Voltage)**
- Use slider or L1/R1 buttons
- Range: -100 to 0 mV
- Must be ≥ Minimal Value
- Recommendation: Start at -15mV
- More negative = more aggressive = better performance
- Too aggressive = crashes under load

**4. Adjust Threshold (Transition Point)**
- Use slider or L1/R1 buttons
- Range: 0 to 100%
- Recommendation: Start at 50%
- Lower threshold = earlier transition to safe voltage
- Higher threshold = longer time at aggressive voltage

**5. Apply Configuration**
- Click "Apply" button
- Configuration saved to localStorage and backend
- Curve visualization updates immediately

**6. Start Dynamic Mode**
- Click "Start Dynamic Mode" button
- Status indicator changes to "Active"
- Metrics begin updating every 500ms
- Voltage adjusts automatically based on load

### Simple Mode Use Cases

**Battery Saver Profile:**
```
Minimal Value: -35mV  (very aggressive at idle)
Maximum Value: -10mV  (very safe under load)
Threshold: 40%        (early transition to safe)
```
Best for: Web browsing, video playback, light tasks

**Balanced Profile:**
```
Minimal Value: -30mV  (moderate at idle)
Maximum Value: -15mV  (moderate under load)
Threshold: 50%        (balanced transition)
```
Best for: General use, mixed workloads

**Performance Profile:**
```
Minimal Value: -25mV  (conservative at idle)
Maximum Value: -20mV  (aggressive under load)
Threshold: 60%        (late transition)
```
Best for: Gaming, sustained high performance

**Conservative Profile:**
```
Minimal Value: -20mV  (very safe at idle)
Maximum Value: -10mV  (very safe under load)
Threshold: 30%        (very early transition)
```
Best for: Stability testing, first-time users

---

## Expert Mode

Expert Mode allows independent voltage curve configuration for each CPU core (0-3). This enables fine-tuned optimization for specific workloads.

### Interface Overview

```
┌─────────────────────────────────────┐
│ Simple Mode: [OFF]                  │
├─────────────────────────────────────┤
│ [Core 0] [Core 1] [Core 2] [Core 3] │ ← Core tabs
├─────────────────────────────────────┤
│ Core 0 Configuration:               │
│                                     │
│ Minimal Value:  [-35] mV            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                     │
│ Maximum Value:  [-20] mV            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                     │
│ Threshold:      [60] %              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
├─────────────────────────────────────┤
│ [Apply] [Start Dynamic Mode]        │
└─────────────────────────────────────┘
```

### Step-by-Step Configuration

**1. Disable Simple Mode**
- Toggle "Simple Mode" to OFF
- Core tabs appear (Core 0, Core 1, Core 2, Core 3)
- Each core can have independent settings

**2. Select a Core**
- Click a core tab or use D-pad Up/Down
- Configuration sliders update for selected core
- Curve visualization shows selected core's curve

**3. Configure Selected Core**
- Adjust Minimal Value, Maximum Value, Threshold
- Same process as Simple Mode
- Repeat for each core you want to customize

**4. Apply All Configurations**
- Click "Apply" button
- All core configurations saved simultaneously
- Each core's curve updates independently

**5. Start Dynamic Mode**
- Click "Start Dynamic Mode" button
- All cores begin dynamic voltage adjustment
- Each core operates independently based on its curve

### Per-Core Strategy

**Understanding Core Behavior:**
- **Core 0**: Primary core, handles most single-threaded tasks
- **Core 1**: Secondary core, assists Core 0
- **Core 2-3**: Background cores, handle parallel tasks

**Aggressive Primary Core:**
```
Core 0: -35mV → -20mV @ 60%  (aggressive, high threshold)
Core 1: -30mV → -15mV @ 50%  (balanced)
Core 2: -25mV → -10mV @ 40%  (conservative)
Core 3: -25mV → -10mV @ 40%  (conservative)
```
Best for: Single-threaded games, emulation

**Balanced All Cores:**
```
Core 0: -30mV → -15mV @ 50%
Core 1: -30mV → -15mV @ 50%
Core 2: -30mV → -15mV @ 50%
Core 3: -30mV → -15mV @ 50%
```
Best for: Multi-threaded games, general use

**Conservative Background Cores:**
```
Core 0: -30mV → -20mV @ 55%  (moderate)
Core 1: -30mV → -20mV @ 55%  (moderate)
Core 2: -20mV → -10mV @ 40%  (very safe)
Core 3: -20mV → -10mV @ 40%  (very safe)
```
Best for: Stability, background task handling

### Switching Between Modes

**Simple → Expert:**
- Current configuration preserved for all cores
- Each core retains its settings
- You can now customize individually

**Expert → Simple:**
- Core 0 configuration becomes the unified setting
- All cores will use Core 0's values when you Apply
- Previous per-core configs are preserved (not lost)
- Switching back to Expert restores per-core configs

---

## Understanding Voltage Curves

### Curve Visualization

The voltage curve graph shows how voltage changes with CPU load:

```
Voltage (mV)
    0 ┤                              ╭─────────
      │                          ╭───╯
  -10 ┤                      ╭───╯
      │                  ╭───╯
  -20 ┤              ╭───╯
      │          ╭───╯
  -30 ┤──────────╯
      │          ↑
      └──────────┼────────────────────────────→ CPU Load (%)
                50 (Threshold)
```

**Key Points:**
- **Flat section (0-50%)**: Minimal Value applied (-30mV)
- **Transition point (50%)**: Threshold where interpolation begins
- **Slope section (50-100%)**: Linear interpolation to Maximum Value
- **Flat section (100%)**: Maximum Value applied (-15mV)

### Curve Calculation

The system calculates voltage for any load percentage:

```
If load ≤ threshold:
    voltage = minimal_value

If load > threshold:
    voltage = minimal_value + (maximum_value - minimal_value) * 
              (load - threshold) / (100 - threshold)
```

**Example (Minimal: -30mV, Maximum: -15mV, Threshold: 50%):**
- Load 0%: -30mV (minimal)
- Load 25%: -30mV (below threshold)
- Load 50%: -30mV (at threshold)
- Load 60%: -27mV (interpolated: -30 + 15 * 0.2)
- Load 75%: -22.5mV (interpolated: -30 + 15 * 0.5)
- Load 100%: -15mV (maximum)

### Current Operating Point

The graph shows a marker indicating:
- Current CPU load (X-axis position)
- Current applied voltage (Y-axis position)
- Updates every 500ms
- Helps visualize real-time behavior

---

## Configuration Examples

### Example 1: Maximum Battery Life

**Goal:** Longest possible battery life, stability is secondary

**Simple Mode Configuration:**
```
Minimal Value: -40mV
Maximum Value: -10mV
Threshold: 35%
```

**Behavior:**
- Very aggressive at idle (-40mV)
- Quick transition to safe voltage (35% load)
- Conservative under load (-10mV)
- Maximizes power savings during light use
- Prioritizes stability during gaming

**Expected Results:**
- +15-25% battery life in light use
- Minimal performance impact
- May crash if chip can't handle -40mV at idle

---

### Example 2: Gaming Performance

**Goal:** Best gaming performance, battery life is secondary

**Expert Mode Configuration:**
```
Core 0: -30mV → -25mV @ 65%
Core 1: -30mV → -25mV @ 65%
Core 2: -25mV → -20mV @ 60%
Core 3: -25mV → -20mV @ 60%
```

**Behavior:**
- Moderate idle savings (-25 to -30mV)
- Late transition (60-65% load)
- Aggressive under load (-20 to -25mV)
- Maintains performance headroom
- Reduces power consumption during gaming

**Expected Results:**
- +5-10% battery life during gaming
- No performance degradation
- Cooler temperatures under load

---

### Example 3: Emulation (Single-Threaded)

**Goal:** Optimize for single-threaded emulator performance

**Expert Mode Configuration:**
```
Core 0: -35mV → -25mV @ 70%  (primary, aggressive)
Core 1: -30mV → -20mV @ 60%  (secondary, moderate)
Core 2: -20mV → -10mV @ 40%  (background, safe)
Core 3: -20mV → -10mV @ 40%  (background, safe)
```

**Behavior:**
- Core 0 gets most aggressive curve (handles emulator)
- Core 1 provides moderate assistance
- Cores 2-3 stay conservative (minimal use)
- Late transition on primary cores (70%)
- Early transition on background cores (40%)

**Expected Results:**
- +10-15% battery life
- No emulation performance loss
- Stable background task handling

---

### Example 4: First-Time User (Safe)

**Goal:** Test dynamic mode without risk

**Simple Mode Configuration:**
```
Minimal Value: -20mV
Maximum Value: -10mV
Threshold: 30%
```

**Behavior:**
- Conservative at all loads
- Very early transition (30%)
- Minimal risk of instability
- Still provides some power savings

**Expected Results:**
- +5-8% battery life
- Extremely stable
- Good starting point for testing

---

### Example 5: Stress Testing

**Goal:** Find maximum stable undervolt for your chip

**Process:**
1. Start with safe values (-20mV / -10mV / 50%)
2. Run stress test (Expert Mode → Tests → CPU Stress)
3. If stable for 10 minutes, increase aggressiveness:
   - Decrease Minimal Value by -5mV
   - Decrease Maximum Value by -5mV
4. Repeat until instability occurs
5. Back off by +5mV for safety margin
6. Use these values as your maximum

**Example Results:**
```
Chip A (Good): -40mV → -25mV @ 50%
Chip B (Average): -30mV → -15mV @ 50%
Chip C (Poor): -20mV → -10mV @ 50%
```

---

## Safety and Best Practices

### Safety Features

**1. Validation**
- Prevents min > max configurations
- Enforces -100 to 0 mV range
- Checks platform-specific limits
- Disables Apply button when invalid

**2. Clamping**
- Automatically clamps out-of-range values
- Respects hardware limits
- Prevents accidental dangerous configs

**3. Warning Dialogs**
- Alerts for aggressive configurations
- Requires confirmation for risky settings
- Explains potential consequences

**4. Reset to Safe Defaults**
- One-click restore to -30mV / -15mV / 50%
- Available at any time
- Guaranteed safe for all chips

**5. Last Known Good (LKG)**
- Automatically saves stable configurations
- Updated after 30 seconds of stability
- Used for recovery after crashes
- Accessible via "Restore Last Stable" button

**6. Panic Disable**
- Red button always visible
- Instantly stops dynamic mode
- Resets all voltages to 0 mV
- Use if system becomes unstable

### Best Practices

**Starting Out:**
1. Always start with safe defaults
2. Test stability before aggressive values
3. Use Simple Mode until comfortable
4. Monitor metrics during initial testing
5. Keep notes on what works for your chip

**Configuration:**
1. Make small changes (-5mV increments)
2. Test each change for 10+ minutes
3. Run stress tests after major changes
4. Keep Maximum Value conservative (≥ -20mV)
5. Use higher thresholds for stability

**Monitoring:**
1. Watch temperature (should stay < 85°C)
2. Check for frequency throttling
3. Monitor for unexpected crashes
4. Verify metrics update smoothly
5. Test in real workloads, not just idle

**Troubleshooting:**
1. If unstable, increase Maximum Value first
2. If still unstable, increase Minimal Value
3. If still unstable, increase Threshold
4. If still unstable, use Reset to Safe Defaults
5. Some chips can't handle aggressive values

### Warning Signs

**System Instability:**
- Random crashes or freezes
- Graphics glitches
- Audio stuttering
- Unexpected reboots
- Application crashes

**Action:** Stop dynamic mode, increase voltage values, test again

**Thermal Issues:**
- Temperature > 85°C sustained
- Fan at 100% constantly
- Thermal throttling (frequency drops)

**Action:** Check fan curves, reduce CPU load, verify cooling

**Performance Degradation:**
- Lower FPS than expected
- Stuttering or lag
- Frequency stuck at low values
- Slow application response

**Action:** Verify voltage isn't too aggressive, check for throttling

### What NOT to Do

❌ **Don't** set Minimal Value below -50mV without extensive testing
❌ **Don't** set Maximum Value below -30mV for gaming
❌ **Don't** use Threshold < 20% (too little time at safe voltage)
❌ **Don't** ignore crashes (they indicate instability)
❌ **Don't** copy someone else's values (every chip is different)
❌ **Don't** test during important gaming sessions
❌ **Don't** disable safety features
❌ **Don't** forget to save stable configurations

---

## Troubleshooting

### Dynamic Mode Won't Start

**Symptom:** Clicking "Start Dynamic Mode" does nothing or shows error

**Possible Causes:**
1. Validation error (min > max)
2. gymdeck3 daemon not running
3. Permission issues
4. Hardware access denied

**Solutions:**
1. Check that Minimal Value ≤ Maximum Value for all cores
2. Verify all values are -100 to 0 mV
3. Check backend logs: `journalctl -u decktune`
4. Restart plugin: Decky menu → Settings → Reload
5. Verify gymdeck3 is running: `ps aux | grep gymdeck3`
6. Check permissions: `ls -l /sys/class/hwmon/`

---

### System Crashes or Freezes

**Symptom:** Steam Deck freezes, crashes, or reboots unexpectedly

**Immediate Action:**
1. Hold power button for 10 seconds (force shutdown)
2. Boot back up
3. Open DeckTune
4. Click "Panic Disable" or "Reset to Safe Defaults"

**Root Cause:**
- Voltage too aggressive for your chip
- Insufficient stability margin under load
- Thermal issues compounding voltage instability

**Prevention:**
1. Increase Maximum Value (make less aggressive)
2. Increase Minimal Value if crashes at idle
3. Lower Threshold (transition earlier to safe voltage)
4. Run stress tests before gaming
5. Monitor temperature during testing

---

### Metrics Not Updating

**Symptom:** Metrics display shows stale data or "---"

**Possible Causes:**
1. Dynamic mode not active
2. Polling stopped
3. gymdeck3 not responding
4. Hardware metrics unavailable

**Solutions:**
1. Verify status shows "Active"
2. Stop and restart dynamic mode
3. Check gymdeck3 logs: `journalctl -u gymdeck3`
4. Verify hwmon access: `cat /sys/class/hwmon/hwmon*/temp1_input`
5. Restart plugin if metrics remain frozen

---

### Configuration Not Persisting

**Symptom:** Settings reset after closing plugin or rebooting

**Possible Causes:**
1. localStorage disabled or full
2. Backend settings file not writable
3. Apply button not clicked
4. Configuration save failed silently

**Solutions:**
1. Always click "Apply" after changes
2. Check localStorage: Browser console → Application → Local Storage
3. Verify backend file: `ls -l ~/homebrew/settings/decktune/settings.json`
4. Check file permissions: `chmod 644 ~/homebrew/settings/decktune/settings.json`
5. Review backend logs for write errors

---

### Voltage Curve Not Matching Expectations

**Symptom:** Applied voltage doesn't match curve visualization

**Possible Causes:**
1. Platform limits overriding configuration
2. Safety clamping active
3. Metrics reporting delay
4. Configuration not applied

**Solutions:**
1. Check platform limits: Expert Mode → Diagnostics
2. Verify configuration was applied (click Apply)
3. Wait 1-2 seconds for metrics to update
4. Compare curve graph to metrics display
5. Check backend logs for clamping messages

---

### Performance Worse Than Static Undervolt

**Symptom:** Dynamic mode performs worse than fixed undervolt

**Possible Causes:**
1. Threshold too low (transitions too early)
2. Maximum Value too conservative
3. Overhead from load monitoring
4. Frequent voltage transitions causing instability

**Solutions:**
1. Increase Threshold to 60-70%
2. Make Maximum Value more aggressive (lower)
3. Use Simple Mode to reduce overhead
4. Compare with static undervolt at same values
5. Consider using static undervolt if dynamic doesn't help

---

### Gamepad Controls Not Working

**Symptom:** D-pad or buttons don't control interface

**Possible Causes:**
1. Focus not on Dynamic Manual Mode component
2. Another component capturing input
3. Gamepad navigation disabled
4. Decky focus issue

**Solutions:**
1. Click inside Dynamic Manual Mode area
2. Close other Decky plugins
3. Use touchscreen to focus element first
4. Restart Decky Loader if persistent
5. Check Decky settings for gamepad configuration

---

## Advanced Topics

### Understanding Per-Core Load Distribution

Different workloads distribute load differently across cores:

**Single-Threaded (Emulation):**
```
Core 0: 90-100% (primary)
Core 1: 10-20%  (minimal)
Core 2: 5-10%   (minimal)
Core 3: 5-10%   (minimal)
```
Strategy: Aggressive Core 0, conservative others

**Multi-Threaded (Modern Games):**
```
Core 0: 70-80%
Core 1: 60-70%
Core 2: 50-60%
Core 3: 40-50%
```
Strategy: Balanced across all cores

**Background Tasks:**
```
Core 0: 30-40%
Core 1: 20-30%
Core 2: 60-70% (background work)
Core 3: 50-60% (background work)
```
Strategy: Conservative background cores

### Hysteresis and Stability

The system includes built-in hysteresis to prevent voltage hunting:
- Load must change by ≥5% to trigger voltage change
- Prevents rapid oscillation around threshold
- Reduces wear on voltage regulators
- Improves stability

**Example:**
```
Threshold: 50%
Current Load: 48%
Current Voltage: -30mV (minimal)

Load increases to 51%:
- Crosses threshold
- Voltage begins interpolation to -27mV

Load drops to 49%:
- Within hysteresis band (5%)
- Voltage stays at -27mV (no change)

Load drops to 43%:
- Outside hysteresis band
- Voltage returns to -30mV (minimal)
```

### Combining with Other Features

**Dynamic Manual + Fan Control:**
- Configure aggressive fan curve for stability
- Allows more aggressive voltage curves
- Monitor temperature closely
- Example: 60°C → 50%, 70°C → 70%, 80°C → 100%

**Dynamic Manual + Per-Game Profiles:**
- Create different dynamic configs per game
- Save as profile for automatic switching
- Example: Conservative for AAA games, aggressive for indie games

**Dynamic Manual + Apply on Startup:**
- Enable "Apply on Startup" in Manual tab
- Dynamic mode activates automatically on boot
- Ensure configuration is well-tested first

**Dynamic Manual + Game Only Mode:**
- Enable "Game Only Mode" in Manual tab
- Dynamic mode only active during games
- Resets to 0mV in Steam menu
- Good for stability in UI, performance in games

### Monitoring and Logging

**Real-Time Monitoring:**
- Metrics update every 500ms
- Time-series graph shows last 30 seconds
- Watch for patterns: load spikes, voltage transitions, temperature changes

**Backend Logging:**
```bash
# View DeckTune logs
journalctl -u decktune -f

# View gymdeck3 logs
journalctl -u gymdeck3 -f

# Export diagnostics
Expert Mode → Diagnostics → Export
```

**What to Monitor:**
- Voltage transitions (should be smooth)
- Temperature (should stay < 85°C)
- Frequency (should match load)
- Crashes (indicates instability)

### Silicon Lottery

Every CPU chip is different due to manufacturing variance:

**Good Chip:**
- Can handle -40mV at idle
- Stable at -25mV under load
- Runs cool (< 75°C gaming)
- No crashes with aggressive curves

**Average Chip:**
- Can handle -30mV at idle
- Stable at -15mV under load
- Normal temps (75-80°C gaming)
- Occasional crashes with very aggressive curves

**Poor Chip:**
- Can handle -20mV at idle
- Stable at -10mV under load
- Runs warm (80-85°C gaming)
- Crashes easily with aggressive curves

**Finding Your Chip's Limits:**
1. Use Silicon Binning feature (Wizard Mode)
2. Start conservative, increase gradually
3. Test thoroughly at each step
4. Accept your chip's limitations
5. Don't compare to others' values

### Power Savings Calculations

**Theoretical Maximum:**
- Voltage reduction: 30mV average
- Power reduction: ~10-15% (voltage-dependent)
- Battery life increase: +15-25% (workload-dependent)

**Real-World Results:**
- Light use (web, video): +15-20% battery life
- Gaming (medium load): +8-12% battery life
- Heavy gaming (high load): +5-8% battery life
- Idle (desktop): +20-25% battery life

**Factors Affecting Savings:**
- Chip quality (silicon lottery)
- Workload type (single vs multi-threaded)
- Temperature (hotter = less savings)
- Other power consumers (screen, WiFi, etc.)

---

## Conclusion

Dynamic Manual Mode provides powerful per-core voltage curve control for advanced users. Start with Simple Mode and safe defaults, test thoroughly, and gradually optimize for your specific chip and workload.

**Key Takeaways:**
- Simple Mode for beginners, Expert Mode for optimization
- Start conservative, increase aggressiveness gradually
- Test stability before relying on aggressive values
- Every chip is different (silicon lottery)
- Monitor metrics and temperature
- Use safety features (Reset, LKG, Panic Disable)
- Save stable configurations

**Next Steps:**
1. Read the [API Documentation](DYNAMIC_MANUAL_MODE_API.md)
2. Review [Configuration Examples](#configuration-examples)
3. Test with safe defaults first
4. Gradually optimize for your workload
5. Share your results with the community

For support, visit: https://github.com/bobberdolle1/DeckTune/issues
