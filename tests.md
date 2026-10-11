# Test Suite

Automated tests for the Asteroid desktop app (`app/` + `main.py`). The suite runs headless: no display
server is required, so it works identically from a local terminal, an IDE, and CI.

The suite is deliberately scoped to the claims the tool makes about **Tropos structural conformance** and
about **state preservation**, rather than to general GUI behaviour. Rendering, zoom, pan, and drag
interactions are deliberately out of scope; they are presentation concerns that carry no methodological
claim.

---

## Commands

```bash
# Install dependencies (first time only)
uv sync

# Run the whole suite
uv run pytest

# Equivalent, without uv
pytest

# Verbose: one line per test
uv run pytest -v

# A single file
uv run pytest tests/test_tropos_semantics.py

# A single test class or test
uv run pytest tests/test_tropos_semantics.py::TestRegistryConstraints
uv run pytest tests/test_tropos_semantics.py::TestRegistryConstraints::test_entities_have_no_subcanvas_model

# Filter by keyword
uv run pytest -k "roundtrip"
uv run pytest -k "not i18n"

# Stop at the first failure (useful while debugging)
uv run pytest -x

# Show why each skip/xfail happened
uv run pytest -ra
```

### Coverage

```bash
# Terminal report
uv run pytest --cov=app --cov-report=term

# Per-package breakdown, which is the figure reported in the paper
uv run pytest --cov=app --cov-report=term-missing

# Machine-readable output for CI
uv run pytest --cov=app --cov-report=xml
```

### Running outside `uv`

The suite needs the project dependencies plus `pytest` and `pytest-cov`:

```bash
pip install -e .
pip install pytest pytest-cov
pytest
```

### Headless guarantee

`tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen` **before** PyQt6 is imported, so a `QApplication` can
be constructed with no display attached. The fixture also stubs the blocking `QMessageBox` calls, because
`QMessageBox.exec()` waits for a click and would hang the suite. `pytest` is therefore safe to invoke with
no environment setup on any machine.

---

## What is covered

**119 tests across 5 files.** Every test drives the real `Canvas` + `CanvasController` rather than the
domain classes in isolation, so the assertions also prove the code paths are wired together.

| File | Tests | Lines | Claim it supports |
|---|---:|---:|---|
| `tests/test_tropos_semantics.py` | 80 | 347 | Tropos structural conformance ("seven well-formedness rules") |
| `tests/test_astr_roundtrip.py` | 14 | 360 | `.astr` persistence and lossless reload |
| `tests/test_export.py` | 14 | 227 | Export: PDF and per-agent report images |
| `tests/test_i18n.py` | 6 | 111 | Translation catalogue integrity |
| `tests/test_undo_redo.py` | 5 | 137 | Command stack integrity |
| `tests/conftest.py` | — | 129 | Fixtures and typed helpers |

---

### 1. `test_tropos_semantics.py` — Tropos structural conformance

This is the file that carries the methodology claim. It asserts the well-formedness rules **twice**: once
against the isolated `Rule` class, and once end-to-end through the controller, so the suite proves the
rules are wired into the interaction path and not merely defined.

#### `TestSevenWellFormednessRules`

Directly pins the "seven rules" claim. Two things are checked, because they are easy to confuse:

1. `Validator` registers exactly **7 rule instances**.
2. All seven actually **fire** through `validate()` — a rule that existed but was unreachable would pass
   the first check alone.

| Test | Cases | Asserts |
|---|---:|---|
| `test_validator_registers_exactly_seven_rules` | 1 | `len(validator._rules) == 7` |
| `test_each_arrow_type_has_exactly_one_firing_rule` | 6 | exactly one error comes back per arrow type, so no arrow type has zero or duplicate guards |
| `test_subcanvas_rule_fires` | 2 | the nested-Actor and nested-Agent paths each return exactly one error |
| `test_distinct_rule_classes_are_two` | 1 | documents why "seven" counts constraints, not classes |
| `test_every_registered_arrow_type_is_guarded` | 6 | every registered arrow type is blocked between two entities |

**Why `test_distinct_rule_classes_are_two` exists.** `Validator._rules` holds seven instances but only
two distinct classes: six are `NoLinkBetweenEntitiesRule`, generated from a `{arrow_type: description}`
table, and one is `NoEntityInEntitySubcanvas`. Read as class names, the rule set looks like two rules;
read as constraints, it is seven. Git history shows there *were* seven separate files and classes until
they were collapsed into the table-driven generator, so a reviewer cross-checking source files against a
"seven rules" claim needs this assertion to see that the count is preserved.

