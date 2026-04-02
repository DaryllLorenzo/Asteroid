# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------

from typing import List, Dict, Any, Optional
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QBuffer, QIODevice


class PDFGenerator:
    """Generador de archivos PDF para diagramas de Asteroid"""
    
    def __init__(self, canvas_controller):
        self.canvas_controller = canvas_controller
    
    def export_to_pdf(self, with_additional_info: bool = True, filename: str = None) -> bool:
        """
        Exporta el diagrama actual a PDF
        
        Args:
            with_additional_info: Si True, incluye información adicional de elementos
            filename: Ruta del archivo de salida (opcional)
        
        Returns:
            True si la exportación fue exitosa
        """
        try:
            # Obtener nombre de archivo
            if not filename:
                filename, _ = QFileDialog.getSaveFileName(
                    self.canvas_controller.canvas,
                    "Exportar a PDF",
                    "",
                    "PDF Files (*.pdf)"
                )
                if not filename:
                    return False
                
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construir contenido
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Diagrama Asteroid", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Agregar imagen del diagrama
            diagram_image = self._capture_canvas_image()
            if diagram_image:
                img = Image(diagram_image, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.5*inch))
            
            # Agregar información adicional si se solicita
            if with_additional_info:
                story.append(PageBreak())
                self._add_additional_info(story, styles)
            
            # Construir PDF
            doc.build(story)
            
            print(f"✅ PDF exportado exitosamente: {filename}")
            QMessageBox.information(
                self.canvas_controller.canvas,
                "Exportación completada",
                f"PDF exportado exitosamente:\n{filename}"
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error exportando a PDF: {e}")
            QMessageBox.critical(
                self.canvas_controller.canvas,
                "Error",
                f"No se pudo exportar el PDF:\n{e}"
            )
            return False
    
    def _capture_canvas_image(self) -> Optional[str]:
        """
        Captura el canvas como imagen y retorna la ruta temporal

        Returns:
            Ruta de la imagen temporal o None si falla
        """
        try:
            canvas = self.canvas_controller.canvas

            # ✅ Obtener los límites reales de todos los items + margen para evitar cortes
            scene_rect = canvas.scene.itemsBoundingRect()
            margin = 50.0  # Margen extra para asegurar que no se corten bordes (subcanvas, etc.)
            expanded_rect = scene_rect.adjusted(-margin, -margin, margin, margin)

            # Crear pixmap del tamaño expandido
            pixmap = QPixmap(int(expanded_rect.width()), int(expanded_rect.height()))
            pixmap.fill(QColor(255, 255, 255))  # Usar QColor en lugar de colors.white

            # Renderizar la escena en el pixmap con el rect expandido
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # ✅ Renderizar usando el rect expandido para capturar todos los elementos completos
            canvas.scene.render(painter, source=expanded_rect)
            painter.end()

            # Guardar como PNG temporal
            temp_path = Path(__file__).parent.parent.parent / "temp_diagram.png"
            pixmap.save(str(temp_path), "PNG")

            return str(temp_path)
            
        except Exception as e:
            print(f"❌ Error capturando imagen del canvas: {e}")
            return None
    
    def _add_additional_info(self, story: list, styles):
        """
        Agrega información adicional de elementos al PDF
        
        Args:
            story: Lista de elementos del PDF
            styles: Estilos de ReportLab
        """
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=20,
            spaceBefore=10
        )
        
        # Sección de Elementos
        story.append(Paragraph("Elementos del Diagrama", section_style))
        self._add_elements_table(story, styles)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Sección de Relaciones
        story.append(Paragraph("Relaciones entre Elementos", section_style))
        self._add_relationships_table(story, styles)
    
    def _add_elements_table(self, story: list, styles):
        """
        Agrega tabla de elementos al PDF
        
        Args:
            story: Lista de elementos del PDF
            styles: Estilos de ReportLab
        """
        nodes = self.canvas_controller.nodes
        
        # Encabezados
        data = [["ID", "Tipo", "Nombre/Label"]]
        
        # Agregar elementos
        for idx, node in enumerate(nodes, 1):
            node_type = self._get_node_type_display(node)
            label = self._get_node_label(node)
            data.append([str(idx), node_type, label])
        
        # Crear tabla
        table = Table(data, colWidths=[0.5*inch, 1.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
    
    def _add_relationships_table(self, story: list, styles):
        """
        Agrega tabla de relaciones al PDF
        
        Args:
            story: Lista de elementos del PDF
            styles: Estilos de ReportLab
        """
        edges = self.canvas_controller.edges
        
        # Encabezados
        data = [["Origen", "Tipo de Relación", "Destino"]]
        
        # Agregar relaciones
        for edge in edges:
            source_label = self._get_node_label(edge.source_node)
            target_label = self._get_node_label(edge.dest_node)
            edge_type = self._get_edge_type_display(edge)
            data.append([source_label, edge_type, target_label])
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
    
    def _get_node_type_display(self, node) -> str:
        """
        Obtiene el nombre legible del tipo de nodo
        
        Args:
            node: Instancia del nodo
        
        Returns:
            String con el tipo de nodo
        """
        type_map = {
            'ActorNodeItem': 'Actor',
            'AgentNodeItem': 'Agente',
            'HardGoalNodeItem': 'Meta Dura',
            'SoftGoalNodeItem': 'Meta Blanda',
            'PlanNodeItem': 'Plan',
            'ResourceNodeItem': 'Recurso'
        }
        return type_map.get(node.__class__.__name__, 'Desconocido')
    
    def _get_node_label(self, node) -> str:
        """
        Obtiene el label/nombre del nodo
        
        Args:
            node: Instancia del nodo
        
        Returns:
            String con el label del nodo
        """
        if hasattr(node, 'model') and hasattr(node.model, 'label'):
            return node.model.label
        elif hasattr(node, 'label'):
            return node.label
        return "Sin nombre"
    
    def _get_edge_type_display(self, edge) -> str:
        """
        Obtiene el nombre legible del tipo de relación
        
        Args:
            edge: Instancia de la relación
        
        Returns:
            String con el tipo de relación
        """
        type_map = {
            'SimpleArrowItem': 'Conexión Simple',
            'DashedArrowItem': 'Conexión Punteada',
            'DependencyLinkArrowItem': 'Dependencia',
            'WhyLinkArrowItem': 'Por qué',
            'OrDecompositionArrowItem': 'Descomposición OR',
            'AndDecompositionArrowItem': 'Descomposición AND',
            'ContributionArrowItem': 'Contribución',
            'MeansEndArrowItem': 'Medio-Fin'
        }
        return type_map.get(edge.__class__.__name__, 'Relación')
