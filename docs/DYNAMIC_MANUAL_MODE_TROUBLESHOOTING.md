# Dynamic Manual Mode Troubleshooting Guide

## Quick Reference

| Symptom | Quick Fix | Details |
|---------|-----------|---------|
| Won't start | Check min ≤ max | [Link](#dynamic-mode-wont-start) |
| System crashes | Increase voltage values | [Link](#system-crashes-or-freezes) |
| Metrics frozen | Restart dynamic mode | [Link](#metrics-not-updating) |
| Config not saved | Click Apply button | [Link](#configuration-not-persisting) |
| Poor performance | Increase threshold | [Link](#performance-worse-than-expected) |
| Gamepad not working | Click to focus | [Link](#gamepad-controls-not-working) |

---

## Common Issues

### Dynamic Mode Won't Start

**Symptom:** Clicking "Start Dynamic Mode" does nothing, shows error, or button is disabled.

**Diagnostic Steps:**

1. **Check Validation Errors**
   - Look for red error messages near sliders
   - Verify Minimal Value ≤ Maximum Value for all cores
   - Ensure all values are between -100 and 0 mV
   - Confirm threshold is between 0 and 100%

2. **Verify Configuration**
   ```
   Simple Mode:
   ✓ Minimal: -30mV ≤ Maximum: -15mV
   ✗ Minimal: -15mV > Maximum: -30mV (INVALID)
   
   Expert Mode (check each core):
   ✓ Core 0: -35mV ≤ -20mV
   ✓ Core 1: -30mV ≤ -15mV
   ✓ Core 2: -25mV ≤ -10mV
   ✓ Core 3: -25mV ≤ -10mV
   ```

3. **Check Backend Status**
   ```bash
   # Check if gymdeck3 is running
   ps aux | grep gymdeck3
   
   # Check DeckTune backend logs
   journalctl -u decktune -n 50
   
   # Check for RPC errors
   journalctl -u decktune | grep "dynamic_mode"
   ```

4. **Verify Permissions**
   ```bash
   # Check hwmon access
   ls -l /sys/class/hwmon/
   
   # Test voltage write access
   cat /sys/class/hwmon/hwmon*/name
   ```

**Solutions:**

- **Validation Error**: Fix the invalid values (make min ≤ max)
- **Backend Not Running**: Restart plugin via Decky settings
- **Permission Denied**: Ensure DeckTune has root access
- **gymdeck3 Unavailable**: Check if daemon is installed in `bin/` directory
- **RPC Timeout**: Increase timeout in settings or restart backend

**Prevention:**
- Always click "Apply" before "Start Dynamic Mode"
- Use "Reset to Safe Defaults" if unsure about values
- Test configuration with "Apply" before starting

---

### System Crashes or Freezes

**Symptom:** Steam Deck freezes, crashes, reboots, or becomes unresponsive after starting dynamic mode.

**Immediate Recovery:**

1. **Force Shutdown**
   - Hold power button for 10 seconds
   - Wait for complete shutdown
   - Boot normally

2. **Disable Dynamic Mode**
   - Open DeckTune immediately after boot
   - Click "Panic Disable" (red button)
   - Or click "Stop Dynamic Mode"
   - System resets to 0mV (safe)

3. **Restore Safe Configuration**
   - Click "Reset to Safe Defaults"
   - Or click "Restore Last Stable"
   - Apply and test stability

**Root Cause Analysis:**

**Crash at Idle:**
- Minimal Value too aggressive for your chip
- Solution: Increase Minimal Value by +5mV increments
- Example: -35mV → -30mV → -25mV until stable

**Crash Under Load:**
- Maximum Value too aggressive for your chip
- Solution: Increase Maximum Value by +5mV increments
- Example: -25mV → -20mV → -15mV until stable

**Crash During Transition:**
- Threshold too high (stays aggressive too long)
- Solution: Decrease Threshold by -10% increments
- Example: 70% → 60% → 50% until stable

**Random Crashes:**
- Chip can't handle dynamic voltage changes
- Solution: Use static undervolt instead
- Or use very conservative values (-20mV / -10mV / 30%)

**Diagnostic Commands:**

```bash
# Check system logs for crash info
journalctl -b -1 -n 100  # Previous boot

# Check for kernel panics
dmesg | grep -i "panic\|oops\|segfault"

# Check DeckTune crash recovery
journalctl -u decktune | grep "crash\|recovery"
```

**Stability Testing:**

1. **Idle Test** (10 minutes)
   - Start dynamic mode
   - Leave Steam Deck at desktop
   - Monitor metrics
   - If crashes: Increase Minimal Value

2. **Load Test** (10 minutes)
   - Start dynamic mode
   - Run CPU stress test (Expert Mode → Tests)
   - Monitor temperature and metrics
   - If crashes: Increase Maximum Value

3. **Gaming Test** (30 minutes)
   - Start dynamic mode
   - Play a demanding game
   - Monitor for stuttering or crashes
   - If crashes: Increase Maximum Value or lower Threshold

**Prevention:**
- Start with safe defaults (-30mV / -15mV / 50%)
- Make small changes (-5mV increments)
- Test each change for 10+ minutes
- Run stress tests before gaming
- Keep notes on what works for your chip

---

### Metrics Not Updating

**Symptom:** Metrics display shows "---", stale data, or doesn't update every 500ms.

**Diagnostic Steps:**

1. **Check Dynamic Mode Status**
   - Verify status indicator shows "Active"
   - If "Inactive", click "Start Dynamic Mode"

2. **Verify Polling**
   - Metrics should update every 500ms
   - Watch for timestamp changes
   - Check if graph is updating

3. **Check Backend Connection**
   ```bash
   # Check gymdeck3 is running
   ps aux | grep gymdeck3
   
   # Check RPC responses
   journalctl -u decktune | grep "get_core_metrics"
   
   # Check for errors
   journalctl -u gymdeck3 -n 50
   ```

4. **Verify Hardware Access**
   ```bash
   # Test CPU load reading
   cat /proc/stat | grep "^cpu[0-3]"
   
   # Test temperature reading
   cat /sys/class/hwmon/hwmon*/temp1_input
   
   # Test frequency reading
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
   ```

**Solutions:**

- **Mode Inactive**: Click "Start Dynamic Mode"
- **Polling Stopped**: Stop and restart dynamic mode
- **Backend Unresponsive**: Restart plugin via Decky settings
- **Hardware Access Denied**: Check permissions on hwmon/proc
- **gymdeck3 Crashed**: Check logs, restart daemon
- **RPC Timeout**: Increase timeout or check network

**Workarounds:**

1. **Manual Restart**
   - Click "Stop Dynamic Mode"
   - Wait 2 seconds
   - Click "Start Dynamic Mode"
   - Metrics should resume

2. **Plugin Reload**
   - Decky menu → Settings → Reload Plugins
   - Reopen DeckTune
   - Reconfigure and start

3. **Full Restart**
   - Close DeckTune
   - Restart Decky Loader
   - Reopen DeckTune

**Prevention:**
- Don't switch tabs rapidly while metrics updating
- Avoid starting/stopping mode repeatedly
- Keep plugin open while monitoring
- Check backend logs for warnings

---

### Configuration Not Persisting

**Symptom:** Settings reset after closing plugin, switching tabs, or rebooting.

**Diagnostic Steps:**

1. **Verify Apply Was Clicked**
   - Configuration only saves when "Apply" is clicked
   - Look for confirmation message
   - Check if curve graph updated

2. **Check localStorage**
   - Open browser console (Ctrl+Shift+I)
   - Go to Application → Local Storage
   - Look for "dynamicMode" key
   - Verify values match your configuration

3. **Check Backend Settings**
   ```bash
   # Check settings file exists
   ls -l ~/homebrew/settings/decktune/settings.json
   
   # View dynamic mode config
   cat ~/homebrew/settings/decktune/settings.json | grep -A 20 "dynamic_manual_mode"
   
   # Check file permissions
   stat ~/homebrew/settings/decktune/settings.json
   ```

4. **Check for Write Errors**
   ```bash
   # Check backend logs for save errors
   journalctl -u decktune | grep "save\|write\|persist"
   
   # Check disk space
   df -h ~/homebrew/settings/
   ```

**Solutions:**

- **Apply Not Clicked**: Always click "Apply" after changes
- **localStorage Disabled**: Enable in browser settings
- **localStorage Full**: Clear old data or increase quota
- **File Not Writable**: Fix permissions: `chmod 644 ~/homebrew/settings/decktune/settings.json`
- **Directory Not Writable**: Fix permissions: `chmod 755 ~/homebrew/settings/decktune/`
- **Disk Full**: Free up space on home partition
- **Backend Save Failed**: Check logs for specific error

**Manual Configuration Backup:**

```bash
# Backup current config
cp ~/homebrew/settings/decktune/settings.json ~/decktune_backup.json

# Restore from backup
cp ~/decktune_backup.json ~/homebrew/settings/decktune/settings.json

# Export config (from UI)
Expert Mode → Presets → Export All
```

**Prevention:**
- Always click "Apply" after changes
- Wait for confirmation message
- Don't close plugin immediately after Apply
- Periodically export configurations as backup

---

### Performance Worse Than Expected

**Symptom:** Dynamic mode performs worse than static undervolt or no undervolt.

**Diagnostic Steps:**

1. **Compare Configurations**
   ```
   Static Undervolt: -25mV all cores
   
   Dynamic Mode:
   Minimal: -30mV (more aggressive)
   Maximum: -15mV (less aggressive)
   Threshold: 50%
   
   Average: -22.5mV (similar to static)
   ```

2. **Check Transition Behavior**
   - Monitor load percentage
   - Watch voltage transitions
   - Look for frequent changes (hunting)
   - Check if threshold is appropriate

3. **Measure Actual Performance**
   ```
   Benchmark with static -25mV: 1000 ops/s
   Benchmark with dynamic mode: 950 ops/s
   
   Difference: -5% (worse)
   ```

4. **Check for Throttling**
   - Monitor temperature (should be < 85°C)
   - Check frequency (should match load)
   - Look for thermal throttling
   - Verify fan is working

**Common Causes:**

**Threshold Too Low:**
- Transitions to safe voltage too early
- Spends most time at Maximum Value
- Solution: Increase threshold to 60-70%

**Maximum Value Too Conservative:**
- Not aggressive enough under load
- Worse than static undervolt
- Solution: Decrease Maximum Value (more aggressive)

**Frequent Transitions:**
- Load oscillates around threshold
- Voltage changes constantly
- Overhead from transitions
- Solution: Increase hysteresis or adjust threshold

**Overhead from Monitoring:**
- Polling every 500ms uses CPU
- Minimal but measurable
- Solution: Use Simple Mode (less overhead)

**Solutions:**

1. **Optimize Threshold**
   - Increase to 60-70% for gaming
   - Decrease to 30-40% for battery life
   - Match to your typical workload

2. **Adjust Maximum Value**
   - Make more aggressive (lower)
   - Match or exceed static undervolt
   - Test stability carefully

3. **Reduce Transitions**
   - Use wider threshold range
   - Avoid threshold near typical load
   - Example: If load is usually 55%, use threshold 40% or 70%

4. **Compare Fairly**
   - Benchmark with same conditions
   - Same game, same settings
   - Same temperature, same time
   - Multiple runs for average

**When to Use Static Instead:**
- Workload has consistent load (always high or always low)
- Dynamic mode shows no benefit
- Overhead is measurable
- Simpler configuration preferred

---

### Gamepad Controls Not Working

**Symptom:** D-pad, L1/R1, or A button don't control Dynamic Manual Mode interface.

**Diagnostic Steps:**

1. **Check Focus**
   - Click inside Dynamic Manual Mode area
   - Look for focus indicator (blue outline)
   - Try touchscreen first to set focus

2. **Check Other Plugins**
   - Close other Decky plugins
   - Some plugins capture gamepad input
   - Test with only DeckTune open

3. **Check Decky Settings**
   - Decky menu → Settings
   - Verify gamepad navigation enabled
   - Check for conflicting keybinds

4. **Test Individual Controls**
   ```
   D-pad Up/Down: Should change core selection
   D-pad Left/Right: Should move focus between controls
   L1/R1: Should adjust slider values
   A Button: Should activate focused button
   B Button: Should go back/cancel
   ```

**Solutions:**

- **No Focus**: Click inside component with touchscreen
- **Other Plugin Interfering**: Close other plugins
- **Decky Issue**: Restart Decky Loader
- **Gamepad Disabled**: Enable in Decky settings
- **Wrong Mode**: Some controls only work in Expert Mode (core tabs)

**Workarounds:**

1. **Use Touchscreen**
   - All controls work with touch
   - More precise than gamepad
   - Faster for configuration

2. **Use Keyboard**
   - Tab key for navigation
   - Arrow keys for sliders
   - Enter for buttons
   - Requires external keyboard

3. **Restart Decky**
   - Sometimes fixes focus issues
   - Settings → Restart Decky Loader
   - Reopen DeckTune

**Prevention:**
- Click to focus before using gamepad
- Close other plugins while configuring
- Use touchscreen for initial setup
- Test gamepad controls after plugin updates

---

## Advanced Troubleshooting

### Backend Logs Analysis

**View Recent Logs:**
```bash
# Last 50 lines
journalctl -u decktune -n 50

# Follow live
journalctl -u decktune -f

# Filter for errors
journalctl -u decktune | grep -i "error\|fail\|exception"

# Filter for dynamic mode
journalctl -u decktune | grep "dynamic"
```

**Common Log Messages:**

**Validation Error:**
```
ERROR: Validation failed: min_mv (-35) must be <= max_mv (-40)
```
Solution: Fix configuration, ensure min ≤ max

**RPC Timeout:**
```
ERROR: RPC timeout: get_core_metrics did not respond within 5000ms
```
Solution: Check gymdeck3 is running, increase timeout

**Hardware Access Error:**
```
ERROR: Failed to read /sys/class/hwmon/hwmon0/temp1_input: Permission denied
```
Solution: Check permissions, run with elevated privileges

**Configuration Save Error:**
```
ERROR: Failed to save settings: [Errno 28] No space left on device
```
Solution: Free up disk space

---

### gymdeck3 Daemon Issues

**Check Daemon Status:**
```bash
# Is it running?
ps aux | grep gymdeck3

# Check logs
journalctl -u gymdeck3 -n 50

# Check for crashes
journalctl -u gymdeck3 | grep -i "crash\|panic\|segfault"
```

**Restart Daemon:**
```bash
# Stop
sudo systemctl stop gymdeck3

# Start
sudo systemctl start gymdeck3

# Restart
sudo systemctl restart gymdeck3

# Check status
sudo systemctl status gymdeck3
```

**Common Daemon Issues:**

**Not Starting:**
- Check binary exists: `ls -l ~/homebrew/plugins/decktune/bin/gymdeck3`
- Check permissions: `chmod +x ~/homebrew/plugins/decktune/bin/gymdeck3`
- Check dependencies: `ldd ~/homebrew/plugins/decktune/bin/gymdeck3`

**Crashing:**
- Check logs for panic messages
- Verify hardware access permissions
- Test with minimal configuration
- Report bug with logs

**High CPU Usage:**
- Check polling interval (should be 500ms)
- Verify not stuck in loop
- Check for excessive logging
- Restart daemon

---

### Hardware Access Issues

**Test Hardware Access:**

```bash
# CPU load
cat /proc/stat | grep "^cpu[0-3]"

# Temperature
cat /sys/class/hwmon/hwmon*/temp1_input

# Frequency
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq

# Voltage (if available)
cat /sys/class/hwmon/hwmon*/in*_input
```

**Fix Permissions:**

```bash
# Add user to required groups
sudo usermod -a -G video,input $USER

# Fix hwmon permissions (temporary)
sudo chmod -R 644 /sys/class/hwmon/hwmon*/

# Fix hwmon permissions (permanent via udev)
sudo nano /etc/udev/rules.d/99-hwmon.rules
# Add: KERNEL=="hwmon*", SUBSYSTEM=="hwmon", MODE="0644"
sudo udevadm control --reload-rules
```

---

### Performance Profiling

**Measure Overhead:**

```bash
# CPU usage of gymdeck3
top -p $(pgrep gymdeck3)

# Memory usage
ps aux | grep gymdeck3 | awk '{print $6}'

# RPC latency
time curl -X POST http://localhost:8080/rpc -d '{"method":"get_core_metrics","params":{"core_id":0}}'
```

**Benchmark Comparison:**

```bash
# Baseline (no undervolt)
stress-ng --cpu 4 --timeout 10s --metrics

# Static undervolt
# (apply -25mV via Manual tab)
stress-ng --cpu 4 --timeout 10s --metrics

# Dynamic mode
# (start dynamic mode with -30/-15/50)
stress-ng --cpu 4 --timeout 10s --metrics

# Compare results
```

---

## Getting Help

### Before Reporting Issues

1. **Check This Guide**: Most issues are covered above
2. **Check Logs**: Backend and gymdeck3 logs often show the problem
3. **Test Safe Defaults**: Verify issue persists with -30/-15/50
4. **Try Simple Mode**: Isolate per-core vs unified configuration
5. **Export Diagnostics**: Expert Mode → Diagnostics → Export

### Reporting Bugs

Include the following information:

**System Info:**
- Steam Deck model (LCD/OLED)
- SteamOS version
- DeckTune version
- gymdeck3 version

**Configuration:**
- Mode (Simple/Expert)
- Voltage values (min/max/threshold)
- Per-core configs (if Expert Mode)

**Logs:**
```bash
# Export all logs
journalctl -u decktune -n 500 > decktune.log
journalctl -u gymdeck3 -n 500 > gymdeck3.log
dmesg > dmesg.log

# Attach to bug report
```

**Steps to Reproduce:**
1. Exact steps to trigger issue
2. Expected behavior
3. Actual behavior
4. Frequency (always/sometimes/rare)

**GitHub Issues:**
https://github.com/bobberdolle1/DeckTune/issues

---

## FAQ

**Q: Why does my configuration keep resetting?**
A: You must click "Apply" to save. Configuration is not saved automatically.

**Q: Can I use Dynamic Manual Mode with Per-Game Profiles?**
A: Yes, save your dynamic configuration as a profile for automatic switching.

**Q: Is Dynamic Manual Mode safe?**
A: Yes, with proper testing. Start with safe defaults and increase aggressiveness gradually.

**Q: Why do my values differ from someone else's?**
A: Every chip is different (silicon lottery). Don't copy others' values blindly.

**Q: Can I damage my Steam Deck?**
A: Undervolting is generally safe. The system will crash before damage occurs. Use safety features.

**Q: Should I use Simple or Expert Mode?**
A: Start with Simple Mode. Use Expert Mode only if you understand per-core behavior.

**Q: Why is performance worse than static undervolt?**
A: Check threshold and Maximum Value. May need adjustment for your workload.

**Q: How do I find my chip's maximum undervolt?**
A: Use Silicon Binning feature (Wizard Mode) or manually test with stress tests.

**Q: What if I can't get dynamic mode to work?**
A: Use static undervolt instead (Manual tab). Dynamic mode isn't required.

**Q: Can I use Dynamic Manual Mode with Fan Control?**
A: Yes, they work together. Configure both independently.

---

## Additional Resources

- **User Guide**: [Dynamic Manual Mode Guide](DYNAMIC_MANUAL_MODE_GUIDE.md)
- **API Documentation**: [Dynamic Manual Mode API](DYNAMIC_MANUAL_MODE_API.md)
- **Main README**: [README.md](../README.md)
- **GitHub Issues**: https://github.com/bobberdolle1/DeckTune/issues
- **Community Discord**: (if available)
