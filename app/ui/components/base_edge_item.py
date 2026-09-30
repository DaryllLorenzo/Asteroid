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
from app.ui.theme_manager import theme_manager
from app.utils import edge_geometry


class BaseEdgeItem(QGraphicsPathItem):
    """A poly-line arrow between two nodes, with draggable control points."""

    def __init__(self, source_node, dest_node, color=None, dashed=False):
        super().__init__()
        if color is None:
            color = QColor(0, 0, 0)
        self.source_node = source_node
        self.dest_node = dest_node
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(5)

        self.control_points: list[QPointF] = []
        self.control_handles: list[ControlPointHandle] = []
        self._handles_visible = False
        self._updating_position = False
        self._dragging_handle = None

        self.edge_color = color
        self.is_dashed = dashed
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        self._start_point = QPointF(0, 0)
        self._end_point = QPointF(0, 0)

        self._saved_control_points: list[QPointF] = []
        self.cp_changed_callback = None

        self.update_position()
        self.update_theme()
        self._connect_to_nodes()

    def _connect_to_nodes(self):
        if self.source_node and hasattr(self.source_node, "positionChanged"):
            try:
                self.source_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass  # node doesn't expose this signal

        if self.dest_node and hasattr(self.dest_node, "positionChanged"):
            try:
                self.dest_node.positionChanged.connect(self._on_node_moved)
            except (TypeError, AttributeError):
                pass

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
        if "radius" in properties:
            self._on_node_moved()

    def _on_node_moved(self):
        if not self._updating_position:
            # Qt needs prepareGeometryChange() before boundingRect() changes,
            # or it won't recompute collisions/repaint correctly.
            self.prepareGeometryChange()
            self.update_position()
            self.update()

    def boundingRect(self):
        points = [self._start_point, self._end_point] + self.control_points

        if not points:
            return QRectF(0, 0, 0, 0)

        min_x = min(p.x() for p in points)
        max_x = max(p.x() for p in points)
        min_y = min(p.y() for p in points)
        max_y = max(p.y() for p in points)

        # Margin for the arrow head and control-point handles.
        extra = max(self.pen().width() + 20, ControlPointHandle.HANDLE_SIZE)

        return QRectF(
            min_x - extra,
            min_y - extra,
            max_x - min_x + extra * 2,
            max_y - min_y + extra * 2,
        )

    def shape(self):
        path = self.path()
        if path.isEmpty():
            return QPainterPath()

        stroker = QPainterPathStroker()
        stroker.setWidth(max(self.pen().widthF() + 6, 8))  # ~8px clickable area
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return stroker.createStroke(path)

    def _get_node_border_point(self, node, target_pos, use_local_coords=False):
        if not node:
            return QPointF(0, 0)

        if use_local_coords:
            node_pos = node.pos()
        else:
            node_pos = node.scenePos()

        if hasattr(node, "model") and hasattr(node.model, "radius"):
            radius = node.model.radius
        else:
            rect = node.boundingRect()
            radius = min(rect.width(), rect.height()) / 2.0

        return edge_geometry.border_point(node_pos, radius, target_pos)

    def _calculate_path_points(self):
        if not self.source_node or not self.dest_node:
            return [], QPointF(0, 0), QPointF(0, 0)

        in_subcanvas = (
            hasattr(self.source_node, "subcanvas_parent")
            and self.source_node.subcanvas_parent is not None
            and hasattr(self.dest_node, "subcanvas_parent")
            and self.dest_node.subcanvas_parent is not None
            and self.source_node.subcanvas_parent == self.dest_node.subcanvas_parent
        )

        if in_subcanvas:
            # Both nodes share a subcanvas: work in its local coordinates.
            src_pos = self.source_node.pos()
            dst_pos = self.dest_node.pos()

            start_point = self._get_node_border_point(
                self.source_node, dst_pos, use_local_coords=True
            )
            end_point = self._get_node_border_point(
                self.dest_node, src_pos, use_local_coords=True
            )
        else:
            # Different contexts: work in scene coordinates, then map to local.
            src_scene_pos = self.source_node.scenePos()
            dst_scene_pos = self.dest_node.scenePos()

            start_point = self._get_node_border_point(
                self.source_node, dst_scene_pos, use_local_coords=False
            )
            end_point = self._get_node_border_point(
                self.dest_node, src_scene_pos, use_local_coords=False
            )

            if self.scene():
                start_point = self.mapFromScene(start_point)
                end_point = self.mapFromScene(end_point)

        self._start_point = start_point
        self._end_point = end_point

        if self.control_points:
            all_points = [start_point] + self.control_points + [end_point]
        else:
            all_points = [start_point, end_point]

        return all_points, start_point, end_point

    def update_position(self):
        if self._updating_position:
            return

        self._updating_position = True

        try:
            path_points, start_point, end_point = self._calculate_path_points()

            if path_points:
                path = QPainterPath(path_points[0])
                for point in path_points[1:]:
                    path.lineTo(point)

                self.setPath(path)

                if self._dragging_handle is None:
                    self._update_handles_position()
        finally:
            self._updating_position = False

    def _update_handles_position(self):
        is_selected = self.isSelected()

        while len(self.control_handles) < len(self.control_points):
            local_pos = self.control_points[len(self.control_handles)]

            handle = ControlPointHandle(
                self,
                local_pos,
                self._on_handle_position_changed,
                self._on_handle_released,
                self._on_handle_drag_start,
            )
            handle.setParentItem(self)
            handle.setVisible(is_selected)

            self.control_handles.append(handle)

        while len(self.control_handles) > len(self.control_points):
            handle = self.control_handles.pop()
            if handle.scene():
                handle.scene().removeItem(handle)
            handle.setParentItem(None)

        for i, handle in enumerate(self.control_handles):
            if handle is not self._dragging_handle:
                handle.setPos(self.control_points[i])
            handle.update_appearance(is_selected)
            handle.setVisible(is_selected)

    def _on_handle_released(self):
        self._dragging_handle = None
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def _on_handle_drag_start(self):
        self._saved_control_points = [QPointF(p) for p in self.control_points]

    def _on_handle_position_changed(self, handle, new_pos):
        self._dragging_handle = handle

        for i, h in enumerate(self.control_handles):
            if h is handle:
                self.control_points[i] = new_pos
                # Only recompute the path here (not handle positions too),
                # or the dragged handle jitters against its own move.
                self._update_path_only()
                self.update()
                break

    def _update_path_only(self):
        path_points, _start_point, _end_point = self._calculate_path_points()

        if not path_points:
            return

        path = QPainterPath(path_points[0])
        for point in path_points[1:]:
            path.lineTo(point)

        self.setPath(path)

    def get_line(self):
        return QLineF(
            self._start_point.x(),
            self._start_point.y(),
            self._end_point.x(),
            self._end_point.y(),
        )

    def set_handles_visible(self, visible: bool):
        self._handles_visible = visible
        for handle in self.control_handles:
            handle.setVisible(visible)

    def _save_cp_state(self):
        self._saved_control_points = [QPointF(p) for p in self.control_points]

    def add_control_point(self, scene_pos: QPointF):
        local_pos = self.mapFromScene(scene_pos)

        path_points, _start_point, _end_point = self._calculate_path_points()

        if len(path_points) < 2:
            return

        min_dist = float("inf")
        insert_index = 0

        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]

            dist = self._point_to_segment_distance(local_pos, p1, p2)

            if dist < min_dist:
                min_dist = dist
                insert_index = i + 1

        self._save_cp_state()
        self.prepareGeometryChange()

        self.control_points.insert(insert_index, local_pos)

        self._update_handles_position()
        self.update_position()
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def _point_to_segment_distance(
        self, point: QPointF, line_start: QPointF, line_end: QPointF
    ) -> float:
        return edge_geometry.point_to_segment_distance(point, line_start, line_end)

    def remove_control_point(self, index: int = -1):
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
        self._save_cp_state()
        self.prepareGeometryChange()
        self.control_points.clear()
        self._update_handles_position()
        self.update_position()
        if self.cp_changed_callback:
            self.cp_changed_callback()

    def get_control_point_at(self, scene_pos: QPointF, tolerance: float = 10.0) -> int:
        for i, point in enumerate(self.control_points):
            dx = point.x() - scene_pos.x()
            dy = point.y() - scene_pos.y()
            if math.hypot(dx, dy) <= tolerance:
                return i
        return -1

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = self.isSelected()
            self.set_handles_visible(is_selected)
            for handle in self.control_handles:
                handle.update_appearance(is_selected)
                handle.setVisible(is_selected)

        return super().itemChange(change, value)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        del option, widget

        if painter is None or not self.source_node or not self.dest_node:
            return

        # Don't call update_position() here - _on_handle_position_changed
        # already keeps the path current, and doing it here causes jitter.

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.pen())
        painter.drawPath(self.path())
        self._draw_arrow_head(painter)

    def _draw_arrow_head(self, painter: QPainter):
        path = self.path()
        if path.isEmpty():
            return

        if self.control_points:
            line_end = self._end_point
            line_start = self.control_points[-1]
        else:
            line_end = self._end_point
            line_start = self._start_point

        arrow_points = edge_geometry.arrow_head_points(line_start, line_end, 10)
        if arrow_points is None:
            return

        painter.setBrush(self.pen().color())
        painter.drawPolygon(QPolygonF(list(arrow_points)))

    def update_theme(self):
        """Update pen color based on current theme."""
        if theme_manager().is_dark:
            color = QColor("#ffffff")
        else:
            color = self.edge_color
        pen = QPen(color, 2)
        if self.is_dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        self.update()

    def clear_handles(self):
        for handle in self.control_handles:
            handle.setParentItem(None)
            if handle.scene():
                handle.scene().removeItem(handle)
        self.control_handles.clear()
        self._dragging_handle = None

    def cleanup(self):
        if self.source_node and hasattr(self.source_node, "positionChanged"):
            try:
                self.source_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass  # already disconnected

        if self.dest_node and hasattr(self.dest_node, "positionChanged"):
            try:
                self.dest_node.positionChanged.disconnect(self._on_node_moved)
            except (TypeError, RuntimeError):
                pass

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

        self.clear_handles()

    def _get_path_segments(self):
        path_points, _start_point, _end_point = self._calculate_path_points()
        return edge_geometry.path_segments(path_points)

    def _get_point_at_distance(self, distance: float) -> tuple[QPointF, float]:
        """Point and tangent angle (radians) at `distance` along the path."""
        return edge_geometry.point_at_distance(self._get_path_segments(), distance)

    def _get_tangent_at_distance(self, distance: float) -> float:
        _, angle = self._get_point_at_distance(distance)
        return angle

    def _get_point_at_percentage(self, percentage: float) -> tuple[QPointF, float]:
        """Point and tangent angle (radians) at `percentage` (0..1) along the path."""
        return edge_geometry.point_at_percentage(self._get_path_segments(), percentage)

    def apply_subcanvas_clipping(self, painter):
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
