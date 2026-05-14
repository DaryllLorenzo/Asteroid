# base_edge_item.py (version with control points)
# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import math

from PyQt6.QtCore import QLineF
from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPainterPathStroker
from PyQt6.QtGui import QPen
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtWidgets import QStyleOptionGraphicsItem
from PyQt6.QtWidgets import QWidget

from app.ui.components.control_point_handle import ControlPointHandle


class BaseEdgeItem(QGraphicsPathItem):
    """
    Base Edge Item.

    Methods:
        __init__: Initialize the instance.
        boundingRect: Boundingrect.
        shape: Shape.
        update_position: Update Position.
        get_line: Get Line.
        set_handles_visible: Set Handles Visible.
        add_control_point: Add Control Point.
        remove_control_point: Remove Control Point.
        clear_control_points: Clear Control Points.
        get_control_point_at: Get Control Point At.
        itemChange: Itemchange.
        paint: Paint.
        clear_handles: Clear Handles.
        cleanup: Cleanup.
        apply_subcanvas_clipping: Apply Subcanvas Clipping.
    """

    def __init__(self, source_node, dest_node, color=None, dashed=False):
        """
        Initialize the instance.

        Args:
            source_node: The source node.
            dest_node: The dest node.
            color: The color.
            dashed: The dashed.
        """
        super().__init__()
        if color is None:
            color = QColor(0, 0, 0)
        self.source_node = source_node
        self.dest_node = dest_node
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(5)

        # List of puntos of control (coordinates LOCAL of the edge)
        self.control_points: list[QPointF] = []
        # List of handles graphics associated a the control points
        self.control_handles: list[ControlPointHandle] = []
        # Indica if the handles están visible (when the edge this selected)
        self._handles_visible = False
        # Flag for avoid actualizaciones recursivas
        self._updating_position = False
        # Handle that itself this arrastrando actualmente
        self._dragging_handle = None

        # Configure pen
        self.edge_color = color
        self.is_dashed = dashed
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        # Cache of last puntos calculated
        self._start_point = QPointF(0, 0)
        self._end_point = QPointF(0, 0)

        # State guardado of control_points for tracking of drag
        self._saved_control_points: list[QPointF] = []
        # Callback for notify cambios of control points (undo tracking)
        self.cp_changed_callback = None

        self.update_position()

        # Conectar a the cambios of position of the nodes
        self._connect_to_nodes()

    def _connect_to_nodes(self):
        """Connect To Nodes."""
        # Conectar a positionChanged of both nodes (if existe)
        if self.source_node and hasattr(self.source_node, "positionChanged"):
            try:
                self.source_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass  # The node no tiene this signal

        if self.dest_node and hasattr(self.dest_node, "positionChanged"):
            try:
                self.dest_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass

        # Conectar a properties_changed for detectar cambios of size (radius)
        if self.source_node and hasattr(self.source_node, "properties_changed"):
            try:
                self.source_node.properties_changed.connect(
                    self._on_node_properties_changed
                )
            except (TypeError, AttributeError):
                pass

        if self.dest_node and hasattr(self.dest_node, "properties_changed"):
            try:
                self.dest_node.properties_changed.connect(
                    self._on_node_properties_changed
                )
            except (TypeError, AttributeError):
                pass

    def _on_node_properties_changed(self, node, properties):
        """
        On Node Properties Changed.

        Args:
            node: The node.
            properties: The properties.
        """
        # If the radius changed, we need update the edge
        if "radius" in properties:
            self._on_node_moved()

    def _on_node_moved(self):
        """On Node Moved."""
        if not self._updating_position:
            # Notify that the geometry this a punto of change
            # CRÍTICO for that Qt sepa that debe recalcular colisiones
            self.prepareGeometryChange()
            self.update_position()
            # Forzar redibujado y update bounding rect
            self.update()

    def boundingRect(self):
        """Boundingrect."""
        # Get todos the puntos relevantes
        points = [self._start_point, self._end_point] + self.control_points

        if not points:
            return QRectF(0, 0, 0, 0)

        # Calculate bounding box of todos the puntos
        min_x = min(p.x() for p in points)
        max_x = max(p.x() for p in points)
        min_y = min(p.y() for p in points)
        max_y = max(p.y() for p in points)

        # Add margin for the punta of flecha y handles
        extra = max(self.pen().width() + 20, ControlPointHandle.HANDLE_SIZE)

        return QRectF(
            min_x - extra,
            min_y - extra,
            max_x - min_x + extra * 2,
            max_y - min_y + extra * 2,
        )

    def shape(self):
        """Shape."""
        path = self.path()
        if path.isEmpty():
            return QPainterPath()

        stroker = QPainterPathStroker()
        stroker.setWidth(max(self.pen().widthF() + 6, 8))  # ~8px of área clickable
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return stroker.createStroke(path)

    def _get_node_border_point(self, node, target_pos, use_local_coords=False):
        """
        Get Node Border Point.

        Args:
            node: The node.
            target_pos: The target pos.
            use_local_coords: The use local coords.
        """
        if not node:
            return QPointF(0, 0)

        # Get the position of the node according to the sistema of coordinates
        if use_local_coords:
            # For subcanvas: usar coordinates local
            node_pos = node.pos()
            target_pos_local = target_pos
        else:
            # For canvas main: usar coordinates of scene
            node_pos = node.scenePos()
            target_pos_local = target_pos

        # Calculate vector from the node al objetivo
        dx = target_pos_local.x() - node_pos.x()
        dy = target_pos_local.y() - node_pos.y()

        # Calculate distancia
        distance = math.sqrt(dx * dx + dy * dy)
        if distance == 0:
            return node_pos

        # Get radius of the node
        if hasattr(node, "model") and hasattr(node.model, "radius"):
            radius = node.model.radius
        else:
            rect = node.boundingRect()
            radius = min(rect.width(), rect.height()) / 2.0

        # Normalizar y escalar al radius
        scale_factor = radius / distance
        border_x = node_pos.x() + dx * scale_factor
        border_y = node_pos.y() + dy * scale_factor

        return QPointF(border_x, border_y)

    def _calculate_path_points(self):
        """Calculate Path Points."""
        if not self.source_node or not self.dest_node:
            return [], QPointF(0, 0), QPointF(0, 0)

        # Determinar if estamos in a subcanvas
        in_subcanvas = (
            hasattr(self.source_node, "subcanvas_parent")
            and self.source_node.subcanvas_parent is not None
            and hasattr(self.dest_node, "subcanvas_parent")
            and self.dest_node.subcanvas_parent is not None
            and self.source_node.subcanvas_parent == self.dest_node.subcanvas_parent
        )

        if in_subcanvas:
            # BOTH nodes in the SAME subcanvas - use LOCAL coordinates
            src_pos = self.source_node.pos()
            dst_pos = self.dest_node.pos()

            # Calculate puntos of connection in the borders usando coordinates local
            start_point = self._get_node_border_point(
                self.source_node, dst_pos, use_local_coords=True
            )
            end_point = self._get_node_border_point(
                self.dest_node, src_pos, use_local_coords=True
            )
        else:
            # Nodes in different contexts - use SCENE coordinates
            src_scene_pos = self.source_node.scenePos()
            dst_scene_pos = self.dest_node.scenePos()

            start_point = self._get_node_border_point(
                self.source_node, dst_scene_pos, use_local_coords=False
            )
            end_point = self._get_node_border_point(
                self.dest_node, src_scene_pos, use_local_coords=False
            )

            # Transform start_point y end_point of scene a local of the edge
            if self.scene():
                start_point = self.mapFromScene(start_point)
                end_point = self.mapFromScene(end_point)

        self._start_point = start_point
        self._end_point = end_point

        # Construir list completa of puntos
        # control_points already this in coordinates local
        if self.control_points:
            # There is control points: start -> controls -> end
            all_points = [start_point] + self.control_points + [end_point]
        else:
            # Without control points: only start y end
            all_points = [start_point, end_point]

        return all_points, start_point, end_point

    def update_position(self):
        """Update Position."""
        # Evitar actualizaciones recursivas
        if self._updating_position:
            return

        self._updating_position = True

        try:
            path_points, start_point, end_point = self._calculate_path_points()

            if path_points:
                # _calculate_path_points already retorna puntos in coordinates LOCAL
                # Create the path in coordinates local directamente
                path = QPainterPath(path_points[0])
                for point in path_points[1:]:
                    path.lineTo(point)

                self.setPath(path)

                # Update position of the handles (only if no itself this arrastrando)
                if self._dragging_handle is None:
                    self._update_handles_position()
        finally:
            self._updating_position = False

    def _update_handles_position(self):
        """Update Handles Position."""
        is_selected = self.isSelected()

        # Asegurar that there is tantos handles as control points
        while len(self.control_handles) < len(self.control_points):
            # The control_points están in coordinates LOCAL of the edge
            local_pos = self.control_points[len(self.control_handles)]

            handle = ControlPointHandle(
                self,
                local_pos,  # Pasar position in coordinates local of the edge
                self._on_handle_position_changed,
                self._on_handle_released,
                self._on_handle_drag_start,
            )
            # The handle es child of the edge, thus that usa coordinates local
            handle.setParentItem(self)
            # IMPORTANTE: The handles only are visible when the edge this selected
            handle.setVisible(is_selected)

            self.control_handles.append(handle)

        while len(self.control_handles) > len(self.control_points):
            handle = self.control_handles.pop()
            if handle.scene():
                handle.scene().removeItem(handle)
            handle.setParentItem(None)  # Desvincular del edge

        # Update position of each handle
        # The handles now are children of the edge, thus that use coordinates local
        for i, handle in enumerate(self.control_handles):
            if handle is not self._dragging_handle:
                handle.setPos(self.control_points[i])
            handle.update_appearance(is_selected)
            handle.setVisible(is_selected)

    def _on_handle_released(self):
        """On Handle Released."""
        self._dragging_handle = None
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def _on_handle_drag_start(self):
        """On Handle Drag Start."""
        self._saved_control_points = [QPointF(p) for p in self.control_points]

    def _on_handle_position_changed(self, handle, new_pos):
        """
        On Handle Position Changed.

        Args:
            handle: The handle.
            new_pos: The new pos.
        """
        # Mark this handle as the that itself this arrastrando
        self._dragging_handle = handle

        # Find the index of the handle that was moved
        for i, h in enumerate(self.control_handles):
            if h is handle:
                # This es the handle that itself moved
                # new_pos this in coordinates LOCAL of the edge
                self.control_points[i] = new_pos
                # Recalcular only the path (without update handles for avoid temblor)
                self._update_path_only()
                # Forzar redibujado suave
                self.update()
                break

    def _update_path_only(self):
        """Update Path Only."""
        path_points, start_point, end_point = self._calculate_path_points()

        if not path_points:
            return

        # _calculate_path_points already retorna puntos in coordinates LOCAL
        # Create the path in coordinates local directamente
        path = QPainterPath(path_points[0])
        for point in path_points[1:]:
            path.lineTo(point)

        self.setPath(path)

    def get_line(self):
        """Get Line."""
        return QLineF(
            self._start_point.x(),
            self._start_point.y(),
            self._end_point.x(),
            self._end_point.y(),
        )

    def set_handles_visible(self, visible: bool):
        """
        Set Handles Visible.

        Args:
            visible (bool): The visible.
        """
        self._handles_visible = visible
        for handle in self.control_handles:
            handle.setVisible(visible)

    def _save_cp_state(self):
        """Save Cp State."""
        self._saved_control_points = [QPointF(p) for p in self.control_points]

    def add_control_point(self, scene_pos: QPointF):
        """
        Add Control Point.

        Args:
            scene_pos (QPointF): The scene pos.
        """
        # Transform scene_pos a coordinates local of the edge
        local_pos = self.mapFromScene(scene_pos)

        # Insert in the position correcta (more cercano al segmento)
        path_points, start_point, end_point = self._calculate_path_points()

        if len(path_points) < 2:
            return

        # Find the segmento more cercano al punto clickeado
        min_dist = float("inf")
        insert_index = 0

        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]

            # Calculate distancia punto-segmento (usando coordinates local)
            dist = self._point_to_segment_distance(local_pos, p1, p2)

            if dist < min_dist:
                min_dist = dist
                insert_index = i + 1

        self._save_cp_state()
        self.prepareGeometryChange()

        # Insert the new control point in coordinates local
        self.control_points.insert(insert_index, local_pos)

        # Update handles
        self._update_handles_position()

        # Recalcular path
        self.update_position()
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def _point_to_segment_distance(
        self, point: QPointF, line_start: QPointF, line_end: QPointF
    ) -> float:
        """
        Point To Segment Distance.

        Args:
            point (QPointF): The point.
            line_start (QPointF): The line start.
            line_end (QPointF): The line end.

        Returns:
            float: Point To Segment Distance.
        """
        dx = line_end.x() - line_start.x()
        dy = line_end.y() - line_start.y()

        if dx == 0 and dy == 0:
            # The segmento es a punto
            return math.hypot(point.x() - line_start.x(), point.y() - line_start.y())

        # Projection of the punto over the line
        t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / (
            dx * dx + dy * dy
        )
        t = max(0, min(1, t))

        # Punto more cercano in the segmento
        closest_x = line_start.x() + t * dx
        closest_y = line_start.y() + t * dy

        return math.hypot(point.x() - closest_x, point.y() - closest_y)

    def remove_control_point(self, index: int = -1):
        """
        Remove Control Point.

        Args:
            index (int): The index.
        """
        if not self.control_points:
            return

        if index == -1:
            index = len(self.control_points) - 1

        if 0 <= index < len(self.control_points):
            self._save_cp_state()
            self.prepareGeometryChange()
            self.control_points.pop(index)
            self._update_handles_position()
            self.update_position()
            if self.cp_changed_callback:
                self.cp_changed_callback()

    def clear_control_points(self):
        """Clear Control Points."""
        self._save_cp_state()
        self.prepareGeometryChange()
        self.control_points.clear()
        self._update_handles_position()
        self.update_position()
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def get_control_point_at(self, scene_pos: QPointF, tolerance: float = 10.0) -> int:
        """
        Get Control Point At.

        Args:
            scene_pos (QPointF): The scene pos.
            tolerance (float): The tolerance.

        Returns:
            int: Get Control Point At.
        """
        for i, point in enumerate(self.control_points):
            dx = point.x() - scene_pos.x()
            dy = point.y() - scene_pos.y()
            if math.hypot(dx, dy) <= tolerance:
                return i
        return -1

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """
        Itemchange.

        Args:
            change (QGraphicsItem.GraphicsItemChange): The change.
            value: The value.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Update visibilidad of handles
            is_selected = self.isSelected()
            self.set_handles_visible(is_selected)
            # Update apariencia of handles
            for handle in self.control_handles:
                handle.update_appearance(is_selected)
                handle.setVisible(is_selected)

        # When the edge itself adds a a scene, the handles itself add automatically
        # porque are children of the edge. No we need hacer nada especial.
        elif change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
            # The handles are children of the edge, itself mueven automatically with the
            pass

        return super().itemChange(change, value)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        """
        Paint.

        Args:
            painter (QPainter | None): The painter.
            option (QStyleOptionGraphicsItem | None): The option.
            widget (QWidget | None): The widget.
        """
        del option, widget

        if painter is None or not self.source_node or not self.dest_node:
            return

        # NO llamar a update_position() here for avoid temblor
        # The path already should estar updated by _on_handle_position_changed

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())

        # Dibujar el path
        painter.drawPath(self.path())

        # Dibujar punta de flecha
        self._draw_arrow_head(painter)

    def _draw_arrow_head(self, painter: QPainter):
        """
        Draw Arrow Head.

        Args:
            painter (QPainter): The painter.
        """
        path = self.path()
        if path.isEmpty():
            return

        if not self.control_points:
            # Line recta simple
            line_end = self._end_point
            line_start = self._start_point
        else:
            # With control points: usar the last segmento
            if len(self.control_points) > 0:
                line_end = self._end_point
                line_start = self.control_points[-1]
            else:
                line_end = self._end_point
                line_start = self._start_point

        # Calculate ángulo
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
        """Clear Handles."""
        for handle in self.control_handles:
            handle.setParentItem(None)  # Desvincular del edge
            if handle.scene():
                handle.scene().removeItem(handle)
        self.control_handles.clear()
        self._dragging_handle = None

    def cleanup(self):
        """Cleanup."""
        # Desconectar of the nodes (positionChanged)
        if self.source_node and hasattr(self.source_node, "positionChanged"):
            try:
                self.source_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass  # The signal already estaba desconectada

        if self.dest_node and hasattr(self.dest_node, "positionChanged"):
            try:
                self.dest_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass

        # Desconectar of the nodes (properties_changed)
        if self.source_node and hasattr(self.source_node, "properties_changed"):
            try:
                self.source_node.properties_changed.disconnect(
                    self._on_node_properties_changed
                )
            except (TypeError, RuntimeError):
                pass

        if self.dest_node and hasattr(self.dest_node, "properties_changed"):
            try:
                self.dest_node.properties_changed.disconnect(
                    self._on_node_properties_changed
                )
            except (TypeError, RuntimeError):
                pass

        # Delete handles
        self.clear_handles()

    def _get_path_segments(self):
        """Get Path Segments."""
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

        # Calculate longitud total of the path
        total_length = sum(seg[2] for seg in segments)

        if total_length == 0:
            return QPointF(0, 0), 0.0

        # If the distancia es mayor that the longitud total, retornar the last punto
        if distance >= total_length:
            last_seg = segments[-1]
            angle = math.atan2(
                last_seg[1].y() - last_seg[0].y(), last_seg[1].x() - last_seg[0].x()
            )
            return last_seg[1], angle

        # Find the segmento that contiene the punto deseado
        accumulated = 0.0
        for p1, p2, seg_length in segments:
            if accumulated + seg_length >= distance:
                # The punto this in this segmento
                t = (distance - accumulated) / seg_length if seg_length > 0 else 0
                x = p1.x() + t * (p2.x() - p1.x())
                y = p1.y() + t * (p2.y() - p1.y())
                angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
                return QPointF(x, y), angle
            accumulated += seg_length

        # No should llegar here
        last_seg = segments[-1]
        angle = math.atan2(
            last_seg[1].y() - last_seg[0].y(), last_seg[1].x() - last_seg[0].x()
        )
        return last_seg[1], angle

    def _get_tangent_at_distance(self, distance: float) -> float:
        """
        Retorna el ángulo/tangente del path en un punto a cierta distancia.

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

        # Calculate longitud total of the path
        total_length = sum(seg[2] for seg in segments)

        if total_length == 0:
            return QPointF(0, 0), 0.0

        target_distance = total_length * percentage
        return self._get_point_at_distance(target_distance)

    def apply_subcanvas_clipping(self, painter):
        """
        Apply Subcanvas Clipping.

        Args:
            painter: The painter.
        """
        if not self.source_node or not self.dest_node:
            return False

        subcanvas = None
        if (
            hasattr(self.source_node, "subcanvas_parent")
            and self.source_node.subcanvas_parent is not None
            and hasattr(self.dest_node, "subcanvas_parent")
            and self.dest_node.subcanvas_parent is not None
            and self.source_node.subcanvas_parent == self.dest_node.subcanvas_parent
        ):
            subcanvas = self.source_node.subcanvas_parent

        if not subcanvas:
            return False

        from app.ui.components.subcanvas_item import SubCanvasItem

        if not isinstance(subcanvas, SubCanvasItem):
            return False

        painter.save()

        clip = QPainterPath()
        r = subcanvas.radius
        clip.addEllipse(QRectF(-r, -r, 2 * r, 2 * r))

        clip_local = self.mapFromItem(subcanvas, clip)
        painter.setClipPath(clip_local)
        return True
