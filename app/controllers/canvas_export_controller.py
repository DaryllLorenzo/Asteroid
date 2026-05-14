# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox

from app.controllers._canvas_mixin import CanvasControllerMixin
from app.utils.astr_format import AstrFormat


class CanvasExportController(CanvasControllerMixin):
    """
    Canvas Export Controller.

    Methods:
        export_to_astr: Export To Astr.
        export_to_image: Export To Image.
    """

    def export_to_astr(
        self,
        filename: str | None = None,
    ) -> bool:
        """
        Export To Astr.

        Args:
            filename (str | None): The filename.

        Returns:
            bool: Export To Astr.
        """
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    "Export as .astr",
                    "",
                    "Asteroid Files (*.astr)",
                )
                if not filename:
                    return False

                if not filename.endswith(".astr"):
                    filename += ".astr"

            scene_data = AstrFormat.serialize_scene(self.nodes, self.edges)

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(scene_data, file, indent=2, ensure_ascii=False)

            print(f"Project exported successfully: {filename}")
            self.mark_as_saved(filename)
            return True

        except Exception as error:
            print(f"Error exporting project: {error}")
            QMessageBox.critical(
                self.canvas, "Error", f"Could not export project:\n{error}"
            )
            return False

    def export_to_image(
        self,
        filename: str | None = None,
    ) -> bool:
        """
        Export To Image.

        Args:
            filename (str | None): The filename.

        Returns:
            bool: Export To Image.
        """
        try:
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    "Export as image",
                    "",
                    "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg)",
                )
                if not filename:
                    return False

                if not filename.endswith(".png"):
                    filename += ".png"

            scene = self.canvas.scene()
            if scene is None:
                return False

            rect = scene.itemsBoundingRect()
            pixmap = QPixmap(rect.size().toSize())
            pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            scene.render(painter, source=rect)
            painter.end()

            pixmap.save(filename)
            print(f"Image exported successfully: {filename}")
            return True

        except Exception as error:
            print(f"Error exporting image: {error}")
            QMessageBox.critical(
                self.canvas, "Error", f"Could not export image:\n{error}"
            )
            return False
