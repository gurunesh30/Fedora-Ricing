"""Reusable custom widgets for the control center."""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout,
)
from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient

from gui.theme import get_temperature_color, get_usage_color, bytes_to_human


class StatCard(QFrame):
    """A small card showing a label, a large value, and optional subtitle."""

    def __init__(self, title: str, value: str = "—", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setMinimumWidth(160)
        self.setMaximumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        self._title = QLabel(title)
        self._title.setProperty("class", "subtitle")
        self._title.setAlignment(Qt.AlignLeft)

        self._value = QLabel(value)
        self._value.setProperty("class", "value-large")
        self._value.setAlignment(Qt.AlignLeft)

        self._subtitle = QLabel(subtitle)
        self._subtitle.setAlignment(Qt.AlignLeft)
        self._subtitle.setStyleSheet("color: #565f89; font-size: 11px;")

        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._subtitle)

    def set_value(self, value: str, color: str = ""):
        self._value.setText(value)
        if color:
            self._value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")

    def set_subtitle(self, text: str, color: str = ""):
        self._subtitle.setText(text)
        if color:
            self._subtitle.setStyleSheet(f"color: {color}; font-size: 11px;")


class CircularProgress(QFrame):
    """A circular progress gauge drawn with QPainter."""

    def __init__(self, label: str = "", size: int = 120, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._max = 100.0
        self._label = label
        self._suffix = "%"
        self._color = QColor("#7aa2f7")
        self.setFixedSize(size, size)

    def set_value(self, value: float, max_val: float = 100.0, color: QColor = None):
        self._value = min(value, max_val)
        self._max = max_val
        if color:
            self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        margin = 6
        pen_width = 8
        rect_size = min(w, h) - margin * 2
        x = (w - rect_size) / 2
        y = (h - rect_size) / 2

        bg_pen = QPen(QColor("#2f3549"), pen_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(
            int(x), int(y), int(rect_size), int(rect_size),
            225 * 16, -270 * 16
        )

        pct = self._value / self._max if self._max > 0 else 0
        span = int(-270 * 16 * pct)

        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, self._color)
        grad.setColorAt(1, QColor("#7dcfff"))

        fg_pen = QPen(self._color, pen_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(fg_pen)
        painter.drawArc(
            int(x), int(y), int(rect_size), int(rect_size),
            225 * 16, span
        )

        painter.setPen(QColor("#c0caf5"))
        font = painter.font()
        font.setPixelSize(int(rect_size * 0.22))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            int(x), int(y), int(rect_size), int(rect_size),
            Qt.AlignCenter, f"{self._value:.0f}{self._suffix}"
        )

        font.setPixelSize(int(rect_size * 0.12))
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("#7aa2f7"))
        painter.drawText(
            int(x), int(y + rect_size * 0.6), int(rect_size), int(rect_size * 0.3),
            Qt.AlignHCenter | Qt.AlignTop, self._label
        )
        painter.end()


class BarWidget(QFrame):
    """Horizontal bar with label and value display."""

    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setMaximumHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self._label = QLabel(label)
        self._label.setFixedWidth(120)
        self._label.setStyleSheet("font-weight: bold;")

        self._bar = QProgressBar()
        self._bar.setTextVisible(True)
        self._bar.setFormat("%p%")
        self._bar.setRange(0, 100)
        self._bar.setValue(0)

        self._detail = QLabel("")
        self._detail.setFixedWidth(100)
        self._detail.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._detail.setStyleSheet("color: #565f89; font-size: 11px;")

        layout.addWidget(self._label)
        layout.addWidget(self._bar, 1)
        layout.addWidget(self._detail)

    def set_value(self, percent: float, detail: str = ""):
        self._bar.setValue(int(percent))
        color = get_usage_color(percent)
        self._bar.setStyleSheet(
            f"QProgressBar::chunk {{ border-radius: 6px; background: {color}; }}"
        )
        if detail:
            self._detail.setText(detail)


class SensorRow(QFrame):
    """A row in the sensors table showing label, value, and optional range bar."""

    def __init__(self, label: str, unit: str = "°C", parent=None):
        super().__init__(parent)
        self._unit = unit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self._label = QLabel(label)
        self._label.setFixedWidth(200)
        self._label.setStyleSheet("font-size: 12px;")

        self._value = QLabel("—")
        self._value.setFixedWidth(80)
        self._value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._value.setStyleSheet("font-weight: bold; font-size: 13px;")

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(8)
        self._bar.setTextVisible(False)

        layout.addWidget(self._label)
        layout.addWidget(self._value)
        layout.addWidget(self._bar, 1)

    def set_value(self, value: float, max_val: float = 100.0):
        self._value.setText(f"{value:.1f}{self._unit}")
        color = get_temperature_color(value) if self._unit == "°C" else "#7aa2f7"
        self._value.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {color};")
        pct = min(100, (value / max_val * 100)) if max_val > 0 else 0
        self._bar.setValue(int(pct))
        self._bar.setStyleSheet(
            f"QProgressBar::chunk {{ border-radius: 4px; background: {color}; }}"
        )


class NetworkSpeedWidget(QFrame):
    """Upload/download speed display with arrows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setMinimumWidth(160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        up_row = QHBoxLayout()
        up_label = QLabel("↑")
        up_label.setStyleSheet("color: #9ece6a; font-size: 16px; font-weight: bold;")
        self._up_value = QLabel("0 B/s")
        self._up_value.setStyleSheet("font-size: 14px; font-weight: bold;")
        up_row.addWidget(up_label)
        up_row.addWidget(self._up_value)

        down_row = QHBoxLayout()
        down_label = QLabel("↓")
        down_label.setStyleSheet("color: #7aa2f7; font-size: 16px; font-weight: bold;")
        self._down_value = QLabel("0 B/s")
        self._down_value.setStyleSheet("font-size: 14px; font-weight: bold;")
        down_row.addWidget(down_label)
        down_row.addWidget(self._down_value)

        layout.addLayout(up_row)
        layout.addLayout(down_row)

    def set_speeds(self, up: float, down: float):
        self._up_value.setText(f"{bytes_to_human(up)}/s")
        self._down_value.setText(f"{bytes_to_human(down)}/s")
