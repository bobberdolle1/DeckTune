"""Property tests for status buffer limit.

**Feature: decktune-3.1-reliability-ux, Property 9: Status buffer limit**
**Validates: Requirements 4.5**

Property 9: Status buffer limit
For any sequence of status updates when delivery fails, the buffer SHALL not 
exceed 10 entries, and oldest entries SHALL be dropped when full.
"""

import pytest
from hypothesis import given, strategies as st, settings
import asyncio

from backend.api.stream import StatusStreamManager


# Strategy for valid status event dictionaries
@st.composite
def status_event(draw, index: int = 0):
    """Generate a valid status event dictionary."""
    return {
        "type": "dynamic_status",
        "timestamp": 1700000000.0 + index,
        "load": [draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)) for _ in range(4)],
        "values": [draw(st.integers(min_value=-50, max_value=0)) for _ in range(4)],
        "running": True
    }


class TestStatusBufferLimit:
    """Property 9: Status buffer limit
    
    For any sequence of status updates when delivery fails, the buffer SHALL not 
    exceed 10 entries, and oldest entries SHALL be dropped when full.
    
    **Feature: decktune-3.1-reliability-ux, Property 9: Status buffer limit**
    **Validates: Requirements 4.5**
    """

    @given(num_events=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_buffer_never_exceeds_limit(self, num_events: int):
        """Buffer length never exceeds 10 entries."""
        manager = StatusStreamManager()
        manager.set_running(True)  # Enable publishing
        
        async def run_test():
            # Publish N events with no subscribers (all go to buffer)
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            assert manager.buffer_size <= StatusStreamManager.MAX_BUFFER, \
                f"Buffer size {manager.buffer_size} exceeds limit {StatusStreamManager.MAX_BUFFER}"
        
        asyncio.run(run_test())

    @given(num_events=st.integers(min_value=11, max_value=50))
    @settings(max_examples=100)
    def test_oldest_removed_when_full(self, num_events: int):
        """Oldest event is removed when buffer is full."""
        manager = StatusStreamManager()
        manager.set_running(True)  # Enable publishing
        
        async def run_test():
            # Publish N events with no subscribers
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            buffered = manager.get_buffered()
            
            # Should have exactly MAX_BUFFER entries
            assert len(buffered) == StatusStreamManager.MAX_BUFFER, \
                f"Expected {StatusStreamManager.MAX_BUFFER} events, got {len(buffered)}"
            
            # First event should be the (N - MAX_BUFFER)th event
            expected_first_index = num_events - StatusStreamManager.MAX_BUFFER
            assert buffered[0]["index"] == expected_first_index, \
                f"First event index should be {expected_first_index}, got {buffered[0]['index']}"
        
        asyncio.run(run_test())

    @given(num_events=st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_buffer_under_limit_not_truncated(self, num_events: int):
        """Buffer with <= 10 events is not truncated."""
        manager = StatusStreamManager()
        manager.set_running(True)  # Enable publishing
        
        async def run_test():
            # Publish N events where N <= 10
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            assert manager.buffer_size == num_events, \
                f"Expected {num_events} events, got {manager.buffer_size}"
        
        asyncio.run(run_test())

    @given(num_events=st.integers(min_value=11, max_value=50))
    @settings(max_examples=100)
    def test_insertion_order_preserved(self, num_events: int):
        """Events are stored in insertion order (oldest first)."""
        manager = StatusStreamManager()
        manager.set_running(True)  # Enable publishing
        
        async def run_test():
            # Publish N events
            for i in range(num_events):
                event = {
                    "type": "dynamic_status",
                    "timestamp": 1700000000.0 + i,
                    "index": i
                }
                await manager.publish(event)
            
            buffered = manager.get_buffered()
            
            # Verify indices are in ascending order
            expected_start = num_events - StatusStreamManager.MAX_BUFFER
            for i, event in enumerate(buffered):
                expected_index = expected_start + i
                assert event["index"] == expected_index, \
                    f"Event {i} should have index {expected_index}, got {event['index']}"
        
        asyncio.run(run_test())

    def test_buffer_max_is_10(self):
        """Buffer max is 10 entries."""
        assert StatusStreamManager.MAX_BUFFER == 10, \
            f"Buffer max should be 10, got {StatusStreamManager.MAX_BUFFER}"
