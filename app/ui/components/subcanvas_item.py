# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsObject, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QBrush, QPen, QPainterPath
from PyQt6.QtCore import QRectF, pyqtSignal, Qt, QPointF
import math

# Lista de tipos de "links" soportados dentro del subcanvas
ARROW_TYPES = {
    "dependency_link", "why_link",
    "or_decomposition", "and_decomposition",
    "contribution", "means_end"
}


class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent_subcanvas, size: float = 10.0):
        super().__init__(-size/2.0, -size/2.0, size, size)
        self.setParentItem(parent_subcanvas)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)
        self.parent_subcanvas = parent_subcanvas
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, event):
        local_scene = event.scenePos()
        center_scene = self.parent_subcanvas.mapToScene(QPointF(0.0, 0.0))
        dx = local_scene.x() - center_scene.x()
        dy = local_scene.y() - center_scene.y()
        new_r = max(20.0, math.hypot(dx, dy))
        self.parent_subcanvas.set_radius(new_r)
        event.accept()


class SubCanvasItem(QGraphicsObject):
    # item_type, local_x, local_y  (nodes)
    subnode_dropped = pyqtSignal(str, float, float)
    # arrow_type (links)
    subarrow_dropped = pyqtSignal(str)

    def __init__(self, radius: float = 80.0, parent=None):
        super().__init__(parent)
        self.radius = float(radius)

        # Clip children visually to the circular shape
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)

        # no movible por separado; se mueve con el nodo padre
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptDrops(True)

        self.border_pen = QPen(Qt.GlobalColor.black, 2)
        self.bg_brush = QBrush(Qt.GlobalColor.white)

        # Create handle as child (no scene.addItem for the handle)
        self.handle = ResizeHandle(self, size=10)
        self._update_handle_pos()

    def boundingRect(self) -> QRectF:
        r = float(self.radius)
        margin = 4.0
        return QRectF(-r - margin, -r - margin, 2.0 * r + margin * 2.0, 2.0 * r + margin * 2.0)

    def shape(self):
        path = QPainterPath()
        r = float(self.radius)
        path.addEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        r = float(self.radius)
        painter.setBrush(self.bg_brush)
        painter.setOpacity(0.04)
        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))
        painter.setOpacity(1.0)
        painter.setPen(self.border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-r, -r, 2.0 * r, 2.0 * r))

    def set_radius(self, new_r: float):
        self.prepareGeometryChange()
        self.radius = max(20.0, float(new_r))
        self._update_handle_pos()
        self.update()

    def _update_handle_pos(self):
        if hasattr(self, "handle") and self.handle is not None:
            # sitúa el handle en el borde derecho del círculo
            self.handle.setPos(self.radius, 0.0)

    # -------------------------
    # Drag & Drop
    # -------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Reconoce si se soltó un nodo o un link (arrow) y emite la señal correspondiente."""
        if not event.mimeData().hasText():
            event.ignore()
            return

        item_type = event.mimeData().text()
        pos = event.pos()  # QPointF local a este item

        # Si es un tipo de flecha (links nuevos)
        if item_type in ARROW_TYPES:
            # Emitimos sólo el tipo de flecha (tu controller espera subarrow_dropped -> handler(arrow_type))
            print(f"SubCanvasItem: arrow dropped '{item_type}' (local {pos})")
            self.subarrow_dropped.emit(item_type)
            event.acceptProposedAction()
            return

        # Si no es flecha, lo tratamos como nodo tropos
        print(f"SubCanvasItem: node dropped '{item_type}' at local ({pos.x():.1f}, {pos.y():.1f})")
        self.subnode_dropped.emit(item_type, float(pos.x()), float(pos.y()))
        event.acceptProposedAction()
