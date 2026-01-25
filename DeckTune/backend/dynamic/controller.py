"""Dynamic mode controller for gymdeck3 subprocess management.

This module provides the `DynamicController` class which manages the lifecycle
of the gymdeck3 Rust binary subprocess. It handles:

- Starting/stopping the gymdeck3 process with proper configuration
- Parsing JSON status output from gymdeck3 stdout
- Emitting events to the frontend for real-time status updates
- Graceful shutdown with SIGTERM for value reset
- Error handling and process crash detection

Feature: dynamic-mode-refactor
Validates: Requirements 10.1-10.6

# Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DynamicController                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   start()    │  │   stop()     │  │ get_status() │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         ▼                 ▼                  ▼          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         gymdeck3 subprocess                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────┐  │   │
│  │  │ LoadMonitor│─►│ Adaptation │─►│ Ryzenadj  │  │   │
│  │  └────────────┘  └────────────┘  └───────────┘  │   │
│  │         │                                        │   │
│  │         ▼                                        │   │
│  │  ┌────────────────────────────────────────┐     │   │
│  │  │  JSON stdout (NDJSON)                  │     │   │
│  │  │  {"type":"status","load":[...],...}    │────►│   │
│  │  └────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│              ┌──────────────────┐                       │
│              │  _read_output()  │                       │
│              │  (async task)    │                       │
│              └────────┬─────────┘                       │
│                       │                                 │
│                       ▼                                 │
│              ┌──────────────────┐                       │
│              │  EventEmitter    │                       │
│              │  (to frontend)   │                       │
│              └──────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

# Usage Example

```python
from backend.dynamic.controller import DynamicController
from backend.dynamic.config import DynamicConfig
from backend.api.events import EventEmitter

# Initialize controller
controller = DynamicController(
    ryzenadj_path="/path/to/ryzenadj",
    gymdeck3_path="/path/to/gymdeck3",
    event_emitter=event_emitter,
)

# Start dynamic mode
config = DynamicConfig(strategy="balanced")
success = await controller.start(config)

# Check status
status = await controller.get_status()
print(f"Running: {status.running}, Load: {status.load}")

# Stop gracefully
await controller.stop()
```

# Signal Handling

- **SIGTERM**: Sent to gymdeck3 for graceful shutdown (resets values to 0)
- **SIGUSR1**: Forces immediate status output from gymdeck3

# Error Handling

The controller handles various error conditions:
- Binary not found: Emits error event, returns False from start()
- Process crashes: Detected in _read_output(), emits error event
- Invalid config: Validated before starting, returns False if invalid
- Timeout on stop: Kills process after 5 seconds if SIGTERM doesn't work
"""

import asyncio
import json
import logging
import os
import signal
import time
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .config import DynamicConfig, DynamicStatus

if TYPE_CHECKING:
    from ..api.events import EventEmitter
    from ..api.stream import StatusStreamManager
    from ..core.safety import SafetyManager
    from ..core.blackbox import BlackBox, MetricSample
    from ..core.telemetry import TelemetryManager, TelemetrySample
    from ..core.session_manager import SessionManager, Session

logger = logging.getLogger(__name__)


