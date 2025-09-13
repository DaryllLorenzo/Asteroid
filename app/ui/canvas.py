from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPainter, QWheelEvent
from PyQt6.QtCore import Qt, pyqtSignal

class Canvas(QGraphicsView):
    """Vista del lienzo. Gestiona la escena y el zoom."""

    zoom_changed = pyqtSignal(float)       # Nuevo factor de zoom
    node_dropped = pyqtSignal(str, float, float)   # tipo, x, y
    arrow_dropped = pyqtSignal(str)        # tipo de flecha
    node_clicked = pyqtSignal(object)      # para controladores

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Drag & Drop
        self.setAcceptDrops(True)

        # Zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        # Configuración de vista
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    # ---------------------
    # Drag & Drop
    # ---------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            return

        item_type = event.mimeData().text()
        scene_pos = self.mapToScene(event.position().toPoint())

        if item_type in ["actor", "agent"]:
            self.node_dropped.emit(item_type, scene_pos.x(), scene_pos.y())
            event.acceptProposedAction()

        elif item_type in ["simple", "dashed"]:
            self.arrow_dropped.emit(item_type)
            event.acceptProposedAction()

    # ---------------------
    # Eventos de mouse
    # ---------------------
    def mousePressEvent(self, event):
        items = self.items(event.pos())
        if items:
            self.node_clicked.emit(items[0])
        super().mousePressEvent(event)

    # ---------------------
    # Zoom
    # ---------------------
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.1 if angle > 0 else 0.9

            new_zoom = self.zoom_factor * factor
            if self.min_zoom <= new_zoom <= self.max_zoom:
                self.zoom_factor = new_zoom
                self.scale(factor, factor)
                self.zoom_changed.emit(self.zoom_factor)
        else:
            super().wheelEvent(event)

    def zoom_in(self):
        factor = 1.2
        new_zoom = self.zoom_factor * factor
        if new_zoom <= self.max_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        factor = 0.8
        new_zoom = self.zoom_factor * factor
        if new_zoom >= self.min_zoom:
            self.zoom_factor = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        self.resetTransform()
        self.zoom_factor = 1.0
        self.zoom_changed.emit(self.zoom_factor)
