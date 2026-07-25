"""Hardware — fan RPM speedometers, EC status."""

import glob
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGroupBox,
    QPushButton, QComboBox, QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from gui.widgets import Speedometer
from gui.theme import get_fan_color
from core.hardware import HardwareController
from core.config import SHIFT_MODES

MSI_WMI_HWMON = None
for p in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
    name_file = os.path.join(p, "name")
    if os.path.isfile(name_file):
        with open(name_file) as f:
            if f.read().strip() == "msi_wmi_platform":
                MSI_WMI_HWMON = p
                break


class HardwareTab(QWidget):
    ec_write = Signal(str, str)

    def __init__(self, hardware: HardwareController, parent=None):
        super().__init__(parent)
        self._hw = hardware
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        header = QLabel("HARDWARE")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        fan_label = QLabel("FAN SPEEDS")
        fan_label.setProperty("class", "subtitle")
        fan_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(fan_label)

        fan_row = QHBoxLayout()
        fan_row.setSpacing(30)
        fan_row.setAlignment(Qt.AlignCenter)
        self.fan_gauges: list[Speedometer] = []
        for i in range(4):
            g = Speedometer(f"FAN {i+1}", 180)
            self.fan_gauges.append(g)
            fan_row.addWidget(g)
        layout.addLayout(fan_row)

        self.fan_note = QLabel("")
        self.fan_note.setStyleSheet("color: #666666; font-size: 11px;")
        self.fan_note.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.fan_note)

        ec_label = QLabel("MSI EC")
        ec_label.setProperty("class", "subtitle")
        ec_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ec_label)

        self.ec_status = QLabel("")
        self.ec_status.setStyleSheet("font-size: 12px;")
        self.ec_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ec_status)

        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(20)
        ctrl_row.setAlignment(Qt.AlignCenter)

        fan_mode_col = QVBoxLayout()
        fan_mode_col.setAlignment(Qt.AlignCenter)
        fan_mode_lbl = QLabel("FAN MODE")
        fan_mode_lbl.setStyleSheet("color: #8b2020; font-weight: bold; font-size: 11px;")
        fan_mode_lbl.setAlignment(Qt.AlignCenter)
        fan_mode_col.addWidget(fan_mode_lbl)
        self.fan_mode_combo = QComboBox()
        self.fan_mode_combo.addItems(["auto", "silent", "basic", "advanced"])
        self.fan_mode_combo.currentTextChanged.connect(self._on_fan_mode_changed)
        fan_mode_col.addWidget(self.fan_mode_combo)
        ctrl_row.addLayout(fan_mode_col)

        cooler_col = QVBoxLayout()
        cooler_col.setAlignment(Qt.AlignCenter)
        cooler_lbl = QLabel("COOLER BOOST")
        cooler_lbl.setStyleSheet("color: #8b2020; font-weight: bold; font-size: 11px;")
        cooler_lbl.setAlignment(Qt.AlignCenter)
        cooler_col.addWidget(cooler_lbl)
        self.cooler_boost_btn = QPushButton("OFF")
        self.cooler_boost_btn.setCheckable(True)
        self.cooler_boost_btn.setFixedWidth(120)
        self.cooler_boost_btn.clicked.connect(self._on_cooler_boost)
        cooler_col.addWidget(self.cooler_boost_btn, alignment=Qt.AlignCenter)
        ctrl_row.addLayout(cooler_col)

        shift_col = QVBoxLayout()
        shift_col.setAlignment(Qt.AlignCenter)
        shift_lbl = QLabel("SHIFT MODE")
        shift_lbl.setStyleSheet("color: #8b2020; font-weight: bold; font-size: 11px;")
        shift_lbl.setAlignment(Qt.AlignCenter)
        shift_col.addWidget(shift_lbl)
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(SHIFT_MODES)
        self.shift_combo.currentTextChanged.connect(self._on_shift_mode)
        shift_col.addWidget(self.shift_combo)
        ctrl_row.addLayout(shift_col)

        layout.addLayout(ctrl_row)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def update_data(self, snap):
        ec = snap.ec

        for i, g in enumerate(self.fan_gauges):
            rpm = 0
            for f in snap.sensors.fans:
                if f"fan{i+1}" in f.label.lower():
                    rpm = f.speed_rpm
                    break
            color = QColor(get_fan_color(rpm, 6000))
            g.set_value(rpm, 6000, color)
            g.set_suffix("RPM")

        active = sum(1 for f in snap.sensors.fans if f.speed_rpm > 0)
        self.fan_note.setText(
            f"{len(snap.sensors.fans)} channels detected  |  {active} active"
        )

        if ec.available:
            self.ec_status.setText("✓ msi-ec connected — controls active")
            self.ec_status.setStyleSheet("color: #8b2020; font-weight: bold; font-size: 12px;")
            self.fan_mode_combo.setEnabled(True)
            self.cooler_boost_btn.setEnabled(True)
            self.shift_combo.setEnabled(True)

            if ec.fan_mode and self.fan_mode_combo.currentText() != ec.fan_mode:
                idx = self.fan_mode_combo.findText(ec.fan_mode)
                if idx >= 0:
                    self.fan_mode_combo.blockSignals(True)
                    self.fan_mode_combo.setCurrentIndex(idx)
                    self.fan_mode_combo.blockSignals(False)
            self.cooler_boost_btn.setChecked(ec.cooler_boost)
            self.cooler_boost_btn.setText("ON" if ec.cooler_boost else "OFF")

            if ec.shift_mode:
                idx = self.shift_combo.findText(ec.shift_mode)
                if idx >= 0:
                    self.shift_combo.blockSignals(True)
                    self.shift_combo.setCurrentIndex(idx)
                    self.shift_combo.blockSignals(False)
        else:
            self.ec_status.setText("msi-ec not loaded — monitoring only")
            self.ec_status.setStyleSheet("color: #666666; font-size: 12px;")
            self.fan_mode_combo.setEnabled(False)
            self.cooler_boost_btn.setEnabled(False)
            self.shift_combo.setEnabled(False)

    def _on_fan_mode_changed(self, mode: str):
        self.ec_write.emit("fan_mode", mode)

    def _on_cooler_boost(self):
        enabled = self.cooler_boost_btn.isChecked()
        self.cooler_boost_btn.setText("ON" if enabled else "OFF")
        self.ec_write.emit("cooler_boost", "on" if enabled else "off")

    def _on_shift_mode(self, mode: str):
        self.ec_write.emit("shift_mode", mode)
