# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from typing import Any


class AstrFormat:
    @staticmethod
    def serialize_scene(nodes, edges):
        scene_data = AstrFormat._create_scene_data_template(nodes, edges)
        AstrFormat._serialize_nodes(nodes, scene_data)
        AstrFormat._serialize_node_parent_ids(nodes, scene_data)
        AstrFormat._serialize_edges(edges, scene_data)
        return scene_data

    @staticmethod
    def _create_scene_data_template(nodes, edges):
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
    def _serialize_nodes(nodes, scene_data):
        serialized_nodes = set()
        node_id_map = {}
        idx = 0

        for node in nodes:
            if hasattr(node, "model") and hasattr(node.model, "get_external_model"):
                external_model = node.model.get_external_model()
                if external_model in serialized_nodes:
                    continue

            node_data = AstrFormat._serialize_node(node, idx)
            node_id_map[node] = idx
            serialized_nodes.add(id(node.model) if hasattr(node, "model") else idx)
            scene_data["nodes"].append(node_data)
            idx += 1

    @staticmethod
    def _serialize_edges(edges, scene_data):
        for edge in edges:
            edge_data = AstrFormat._serialize_edge(edge, {})
            if edge_data:
                scene_data["edges"].append(edge_data)

    @staticmethod
    def _serialize_node(node, node_id: int) -> dict[str, Any]:
        """Serializa un nodo individual"""
        pos = node.pos()
        node_data = {
            "id": node_id,
            "type": AstrFormat._get_node_type(node),
            "position": {"x": float(pos.x()), "y": float(pos.y())},
            "properties": {},
            "parent_id": None,
        }

        # Obtener propiedades serializables (incluye los nuevos text_width y align)
        try:
            if hasattr(node, "get_serializable_properties") and callable(
                node.get_serializable_properties
            ):
                node_data["properties"] = node.get_serializable_properties()
            else:
                # Fallback básico
                node_data["properties"] = {
                    "radius": getattr(node.model, "radius", 40),
                    "label": getattr(node.model, "label", ""),
                    "text_width": getattr(node.model, "text_width", 150),
                    "text_align": getattr(node.model, "text_align", "center"),
                }
        except Exception as e:
            print(f"Error serializando propiedades: {e}")
            node_data["properties"] = {}

        # Información del subcanvas
        if hasattr(node, "subcanvas") and node.subcanvas:
            node_data["subcanvas"] = {
                "visible": getattr(node, "_subcanvas_visible", False),
                "radius": float(node.subcanvas.radius),
                "original_radius": float(
                    getattr(node.subcanvas, "original_radius", node.subcanvas.radius)
                ),
            }

        # Información del modelo completa
        if hasattr(node, "model"):
            # Si es un CompositeModelWrapper, guardar información de ambos modelos
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
                    # Posición en subcanvas (del modelo interno)
                    "internal_position_in_subcanvas_x": float(
                        getattr(internal_model, "position_in_subcanvas_x", 0.0)
                    ),
                    "internal_position_in_subcanvas_y": float(
                        getattr(internal_model, "position_in_subcanvas_y", 0.0)
                    ),
                    # Posición en subcanvas (del modelo externo también)
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
                    # Marcar como nodo composite
                    "is_composite": True,
                }
            else:
                # Nodo normal (no composite)
                node_data["model_properties"] = {
                    "show_subcanvas": getattr(node.model, "show_subcanvas", False),
                    "x": float(getattr(node.model, "x", 0)),
                    "y": float(getattr(node.model, "y", 0)),
                    "radius": float(getattr(node.model, "radius", 50)),
                    "label": getattr(node.model, "label", ""),
                    "color": getattr(node.model, "color", "#3498db"),
                    "border_color": getattr(node.model, "border_color", "#2980b9"),
                    "text_color": getattr(node.model, "text_color", "#ffffff"),
                    # Posición en subcanvas
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
    def _serialize_edge(edge, node_id_map: dict) -> dict[str, Any]:
        """Serializa una edge individual"""
        if edge.source_node not in node_id_map or edge.dest_node not in node_id_map:
            return None

        edge_data = {
            "type": AstrFormat._get_edge_type(edge),
            "source_id": node_id_map.get(edge.source_node, -1),
            "target_id": node_id_map.get(edge.dest_node, -1),
            "properties": {},
            "parent_id": None,
            "control_points": [],
        }

        # Serializar control points si existen
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
        """Obtiene el tipo de nodo como string"""
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
        """Obtiene el tipo de edge como string"""
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
