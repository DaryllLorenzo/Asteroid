# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from typing import Any

from app.controller_types import CanvasNodeItem
from app.ui.components.base_edge_item import BaseEdgeItem


class AstrFormat:
    """
    Astr Format.

    Methods:
        serialize_scene: Serialize Scene.
    """

    @staticmethod
    def serialize_scene(
        nodes: list[CanvasNodeItem],
        edges: list[BaseEdgeItem],
    ) -> dict[str, Any]:
        """
        Serialize Scene.

        Args:
            nodes (list[CanvasNodeItem]): The nodes.
            edges (list[BaseEdgeItem]): The edges.

        Returns:
            dict[str, Any]: Serialize Scene.
        """
        scene_data = AstrFormat._create_scene_data_template(nodes, edges)
        node_id_map = AstrFormat._serialize_nodes(nodes, scene_data)
        AstrFormat._serialize_node_parent_ids(node_id_map, scene_data)
        AstrFormat._serialize_edges(edges, node_id_map, scene_data)
        return scene_data

    @staticmethod
    def _create_scene_data_template(
        nodes: list[CanvasNodeItem],
        edges: list[BaseEdgeItem],
    ) -> dict[str, Any]:
        """
        Create Scene Data Template.

        Args:
            nodes (list[CanvasNodeItem]): The nodes.
            edges (list[BaseEdgeItem]): The edges.

        Returns:
            dict[str, Any]: Create Scene Data Template.
        """
        return {
            "version": "1.4",
            "metadata": {
                "created_by": "Asteroid",
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
            "nodes": [],
            "edges": [],
        }

    @staticmethod
    def _serialize_nodes(
        nodes: list[CanvasNodeItem],
        scene_data: dict[str, Any],
    ) -> dict[CanvasNodeItem, int]:
        """
        Serialize Nodes.

        Args:
            nodes (list[CanvasNodeItem]): The nodes.
            scene_data (dict[str, Any]): The scene data.

        Returns:
            dict[CanvasNodeItem, int]: Serialize Nodes.
        """
        node_id_map: dict[CanvasNodeItem, int] = {}

        for idx, node in enumerate(nodes):
            node_data = AstrFormat._serialize_node(node, idx)
            node_id_map[node] = idx
            scene_data["nodes"].append(node_data)

        return node_id_map

    @staticmethod
    def _serialize_node_parent_ids(
        node_id_map: dict[CanvasNodeItem, int],
        scene_data: dict[str, Any],
    ) -> None:
        """
        Serialize Node Parent Ids.

        Args:
            node_id_map (dict[CanvasNodeItem, int]): The node id map.
            scene_data (dict[str, Any]): The scene data.
        """
        for node, node_id in node_id_map.items():
            if hasattr(node, "subcanvas_parent") and node.subcanvas_parent:
                parent_node = node.subcanvas_parent.parentItem()
                if parent_node in node_id_map:
                    scene_data["nodes"][node_id]["parent_id"] = node_id_map[parent_node]

    @staticmethod
    def _serialize_edges(
        edges: list[BaseEdgeItem],
        node_id_map: dict[CanvasNodeItem, int],
        scene_data: dict[str, Any],
    ) -> None:
        """
        Serialize Edges.

        Args:
            edges (list[BaseEdgeItem]): The edges.
            node_id_map (dict[CanvasNodeItem, int]): The node id map.
            scene_data (dict[str, Any]): The scene data.
        """
        for edge in edges:
            edge_data = AstrFormat._serialize_edge(edge, node_id_map)
            if edge_data:
                parent_item = edge.parentItem() if hasattr(edge, "parentItem") else None
                if parent_item and hasattr(parent_item, "subnode_dropped"):
                    parent_node = parent_item.parentItem()
                    if parent_node in node_id_map:
                        edge_data["parent_id"] = node_id_map[parent_node]
                scene_data["edges"].append(edge_data)

    @staticmethod
    def _serialize_node(node, node_id: int) -> dict[str, Any]:
        """
        Serialize Node.

        Args:
            node: The node.
            node_id (int): The node id.

        Returns:
            dict[str, Any]: Serialize Node.
        """
        pos = node.pos()
        node_data = {
            "id": node_id,
            "type": AstrFormat._get_node_type(node),
            "position": {"x": float(pos.x()), "y": float(pos.y())},
            "properties": {},
            "parent_id": None,
        }

        # Get properties serializables (includes the new text_width y align)
        try:
            if hasattr(node, "get_serializable_properties") and callable(
                node.get_serializable_properties
            ):
                node_data["properties"] = node.get_serializable_properties()
            else:
                # Fallback basic
                node_data["properties"] = {
                    "radius": getattr(node.model, "radius", 40),
                    "label": getattr(node.model, "label", ""),
                    "text_width": getattr(node.model, "text_width", 150),
                    "text_align": getattr(node.model, "text_align", "center"),
                }
        except Exception as e:
            print(f"Error serializando propiedades: {e}")
            node_data["properties"] = {}

        # Information of the subcanvas
        if hasattr(node, "subcanvas") and node.subcanvas:
            node_data["subcanvas"] = {
                "visible": getattr(node, "_subcanvas_visible", False),
                "radius": float(node.subcanvas.radius),
                "original_radius": float(
                    getattr(node.subcanvas, "original_radius", node.subcanvas.radius)
                ),
            }

        # Information of the model completa
        if hasattr(node, "model"):
            # If es a CompositeModelWrapper, save information of both modelos
            if hasattr(node.model, "get_internal_model"):
                internal_model = node.model.get_internal_model()
                node_data["model_properties"] = {
                    "show_subcanvas": getattr(node.model, "show_subcanvas", False),
                    "x": float(getattr(node.model, "x", 0)),
                    "y": float(getattr(node.model, "y", 0)),
                    "radius": float(getattr(node.model, "radius", 50)),
                    "label": getattr(node.model, "label", ""),
                    "color": getattr(node.model, "color", "#3498db"),
                    "border_color": getattr(node.model, "border_color", "#2980b9"),
                    "text_color": getattr(node.model, "text_color", "#ffffff"),
                    # Position in subcanvas (of the model internal)
                    "internal_position_in_subcanvas_x": float(
                        getattr(internal_model, "position_in_subcanvas_x", 0.0)
                    ),
                    "internal_position_in_subcanvas_y": float(
                        getattr(internal_model, "position_in_subcanvas_y", 0.0)
                    ),
                    # Position in subcanvas (of the model external also)
                    "position_in_subcanvas_x": float(
                        getattr(node.model, "position_in_subcanvas_x", 0.0)
                    ),
                    "position_in_subcanvas_y": float(
                        getattr(node.model, "position_in_subcanvas_y", 0.0)
                    ),
                    "content_offset_x": float(
                        getattr(node.model, "content_offset_x", 0.0)
                    ),
                    "content_offset_y": float(
                        getattr(node.model, "content_offset_y", 0.0)
                    ),
                    "text_width": float(getattr(node.model, "text_width", 150)),
                    "text_align": getattr(node.model, "text_align", "center"),
                    # Mark as node composite
                    "is_composite": True,
                }
            else:
                # Node normal (no composite)
                node_data["model_properties"] = {
                    "show_subcanvas": getattr(node.model, "show_subcanvas", False),
                    "x": float(getattr(node.model, "x", 0)),
                    "y": float(getattr(node.model, "y", 0)),
                    "radius": float(getattr(node.model, "radius", 50)),
                    "label": getattr(node.model, "label", ""),
                    "color": getattr(node.model, "color", "#3498db"),
                    "border_color": getattr(node.model, "border_color", "#2980b9"),
                    "text_color": getattr(node.model, "text_color", "#ffffff"),
                    # Position in subcanvas
                    "position_in_subcanvas_x": float(
                        getattr(node.model, "position_in_subcanvas_x", 0.0)
                    ),
                    "position_in_subcanvas_y": float(
                        getattr(node.model, "position_in_subcanvas_y", 0.0)
                    ),
                    "content_offset_x": float(
                        getattr(node.model, "content_offset_x", 0.0)
                    ),
                    "content_offset_y": float(
                        getattr(node.model, "content_offset_y", 0.0)
                    ),
                    "text_width": float(getattr(node.model, "text_width", 150)),
                    "text_align": getattr(node.model, "text_align", "center"),
                }

        return node_data

    @staticmethod
    def _serialize_edge(
        edge: BaseEdgeItem,
        node_id_map: dict[CanvasNodeItem, int],
    ) -> dict[str, Any] | None:
        """
        Serialize Edge.

        Args:
            edge (BaseEdgeItem): The edge.
            node_id_map (dict[CanvasNodeItem, int]): The node id map.

        Returns:
            dict[str, Any] | None: Serialize Edge.
        """
        if edge.source_node not in node_id_map or edge.dest_node not in node_id_map:
            return None

        edge_data: dict[str, Any] = {
            "type": AstrFormat._get_edge_type(edge),
            "source_id": node_id_map.get(edge.source_node, -1),
            "target_id": node_id_map.get(edge.dest_node, -1),
            "properties": {},
            "parent_id": None,
            "control_points": [],
        }

        # Serialize control points if existen
        if hasattr(edge, "control_points") and edge.control_points:
            for point in edge.control_points:
                edge_data["control_points"].append(
                    {"x": float(point.x()), "y": float(point.y())}
                )

        try:
            if hasattr(edge, "get_serializable_properties") and callable(
                edge.get_serializable_properties
            ):
                edge_data["properties"] = edge.get_serializable_properties()
        except Exception:
            pass

        return edge_data

    @staticmethod
    def _get_node_type(node) -> str:
        """
        Get Node Type.

        Args:
            node: The node.

        Returns:
            str: Get Node Type.
        """
        node_type_map = {
            "ActorNodeItem": "actor",
            "AgentNodeItem": "agent",
            "HardGoalNodeItem": "hard_goal",
            "SoftGoalNodeItem": "soft_goal",
            "PlanNodeItem": "plan",
            "ResourceNodeItem": "resource",
        }
        return node_type_map.get(node.__class__.__name__, "unknown")

    @staticmethod
    def _get_edge_type(edge) -> str:
        """
        Get Edge Type.

        Args:
            edge: The edge.

        Returns:
            str: Get Edge Type.
        """
        edge_type_map = {
            "SimpleArrowItem": "simple",
            "DashedArrowItem": "dashed",
            "DependencyLinkArrowItem": "dependency_link",
            "WhyLinkArrowItem": "why_link",
            "OrDecompositionArrowItem": "or_decomposition",
            "AndDecompositionArrowItem": "and_decomposition",
            "ContributionArrowItem": "contribution",
            "MeansEndArrowItem": "means_end",
        }
        return edge_type_map.get(edge.__class__.__name__, "unknown")
