# DeckTune 3.0 User Guide

This guide covers the three major automation features introduced in DeckTune 3.0: Automated Silicon Binning, Per-Game Profiles, and Benchmarking.

## Table of Contents

1. [Automated Silicon Binning](#automated-silicon-binning)
2. [Per-Game Profiles](#per-game-profiles)
3. [Benchmarking](#benchmarking)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)

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
