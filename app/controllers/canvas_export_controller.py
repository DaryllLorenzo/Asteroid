# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
import json
import logging
import os
import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox

from app.controllers._canvas_mixin import CanvasControllerMixin
from app.i18n import tr
from app.utils.astr_format import AstrFormat

logger = logging.getLogger(__name__)


class CanvasExportController(CanvasControllerMixin):
    """Serializes the canvas to a .astr file or a PNG/JPEG image."""

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        name = re.sub(r'[\\/:*?"<>|]', "_", name)
        name = name.strip(". ")
        if not name:
            name = "untitled"
        return name[:200]

    def _get_default_basename(self) -> str:
        path = getattr(self, "_current_file_path", None)
        if path:
            base = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
            base = base.rsplit(".", 1)[0] if "." in base else base
            return self._sanitize_filename(base)
        return "diagram"

    def export_to_astr(
        self,
        filename: str | None = None,
    ) -> bool:
        try:
            if not filename:
                default_name = self._get_default_basename() + ".astr"
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    tr("Export as .astr"),
                    default_name,
                    tr("Asteroid Files (*.astr)"),
                )
                if not filename:
                    return False

                if not filename.endswith(".astr"):
                    filename += ".astr"

            dir_part, file_part = os.path.split(filename)
            file_part = self._sanitize_filename(file_part)
            filename = os.path.join(dir_part, file_part)

            scene_data = AstrFormat.serialize_scene(self.nodes, self.edges)

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(scene_data, file, indent=2, ensure_ascii=False)

            logger.info("Project exported successfully: %s", filename)
            self.mark_as_saved(filename)
            return True

        except Exception as error:
            logger.exception("Error exporting project")
            QMessageBox.critical(
                self.canvas,
                tr("Error"),
                tr("Could not export project:\n{error}").format(error=error),
            )
            return False

    def export_to_image(
        self,
        filename: str | None = None,
    ) -> bool:
        try:
            if not filename:
                default_name = self._get_default_basename() + ".png"
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas,
                    tr("Export as image"),
                    default_name,
                    tr("PNG Images (*.png);;JPEG Images (*.jpg *.jpeg)"),
                )
                if not filename:
                    return False

                if not filename.endswith(".png"):
                    filename += ".png"

            dir_part, file_part = os.path.split(filename)
            file_part = self._sanitize_filename(file_part)
            filename = os.path.join(dir_part, file_part)

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
            logger.info("Image exported successfully: %s", filename)
            return True

        except Exception as error:
            logger.exception("Error exporting image")
            QMessageBox.critical(
                self.canvas, "Error", f"Could not export image:\n{error}"
            )
            return False
