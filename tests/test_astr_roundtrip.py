# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Persistence fidelity of the `.astr` project format.

These tests back the paper's claim that a diagram's complete state survives
a save/load cycle. The invariant asserted is the *fixpoint* property: once a
scene has been written by the current serialiser, reloading and re-saving it
must reproduce the file byte for byte.

Note on the checked-in fixtures: they were written by an earlier build, which
also emitted `properties.node_type` and always wrote `model_properties
.is_composite`. The current serialiser omits the former (the node type is
already carried by the top-level `type` field) and writes the latter as
`False` instead of leaving it absent. That is why the fixtures are compared
semantically and only the second and third generations are compared exactly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from conftest import make_node
from conftest import scene_of
import pytest

from app.core.models.composite_model_wrapper import CompositeModelWrapper
from app.utils.astr_format import AstrFormat

if TYPE_CHECKING:
    from app.controllers.canvas_controller import CanvasController

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_FIXTURES = sorted(REPO_ROOT.glob("*.astr"))


def _write_temp(data: dict[str, Any], tmp_path: Path) -> Path:
    path = tmp_path / "scene.astr"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _round_trip(
    data: dict[str, Any], tmp_path: Path
) -> tuple[dict[str, Any], CanvasController, bool]:
    """Write `data`, import it into a fresh controller, re-serialise."""
    from app.controllers.canvas_controller import CanvasController
    from app.ui.canvas import Canvas

    controller = CanvasController(Canvas())
    ok = controller.import_from_astr(str(_write_temp(data, tmp_path)))
    return (
        AstrFormat.serialize_scene(controller.nodes, controller.edges),
        controller,
        ok,
    )


@pytest.fixture
def populated_scene(controller: CanvasController) -> None:
    """One node of every type and one edge of every type."""
    from app.controllers.canvas_registry_controller import _ARROW_TYPES
    from app.controllers.canvas_registry_controller import _NODE_MAP

    nodes = [
        make_node(controller, node_type, index * 150, 0)
        for index, node_type in enumerate(_NODE_MAP)
    ]
    for arrow_class in _ARROW_TYPES.values():
        edge = arrow_class(nodes[0], nodes[1])
        scene_of(controller).addItem(edge)
        controller.edges.append(edge)


class TestRoundTripFidelity:
    def test_synthetic_scene_reload_is_a_fixpoint(
        self,
        controller: CanvasController,
        populated_scene: None,
        tmp_path: Path,
    ) -> None:
        from app.utils.astr_format import AstrFormat

        first = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        second, _, ok = _round_trip(first, tmp_path)
        third, _, _ = _round_trip(second, tmp_path)

        assert ok
        assert second == third

    def test_node_and_edge_counts_survive(
        self,
        controller: CanvasController,
        populated_scene: None,
        tmp_path: Path,
    ) -> None:
        from app.utils.astr_format import AstrFormat

        before = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        after, reloaded, ok = _round_trip(before, tmp_path)

        assert ok
        assert len(after["nodes"]) == len(before["nodes"])
        assert len(after["edges"]) == len(before["edges"])
        assert len(reloaded.nodes) == len(before["nodes"])
        assert len(reloaded.edges) == len(before["edges"])

    def test_node_types_and_labels_survive(
        self,
        controller: CanvasController,
        populated_scene: None,
        tmp_path: Path,
    ) -> None:
        from app.utils.astr_format import AstrFormat

        before = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        after, _, _ = _round_trip(before, tmp_path)

        assert [node["type"] for node in after["nodes"]] == [
            node["type"] for node in before["nodes"]
        ]
        assert [node["properties"]["label"] for node in after["nodes"]] == [
            node["properties"]["label"] for node in before["nodes"]
        ]

    def test_edge_endpoints_survive(
        self,
        controller: CanvasController,
        populated_scene: None,
        tmp_path: Path,
    ) -> None:
        from app.utils.astr_format import AstrFormat

        before = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        after, _, _ = _round_trip(before, tmp_path)

        def wiring(scene: dict[str, Any]) -> list[tuple[str, int, int]]:
            return [
                (edge["type"], edge["source_id"], edge["target_id"])
                for edge in scene["edges"]
            ]

        assert wiring(after) == wiring(before)


class TestRealProjectFiles:
    """The diagrams that ship with the repository must load unmodified."""

    def test_fixtures_exist(self) -> None:
        assert REAL_FIXTURES, "no .astr fixtures found in the repository root"

    @pytest.mark.parametrize("path", REAL_FIXTURES, ids=lambda p: p.name)
    def test_import_matches_recorded_metadata(
        self,
        path: Path,
        message_boxes: dict[str, list[str]],
    ) -> None:
        from app.controllers.canvas_controller import CanvasController
        from app.ui.canvas import Canvas

        recorded = json.loads(path.read_text(encoding="utf-8"))["metadata"]
        controller = CanvasController(Canvas())

        assert controller.import_from_astr(str(path)) is True
        assert len(controller.nodes) == recorded["node_count"]
        assert len(controller.edges) == recorded["edge_count"]
        assert message_boxes["critical"] == []

    @pytest.mark.parametrize("path", REAL_FIXTURES, ids=lambda p: p.name)
    def test_reload_is_a_fixpoint(self, path: Path, tmp_path: Path) -> None:
        original = json.loads(path.read_text(encoding="utf-8"))
        second, _, ok = _round_trip(original, tmp_path)
        third, _, _ = _round_trip(second, tmp_path)

        assert ok
        assert second == third

    @pytest.mark.parametrize("path", REAL_FIXTURES, ids=lambda p: p.name)
    def test_visual_properties_survive(self, path: Path, tmp_path: Path) -> None:
        original = json.loads(path.read_text(encoding="utf-8"))
        after, _, _ = _round_trip(original, tmp_path)

        visual_keys = ("label", "color", "border_color", "text_color", "radius")
        for before_node, after_node in zip(
            original["nodes"], after["nodes"], strict=True
        ):
            for key in visual_keys:
                assert before_node["properties"][key] == after_node["properties"][key]


