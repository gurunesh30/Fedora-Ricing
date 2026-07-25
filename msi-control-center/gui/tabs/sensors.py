"""Sensors — all temperature, fan, voltage, battery as speedometers."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from gui.widgets import Speedometer
from gui.theme import get_temperature_color, get_usage_color
from core.monitor import SystemSnapshot


class SensorsTab(QWidget):
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

        header = QLabel("SENSORS")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        temp_label = QLabel("TEMPERATURES")
        temp_label.setProperty("class", "subtitle")
        temp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(temp_label)

        self._temp_grid = QGridLayout()
        self._temp_grid.setSpacing(16)
        self._temp_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self._temp_grid)

        fan_label = QLabel("FAN SPEEDS")
        fan_label.setProperty("class", "subtitle")
        fan_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(fan_label)

        self._fan_grid = QGridLayout()
        self._fan_grid.setSpacing(16)
        self._fan_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self._fan_grid)

        volt_label = QLabel("VOLTAGES")
        volt_label.setProperty("class", "subtitle")
        volt_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(volt_label)

        self._volt_grid = QGridLayout()
        self._volt_grid.setSpacing(16)
        self._volt_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self._volt_grid)

        bat_label = QLabel("BATTERY")
        bat_label.setProperty("class", "subtitle")
        bat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(bat_label)

        bat_row = QHBoxLayout()
        bat_row.setSpacing(30)
        bat_row.setAlignment(Qt.AlignCenter)
        self.bat_charge_gauge = Speedometer("CHARGE", 180)
        self.bat_voltage_gauge = Speedometer("VOLTAGE", 180)
        self.bat_time_gauge = Speedometer("TIME LEFT", 180)
        bat_row.addWidget(self.bat_charge_gauge)
        bat_row.addWidget(self.bat_voltage_gauge)
        bat_row.addWidget(self.bat_time_gauge)
        layout.addLayout(bat_row)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _fill_grid(self, grid: QGridLayout, items: list, suffix: str, max_val: float, getter):
        while grid.count():
            grid.takeAt(0)
        cols = min(len(items), 6) or 1
        for i, item in enumerate(items):
            g = Speedometer("", 150)
            g.set_suffix(suffix)
            label, value = getter(item)
            g._label = label
            color_val = value / max_val if max_val > 0 else 0
            color = QColor(get_temperature_color(color_val * 100)) if "°C" in suffix or "RPM" in suffix else QColor("#8b2020")
            g.set_value(value, max_val, color)
            g.set_unit_label(f"{value:.0f}{suffix}" if isinstance(value, (int, float)) else str(value))
            row, col = divmod(i, cols)
            grid.addWidget(g, row, col)

    def update_data(self, snap: SystemSnapshot):
        def temp_getter(t):
            label = t.label.split(":")[-1].strip() if ":" in t.label else t.label
            return label[:12], t.current

        def fan_getter(f):
            label = f.label.split(":")[-1].strip() if ":" in f.label else f.label
            return label[:12], float(f.speed_rpm)

        def volt_getter(v):
            label = v.label.split(":")[-1].strip() if ":" in v.label else v.label
            return label[:12], v.current

        temps = snap.sensors.temps
        if temps:
            self._fill_grid(self._temp_grid, temps, "°C", 100.0, temp_getter)
        else:
            while self._temp_grid.count():
                self._temp_grid.takeAt(0)

        fans = snap.sensors.fans
        if fans:
            self._fill_grid(self._fan_grid, fans, "RPM", 7000.0, fan_getter)
        else:
            while self._fan_grid.count():
                self._fan_grid.takeAt(0)

        volts = snap.sensors.voltages
        if volts:
            self._fill_grid(self._volt_grid, volts, "V", 5.0, volt_getter)
        else:
            while self._volt_grid.count():
                self._volt_grid.takeAt(0)

        bat = snap.sensors.battery
        if bat:
            self.bat_charge_gauge.set_value(bat.percent, 100,
                                            QColor(get_usage_color(100 - bat.percent)))
            self.bat_charge_gauge.set_suffix("%")
            self.bat_charge_gauge.set_unit_label(f"{bat.percent:.0f}%")

            self.bat_voltage_gauge.set_value(0, 100, QColor("#8b2020"))
            self.bat_voltage_gauge.set_suffix("V")
            self.bat_voltage_gauge.set_unit_label("N/A")

            if bat.secs_left > 0:
                mins = bat.secs_left / 60
                self.bat_time_gauge.set_value(mins, 480, QColor("#8b2020"))
                hrs = bat.secs_left // 3600
                mns = (bat.secs_left % 3600) // 60
                self.bat_time_gauge.set_unit_label(f"{hrs}h {mns}m")
            else:
                self.bat_time_gauge.set_value(0, 480, QColor("#333333"))
                self.bat_time_gauge.set_unit_label("Charging" if bat.power_plugged else "N/A")
            self.bat_time_gauge.set_suffix("min")
        else:
            self.bat_charge_gauge.set_value(0, 100, QColor("#1a1a1a"))
            self.bat_charge_gauge.set_unit_label("N/A")
            self.bat_voltage_gauge.set_value(0, 100, QColor("#1a1a1a"))
            self.bat_voltage_gauge.set_unit_label("N/A")
            self.bat_time_gauge.set_value(0, 480, QColor("#1a1a1a"))
            self.bat_time_gauge.set_unit_label("N/A")
