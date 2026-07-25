"""Main application window for MSI Control Center."""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QStatusBar,
)
from PySide6.QtCore import Qt, Slot, QTimer

from core.config import APP_NAME, APP_VERSION, UPDATE_INTERVAL_MS
from core.monitor import MonitorService, SystemSnapshot
from core.hardware import HardwareController
from gui.theme import DARK_THEME
from gui.tabs.overview import OverviewTab
from gui.tabs.performance import PerformanceTab
from gui.tabs.hardware import HardwareTab
from gui.tabs.sensors import SensorsTab

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main control center window with tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(960, 700)
        self.resize(1050, 750)

        self.setStyleSheet(DARK_THEME)

        self._monitor = MonitorService(self)
        self._hardware = self._monitor.hardware

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.overview_tab = OverviewTab()
        self.performance_tab = PerformanceTab()
        self.hardware_tab = HardwareTab(self._hardware)
        self.sensors_tab = SensorsTab()

        self.tabs.addTab(self.overview_tab, "  OVERVIEW  ")
        self.tabs.addTab(self.performance_tab, "  PERFORMANCE  ")
        self.tabs.addTab(self.hardware_tab, "  HARDWARE  ")
        self.tabs.addTab(self.sensors_tab, "  SENSORS  ")

        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing...")

    def _connect_signals(self):
        self._monitor.data_updated.connect(self._on_data_updated)
        self._monitor.error_occurred.connect(self._on_error)
        self.hardware_tab.ec_write.connect(self._on_ec_write)

    @Slot()
    def start_monitoring(self):
        self._monitor.start()
        self.status_bar.showMessage("Monitoring active")

    @Slot()
    def stop_monitoring(self):
        self._monitor.stop()
        self.status_bar.showMessage("Monitoring paused")

    @Slot(object)
    def _on_data_updated(self, snap: SystemSnapshot):
        try:
            self.overview_tab.update_data(snap)
            self.performance_tab.update_data(snap)
            self.hardware_tab.update_data(snap)
            self.sensors_tab.update_data(snap)

            temp_str = ""
            if snap.sensors.temps:
                t = snap.sensors.temps[0]
                temp_str = f" | {t.label}: {t.current:.0f}°C"
            self.status_bar.showMessage(
                f"CPU: {snap.cpu.overall:.0f}% | "
                f"RAM: {snap.memory.percent:.0f}% | "
                f"Up: {snap.network.speed_up:.0f} B/s | "
                f"Down: {snap.network.speed_down:.0f} B/s"
                f"{temp_str}"
            )
        except Exception as e:
            log.error("Error updating UI: %s", e)

    @Slot(str)
    def _on_error(self, msg: str):
        self.status_bar.showMessage(f"Error: {msg}", 5000)

    @Slot(str, str)
    def _on_ec_write(self, action: str, value: str):
        success = False
        if action == "fan_mode":
            success = self._hardware.set_fan_mode(value)
        elif action == "shift_mode":
            success = self._hardware.set_shift_mode(value)
        elif action == "cooler_boost":
            success = self._hardware.set_cooler_boost(value == "on")
        elif action == "webcam":
            success = self._hardware.set_webcam(value)
        elif action == "fn_key":
            success = self._hardware.set_fn_key(value)
        elif action == "super_battery":
            success = self._hardware.set_super_battery(value == "on")

        if success:
            self.status_bar.showMessage(f"Set {action} = {value}", 3000)
        else:
            self.status_bar.showMessage(f"Failed to set {action} (check permissions)", 5000)

    def closeEvent(self, event):
        self._monitor.stop()
        super().closeEvent(event)
