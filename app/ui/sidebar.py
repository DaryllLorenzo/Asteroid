# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from PyQt6.QtCore import QMimeData
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.i18n import tr
from app.ui.theme_manager import theme_manager
from app.ui.components.dependency_item.and_decomposition_edge_item import (
    AndDecompositionArrowItem,
)
from app.ui.components.dependency_item.contribution_edge_item import (
    ContributionArrowItem,
)

# Arrow/link items (deben aceptar (source_node, dest_node) in its constructor)
from app.ui.components.dependency_item.dependency_link_edge_item import (
    DependencyLinkArrowItem,
)
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import (
    OrDecompositionArrowItem,
)
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem

# Node items
from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem


class DraggableLabel(QLabel):
    """
    Draggable Label.

    Methods:
        __init__: Initialize the instance.
        create_pixmap: Create Pixmap.
        mousePressEvent: Mousepressevent.
        start_drag: Start Drag.
    """

    def __init__(
        self,
        text: str,
        item_type: str,
        on_click=None,
        tooltip_text: str | None = None,
    ) -> None:
        """
        Initialize the instance.

        Args:
            text (str): The text.
            item_type (str): The item type.
            on_click: The on click.
            tooltip_text (str | None): The tooltip text.
        """
        self._text_key = text
        self._tooltip_key = tooltip_text
        super().__init__()
        self.item_type = item_type
        self.on_click = on_click
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        if tooltip_text:
            self.setToolTip(tr(tooltip_text))
        self._update_style()

    def _update_style(self):
        """Update stylesheet based on current theme."""
        if theme_manager().is_dark:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #666666;
                    border-radius: 10px;
                    padding: 8px;
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    min-width: 90px;
                    min-height: 90px;
                }
                QLabel:hover {
                    background-color: #3d3d3d;
                    border: 2px solid #aaaaaa;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #cccccc;
                    border-radius: 10px;
                    padding: 8px;
                    background-color: #fafafa;
                    color: #000000;
                    min-width: 90px;
                    min-height: 90px;
                }
                QLabel:hover {
                    background-color: #f0f0f0;
                    border: 2px solid #888888;
                }
            """)
        self.setPixmap(self.create_pixmap())

    def retranslate(self):
        """Retranslate the label text and tooltip."""
        self.setPixmap(self.create_pixmap())
        if self._tooltip_key:
            self.setToolTip(tr(self._tooltip_key))

    def create_pixmap(self) -> QPixmap:
        """
        Create Pixmap.

        Returns:
            QPixmap: Create Pixmap.
        """
        W, H = 80, 80
        pixmap = QPixmap(W, H)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        node_map = {
            "actor": ActorNodeItem,
            "agent": AgentNodeItem,
            "hard_goal": HardGoalNodeItem,
            "soft_goal": SoftGoalNodeItem,
            "plan": PlanNodeItem,
            "resource": ResourceNodeItem,
        }

        arrow_map = {
            "dependency_link": DependencyLinkArrowItem,
            "why_link": WhyLinkArrowItem,
            "or_decomposition": OrDecompositionArrowItem,
            "and_decomposition": AndDecompositionArrowItem,
            "contribution": ContributionArrowItem,
            "means_end": MeansEndArrowItem,
        }

        self._render_preview(painter, W, H, node_map, arrow_map)

        painter.end()
        return pixmap

    def _render_preview(self, painter, W, H, node_map, arrow_map):
        """
        Render Preview.

        Args:
            painter: The painter.
            W: The W.
            H: The H.
            node_map: The node map.
            arrow_map: The arrow map.
        """
        if self.item_type.startswith("composite:"):
            self._render_composite_preview(painter, W, H, node_map)
        elif self.item_type in node_map:
            self._render_node_preview(painter, W, H, node_map)
        elif self.item_type in arrow_map:
            self._render_arrow_preview(painter, W, H, arrow_map)

    def _render_composite_preview(self, painter, W, H, node_map):
        """
        Render Composite Preview.

        Args:
            painter: The painter.
            W: The W.
            H: The H.
            node_map: The node map.
        """
        scene = QGraphicsScene()
        node_key = self.item_type.split(":")[1]
        NodeClass = node_map.get(node_key)
        node_center_x, node_center_y = W / 2, H / 2

        node = None
        if NodeClass:
            try:
                node = NodeClass(0, 0, radius=18)
            except TypeError:
                node = NodeClass(0, 0)
            node.setPos(node_center_x, node_center_y)
            scene.addItem(node)

        rect = scene.itemsBoundingRect()
        if rect.isNull() or rect.width() == 0 or rect.height() == 0:
            rect = QRectF(0, 0, W, H)
        scene.render(painter, QRectF(0, 0, W, H), rect)

        if node:
            node_bounds = node.boundingRect()
            node_left = node_center_x + node_bounds.left()
            node_right = node_center_x + node_bounds.right()

            margin = 4
            y = int(H / 2)

            from PyQt6.QtGui import QColor
            edge_color = QColor("#ffffff") if theme_manager().is_dark else QColor("#000000")
            pen = painter.pen()
            pen.setWidth(2)
            pen.setColor(edge_color)
            painter.setPen(pen)

            painter.drawLine(8, y, int(node_left - margin), y)
            painter.drawLine(int(node_right + margin), y, W - 8, y)

    def _render_node_preview(self, painter, W, H, node_map):
        """
        Render Node Preview.

        Args:
            painter: The painter.
            W: The W.
            H: The H.
            node_map: The node map.
        """
        NodeClass = node_map[self.item_type]
        scene = QGraphicsScene()
        try:
            node = NodeClass(0, 0, radius=18)
        except TypeError:
            node = NodeClass(0, 0)
        scene.addItem(node)

        rect = scene.itemsBoundingRect()
        if rect.isNull() or rect.width() == 0 or rect.height() == 0:
            rect = QRectF(0, 0, W, H)
        scene.render(painter, QRectF(0, 0, W, H), rect)

    def _render_arrow_preview(self, painter, W, H, arrow_map):
        """
        Render Arrow Preview.

        Args:
            painter: The painter.
            W: The W.
            H: The H.
            arrow_map: The arrow map.
        """
        ArrowClass = arrow_map[self.item_type]
        from PyQt6.QtWidgets import QGraphicsEllipseItem

        scene = QGraphicsScene()
        src_node = QGraphicsEllipseItem(-2, -2, 4, 4)
        dst_node = QGraphicsEllipseItem(-2, -2, 4, 4)
        src_node.setPos(8, H / 2)
        dst_node.setPos(W - 8, H / 2)
        scene.addItem(src_node)
        scene.addItem(dst_node)
        try:
            arrow = ArrowClass(src_node, dst_node)
            scene.addItem(arrow)
        except Exception as e:
            print(f"[ERROR] Sidebar preview error for {self.item_type}: {e}")

        rect = scene.itemsBoundingRect()
        if rect.isNull() or rect.width() == 0 or rect.height() == 0:
            rect = QRectF(0, 0, W, H)
        scene.render(painter, QRectF(0, 0, W, H), rect)

    def mousePressEvent(self, event):
        # if on_click this presente, tratar clicks as action (ej. composites)
        """
        Mousepressevent.

        Args:
            event: The event.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            # llamar callback (sin argumentos)
            try:
                self.on_click()
            except Exception as e:
                print(f"[ERROR] Error executing on_click for {self.item_type}: {e}")
            return
        # if no there is callback, iniciar drag normal
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_drag()

    def start_drag(self):
        """Start Drag."""
        mime = QMimeData()
        mime.setText(self.item_type)
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(self.pixmap().rect().center())
        drag.exec(Qt.DropAction.CopyAction)


