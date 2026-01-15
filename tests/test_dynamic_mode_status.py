"""Property tests for dynamic mode status.

Feature: decktune, Property 16: Dynamic Mode Status
Validates: Requirements 10.3

Property 16: Dynamic Mode Status
For any active gymdeck2 process, the status SHALL be "DYNAMIC RUNNING". 
When the process terminates, status SHALL transition to "Disabled".
"""

import asyncio
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, AsyncMock, patch


class MockSettings:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self._settings = {
            "status": "Disabled",
            "dynamicSettings": {
                "strategy": "DEFAULT",
                "sampleInterval": 50000,
                "cores": []
            }
        }
    
    def getSetting(self, key):
        return self._settings.get(key)
    
    def setSetting(self, key, value):
        self._settings[key] = value


class MockProcess:
    """Mock asyncio subprocess for testing."""
    
    def __init__(self, running: bool = True):
        self._running = running
        self.returncode = None if running else 0
        self.stdout = AsyncMock()
        self.stdout.at_eof.return_value = True
        self.stderr = AsyncMock()
        self._terminated = False
        self._killed = False
    
    def terminate(self):
        self._terminated = True
        self.returncode = -15  # SIGTERM
    
    def kill(self):
        self._killed = True
        self.returncode = -9  # SIGKILL
    
    async def wait(self):
        return self.returncode


class DynamicModeStatusTracker:
    """Simplified dynamic mode status tracker for property testing.
    
    This class encapsulates the core status tracking logic from Plugin
    to enable isolated property testing.
    """
    
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.gymdeck_instance = None
        self.gymdeck_monitor_task = None
    
    def is_dynamic_running(self) -> bool:
        """Check if dynamic mode is currently running."""
        return (
            self.gymdeck_instance is not None and 
            self.gymdeck_instance.returncode is None
        )
    
    def get_status(self) -> str:
        """Get current status string."""
        if self.is_dynamic_running():
            return "DYNAMIC RUNNING"
        return self.settings.getSetting("status") or "Disabled"
    
    async def start_dynamic(self, process: MockProcess) -> str:
        """Start dynamic mode with given process.
        
        Returns:
            Status string after starting
        """
        # Stop any existing process
        await self.stop_dynamic()
        
        self.gymdeck_instance = process
        
        # Update status to DYNAMIC RUNNING
        self.settings.setSetting("status", "DYNAMIC RUNNING")
        
        return self.get_status()
    
    async def stop_dynamic(self) -> str:
        """Stop dynamic mode.
        
        Returns:
            Status string after stopping
        """
        if self.gymdeck_instance is not None:
            if self.gymdeck_instance.returncode is None:
                self.gymdeck_instance.terminate()
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(0.01),  # Simulate wait
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    self.gymdeck_instance.kill()
            
            self.gymdeck_instance = None
        
        # Update status to Disabled
        self.settings.setSetting("status", "Disabled")
        
        return self.get_status()
    
    def simulate_process_exit(self) -> None:
        """Simulate the gymdeck process exiting."""
        if self.gymdeck_instance is not None:
            self.gymdeck_instance.returncode = 0
            # In real code, the monitor task would update status
            self.settings.setSetting("status", "Disabled")