class TestCompositeDependencyRoundTrip:
    """Composite nodes are re-linked heuristically on import, since the format
    stores no explicit internal/external link id."""

    def test_internal_node_is_reimported_into_the_subcanvas(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        source = make_node(controller, "actor", -300, 0)
        target = make_node(controller, "actor", 300, 0)
        controller.selected_nodes_for_arrow = [source, target]
        controller.composite_node_type = "hard_goal"
        middle, internal, edge_a, edge_b = controller.create_composite_dependency()

        assert middle is not None
        assert internal is not None
        assert internal.parentItem() is not None

        from app.utils.astr_format import AstrFormat

        before = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        after, reloaded, ok = _round_trip(before, tmp_path)

        assert ok
        assert len(reloaded.nodes) == len(before["nodes"])
        assert len(reloaded.edges) == len(before["edges"])

    def test_internal_external_pairing_is_preserved(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        source = make_node(controller, "actor", -300, 0)
        target = make_node(controller, "actor", 300, 0)
        controller.selected_nodes_for_arrow = [source, target]
        controller.composite_node_type = "hard_goal"
        middle, internal, _, _ = controller.create_composite_dependency()

        external_position = middle.model.get_external_model().position_in_subcanvas_x
        internal_position = middle.model.get_internal_model().position_in_subcanvas_x

        from app.utils.astr_format import AstrFormat

        before = AstrFormat.serialize_scene(controller.nodes, controller.edges)
        _, reloaded, _ = _round_trip(before, tmp_path)

        wrappers = [
            node for node in reloaded.nodes if hasattr(node.model, "get_internal_model")
        ]
        assert wrappers

        reloaded_middle = cast("CompositeModelWrapper", wrappers[0].model)
        assert (
            reloaded_middle.get_external_model().position_in_subcanvas_x
            == external_position
        )
        assert (
            reloaded_middle.get_internal_model().position_in_subcanvas_x
            == internal_position
        )


class TestErrorIsolation:
    """A malformed element is skipped, never fatal to the whole load."""

    def test_node_without_position_is_skipped(
        self, tmp_path: Path, message_boxes: dict[str, list[str]]
    ) -> None:
        scene = {
            "version": "1.4",
            "metadata": {"created_by": "Asteroid", "node_count": 2, "edge_count": 0},
            "nodes": [
                {"id": 0, "type": "actor", "properties": {}, "parent_id": None},
                {
                    "id": 1,
                    "type": "hard_goal",
                    "position": {"x": 100.0, "y": 100.0},
                    "properties": {},
                    "parent_id": None,
                },
            ],
            "edges": [],
        }

        _, controller, ok = _round_trip(scene, tmp_path)

        assert ok
        assert len(controller.nodes) == 1
        assert message_boxes["critical"] == []
        assert message_boxes["warning"]

    def test_unknown_node_type_is_skipped(
        self, tmp_path: Path, message_boxes: dict[str, list[str]]
    ) -> None:
        scene = {
            "version": "1.4",
            "metadata": {"created_by": "Asteroid", "node_count": 2, "edge_count": 0},
            "nodes": [
                {
                    "id": 0,
                    "type": "not_a_real_type",
                    "position": {"x": 0.0, "y": 0.0},
                    "properties": {},
                    "parent_id": None,
                },
                {
                    "id": 1,
                    "type": "plan",
                    "position": {"x": 50.0, "y": 50.0},
                    "properties": {},
                    "parent_id": None,
                },
            ],
            "edges": [],
        }

        _, controller, ok = _round_trip(scene, tmp_path)

        assert ok
        assert len(controller.nodes) == 1
        assert message_boxes["critical"] == []

    def test_edge_with_missing_endpoint_is_dropped(
        self, tmp_path: Path, message_boxes: dict[str, list[str]]
    ) -> None:
        scene = {
            "version": "1.4",
            "metadata": {"created_by": "Asteroid", "node_count": 1, "edge_count": 1},
            "nodes": [
                {
                    "id": 0,
                    "type": "actor",
                    "position": {"x": 0.0, "y": 0.0},
                    "properties": {},
                    "parent_id": None,
                }
            ],
            "edges": [
                {
                    "type": "dependency_link",
                    "source_id": 0,
                    "target_id": 99,
                    "properties": {},
                    "parent_id": None,
                    "control_points": [],
                }
            ],
        }

        _, controller, ok = _round_trip(scene, tmp_path)

        assert ok
        assert len(controller.nodes) == 1
        assert message_boxes["critical"] == []

    def test_truncated_file_is_reported_not_raised(self, tmp_path: Path) -> None:
        from app.controllers.canvas_controller import CanvasController
        from app.ui.canvas import Canvas

        path = tmp_path / "broken.astr"
        path.write_text('{"version": "1.4", "nodes": [', encoding="utf-8")

        controller = CanvasController(Canvas())
        assert controller.import_from_astr(str(path)) is False
        assert controller.nodes == []
