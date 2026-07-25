"""Overview — speedometer gauges for CPU, GPU, RAM, battery, fans."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from gui.widgets import Speedometer
from gui.theme import get_temperature_color, get_usage_color, bytes_to_human, seconds_to_human
from core.monitor import SystemSnapshot


class OverviewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        header = QLabel("SYSTEM OVERVIEW")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        row1 = QHBoxLayout()
        row1.setSpacing(30)
        row1.setAlignment(Qt.AlignCenter)
        self.cpu_gauge = Speedometer("CPU LOAD", 180)
        self.gpu_gauge = Speedometer("GPU TEMP", 180)
        self.ram_gauge = Speedometer("MEMORY", 180)
        self.bat_gauge = Speedometer("BATTERY", 180)
        row1.addWidget(self.cpu_gauge)
        row1.addWidget(self.gpu_gauge)
        row1.addWidget(self.ram_gauge)
        row1.addWidget(self.bat_gauge)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(30)
        row2.setAlignment(Qt.AlignCenter)
        self.cpu_temp_gauge = Speedometer("CPU TEMP", 180)
        self.cpu_freq_gauge = Speedometer("CPU FREQ", 180)
        self.net_up_gauge = Speedometer("UPLOAD", 180)
        self.net_down_gauge = Speedometer("DOWNLOAD", 180)
        row2.addWidget(self.cpu_temp_gauge)
        row2.addWidget(self.cpu_freq_gauge)
        row2.addWidget(self.net_up_gauge)
        row2.addWidget(self.net_down_gauge)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(30)
        row3.setAlignment(Qt.AlignCenter)
        self.fan1_gauge = Speedometer("FAN 1", 180)
        self.fan2_gauge = Speedometer("FAN 2", 180)
        self.disk_gauge = Speedometer("DISK", 180)
        self.uptime_gauge = Speedometer("UPTIME", 180)
        row3.addWidget(self.fan1_gauge)
        row3.addWidget(self.fan2_gauge)
        row3.addWidget(self.disk_gauge)
        row3.addWidget(self.uptime_gauge)
        layout.addLayout(row3)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def update_data(self, snap: SystemSnapshot):
        cpu_pct = snap.cpu.overall
        self.cpu_gauge.set_value(cpu_pct, 100, QColor(get_usage_color(cpu_pct)))
        self.cpu_gauge.set_suffix("%")
        self.cpu_gauge.set_unit_label(f"{snap.cpu.count_logical} threads")

        gpu_temp = 0
        for t in snap.sensors.temps:
            if "iwlwifi" in t.source.lower():
                continue
            gpu_temp = max(gpu_temp, t.current)
        self.gpu_gauge.set_value(gpu_temp, 100, QColor(get_temperature_color(gpu_temp)))
        self.gpu_gauge.set_suffix("°C")

        self.ram_gauge.set_value(snap.memory.percent, 100, QColor(get_usage_color(snap.memory.percent)))
        self.ram_gauge.set_suffix("%")
        self.ram_gauge.set_unit_label(bytes_to_human(snap.memory.used))

        if snap.sensors.battery:
            self.bat_gauge.set_value(snap.sensors.battery.percent, 100,
                                     QColor(get_usage_color(100 - snap.sensors.battery.percent)))
            self.bat_gauge.set_suffix("%")
        else:
            self.bat_gauge.set_value(0, 100, QColor("#333333"))
            self.bat_gauge.set_suffix("%")
            self.bat_gauge.set_unit_label("N/A")

        cpu_temp = 0
        for t in snap.sensors.temps:
            if "Package" in t.label or "coretemp" in t.source.lower():
                cpu_temp = t.current
                break
        if cpu_temp == 0 and snap.sensors.temps:
            cpu_temp = snap.sensors.temps[0].current
        self.cpu_temp_gauge.set_value(cpu_temp, 100, QColor(get_temperature_color(cpu_temp)))
        self.cpu_temp_gauge.set_suffix("°C")

        freq = snap.cpu.freq_current
        freq_max = max(snap.cpu.freq_max, 1)
        self.cpu_freq_gauge.set_value(freq, freq_max, QColor("#8b2020"))
        self.cpu_freq_gauge.set_suffix("MHz")

        self.net_up_gauge.set_value(snap.network.speed_up / 1024, 1024, QColor("#8b2020"))
        self.net_up_gauge.set_suffix("KB/s")

        self.net_down_gauge.set_value(snap.network.speed_down / 1024, 1024, QColor("#8b2020"))
        self.net_down_gauge.set_suffix("KB/s")

        fans = snap.sensors.fans
        fan1_rpm = fans[0].speed_rpm if len(fans) > 0 else 0
        fan2_rpm = fans[1].speed_rpm if len(fans) > 1 else 0
        self.fan1_gauge.set_value(fan1_rpm, 6000, QColor(get_temperature_color(fan1_rpm / 60)))
        self.fan1_gauge.set_suffix("RPM")
        self.fan2_gauge.set_value(fan2_rpm, 6000, QColor(get_temperature_color(fan2_rpm / 60)))
        self.fan2_gauge.set_suffix("RPM")

        disk_pct = snap.disk.partitions[0]["percent"] if snap.disk.partitions else 0
        self.disk_gauge.set_value(disk_pct, 100, QColor(get_usage_color(disk_pct)))
        self.disk_gauge.set_suffix("%")

        self.uptime_gauge.set_value(snap.uptime / 60, 1440, QColor("#8b2020"))
        self.uptime_gauge.set_suffix("min")
        self.uptime_gauge.set_unit_label(seconds_to_human(snap.uptime))
