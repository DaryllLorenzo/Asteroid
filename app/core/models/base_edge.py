# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from abc import ABC
from abc import abstractmethod


class BaseEdge(ABC):
    """
    Base Edge.

    Methods:
        __init__: Initialize the instance.
        edge_type: Edge Type.
    """

    def __init__(self, source, target):
        """
        Initialize the instance.

        Args:
            source: The source.
            target: The target.
        """
        self.source = source
        self.target = target

    @abstractmethod
    def edge_type(self):
        """Edge Type."""
        pass
