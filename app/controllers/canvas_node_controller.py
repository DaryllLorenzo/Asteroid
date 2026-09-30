# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from functools import partial
import logging

from app.controller_types import CanvasNodeItem
from app.controllers._canvas_mixin import CanvasControllerMixin
from app.controllers.canvas_registry_controller import _NODE_MAP
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem

logger = logging.getLogger(__name__)


class CanvasNodeController(CanvasControllerMixin):
    def add_node(
        self,
        node_type: str,
        x: float,
        y: float,
    ) -> CanvasNodeItem | None:
        NodeClass = _NODE_MAP.get(node_type)
        if NodeClass is None:
            return None

        node_item = NodeClass(0, 0)
        node_item.setPos(x, y)

        if hasattr(node_item, "model"):
            node_item.model.x = x
            node_item.model.y = y

        scene = self.canvas.scene()
        if scene is None:
            return None

        scene.addItem(node_item)
        self.nodes.append(node_item)

        if hasattr(node_item, "properties_changed"):
            node_item.properties_changed.connect(self.on_node_properties_changed)
        else:
            logger.warning("Node %s lacks properties_changed signal", node_type)

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        if hasattr(node_item, "drag_finished"):
            node_item.drag_finished.connect(self._on_node_drag_finished)

        if hasattr(node_item, "resize_finished"):
            node_item.resize_finished.connect(self._on_node_resize_finished)

        if hasattr(node_item, "subcanvas_toggle_requested"):
            node_item.subcanvas_toggle_requested.connect(
                self._on_subcanvas_toggle_requested
            )

        self.mark_as_modified()
        return node_item

    def _restore_node(
        self,
        node_item: CanvasNodeItem,
    ) -> None:
        scene = self.canvas.scene()
        if scene is not None and node_item.scene() is None:
            scene.addItem(node_item)
        if node_item not in self.nodes:
            self.nodes.append(node_item)

        if hasattr(node_item, "properties_changed"):
            node_item.properties_changed.connect(self.on_node_properties_changed)

        if hasattr(node_item, "subcanvas_toggled"):
            node_item.subcanvas_toggled.connect(self._on_subcanvas_toggled)

        if hasattr(node_item, "drag_finished"):
            node_item.drag_finished.connect(self._on_node_drag_finished)

        if hasattr(node_item, "resize_finished"):
            node_item.resize_finished.connect(self._on_node_resize_finished)

        if hasattr(node_item, "subcanvas_toggle_requested"):
            node_item.subcanvas_toggle_requested.connect(
                self._on_subcanvas_toggle_requested
            )

    def on_node_properties_changed(
        self,
        node_item: CanvasNodeItem,
        properties: dict[str, object],
    ) -> None:
        if node_item == self.selected_node:
            self.selected_node_properties_changed.emit(properties)

        if node_item == self.selected_node or (
            hasattr(node_item, "_resizing") and node_item._resizing
        ):
            self.selected_node_properties_changed.emit(properties)

        self.mark_as_modified()

    def _on_subcanvas_toggled(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas,
    ) -> None:
        if subcanvas is None:
            stored = self._subcanvas_handlers.pop(parent_node_item, None)
            if stored:
                prev_subcanvas, handler_node, handler_arrow = stored
                try:
                    prev_subcanvas.subnode_dropped.disconnect(handler_node)
                    prev_subcanvas.subarrow_dropped.disconnect(handler_arrow)
                except TypeError:
                    pass  # already disconnected
            return

        stored = self._subcanvas_handlers.get(parent_node_item)
        if stored:
            prev_subcanvas, handler_node, handler_arrow = stored
            if prev_subcanvas is subcanvas:
                return
            try:
                prev_subcanvas.subnode_dropped.disconnect(handler_node)
                prev_subcanvas.subarrow_dropped.disconnect(handler_arrow)
            except TypeError:
                pass  # already disconnected

        handler_node = partial(
            self._on_subcanvas_node_dropped, parent_node_item, subcanvas
        )
        handler_arrow = partial(self._start_subarrow_mode, parent_node_item, subcanvas)

        subcanvas.subnode_dropped.connect(handler_node)
        subcanvas.subarrow_dropped.connect(handler_arrow)
        self._subcanvas_handlers[parent_node_item] = (
            subcanvas,
            handler_node,
            handler_arrow,
        )

        subcanvas.setZValue(parent_node_item.zValue() - 1)

    def _add_to_subcanvas(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas,
        item_type: str,
        local_x: float,
        local_y: float,
    ) -> CanvasNodeItem | None:
        NodeClass = _NODE_MAP.get(item_type)
        if NodeClass is None:
            return None

        child = NodeClass(0, 0, radius=20)
        if child.scene() is not None and child.parentItem() is None:
            scene = child.scene()
            if scene is not None:
                scene.removeItem(child)

        child.setParentItem(subcanvas)
        child.setPos(local_x, local_y)
        child.setVisible(subcanvas.isVisible())
        child.subcanvas_parent = subcanvas

        self.nodes.append(child)

        if hasattr(child, "properties_changed"):
            child.properties_changed.connect(self.on_node_properties_changed)
        else:
            logger.warning(
                "Internal node %s lacks properties_changed signal", item_type
            )

        if hasattr(child, "drag_finished"):
            child.drag_finished.connect(self._on_node_drag_finished)

        if hasattr(child, "resize_finished"):
            child.resize_finished.connect(self._on_node_resize_finished)

        if hasattr(child, "subcanvas_toggle_requested"):
            child.subcanvas_toggle_requested.connect(
                self._on_subcanvas_toggle_requested
            )

        if not hasattr(parent_node_item, "child_nodes"):
            parent_node_item.child_nodes = []
        parent_node_item.child_nodes.append(child)

        self.mark_as_modified()
        return child

    def _on_subcanvas_node_dropped(
        self,
        parent_node_item: CanvasNodeItem,
        subcanvas,
        item_type: str,
        local_x: float,
        local_y: float,
    ) -> None:
        errors = self.validator.validate(
            "subcanvas_add_node",
            {
                "parent_is_entity": isinstance(
                    parent_node_item, (ActorNodeItem, AgentNodeItem)
                ),
                "child_type": item_type,
            },
        )
        if errors:
            self._show_validation_errors(errors)
            return

        from app.commands.add_subcanvas_node_command import AddSubcanvasNodeCommand

        self.undo_stack.push(
            AddSubcanvasNodeCommand(
                self,
                parent_node_item,
                subcanvas,
                item_type,
                local_x,
                local_y,
            )
        )
