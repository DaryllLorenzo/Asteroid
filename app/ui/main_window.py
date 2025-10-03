# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

# main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
)
from PyQt6.QtCore import pyqtSlot

from app.ui.canvas import Canvas
from app.ui.sidebar import Sidebar

from app.controllers.canvas_controller import CanvasController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteroid")
        self.resize(1200, 800)

        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(main_widget)

        # Layout vertical para sidebar + controles
        sidebar_layout = QVBoxLayout()

        ## Instancias de UI
        #self.sidebar = Sidebar()
        #self.canvas = Canvas()
#
        ## Conectar controlador
        #self.canvas_controller = CanvasController(self.canvas)

        # Instancias de UI
        self.canvas = Canvas()
        self.canvas_controller = CanvasController(self.canvas)   # crear controlador primero
        self.sidebar = Sidebar(controller=self.canvas_controller)  # pasar controlador

        # ------------------
        # Controles de zoom
        # ------------------
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)

        zoom_out_btn = QPushButton("-")
        self.zoom_label = QPushButton("100%")
        zoom_in_btn = QPushButton("+")

        zoom_out_btn.clicked.connect(self.canvas.zoom_out)
        self.zoom_label.clicked.connect(self.canvas.reset_zoom)
        zoom_in_btn.clicked.connect(self.canvas.zoom_in)

        # Conectar señal del canvas
        self.canvas.zoom_changed.connect(self.update_zoom_label)

        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)

        # ------------------
        # Sidebar + zoom
        # ------------------
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addWidget(zoom_widget)
        sidebar_layout.addStretch()

        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar_layout)

        # Agregar al layout principal
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.canvas)

        # Inicializar label
        self.update_zoom_label()

    # ------------------
    # Slots
    # ------------------
    @pyqtSlot()
    def update_zoom_label(self):
        zoom_percentage = int(self.canvas.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")
