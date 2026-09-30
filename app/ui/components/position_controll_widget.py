# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPen
from PyQt6.QtGui import QRadialGradient
from PyQt6.QtWidgets import QWidget

from app.ui.theme_manager import theme_manager


class PositionControlWidget(QWidget):
    """A circular pad for picking a normalized (-1..1, -1..1) position."""

    position_changed = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self._x = 0.0
        self._y = 0.0
        self.is_dragging = False

    def set_position(self, x_norm, y_norm):
        self._x = max(-1.0, min(1.0, x_norm))
        self._y = max(-1.0, min(1.0, y_norm))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        center = QPointF(w / 2, h / 2)
        radius = min(w, h) / 2 - 5

        dark = theme_manager().is_dark
        if dark:
            bg_gradient = QRadialGradient(center, radius)
            bg_gradient.setColorAt(0, QColor("#3d3d3d"))
            bg_gradient.setColorAt(1, QColor("#2d2d2d"))
            painter.setPen(QPen(QColor("#555555"), 2))
        else:
            bg_gradient = QRadialGradient(center, radius)
            bg_gradient.setColorAt(0, QColor("#f0f0f0"))
            bg_gradient.setColorAt(1, QColor("#e0e0e0"))
            painter.setPen(QPen(QColor("#cccccc"), 2))

        painter.setBrush(QBrush(bg_gradient))
        painter.drawEllipse(center, radius, radius)

        guide_color = QColor("#555555") if dark else QColor("#dddddd")
        painter.setPen(QPen(guide_color, 1, Qt.PenStyle.DashLine))
        painter.drawLine(
            int(center.x()),
            int(center.y() - radius),
            int(center.x()),
            int(center.y() + radius),
        )
        painter.drawLine(
            int(center.x() - radius),
            int(center.y()),
            int(center.x() + radius),
            int(center.y()),
        )

        handle_x = center.x() + (self._x * radius)
        handle_y = center.y() + (self._y * radius)
        handle_pos = QPointF(handle_x, handle_y)
        handle_radius = 8

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3498db"))
        painter.drawEllipse(handle_pos, handle_radius, handle_radius)

        painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawEllipse(QPointF(handle_x - 2, handle_y - 2), 3, 3)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_from_mouse(event.pos())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self._update_from_mouse(event.pos())

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def _update_from_mouse(self, pos):
        w, h = self.width(), self.height()
        center_x, center_y = w / 2, h / 2
        max_radius = min(w, h) / 2 - 5

        dx = pos.x() - center_x
        dy = pos.y() - center_y

        dist = (dx**2 + dy**2) ** 0.5

        if dist > max_radius:
            ratio = max_radius / dist
            dx *= ratio
            dy *= ratio

        self._x = dx / max_radius
        self._y = dy / max_radius

        self.update()
        self.position_changed.emit(self._x, self._y)
