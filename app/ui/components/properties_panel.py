# properties_panel.py
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QColorDialog, QFrame,
                            QSpinBox, QFormLayout, QGroupBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from app.ui.components.base_edge_item import BaseEdgeItem

class PropertiesPanel(QWidget):
    properties_changed = pyqtSignal(dict)
    selection_mode_changed = pyqtSignal(bool)
    delete_requested = pyqtSignal()  # ✅ Señal única para eliminar

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.current_selection = None
        self.selection_mode = False
        self.init_ui()
        
        if controller:
            controller.selected_node_properties_changed.connect(self.on_controller_properties_changed)
            controller.selection_changed.connect(self.on_selection_changed)  # ✅ Usar señal unificada

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # ✅ Grupo de propiedades de NODO
        self.node_group = QGroupBox("Propiedades del Nodo")
        node_layout = QFormLayout()
        node_layout.setVerticalSpacing(8)
        
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Nombre del nodo...")
        self.label_edit.textChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Nombre:", self.label_edit)
        
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(10, 500)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.on_node_property_changed)
        node_layout.addRow("Radio:", self.radius_spin)
        
        self.node_group.setLayout(node_layout)
        layout.addWidget(self.node_group)

        # ✅ Grupo de colores de NODO
        self.colors_group = QGroupBox("Colores del Nodo")
        colors_layout = QFormLayout()
        colors_layout.setVerticalSpacing(8)
        
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

        # ✅ Grupo de información de EDGE (solo información)
        self.edge_group = QGroupBox("Flecha Seleccionada")
        edge_layout = QVBoxLayout()
        
        self.edge_info_label = QLabel("Flecha seleccionada")
        self.edge_info_label.setWordWrap(True)
        self.edge_info_label.setStyleSheet("color: #666; padding: 5px;")
        edge_layout.addWidget(self.edge_info_label)
        
        self.edge_group.setLayout(edge_layout)
        layout.addWidget(self.edge_group)

        # ✅ Grupo de acciones - BOTÓN ÚNICO DELETE
        self.actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        self.delete_button = QPushButton("🗑️ Eliminar Elemento")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        actions_layout.addWidget(self.delete_button)
        
        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)

        # ✅ Mensaje cuando no hay selección
        self.no_selection_label = QLabel("🔍 Selecciona un nodo o flecha")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setWordWrap(True)
        self.no_selection_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        layout.addWidget(self.no_selection_label)

        layout.addStretch()
        self.setLayout(layout)
        
        self.update_visibility()

    def on_selection_changed(self, item):
        """Maneja cualquier tipo de selección (nodo o edge)"""
        self.current_selection = item
        
        if isinstance(item, BaseEdgeItem):
            # Es una flecha
            self.on_edge_selected(item)
        else:
            # Es un nodo (o None)
            self.on_node_selected(item)

    def on_edge_selected(self, edge):
        """Actualiza el panel cuando se selecciona una flecha"""
        self.edge_info_label.setText("Flecha seleccionada\n(Usa Delete para eliminar)")
        self.update_visibility()

    def on_node_selected(self, node):
        """Actualiza el panel cuando se selecciona un nodo"""
        if node and hasattr(node, 'model'):
            self.label_edit.setText(node.model.label)
            self.radius_spin.setValue(int(node.model.radius))
            self.update_color_buttons()
        else:
            self.label_edit.clear()
            
        self.update_visibility()

    def choose_color(self, color_type):
        if not self.current_selection or not hasattr(self.current_selection, 'model'):
            return
            
        current_color = QColor(getattr(self.current_selection.model, color_type, "#000000"))
        color = QColorDialog.getColor(current_color, self, f"Elegir color {color_type}")
        
        if color.isValid():
            if color_type == 'color':
                btn = self.color_btn
            elif color_type == 'border_color':
                btn = self.border_color_btn
            elif color_type == 'text_color':
                btn = self.text_color_btn
            else:
                return
                
            btn.setStyleSheet(f"background-color: {color.name()}; color: white; border: 1px solid #ccc;")
            
            self.properties_changed.emit({color_type: color.name()})

    def on_node_property_changed(self):
        if not self.current_selection or not hasattr(self.current_selection, 'model'):
            return
            
        properties = {}
        
        if self.label_edit.text() != self.current_selection.model.label:
            properties['label'] = self.label_edit.text()
            
        if self.radius_spin.value() != self.current_selection.model.radius:
            properties['radius'] = self.radius_spin.value()
            
        if properties:
            self.properties_changed.emit(properties)

    def on_controller_properties_changed(self, properties: dict):
        """Actualiza la UI cuando el controlador notifica cambios de propiedades"""
        if not self.current_selection:
            return
            
        if 'radius' in properties:
            self.radius_spin.blockSignals(True)
            self.radius_spin.setValue(int(properties['radius']))
            self.radius_spin.blockSignals(False)
            
        if 'label' in properties and hasattr(self.current_selection.model, 'label'):
            self.label_edit.blockSignals(True)
            self.label_edit.setText(properties['label'])
            self.label_edit.blockSignals(False)
            
        color_props = ['color', 'border_color', 'text_color']
        if any(prop in properties for prop in color_props):
            self.update_color_buttons()

    def on_delete_clicked(self):
        """Maneja el clic en el botón de eliminar"""
        if not self.current_selection:
            return
            
        # Determinar tipo de elemento
        element_type = "flecha" if isinstance(self.current_selection, BaseEdgeItem) else "nodo"
        element_name = ""
        
        if isinstance(self.current_selection, BaseEdgeItem):
            element_name = "Flecha"
        else:
            element_name = getattr(self.current_selection.model, 'label', 'Nodo sin nombre')
            
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Estás seguro de que quieres eliminar este {element_type}?\n\n"
            f"Elemento: {element_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit()

    def update_visibility(self):
        """Actualiza qué elementos son visibles según el estado"""
        has_selection = self.current_selection is not None
        is_node = has_selection and not isinstance(self.current_selection, BaseEdgeItem)
        is_edge = has_selection and isinstance(self.current_selection, BaseEdgeItem)
        
        self.node_group.setVisible(is_node)
        self.colors_group.setVisible(is_node)
        self.edge_group.setVisible(is_edge)
        self.actions_group.setVisible(has_selection)
        self.no_selection_label.setVisible(not has_selection)

    def update_color_buttons(self):
        """Actualiza la apariencia de los botones de color"""
        if not self.current_selection or not hasattr(self.current_selection, 'model'):
            return
            
        color_mapping = {
            'color': self.color_btn,
            'border_color': self.border_color_btn, 
            'text_color': self.text_color_btn
        }
        
        for color_type, btn in color_mapping.items():
            color_value = getattr(self.current_selection.model, color_type, "#000000")
            btn.setStyleSheet(f"background-color: {color_value}; color: white; border: 1px solid #ccc;")