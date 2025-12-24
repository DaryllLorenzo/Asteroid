# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QRadialGradient

class PositionControlWidget(QWidget):
    """
    Widget tipo 'Joystick' para controlar la posición relativa (offset)
    de un elemento dentro de su contenedor circular.
    Emite valores normalizados entre -1.0 y 1.0.
    """
    position_changed = pyqtSignal(float, float)  # x, y (normalizados -1 a 1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self._x = 0.0  # Normalizado -1 a 1
        self._y = 0.0  # Normalizado -1 a 1
        self.is_dragging = False

    def set_position(self, x_norm, y_norm):
        """Establece la posición visual basada en valores normalizados (-1 a 1)"""
        self._x = max(-1.0, min(1.0, x_norm))
        self._y = max(-1.0, min(1.0, y_norm))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        center = QPointF(w / 2, h / 2)
        radius = min(w, h) / 2 - 5  # Margen de 5px

        # 1. Dibujar fondo (el área permitida)
        bg_gradient = QRadialGradient(center, radius)
        bg_gradient.setColorAt(0, QColor("#f0f0f0"))
        bg_gradient.setColorAt(1, QColor("#e0e0e0"))
        
        painter.setPen(QPen(QColor("#cccccc"), 2))
        painter.setBrush(QBrush(bg_gradient))
        painter.drawEllipse(center, radius, radius)

        # 2. Dibujar ejes cruzados (guías visuales)
        painter.setPen(QPen(QColor("#dddddd"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(center.x()), int(center.y() - radius), int(center.x()), int(center.y() + radius))
        painter.drawLine(int(center.x() - radius), int(center.y()), int(center.x() + radius), int(center.y()))

        # 3. Calcular posición del "handle" (la bolita)
        handle_x = center.x() + (self._x * radius)
        handle_y = center.y() + (self._y * radius)
        handle_pos = QPointF(handle_x, handle_y)
        handle_radius = 8

        # 4. Dibujar el handle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3498db"))
        painter.drawEllipse(handle_pos, handle_radius, handle_radius)
        
        # Brillo del handle
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

        # Calcular vector desde el centro
        dx = pos.x() - center_x
        dy = pos.y() - center_y

        # Distancia actual
        dist = (dx**2 + dy**2)**0.5

        # Normalizar si se sale del círculo
        if dist > max_radius:
            ratio = max_radius / dist
            dx *= ratio
            dy *= ratio

        # Convertir a rango -1 a 1
        self._x = dx / max_radius
        self._y = dy / max_radius
        
        self.update()
        self.position_changed.emit(self._x, self._y)