class Sidebar(QWidget):
    """
    Sidebar.

    Methods:
        __init__: Initialize the instance.
    """

    def __init__(self, controller=None):
        """
        Initialize the instance.

        Args:
            controller: The controller.
        """
        super().__init__()
        self.controller = controller
        self._all_labels: list[DraggableLabel] = []

        self._update_tooltip_style()

        # Listen for theme changes
        theme_manager().theme_changed.connect(self._on_theme_changed)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self._update_tooltip_style()

        # ===== Items =====
        items_title = QLabel(tr("Items"))
        items_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        items_title.setProperty("class", "sidebar-title")
        items_title.setStyleSheet("font-weight:bold; font-size:14px; margin:8px;")
        self._title_labels = [items_title]
        main_layout.addWidget(items_title)

        items_grid = QGridLayout()
        items_grid.setHorizontalSpacing(8)
        items_grid.setVerticalSpacing(8)

        self.actor_label = DraggableLabel("Actor", "actor", tooltip_text="Actor")
        self._all_labels.append(self.actor_label)
        self.agent_label = DraggableLabel("Agent", "agent", tooltip_text="Agent")
        self._all_labels.append(self.agent_label)
        self.hardgoal_label = DraggableLabel(
            "HardGoal", "hard_goal", tooltip_text="HardGoal"
        )
        self._all_labels.append(self.hardgoal_label)
        self.softgoal_label = DraggableLabel(
            "SoftGoal", "soft_goal", tooltip_text="SoftGoal"
        )
        self._all_labels.append(self.softgoal_label)
        self.plan_label = DraggableLabel("Plan", "plan", tooltip_text="Plan")
        self._all_labels.append(self.plan_label)
        self.resource_label = DraggableLabel(
            "Resource", "resource", tooltip_text="Resource"
        )
        self._all_labels.append(self.resource_label)

        items_grid.addWidget(self.actor_label, 0, 0)
        items_grid.addWidget(self.agent_label, 0, 1)
        items_grid.addWidget(self.hardgoal_label, 1, 0)
        items_grid.addWidget(self.softgoal_label, 1, 1)
        items_grid.addWidget(self.plan_label, 2, 0)
        items_grid.addWidget(self.resource_label, 2, 1)

        main_layout.addLayout(items_grid)

        # ===== Links =====
        links_title = QLabel(tr("Links"))
        links_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        links_title.setProperty("class", "sidebar-title")
        links_title.setStyleSheet(
            "font-weight:bold; font-size:14px; margin:12px 8px 6px 8px;"
        )
        self._title_labels.append(links_title)
        main_layout.addWidget(links_title)

        links_grid = QGridLayout()
        links_grid.setHorizontalSpacing(8)
        links_grid.setVerticalSpacing(8)

        self.dependency_label = DraggableLabel(
            "Dependency", "dependency_link", tooltip_text="Dependency Link"
        )
        self._all_labels.append(self.dependency_label)
        self.why_label = DraggableLabel("Why", "why_link", tooltip_text="Why Link")
        self._all_labels.append(self.why_label)
        self.or_label = DraggableLabel(
            "OR Decomposition", "or_decomposition", tooltip_text="OR Decomposition"
        )
        self._all_labels.append(self.or_label)
        self.and_label = DraggableLabel(
            "AND Decomposition", "and_decomposition", tooltip_text="AND Decomposition"
        )
        self._all_labels.append(self.and_label)
        self.contribution_label = DraggableLabel(
            "Contribution", "contribution", tooltip_text="Contribution"
        )
        self._all_labels.append(self.contribution_label)
        self.means_label = DraggableLabel(
            "Means-End", "means_end", tooltip_text="Means-End"
        )
        self._all_labels.append(self.means_label)

        links_grid.addWidget(self.dependency_label, 0, 0)
        links_grid.addWidget(self.why_label, 0, 1)
        links_grid.addWidget(self.or_label, 1, 0)
        links_grid.addWidget(self.and_label, 1, 1)
        links_grid.addWidget(self.contribution_label, 2, 0)
        links_grid.addWidget(self.means_label, 2, 1)

        main_layout.addLayout(links_grid)

        # ===== Composite Dependencies =====
        comp_title = QLabel(tr("Composite Dependencies"))
        comp_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        comp_title.setProperty("class", "sidebar-title")
        comp_title.setStyleSheet(
            "font-weight:bold; font-size:14px; margin:12px 8px 6px 8px;"
        )
        self._title_labels.append(comp_title)
        main_layout.addWidget(comp_title)

        comp_grid = QGridLayout()
        comp_grid.setHorizontalSpacing(8)
        comp_grid.setVerticalSpacing(8)

        # when itself hace click in these labels, llamamos al controlador
        # para activar modo composite
        def make_onclick(node_type):
            """
            Make Onclick.

            Args:
                node_type: The node type.
            """
            return lambda: self._start_composite(node_type)

        self.hard_comp = DraggableLabel(
            "HardGoal Composite",
            "composite:hard_goal",
            on_click=make_onclick("hard_goal"),
            tooltip_text="HardGoal Composite",
        )
        self._all_labels.append(self.hard_comp)
        self.soft_comp = DraggableLabel(
            "SoftGoal Composite",
            "composite:soft_goal",
            on_click=make_onclick("soft_goal"),
            tooltip_text="SoftGoal Composite",
        )
        self._all_labels.append(self.soft_comp)
        self.plan_comp = DraggableLabel(
            "Plan Composite",
            "composite:plan",
            on_click=make_onclick("plan"),
            tooltip_text="Plan Composite",
        )
        self._all_labels.append(self.plan_comp)
        self.res_comp = DraggableLabel(
            "Resource Composite",
            "composite:resource",
            on_click=make_onclick("resource"),
            tooltip_text="Resource Composite",
        )
        self._all_labels.append(self.res_comp)

        comp_grid.addWidget(self.hard_comp, 0, 0)
        comp_grid.addWidget(self.soft_comp, 0, 1)
        comp_grid.addWidget(self.plan_comp, 1, 0)
        comp_grid.addWidget(self.res_comp, 1, 1)

        main_layout.addLayout(comp_grid)
        main_layout.addStretch()

    def retranslate(self):
        """Retranslate all sidebar text."""
        for child in self.findChildren(DraggableLabel):
            child.retranslate()
    def _update_tooltip_style(self):
        """Update tooltip stylesheet based on theme."""
        if theme_manager().is_dark:
            self.setStyleSheet("""
                QToolTip {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 4px;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QToolTip {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #333333;
                    padding: 4px;
                    font-size: 12px;
                }
            """)

    def _on_theme_changed(self, dark: bool):
        """Update sidebar styles when theme changes."""
        self._update_tooltip_style()
        for label in self._all_labels:
            label._update_style()
        for title in self._title_labels:
            if dark:
                title.setStyleSheet(
                    "font-weight:bold; font-size:14px; margin:8px; color: #e0e0e0;"
                )
            else:
                title.setStyleSheet(
                    "font-weight:bold; font-size:14px; margin:8px;"
                )

    def _start_composite(self, node_type):
        """
        Start Composite.

        Args:
            node_type: The node type.
        """
        if not self.controller:
            print("Sidebar: composite clicked but no controller attached.")
            return
        try:
            self.controller.start_composite_dependency_mode(node_type)
        except Exception as e:
            print(f"[ERROR] Error starting composite mode for {node_type}: {e}")
