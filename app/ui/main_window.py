# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QSplitter, QScrollArea, QGroupBox
)
from PyQt6.QtCore import pyqtSlot, Qt

from app.ui.canvas import Canvas
from app.ui.sidebar import Sidebar
from app.ui.components.properties_panel import PropertiesPanel
from app.controllers.canvas_controller import CanvasController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteroid")
        self.resize(1600, 900)  # ✅ Más ancho para tres paneles

        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        ## Instancias de UI
        self.canvas = Canvas()
        self.canvas_controller = CanvasController(self.canvas)
        
        # ✅ Sidebar con scroll y mejor organización
        self.sidebar = Sidebar(controller=self.canvas_controller)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidget(self.sidebar)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setMaximumWidth(300)  # Ancho fijo para sidebar
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # ✅ Panel de propiedades a la derecha
        self.properties_panel = PropertiesPanel(controller=self.canvas_controller)
        properties_scroll = QScrollArea()
        properties_scroll.setWidget(self.properties_panel)
        properties_scroll.setWidgetResizable(True)
        properties_scroll.setMaximumWidth(300)  # Ancho fijo para propiedades
        properties_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        properties_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # ✅ Conectar señales entre controlador y panel de propiedades
        #self.canvas_controller.node_selected.connect(self.properties_panel.set_node)
        self.canvas_controller.node_selected.connect(self.properties_panel.on_node_selected)
        self.properties_panel.properties_changed.connect(self.canvas_controller.update_node_properties)
        self.properties_panel.selection_mode_changed.connect(self.canvas_controller.set_selection_mode)
        
        # ✅ Conectar señales unificadas
        self.canvas_controller.selection_changed.connect(self.properties_panel.on_selection_changed)
        self.properties_panel.delete_requested.connect(self.canvas_controller.delete_selected_item)

        # ✅ Conectar la señal de eliminación del panel al controlador
        #self.properties_panel.delete_node_requested.connect(
        #    self.canvas_controller.delete_selected_node
        #)

        # ------------------
        # Controles de zoom (ahora en la parte inferior del canvas)
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
        canvas_layout.addWidget(self.canvas, 1)  # Canvas ocupa máximo espacio
        canvas_layout.addWidget(zoom_widget)     # Zoom en la parte inferior

        # ------------------
        # Splitter principal con tres áreas
        # ------------------
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Área izquierda: Sidebar con scroll
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(sidebar_scroll)
        main_splitter.addWidget(left_container)
        
        # Área central: Canvas con controles de zoom
        main_splitter.addWidget(canvas_container)
        
        # Área derecha: Panel de propiedades
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(properties_scroll)
        main_splitter.addWidget(right_container)

        # Configurar tamaños iniciales
        main_splitter.setSizes([300, 1000, 300])  # sidebar, canvas, properties

        main_layout.addWidget(main_splitter)

        # Inicializar label
        self.update_zoom_label()

    @pyqtSlot()
    def update_zoom_label(self):
        zoom_percentage = int(self.canvas.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")