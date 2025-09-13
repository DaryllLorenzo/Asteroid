from abc import ABC, abstractmethod

class BaseEdge(ABC):
    """Modelo lógico de una arista entre dos nodos."""

    def __init__(self, source, target):
        self.source = source
        self.target = target

    @abstractmethod
    def edge_type(self):
        """Devuelve el tipo de arista (simple/dashed/etc)."""
        pass