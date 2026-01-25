# Frequency Wizard API Reference

## Overview

The Frequency Wizard API provides programmatic access to DeckTune's frequency-based voltage optimization system. This API allows developers to:

- Generate frequency-voltage curves through automated testing
- Monitor wizard progress in real-time
- Manage frequency curves (save, load, apply)
- Control frequency-based voltage mode
- Integrate frequency optimization into custom workflows

All API methods are exposed through the RPC interface and can be called from the frontend or external applications.

## Table of Contents

1. [Data Structures](#data-structures)
2. [RPC Methods](#rpc-methods)
3. [Error Handling](#error-handling)
4. [Integration Examples](#integration-examples)
5. [Error Codes](#error-codes)

---

## Data Structures

### FrequencyPoint

Represents a single point in a frequency-voltage curve.

```python
{
    "frequency_mhz": int,      # CPU frequency in MHz
    "voltage_mv": int,         # Voltage offset in mV (negative value, e.g., -30)
    "stable": bool,            # Whether this voltage was stable at this frequency
    "test_duration": int,      # Duration in seconds that this point was tested
    "timestamp": float         # Unix timestamp when this point was tested
}
```

**Example:**
```json
{
    "frequency_mhz": 1600,
    "voltage_mv": -35,
    "stable": true,
    "test_duration": 30,
    "timestamp": 1706198430.0
}
```


### FrequencyCurve

Complete frequency-voltage curve for a CPU core.

```python
{
    "core_id": int,                    # CPU core identifier (0-based)
    "points": List[FrequencyPoint],    # List of frequency-voltage points (sorted by frequency)
    "created_at": float,               # Unix timestamp when curve was created
    "wizard_config": dict              # Configuration used to generate this curve
}
```

**Example:**
```json
{
    "core_id": 0,
    "created_at": 1706198400.0,
    "wizard_config": {
        "freq_start": 400,
        "freq_end": 3500,
        "freq_step": 100,
        "test_duration": 30,
        "voltage_start": -30,
        "voltage_step": 2,
        "safety_margin": 5
    },
    "points": [
        {
            "frequency_mhz": 400,
            "voltage_mv": -50,
            "stable": true,
            "test_duration": 30,
            "timestamp": 1706198430.0
        },
        {
            "frequency_mhz": 500,
            "voltage_mv": -48,
            "stable": true,
            "test_duration": 30,
            "timestamp": 1706198460.0
        }
    ]
}
```


### FrequencyWizardConfig

Configuration parameters for the frequency wizard.

```python
{
    "core_id": int,           # CPU core ID to test (default: 0)
    "freq_start": int,        # Starting frequency in MHz (400-3500, default: 400)
    "freq_end": int,          # Ending frequency in MHz (must be > freq_start, default: 3500)
    "freq_step": int,         # Frequency step size in MHz (50-500, default: 100)
    "test_duration": int,     # Test duration per frequency in seconds (10-120, default: 30)
    "voltage_start": int,     # Starting voltage offset in mV (-100 to 0, default: -30)
    "voltage_step": int,      # Voltage step size in mV (1-10, default: 2)
    "safety_margin": int,     # Safety margin to add in mV (0-20, default: 5)
    "adaptive_step": bool,    # Enable adaptive stepping (default: True)
    "preset": str             # Optional preset name: "quick", "balanced", or "thorough"
}
```

**Validation Rules:**
- `freq_start`: Must be between 400-3500 MHz
- `freq_end`: Must be greater than `freq_start`
- `freq_step`: Must be between 50-500 MHz
- `test_duration`: Must be between 10-120 seconds
- `voltage_start`: Must be between -100 and 0 mV
- `voltage_step`: Must be between 1-10 mV
- `safety_margin`: Must be between 0-20 mV

**Presets:**
- `"quick"`: Fast testing (~10-15 minutes) - freq_step=200, test_duration=15
- `"balanced"`: Balanced coverage (~20-30 minutes) - freq_step=100, test_duration=30
- `"thorough"`: Maximum coverage (~45-60 minutes) - freq_step=50, test_duration=60


### WizardProgress

Real-time progress information for a running wizard.

```python
{
    "running": bool,              # Whether wizard is currently running
    "current_frequency": int,     # Current frequency being tested (MHz)
    "current_voltage": int,       # Current voltage being tested (mV)
    "progress_percent": float,    # Progress percentage (0-100)
    "estimated_remaining": int,   # Estimated time remaining (seconds)
    "completed_points": int,      # Number of completed frequency points
    "total_points": int           # Total number of frequency points to test
}
```

**Example:**
```json
{
    "running": true,
    "current_frequency": 1600,
    "current_voltage": -35,
    "progress_percent": 45.5,
    "estimated_remaining": 820,
    "completed_points": 15,
    "total_points": 33
}
```

---

## RPC Methods

### start_frequency_wizard

Start a frequency wizard session to generate a frequency-voltage curve.

**Method:** `start_frequency_wizard(config: Dict[str, Any]) -> Dict[str, Any]`

**Parameters:**
- `config` (dict): Wizard configuration (see [FrequencyWizardConfig](#frequencywizardconfig))

**Returns:**
```python
{
    "success": bool,              # Whether wizard started successfully
    "session_id": str,            # Unique session identifier (UUID)
    "estimated_duration": int     # Estimated completion time in seconds
}
```

**Error Response:**
```python
{
    "success": false,
    "error": str                  # Error message
}
```


**Example Usage:**

```python
# Start wizard with quick preset
config = {
    "core_id": 0,
    "preset": "quick"
}
result = await rpc.start_frequency_wizard(config)

if result["success"]:
    session_id = result["session_id"]
    estimated_duration = result["estimated_duration"]
    print(f"Wizard started: {session_id}, ETA: {estimated_duration}s")
else:
    print(f"Failed to start wizard: {result['error']}")
```

```python
# Start wizard with custom configuration
config = {
    "core_id": 0,
    "freq_start": 800,
    "freq_end": 3000,
    "freq_step": 200,
    "test_duration": 20,
    "voltage_start": -40,
    "voltage_step": 2,
    "safety_margin": 5,
    "adaptive_step": True
}
result = await rpc.start_frequency_wizard(config)
```

**Error Conditions:**
- `ERR_OPERATION_RUNNING`: Another operation (autotune, binning, etc.) is already running
- `ERR_INVALID_CONFIG`: Configuration validation failed
- `ERR_PERMISSION_DENIED`: Insufficient permissions to control CPU frequency (requires root)
- `ERR_UNSUPPORTED`: CPU frequency control not supported on this system

---

### get_frequency_wizard_progress

Get real-time progress information for the running wizard.

**Method:** `get_frequency_wizard_progress() -> Dict[str, Any]`

**Parameters:** None

**Returns:**
```python
{
    "running": bool,              # Whether wizard is currently running
    "current_frequency": int,     # Current frequency being tested (MHz)
    "current_voltage": int,       # Current voltage being tested (mV)
    "progress_percent": float,    # Progress percentage (0-100)
    "estimated_remaining": int,   # Estimated time remaining (seconds)
    "completed_points": int,      # Number of completed frequency points
    "total_points": int           # Total number of frequency points to test
}
```


**Example Usage:**

```python
# Poll progress every second
import asyncio

async def monitor_wizard_progress():
    while True:
        progress = await rpc.get_frequency_wizard_progress()
        
        if not progress["running"]:
            print("Wizard not running")
            break
        
        print(f"Progress: {progress['progress_percent']:.1f}%")
        print(f"Testing: {progress['current_frequency']} MHz @ {progress['current_voltage']} mV")
        print(f"ETA: {progress['estimated_remaining']}s")
        print(f"Completed: {progress['completed_points']}/{progress['total_points']}")
        
        await asyncio.sleep(1.0)

await monitor_wizard_progress()
```

**Notes:**
- Returns default values (all zeros, running=false) when no wizard is active
- Progress updates occur approximately every 1-2 seconds during wizard execution
- `progress_percent` is calculated as: `(completed_points / total_points) * 100`

---

### cancel_frequency_wizard

Cancel a running frequency wizard and restore original settings.

**Method:** `cancel_frequency_wizard() -> Dict[str, Any]`

**Parameters:** None

**Returns:**
```python
{
    "success": bool              # Whether cancellation succeeded
}
```

**Error Response:**
```python
{
    "success": false,
    "error": str                 # Error message
}
```

**Example Usage:**

```python
# Cancel running wizard
result = await rpc.cancel_frequency_wizard()

if result["success"]:
    print("Wizard cancelled successfully")
else:
    print(f"Failed to cancel: {result['error']}")
```


**Behavior:**
- Wizard stops after the current test completes (within 2 seconds)
- Original CPU governor is restored
- Original voltage settings are restored
- Partial results are saved to allow resumption
- Cancellation is graceful and safe

**Error Conditions:**
- `ERR_NOT_RUNNING`: No wizard is currently running

---

### get_frequency_curve

Retrieve a saved frequency curve for a specific CPU core.

**Method:** `get_frequency_curve(core_id: int) -> Dict[str, Any]`

**Parameters:**
- `core_id` (int): CPU core ID (0-based)

**Returns:**
```python
{
    "success": bool,
    "curve": FrequencyCurve      # See FrequencyCurve structure
}
```

**Error Response:**
```python
{
    "success": false,
    "error": str                 # Error message
}
```

**Example Usage:**

```python
# Get curve for core 0
result = await rpc.get_frequency_curve(0)

if result["success"]:
    curve = result["curve"]
    print(f"Core {curve['core_id']}: {len(curve['points'])} points")
    
    # Print all frequency points
    for point in curve["points"]:
        print(f"  {point['frequency_mhz']} MHz: {point['voltage_mv']} mV")
else:
    print(f"No curve found: {result['error']}")
```

**Error Conditions:**
- `ERR_NOT_FOUND`: No curve exists for the specified core
- `ERR_INVALID_CORE`: Invalid core ID

---


### apply_frequency_curve

Apply frequency curves to CPU cores.

**Method:** `apply_frequency_curve(curves: Dict[str, Any]) -> Dict[str, Any]`

**Parameters:**
- `curves` (dict): Dictionary mapping core IDs (as strings) to FrequencyCurve objects

**Returns:**
```python
{
    "success": bool              # Whether curves were applied successfully
}
```

**Error Response:**
```python
{
    "success": false,
    "error": str                 # Error message
}
```

**Example Usage:**

```python
# Apply curves for multiple cores
curves = {
    "0": {
        "core_id": 0,
        "points": [
            {"frequency_mhz": 400, "voltage_mv": -50, "stable": True, "test_duration": 30, "timestamp": 1706198430.0},
            {"frequency_mhz": 500, "voltage_mv": -48, "stable": True, "test_duration": 30, "timestamp": 1706198460.0}
        ],
        "created_at": 1706198400.0,
        "wizard_config": {}
    },
    "1": {
        "core_id": 1,
        "points": [
            {"frequency_mhz": 400, "voltage_mv": -45, "stable": True, "test_duration": 30, "timestamp": 1706198430.0}
        ],
        "created_at": 1706198400.0,
        "wizard_config": {}
    }
}

result = await rpc.apply_frequency_curve(curves)

if result["success"]:
    print("Curves applied successfully")
else:
    print(f"Failed to apply curves: {result['error']}")
```

**Validation:**
- All curves are validated before application
- Voltages must be in range [-100, 0] mV
- Frequencies must be in ascending order
- No duplicate frequencies allowed

**Error Conditions:**
- `ERR_INVALID_CURVE`: Curve validation failed
- `ERR_INVALID_FORMAT`: Malformed curve data

---


### enable_frequency_mode

Enable frequency-based voltage control mode.

**Method:** `enable_frequency_mode() -> Dict[str, Any]`

**Parameters:** None

**Returns:**
```python
{
    "success": bool              # Whether mode was enabled successfully
}
```

**Error Response:**
```python
{
    "success": false,
    "error": str                 # Error message
}
```

**Example Usage:**

```python
# Enable frequency-based mode
result = await rpc.enable_frequency_mode()

if result["success"]:
    print("Frequency-based mode enabled")
    # Voltage will now be adjusted based on CPU frequency
else:
    print(f"Failed to enable: {result['error']}")
```

**Behavior:**
- Activates the frequency voltage controller
- Voltage adjustments are based on current CPU frequency
- Uses loaded frequency curves for voltage calculation
- Monitors frequency every 10-50ms
- Applies voltage changes within 50ms of frequency change

**Prerequisites:**
- At least one frequency curve must be loaded
- Frequency curves must be valid

**Error Conditions:**
- `ERR_NO_CURVES`: No frequency curves loaded
- `ERR_INVALID_CURVES`: Loaded curves are invalid

---

### disable_frequency_mode

Disable frequency-based voltage control mode.

**Method:** `disable_frequency_mode() -> Dict[str, Any]`

**Parameters:** None

**Returns:**
```python
{
    "success": bool              # Whether mode was disabled successfully
}
```


**Error Response:**
```python
{
    "success": false,
    "error": str                 # Error message
}
```

**Example Usage:**

```python
# Disable frequency-based mode
result = await rpc.disable_frequency_mode()

if result["success"]:
    print("Frequency-based mode disabled")
    # System returns to previous voltage control mode
else:
    print(f"Failed to disable: {result['error']}")
```

**Behavior:**
- Deactivates the frequency voltage controller
- Returns to previous voltage control mode (load-based or manual)
- Preserves current voltage settings for smooth transition

---

## Error Handling

### Error Response Format

All RPC methods return a consistent error format when operations fail:

```python
{
    "success": false,
    "error": str,                    # Human-readable error message
    "error_code": str,               # Machine-readable error code (optional)
    "diagnostics": dict              # Additional diagnostic information (optional)
}
```

### Error Handling Strategy

**1. Validation Errors**
- Occur before any system changes
- Safe to retry with corrected parameters
- No cleanup required

**2. Permission Errors**
- Require root/sudo access
- Provide clear instructions in error message
- No system state changes

**3. Runtime Errors**
- System state may be partially modified
- Automatic rollback to safe state
- Original settings restored

**4. Hardware Errors**
- Graceful degradation
- Fallback to safe defaults
- Clear error reporting


### Example Error Handling

```python
async def safe_wizard_execution():
    try:
        # Start wizard
        config = {"core_id": 0, "preset": "quick"}
        result = await rpc.start_frequency_wizard(config)
        
        if not result["success"]:
            error = result["error"]
            
            # Handle specific errors
            if "permission" in error.lower():
                print("Error: Root access required")
                print("Please run: sudo systemctl restart plugin_loader")
                return
            
            elif "already running" in error.lower():
                print("Error: Another operation is in progress")
                print("Please wait or cancel the current operation")
                return
            
            elif "invalid" in error.lower():
                print(f"Configuration error: {error}")
                return
            
            else:
                print(f"Unexpected error: {error}")
                return
        
        # Monitor progress
        session_id = result["session_id"]
        print(f"Wizard started: {session_id}")
        
        while True:
            progress = await rpc.get_frequency_wizard_progress()
            
            if not progress["running"]:
                break
            
            print(f"Progress: {progress['progress_percent']:.1f}%")
            await asyncio.sleep(1.0)
        
        # Get generated curve
        curve_result = await rpc.get_frequency_curve(0)
        
        if curve_result["success"]:
            print("Curve generated successfully!")
            return curve_result["curve"]
        else:
            print(f"Failed to retrieve curve: {curve_result['error']}")
            return None
    
    except Exception as e:
        print(f"Unexpected exception: {e}")
        
        # Attempt to cancel wizard if running
        try:
            await rpc.cancel_frequency_wizard()
        except:
            pass
        
        return None
```

---


## Integration Examples

### Example 1: Basic Wizard Workflow

Complete workflow for generating and applying a frequency curve:

```python
import asyncio

async def generate_and_apply_curve(rpc, core_id=0):
    """Generate frequency curve and apply it."""
    
    # Step 1: Start wizard with quick preset
    print("Starting frequency wizard...")
    config = {
        "core_id": core_id,
        "preset": "quick"
    }
    
    result = await rpc.start_frequency_wizard(config)
    if not result["success"]:
        print(f"Failed to start: {result['error']}")
        return False
    
    session_id = result["session_id"]
    eta = result["estimated_duration"]
    print(f"Wizard started (session: {session_id}, ETA: {eta}s)")
    
    # Step 2: Monitor progress
    print("\nMonitoring progress...")
    last_percent = 0
    
    while True:
        progress = await rpc.get_frequency_wizard_progress()
        
        if not progress["running"]:
            break
        
        percent = progress["progress_percent"]
        if percent - last_percent >= 5.0:  # Update every 5%
            print(f"  {percent:.1f}% complete - Testing {progress['current_frequency']} MHz")
            last_percent = percent
        
        await asyncio.sleep(2.0)
    
    print("Wizard completed!")
    
    # Step 3: Retrieve generated curve
    print("\nRetrieving curve...")
    curve_result = await rpc.get_frequency_curve(core_id)
    
    if not curve_result["success"]:
        print(f"Failed to get curve: {curve_result['error']}")
        return False
    
    curve = curve_result["curve"]
    print(f"Curve has {len(curve['points'])} frequency points")
    
    # Step 4: Apply curve
    print("\nApplying curve...")
    apply_result = await rpc.apply_frequency_curve({str(core_id): curve})
    
    if not apply_result["success"]:
        print(f"Failed to apply: {apply_result['error']}")
        return False
    
    # Step 5: Enable frequency mode
    print("Enabling frequency-based mode...")
    enable_result = await rpc.enable_frequency_mode()
    
    if not enable_result["success"]:
        print(f"Failed to enable: {enable_result['error']}")
        return False
    
    print("\n✓ Frequency-based voltage optimization is now active!")
    return True

# Run the workflow
await generate_and_apply_curve(rpc)
```


### Example 2: Custom Configuration with Progress Callback

Advanced wizard usage with custom configuration and detailed progress tracking:

```python
async def advanced_wizard_with_progress(rpc):
    """Run wizard with custom config and detailed progress tracking."""
    
    # Custom configuration for thorough testing
    config = {
        "core_id": 0,
        "freq_start": 800,      # Start at 800 MHz
        "freq_end": 3200,       # End at 3200 MHz
        "freq_step": 100,       # Test every 100 MHz
        "test_duration": 45,    # 45 seconds per test
        "voltage_start": -40,   # Start at -40mV
        "voltage_step": 2,      # 2mV steps
        "safety_margin": 8,     # 8mV safety margin
        "adaptive_step": True   # Enable adaptive stepping
    }
    
    # Start wizard
    result = await rpc.start_frequency_wizard(config)
    if not result["success"]:
        print(f"Error: {result['error']}")
        return
    
    print(f"Wizard started - ETA: {result['estimated_duration']}s")
    print("=" * 60)
    
    # Track progress with detailed output
    start_time = time.time()
    
    while True:
        progress = await rpc.get_frequency_wizard_progress()
        
        if not progress["running"]:
            break
        
        # Calculate elapsed time
        elapsed = int(time.time() - start_time)
        
        # Display detailed progress
        print(f"\rProgress: {progress['progress_percent']:5.1f}% | "
              f"Freq: {progress['current_frequency']:4d} MHz | "
              f"Voltage: {progress['current_voltage']:3d} mV | "
              f"Points: {progress['completed_points']}/{progress['total_points']} | "
              f"Elapsed: {elapsed}s | "
              f"ETA: {progress['estimated_remaining']}s", end="")
        
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("Wizard completed!")
    
    # Analyze results
    curve_result = await rpc.get_frequency_curve(0)
    if curve_result["success"]:
        curve = curve_result["curve"]
        points = curve["points"]
        
        # Calculate statistics
        stable_points = [p for p in points if p["stable"]]
        voltages = [p["voltage_mv"] for p in stable_points]
        
        print(f"\nResults:")
        print(f"  Total points: {len(points)}")
        print(f"  Stable points: {len(stable_points)}")
        print(f"  Average voltage: {sum(voltages) / len(voltages):.1f} mV")
        print(f"  Min voltage: {min(voltages)} mV")
        print(f"  Max voltage: {max(voltages)} mV")

await advanced_wizard_with_progress(rpc)
```


### Example 3: Multi-Core Curve Generation

Generate curves for multiple CPU cores sequentially:

```python
async def generate_multi_core_curves(rpc, core_ids=[0, 1, 2, 3]):
    """Generate frequency curves for multiple cores."""
    
    curves = {}
    
    for core_id in core_ids:
        print(f"\n{'='*60}")
        print(f"Generating curve for Core {core_id}")
        print(f"{'='*60}")
        
        # Start wizard for this core
        config = {
            "core_id": core_id,
            "preset": "balanced"
        }
        
        result = await rpc.start_frequency_wizard(config)
        if not result["success"]:
            print(f"Failed to start wizard for core {core_id}: {result['error']}")
            continue
        
        # Wait for completion
        while True:
            progress = await rpc.get_frequency_wizard_progress()
            if not progress["running"]:
                break
            
            print(f"\rCore {core_id}: {progress['progress_percent']:.1f}%", end="")
            await asyncio.sleep(2.0)
        
        print()  # New line
        
        # Get curve
        curve_result = await rpc.get_frequency_curve(core_id)
        if curve_result["success"]:
            curves[str(core_id)] = curve_result["curve"]
            print(f"✓ Core {core_id} curve generated")
        else:
            print(f"✗ Failed to get curve for core {core_id}")
    
    # Apply all curves at once
    if curves:
        print(f"\nApplying curves for {len(curves)} cores...")
        result = await rpc.apply_frequency_curve(curves)
        
        if result["success"]:
            print("✓ All curves applied successfully")
            
            # Enable frequency mode
            await rpc.enable_frequency_mode()
            print("✓ Frequency-based mode enabled")
        else:
            print(f"✗ Failed to apply curves: {result['error']}")
    
    return curves

# Generate curves for all cores
curves = await generate_multi_core_curves(rpc)
```


### Example 4: Curve Export and Import

Save and load frequency curves for backup or sharing:

```python
import json
from pathlib import Path

async def export_curves(rpc, output_file="frequency_curves.json"):
    """Export all frequency curves to a JSON file."""
    
    # Get curves for all cores
    all_curves = {}
    
    for core_id in range(4):  # Assuming 4 cores
        result = await rpc.get_frequency_curve(core_id)
        
        if result["success"]:
            all_curves[str(core_id)] = result["curve"]
    
    if not all_curves:
        print("No curves to export")
        return False
    
    # Save to file
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(all_curves, f, indent=2)
    
    print(f"Exported {len(all_curves)} curves to {output_path}")
    return True

async def import_curves(rpc, input_file="frequency_curves.json"):
    """Import frequency curves from a JSON file."""
    
    # Load from file
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return False
    
    with open(input_path, 'r') as f:
        curves = json.load(f)
    
    # Validate and apply curves
    result = await rpc.apply_frequency_curve(curves)
    
    if result["success"]:
        print(f"Imported and applied {len(curves)} curves")
        return True
    else:
        print(f"Failed to import curves: {result['error']}")
        return False

# Export current curves
await export_curves(rpc, "my_curves_backup.json")

# Import curves from file
await import_curves(rpc, "my_curves_backup.json")
```


### Example 5: Wizard Cancellation with Cleanup

Properly handle wizard cancellation and cleanup:

```python
async def cancellable_wizard(rpc):
    """Run wizard with user cancellation support."""
    
    import signal
    
    # Flag for cancellation
    cancelled = False
    
    def signal_handler(sig, frame):
        nonlocal cancelled
        cancelled = True
        print("\n\nCancellation requested...")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start wizard
        config = {"core_id": 0, "preset": "balanced"}
        result = await rpc.start_frequency_wizard(config)
        
        if not result["success"]:
            print(f"Failed to start: {result['error']}")
            return
        
        print("Wizard running... Press Ctrl+C to cancel")
        
        # Monitor progress
        while True:
            # Check for cancellation
            if cancelled:
                print("Cancelling wizard...")
                cancel_result = await rpc.cancel_frequency_wizard()
                
                if cancel_result["success"]:
                    print("✓ Wizard cancelled successfully")
                else:
                    print(f"✗ Cancellation failed: {cancel_result['error']}")
                
                break
            
            # Get progress
            progress = await rpc.get_frequency_wizard_progress()
            
            if not progress["running"]:
                print("\n✓ Wizard completed!")
                break
            
            print(f"\rProgress: {progress['progress_percent']:.1f}%", end="")
            await asyncio.sleep(1.0)
    
    finally:
        # Restore signal handler
        signal.signal(signal.SIGINT, signal.SIG_DFL)

await cancellable_wizard(rpc)
```

---


## Error Codes

### Configuration Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `ERR_INVALID_CONFIG` | Configuration validation failed | Check parameter ranges and types |
| `ERR_INVALID_PRESET` | Unknown preset name | Use "quick", "balanced", or "thorough" |
| `ERR_FREQ_RANGE` | Invalid frequency range | Ensure freq_start < freq_end, both in 400-3500 MHz |
| `ERR_FREQ_STEP` | Invalid frequency step | Use value between 50-500 MHz |
| `ERR_TEST_DURATION` | Invalid test duration | Use value between 10-120 seconds |
| `ERR_VOLTAGE_RANGE` | Invalid voltage range | Ensure voltage_start in -100 to 0 mV |
| `ERR_VOLTAGE_STEP` | Invalid voltage step | Use value between 1-10 mV |
| `ERR_SAFETY_MARGIN` | Invalid safety margin | Use value between 0-20 mV |

### Runtime Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `ERR_OPERATION_RUNNING` | Another operation is active | Wait for completion or cancel current operation |
| `ERR_NOT_RUNNING` | No wizard is running | Start wizard before calling this method |
| `ERR_PERMISSION_DENIED` | Insufficient permissions | Run with root/sudo access |
| `ERR_UNSUPPORTED` | Feature not supported | Check CPU and kernel support for cpufreq |
| `ERR_HARDWARE_ERROR` | Hardware access failed | Check system logs, verify hardware compatibility |

### Data Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `ERR_NOT_FOUND` | Curve not found | Generate curve first using wizard |
| `ERR_INVALID_CURVE` | Curve validation failed | Check voltage range and frequency order |
| `ERR_INVALID_FORMAT` | Malformed data | Verify JSON structure matches specification |
| `ERR_NO_CURVES` | No curves loaded | Load or generate curves before enabling mode |
| `ERR_INVALID_CORE` | Invalid core ID | Use valid core ID (0-based, typically 0-3) |

### Safety Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `ERR_TEMPERATURE_ABORT` | Temperature exceeded 85°C | Allow system to cool, check cooling solution |
| `ERR_TEST_TIMEOUT` | Test exceeded timeout | Check system stability, reduce test duration |
| `ERR_CONSECUTIVE_FAILURES` | Too many test failures | Reduce voltage aggressiveness, check system |
| `ERR_VERIFICATION_FAILED` | Curve verification failed | Regenerate curve with more conservative settings |


---

## Best Practices

### 1. Configuration Selection

**For Quick Testing (10-15 minutes):**
```python
config = {"preset": "quick"}
# Or manually:
config = {
    "freq_step": 200,
    "test_duration": 15,
    "adaptive_step": True
}
```

**For Balanced Testing (20-30 minutes):**
```python
config = {"preset": "balanced"}
# Or manually:
config = {
    "freq_step": 100,
    "test_duration": 30,
    "adaptive_step": True
}
```

**For Thorough Testing (45-60 minutes):**
```python
config = {"preset": "thorough"}
# Or manually:
config = {
    "freq_step": 50,
    "test_duration": 60,
    "adaptive_step": False
}
```

### 2. Progress Monitoring

- Poll progress every 1-2 seconds (not more frequently)
- Display progress percentage and ETA to users
- Handle wizard completion gracefully
- Implement timeout detection for stuck wizards

### 3. Error Handling

- Always check `success` field in responses
- Implement retry logic for transient errors
- Provide clear error messages to users
- Log errors for debugging

### 4. Curve Management

- Export curves after generation for backup
- Validate curves before applying
- Test curves in safe environments first
- Keep multiple curve profiles for different scenarios

### 5. Safety Considerations

- Start with conservative presets ("quick" or "balanced")
- Monitor system temperature during testing
- Test during low system load
- Keep safety margin at 5mV or higher
- Verify curves with real workloads before daily use


### 6. Performance Optimization

- Use adaptive stepping for faster curve generation
- Test during idle periods to avoid interference
- Consider parallel core testing if hardware supports it
- Cache frequency readings to reduce sysfs overhead

### 7. Integration Patterns

**Pattern 1: One-Time Setup**
```python
# Generate curve once, use indefinitely
await generate_and_apply_curve(rpc)
await export_curves(rpc, "production_curves.json")
```

**Pattern 2: Per-Game Profiles**
```python
# Generate different curves for different games
game_curves = {}
for game in ["cyberpunk", "elden_ring", "baldurs_gate"]:
    curve = await generate_curve_for_game(rpc, game)
    game_curves[game] = curve
```

**Pattern 3: Periodic Re-calibration**
```python
# Regenerate curves monthly to account for silicon aging
if should_recalibrate():
    await generate_and_apply_curve(rpc)
```

---

## Troubleshooting

### Wizard Won't Start

**Symptom:** `start_frequency_wizard` returns `ERR_PERMISSION_DENIED`

**Solution:**
```bash
# Ensure DeckTune is running with root privileges
sudo systemctl restart plugin_loader
```

### Wizard Stuck at 0%

**Symptom:** Progress remains at 0% for extended period

**Possible Causes:**
1. CPU frequency locking not working
2. Test runner not starting
3. Permission issues

**Solution:**
```python
# Cancel and check system logs
await rpc.cancel_frequency_wizard()

# Check cpufreq support
import subprocess
result = subprocess.run(["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"], 
                       capture_output=True, text=True)
print(f"Governor: {result.stdout}")
```

### Curves Not Applied

**Symptom:** `enable_frequency_mode` succeeds but voltage doesn't change

**Possible Causes:**
1. Curves not loaded properly
2. Frequency controller not active
3. Conflicting voltage control mode

**Solution:**
```python
# Verify curves are loaded
for core_id in range(4):
    result = await rpc.get_frequency_curve(core_id)
    if result["success"]:
        print(f"Core {core_id}: {len(result['curve']['points'])} points")
    else:
        print(f"Core {core_id}: No curve")

# Disable other modes first
await rpc.disable_undervolt()
await rpc.enable_frequency_mode()
```


### High Temperature Abort

**Symptom:** Wizard aborts with temperature error

**Solution:**
1. Allow system to cool down (10-15 minutes)
2. Check cooling solution (fan, thermal paste)
3. Reduce test duration or use "quick" preset
4. Test in cooler environment

### Verification Tests Fail

**Symptom:** Wizard completes but verification tests fail

**Solution:**
```python
# Regenerate with more conservative settings
config = {
    "preset": "balanced",
    "safety_margin": 10,  # Increase safety margin
    "voltage_start": -25  # Start with less aggressive voltage
}
await rpc.start_frequency_wizard(config)
```

---

## API Versioning

Current API Version: **1.0**

### Version History

**v1.0 (2024-01)**
- Initial release
- Core wizard functionality
- Basic curve management
- Frequency mode control

### Compatibility

- **Minimum DeckTune Version:** 3.2.0
- **Python Version:** 3.8+
- **Kernel Requirements:** Linux 4.0+ with cpufreq support
- **Hardware Requirements:** AMD Ryzen processor with ryzenadj support

---

## Additional Resources

### Related Documentation

- [Frequency Wizard User Guide](FREQUENCY_WIZARD_GUIDE.md) - End-user documentation
- [DeckTune User Guide](USER_GUIDE.md) - General DeckTune documentation
- [Dynamic Manual Mode API](DYNAMIC_MANUAL_MODE_API.md) - Load-based voltage control

### External References

- [Linux cpufreq Documentation](https://www.kernel.org/doc/html/latest/admin-guide/pm/cpufreq.html)
- [ryzenadj GitHub](https://github.com/FlyGoat/RyzenAdj)
- [AMD Ryzen Undervolting Guide](https://github.com/FlyGoat/RyzenAdj/wiki)

### Support

For issues, questions, or contributions:
- GitHub Issues: [DeckTune Issues](https://github.com/your-repo/decktune/issues)
- Discord: [DeckTune Community](https://discord.gg/your-invite)
- Documentation: [DeckTune Docs](https://your-docs-site.com)

---

## License

This API documentation is part of DeckTune and is licensed under the same terms as the main project.

Copyright © 2024 DeckTune Contributors

