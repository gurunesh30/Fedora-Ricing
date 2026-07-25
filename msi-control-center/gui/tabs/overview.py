"""Overview dashboard tab — real-time system at a glance."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt

from gui.widgets import StatCard, CircularProgress, NetworkSpeedWidget, BarWidget
from gui.theme import bytes_to_human, seconds_to_human, get_temperature_color, get_usage_color
from core.monitor import SystemSnapshot


class OverviewTab(QWidget):
    """Main dashboard with CPU, GPU, RAM, battery, and network cards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        header = QLabel("System Overview")
        header.setProperty("class", "title")
        layout.addWidget(header)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        self.cpu_gauge = CircularProgress("CPU", 140)
        self.gpu_gauge = CircularProgress("GPU", 140)
        self.ram_gauge = CircularProgress("RAM", 140)
        self.battery_gauge = CircularProgress("BAT", 140)
        top_row.addWidget(self.cpu_gauge)
        top_row.addWidget(self.gpu_gauge)
        top_row.addWidget(self.ram_gauge)
        top_row.addWidget(self.battery_gauge)
        layout.addLayout(top_row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.cpu_freq_card = StatCard("CPU Freq", "—", "MHz")
        self.cpu_temp_card = StatCard("CPU Temp", "—", "°C")
        self.core_count_card = StatCard("Cores", "—", "physical / logical")
        self.uptime_card = StatCard("Uptime", "—")
        stats_row.addWidget(self.cpu_freq_card)
        stats_row.addWidget(self.cpu_temp_card)
        stats_row.addWidget(self.core_count_card)
        stats_row.addWidget(self.uptime_card)
        layout.addLayout(stats_row)

        net_row = QHBoxLayout()
        net_row.setSpacing(12)
        self.net_widget = NetworkSpeedWidget()
        self.net_total_card = StatCard("Total", "—", "sent / recv")
        net_row.addWidget(self.net_widget)
        net_row.addWidget(self.net_total_card, 1)
        layout.addLayout(net_row)

        disk_header = QLabel("Disk Usage")
        disk_header.setProperty("class", "subtitle")
        layout.addWidget(disk_header)
        self.disk_bars: list[BarWidget] = []
        self.disk_container = QVBoxLayout()
        self.disk_container.setSpacing(4)
        layout.addLayout(self.disk_container)

        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def update_data(self, snap: SystemSnapshot):
        from PySide6.QtGui import QColor

        cpu_pct = snap.cpu.overall
        cpu_color = QColor(get_usage_color(cpu_pct))
        self.cpu_gauge.set_value(cpu_pct, 100, cpu_color)

        gpu_temp = snap.sensors.temps[0].current if snap.sensors.temps else 0
        gpu_color = QColor(get_temperature_color(gpu_temp))
        self.gpu_gauge.set_value(gpu_temp, 100, gpu_color)

        self.ram_gauge.set_value(snap.memory.percent, 100,
                                 QColor(get_usage_color(snap.memory.percent)))

        if snap.sensors.battery:
            self.battery_gauge.set_value(snap.sensors.battery.percent, 100,
                                         QColor(get_usage_color(100 - snap.sensors.battery.percent)))
        else:
            self.battery_gauge.set_value(0, 100, QColor("#565f89"))

        self.cpu_freq_card.set_value(f"{snap.cpu.freq_current:.0f}")
        self.cpu_freq_card.set_subtitle(f"max {snap.cpu.freq_max:.0f} MHz")

        cpu_temp = 0
        for t in snap.sensors.temps:
            if "Package" in t.label or "coretemp" in t.source.lower():
                cpu_temp = t.current
                break
        if cpu_temp == 0 and snap.sensors.temps:
            cpu_temp = snap.sensors.temps[0].current
        temp_color = get_temperature_color(cpu_temp)
        self.cpu_temp_card.set_value(f"{cpu_temp:.0f}", temp_color)

        self.core_count_card.set_value(
            f"{snap.cpu.count_physical}/{snap.cpu.count_logical}"
        )

        self.uptime_card.set_value(seconds_to_human(snap.uptime))

        self.net_widget.set_speeds(snap.network.speed_up, snap.network.speed_down)
        self.net_total_card.set_value(
            f"{bytes_to_human(snap.network.bytes_sent)} / {bytes_to_human(snap.network.bytes_recv)}"
        )

        self._update_disk_bars(snap)

    def _update_disk_bars(self, snap: SystemSnapshot):
        while self.disk_container.count():
            item = self.disk_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.disk_bars.clear()
        for part in snap.disk.partitions:
            bar = BarWidget(f"{part['mountpoint']}")
            detail = f"{bytes_to_human(part['used'])} / {bytes_to_human(part['total'])}"
            bar.set_value(part["percent"], detail)
            self.disk_container.addWidget(bar)
            self.disk_bars.append(bar)
