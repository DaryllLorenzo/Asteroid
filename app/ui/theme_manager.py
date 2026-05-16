from dataclasses import dataclass

from PyQt6.QtCore import QObject
from PyQt6.QtCore import QSettings
from PyQt6.QtCore import pyqtSignal


@dataclass
class ThemeColors:
    canvas_bg: str
    node_border: str
    node_text: str
    edge_color: str
    subcanvas_border: str
    subcanvas_fill: str
    control_point_border: str
    control_point_fill: str
    control_point_hover: str
    control_point_selected: str


LIGHT_THEME = ThemeColors(
    canvas_bg="#ffffff",
    node_border="#000000",
    node_text="#ffffff",
    edge_color="#000000",
    subcanvas_border="#000000",
    subcanvas_fill="#ffffff",
    control_point_border="#0064c8",
    control_point_fill="#ffffff",
    control_point_hover="#c8e6ff",
    control_point_selected="#0064c8",
)

DARK_THEME = ThemeColors(
    canvas_bg="#2b2b2b",
    node_border="#ffffff",
    node_text="#ffffff",
    edge_color="#ffffff",
    subcanvas_border="#ffffff",
    subcanvas_fill="#ffffff",
    control_point_border="#64b5f6",
    control_point_fill="#2b2b2b",
    control_point_hover="#1e3a5f",
    control_point_selected="#64b5f6",
)


class ThemeManager(QObject):
    theme_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark = False
        self._load()

    def _load(self):
        settings = QSettings("Asteroid", "Asteroid")
        self._is_dark = settings.value("theme/dark", False, type=bool)

    def _save(self):
        settings = QSettings("Asteroid", "Asteroid")
        settings.setValue("theme/dark", self._is_dark)

    @property
    def is_dark(self):
        return self._is_dark

    def set_dark(self, dark: bool):
        if self._is_dark != dark:
            self._is_dark = dark
            self._save()
            self.theme_changed.emit(dark)

    def toggle(self):
        self.set_dark(not self._is_dark)

    @property
    def current(self) -> ThemeColors:
        return DARK_THEME if self._is_dark else LIGHT_THEME


_manager_instance: ThemeManager | None = None


def theme_manager() -> ThemeManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ThemeManager()
    return _manager_instance


def generate_stylesheet(is_dark: bool) -> str:
    if not is_dark:
        return ""

    return """
        QMainWindow {
            background-color: #3c3c3c;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #e0e0e0;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background-color: #505050;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #505050;
        }
        QMenu::separator {
            height: 1px;
            background-color: #555555;
            margin: 4px 8px;
        }
        QSplitter::handle {
            background-color: #555555;
            width: 1px;
        }
        QScrollArea {
            background-color: #3c3c3c;
            border: none;
        }
        QScrollBar:vertical {
            background: #2d2d2d;
            width: 12px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: #555555;
            border-radius: 6px;
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
            height: 12px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal {
            background: #555555;
            border-radius: 6px;
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
        QGroupBox {
            color: #e0e0e0;
            font-weight: bold;
            border: 1px solid #555555;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 2px 8px;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #505050;
            color: #e0e0e0;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QPushButton:hover {
            background-color: #606060;
        }
        QPushButton:pressed {
            background-color: #404040;
        }
        QPushButton:checked {
            background-color: #2a6da0;
            border: 1px solid #4a8dc0;
        }
        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }
        QPlainTextEdit {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px;
        }
        QSpinBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 2px 4px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #505050;
            border: 1px solid #555555;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow {
            color: #e0e0e0;
        }
        QDialog {
            background-color: #3c3c3c;
        }
        QGroupBox QLabel {
            color: #cccccc;
        }
        QDialog QLabel {
            color: #e0e0e0;
        }
        QRadioButton {
            color: #e0e0e0;
        }
        QDialogButtonBox QPushButton {
            min-width: 80px;
            padding: 6px 16px;
        }
        QFrame {
            border: none;
        }
        QSplitter {
            background-color: #3c3c3c;
        }
        QToolTip {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #555555;
            padding: 4px;
            font-size: 12px;
        }
    """
