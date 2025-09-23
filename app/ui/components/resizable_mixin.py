from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsObject
from PyQt6.QtCore import Qt

class ResizeHandle(QGraphicsRectItem):
    """Cuadradito para redimensionar el nodo."""
    def __init__(self, owner, size=10):
        super().__init__(-size/2, -size/2, size, size, owner)
        self.setBrush(Qt.GlobalColor.red)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.owner = owner
        self._resizing = False

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            if self._resizing:
                return self.pos()
            self._resizing = True

            # Nuevo tamaño basado en posición relativa del handle
            new_pos = value
            new_r = max(new_pos.x(), new_pos.y(), 10)
            self.owner.set_radius(new_r)

            self._resizing = False
            return self.pos()  # el handle no se mueve libremente
        return super().itemChange(change, value)


class ResizableMixin:
    """Mixin para agregar resize vía handle a cualquier nodo."""
    def _init_resizable(self, initial_radius: float):
        self.radius = initial_radius
        self.resize_handle = ResizeHandle(self)
        self._update_handle_pos()

    def _update_handle_pos(self):
        # Coloca el handle en la esquina inferior derecha del boundingRect
        br = self.boundingRect()
        self.resize_handle.setPos(br.right(), br.bottom())

    def set_radius(self, new_r: float):
        self.prepareGeometryChange()
        self.radius = new_r
        if hasattr(self, "model") and hasattr(self.model, "radius"):
            self.model.radius = new_r
        self._update_handle_pos()
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionHasChanged:
            self._update_handle_pos()
        return QGraphicsRectItem.itemChange(self, change, value)
