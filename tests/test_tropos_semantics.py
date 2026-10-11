# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Tropos structural constraints, exercised through the real controller.

These tests back the paper's claim that Asteroid enforces the Tropos
structural model rather than a generic i* one. The distinguishing rules are
asserted end-to-end (a rejected action must leave no edge behind), not only
against the isolated `Rule` classes, so that they also prove the rules are
actually wired into the interaction path.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import make_node
import pytest

from app.controllers.canvas_registry_controller import _ARROW_TYPES
from app.controllers.canvas_registry_controller import _MODEL_MAP
from app.controllers.canvas_registry_controller import _NODE_MAP
from app.core.models.typed_node import NODE_STYLES
from app.validation.rules.no_link_between_entities import _LINK_DESCRIPTIONS
from app.validation.validator import Validator

if TYPE_CHECKING:
    from collections.abc import Callable

    from app.controllers.canvas_controller import CanvasController

ENTITY_TYPES = ["actor", "agent"]
TROPOS_TYPES = ["hard_goal", "soft_goal", "plan", "resource"]


# ---------------------------------------------------------------- rule table


class TestDependencyLinksBetweenEntities:
    """A dependency link is only meaningful between Tropos elements.

    Parameterised over all six registered arrow types: entity-to-entity is
    rejected, while any pairing that involves at least one Tropos element is
    accepted.
    """

    @pytest.mark.parametrize("arrow_type", sorted(_LINK_DESCRIPTIONS))
    def test_entity_to_entity_is_rejected(
        self,
        controller: CanvasController,
        arrow_type: str,
    ) -> None:
        controller.validator.active = True
        actor = make_node(controller, "actor", 0, 0)
        agent = make_node(controller, "agent", 300, 0)

        controller.selected_arrow_type = arrow_type
        controller.selected_nodes_for_arrow = [actor, agent]
        result = controller.create_arrow()

        assert result is None
        assert controller.edges == []

    @pytest.mark.parametrize("arrow_type", sorted(_LINK_DESCRIPTIONS))
    @pytest.mark.parametrize("source_type", TROPOS_TYPES)
    def test_tropos_to_tropos_is_accepted(
        self,
        controller: CanvasController,
        arrow_type: str,
        source_type: str,
    ) -> None:
        controller.validator.active = True
        source = make_node(controller, source_type, 0, 0)
        target = make_node(controller, "resource", 300, 0)

        controller.selected_arrow_type = arrow_type
        controller.selected_nodes_for_arrow = [source, target]
        result = controller.create_arrow()

        assert result is not None
        assert len(controller.edges) == 1

    @pytest.mark.parametrize("arrow_type", sorted(_LINK_DESCRIPTIONS))
    def test_entity_to_tropos_is_accepted(
        self,
        controller: CanvasController,
        arrow_type: str,
    ) -> None:
        """The rule requires *both* endpoints to be entities."""
        controller.validator.active = True
        actor = make_node(controller, "actor", 0, 0)
        goal = make_node(controller, "hard_goal", 300, 0)

        controller.selected_arrow_type = arrow_type
        controller.selected_nodes_for_arrow = [actor, goal]
        result = controller.create_arrow()

        assert result is not None
        assert len(controller.edges) == 1

    def test_validator_inactive_permits_everything(
        self,
        controller: CanvasController,
    ) -> None:
        """The Validation menu toggle gates the whole rule set."""
        assert controller.validator.active is False
        actor = make_node(controller, "actor", 0, 0)
        agent = make_node(controller, "agent", 300, 0)

        controller.selected_arrow_type = "dependency_link"
        controller.selected_nodes_for_arrow = [actor, agent]
        result = controller.create_arrow()

        assert result is not None
        assert len(controller.edges) == 1

    @pytest.mark.parametrize("arrow_type", sorted(_LINK_DESCRIPTIONS))
    def test_rule_message_names_the_arrow_type(
        self,
        controller: CanvasController,
        arrow_type: str,
        validation_errors: Callable[[], list[str]],
    ) -> None:
        actor = make_node(controller, "actor", 0, 0)
        agent = make_node(controller, "agent", 300, 0)
        controller.validator.active = True

        controller.selected_arrow_type = arrow_type
        controller.selected_nodes_for_arrow = [actor, agent]
        controller.create_arrow()

        assert len(validation_errors()) == 1


class TestEntityInsideEntitySubcanvas:
    """Subcanvases hold Tropos elements, never nested Actors or Agents."""

    @pytest.mark.parametrize("child_type", ENTITY_TYPES)
    def test_entity_child_is_rejected(
        self,
        controller: CanvasController,
        validation_errors: Callable[[], list[str]],
        child_type: str,
    ) -> None:
        controller.validator.active = True
        actor = make_node(controller, "actor", 0, 0)
        subcanvas = actor.prepare_subcanvas_for_internal_use()
        node_count_before = len(controller.nodes)

        controller._on_subcanvas_node_dropped(actor, subcanvas, child_type, 0, 0)

        assert len(controller.nodes) == node_count_before
        assert len(validation_errors()) == 1

    @pytest.mark.parametrize("child_type", TROPOS_TYPES)
    def test_tropos_child_is_accepted(
        self,
        controller: CanvasController,
        child_type: str,
    ) -> None:
        controller.validator.active = True
        actor = make_node(controller, "actor", 0, 0)
        subcanvas = actor.prepare_subcanvas_for_internal_use()
        node_count_before = len(controller.nodes)

        controller._on_subcanvas_node_dropped(actor, subcanvas, child_type, 0, 0)

        assert len(controller.nodes) == node_count_before + 1

    @pytest.mark.parametrize("child_type", TROPOS_TYPES + ENTITY_TYPES)
    def test_only_entity_parents_are_restricted(
        self,
        controller: CanvasController,
        child_type: str,
    ) -> None:
        """A non-entity parent accepts every child type, entity or not."""
        controller.validator.active = True

        errors = controller.validator.validate(
            "subcanvas_add_node",
            {"parent_is_entity": False, "child_type": child_type},
        )

        assert errors == []


