from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal
from app.ui.components.resizable_mixin import ResizableMixin

class BaseTroposItem(QGraphicsObject, ResizableMixin):
    nodeDoubleClicked = pyqtSignal(object)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self._init_resizable(getattr(self.model, "radius", 40))

    def boundingRect(self) -> QRectF:
        r = getattr(self.model, "radius", self.radius)
        return QRectF(-r, -r, r*2, r*2)

    def set_radius(self, new_r: float):
        ResizableMixin.set_radius(self, new_r)

    def mouseDoubleClickEvent(self, event):
        event.ignore()
        super().mouseDoubleClickEvent(event)
