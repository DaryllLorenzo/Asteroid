# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

import logging
import os
from pathlib import Path

from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.units import inch
from reportlab.platypus import Image
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle

from app.i18n import tr

logger = logging.getLogger(__name__)


class PDFGenerator:
    def __init__(self, canvas_controller):
        self.canvas_controller = canvas_controller

    def export_to_pdf(
        self,
        with_additional_info: bool = True,
        filename: str | None = None,
    ) -> bool:
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas_controller.canvas,
                    "Exportar a PDF",
                    "",
                    "PDF Files (*.pdf)",
                )
                if not filename:
                    return False

                if not filename.endswith(".pdf"):
                    filename += ".pdf"

            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=30,
                alignment=TA_CENTER,
            )
            story.append(Paragraph("Diagrama Asteroid", title_style))
            story.append(Spacer(1, 0.3 * inch))

            diagram_image = self._capture_canvas_image()
            if diagram_image:
                img = Image(diagram_image, width=6 * inch, height=4 * inch)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 0.5 * inch))

            if with_additional_info:
                story.append(PageBreak())
                self._add_additional_info(story, styles)

            doc.build(story)

            QMessageBox.information(
                self.canvas_controller.canvas,
                tr("Export completed"),
                f"{tr('PDF exported successfully')}:\n{filename}",
            )
            if diagram_image:
                os.remove(diagram_image)

            return True

        except Exception as e:
            logger.exception("Error exporting PDF")
            QMessageBox.critical(
                self.canvas_controller.canvas,
                "Error",
                f"No se pudo exportar el PDF:\n{e}",
            )
            return False

    def _capture_canvas_image(self) -> str | None:
        try:
            canvas = self.canvas_controller.canvas

            scene = canvas.scene()
            if scene is None:
                return None

            scene_rect = scene.itemsBoundingRect()
            # Extra margin so subcanvas circles near the edge aren't clipped.
            margin = 50.0
            expanded_rect = scene_rect.adjusted(-margin, -margin, margin, margin)

            pixmap = QPixmap(int(expanded_rect.width()), int(expanded_rect.height()))
            pixmap.fill(QColor(255, 255, 255))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            scene.render(painter, source=expanded_rect)
            painter.end()

            temp_path = Path(__file__).parent.parent.parent / "temp_diagram.png"
            pixmap.save(str(temp_path), "PNG")

            return str(temp_path)

        except Exception:
            logger.exception("Error capturing canvas image")
            return None

    def _add_additional_info(self, story: list, styles):
        section_style = ParagraphStyle(
            "CustomSection",
            parent=styles["Heading2"],
            fontSize=18,
            textColor=colors.HexColor("#34495E"),
            spaceAfter=20,
            spaceBefore=10,
        )

        story.append(Paragraph("Elementos del Diagrama", section_style))
        self._add_elements_table(story, styles)

        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("Relaciones entre Elementos", section_style))
        self._add_relationships_table(story, styles)

    def _add_elements_table(self, story: list, styles):
        nodes = self.canvas_controller.nodes

        data = [["ID", "Tipo", "Nombre/Label"]]

        for idx, node in enumerate(nodes, 1):
            node_type = self._get_node_type_display(node)
            label = self._get_node_label(node)
            data.append([str(idx), node_type, label])

        table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 3.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#2C3E50")),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F8F9FA")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#BDC3C7")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)

    def _add_relationships_table(self, story: list, styles):
        edges = self.canvas_controller.edges

        data = [["Origen", "Tipo de Relación", "Destino"]]

        for edge in edges:
            source_label = self._get_node_label(edge.source_node)
            target_label = self._get_node_label(edge.dest_node)
            edge_type = self._get_edge_type_display(edge)
            data.append([source_label, edge_type, target_label])

        table = Table(data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#2C3E50")),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F8F9FA")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#BDC3C7")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)

    def _get_node_type_display(self, node) -> str:
        type_map = {
            "ActorNodeItem": "Actor",
            "AgentNodeItem": "Agente",
            "HardGoalNodeItem": "Meta Dura",
            "SoftGoalNodeItem": "Meta Blanda",
            "PlanNodeItem": "Plan",
            "ResourceNodeItem": "Recurso",
        }
        return type_map.get(node.__class__.__name__, "Desconocido")

    def _get_node_label(self, node) -> str:
        if hasattr(node, "model") and hasattr(node.model, "label"):
            return str(node.model.label)
        elif hasattr(node, "label"):
            return str(node.label)
        return "Sin nombre"

    def _get_edge_type_display(self, edge) -> str:
        type_map = {
            "SimpleArrowItem": "Conexión Simple",
            "DashedArrowItem": "Conexión Punteada",
            "DependencyLinkArrowItem": "Dependencia",
            "WhyLinkArrowItem": "Por qué",
            "OrDecompositionArrowItem": "Descomposición OR",
            "AndDecompositionArrowItem": "Descomposición AND",
            "ContributionArrowItem": "Contribución",
            "MeansEndArrowItem": "Medio-Fin",
        }
        return type_map.get(edge.__class__.__name__, "Relación")
