# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

This repo holds two independent applications that share the `.astr` project-file format:

- **`app/` + `main.py`** — the primary desktop app: a PyQt6 diagram editor for the Tropos/i* modeling
  methodology (actors, agents, goals, resources, plans, and dependency links between them). This is what
  the rest of this file documents.
- **`mobile/`** — a separate Flutter/Dart reimplementation (touch-first companion app, different
  maintainer), with its own `pubspec.yaml`, its own CI (`.github/workflows/flutter-build.yml`), and its own
  `.astr` reader/writer. Treat it as a distinct project; nothing in `app/` imports or depends on it.

## Commands (desktop app, `app/`)

```bash
# Run the app
uv run main.py                    # preferred (uv-managed env)
python main.py                    # if a venv is already activated

# Lint / format / type-check (what CI runs — see .github/workflows/ci.yml)
ruff check .
ruff format . --check             # ruff format .  (no --check) to actually reformat
mypy .
```

There is no automated Python test suite (no `pytest`, no `tests/` directory) — `ruff` + `mypy` passing and
a manual run of the app are the only checks CI performs. When verifying a change, prefer a headless
functional smoke test over trusting lint alone: construct a `Canvas` + `CanvasController` under
`QT_QPA_PLATFORM=offscreen`, drive it through `app.controllers.canvas_registry_controller._NODE_MAP` /
`_ARROW_TYPES`, and round-trip through `AstrFormat`/`CanvasImportController` — see the `run` skill in this
repo (if present) for a worked example, since this environment's `DISPLAY` is normally a real user desktop
and should not be used for automated verification.

## Commands (mobile app, `mobile/`)

```bash
cd mobile
flutter pub get
flutter analyze
flutter test
flutter build apk --release --split-per-abi   # release Android build, as CI does
```

## Architecture (desktop app)

MVC-inspired, with domain models fully decoupled from their Qt graphical representation (`Actor` model ≠
`ActorNodeItem` view) and a registry-driven type system instead of hardcoded dispatch.

- **`app.core.models`** — pure domain layer, zero PyQt6/controller/UI imports. `BaseNode` is abstract;
  concrete node "types" (actor, agent, hard_goal, soft_goal, plan, resource) are all one class,
  `TypedNode`, parameterized by a `type_name` string that's looked up in the `NODE_STYLES` dict (label,
  color, border_color, text_color) inside `typed_node.py` — adding a new node type is a dict entry, not a
  new file/class. `CompositeModelWrapper` pairs an "external" model (the canvas-level node) with an
  "internal" model (its mirror inside its own subcanvas) so a node can act as both an endpoint and a
  container; writes to `SYNCED_PROPERTIES` (label/color/border_color/text_color) propagate to both and fire
  change callbacks, everything else only touches the external model. There is currently no equivalent
  registry for edge *domain* models — edges only exist as `app.ui.components` graphics items (see below);
  `BaseEdge` was removed as dead code.
- **`app.ui.components`** — the `QGraphicsItem`/`QGraphicsObject` view layer. `BaseNodeItem`/`BaseTroposItem`
  wrap a `TypedNode` (or a `CompositeModelWrapper`) as `self.model`; `BaseEdgeItem` implements the shared
  poly-line/control-point/arrow-head machinery that every `*ArrowItem` subclass in `dependency_item/`
  inherits (edge *type* only changes `paint()`/arrow-head styling, not the geometry). The pure geometry math
  behind `BaseEdgeItem` (segment distance, point-at-percentage-along-path, arrow-head triangle) lives in
  `app.utils.edge_geometry` as plain functions independent of any Qt scene state — prefer adding new path
  math there, not as `BaseEdgeItem` methods, so it stays testable without a `QApplication`.
