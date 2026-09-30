# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.core.models.base_node import BaseNode

NODE_STYLES: dict[str, dict[str, str]] = {
    "actor": {
        "label": "Actor",
        "color": "#6496fa",
        "border_color": "#000000",
        "text_color": "#ffffff",
    },
    "agent": {
        "label": "Agent",
        "color": "#fa9664",
        "border_color": "#000000",
        "text_color": "#ffffff",
    },
    "hard_goal": {
        "label": "Hard Goal",
        "color": "#96c896",
        "border_color": "#000000",
        "text_color": "#ffffff",
    },
    "plan": {
        "label": "Plan",
        "color": "#96b4fa",
        "border_color": "#000000",
        "text_color": "#ffffff",
    },
    "resource": {
        "label": "Resource",
        "color": "#c896fa",
        "border_color": "#000000",
        "text_color": "#ffffff",
    },
    "soft_goal": {
        "label": "Soft Goal",
        "color": "#dcdcb4",
        "border_color": "#000000",
        "text_color": "#000000",
    },
}


class TypedNode(BaseNode):
    """A BaseNode whose label/colors come from NODE_STYLES[type_name]."""

    def __init__(
        self, type_name: str, x: float = 0, y: float = 0, radius: float = 50
    ) -> None:
        super().__init__(x, y, radius)
        style = NODE_STYLES[type_name]
        self._type_name = type_name
        self.label = style["label"]
        self.color = style["color"]
        self.border_color = style["border_color"]
        self.text_color = style["text_color"]

    def node_type(self) -> str:
        return self._type_name
