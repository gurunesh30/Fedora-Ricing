"""Sensors tab — all temperature, fan, and voltage readings."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox,
    QGridLayout, QScrollArea,
)
from PySide6.QtCore import Qt

from gui.widgets import SensorRow, StatCard
from core.monitor import SystemSnapshot


class SensorsTab(QWidget):
    """Display all sensor readings from psutil and hwmon."""

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

        header = QLabel("Sensor Readings")
        header.setProperty("class", "title")
        layout.addWidget(header)

        temp_group = QGroupBox("Temperatures")
        self.temp_layout = QVBoxLayout(temp_group)
        self.temp_layout.setSpacing(2)
        layout.addWidget(temp_group)

        fan_group = QGroupBox("Fan Speeds")
        self.fan_layout = QVBoxLayout(fan_group)
        self.fan_layout.setSpacing(2)
        layout.addWidget(fan_group)

        volt_group = QGroupBox("Voltages")
        self.volt_layout = QVBoxLayout(volt_group)
        self.volt_layout.setSpacing(2)
        layout.addWidget(volt_group)

        bat_group = QGroupBox("Battery")
        bat_grid = QGridLayout(bat_group)
        self.bat_labels = {}
        for i, (key, label) in enumerate([
            ("percent", "Charge Level"),
            ("status", "Status"),
            ("time_left", "Time Remaining"),
            ("power", "Power Source"),
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: bold;")
            val = QLabel("—")
            val.setAlignment(Qt.AlignRight)
            bat_grid.addWidget(lbl, i, 0)
            bat_grid.addWidget(val, i, 1)
            self.bat_labels[key] = val
        layout.addWidget(bat_group)

        self.no_data_label = QLabel("")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        self.no_data_label.setStyleSheet("color: #565f89; font-size: 14px; padding: 20px;")
        layout.addWidget(self.no_data_label)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def update_data(self, snap: SystemSnapshot):
        self._clear_layout(self.temp_layout)
        self._clear_layout(self.fan_layout)
        self._clear_layout(self.volt_layout)

        if snap.sensors.temps:
            self.no_data_label.setText("")
            for t in snap.sensors.temps:
                max_val = t.critical if t.critical > 0 else 100.0
                row = SensorRow(t.label, "°C")
                row.set_value(t.current, max_val)
                self.temp_layout.addWidget(row)
        else:
            self.temp_layout.addWidget(QLabel("No temperature sensors found."))

        if snap.sensors.fans:
            for f in snap.sensors.fans:
                row = SensorRow(f.label, " RPM")
                row.set_value(f.speed_rpm, 7000)
                row._unit = " RPM"
                row._value.setText(f"{f.speed_rpm} RPM")
                self.fan_layout.addWidget(row)
        else:
            self.fan_layout.addWidget(QLabel("No fan sensors found."))

        if snap.sensors.voltages:
            for v in snap.sensors.voltages:
                row = SensorRow(v.label, "V")
                row.set_value(v.current, 5.0)
                self.volt_layout.addWidget(row)
        else:
            self.volt_layout.addWidget(QLabel("No voltage sensors found."))

        if snap.sensors.battery:
            b = snap.sensors.battery
            self.bat_labels["percent"].setText(f"{b.percent:.1f}%")
            status = "Charging" if b.power_plugged else "Discharging"
            if b.percent >= 100 and b.power_plugged:
                status = "Full"
            self.bat_labels["status"].setText(status)
            if b.secs_left > 0:
                hrs = b.secs_left // 3600
                mins = (b.secs_left % 3600) // 60
                self.bat_labels["time_left"].setText(f"{hrs}h {mins}m")
            else:
                self.bat_labels["time_left"].setText("Calculating..." if not b.power_plugged else "N/A")
            self.bat_labels["power"].setText("AC Power" if b.power_plugged else "Battery")
        else:
            for lbl in self.bat_labels.values():
                lbl.setText("N/A")
