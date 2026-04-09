from __future__ import annotations

from math import sin

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget


STATE_COLORS = {
    "IDLE": "#44c2ff",
    "PASSIVE_LISTENING": "#36dca5",
    "ACTIVATED_LISTENING": "#ffd166",
    "THINKING": "#f089ff",
    "SPEAKING": "#7dfc8b",
    "WATCHING": "#66a3ff",
    "LEARNING_PERSON": "#ffb347",
    "CONTROLLING_APP": "#ff8a65",
    "ERROR": "#ff5a5f",
}


class OrbWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("OrbCard")
        self._mode = "IDLE"
        self._phase = 0.0
        self._pulse_strength = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(40)
        self.setMinimumHeight(220)

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self.update()

    def _tick(self) -> None:
        self._phase += 0.12
        self._pulse_strength = (sin(self._phase) + 1.0) / 2.0
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        base_color = QColor(STATE_COLORS.get(self._mode, "#44c2ff"))
        center = self.rect().center()
        radius = min(self.width(), self.height()) * (0.24 + self._pulse_strength * 0.06)

        glow = QRadialGradient(center, radius * 2.3)
        glow.setColorAt(0.0, QColor(base_color.red(), base_color.green(), base_color.blue(), 200))
        glow.setColorAt(0.35, QColor(base_color.red(), base_color.green(), base_color.blue(), 120))
        glow.setColorAt(1.0, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
        painter.setBrush(glow)
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(center, radius * 2.1, radius * 2.1)

        core = QRadialGradient(center, radius)
        core.setColorAt(0.0, QColor(255, 255, 255, 230))
        core.setColorAt(0.25, QColor(base_color.red(), base_color.green(), base_color.blue(), 255))
        core.setColorAt(1.0, QColor(base_color.red() // 2, base_color.green() // 2, base_color.blue() // 2, 230))
        painter.setBrush(core)
        painter.drawEllipse(center, radius, radius)
