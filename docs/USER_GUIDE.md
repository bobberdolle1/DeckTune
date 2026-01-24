# DeckTune 3.1 User Guide

This guide covers all major features in DeckTune, including the new reliability and UX improvements in v3.1: Crash Recovery Metrics, Real-Time Telemetry, Platform Caching, Session History, Setup Wizard, and Streaming Status Updates.

## Table of Contents

1. [What's New in v3.2](#whats-new-in-v32)
2. [Dynamic Manual Mode](#dynamic-manual-mode)
3. [Setup Wizard](#setup-wizard)
4. [Real-Time Telemetry](#real-time-telemetry)
5. [Session History](#session-history)
6. [Crash Recovery Metrics](#crash-recovery-metrics)
7. [Context-Aware Profiles](#context-aware-profiles)
8. [Progressive Recovery](#progressive-recovery)
9. [BlackBox Recorder](#blackbox-recorder)
10. [Fan Control with Custom Curves](#fan-control-with-custom-curves)
11. [Acoustic Fan Profiles](#acoustic-fan-profiles)
12. [PWM Smoothing](#pwm-smoothing)
13. [Iron Seeker — Per-Core Curve Optimizer](#iron-seeker--per-core-curve-optimizer)
14. [Automated Silicon Binning](#automated-silicon-binning)
15. [Per-Game Profiles](#per-game-profiles)
16. [Benchmarking](#benchmarking)
17. [Best Practices](#best-practices)
18. [Troubleshooting](#troubleshooting)

---

## What's New in v3.2

DeckTune 3.2 introduces Dynamic Manual Mode with per-core voltage curve control:

- **Dynamic Manual Mode** — Configure custom voltage curves for each CPU core
- **Simple Mode** — Apply identical settings to all cores for quick configuration
- **Expert Mode** — Fine-tune each core individually for maximum optimization
- **Real-Time Visualization** — Live voltage curve graphs and metrics
- **Gamepad Navigation** — Full Steam Deck controller support
- **Safety Validation** — Multi-layer validation prevents dangerous configurations

**📖 For detailed Dynamic Manual Mode documentation, see [Dynamic Manual Mode Guide](DYNAMIC_MANUAL_MODE_GUIDE.md)**

---

## Dynamic Manual Mode

Dynamic Manual Mode provides granular per-core voltage curve control, allowing you to define custom voltage curves that automatically adjust based on CPU load.

### Quick Start

**For Beginners (Simple Mode):**
1. Open **Expert Mode** → **Dynamic Manual** tab
2. Enable **Simple Mode** toggle
3. Use safe defaults: **-30mV / -15mV / 50%**
4. Click **Apply** to save
5. Click **Start Dynamic Mode**
6. Monitor metrics for stability

**For Advanced Users (Expert Mode):**
1. Open **Expert Mode** → **Dynamic Manual** tab
2. Disable **Simple Mode** toggle
3. Select a core using tabs (Core 0-3)
4. Configure each core independently
5. Click **Apply** to save all
6. Click **Start Dynamic Mode**
7. Monitor per-core metrics

### Key Features

**Voltage Curves:**
- **Minimal Value** (-100 to 0 mV): Voltage at low CPU load
- **Maximum Value** (-100 to 0 mV): Voltage at high CPU load
- **Threshold** (0-100%): Load percentage where transition occurs

**Real-Time Monitoring:**
- Live voltage curve visualization
- Per-core metrics (load, voltage, frequency, temperature)
- Time-series graphs (last 30 seconds)
- Current operating point marker

**Safety Features:**
- Validation prevents dangerous configurations
- Platform limit enforcement
- Reset to Safe Defaults button
- Last Known Good configuration recovery
- Panic Disable for instant shutdown

### Configuration Examples

**Battery Saver:**
```
Minimal: -35mV  (aggressive at idle)
Maximum: -10mV  (safe under load)
Threshold: 40%  (early transition)
```

**Balanced:**
```
Minimal: -30mV  (moderate at idle)
Maximum: -15mV  (moderate under load)
Threshold: 50%  (balanced transition)
```

**Performance:**
```
Minimal: -25mV  (conservative at idle)
Maximum: -20mV  (aggressive under load)
Threshold: 60%  (late transition)
```

### Gamepad Controls

- **D-pad Up/Down**: Switch cores (Expert Mode)
- **D-pad Left/Right**: Navigate controls
- **L1/R1**: Adjust slider values
- **A Button**: Activate buttons
- **B Button**: Cancel/Back

### Documentation

For comprehensive documentation:
- **User Guide**: [Dynamic Manual Mode Guide](DYNAMIC_MANUAL_MODE_GUIDE.md)
- **API Reference**: [Dynamic Manual Mode API](DYNAMIC_MANUAL_MODE_API.md)
- **Configuration Examples**: See guide for detailed examples
- **Troubleshooting**: See guide for common issues

---

## What's New in v3.1

DeckTune 3.1 focuses on reliability improvements and UX enhancements:

- **Setup Wizard** — Guided first-run experience for new users
- **Real-Time Telemetry** — Live temperature and power graphs
- **Session History** — Track gaming sessions with performance metrics
- **Crash Recovery Metrics** — See how many times crash recovery saved your system
- **Faster Startup** — Platform detection caching eliminates delays
- **Streaming Updates** — Real-time status via server-sent events (no more polling)

---

## Setup Wizard

New users are greeted with a guided setup wizard that explains undervolting and helps choose the right settings.

### First-Run Experience

When you open DeckTune for the first time:

1. **Welcome Screen** — Introduction to DeckTune
2. **What is Undervolting?** — Simple explanation of benefits and risks
3. **Choose Your Goal** — Select from preset goals
4. **Confirmation** — Review and apply settings

### Goal Selection

| Goal | Battery Improvement | Temp Reduction | Best For |
|------|---------------------|----------------|----------|
| **Quiet/Cool** | +10-15% | -8-12°C | Silent operation, light tasks |
| **Balanced** | +15-20% | -5-8°C | General use, most games |
| **Max Battery** | +20-30% | -3-5°C | Long gaming sessions |
| **Max Performance** | +5-10% | -2-4°C | Competitive gaming |

### Skip or Cancel

You can skip or cancel the wizard at any step:
- **Skip** — Marks first-run as complete, uses default settings
- **Cancel** — Returns to main screen without changes

### Re-Running the Wizard

To run the wizard again:
1. Open **Expert Mode** → **Settings**
2. Click **"Run Setup Wizard"**

---

## Real-Time Telemetry

Monitor your system's temperature and power consumption with live graphs.

### Temperature Graph

- **Data**: CPU temperature in °C
- **Range**: Last 60 seconds
- **Update Rate**: 1 Hz (every second)
- **Hover**: Shows exact value and timestamp

### Power Graph

- **Data**: Power consumption in Watts
- **Range**: Last 60 seconds
- **Update Rate**: 1 Hz (every second)
- **Hover**: Shows exact value and timestamp

### Viewing Telemetry

1. Open **Expert Mode** → **Monitoring Tab**
2. Graphs update automatically when gymdeck3 is running
3. Hover over any point for details

### Data Storage

- **Buffer Size**: 300 samples (5 minutes)
- **Behavior**: Circular buffer (oldest samples discarded)
- **Persistence**: In-memory only (not saved to disk)

---

## Session History

Track your gaming sessions with detailed performance metrics.

### What Gets Tracked

Each session records:
- **Start/End Time** — When gymdeck3 started and stopped
- **Duration** — Total session length
- **Temperature** — Average, minimum, and maximum
- **Power** — Average consumption
- **Battery Savings** — Estimated Wh saved
- **Undervolt Values** — Settings used during session

### Viewing Session History

1. Open **Expert Mode** → **Sessions Tab**
2. See list of last 30 sessions
3. Click any session for detailed view

### Session Details

The detail view shows:
- **Temperature Graph** — Temperature over session duration
- **Power Graph** — Power consumption over time
- **Metrics Summary** — All calculated metrics
- **Undervolt Values** — Per-core values used

### Comparing Sessions

Compare any two sessions side-by-side:

1. Open **Sessions Tab**
2. Click **"Compare"** button
3. Select two sessions
4. View metric differences:
   - Duration difference
   - Temperature difference (avg, min, max)
   - Power difference
   - Battery savings difference

### Session Archival

- **Active Storage**: Last 100 sessions
- **Archive**: Older sessions moved to separate file
- **Diagnostics**: Session summary included in export

---

## Crash Recovery Metrics

See how many times DeckTune's crash recovery system has protected your system.

### Viewing Crash Metrics

1. Open **Expert Mode** → **Diagnostics Tab**
2. See **Crash Recovery** section:
   - **Total Count** — Number of crash recoveries
   - **Last Crash** — Date of most recent crash
   - **History** — Detailed crash records

### Crash Record Details

Each crash record contains:
- **Timestamp** — When the crash occurred
- **Crashed Values** — Undervolt values that caused the crash
- **Restored Values** — LKG values that were restored
- **Recovery Reason** — Why recovery was triggered (boot_recovery, watchdog_timeout, etc.)

### History Management

- **Limit**: 50 entries maximum
- **Behavior**: FIFO (oldest entries removed when full)
- **Export**: Included in diagnostics archive

---

## Context-Aware Profiles

DeckTune 3.0 introduces intelligent profile switching based on multiple conditions beyond just the running game.

### What are Context Conditions?

Context conditions allow profiles to activate based on:
- **Battery Level**: Activate when battery drops below a threshold (e.g., 30%)
- **Power Mode**: Activate only on AC power or battery power
- **Temperature**: Activate when CPU temperature exceeds a threshold

### Why Use Context-Aware Profiles?

Different situations require different settings:
- **On battery at 20%**: Use aggressive power saving
- **Plugged in**: Use performance-focused settings
- **High temperature**: Use conservative values for stability

### Creating Context-Aware Profiles

1. **Open Expert Mode** → **Presets Tab**
2. **Click "Create Profile"**
3. **Set context conditions:**
   - Battery threshold (0-100%)
   - Power mode (AC / Battery / Any)
   - Temperature threshold (optional)
4. **Configure undervolt values**
5. **Save the profile**

### Profile Priority

When multiple profiles match, DeckTune selects the most specific one:
1. **Most conditions** wins (3 conditions > 2 conditions > 1 condition)
2. **Ties** broken by creation timestamp (newer wins)
3. **Fallback chain**: Context match → App-only match → Global default

### Example Setup

```
Profile: "Cyberpunk - Battery Saver"
  AppID: 1091500
  Conditions:
    - Battery: ≤ 30%
    - Power Mode: Battery
  Cores: [-20, -20, -20, -20]

Profile: "Cyberpunk - Performance"
  AppID: 1091500
  Conditions:
    - Power Mode: AC
  Cores: [-30, -30, -30, -30]
```

When playing Cyberpunk:
- On AC power → "Performance" profile activates
- On battery at 25% → "Battery Saver" profile activates
- On battery at 50% → Falls back to app-only or global default

---

## Progressive Recovery

DeckTune 3.0 includes a smarter recovery system that tries to preserve some power savings even after detecting instability.

### How It Works

1. **Instability detected** (missed heartbeats)
2. **First attempt**: Reduce all undervolt values by 5mV
3. **Wait** for 2 heartbeat cycles (~10 seconds)
4. **If stable**: Update LKG to reduced values, continue
5. **If still unstable**: Full rollback to original LKG values

### Benefits

- **Preserves optimization**: You keep some undervolt benefit
- **Automatic recovery**: No manual intervention needed
- **Safe fallback**: Full rollback if reduction doesn't help
- **LKG update**: Successful recovery updates your safe baseline

### Monitoring Recovery

Recovery events are shown in the UI:
- "Progressive recovery started" — reduction applied
- "Progressive recovery success" — stability confirmed
- "Progressive recovery failed" — full rollback performed

---

## BlackBox Recorder

The BlackBox continuously records system metrics, allowing post-mortem analysis after crashes or instability.

### What Gets Recorded

Every 500ms, the BlackBox captures:
- **Timestamp**
- **CPU Temperature** (°C)
- **CPU Load** (%)
- **Undervolt Values** (all 4 cores)
- **Fan Speed** (RPM)
- **Fan PWM** (0-255)

### Ring Buffer

- **Duration**: Last 30 seconds
- **Capacity**: 60 samples
- **Behavior**: FIFO (oldest samples discarded when full)

### Viewing Recordings

1. **Open Expert Mode** → **Diagnostics Tab**
2. **Click "BlackBox Recordings"**
3. **Select a recording** to view details
4. **Analyze** temperature spikes, load patterns, etc.

### Recording Format

```json
{
  "timestamp": "2026-01-16T12:30:45Z",
  "reason": "watchdog_timeout",
  "duration_sec": 30,
  "samples": [
    {
      "timestamp": 1737030615.0,
      "temperature_c": 75,
      "cpu_load_percent": 85.5,
      "undervolt_values": [-30, -30, -30, -30],
      "fan_speed_rpm": 4200,
      "fan_pwm": 180
    }
  ]
}
```

---

## Fan Control with Custom Curves

DeckTune now includes comprehensive fan control with customizable fan curves, allowing you to fine-tune cooling behavior for your specific needs.

### What is Fan Control?

Fan control lets you define custom temperature-to-speed mappings (fan curves) that determine how fast the fan spins at different temperatures. This gives you precise control over the balance between cooling performance and noise levels.

### Key Features

- **Custom Fan Curves**: Define 3-10 temperature/speed points
- **Linear Interpolation**: Smooth speed transitions between points
- **Three Presets**: Stock, Silent, and Turbo curves
- **Safety Overrides**: Automatic 100% fan speed at critical temperatures (≥95°C)
- **Persistent Configuration**: Curves saved and restored across reboots
- **Real-Time Monitoring**: View current temperature, fan speed, and target speed

### Accessing Fan Control

1. **Open DeckTune** from the Decky menu
2. **Switch to Expert Mode**
3. **Navigate to Admin Panel** (button in top-right)
4. **Click "Fan Control"** button

### Using Preset Curves

#### Stock Preset (Balanced)
```
40°C → 0%   (Zero RPM)
60°C → 40%
75°C → 70%
85°C → 100%
```
Best for: General use, balanced cooling and noise

#### Silent Preset (Quiet)
```
50°C → 0%   (Zero RPM)
70°C → 30%
85°C → 60%
95°C → 100%
```
Best for: Quiet environments, light tasks, prioritizing low noise

#### Turbo Preset (Aggressive)
```
30°C → 20%  (Always spinning)
50°C → 60%
65°C → 80%
80°C → 100%
```
Best for: Heavy gaming, benchmarking, maximum cooling

### Applying a Preset

1. **Open Fan Control** menu
2. **Click one of the preset buttons**: Stock, Silent, or Turbo
3. **Preset applies immediately**
4. **Monitor status** to verify fan behavior

### Creating Custom Curves

1. **Click "Edit Curve"** button
2. **Add points** by clicking on the graph
3. **Drag points** to adjust temperature/speed
4. **Remove points** by double-clicking them
5. **Save** when satisfied

#### Custom Curve Rules

- **Minimum 3 points** required
- **Maximum 10 points** allowed
- **Temperature range**: 0-120°C
- **Speed range**: 0-100%
- **Automatic sorting**: Points sorted by temperature

#### Example Custom Curve

For quiet operation with good cooling:
```
45°C → 0%   (Zero RPM threshold)
60°C → 35%  (Gentle ramp-up)
70°C → 55%  (Moderate cooling)
80°C → 80%  (Strong cooling)
90°C → 100% (Maximum cooling)
```

### Safety Features

#### Critical Temperature Override
- **≥95°C**: Fan forced to 100% regardless of curve
- **≥90°C**: Minimum 80% fan speed enforced
- **Cannot be disabled**: Safety always active

#### Zero RPM Safety
- **0% speed only allowed** when temperature ≤ minimum curve point
- **Prevents overheating** from fan stopping at high temps
- **Automatic enforcement**: No configuration needed

### Monitoring Fan Status

The status display shows:
- **Current Temperature**: Real-time CPU/GPU temperature
- **Current Speed**: Actual fan speed percentage
- **Target Speed**: Calculated speed from active curve
- **Active Curve**: Name of current preset or "Custom"
- **Monitoring Status**: Whether automatic control is active

### Configuration Persistence

Fan curves are saved to:
```
~/.config/decktune/fan_control.json
```

This includes:
- Active curve (preset or custom)
- All custom curves
- Last applied settings
- Configuration version

### Tips for Custom Curves

✅ **DO:**
- Start with a preset and modify it
- Test curves during actual gaming
- Monitor temperatures during heavy load
- Keep at least one point below 50°C
- Use gradual speed increases for quieter operation

❌ **DON'T:**
- Set 0% speed above 50°C (overheating risk)
- Use too few points (< 3)
- Create extreme jumps between points
- Disable safety overrides (not possible anyway)
- Forget to test under load

### Troubleshooting Fan Control

**Fan not responding to curve:**
- Check that monitoring is active
- Verify hwmon interface is available
- Look for permission errors in Diagnostics
- Restart the plugin

**Fan speed incorrect:**
- Safety override may be active (check temperature)
- Curve points may need adjustment
- Check for conflicting fan control software
- Verify PWM interface is accessible

**Configuration not persisting:**
- Check file permissions on config directory
- Verify disk space available
- Look for write errors in Diagnostics
- Try manually saving curve again

**Hardware interface unavailable:**
- hwmon interface may not be detected
- Check `/sys/class/hwmon/` exists
- Verify kernel modules loaded
- May not be supported on all devices

---

## Acoustic Fan Profiles

DeckTune 3.0 adds preset fan profiles optimized for different priorities.

### Available Profiles

| Profile | Description | Best For |
|---------|-------------|----------|
| **Silent** | Max 60% (~3000 RPM) until 85°C | Quiet environments, light tasks |
| **Balanced** | Linear 30-70°C → 30-90% | General use, gaming |
| **Max Cooling** | 100% at 60°C+ | Heavy gaming, benchmarking |
| **Custom** | Your own curve | Specific preferences |

### Silent Profile Curve

```
40°C → 0%   (Zero RPM if enabled)
60°C → 20%
75°C → 40%
85°C → 60%  (Max before safety override)
90°C → 100% (Safety override)
```

### Balanced Profile Curve

```
30°C → 30%  (~1500 RPM)
50°C → 50%
70°C → 90%  (~4500 RPM)
80°C → 100%
```

### Max Cooling Profile Curve

```
40°C → 50%
60°C → 100% (Max RPM)
```

### Selecting a Profile

1. **Open Expert Mode** → **Fan Control Tab**
2. **Enable Fan Control**
3. **Select Acoustic Profile** from dropdown
4. **Profile applies immediately**

### Safety Override

Regardless of selected profile:
- **90°C+**: Forces 100% fan speed
- **85°C+**: Enforces minimum 80% fan speed

---

## PWM Smoothing

PWM Smoothing eliminates annoying sudden fan speed changes by gradually transitioning between speeds.

### How It Works

Instead of jumping from 30% to 70% instantly:
1. **Target set** to 70%
2. **Interpolation** over 2 seconds (default)
3. **Gradual increase** at ~1000 RPM/second
4. **Smooth transition** without audible jumps

### Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Ramp Time | 2.0s | 0.5-5.0s | Time to reach target |
| Increase Rate | ~1000 RPM/s | - | Calculated from ramp time |
| Decrease Rate | ~500 RPM/s | - | 50% of increase rate |

### Asymmetric Rates

Fan speed **decreases slower** than it increases:
- **Increase**: Full ramp rate (e.g., 1000 RPM/s)
- **Decrease**: Half ramp rate (e.g., 500 RPM/s)

This prevents thermal spikes when load drops temporarily.

### Emergency Bypass

When temperature reaches **90°C+**:
- Smoothing is **bypassed**
- Fan immediately set to **100%**
- Safety takes priority over comfort

---

## Iron Seeker — Per-Core Curve Optimizer

Iron Seeker is an advanced algorithm for automatically discovering optimal undervolt values for each CPU core individually. Unlike standard binning which applies the same value to all cores, Iron Seeker accounts for the "silicon lottery" — the varying quality of silicon in each core.

### Why Per-Core Tuning?

Every CPU core is unique:
- **Strong cores** can handle deep undervolt (-40mV and below)
- **Weak cores** require conservative values (-15mV)
- **Standard binning** is limited by the weakest core

Iron Seeker allows you to:
- **Maximize performance** from strong cores
- **Maintain stability** despite weak cores
- **See quality ratings** for each core (Gold/Silver/Bronze)
- **Automatically recover** from crashes

### How Iron Seeker Works

1. **Tests each core separately** (0, 1, 2, 3)
2. **Uses Vdroop testing** — pulsating load pattern (100ms load / 100ms idle)
3. **Steps down** from 0mV with configured step size until failure or limit
4. **Saves state** before each test for crash recovery
5. **Classifies quality** of each core

### Vdroop Testing

Unlike constant load testing, Vdroop creates a pulsating load pattern:
- **100ms** — maximum load (AVX2 workload)
- **100ms** — idle
- **Repeats** throughout the test duration

This reveals instability during transient load conditions that standard stress tests miss.

### Quality Tiers

| Tier | Range | Description |
|------|-------|-------------|
| 🥇 Gold | ≤ -35mV | Excellent silicon quality |
| 🥈 Silver | -34 to -20mV | Average quality |
| 🥉 Bronze | > -20mV | Requires conservative values |

### How to Use

1. **Open DeckTune** → Expert Mode → Tests

2. **Click "Start Iron Seeker"**
   - Close all games and heavy applications
   - Connect charger
   - Process takes 10-30 minutes

3. **Monitor progress:**
   - Current core and value being tested
   - ETA to completion
   - Results for already-tested cores

4. **Review results:**
   ```
   Core 0: -35mV (Gold 🥇)
   Core 1: -40mV (Gold 🥇)
   Core 2: -25mV (Silver 🥈)
   Core 3: -20mV (Bronze 🥉)
   ```

5. **Save as preset** for future use

### Configuration Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Step Size | 1-20mV | 5mV | Increment between iterations |
| Test Duration | 10-300s | 60s | Duration of each test |
| Safety Margin | 0-20mV | 5mV | Buffer added to discovered values |
| Vdroop Pulse | 50-500ms | 100ms | Load pulse duration |

### Crash Recovery

Iron Seeker has built-in crash protection:

1. **Before each test** state is saved to disk
2. **On reboot** DeckTune detects incomplete test
3. **Automatically restores** last stable values
4. **Records failed value** as unstable
5. **Continues testing** from next value or core

### Preset Integration

After Iron Seeker completes, you can:
- **Save results** as a new preset
- **Include per-core values** in game profiles
- **Export** for use on another device

Iron Seeker presets contain:
- Per-core values [V0, V1, V2, V3]
- Quality tiers for each core
- Discovery timestamp
- Max stable and recommended values

### Tips for Best Results

- **Run on a cool device** — results will be more accurate
- **Don't interrupt tests** unnecessarily — use Cancel button
- **Test results** in real games before permanent use
- **Re-run every 6-12 months** — chip characteristics may change

---

## Automated Silicon Binning

Silicon Binning automatically discovers your chip's maximum stable undervolt value through iterative testing with built-in crash recovery.

### What is Silicon Binning?

Every CPU chip is slightly different due to manufacturing variations. Silicon binning finds the exact limit for YOUR specific chip, rather than using conservative generic values. This can result in:

- **Better battery life** (5-15% improvement)
- **Lower temperatures** (3-8°C reduction)
- **Quieter operation** (reduced fan noise)
- **Optimal settings** tailored to your hardware

### How to Use Silicon Binning

#### Basic Usage (Wizard Mode)

1. **Open DeckTune** from the Decky menu (Quick Access → DeckTune)

2. **Switch to Wizard Mode** if not already there (toggle at top)

3. **Click "Find Max Undervolt"** button
   - The button is located after the goal selection
   - Make sure no games are running for best results

4. **Wait for completion** (typically 5-15 minutes)
   - Progress bar shows current iteration
   - Current test value and last stable value are displayed
   - ETA updates in real-time
   - You can cancel anytime with the "Stop" button

5. **Review results**
   - **Max Stable**: The lowest value that passed all tests
   - **Recommended**: Max stable + 5mV safety margin
   - **Iterations**: Number of tests performed
   - **Duration**: Total time taken

6. **Apply settings**
   - Click "Apply Recommended" to use the safe value
   - Or manually adjust if you want to be more/less conservative

#### Advanced Configuration

For experienced users who want to customize the binning process:

1. **Click "Advanced Settings"** in the binning dialog

2. **Configure parameters:**
   - **Test Duration**: 30-300 seconds per iteration
     - Shorter = faster but less thorough
     - Longer = more reliable but slower
     - Default: 60 seconds (recommended)
   
   - **Step Size**: 1-10mV increments
     - Smaller = more precise but slower
     - Larger = faster but less precise
     - Default: 5mV (good balance)
   
   - **Start Value**: 0 to -20mV starting point
     - Start higher if you know your chip is weak
     - Start lower for more aggressive testing
     - Default: -10mV (safe starting point)

3. **Save settings** and run binning with custom parameters

### Understanding the Process

**What happens during binning:**

1. **Iteration 1**: Tests -10mV (start value)
   - Applies undervolt to all cores
   - Runs 60-second stress test (CPU + memory)
   - If pass: marks as stable, continues
   - If fail: stops and recommends previous value

2. **Iteration 2**: Tests -15mV (start - step)
   - Same process as iteration 1
   - State saved before test for crash recovery

3. **Continues** until failure or platform limit reached

4. **Completion**: Returns max stable value + recommendation

**Crash Recovery:**

If your system crashes during a test:
- State file persists the last stable value
- On next boot, DeckTune detects the crash
- Automatically restores the last stable value
- Shows notification with failed test value
- You can review results and decide next steps

### Safety Features

- **State Persistence**: Every test value is saved before application
- **Boot Recovery**: Automatic detection and recovery from crashes
- **Platform Limits**: Never exceeds safe limits for your model
- **Iteration Limit**: Maximum 20 attempts to prevent infinite loops
- **Consecutive Failures**: Aborts after 3 consecutive failures
- **Instant Cancellation**: Stop button immediately restores previous values

### Tips for Best Results

✅ **DO:**
- Close all games and heavy applications
- Let the full test duration complete
- Use default settings for first run
- Run when system is cool (not after gaming)
- Keep Steam Deck plugged in

❌ **DON'T:**
- Interrupt tests manually (use Stop button instead)
- Run while gaming or streaming
- Use very short test durations (< 30s)
- Start too aggressively (< -15mV)
- Run immediately after heavy load

### When to Re-run Binning

Consider re-running binning if:
- You've updated SteamOS
- Ambient temperature has changed significantly
- You're experiencing instability with current values
- You want to verify results after hardware changes
- Several months have passed (chip aging)

---

## Per-Game Profiles

Automatically switch undervolt settings based on the currently running Steam game.

### Why Use Per-Game Profiles?

Different games have different power requirements:

- **Light games** (indie, 2D): Can use aggressive undervolt for max battery
- **Heavy games** (AAA, 3D): May need conservative values for stability
- **Competitive games**: Prioritize performance over efficiency
- **Story games**: Prioritize battery life and quiet operation

Per-game profiles let you optimize for each scenario automatically.

### Creating Your First Profile

#### Method 1: Quick-Create (Recommended)

1. **Launch a game** you want to create a profile for

2. **Tune settings** while the game is running
   - Adjust undervolt values in Expert Mode
   - Enable/disable dynamic mode as desired
   - Test stability with the game running

3. **Open Expert Mode** → **Presets Tab**

4. **Click "Save as Profile for [Game Name]"**
   - Button appears automatically when game is detected
   - Game name and AppID are auto-populated
   - Current settings are captured

5. **Confirm** and the profile is saved
   - Profile automatically applies next time you launch this game

#### Method 2: Manual Creation

1. **Open Expert Mode** → **Presets Tab**

2. **Click "Create Profile"** button

3. **Fill in details:**
   - **AppID**: Steam's game identifier (find in Steam properties)
   - **Name**: Friendly name for the profile
   - **Cores**: Undervolt values for each core
   - **Dynamic Mode**: Enable/disable and configure

4. **Save** the profile

### Managing Profiles

#### Viewing Profiles

In Expert Mode → Presets Tab, you'll see:
- **Profile List**: All saved profiles
- **Game Name**: Friendly name
- **AppID**: Steam identifier
- **Settings**: Core values and dynamic mode status
- **Active Indicator**: Shows which profile is currently applied

#### Editing Profiles

1. **Click "Edit"** next to any profile
2. **Modify settings** as needed
3. **Save changes**
4. If that game is currently running, changes apply immediately

#### Deleting Profiles

1. **Click "Delete"** next to any profile
2. **Confirm deletion**
3. If that game is currently running, reverts to global default

### Global Default Profile

The global default is used when:
- No game is running
- A game is running but has no specific profile
- A profile is deleted while that game is active

**To set global default:**
1. Configure desired settings in Manual tab
2. These become the fallback for all games

### Import/Export Profiles

#### Exporting Profiles

Share your profiles with others or backup your settings:

1. **Open Expert Mode** → **Presets Tab**
2. **Click "Export All"** button
3. **File is saved** to `~/decktune_profiles_export.json`
4. **Share or backup** this file

#### Importing Profiles

Import profiles from other users or restore from backup:

1. **Open Expert Mode** → **Presets Tab**
2. **Click "Import"** button
3. **Select JSON file** to import
4. **Review preview** showing:
   - Profiles to be imported
   - Conflicts with existing profiles
   - Recommended actions

5. **Choose merge strategy:**
   - **Skip**: Keep existing, ignore imports with same AppID
   - **Overwrite**: Replace existing with imported
   - **Rename**: Import with modified name (AppID_imported)

6. **Confirm import**

### How Automatic Switching Works

**Detection Process:**

1. **AppWatcher monitors** Steam every 2 seconds
2. **Detects game launch** via:
   - Steam appmanifest files (`~/.steam/steam/steamapps/`)
   - Process scanning (`/proc` for `-applaunch` argument)

3. **Debouncing** waits 5 seconds to prevent rapid switching

4. **Profile lookup** searches for matching AppID

5. **Application** applies profile settings:
   - Undervolt values via ryzenadj
   - Dynamic mode start/stop if needed
   - Event emitted to UI

6. **Notification** shows active profile name

**Switching Speed:**
- Profile detection: < 2 seconds
- Debouncing delay: 5 seconds
- Application time: < 500ms
- Total: ~7-8 seconds from game launch

### Profile Best Practices

✅ **DO:**
- Create profiles for your most-played games first
- Test stability with each game before saving
- Use descriptive names for easy identification
- Export profiles regularly as backup
- Share successful profiles with the community

❌ **DON'T:**
- Create profiles for every game immediately
- Use untested aggressive values
- Forget to update profiles after SteamOS updates
- Delete profiles without testing global default first

### Troubleshooting Profiles

**Profile not switching automatically:**
- Check that AppWatcher is running (should be automatic)
- Verify game is launched through Steam (not external)
- Check AppID matches (view in Steam properties)
- Look for errors in Diagnostics tab

**Game crashes with profile:**
- Profile values may be too aggressive for that game
- Edit profile to use more conservative values
- Test with global default first
- Consider running binning specifically for that game

**Profile conflicts after import:**
- Review conflict resolution options
- Choose appropriate merge strategy
- Manually edit conflicting profiles if needed

---

## Benchmarking

Quick performance testing to measure the impact of your undervolt settings.

### Why Benchmark?

Benchmarking helps you:
- **Verify improvements** from undervolt settings
- **Compare different configurations** objectively
- **Detect performance regressions** from aggressive values
- **Optimize** for your specific workload
- **Track changes** over time

### Running a Benchmark

#### Basic Usage

1. **Open DeckTune** (Wizard or Expert Mode)

2. **Click "Run Benchmark"** button
   - Available in both modes
   - Located in Manual tab (Expert) or main screen (Wizard)

3. **Wait 10 seconds** for completion
   - Progress bar shows remaining time
   - All tuning controls are disabled during test
   - Don't interact with system during benchmark

4. **View results:**
   - **Score**: Operations per second (bogo ops/s)
   - **Duration**: Actual test time (should be ~10s)
   - **Cores Used**: Undervolt values during test
   - **Comparison**: Difference from previous run (if available)

#### Comparing Configurations

**Before/After Testing:**

1. **Run baseline benchmark** with current settings
   - Note the score (e.g., 123,456 ops/s)

2. **Adjust undervolt values**
   - Make your changes in Manual tab

3. **Run benchmark again**
   - New score is compared to baseline
   - Shows percentage improvement/degradation

4. **Interpret results:**
   - **Positive %**: Performance improved (good!)
   - **Negative %**: Performance degraded (values too aggressive)
   - **~0%**: No significant change (undervolt not affecting performance)

**Example:**
```
Baseline: 123,456 ops/s (cores: 0, 0, 0, 0)
After:    125,789 ops/s (cores: -25, -25, -25, -25)
Change:   +2,333 ops/s (+1.89%)
```

### Benchmark History

View past benchmark results:

1. **Open Expert Mode** → **Manual Tab**
2. **Click "View History"** (if available)
3. **See last 20 results:**
   - Timestamp
   - Score
   - Cores used
   - Comparison with previous

4. **Compare any two results:**
   - Select two entries
   - View detailed comparison

### Understanding Benchmark Scores

**What the score means:**
- **Higher is better**: More operations per second
- **Typical range**: 100,000 - 150,000 ops/s
- **Variance**: ±2-3% is normal between runs
- **Significant change**: > 5% indicates real difference

**Factors affecting score:**
- **Undervolt values**: More aggressive = potentially higher score
- **Temperature**: Cooler = better performance
- **Background processes**: Close apps for consistent results
- **Power mode**: Performance mode vs battery saver
- **Dynamic mode**: Disabled for consistent benchmarking

### Benchmark Best Practices

✅ **DO:**
- Close all games and applications
- Run multiple times for average
- Wait for system to cool between runs
- Use same conditions for comparisons
- Disable dynamic mode during benchmarking
- Keep Steam Deck plugged in

❌ **DON'T:**
- Run while gaming or streaming
- Compare results from different temperatures
- Expect huge improvements (1-3% is good)
- Use benchmark as stability test (use stress tests instead)
- Run immediately after heavy load

### Interpreting Results

**Performance improved (+%):**
- Undervolt is working well
- System is more efficient
- Consider this configuration successful

**Performance degraded (−%):**
- Values may be too aggressive
- System is throttling or unstable
- Reduce undervolt values
- Run stability tests

**No change (~0%):**
- Undervolt not affecting this workload
- May still improve battery/temps
- Consider running game-specific tests

### When to Benchmark

**Good times to benchmark:**
- After changing undervolt values
- After creating new profiles
- After SteamOS updates
- When troubleshooting performance
- Before and after binning

**Not necessary to benchmark:**
- Every time you play a game
- Multiple times per day
- When settings haven't changed
- During normal usage

---

## Best Practices

### General Recommendations

1. **Start Conservative**
   - Begin with -15 to -20mV
   - Test stability thoroughly
   - Gradually increase if stable

2. **Use Binning First**
   - Let automated binning find your limits
   - Use recommended value as starting point
   - Fine-tune per-game from there

3. **Create Profiles Gradually**
   - Start with most-played games
   - Test each profile thoroughly
   - Expand to other games over time

4. **Benchmark Regularly**
   - Before and after major changes
   - After SteamOS updates
   - When troubleshooting issues

5. **Monitor Stability**
   - Watch for crashes or freezes
   - Check system logs in Diagnostics
   - Reduce values if instability occurs

### Optimal Workflow

**For New Users:**

1. Run automated binning (Wizard Mode)
2. Apply recommended value globally
3. Test with various games for a week
4. Create profiles for games that need adjustment
5. Benchmark to verify improvements

**For Experienced Users:**

1. Run binning with custom parameters
2. Create profiles for all main games
3. Fine-tune each profile with benchmarking
4. Export profiles as backup
5. Share successful configurations

### Safety Reminders

- **Panic Disable** button is always available
- **Boot recovery** protects against crashes
- **Platform limits** prevent dangerous values
- **Watchdog** monitors for freezes
- **LKG values** provide fallback

---

## Troubleshooting

### Context-Aware Profile Issues

**Profile not switching on battery change:**
- Check that battery threshold is set correctly
- Verify context monitoring is active (check Diagnostics)
- Ensure profile conditions match current context

**Wrong profile selected:**
- Review profile specificity (more conditions = higher priority)
- Check for conflicting profiles with same conditions
- Verify AppID matches the running game

**Context not detected:**
- Battery level read from `/sys/class/power_supply/`
- Power mode detected from power supply status
- Check system permissions for sysfs access

### Progressive Recovery Issues

**Recovery not triggering:**
- Verify watchdog is active
- Check heartbeat interval settings
- Review Diagnostics for watchdog status

**Recovery always escalates to full rollback:**
- Your undervolt values may be too aggressive
- Consider running binning again with longer test duration
- Check for other system instability sources

**LKG not updating after recovery:**
- Recovery must complete 2 heartbeat cycles
- Check for interruptions during recovery
- Verify LKG file permissions

### BlackBox Issues

**No recordings available:**
- BlackBox only saves on crash/instability detection
- Check storage path permissions (`/tmp/decktune_blackbox/`)
- Verify dynamic mode was active during the event

**Recordings missing data:**
- All fields are required for valid samples
- Check for disk space issues
- Review sample interval (500ms default)

**Old recordings not visible:**
- Only last 5 recordings are kept
- Older recordings are automatically deleted
- Export important recordings before they're overwritten

### Acoustic Profile Issues

**Fan not following profile curve:**
- Check that fan control is enabled
- Verify acoustic profile is selected (not "Default")
- Safety override may be active (check temperature)

**Fan too loud on Silent profile:**
- Temperature may be above 85°C (safety override)
- Check for background processes causing load
- Consider improving ventilation

**Fan stops unexpectedly:**
- Zero RPM mode may be enabled
- Check temperature is below 45°C
- Disable Zero RPM if unwanted

### PWM Smoothing Issues

**Fan changes still feel abrupt:**
- Increase ramp time (try 3-4 seconds)
- Check that smoothing is enabled
- Emergency bypass may be triggering (90°C+)

**Fan response too slow:**
- Decrease ramp time (try 1 second)
- Check for temperature spikes
- Consider using Max Cooling profile for heavy loads

**Asymmetric rates not working:**
- Verify decrease rate is 50% of increase rate
- Check smoother configuration
- Review fan controller logs

### Binning Issues

**Binning takes too long:**
- Reduce test duration (but not below 30s)
- Increase step size (but not above 10mV)
- Start at a higher value (less aggressive)

**Binning finds no stable value:**
- Your chip may not support undervolt
- Try starting at 0mV and working down slowly
- Check platform limits aren't too restrictive
- Verify stress test tools are installed

**System crashes during binning:**
- This is expected and safe
- Boot recovery will restore last stable value
- Review failed value and adjust start point
- Consider longer test duration

### Iron Seeker Issues

**Iron Seeker hangs on one core:**
- Increase test_duration for more reliable testing
- Decrease step_size for more precise search
- Check if system is overheating
- Try restarting — state will recover automatically

**Iron Seeker shows all cores as Bronze:**
- Your chip may have lower silicon quality
- This is normal — not all chips support deep undervolt
- Use discovered values anyway — they're still optimal for your chip

**Iron Seeker doesn't recover after crash:**
- Check file `/tmp/decktune_iron_seeker_state.json`
- Restart the plugin
- If problem persists, delete state file and start fresh

**Vdroop test fails immediately:**
- stress-ng may not be installed
- Check Diagnostics for error messages
- Verify system has enough resources

### Profile Issues

**Profiles not switching:**
- Verify game launched through Steam
- Check AppID in profile matches game
- Look for errors in Diagnostics tab
- Restart AppWatcher (plugin reload)

**Game crashes with profile:**
- Profile values too aggressive for that game
- Edit profile to more conservative values
- Test with global default first
- Run binning specifically for that game

**Import fails:**
- Verify JSON file format is correct
- Check for syntax errors in file
- Try importing one profile at a time
- Review error message in Diagnostics

### Benchmark Issues

**Benchmark fails to run:**
- Verify stress-ng is installed
- Check for other operations running
- Look for errors in Diagnostics
- Try running manually from terminal

**Inconsistent results:**
- Close all background applications
- Wait for system to cool
- Run multiple times and average
- Disable dynamic mode during testing

**Score lower than expected:**
- Check temperature (thermal throttling)
- Verify no background processes
- Ensure power mode is performance
- Compare with similar configurations

### Getting Help

If you encounter issues:

1. **Check Diagnostics Tab**
   - View recent logs
   - Look for error messages
   - Export diagnostics for sharing

2. **Review Settings**
   - Verify configuration is correct
   - Check platform detection
   - Confirm limits are appropriate

3. **Test with Defaults**
   - Reset to 0mV (Panic Disable)
   - Test with global default
   - Isolate the problematic setting

4. **Community Support**
   - Share diagnostics export
   - Describe steps to reproduce
   - Include system information
   - Check existing issues on GitHub

---

## Conclusion

DeckTune 3.0's automation features make CPU tuning accessible and safe:

- **Silicon Binning** finds optimal values automatically
- **Per-Game Profiles** adapt to your workload
- **Benchmarking** provides objective measurements

Start with binning, create profiles for your favorite games, and use benchmarking to verify improvements. The safety systems ensure your Steam Deck stays stable throughout the process.

Happy tuning! 🎮⚡
