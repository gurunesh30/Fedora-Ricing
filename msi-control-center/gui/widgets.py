"""Speedometer-only widget set."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QRadialGradient, QFont


class Speedometer(QFrame):
    """Circular speedometer gauge with arc, value, and label."""

    def __init__(self, label: str = "", size: int = 160, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._max = 100.0
        self._label = label
        self._suffix = "%"
        self._color = QColor("#8b2020")
        self._unit_label = ""
        self.setFixedSize(size, size)

    def set_value(self, value: float, max_val: float = 100.0, color: QColor = None):
        self._value = min(value, max_val)
        self._max = max_val
        if color:
            self._color = color
        self.update()

    def set_suffix(self, s: str):
        self._suffix = s

    def set_unit_label(self, s: str):
        self._unit_label = s

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 10
        pen_w = 6

        # Background dark circle
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#0f0f0f"))
        p.drawEllipse(int(cx - radius - 4), int(cy - radius - 4),
                       int((radius + 4) * 2), int((radius + 4) * 2))

        # Arc track
        arc_rect_w = int(radius * 2)
        arc_rect_h = int(radius * 2)
        arc_x = int(cx - radius)
        arc_y = int(cy - radius)

        bg_pen = QPen(QColor("#1a1a1a"), pen_w)
        bg_pen.setCapStyle(Qt.RoundCap)
        p.setPen(bg_pen)
        p.drawArc(arc_x, arc_y, arc_rect_w, arc_rect_h, 225 * 16, -270 * 16)

        # Filled arc
        pct = self._value / self._max if self._max > 0 else 0
        span = int(-270 * 16 * pct)

        # Gradient on the arc
        fg_pen = QPen(self._color, pen_w)
        fg_pen.setCapStyle(Qt.RoundCap)
        p.setPen(fg_pen)
        p.drawArc(arc_x, arc_y, arc_rect_w, arc_rect_h, 225 * 16, span)

        # Tick marks
        p.setPen(QPen(QColor("#2a2a2a"), 1))
        import math
        for i in range(28):
            angle = math.radians(225 - i * (270 / 27))
            inner = radius - 12
            outer = radius - 6
            x1 = cx + inner * math.cos(angle)
            y1 = cy - inner * math.sin(angle)
            x2 = cx + outer * math.cos(angle)
            y2 = cy - outer * math.sin(angle)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Major ticks at 0, 25, 50, 75, 100%
        p.setPen(QPen(QColor("#444444"), 2))
        for i in range(5):
            angle = math.radians(225 - i * (270 / 4))
            inner = radius - 16
            outer = radius - 6
            x1 = cx + inner * math.cos(angle)
            y1 = cy - inner * math.sin(angle)
            x2 = cx + outer * math.cos(angle)
            y2 = cy - outer * math.sin(angle)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Value text
        p.setPen(QColor("#d4d4d4"))
        font = QFont("JetBrains Mono", int(radius * 0.24), QFont.Bold)
        p.setFont(font)
        val_text = f"{self._value:.0f}" if self._value < 1000 else f"{self._value:.0f}"
        p.drawText(int(cx - radius), int(cy - radius * 0.35),
                   arc_rect_w, int(radius * 0.5),
                   Qt.AlignCenter, val_text)

        # Suffix / unit
        if self._suffix:
            p.setPen(QColor("#666666"))
            font.setPixelSize(int(radius * 0.13))
            font.setBold(False)
            p.setFont(font)
            p.drawText(int(cx - radius), int(cy + radius * 0.05),
                       arc_rect_w, int(radius * 0.3),
                       Qt.AlignCenter, self._unit_label or self._suffix)

        # Label at bottom
        p.setPen(QColor("#8b2020"))
        font.setPixelSize(int(radius * 0.14))
        font.setBold(True)
        p.setFont(font)
        p.drawText(int(cx - radius), int(cy + radius * 0.45),
                   arc_rect_w, int(radius * 0.3),
                   Qt.AlignHCenter | Qt.AlignTop, self._label)

        p.end()
