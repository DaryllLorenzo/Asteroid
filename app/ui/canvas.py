# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPainter, QWheelEvent, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.subcanvas_item import SubCanvasItem
from app.ui.components.control_point_handle import ControlPointHandle


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
        
        # ✅ Fondo blanco
        self.setBackgroundBrush(Qt.GlobalColor.white)
        self.scene.setBackgroundBrush(Qt.GlobalColor.white)


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

        # revisar si se soltó sobre un subcanvas
        viewport_pos = event.position().toPoint()
        items = self.items(viewport_pos)
        for it in items:
            if hasattr(it, "subnode_dropped") or hasattr(it, "subarrow_dropped"):
                local_pt = it.mapFromScene(scene_pos)
                if item_type in ["simple", "dashed", "dependency_link", "why_link",
                                 "or_decomposition", "and_decomposition", "contribution", "means_end"]:
                    # forward a subcanvas
                    it.subarrow_dropped.emit(item_type)
                    print(f"Canvas: forwarded arrow '{item_type}' to subcanvas {it}")
                else:
                    # forward a subcanvas node
                    it.subnode_dropped.emit(item_type, float(local_pt.x()), float(local_pt.y()))
                    print(f"Canvas: forwarded node '{item_type}' to subcanvas {it} at local {local_pt}")
                event.acceptProposedAction()
                return

        # si no hay subcanvas debajo, dropeo global
        if item_type in ["actor", "agent", "hard_goal", "soft_goal", "plan", "resource"]:
            self.node_dropped.emit(item_type, scene_pos.x(), scene_pos.y())
            print(f"Canvas: node dropped globally '{item_type}' at scene {scene_pos}")
            event.acceptProposedAction()
        elif item_type in ["simple", "dashed", "dependency_link", "why_link",
                           "or_decomposition", "and_decomposition", "contribution", "means_end"]:
            self.arrow_dropped.emit(item_type)
            print(f"Canvas: arrow dropped globally '{item_type}'")
            event.acceptProposedAction()
    
    def mousePressEvent(self, event):
        items = self.items(event.pos())

        # ✅ Prioridad: primero buscar nodos regulares (incluyendo nodos padre con subcanvas)
        for item in items:
            # Si es un nodo regular (no edge, no subcanvas)
            if not isinstance(item, (BaseEdgeItem, SubCanvasItem)):
                self.node_clicked.emit(item)
                super().mousePressEvent(event)
                return

            # ✅ Si es subcanvas, buscar el nodo padre y emitir ese
            if isinstance(item, SubCanvasItem):
                parent = item.parentItem()
                # Buscar recursivamente hasta encontrar un nodo que no sea subcanvas
                while parent is not None and isinstance(parent, SubCanvasItem):
                    parent = parent.parentItem()
                
                # Si encontramos un nodo padre válido, usarlo
                if parent is not None and not isinstance(parent, BaseEdgeItem):
                    print(f"🔍 Subcanvas click - usando nodo padre: {parent}")
                    self.node_clicked.emit(parent)
                else:
                    # Si no hay padre válido, ignorar
                    pass
                super().mousePressEvent(event)
                return

        # Comportamiento por defecto
        if items:
            self.node_clicked.emit(items[0])
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        Doble-click en una arista agrega un control point en esa posición.
        """
        scene_pos = self.mapToScene(event.position().toPoint())
        items = self.items(event.position().toPoint())
        
        # Buscar si hay un edge bajo el cursor
        for item in items:
            if isinstance(item, BaseEdgeItem) and not isinstance(item, ControlPointHandle):
                # Agregar control point en la posición del doble-click
                item.add_control_point(scene_pos)
                # Seleccionar el edge para mostrar los handles
                item.setSelected(True)
                return
        
        # Si no es en un edge, comportamiento por defecto
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """
        Cambia el cursor cuando está sobre un handle o edge.
        """
        scene_pos = self.mapToScene(event.position().toPoint())
        items = self.items(event.position().toPoint())
        
        # Buscar si hay un handle bajo el cursor
        cursor_over_handle = False
        for item in items:
            if isinstance(item, ControlPointHandle):
                cursor_over_handle = True
                break
        
        if cursor_over_handle:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            # Verificar si está sobre un edge
            cursor_over_edge = False
            for item in items:
                if isinstance(item, BaseEdgeItem) and item.isSelected():
                    cursor_over_edge = True
                    break
            
            if cursor_over_edge:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
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

    def keyPressEvent(self, event):
        """Maneja eventos de teclado para eliminación"""
        # Delegar el manejo de teclas al controlador
        # Las teclas Delete y Ctrl+D ya están manejadas por los QShortcut
        super().keyPressEvent(event)