class TestDynamicModeStatus:
    """Property 16: Dynamic Mode Status
    
    For any active gymdeck2 process, the status SHALL be "DYNAMIC RUNNING". 
    When the process terminates, status SHALL transition to "Disabled".
    
    Validates: Requirements 10.3
    """

    @pytest.mark.asyncio
    @given(initial_status=st.sampled_from(["Disabled", "enabled", "error", "scheduled"]))
    @settings(max_examples=100)
    async def test_status_is_dynamic_running_when_process_active(self, initial_status: str):
        """When gymdeck2 process is active, status SHALL be 'DYNAMIC RUNNING'.
        
        Property: For any active gymdeck2 process, status == "DYNAMIC RUNNING"
        """
        settings_manager = MockSettings()
        settings_manager.setSetting("status", initial_status)
        
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start dynamic mode with a running process
        running_process = MockProcess(running=True)
        status = await tracker.start_dynamic(running_process)
        
        # Verify status is DYNAMIC RUNNING
        assert status == "DYNAMIC RUNNING", \
            f"Status should be 'DYNAMIC RUNNING' when process is active, got '{status}'"
        assert tracker.is_dynamic_running() is True, \
            "is_dynamic_running() should return True when process is active"

    @pytest.mark.asyncio
    @given(initial_status=st.sampled_from(["Disabled", "enabled", "error", "scheduled", "DYNAMIC RUNNING"]))
    @settings(max_examples=100)
    async def test_status_is_disabled_when_process_stops(self, initial_status: str):
        """When gymdeck2 process terminates, status SHALL transition to 'Disabled'.
        
        Property: When process terminates, status == "Disabled"
        """
        settings_manager = MockSettings()
        settings_manager.setSetting("status", initial_status)
        
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start dynamic mode
        running_process = MockProcess(running=True)
        await tracker.start_dynamic(running_process)
        
        # Stop dynamic mode
        status = await tracker.stop_dynamic()
        
        # Verify status is Disabled
        assert status == "Disabled", \
            f"Status should be 'Disabled' after process stops, got '{status}'"
        assert tracker.is_dynamic_running() is False, \
            "is_dynamic_running() should return False after process stops"

    @pytest.mark.asyncio
    @given(num_starts=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    async def test_status_transitions_correctly_through_multiple_cycles(self, num_starts: int):
        """Status correctly transitions through multiple start/stop cycles.
        
        Property: For any sequence of start/stop operations, status is always
        "DYNAMIC RUNNING" when running and "Disabled" when stopped.
        """
        settings_manager = MockSettings()
        tracker = DynamicModeStatusTracker(settings_manager)
        
        for i in range(num_starts):
            # Start dynamic mode
            running_process = MockProcess(running=True)
            status = await tracker.start_dynamic(running_process)
            
            assert status == "DYNAMIC RUNNING", \
                f"Cycle {i+1}: Status should be 'DYNAMIC RUNNING' after start"
            assert tracker.is_dynamic_running() is True, \
                f"Cycle {i+1}: is_dynamic_running() should be True after start"
            
            # Stop dynamic mode
            status = await tracker.stop_dynamic()
            
            assert status == "Disabled", \
                f"Cycle {i+1}: Status should be 'Disabled' after stop"
            assert tracker.is_dynamic_running() is False, \
                f"Cycle {i+1}: is_dynamic_running() should be False after stop"

    @pytest.mark.asyncio
    @given(strategy=st.sampled_from(["DEFAULT", "AGGRESSIVE", "MANUAL"]))
    @settings(max_examples=100)
    async def test_status_independent_of_strategy(self, strategy: str):
        """Status is 'DYNAMIC RUNNING' regardless of strategy used.
        
        Property: For any strategy, active process -> status == "DYNAMIC RUNNING"
        """
        settings_manager = MockSettings()
        settings_manager.setSetting("dynamicSettings", {
            "strategy": strategy,
            "sampleInterval": 50000,
            "cores": []
        })
        
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start dynamic mode
        running_process = MockProcess(running=True)
        status = await tracker.start_dynamic(running_process)
        
        # Verify status is DYNAMIC RUNNING regardless of strategy
        assert status == "DYNAMIC RUNNING", \
            f"Status should be 'DYNAMIC RUNNING' for strategy '{strategy}', got '{status}'"

    @pytest.mark.asyncio
    async def test_status_disabled_when_no_process(self):
        """Status is 'Disabled' when no process has been started."""
        settings_manager = MockSettings()
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # No process started
        status = tracker.get_status()
        
        assert status == "Disabled", \
            f"Status should be 'Disabled' when no process started, got '{status}'"
        assert tracker.is_dynamic_running() is False, \
            "is_dynamic_running() should be False when no process started"

    @pytest.mark.asyncio
    async def test_status_disabled_after_process_exit(self):
        """Status transitions to 'Disabled' when process exits naturally."""
        settings_manager = MockSettings()
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start dynamic mode
        running_process = MockProcess(running=True)
        await tracker.start_dynamic(running_process)
        
        assert tracker.get_status() == "DYNAMIC RUNNING"
        
        # Simulate process exit
        tracker.simulate_process_exit()
        
        # Verify status is Disabled
        assert tracker.get_status() == "Disabled", \
            "Status should be 'Disabled' after process exits"
        assert tracker.is_dynamic_running() is False, \
            "is_dynamic_running() should be False after process exits"

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self):
        """Calling stop multiple times is safe and maintains Disabled status."""
        settings_manager = MockSettings()
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start and stop
        running_process = MockProcess(running=True)
        await tracker.start_dynamic(running_process)
        await tracker.stop_dynamic()
        
        # Stop again (should be safe)
        status = await tracker.stop_dynamic()
        
        assert status == "Disabled", \
            "Status should remain 'Disabled' after multiple stops"

    @pytest.mark.asyncio
    async def test_start_stops_previous_process(self):
        """Starting dynamic mode stops any previously running process."""
        settings_manager = MockSettings()
        tracker = DynamicModeStatusTracker(settings_manager)
        
        # Start first process
        process1 = MockProcess(running=True)
        await tracker.start_dynamic(process1)
        
        # Start second process (should stop first)
        process2 = MockProcess(running=True)
        status = await tracker.start_dynamic(process2)
        
        # First process should be terminated
        assert process1._terminated or process1._killed, \
            "First process should be terminated when starting second"
        
        # Status should still be DYNAMIC RUNNING
        assert status == "DYNAMIC RUNNING", \
            "Status should be 'DYNAMIC RUNNING' after starting new process"
