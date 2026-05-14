# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.model_types import ChangeCallback
from app.model_types import NodeModelLike


class CompositeModelWrapper:
    """
    Composite Model Wrapper.

    Attributes:
        _external_model (NodeModelLike): external model.
        _internal_model (NodeModelLike): internal model.
        _on_change_callbacks (list[ChangeCallback]): on change callbacks.

    Methods:
        __init__: Initialize the instance.
        add_change_callback: Add Change Callback.
        label: Label.
        color: Color.
        border_color: Border Color.
        text_color: Text Color.
        x: X.
        y: Y.
        radius: Radius.
        text_align: Text Align.
        text_width: Text Width.
        font_size: Font Size.
        content_offset_x: Content Offset X.
        content_offset_y: Content Offset Y.
        position_in_subcanvas_x: Position In Subcanvas X.
        position_in_subcanvas_y: Position In Subcanvas Y.
        show_subcanvas: Show Subcanvas.
        child_nodes: Child Nodes.
        toggle_subcanvas: Toggle Subcanvas.
        node_type: Node Type.
        get_external_model: Get External Model.
        get_internal_model: Get Internal Model.
    """

    # List of properties that itself sincronizan between both modelos
    SYNCED_PROPERTIES = {"label", "color", "border_color", "text_color"}
    _external_model: NodeModelLike
    _internal_model: NodeModelLike
    _on_change_callbacks: list[ChangeCallback]

    def __init__(
        self,
        external_model: NodeModelLike,
        internal_model: NodeModelLike,
    ) -> None:
        """
        Initialize the instance.

        Args:
            external_model (NodeModelLike): The external model.
            internal_model (NodeModelLike): The internal model.
        """
        object.__setattr__(self, "_external_model", external_model)
        object.__setattr__(self, "_internal_model", internal_model)
        # Callbacks for notify cambios (opcional)
        object.__setattr__(self, "_on_change_callbacks", [])

    def _notify_change(self, prop_name: str, value: object) -> None:
        """
        Notify Change.

        Args:
            prop_name (str): The prop name.
            value (object): The value.
        """
        callbacks: list[ChangeCallback] = self._on_change_callbacks
        for callback in callbacks:
            try:
                callback(prop_name, value)
            except Exception:
                pass

    def add_change_callback(self, callback: ChangeCallback) -> None:
        """
        Add Change Callback.

        Args:
            callback (ChangeCallback): The callback.
        """
        self._on_change_callbacks.append(callback)

    # ==================== PROPERTIES SINCRONIZADAS ====================

    @property
    def label(self) -> str:
        """
        Label.

        Returns:
            str: Label.
        """
        return self._external_model.label

    @label.setter
    def label(self, value: str) -> None:
        # Sincronizar in BOTH modelos
        """
        Label.

        Args:
            value (str): The value.
        """
        self._external_model.label = value
        self._internal_model.label = value
        self._notify_change("label", value)

    @property
    def color(self) -> str:
        """
        Color.

        Returns:
            str: Color.
        """
        return self._external_model.color

    @color.setter
    def color(self, value: str) -> None:
        """
        Color.

        Args:
            value (str): The value.
        """
        self._external_model.color = value
        self._internal_model.color = value
        self._notify_change("color", value)

    @property
    def border_color(self) -> str:
        """
        Border Color.

        Returns:
            str: Border Color.
        """
        return self._external_model.border_color

    @border_color.setter
    def border_color(self, value: str) -> None:
        """
        Border Color.

        Args:
            value (str): The value.
        """
        self._external_model.border_color = value
        self._internal_model.border_color = value
        self._notify_change("border_color", value)

    @property
    def text_color(self) -> str:
        """
        Text Color.

        Returns:
            str: Text Color.
        """
        return self._external_model.text_color

    @text_color.setter
    def text_color(self, value: str) -> None:
        """
        Text Color.

        Args:
            value (str): The value.
        """
        self._external_model.text_color = value
        self._internal_model.text_color = value
        self._notify_change("text_color", value)

    # ==================== PROPERTIES INDEPENDIENTES ====================
    # Itself delegan al model external by defecto (the of the canvas main)

    @property
    def x(self) -> float:
        """
        X.

        Returns:
            float: X.
        """
        return self._external_model.x

    @x.setter
    def x(self, value: float) -> None:
        """
        X.

        Args:
            value (float): The value.
        """
        self._external_model.x = value

    @property
    def y(self) -> float:
        """
        Y.

        Returns:
            float: Y.
        """
        return self._external_model.y

    @y.setter
    def y(self, value: float) -> None:
        """
        Y.

        Args:
            value (float): The value.
        """
        self._external_model.y = value

    @property
    def radius(self) -> float:
        """
        Radius.

        Returns:
            float: Radius.
        """
        return self._external_model.radius

    @radius.setter
    def radius(self, value: float) -> None:
        """
        Radius.

        Args:
            value (float): The value.
        """
        self._external_model.radius = value

    @property
    def text_align(self) -> str:
        """
        Text Align.

        Returns:
            str: Text Align.
        """
        return self._external_model.text_align

    @text_align.setter
    def text_align(self, value: str) -> None:
        """
        Text Align.

        Args:
            value (str): The value.
        """
        self._external_model.text_align = value

    @property
    def text_width(self) -> float:
        """
        Text Width.

        Returns:
            float: Text Width.
        """
        return self._external_model.text_width

    @text_width.setter
    def text_width(self, value: float) -> None:
        """
        Text Width.

        Args:
            value (float): The value.
        """
        self._external_model.text_width = value

    @property
    def font_size(self) -> float:
        """
        Font Size.

        Returns:
            float: Font Size.
        """
        return self._external_model.font_size

    @font_size.setter
    def font_size(self, value: float) -> None:
        """
        Font Size.

        Args:
            value (float): The value.
        """
        self._external_model.font_size = value

    @property
    def content_offset_x(self) -> float:
        """
        Content Offset X.

        Returns:
            float: Content Offset X.
        """
        return self._external_model.content_offset_x

    @content_offset_x.setter
    def content_offset_x(self, value: float) -> None:
        """
        Content Offset X.

        Args:
            value (float): The value.
        """
        self._external_model.content_offset_x = value

    @property
    def content_offset_y(self) -> float:
        """
        Content Offset Y.

        Returns:
            float: Content Offset Y.
        """
        return self._external_model.content_offset_y

    @content_offset_y.setter
    def content_offset_y(self, value: float) -> None:
        """
        Content Offset Y.

        Args:
            value (float): The value.
        """
        self._external_model.content_offset_y = value

    @property
    def position_in_subcanvas_x(self) -> float:
        """
        Position In Subcanvas X.

        Returns:
            float: Position In Subcanvas X.
        """
        return self._external_model.position_in_subcanvas_x

    @position_in_subcanvas_x.setter
    def position_in_subcanvas_x(self, value: float) -> None:
        """
        Position In Subcanvas X.

        Args:
            value (float): The value.
        """
        self._external_model.position_in_subcanvas_x = value

    @property
    def position_in_subcanvas_y(self) -> float:
        """
        Position In Subcanvas Y.

        Returns:
            float: Position In Subcanvas Y.
        """
        return self._external_model.position_in_subcanvas_y

    @position_in_subcanvas_y.setter
    def position_in_subcanvas_y(self, value: float) -> None:
        """
        Position In Subcanvas Y.

        Args:
            value (float): The value.
        """
        self._external_model.position_in_subcanvas_y = value

    @property
    def show_subcanvas(self) -> bool:
        """
        Show Subcanvas.

        Returns:
            bool: Show Subcanvas.
        """
        return self._external_model.show_subcanvas

    @show_subcanvas.setter
    def show_subcanvas(self, value: bool) -> None:
        """
        Show Subcanvas.

        Args:
            value (bool): The value.
        """
        self._external_model.show_subcanvas = value

    @property
    def child_nodes(self) -> list[object]:
        """
        Child Nodes.

        Returns:
            list[object]: Child Nodes.
        """
        return self._external_model.child_nodes

    @child_nodes.setter
    def child_nodes(self, value: list[object]) -> None:
        """
        Child Nodes.

        Args:
            value (list[object]): The value.
        """
        self._external_model.child_nodes = value

    # ==================== MÉTODOS ====================

    def toggle_subcanvas(self) -> bool:
        """
        Toggle Subcanvas.

        Returns:
            bool: Toggle Subcanvas.
        """
        return self._external_model.toggle_subcanvas()

    def node_type(self) -> str:
        """
        Node Type.

        Returns:
            str: Node Type.
        """
        return self._external_model.node_type()

    # ==================== ACCESO A MODELOS INTERNOS ====================

    def get_external_model(self) -> NodeModelLike:
        """
        Get External Model.

        Returns:
            NodeModelLike: Get External Model.
        """
        return self._external_model

    def get_internal_model(self) -> NodeModelLike:
        """
        Get Internal Model.

        Returns:
            NodeModelLike: Get Internal Model.
        """
        return self._internal_model

    # ==================== DELEGACIÓN GENÉRICA ====================
    # For cualquier otra propiedad no definida, delegar al external

    def __getattr__(self, name: str) -> object:
        """
        Getattr  .

        Args:
            name (str): The name.

        Returns:
            object: Getattr  .

        Raises:
            AttributeError: If an error occurs.
        """
        # Avoid recursion infinite for attributes private
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        return getattr(self._external_model, name)

    def __setattr__(self, name: str, value: object) -> None:
        """
        Setattr  .

        Args:
            name (str): The name.
            value (object): The value.
        """
        # If es a propiedad sincronizada, update both modelos
        if name in self.SYNCED_PROPERTIES:
            setattr(self._external_model, name, value)
            setattr(self._internal_model, name, value)
            self._notify_change(name, value)
        # For the rest, only update the model external
        else:
            setattr(self._external_model, name, value)
