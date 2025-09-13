from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem
from app.ui.components.dependency_item.simple_edge_item import SimpleArrowItem
from app.ui.components.dependency_item.dashed_edge_item import DashedArrowItem


class CanvasController:
    """Conecta el Canvas (vista) con la lógica de nodos y aristas."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.nodes = []
        self.edges = []

        # Estado para modo flecha
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []

        # Conectar señales del canvas
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)

    # ---------------------
    # NODOS
    # ---------------------
    def add_node(self, node_type, x, y):
        if node_type == "actor":
            node_item = ActorNodeItem(x, y)
        elif node_type == "agent":
            node_item = AgentNodeItem(x, y)
        else:
            return None

        self.canvas.scene.addItem(node_item)
        self.nodes.append(node_item)
        return node_item

    # ---------------------
    # ARISTAS
    # ---------------------
    def start_arrow_mode(self, arrow_type):
        """Activa el modo flecha al soltar un tipo en el canvas."""
        self.arrow_mode = True
        self.selected_arrow_type = arrow_type
        self.selected_nodes_for_arrow = []

    def handle_node_click(self, node_item):
        """Cuando se clickea un nodo, si estamos en modo flecha se selecciona para conectar."""
        if not self.arrow_mode:
            return

        if node_item not in self.selected_nodes_for_arrow:
            self.selected_nodes_for_arrow.append(node_item)
            node_item.setSelected(True)

        # Si ya hay dos nodos, crear la flecha
        if len(self.selected_nodes_for_arrow) == 2:
            self.create_arrow()

    def create_arrow(self):
        src, dst = self.selected_nodes_for_arrow

        if self.selected_arrow_type == "simple":
            edge_item = SimpleArrowItem(src, dst)
        elif self.selected_arrow_type == "dashed":
            edge_item = DashedArrowItem(src, dst)
        else:
            return None

        self.canvas.scene.addItem(edge_item)
        self.edges.append(edge_item)

        # Reset estado
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []

        # Deseleccionar nodos
        for node in self.nodes:
            node.setSelected(False)

        return edge_item