#### `TestDependencyLinksBetweenEntities`

A dependency link is only meaningful between Tropos elements, never between two Actors or Agents. Each of
the six registered arrow types is exercised in all three endpoint combinations.

| Test | Cases | Asserts |
|---|---:|---|
| `test_entity_to_entity_is_rejected` | 6 | `create_arrow()` returns `None` and `controller.edges` stays empty, for each arrow type |
| `test_entity_to_tropos_is_accepted` | 6 | the rule requires *both* endpoints to be entities, so a mixed pair is legal |
| `test_tropos_to_tropos_is_accepted` | 24 | all six arrow types across all four Tropos element types are accepted |
| `test_validator_inactive_permits_everything` | 1 | the Validation menu toggle gates the whole rule set |
| `test_rule_message_names_the_arrow_type` | 6 | each rejection surfaces exactly one message naming the arrow type |

#### `TestEntityInsideEntitySubcanvas`

Subcanvases hold Tropos elements, never nested Actors or Agents.

| Test | Cases | Asserts |
|---|---:|---|
| `test_entity_child_is_rejected` | 2 | adding an `actor` or `agent` creates no node and reports one error |
| `test_tropos_child_is_accepted` | 4 | all four Tropos element types are added successfully |
| `test_only_entity_parents_are_restricted` | 6 | a non-entity parent accepts every child type, entity or not |

#### `TestRegistryConstraints`

Structural invariants encoded in the three lookup tables that drive all dispatch.

| Test | Asserts |
|---|---|
| `test_entities_have_no_subcanvas_model` | `_MODEL_MAP` has **no** `actor`/`agent` entry, while `_NODE_MAP` does |
| `test_tropos_elements_have_a_model` | every Tropos element type has both a node class and a model factory |
| `test_every_node_type_has_a_style` | `_NODE_MAP` keys and `NODE_STYLES` keys are identical |
| `test_every_arrow_type_has_a_validation_rule` | `_ARROW_TYPES` keys and `_LINK_DESCRIPTIONS` keys are identical |
| `test_styles_are_complete` | every `NODE_STYLES` entry defines all four style keys |

`test_entities_have_no_subcanvas_model` is the single assertion that most directly encodes the Tropos
distinction: an entity has no internal sub-canvas model, so `create_composite_dependency` cannot
manufacture one for it.

#### `TestValidator`

Direct tests of the `Validator` engine itself, covering the inactive default, the two action types it
responds to, and the fact that unrelated actions are ignored.

---

### 2. `test_astr_roundtrip.py` — `.astr` persistence

#### `TestRoundTripFidelity`

Builds a scene containing one node of every registered type and one edge of every registered arrow type,
then round-trips it.

| Test | Asserts |
|---|---|
| `test_synthetic_scene_reload_is_a_fixpoint` | serialise → import → serialise → import → serialise is stable |
| `test_node_and_edge_counts_survive` | node and edge counts are preserved |
| `test_node_types_and_labels_survive` | node types and labels are preserved |
| `test_edge_endpoints_survive` | every edge keeps its type, source id, and target id |

#### `TestRealProjectFiles`

Exercises the two real diagrams checked into the repository root, which are real-world inputs rather than
synthetic ones.

| Test | Cases | Asserts |
|---|---:|---|
| `test_fixtures_exist` | 1 | the `.astr` fixtures are present |
| `test_import_matches_recorded_metadata` | 2 | loaded node and edge counts equal the counts recorded in the file's `metadata`, with no critical dialogs |
| `test_reload_is_a_fixpoint` | 2 | the same fixpoint property holds for real files |
| `test_visual_properties_survive` | 2 | label, colour, border colour, text colour, and radius survive unchanged |

#### `TestCompositeDependencyRoundTrip`

Composite nodes are the trickiest case, because the `.astr` format stores no explicit internal-to-external
link id, so `import_from_astr` reconstructs the pairing heuristically.

| Test | Asserts |
|---|---|
| `test_internal_node_is_reimported_into_the_subcanvas` | the internal node survives and the diagram's node and edge counts are preserved |
| `test_internal_external_pairing_is_preserved` | after reload, the wrapper still pairs the correct external and internal models |

