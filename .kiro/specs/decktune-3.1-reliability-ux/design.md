# Design Document: DeckTune 3.1 - Reliability & UX

## Overview

DeckTune 3.1 enhances reliability through crash recovery metrics, session history tracking, and improved frontend-backend communication. UX improvements include real-time telemetry graphs, platform detection caching for faster startup, and a guided setup wizard for new users.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ SetupWizard  │  │TelemetryGraph│  │   SessionHistory     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│           │                │                    │               │
│           └────────────────┼────────────────────┘               │
│                            │ Server-Sent Events                 │
│                            ▼                                    │
├─────────────────────────────────────────────────────────────────┤
│                      Backend (Python)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │CrashMetrics  │  │TelemetryMgr  │  │   SessionManager     │  │
│  │  Manager     │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│           │                │                    │               │
│           ▼                ▼                    ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   PlatformCache                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. CrashMetricsManager

Tracks crash recovery events and maintains history.

```python
@dataclass
class CrashRecord:
    timestamp: str           # ISO 8601
    crashed_values: List[int]  # Values that caused crash
    restored_values: List[int] # LKG values restored
    recovery_reason: str     # "boot_recovery", "watchdog_timeout", etc.
    
@dataclass  
class CrashMetrics:
    total_count: int
    last_crash_date: Optional[str]
    history: List[CrashRecord]  # Max 50 entries

class CrashMetricsManager:
    HISTORY_LIMIT = 50
    
    def record_crash(self, crashed_values, restored_values, reason) -> None
    def get_metrics() -> CrashMetrics
    def export_for_diagnostics() -> dict
```

**Location:** `backend/core/crash_metrics.py`

### 2. TelemetryManager

Collects and buffers real-time temperature and power data.

```python
@dataclass
class TelemetrySample:
    timestamp: float         # Unix timestamp
    temperature_c: float     # CPU temperature
    power_w: float          # Power consumption
    load_percent: float     # CPU load

class TelemetryManager:
    BUFFER_SIZE = 300       # 5 minutes at 1Hz
    SAMPLE_INTERVAL = 1.0   # seconds
    
    def __init__(self):
        self._buffer: deque[TelemetrySample] = deque(maxlen=BUFFER_SIZE)
        
    def record_sample(self, sample: TelemetrySample) -> None
    def get_recent(self, seconds: int = 60) -> List[TelemetrySample]
    def get_all() -> List[TelemetrySample]
```

**Location:** `backend/core/telemetry.py`

### 3. PlatformCache

Caches platform detection results for faster startup.

```python
@dataclass
class CachedPlatform:
    model: str
    variant: str
    safe_limit: int
    cached_at: str          # ISO 8601
    
class PlatformCache:
    CACHE_FILE = "platform_cache.json"
    CACHE_TTL_DAYS = 30
    
    def load() -> Optional[PlatformInfo]
    def save(platform: PlatformInfo) -> None
    def clear() -> None
    def is_valid() -> bool
```

**Location:** `backend/platform/cache.py`

### 4. SessionManager

Tracks gaming sessions with metrics.

```python
@dataclass
class SessionMetrics:
    duration_sec: float
    avg_temperature_c: float
    min_temperature_c: float
    max_temperature_c: float
    avg_power_w: float
    estimated_battery_saved_wh: float
    undervolt_values: List[int]

@dataclass
class Session:
    id: str                  # UUID
    start_time: str          # ISO 8601
    end_time: Optional[str]
    game_name: Optional[str]
    app_id: Optional[int]
    metrics: Optional[SessionMetrics]
    samples: List[TelemetrySample]  # Raw data for graphs

class SessionManager:
    ACTIVE_LIMIT = 100
    ARCHIVE_FILE = "sessions_archive.json"
    
    def start_session(game_name: Optional[str], app_id: Optional[int]) -> Session
    def end_session(session_id: str) -> SessionMetrics
    def get_history(limit: int = 30) -> List[Session]
    def get_session(session_id: str) -> Session
    def compare_sessions(id1: str, id2: str) -> dict
    def archive_old_sessions() -> int  # Returns count archived
```

