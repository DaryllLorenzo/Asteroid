from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QDrag


class DraggableLabel(QLabel):
    def __init__(self, text, item_type, node_type=None):
        super().__init__(text)
        self.item_type = item_type
        self.node_type = node_type
        self.arrow_type = item_type if item_type in ["simple", "dashed"] else None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 10px;
                background-color: #f0f0f0;
                min-width: 80px;
                min-height: 80px;
            }
            QLabel:hover {
                background-color: #e0e0e0;
                border: 2px solid #999999;
            }
        """)
        self.setPixmap(self.create_pixmap())

    def create_pixmap(self):
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.item_type == "actor":
            painter.setBrush(QBrush(QColor(100, 150, 250)))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(10, 10, 40, 40)
        elif self.item_type == "agent":
            painter.setBrush(QBrush(QColor(250, 150, 100)))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(10, 10, 40, 40)
            painter.drawLine(10, 28, 50, 28)
        elif self.item_type == "simple":
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawLine(15, 30, 45, 30)
            painter.drawLine(45, 30, 38, 25)
            painter.drawLine(45, 30, 38, 35)
        elif self.item_type == "dashed":
            pen = QPen(QColor(100, 100, 100), 2)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(15, 30, 45, 30)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawLine(45, 30, 38, 25)
            painter.drawLine(45, 30, 38, 35)

        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_drag()

    def start_drag(self):
        mime_data = QMimeData()
        mime_data.setText(self.item_type)

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(self.pixmap().rect().center())
        drag.exec(Qt.DropAction.CopyAction)


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)

        # Elementos arrastrables
        self.actor_label = DraggableLabel("Actor", "actor")
        self.agente_label = DraggableLabel("Agente", "agent")
        self.simple_arrow_label = DraggableLabel("Flecha Simple", "simple")
        self.dashed_arrow_label = DraggableLabel("Flecha Punteada", "dashed")

        layout.addWidget(self.actor_label, 0, 0)
        layout.addWidget(self.agente_label, 0, 1)
        layout.addWidget(self.simple_arrow_label, 1, 0)
        layout.addWidget(self.dashed_arrow_label, 1, 1)
