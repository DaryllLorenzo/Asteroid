# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QBrush, QPen, QColor, QCursor
from PyQt6.QtCore import QPointF, Qt, QPoint
from typing import Callable, Optional


class ControlPointHandle(QGraphicsEllipseItem):
    """
    Handle arrastrable para modificar la forma de una arista.
    Representa un punto de control que el usuario puede arrastrar
    para deformar la línea (estilo Draw.io).
    """

    HANDLE_SIZE = 10.0  # Tamaño del handle en píxeles

    def __init__(self, parent_edge, position: QPointF, on_position_changed: Optional[Callable] = None, on_release: Optional[Callable] = None):
        super().__init__(-self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2,
                         self.HANDLE_SIZE, self.HANDLE_SIZE)

        self.parent_edge = parent_edge
        self.on_position_changed = on_position_changed
        self.on_release = on_release
        self.setPos(position)
        
        # Punto donde se hizo click inicial (para calcular offset)
        self._click_offset = QPointF(0, 0)

        # Configurar apariencia
        self.setPen(QPen(QColor(0, 100, 200), 2))
        self.setBrush(QBrush(QColor(255, 255, 255)))

        # NO usar ItemIsMovable - lo manejamos manualmente
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        # Cursor personalizado
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Z-value alto para estar por encima de la línea
        self.setZValue(100)

        # Estado
        self._is_dragging = False

    def mousePressEvent(self, event):
        """Iniciar arrastre del handle"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            # Seleccionar el handle para indicar que está activo
            self.setSelected(True)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mover el handle y notificar al edge padre"""
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Transformar posición de escena a coordenadas locales del padre (edge)
            parent = self.parentItem()
            if parent:
                # Convertir de coordenadas de escena a coordenadas locales del padre
                local_pos = parent.mapFromScene(event.scenePos())
                self.setPos(local_pos)
                new_pos = local_pos
            else:
                # Sin padre, usar coordenadas de escena directamente
                new_pos = event.scenePos()
                self.setPos(new_pos)

            # Notificar al edge padre sobre el cambio de posición
            if self.on_position_changed:
                self.on_position_changed(self, new_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finalizar arrastre"""
        self._is_dragging = False
        # Notificar que se soltó el handle
        if self.on_release:
            self.on_release()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        """Hover: resaltar el handle"""
        self.setBrush(QBrush(QColor(200, 230, 255)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Salir del hover: restaurar apariencia"""
        if not self.isSelected():
            self.setBrush(QBrush(QColor(255, 255, 255)))
        super().hoverLeaveEvent(event)

    def update_appearance(self, is_selected: bool):
        """Actualizar apariencia según estado de selección"""
        if is_selected:
            self.setBrush(QBrush(QColor(0, 100, 200)))
        else:
            self.setBrush(QBrush(QColor(255, 255, 255)))
