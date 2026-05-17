# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QDialogButtonBox
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtWidgets import QVBoxLayout

from app.ui.theme_manager import theme_manager


class PDFExportDialog(QDialog):
    """
    P D F Export Dialog.

    Methods:
        __init__: Initialize the instance.
        should_export_with_info: Should Export With Info.
    """

    def __init__(self, parent=None):
        """
        Initialize the instance.

        Args:
            parent: The parent.
        """
        super().__init__(parent)
        self.setWindowTitle("Exportar a PDF")
        self.setModal(True)
        self.resize(400, 250)

        self.export_with_info: bool = True

        self._setup_ui()

    def _setup_ui(self):
        """Setup Ui."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        dark = theme_manager().is_dark

        # Title
        title_label = QLabel("¿Qué desea incluir en el PDF?")
        if dark:
            title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #e0e0e0;"
            )
        else:
            title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # Grupo de opciones
        options_group = QGroupBox("Opciones de exportación")
        options_layout = QVBoxLayout(options_group)

        # Buttons of radius
        self.radio_image_only = QRadioButton("Solo imagen del diagrama")
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
        if dark:
            info_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        else:
            info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_label.setWordWrap(True)
        options_layout.addWidget(info_label)

        layout.addWidget(options_group)

        # Buttons of action
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_option_changed(self) -> None:
        """On Option Changed."""
        self.export_with_info = self.radio_with_info.isChecked()

    def should_export_with_info(self) -> bool:
        """
        Should Export With Info.

        Returns:
            bool: Should Export With Info.
        """
        return self.export_with_info
