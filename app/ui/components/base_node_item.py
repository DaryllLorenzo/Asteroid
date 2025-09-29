# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal, Qt, QPointF
from app.ui.components.subcanvas_item import SubCanvasItem
import math


class BaseNodeItem(QGraphicsObject):
    nodeDoubleClicked = pyqtSignal(object)
    subcanvas_toggled = pyqtSignal(object, object)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self._resizing = False
        self.subcanvas = None

    def boundingRect(self) -> QRectF:
        r = getattr(self.model, "radius", 50)
        return QRectF(-r, -r, 2 * r, 2 * r)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """Distancia al borde del círculo (implementación por defecto)."""
        r = getattr(self.model, "radius", 50)
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return abs(center_dist - r)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """Calcula nuevo radio basado en la posición del mouse."""
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return max(center_dist, 10.0)

    def hoverMoveEvent(self, event):
        """Solo activar cursor de redimensionamiento cerca del borde."""
        dist = self._get_distance_to_border(event.pos())
        if dist < 8:  # Umbral de proximidad al borde
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        """Restaurar cursor al salir del item."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._get_distance_to_border(event.pos())
            if dist < 8:  # Solo activar redimensionamiento si está cerca del borde
                self._resizing = True
                event.accept()
                return
        # Si no es resize, delegamos (para permitir movimiento)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            new_r = self._get_new_radius_from_pos(event.pos())
            self.set_radius(new_r)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing and event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_radius(self, new_r: float):
        """Actualiza el radio del modelo y del subcanvas si existe."""
        self.prepareGeometryChange()
        self.model.radius = new_r
        if self.subcanvas:
            self.subcanvas.set_radius(new_r * 1.05)
        self.update()

    def mouseDoubleClickEvent(self, event):
        """Maneja el doble click para mostrar/ocultar subcanvas."""
        if hasattr(self.model, "toggle_subcanvas"):
            self.model.toggle_subcanvas()
        else:
            self.model.show_subcanvas = not getattr(self.model, "show_subcanvas", False)

        if getattr(self.model, "show_subcanvas", False):
            if not self.subcanvas:
                self.subcanvas = SubCanvasItem(radius=self.model.radius * 1.05)
                self.subcanvas.setParentItem(self)
                self.subcanvas.setPos(0.0, 0.0)
                try:
                    self.subcanvas.setZValue(self.zValue() - 1)
                except Exception:
                    pass
            else:
                self.subcanvas.setVisible(True)
            self.subcanvas_toggled.emit(self, self.subcanvas)
        else:
            if self.subcanvas:
                self.subcanvas.setVisible(False)
            self.subcanvas_toggled.emit(self, None)

        self.update()
        self.nodeDoubleClicked.emit(self.model)
        super().mouseDoubleClickEvent(event)