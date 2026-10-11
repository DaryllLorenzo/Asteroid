# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Export paths: PDF and the per-agent report images.

These back the paper's "export and persistence" claim. Assertions are on
observable output — the magic bytes of the produced file, its presence, and
the dialog the user would have seen — rather than on reportlab's internals.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog
import pytest

from app.controllers.canvas_registry_controller import _ARROW_TYPES
from app.utils.agent_report_export import AgentReportExporter
from app.utils.pdf_export import PDFGenerator

if TYPE_CHECKING:
    from app.controllers.canvas_controller import CanvasController

from conftest import make_node
from conftest import scene_of

PDF_MAGIC = b"%PDF-"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def diagram(controller: CanvasController) -> CanvasController:
    """A small representative diagram: two entities, a goal, one link."""
    actor = make_node(controller, "actor", 0, 0)
    goal = make_node(controller, "hard_goal", 250, 0)
    edge = _ARROW_TYPES["dependency_link"](actor, goal)
    scene_of(controller).addItem(edge)
    controller.edges.append(edge)
    return controller


# --------------------------------------------------------------------- PDF


class TestPdfExport:
    def test_produces_a_valid_pdf(
        self, diagram: CanvasController, tmp_path: Path
    ) -> None:
        target = tmp_path / "diagram.pdf"

        result = PDFGenerator(diagram).export_to_pdf(
            with_additional_info=True, filename=str(target)
        )

        assert result is True
        assert target.exists()
        assert target.stat().st_size > 0
        assert target.read_bytes().startswith(PDF_MAGIC)

    @pytest.mark.parametrize("with_additional_info", [True, False])
    def test_succeeds_with_or_without_element_tables(
        self, diagram: CanvasController, tmp_path: Path, with_additional_info: bool
    ) -> None:
        target = tmp_path / f"info_{with_additional_info}.pdf"

        result = PDFGenerator(diagram).export_to_pdf(
            with_additional_info=with_additional_info, filename=str(target)
        )

        assert result is True
        assert target.read_bytes().startswith(PDF_MAGIC)

    def test_additional_info_adds_content(
        self, diagram: CanvasController, tmp_path: Path
    ) -> None:
        """The flag must actually change the output, not just be accepted."""
        bare = tmp_path / "bare.pdf"
        full = tmp_path / "full.pdf"

        PDFGenerator(diagram).export_to_pdf(
            with_additional_info=False, filename=str(bare)
        )
        PDFGenerator(diagram).export_to_pdf(
            with_additional_info=True, filename=str(full)
        )

        assert full.stat().st_size > bare.stat().st_size

    def test_reports_success_dialog_with_target(
        self,
        diagram: CanvasController,
        tmp_path: Path,
        message_boxes: dict[str, list[str]],
    ) -> None:
        target = tmp_path / "announced.pdf"

        PDFGenerator(diagram).export_to_pdf(filename=str(target))

        assert len(message_boxes["information"]) == 1
        assert str(target) in message_boxes["information"][0]

    def test_cancelled_save_dialog_returns_false(
        self, diagram: CanvasController, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """No filename and a cancelled dialog must not create a file."""
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: ("", ""))
        )

        result = PDFGenerator(diagram).export_to_pdf(filename=None)

        assert result is False
        assert list(tmp_path.iterdir()) == []

    def test_leaves_no_temporary_image_behind(
        self, diagram: CanvasController, tmp_path: Path
    ) -> None:
        """`_capture_canvas_image` writes into the repo root and must clean up."""
        temp_image = Path(__file__).resolve().parent.parent / "temp_diagram.png"

        PDFGenerator(diagram).export_to_pdf(filename=str(tmp_path / "clean.pdf"))

        assert not temp_image.exists()

    def test_empty_scene_still_produces_a_pdf(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        target = tmp_path / "empty.pdf"

        result = PDFGenerator(controller).export_to_pdf(filename=str(target))

        assert result is True
        assert target.read_bytes().startswith(PDF_MAGIC)


# ------------------------------------------------------------- agent reports


class TestAgentReportExport:
    def test_produces_one_image_per_entity(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        """Reports cover Actors and Agents only.

        `export_reports` filters on `isinstance(item, BaseNodeItem)`, which
        matches entities; Tropos elements sit on the sibling class
        `BaseTroposItem` and are never treated as report subjects.
        """
        for index, entity_type in enumerate(("actor", "agent")):
            make_node(controller, entity_type, index * 200, 0)
        make_node(controller, "hard_goal", 400, 0)

        output_dir = tmp_path / "reports"

        result = AgentReportExporter(controller).export_reports(str(output_dir))

        assert result is True
        assert len(list(output_dir.glob("*.png"))) == 2

    def test_tropos_elements_produce_no_report(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        for index, tropos_type in enumerate(
            ("hard_goal", "soft_goal", "plan", "resource")
        ):
            make_node(controller, tropos_type, index * 200, 0)

        output_dir = tmp_path / "reports"

        assert AgentReportExporter(controller).export_reports(str(output_dir)) is False
        assert not output_dir.exists()

    def test_images_are_valid_pngs(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        make_node(controller, "actor", 0, 0)

        output_dir = tmp_path / "reports"
        AgentReportExporter(controller).export_reports(str(output_dir))

        images = list(output_dir.glob("*.png"))
        assert images
        for image in images:
            assert image.read_bytes().startswith(PNG_MAGIC)
            assert image.stat().st_size > 0

    def test_filenames_carry_the_node_label(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        node = make_node(controller, "actor", 0, 0)
        node.model.label = "Editor jefe"

        output_dir = tmp_path / "reports"
        AgentReportExporter(controller).export_reports(str(output_dir))

        assert [p.name for p in output_dir.glob("*.png")] == [
            "agente_01_Editor jefe.png"
        ]

    def test_empty_scene_returns_false(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        output_dir = tmp_path / "reports"

        result = AgentReportExporter(controller).export_reports(str(output_dir))

        assert result is False
        assert not output_dir.exists()

    def test_visibility_is_restored_after_export(
        self, controller: CanvasController, tmp_path: Path
    ) -> None:
        """Items outside the exported agent's tree are hidden only temporarily."""
        make_node(controller, "actor", 0, 0)
        agent = make_node(controller, "agent", 300, 0)
        goal = make_node(controller, "hard_goal", 600, 0)

        AgentReportExporter(controller).export_reports(str(tmp_path / "reports"))

        assert goal.isVisible() is True
        assert agent.isVisible() is True