#### `TestErrorIsolation`

A malformed element must be skipped, never fatal to the whole load.

| Test | Asserts |
|---|---|
| `test_node_without_position_is_skipped` | the good nodes still load, one warning is recorded, no critical dialog |
| `test_unknown_node_type_is_skipped` | an unregistered `type` is skipped without aborting the load |
| `test_edge_with_missing_endpoint_is_dropped` | an edge referencing a non-existent node id is dropped |
| `test_truncated_file_is_reported_not_raised` | a malformed JSON file returns `False` and raises nothing |

---

### 3. `test_export.py` — Export

Backs the paper's export claim. Assertions are on observable output — the magic bytes of the produced
file, its presence, and the dialog the user would have been shown — not on reportlab's internals.

#### `TestPdfExport`

| Test | Asserts |
|---|---|
| `test_produces_a_valid_pdf` | the file exists, is non-empty, and starts with `%PDF-` |
| `test_succeeds_with_or_without_element_tables` | both values of `with_additional_info` produce a valid PDF |
| `test_additional_info_adds_content` | the flag actually changes the output, rather than being silently ignored |
| `test_reports_success_dialog_with_target` | one `information` dialog carrying the target path |
| `test_cancelled_save_dialog_returns_false` | with no filename, a cancelled dialog returns `False` and creates nothing |
| `test_leaves_no_temporary_image_behind` | `_capture_canvas_image` writes `temp_diagram.png` into the repo root and must clean it up |
| `test_empty_scene_still_produces_a_pdf` | an empty diagram still exports successfully |

#### `TestAgentReportExport`

| Test | Asserts |
|---|---|
| `test_produces_one_image_per_entity` | one PNG per Actor/Agent, and no image for a Tropos element |
| `test_tropos_elements_produce_no_report` | a scene with only Tropos elements returns `False` and writes nothing |
| `test_images_are_valid_pngs` | every output starts with the PNG signature and is non-empty |
| `test_filenames_carry_the_node_label` | the filename is `agente_<n>_<label>.png`, sanitised |
| `test_empty_scene_returns_false` | an empty scene returns `False` |
| `test_visibility_is_restored_after_export` | items hidden during the capture are visible again afterwards |

**A design detail the tests pin down.** `AgentReportExporter.export_reports` filters top-level items with
`isinstance(item, BaseNodeItem)`. Actors and Agents sit on `BaseNodeItem`, while Tropos elements sit on
the sibling class `BaseTroposItem` — both extend `QGraphicsObject` directly, so neither is a subclass of
the other. The consequence is that reports cover entities only. `test_produces_one_image_per_entity`
asserts this explicitly so the scoping is visible rather than implied by a count that happens to pass.

---

### 4. `test_undo_redo.py` — Command stack integrity

Rather than exercising each of the eleven `QUndoCommand` subclasses in isolation, the suite asserts a single
invariant that subsumes them: **the serialised scene is a faithful fingerprint of editor state**, so undoing
every pushed command must reproduce the scene exactly, and redoing them must reproduce the edited state.

| Test | Asserts |
|---|---|
| `test_undo_redo_of_every_command_restores_the_scene` | four commands (add node, add edge, move, resize) fully round-trip: undo reproduces the original fingerprint, redo reproduces the edited one |
| `test_new_commands_are_appended_after_undo` | a command pushed after an undo replaces the redo branch |
| `test_delete_then_undo_restores_the_node` | a destructive command restores the deleted node exactly |
| `test_delete_removes_incident_edges` | deleting a node leaves no dangling edge in the scene |
| `test_stack_starts_empty_and_clean` | a fresh controller has an empty, clean stack |

---

### 5. `test_i18n.py` — Translation catalogue integrity

`tr()` resolves by exact-string lookup against `es.json`. There is no `en.json`: English is the source
language, and a missing key returns the argument unchanged.

| Test | Asserts |
|---|---|
| `test_catalogue_is_valid_json` | `es.json` parses and is non-empty |
| `test_catalogue_entries_are_non_empty_strings` | no key maps to an empty value |
| `test_every_literal_is_translated` | every literal argument passed to `tr()` anywhere in `app/` is a key in `es.json` |
| `test_known_untranslated_list_is_accurate` | the known-exceptions list is accurate in both directions |
| `test_source_language_fallback` | with no catalogue loaded, `tr()` returns its argument unchanged |
| `test_lookup_is_exact_match` | a near-miss (different case, trailing space) does not resolve |

