"""Dark theme stylesheet for MSI Control Center."""

DARK_THEME = """
/* ===== Global ===== */
QWidget {
    background-color: #1a1b26;
    color: #c0caf5;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
    font-size: 13px;
}

QMainWindow {
    background-color: #1a1b26;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #2f3549;
    background-color: #1a1b26;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #24283b;
    color: #7aa2f7;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #2f3549;
    border-bottom: none;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #1a1b26;
    color: #c0caf5;
    border-bottom: 2px solid #7aa2f7;
}

QTabBar::tab:hover:!selected {
    background-color: #2f3549;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background-color: #1a1b26;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #3b4261;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7aa2f7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1a1b26;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #3b4261;
    border-radius: 5px;
    min-width: 30px;
}

/* ===== Cards / Frames ===== */
QFrame.card {
    background-color: #24283b;
    border: 1px solid #2f3549;
    border-radius: 10px;
    padding: 12px;
}

QFrame.card-accent {
    background-color: #24283b;
    border: 1px solid #7aa2f7;
    border-radius: 10px;
    padding: 12px;
}

/* ===== Labels ===== */
QLabel.title {
    font-size: 18px;
    font-weight: bold;
    color: #c0caf5;
}

QLabel.subtitle {
    font-size: 12px;
    color: #7aa2f7;
}

QLabel.value-large {
    font-size: 28px;
    font-weight: bold;
    color: #c0caf5;
}

QLabel.value-medium {
    font-size: 16px;
    font-weight: bold;
    color: #c0caf5;
}

QLabel.value-good { color: #9ece6a; }
QLabel.value-warn { color: #e0af68; }
QLabel.value-crit { color: #f7768e; }

/* ===== Progress Bars ===== */
QProgressBar {
    background-color: #2f3549;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: #c0caf5;
    font-size: 10px;
}

QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7aa2f7, stop:1 #7dcfff);
}

QProgressBar.temp-bar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #9ece6a, stop:0.6 #e0af68, stop:1.0 #f7768e);
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #2f3549;
    color: #c0caf5;
    border: 1px solid #3b4261;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3b4261;
    border-color: #7aa2f7;
}

QPushButton:pressed {
    background-color: #7aa2f7;
    color: #1a1b26;
}

QPushButton:checked {
    background-color: #7aa2f7;
    color: #1a1b26;
    border-color: #7aa2f7;
}

QPushButton:disabled {
    background-color: #1f2335;
    color: #565f89;
    border-color: #2f3549;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #2f3549;
    color: #c0caf5;
    border: 1px solid #3b4261;
    border-radius: 6px;
    padding: 5px 12px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #7aa2f7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #7aa2f7;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #3b4261;
    border-radius: 4px;
    selection-background-color: #7aa2f7;
    selection-color: #1a1b26;
}

/* ===== Slider ===== */
QSlider::groove:horizontal {
    background-color: #2f3549;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #7aa2f7;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #7dcfff;
}

QSlider::sub-page:horizontal {
    background-color: #7aa2f7;
    border-radius: 3px;
}

/* ===== Group Box ===== */
QGroupBox {
    border: 1px solid #2f3549;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #7aa2f7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* ===== Spin Box ===== */
QSpinBox {
    background-color: #2f3549;
    color: #c0caf5;
    border: 1px solid #3b4261;
    border-radius: 4px;
    padding: 3px 6px;
}

/* ===== Tooltips ===== */
QToolTip {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #7aa2f7;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #24283b;
    color: #565f89;
    border-top: 1px solid #2f3549;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #2f3549;
    width: 2px;
}

/* ===== Grid Layout Spacing ===== */
QFrame > QGridLayout {
    spacing: 10px;
}
"""


def get_temperature_color(temp: float, warn: float = 75, crit: float = 90) -> str:
    if temp >= crit:
        return "#f7768e"
    elif temp >= warn:
        return "#e0af68"
    return "#9ece6a"


def get_fan_color(speed_rpm: int, max_rpm: int = 6000) -> str:
    pct = (speed_rpm / max_rpm * 100) if max_rpm > 0 else 0
    if pct >= 95:
        return "#f7768e"
    elif pct >= 70:
        return "#e0af68"
    return "#7aa2f7"


def get_usage_color(percent: float) -> str:
    if percent >= 90:
        return "#f7768e"
    elif percent >= 70:
        return "#e0af68"
    return "#9ece6a"


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
