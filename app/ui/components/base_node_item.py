from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal
from app.ui.components.subcanvas_item import SubCanvasItem
from app.ui.components.resizable_mixin import ResizableMixin

class BaseNodeItem(QGraphicsObject, ResizableMixin):
    nodeDoubleClicked = pyqtSignal(object)
    subcanvas_toggled = pyqtSignal(object, object)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)

        self.subcanvas = None
        self._init_resizable(getattr(self.model, "radius", 50))

    def boundingRect(self) -> QRectF:
        r = getattr(self.model, "radius", self.radius)
        return QRectF(-r, -r, r*2, r*2)

    def set_radius(self, new_r: float):
        ResizableMixin.set_radius(self, new_r)
        if self.subcanvas:
            self.subcanvas.set_radius(new_r * 1.05)

    def mouseDoubleClickEvent(self, event):
        if hasattr(self.model, "toggle_subcanvas"):
            self.model.toggle_subcanvas()
        else:
            self.model.show_subcanvas = not getattr(self.model, "show_subcanvas", False)

        if getattr(self.model, "show_subcanvas", False):
            if not self.subcanvas:
                self.subcanvas = SubCanvasItem(radius=self.model.radius*1.05)
                self.subcanvas.setParentItem(self)
                self.subcanvas.setPos(0.0, 0.0)
                try:
                    self.subcanvas.setZValue(self.zValue()-1)
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
