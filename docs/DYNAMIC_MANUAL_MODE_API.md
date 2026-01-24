# Dynamic Manual Mode RPC API Documentation

## Overview

The Dynamic Manual Mode RPC API provides methods for configuring and controlling per-core dynamic voltage curves. All methods follow the JSON-RPC protocol and return structured responses with success/error status.

## Base Protocol

### Request Format
```json
{
  "method": "string",
  "params": {
    // Method-specific parameters
  }
}
```

### Response Format
```json
{
  "success": boolean,
  "data": object | null,
  "error": string | null
}
```

## RPC Methods

### 1. get_dynamic_config

Retrieves the current dynamic mode configuration for all CPU cores.

**Method:** `get_dynamic_config`

**Parameters:** None

**Returns:**
```typescript
{
  success: true,
  data: {
    mode: 'simple' | 'expert',
    cores: [
      {
        core_id: number,      // 0-3
        min_mv: number,       // -100 to 0
        max_mv: number,       // -100 to 0
        threshold: number     // 0 to 100
      },
      // ... for each core
    ],
    version: number
  }
}
```

**Example Request:**
```json
{
  "method": "get_dynamic_config",
  "params": {}
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "mode": "expert",
    "cores": [
      { "core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 1, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 2, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 3, "min_mv": -30, "max_mv": -15, "threshold": 50 }
    ],
    "version": 1
  }
}
```

**Error Codes:**
- `config_load_failed`: Unable to load configuration from storage
- `invalid_config_format`: Configuration file is corrupted

---

### 2. set_dynamic_core_config

Updates the configuration for a specific CPU core.

**Method:** `set_dynamic_core_config`

**Parameters:**
```typescript
{
  core_id: number,      // 0-3
  min_mv: number,       // -100 to 0
  max_mv: number,       // -100 to 0
  threshold: number     // 0 to 100
}
```

**Returns:**
```typescript
{
  success: boolean,
  data: null,
  error: string | null
}
```

**Example Request:**
```json
{
  "method": "set_dynamic_core_config",
  "params": {
    "core_id": 0,
    "min_mv": -35,
    "max_mv": -20,
    "threshold": 60
  }
}
```

**Example Response (Success):**
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

**Example Response (Error):**
```json
{
  "success": false,
  "data": null,
  "error": "Validation failed: min_mv (-35) must be <= max_mv (-40)"
}
```

**Validation Rules:**
- `core_id` must be 0-3
- `min_mv` must be -100 to 0
- `max_mv` must be -100 to 0
- `min_mv` must be ≤ `max_mv`
- `threshold` must be 0 to 100

**Error Codes:**
- `invalid_core_id`: Core ID out of range
- `invalid_voltage_range`: Voltage outside -100 to 0 mV
- `min_max_order_violation`: min_mv > max_mv
- `invalid_threshold`: Threshold outside 0-100%
- `platform_limit_exceeded`: Voltage exceeds hardware limits

---

### 3. get_dynamic_curve_data

Returns the calculated voltage curve points for visualization.

**Method:** `get_dynamic_curve_data`

**Parameters:**
```typescript
{
  core_id: number       // 0-3
}
```

**Returns:**
```typescript
{
  success: true,
  data: {
    core_id: number,
    points: [
      {
        load: number,      // 0-100
        voltage: number    // -100 to 0
      },
      // ... 101 points total (load 0 to 100)
    ]
  }
}
```

**Example Request:**
```json
{
  "method": "get_dynamic_curve_data",
  "params": {
    "core_id": 0
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "core_id": 0,
    "points": [
      { "load": 0, "voltage": -30 },
      { "load": 1, "voltage": -30 },
      // ... points 2-49 all -30
      { "load": 50, "voltage": -30 },
      { "load": 51, "voltage": -29.7 },
      { "load": 52, "voltage": -29.4 },
      // ... interpolated values
      { "load": 99, "voltage": -15.3 },
      { "load": 100, "voltage": -15 }
    ]
  }
}
```

**Curve Calculation Formula:**
```
voltage(load) = {
  min_mv                                          if load <= threshold
  min_mv + (max_mv - min_mv) * 
    (load - threshold) / (100 - threshold)        if load > threshold
}
```

**Error Codes:**
- `invalid_core_id`: Core ID out of range
- `config_not_found`: No configuration exists for core

---

### 4. start_dynamic_mode

Activates dynamic voltage adjustment with the current configuration.

**Method:** `start_dynamic_mode`

**Parameters:**
```typescript
{
  config: {
    mode: 'simple' | 'expert',
    cores: CoreConfig[]
  }
}
```

