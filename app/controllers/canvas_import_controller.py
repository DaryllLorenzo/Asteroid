# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
import json
from typing import TypedDict
from typing import cast

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox

from app.controller_types import CanvasNodeItem
from app.controllers._canvas_mixin import CanvasControllerMixin
from app.controllers.canvas_registry_controller import _ARROW_TYPES
from app.controllers.canvas_registry_controller import _MODEL_MAP
from app.controllers.canvas_registry_controller import _NODE_MAP
from app.core.models.composite_model_wrapper import CompositeModelWrapper
from app.i18n import tr
from app.model_types import PropertyMap
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.base_node_item import BaseNodeItem
from app.ui.components.base_tropos_item import BaseTroposItem


class PositionData(TypedDict):
    """
    Position Data.

    Attributes:
        x (float): x.
        y (float): y.
    """

    x: float
    y: float


class SerializedSubcanvasData(TypedDict, total=False):
    """
    Serialized Subcanvas Data.

    Attributes:
        visible (bool): visible.
        radius (float): radius.
        original_radius (float): original radius.
    """

    visible: bool
    radius: float
    original_radius: float


class SerializedNodeData(TypedDict, total=False):
    """
    Serialized Node Data.

    Attributes:
        id (int): id.
        type (str): type.
        position (PositionData): position.
        properties (dict[str, object]): properties.
        parent_id (int | None): parent id.
        model_properties (dict[str, object]): model properties.
        subcanvas (SerializedSubcanvasData): subcanvas.
    """

    id: int
    type: str
    position: PositionData
    properties: dict[str, object]
    parent_id: int | None
    model_properties: dict[str, object]
    subcanvas: SerializedSubcanvasData


class SerializedEdgeData(TypedDict, total=False):
    """
    Serialized Edge Data.

    Attributes:
        type (str): type.
        source_id (int): source id.
        target_id (int): target id.
        properties (dict[str, object]): properties.
        parent_id (int | None): parent id.
        control_points (list[PositionData]): control points.
    """

    type: str
    source_id: int
    target_id: int
    properties: dict[str, object]
    parent_id: int | None
    control_points: list[PositionData]


class SerializedSceneData(TypedDict):
    """
    Serialized Scene Data.

    Attributes:
        nodes (list[SerializedNodeData]): nodes.
        edges (list[SerializedEdgeData]): edges.
    """

    nodes: list[SerializedNodeData]
    edges: list[SerializedEdgeData]


