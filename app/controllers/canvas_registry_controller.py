# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------
from functools import partial

from app.controller_types import NodeItemFactory
from app.core.models.typed_node import TypedNode
from app.model_types import ModelFactory
from app.ui.components.base_edge_item import BaseEdgeItem
from app.ui.components.dependency_item.and_decomposition_edge_item import (
    AndDecompositionArrowItem,
)
from app.ui.components.dependency_item.contribution_edge_item import (
    ContributionArrowItem,
)
from app.ui.components.dependency_item.dependency_link_edge_item import (
    DependencyLinkArrowItem,
)
from app.ui.components.dependency_item.means_end_edge_item import MeansEndArrowItem
from app.ui.components.dependency_item.or_decomposition_edge_item import (
    OrDecompositionArrowItem,
)
from app.ui.components.dependency_item.why_link_edge_item import WhyLinkArrowItem
from app.ui.components.entity_item.actor_node_item import ActorNodeItem
from app.ui.components.entity_item.agent_node_item import AgentNodeItem
from app.ui.components.tropos_element_item.hard_goal_item import HardGoalNodeItem
from app.ui.components.tropos_element_item.plan_item import PlanNodeItem
from app.ui.components.tropos_element_item.resource_item import ResourceNodeItem
from app.ui.components.tropos_element_item.soft_goal_item import SoftGoalNodeItem

_NODE_MAP: dict[str, NodeItemFactory] = {
    "actor": ActorNodeItem,
    "agent": AgentNodeItem,
    "hard_goal": HardGoalNodeItem,
    "soft_goal": SoftGoalNodeItem,
    "plan": PlanNodeItem,
    "resource": ResourceNodeItem,
}

_MODEL_MAP: dict[str, ModelFactory] = {
    "hard_goal": partial(TypedNode, "hard_goal"),
    "soft_goal": partial(TypedNode, "soft_goal"),
    "plan": partial(TypedNode, "plan"),
    "resource": partial(TypedNode, "resource"),
}

_ARROW_TYPES: dict[str, type[BaseEdgeItem]] = {
    "dependency_link": DependencyLinkArrowItem,
    "why_link": WhyLinkArrowItem,
    "or_decomposition": OrDecompositionArrowItem,
    "and_decomposition": AndDecompositionArrowItem,
    "contribution": ContributionArrowItem,
    "means_end": MeansEndArrowItem,
}
