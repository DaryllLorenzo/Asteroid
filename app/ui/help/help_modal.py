# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.i18n import tr

from app.ui.theme_manager import theme_manager
from .markdown_viewer import MarkdownViewer


class HelpModal(QDialog):
    """
    Help Modal.

    Methods:
        __init__: Initialize the instance.
    """

    def __init__(self, title, md_file_path, parent=None):
        """
        Initialize the instance.

        Args:
            title: The title.
            md_file_path: The md file path.
            parent: The parent.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)

        # Configure style of the dialog - PROFESSIONAL
        dark = theme_manager().is_dark
        if dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 10px;
                }
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    padding: 10px 25px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 25px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
                QPushButton:pressed {
                    background-color: #1d6fa5;
                    padding: 11px 26px 9px 24px;
                }
                QPushButton:focus {
                    outline: 2px solid rgba(52, 152, 219, 0.5);
                    outline-offset: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 10px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 25px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 25px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1d6fa5;
                    padding: 11px 26px 9px 24px;
                }
                QPushButton:focus {
                    outline: 2px solid rgba(52, 152, 219, 0.5);
                    outline-offset: 2px;
                }
            """)

        # Layout main with margins elegant
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create visor of markdown
        self.viewer = MarkdownViewer()

        # Aplicar style al QTextBrowser for borders redondeados, etc.
        if dark:
            self.viewer.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #1e1e1e;
                    border: 2px solid #555555;
                    border-radius: 8px;
                    padding: 0px;
                }
                QScrollBar:vertical {
                    background: #2d2d2d;
                    width: 14px;
                    border-radius: 7px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical {
                    background: #555555;
                    border-radius: 7px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #777777;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0;
                }
                QScrollBar:horizontal {
                    background: #2d2d2d;
                    height: 14px;
                    border-radius: 7px;
                    margin: 2px;
                }
                QScrollBar::handle:horizontal {
                    background: #555555;
                    border-radius: 7px;
                    min-width: 30px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #777777;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    width: 0;
                }
                QTextBrowser QAbstractScrollArea::viewport {
                    border: none;
                    background: #1e1e1e;
                }
            """)
        else:
            self.viewer.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: white;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 0px;
                }
                QScrollBar:vertical {
                    background: #f8f9fa;
                    width: 14px;
                    border-radius: 7px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical {
                    background: #c1c9d1;
                    border-radius: 7px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #a8b1bb;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0;
                }
                QScrollBar:horizontal {
                    background: #f8f9fa;
                    height: 14px;
                    border-radius: 7px;
                    margin: 2px;
                }
                QScrollBar::handle:horizontal {
                    background: #c1c9d1;
                    border-radius: 7px;
                    min-width: 30px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #a8b1bb;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    width: 0;
                }
                QTextBrowser QAbstractScrollArea::viewport {
                    border: none;
                    background: white;
                }
            """)

        main_layout.addWidget(self.viewer, 1)  # The 1 hace that itself expanda

        # Container for the button with alignment centered
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 15, 0, 0)

        close_btn = QPushButton(tr("Close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedSize(120, 42)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Style adicional for the button
        if dark:
            close_btn.setStyleSheet("""
                QPushButton {
                    font-size: 25px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }
            """)
        else:
            close_btn.setStyleSheet("""
                QPushButton {
                    font-size: 25px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }
            """)

        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        main_layout.addWidget(button_container)

        # Load the file markdown
        self.viewer.load_markdown(md_file_path)

        # Foco in the button by defecto
        close_btn.setFocus()

        # Añadir sombra of window (efecto visual)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
