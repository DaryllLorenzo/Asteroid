# Asteroid — Package Architecture

Companion document for [`architecture_packages.drawio`](architecture_packages.drawio). Open the diagram
side by side with this file — the section headings below match the ten package boxes drawn there, and
the dependency table matches the thirteen arrows.

## What Asteroid is

Asteroid is a PyQt6 desktop application for building interactive **i\*** and **Tropos** diagrams (actors,
agents, goals, resources, plans, and their dependency links). It follows an MVC-inspired layout: a pure
Python domain model, a QGraphicsScene-based view layer, and a controller layer that mediates between them.

## How to read the diagram

- **Folder-shaped boxes** are Python packages (`app.ui`, `app.controllers`, …) or the entry module (`main.py`).
- **Dashed arrows** are real import/usage dependencies found in the source, each labeled with *why* the
  dependency exists — not just *that* it exists.
- **Color = architectural layer**: blue is Presentation, orange is Orchestration, purple is Commands,
  green is Domain, yellow is Validation, gray is Infrastructure, teal is the shared type-contracts package.
- **The red arrow** (`app.utils → app.controllers`) is deliberately called out in a different color. It is
  the one dependency that runs *against* the normal top-down flow — see [The one inverse dependency](#the-one-inverse-dependency) below.
- The diagram intentionally omits `app.i18n`'s incoming edges: `tr()` is called from almost every package,
  and drawing that fan-in from all of them added noise without adding insight.

## Packages

### `main.py` — Entry point
Creates the `QApplication` and instantiates `MainWindow`. Nothing else in the codebase imports it, so it
only ever appears as a source node in the diagram.

### `app.ui` — Presentation
The application shell: `MainWindow`, `Canvas` (the `QGraphicsView`/`QGraphicsScene` surface), `Sidebar`
(drag source for new nodes/arrows), `ThemeManager`, `PDFExportDialog`, and the `help/` subpackage
(`HelpModal`, `MarkdownViewer`). It owns a `CanvasController` and forwards user interaction to it; it does
not contain diagramming logic itself.

### `app.ui.components` — Graphics items
The visual half of every diagram element, built on `QGraphicsItem`/`QGraphicsObject`. Base classes
(`BaseNodeItem`, `BaseEdgeItem`, `BaseTroposItem`, `SubCanvasItem`, `ControlPointHandle`,
`PropertiesPanel`) are specialized by three subpackages that mirror the domain model one-to-one:

| Subpackage | Classes |
|---|---|
| `entity_item/` | `ActorNodeItem`, `AgentNodeItem` |
| `tropos_element_item/` | `HardGoalNodeItem`, `SoftGoalNodeItem`, `PlanNodeItem`, `ResourceNodeItem` |
| `dependency_item/` | `DependencyLinkArrowItem`, `WhyLinkArrowItem`, `OrDecompositionArrowItem`, `AndDecompositionArrowItem`, `ContributionArrowItem`, `MeansEndArrowItem` |

Each item instantiates and wraps the matching class from `app.core.models` — the logical model and its
graphical representation are deliberately kept as separate objects (`Actor` ≠ `ActorNodeItem`).

### `app.controllers` — Orchestration
The mediator between UI and domain. `CanvasController` is a **composition root** built entirely out of
mixins: it inherits from `CanvasStateController`, `CanvasNodeController`, `CanvasInteractionController`,
`CanvasDeletionController`, `CanvasExportController`, and `CanvasImportController`, all of which extend a
shared `CanvasControllerMixin` base that declares the full interface (as `NotImplementedError` stubs) so
each mixin can be type-checked independently. `CanvasRegistryController` holds three static lookup tables
(`_NODE_MAP`, `_MODEL_MAP`, `_ARROW_TYPES`) that map a `node_type` string to the concrete item class and
model class to instantiate — this registry is what lets `app.commands` and the import/export controllers
create nodes without hard-coding a type dispatch everywhere.

### `app.commands` — Undo/Redo commands
Eleven `QUndoCommand` subclasses (`AddNodeCommand`, `DeleteNodeCommand`, `AddEdgeCommand`,
`DeleteEdgeCommand`, `MoveNodeCommand`, `ResizeNodeCommand`, `ChangePropertyCommand`,
`ChangeControlPointsCommand`, `AddSubcanvasNodeCommand`, `AddCompositeDependencyCommand`,
`ToggleSubcanvasCommand`) pushed onto `CanvasController.undo_stack`. Each command receives the controller
as a loosely-typed parameter (not a concrete `CanvasController` import) specifically to avoid a circular
import, since `app.controllers` is what imports and drives `app.commands`.

### `app.core.models` — Domain (pure)
The i\*/Tropos metamodel itself: abstract `BaseNode` and `BaseEdge`, plus `CompositeModelWrapper` (which
keeps an "external" and an "internal" model in sync for nodes that have an expandable sub-canvas). Three
subpackages hold the concrete elements:

| Subpackage | Classes |
|---|---|
| `entity/` | `Actor`, `Agent` |
| `tropos_element/` | `HardGoal`, `SoftGoal`, `Plan`, `Resource` |
| `dependency/` | `DependencyLinkEdge`, `WhyLinkEdge`, `OrDecompositionEdge`, `AndDecompositionEdge`, `ContributionEdge`, `MeansEndEdge` |

This package imports nothing else in the app — no PyQt6, no controllers, no UI, no utils. It only uses
`abc.ABC`/`abstractmethod` from the standard library, which is why it sits at the bottom of the diagram with
no outgoing arrows.

### `app.validation` — Business rules
A small Strategy/plugin engine: `Rule` is an abstract base (`applies_to`, `check`), and `Validator`
auto-discovers every `Rule` instance under `validation/rules/` via `pkgutil.iter_modules` at startup — no
rule has to be registered by hand. The seven current rules (`NoEntityInEntitySubcanvas`,
`NoAndDecompositionBetweenEntities`, `NoContributionBetweenEntities`, `NoDependencyLinkBetweenEntities`,
`NoMeansEndBetweenEntities`, `NoOrDecompositionBetweenEntities`, `NoWhyLinkBetweenEntities`) all encode i\*
well-formedness constraints, e.g. rejecting a dependency link drawn directly between two entities.

### `app.utils` — Export & serialization
Three independent services: `AstrFormat` (the `.astr` project save/load format), `PDFGenerator`
(reportlab-based PDF export), and `AgentReportExporter` (renders a one-page visual report per agent).

### `app.model_types` / `app.controller_types` — Shared type contracts
Two small modules whose only job is to let packages type against each other without importing each
other's concrete classes:

- **`model_types.py`** defines `NodeModelLike`, `CompositeModelLike`, and `ModelFactory` as `Protocol`s.
  It has **zero internal imports** — it's pure typing surface.
- **`controller_types.py`** defines the `CanvasNodeItem`/`CanvasSelection` type aliases and the
  `NodeItemFactory` `Protocol`. Unlike its sibling, it *does* import concrete classes from
  `app.ui.components` (`BaseEdgeItem`, `BaseNodeItem`, `BaseTroposItem`, `SubCanvasItem`) to build those
  aliases — a small, deliberate asymmetry between the two modules that the diagram shows as a single
  `type contracts` arrow from `app.ui.components`.

### `app.i18n` — Internationalization
`tr(text)`, `load_language(lang)`, `get_language()`. Strings are authored in English directly in the source
and looked up in `es.json` when Spanish is active; `tr()` simply returns the original text unchanged if no
translation is found (which is also what happens in English mode, since there's no `en.json`). Used
throughout the codebase; omitted from the diagram's arrows for clarity (see [How to read the diagram](#how-to-read-the-diagram)).

## Cross-package dependencies

Each row is one arrow in the diagram, in the same order (`e1`–`e13`).

| # | From | To | Label | Why |
|---|---|---|---|---|
| e1 | `main.py` | `app.ui` | instantiates | `main()` creates the `MainWindow`. |
| e2 | `app.ui` | `app.controllers` | delegates to | `MainWindow` owns and drives a `CanvasController`. |
| e3 | `app.ui` | `app.ui.components` | uses items | `MainWindow` directly references `BaseEdgeItem`, `PropertiesPanel`, etc. |
| e4 | `app.ui` | `app.utils` | exports via | `PDFExportDialog` uses `PDFGenerator`; the report menu uses `AgentReportExporter`. |
| e5 | `app.ui.components` | `app.core.models` | wraps models | Each item class instantiates and wraps its matching domain model (`ActorNodeItem` ↔ `Actor`). |
| e6 | `app.ui.components` | shared type contracts | type contracts | `controller_types.py` imports the concrete item base classes to build its type aliases. |
| e7 | `app.controllers` | `app.ui.components` | via registry | `CanvasRegistryController._NODE_MAP` maps node types to item classes to instantiate. |
| e8 | `app.controllers` | `app.commands` | pushes commands | `CanvasController.undo_stack.push(...)` for every undoable action. |
| e9 | `app.controllers` | `app.core.models` | instantiates models | `CanvasRegistryController._MODEL_MAP` maps node types to domain model classes. |
| e10 | `app.controllers` | `app.validation` | validates actions | Every mutating action is checked against `Validator` before it's applied. |
| e11 | `app.controllers` | `app.utils` | serializes (.astr) | `CanvasExportController` saves/loads projects through `AstrFormat`. |
| e12 | `app.utils` | `app.controllers` | reads (inverse dep.) | `AgentReportExporter` reads the live `CanvasController` state — see below. |
| e13 | `app.utils` | `app.ui.components` | reads geometry | `AgentReportExporter` reads item positions/labels to lay out its report. |

## Notable design decisions

**Mixin composition, not inheritance chains.** `CanvasController` doesn't build up its behavior through a
deep inheritance hierarchy; it composes six single-purpose mixins side by side. Each mixin can be read,
tested, and typed independently against the shared `CanvasControllerMixin` interface.

**Commands don't import their invoker.** `app.commands` is driven by `app.controllers`, so if a command
imported `CanvasController` directly, the two packages would form a circular import. Every command instead
takes the controller as an untyped/duck-typed parameter — a small, deliberate coupling trade-off in exchange
for avoiding the cycle.

**Validation rules register themselves.** Adding a new i\* well-formedness constraint means dropping a new
file into `validation/rules/` with a module-level `rule = SomeRule()` — `Validator` finds it automatically
via `pkgutil`. Nothing else needs to change.

**The domain layer has no outgoing dependencies.** `app.core.models` never imports PyQt6, `app.controllers`,
`app.ui`, or `app.utils`. The i\*/Tropos metamodel can be reasoned about, tested, and reused independently of
the desktop UI built on top of it.

**Two typing modules with different purity levels.** `model_types.py` is dependency-free and could be lifted
into any project; `controller_types.py` trades a bit of that purity for the convenience of aliasing concrete
UI item types directly. The diagram's single `type contracts` arrow from `app.ui.components` reflects that
`controller_types.py` side of the pair.

### The one inverse dependency

`app.utils.AgentReportExporter` reads directly from a live `CanvasController` (its nodes, edges, and their
properties) to build its report — meaning `app.utils`, a package everything else exports *through*, also
reaches back *up* into `app.controllers`. This is the one edge in the diagram that runs against the general
top-down flow (Presentation → Orchestration → Commands/Validation/Utils → Domain), and it's colored red for
that reason. It's a pragmatic shortcut rather than a layering violation to fix: the report needs the exact
in-memory state of the open project, and `CanvasController` is where that state lives.

## Quick reference — "where do I add a new one of these?"

| Task | Package |
|---|---|
| New i\* element type (node) | `app.core.models` (model) + `app.ui.components` (item) + `CanvasRegistryController` (register it) |
| New dependency/arrow type | Same three spots, under `dependency/` / `dependency_item/` |
| New undoable action | `app.commands` (new `QUndoCommand`) |
| New well-formedness constraint | `app.validation/rules/` (new `Rule`, self-registers) |
| New export format | `app.utils` |
| New UI panel/dialog | `app.ui` |
| New translated string | `app.i18n/es.json`, `app.i18n/en.json` |
