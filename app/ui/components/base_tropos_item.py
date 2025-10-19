# base_tropos_item.py (corregido)
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal, Qt, QPointF
import math

class BaseTroposItem(QGraphicsObject):
    nodeDoubleClicked = pyqtSignal(object)
    properties_changed = pyqtSignal(object, dict)  # ✅ CORREGIDO: "properties_changed"

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self._resizing = False
        self.setZValue(10)

    def boundingRect(self) -> QRectF:
        r = getattr(self.model, "radius", 50)
        return QRectF(-r, -r, 2 * r, 2 * r)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        # Método base que será sobrescrito por las subclases
        r = getattr(self.model, "radius", 50)
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return abs(center_dist - r)

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        center_dist = (pos.x()**2 + pos.y()**2) ** 0.5
        return max(center_dist, 10.0)

    def hoverMoveEvent(self, event):
        # Solo activar el cursor de redimensionamiento si está cerca del borde
        dist = self._get_distance_to_border(event.pos())
        if dist < 8:  # Umbral de proximidad al borde
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        # Restaurar cursor al salir del item
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._get_distance_to_border(event.pos())
            if dist < 8:  # Solo activar redimensionamiento si está cerca del borde
                self._resizing = True
                self.setSelected(True)  # ✅ Añadido: seleccionar durante resize
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
        """Actualiza el radio del modelo"""
        self.prepareGeometryChange()
        old_r = getattr(self.model, 'radius', new_r)
        self.model.radius = new_r
        self.update()

        # ✅ Emitir señal solo si el valor realmente cambió
        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def mouseDoubleClickEvent(self, event):
        event.ignore()
        super().mouseDoubleClickEvent(event)

    #def update_properties(self, properties: dict):
    #    """Actualiza las propiedades visuales del nodo"""
    #    for key, value in properties.items():
    #        if key == 'radius':
    #            # ✅ Usar set_radius para garantizar prepareGeometryChange y emisión
    #            self.set_radius(float(value))
    #        elif hasattr(self.model, key):
    #            setattr(self.model, key, value)
    #    
    #    # Solo update() si no fue radio (porque set_radius ya hace update)
    #    if 'radius' not in properties:
    #        self.update()
    #    
    #    # Emitir señal para el panel (aunque set_radius ya emite para radius)
    #    if 'radius' not in properties:
    #        self.properties_changed.emit(self, properties)

    # En base_tropos_item.py - agrega al final de la clase BaseTroposItem

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
            # Agrega más propiedades según necesites
        }
    
    def update_properties(self, properties: dict):
        """Actualiza las propiedades del nodo desde datos serializados"""
        for key, value in properties.items():
            if key == 'radius':
                # Usar set_radius para garantizar prepareGeometryChange y emisión
                self.set_radius(float(value))
            elif hasattr(self.model, key):
                setattr(self.model, key, value)
        
        # Actualizar posición si está en las propiedades
        if 'x' in properties and 'y' in properties:
            self.model.x = properties['x']
            self.model.y = properties['y']
            self.setPos(properties['x'], properties['y'])
        
        # Solo update() si no fue radio (porque set_radius ya hace update)
        if 'radius' not in properties:
            self.update()
        
        # Emitir señal para el panel
        self.properties_changed.emit(self, properties)