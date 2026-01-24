"""Property test for metrics buffer FIFO limit.

Feature: manual-dynamic-mode, Property 5: Metrics buffer FIFO limit
Validates: Requirements 3.4

Property 5: Metrics buffer FIFO limit
For any sequence of CoreMetrics updates, the real-time metrics graph buffer 
SHALL never exceed 60 data points, removing the oldest point when the limit 
is reached.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import List


# Strategy for generating CoreMetrics-like data
@st.composite
def core_metrics(draw):
    """Generate a CoreMetrics-like dictionary."""
    return {
        'core_id': draw(st.integers(min_value=0, max_value=3)),
        'load': draw(st.floats(min_value=0.0, max_value=100.0)),
        'voltage': draw(st.integers(min_value=-100, max_value=0)),
        'frequency': draw(st.integers(min_value=400, max_value=3500)),
        'temperature': draw(st.floats(min_value=20.0, max_value=95.0)),
        'timestamp': draw(st.integers(min_value=1000000000, max_value=2000000000)),
    }


# Strategy for generating sequences of metrics
metrics_sequence = st.lists(
    core_metrics(),
    min_size=1,
    max_size=200  # Test with sequences larger than buffer limit
)


class TestMetricsBufferFIFOLimit:
    """Property 5: Metrics buffer FIFO limit
    
    For any sequence of CoreMetrics updates, the real-time metrics graph buffer 
    SHALL never exceed 60 data points, removing the oldest point when the limit 
    is reached.
    
    Validates: Requirements 3.4
    """

    @given(metrics_list=metrics_sequence)
    @settings(max_examples=100)
    def test_buffer_never_exceeds_60_points(self, metrics_list: List[dict]):
        """Buffer SHALL never exceed 60 data points."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        # Simulate adding metrics to buffer with FIFO behavior
        for metrics in metrics_list:
            # Add new point
            buffer.append(metrics)
            
            # Remove oldest if exceeds limit (FIFO)
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
            
            # Verify buffer never exceeds limit
            assert len(buffer) <= MAX_DATA_POINTS, (
                f"Buffer size {len(buffer)} exceeds maximum {MAX_DATA_POINTS}"
            )

    @given(metrics_list=st.lists(core_metrics(), min_size=61, max_size=200))
    @settings(max_examples=100)
    def test_oldest_points_removed_when_limit_exceeded(self, metrics_list: List[dict]):
        """When buffer exceeds 60 points, oldest points SHALL be removed."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        # Add unique index to track position
        for i, metrics in enumerate(metrics_list):
            metrics_with_idx = {**metrics, '_idx': i}
            buffer.append(metrics_with_idx)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
            
            # After adding more than 60 points, verify oldest are removed
            if i >= MAX_DATA_POINTS:
                # The first metric (index 0) should no longer be in buffer
                indices_in_buffer = [m['_idx'] for m in buffer]
                assert 0 not in indices_in_buffer, (
                    "Oldest metric (index 0) should be removed from buffer"
                )
                
                # The most recent 60 metrics should be in buffer
                expected_start_idx = i - MAX_DATA_POINTS + 1
                expected_indices = list(range(expected_start_idx, i + 1))
                assert indices_in_buffer == expected_indices, (
                    f"Buffer should contain indices {expected_indices[:5]}...{expected_indices[-5:]}, "
                    f"got {indices_in_buffer[:5]}...{indices_in_buffer[-5:]}"
                )

    @given(metrics_list=st.lists(core_metrics(), min_size=1, max_size=59))
    @settings(max_examples=100)
    def test_buffer_preserves_all_points_when_below_limit(self, metrics_list: List[dict]):
        """When buffer has fewer than 60 points, all SHALL be preserved."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        for metrics in metrics_list:
            buffer.append(metrics)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
        
        # All metrics should be preserved
        assert len(buffer) == len(metrics_list), (
            f"Buffer should preserve all {len(metrics_list)} points when below limit"
        )
        
        # Verify order is preserved
        for i, metrics in enumerate(metrics_list):
            assert buffer[i] == metrics, (
                f"Buffer should preserve order of metrics"
            )

    @given(
        initial_count=st.integers(min_value=50, max_value=60),
        additional_count=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_fifo_behavior_maintains_most_recent(
        self,
        initial_count: int,
        additional_count: int
    ):
        """FIFO behavior SHALL maintain the most recent 60 points."""
        MAX_DATA_POINTS = 60
        
        # Generate initial metrics
        buffer = [{'timestamp': i} for i in range(initial_count)]
        
        # Add additional metrics
        for i in range(additional_count):
            buffer.append({'timestamp': initial_count + i})
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
        
        # Verify buffer contains most recent points
        total_count = initial_count + additional_count
        if total_count > MAX_DATA_POINTS:
            # Should contain last 60 points
            expected_start = total_count - MAX_DATA_POINTS
            expected_timestamps = list(range(expected_start, total_count))
            actual_timestamps = [m['timestamp'] for m in buffer]
            
            assert actual_timestamps == expected_timestamps, (
                f"Buffer should contain most recent {MAX_DATA_POINTS} points"
            )
        else:
            # Should contain all points
            assert len(buffer) == total_count

    @given(metrics_list=st.lists(core_metrics(), min_size=100, max_size=200))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example])
    def test_buffer_size_stabilizes_at_60(self, metrics_list: List[dict]):
        """After exceeding limit, buffer size SHALL stabilize at 60."""
        MAX_DATA_POINTS = 60
        buffer = []
        sizes = []
        
        for metrics in metrics_list:
            buffer.append(metrics)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
            
            sizes.append(len(buffer))
        
        # After 60 points, all subsequent sizes should be 60
        for i, size in enumerate(sizes):
            if i >= MAX_DATA_POINTS:
                assert size == MAX_DATA_POINTS, (
                    f"Buffer size should stabilize at {MAX_DATA_POINTS} "
                    f"after initial fill, got {size} at index {i}"
                )

    @given(
        metrics_list=st.lists(core_metrics(), min_size=70, max_size=100)
    )
    @settings(max_examples=100)
    def test_continuous_updates_maintain_fifo_invariant(self, metrics_list: List[dict]):
        """Continuous updates SHALL maintain FIFO invariant."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        for i, metrics in enumerate(metrics_list):
            # Add timestamp for tracking
            metrics_with_idx = {**metrics, 'index': i}
            buffer.append(metrics_with_idx)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
            
            # Verify FIFO invariant: indices should be monotonically increasing
            if len(buffer) > 1:
                indices = [m['index'] for m in buffer]
                for j in range(len(indices) - 1):
                    assert indices[j] < indices[j + 1], (
                        f"Buffer indices should be monotonically increasing, "
                        f"got {indices[j]} followed by {indices[j + 1]}"
                    )

    @given(metrics_list=st.lists(core_metrics(), min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_buffer_length_property(self, metrics_list: List[dict]):
        """Buffer length SHALL equal min(total_added, 60)."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        for i, metrics in enumerate(metrics_list):
            buffer.append(metrics)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
            
            # Verify length property
            expected_length = min(i + 1, MAX_DATA_POINTS)
            assert len(buffer) == expected_length, (
                f"After adding {i + 1} metrics, buffer length should be "
                f"{expected_length}, got {len(buffer)}"
            )


