from app.ui.components.base_tropos_item import BaseTroposItem
from app.core.models.tropos_element.soft_goal import SoftGoal
from PyQt6.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt6.QtCore import QRectF

class SoftGoalNodeItem(BaseTroposItem):
    def __init__(self, x=0, y=0, radius=30):
        super().__init__(SoftGoal(x, y, radius))
        self.model.radius = radius
        self.path = self._create_cloud_path()
        self._update_handle_pos()

    def _create_cloud_path(self):
        r = float(self.model.radius)
        cloud_parts = [
            (-r*1.4, 0, r*0.9),
            (-r*0.9, -r*0.4, r*0.9),
            (-r*0.5, 0, r*0.8),
            (0, -r*0.5, r*1.0),
            (r*0.5, 0, r*0.8),
            (r*0.9, -r*0.4, r*0.9),
            (r*1.4, 0, r*0.9),
            (-r*0.7, r*0.3, r*0.6),
            (r*0.7, r*0.3, r*0.6),
            (0, r*0.2, r*0.7),
        ]
        p = QPainterPath()
        for dx, dy, pr in cloud_parts:
            ellipse = QPainterPath()
            ellipse.addEllipse(dx - pr, dy - pr, pr*2, pr*2)
            p = p.united(ellipse) if not p.isEmpty() else ellipse
        return p

    def set_radius(self, new_r: float):
        self.prepareGeometryChange()
        self.model.radius = new_r
        self.radius = new_r
        self.path = self._create_cloud_path()

        # Coloca el handle en la esquina inferior derecha del bounding rect de la nube
        br = self.path.boundingRect()
        self.resize_handle.setPos(br.right(), br.bottom())

        self.update()

    def boundingRect(self):
        if not hasattr(self, "path") or self.path.isEmpty():
            r = self.model.radius
            return QRectF(-r, -r, r*2, r*2)
        return self.path.boundingRect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(220, 220, 180)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawPath(self.path)
