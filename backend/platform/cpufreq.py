"""CPU frequency control and monitoring for frequency-based voltage optimization.

This module provides interfaces to the Linux cpufreq subsystem for:
- Reading current CPU frequencies
- Managing CPU governors
- Locking CPUs to specific frequencies for testing

Feature: frequency-based-wizard
Validates: Requirements 1.2, 6.3
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

# Sysfs paths for cpufreq control
CPUFREQ_BASE = "/sys/devices/system/cpu"


class CPUFreqError(Exception):
    """Base exception for cpufreq operations."""
    pass


class PermissionError(CPUFreqError):
    """Raised when cpufreq operations require root access."""
    pass


class UnsupportedError(CPUFreqError):
    """Raised when cpufreq feature is not supported."""
    pass


@dataclass
class FrequencyCache:
    """Cache for frequency readings to reduce sysfs access overhead.
    
    Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
    Validates: Requirements 12.3
    """
    frequency_mhz: int
    timestamp: float
    ttl_ms: float = 10.0  # 10ms cache TTL
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        age_ms = (time.time() - self.timestamp) * 1000
        return age_ms < self.ttl_ms


class CPUFreqController:
    """Manages CPU frequency scaling and governor control.
    
    This controller provides low-level access to the Linux cpufreq subsystem
    for frequency monitoring and control operations needed by the frequency
    wizard.
    
    Feature: frequency-based-wizard
    Validates: Requirements 1.2, 6.3, 12.3
    """
    
    def __init__(self, base_path: str = CPUFREQ_BASE):
        """Initialize CPUFreq controller.
        
        Args:
            base_path: Base path to cpufreq sysfs (for testing)
        """
        self.base_path = Path(base_path)
        self._frequency_cache: Dict[int, FrequencyCache] = {}
        self._original_governors: Dict[int, str] = {}
        
    def _get_cpufreq_path(self, core_id: int) -> Path:
        """Get cpufreq sysfs path for a specific core.
        
        Args:
            core_id: CPU core ID
            
        Returns:
            Path to cpufreq directory for the core
        """
        return self.base_path / f"cpu{core_id}" / "cpufreq"
    
    def _read_sysfs_file(self, path: Path) -> str:
        """Read a sysfs file with error handling.
        
        Args:
            path: Path to sysfs file
            
        Returns:
            File contents as string
            
        Raises:
            PermissionError: If file cannot be read due to permissions
            UnsupportedError: If file does not exist (feature not supported)
            CPUFreqError: For other I/O errors
        """
        try:
            return path.read_text().strip()
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied reading {path}. Root access may be required."
            ) from e
        except FileNotFoundError as e:
            raise UnsupportedError(
                f"cpufreq file {path} not found. Feature may not be supported."
            ) from e
        except (OSError, IOError) as e:
            raise CPUFreqError(f"Failed to read {path}: {e}") from e
    
    def _write_sysfs_file(self, path: Path, value: str) -> None:
        """Write to a sysfs file with error handling.
        
        Args:
            path: Path to sysfs file
            value: Value to write
            
        Raises:
            PermissionError: If file cannot be written due to permissions
            UnsupportedError: If file does not exist
            CPUFreqError: For other I/O errors
        """
        try:
            path.write_text(value)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied writing to {path}. Root access required."
            ) from e
        except FileNotFoundError as e:
            raise UnsupportedError(
                f"cpufreq file {path} not found. Feature may not be supported."
            ) from e
        except (OSError, IOError) as e:
            raise CPUFreqError(f"Failed to write to {path}: {e}") from e
    
    def get_current_frequency(self, core_id: int, use_cache: bool = True) -> int:
        """Read current frequency from sysfs.
        
        Reads from /sys/devices/system/cpu/cpu{N}/cpufreq/scaling_cur_freq
        
        Args:
            core_id: CPU core ID
            use_cache: Whether to use cached value if available (default True)
            
        Returns:
            Frequency in MHz
            
        Raises:
            PermissionError: If sysfs cannot be read
            UnsupportedError: If cpufreq is not supported
            CPUFreqError: For other errors
            
        Feature: frequency-based-wizard, Property 23: Frequency reading cache consistency
        Validates: Requirements 2.1, 12.3
        """
        # Check cache first if enabled
        if use_cache and core_id in self._frequency_cache:
            cache_entry = self._frequency_cache[core_id]
            if cache_entry.is_valid():
                return cache_entry.frequency_mhz
        
        # Read from sysfs
        freq_path = self._get_cpufreq_path(core_id) / "scaling_cur_freq"
        freq_khz_str = self._read_sysfs_file(freq_path)
        
        try:
            freq_khz = int(freq_khz_str)
            freq_mhz = freq_khz // 1000
        except ValueError as e:
            raise CPUFreqError(
                f"Invalid frequency value from {freq_path}: {freq_khz_str}"
            ) from e
        
        # Update cache
        if use_cache:
            self._frequency_cache[core_id] = FrequencyCache(
                frequency_mhz=freq_mhz,
                timestamp=time.time()
            )
        
        return freq_mhz
    
    def get_available_frequencies(self, core_id: int) -> List[int]:
        """Get list of supported frequencies for core.
        
        Reads from /sys/devices/system/cpu/cpu{N}/cpufreq/scaling_available_frequencies
        
        Args:
            core_id: CPU core ID
            
        Returns:
            List of frequencies in MHz, sorted ascending
            
        Raises:
            PermissionError: If sysfs cannot be read
            UnsupportedError: If cpufreq is not supported
            CPUFreqError: For other errors
        """
        freq_path = self._get_cpufreq_path(core_id) / "scaling_available_frequencies"
        
        try:
            freq_str = self._read_sysfs_file(freq_path)
        except UnsupportedError:
            # Some systems don't expose available frequencies
            # Fall back to reading min/max
            logger.warning(
                f"scaling_available_frequencies not available for core {core_id}, "
                "using min/max range"
            )
            return self._get_frequency_range(core_id)
        
        try:
            # Parse space-separated frequency list (in kHz)
            freq_khz_list = [int(f) for f in freq_str.split()]
            freq_mhz_list = [f // 1000 for f in freq_khz_list]
            return sorted(freq_mhz_list)
        except ValueError as e:
            raise CPUFreqError(
                f"Invalid frequency list from {freq_path}: {freq_str}"
            ) from e
    
    def _get_frequency_range(self, core_id: int) -> List[int]:
        """Get min/max frequency range when available frequencies not exposed.
        
        Args:
            core_id: CPU core ID
            
        Returns:
            List containing [min_freq, max_freq] in MHz
        """
        cpufreq_path = self._get_cpufreq_path(core_id)
        
        min_freq_str = self._read_sysfs_file(cpufreq_path / "cpuinfo_min_freq")
        max_freq_str = self._read_sysfs_file(cpufreq_path / "cpuinfo_max_freq")
        
        min_freq_mhz = int(min_freq_str) // 1000
        max_freq_mhz = int(max_freq_str) // 1000
        
        return [min_freq_mhz, max_freq_mhz]
    
    def get_current_governor(self, core_id: int) -> str:
        """Get current cpufreq governor name.
        
        Reads from /sys/devices/system/cpu/cpu{N}/cpufreq/scaling_governor
        
        Args:
            core_id: CPU core ID
            
        Returns:
            Governor name (e.g., "schedutil", "performance", "userspace")
            
        Raises:
            PermissionError: If sysfs cannot be read
            UnsupportedError: If cpufreq is not supported
            CPUFreqError: For other errors
        """
        gov_path = self._get_cpufreq_path(core_id) / "scaling_governor"
        return self._read_sysfs_file(gov_path)
    
    def get_available_governors(self, core_id: int) -> List[str]:
        """Get list of available governors for core.
        
        Args:
            core_id: CPU core ID
            
        Returns:
            List of available governor names
        """
        gov_path = self._get_cpufreq_path(core_id) / "scaling_available_governors"
        gov_str = self._read_sysfs_file(gov_path)
        return gov_str.split()
    
    def set_governor(self, core_id: int, governor: str) -> None:
        """Set cpufreq governor (requires root).
        
        Writes to /sys/devices/system/cpu/cpu{N}/cpufreq/scaling_governor
        
        Args:
            core_id: CPU core ID
            governor: Governor name to set
            
        Raises:
            PermissionError: If not running as root
            UnsupportedError: If governor is not available
            CPUFreqError: For other errors
            
        Feature: frequency-based-wizard
        Validates: Requirements 1.2
        """
        # Validate governor is available
        available = self.get_available_governors(core_id)
        if governor not in available:
            raise UnsupportedError(
                f"Governor '{governor}' not available for core {core_id}. "
                f"Available: {', '.join(available)}"
            )
        
        gov_path = self._get_cpufreq_path(core_id) / "scaling_governor"
        self._write_sysfs_file(gov_path, governor)
        
        logger.info(f"Set core {core_id} governor to '{governor}'")
    
    def lock_frequency(self, core_id: int, freq_mhz: int) -> None:
        """Lock CPU to specific frequency.
        
        Sets governor to 'userspace' and fixes frequency to the specified value.
        Stores the original governor for later restoration.
        
        On Steam Deck where 'userspace' is not available, uses 'performance' governor
        with min/max frequency limits as a fallback.
        
        Args:
            core_id: CPU core ID
            freq_mhz: Frequency to lock to in MHz
            
        Raises:
            PermissionError: If not running as root
            UnsupportedError: If userspace governor not available
            CPUFreqError: For other errors
            
        Feature: frequency-based-wizard
        Validates: Requirements 1.2, 6.3
        """
        # Store original governor if not already stored
        if core_id not in self._original_governors:
            self._original_governors[core_id] = self.get_current_governor(core_id)
        
        # Check if userspace governor is available
        available_governors = self.get_available_governors(core_id)
        
        if "userspace" in available_governors:
            # Set userspace governor
            self.set_governor(core_id, "userspace")
            
            # Set frequency (in kHz)
            freq_khz = freq_mhz * 1000
            freq_path = self._get_cpufreq_path(core_id) / "scaling_setspeed"
            self._write_sysfs_file(freq_path, str(freq_khz))
        else:
            # Fallback for Steam Deck: use performance governor with min/max limits
            logger.warning(
                f"Governor 'userspace' not available for core {core_id}. "
                f"Using 'performance' governor with frequency limits as fallback."
            )
            
            # Set performance governor
            self.set_governor(core_id, "performance")
            
            # Set both min and max frequency to lock the frequency
            freq_khz = freq_mhz * 1000
            min_freq_path = self._get_cpufreq_path(core_id) / "scaling_min_freq"
            max_freq_path = self._get_cpufreq_path(core_id) / "scaling_max_freq"
            
            self._write_sysfs_file(min_freq_path, str(freq_khz))
            self._write_sysfs_file(max_freq_path, str(freq_khz))
        
        # Invalidate cache
        if core_id in self._frequency_cache:
            del self._frequency_cache[core_id]
        
        logger.info(f"Locked core {core_id} to {freq_mhz} MHz")
    
    def unlock_frequency(self, core_id: int, original_governor: Optional[str] = None) -> None:
        """Restore original governor and unlock frequency.
        
        Also restores original min/max frequency limits if they were modified.
        
        Args:
            core_id: CPU core ID
            original_governor: Governor to restore (uses stored value if None)
            
        Raises:
            PermissionError: If not running as root
            CPUFreqError: For other errors
            
        Feature: frequency-based-wizard
        Validates: Requirements 2.5, 6.4
        """
        # Determine which governor to restore
        if original_governor is None:
            original_governor = self._original_governors.get(core_id)
        
        if original_governor is None:
            logger.warning(
                f"No original governor stored for core {core_id}, "
                "defaulting to 'schedutil'"
            )
            original_governor = "schedutil"
        
        # Restore min/max frequency limits to full range before changing governor
        try:
            cpufreq_path = self._get_cpufreq_path(core_id)
            
            # Get the hardware limits
            min_freq_hw_path = cpufreq_path / "cpuinfo_min_freq"
            max_freq_hw_path = cpufreq_path / "cpuinfo_max_freq"
            
            min_freq_hw = self._read_sysfs_file(min_freq_hw_path).strip()
            max_freq_hw = self._read_sysfs_file(max_freq_hw_path).strip()
            
            # Restore to hardware limits
            min_freq_path = cpufreq_path / "scaling_min_freq"
            max_freq_path = cpufreq_path / "scaling_max_freq"
            
            self._write_sysfs_file(min_freq_path, min_freq_hw)
            self._write_sysfs_file(max_freq_path, max_freq_hw)
            
            logger.debug(f"Restored frequency limits for core {core_id}")
        except Exception as e:
            logger.warning(f"Failed to restore frequency limits for core {core_id}: {e}")
        
        # Restore governor
        try:
            self.set_governor(core_id, original_governor)
        except UnsupportedError:
            # If original governor not available, try schedutil
            logger.warning(
                f"Original governor '{original_governor}' not available, "
                "falling back to 'schedutil'"
            )
            self.set_governor(core_id, "schedutil")
        
        # Clear stored governor
        if core_id in self._original_governors:
            del self._original_governors[core_id]
        
        # Invalidate cache
        if core_id in self._frequency_cache:
            del self._frequency_cache[core_id]
        
        logger.info(f"Unlocked core {core_id}, restored governor to '{original_governor}'")
    
    def is_frequency_control_supported(self, core_id: int = 0) -> bool:
        """Check if frequency control is supported on this system.
        
        Args:
            core_id: CPU core ID to check (default 0)
            
        Returns:
            True if cpufreq is supported, False otherwise
        """
        cpufreq_path = self._get_cpufreq_path(core_id)
        return cpufreq_path.exists()
    
    def clear_cache(self) -> None:
        """Clear all cached frequency readings.
        
        Useful for testing or when forcing fresh reads.
        """
        self._frequency_cache.clear()
