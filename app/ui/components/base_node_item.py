# base_node_item.py (corregido)
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
    properties_changed = pyqtSignal(object, dict)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self._resizing = False
        self.subcanvas = None
        self._subcanvas_visible = False
        self.setZValue(10) # para superponer sobre flechas

    def boundingRect(self) -> QRectF:
        r = getattr(self.model, "radius", 50)
        return QRectF(-r, -r, 2 * r, 2 * r)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        r = getattr(self.model, "radius", 50)
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return abs(center_dist - r)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return max(center_dist, 10.0)

    def hoverMoveEvent(self, event):
        dist = self._get_distance_to_border(event.pos())
        if dist < 8:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._get_distance_to_border(event.pos())
            if dist < 8:
                self._resizing = True
                self.setSelected(True)
                event.accept()
                return
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
        self.prepareGeometryChange()
        old_r = getattr(self.model, 'radius', new_r)
        self.model.radius = new_r
        self.update()

        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def mouseDoubleClickEvent(self, event):
        """Maneja el doble click para mostrar/ocultar subcanvas."""
        # ✅ Solo procesar si el clic es directamente en este nodo
        self._toggle_subcanvas()
        self.nodeDoubleClicked.emit(self.model)
        event.accept()

    def _toggle_subcanvas(self):
        """Alterna la visibilidad del subcanvas"""
        if hasattr(self.model, "toggle_subcanvas"):
            self.model.toggle_subcanvas()
        else:
            self.model.show_subcanvas = not getattr(self.model, "show_subcanvas", False)

        show = getattr(self.model, "show_subcanvas", False)
        
        if show:
            if not self.subcanvas:
                subcanvas_radius = max(120.0, self.model.radius * 2.0)
                self.subcanvas = SubCanvasItem(radius=subcanvas_radius)
                self.subcanvas.setParentItem(self)
                self.subcanvas.setPos(0.0, 0.0)
                try:
                    self.subcanvas.setZValue(self.zValue() - 1)
                except Exception:
                    pass
            else:
                self.subcanvas.setVisible(True)
            self.subcanvas_toggled.emit(self, self.subcanvas)
            self._subcanvas_visible = True
        else:
            if self.subcanvas:
                self.subcanvas.setVisible(False)
            self.subcanvas_toggled.emit(self, None)
            self._subcanvas_visible = False

        self.update()

    def ensure_subcanvas_visible(self):
        if not getattr(self.model, "show_subcanvas", False):
            self.model.show_subcanvas = True

        if not self.subcanvas:
            initial_radius = max(120.0, self.model.radius * 2.0)
            self.subcanvas = SubCanvasItem(radius=initial_radius)
            self.subcanvas.setParentItem(self)
            self.subcanvas.setPos(0, 0)
            self.subcanvas.setVisible(False)
            try:
                self.subcanvas.setZValue(self.zValue() - 1)
            except Exception:
                pass
        else:
            self.subcanvas.setVisible(True)

        self.subcanvas_toggled.emit(self, self.subcanvas)
        self._subcanvas_visible = True
        return self.subcanvas
    
    def prepare_subcanvas_for_internal_use(self):
        if not self.subcanvas:
            initial_radius = max(250.0, self.model.radius * 3.0)
            self.subcanvas = SubCanvasItem(radius=initial_radius)
            self.subcanvas.setParentItem(self)
            self.subcanvas.setPos(0, 0)
            self.subcanvas.setVisible(False)
            try:
                self.subcanvas.setZValue(self.zValue() - 1)
            except Exception:
                pass
            self.subcanvas._update_handle_pos()
        return self.subcanvas
    
    def update_properties(self, properties: dict):
        for key, value in properties.items():
            if key == 'radius':
                self.set_radius(float(value))
            elif hasattr(self.model, key):
                setattr(self.model, key, value)
        
        if 'radius' not in properties:
            self.update()
        
        if 'radius' not in properties:
            self.properties_changed.emit(self, properties)

    #def is_subcanvas_visible(self):
    #    return self._subcanvas_visible and self.subcanvas and self.subcanvas.isVisible()
    def is_subcanvas_visible(self):
        return (
            self.subcanvas is not None 
            and self.subcanvas.isVisible() 
            and getattr(self.model, "show_subcanvas", False)
        )