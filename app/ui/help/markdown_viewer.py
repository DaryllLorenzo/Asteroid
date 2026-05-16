# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from pathlib import Path

import markdown
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.ui.theme_manager import theme_manager


class MarkdownViewer(QWidget):
    """
    Markdown Viewer.

    Methods:
        __init__: Initialize the instance.
        setup_ui: Setup Ui.
        get_stylesheet: Get Stylesheet.
        load_markdown: Load Markdown.
        show_error: Show Error.
    """

    def __init__(self, parent=None):
        """
        Initialize the instance.

        Args:
            parent: The parent.
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup Ui."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        # Configure font base
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.text_browser.setFont(font)

        # Configure scroll
        self.text_browser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.text_browser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        layout.addWidget(self.text_browser)

    def get_stylesheet(self):
        """Get Stylesheet."""
        if theme_manager().is_dark:
            return self._get_dark_stylesheet()
        return self._get_light_stylesheet()

    def _get_light_stylesheet(self):
        """Get light mode CSS."""
        return """
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #2c3e50;
                background-color: #ffffff;
                margin: 0;
                padding: 25px 30px;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
            }
            h2 {
                color: #34495e;
                font-size: 22px;
                font-weight: bold;
                margin-top: 30px;
                margin-bottom: 15px;
                padding-bottom: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            h3 {
                color: #4a6572;
                font-size: 18px;
                font-weight: bold;
                margin-top: 25px;
                margin-bottom: 12px;
            }
            h4 {
                color: #5d6d7e;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            p {
                margin-bottom: 16px;
                color: #3a506b;
            }
            ul {
                margin-bottom: 18px;
                margin-left: 25px;
                padding-left: 0;
            }
            ul li {
                margin-bottom: 8px;
                color: #3a506b;
                list-style-type: disc;
            }
            ol {
                margin-bottom: 18px;
                margin-left: 30px;
                padding-left: 0;
            }
            ol li {
                margin-bottom: 8px;
                color: #3a506b;
                list-style-type: decimal;
            }
            code {
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 2px 6px;
                border-radius: 3px;
                border: 1px solid #e9ecef;
                color: #2c3e50;
            }
            pre {
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
                margin-bottom: 20px;
                overflow-x: auto;
            }
            pre code {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            a {
                color: #2980b9;
                text-decoration: none;
            }
            a:hover {
                color: #1a5276;
                text-decoration: underline;
            }
            strong {
                font-weight: bold;
                color: #2c3e50;
            }
            em {
                font-style: italic;
                color: #5d6d7e;
            }
            blockquote {
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px 20px;
                margin: 20px 0;
                font-style: italic;
                color: #4a6572;
            }
            blockquote p {
                margin: 0;
                color: #4a6572;
            }
            hr {
                border: none;
                height: 1px;
                background-color: #ecf0f1;
                margin: 30px 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
                border: 1px solid #dee2e6;
            }
            th {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                text-align: left;
                padding: 12px 15px;
                border: 1px solid #dee2e6;
            }
            td {
                padding: 10px 15px;
                border: 1px solid #dee2e6;
                color: #3a506b;
            }
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15px auto;
                border: 1px solid #dee2e6;
                padding: 3px;
                background-color: white;
            }
            .note {
                background-color: #fff8e1;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
                color: #856404;
            }
            .tip {
                background-color: #d1ecf1;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                margin: 15px 0;
                color: #0c5460;
            }
            .warning {
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin: 15px 0;
                color: #721c24;
            }
            .success {
                background-color: #d1fae5;
                border-left: 4px solid #10b981;
                padding: 15px;
                margin: 15px 0;
                color: #065f46;
            }
            .center { text-align: center; }
            .right { text-align: right; }
            .left { text-align: left; }
            .inline-code {
                background-color: #f8f9fa;
                font-family: 'Consolas', monospace;
                padding: 2px 6px;
                border-radius: 3px;
                border: 1px solid #e9ecef;
                color: #2c3e50;
            }
            .diagram {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 15px 0;
                border: 1px solid #dee2e6;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
            .image-container {
                text-align: center;
                margin-top: 15px;
                margin: 15px 0;
            }
            .image-caption {
                font-style: italic;
                color: #7f8c8d;
                font-size: 13px;
                margin-top: 15px;
                margin-bottom: 15px;
            }
            .card {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
        """

    def _get_dark_stylesheet(self):
        """Get dark mode CSS."""
        return """
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #d4d4d4;
                background-color: #1e1e1e;
                margin: 0;
                padding: 25px 30px;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #e0e0e0;
                font-size: 28px;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
            }
            h2 {
                color: #cccccc;
                font-size: 22px;
                font-weight: bold;
                margin-top: 30px;
                margin-bottom: 15px;
                padding-bottom: 5px;
                border-bottom: 1px solid #3a3a3a;
            }
            h3 {
                color: #bbbbbb;
                font-size: 18px;
                font-weight: bold;
                margin-top: 25px;
                margin-bottom: 12px;
            }
            h4 {
                color: #aaaaaa;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            p {
                margin-bottom: 16px;
                color: #d4d4d4;
            }
            ul {
                margin-bottom: 18px;
                margin-left: 25px;
                padding-left: 0;
            }
            ul li {
                margin-bottom: 8px;
                color: #d4d4d4;
                list-style-type: disc;
            }
            ol {
                margin-bottom: 18px;
                margin-left: 30px;
                padding-left: 0;
            }
            ol li {
                margin-bottom: 8px;
                color: #d4d4d4;
                list-style-type: decimal;
            }
            code {
                background-color: #2d2d2d;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 2px 6px;
                border-radius: 3px;
                border: 1px solid #444444;
                color: #d4d4d4;
            }
            pre {
                background-color: #2d2d2d;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
                margin-bottom: 20px;
                overflow-x: auto;
            }
            pre code {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            a {
                color: #5dade2;
                text-decoration: none;
            }
            a:hover {
                color: #85c1e9;
                text-decoration: underline;
            }
            strong {
                font-weight: bold;
                color: #e0e0e0;
            }
            em {
                font-style: italic;
                color: #aaaaaa;
            }
            blockquote {
                background-color: #2d2d2d;
                border-left: 4px solid #3498db;
                padding: 15px 20px;
                margin: 20px 0;
                font-style: italic;
                color: #bbbbbb;
            }
            blockquote p {
                margin: 0;
                color: #bbbbbb;
            }
            hr {
                border: none;
                height: 1px;
                background-color: #3a3a3a;
                margin: 30px 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
                border: 1px solid #444444;
            }
            th {
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-weight: bold;
                text-align: left;
                padding: 12px 15px;
                border: 1px solid #444444;
            }
            td {
                padding: 10px 15px;
                border: 1px solid #444444;
                color: #d4d4d4;
            }
            tr:nth-child(even) {
                background-color: #2a2a2a;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15px auto;
                border: 1px solid #444444;
                padding: 3px;
                background-color: #2d2d2d;
            }
            .note {
                background-color: #3d3500;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
                color: #ffd54f;
            }
            .tip {
                background-color: #0a3d3d;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                margin: 15px 0;
                color: #4dd0e1;
            }
            .warning {
                background-color: #3d1010;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin: 15px 0;
                color: #ef5350;
            }
            .success {
                background-color: #0a2d1a;
                border-left: 4px solid #10b981;
                padding: 15px;
                margin: 15px 0;
                color: #66bb6a;
            }
            .center { text-align: center; }
            .right { text-align: right; }
            .left { text-align: left; }
            .inline-code {
                background-color: #2d2d2d;
                font-family: 'Consolas', monospace;
                padding: 2px 6px;
                border-radius: 3px;
                border: 1px solid #444444;
                color: #d4d4d4;
            }
            .diagram {
                background-color: #2d2d2d;
                padding: 15px;
                margin: 15px 0;
                border: 1px solid #444444;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
            .image-container {
                text-align: center;
                margin-top: 15px;
                margin: 15px 0;
            }
            .image-caption {
                font-style: italic;
                color: #888888;
                font-size: 13px;
                margin-top: 15px;
                margin-bottom: 15px;
            }
            .card {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
        """

    def load_markdown(self, file_path):
        """
        Load Markdown.

        Args:
            file_path: The file path.
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.show_error(f"Archivo no encontrado: {file_path}")
                return

            content = file_path.read_text(encoding="utf-8")

            if not content.strip():
                self.show_error(f"El archivo está vacío: {file_path.name}")
                return

            # Convert markdown a HTML with extensiones
            html = markdown.markdown(
                content, extensions=["extra", "nl2br", "toc"], output_format="html5"
            )

            # Aplicar estilos CSS
            self.text_browser.document().setDefaultStyleSheet(self.get_stylesheet())

            # Set the HTML
            self.text_browser.setHtml(html)

        except Exception as e:
            print(f"Error al cargar markdown: {e}")
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        """
        Show Error.

        Args:
            message: The message.
        """
        error_html = f"""
        <div class="warning">
            <h3>⚠️ Error</h3>
            <p><strong>{message}</strong></p>
            <p>Por favor, verifica que el archivo exista y tenga contenido válido.</p>
        </div>
        """
        self.text_browser.setHtml(error_html)