class DynamicController:
    """Controller for gymdeck3 dynamic mode subprocess.
    
    Manages the lifecycle of the gymdeck3 Rust binary, parses its
    JSON status output, and emits events to the frontend.
    
    Requirements: 10.1-10.6
    Feature: decktune-3.0-automation
    Validates: Requirements 3.1, 3.2
    """
    
    def __init__(
        self,
        ryzenadj_path: str,
        gymdeck3_path: str,
        event_emitter: "EventEmitter",
        safety_manager: Optional["SafetyManager"] = None,
        blackbox: Optional["BlackBox"] = None,
        telemetry_manager: Optional["TelemetryManager"] = None,
        session_manager: Optional["SessionManager"] = None,
        status_stream_manager: Optional["StatusStreamManager"] = None,
    ):
        """Initialize the dynamic controller.
        
        Args:
            ryzenadj_path: Path to ryzenadj binary
            gymdeck3_path: Path to gymdeck3 binary
            event_emitter: EventEmitter for frontend communication
            safety_manager: Optional SafetyManager for LKG persistence
            blackbox: Optional BlackBox for metrics recording
            telemetry_manager: Optional TelemetryManager for telemetry collection
            session_manager: Optional SessionManager for session tracking
            status_stream_manager: Optional StatusStreamManager for SSE status updates
        """
        self._ryzenadj_path = ryzenadj_path
        self._gymdeck3_path = gymdeck3_path
        self._event_emitter = event_emitter
        self._safety_manager = safety_manager
        self._blackbox = blackbox
        self._telemetry_manager = telemetry_manager
        self._session_manager = session_manager
        self._status_stream_manager = status_stream_manager
        
        self._process: Optional[asyncio.subprocess.Process] = None
        self._config: Optional[DynamicConfig] = None
        self._status = DynamicStatus()
        self._reader_task: Optional[asyncio.Task] = None
        self._running = False
        self._current_session_id: Optional[str] = None
    
    def is_running(self) -> bool:
        """Check if gymdeck3 is currently running."""
        return self._running and self._process is not None
    
    def set_blackbox(self, blackbox: "BlackBox") -> None:
        """Set the BlackBox instance for metrics recording.
        
        Args:
            blackbox: BlackBox instance for recording metrics
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.1
        """
        self._blackbox = blackbox
    
    def set_telemetry_manager(self, telemetry_manager: "TelemetryManager") -> None:
        """Set the TelemetryManager instance for telemetry collection.
        
        Args:
            telemetry_manager: TelemetryManager instance for recording telemetry
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 2.1, 2.2
        """
        self._telemetry_manager = telemetry_manager
    
    def set_session_manager(self, session_manager: "SessionManager") -> None:
        """Set the SessionManager instance for session tracking.
        
        Args:
            session_manager: SessionManager instance for tracking sessions
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.1, 8.2
        """
        self._session_manager = session_manager
    
    def set_status_stream_manager(self, status_stream_manager: "StatusStreamManager") -> None:
        """Set the StatusStreamManager instance for SSE status updates.
        
        Args:
            status_stream_manager: StatusStreamManager instance for streaming status
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 4.1, 4.2, 4.3, 4.4
        """
        self._status_stream_manager = status_stream_manager
    
    async def start(self, config: DynamicConfig) -> bool:
        """Start gymdeck3 with the given configuration.
        
        Args:
            config: Dynamic mode configuration
            
        Returns:
            True if started successfully, False otherwise
        """
        # Validate configuration
        errors = config.validate()
        if errors:
            logger.error(f"Invalid config: {errors}")
            await self._event_emitter.emit_status("error")
            return False
        
        # Stop existing process if running
        if self.is_running():
            await self.stop()
        
        # Check binary exists
        if not Path(self._gymdeck3_path).exists():
            logger.error(f"gymdeck3 binary not found: {self._gymdeck3_path}")
            await self._event_emitter.emit_status("error")
            return False
        
        # Build command line arguments
        args = self._build_args(config)
        
        try:
            logger.info(f"Starting gymdeck3: {self._gymdeck3_path} {' '.join(args)}")
            
            self._process = await asyncio.create_subprocess_exec(
                self._gymdeck3_path,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            self._config = config
            self._running = True
            self._status = DynamicStatus(running=True, strategy=config.strategy)
            
            # Update status stream manager running state
            # Feature: decktune-3.1-reliability-ux
            # Validates: Requirements 4.3
            if self._status_stream_manager is not None:
                self._status_stream_manager.set_running(True)
            
            # Start reader task for stdout
            self._reader_task = asyncio.create_task(self._read_output())
            
            # Start session tracking
            # Feature: decktune-3.1-reliability-ux
            # Validates: Requirements 8.1
            await self._start_session()
            
            await self._event_emitter.emit_status("dynamic_running")
            logger.info(f"gymdeck3 started with PID {self._process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start gymdeck3: {e}")
            self._running = False
            await self._event_emitter.emit_status("error")
            return False
    
    async def stop(self) -> bool:
        """Stop gymdeck3 gracefully.
        
        Sends SIGTERM to allow gymdeck3 to reset values to 0 before exit.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_running():
            return True
        
        try:
            logger.info("Stopping gymdeck3...")
            
            # Send SIGTERM for graceful shutdown
            self._process.send_signal(signal.SIGTERM)
            
            # Wait for process to exit (with timeout)
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("gymdeck3 did not exit gracefully, killing...")
                self._process.kill()
                await self._process.wait()
            
            # Cancel reader task
            if self._reader_task:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
                self._reader_task = None
            
            self._process = None
            self._running = False
            self._status = DynamicStatus(running=False)
            
            # Update status stream manager running state
            # Feature: decktune-3.1-reliability-ux
            # Validates: Requirements 4.3
            if self._status_stream_manager is not None:
                self._status_stream_manager.set_running(False)
            
            # End session tracking
            # Feature: decktune-3.1-reliability-ux
            # Validates: Requirements 8.2
            await self._end_session()
            
            await self._event_emitter.emit_status("disabled")
            logger.info("gymdeck3 stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping gymdeck3: {e}")
            self._running = False
            return False
    
    async def get_status(self) -> DynamicStatus:
        """Get current dynamic mode status.
        
        Returns:
            Current DynamicStatus
        """
        # Check if process is still alive
        if self._process is not None and self._process.returncode is not None:
            # Process has exited
            self._running = False
            self._status = DynamicStatus(
                running=False,
                error=f"Process exited with code {self._process.returncode}"
            )
        
        return self._status
    
    async def force_status_output(self) -> None:
        """Send SIGUSR1 to force immediate status output."""
        if self.is_running():
            try:
                self._process.send_signal(signal.SIGUSR1)
            except Exception as e:
                logger.warning(f"Failed to send SIGUSR1: {e}")
    
    def _build_args(self, config: DynamicConfig) -> list:
        """Build command line arguments for gymdeck3.
        
        Constructs the argument list for launching gymdeck3 with the given
        configuration. Handles both simple mode (single value for all cores)
        and per-core mode (individual settings per core).
        
        Args:
            config: Dynamic mode configuration
            
        Returns:
            List of command line arguments in the format:
            [strategy, sample_interval_us, --hysteresis=X, --ryzenadj-path=Y,
             --status-interval=Z, --core=0:MIN:MAX:THRESHOLD, ...]
             
        Example:
            For a balanced config with simple_mode=True and simple_value=-25:
            ["balanced", "100000", "--hysteresis=5.0", 
             "--ryzenadj-path=/usr/bin/ryzenadj", "--status-interval=1000",
             "--core=0:-25:-25:50.0", "--core=1:-25:-25:50.0", ...]
        """
        args = [
            config.strategy,
            str(config.sample_interval_ms * 1000),  # Convert to microseconds
            f"--hysteresis={config.hysteresis_percent}",
            f"--ryzenadj-path={self._ryzenadj_path}",
            f"--status-interval={config.status_interval_ms}",
        ]
        
        # Get effective values (handles simple_mode propagation)
        effective_values = config.get_effective_core_values()
        
        # Add per-core configuration
        for i, core in enumerate(config.cores):
            if config.simple_mode:
                # In simple mode, use the simple_value for both min and max
                args.append(f"--core={i}:{config.simple_value}:{config.simple_value}:{core.threshold}")
            else:
                # In per-core mode, use individual core settings
                args.append(f"--core={i}:{core.min_mv}:{core.max_mv}:{core.threshold}")
        
        # Add fan control arguments if enabled
        fan = config.fan_config
        if fan.enabled:
            args.append("--fan-control")
            args.append(f"--fan-mode={fan.mode}")
            args.append(f"--fan-hysteresis={fan.hysteresis_temp}")
            
            if fan.zero_rpm_enabled:
                args.append("--fan-zero-rpm")
            
            # Add fan curve points for custom mode
            if fan.mode == "custom" and fan.curve:
                for point in fan.curve:
                    args.append(f"--fan-curve={point.temp_c}:{point.speed_percent}")
        
        return args
    
    async def _read_output(self) -> None:
        """Read and parse JSON output from gymdeck3 stdout."""
        if self._process is None or self._process.stdout is None:
            return
        
        try:
            while self._running:
                line = await self._process.stdout.readline()
                if not line:
                    # EOF - process has exited
                    break
                
                try:
                    data = json.loads(line.decode().strip())
                    await self._handle_json_message(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from gymdeck3: {e}")
                    
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error reading gymdeck3 output: {e}")
        
        # Process has exited
        if self._running:
            self._running = False
            returncode = self._process.returncode if self._process else -1
            logger.warning(f"gymdeck3 exited unexpectedly with code {returncode}")
            self._status = DynamicStatus(
                running=False,
                error=f"Process exited with code {returncode}"
            )
            
            # Update status stream manager running state
            # Feature: decktune-3.1-reliability-ux
            # Validates: Requirements 4.3
            if self._status_stream_manager is not None:
                self._status_stream_manager.set_running(False)
            
            # Persist BlackBox on crash
            # Feature: decktune-3.0-automation, Validates: Requirements 3.2
            await self.persist_blackbox(f"gymdeck3_crash_code_{returncode}")
            
            await self._event_emitter.emit_status("error")
    
    async def _handle_json_message(self, data: dict) -> None:
        """Handle a parsed JSON message from gymdeck3.
        
        Args:
            data: Parsed JSON data
        """
        msg_type = data.get("type", "")
        
        if msg_type == "status":
            self._status = DynamicStatus.from_json_line(data, running=True)
            # Emit dynamic status event to frontend
            await self._emit_dynamic_status()
            # Record sample to BlackBox if available
            self._record_blackbox_sample()
            # Record telemetry sample if available
            await self._record_telemetry_sample()
            
        elif msg_type == "transition":
            # Log transition for debugging
            logger.debug(
                f"Transition: {data.get('from')} -> {data.get('to')} "
                f"({data.get('progress', 0) * 100:.0f}%)"
            )
            
        elif msg_type == "error":
            error_msg = data.get("message", "Unknown error")
            logger.error(f"gymdeck3 error: {error_msg}")
            self._status.error = error_msg
            
        else:
            logger.debug(f"Unknown message type: {msg_type}")
    
    def _record_blackbox_sample(self) -> None:
        """Record current status to BlackBox.
        
        Creates a MetricSample from current status and records it
        to the BlackBox ring buffer.
        
        Feature: decktune-3.0-automation
        Validates: Requirements 3.1
        """
        if self._blackbox is None:
            return
        
        # Import here to avoid circular imports
        from ..core.blackbox import MetricSample
        
        # Get fan data if available
        fan_rpm = 0
        fan_pwm = 0
        temp_c = 0
        if self._status.fan is not None:
            fan_rpm = self._status.fan.rpm or 0
            fan_pwm = self._status.fan.pwm
            temp_c = self._status.fan.temp_c
        
        # Calculate average CPU load
        avg_load = sum(self._status.load) / len(self._status.load) if self._status.load else 0.0
        
        sample = MetricSample(
            timestamp=time.time(),
            temperature_c=temp_c,
            cpu_load_percent=avg_load,
            undervolt_values=self._status.values.copy(),
            fan_speed_rpm=fan_rpm,
            fan_pwm=fan_pwm
        )
        
        self._blackbox.record_sample(sample)
    
    async def _record_telemetry_sample(self) -> None:
        """Record current status to TelemetryManager and emit to frontend.
        
        Creates a TelemetrySample from current status and records it
        to the TelemetryManager buffer. Also emits telemetry event to frontend
        and records to active session.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 2.1, 2.2, 8.1
        """
        # Get temperature from fan data if available
        temp_c = 0.0
        if self._status.fan is not None:
            temp_c = self._status.fan.temp_c
        
        # Calculate average CPU load
        avg_load = sum(self._status.load) / len(self._status.load) if self._status.load else 0.0
        
        # Get power from status (if available, otherwise estimate)
        # Note: Power data may come from ryzenadj or be estimated
        power_w = getattr(self._status, 'power_w', 0.0)
        
        # Record to TelemetryManager if available
        if self._telemetry_manager is not None:
            # Import here to avoid circular imports
            from ..core.telemetry import TelemetrySample
            
            sample = TelemetrySample(
                timestamp=time.time(),
                temperature_c=temp_c,
                power_w=power_w,
                load_percent=avg_load
            )
            
            self._telemetry_manager.record_sample(sample)
            
            # Emit telemetry event to frontend
            await self._event_emitter._emit_event("telemetry_sample", sample.to_dict())
        
        # Record to active session
        # Feature: decktune-3.1-reliability-ux
        # Validates: Requirements 8.1
        self._record_session_sample(temp_c, power_w)
    
    async def persist_blackbox(self, reason: str) -> Optional[str]:
        """Persist BlackBox buffer to disk.
        
        Called when crash or instability is detected.
        
        Args:
            reason: Reason for persistence (e.g., "watchdog_timeout")
            
        Returns:
            Filename of saved recording, or None if save failed
            
        Feature: decktune-3.0-automation
        Validates: Requirements 3.2
        """
        if self._blackbox is None:
            logger.warning("Cannot persist BlackBox: not configured")
            return None
        
        filename = self._blackbox.persist_on_crash(reason)
        if filename:
            logger.info(f"BlackBox persisted: {filename}")
            # Emit event to frontend
            await self._event_emitter._emit_event("blackbox_saved", {
                "filename": filename,
                "reason": reason
            })
        return filename
    
    async def _emit_dynamic_status(self) -> None:
        """Emit dynamic status event to frontend via SSE.
        
        Uses StatusStreamManager for SSE delivery if available,
        falls back to direct event emission otherwise.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 4.1, 4.2
        """
        status_dict = self._status.to_dict()
        
        # Use SSE via StatusStreamManager if available
        # Feature: decktune-3.1-reliability-ux
        # Validates: Requirements 4.1, 4.2
        if self._status_stream_manager is not None:
            await self._status_stream_manager.publish({
                "type": "dynamic_status",
                "data": status_dict
            })
        
        # Also emit via EventEmitter for backward compatibility
        await self._event_emitter._emit_event("dynamic_status", status_dict)
    
    async def _start_session(self) -> None:
        """Start a new session when gymdeck3 starts.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.1
        """
        if self._session_manager is None:
            return
        
        # Get game info from app watcher if available
        game_name = None
        app_id = None
        
        session = self._session_manager.start_session(
            game_name=game_name,
            app_id=app_id
        )
        self._current_session_id = session.id
        logger.info(f"Started session {session.id} for dynamic mode")
    
    async def _end_session(self) -> None:
        """End the current session when gymdeck3 stops.
        
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.2
        """
        if self._session_manager is None or self._current_session_id is None:
            return
        
        metrics = self._session_manager.end_session(self._current_session_id)
        if metrics:
            logger.info(
                f"Ended session {self._current_session_id}, "
                f"duration: {metrics.duration_sec:.1f}s, "
                f"avg_temp: {metrics.avg_temperature_c:.1f}°C"
            )
            # Emit session ended event to frontend
            await self._event_emitter._emit_event("session_ended", {
                "session_id": self._current_session_id,
                "metrics": metrics.to_dict()
            })
        
        self._current_session_id = None
    
    def _record_session_sample(self, temp_c: float, power_w: float) -> None:
        """Record a telemetry sample to the active session.
        
        Args:
            temp_c: Temperature in Celsius
            power_w: Power in Watts
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.1
        """
        if self._session_manager is None or self._current_session_id is None:
            return
        
        self._session_manager.add_sample(
            temperature_c=temp_c,
            power_w=power_w
        )
    
    def get_session_diagnostics(self) -> dict:
        """Get session history for diagnostics export.
        
        Returns:
            Dictionary containing session history summary
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 8.8
        """
        if self._session_manager is None:
            return {"session_count": 0, "active_session": None, "recent_sessions": []}
        
        return self._session_manager.export_for_diagnostics()

    async def subscribe_status(self):
        """Subscribe to status updates via SSE.
        
        Returns an async iterator that yields status events.
        Automatically delivers buffered events on reconnection.
        
        Returns:
            AsyncIterator yielding status event dictionaries, or None if
            StatusStreamManager is not configured
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 4.2, 4.4
        """
        if self._status_stream_manager is None:
            logger.warning("Cannot subscribe to status: StatusStreamManager not configured")
            return None
        
        return self._status_stream_manager.subscribe()
    
    def get_status_stream_manager(self) -> Optional["StatusStreamManager"]:
        """Get the StatusStreamManager instance.
        
        Returns:
            StatusStreamManager instance or None if not configured
            
        Feature: decktune-3.1-reliability-ux
        Validates: Requirements 4.2
        """
        return self._status_stream_manager