`test_every_literal_is_translated` works by parsing every `.py` file under `app/` with `ast` and collecting
constant arguments to `tr()` calls. Call sites whose argument is dynamic (f-strings, variables) are out of
scope by construction, since their key depends on runtime values.

**Known exception.** `tr("Node")` is called four times in `app/ui/components/properties_panel.py` and is
absent from `es.json`, so it currently renders untranslated. It is listed in the module-level
`KNOWN_UNTRANSLATED` set. That list fails in both directions: adding any *new* untranslated string fails the
suite, and translating `"Node"` also fails until the entry is removed.

---

## Coverage

Measured with `uv run pytest --cov=app --cov-report=term`. The aggregate is **42%**, but the meaningful
figure is the per-package breakdown, because it shows where the testable logic lives:

| Package | Covered | |
|---|---:|---|
| `app/validation` | 44/44 | **100%** |
| `app/i18n` | 14/15 | 93% |
| `app/core` | 147/183 | 80% |
| `app/utils` | 385/532 | 72% |
| `app/controllers` | 763/1253 | 61% |
| `app/commands` | 233/567 | 41% |
| `app/ui` | 900/2800 | 32% |

| Module | Coverage |
|---|---:|
| `app/validation/*` (all modules) | 100% |
| `app/controllers/canvas_registry_controller.py` | 100% |
| `app/i18n/__init__.py` | 94% |
| `app/core/models/typed_node.py` | 92% |
| `app/core/models/base_node.py` | 89% |
| `app/utils/astr_format.py` | 86% |
| `app/utils/pdf_export.py` | 85% |
| `app/core/models/composite_model_wrapper.py` | 77% |
| `app/utils/agent_report_export.py` | 57% |
| `app/utils/edge_geometry.py` | 53% |

Two figures matter for the paper:

- **`app/validation` is at 100%**, which is the evidence for the claim that all seven well-formedness rules
  are implemented and enforced.
- **The domain and validation layers are high while `app/ui` is low.** That contrast is the evidence for the
  architectural decoupling claim: the layer carrying the methodology logic is fully testable without a
  window, and the suite needs no display to exercise it.

Two module-level numbers moved when the export tests were added. `app/utils/edge_geometry.py` rose from
17% to 53%, because rendering a scene for the agent reports now runs the polyline and arrow-head math.
`app/utils/astr_format.py` fell from 91% to 86%, because the suite no longer loads a second `.astr`
diagram from the repository root — one fixture remains and exercises fewer node shapes.

---

## Continuous integration

`.github/workflows/ci.yml` defines two jobs.

**`ruff`** — lint, format check, and `mypy`, on `ubuntu-latest`.

**`test`** — the suite on a three-OS matrix:

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
env:
  QT_QPA_PLATFORM: offscreen
```

Each leg runs `uv run pytest -q`. The `ubuntu-latest` leg additionally produces `coverage.xml`, which is
uploaded as a build artifact.

Note that `mypy` runs with `disallow_untyped_defs = true` over the whole repository, `tests/` included, so
every test function carries a return annotation. `ruff check` and `ruff format --check` cover `tests/` too.

---

## Conventions

- **Headless by default.** Never launch `main.py` to verify a change; construct `Canvas` +
  `CanvasController` under `QT_QPA_PLATFORM=offscreen` instead, so no window appears on a real display.
- **Drive the controller, not the model classes.** Bugs tend to live in the glue between the registry, the
  commands, and the scene. Tests that instantiate `TypedNode` directly miss those.
- **Go through the registries.** Use `_NODE_MAP`, `_MODEL_MAP`, and `_ARROW_TYPES` rather than hardcoding
  type strings, so a new registered type is covered without editing tests.
- **Assert on state, not on call counts.** `controller.nodes` and the serialised fingerprint describe
  observable editor state; they survive refactors that a mock-count assertion would not.
- **Stub dialogs, never wait for them.** Anything reaching `QMessageBox.exec()` will hang the suite; the
  `message_boxes` fixture captures what the user would have been shown.
- **Use the typed helpers.** `make_node(controller, type, x, y)` asserts the controller accepted the node
  and narrows the return type, which keeps the tests free of `cast` calls.