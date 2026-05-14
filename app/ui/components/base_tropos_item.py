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


class BaseTroposItem(QGraphicsObject):
    """
    Base Tropos Item.

    Methods:
        __init__: Initialize the instance.
        boundingRect: Boundingrect.
        hoverMoveEvent: Hovermoveevent.
        hoverLeaveEvent: Hoverleaveevent.
        mousePressEvent: Mousepressevent.
        mouseMoveEvent: Mousemoveevent.
        mouseReleaseEvent: Mousereleaseevent.
        itemChange: Itemchange.
        set_radius: Set Radius.
        mouseDoubleClickEvent: Mousedoubleclickevent.
        draw_multiline_text: Draw Multiline Text.
        get_serializable_properties: Get Serializable Properties.
        update_properties: Update Properties.
        apply_subcanvas_clipping: Apply Subcanvas Clipping.
    """

    nodeDoubleClicked = pyqtSignal(object)
    properties_changed = pyqtSignal(object, dict)
    positionChanged = pyqtSignal()  # Signal for notify when the node itself moves
    drag_finished = pyqtSignal(object, QPointF)  # Node, position initial
    resize_finished = pyqtSignal(object, float)  # Node, radius initial

    def __init__(self, model: NodeModelLike) -> None:
        """
        Initialize the instance.

        Args:
            model (NodeModelLike): The model.
        """
        super().__init__()
        self.model: NodeModelLike = model
        # For nodes composite internos:
        # model independiente for radius, position, etc.
        self._independent_model: NodeModelLike | None = None
        self.subcanvas_parent: SubCanvasItem | None = None
        self.child_nodes: list[object] = []
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsObject.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
        self._resizing = False
        if not hasattr(self.model, "font_size"):
            self.model.font_size = 10

    def _get_model_for_independent_prop(
        self,
        prop_name: str,
        default: object = None,
    ) -> object:
        """
        Get Model For Independent Prop.

        Args:
            prop_name (str): The prop name.
            default (object): The default.

        Returns:
            object: Get Model For Independent Prop.
        """
        if self._independent_model and hasattr(self._independent_model, prop_name):
            return getattr(self._independent_model, prop_name)
        return getattr(self.model, prop_name, default)

    def boundingRect(self) -> QRectF:
        """
        Boundingrect.

        Returns:
            QRectF: Boundingrect.
        """
        r = (
            float(self._independent_model.radius)
            if self._independent_model
            else float(self.model.radius)
        )
        return QRectF(-r, -r, 2 * r, 2 * r)

    def _get_distance_to_border(self, pos: QPointF) -> float:
        """
        Get Distance To Border.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get Distance To Border.
        """
        r = (
            float(self._independent_model.radius)
            if self._independent_model
            else float(self.model.radius)
        )
        center_dist = (pos.x() ** 2 + pos.y() ** 2) ** 0.5
        return float(abs(center_dist - r))

    def _get_new_radius_from_pos(self, pos: QPointF) -> float:
        """
        Get New Radius From Pos.

        Args:
            pos (QPointF): The pos.

        Returns:
            float: Get New Radius From Pos.
        """
        center_dist = (pos.x() ** 2 + pos.y() ** 2) ** 0.5
        return float(max(center_dist, 10.0))

    def hoverMoveEvent(self, event):
        """
        Hovermoveevent.

        Args:
            event: The event.
        """
        dist = self._get_distance_to_border(event.pos())
        if dist < 8:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        """
        Hoverleaveevent.

        Args:
            event: The event.
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """
        Mousepressevent.

        Args:
            event: The event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._get_distance_to_border(event.pos())
            if dist < 8:
                self._resizing = True
                self._resize_start_radius = float(
                    self._get_model_for_independent_prop("radius", 50)
                )
                self.setSelected(True)
                event.accept()
                return
            self._drag_start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Mousemoveevent.

        Args:
            event: The event.
        """
        if self._resizing:
            new_r = self._get_new_radius_from_pos(event.pos())
            self.set_radius(new_r)
            event.accept()
            return
        super().mouseMoveEvent(event)
        # Emitir signal of movimiento for update edges conectados
        self.positionChanged.emit()

    def mouseReleaseEvent(self, event):
        """
        Mousereleaseevent.

        Args:
            event: The event.
        """
        if self._resizing and event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            old_r = getattr(
                self,
                "_resize_start_radius",
                float(self._get_model_for_independent_prop("radius", 50)),
            )
            current_r = float(self._get_model_for_independent_prop("radius", 50))
            if old_r != current_r:
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
        """
        Itemchange.

        Args:
            change (QGraphicsItem.GraphicsItemChange): The change.
            value: The value.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.positionChanged.emit()
        return super().itemChange(change, value)

    def set_radius(self, new_r: float):
        """
        Set Radius.

        Args:
            new_r (float): The new r.
        """
        self.prepareGeometryChange()
        old_r = self._get_model_for_independent_prop("radius", new_r)

        # Usar the model independiente if existe, sino the model normal
        if self._independent_model:
            self._independent_model.radius = new_r
        else:
            self.model.radius = new_r

        self.update()

        if old_r != new_r:
            self.properties_changed.emit(self, {"radius": new_r})

    def mouseDoubleClickEvent(self, event):
        """
        Mousedoubleclickevent.

        Args:
            event: The event.
        """
        event.ignore()
        super().mouseDoubleClickEvent(event)

    def draw_multiline_text(self, painter, text_color_hex):
        # Label y color itself sincronizan, thus that usar self.model (wrapper)
        """
        Draw Multiline Text.

        Args:
            painter: The painter.
            text_color_hex: The text color hex.
        """
        label = getattr(self.model, "label", "")
        if not label:
            return

        # text_width, font_size, align pueden ser independientes
        text_width = self._get_model_for_independent_prop("text_width", 150)
        font_size = self._get_model_for_independent_prop("font_size", 10)
        align_str = self._get_model_for_independent_prop("text_align", "center")

        align_flag = Qt.AlignmentFlag.AlignCenter
        if align_str == "left":
            align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif align_str == "right":
            align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        painter.setPen(QColor(text_color_hex))
        font = QFont("Arial", int(font_size))
        font.setBold(True)
        painter.setFont(font)

        rect_height = 500
        text_rect = QRectF(-text_width / 2, -rect_height / 2, text_width, rect_height)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | align_flag, label)

    def get_serializable_properties(self):
        # Radius es independiente
        """Get Serializable Properties."""
        radius = self._get_model_for_independent_prop("radius", 50)
        # Label y color are sincronizados (wrapper)
        label = getattr(self.model, "label", "")
        color = getattr(self.model, "color", "#3498db")
        border_color = getattr(self.model, "border_color", "#2980b9")
        text_color = getattr(self.model, "text_color", "#ffffff")
        # Font properties pueden ser independientes
        font_size = self._get_model_for_independent_prop("font_size", 10)
        text_width = self._get_model_for_independent_prop("text_width", 150)
        text_align = self._get_model_for_independent_prop("text_align", "center")

        return {
            "radius": radius,
            "label": label,
            "font_size": font_size,
            "text_width": text_width,
            "text_align": text_align,
            "color": color,
            "border_color": border_color,
            "text_color": text_color,
            "x": self.pos().x(),
            "y": self.pos().y(),
        }

    def update_properties(self, properties: dict):
        """
        Update Properties.

        Args:
            properties (dict): The properties.
        """
        for key, value in properties.items():
            if key == "radius":
                self.set_radius(float(value))
            elif key in ("label", "color", "border_color", "text_color"):
                # Properties sincronizadas - usar the model wrapper
                if hasattr(self.model, key):
                    setattr(self.model, key, value)
            elif self._independent_model and hasattr(self._independent_model, key):
                # Properties independientes - usar the model independiente
                setattr(self._independent_model, key, value)
            elif hasattr(self.model, key):
                setattr(self.model, key, value)

        if "x" in properties and "y" in properties:
            if self._independent_model:
                self._independent_model.x = properties["x"]
                self._independent_model.y = properties["y"]
            else:
                self.model.x = properties["x"]
                self.model.y = properties["y"]
            self.setPos(properties["x"], properties["y"])

        if "radius" not in properties:
            self.update()

        self.properties_changed.emit(self, properties)

    def apply_subcanvas_clipping(self, painter):
        """
        Apply Subcanvas Clipping.

        Args:
            painter: The painter.
        """
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
