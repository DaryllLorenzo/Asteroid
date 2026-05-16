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

from app.i18n import tr


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
        self.setWindowTitle(tr("Export to PDF"))
        self.setModal(True)
        self.resize(400, 250)

        self.export_with_info: bool = True

        self._setup_ui()

    def _setup_ui(self):
        """Setup Ui."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(tr("What would you like to include in the PDF?"))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # Export options
        options_group = QGroupBox(tr("Export options"))
        options_layout = QVBoxLayout(options_group)

        self.radio_image_only = QRadioButton(tr("Diagram image only"))
        self.radio_image_only.setStyleSheet("font-size: 12px;")
        self.radio_image_only.toggled.connect(self._on_option_changed)
        options_layout.addWidget(self.radio_image_only)

        self.radio_with_info = QRadioButton(
            tr("Diagram image + Additional element information")
        )
        self.radio_with_info.setChecked(True)
        self.radio_with_info.setStyleSheet("font-size: 12px;")
        self.radio_with_info.toggled.connect(self._on_option_changed)
        options_layout.addWidget(self.radio_with_info)

        info_label = QLabel(
            tr("Additional information includes:\n• List of elements with their classification (Actor, Agent, Goal, etc.)\n• Relationships between elements (dependencies, decompositions, etc.)")
        )
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