**Returns:**
```typescript
{
  success: boolean,
  data: {
    active: boolean,
    cores_configured: number
  },
  error: string | null
}
```

**Example Request:**
```json
{
  "method": "start_dynamic_mode",
  "params": {
    "config": {
      "mode": "simple",
      "cores": [
        { "core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50 },
        { "core_id": 1, "min_mv": -30, "max_mv": -15, "threshold": 50 },
        { "core_id": 2, "min_mv": -30, "max_mv": -15, "threshold": 50 },
        { "core_id": 3, "min_mv": -30, "max_mv": -15, "threshold": 50 }
      ]
    }
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "active": true,
    "cores_configured": 4
  },
  "error": null
}
```

**Behavior:**
- Validates all core configurations before activation
- Applies configurations to gymdeck3 voltage controller
- Starts real-time load monitoring and voltage adjustment
- Returns error if any core configuration is invalid

**Error Codes:**
- `validation_failed`: One or more core configs invalid
- `gymdeck3_unavailable`: Backend daemon not running
- `hardware_error`: Failed to apply voltage to hardware
- `already_active`: Dynamic mode already running

---

### 5. stop_dynamic_mode

Deactivates dynamic voltage adjustment and resets voltages to 0.

**Method:** `stop_dynamic_mode`

**Parameters:** None

**Returns:**
```typescript
{
  success: boolean,
  data: {
    active: boolean
  },
  error: string | null
}
```

**Example Request:**
```json
{
  "method": "stop_dynamic_mode",
  "params": {}
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "active": false
  },
  "error": null
}
```

**Behavior:**
- Stops load monitoring
- Resets all core voltages to 0 mV (safe default)
- Clears active configuration from gymdeck3
- Always succeeds even if not currently active

**Error Codes:**
- `gymdeck3_unavailable`: Backend daemon not responding
- `reset_failed`: Failed to reset voltages to 0

---

### 6. get_core_metrics

Retrieves real-time metrics for a specific CPU core.

**Method:** `get_core_metrics`

**Parameters:**
```typescript
{
  core_id: number       // 0-3
}
```

**Returns:**
```typescript
{
  success: true,
  data: {
    core_id: number,
    load: number,           // 0-100 (percentage)
    voltage: number,        // Current voltage offset in mV
    frequency: number,      // Current frequency in MHz
    temperature: number,    // Current temperature in °C
    timestamp: number       // Unix timestamp (milliseconds)
  }
}
```

**Example Request:**
```json
{
  "method": "get_core_metrics",
  "params": {
    "core_id": 0
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "core_id": 0,
    "load": 45.2,
    "voltage": -28,
    "frequency": 2800,
    "temperature": 62.5,
    "timestamp": 1706140800000
  }
}
```

**Polling Recommendations:**
- Poll every 500ms for real-time updates
- Stop polling when component unmounts or mode is inactive
- Buffer last 60 data points for time-series visualization
- Handle missing data gracefully (metrics may be unavailable)

**Error Codes:**
- `invalid_core_id`: Core ID out of range
- `metrics_unavailable`: Unable to read hardware metrics
- `mode_inactive`: Dynamic mode not running

---

## Error Handling

### Error Response Structure
```typescript
{
  success: false,
  data: null,
  error: string  // Human-readable error message
}
```

### Common Error Scenarios

**1. Connection Timeout**
```json
{
  "success": false,
  "data": null,
  "error": "RPC timeout: Backend did not respond within 5000ms"
}
```

**Frontend Handling:**
- Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- Display error banner after retries exhausted
- Disable controls until connection restored

**2. Validation Error**
```json
{
  "success": false,
  "data": null,
  "error": "Validation failed: min_mv (-35) must be <= max_mv (-40)"
}
```

**Frontend Handling:**
- Display inline error message near affected control
- Disable Apply button until validation passes
- Highlight invalid fields in red

**3. Hardware Error**
```json
{
  "success": false,
  "data": null,
  "error": "Hardware error: Failed to write to sysfs: Permission denied"
}
```

**Frontend Handling:**
- Display error dialog with troubleshooting steps
- Suggest running with elevated permissions
- Offer "Restore Last Stable" option

---

## Configuration Storage

### localStorage Format
```json
{
  "dynamicMode": {
    "mode": "expert",
    "cores": [
      { "core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 1, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 2, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 3, "min_mv": -30, "max_mv": -15, "threshold": 50 }
    ],
    "version": 1,
    "lastUpdated": 1706140800000
  }
}
```