**Location:** `backend/core/session_manager.py`

### 5. SetupWizard (Frontend)

Guided first-run experience.

```typescript
interface WizardState {
    step: 'welcome' | 'explanation' | 'goal' | 'confirm' | 'complete';
    selectedGoal: 'quiet' | 'balanced' | 'battery' | 'performance' | null;
}

interface GoalEstimate {
    batteryImprovement: string;  // e.g., "+15-25%"
    tempReduction: string;       // e.g., "-5-10°C"
    description: string;
}

const GOAL_ESTIMATES: Record<string, GoalEstimate> = {
    quiet: { batteryImprovement: "+10-15%", tempReduction: "-8-12°C", ... },
    balanced: { batteryImprovement: "+15-20%", tempReduction: "-5-8°C", ... },
    battery: { batteryImprovement: "+20-30%", tempReduction: "-3-5°C", ... },
    performance: { batteryImprovement: "+5-10%", tempReduction: "-2-4°C", ... },
};
```

**Location:** `src/components/SetupWizard.tsx`

### 6. TelemetryGraph (Frontend)

Real-time scrolling graphs for temperature and power.

```typescript
interface TelemetryGraphProps {
    data: TelemetrySample[];
    type: 'temperature' | 'power';
    width: number;
    height: number;
}

// Uses SVG path for smooth line rendering
// Updates every second via SSE
```

**Location:** `src/components/TelemetryGraph.tsx`

### 7. StatusStreamManager

Server-sent events for real-time updates (replaces polling).

```python
class StatusStreamManager:
    MAX_BUFFER = 10
    
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []
        self._buffer: deque = deque(maxlen=MAX_BUFFER)
        
    async def subscribe() -> AsyncIterator[dict]
    async def publish(event: dict) -> None
    def get_buffered() -> List[dict]
```

**Location:** `backend/api/stream.py`

## Data Models

### Crash History Storage

```json
{
    "crash_metrics": {
        "total_count": 5,
        "last_crash_date": "2025-01-15T14:30:00Z",
        "history": [
            {
                "timestamp": "2025-01-15T14:30:00Z",
                "crashed_values": [-35, -35, -35, -35],
                "restored_values": [-25, -25, -25, -25],
                "recovery_reason": "boot_recovery"
            }
        ]
    }
}
```

### Session Storage

```json
{
    "sessions": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T12:30:00Z",
            "game_name": "Elden Ring",
            "app_id": 1245620,
            "metrics": {
                "duration_sec": 9000,
                "avg_temperature_c": 72.5,
                "min_temperature_c": 45.0,
                "max_temperature_c": 85.0,
                "avg_power_w": 18.5,
                "estimated_battery_saved_wh": 2.3,
                "undervolt_values": [-25, -25, -25, -25]
            }
        }
    ]
}
```

### Platform Cache

```json
{
    "model": "Galileo",
    "variant": "OLED", 
    "safe_limit": -35,
    "cached_at": "2025-01-01T00:00:00Z"
}
```

### Wizard Settings

