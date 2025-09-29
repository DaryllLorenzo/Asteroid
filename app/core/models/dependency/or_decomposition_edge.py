from app.core.models.base_edge import BaseEdge

class OrDecompositionEdge(BaseEdge):
    def __init__(self, source, target):
        super().__init__(source, target)

    def edge_type(self):
        return "or_decomposition"
