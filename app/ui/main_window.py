# main_window.py
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QSplitter, QScrollArea, QGroupBox, QMessageBox, QMenuBar, QMenu
)
from PyQt6.QtCore import pyqtSlot, Qt
from pathlib import Path

from app.ui.canvas import Canvas
from app.ui.sidebar import Sidebar
from app.ui.components.properties_panel import PropertiesPanel
from app.controllers.canvas_controller import CanvasController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteroid")
        self.resize(1600, 900)

        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        ## Instancias de UI
        self.canvas = Canvas()
        self.canvas_controller = CanvasController(self.canvas)
        
        # Sidebar con scroll
        self.sidebar = Sidebar(controller=self.canvas_controller)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidget(self.sidebar)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setMaximumWidth(300)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Panel de propiedades
        self.properties_panel = PropertiesPanel(controller=self.canvas_controller)
        properties_scroll = QScrollArea()
        properties_scroll.setWidget(self.properties_panel)
        properties_scroll.setWidgetResizable(True)
        properties_scroll.setMaximumWidth(300)
        properties_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        properties_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Conectar señales
        self.canvas_controller.node_selected.connect(self.properties_panel.on_node_selected)
        self.properties_panel.properties_changed.connect(self.canvas_controller.update_node_properties)
        self.properties_panel.selection_mode_changed.connect(self.canvas_controller.set_selection_mode)
        
        # Conectar señales unificadas
        self.canvas_controller.selection_changed.connect(self.properties_panel.on_selection_changed)
        self.properties_panel.delete_requested.connect(self.canvas_controller.delete_selected_item)

        # Conectar señal de modificación del proyecto
        self.canvas_controller.project_modified.connect(self.on_project_modified)

        # ------------------
        # Controles de zoom
        # ------------------
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(5, 5, 5, 5)

        zoom_out_btn = QPushButton("-")
        self.zoom_label = QPushButton("100%")
        zoom_in_btn = QPushButton("+")

        zoom_out_btn.clicked.connect(self.canvas.zoom_out)
        self.zoom_label.clicked.connect(self.canvas.reset_zoom)
        zoom_in_btn.clicked.connect(self.canvas.zoom_in)
        self.canvas.zoom_changed.connect(self.update_zoom_label)

        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)

        # ------------------
        # Layout del canvas con controles de zoom
        # ------------------
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas, 1)
        canvas_layout.addWidget(zoom_widget)

        # ------------------
        # Splitter principal con tres áreas
        # ------------------
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Área izquierda: Sidebar
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(sidebar_scroll)
        main_splitter.addWidget(left_container)
        
        # Área central: Canvas
        main_splitter.addWidget(canvas_container)
        
        # Área derecha: Panel de propiedades
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(properties_scroll)
        main_splitter.addWidget(right_container)

        # Configurar tamaños iniciales
        main_splitter.setSizes([300, 1000, 300])

        main_layout.addWidget(main_splitter)

        # Inicializar label
        self.update_zoom_label()

        # Crear barra de menú
        self.create_menu_bar()

        # Actualizar título inicial
        self.update_window_title()

    @pyqtSlot()
    def update_zoom_label(self):
        zoom_percentage = int(self.canvas.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")

    def on_project_modified(self, modified):
        """Se llama cuando el estado de modificación del proyecto cambia"""
        self.update_window_title()

    def update_window_title(self):
        """Actualiza el título de la ventana con el estado del proyecto"""
        base_title = "Asteroid"
        if self.canvas_controller._current_file_path:
            file_name = Path(self.canvas_controller._current_file_path).name
            title = f"{base_title} - {file_name}"
        else:
            title = f"{base_title} - Proyecto sin título"
        
        if self.canvas_controller.is_modified:
            title += " *"
        
        self.setWindowTitle(title)
    
    def create_menu_bar(self):
        """Crea la barra de menú con las opciones de archivo"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('&Archivo')
        
        # Acción para nuevo proyecto
        new_action = file_menu.addAction('&Nuevo proyecto')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        
        # Acción para cargar .astr
        load_action = file_menu.addAction('&Cargar proyecto...')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_project)
        
        # Acción para guardar .astr
        save_action = file_menu.addAction('&Guardar proyecto...')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        
        # Separador
        file_menu.addSeparator()
        
        # Acción para exportar imagen
        export_image_action = file_menu.addAction('&Exportar como imagen...')
        export_image_action.setShortcut('Ctrl+E')
        export_image_action.triggered.connect(self.export_image)
    
    def load_project(self):
        """Carga un proyecto .astr"""
        if self.check_unsaved_changes():
            success = self.canvas_controller.import_from_astr()
            if success:
                self.update_window_title()

    def save_project(self) -> bool:
        """Guarda el proyecto actual como .astr"""
        success = self.canvas_controller.export_to_astr()
        if success:
            self.update_window_title()
        return success

    def export_image(self):
        """Exporta el canvas como imagen"""
        self.canvas_controller.export_to_image()
    
    def new_project(self):
        """Crea un nuevo proyecto"""
        if self.check_unsaved_changes():
            self.canvas_controller.clear_canvas()
            self.update_window_title()
    
    def check_unsaved_changes(self) -> bool:
        """
        Verifica si hay cambios sin guardar.
        Retorna True si puede continuar, False si debe cancelar.
        """
        if not self.canvas_controller.is_modified:
            return True
        
        reply = QMessageBox.question(
            self,
            'Cambios sin guardar',
            '¿Desea guardar los cambios del proyecto actual?',
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return self.save_project()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()