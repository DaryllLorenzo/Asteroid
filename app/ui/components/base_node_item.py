from PyQt6.QtWidgets import QGraphicsObject
from PyQt6.QtCore import QRectF, pyqtSignal

class BaseNodeItem(QGraphicsObject):
    nodeDoubleClicked = pyqtSignal(object)  # emite el modelo lógico

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setPos(model.x, model.y)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)

    def boundingRect(self) -> QRectF:
        r = self.model.radius
        return QRectF(-r, -r, r * 2, r * 2)

    def mouseDoubleClickEvent(self, event):
        self.model.toggle_subcanvas()
        for node in self.model.child_nodes:
            if hasattr(node, "setVisible"):
                node.setVisible(self.model.show_subcanvas)
        self.update()
        self.nodeDoubleClicked.emit(self.model)
        super().mouseDoubleClickEvent(event)