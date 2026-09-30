# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtWidgets import QGraphicsObject

from app.model_types import NodeModelLike
from app.ui.components.subcanvas_item import SubCanvasItem


class BaseNodeItem(QGraphicsObject):
    """A resizable, draggable canvas node with an optional subcanvas."""

    nodeDoubleClicked = pyqtSignal(object)
    subcanvas_toggled = pyqtSignal(object, object)
    properties_changed = pyqtSignal(object, dict)
    positionChanged = pyqtSignal()
    drag_finished = pyqtSignal(object, QPointF)  # node, initial position
    resize_finished = pyqtSignal(object, float)  # node, initial radius
    subcanvas_toggle_requested = pyqtSignal(object)

    def __init__(self, model: NodeModelLike) -> None:
        super().__init__()
        self.model: NodeModelLike = model
        self._independent_model: NodeModelLike | None = None
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self._resizing: bool = False
        self.subcanvas: SubCanvasItem | None = None
        self.subcanvas_parent: SubCanvasItem | None = None
        self.child_nodes: list[object] = []
        self._subcanvas_visible: bool = False
        self.setZValue(10)

        if not hasattr(self.model, "font_size"):
            self.model.font_size = 10
        if not hasattr(self.model, "text_width"):
            self.model.text_width = 150
        if not hasattr(self.model, "text_align"):
            self.model.text_align = "center"

    def boundingRect(self) -> QRectF:
        r = float(self.model.radius)
        return QRectF(-r, -r, 2 * r, 2 * r)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        r = float(self.model.radius)
        center_dist = (pos.x() ** 2 + pos.y() ** 2) ** 0.5
        return float(abs(center_dist - r))

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        center_dist = (pos.x() ** 2 + pos.y() ** 2) ** 0.5
        return float(max(center_dist, 10.0))

    def hoverMoveEvent(self, event):
        dist = self._get_distance_to_border(event.pos())
        if dist < 8:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._get_distance_to_border(event.pos())
            if dist < 8:
                self._resizing = True
                self._resize_start_radius = float(self.model.radius)
                self.setSelected(True)
                event.accept()
                return
            self._drag_start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            new_r = self._get_new_radius_from_pos(event.pos())
            self.set_radius(new_r)
            event.accept()
            return
        super().mouseMoveEvent(event)
        self.positionChanged.emit()

    def mouseReleaseEvent(self, event):
        if self._resizing and event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            old_r = getattr(self, "_resize_start_radius", float(self.model.radius))
            if old_r != float(self.model.radius):
                self.resize_finished.emit(self, old_r)
            self._resize_start_radius = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
        if hasattr(self, "_drag_start_pos") and self._drag_start_pos is not None:
            if self._drag_start_pos != self.pos():
                self.drag_finished.emit(self, self._drag_start_pos)
            self._drag_start_pos = None

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.positionChanged.emit()
        return super().itemChange(change, value)

    def set_radius(self, new_r: float):
        self.prepareGeometryChange()
        old_r = getattr(self.model, "radius", new_r)
        self.model.radius = new_r
        self.update()

        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def mouseDoubleClickEvent(self, event):
        self.subcanvas_toggle_requested.emit(self)
        event.accept()

    def _create_subcanvas(self, radius: float, *, visible: bool) -> SubCanvasItem:
        """Create, parent, and position a new SubCanvasItem for this node."""
        subcanvas = SubCanvasItem(radius=radius)
        subcanvas.setParentItem(self)
        subcanvas.setPos(0.0, 0.0)
        subcanvas.setVisible(visible)
        subcanvas.setZValue(self.zValue() - 1)
        self._subcanvas_original_pos = QPointF(0, 0)
        return subcanvas

    def _toggle_subcanvas(self):
        if hasattr(self.model, "toggle_subcanvas"):
            self.model.toggle_subcanvas()
        else:
            self.model.show_subcanvas = not getattr(self.model, "show_subcanvas", False)

        show = getattr(self.model, "show_subcanvas", False)

        if show:
            if not self.subcanvas:
                self.subcanvas = self._create_subcanvas(
                    max(120.0, self.model.radius * 2.0), visible=True
                )
            else:
                self.subcanvas.setVisible(True)
                self.subcanvas.setZValue(self.zValue() - 1)

            self.subcanvas_toggled.emit(self, self.subcanvas)
            self._subcanvas_visible = True

            if hasattr(self.model, "position_in_subcanvas_x") and hasattr(
                self.model, "position_in_subcanvas_y"
            ):
                if (
                    abs(self.model.position_in_subcanvas_x) > 0.001
                    or abs(self.model.position_in_subcanvas_y) > 0.001
                ):
                    self.apply_position_in_subcanvas()

        else:
            if self.subcanvas:
                self.subcanvas.setVisible(False)
            self.subcanvas_toggled.emit(self, None)
            self._subcanvas_visible = False

        self.update()

    def ensure_subcanvas_visible(self):
        if not getattr(self.model, "show_subcanvas", False):
            self.model.show_subcanvas = True

        if not self.subcanvas:
            self.subcanvas = self._create_subcanvas(
                max(120.0, self.model.radius * 2.0), visible=True
            )
        else:
            self.subcanvas.setVisible(True)
            self.subcanvas.setZValue(self.zValue() - 1)

        self.subcanvas_toggled.emit(self, self.subcanvas)
        self._subcanvas_visible = True

        if hasattr(self.model, "position_in_subcanvas_x") and hasattr(
            self.model, "position_in_subcanvas_y"
        ):
            if (
                abs(self.model.position_in_subcanvas_x) > 0.001
                or abs(self.model.position_in_subcanvas_y) > 0.001
            ):
                self.apply_position_in_subcanvas()

        return self.subcanvas

    def prepare_subcanvas_for_internal_use(self):
        if not self.subcanvas:
            self.subcanvas = self._create_subcanvas(
                max(250.0, self.model.radius * 3.0), visible=False
            )
            self.subcanvas._update_handle_pos()
        else:
            if not self.subcanvas.isVisible() and getattr(
                self.model, "show_subcanvas", False
            ):
                self.subcanvas.setVisible(True)
                self.subcanvas.setZValue(self.zValue() - 1)

        return self.subcanvas

    def apply_position_in_subcanvas(self):
        if not hasattr(self.model, "position_in_subcanvas_x") or not hasattr(
            self.model, "position_in_subcanvas_y"
        ):
            return

        if self.is_subcanvas_visible() and self.subcanvas:
            body_radius = float(self.model.radius)
            max_offset = self.subcanvas.radius + body_radius

            offset_x = self.model.position_in_subcanvas_x * max_offset
            offset_y = self.model.position_in_subcanvas_y * max_offset

            if not hasattr(self, "_subcanvas_original_pos"):
                self._subcanvas_original_pos = QPointF(0, 0)

            new_subcanvas_pos = self._subcanvas_original_pos - QPointF(
                offset_x, offset_y
            )
            self.subcanvas.setPos(new_subcanvas_pos)
            self.setZValue(self.subcanvas.zValue() + 1)
            self.update()

    def position_within_subcanvas(self, x_norm, y_norm):
        if not self.is_subcanvas_visible() or not self.subcanvas:
            return

        self.model.position_in_subcanvas_x = x_norm
        self.model.position_in_subcanvas_y = y_norm

        self.apply_position_in_subcanvas()

        self.properties_changed.emit(
            self, {"position_in_subcanvas_x": x_norm, "position_in_subcanvas_y": y_norm}
        )

    def draw_multiline_text(self, painter, text_color_hex):
        label = getattr(self.model, "label", "")
        if not label:
            return

        text_width = getattr(self.model, "text_width", 150)
        font_size = getattr(self.model, "font_size", 10)
        align_str = getattr(self.model, "text_align", "center")

        align_flag = Qt.AlignmentFlag.AlignCenter
        if align_str == "left":
            align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif align_str == "right":
            align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        flags = Qt.TextFlag.TextWordWrap | align_flag
        painter.setPen(QColor(text_color_hex))
        painter.setFont(QFont("Arial", int(font_size)))

        offset_x = getattr(self.model, "content_offset_x", 0)
        offset_y = getattr(self.model, "content_offset_y", 0)
        rect_height = 500
        text_rect = QRectF(
            -text_width / 2 + offset_x,
            -rect_height / 2 + offset_y,
            text_width,
            rect_height,
        )
        painter.drawText(text_rect, flags, label)

    def get_serializable_properties(self):
        return {
            "radius": getattr(self.model, "radius", 50),
            "label": getattr(self.model, "label", ""),
            "color": getattr(self.model, "color", "#3498db"),
            "border_color": getattr(self.model, "border_color", "#2980b9"),
            "text_color": getattr(self.model, "text_color", "#ffffff"),
            "font_size": getattr(self.model, "font_size", 10),
            "text_width": getattr(self.model, "text_width", 150),
            "text_align": getattr(self.model, "text_align", "center"),
            "x": self.pos().x(),
            "y": self.pos().y(),
            "position_in_subcanvas_x": getattr(
                self.model, "position_in_subcanvas_x", 0.0
            ),
            "position_in_subcanvas_y": getattr(
                self.model, "position_in_subcanvas_y", 0.0
            ),
        }

    def update_properties(self, properties: dict):
        for key, value in properties.items():
            # Only overwrite plain data attributes - never a method (e.g. a
            # stray "node_type" key would otherwise clobber node_type()).
            if hasattr(self.model, key) and not callable(getattr(self.model, key)):
                setattr(self.model, key, value)

        if "radius" in properties:
            self.prepareGeometryChange()
            self.model.radius = properties["radius"]

        if "x" in properties and "y" in properties:
            self.model.x = properties["x"]
            self.model.y = properties["y"]
            self.setPos(properties["x"], properties["y"])

        if (
            "position_in_subcanvas_x" in properties
            or "position_in_subcanvas_y" in properties
        ):
            if self.is_subcanvas_visible():
                self.apply_position_in_subcanvas()

        self.update()
        self.properties_changed.emit(self, properties)

    def is_subcanvas_visible(self) -> bool:
        return (
            self.subcanvas is not None
            and self.subcanvas.isVisible()
            and getattr(self.model, "show_subcanvas", False)
        )

    def apply_subcanvas_clipping(self, painter):
        subcanvas = getattr(self, "subcanvas_parent", None)
        if not subcanvas or not isinstance(subcanvas, SubCanvasItem):
            return False

        painter.save()

        clip = QPainterPath()
        r = subcanvas.radius
        clip.addEllipse(QRectF(-r, -r, 2 * r, 2 * r))

        clip_local = self.mapFromItem(subcanvas, clip)
        painter.setClipPath(clip_local)
        return True