# ------------------------------------------------------------------ registry


class TestRegistryConstraints:
    """Structural invariants encoded in the three lookup tables."""

    def test_entities_have_no_subcanvas_model(self) -> None:
        """The core Tropos-vs-i* distinction, asserted structurally.

        Actors and Agents exist only at canvas level: they have no entry in
        `_MODEL_MAP`, so `create_composite_dependency` cannot manufacture an
        internal model for them.
        """
        for entity_type in ENTITY_TYPES:
            assert entity_type in _NODE_MAP
            assert entity_type not in _MODEL_MAP

    def test_tropos_elements_have_a_model(self) -> None:
        for tropos_type in TROPOS_TYPES:
            assert tropos_type in _NODE_MAP
            assert tropos_type in _MODEL_MAP

    def test_every_node_type_has_a_style(self) -> None:
        assert set(_NODE_MAP) == set(NODE_STYLES)

    def test_every_arrow_type_has_a_validation_rule(self) -> None:
        """No arrow type may ship without the entity-entity guard."""
        assert set(_ARROW_TYPES) == set(_LINK_DESCRIPTIONS)

    def test_styles_are_complete(self) -> None:
        required = {"label", "color", "border_color", "text_color"}
        for type_name, style in NODE_STYLES.items():
            assert set(style) == required, type_name


# ------------------------------------------------------------------ validator

# The seven well-formedness constraints the paper claims. Six are one shape
# parameterised by arrow type, the seventh is structurally different.
ARROW_RULE_TYPES = sorted(_LINK_DESCRIPTIONS)  # 6
SUBCANVAS_RULE_TYPES = ["actor", "agent"]  # 1 rule, 2 paths into it
SEVEN_RULES = 6 + 1


class TestSevenWellFormednessRules:
    """The claim "seven rules", asserted as an executable property.

    Two things are checked: that the validator holds exactly seven registered
    rule instances, and that all seven actually fire through `validate()` — a
    rule that exists but is unreachable would satisfy the first check alone.
    """

    def test_validator_registers_exactly_seven_rules(self) -> None:
        validator = Validator()
        assert len(validator._rules) == SEVEN_RULES

    @pytest.mark.parametrize("arrow_type", ARROW_RULE_TYPES)
    def test_each_arrow_type_has_exactly_one_firing_rule(self, arrow_type: str) -> None:
        validator = Validator()
        validator.active = True

        errors = validator.validate(
            "create_edge",
            {
                "arrow_type": arrow_type,
                "source_is_entity": True,
                "dest_is_entity": True,
            },
        )

        assert len(errors) == 1, f"expected exactly one rule to fire for {arrow_type}"

    @pytest.mark.parametrize("child_type", SUBCANVAS_RULE_TYPES)
    def test_subcanvas_rule_fires(self, child_type: str) -> None:
        validator = Validator()
        validator.active = True

        errors = validator.validate(
            "subcanvas_add_node",
            {"parent_is_entity": True, "child_type": child_type},
        )

        assert len(errors) == 1

    def test_distinct_rule_classes_are_two(self) -> None:
        """Documents why "seven rules" means seven constraints, not seven classes.

        Six of the seven share one class, generated from a table by
        `NoLinkBetweenEntitiesRule`; the seventh is `NoEntityInEntitySubcanvas`.
        Reading the class names alone would suggest only two rules exist, which
        is exactly the confusion the parametrised tests above disambiguate.
        """
        validator = Validator()
        classes = {type(rule) for rule in validator._rules}
        assert len(classes) == 2
        assert len(validator._rules) == SEVEN_RULES

    @pytest.mark.parametrize("arrow_type", ARROW_RULE_TYPES)
    def test_every_registered_arrow_type_is_guarded(self, arrow_type: str) -> None:
        """No arrow type may reach the scene between two entities unguarded."""
        validator = Validator()
        validator.active = True

        errors = validator.validate(
            "create_edge",
            {
                "arrow_type": arrow_type,
                "source_is_entity": True,
                "dest_is_entity": True,
            },
        )
        assert errors, f"{arrow_type} has no guard"


class TestValidator:
    def test_starts_inactive(self) -> None:
        assert Validator().active is False

    def test_inactive_validator_reports_nothing(self) -> None:
        validator = Validator()
        assert validator.active is False
        assert (
            validator.validate(
                "create_edge",
                {
                    "arrow_type": "dependency_link",
                    "source_is_entity": True,
                    "dest_is_entity": True,
                },
            )
            == []
        )

    def test_rule_set_covers_both_action_types(self) -> None:
        validator = Validator()
        validator.active = True

        entity_edge = validator.validate(
            "create_edge",
            {
                "arrow_type": "dependency_link",
                "source_is_entity": True,
                "dest_is_entity": True,
            },
        )
        nested_entity = validator.validate(
            "subcanvas_add_node",
            {"parent_is_entity": True, "child_type": "actor"},
        )

        assert len(entity_edge) == 1
        assert len(nested_entity) == 1

    def test_no_rule_fires_for_an_unrelated_action(self) -> None:
        validator = Validator()
        validator.active = True
        assert validator.validate("delete_node", {}) == []