def _as_float(value: object, default: float) -> float:
    """
    As Float.

    Args:
        value (object): The value.
        default (float): The default.

    Returns:
        float: As Float.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


class CanvasImportController(CanvasControllerMixin):
    """
    Canvas Import Controller.

    Methods:
        import_from_astr: Import From Astr.
    """

    def import_from_astr(
        self,
        filename: str | None = None,
    ) -> bool:
        """
        Import From Astr.

        Args:
            filename (str | None): The filename.

        Returns:
            bool: Import From Astr.
        """
        try:
            if not filename:
                filename, _ = QFileDialog.getOpenFileName(
                    self.canvas,
                    tr("Load .astr project"),
                    "",
                    tr("Asteroid Files (*.astr)"),
                )
                if not filename:
                    return False

            print(f"Loading project from: {filename}")

            with open(filename, encoding="utf-8") as file:
                scene_data = cast(SerializedSceneData, json.load(file))

            print(
                f"Project contains: {len(scene_data.get('nodes', []))} nodes, "
                f"{len(scene_data.get('edges', []))} edges"
            )

            self.clear_canvas()

            node_map: dict[int, CanvasNodeItem] = {}
            parent_child_map: dict[int, list[int]] = {}

            for node_data in scene_data.get("nodes", []):
                print(f"Processing node {node_data['id']} of type {node_data['type']}")
                node = self._create_node_from_data(node_data)
                if node:
                    node_map[node_data["id"]] = node
                    parent_id = node_data.get("parent_id")
                    if parent_id is not None:
                        if parent_id not in parent_child_map:
                            parent_child_map[parent_id] = []
                        parent_child_map[parent_id].append(node_data["id"])

            for parent_id, child_ids in parent_child_map.items():
                parent_node = node_map.get(parent_id)
                if isinstance(parent_node, BaseNodeItem):
                    print(
                        f"Moving {len(child_ids)} nodes to subcanvas "
                        f"of node {parent_id}"
                    )
                    for child_id in child_ids:
                        child_node = node_map.get(child_id)
                        if child_node:
                            self._move_node_to_subcanvas(child_node, parent_node)

            edge_count = 0
            edge_parent_map = {}

            for edge_data in scene_data.get("edges", []):
                edge = self._create_edge_from_data(edge_data, node_map)
                if edge:
                    edge_count += 1
                    parent_id = edge_data.get("parent_id")
                    if parent_id is not None:
                        edge_parent_map[edge] = parent_id

            for edge, parent_id in edge_parent_map.items():
                parent_node = node_map.get(parent_id)
                if isinstance(parent_node, BaseNodeItem):
                    self._move_edge_to_subcanvas(edge, parent_node)

            composite_nodes: dict[int, SerializedNodeData] = {}
            for node_data in scene_data.get("nodes", []):
                model_props = node_data.get("model_properties", {})
                if bool(model_props.get("is_composite", False)):
                    parent_id = node_data.get("parent_id")
                    if parent_id is None:
                        composite_nodes[node_data["id"]] = node_data

            linked_internal_nodes = set()

            for node_id, node_data in composite_nodes.items():
                external_node = node_map.get(node_id)
                if not external_node:
                    continue

                model_props = node_data.get("model_properties", {})
                target_node = None
                for edge in self.edges:
                    if edge.source_node == external_node:
                        target_node = edge.dest_node
                        break

                if not target_node:
                    print(f"No outgoing edge found for composite node {node_id}")
                    continue

                if isinstance(target_node, BaseNodeItem) and target_node.subcanvas:
                    internal_node = None
                    expected_x = target_node.subcanvas.radius * _as_float(
                        model_props.get("internal_position_in_subcanvas_x", 0.6),
                        0.6,
                    )
                    expected_y = target_node.subcanvas.radius * _as_float(
                        model_props.get("internal_position_in_subcanvas_y", 0.0),
                        0.0,
                    )

                    candidates = []
                    for child in target_node.subcanvas.childItems():
                        if id(child) in linked_internal_nodes:
                            continue
                        if isinstance(child, type(external_node)) and hasattr(
                            child, "model"
                        ):
                            candidates.append(child)

                    if len(candidates) == 1:
                        internal_node = candidates[0]
                    elif len(candidates) > 1:
                        min_dist = float("inf")
                        for candidate in candidates:
                            dist = abs(candidate.pos().x() - expected_x) + abs(
                                candidate.pos().y() - expected_y
                            )
                            if dist < min_dist:
                                min_dist = dist
                                internal_node = candidate
                    else:
                        print(
                            f"No internal nodes of type "
                            f"{type(external_node).__name__} found in "
                            f"subcanvas of {target_node}"
                        )

                    if internal_node:
                        linked_internal_nodes.add(id(internal_node))
                        ModelClass = _MODEL_MAP.get(node_data["type"])
                        if ModelClass:
                            internal_radius = (
                                internal_node._independent_model.radius
                                if internal_node._independent_model
                                else getattr(internal_node.model, "radius", 50)
                            )

                            new_internal_model = ModelClass(0, 0)
                            new_internal_model.position_in_subcanvas_x = _as_float(
                                model_props.get(
                                    "internal_position_in_subcanvas_x",
                                    0.6,
                                ),
                                0.6,
                            )
                            new_internal_model.position_in_subcanvas_y = _as_float(
                                model_props.get(
                                    "internal_position_in_subcanvas_y",
                                    0.0,
                                ),
                                0.0,
                            )
                            new_internal_model.radius = internal_radius

                            external_model = external_node.model
                            wrapper = CompositeModelWrapper(
                                external_model, new_internal_model
                            )

                            external_node.model = wrapper
                            external_node._independent_model = external_model
                            internal_node.model = wrapper
                            internal_node._independent_model = new_internal_model

                            wrapper.label = str(model_props.get("label", ""))
                            wrapper.color = str(model_props.get("color", "#3498db"))
                            wrapper.border_color = str(
                                model_props.get("border_color", "#2980b9")
                            )
                            wrapper.text_color = str(
                                model_props.get("text_color", "#ffffff")
                            )

                            external_model.radius = _as_float(
                                model_props.get("radius", 50),
                                50.0,
                            )

                            external_node.update()
                            internal_node.update()

                            def on_external_changed(
                                prop_name: str,
                                value: object,
                                node: BaseNodeItem | BaseTroposItem = external_node,
                            ) -> None:
                                """
                                On External Changed.

                                Args:
                                    prop_name (str): The prop name.
                                    value (object): The value.
                                    node (BaseNodeItem | BaseTroposItem): The node.
                                """
                                node.update()
                                node.properties_changed.emit(node, {prop_name: value})

                            def on_internal_changed(
                                prop_name: str,
                                value: object,
                                node: CanvasNodeItem = internal_node,
                            ) -> None:
                                """
                                On Internal Changed.

                                Args:
                                    prop_name (str): The prop name.
                                    value (object): The value.
                                    node (CanvasNodeItem): The node.
                                """
                                del prop_name, value
                                node.update()

                            wrapper.add_change_callback(on_external_changed)
                            wrapper.add_change_callback(on_internal_changed)
                    else:
                        print(f"No internal node found in subcanvas of {target_node}")
                else:
                    print(f"Target {target_node} has no subcanvas")

            print(f"Project loaded successfully: {filename}")
            print(f"Summary: {len(node_map)} nodes, {edge_count} edges reconstructed")

            self.mark_as_saved(filename)
            return True

        except Exception as error:
            print(f"Error loading project: {error}")
            import traceback

            traceback.print_exc()
            QMessageBox.critical(
                self.canvas,
                tr("Error"),
                tr("Could not load project:\n{error}").format(error=error),
            )
            return False

    def _move_node_to_subcanvas(
        self,
        child_node: CanvasNodeItem,
        parent_node: BaseNodeItem,
    ) -> bool:
        """
        Move Node To Subcanvas.

        Args:
            child_node (CanvasNodeItem): The child node.
            parent_node (BaseNodeItem): The parent node.

        Returns:
            bool: Move Node To Subcanvas.
        """
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"Could not get subcanvas from parent node {parent_node}")
                return False

            child_scene = child_node.scene()
            if child_scene is not None:
                child_scene.removeItem(child_node)

            child_node.setParentItem(subcanvas)
            child_node.subcanvas_parent = subcanvas

            current_pos = child_node.pos()
            child_node.setPos(current_pos)

            if not hasattr(parent_node, "child_nodes"):
                parent_node.child_nodes = []
            if child_node not in parent_node.child_nodes:
                parent_node.child_nodes.append(child_node)

            print(f"Node moved to subcanvas of {parent_node} at position {current_pos}")
            return True

        except Exception as error:
            print(f"Error moving node to subcanvas: {error}")
            return False

    def _create_composite_internal_node(
        self,
        parent_node: BaseNodeItem,
        model_props: PropertyMap,
    ) -> bool:
        """
        Create Composite Internal Node.

        Args:
            parent_node (BaseNodeItem): The parent node.
            model_props (PropertyMap): The model props.

        Returns:
            bool: Create Composite Internal Node.
        """
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(
                    f"Could not get subcanvas for composite internal of {parent_node}"
                )
                return False

            if not hasattr(parent_node.model, "get_internal_model"):
                return False

            wrapper = cast(CompositeModelWrapper, parent_node.model)
            internal_model = wrapper.get_internal_model()
            node_type = internal_model.node_type()
            NodeClass = _NODE_MAP.get(node_type)
            if not NodeClass:
                return False

            internal_node = NodeClass(0, 0)
            internal_node.model = parent_node.model
            internal_node._independent_model = internal_model

            def on_model_changed(prop_name: str, value: object) -> None:
                """
                On Model Changed.

                Args:
                    prop_name (str): The prop name.
                    value (object): The value.
                """
                del prop_name, value
                internal_node.update()

            wrapper.add_change_callback(on_model_changed)

            internal_node.setParentItem(subcanvas)
            offset_x = subcanvas.radius * _as_float(
                model_props.get("internal_position_in_subcanvas_x", 0.6),
                0.6,
            )
            offset_y = subcanvas.radius * _as_float(
                model_props.get("internal_position_in_subcanvas_y", 0.0),
                0.0,
            )
            internal_node.setPos(offset_x, offset_y)
            internal_node.setVisible(True)
            internal_node.subcanvas_parent = subcanvas

            self.nodes.append(internal_node)

            if not hasattr(parent_node, "child_nodes"):
                parent_node.child_nodes = []
            parent_node.child_nodes.append(internal_node)

            print(
                f"Internal composite node '{node_type}' created in "
                f"subcanvas of {parent_node} at ({offset_x:.1f}, "
                f"{offset_y:.1f})"
            )
            return True

        except Exception as error:
            print(f"Error creating internal composite node: {error}")
            import traceback

            traceback.print_exc()
            return False

    def _create_node_from_data(
        self,
        node_data: SerializedNodeData,
    ) -> CanvasNodeItem | None:
        """
        Create Node From Data.

        Args:
            node_data (SerializedNodeData): The node data.

        Returns:
            CanvasNodeItem | None: Create Node From Data.
        """
        node_type = node_data["type"]
        pos_data = node_data["position"]

        print(
            f"Creating node {node_type} at position ({pos_data['x']}, {pos_data['y']})"
        )

        node = self.add_node(node_type, 0, 0)
        if not node:
            return None

        node.setPos(float(pos_data["x"]), float(pos_data["y"]))

        if hasattr(node, "model"):
            model_props = node_data.get("model_properties", {})
            if model_props:
                is_composite = bool(model_props.get("is_composite", False))
                if is_composite:
                    ModelClass = _MODEL_MAP.get(node_type)
                    if ModelClass is None:
                        return node

                    internal_model = ModelClass(0, 0)
                    internal_model.position_in_subcanvas_x = _as_float(
                        model_props.get("internal_position_in_subcanvas_x", 0.6),
                        0.6,
                    )
                    internal_model.position_in_subcanvas_y = _as_float(
                        model_props.get("internal_position_in_subcanvas_y", 0.0),
                        0.0,
                    )

                    external_model = node.model
                    wrapper = CompositeModelWrapper(external_model, internal_model)
                    node.model = wrapper
                    node._independent_model = external_model

                    def on_model_changed(
                        prop_name: str,
                        value: object,
                    ) -> None:
                        """
                        On Model Changed.

                        Args:
                            prop_name (str): The prop name.
                            value (object): The value.
                        """
                        node.update()
                        node.properties_changed.emit(node, {prop_name: value})

                    wrapper.add_change_callback(on_model_changed)

                    wrapper.label = str(model_props.get("label", ""))
                    wrapper.color = str(model_props.get("color", "#3498db"))
                    wrapper.border_color = str(
                        model_props.get("border_color", "#2980b9")
                    )
                    wrapper.text_color = str(model_props.get("text_color", "#ffffff"))

                    external_model = (
                        node._independent_model
                        if node._independent_model
                        else node.model
                    )
                    external_model.x = _as_float(
                        model_props.get("x", pos_data["x"]),
                        pos_data["x"],
                    )
                    external_model.y = _as_float(
                        model_props.get("y", pos_data["y"]),
                        pos_data["y"],
                    )
                    external_model.radius = _as_float(
                        model_props.get("radius", 50),
                        50.0,
                    )
                    external_model.show_subcanvas = bool(
                        model_props.get("show_subcanvas", False)
                    )
                    external_model.position_in_subcanvas_x = _as_float(
                        model_props.get("position_in_subcanvas_x", 0.0),
                        0.0,
                    )
                    external_model.position_in_subcanvas_y = _as_float(
                        model_props.get("position_in_subcanvas_y", 0.0),
                        0.0,
                    )
                    external_model.content_offset_x = _as_float(
                        model_props.get("content_offset_x", 0.0),
                        0.0,
                    )
                    external_model.content_offset_y = _as_float(
                        model_props.get("content_offset_y", 0.0),
                        0.0,
                    )
                else:
                    node.model.x = _as_float(
                        model_props.get("x", pos_data["x"]),
                        pos_data["x"],
                    )
                    node.model.y = _as_float(
                        model_props.get("y", pos_data["y"]),
                        pos_data["y"],
                    )
                    node.model.radius = _as_float(
                        model_props.get("radius", 50),
                        50.0,
                    )
                    node.model.label = str(model_props.get("label", ""))
                    node.model.color = str(model_props.get("color", "#3498db"))
                    node.model.border_color = str(
                        model_props.get("border_color", "#2980b9")
                    )
                    node.model.text_color = str(
                        model_props.get("text_color", "#ffffff")
                    )
                    node.model.show_subcanvas = bool(
                        model_props.get("show_subcanvas", False)
                    )
                    node.model.position_in_subcanvas_x = _as_float(
                        model_props.get("position_in_subcanvas_x", 0.0),
                        0.0,
                    )
                    node.model.position_in_subcanvas_y = _as_float(
                        model_props.get("position_in_subcanvas_y", 0.0),
                        0.0,
                    )
                    node.model.content_offset_x = _as_float(
                        model_props.get("content_offset_x", 0.0),
                        0.0,
                    )
                    node.model.content_offset_y = _as_float(
                        model_props.get("content_offset_y", 0.0),
                        0.0,
                    )
            else:
                node.model.x = float(pos_data["x"])
                node.model.y = float(pos_data["y"])
                node.model.position_in_subcanvas_x = 0.0
                node.model.position_in_subcanvas_y = 0.0
                node.model.content_offset_x = 0.0
                node.model.content_offset_y = 0.0

        subcanvas_data = node_data.get("subcanvas")
        if subcanvas_data and isinstance(node, BaseNodeItem):
            if node.subcanvas is None:
                node.prepare_subcanvas_for_internal_use()

            if node.subcanvas is not None:
                if "radius" in subcanvas_data:
                    node.subcanvas.radius = float(subcanvas_data["radius"])
                if "original_radius" in subcanvas_data:
                    node.subcanvas.original_radius = float(
                        subcanvas_data["original_radius"]
                    )

                if subcanvas_data.get("visible", False):
                    node.ensure_subcanvas_visible()
                else:
                    node.model.show_subcanvas = False
                    if node.subcanvas:
                        node.subcanvas.setVisible(False)

                node.subcanvas._update_handle_pos()

        properties = dict(node_data.get("properties", {}))
        if hasattr(node, "update_properties"):
            properties["x"] = float(pos_data["x"])
            properties["y"] = float(pos_data["y"])

            if hasattr(node, "model"):
                properties["content_offset_x"] = node.model.content_offset_x
                properties["content_offset_y"] = node.model.content_offset_y
                properties["position_in_subcanvas_x"] = (
                    node.model.position_in_subcanvas_x
                )
                properties["position_in_subcanvas_y"] = (
                    node.model.position_in_subcanvas_y
                )

            node.update_properties(properties)

        if isinstance(node, BaseNodeItem) and node.is_subcanvas_visible():
            node.apply_position_in_subcanvas()

        node.update()
        print(
            f"Node {node_type} created. Subcanvas position: "
            f"({node.model.position_in_subcanvas_x}, "
            f"{node.model.position_in_subcanvas_y})"
        )
        return node

    def _create_edge_from_data(
        self,
        edge_data: SerializedEdgeData,
        node_map: dict[int, CanvasNodeItem],
    ) -> BaseEdgeItem | None:
        """
        Create Edge From Data.

        Args:
            edge_data (SerializedEdgeData): The edge data.
            node_map (dict[int, CanvasNodeItem]): The node map.

        Returns:
            BaseEdgeItem | None: Create Edge From Data.
        """
        edge_type = edge_data["type"]
        source_id = edge_data["source_id"]
        target_id = edge_data["target_id"]

        source_node = node_map.get(source_id)
        target_node = node_map.get(target_id)

        if not source_node or not target_node:
            print(
                f"Could not create edge: source({source_id}) or "
                f"target({target_id}) nodes not found"
            )
            return None

        ArrowClass = _ARROW_TYPES.get(edge_type)
        if not ArrowClass:
            print(f"Unknown edge type: {edge_type}")
            return None

        edge_item = ArrowClass(source_node, target_node)
        scene = self.canvas.scene()
        if scene is None:
            return None

        scene.addItem(edge_item)
        self.edges.append(edge_item)

        properties = dict(edge_data.get("properties", {}))
        if hasattr(edge_item, "update_properties"):
            edge_item.update_properties(properties)

        control_points = edge_data.get("control_points", [])
        if control_points and hasattr(edge_item, "control_points"):
            for point_data in control_points:
                point = QPointF(float(point_data["x"]), float(point_data["y"]))
                edge_item.control_points.append(point)
            edge_item._update_handles_position()
            edge_item.update_position()
            edge_item.setSelected(False)
            edge_item.set_handles_visible(False)

        return edge_item

    def _move_edge_to_subcanvas(
        self,
        edge: BaseEdgeItem,
        parent_node: BaseNodeItem,
    ) -> bool:
        """
        Move Edge To Subcanvas.

        Args:
            edge (BaseEdgeItem): The edge.
            parent_node (BaseNodeItem): The parent node.

        Returns:
            bool: Move Edge To Subcanvas.
        """
        try:
            subcanvas = parent_node.ensure_subcanvas_visible()
            if not subcanvas:
                print(f"Could not get subcanvas from parent node {parent_node}")
                return False

            edge_scene = edge.scene()
            if edge_scene is not None:
                edge_scene.removeItem(edge)

            edge.setParentItem(subcanvas)
            print(f"Edge moved to subcanvas of {parent_node}")
            return True

        except Exception as error:
            print(f"Error moving edge to subcanvas: {error}")
            return False
