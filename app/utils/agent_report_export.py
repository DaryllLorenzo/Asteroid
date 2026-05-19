from __future__ import annotations

import os
import re

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtGui import QImage
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtWidgets import QGraphicsSimpleTextItem

from app.controllers.canvas_controller import CanvasController
from app.i18n import tr
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.dependency_item.and_decomposition_edge_item import (
    AndDecompositionArrowItem,
)
from app.ui.components.dependency_item.contribution_edge_item import (
    ContributionArrowItem,
)
from app.ui.components.dependency_item.dependency_link_edge_item import (
    DependencyLinkArrowItem,
)
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import (
    OrDecompositionArrowItem,
)
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem

EDGE_DISPLAY_NAMES: dict[type[BaseEdgeItem], str] = {
    MeansEndArrowItem: "Means-End",
    DependencyLinkArrowItem: "Dependency",
    ContributionArrowItem: "Contribution",
    OrDecompositionArrowItem: "OR Decomposition",
    AndDecompositionArrowItem: "AND Decomposition",
    WhyLinkArrowItem: "Why",
}


class RelationshipInfo:
    def __init__(
        self,
        direction: str,
        edge_type_display: str,
        external_label: str,
        owning_agent_label: str | None,
    ) -> None:
        self.direction = direction
        self.edge_type_display = edge_type_display
        self.external_label = external_label
        self.owning_agent_label = owning_agent_label


