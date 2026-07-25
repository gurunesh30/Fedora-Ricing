"""Black + dull red speedometer theme."""

DARK_THEME = """
* {
    font-family: "JetBrains Mono", "Cascadia Code", monospace;
}

QWidget {
    background-color: #0a0a0a;
    color: #d4d4d4;
    font-size: 13px;
}

QMainWindow { background-color: #0a0a0a; }

QTabWidget::pane {
    border: 1px solid #1a1a1a;
    background-color: #0a0a0a;
}

QTabBar::tab {
    background-color: #111111;
    color: #8b2020;
    padding: 10px 24px;
    margin-right: 1px;
    border: none;
    font-weight: bold;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QTabBar::tab:selected {
    background-color: #0a0a0a;
    color: #cc3333;
    border-bottom: 2px solid #cc3333;
}

QTabBar::tab:hover:!selected {
    background-color: #1a1a1a;
    color: #aa2222;
}

QScrollBar:vertical {
    background: #0a0a0a;
    width: 6px;
}
QScrollBar::handle:vertical {
    background: #2a1010;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #8b2020; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #0a0a0a;
    height: 6px;
}
QScrollBar::handle:horizontal {
    background: #2a1010;
    border-radius: 3px;
    min-width: 30px;
}

QGroupBox {
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: bold;
    color: #8b2020;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QPushButton {
    background-color: #1a1010;
    color: #cc3333;
    border: 1px solid #3a1515;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2a1515;
    border-color: #8b2020;
}
QPushButton:pressed {
    background-color: #8b2020;
    color: #0a0a0a;
}
QPushButton:checked {
    background-color: #8b2020;
    color: #0a0a0a;
    border-color: #cc3333;
}
QPushButton:disabled {
    background-color: #0f0f0f;
    color: #333333;
    border-color: #1a1a1a;
}

QComboBox {
    background-color: #1a1010;
    color: #d4d4d4;
    border: 1px solid #3a1515;
    border-radius: 4px;
    padding: 5px 12px;
    min-width: 100px;
}
QComboBox:hover { border-color: #8b2020; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #cc3333;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #111111;
    color: #d4d4d4;
    border: 1px solid #3a1515;
    selection-background-color: #8b2020;
    selection-color: #0a0a0a;
}

QProgressBar {
    background-color: #1a1a1a;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    border-radius: 4px;
    background: #8b2020;
}

QSlider::groove:horizontal {
    background: #1a1a1a;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #cc3333;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #ff4444; }
QSlider::sub-page:horizontal {
    background: #8b2020;
    border-radius: 2px;
}

QToolTip {
    background-color: #1a1010;
    color: #d4d4d4;
    border: 1px solid #8b2020;
    border-radius: 3px;
    padding: 4px 8px;
}

QStatusBar {
    background-color: #0f0a0a;
    color: #666666;
    border-top: 1px solid #1a1a1a;
    font-size: 11px;
}

QLabel.title { font-size: 18px; font-weight: bold; color: #cc3333; }
QLabel.subtitle { font-size: 12px; color: #8b2020; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
"""


def get_temperature_color(temp: float, warn: float = 75, crit: float = 90) -> str:
    if temp >= crit:
        return "#ff4444"
    elif temp >= warn:
        return "#cc3333"
    return "#8b2020"


def get_fan_color(speed_rpm: int, max_rpm: int = 6000) -> str:
    pct = (speed_rpm / max_rpm * 100) if max_rpm > 0 else 0
    if pct >= 95:
        return "#ff4444"
    elif pct >= 70:
        return "#cc3333"
    return "#8b2020"


def get_usage_color(percent: float) -> str:
    if percent >= 90:
        return "#ff4444"
    elif percent >= 70:
        return "#cc3333"
    return "#8b2020"


def bytes_to_human(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def seconds_to_human(secs: float) -> str:
    if secs < 0:
        return "N/A"
    days = int(secs // 86400)
    hours = int((secs % 86400) // 3600)
    minutes = int((secs % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
