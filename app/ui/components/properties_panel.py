# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QSpinBox
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.control_point_handle import ControlPointHandle
from app.ui.components.position_controll_widget import PositionControlWidget
from app.ui.theme_manager import theme_manager


class PropertiesPanel(QWidget):
    """
    Properties Panel.

    Methods:
        __init__: Initialize the instance.
        init_ui: Init Ui.
        on_selection_changed: On Selection Changed.
        on_edge_selected: On Edge Selected.
        on_straighten_edge_clicked: On Straighten Edge Clicked.
        on_node_selected: On Node Selected.
        on_node_property_changed: On Node Property Changed.
        on_controller_properties_changed: On Controller Properties Changed.
        update_visibility: Update Visibility.
        choose_color: Choose Color.
        update_color_buttons: Update Color Buttons.
        on_delete_clicked: On Delete Clicked.
        on_position_in_subcanvas_changed: On Position In Subcanvas Changed.
        reset_position_in_subcanvas: Reset Position In Subcanvas.
    """

    properties_changed = pyqtSignal(dict)
    selection_mode_changed = pyqtSignal(bool)
    delete_requested = pyqtSignal()

    def __init__(self, controller=None):
        """
        Initialize the instance.

        Args:
            controller: The controller.
        """
        super().__init__()
        self.controller = controller
        self.current_selection = None
        self.selection_mode = False
        self.init_ui()

        if controller:
            controller.selected_node_properties_changed.connect(
                self.on_controller_properties_changed
            )
            controller.selection_changed.connect(self.on_selection_changed)

        theme_manager().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, dark: bool):
        """Update hardcoded styles when theme changes."""
        if dark:
            self.edge_group.setStyleSheet(
                "QGroupBox { color: #e0e0e0; font-weight: bold; }"
            )
            self.edge_info_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            self.instructions_label.setStyleSheet(
                "background-color: #2d2d2d; color: #cccccc; "
                "padding: 8px; border-radius: 4px; margin: 4px 0;"
            )
        else:
            self.edge_group.setStyleSheet(
                "QGroupBox { color: #FFFFFF; font-weight: bold; }"
            )
            self.edge_info_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            self.instructions_label.setStyleSheet(
                "background-color: #f5f5f5; color: #333333; "
                "padding: 8px; border-radius: 4px; margin: 4px 0;"
            )

    def init_ui(self):
        """Init Ui."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Grupo of Properties of NODE ---
        self.node_group = QGroupBox("Propiedades del Nodo")
        node_layout = QFormLayout()

        self.label_edit = QPlainTextEdit()
        self.label_edit.setPlaceholderText("Nombre del nodo...")
        self.label_edit.setMaximumHeight(60)
        self.label_edit.textChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Nombre:", self.label_edit)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(10, 500)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Radio:", self.radius_spin)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(5, 100)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.valueChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Tam. Letra:", self.font_size_spin)

        self.text_width_spin = QSpinBox()
        self.text_width_spin.setRange(50, 800)
        self.text_width_spin.setSuffix(" px")
        self.text_width_spin.valueChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Ancho Texto:", self.text_width_spin)

        # --- Alignment Compacta ---
        align_layout = QHBoxLayout()
        align_layout.setSpacing(2)
        self.align_group = QButtonGroup(self)

        self.btn_align_left = QPushButton("L")
        self.btn_align_center = QPushButton("C")
        self.btn_align_right = QPushButton("R")

        for btn in [self.btn_align_left, self.btn_align_center, self.btn_align_right]:
            btn.setCheckable(True)
            btn.setFixedWidth(35)
            self.align_group.addButton(btn)
            align_layout.addWidget(btn)

        self.btn_align_center.setChecked(True)
        self.align_group.buttonClicked.connect(self.on_node_property_changed)
        node_layout.addRow("Alineación:", align_layout)

        self.node_group.setLayout(node_layout)
        layout.addWidget(self.node_group)

        # --- Colores ---
        self.colors_group = QGroupBox("Colores")
        colors_layout = QFormLayout()
        self.color_btn = QPushButton("▆▆▆")
        self.color_btn.clicked.connect(lambda: self.choose_color("color"))
        colors_layout.addRow("Relleno:", self.color_btn)

        self.border_color_btn = QPushButton("▆▆▆")
        self.border_color_btn.clicked.connect(lambda: self.choose_color("border_color"))
        colors_layout.addRow("Borde:", self.border_color_btn)

        self.text_color_btn = QPushButton("▆▆▆")
        self.text_color_btn.clicked.connect(lambda: self.choose_color("text_color"))
        colors_layout.addRow("Texto:", self.text_color_btn)
        self.colors_group.setLayout(colors_layout)
        layout.addWidget(self.colors_group)

        # --- Position Canvas ---
        self.pos_group = QGroupBox("Behaviour Canvas")
        pos_layout = QVBoxLayout()
        self.pos_control = PositionControlWidget()
        self.pos_control.position_changed.connect(self.on_position_in_subcanvas_changed)
        pos_container = QHBoxLayout()
        pos_container.addStretch()
        pos_container.addWidget(self.pos_control)
        pos_container.addStretch()
        pos_layout.addLayout(pos_container)
        self.pos_reset_btn = QPushButton("Centrar")
        self.pos_reset_btn.clicked.connect(self.reset_position_in_subcanvas)
        pos_layout.addWidget(self.pos_reset_btn)
        self.pos_group.setLayout(pos_layout)
        layout.addWidget(self.pos_group)

        # --- Flecha ---
        self.edge_group = QGroupBox("Flecha")
        self.edge_group.setStyleSheet(
            "QGroupBox { color: #FFFFFF; font-weight: bold; }"
        )
        edge_layout = QVBoxLayout()

        # Information of the flecha
        self.edge_info_label = QLabel("Flecha seleccionada")
        self.edge_info_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        edge_layout.addWidget(self.edge_info_label)

        # Instrucciones of edición
        self.instructions_label = QLabel(
            "<b>Edición de Flecha</b><br><br>"
            "• Arrastra los puntos para modificar la forma<br>"
            "• Doble-click en la línea para agregar un punto<br>"
            "• Selecciona un punto y presiona Delete para eliminar<br>"
            "• Click en 'Enderezar' para línea recta"
        )
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setStyleSheet(
            "background-color: #f5f5f5; color: #333333; "
            "padding: 8px; border-radius: 4px; margin: 4px 0;"
        )
        edge_layout.addWidget(self.instructions_label)

        # Button for enderezar the flecha
        self.straighten_button = QPushButton("Enderezar Flecha")
        self.straighten_button.clicked.connect(self.on_straighten_edge_clicked)
        edge_layout.addWidget(self.straighten_button)

        self.edge_group.setLayout(edge_layout)
        layout.addWidget(self.edge_group)

        # --- Acciones ---
        self.actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        self.delete_button = QPushButton(" Eliminar Elemento")
        self.delete_button.setStyleSheet(
            "background-color: #ff4444; color: white; font-weight: bold; padding: 6px;"
        )
        self.delete_button.clicked.connect(self.on_delete_clicked)
        actions_layout.addWidget(self.delete_button)
        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)

        self.no_selection_label = QLabel(" Selecciona un elemento")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.no_selection_label)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.update_visibility()

    def on_selection_changed(self, item):
        """
        On Selection Changed.

        Args:
            item: The item.
        """
        self.current_selection = item
        # Verificar if es a ControlPointHandle (no show properties)
        if isinstance(item, ControlPointHandle):
            self.update_visibility()
            return
        if isinstance(item, BaseEdgeItem):
            self.on_edge_selected(item)
        else:
            self.on_node_selected(item)

    def on_edge_selected(self, edge):
        """
        On Edge Selected.

        Args:
            edge: The edge.
        """
        # Get the type of flecha
        edge_type = "Flecha"
        if hasattr(edge, "source_node") and hasattr(edge, "dest_node"):
            src_name = (
                getattr(edge.source_node.model, "label", "Nodo")
                if hasattr(edge.source_node, "model")
                else "Nodo"
            )
            dst_name = (
                getattr(edge.dest_node.model, "label", "Nodo")
                if hasattr(edge.dest_node, "model")
                else "Nodo"
            )
            edge_type = f"{src_name} → {dst_name}"

        self.edge_info_label.setText(edge_type)
        self.update_visibility()

    def on_straighten_edge_clicked(self):
        """On Straighten Edge Clicked."""
        if self.current_selection and isinstance(self.current_selection, BaseEdgeItem):
            if self.controller and hasattr(self.controller, "straighten_edge"):
                self.controller.straighten_edge(self.current_selection)

    def on_node_selected(self, node):
        """
        On Node Selected.

        Args:
            node: The node.
        """
        if node and hasattr(node, "model"):
            self.blockSignals(True)
            # Only update if the text es distinto for no move the cursor
            if self.label_edit.toPlainText() != node.model.label:
                self.label_edit.setPlainText(node.model.label)

            # Use _independent_model if it exists (for internal composite nodes)
            has_independent = (
                hasattr(node, "_independent_model") and node._independent_model
            )
            model_for_independent = (
                node._independent_model if has_independent else node.model
            )

            self.radius_spin.setValue(int(model_for_independent.radius))
            self.font_size_spin.setValue(
                int(getattr(model_for_independent, "font_size", 10))
            )
            self.text_width_spin.setValue(
                int(getattr(model_for_independent, "text_width", 150))
            )

            align = getattr(model_for_independent, "text_align", "center")
            self.btn_align_left.setChecked(align == "left")
            self.btn_align_center.setChecked(align == "center")
            self.btn_align_right.setChecked(align == "right")
            self.blockSignals(False)
            self.update_color_buttons()

            if hasattr(node.model, "position_in_subcanvas_x"):
                self.pos_control.set_position(
                    node.model.position_in_subcanvas_x,
                    node.model.position_in_subcanvas_y,
                )
        self.update_visibility()

    def on_node_property_changed(self):
        """On Node Property Changed."""
        if not self.current_selection or not hasattr(self.current_selection, "model"):
            return

        props = {
            "label": self.label_edit.toPlainText(),
            "radius": self.radius_spin.value(),
            "font_size": self.font_size_spin.value(),
            "text_width": self.text_width_spin.value(),
            "text_align": "left"
            if self.btn_align_left.isChecked()
            else "right"
            if self.btn_align_right.isChecked()
            else "center",
        }
        self.properties_changed.emit(props)

    def on_controller_properties_changed(self, properties: dict):
        # This part es vital for the cursor
        """
        On Controller Properties Changed.

        Args:
            properties (dict): The properties.
        """
        if not self.current_selection:
            return

        self.blockSignals(True)
        if "label" in properties:
            # Only actualizamos the widget if the text realmente changed externamente
            # y no es lo that the usuario acaba of write
            if self.label_edit.toPlainText() != properties["label"]:
                self.label_edit.setPlainText(properties["label"])
                # Move cursor al final by if acaso
                cursor = self.label_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.label_edit.setTextCursor(cursor)

        # Update the other campos without problemas of cursor
        if "radius" in properties:
            self.radius_spin.setValue(int(properties["radius"]))
        if "font_size" in properties:
            self.font_size_spin.setValue(int(properties["font_size"]))
        if "text_width" in properties:
            self.text_width_spin.setValue(int(properties["text_width"]))
        self.blockSignals(False)
        self.update_color_buttons()

    def update_visibility(self):
        """Update Visibility."""
        has_selection = self.current_selection is not None
        # Excluir ControlPointHandle of the selecciones válidas
        is_control_point = isinstance(self.current_selection, ControlPointHandle)
        is_node = (
            has_selection
            and not isinstance(self.current_selection, BaseEdgeItem)
            and not is_control_point
        )
        is_edge = has_selection and isinstance(self.current_selection, BaseEdgeItem)

        is_behaviour_node = False
        has_subcanvas = False
        if is_node:
            type_name = self.current_selection.__class__.__name__
            is_behaviour_node = type_name in ["ActorNodeItem", "AgentNodeItem"]
            # Usar model directamente for show_subcanvas (propiedad no sincronizada)
            has_subcanvas = getattr(
                self.current_selection.model, "show_subcanvas", False
            )

        self.node_group.setVisible(is_node)
        self.colors_group.setVisible(is_node)
        self.pos_group.setVisible(is_behaviour_node and has_subcanvas)
        self.edge_group.setVisible(is_edge)
        self.actions_group.setVisible(has_selection and not is_control_point)
        self.no_selection_label.setVisible(not has_selection or is_control_point)

    def choose_color(self, color_type):
        """
        Choose Color.

        Args:
            color_type: The color type.
        """
        if not self.current_selection:
            return
        # Colores son sincronizados, usar node.model (wrapper)
        current = QColor(getattr(self.current_selection.model, color_type, "#ffffff"))
        color = QColorDialog.getColor(current, self)
        if color.isValid():
            self.properties_changed.emit({color_type: color.name()})
            self.update_color_buttons()

    def update_color_buttons(self):
        """Update Color Buttons."""
        if not self.current_selection or not hasattr(self.current_selection, "model"):
            return
        # Colores son sincronizados, usar node.model (wrapper)
        m = self.current_selection.model
        self.color_btn.setStyleSheet(
            f"background-color: {getattr(m, 'color', '#eee')}; border: 1px solid #999;"
        )
        self.border_color_btn.setStyleSheet(
            f"background-color: {getattr(m, 'border_color', '#eee')}; "
            "border: 1px solid #999;"
        )
        self.text_color_btn.setStyleSheet(
            f"background-color: {getattr(m, 'text_color', '#eee')}; "
            "border: 1px solid #999;"
        )

    def on_delete_clicked(self):
        """On Delete Clicked."""
        self.delete_requested.emit()

    def on_position_in_subcanvas_changed(self, x, y):
        """
        On Position In Subcanvas Changed.

        Args:
            x: The x.
            y: The y.
        """
        if self.current_selection:
            # Position es independiente, emitir as this
            self.properties_changed.emit(
                {"position_in_subcanvas_x": x, "position_in_subcanvas_y": y}
            )

    def reset_position_in_subcanvas(self):
        """Reset Position In Subcanvas."""
        self.pos_control.set_position(0, 0)
        self.on_position_in_subcanvas_changed(0, 0)