```json
{
    "first_run_complete": false,
    "wizard_goal": null,
    "wizard_completed_at": null
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Crash history FIFO limit
*For any* sequence of crash records added to the history, the history length SHALL never exceed 50 entries, and when the limit is reached, the oldest entry SHALL be removed first.
**Validates: Requirements 1.5**

### Property 2: Crash record completeness
*For any* crash recovery event, the recorded CrashRecord SHALL contain non-null values for timestamp, crashed_values (4 integers), restored_values (4 integers), and recovery_reason.
**Validates: Requirements 1.3**

### Property 3: Telemetry buffer circular behavior
*For any* sequence of telemetry samples added to the buffer, the buffer length SHALL never exceed 300 samples, and adding a sample when full SHALL remove the oldest sample.
**Validates: Requirements 2.5**

### Property 4: Platform cache validity
*For any* cached platform data, if the cache age exceeds 30 days, is_valid() SHALL return False and fresh detection SHALL be performed.
**Validates: Requirements 3.3**

### Property 5: Platform cache corruption resilience
*For any* corrupted or malformed cache file, loading SHALL return None and not raise an exception, allowing fallback to fresh detection.
**Validates: Requirements 3.5**

### Property 6: Session history limit
*For any* sequence of sessions, the active session list SHALL never exceed 100 entries, and excess sessions SHALL be moved to archive.
**Validates: Requirements 8.7**

### Property 7: Session metrics calculation
*For any* completed session with N samples, the calculated metrics SHALL satisfy: min_temp ≤ avg_temp ≤ max_temp, and duration_sec equals (end_time - start_time).
**Validates: Requirements 8.3**

### Property 8: Wizard cancellation safety
*For any* wizard state, cancelling the wizard SHALL not modify any settings or apply any undervolt values.
**Validates: Requirements 5.7**

### Property 9: Status buffer limit
*For any* sequence of status updates when delivery fails, the buffer SHALL not exceed 10 entries, and oldest entries SHALL be dropped when full.
**Validates: Requirements 4.5**

### Property 10: No events when stopped
*For any* state where gymdeck3 is not running, no dynamic_status events SHALL be emitted to subscribers.
**Validates: Requirements 4.3**

### Property 11: Goal estimates availability
*For any* goal selection in the wizard, estimated battery improvement and temperature reduction SHALL be provided.
**Validates: Requirements 5.4**

### Property 12: Fuzzing no-panic guarantee
*For any* byte sequence input to the config parser, the parser SHALL not panic and SHALL return either a valid config or an error.
**Validates: Requirements 6.1, 6.2**

### Property 13: RPC response schema compliance
*For any* RPC method call, the response SHALL match the expected schema with all required fields present.
**Validates: Requirements 7.1**

### Property 14: Error response structure
*For any* RPC error response, the response SHALL contain an error code (string) and message (string).
**Validates: Requirements 7.4**

### Property 15: Session comparison symmetry
*For any* two sessions A and B, compare_sessions(A, B) and compare_sessions(B, A) SHALL produce inverse diff values.
**Validates: Requirements 8.6**

## Error Handling

### Crash Metrics
- File I/O errors: Log warning, continue with in-memory data
- Corrupted history file: Reset to empty history, log error

### Telemetry
- Sensor read failure: Skip sample, log warning
- Buffer overflow: Handled by deque maxlen

### Platform Cache
- Missing file: Fresh detection
- Corrupted JSON: Delete cache, fresh detection
- Permission error: Log warning, fresh detection

### Sessions
- Archive write failure: Keep in active storage, retry later
- Missing session ID: Return None, log warning

### Status Streaming
- Subscriber disconnect: Remove from list, no error
- Publish failure: Buffer event, retry on next publish

## Testing Strategy

### Property-Based Testing (Python - hypothesis)

Tests will use hypothesis to verify correctness properties:

```python
# Example: Property 1 - Crash history FIFO limit
@given(st.lists(crash_record_strategy(), min_size=0, max_size=100))
def test_crash_history_fifo_limit(records):
    manager = CrashMetricsManager()
    for record in records:
        manager.record_crash(...)
    assert len(manager.get_metrics().history) <= 50
```

Minimum 100 iterations per property test.

### Property-Based Testing (Rust - proptest)

Fuzzing for config parsing:

```rust
proptest! {
    #[test]
    fn config_parser_no_panic(input in any::<Vec<u8>>()) {
        let _ = parse_config(&input);  // Should not panic
    }
}
```

### Unit Tests

- CrashMetricsManager: record, retrieve, export, limit enforcement
- TelemetryManager: sample recording, buffer behavior, retrieval
- PlatformCache: save, load, expiration, corruption handling
- SessionManager: start, end, metrics calculation, archival
- SetupWizard: state transitions, cancellation, completion

### Integration Tests

- RPC contract tests: Verify all methods return expected shapes
- Event payload tests: Verify event structure matches TypeScript types
- End-to-end: Wizard completion → settings saved → autotune starts

### Test Annotations

Each property-based test MUST include:
```python
# **Feature: decktune-3.1-reliability-ux, Property {N}: {property_text}**
# **Validates: Requirements X.Y**
```
