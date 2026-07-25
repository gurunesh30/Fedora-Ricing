"""Central monitoring service.

Runs background collection of CPU, memory, disk, network, and sensor data.
Emits Qt signals for real-time GUI updates.
"""

import time
import threading
from collections import deque
from dataclasses import dataclass, field

import psutil
from PySide6.QtCore import QObject, Signal, Slot

from .config import GRAPH_MAX_POINTS
from .hardware import HardwareController, ECStatus
from .sensors import SensorReader, SensorSnapshot


@dataclass
class CPUData:
    overall: float = 0.0
    per_core: list[float] = field(default_factory=list)
    freq_current: float = 0.0
    freq_max: float = 0.0
    count_physical: int = 0
    count_logical: int = 0
    times: dict = field(default_factory=dict)


@dataclass
class MemoryData:
    total: int = 0
    used: int = 0
    available: int = 0
    percent: float = 0.0
    swap_total: int = 0
    swap_used: int = 0
    swap_percent: float = 0.0


@dataclass
class DiskData:
    partitions: list[dict] = field(default_factory=list)
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    io_read_count: int = 0
    io_write_count: int = 0


@dataclass
class NetworkData:
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    speed_up: float = 0.0
    speed_down: float = 0.0
    interfaces: dict = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    cpu: CPUData = field(default_factory=CPUData)
    memory: MemoryData = field(default_factory=MemoryData)
    disk: DiskData = field(default_factory=DiskData)
    network: NetworkData = field(default_factory=NetworkData)
    sensors: SensorSnapshot = field(default_factory=SensorSnapshot)
    ec: ECStatus = field(default_factory=ECStatus)
    uptime: float = 0.0
    timestamp: float = 0.0


class MonitorService(QObject):
    """Background monitoring service emitting Qt signals."""

    data_updated = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hardware = HardwareController()
        self.sensors = SensorReader()

        self._running = False
        self._thread: threading.Thread | None = None

        self.cpu_history: deque[list[float]] = deque(maxlen=GRAPH_MAX_POINTS)
        self.net_up_history: deque[float] = deque(maxlen=GRAPH_MAX_POINTS)
        self.net_down_history: deque[float] = deque(maxlen=GRAPH_MAX_POINTS)
        self.temp_history: deque[dict[str, float]] = deque(maxlen=GRAPH_MAX_POINTS)

        self._prev_net = None
        self._prev_disk_io = None
        self._prev_time = None

    @Slot()
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()

    @Slot()
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _collect_loop(self):
        while self._running:
            try:
                snap = self._collect_snapshot()
                self.data_updated.emit(snap)
            except Exception as e:
                self.error_occurred.emit(str(e))
            time.sleep(1.0)

    def _collect_snapshot(self) -> SystemSnapshot:
        snap = SystemSnapshot(timestamp=time.time())

        snap.cpu = self._collect_cpu()
        snap.memory = self._collect_memory()
        snap.disk = self._collect_disk()
        snap.network = self._collect_network()
        snap.sensors = self.sensors.read_all()
        snap.ec = self.hardware.get_status()

        try:
            snap.uptime = time.time() - psutil.boot_time()
        except Exception:
            snap.uptime = 0.0

        self.cpu_history.append(snap.cpu.per_core or [snap.cpu.overall])
        self.net_up_history.append(snap.network.speed_up)
        self.net_down_history.append(snap.network.speed_down)

        temp_dict = {}
        for t in snap.sensors.temps[:8]:
            temp_dict[t.label] = t.current
        self.temp_history.append(temp_dict)

        return snap

    def _collect_cpu(self) -> CPUData:
        data = CPUData()
        data.overall = psutil.cpu_percent(interval=0)
        data.per_core = psutil.cpu_percent(interval=0, percpu=True)

        try:
            freq = psutil.cpu_freq()
            if freq:
                data.freq_current = freq.current
                data.freq_max = freq.max
        except Exception:
            pass

        data.count_physical = psutil.cpu_count(logical=False) or 0
        data.count_logical = psutil.cpu_count(logical=True) or 0

        try:
            times = psutil.cpu_times_percent(interval=0)
            data.times = {
                "user": times.user,
                "system": times.system,
                "idle": times.idle,
                "iowait": getattr(times, "iowait", 0),
            }
        except Exception:
            pass

        return data

    def _collect_memory(self) -> MemoryData:
        data = MemoryData()
        try:
            vm = psutil.virtual_memory()
            data.total = vm.total
            data.used = vm.used
            data.available = vm.available
            data.percent = vm.percent
        except Exception:
            pass
        try:
            sw = psutil.swap_memory()
            data.swap_total = sw.total
            data.swap_used = sw.used
            data.swap_percent = sw.percent
        except Exception:
            pass
        return data

    def _collect_disk(self) -> DiskData:
        data = DiskData()
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    data.partitions.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    })
                except (PermissionError, OSError):
                    continue
        except Exception:
            pass

        try:
            io = psutil.disk_io_counters()
            if io:
                if self._prev_disk_io and self._prev_time:
                    dt = time.time() - self._prev_time
                    if dt > 0:
                        data.io_read_bytes = int(
                            (io.read_bytes - self._prev_disk_io.read_bytes) / dt
                        )
                        data.io_write_bytes = int(
                            (io.write_bytes - self._prev_disk_io.write_bytes) / dt
                        )
                self._prev_disk_io = io
                self._prev_time = time.time()
        except Exception:
            pass

        return data

    def _collect_network(self) -> NetworkData:
        data = NetworkData()
        try:
            io = psutil.net_io_counters()
            data.bytes_sent = io.bytes_sent
            data.bytes_recv = io.bytes_recv
            data.packets_sent = io.packets_sent
            data.packets_recv = io.packets_recv

            if self._prev_net:
                dt = time.time() - (self._prev_net.get("time", time.time()))
                if dt > 0:
                    data.speed_up = max(
                        0, (io.bytes_sent - self._prev_net["sent"]) / dt
                    )
                    data.speed_down = max(
                        0, (io.bytes_recv - self._prev_net["recv"]) / dt
                    )
            self._prev_net = {
                "sent": io.bytes_sent,
                "recv": io.bytes_recv,
                "time": time.time(),
            }

            per_nic = psutil.net_io_counters(pernic=True)
            for iface, counters in per_nic.items():
                data.interfaces[iface] = {
                    "bytes_sent": counters.bytes_sent,
                    "bytes_recv": counters.bytes_recv,
                    "packets_sent": counters.packets_sent,
                    "packets_recv": counters.packets_recv,
                }
        except Exception:
            pass
        return data
