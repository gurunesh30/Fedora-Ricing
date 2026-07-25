"""MSI Embedded Controller hardware interface.

Provides read/write access to MSI laptop EC sysfs files for fan control,
shift modes, cooler boost, webcam, keyboard backlight, and battery thresholds.
Falls back gracefully when msi-ec module is not loaded.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

from .config import MSI_EC_BASE, MSI_EC_CPU, MSI_EC_GPU

log = logging.getLogger(__name__)


@dataclass
class ECStatus:
    available: bool = False
    firmware_version: str = ""
    firmware_date: str = ""
    shift_mode: str = ""
    available_shift_modes: list[str] = field(default_factory=list)
    fan_mode: str = ""
    available_fan_modes: list[str] = field(default_factory=list)
    cooler_boost: bool = False
    webcam: str = ""
    fn_key: str = ""
    super_battery: str = ""
    cpu_temp: int = 0
    cpu_fan_speed: int = 0
    gpu_temp: int = 0
    gpu_fan_speed: int = 0


def _read_sysfs(path: str) -> str:
    """Read a sysfs file, returning empty string on failure."""
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except (OSError, IOError, PermissionError):
        return ""


def _write_sysfs(path: str, value: str) -> bool:
    """Write to a sysfs file, returning True on success."""
    try:
        with open(path, "w") as f:
            f.write(value)
        return True
    except (OSError, IOError, PermissionError) as e:
        log.warning("Failed to write %s to %s: %s", value, path, e)
        return False


class HardwareController:
    """Interface to MSI Embedded Controller via sysfs."""

    def __init__(self):
        self.available = os.path.isdir(MSI_EC_BASE)
        if self.available:
            log.info("MSI EC found at %s", MSI_EC_BASE)
        else:
            log.info("MSI EC not available at %s — using fallback modes", MSI_EC_BASE)

    def get_status(self) -> ECStatus:
        """Read all EC values and return a snapshot."""
        status = ECStatus(available=self.available)
        if not self.available:
            return status

        status.firmware_version = _read_sysfs(os.path.join(MSI_EC_BASE, "fw_version"))
        status.firmware_date = _read_sysfs(os.path.join(MSI_EC_BASE, "fw_release_date"))

        status.shift_mode = _read_sysfs(os.path.join(MSI_EC_BASE, "shift_mode"))
        raw = _read_sysfs(os.path.join(MSI_EC_BASE, "available_shift_modes"))
        status.available_shift_modes = raw.split() if raw else []

        status.fan_mode = _read_sysfs(os.path.join(MSI_EC_BASE, "fan_mode"))
        raw = _read_sysfs(os.path.join(MSI_EC_BASE, "available_fan_modes"))
        status.available_fan_modes = raw.split() if raw else []

        cb = _read_sysfs(os.path.join(MSI_EC_BASE, "cooler_boost"))
        status.cooler_boost = cb == "on"

        status.webcam = _read_sysfs(os.path.join(MSI_EC_BASE, "webcam"))
        status.fn_key = _read_sysfs(os.path.join(MSI_EC_BASE, "fn_key"))
        status.super_battery = _read_sysfs(os.path.join(MSI_EC_BASE, "super_battery"))

        t = _read_sysfs(os.path.join(MSI_EC_CPU, "realtime_temperature"))
        status.cpu_temp = int(t) if t.isdigit() else 0
        f = _read_sysfs(os.path.join(MSI_EC_CPU, "realtime_fan_speed"))
        status.cpu_fan_speed = int(f) if f.isdigit() else 0
        t = _read_sysfs(os.path.join(MSI_EC_GPU, "realtime_temperature"))
        status.gpu_temp = int(t) if t.isdigit() else 0
        f = _read_sysfs(os.path.join(MSI_EC_GPU, "realtime_fan_speed"))
        status.gpu_fan_speed = int(f) if f.isdigit() else 0

        return status

    def set_shift_mode(self, mode: str) -> bool:
        if not self.available:
            return False
        return _write_sysfs(os.path.join(MSI_EC_BASE, "shift_mode"), mode)

    def set_fan_mode(self, mode: str) -> bool:
        if not self.available:
            return False
        return _write_sysfs(os.path.join(MSI_EC_BASE, "fan_mode"), mode)

    def set_cooler_boost(self, enabled: bool) -> bool:
        if not self.available:
            return False
        return _write_sysfs(
            os.path.join(MSI_EC_BASE, "cooler_boost"), "on" if enabled else "off"
        )

    def set_webcam(self, state: str) -> bool:
        if not self.available:
            return False
        return _write_sysfs(os.path.join(MSI_EC_BASE, "webcam"), state)

    def set_fn_key(self, pos: str) -> bool:
        if not self.available:
            return False
        return _write_sysfs(os.path.join(MSI_EC_BASE, "fn_key"), pos)

    def set_super_battery(self, enabled: bool) -> bool:
        if not self.available:
            return False
        return _write_sysfs(
            os.path.join(MSI_EC_BASE, "super_battery"), "on" if enabled else "off"
        )

    def set_keyboard_backlight(self, level: int) -> bool:
        """Set keyboard backlight level (0=off, 1=on, 2=half, 3=full)."""
        path = "/sys/class/leds/msiacpi::kbd_backlight/brightness"
        return _write_sysfs(path, str(max(0, min(3, level))))

    def get_keyboard_backlight(self) -> int:
        val = _read_sysfs("/sys/class/leds/msiacpi::kbd_backlight/brightness")
        return int(val) if val.isdigit() else 0
