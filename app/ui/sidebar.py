# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QGraphicsScene
from PyQt6.QtCore import Qt, QMimeData, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QDrag

# Node items
from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem

# Arrow/link items (deben aceptar (source_node, dest_node) en su constructor)
from app.ui.components.dependency_item.dependency_link_edge_item import DependencyLinkArrowItem
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import OrDecompositionArrowItem
from app.ui.components.dependency_item.and_decomposition_edge_item import AndDecompositionArrowItem
from app.ui.components.dependency_item.contribution_edge_item import ContributionArrowItem
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem


class DraggableLabel(QLabel):
    """
    Label arrastrable para nodos / links o boton de composite.
    Si se proporciona `on_click` se ejecuta con click (usado para composites).
    """
    def __init__(self, text: str, item_type: str, on_click=None):
        super().__init__(text)
        self.item_type = item_type
        self.on_click = on_click
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
        self.setPixmap(self.create_pixmap())

    def create_pixmap(self) -> QPixmap:
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
    
        # === Caso especial: composite preview ===
        if self.item_type.startswith("composite:"):
            scene = QGraphicsScene()
    
            # 1️⃣ Crear nodo centrado
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
    
            # Renderizar nodo
            rect = scene.itemsBoundingRect()
            if rect.isNull() or rect.width() == 0 or rect.height() == 0:
                rect = QRectF(0, 0, W, H)
            scene.render(painter, QRectF(0, 0, W, H), rect)
    
            # 2️⃣ Calcular límites reales del nodo y dibujar líneas
            if node:
                node_bounds = node.boundingRect()
                # El boundingRect es relativo al nodo → lo convertimos a coordenadas de escena
                node_left = node_center_x + node_bounds.left()
                node_right = node_center_x + node_bounds.right()
    
                # Separación adicional para que la línea no toque el borde
                margin = 4
                y = int(H / 2)
    
                pen = painter.pen()
                pen.setWidth(2)
                painter.setPen(pen)
    
                # Línea izquierda: desde el borde hasta un poco antes del nodo
                painter.drawLine(8, y, int(node_left - margin), y)
                # Línea derecha: desde un poco después del nodo hasta el borde derecho
                painter.drawLine(int(node_right + margin), y, W - 8, y)
    
        else:
            # === Nodos normales ===
            if self.item_type in node_map:
                NodeClass = node_map[self.item_type]
                scene = QGraphicsScene()
                try:
                    node = NodeClass(0, 0, radius=18)
                except TypeError:
                    node = NodeClass(0, 0)
                scene.addItem(node)
    
            # === Flechas normales ===
            elif self.item_type in arrow_map:
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
                    print(f"⚠️ Sidebar preview error for {self.item_type}: {e}")
    
            # Render general
            rect = scene.itemsBoundingRect()
            if rect.isNull() or rect.width() == 0 or rect.height() == 0:
                rect = QRectF(0, 0, W, H)
            scene.render(painter, QRectF(0, 0, W, H), rect)
    
        painter.end()
        return pixmap



    def mousePressEvent(self, event):
        # si on_click está presente, tratar clicks como acción (ej. composites)
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            # llamar callback (sin argumentos)
            try:
                self.on_click()
            except Exception as e:
                print(f"⚠️ Error al ejecutar on_click de {self.item_type}: {e}")
            return
        # si no hay callback, iniciar drag normal
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
    """
    Sidebar con 3 secciones:
      - Items (nodos)
      - Links (flechas)
      - Composite Dependencies (botones que activan modo composite en el controller)
    Si `controller` es provisto, los composites invocan controller.start_composite_dependency_mode(tipo).
    """
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
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

        # ===== Composite Dependencies =====
        comp_title = QLabel("🧩 Composite Dependencies")
        comp_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        comp_title.setStyleSheet("font-weight:bold; font-size:14px; margin:12px 8px 6px 8px;")
        main_layout.addWidget(comp_title)

        comp_grid = QGridLayout()
        comp_grid.setHorizontalSpacing(8)
        comp_grid.setVerticalSpacing(8)

        # cuando se hace click en estos labels, llamamos al controlador para activar modo composite
        def make_onclick(node_type):
            return lambda: self._start_composite(node_type)

        self.hard_comp = DraggableLabel("HardGoal Composite", "composite:hard_goal", on_click=make_onclick("hard_goal"))
        self.soft_comp = DraggableLabel("SoftGoal Composite", "composite:soft_goal", on_click=make_onclick("soft_goal"))
        self.plan_comp = DraggableLabel("Plan Composite", "composite:plan", on_click=make_onclick("plan"))
        self.res_comp = DraggableLabel("Resource Composite", "composite:resource", on_click=make_onclick("resource"))

        comp_grid.addWidget(self.hard_comp, 0, 0)
        comp_grid.addWidget(self.soft_comp, 0, 1)
        comp_grid.addWidget(self.plan_comp, 1, 0)
        comp_grid.addWidget(self.res_comp, 1, 1)

        main_layout.addLayout(comp_grid)
        main_layout.addStretch()

    def _start_composite(self, node_type):
        """Callback de los botones composite: delega al controller si existe."""
        if not self.controller:
            print("Sidebar: composite clicked but no controller attached.")
            return
        try:
            self.controller.start_composite_dependency_mode(node_type)
        except Exception as e:
            print(f"⚠️ Error starting composite mode for {node_type}: {e}")
