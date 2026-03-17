# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QRadioButton, QButtonGroup, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class PDFExportDialog(QDialog):
    """Dialogo para seleccionar el tipo de exportación PDF"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar a PDF")
        self.setModal(True)
        self.resize(400, 250)
        
        self.export_with_info = True  # Default: con información adicional
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("¿Qué desea incluir en el PDF?")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Grupo de opciones
        options_group = QGroupBox("Opciones de exportación")
        options_layout = QVBoxLayout(options_group)
        
        # Botones de radio
        self.radio_image_only = QRadioButton(
            "Solo imagen del diagrama"
        )
        self.radio_image_only.setStyleSheet("font-size: 12px;")
        self.radio_image_only.toggled.connect(self._on_option_changed)
        options_layout.addWidget(self.radio_image_only)
        
        self.radio_with_info = QRadioButton(
            "Imagen del diagrama + Información adicional de elementos"
        )
        self.radio_with_info.setChecked(True)
        self.radio_with_info.setStyleSheet("font-size: 12px;")
        self.radio_with_info.toggled.connect(self._on_option_changed)
        options_layout.addWidget(self.radio_with_info)
        
        # Descripción
        info_label = QLabel(
            "La información adicional incluye:\n"
            "• Lista de elementos con su clasificación (Actor, Agente, Meta, etc.)\n"
            "• Relaciones entre elementos (dependencias, descomposiciones, etc.)"
        )
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_label.setWordWrap(True)
        options_layout.addWidget(info_label)
        
        layout.addWidget(options_group)
        
        # Botones de acción
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_option_changed(self):
        self.export_with_info = self.radio_with_info.isChecked()
    
    def should_export_with_info(self) -> bool:
        """Retorna True si se debe exportar con información adicional"""
        return self.export_with_info