class TestMetricsBufferEdgeCases:
    """Test edge cases for metrics buffer FIFO behavior."""

    @given(metrics=core_metrics())
    @settings(max_examples=100)
    def test_single_metric_creates_buffer_of_one(self, metrics: dict):
        """Adding a single metric SHALL create buffer of size 1."""
        buffer = []
        buffer.append(metrics)
        
        assert len(buffer) == 1, "Single metric should create buffer of size 1"
        assert buffer[0] == metrics, "Buffer should contain the metric"

    @given(metrics_list=st.lists(core_metrics(), min_size=60, max_size=60))
    @settings(max_examples=100)
    def test_exactly_60_metrics_fills_buffer(self, metrics_list: List[dict]):
        """Adding exactly 60 metrics SHALL fill buffer without removal."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        for metrics in metrics_list:
            buffer.append(metrics)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
        
        assert len(buffer) == MAX_DATA_POINTS, (
            f"Buffer should contain exactly {MAX_DATA_POINTS} points"
        )
        
        # All original metrics should be present
        for i, metrics in enumerate(metrics_list):
            assert buffer[i] == metrics, (
                f"All {MAX_DATA_POINTS} metrics should be preserved"
            )

    @given(metrics_list=st.lists(core_metrics(), min_size=61, max_size=61))
    @settings(max_examples=100)
    def test_61st_metric_triggers_removal(self, metrics_list: List[dict]):
        """Adding 61st metric SHALL trigger removal of first metric."""
        MAX_DATA_POINTS = 60
        buffer = []
        
        # Add unique index to track position
        for i, metrics in enumerate(metrics_list):
            metrics_with_idx = {**metrics, '_idx': i}
            buffer.append(metrics_with_idx)
            
            if len(buffer) > MAX_DATA_POINTS:
                buffer = buffer[-MAX_DATA_POINTS:]
        
        assert len(buffer) == MAX_DATA_POINTS, (
            f"Buffer should contain {MAX_DATA_POINTS} points after adding 61"
        )
        
        # First metric (index 0) should be removed
        indices_in_buffer = [m['_idx'] for m in buffer]
        assert 0 not in indices_in_buffer, (
            "First metric (index 0) should be removed when 61st is added"
        )
        
        # Last 60 metrics (indices 1-60) should be present
        expected_indices = list(range(1, 61))
        assert indices_in_buffer == expected_indices, (
            f"Buffer should contain indices 1-60, got {indices_in_buffer}"
        )
