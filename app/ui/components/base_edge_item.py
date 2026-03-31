# base_edge_item.py (versión con control points)
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui import QPen, QPolygonF, QColor, QPainterPath, QPainter
from PyQt6.QtCore import QPointF, QRectF, Qt
import math

from app.ui.components.control_point_handle import ControlPointHandle


class BaseEdgeItem(QGraphicsPathItem):
    """
    Item gráfico base para una arista con punta de flecha.
    Soporta puntos de control para modificar la forma de la línea (estilo Draw.io).
    """

    def __init__(self, source_node, dest_node, color=QColor(0, 0, 0), dashed=False):
        super().__init__()
        self.source_node = source_node
        self.dest_node = dest_node
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(5)

        # Lista de puntos de control (coordenadas en sistema de escena)
        self.control_points: list[QPointF] = []
        # Lista de handles gráficos asociados a los control points
        self.control_handles: list[ControlPointHandle] = []
        # Indica si los handles están visibles (cuando el edge está seleccionado)
        self._handles_visible = False
        # Flag para evitar actualizaciones recursivas
        self._updating_position = False
        # Handle que se está arrastrando actualmente
        self._dragging_handle = None

        # Configurar pen
        self.edge_color = color
        self.is_dashed = dashed
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        # Cache de últimos puntos calculados
        self._start_point = QPointF(0, 0)
        self._end_point = QPointF(0, 0)

        self.update_position()
        
        # Conectar a los cambios de posición de los nodos
        self._connect_to_nodes()
    
    def _connect_to_nodes(self):
        """Conecta a las señales de cambio de posición de los nodos"""
        # Conectar a positionChanged de ambos nodos (si existe)
        if self.source_node and hasattr(self.source_node, 'positionChanged'):
            try:
                self.source_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass  # El nodo no tiene esta señal
        
        if self.dest_node and hasattr(self.dest_node, 'positionChanged'):
            try:
                self.dest_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass
    
    def _on_node_moved(self):
        """Callback cuando un nodo conectado se mueve"""
        if not self._updating_position:
            self.update_position()
            # Forzar redibujado y actualizar bounding rect
            self.update()
            self.prepareGeometryChange()

    def boundingRect(self):
        """Rectángulo delimitador que incluye la línea y los handles"""
        # Obtener todos los puntos relevantes
        points = [self._start_point, self._end_point] + self.control_points
        
        if not points:
            return QRectF(0, 0, 0, 0)
        
        # Calcular bounding box de todos los puntos
        min_x = min(p.x() for p in points)
        max_x = max(p.x() for p in points)
        min_y = min(p.y() for p in points)
        max_y = max(p.y() for p in points)
        
        # Agregar margen para la punta de flecha y handles
        extra = max(self.pen().width() + 20, ControlPointHandle.HANDLE_SIZE)
        
        return QRectF(min_x - extra, min_y - extra, 
                      max_x - min_x + extra * 2, max_y - min_y + extra * 2)

    def _get_node_border_point(self, node, target_pos, use_local_coords=False):
        """Calcula el punto de intersección en el borde del nodo hacia el punto objetivo"""
        if not node:
            return QPointF(0, 0)

        # Obtener la posición del nodo según el sistema de coordenadas
        if use_local_coords:
            # Para subcanvas: usar coordenadas locales
            node_pos = node.pos()
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

    def _calculate_path_points(self):
        """
        Calcula los puntos de la ruta (inicio, control points, fin).
        Retorna lista de puntos en coordenadas de escena.
        """
        if not self.source_node or not self.dest_node:
            return [], QPointF(0, 0), QPointF(0, 0)

        # Determinar si estamos en un subcanvas
        in_subcanvas = (hasattr(self.source_node, 'subcanvas_parent') and
                       self.source_node.subcanvas_parent is not None and
                       hasattr(self.dest_node, 'subcanvas_parent') and
                       self.dest_node.subcanvas_parent is not None and
                       self.source_node.subcanvas_parent == self.dest_node.subcanvas_parent)

        if in_subcanvas:
            # Ambos nodos en el mismo subcanvas - usar coordenadas locales convertidas a escena
            src_pos = self.source_node.scenePos()
            dst_pos = self.dest_node.scenePos()
            
            # Calcular puntos de conexión en los bordes
            start_point = self._get_node_border_point(self.source_node, dst_pos, use_local_coords=False)
            end_point = self._get_node_border_point(self.dest_node, src_pos, use_local_coords=False)
        else:
            # Nodos en canvas principal o diferentes contextos
            src_scene_pos = self.source_node.scenePos()
            dst_scene_pos = self.dest_node.scenePos()
            
            start_point = self._get_node_border_point(self.source_node, dst_scene_pos, use_local_coords=False)
            end_point = self._get_node_border_point(self.dest_node, src_scene_pos, use_local_coords=False)

        self._start_point = start_point
        self._end_point = end_point
        
        # Construir lista completa de puntos
        if self.control_points:
            # Hay control points: inicio -> controls -> fin
            all_points = [start_point] + self.control_points + [end_point]
        else:
            # Sin control points: solo inicio y fin
            all_points = [start_point, end_point]
        
        return all_points, start_point, end_point

    def update_position(self):
        """Recalcular la ruta completa incluyendo control points"""
        # Evitar actualizaciones recursivas
        if self._updating_position:
            return
        
        self._updating_position = True
        
        try:
            path_points, start_point, end_point = self._calculate_path_points()

            if not path_points:
                return

            # Transformar puntos de coordenadas de escena a locales
            # Si el edge no tiene escena, usar las coordenadas directamente
            if self.scene():
                local_points = [self.mapFromScene(p) for p in path_points]
            else:
                # Sin escena, asumir que el edge está en (0,0) y los puntos son relativos
                local_points = path_points
            
            # Crear el path en coordenadas locales
            path = QPainterPath(local_points[0])
            for point in local_points[1:]:
                path.lineTo(point)

            self.setPath(path)

            # Actualizar posición de los handles (solo si no se está arrastrando uno)
            if self._dragging_handle is None:
                self._update_handles_position()
        finally:
            self._updating_position = False

    def _update_handles_position(self):
        """Sincroniza la posición visual de los handles con los control_points"""
        # Asegurar que hay tantos handles como control points
        while len(self.control_handles) < len(self.control_points):
            handle = ControlPointHandle(
                self,
                self.control_points[len(self.control_handles)],
                self._on_handle_position_changed,
                self._on_handle_released
            )
            # Agregar el handle a la escena (los handles viven en coordenadas de escena)
            if self.scene():
                self.scene().addItem(handle)
            else:
                # Si el edge no tiene escena aún, se agregará cuando la tenga
                pass
            self.control_handles.append(handle)

        while len(self.control_handles) > len(self.control_points):
            handle = self.control_handles.pop()
            if handle.scene():
                handle.scene().removeItem(handle)

        # Actualizar posición de cada handle en coordenadas de escena
        # Los control_points están en coordenadas de escena
        for i, handle in enumerate(self.control_handles):
            if handle is not self._dragging_handle:
                # Los handles viven en la escena, así que usamos las coordenadas de escena directamente
                handle.setPos(self.control_points[i])
            handle.update_appearance(self.isSelected())
    
    def _on_handle_released(self):
        """Callback cuando se suelta un handle"""
        self._dragging_handle = None

    def _on_handle_position_changed(self, handle, new_pos):
        """Callback cuando un handle es arrastrado"""
        # Marcar este handle como el que se está arrastrando
        self._dragging_handle = handle

        # Encontrar el índice del handle que fue movido
        for i, h in enumerate(self.control_handles):
            if h is handle:
                # Este es el handle que se movió
                # new_pos está en coordenadas de escena (porque el handle vive en la escena)
                self.control_points[i] = new_pos
                # Recalcular solo el path (sin actualizar handles para evitar temblor)
                self._update_path_only()
                # Forzar redibujado suave
                self.update()
                break

    def _update_path_only(self):
        """Actualiza solo el path sin tocar los handles"""
        path_points, start_point, end_point = self._calculate_path_points()

        if not path_points:
            return

        # Transformar puntos de coordenadas de escena a locales
        # Si el edge no tiene escena, usar las coordenadas directamente
        if self.scene():
            local_points = [self.mapFromScene(p) for p in path_points]
        else:
            local_points = path_points
        
        # Crear el path en coordenadas locales
        path = QPainterPath(local_points[0])
        for point in local_points[1:]:
            path.lineTo(point)

        self.setPath(path)

    def set_handles_visible(self, visible: bool):
        """Muestra u oculta los handles de control"""
        self._handles_visible = visible
        for handle in self.control_handles:
            handle.setVisible(visible)

    def add_control_point(self, scene_pos: QPointF):
        """
        Agrega un punto de control en la posición dada.
        La posición debe estar en coordenadas de escena.
        """
        # Insertar en la posición correcta (más cercano al segmento)
        path_points, start_point, end_point = self._calculate_path_points()
        
        if len(path_points) < 2:
            return
        
        # Encontrar el segmento más cercano al punto clickeado
        min_dist = float('inf')
        insert_index = 0
        
        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]
            
            # Calcular distancia punto-segmento
            dist = self._point_to_segment_distance(scene_pos, p1, p2)
            
            if dist < min_dist:
                min_dist = dist
                insert_index = i + 1
        
        # Insertar el nuevo control point
        self.control_points.insert(insert_index, scene_pos)
        
        # Actualizar handles
        self._update_handles_position()
        
        # Recalcular ruta
        self.update_position()

    def _point_to_segment_distance(self, point: QPointF, line_start: QPointF, line_end: QPointF) -> float:
        """Calcula la distancia mínima de un punto a un segmento de línea"""
        dx = line_end.x() - line_start.x()
        dy = line_end.y() - line_start.y()
        
        if dx == 0 and dy == 0:
            # El segmento es un punto
            return math.hypot(point.x() - line_start.x(), point.y() - line_start.y())
        
        # Proyección del punto sobre la línea
        t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        
        # Punto más cercano en el segmento
        closest_x = line_start.x() + t * dx
        closest_y = line_start.y() + t * dy
        
        return math.hypot(point.x() - closest_x, point.y() - closest_y)

    def remove_control_point(self, index: int = -1):
        """
        Elimina un punto de control.
        Si index es -1, elimina el último.
        """
        if not self.control_points:
            return
        
        if index == -1:
            index = len(self.control_points) - 1
        
        if 0 <= index < len(self.control_points):
            self.control_points.pop(index)
            self._update_handles_position()
            self.update_position()

    def clear_control_points(self):
        """Elimina todos los puntos de control, volviendo a línea recta"""
        self.control_points.clear()
        self._update_handles_position()
        self.update_position()

    def get_control_point_at(self, scene_pos: QPointF, tolerance: float = 10.0) -> int:
        """
        Retorna el índice del control point más cercano a la posición dada.
        Retorna -1 si no hay ninguno dentro de la tolerancia.
        """
        for i, point in enumerate(self.control_points):
            dx = point.x() - scene_pos.x()
            dy = point.y() - scene_pos.y()
            if math.hypot(dx, dy) <= tolerance:
                return i
        return -1

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Maneja cambios de estado del item (selección, escena, etc.)"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Actualizar visibilidad de handles
            self.set_handles_visible(self.isSelected())
            # Actualizar apariencia de handles
            for handle in self.control_handles:
                handle.update_appearance(self.isSelected())
        
        # Cuando el edge se agrega a una escena, asegurar que los handles también se agreguen
        elif change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
            new_scene = value
            if new_scene:
                # Agregar handles a la nueva escena si no están ya
                for handle in self.control_handles:
                    if not handle.scene():
                        new_scene.addItem(handle)
        
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        """Dibuja la arista con su punta de flecha"""
        if not self.source_node or not self.dest_node:
            return

        # NO llamar a update_position() aquí para evitar temblor
        # El path ya debería estar actualizado por _on_handle_position_changed
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Dibujar el path
        painter.drawPath(self.path())

        # Dibujar punta de flecha
        self._draw_arrow_head(painter)

    def _draw_arrow_head(self, painter: QPainter):
        """Dibuja la punta de la flecha al final de la línea."""
        path = self.path()
        if path.isEmpty():
            return
        
        # Obtener el último punto del path
        end_point = self._end_point
        start_point = self._start_point
        
        if not self.control_points:
            # Línea recta simple
            line_end = self._end_point
            line_start = self._start_point
        else:
            # Con control points: usar el último segmento
            if len(self.control_points) > 0:
                line_end = self._end_point
                line_start = self.control_points[-1]
            else:
                line_end = self._end_point
                line_start = self._start_point
        
        # Calcular ángulo
        dx = line_end.x() - line_start.x()
        dy = line_end.y() - line_start.y()
        
        if dx == 0 and dy == 0:
            return
        
        angle = math.atan2(dy, dx)
        arrow_size = 10

        # Ajustar el punto final
        adjusted_end = QPointF(
            line_end.x() - arrow_size * 0.5 * math.cos(angle),
            line_end.y() - arrow_size * 0.5 * math.sin(angle),
        )

        arrow_p1 = QPointF(
            adjusted_end.x() - arrow_size * math.cos(angle - math.pi / 6),
            adjusted_end.y() - arrow_size * math.sin(angle - math.pi / 6),
        )
        arrow_p2 = QPointF(
            adjusted_end.x() - arrow_size * math.cos(angle + math.pi / 6),
            adjusted_end.y() - arrow_size * math.sin(angle + math.pi / 6),
        )

        painter.setBrush(self.pen().color())
        painter.drawPolygon(QPolygonF([adjusted_end, arrow_p1, arrow_p2]))

    def clear_handles(self):
        """Elimina todos los handles de la escena"""
        for handle in self.control_handles:
            if handle.scene():
                handle.scene().removeItem(handle)
        self.control_handles.clear()
        self._dragging_handle = None
    
    def cleanup(self):
        """Limpia el edge: desconecta señales y elimina handles"""
        # Desconectar de los nodos
        if self.source_node and hasattr(self.source_node, 'positionChanged'):
            try:
                self.source_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass  # La señal ya estaba desconectada

        if self.dest_node and hasattr(self.dest_node, 'positionChanged'):
            try:
                self.dest_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass

        # Eliminar handles
        self.clear_handles()

    def _get_path_segments(self):
        """
        Retorna una lista de segmentos del path como tuplas (p1, p2, length).
        Cada segmento es una línea recta entre dos puntos consecutivos.
        """
        path_points, start_point, end_point = self._calculate_path_points()
        
        if len(path_points) < 2:
            return []
        
        segments = []
        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            length = math.hypot(dx, dy)
            segments.append((p1, p2, length))
        
        return segments

    def _get_point_at_distance(self, distance: float) -> tuple[QPointF, float]:
        """
        Retorna el punto en el path a una distancia específica desde el inicio.
        También retorna el ángulo/tangente en ese punto.
        
        Returns:
            tuple: (QPointF del punto, float del ángulo en radianes)
        """
        segments = self._get_path_segments()
        
        if not segments:
            return QPointF(0, 0), 0.0
        
        # Calcular longitud total del path
        total_length = sum(seg[2] for seg in segments)
        
        if total_length == 0:
            return QPointF(0, 0), 0.0
        
        # Si la distancia es mayor que la longitud total, retornar el último punto
        if distance >= total_length:
            last_seg = segments[-1]
            angle = math.atan2(last_seg[1].y() - last_seg[0].y(), 
                              last_seg[1].x() - last_seg[0].x())
            return last_seg[1], angle
        
        # Encontrar el segmento que contiene el punto deseado
        accumulated = 0.0
        for p1, p2, seg_length in segments:
            if accumulated + seg_length >= distance:
                # El punto está en este segmento
                t = (distance - accumulated) / seg_length if seg_length > 0 else 0
                x = p1.x() + t * (p2.x() - p1.x())
                y = p1.y() + t * (p2.y() - p1.y())
                angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
                return QPointF(x, y), angle
            accumulated += seg_length
        
        # No debería llegar aquí
        last_seg = segments[-1]
        angle = math.atan2(last_seg[1].y() - last_seg[0].y(), 
                          last_seg[1].x() - last_seg[0].x())
        return last_seg[1], angle

    def _get_tangent_at_distance(self, distance: float) -> float:
        """
        Retorna el ángulo/tangente del path en un punto a cierta distancia desde el inicio.
        
        Returns:
            float: ángulo en radianes
        """
        _, angle = self._get_point_at_distance(distance)
        return angle

    def _get_point_at_percentage(self, percentage: float) -> tuple[QPointF, float]:
        """
        Retorna el punto en el path a un porcentaje específico (0.0 a 1.0).
        También retorna el ángulo/tangente en ese punto.
        
        Returns:
            tuple: (QPointF del punto, float del ángulo en radianes)
        """
        segments = self._get_path_segments()
        
        if not segments:
            return QPointF(0, 0), 0.0
        
        # Calcular longitud total del path
        total_length = sum(seg[2] for seg in segments)
        
        if total_length == 0:
            return QPointF(0, 0), 0.0
        
        target_distance = total_length * percentage
        return self._get_point_at_distance(target_distance)
