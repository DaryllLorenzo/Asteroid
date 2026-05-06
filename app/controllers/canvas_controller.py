# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSignal

from app.controllers.canvas_deletion_controller import CanvasDeletionController
from app.controllers.canvas_export_controller import CanvasExportController
from app.controllers.canvas_import_controller import CanvasImportController
from app.controllers.canvas_interaction_controller import CanvasInteractionController
from app.controllers.canvas_node_controller import CanvasNodeController
from app.controllers.canvas_state_controller import CanvasStateController


class CanvasController(
    QObject,
    CanvasStateController,
    CanvasNodeController,
    CanvasInteractionController,
    CanvasDeletionController,
    CanvasExportController,
    CanvasImportController,
):
    node_selected = pyqtSignal(object)
    selected_node_properties_changed = pyqtSignal(dict)
    node_deleted = pyqtSignal(object)
    edge_selected = pyqtSignal(object)
    edge_deleted = pyqtSignal(object)
    selection_changed = pyqtSignal(object)
    project_modified = pyqtSignal(bool)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.nodes = []
        self.edges = []

        # Arrow mode
        self.arrow_mode = False
        self.selected_arrow_type = None
        self.selected_nodes_for_arrow = []

        # Composite mode
        self.composite_mode = False
        self.composite_node_type = None

        self._current_subcanvas = None

        # Selection mode
        self.selection_mode = False
        self.selected_node = None
        self.selected_edge = None
        self.current_selection = None

        self._subcanvas_handlers: dict[object, tuple[object, callable, callable]] = {}

        # Project state tracking
        self._current_file_path = None
        self._is_modified = False

        # Connect signals
        self.canvas.node_dropped.connect(self.add_node)
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)
        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)

        # Setup keyboard shortcuts for deletion
        self._setup_delete_shortcut()
