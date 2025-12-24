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
        self.setZValue(10)  # para superponer sobre flechas
        
        # Inicializar posición en subcanvas si no existe
        if not hasattr(self.model, 'position_in_subcanvas_x'):
            self.model.position_in_subcanvas_x = 0.0
        if not hasattr(self.model, 'position_in_subcanvas_y'):
            self.model.position_in_subcanvas_y = 0.0

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
        # Solo procesar si el clic es directamente en este nodo
        self._toggle_subcanvas()
        self.nodeDoubleClicked.emit(self.model)
        event.accept()

    def _toggle_subcanvas(self):
        """Alterna la visibilidad del subcanvas SIN mover el nodo"""
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
                # Solo establecer posición relativa al nodo
                self.subcanvas.setPos(0.0, 0.0)
                try:
                    self.subcanvas.setZValue(self.zValue() - 1)
                except Exception:
                    pass
                # ✅ Inicializar posición original del subcanvas
                self._subcanvas_original_pos = QPointF(0, 0)
            else:
                self.subcanvas.setVisible(True)
                try:
                    self.subcanvas.setZValue(self.zValue() - 1)
                except Exception:
                    pass
            
            self.subcanvas_toggled.emit(self, self.subcanvas)
            self._subcanvas_visible = True
            
            # ✅ Aplicar posición en subcanvas si existe (solo mueve el subcanvas)
            if hasattr(self.model, 'position_in_subcanvas_x') and hasattr(self.model, 'position_in_subcanvas_y'):
                if abs(self.model.position_in_subcanvas_x) > 0.001 or abs(self.model.position_in_subcanvas_y) > 0.001:
                    self.apply_position_in_subcanvas()
            
        else:
            if self.subcanvas:
                self.subcanvas.setVisible(False)
            self.subcanvas_toggled.emit(self, None)
            self._subcanvas_visible = False

        self.update()

    def ensure_subcanvas_visible(self):
        """Asegura que el subcanvas esté visible SIN mover el nodo"""
        if not getattr(self.model, "show_subcanvas", False):
            self.model.show_subcanvas = True

        if not self.subcanvas:
            initial_radius = max(120.0, self.model.radius * 2.0)
            self.subcanvas = SubCanvasItem(radius=initial_radius)
            self.subcanvas.setParentItem(self)
            self.subcanvas.setPos(0, 0)
            self.subcanvas.setVisible(True)
            try:
                self.subcanvas.setZValue(self.zValue() - 1)
            except Exception:
                pass
            # ✅ Inicializar posición original del subcanvas
            self._subcanvas_original_pos = QPointF(0, 0)
        else:
            self.subcanvas.setVisible(True)
            try:
                self.subcanvas.setZValue(self.zValue() - 1)
            except Exception:
                pass

        self.subcanvas_toggled.emit(self, self.subcanvas)
        self._subcanvas_visible = True
        
        # ✅ Aplicar posición en subcanvas si existe
        if hasattr(self.model, 'position_in_subcanvas_x') and hasattr(self.model, 'position_in_subcanvas_y'):
            if abs(self.model.position_in_subcanvas_x) > 0.001 or abs(self.model.position_in_subcanvas_y) > 0.001:
                self.apply_position_in_subcanvas()
        
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
            # ✅ Inicializar posición original del subcanvas
            self._subcanvas_original_pos = QPointF(0, 0)
        else:
            # Si el subcanvas ya existe, asegurarse de que esté configurado correctamente
            if not self.subcanvas.isVisible() and getattr(self.model, "show_subcanvas", False):
                self.subcanvas.setVisible(True)
                try:
                    self.subcanvas.setZValue(self.zValue() - 1)
                except Exception:
                    pass
        
        return self.subcanvas

    def apply_position_in_subcanvas(self):
        """Aplica la posición física del nodo dentro de su subcanvas manteniendo el subcanvas visualmente fijo"""
        if not hasattr(self.model, 'position_in_subcanvas_x') or not hasattr(self.model, 'position_in_subcanvas_y'):
            return

        # Solo aplicar si el subcanvas está visible
        if self.is_subcanvas_visible() and self.subcanvas:
            # 1. Calcular desplazamiento en píxeles
            offset_x = self.model.position_in_subcanvas_x * self.subcanvas.radius
            offset_y = self.model.position_in_subcanvas_y * self.subcanvas.radius
            
            # 2. Asegurar que tenemos posición original del subcanvas
            if not hasattr(self, '_subcanvas_original_pos'):
                self._subcanvas_original_pos = QPointF(0, 0)

            # 3. MOVER el subcanvas en la dirección OPUESTA para mantenerlo visualmente fijo
            # La posición visual del subcanvas debe ser: posición_original - offset
            new_subcanvas_pos = self._subcanvas_original_pos - QPointF(offset_x, offset_y)
            self.subcanvas.setPos(new_subcanvas_pos)

            # 4. Asegurar el correcto Z-order: nodo por encima del subcanvas
            self.setZValue(self.subcanvas.zValue() + 1)
            
            self.update()

    def position_within_subcanvas(self, x_norm, y_norm):
        """Posiciona el nodo dentro de su subcanvas manteniendo el subcanvas visualmente fijo"""
        if not self.is_subcanvas_visible() or not self.subcanvas:
            return
        
        # Aplicar posición al modelo
        self.model.position_in_subcanvas_x = x_norm
        self.model.position_in_subcanvas_y = y_norm
        
        # Aplicar posición física (solo mueve el subcanvas, NO el nodo)
        self.apply_position_in_subcanvas()
        
        # Emitir cambios para serialización
        self.properties_changed.emit(self, {
            'position_in_subcanvas_x': x_norm,
            'position_in_subcanvas_y': y_norm
        })

    def get_serializable_properties(self):
        """Devuelve propiedades serializables del nodo"""
        return {
            'radius': getattr(self.model, 'radius', 50),
            'label': getattr(self.model, 'label', ''),
            'color': getattr(self.model, 'color', '#3498db'),
            'border_color': getattr(self.model, 'border_color', '#2980b9'),
            'text_color': getattr(self.model, 'text_color', '#ffffff'),
            'x': self.model.x,
            'y': self.model.y,
            'content_offset_x': getattr(self.model, 'content_offset_x', 0.0),
            'content_offset_y': getattr(self.model, 'content_offset_y', 0.0),
            'position_in_subcanvas_x': getattr(self.model, 'position_in_subcanvas_x', 0.0),
            'position_in_subcanvas_y': getattr(self.model, 'position_in_subcanvas_y', 0.0),
        }

    def update_properties(self, properties: dict):
        """Actualiza las propiedades del nodo desde datos serializados"""
        for key, value in properties.items():
            if hasattr(self.model, key):
                setattr(self.model, key, value)

        # Actualizar radio si está en las propiedades
        if 'radius' in properties:
            self.prepareGeometryChange()
            self.model.radius = properties['radius']

        # Actualizar posición si está en las propiedades
        if 'x' in properties and 'y' in properties:
            self.model.x = properties['x']
            self.model.y = properties['y']
            self.setPos(properties['x'], properties['y'])

        # Aplicar posición dentro del subcanvas si cambió
        if ('position_in_subcanvas_x' in properties or 
            'position_in_subcanvas_y' in properties):
            # ✅ Solo aplicar si el subcanvas está visible
            if self.is_subcanvas_visible():
                self.apply_position_in_subcanvas()

        # Actualizar la visualización
        self.update()

        # Emitir señal de propiedades cambiadas
        self.properties_changed.emit(self, properties)

    def is_subcanvas_visible(self):
        """Verifica si el subcanvas está visible"""
        return (
            self.subcanvas is not None 
            and self.subcanvas.isVisible() 
            and getattr(self.model, "show_subcanvas", False)
        )