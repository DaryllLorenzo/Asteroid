# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# app/ui/sidebar.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QGraphicsScene, QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QMimeData, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QDrag

# Node items
from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem

# Arrow/link items (ahora aceptan source_node, dest_node)
from app.ui.components.dependency_item.dependency_link_edge_item import DependencyLinkArrowItem
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import OrDecompositionArrowItem
from app.ui.components.dependency_item.and_decomposition_edge_item import AndDecompositionArrowItem
from app.ui.components.dependency_item.contribution_edge_item import ContributionArrowItem
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem


class DraggableLabel(QLabel):
    def __init__(self, text: str, item_type: str):
        super().__init__(text)
        self.item_type = item_type
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 8px;
                background-color: #fafafa;
                min-width: 90px;
                min-height: 90px;
            }
            QLabel:hover {
                background-color: #f0f0f0;
                border: 2px solid #888888;
            }
        """)
        # render thumbnail once
        self.setPixmap(self.create_pixmap())

    def create_pixmap(self) -> QPixmap:
        W, H = 80, 80
        pixmap = QPixmap(W, H)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Map de clases para nodos y flechas
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

        scene = QGraphicsScene()

        # Crear vista previa para nodos
        if self.item_type in node_map:
            NodeClass = node_map[self.item_type]
            try:
                node = NodeClass(0, 0, radius=18)
            except TypeError:
                node = NodeClass(0, 0)
            scene.addItem(node)

        # Crear vista previa para flechas
        elif self.item_type in arrow_map:
            ArrowClass = arrow_map[self.item_type]

            # Crear nodos ficticios en la escena (pequeños, centrados en la miniatura)
            src_node = QGraphicsEllipseItem(-2, -2, 4, 4)
            dst_node = QGraphicsEllipseItem(-2, -2, 4, 4)
            src_node.setPos(8, H / 2)
            dst_node.setPos(W - 8, H / 2)
            scene.addItem(src_node)
            scene.addItem(dst_node)

            # Crear la flecha con los nodos ficticios
            try:
                arrow = ArrowClass(src_node, dst_node)
                scene.addItem(arrow)
            except Exception as e:
                # si ocurre algo no crítico, lo mostramos por consola pero no rompemos la UI
                print(f"⚠️ Error creando preview para {self.item_type}: {e}")

        # Renderizar la escena dentro del pixmap
        rect = scene.itemsBoundingRect()
        if rect.isNull() or rect.width() == 0 or rect.height() == 0:
            rect = QRectF(0, 0, W, H)

        scene.render(painter, QRectF(0, 0, W, H), rect)
        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_drag()

    def start_drag(self):
        mime = QMimeData()
        mime.setText(self.item_type)
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(self.pixmap().rect().center())
        drag.exec(Qt.DropAction.CopyAction)


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ===== Items =====
        items_title = QLabel("🧩 Items")
        items_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        items_title.setStyleSheet("font-weight:bold; font-size:14px; margin:8px;")
        main_layout.addWidget(items_title)

        items_grid = QGridLayout()
        items_grid.setHorizontalSpacing(8)
        items_grid.setVerticalSpacing(8)

        self.actor_label = DraggableLabel("Actor", "actor")
        self.agent_label = DraggableLabel("Agent", "agent")
        self.hardgoal_label = DraggableLabel("HardGoal", "hard_goal")
        self.softgoal_label = DraggableLabel("SoftGoal", "soft_goal")
        self.plan_label = DraggableLabel("Plan", "plan")
        self.resource_label = DraggableLabel("Resource", "resource")

        items_grid.addWidget(self.actor_label, 0, 0)
        items_grid.addWidget(self.agent_label, 0, 1)
        items_grid.addWidget(self.hardgoal_label, 1, 0)
        items_grid.addWidget(self.softgoal_label, 1, 1)
        items_grid.addWidget(self.plan_label, 2, 0)
        items_grid.addWidget(self.resource_label, 2, 1)

        main_layout.addLayout(items_grid)

        # ===== Links =====
        links_title = QLabel("🔗 Links")
        links_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        links_title.setStyleSheet("font-weight:bold; font-size:14px; margin:12px 8px 6px 8px;")
        main_layout.addWidget(links_title)

        links_grid = QGridLayout()
        links_grid.setHorizontalSpacing(8)
        links_grid.setVerticalSpacing(8)

        self.dependency_label = DraggableLabel("Dependency", "dependency_link")
        self.why_label = DraggableLabel("Why", "why_link")
        self.or_label = DraggableLabel("OR Decomposition", "or_decomposition")
        self.and_label = DraggableLabel("AND Decomposition", "and_decomposition")
        self.contribution_label = DraggableLabel("Contribution", "contribution")
        self.means_label = DraggableLabel("Means-End", "means_end")

        links_grid.addWidget(self.dependency_label, 0, 0)
        links_grid.addWidget(self.why_label, 0, 1)
        links_grid.addWidget(self.or_label, 1, 0)
        links_grid.addWidget(self.and_label, 1, 1)
        links_grid.addWidget(self.contribution_label, 2, 0)
        links_grid.addWidget(self.means_label, 2, 1)

        main_layout.addLayout(links_grid)
        main_layout.addStretch()
