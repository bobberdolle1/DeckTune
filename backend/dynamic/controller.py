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
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .config import DynamicConfig, DynamicStatus

if TYPE_CHECKING:
    from ..api.events import EventEmitter
    from ..core.safety import SafetyManager

logger = logging.getLogger(__name__)


class DynamicController:
    """Controller for gymdeck3 dynamic mode subprocess.
    
    Manages the lifecycle of the gymdeck3 Rust binary, parses its
    JSON status output, and emits events to the frontend.
    
    Requirements: 10.1-10.6
    """
    
    def __init__(
        self,
        ryzenadj_path: str,
        gymdeck3_path: str,
        event_emitter: "EventEmitter",
        safety_manager: Optional["SafetyManager"] = None,
    ):
        """Initialize the dynamic controller.
        
        Args:
            ryzenadj_path: Path to ryzenadj binary
            gymdeck3_path: Path to gymdeck3 binary
            event_emitter: EventEmitter for frontend communication
            safety_manager: Optional SafetyManager for LKG persistence
        """
        self._ryzenadj_path = ryzenadj_path
        self._gymdeck3_path = gymdeck3_path
        self._event_emitter = event_emitter
        self._safety_manager = safety_manager
        
        self._process: Optional[asyncio.subprocess.Process] = None
        self._config: Optional[DynamicConfig] = None
        self._status = DynamicStatus()
        self._reader_task: Optional[asyncio.Task] = None
        self._running = False
    
    def is_running(self) -> bool:
        """Check if gymdeck3 is currently running."""
        return self._running and self._process is not None
    
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
            
            # Start reader task for stdout
            self._reader_task = asyncio.create_task(self._read_output())
            
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
    
    async def _emit_dynamic_status(self) -> None:
        """Emit dynamic status event to frontend."""
        await self._event_emitter._emit_event("dynamic_status", self._status.to_dict())
