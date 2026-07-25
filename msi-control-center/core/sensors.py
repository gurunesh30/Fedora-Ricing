"""Sensor data reader.

Reads temperature, fan speed, voltage, and power data from:
  1. psutil.sensors_* (coretemp, k10temp, acpitz, etc.)
  2. Direct hwmon sysfs fallback
  3. MSI EC via HardwareController

All data is normalized into unified dataclasses for the GUI.
"""

import os
import glob
import logging
from dataclasses import dataclass, field
from typing import Optional

import psutil

log = logging.getLogger(__name__)


@dataclass
class TempReading:
    label: str
    current: float
    high: float = 0.0
    critical: float = 0.0
    source: str = "coretemp"


@dataclass
class FanReading:
    label: str
    speed_rpm: int
    source: str = "hwmon"


@dataclass
class VoltageReading:
    label: str
    current: float
    source: str = "hwmon"


@dataclass
class BatteryInfo:
    percent: float = 0.0
    secs_left: int = -1
    power_plugged: bool = False
    voltage: float = 0.0
    wattage: float = 0.0


@dataclass
class SensorSnapshot:
    temps: list[TempReading] = field(default_factory=list)
    fans: list[FanReading] = field(default_factory=list)
    voltages: list[VoltageReading] = field(default_factory=list)
    battery: Optional[BatteryInfo] = None


class SensorReader:
    """Unified sensor data reader."""

    def __init__(self):
        self._hwmon_paths = self._discover_hwmon()

    def _discover_hwmon(self) -> dict[str, dict]:
        """Discover hwmon devices and their capabilities."""
        devices = {}
        for hwmon_dir in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
            name_path = os.path.join(hwmon_dir, "name")
            if not os.path.isfile(name_path):
                continue
            with open(name_path) as f:
                name = f.read().strip()

            info = {"path": hwmon_dir, "name": name, "temps": [], "fans": [], "voltages": []}

            for temp_file in sorted(glob.glob(os.path.join(hwmon_dir, "temp*_input"))):
                idx = os.path.basename(temp_file).replace("temp", "").replace("_input", "")
                label_file = os.path.join(hwmon_dir, f"temp{idx}_label")
                label = name
                if os.path.isfile(label_file):
                    with open(label_file) as f:
                        label = f.read().strip()
                info["temps"].append({
                    "path": temp_file,
                    "label": label,
                    "high": _read_int(os.path.join(hwmon_dir, f"temp{idx}_max")) / 1000.0,
                    "crit": _read_int(os.path.join(hwmon_dir, f"temp{idx}_crit")) / 1000.0,
                })

            for fan_file in sorted(glob.glob(os.path.join(hwmon_dir, "fan*_input"))):
                idx = os.path.basename(fan_file).replace("fan", "").replace("_input", "")
                label_file = os.path.join(hwmon_dir, f"fan{idx}_label")
                label = name
                if os.path.isfile(label_file):
                    with open(label_file) as f:
                        label = f.read().strip()
                info["fans"].append({"path": fan_file, "label": label})

            for in_file in sorted(glob.glob(os.path.join(hwmon_dir, "in*_input"))):
                idx = os.path.basename(in_file).replace("in", "").replace("_input", "")
                label_file = os.path.join(hwmon_dir, f"in{idx}_label")
                label = f"in{idx}"
                if os.path.isfile(label_file):
                    with open(label_file) as f:
                        label = f.read().strip()
                info["voltages"].append({"path": in_file, "label": label})

            devices[name] = info
        return devices

    def read_psutil_sensors(self) -> SensorSnapshot:
        """Read sensors via psutil."""
        snap = SensorSnapshot()

        try:
            temps = psutil.sensors_temperatures()
            for chip, entries in temps.items():
                for entry in entries:
                    snap.temps.append(TempReading(
                        label=f"{chip}: {entry.label}" if entry.label else chip,
                        current=entry.current,
                        high=entry.high or 0.0,
                        critical=entry.critical or 0.0,
                        source=chip,
                    ))
        except (AttributeError, Exception) as e:
            log.debug("psutil.sensors_temperatures failed: %s", e)

        try:
            fans = psutil.sensors_fans()
            for chip, entries in fans.items():
                for entry in entries:
                    snap.fans.append(FanReading(
                        label=f"{chip}: {entry.label}" if entry.label else chip,
                        speed_rpm=entry.current,
                        source=chip,
                    ))
        except (AttributeError, Exception) as e:
            log.debug("psutil.sensors_fans failed: %s", e)

        try:
            bat = psutil.sensors_battery()
            if bat:
                snap.battery = BatteryInfo(
                    percent=bat.percent,
                    secs_left=bat.secsleft,
                    power_plugged=bat.power_plugged,
                )
        except (AttributeError, Exception):
            pass

        return snap

    def read_hwmon_sensors(self) -> SensorSnapshot:
        """Read sensors directly from hwmon sysfs as fallback."""
        snap = SensorSnapshot()
        for name, info in self._hwmon_paths.items():
            for temp in info["temps"]:
                val = _read_int(temp["path"])
                if val > 0:
                    snap.temps.append(TempReading(
                        label=f"{name}: {temp['label']}",
                        current=val / 1000.0,
                        high=temp.get("high", 0.0),
                        critical=temp.get("crit", 0.0),
                        source=name,
                    ))
            for fan in info["fans"]:
                val = _read_int(fan["path"])
                if val > 0:
                    snap.fans.append(FanReading(
                        label=f"{name}: {fan['label']}",
                        speed_rpm=val,
                        source=name,
                    ))
            for vin in info["voltages"]:
                val = _read_int(vin["path"])
                if val > 0:
                    snap.voltages.append(VoltageReading(
                        label=f"{name}: {vin['label']}",
                        current=val / 1000.0,
                        source=name,
                    ))
        return snap

    def read_all(self) -> SensorSnapshot:
        """Read all sensors, merging psutil and hwmon data."""
        snap = self.read_psutil_sensors()
        hwmon = self.read_hwmon_sensors()

        psutil_labels = {t.label for t in snap.temps}
        for t in hwmon.temps:
            if t.label not in psutil_labels:
                snap.temps.append(t)

        psutil_fan_labels = {f.label for f in snap.fans}
        for f in hwmon.fans:
            if f.label not in psutil_fan_labels:
                snap.fans.append(f)

        snap.voltages = hwmon.voltages
        return snap


def _read_int(path: str) -> int:
    try:
        with open(path) as f:
            val = f.read().strip()
            return int(val) if val.isdigit() else 0
    except (OSError, IOError):
        return 0
