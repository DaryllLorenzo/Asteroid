# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.controllers.canvas_controller import CanvasController
from app.i18n import get_language
from app.i18n import load_language
from app.i18n import tr
from app.ui.canvas import Canvas
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.properties_panel import PropertiesPanel
from app.ui.help.help_modal import HelpModal
from app.ui.pdf_export_dialog import PDFExportDialog
from app.ui.sidebar import Sidebar
from app.ui.theme_manager import generate_stylesheet
from app.ui.theme_manager import theme_manager
from app.utils.agent_report_export import AgentReportExporter
from app.utils.pdf_export import PDFGenerator


class MainWindow(QMainWindow):
    """
    Main Window.

    Methods:
        __init__: Initialize the instance.
        update_zoom_label: Update Zoom Label.
        on_project_modified: On Project Modified.
        update_window_title: Update Window Title.
        create_menu_bar: Create Menu Bar.
        load_project: Load Project.
        save_project: Save Project.
        export_image: Export Image.
        export_pdf: Export Pdf.
        new_project: New Project.
        check_unsaved_changes: Check Unsaved Changes.
        closeEvent: Closeevent.
        get_help_file_path: Get Help File Path.
        show_elements_help: Show Elements Help.
        show_examples_help: Show Examples Help.
        show_about_help: Show About Help.
        show_validation_help: Show Validation Help.
        show_quick_help: Show Quick Help.
    """

    def __init__(self):
        """Initialize the instance."""
        super().__init__()
        settings = QSettings("Asteroid", "Asteroid")
        saved_lang = settings.value("language", "en")
        load_language(saved_lang)
        self.setWindowTitle(tr("Asteroid"))
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
        sidebar_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Panel of properties
        self.properties_panel = PropertiesPanel(controller=self.canvas_controller)
        properties_scroll = QScrollArea()
        properties_scroll.setWidget(self.properties_panel)
        properties_scroll.setWidgetResizable(True)
        properties_scroll.setMaximumWidth(300)
        properties_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        properties_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Conectar señales
        self.canvas_controller.node_selected.connect(
            self.properties_panel.on_node_selected
        )
        self.properties_panel.properties_changed.connect(
            self.canvas_controller.update_node_properties
        )
        self.properties_panel.selection_mode_changed.connect(
            self.canvas_controller.set_selection_mode
        )

        # Conectar señales unificadas
        self.canvas_controller.selection_changed.connect(
            self.properties_panel.on_selection_changed
        )
        self.properties_panel.delete_requested.connect(
            self.canvas_controller.delete_selected_item
        )

        # Conectar signal of modificación of the project
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
        # Layout of the canvas with controles of zoom
        # ------------------
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas, 1)
        canvas_layout.addWidget(zoom_widget)

        # ------------------
        # Splitter main with tres áreas
        # ------------------
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Área left: Sidebar
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(sidebar_scroll)
        main_splitter.addWidget(left_container)

        # Área central: Canvas
        main_splitter.addWidget(canvas_container)

        # Área right: Panel of properties
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(properties_scroll)
        main_splitter.addWidget(right_container)

        # Configure tamaños iniciales
        main_splitter.setSizes([300, 1000, 300])

        main_layout.addWidget(main_splitter)

        # Theme manager (before menu bar creation)
        self._tm = theme_manager()
        self._tm.theme_changed.connect(self._on_theme_changed)

        # Initialize label
        self.update_zoom_label()

        # Create bar of menú
        self.create_menu_bar()

        # Apply initial theme
        self._on_theme_changed(self._tm.is_dark)

        # Conectar signals of undo stack for update menú
        self.canvas_controller.undo_stack.canUndoChanged.connect(
            self._update_undo_redo_actions
        )
        self.canvas_controller.undo_stack.canRedoChanged.connect(
            self._update_undo_redo_actions
        )
        self.canvas_controller.undo_stack.indexChanged.connect(
            self._update_undo_redo_texts
        )

        # Update title initial
        self.update_window_title()

    @pyqtSlot()
    def update_zoom_label(self):
        """Update Zoom Label."""
        zoom_percentage = int(self.canvas.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")

    def on_project_modified(self, modified):
        """
        On Project Modified.

        Args:
            modified: The modified.
        """
        self.update_window_title()

    def _update_undo_redo_actions(self):
        """Update Undo Redo Actions."""
        self.undo_action.setEnabled(self.canvas_controller.undo_stack.canUndo())
        self.redo_action.setEnabled(self.canvas_controller.undo_stack.canRedo())

    def _update_undo_redo_texts(self):
        """Update Undo Redo Texts."""
        undo_text = self.canvas_controller.undo_stack.undoText()
        redo_text = self.canvas_controller.undo_stack.redoText()
        self.undo_action.setText(f"{tr('&Undo')}{' ' + undo_text if undo_text else ''}")
        self.redo_action.setText(f"{tr('&Redo')}{' ' + redo_text if redo_text else ''}")

    def update_window_title(self):
        """Update Window Title."""
        if self.canvas_controller._current_file_path:
            file_name = Path(self.canvas_controller._current_file_path).name
            title = f"{tr('Asteroid')} - {file_name}"
        else:
            title = f"{tr('Asteroid')} - {tr('Untitled project')}"

        if self.canvas_controller.is_modified:
            title += " *"

        self.setWindowTitle(title)

    def create_menu_bar(self):
        """Create Menu Bar."""
        menubar = self.menuBar()

        # File menu
        self.file_menu = menubar.addMenu(tr("&File"))
        file_menu = self.file_menu

        self.new_action = file_menu.addAction(tr("&New project"))
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_project)

        self.load_action = file_menu.addAction(tr("&Load project..."))
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load_project)

        self.save_action = file_menu.addAction(tr("&Save project..."))
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_project)

        file_menu.addSeparator()

        self.export_image_action = file_menu.addAction(tr("&Export as image..."))
        self.export_image_action.setShortcut("Ctrl+E")
        self.export_image_action.triggered.connect(self.export_image)

        file_menu.addSeparator()

        self.export_pdf_action = file_menu.addAction(tr("&Export to PDF..."))
        self.export_pdf_action.setShortcut("Ctrl+P")
        self.export_pdf_action.triggered.connect(self.export_pdf)

        file_menu.addSeparator()

        self.export_agents_action = file_menu.addAction(tr("&Export agent reports..."))
        self.export_agents_action.triggered.connect(self.export_agent_reports)

        # Edit menu
        self.edit_menu = menubar.addMenu(tr("&Edit"))
        edit_menu = self.edit_menu

        self.undo_action = edit_menu.addAction(tr("&Undo"))
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.canvas_controller.undo_stack.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = edit_menu.addAction(tr("&Redo"))
        self.redo_action.setShortcuts(["Ctrl+Y", "Ctrl+Shift+Z"])
        self.redo_action.triggered.connect(self.canvas_controller.undo_stack.redo)
        self.redo_action.setEnabled(False)

        # Separator
        file_menu.addSeparator()

        # ---------------------------
        # Menú Ver (tema)
        # ---------------------------
        self.view_menu = menubar.addMenu(tr("&View"))

        self.theme_action = self.view_menu.addAction(tr("&Dark mode"))
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(self._tm.is_dark)
        self.theme_action.triggered.connect(self._tm.toggle)

        # ---------------------------
        # Menú Validación
        # ---------------------------

        self.validation_menu = menubar.addMenu(tr("&Validation"))
        validation_menu = self.validation_menu

        self.validation_action = validation_menu.addAction(tr("&Validator mode"))
        self.validation_action.setCheckable(True)
        self.validation_action.setChecked(False)
        self.validation_action.triggered.connect(self._toggle_validator)

        # Language menu
        self.lang_menu = menubar.addMenu(tr("&Language"))
        lang_menu = self.lang_menu
        self.en_action = lang_menu.addAction(tr("&English"))
        self.en_action.setCheckable(True)
        self.en_action.setChecked(get_language() == "en")
        self.en_action.triggered.connect(lambda: self._change_language("en"))

        self.es_action = lang_menu.addAction(tr("&Spanish"))
        self.es_action.setCheckable(True)
        self.es_action.setChecked(get_language() == "es")
        self.es_action.triggered.connect(lambda: self._change_language("es"))

        # Help menu
        self.help_menu = menubar.addMenu(tr("&Help"))
        help_menu = self.help_menu

        self.elements_action = help_menu.addAction(tr("&Elements"))
        self.elements_action.triggered.connect(self.show_elements_help)

        self.examples_action = help_menu.addAction(tr("&Examples"))
        self.examples_action.triggered.connect(self.show_examples_help)

        self.validation_help_action = help_menu.addAction(tr("&Validator mode"))
        self.validation_help_action.triggered.connect(self.show_validation_help)

        self.quick_help_action = help_menu.addAction(tr("&Quick help"))
        self.quick_help_action.setShortcut("F1")
        self.quick_help_action.triggered.connect(self.show_quick_help)

        help_menu.addSeparator()

        self.about_action = help_menu.addAction(tr("&About Asteroid"))
        self.about_action.triggered.connect(self.show_about_help)

    def _toggle_validator(self, checked: bool) -> None:
        """
        Toggle Validator.

        Args:
            checked (bool): The checked.
        """
        self.canvas_controller.validator.active = checked

    def _on_theme_changed(self, dark: bool) -> None:
        """On Theme Changed."""
        self.theme_action.setChecked(dark)

        # Apply QSS to app
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(generate_stylesheet(dark))

        # Update canvas background
        self.canvas.apply_theme(dark)

        # Update edges
        scene = self.canvas.scene()
        if scene:
            for item in scene.items():
                if isinstance(item, BaseEdgeItem):
                    item.update_theme()
                else:
                    item.update()

    def load_project(self):
        """Load Project."""
        if self.check_unsaved_changes():
            success = self.canvas_controller.import_from_astr()
            if success:
                self.update_window_title()

    def save_project(self) -> bool:
        """
        Save Project.

        Returns:
            bool: Save Project.
        """
        success = self.canvas_controller.export_to_astr()
        if success:
            self.update_window_title()
        return bool(success)

    def export_image(self):
        """Export Image."""
        self.canvas_controller.export_to_image()

    def export_pdf(self):
        """Export Pdf."""
        # Show dialog of opciones
        dialog = PDFExportDialog(self)
        if dialog.exec() != 1:  # QDialog.Accepted
            return

        # Generate PDF
        with_info = dialog.should_export_with_info()
        pdf_generator = PDFGenerator(self.canvas_controller)
        pdf_generator.export_to_pdf(with_additional_info=with_info)

    def export_agent_reports(self):
        """Export Agent Reports."""
        from PyQt6.QtWidgets import QFileDialog

        output_dir = QFileDialog.getExistingDirectory(
            self, tr("Select output folder for agent reports"), ""
        )
        if not output_dir:
            return

        exporter = AgentReportExporter(self.canvas_controller)
        success = exporter.export_reports(output_dir)

        if success:
            QMessageBox.information(
                self,
                tr("Export complete"),
                tr("Agent reports exported successfully to:\n{path}").format(
                    path=output_dir
                ),
            )
        else:
            QMessageBox.warning(
                self,
                tr("Export failed"),
                tr("No top-level agents found in the diagram."),
            )

    def new_project(self):
        """New Project."""
        if self.check_unsaved_changes():
            self.canvas_controller.clear_canvas()
            self.update_window_title()

    def _change_language(self, lang: str) -> None:
        """Change Language."""
        load_language(lang)
        settings = QSettings("Asteroid", "Asteroid")
        settings.setValue("language", lang)
        self.en_action.setChecked(lang == "en")
        self.es_action.setChecked(lang == "es")
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Retranslate all UI elements."""
        self.update_window_title()
        self._retranslate_menus()
        self.sidebar.retranslate()
        self.properties_panel.retranslate()

    def _retranslate_menus(self) -> None:
        """Retranslate menu texts."""
        self.new_action.setText(tr("&New project"))
        self.load_action.setText(tr("&Load project..."))
        self.save_action.setText(tr("&Save project..."))
        self.export_image_action.setText(tr("&Export as image..."))
        self.export_pdf_action.setText(tr("&Export to PDF..."))
        self.export_agents_action.setText(tr("&Export agent reports..."))
        self.undo_action.setText(tr("&Undo"))
        self.redo_action.setText(tr("&Redo"))
        self.validation_action.setText(tr("&Validator mode"))
        self.en_action.setText(tr("&English"))
        self.es_action.setText(tr("&Spanish"))
        self.elements_action.setText(tr("&Elements"))
        self.examples_action.setText(tr("&Examples"))
        self.validation_help_action.setText(tr("&Validator mode"))
        self.quick_help_action.setText(tr("&Quick help"))
        self.about_action.setText(tr("&About Asteroid"))

        self.file_menu.setTitle(tr("&File"))
        self.edit_menu.setTitle(tr("&Edit"))
        self.view_menu.setTitle(tr("&View"))
        self.validation_menu.setTitle(tr("&Validation"))
        self.lang_menu.setTitle(tr("&Language"))
        self.help_menu.setTitle(tr("&Help"))

        self.theme_action.setText(tr("&Dark mode"))

    def check_unsaved_changes(self) -> bool:
        """
        Check Unsaved Changes.

        Returns:
            bool: Check Unsaved Changes.
        """
        if not self.canvas_controller.is_modified:
            return True

        reply = QMessageBox.question(
            self,
            tr("Unsaved changes"),
            tr("Do you want to save the current project?"),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_project()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False

    def closeEvent(self, event):
        """
        Closeevent.

        Args:
            event: The event.
        """
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()

    # ---------------------------
    # Métodos for show ayuda
    # ---------------------------

    def get_help_file_path(self, filename):
        """
        Get Help File Path.

        Args:
            filename: The filename.
        """
        current_dir = Path(__file__).parent
        lang_dir = current_dir / "help" / "content" / get_language()
        if lang_dir.exists():
            return lang_dir / filename
        return current_dir / "help" / "content" / filename

    def show_elements_help(self):
        """Show Elements Help."""
        md_file = self.get_help_file_path("elements.md")
        dialog = HelpModal(tr("Asteroid Elements"), md_file, self)
        dialog.exec()

    def show_examples_help(self):
        """Show Examples Help."""
        md_file = self.get_help_file_path("examples.md")
        dialog = HelpModal(tr("Usage Examples"), md_file, self)
        dialog.exec()

    def show_about_help(self):
        """Show About Help."""
        md_file = self.get_help_file_path("about.md")
        dialog = HelpModal(tr("About Asteroid"), md_file, self)
        dialog.exec()

    def show_validation_help(self):
        """Show Validation Help."""
        md_file = self.get_help_file_path("validation_help.md")
        dialog = HelpModal(tr("Validator Mode"), md_file, self)
        dialog.exec()

    def show_quick_help(self):
        """Show Quick Help."""
        md_file = self.get_help_file_path("quick_help.md")
        dialog = HelpModal(tr("Quick Help - Keyboard Shortcuts"), md_file, self)
        dialog.exec()
