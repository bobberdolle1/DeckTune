"""Server-sent events manager for real-time status updates.

Feature: decktune-3.1-reliability-ux
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5

This module provides the StatusStreamManager class which manages
server-sent events for real-time status updates to the frontend.
It replaces polling with push-based updates for better responsiveness.
"""

import asyncio
import logging
from collections import deque
from typing import AsyncIterator, Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class StatusStreamManager:
    """Manager for server-sent events (SSE) status streaming.
    
    Manages subscriber queues and buffers status updates for delivery.
    Supports multiple concurrent subscribers with automatic cleanup.
    
    Requirements: 4.2, 4.4, 4.5
    Feature: decktune-3.1-reliability-ux
    """
    
    MAX_BUFFER = 10
    
    def __init__(self):
        """Initialize the status stream manager."""
        self._subscribers: List[asyncio.Queue] = []
        self._buffer: deque = deque(maxlen=self.MAX_BUFFER)
        self._running = False
        self._lock: Optional[asyncio.Lock] = None
    
    def _get_lock(self) -> asyncio.Lock:
        """Get or create the async lock (lazy initialization for Python 3.9 compatibility)."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    @property
    def subscriber_count(self) -> int:
        """Get the number of active subscribers."""
        return len(self._subscribers)
    
    @property
    def buffer_size(self) -> int:
        """Get the current buffer size."""
        return len(self._buffer)
    
    def set_running(self, running: bool) -> None:
        """Set the running state of the dynamic mode.
        
        Args:
            running: True if gymdeck3 is running, False otherwise
            
        Requirements: 4.3
        """
        self._running = running
        if not running:
            # Clear buffer when stopped
            self._buffer.clear()
    
    def is_running(self) -> bool:
        """Check if dynamic mode is running.
        
        Returns:
            True if gymdeck3 is running
        """
        return self._running
    
    async def subscribe(self) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to status updates.
        
        Returns an async iterator that yields status events.
        Automatically delivers buffered events on reconnection.
        
        Yields:
            Status event dictionaries
            
        Requirements: 4.2, 4.4
        """
        queue: asyncio.Queue = asyncio.Queue()
        
        async with self._get_lock():
            self._subscribers.append(queue)
            logger.debug(f"New subscriber added, total: {len(self._subscribers)}")
            
            # Deliver buffered events on reconnection
            for event in self._buffer:
                await queue.put(event)
        
        try:
            while True:
                event = await queue.get()
                yield event
        except asyncio.CancelledError:
            pass
        finally:
            async with self._get_lock():
                if queue in self._subscribers:
                    self._subscribers.remove(queue)
                    logger.debug(f"Subscriber removed, total: {len(self._subscribers)}")
    
    async def publish(self, event: Dict[str, Any]) -> None:
        """Publish a status event to all subscribers.
        
        If no subscribers are connected, buffers the event for later delivery.
        Buffer is limited to MAX_BUFFER entries (oldest dropped when full).
        
        Args:
            event: Status event dictionary to publish
            
        Requirements: 4.2, 4.5
        """
        # Don't publish if not running
        # Requirements: 4.3
        if not self._running:
            return
        
        async with self._get_lock():
            if not self._subscribers:
                # No subscribers, buffer the event
                self._buffer.append(event)
                logger.debug(f"Event buffered, buffer size: {len(self._buffer)}")
                return
            
            # Publish to all subscribers
            failed_queues = []
            for queue in self._subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Queue is full, mark for removal
                    failed_queues.append(queue)
                    logger.warning("Subscriber queue full, removing subscriber")
            
            # Remove failed subscribers
            for queue in failed_queues:
                self._subscribers.remove(queue)
    
    def get_buffered(self) -> List[Dict[str, Any]]:
        """Get all buffered events.
        
        Returns:
            List of buffered event dictionaries
        """
        return list(self._buffer)
    
    def clear_buffer(self) -> None:
        """Clear the event buffer."""
        self._buffer.clear()
    
    async def close(self) -> None:
        """Close all subscriber connections and clear state.
        
        Should be called when shutting down the stream manager.
        """
        async with self._get_lock():
            # Cancel all subscriber queues by putting a sentinel
            for queue in self._subscribers:
                try:
                    queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            
            self._subscribers.clear()
            self._buffer.clear()
            self._running = False
            logger.info("StatusStreamManager closed")
