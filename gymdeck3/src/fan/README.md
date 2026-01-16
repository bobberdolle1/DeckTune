# Fan Control Module

Low-level fan control for Steam Deck via hwmon sysfs interface.

## Features

- **Automatic hwmon discovery**: Finds jupiter/galileo fan controller
- **Temperature-based curves**: Linear interpolation between points
- **Hysteresis**: Prevents rapid speed changes on small temp fluctuations (±2°C default)
- **Smoothing**: Moving average over 5 samples for gradual transitions
- **Safety overrides**: 
  - 90°C+ forces 100% PWM (critical)
  - 85°C+ enforces minimum 80% PWM (high)
- **Fail-safe**: Drop trait returns control to BIOS

## Usage

```rust
use gymdeck3::fan::{FanController, FanCurve, FanMode};

// Create controller (auto-discovers hwmon device)
let mut controller = FanController::new()?;

// Set custom curve
let curve = FanCurve::from_tuples(vec![
    (40, 0),    // 40°C -> 0% (Zero RPM)
    (50, 30),   // 50°C -> 30%
    (70, 60),   // 70°C -> 60%
    (85, 100),  // 85°C -> 100%
])?;
controller.set_curve(curve);

// Enable manual control
controller.enable()?;

// In main loop (every 500ms)
loop {
    let pwm = controller.update()?;
    // pwm is the applied value (0-255)
    
    tokio::time::sleep(Duration::from_millis(500)).await;
}

// On shutdown, Drop returns control to BIOS automatically
```

## Safety

The module enforces hard safety limits that cannot be bypassed:

| Temperature | Action |
|-------------|--------|
| ≥90°C | Force 100% PWM immediately |
| ≥85°C | Minimum 80% PWM |
| ≤45°C | Zero RPM allowed (if enabled) |

## Sysfs Interface

Steam Deck fan control uses standard hwmon interface:

```
/sys/class/hwmon/hwmonX/
├── name           # "jupiter" or "galileo"
├── pwm1           # PWM value (0-255)
├── pwm1_enable    # 1=manual, 2=auto (BIOS)
├── temp1_input    # Temperature in millidegrees
└── fan1_input     # RPM (optional)
```

## Integration with gymdeck3

The fan module integrates into the main gymdeck3 loop:

1. Read temperature via `controller.update()`
2. Curve calculates target speed
3. Safety checks apply overrides
4. Hysteresis prevents hunting
5. Smoothing averages recent values
6. PWM written to sysfs (if changed significantly)

## Testing

```bash
# Run fan module tests
cargo test --lib fan

# Run property-based tests (requires Linux or cross-compile)
cargo test --test fan_test
```
