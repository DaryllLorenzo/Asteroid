# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QColorDialog, QFrame,
                            QSpinBox, QFormLayout, QGroupBox, QCheckBox, QMessageBox,
                            QPlainTextEdit, QButtonGroup, QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QTextCursor
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.position_controll_widget import PositionControlWidget

class PropertiesPanel(QWidget):
    properties_changed = pyqtSignal(dict)
    selection_mode_changed = pyqtSignal(bool)
    delete_requested = pyqtSignal()
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.current_selection = None
        self.selection_mode = False
        self.init_ui()
        
        if controller:
            controller.selected_node_properties_changed.connect(self.on_controller_properties_changed)
            controller.selection_changed.connect(self.on_selection_changed)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Grupo de Propiedades de NODO ---
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

        # --- Alineación Compacta ---
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
        self.color_btn.clicked.connect(lambda: self.choose_color('color'))
        colors_layout.addRow("Relleno:", self.color_btn)
        
        self.border_color_btn = QPushButton("▆▆▆")
        self.border_color_btn.clicked.connect(lambda: self.choose_color('border_color'))
        colors_layout.addRow("Borde:", self.border_color_btn)
        
        self.text_color_btn = QPushButton("▆▆▆")
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text_color'))
        colors_layout.addRow("Texto:", self.text_color_btn)
        self.colors_group.setLayout(colors_layout)
        layout.addWidget(self.colors_group)

        # --- Posición Canvas ---
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
        edge_layout = QVBoxLayout()
        self.edge_info_label = QLabel("Flecha seleccionada")
        edge_layout.addWidget(self.edge_info_label)
        self.edge_group.setLayout(edge_layout)
        layout.addWidget(self.edge_group)

        # --- Acciones ---
        self.actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        self.delete_button = QPushButton("🗑️ Eliminar Elemento")
        self.delete_button.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold; padding: 6px;")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        actions_layout.addWidget(self.delete_button)
        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)

        self.no_selection_label = QLabel("🔍 Selecciona un elemento")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.no_selection_label)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.update_visibility()

    def on_selection_changed(self, item):
        self.current_selection = item
        if isinstance(item, BaseEdgeItem):
            self.on_edge_selected(item)
        else:
            self.on_node_selected(item)

    def on_edge_selected(self, edge):
        self.update_visibility()

    def on_node_selected(self, node):
        if node and hasattr(node, 'model'):
            self.blockSignals(True)
            # Solo actualizar si el texto es distinto para no mover el cursor
            if self.label_edit.toPlainText() != node.model.label:
                self.label_edit.setPlainText(node.model.label)
            
            self.radius_spin.setValue(int(node.model.radius))
            self.font_size_spin.setValue(int(getattr(node.model, 'font_size', 10)))
            self.text_width_spin.setValue(int(getattr(node.model, 'text_width', 150)))
            
            align = getattr(node.model, 'text_align', 'center')
            self.btn_align_left.setChecked(align == 'left')
            self.btn_align_center.setChecked(align == 'center')
            self.btn_align_right.setChecked(align == 'right')
            self.blockSignals(False)
            self.update_color_buttons()

            if hasattr(node.model, 'position_in_subcanvas_x'):
                self.pos_control.set_position(node.model.position_in_subcanvas_x, node.model.position_in_subcanvas_y)
        self.update_visibility()

    def on_node_property_changed(self):
        if not self.current_selection or not hasattr(self.current_selection, 'model'):
            return
        
        props = {
            'label': self.label_edit.toPlainText(),
            'radius': self.radius_spin.value(),
            'font_size': self.font_size_spin.value(),
            'text_width': self.text_width_spin.value(),
            'text_align': 'left' if self.btn_align_left.isChecked() else 'right' if self.btn_align_right.isChecked() else 'center'
        }
        self.properties_changed.emit(props)

    def on_controller_properties_changed(self, properties: dict):
        # Esta parte es vital para el cursor
        if not self.current_selection: return
        
        self.blockSignals(True)
        if 'label' in properties:
            # Solo actualizamos el widget si el texto realmente cambió externamente
            # y no es lo que el usuario acaba de escribir
            if self.label_edit.toPlainText() != properties['label']:
                self.label_edit.setPlainText(properties['label'])
                # Mover cursor al final por si acaso
                cursor = self.label_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.label_edit.setTextCursor(cursor)
        
        # Actualizar los demás campos sin problemas de cursor
        if 'radius' in properties: self.radius_spin.setValue(int(properties['radius']))
        if 'font_size' in properties: self.font_size_spin.setValue(int(properties['font_size']))
        if 'text_width' in properties: self.text_width_spin.setValue(int(properties['text_width']))
        self.blockSignals(False)
        self.update_color_buttons()

    def update_visibility(self):
        has_selection = self.current_selection is not None
        is_node = has_selection and not isinstance(self.current_selection, BaseEdgeItem)
        is_edge = has_selection and isinstance(self.current_selection, BaseEdgeItem)
        
        is_behaviour_node = False
        has_subcanvas = False
        if is_node:
            type_name = self.current_selection.__class__.__name__
            is_behaviour_node = type_name in ["ActorNodeItem", "AgentNodeItem"]
            has_subcanvas = getattr(self.current_selection.model, 'show_subcanvas', False)

        self.node_group.setVisible(is_node)
        self.colors_group.setVisible(is_node)
        self.pos_group.setVisible(is_behaviour_node and has_subcanvas)
        self.edge_group.setVisible(is_edge)
        self.actions_group.setVisible(has_selection)
        self.no_selection_label.setVisible(not has_selection)

    def choose_color(self, color_type):
        if not self.current_selection: return
        current = QColor(getattr(self.current_selection.model, color_type, "#ffffff"))
        color = QColorDialog.getColor(current, self)
        if color.isValid():
            self.properties_changed.emit({color_type: color.name()})
            self.update_color_buttons()

    def update_color_buttons(self):
        if not self.current_selection or not hasattr(self.current_selection, 'model'): return
        m = self.current_selection.model
        self.color_btn.setStyleSheet(f"background-color: {getattr(m, 'color', '#eee')}; border: 1px solid #999;")
        self.border_color_btn.setStyleSheet(f"background-color: {getattr(m, 'border_color', '#eee')}; border: 1px solid #999;")
        self.text_color_btn.setStyleSheet(f"background-color: {getattr(m, 'text_color', '#eee')}; border: 1px solid #999;")

    def on_delete_clicked(self):
        self.delete_requested.emit()

    def on_position_in_subcanvas_changed(self, x, y):
        if self.current_selection:
            self.properties_changed.emit({'position_in_subcanvas_x': x, 'position_in_subcanvas_y': y})

    def reset_position_in_subcanvas(self):
        self.pos_control.set_position(0, 0)
        self.on_position_in_subcanvas_changed(0, 0)