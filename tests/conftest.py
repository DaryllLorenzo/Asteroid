# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Shared fixtures and typed helpers.

`QT_QPA_PLATFORM` must be set before PyQt6 is imported anywhere, hence the
early assignment at module import time.
"""

import os
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtWidgets import QMessageBox
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

    from app.controllers.canvas_controller import CanvasController
    from app.ui.components.base_node_item import BaseNodeItem


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """One QApplication for the whole session; Qt forbids more than one."""
    return cast("QApplication", QApplication.instance() or QApplication([]))


@pytest.fixture(autouse=True)
def message_boxes(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Capture dialogs instead of blocking on `exec()`.

    Every `QMessageBox` variant waits for a click on `exec()`, and offscreen
    Qt still spins an event loop, so an unstubbed dialog hangs the suite.
    `information` matters as much as `warning`/`critical`: the export
    success path calls it.
    """
    captured: dict[str, list[str]] = {
        "warning": [],
        "critical": [],
        "information": [],
        "validation": [],
    }

    def _text(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        if "text" in kwargs:
            return str(kwargs["text"])
        return str(args[2]) if len(args) > 2 else ""

    for variant in ("warning", "critical", "information"):
        monkeypatch.setattr(
            QMessageBox,
            variant,
            (lambda bucket: staticmethod(lambda *a, **k: bucket.append(_text(a, k))))(
                captured[variant]
            ),
        )

    return captured


_VALIDATION_ERRORS: list[str] = []


def _record_validation_errors(_controller: Any, errors: list[str]) -> None:
    """Stand-in for `CanvasController._show_validation_errors`.

    Bound onto the class by the fixture, hence the leading `self` parameter.
    """
    _VALIDATION_ERRORS.clear()
    _VALIDATION_ERRORS.extend(errors)


@pytest.fixture
def controller(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> "CanvasController":
    """A fresh Canvas + CanvasController, with the blocking dialog stubbed out."""
    from app.controllers.canvas_controller import CanvasController
    from app.ui.canvas import Canvas

    monkeypatch.setattr(
        CanvasController, "_show_validation_errors", _record_validation_errors
    )
    return CanvasController(Canvas())


@pytest.fixture
def validation_errors() -> "Callable[[], list[str]]":
    """Accessor for the errors the last blocked action would have shown."""

    def _get() -> list[str]:
        return list(_VALIDATION_ERRORS)

    return _get


# ------------------------------------------------------------------ helpers


def make_node(
    controller: "CanvasController", node_type: str, x: float, y: float
) -> "BaseNodeItem":
    """Create a node through the real controller, asserting it was accepted.

    `add_node` returns `None` for an unknown type; every caller in this suite
    passes a type that `_NODE_MAP` is expected to know, so a `None` here is a
    failure worth surfacing rather than a value to assert on later.
    """
    node = controller.add_node(node_type, x, y)
    assert node is not None, f"controller refused to create a {node_type!r}"
    return cast("BaseNodeItem", node)


def scene_of(controller: "CanvasController") -> QGraphicsScene:
    """The controller's scene, asserted present."""
    scene = controller.canvas.scene()
    assert scene is not None
    return scene
