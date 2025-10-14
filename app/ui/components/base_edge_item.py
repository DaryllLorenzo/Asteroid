# base_edge_item.py (versión corregida para subcanvas)
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui import QPen, QPolygonF, QColor
from PyQt6.QtCore import QPointF, QRectF, Qt
import math

class BaseEdgeItem(QGraphicsLineItem):
    """Item gráfico base para una arista con punta de flecha."""

    def __init__(self, source_node, dest_node, color=QColor(0, 0, 0), dashed=False):
        super().__init__()
        self.source_node = source_node
        self.dest_node = dest_node
        self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(5)

        # Configurar pen
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        self.update_position()

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        return QRectF(
            self.line().p1(), self.line().p2()
        ).normalized().adjusted(-extra, -extra, extra, extra)

    def _get_node_border_point(self, node, target_pos, use_local_coords=False):
        """Calcula el punto de intersección en el borde del nodo hacia el punto objetivo"""
        if not node:
            return QPointF(0, 0)
            
        # Obtener la posición del nodo según el sistema de coordenadas
        if use_local_coords:
            # Para subcanvas: usar coordenadas locales
            node_pos = node.pos()
            # El target_pos ya está en coordenadas locales del subcanvas
            target_pos_local = target_pos
        else:
            # Para canvas principal: usar coordenadas de escena
            node_pos = node.scenePos()
            target_pos_local = target_pos
        
        # Calcular vector desde el nodo al objetivo
        dx = target_pos_local.x() - node_pos.x()
        dy = target_pos_local.y() - node_pos.y()
        
        # Calcular distancia
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:
            return node_pos
            
        # Obtener radio del nodo
        if hasattr(node, 'model') and hasattr(node.model, 'radius'):
            radius = node.model.radius
        else:
            rect = node.boundingRect()
            radius = min(rect.width(), rect.height()) / 2.0
        
        # Normalizar y escalar al radio
        scale_factor = radius / distance
        border_x = node_pos.x() + dx * scale_factor
        border_y = node_pos.y() + dy * scale_factor
        
        return QPointF(border_x, border_y)

    def update_position(self):
        """Recalcular posición - VERSIÓN CORREGIDA PARA SUBCANVAS"""
        if not self.source_node or not self.dest_node:
            return
    
        # Determinar si estamos en un subcanvas
        in_subcanvas = (hasattr(self.source_node, 'subcanvas_parent') and 
                       self.source_node.subcanvas_parent is not None and
                       hasattr(self.dest_node, 'subcanvas_parent') and 
                       self.dest_node.subcanvas_parent is not None and
                       self.source_node.subcanvas_parent == self.dest_node.subcanvas_parent)
    
        if in_subcanvas:
            # ✅ AMBOS nodos están en el MISMO subcanvas - usar coordenadas LOCALES
            src_pos = self.source_node.pos()
            dst_pos = self.dest_node.pos()
            
            # Calcular puntos de conexión en los bordes usando coordenadas locales
            start_point = self._get_node_border_point(self.source_node, dst_pos, use_local_coords=True)
            end_point = self._get_node_border_point(self.dest_node, src_pos, use_local_coords=True)
            
        else:
            # ❌ Nodos en diferentes contextos - usar coordenadas de ESCENA
            src_scene_pos = self.source_node.scenePos()
            dst_scene_pos = self.dest_node.scenePos()
            
            # Calcular puntos de conexión en los bordes usando coordenadas de escena
            start_point = self._get_node_border_point(self.source_node, dst_scene_pos, use_local_coords=False)
            end_point = self._get_node_border_point(self.dest_node, src_scene_pos, use_local_coords=False)
    
        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())

    def paint(self, painter, option, widget=None):
        if not self.source_node or not self.dest_node:
            return

        self.update_position()
        painter.setPen(self.pen())
        painter.drawLine(self.line())
        self._draw_arrow_head(painter)

    def _draw_arrow_head(self, painter):
        """Dibuja la punta de la flecha al final de la línea."""
        line = self.line()
        angle = math.atan2(line.dy(), line.dx())
        arrow_size = 10

        # Ajustar el punto final
        adjusted_end = line.p2() - QPointF(
            arrow_size * 0.5 * math.cos(angle),
            arrow_size * 0.5 * math.sin(angle),
        )

        arrow_p1 = adjusted_end - QPointF(
            arrow_size * math.cos(angle - math.pi / 6),
            arrow_size * math.sin(angle - math.pi / 6),
        )
        arrow_p2 = adjusted_end - QPointF(
            arrow_size * math.cos(angle + math.pi / 6),
            arrow_size * math.sin(angle + math.pi / 6),
        )

        painter.setBrush(self.pen().color())
        painter.drawPolygon(QPolygonF([adjusted_end, arrow_p1, arrow_p2]))