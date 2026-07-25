"""Configuration constants for MSI Control Center."""

import os

APP_NAME = "MSI Control Center"
APP_VERSION = "1.0.0"
APP_ICON = "utilities-system-monitor"

MSI_EC_BASE = "/sys/devices/platform/msi-ec"
MSI_EC_CPU = os.path.join(MSI_EC_BASE, "cpu")
MSI_EC_GPU = os.path.join(MSI_EC_BASE, "gpu")

UPDATE_INTERVAL_MS = 1000
GRAPH_HISTORY_SECONDS = 60
GRAPH_MAX_POINTS = 60

CPU_TEMP_WARN = 75
CPU_TEMP_CRIT = 90
GPU_TEMP_WARN = 75
GPU_TEMP_CRIT = 90
FAN_SPEED_WARN = 80
FAN_SPEED_CRIT = 95

FAN_MODES = ["auto", "silent", "basic", "advanced"]
SHIFT_MODES = ["eco", "comfort", "sport", "turbo"]

FAN_CURVE_PRESETS = {
    "Silent": {30: 0, 40: 20, 50: 30, 60: 40, 70: 50, 80: 70, 90: 90, 100: 100},
    "Balanced": {30: 0, 40: 25, 50: 40, 60: 55, 70: 70, 80: 85, 90: 95, 100: 100},
    "Performance": {30: 10, 40: 35, 50: 55, 60: 70, 70: 85, 80: 95, 90: 100, 100: 100},
    "Aggressive": {30: 20, 40: 50, 50: 70, 60: 85, 70: 95, 80: 100, 90: 100, 100: 100},
}
