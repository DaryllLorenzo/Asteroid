# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

from app.core.models.base_edge import BaseEdge


class WhyLinkEdge(BaseEdge):
    """
    Why Link Edge.

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
        super().__init__(source, target)

    def edge_type(self):
        """Edge Type."""
        return "why_link"
