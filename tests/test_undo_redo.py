# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Undo/redo correctness of the command stack.

Rather than exercising each command in isolation, these tests assert a single
invariant that subsumes them: the serialised scene is a faithful fingerprint
of editor state, so undoing every pushed command must reproduce the scene
exactly as it was beforehand, and redoing them must reproduce the edited
state. Any command that restores state incorrectly breaks this property.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import make_node
from conftest import scene_of
from PyQt6.QtCore import QPointF

from app.commands.add_edge_command import AddEdgeCommand
from app.commands.add_node_command import AddNodeCommand
from app.commands.delete_node_command import DeleteNodeCommand
from app.commands.move_node_command import MoveNodeCommand
from app.commands.resize_node_command import ResizeNodeCommand
from app.controllers.canvas_registry_controller import _ARROW_TYPES
from app.utils.astr_format import AstrFormat

if TYPE_CHECKING:
    from app.controllers.canvas_controller import CanvasController


def _fingerprint(controller: CanvasController) -> dict:
    return AstrFormat.serialize_scene(controller.nodes, controller.edges)


def _rewind(controller: CanvasController) -> None:
    for _ in range(controller.undo_stack.count()):
        controller.undo_stack.undo()


def _replay(controller: CanvasController) -> None:
    for _ in range(controller.undo_stack.count()):
        controller.undo_stack.redo()


class TestUndoRedoInvariant:
    def test_undo_redo_of_every_command_restores_the_scene(
        self, controller: CanvasController
    ) -> None:
        actor = make_node(controller, "actor", 0, 0)
        goal = make_node(controller, "hard_goal", 250, 0)
        original = _fingerprint(controller)
        original_radius = goal.model.radius
        original_position = goal.pos()

        controller.undo_stack.push(AddNodeCommand(controller, "resource", 700, 0))
        edge = _ARROW_TYPES["dependency_link"](actor, goal)
        controller.undo_stack.push(AddEdgeCommand(controller, edge, None))
        controller.undo_stack.push(
            MoveNodeCommand(
                controller,
                goal,
                original_position,
                original_position + QPointF(0, 40),
            )
        )
        controller.undo_stack.push(
            ResizeNodeCommand(controller, goal, original_radius, 90.0)
        )

        depth = controller.undo_stack.count()
        assert depth == 4
        edited = _fingerprint(controller)
        assert edited != original

        _rewind(controller)
        assert _fingerprint(controller) == original

        _replay(controller)
        assert _fingerprint(controller) == edited

    def test_new_commands_are_appended_after_undo(
        self, controller: CanvasController
    ) -> None:
        make_node(controller, "actor", 0, 0)
        controller.undo_stack.push(AddNodeCommand(controller, "plan", 100, 0))
        controller.undo_stack.undo()

        # `count()` is the stack size; `index()` is the redo cursor.
        assert controller.undo_stack.count() == 1
        assert controller.undo_stack.index() == 0
        assert controller.undo_stack.canRedo() is True

        controller.undo_stack.push(AddNodeCommand(controller, "plan", 100, 0))
        assert controller.undo_stack.count() == 1
        assert controller.undo_stack.index() == 1
        assert controller.undo_stack.canUndo() is True
        assert controller.undo_stack.canRedo() is False


class TestDestructiveCommands:
    def test_delete_then_undo_restores_the_node(
        self, controller: CanvasController
    ) -> None:
        actor = make_node(controller, "actor", 0, 0)
        original = _fingerprint(controller)

        controller.undo_stack.push(DeleteNodeCommand(controller, actor))
        assert len(controller.nodes) == 0

        controller.undo_stack.undo()
        assert _fingerprint(controller) == original

    def test_delete_removes_incident_edges(self, controller: CanvasController) -> None:
        """Deleting a node must not leave a dangling edge in the scene."""
        actor = make_node(controller, "actor", 0, 0)
        goal = make_node(controller, "hard_goal", 250, 0)
        edge = _ARROW_TYPES["dependency_link"](actor, goal)
        scene_of(controller).addItem(edge)
        controller.edges.append(edge)

        controller.undo_stack.push(DeleteNodeCommand(controller, actor))

        assert len(controller.nodes) == 1
        assert all(
            e.source_node is not actor and e.dest_node is not actor
            for e in controller.edges
        )

    def test_stack_starts_empty_and_clean(self, controller: CanvasController) -> None:
        assert controller.undo_stack.count() == 0
        assert controller.undo_stack.isClean() is True
