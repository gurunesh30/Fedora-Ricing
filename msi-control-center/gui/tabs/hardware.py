"""MSI hardware control tab — fan modes, shift modes, cooler boost, peripherals."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox,
    QPushButton, QComboBox, QSlider, QGridLayout, QScrollArea, QButtonGroup,
)
from PySide6.QtCore import Qt, Signal

from gui.widgets import StatCard
from gui.theme import get_fan_color
from core.hardware import HardwareController, ECStatus
from core.config import FAN_CURVE_PRESETS, SHIFT_MODES


class HardwareTab(QWidget):
    """MSI-specific hardware controls."""

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
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        header = QLabel("Hardware Control")
        header.setProperty("class", "title")
        layout.addWidget(header)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #565f89; font-size: 11px;")
        layout.addWidget(self.status_label)

        ec_group = QGroupBox("Embedded Controller")
        ec_layout = QGridLayout(ec_group)
        ec_layout.setSpacing(10)

        ec_layout.addWidget(QLabel("EC Firmware:"), 0, 0)
        self.fw_version = QLabel("—")
        ec_layout.addWidget(self.fw_version, 0, 1)
        ec_layout.addWidget(QLabel("EC Date:"), 0, 2)
        self.fw_date = QLabel("—")
        ec_layout.addWidget(self.fw_date, 0, 3)
        layout.addWidget(ec_group)

        fan_group = QGroupBox("Fan Control")
        fan_layout = QVBoxLayout(fan_group)

        fan_mode_row = QHBoxLayout()
        fan_mode_row.addWidget(QLabel("Fan Mode:"))
        self.fan_mode_combo = QComboBox()
        self.fan_mode_combo.addItems(["auto", "silent", "basic", "advanced"])
        self.fan_mode_combo.currentTextChanged.connect(self._on_fan_mode_changed)
        fan_mode_row.addWidget(self.fan_mode_combo)
        fan_mode_row.addStretch()
        fan_layout.addLayout(fan_mode_row)

        self.cooler_boost_btn = QPushButton("Cooler Boost (Max Fans)")
        self.cooler_boost_btn.setCheckable(True)
        self.cooler_boost_btn.clicked.connect(self._on_cooler_boost)
        fan_layout.addWidget(self.cooler_boost_btn)

        fan_stats_row = QHBoxLayout()
        self.cpu_fan_card = StatCard("CPU Fan", "—", "RPM")
        self.gpu_fan_card = StatCard("GPU Fan", "—", "RPM")
        fan_stats_row.addWidget(self.cpu_fan_card)
        fan_stats_row.addWidget(self.gpu_fan_card)
        fan_layout.addLayout(fan_stats_row)

        layout.addWidget(fan_group)

        shift_group = QGroupBox("Performance Profile")
        shift_layout = QVBoxLayout(shift_group)

        shift_btn_row = QHBoxLayout()
        self.shift_buttons: dict[str, QPushButton] = {}
        self.shift_group = QButtonGroup(self)
        for mode in SHIFT_MODES:
            btn = QPushButton(mode.capitalize())
            btn.setCheckable(True)
            btn.setMinimumWidth(90)
            self.shift_group.addButton(btn)
            self.shift_buttons[mode] = btn
            btn.clicked.connect(lambda checked, m=mode: self._on_shift_mode(m))
            shift_btn_row.addWidget(btn)
        shift_btn_row.addStretch()
        shift_layout.addLayout(shift_btn_row)
        layout.addWidget(shift_group)

        kb_group = QGroupBox("Keyboard Backlight")
        kb_layout = QHBoxLayout(kb_group)
        kb_layout.addWidget(QLabel("Brightness:"))
        self.kb_slider = QSlider(Qt.Horizontal)
        self.kb_slider.setRange(0, 3)
        self.kb_slider.setTickPosition(QSlider.TicksBelow)
        self.kb_slider.setTickInterval(1)
        self.kb_slider.valueChanged.connect(self._on_kb_backlight)
        kb_layout.addWidget(self.kb_slider)
        self.kb_level_label = QLabel("0")
        self.kb_level_label.setFixedWidth(30)
        kb_layout.addWidget(self.kb_level_label)
        layout.addWidget(kb_group)

        periph_group = QGroupBox("Peripherals")
        periph_layout = QGridLayout(periph_group)

        periph_layout.addWidget(QLabel("Webcam:"), 0, 0)
        self.webcam_combo = QComboBox()
        self.webcam_combo.addItems(["on", "off"])
        self.webcam_combo.currentTextChanged.connect(
            lambda v: self.ec_write.emit("webcam", v)
        )
        periph_layout.addWidget(self.webcam_combo, 0, 1)

        periph_layout.addWidget(QLabel("Fn Key Position:"), 1, 0)
        self.fn_combo = QComboBox()
        self.fn_combo.addItems(["left", "right"])
        self.fn_combo.currentTextChanged.connect(
            lambda v: self.ec_write.emit("fn_key", v)
        )
        periph_layout.addWidget(self.fn_combo, 1, 1)

        periph_layout.addWidget(QLabel("Super Battery:"), 2, 0)
        self.super_bat_btn = QPushButton("Off")
        self.super_bat_btn.setCheckable(True)
        self.super_bat_btn.clicked.connect(self._on_super_battery)
        periph_layout.addWidget(self.super_bat_btn, 2, 1)

        layout.addWidget(periph_group)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def update_data(self, snap):
        ec = snap.ec
        if not ec.available:
            self.status_label.setText(
                "⚠ msi-ec module not loaded. Install: https://github.com/BeardOverflow/msi-ec"
            )
            return

        self.status_label.setText("✓ MSI EC connected")
        self.fw_version.setText(ec.firmware_version or "—")
        self.fw_date.setText(ec.firmware_date or "—")

        if ec.fan_mode and self.fan_mode_combo.currentText() != ec.fan_mode:
            idx = self.fan_mode_combo.findText(ec.fan_mode)
            if idx >= 0:
                self.fan_mode_combo.blockSignals(True)
                self.fan_mode_combo.setCurrentIndex(idx)
                self.fan_mode_combo.blockSignals(False)

        self.cooler_boost_btn.setChecked(ec.cooler_boost)

        if ec.shift_mode:
            for mode, btn in self.shift_buttons.items():
                btn.setChecked(mode == ec.shift_mode)

        cpu_fan = ec.cpu_fan_speed
        gpu_fan = ec.gpu_fan_speed
        self.cpu_fan_card.set_value(f"{cpu_fan}", get_fan_color(cpu_fan))
        self.cpu_fan_card.set_subtitle(f"{cpu_fan * 60} RPM est.")
        self.gpu_fan_card.set_value(f"{gpu_fan}", get_fan_color(gpu_fan))
        self.gpu_fan_card.set_subtitle(f"{gpu_fan * 60} RPM est.")

        if ec.webcam:
            idx = self.webcam_combo.findText(ec.webcam)
            if idx >= 0:
                self.webcam_combo.blockSignals(True)
                self.webcam_combo.setCurrentIndex(idx)
                self.webcam_combo.blockSignals(False)

        if ec.fn_key:
            idx = self.fn_combo.findText(ec.fn_key)
            if idx >= 0:
                self.fn_combo.blockSignals(True)
                self.fn_combo.setCurrentIndex(idx)
                self.fn_combo.blockSignals(False)

        self.super_bat_btn.setChecked(ec.super_battery == "on")
        self.super_bat_btn.setText("On" if ec.super_battery == "on" else "Off")

    def _on_fan_mode_changed(self, mode: str):
        self.ec_write.emit("fan_mode", mode)

    def _on_cooler_boost(self):
        enabled = self.cooler_boost_btn.isChecked()
        self.ec_write.emit("cooler_boost", "on" if enabled else "off")

    def _on_shift_mode(self, mode: str):
        self.ec_write.emit("shift_mode", mode)

    def _on_kb_backlight(self, level: int):
        self.kb_level_label.setText(str(level))
        self._hw.set_keyboard_backlight(level)

    def _on_super_battery(self):
        enabled = self.super_bat_btn.isChecked()
        self.super_bat_btn.setText("On" if enabled else "Off")
        self.ec_write.emit("super_battery", "on" if enabled else "off")
