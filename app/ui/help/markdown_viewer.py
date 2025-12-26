# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import markdown
from pathlib import Path

class MarkdownViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Configurar fuente base
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.text_browser.setFont(font)
        
        # Configurar scroll
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        layout.addWidget(self.text_browser)
    
    def get_stylesheet(self):
        """CSS profesional y elegante para el visor de markdown"""
        return """
            /* ===== ESTILOS GENERALES ===== */
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
            
            /* ===== ENCABEZADOS ===== */
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
            
            /* ===== PÁRRAFOS Y TEXTO ===== */
            p {
                margin-bottom: 16px;
                color: #3a506b;
            }
            
            /* ===== LISTAS ===== */
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
            
            /* ===== CÓDIGO ===== */
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
            
            /* ===== ENLACES ===== */
            a {
                color: #2980b9;
                text-decoration: none;
            }
            
            a:hover {
                color: #1a5276;
                text-decoration: underline;
            }
            
            /* ===== TEXTO RESALTADO ===== */
            strong {
                font-weight: bold;
                color: #2c3e50;
            }
            
            em {
                font-style: italic;
                color: #5d6d7e;
            }
            
            /* ===== CITAS ===== */
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
            
            /* ===== LÍNEAS DIVISORIAS ===== */
            hr {
                border: none;
                height: 1px;
                background-color: #ecf0f1;
                margin: 30px 0;
            }
            
            /* ===== TABLAS ===== */
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
            
            /* ===== IMÁGENES - ESPACIO CONTROLADO ===== */
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15px auto;
                border: 1px solid #dee2e6;
                padding: 3px;
                background-color: white;
            }
            
            /* ===== CLASES ESPECIALES ===== */
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
            
            /* ===== UTILIDADES ===== */
            .center {
                text-align: center;
            }
            
            .right {
                text-align: right;
            }
            
            .left {
                text-align: left;
            }
            
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
            
            /* ===== CONTENEDORES ESPECIALES ===== */
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
    
    def load_markdown(self, file_path):
        """Carga y renderiza un archivo markdown con estilos profesionales"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.show_error(f"Archivo no encontrado: {file_path}")
                return
            
            content = file_path.read_text(encoding='utf-8')
            
            if not content.strip():
                self.show_error(f"El archivo está vacío: {file_path.name}")
                return
            
            # Convertir markdown a HTML con extensiones
            html = markdown.markdown(
                content,
                extensions=['extra', 'nl2br', 'toc'],
                output_format='html5'
            )
            
            # Aplicar estilos CSS
            self.text_browser.document().setDefaultStyleSheet(self.get_stylesheet())
            
            # Establecer el HTML
            self.text_browser.setHtml(html)
            
        except Exception as e:
            print(f"Error al cargar markdown: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def show_error(self, message):
        """Muestra un mensaje de error estilizado"""
        error_html = f"""
        <div class="warning">
            <h3>⚠️ Error</h3>
            <p><strong>{message}</strong></p>
            <p>Por favor, verifica que el archivo exista y tenga contenido válido.</p>
        </div>
        """
        self.text_browser.setHtml(error_html)