class AgentReportExporter:
    def __init__(self, controller: CanvasController) -> None:
        self.controller = controller

    def export_reports(self, output_dir: str) -> bool:
        scene = self.controller.canvas.scene()
        if not scene:
            return False

        all_items = scene.items()
        all_edges = self.controller.edges

        top_agents: list[BaseNodeItem] = [
            item
            for item in all_items
            if isinstance(item, BaseNodeItem) and item.subcanvas_parent is None
        ]
        if not top_agents:
            return False

        os.makedirs(output_dir, exist_ok=True)

        for i, agent in enumerate(top_agents, 1):
            tree_set = self._collect_tree_set(agent)
            relationships = self._get_relationships(agent, tree_set, all_edges)

            saved_visibility: dict[QGraphicsItem, bool] = {}
            for item in all_items:
                if item not in tree_set:
                    saved_visibility[item] = item.isVisible()
                    item.setVisible(False)

            agent.ensure_subcanvas_visible()

            agent_rect = self._agent_visual_rect(agent, tree_set)
            panel_x = agent_rect.right() + 60
            panel_y = agent_rect.top()

            annotations = self._add_annotation_panel(
                agent, relationships, scene, panel_x, panel_y
            )

            agent_br = agent_rect.adjusted(-60, -60, 60, 60)
            annotations_br = self._annotations_rect(annotations)
            total_rect = agent_br.united(annotations_br)

            scale = 2
            iw = max(1, int(total_rect.width() * scale))
            ih = max(1, int(total_rect.height() * scale))
            image = QImage(iw, ih, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.white)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            tw = total_rect.width() * scale
            th = total_rect.height() * scale
            target_rect = QRectF(0, 0, tw, th)
            scene.render(painter, target_rect, total_rect)
            painter.end()

            name = self._sanitize_name(str(agent.model.label))
            filename = f"agente_{i:02d}_{name}.png"
            image.save(os.path.join(output_dir, filename))

            for ann in annotations:
                scene.removeItem(ann)

            for item, visible in saved_visibility.items():
                item.setVisible(visible)

        return True

    def _collect_tree_set(self, root: BaseNodeItem) -> set[QGraphicsItem]:
        items: set[QGraphicsItem] = set()

        def collect(item: QGraphicsItem) -> None:
            if item in items:
                return
            items.add(item)
            for child in item.childItems():
                collect(child)

        collect(root)
        return items

    def _get_owning_agent(self, item: object) -> BaseNodeItem | None:
        if isinstance(item, BaseNodeItem) and item.subcanvas_parent is None:
            return item
        if hasattr(item, "subcanvas_parent") and item.subcanvas_parent is not None:
            sc = item.subcanvas_parent
            p = sc.parentItem()
            if isinstance(p, BaseNodeItem):
                return p
        return None

    def _trace_forward_to_agent(
        self,
        from_node: object,
        all_edges: list[BaseEdgeItem],
        visited: set[int] | None = None,
    ) -> str | None:
        if visited is None:
            visited = set()
        if id(from_node) in visited:
            return None
        visited.add(id(from_node))

        owning = self._get_owning_agent(from_node)
        if owning:
            return self._get_node_label(owning)

        for edge in all_edges:
            if edge.source_node is from_node:
                result = self._trace_forward_to_agent(
                    edge.dest_node, all_edges, visited
                )
                if result:
                    return result
        return None

    def _trace_backward_to_agent(
        self,
        from_node: object,
        all_edges: list[BaseEdgeItem],
        visited: set[int] | None = None,
    ) -> str | None:
        if visited is None:
            visited = set()
        if id(from_node) in visited:
            return None
        visited.add(id(from_node))

        owning = self._get_owning_agent(from_node)
        if owning:
            return self._get_node_label(owning)

        for edge in all_edges:
            if edge.dest_node is from_node:
                result = self._trace_backward_to_agent(
                    edge.source_node, all_edges, visited
                )
                if result:
                    return result
        return None

    def _get_relationships(
        self,
        agent: BaseNodeItem,
        tree_set: set[QGraphicsItem],
        all_edges: list[BaseEdgeItem],
    ) -> list[RelationshipInfo]:
        rels: list[RelationshipInfo] = []
        for edge in all_edges:
            source_in = edge.source_node in tree_set
            dest_in = edge.dest_node in tree_set

            if source_in and not dest_in:
                external = edge.dest_node
                ext_label = self._get_node_label(external)
                edge_key = EDGE_DISPLAY_NAMES.get(
                    type(edge), self._get_edge_class_name(edge)
                )
                edge_display = tr(edge_key)
                owning = self._get_owning_agent(external)
                owner_label = self._get_node_label(owning) if owning else None
                if not owner_label:
                    owner_label = self._trace_forward_to_agent(external, all_edges)
                rels.append(
                    RelationshipInfo("outgoing", edge_display, ext_label, owner_label)
                )
            elif not source_in and dest_in:
                external = edge.source_node
                ext_label = self._get_node_label(external)
                edge_key = EDGE_DISPLAY_NAMES.get(
                    type(edge), self._get_edge_class_name(edge)
                )
                edge_display = tr(edge_key)
                owning = self._get_owning_agent(external)
                owner_label = self._get_node_label(owning) if owning else None
                if not owner_label:
                    owner_label = self._trace_backward_to_agent(external, all_edges)
                rels.append(
                    RelationshipInfo("incoming", edge_display, ext_label, owner_label)
                )

        return rels

    def _get_node_label(self, item: object) -> str:
        if item is None:
            return ""
        if hasattr(item, "model") and hasattr(item.model, "label"):
            return str(item.model.label).replace("\n", " ")
        return "?"

    def _get_edge_class_name(self, edge: BaseEdgeItem) -> str:
        return type(edge).__name__.replace("ArrowItem", "").replace("EdgeItem", "")

    def _agent_visual_rect(
        self, agent: BaseNodeItem, tree_set: set[QGraphicsItem]
    ) -> QRectF:
        rect = QRectF()
        for item in tree_set:
            try:
                r = item.sceneBoundingRect()
                rect = rect.united(r) if not rect.isEmpty() else r
            except RuntimeError:
                pass
        if rect.isEmpty():
            radius = float(getattr(agent.model, "radius", 50))
            p = agent.scenePos()
            rect = QRectF(p.x() - radius, p.y() - radius, 2 * radius, 2 * radius)
        return rect

    def _annotations_rect(self, annotations: list[QGraphicsItem]) -> QRectF:
        rect = QRectF()
        for ann in annotations:
            try:
                r = ann.sceneBoundingRect()
                rect = rect.united(r) if not rect.isEmpty() else r
            except RuntimeError:
                pass
        if rect.isEmpty():
            rect = QRectF(0, 0, 1, 1)
        return rect

    def _add_annotation_panel(
        self,
        agent: BaseNodeItem,
        relationships: list[RelationshipInfo],
        scene: QGraphicsScene,
        panel_x: float,
        panel_y: float,
    ) -> list[QGraphicsItem]:
        annotations: list[QGraphicsItem] = []
        lh = 26
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        sec_font = QFont("Arial", 14, QFont.Weight.Bold)
        text_font = QFont("Arial", 13)
        small_font = QFont("Arial", 11)

        rows: list[tuple[str, QFont, QColor]] = []

        raw_label = str(getattr(agent.model, "label", tr("Agent"))).replace("\n", " ")
        rows.append((raw_label, title_font, QColor("#c64600")))
        rows.append(("", text_font, QColor(0, 0, 0)))

        outgoing = [r for r in relationships if r.direction == "outgoing"]
        incoming = [r for r in relationships if r.direction == "incoming"]

        if outgoing:
            out_header = f"--- {tr('Outgoing')} ---"
            rows.append((out_header, sec_font, QColor("#c64600")))
            for r in outgoing:
                agent_tag = (
                    f"  [{tr('towards')} {r.owning_agent_label}]"
                    if r.owning_agent_label
                    else ""
                )
                text = f"  \u2192  {r.external_label}{agent_tag}"
                rows.append((text, text_font, QColor("#333")))
                edge_line = f"       ({r.edge_type_display})"
                rows.append((edge_line, small_font, QColor(130, 130, 130)))

        if outgoing and incoming:
            rows.append(("", text_font, QColor(0, 0, 0)))

        if incoming:
            in_header = f"--- {tr('Incoming')} ---"
            rows.append((in_header, sec_font, QColor("#1a5fb4")))
            for r in incoming:
                agent_tag = (
                    f"  [{tr('from')} {r.owning_agent_label}]"
                    if r.owning_agent_label
                    else ""
                )
                text = f"  \u2190  {r.external_label}{agent_tag}"
                rows.append((text, text_font, QColor("#333")))
                edge_line = f"       ({r.edge_type_display})"
                rows.append((edge_line, small_font, QColor(130, 130, 130)))

        if not outgoing and not incoming:
            rows.append((tr("(No relationships)"), small_font, QColor(150, 150, 150)))

        font_metrics = {
            title_font: QFontMetrics(title_font),
            sec_font: QFontMetrics(sec_font),
            text_font: QFontMetrics(text_font),
            small_font: QFontMetrics(small_font),
        }
        max_text_width = 0
        for text, font, _ in rows:
            if not text:
                continue
            fm = font_metrics[font]
            tw = fm.horizontalAdvance(text)
            if tw > max_text_width:
                max_text_width = tw

        panel_w = max(max_text_width + 28, 380)

        panel_h = sum(lh if txt else lh * 0.4 for txt, _, _ in rows) + 30

        bg = QGraphicsRectItem(panel_x, panel_y, panel_w, panel_h)
        bg.setBrush(QBrush(QColor(248, 248, 248)))
        bg.setPen(QPen(QColor(210, 210, 210), 1))
        scene.addItem(bg)
        annotations.append(bg)

        y = panel_y + 15
        for text, font, color in rows:
            if not text:
                y += lh * 0.4
                continue
            item = QGraphicsSimpleTextItem(text)
            item.setFont(font)
            item.setBrush(QBrush(color))
            item.setPos(panel_x + 14, y)
            scene.addItem(item)
            annotations.append(item)
            if "---" in text:
                y += lh * 0.7
            else:
                y += lh

        return annotations

    @staticmethod
    def _sanitize_name(name: str) -> str:
        name = re.sub(r"[\\/:*?\"<>|\n]", "_", name)
        name = name.strip("_. ")
        if not name:
            name = "agente"
        # Collapse multiple spaces/underscores
        name = re.sub(r"\s+", " ", name)
        name = re.sub(r"_+", "_", name)
        return name[:60]
