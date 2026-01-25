# Frequency-Based Voltage Wizard Guide

## Table of Contents

1. [Introduction](#introduction)
2. [What is Frequency-Based Mode?](#what-is-frequency-based-mode)
3. [When to Use Frequency-Based vs Load-Based Mode](#when-to-use-frequency-based-vs-load-based-mode)
4. [Getting Started](#getting-started)
5. [Step-by-Step Wizard Walkthrough](#step-by-step-wizard-walkthrough)
6. [Configuration Recommendations](#configuration-recommendations)
7. [Understanding Your Results](#understanding-your-results)
8. [Safety Guidelines](#safety-guidelines)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

The Frequency-Based Voltage Wizard is an advanced power optimization feature in DeckTune that creates custom voltage curves based on your CPU's operating frequency. This guide will help you understand, configure, and use this powerful tool to maximize your Steam Deck's battery life and performance.

**⚠️ Important:** This feature requires root access and involves undervolting your CPU. While designed with safety features, improper use can cause system instability. Always follow the safety guidelines in this document.

---

## What is Frequency-Based Mode?

### Overview

Frequency-based mode adjusts your CPU voltage based on the current operating frequency (speed) of your processor, rather than CPU load percentage. This provides more precise voltage control because:

- **Frequency is directly related to power consumption**: Higher frequencies require more voltage for stability
- **More predictable behavior**: Frequency changes are discrete and measurable
- **Better efficiency**: Each frequency point can be individually optimized

### How It Works

1. **Curve Generation**: The wizard tests your CPU at different frequencies (e.g., 400 MHz, 500 MHz, 600 MHz, etc.)
2. **Voltage Optimization**: For each frequency, it finds the lowest stable voltage through automated testing
3. **Real-Time Application**: During normal use, the system monitors CPU frequency and applies the optimal voltage from your curve
4. **Interpolation**: For frequencies between tested points, voltage is calculated using linear interpolation

### Technical Details

- **Frequency Range**: Typically 400 MHz to 3500 MHz on Steam Deck
- **Voltage Range**: -100 mV to 0 mV (negative values = undervolt)
- **Update Rate**: Voltage adjusts within 50ms of frequency changes
- **Safety Margin**: Additional voltage headroom (default 5 mV) ensures stability

---

## When to Use Frequency-Based vs Load-Based Mode

### Use Frequency-Based Mode When:

✅ **You want maximum battery life**
- Frequency-based mode can achieve 5-15% better battery life than load-based mode
- More precise voltage control means less wasted power

✅ **You play games with variable performance demands**
- Games that alternate between intense and light scenes
- Open-world games with varying complexity
- Strategy games with turn-based gameplay

✅ **You want consistent performance**
- Frequency-based mode provides more predictable behavior
- Less voltage fluctuation means more stable frame times

✅ **You're willing to invest time in optimization**
- Initial wizard run takes 10-30 minutes
- Results are saved and reused automatically

### Use Load-Based Mode When:

✅ **You want quick setup**
- Load-based mode works immediately without calibration
- Good for testing or temporary configurations

✅ **You frequently change hardware or BIOS settings**
- Frequency curves need regeneration after hardware changes
- Load-based mode adapts automatically

✅ **You prefer simpler configuration**
- Fewer parameters to understand
- More straightforward troubleshooting

### Comparison Table

| Feature | Frequency-Based | Load-Based |
|---------|----------------|------------|
| Setup Time | 10-30 minutes | Immediate |
| Battery Life | Excellent (best) | Good |
| Stability | Excellent | Good |
| Complexity | Moderate | Simple |
| Adaptability | Requires recalibration | Automatic |
| Precision | Very High | Moderate |

---

## Getting Started

### Prerequisites

Before using the Frequency Wizard, ensure:

1. **Root Access**: DeckTune must run with sudo/root privileges
   ```bash
   sudo systemctl restart plugin_loader
   ```

2. **System Requirements**:
   - Linux kernel 4.0+ with cpufreq support
   - AMD Ryzen processor (Steam Deck)
   - Temperature sensors accessible
   - At least 30 minutes of uninterrupted time

3. **Preparation**:
   - Close all games and applications
   - Ensure adequate cooling (not in a case or covered)
   - Plug in to AC power (recommended)
   - Disable sleep/suspend during wizard execution

### Accessing the Wizard

1. Open DeckTune from the Quick Access Menu (... button)
2. Navigate to the **Mode Selector** at the top
3. Select **"Frequency-Based"** mode
4. The Frequency Wizard interface will appear

---

## Step-by-Step Wizard Walkthrough

### Step 1: Choose a Preset (Recommended for First-Time Users)

The wizard offers three quick presets optimized for different priorities:

**🛡️ Conservative (Recommended for beginners)**
- Frequency Range: 400-3500 MHz
- Frequency Step: 200 MHz
- Test Duration: 30 seconds per frequency
- Voltage Step: 2 mV
- Safety Margin: 10 mV
- **Estimated Time**: ~15 minutes
- **Best For**: Maximum stability, first-time users

**⚖️ Balanced (Recommended for most users)**
- Frequency Range: 400-3500 MHz
- Frequency Step: 100 MHz
- Test Duration: 30 seconds per frequency
- Voltage Step: 2 mV
- Safety Margin: 5 mV
- **Estimated Time**: ~25 minutes
- **Best For**: Good balance of optimization and time investment

**⚡ Aggressive (For experienced users)**
- Frequency Range: 400-3500 MHz
- Frequency Step: 100 MHz
- Test Duration: 45 seconds per frequency
- Voltage Step: 1 mV
- Safety Margin: 3 mV
- **Estimated Time**: ~35 minutes
- **Best For**: Maximum power savings, experienced users willing to test stability

### Step 2: Advanced Configuration (Optional)

If you want to customize parameters, expand the **Advanced Settings** section:

#### Frequency Range Settings

**Start Frequency** (400-3500 MHz)
- Lower bound of testing range
- Default: 400 MHz (minimum CPU frequency)
- **Tip**: Don't change unless you know your CPU's frequency range

**End Frequency** (400-3500 MHz)
- Upper bound of testing range
- Default: 3500 MHz (maximum boost frequency)
- **Tip**: Use 3000 MHz if you've limited max frequency in BIOS

**Frequency Step** (50-500 MHz)
- Interval between tested frequencies
- Smaller = more precise curve, longer testing time
- Larger = faster testing, less precision
- **Recommended**: 100-200 MHz for most users

#### Test Parameters

**Test Duration** (10-120 seconds)
- How long to stress-test each frequency
- Longer = more confidence in stability
- Shorter = faster completion
- **Recommended**: 30 seconds minimum, 45 seconds for aggressive undervolting

**Starting Voltage** (-100 to 0 mV)
- Initial voltage offset to test
- More negative = more aggressive starting point
- **Recommended**: -30 mV for first run, -40 mV if you know your chip is good

**Voltage Step** (1-10 mV)
- Granularity of voltage testing
- Smaller = more precise, more tests per frequency
- Larger = faster, less precise
- **Recommended**: 2 mV for balanced, 1 mV for maximum precision

**Safety Margin** (0-20 mV)
- Extra voltage added to stable point for safety
- Higher = more stable, less power savings
- Lower = more savings, slightly less stable
- **Recommended**: 5 mV for balanced, 10 mV for conservative, 3 mV for aggressive

### Step 3: Start the Wizard

1. Review your configuration
2. Click **"Start Wizard"** button
3. The wizard will begin testing

**What happens during testing:**
- CPU governor changes to "userspace" mode
- CPU frequency locks to each test point
- Stress test runs at that frequency
- Voltage is reduced incrementally until instability is detected
- Process repeats for each frequency in your range

### Step 4: Monitor Progress

The wizard displays real-time progress information:

**Progress Bar**
- Shows percentage of frequencies completed
- Example: "45% Complete (14/31 frequencies)"

**Current Status**
- **Current Frequency**: The frequency being tested right now
- **Current Voltage**: The voltage offset being tested
- **Estimated Time Remaining**: Calculated based on completed tests

**Status Messages**
- "Testing 1400 MHz at -35 mV..."
- "Found stable voltage: -33 mV"
- "Moving to next frequency..."

### Step 5: Review Results

When the wizard completes, you'll see:

**Frequency Curve Visualization**
- Line chart showing frequency (X-axis) vs voltage (Y-axis)
- Blue markers: Successfully tested stable points
- Red markers: Failed tests (if any)
- Green line: Interpolated curve
- Yellow highlight: Current operating point (if active)

**Statistics**
- Total frequencies tested
- Average voltage offset achieved
- Estimated power savings
- Test duration

**Curve Quality Indicators**
- ✅ **Excellent**: All frequencies tested successfully, smooth curve
- ⚠️ **Good**: 1-2 failed points, curve mostly complete
- ❌ **Poor**: Multiple failures, consider re-running with conservative settings

### Step 6: Apply Your Curve

1. Review the curve visualization
2. Check that the curve looks smooth and reasonable
3. Click **"Apply Curve"** to activate frequency-based mode
4. Your custom voltage curve is now active!

### Step 7: Verify Stability

After applying your curve, test stability:

1. **Light Testing** (First 30 minutes):
   - Browse menus
   - Watch videos
   - Light gaming

2. **Moderate Testing** (Next 2 hours):
   - Play your favorite games
   - Monitor for crashes or freezes
   - Check for visual artifacts

3. **Heavy Testing** (Next few days):
   - Extended gaming sessions
   - Demanding titles
   - Various workloads

**If you experience instability:**
- Disable frequency-based mode temporarily
- Re-run wizard with more conservative settings
- Increase safety margin by 5-10 mV

---

## Configuration Recommendations

### For Maximum Battery Life

```
Preset: Aggressive
Frequency Step: 100 MHz
Test Duration: 45 seconds
Safety Margin: 3 mV
```

**Expected Results**: 10-15% battery life improvement
**Risk Level**: Moderate - requires thorough stability testing
**Best For**: Users who prioritize battery life and are willing to test thoroughly

### For Maximum Stability

```
Preset: Conservative
Frequency Step: 200 MHz
Test Duration: 30 seconds
Safety Margin: 10 mV
```

**Expected Results**: 5-8% battery life improvement
**Risk Level**: Low - very stable
**Best For**: First-time users, users who want "set and forget" reliability

### For Quick Testing

```
Frequency Range: 800-3000 MHz
Frequency Step: 300 MHz
Test Duration: 20 seconds
Safety Margin: 8 mV
```

**Expected Results**: 3-5% battery life improvement
**Risk Level**: Low
**Time**: ~8 minutes
**Best For**: Quick experimentation, testing if your hardware supports undervolting

### For Specific Games

**High-Performance Games** (Cyberpunk, Elden Ring):
```
Frequency Range: 2000-3500 MHz (focus on high frequencies)
Frequency Step: 100 MHz
Test Duration: 45 seconds
Safety Margin: 5 mV
```

**Indie/2D Games** (Hades, Celeste):
```
Frequency Range: 400-2000 MHz (focus on low frequencies)
Frequency Step: 100 MHz
Test Duration: 30 seconds
Safety Margin: 5 mV
```

---

## Understanding Your Results

### Reading the Curve Chart

**X-Axis (Frequency)**
- Shows CPU frequency in MHz
- Left side: Low frequencies (idle, light tasks)
- Right side: High frequencies (gaming, demanding tasks)

**Y-Axis (Voltage Offset)**
- Shows voltage reduction in mV
- More negative = more undervolt = more power savings
- Less negative = less undervolt = more stability

**Curve Shape Interpretation**

**Ideal Curve** (Smooth, gradually increasing):
```
Voltage
  0 mV  |                                    ●
        |                              ●
 -10 mV |                        ●
        |                  ●
 -20 mV |            ●
        |      ●
 -30 mV | ●
        +--------------------------------
         400   1000   2000   3000   MHz
```
- Smooth progression
- Higher frequencies need less aggressive undervolt
- This is normal and expected

**Problematic Curve** (Erratic, many failures):
```
Voltage
  0 mV  |                              ✗
        |                        ●
 -10 mV |                  ✗
        |            ●
 -20 mV |      ✗
        | ●
 -30 mV |
        +--------------------------------
         400   1000   2000   3000   MHz
```
- Multiple failed points (✗)
- Inconsistent results
- May indicate cooling issues or unstable system
- **Action**: Re-run with conservative settings

### Voltage Offset Ranges

**Typical Results by Frequency:**

| Frequency Range | Expected Voltage Offset | Power Savings |
|----------------|------------------------|---------------|
| 400-800 MHz | -40 to -50 mV | High |
| 800-1500 MHz | -30 to -40 mV | Moderate-High |
| 1500-2500 MHz | -20 to -30 mV | Moderate |
| 2500-3500 MHz | -10 to -20 mV | Low-Moderate |

**Note**: These are typical ranges. Your specific CPU may vary significantly based on silicon quality ("silicon lottery").

### Performance Metrics

**Power Savings Estimation**:
- Average -30 mV offset: ~8-12% power reduction
- Average -40 mV offset: ~12-18% power reduction
- Average -50 mV offset: ~18-25% power reduction

**Battery Life Impact**:
- 10% power reduction ≈ 15-20 minutes additional battery life (gaming)
- 15% power reduction ≈ 25-35 minutes additional battery life (gaming)
- 20% power reduction ≈ 35-50 minutes additional battery life (gaming)

---

## Safety Guidelines

### Before You Start

✅ **DO:**
- Read this entire guide before running the wizard
- Ensure your device is adequately cooled
- Close all applications and games
- Save any important work
- Have AC power connected (recommended)
- Allow sufficient time for completion

❌ **DON'T:**
- Run the wizard while gaming or under heavy load
- Cover or restrict airflow to your device
- Interrupt the wizard mid-test (use Cancel button instead)
- Run multiple wizards simultaneously
- Modify system settings during wizard execution

### During Wizard Execution

**Automatic Safety Features:**

1. **Temperature Monitoring**
   - Wizard aborts if CPU temperature exceeds 85°C
   - Automatic cooldown period before resuming
   - Safe voltage restored immediately

2. **Timeout Detection**
   - Tests that freeze are automatically aborted after 30 seconds
   - System restored to safe state
   - Frequency marked as unstable

3. **Consecutive Failure Protection**
   - After 3 consecutive failures at a frequency, that frequency is skipped
   - Prevents endless testing of problematic frequencies
   - Ensures wizard completion

4. **Verification Tests**
   - After curve generation, 3-5 random frequencies are re-tested
   - Confirms curve stability
   - Provides confidence in results

### After Applying Your Curve

**Monitoring for Issues:**

⚠️ **Warning Signs of Instability:**
- Random crashes or freezes
- Visual artifacts or glitches
- Audio stuttering or crackling
- System reboots
- Application crashes
- Corrupted saves or data

**If you experience any warning signs:**

1. **Immediate Action**:
   - Switch back to Load-Based mode or disable undervolting
   - Reboot your device
   - Check for system damage (run filesystem check if needed)

2. **Re-calibration**:
   - Wait for system to cool completely
   - Re-run wizard with more conservative settings:
     - Increase safety margin by 5-10 mV
     - Increase test duration to 45-60 seconds
     - Use Conservative preset

3. **If problems persist**:
   - Your CPU may not tolerate undervolting well
   - Use Load-Based mode with conservative settings
   - Consider that some CPUs simply don't undervolt well

### Best Practices

1. **Start Conservative**
   - Use Conservative preset for first run
   - Gradually move to Balanced or Aggressive after confirming stability

2. **Test Thoroughly**
   - Spend at least 2-3 hours gaming after applying a new curve
   - Test various games and workloads
   - Monitor temperatures and performance

3. **Keep Backups**
   - DeckTune automatically saves your curves
   - You can always revert to previous curves
   - Export successful curves for backup

4. **Document Your Results**
   - Note which settings worked well
   - Record any instability issues
   - Track battery life improvements

5. **Re-run Periodically**
   - CPU characteristics can change over time
   - Re-run wizard every 3-6 months
   - Re-run after BIOS updates or hardware changes

### Hardware Limitations

**Some CPUs undervolt better than others** ("silicon lottery"):
- High-quality chips: May achieve -50 mV or more
- Average chips: Typically -30 to -40 mV
- Poor-quality chips: May only handle -10 to -20 mV

**This is normal and not a defect.** Work with what your specific CPU can handle.

---

## Troubleshooting

### Wizard Won't Start

**Error: "Permission denied accessing cpufreq"**

**Cause**: DeckTune doesn't have root access

**Solution**:
```bash
# Restart plugin loader with sudo
sudo systemctl restart plugin_loader

# Or run DeckTune with sudo
sudo decky-loader
```

**Error: "CPU frequency locking not supported"**

**Cause**: Your system doesn't support userspace governor

**Solution**:
1. Check available governors:
   ```bash
   cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
   ```
2. If "userspace" is not listed, your kernel doesn't support frequency locking
3. Use Load-Based mode instead

### Wizard Fails or Crashes

**Problem: Wizard stops with "Temperature too high"**

**Cause**: CPU temperature exceeded 85°C safety limit

**Solution**:
1. Allow device to cool for 15-30 minutes
2. Ensure adequate ventilation (not in case, not covered)
3. Clean air vents if dusty
4. Consider using a cooling stand
5. Reduce test duration to 20-25 seconds
6. Test in a cooler environment

**Problem: Multiple frequencies fail testing**

**Cause**: System instability, inadequate cooling, or hardware limitations

**Solution**:
1. Ensure system is cool and well-ventilated
2. Close all background applications
3. Use Conservative preset
4. Increase safety margin to 10-15 mV
5. If problems persist, your CPU may not undervolt well

**Problem: Wizard freezes or becomes unresponsive**

**Cause**: Test caused system instability

**Solution**:
1. Wait 2-3 minutes for automatic timeout
2. If no recovery, force reboot (hold power button)
3. After reboot, use more conservative settings
4. Increase test duration for better stability detection

### Results Look Strange

**Problem: Curve shows higher voltages needed at lower frequencies**

**Cause**: This is actually normal for some CPUs

**Explanation**: Some frequency/voltage combinations are less stable than others. The curve reflects your specific CPU's characteristics.

**Action**: If the curve looks very erratic, consider re-running with longer test duration.

**Problem: Very little undervolt achieved (only -5 to -10 mV)**

**Cause**: Your CPU doesn't tolerate aggressive undervolting ("silicon lottery")

**Solution**:
1. This is normal for some CPUs
2. Even small undervolts provide some benefit
3. Focus on stability rather than maximum undervolt
4. Consider that your CPU is already efficient

**Problem: Curve has gaps or missing frequencies**

**Cause**: Those frequencies failed testing and were skipped

**Solution**:
1. The system will interpolate voltages for missing frequencies
2. If many frequencies are missing, re-run with conservative settings
3. Missing frequencies at extremes (very low/high) are usually not problematic

### Stability Issues After Applying Curve

**Problem: Random crashes during gaming**

**Cause**: Curve is too aggressive for real-world use

**Solution**:
1. Immediately switch to Load-Based mode
2. Re-run wizard with:
   - Increased safety margin (+5-10 mV)
   - Longer test duration (45-60 seconds)
   - Conservative preset
3. Test new curve thoroughly before extended use

**Problem: Crashes only in specific games**

**Cause**: Those games stress specific frequency ranges more

**Solution**:
1. Create game-specific profiles with more conservative curves
2. Increase safety margin for problematic frequency ranges
3. Use Load-Based mode for those specific games

**Problem: System becomes unstable after hours of use**

**Cause**: Thermal throttling or cumulative instability

**Solution**:
1. Increase safety margin by 5 mV
2. Ensure adequate cooling during extended sessions
3. Consider that sustained loads may need more voltage than short tests

### Performance Issues

**Problem: Lower performance than expected**

**Cause**: Frequency-based mode doesn't boost performance, only efficiency

**Explanation**: Undervolting reduces power consumption but doesn't increase performance. If you're seeing lower performance, check:
1. CPU frequency limits in BIOS/settings
2. Thermal throttling (check temperatures)
3. Power limits (TDP settings)

**Problem: Voltage changes lag behind frequency changes**

**Cause**: System overhead or configuration issue

**Solution**:
1. Check that frequency monitoring is working (see telemetry)
2. Verify curve is loaded correctly
3. Restart DeckTune service
4. Check system logs for errors

---

## FAQ

### General Questions

**Q: How much battery life improvement can I expect?**

A: Typical improvements range from 5-15% depending on your CPU quality and settings. This translates to approximately 15-45 minutes of additional gaming time on Steam Deck.

**Q: Is undervolting safe?**

A: Yes, when done properly. Undervolting reduces power consumption and heat, which can actually extend hardware lifespan. The worst-case scenario is system instability (crashes), which is immediately reversible. Undervolting cannot physically damage your hardware.

**Q: Will this void my warranty?**

A: Undervolting is a software change and doesn't modify hardware. However, check your device's warranty terms. On Steam Deck, software modifications are generally acceptable.

**Q: Can I use this with other performance tools?**

A: Yes, but be cautious. Frequency-based mode works alongside:
- TDP limits (compatible)
- GPU undervolting (compatible)
- CPU frequency limits (compatible)
- Other undervolting tools (NOT recommended - conflicts possible)

**Q: Do I need to re-run the wizard after updates?**

A: Generally no. Your curve is saved and persists across:
- DeckTune updates
- SteamOS updates
- Reboots

Re-run only if:
- BIOS/firmware updated
- Hardware changed
- Experiencing new instability

### Technical Questions

**Q: What's the difference between frequency-based and load-based mode?**

A: 
- **Frequency-based**: Adjusts voltage based on CPU frequency (speed)
- **Load-based**: Adjusts voltage based on CPU utilization (percentage)

Frequency-based is more precise because frequency directly correlates with power needs, while load percentage is less predictable.

**Q: How does interpolation work?**

A: The wizard tests specific frequencies (e.g., 400, 500, 600 MHz). For frequencies in between (e.g., 550 MHz), the system calculates voltage using linear interpolation:

```
voltage(550) = voltage(500) + (550-500)/(600-500) * (voltage(600)-voltage(500))
```

This provides smooth voltage transitions across the entire frequency range.

**Q: Why do higher frequencies sometimes need less undervolt?**

A: Higher frequencies are more sensitive to voltage. A voltage that's stable at 1000 MHz might cause crashes at 3000 MHz. The wizard finds the safe voltage for each frequency independently.

**Q: Can I manually edit my curve?**

A: Currently, manual editing is not supported in the UI. Curves are generated through automated testing to ensure stability. If you need adjustments, re-run the wizard with different parameters.

**Q: What happens if my CPU frequency goes outside the tested range?**

A: The system uses boundary clamping:
- Frequencies below minimum: Use minimum tested voltage
- Frequencies above maximum: Use maximum tested voltage

This ensures safe operation even at unexpected frequencies.

### Troubleshooting Questions

**Q: The wizard takes too long. Can I speed it up?**

A: Yes, use the Quick Testing configuration:
- Frequency Step: 300 MHz
- Test Duration: 20 seconds
- Frequency Range: 800-3000 MHz

This completes in ~8 minutes but provides less optimization.

**Q: I get different results each time I run the wizard. Why?**

A: Several factors affect results:
- CPU temperature (cooler = better undervolt)
- Background processes
- Random variation in stability testing
- Thermal paste degradation over time

For consistent results:
- Ensure system is cool before starting
- Close all applications
- Run multiple times and use the most conservative result

**Q: Can I have different curves for different games?**

A: Yes! Use DeckTune's profile system:
1. Create a game profile
2. Run the wizard with game-specific settings
3. Associate the curve with that profile
4. The curve automatically applies when the game launches

**Q: My curve looks jagged/irregular. Is this normal?**

A: Some irregularity is normal due to:
- CPU architecture characteristics
- Voltage/frequency interaction complexity
- Test variation

If the curve is very erratic (many failures), re-run with conservative settings.

**Q: Does frequency-based mode work with SMT/Hyperthreading?**

A: Yes, frequency-based mode works with SMT enabled or disabled. The wizard tests physical cores, and voltage applies to all threads on that core.

### Advanced Questions

**Q: Can I export/import curves between devices?**

A: Curves are device-specific due to silicon lottery. However, you can:
- Export curves as backup
- Import as starting point for similar devices
- Always verify stability after importing

**Q: How does this compare to BIOS-level undervolting?**

A: 
- **BIOS undervolting**: Static offset, applies to all frequencies
- **Frequency-based mode**: Dynamic, frequency-specific offsets

Frequency-based mode is more sophisticated and typically achieves better results.

**Q: Can I use this on non-Steam Deck devices?**

A: The wizard works on any Linux system with:
- AMD Ryzen processor
- cpufreq support
- ryzenadj tool
- Root access

However, it's primarily tested on Steam Deck.

**Q: What's the performance overhead of frequency monitoring?**

A: Minimal. Frequency monitoring uses:
- <0.5% CPU overhead
- <1MB memory
- Cached reads (10ms TTL) minimize sysfs access

You won't notice any performance impact.

---

## Additional Resources

### Documentation

- [DeckTune User Guide](USER_GUIDE.md) - General DeckTune documentation
- [Frequency Wizard API](FREQUENCY_WIZARD_API.md) - Developer documentation
- [Dynamic Manual Mode Guide](DYNAMIC_MANUAL_MODE_GUIDE.md) - Related feature

### Community

- **Discord**: Join the DeckTune community for support and tips
- **GitHub**: Report issues and contribute at [DeckTune Repository]
- **Reddit**: r/SteamDeck for general Steam Deck optimization discussions

### External Resources

- [Understanding CPU Undervolting](https://en.wikipedia.org/wiki/Dynamic_voltage_scaling)
- [Linux cpufreq Documentation](https://www.kernel.org/doc/html/latest/admin-guide/pm/cpufreq.html)
- [AMD Ryzen Power Management](https://www.amd.com/en/technologies/ryzen-master)

---

## Conclusion

The Frequency-Based Voltage Wizard is a powerful tool for optimizing your Steam Deck's power efficiency. By following this guide and starting with conservative settings, you can safely achieve significant battery life improvements.

**Remember:**
- Start with Conservative preset
- Test thoroughly after applying curves
- Monitor for stability issues
- Re-run with more conservative settings if needed
- Enjoy your extended battery life!

**Happy gaming! 🎮**

---

*Last Updated: January 2026*
*DeckTune Version: 3.2.0+*
