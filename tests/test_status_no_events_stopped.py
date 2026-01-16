"""Property tests for no events when stopped.

**Feature: decktune-3.1-reliability-ux, Property 10: No events when stopped**
**Validates: Requirements 4.3**

Property 10: No events when stopped
For any state where gymdeck3 is not running, no dynamic_status events SHALL 
be emitted to subscribers.
"""

import pytest
from hypothesis import given, strategies as st, settings
import asyncio

from backend.api.stream import StatusStreamManager


class TestNoEventsWhenStopped:
    """Property 10: No events when stopped
    
    For any state where gymdeck3 is not running, no dynamic_status events SHALL 
    be emitted to subscribers.
    
    **Feature: decktune-3.1-reliability-ux, Property 10: No events when stopped**
    **Validates: Requirements 4.3**
    """

    @given(num_events=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_no_buffer_when_stopped(self, num_events: int):
        """No events are buffered when gymdeck3 is not running."""
        manager = StatusStreamManager()
        # Default state is not running (set_running not called or set to False)
        manager.set_running(False)
        
        async def run_test():
            # Try to publish N events while stopped
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            # Buffer should be empty
            assert manager.buffer_size == 0, \
                f"Buffer should be empty when stopped, got {manager.buffer_size} events"
        
        asyncio.run(run_test())

    @given(num_events=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_no_subscriber_delivery_when_stopped(self, num_events: int):
        """No events are delivered to subscribers when gymdeck3 is not running."""
        manager = StatusStreamManager()
        manager.set_running(False)
        
        async def run_test():
            received_events = []
            
            # Create a subscriber
            async def subscriber():
                async for event in manager.subscribe():
                    if event is None:  # Sentinel for close
                        break
                    received_events.append(event)
            
            # Start subscriber task
            subscriber_task = asyncio.create_task(subscriber())
            
            # Give subscriber time to register
            await asyncio.sleep(0.01)
            
            # Try to publish events while stopped
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            # Close the manager to stop the subscriber
            await manager.close()
            
            # Wait for subscriber to finish
            try:
                await asyncio.wait_for(subscriber_task, timeout=1.0)
            except asyncio.TimeoutError:
                subscriber_task.cancel()
            
            # No events should have been received
            assert len(received_events) == 0, \
                f"Should receive 0 events when stopped, got {len(received_events)}"
        
        asyncio.run(run_test())

    @given(
        events_before=st.integers(min_value=1, max_value=10),
        events_after=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100)
    def test_buffer_cleared_when_stopped(self, events_before: int, events_after: int):
        """Buffer is cleared when gymdeck3 stops."""
        manager = StatusStreamManager()
        
        async def run_test():
            # Start running and publish some events
            manager.set_running(True)
            for i in range(events_before):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            # Verify events were buffered
            assert manager.buffer_size == events_before, \
                f"Expected {events_before} buffered events, got {manager.buffer_size}"
            
            # Stop running - buffer should be cleared
            manager.set_running(False)
            
            assert manager.buffer_size == 0, \
                f"Buffer should be cleared when stopped, got {manager.buffer_size} events"
            
            # Try to publish more events while stopped
            for i in range(events_after):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + events_before + i,
                    "index": events_before + i
                }
                await manager.publish(event)
            
            # Buffer should still be empty
            assert manager.buffer_size == 0, \
                f"Buffer should remain empty when stopped, got {manager.buffer_size} events"
        
        asyncio.run(run_test())

    def test_default_state_is_not_running(self):
        """Default state is not running."""
        manager = StatusStreamManager()
        assert not manager.is_running(), \
            "Default state should be not running"

    @given(num_events=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_events_flow_when_running(self, num_events: int):
        """Events are delivered when gymdeck3 is running (control test)."""
        manager = StatusStreamManager()
        manager.set_running(True)
        
        async def run_test():
            received_events = []
            
            # Create a subscriber
            async def subscriber():
                async for event in manager.subscribe():
                    if event is None:  # Sentinel for close
                        break
                    received_events.append(event)
                    if len(received_events) >= num_events:
                        break
            
            # Start subscriber task
            subscriber_task = asyncio.create_task(subscriber())
            
            # Give subscriber time to register
            await asyncio.sleep(0.01)
            
            # Publish events while running
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            # Wait for subscriber to receive all events
            try:
                await asyncio.wait_for(subscriber_task, timeout=1.0)
            except asyncio.TimeoutError:
                pass
            
            # All events should have been received
            assert len(received_events) == num_events, \
                f"Should receive {num_events} events when running, got {len(received_events)}"
        
        asyncio.run(run_test())
