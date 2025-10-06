# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QColorDialog, QFrame,
                            QSpinBox, QFormLayout, QGroupBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

class PropertiesPanel(QWidget):
    properties_changed = pyqtSignal(dict)
    selection_mode_changed = pyqtSignal(bool)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.current_node = None
        self.selection_mode = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # ✅ Grupo de modo selección (SIEMPRE HABILITADO)
        self.mode_group = QGroupBox("Modo de Interacción")
        mode_layout = QVBoxLayout()
        
        self.selection_toggle = QCheckBox("Modo Selección/Edición")
        self.selection_toggle.setToolTip("Activar para seleccionar y editar nodos. Desactivar para arrastrar nodos libremente.")
        self.selection_toggle.toggled.connect(self.on_selection_mode_toggled)
        mode_layout.addWidget(self.selection_toggle)
        
        mode_info = QLabel("✓ Activado: Click para seleccionar/editar\n✗ Desactivado: Drag & Drop libre")
        mode_info.setStyleSheet("color: #666; font-size: 10px; margin-top: 5px;")
        mode_info.setWordWrap(True)
        mode_layout.addWidget(mode_info)
        
        self.mode_group.setLayout(mode_layout)
        layout.addWidget(self.mode_group)

        # Grupo de propiedades básicas (solo visible cuando hay nodo seleccionado)
        self.basic_group = QGroupBox("Propiedades del Nodo")
        basic_layout = QFormLayout()
        basic_layout.setVerticalSpacing(8)
        
        # Label (nombre)
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Nombre del nodo...")
        self.label_edit.textChanged.connect(self.on_property_changed)
        basic_layout.addRow("Nombre:", self.label_edit)
        
        # Radio
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(10, 500)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.on_property_changed)
        basic_layout.addRow("Radio:", self.radius_spin)
        
        self.basic_group.setLayout(basic_layout)
        layout.addWidget(self.basic_group)

        # Grupo de colores (solo visible cuando hay nodo seleccionado)
        self.colors_group = QGroupBox("Colores")
        colors_layout = QFormLayout()
        colors_layout.setVerticalSpacing(8)
        
        # Color de relleno
        self.color_btn = QPushButton("▆▆▆")
        self.color_btn.clicked.connect(lambda: self.choose_color('color'))
        colors_layout.addRow("Relleno:", self.color_btn)
        
        # Color del borde
        self.border_color_btn = QPushButton("▆▆▆")
        self.border_color_btn.clicked.connect(lambda: self.choose_color('border_color'))
        colors_layout.addRow("Borde:", self.border_color_btn)
        
        # Color del texto
        self.text_color_btn = QPushButton("▆▆▆")
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text_color'))
        colors_layout.addRow("Texto:", self.text_color_btn)
        
        self.colors_group.setLayout(colors_layout)
        layout.addWidget(self.colors_group)

        # ✅ Mensaje cuando no hay nodo seleccionado
        self.no_selection_label = QLabel("🔍 Selecciona un nodo para editar sus propiedades")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setWordWrap(True)
        self.no_selection_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        layout.addWidget(self.no_selection_label)

        layout.addStretch()
        self.setLayout(layout)
        
        # ✅ Inicializar visibilidad
        self.update_visibility()
        
    def on_selection_mode_toggled(self, enabled):
        """Cuando se activa/desactiva el modo selección"""
        self.selection_mode = enabled
        self.selection_mode_changed.emit(enabled)
        
    def update_visibility(self):
        """Actualiza qué elementos son visibles según el estado"""
        has_selection = self.current_node is not None
        
        # ✅ SOLO actualizar visibilidad, NO habilitación
        self.basic_group.setVisible(has_selection)
        self.colors_group.setVisible(has_selection)
        self.no_selection_label.setVisible(not has_selection)
        
    def choose_color(self, color_type):
        if not self.current_node or not hasattr(self.current_node, 'model'):
            return
            
        current_color = QColor(getattr(self.current_node.model, color_type, "#000000"))
        color = QColorDialog.getColor(current_color, self, f"Elegir color {color_type}")
        
        if color.isValid():
            # Actualizar el botón correspondiente
            if color_type == 'color':
                btn = self.color_btn
            elif color_type == 'border_color':
                btn = self.border_color_btn
            elif color_type == 'text_color':
                btn = self.text_color_btn
            else:
                return
                
            btn.setStyleSheet(f"background-color: {color.name()}; color: white; border: 1px solid #ccc;")
            
            # Emitir cambio
            self.properties_changed.emit({color_type: color.name()})
    
    def on_property_changed(self):
        if not self.current_node or not hasattr(self.current_node, 'model'):
            return
            
        properties = {}
        
        if self.label_edit.text() != self.current_node.model.label:
            properties['label'] = self.label_edit.text()
            
        if self.radius_spin.value() != self.current_node.model.radius:
            properties['radius'] = self.radius_spin.value()
            
        if properties:
            self.properties_changed.emit(properties)
    
    def set_node(self, node):
        """Actualiza el panel con las propiedades del nodo seleccionado"""
        self.current_node = node
        
        if node and hasattr(node, 'model'):
            # ✅ NO deshabilitar el panel completo, solo actualizar valores
            self.label_edit.setText(node.model.label)
            self.radius_spin.setValue(int(node.model.radius))
            self.update_color_buttons()
        else:
            self.label_edit.clear()
            
        # ✅ Actualizar visibilidad cuando cambia la selección
        self.update_visibility()
    
    def update_color_buttons(self):
        """Actualiza la apariencia de los botones de color"""
        if not self.current_node or not hasattr(self.current_node, 'model'):
            return
            
        # Mapeo de botones
        color_mapping = {
            'color': self.color_btn,
            'border_color': self.border_color_btn, 
            'text_color': self.text_color_btn
        }
        
        for color_type, btn in color_mapping.items():
            color_value = getattr(self.current_node.model, color_type, "#000000")
            btn.setStyleSheet(f"background-color: {color_value}; color: white; border: 1px solid #ccc;")