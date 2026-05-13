# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QUndoStack

from app.commands.add_node_command import AddNodeCommand
from app.commands.delete_edge_command import DeleteEdgeCommand
from app.commands.delete_node_command import DeleteNodeCommand
from app.controller_types import CanvasNodeItem
from app.controller_types import SubcanvasHandler
from app.controllers.canvas_deletion_controller import CanvasDeletionController
from app.controllers.canvas_export_controller import CanvasExportController
from app.controllers.canvas_import_controller import CanvasImportController
from app.controllers.canvas_interaction_controller import CanvasInteractionController
from app.controllers.canvas_node_controller import CanvasNodeController
from app.controllers.canvas_state_controller import CanvasStateController
from app.ui.canvas import Canvas
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.control_point_handle import ControlPointHandle


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

    def __init__(self, canvas: Canvas) -> None:
        super().__init__()
        self.canvas = canvas
        self.nodes: list[CanvasNodeItem] = []
        self.edges: list[BaseEdgeItem] = []

        # Arrow mode
        self.arrow_mode: bool = False
        self.selected_arrow_type: str | None = None
        self.selected_nodes_for_arrow: list[CanvasNodeItem] = []

        # Composite mode
        self.composite_mode: bool = False
        self.composite_node_type: str | None = None

        self._current_subcanvas = None

        # Selection mode
        self.selection_mode: bool = False
        self.selected_node: CanvasNodeItem | None = None
        self.selected_edge: BaseEdgeItem | None = None
        self.current_selection: CanvasNodeItem | BaseEdgeItem | None = None

        self._subcanvas_handlers: dict[CanvasNodeItem, SubcanvasHandler] = {}

        # Project state tracking
        self._current_file_path: str | None = None
        self._is_modified: bool = False

        # Undo stack
        self.undo_stack = QUndoStack(self)
        self.undo_stack.cleanChanged.connect(self._on_clean_changed)

        # Connect signals
        self.canvas.node_dropped.connect(
            lambda t, x, y: self.undo_stack.push(AddNodeCommand(self, t, x, y))
        )
        self.canvas.arrow_dropped.connect(self.start_arrow_mode)
        self.canvas.node_clicked.connect(self.handle_node_click)
        scene = self.canvas.scene()
        if scene is not None:
            scene.selectionChanged.connect(self.on_selection_changed)

        # Setup keyboard shortcuts for deletion
        self._setup_delete_shortcut()

    def _on_clean_changed(self, clean: bool) -> None:
        """Sync undo stack clean state with project modified state."""
        self._is_modified = not clean
        self.project_modified.emit(not clean)

    def delete_selected_item(self) -> None:
        """Override: push DeleteNodeCommand when deleting a node."""
        scene = self.canvas.scene()
        if scene is None:
            return

        selected_items = scene.selectedItems()
        for item in selected_items:
            if isinstance(item, ControlPointHandle):
                self._delete_selected_control_point(item)
                return

        if self.selected_edge:
            self.undo_stack.push(DeleteEdgeCommand(self, self.selected_edge))
        elif self.selected_node:
            self.undo_stack.push(DeleteNodeCommand(self, self.selected_node))
        else:
            print("No element selected for deletion")