### Backend Settings Format
```json
{
  "dynamic_manual_mode": {
    "mode": "expert",
    "cores": [
      { "core_id": 0, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 1, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 2, "min_mv": -30, "max_mv": -15, "threshold": 50 },
      { "core_id": 3, "min_mv": -30, "max_mv": -15, "threshold": 50 }
    ],
    "version": 1,
    "last_updated": 1706140800
  }
}
```

**Storage Location:** `~/homebrew/settings/decktune/settings.json`

**Persistence Strategy:**
1. Save to localStorage on Apply (immediate)
2. Save to backend settings on Apply (persistent)
3. Load from localStorage on mount (fast)
4. Fallback to backend settings if localStorage empty
5. Use safe defaults if both empty

---

## Rate Limiting

### Polling Limits
- **get_core_metrics**: Maximum 2 requests/second per core
- **get_dynamic_curve_data**: Maximum 10 requests/second
- **get_dynamic_config**: Maximum 10 requests/second

### Configuration Updates
- **set_dynamic_core_config**: Maximum 10 requests/second
- **start_dynamic_mode**: Maximum 1 request/second
- **stop_dynamic_mode**: Maximum 1 request/second

**Exceeding Limits:**
```json
{
  "success": false,
  "data": null,
  "error": "Rate limit exceeded: Maximum 2 requests/second for get_core_metrics"
}
```

---

## Security Considerations

### Input Validation
- All voltage values clamped to -100 to 0 mV
- All threshold values clamped to 0 to 100%
- Core IDs validated against platform core count
- Configuration version checked for compatibility

### Platform Limits
- Hardware-specific limits enforced by backend
- LCD (Jupiter): -100mV minimum
- OLED (Galileo): -100mV minimum
- Limits retrieved from platform detection module

### Permission Requirements
- Read access to `/proc/stat` for load monitoring
- Write access to hwmon sysfs for voltage control
- Read access to hwmon sysfs for metrics
- Typically requires root or specific udev rules

---

## Migration and Versioning

### Configuration Version
Current version: `1`

### Version 1 Schema
```typescript
interface DynamicConfigV1 {
  mode: 'simple' | 'expert';
  cores: CoreConfig[];
  version: 1;
}
```

### Future Migrations
When schema changes occur:
1. Backend detects old version number
2. Applies migration transformations
3. Updates version to current
4. Saves migrated configuration
5. Returns migrated config to frontend

**Example Migration (v1 → v2):**
```python
def migrate_v1_to_v2(config_v1):
    config_v2 = {
        'mode': config_v1['mode'],
        'cores': config_v1['cores'],
        'version': 2,
        'hysteresis': 5.0  # New field in v2
    }
    return config_v2
```

---

## Testing

### RPC Method Testing
All RPC methods have property-based tests:
- **Property 20**: RPC configuration round-trip
- **Property 21**: RPC curve data consistency
- **Property 22**: RPC metrics completeness

### Test Coverage
- Unit tests: 90%+ backend coverage
- Integration tests: Full workflow end-to-end
- Property tests: 100 iterations per property

### Example Test (pytest + hypothesis)
```python
from hypothesis import given, strategies as st

@given(
    core_id=st.integers(min_value=0, max_value=3),
    min_mv=st.integers(min_value=-100, max_value=0),
    max_mv=st.integers(min_value=-100, max_value=0),
    threshold=st.integers(min_value=0, max_value=100)
)
def test_rpc_config_roundtrip(core_id, min_mv, max_mv, threshold):
    """Property 20: RPC configuration round-trip"""
    # Assume min_mv <= max_mv for valid configs
    if min_mv > max_mv:
        min_mv, max_mv = max_mv, min_mv
    
    # Set config
    response = rpc.set_dynamic_core_config(
        core_id=core_id,
        min_mv=min_mv,
        max_mv=max_mv,
        threshold=threshold
    )
    assert response['success']
    
    # Get config
    config = rpc.get_dynamic_config()
    core_config = config['data']['cores'][core_id]
    
    # Verify round-trip
    assert core_config['min_mv'] == min_mv
    assert core_config['max_mv'] == max_mv
    assert core_config['threshold'] == threshold
```

---

## Changelog

### v3.2.0 (2026-01-24)
- Initial release of Dynamic Manual Mode RPC API
- Added 6 RPC methods for configuration and control
- Implemented per-core voltage curve support
- Added real-time metrics polling
- Integrated with gymdeck3 backend

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/bobberdolle1/DeckTune/issues
- Documentation: https://github.com/bobberdolle1/DeckTune/docs
- User Guide: docs/USER_GUIDE.md
