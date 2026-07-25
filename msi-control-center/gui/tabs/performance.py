"""Performance — per-core CPU speedometers, memory, I/O gauges."""

import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from gui.widgets import Speedometer
from gui.theme import get_usage_color, bytes_to_human
from core.monitor import SystemSnapshot


class PerformanceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._core_gauges: list[Speedometer] = []
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        header = QLabel("PERFORMANCE")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        cpu_label = QLabel("CPU CORES")
        cpu_label.setProperty("class", "subtitle")
        cpu_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cpu_label)

        self._core_grid = QGridLayout()
        self._core_grid.setSpacing(16)
        self._core_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self._core_grid)

        mem_label = QLabel("MEMORY")
        mem_label.setProperty("class", "subtitle")
        mem_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(mem_label)

        mem_row = QHBoxLayout()
        mem_row.setSpacing(30)
        mem_row.setAlignment(Qt.AlignCenter)
        self.ram_gauge = Speedometer("RAM", 180)
        self.swap_gauge = Speedometer("SWAP", 180)
        self.disk_read_gauge = Speedometer("DISK READ", 180)
        self.disk_write_gauge = Speedometer("DISK WRITE", 180)
        mem_row.addWidget(self.ram_gauge)
        mem_row.addWidget(self.swap_gauge)
        mem_row.addWidget(self.disk_read_gauge)
        mem_row.addWidget(self.disk_write_gauge)
        layout.addLayout(mem_row)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _ensure_core_gauges(self, count: int):
        while len(self._core_gauges) < count:
            g = Speedometer("", 140)
            self._core_gauges.append(g)
        while self._core_grid.count():
            item = self._core_grid.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
        cols = min(count, 6)
        for i, g in enumerate(self._core_gauges[:count]):
            row, col = divmod(i, cols)
            self._core_grid.addWidget(g, row, col)
            g.show()

    def update_data(self, snap: SystemSnapshot):
        cores = snap.cpu.per_core or [snap.cpu.overall]
        self._ensure_core_gauges(len(cores))

        for i, pct in enumerate(cores):
            g = self._core_gauges[i]
            g.set_value(pct, 100, QColor(get_usage_color(pct)))
            g._label = f"CORE {i}"
            g.set_suffix("%")
            g.update()

        self.ram_gauge.set_value(snap.memory.percent, 100,
                                 QColor(get_usage_color(snap.memory.percent)))
        self.ram_gauge.set_suffix("%")
        self.ram_gauge.set_unit_label(
            f"{bytes_to_human(snap.memory.used)} / {bytes_to_human(snap.memory.total)}"
        )

        self.swap_gauge.set_value(snap.memory.swap_percent, 100,
                                  QColor(get_usage_color(snap.memory.swap_percent)))
        self.swap_gauge.set_suffix("%")
        self.swap_gauge.set_unit_label(
            f"{bytes_to_human(snap.memory.swap_used)} / {bytes_to_human(snap.memory.swap_total)}"
        )

        read_kb = snap.disk.io_read_bytes / 1024
        self.disk_read_gauge.set_value(read_kb, max(read_kb + 1, 1024), QColor("#8b2020"))
        self.disk_read_gauge.set_suffix("KB/s")

        write_kb = snap.disk.io_write_bytes / 1024
        self.disk_write_gauge.set_value(write_kb, max(write_kb + 1, 1024), QColor("#8b2020"))
        self.disk_write_gauge.set_suffix("KB/s")
