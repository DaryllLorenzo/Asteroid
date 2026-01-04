# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QFont, QColor

class BaseTroposItem(QGraphicsObject):
    nodeDoubleClicked = pyqtSignal(object)
    properties_changed = pyqtSignal(object, dict)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
        self._resizing = False
        if not hasattr(self.model, 'font_size'): self.model.font_size = 10

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
        """Actualiza el radio del modelo"""
        self.prepareGeometryChange()
        old_r = getattr(self.model, 'radius', new_r)
        self.model.radius = new_r
        self.update()

        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def mouseDoubleClickEvent(self, event):
        event.ignore()
        super().mouseDoubleClickEvent(event)

    def draw_multiline_text(self, painter, text_color_hex):
        label = getattr(self.model, "label", "")
        if not label: return
        text_width = getattr(self.model, "text_width", 150)
        font_size = getattr(self.model, "font_size", 10)
        align_str = getattr(self.model, "text_align", "center")
        
        align_flag = Qt.AlignmentFlag.AlignCenter
        if align_str == "left": align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif align_str == "right": align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        
        painter.setPen(QColor(text_color_hex))
        font = QFont("Arial", int(font_size))
        font.setBold(True)
        painter.setFont(font)

        rect_height = 500 
        text_rect = QRectF(-text_width/2, -rect_height/2, text_width, rect_height)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | align_flag, label)

    def get_serializable_properties(self):
        return {
            'radius': getattr(self.model, 'radius', 50),
            'label': getattr(self.model, 'label', ''),
            'font_size': getattr(self.model, 'font_size', 10),
            'text_width': getattr(self.model, 'text_width', 150),
            'text_align': getattr(self.model, 'text_align', 'center'),
            'color': getattr(self.model, 'color', '#3498db'),
            'border_color': getattr(self.model, 'border_color', '#2980b9'),
            'text_color': getattr(self.model, 'text_color', '#ffffff'),
            'x': self.pos().x(),
            'y': self.pos().y()
        }
    
    def update_properties(self, properties: dict):
        """Actualiza las propiedades del nodo desde datos serializados"""
        for key, value in properties.items():
            if key == 'radius':
                self.set_radius(float(value))
            elif hasattr(self.model, key):
                setattr(self.model, key, value)
        
        if 'x' in properties and 'y' in properties:
            self.model.x = properties['x']
            self.model.y = properties['y']
            self.setPos(properties['x'], properties['y'])
        
        if 'radius' not in properties:
            self.update()
        
        self.properties_changed.emit(self, properties)