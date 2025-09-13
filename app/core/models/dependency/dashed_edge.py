from app.core.models.base_edge import BaseEdge

class DashedEdge(BaseEdge):

    def __init__(self, source, target):
        super().__init__(source, target)

    def edge_type(self):
        return "dashed"
