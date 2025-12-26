# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from .markdown_viewer import MarkdownViewer

class HelpModal(QDialog):
    def __init__(self, title, md_file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)
        
        # Configurar estilo del diálogo - PROFESIONAL
        self.setStyleSheet("""
            /* ===== DIÁLOGO PRINCIPAL ===== */
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
            }
            
            /* ===== BOTONES ===== */
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
        
        # Layout principal con márgenes elegantes
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Crear visor de markdown
        self.viewer = MarkdownViewer()
        
        # Aplicar estilo al QTextBrowser para bordes redondeados, etc.
        self.viewer.text_browser.setStyleSheet("""
            /* ===== QTextBrowser ===== */
            QTextBrowser {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 0px;
            }
            
            /* ===== SCROLLBAR VERTICAL ===== */
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
            
            /* ===== SCROLLBAR HORIZONTAL ===== */
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
            
            /* ===== BORDES DEL VIEWPORT ===== */
            QTextBrowser QAbstractScrollArea::viewport {
                border: none;
                background: white;
            }
        """)
        
        main_layout.addWidget(self.viewer, 1)  # El 1 hace que se expanda
        
        # Contenedor para el botón con alineación centrada
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        # Botón de cerrar elegante
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedSize(120, 42)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilo adicional para el botón
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
        
        # Cargar el archivo markdown
        self.viewer.load_markdown(md_file_path)
        
        # Foco en el botón por defecto
        close_btn.setFocus()
        
        # Añadir sombra de ventana (efecto visual)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)