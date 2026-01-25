"""Stub interface for gymdeck3 testing.

This module provides a stub implementation of the gymdeck3 interface
for testing Manual Dynamic Mode without requiring the actual Rust binary.

Feature: manual-dynamic-mode
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class Gymdeck3Stub:
    """Stub implementation of gymdeck3 interface for testing.
    
    Simulates gymdeck3 behavior without actual hardware interaction.
    Useful for development and testing on non-Steam Deck systems.
    """
    
    def __init__(self):
        """Initialize the stub interface."""
        self.is_running = False
        self.core_configs = [
            {"min_mv": -30, "max_mv": -15, "threshold": 50.0}
            for _ in range(4)
        ]
        self.start_time = None
        
        logger.info("Gymdeck3Stub initialized")
    
    def set_core_config(
        self,
        core_id: int,
        min_mv: int,
        max_mv: int,
        threshold: float
    ) -> bool:
        """Set configuration for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            min_mv: Minimum undervolt value
            max_mv: Maximum undervolt value
            threshold: Load threshold percentage
            
        Returns:
            True if configuration was set successfully
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return False
        
        self.core_configs[core_id] = {
            "min_mv": min_mv,
            "max_mv": max_mv,
            "threshold": threshold
        }
        
        logger.debug(f"Stub: Set core {core_id} config: {self.core_configs[core_id]}")
        return True
    
    def start(self) -> bool:
        """Start dynamic voltage adjustment.
        
        Returns:
            True if started successfully
        """
        if self.is_running:
            logger.warning("Stub: Already running")
            return False
        
        self.is_running = True
        self.start_time = time.time()
        logger.info("Stub: Dynamic mode started")
        return True
    
    def stop(self) -> bool:
        """Stop dynamic voltage adjustment.
        
        Returns:
            True if stopped successfully
        """
        if not self.is_running:
            logger.warning("Stub: Not running")
            return False
        
        self.is_running = False
        self.start_time = None
        logger.info("Stub: Dynamic mode stopped")
        return True
    
    def get_core_metrics(self, core_id: int) -> Optional[dict]:
        """Get current metrics for a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return None
        
        if not self.is_running:
            return None
        
        # Simulate metrics with some variation
        import random
        
        config = self.core_configs[core_id]
        load = random.uniform(0, 100)
        
        # Calculate voltage based on load and config
        if load <= config["threshold"]:
            voltage = config["min_mv"]
        else:
            progress = (load - config["threshold"]) / (100 - config["threshold"])
            voltage = config["min_mv"] + (config["max_mv"] - config["min_mv"]) * progress
        
        return {
            "core_id": core_id,
            "load": load,
            "voltage": int(voltage),
            "frequency": random.randint(1400, 3500),
            "temperature": random.uniform(40, 75),
            "timestamp": time.time()
        }
    
    def apply_voltage(self, core_id: int, voltage_mv: int) -> bool:
        """Apply voltage offset to a specific core.
        
        Args:
            core_id: Core identifier (0-3)
            voltage_mv: Voltage offset in mV
            
        Returns:
            True if applied successfully
        """
        if not 0 <= core_id < 4:
            logger.error(f"Invalid core_id: {core_id}")
            return False
        
        logger.debug(f"Stub: Applied {voltage_mv}mV to core {core_id}")
        return True