- **`app.controllers`** — `CanvasController` is a composition root built from mixins (`CanvasStateController`,
  `CanvasNodeController`, `CanvasInteractionController`, `CanvasDeletionController`, `CanvasExportController`,
  `CanvasImportController`), all extending `CanvasControllerMixin` (a `NotImplementedError`-stub interface
  so each mixin type-checks independently even though they call each other's methods). `CanvasRegistryController`
  holds the three lookup tables everything else dispatches through: `_NODE_MAP` (type string → item class),
  `_MODEL_MAP` (type string → model factory, used for composite/internal models), `_ARROW_TYPES` (type
  string → arrow item class). Import/export and command code goes through these tables instead of
  hardcoding per-type branches.
- **`app.commands`** — `QUndoCommand` subclasses pushed onto `CanvasController.undo_stack`. They receive the
  controller as a loosely-typed parameter (not a concrete `CanvasController` import) specifically to avoid
  a circular import, since `app.controllers` is what drives `app.commands`, not the reverse.
- **`app.validation`** — `Rule` is an ABC (`applies_to(action_type)`, `check(context) -> str | None`).
  `Validator` holds an explicit list of rule instances (built in `validator.py`, no filesystem scanning).
  Six of the seven rules are the same "reject this arrow type between two entities" shape and are generated
  from a `{arrow_type: description}` table by `NoLinkBetweenEntitiesRule` in
  `validation/rules/no_link_between_entities.py`; `NoEntityInEntitySubcanvas` is the one structurally
  different rule (different `action_type`, different context keys) and stays its own file. A rule only
  fires when `Validator.active` is `True` (Validation menu toggle).
- **`app.utils.astr_format`** — the `.astr` (JSON) project save/load format. `AstrFormat.serialize_scene`
  walks live `BaseNodeItem`/`BaseEdgeItem` instances; import is the reverse, in
  `CanvasImportController.import_from_astr`. Each node/edge is imported inside its own `try/except` — a
  malformed entry is logged and skipped (reported to the user in one summary dialog at the end), not an
  abort of the whole load. Composite (subcanvas-linked) nodes are the trickiest part of import: the
  `.astr` format doesn't store an explicit internal↔external link id, so `import_from_astr` *reconstructs*
  the link heuristically (the composite node's first outgoing edge → that edge's target's subcanvas → the
  nearest same-type child by stored `position_in_subcanvas_*`), logging a warning and surfacing a
  non-fatal dialog item when more than one candidate matches.
- **`app.i18n`** — `tr(text)` does an **exact-string dict lookup** into `es.json` (loaded by
  `load_language("es")`); there is no `en.json` — English is whatever string is passed to `tr()`. This
  means any string passed to `tr()` that should be translatable must match an `es.json` key **byte-for-byte**,
  including cases built with an f-string/`.format()` — when adding a new user-facing message assembled
  from parts, add the fully-assembled result (not the template) as the `es.json` key.
- **`app.model_types` / `app.controller_types`** — `Protocol`-based type contracts so packages can type
  against each other without importing concrete classes. `model_types.py` has zero internal imports;
  `controller_types.py` imports concrete `app.ui.components` classes to build its aliases (`CanvasNodeItem`,
  `CanvasSelection`) — a deliberate asymmetry, not an oversight.

### Property-update invariant

`BaseNodeItem.update_properties()` / `BaseTroposItem.update_properties()` apply an incoming property dict
to a model via `setattr` for any key the model `hasattr`s. Guard this against ever matching a *method* name
on the model (`node_type`, `toggle_subcanvas`, `get_internal_model`, …) — `hasattr` alone doesn't
distinguish a data attribute from a bound method, and `setattr`ing over a method silently replaces it with
whatever value was in the dict, breaking every later call to it. Both implementations check
`not callable(getattr(self.model, key))` before assigning; keep that check if you touch either method, and
don't add new keys to `get_serializable_properties()` that collide with a model method name.

## Known-stale doc

`docs/architecture_packages.md` (and its companion `.drawio`) describes the pre-refactor layout: it still
shows `app.core.models.entity/` / `.tropos_element/` / `.dependency/` as separate per-type files and
describes `Validator` as auto-discovering rules via `pkgutil`. Both were collapsed into the
`TypedNode`/`NODE_STYLES` and explicit-rule-list design described above. Treat that doc as historical
context, not current fact, until it's regenerated.
