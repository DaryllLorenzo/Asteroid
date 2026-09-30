---
name: run
description: Launch and verify the Asteroid PyQt6 desktop app (app/ + main.py) without opening a window on the user's real display. Use whenever asked to run, test, or confirm a change works in the desktop app.
---

# Running Asteroid (desktop app)

This is a PyQt6 `QGraphicsView`/`QGraphicsScene` desktop app, not a web app or CLI — there is no dev
server and no automated test suite (no `pytest`, no `tests/` directory). Verifying a change means actually
constructing the app's objects and exercising them.

**Important**: `DISPLAY` in this environment is normally the user's real desktop session, not a disposable
CI display. Do not launch `main.py` directly (`python main.py`) for automated verification — that pops a
real window on the user's screen. Xvfb (a virtual display) is also unreliable to keep alive across separate
Bash tool calls in this sandbox (background processes tend to get reaped between commands) — don't spend
time fighting it. Instead, do everything below with `QT_QPA_PLATFORM=offscreen`, which runs the full Qt
paint/layout pipeline without any real display and is completely invisible to the user.

## Setup

```bash
cd /home/daryll/asteroid
source .venv/bin/activate   # or: uv sync  if the venv doesn't exist yet
```

## Static checks (fast, always run these first)

```bash
ruff check app main.py
ruff format --check app main.py   # add --fix / drop --check to actually reformat
mypy app main.py
```

## Headless functional smoke test

A `QApplication` is required even offscreen (Qt object construction needs one alive). Build the real
`Canvas` + `CanvasController` — don't test through `AstrFormat`/model classes in isolation only, since the
interesting bugs tend to live in the controller glue between them.

```bash
export QT_QPA_PLATFORM=offscreen
python3 << 'EOF'
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
app = QApplication(sys.argv)

# QMessageBox.warning/critical block on exec() waiting for a click - stub them
# out to capture what the app *would* show the user instead of hanging.
shown = {"warning": [], "critical": []}
QMessageBox.warning = staticmethod(lambda *a, **k: shown["warning"].append(a[2] if len(a) > 2 else ""))
QMessageBox.critical = staticmethod(lambda *a, **k: shown["critical"].append(a[2] if len(a) > 2 else ""))

from app.ui.canvas import Canvas
from app.controllers.canvas_controller import CanvasController
from app.controllers.canvas_registry_controller import _NODE_MAP, _ARROW_TYPES
from app.utils.astr_format import AstrFormat

canvas = Canvas()
controller = CanvasController(canvas)

# Create one of every node type through the real controller (exercises
# _NODE_MAP, not just the model classes directly).
nodes = [controller.add_node(t, i * 150, 0) for i, t in enumerate(_NODE_MAP)]
assert all(nodes)

# Create one of every edge type between two of them.
edges = []
for cls in _ARROW_TYPES.values():
    e = cls(nodes[0], nodes[1])
    canvas.scene().addItem(e)
    controller.edges.append(e)
    edges.append(e)

# Export -> reimport into a fresh controller, the riskiest path for changes
# touching astr_format.py / canvas_import_controller.py.
import json, tempfile, os
data = AstrFormat.serialize_scene(controller.nodes, controller.edges)
fd, path = tempfile.mkstemp(suffix=".astr")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    json.dump(data, f)

controller2 = CanvasController(Canvas())
ok = controller2.import_from_astr(path)
os.unlink(path)

print("import ok:", ok, "warnings:", shown["warning"], "criticals:", shown["critical"])
print("nodes:", len(controller2.nodes), "edges:", len(controller2.edges))
assert ok and not shown["critical"]
print("SMOKE TEST PASSED")
EOF
```

For composite (subcanvas-linked) nodes specifically: set `controller.selected_nodes_for_arrow = [src, dst]`
and `controller.composite_node_type = "hard_goal"` (or another Tropos type), then call
`controller.create_composite_dependency()` — it returns `(mid_node, internal_node, e1, e2)`, which you add
to `canvas.scene()` / `controller.nodes` / `controller.edges` the same way `AddCompositeDependencyCommand`
does. This path (composite export → reimport → relink) is where subtle bugs hide, since the `.astr` format
has no explicit internal↔external link id and import has to reconstruct it heuristically.

To simulate a malformed `.astr` file (verifying per-element import error isolation), write a hand-built
scene dict missing a required key (e.g. a node without `"position"`) and confirm `import_from_astr` still
returns `True`, still imports the good elements, and populates `shown["warning"]` with one entry per
skipped element — it should never abort the whole load or show `criticals` for a single bad element.

## Visual confirmation without a real display

`QGraphicsScene.render()` works fully offscreen — use it to produce an actual PNG you can inspect with the
`Read` tool, exactly like `CanvasExportController.export_to_image` does:

```python
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import Qt

scene = canvas.scene()
rect = scene.itemsBoundingRect()
rect.adjust(-20, -20, 20, 20)
pixmap = QPixmap(int(rect.width()), int(rect.height()))
pixmap.fill(Qt.GlobalColor.white)
painter = QPainter(pixmap)
painter.setRenderHint(QPainter.RenderHint.Antialiasing)
scene.render(painter, source=rect)
painter.end()
pixmap.save("/tmp/.../preview.png")
```

Then `Read` the PNG path directly — layout/color/shape regressions in `app.ui.components` (node fills,
arrow heads, subcanvas open/closed state) are visible this way without ever touching the user's screen.

## Mobile app (`mobile/`)

Unrelated Flutter project, different toolchain — see its own CI at
`.github/workflows/flutter-build.yml`: `flutter pub get && flutter analyze && flutter test`.
