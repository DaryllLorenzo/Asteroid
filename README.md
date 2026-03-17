# 🌌 Asteroid — Interactive Diagramming I* Tropos Desktop App

![](images/AsteroidLogo.png)

**Asteroid** is a desktop application built with **Python** and **PyQt6** to create interactive, model-driven diagrams — ideal for visualizing Tropos-style actor-agent relationships, dependencies, and resources.  
It follows a clean **MVC-inspired architecture**, strictly separating **core models**, **UI components**, and **controllers** for maximum modularity and maintainability.

> 💡 Built with **`uv`** as the *exclusive* Python package manager — no `pip`, no `venv` manual setup. Just `uv`.

---

## 🚀 Features

- **Interactive QGraphicsView canvas** with:
  - Drag & drop nodes from a sidebar (Actor, Agent, Goal, Resource, etc.)
  - Support for **simple and dashed arrows** (dependencies)
  - Zoom in/out, pan, and reset view
- **PDF Export** with two modes:
  - Diagram image only
  - Diagram + detailed element information (classification and relationships)
- **Logical models decoupled** from graphical representation (e.g., `Actor` ≠ `ActorNodeItem`)
- **Controller layer** managing interactions between UI and domain logic
- **Extensible design**: Easily add new node types, edge styles, or behaviors
- **Built for collaboration**: Clear separation enables team development and testing

---

## 🏗️ Project Structure

```bash

.
├── app
│   ├── controllers
│   │   ├── canvas_controller.py      # Logic for managing canvas interactions and state
│   │   └── __init__.py
│   ├── core                          # Core business logic and data structures
│   │   ├── __init__.py
│   │   └── models                    # Backend data models for graph elements
│   │       ├── base_edge.py          # Abstract base class for all connections
│   │       ├── base_node.py          # Abstract base class for all nodes
│   │       ├── dependency            # Model definitions for Tropos/i* links
│   │       │   ├── and_decomposition_edge.py
│   │       │   ├── contribution_edge.py
│   │       │   ├── dashed_edge.py
│   │       │   ├── dependency_link_edge.py
│   │       │   ├── __init__.py
│   │       │   ├── means_end_edge.py
│   │       │   ├── or_decomposition_edge.py
│   │       │   ├── simple_edge.py
│   │       │   └── why_link_edge.py
│   │       ├── entity                # Model definitions for high-level entities
│   │       │   ├── actor.py
│   │       │   ├── agent.py
│   │       │   └── __init__.py
│   │       ├── __init__.py
│   │       └── tropos_element        # Model definitions for internal goals/tasks
│   │           ├── hard_goal.py
│   │           ├── __init__.py
│   │           ├── plan.py
│   │           ├── resource.py
│   │           └── soft_goal.py
│   ├── __init__.py
│   ├── ui                            # User Interface components (PyQt6)
│   │   ├── canvas.py                 # Main drawing area implementation
│   │   ├── components                # Reusable visual graphic items
│   │   │   ├── base_edge_item.py     # Base visual class for links
│   │   │   ├── base_node_item.py     # Base visual class for entity nodes
│   │   │   ├── base_tropos_item.py   # Shared logic for Tropos-specific shapes
│   │   │   ├── dependency_item       # Visual items for dependency links
│   │   │   │   ├── and_decomposition_edge_item.py
│   │   │   │   ├── contribution_edge_item.py
│   │   │   │   ├── dashed_edge_item.py
│   │   │   │   ├── dependency_link_edge_item.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── means_end_edge_item.py
│   │   │   │   ├── or_decomposition_edge_item.py
│   │   │   │   ├── simple_edge_item.py
│   │   │   │   └── why_link_edge_item.py
│   │   │   ├── entity_item           # Visual items for Actors and Agents
│   │   │   │   ├── actor_node_item.py
│   │   │   │   ├── agent_node_item.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── position_controll_widget.py # Widget to adjust subcanvas offsets
│   │   │   ├── properties_panel.py   # Side panel for editing element attributes
│   │   │   ├── subcanvas_item.py     # Logic for nested canvas (Actor internal view)
│   │   │   └── tropos_element_item   # Visual items for goals, plans, and resources
│   │   │       ├── hard_goal_item.py
│   │   │       ├── plan_item.py
│   │   │       ├── resource_item.py
│   │   │       └── soft_goal_item.py
│   │   ├── help                      # Documentation and help system
│   │   │   ├── content               # Markdown help files
│   │   │   │   ├── about.md
│   │   │   │   ├── elements.md
│   │   │   │   ├── examples.md
│   │   │   │   └── quick_help.md
│   │   │   ├── help_modal.py         # Modal window for documentation
│   │   │   └── markdown_viewer.py    # Renderer for markdown help files
│   │   ├── __init__.py
│   │   ├── main_window.py            # Main application window assembly
│   │   └── sidebar.py                # Toolbar for selecting elements to draw
│   └── utils
│       └── astr_format.py            # Utilities for data serialization/formatting
├── images                            # Static assets and icons
│   ├── AsteroidLogo.png
│   ├── elements_help                 # Documentation icons for elements
│   ├── examples_help                 # Visual guides for help system
│   └── main_interface_examples.png   # Interface screenshots
├── LICENSE
├── main.py                           # Application entry point
├── pyproject.toml                    # Project metadata and dependencies
├── README.md                         # Project documentation
└── uv.lock                           # Locked dependency versions

```

---

## ⚙️ Requirements

- ✅ **Python 3.12.3+**
- ✅ **[uv](https://github.com/astral-sh/uv)** — *the only package manager used*
- ✅ **PyQt6**

> 🛑 **No `pip`, no `requirements.txt` installation via pip.**  
> This project uses **`uv`** exclusively to manage virtual environments and dependencies — ensuring fast, deterministic, and reproducible setups across all platforms.

---

## 📦 Installation & Setup (Using `uv`)

### Step 1: Install `uv` (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2...

### Step 3: Run project
```bash
uv run main.py
```

# Examples
![Main interface 1](images/main_interface_example1.png)
![Main interface 2](images/main_interface_example2.png)
![Main interface 3](images/main_interface_example3.png)


## 📋 TODO & Roadmap

- [x] **Actor/agent node movement within subcanvas** — Allow reorganization of child nodes internally *(completed Dec 24)*
- [x] **Size property for component names** — Configurable text size for different components
- [x] **Multi-line text labels** — Support for writing text in multiple lines within node labels
- [x] **Review of softgoal visual component** — check for a better form of softgoal ui component 
- [ ] **Cross-platform packaging** — Research options for:
  - `.deb`/APT package (golden dream for Linux)
  - Windows installer (NSIS/InnoSetup)
  - macOS app bundle
  - PyInstaller/Cx_Freeze as intermediate solution
- [ ] **Visual themes** — Customizable light/dark theme system
- [ ] **Model validation** — Diagram consistency verification according to Tropos methodology
- [ ] **Undo/redo history** — Complete undo/redo system for all actions
- [x] **Keyboard shortcuts** — Comprehensive shortcut system for common operations
- [ ] **Diagram templates** — Pre-built templates for common Tropos patterns
- [ ] **Flexible link shape** — The user should be able to drag specific points of a link to change its shape to be more flexible and not just pure straight

---

**✨ Contributions Welcome** — Feel free to fork the project or open issues to discuss new features!