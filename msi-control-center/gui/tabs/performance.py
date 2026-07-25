"""Performance details tab — per-core CPU, memory breakdown, CPU times, I/O."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea,
    QProgressBar,
)
from PySide6.QtCore import Qt

from gui.widgets import BarWidget, StatCard
from gui.theme import bytes_to_human, get_usage_color
from core.monitor import SystemSnapshot


class PerformanceTab(QWidget):
    """Detailed performance metrics with per-core CPU bars and memory breakdown."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._core_bars: list[BarWidget] = []
        self._net_iface_bars: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        header = QLabel("Performance Details")
        header.setProperty("class", "title")
        layout.addWidget(header)

        cpu_section = QLabel("CPU Usage — Per Core")
        cpu_section.setProperty("class", "subtitle")
        layout.addWidget(cpu_section)

        self._core_container = QVBoxLayout()
        self._core_container.setSpacing(3)
        layout.addLayout(self._core_container)

        cpu_times_header = QLabel("CPU Time Distribution")
        cpu_times_header.setProperty("class", "subtitle")
        layout.addWidget(cpu_times_header)

        self.cpu_times_grid = QGridLayout()
        self.cpu_times_grid.setSpacing(8)
        self._cpu_time_labels = {}
        for i, (key, label) in enumerate([
            ("user", "User"), ("system", "System"),
            ("iowait", "I/O Wait"), ("idle", "Idle"),
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #7aa2f7; font-weight: bold;")
            val = QLabel("—")
            val.setAlignment(Qt.AlignRight)
            self.cpu_times_grid.addWidget(lbl, i, 0)
            self.cpu_times_grid.addWidget(val, i, 1)
            self._cpu_time_labels[key] = val
        layout.addLayout(self.cpu_times_grid)

        mem_header = QLabel("Memory")
        mem_header.setProperty("class", "subtitle")
        layout.addWidget(mem_header)

        mem_grid = QGridLayout()
        mem_grid.setSpacing(8)
        self.mem_stats = {}
        for i, (key, label) in enumerate([
            ("total", "Total"), ("used", "Used"), ("available", "Available"),
            ("percent", "Usage %"), ("swap_total", "Swap Total"),
            ("swap_used", "Swap Used"), ("swap_percent", "Swap %"),
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: bold;")
            val = QLabel("—")
            val.setAlignment(Qt.AlignRight)
            mem_grid.addWidget(lbl, i, 0)
            mem_grid.addWidget(val, i, 1)
            self.mem_stats[key] = val
        layout.addLayout(mem_grid)

        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        self.mem_bar.setValue(0)
        self.mem_bar.setFormat("RAM: %p%")
        self.mem_bar.setFixedHeight(16)
        layout.addWidget(self.mem_bar)

        self.swap_bar = QProgressBar()
        self.swap_bar.setRange(0, 100)
        self.swap_bar.setValue(0)
        self.swap_bar.setFormat("Swap: %p%")
        self.swap_bar.setFixedHeight(16)
        layout.addWidget(self.swap_bar)

        io_header = QLabel("Disk I/O")
        io_header.setProperty("class", "subtitle")
        layout.addWidget(io_header)

        io_grid = QGridLayout()
        self.io_labels = {}
        for i, (key, label) in enumerate([
            ("read", "Read Speed"), ("write", "Write Speed"),
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: bold;")
            val = QLabel("—")
            val.setAlignment(Qt.AlignRight)
            io_grid.addWidget(lbl, i, 0)
            io_grid.addWidget(val, i, 1)
            self.io_labels[key] = val
        layout.addLayout(io_grid)

        net_header = QLabel("Network Interfaces")
        net_header.setProperty("class", "subtitle")
        layout.addWidget(net_header)

        self._net_container = QGridLayout()
        self._net_container.setSpacing(4)
        layout.addLayout(self._net_container)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def update_data(self, snap: SystemSnapshot):
        self._update_cpu_cores(snap)
        self._update_cpu_times(snap)
        self._update_memory(snap)
        self._update_io(snap)
        self._update_network(snap)

    def _update_cpu_cores(self, snap: SystemSnapshot):
        while self._core_container.count():
            item = self._core_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._core_bars.clear()

        for i, pct in enumerate(snap.cpu.per_core):
            bar = BarWidget(f"Core {i}")
            bar.set_value(pct)
            self._core_container.addWidget(bar)
            self._core_bars.append(bar)

    def _update_cpu_times(self, snap: SystemSnapshot):
        for key, label in self._cpu_time_labels.items():
            val = snap.cpu.times.get(key, 0)
            label.setText(f"{val:.1f}%")
            color = get_usage_color(val) if key != "idle" else "#9ece6a"
            label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _update_memory(self, snap: SystemSnapshot):
        m = snap.memory
        self.mem_stats["total"].setText(bytes_to_human(m.total))
        self.mem_stats["used"].setText(bytes_to_human(m.used))
        self.mem_stats["available"].setText(bytes_to_human(m.available))
        self.mem_stats["percent"].setText(f"{m.percent:.1f}%")
        self.mem_stats["swap_total"].setText(bytes_to_human(m.swap_total))
        self.mem_stats["swap_used"].setText(bytes_to_human(m.swap_used))
        self.mem_stats["swap_percent"].setText(f"{m.swap_percent:.1f}%")

        color = get_usage_color(m.percent)
        self.mem_bar.setValue(int(m.percent))
        self.mem_bar.setStyleSheet(
            f"QProgressBar::chunk {{ border-radius: 6px; background: {color}; }}"
        )
        color = get_usage_color(m.swap_percent)
        self.swap_bar.setValue(int(m.swap_percent))
        self.swap_bar.setStyleSheet(
            f"QProgressBar::chunk {{ border-radius: 6px; background: {color}; }}"
        )

    def _update_io(self, snap: SystemSnapshot):
        self.io_labels["read"].setText(f"{bytes_to_human(snap.disk.io_read_bytes)}/s")
        self.io_labels["write"].setText(f"{bytes_to_human(snap.disk.io_write_bytes)}/s")

    def _update_network(self, snap: SystemSnapshot):
        while self._net_container.count():
            item = self._net_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        row = 0
        for iface, data in snap.network.interfaces.items():
            lbl = QLabel(f"  {iface}")
            lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
            sent = QLabel(f"TX: {bytes_to_human(data['bytes_sent'])}")
            recv = QLabel(f"RX: {bytes_to_human(data['bytes_recv'])}")
            sent.setStyleSheet("color: #9ece6a;")
            recv.setStyleSheet("color: #7aa2f7;")
            self._net_container.addWidget(lbl, row, 0)
            self._net_container.addWidget(sent, row, 1)
            self._net_container.addWidget(recv, row, 2)
            row += 1
