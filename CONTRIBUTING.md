# Contributing to Asteroid

Thank you for your interest in contributing to Asteroid! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- Basic knowledge of PyQt6

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/asteroid.git
cd asteroid

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv run main.py

# Or with pip
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -e .
```

## 📁 Project Structure

- **`app/core/models/`** → Pure data models (no Qt)
- **`app/ui/components/`** → Qt graphical items
- **`app/controllers/`** → Business logic
- **`app/utils/`** → Helpers (PDF export, etc.)

**Important:** Keep Qt out of `core/` folder.

## 🐛 Reporting Bugs

Before opening an issue:
1. Check if it already exists
2. Use the bug report template
3. Include steps to reproduce
4. Add screenshots if possible

## 💡 Feature Requests

When suggesting a feature:
- Explain the problem you're solving
- Describe your proposed solution
- Mention if you can help implement it

## 🔧 Pull Requests

### Steps
1. Fork the repo and create a branch from `development`
2. Make your changes
3. Test that the app still runs
4. Open a Pull Request

### PR Checklist
- [ ] Code follows existing style
- [ ] No unnecessary dependencies
- [ ] Clear commit messages
- [ ] Changes tested manually (app runs without errors)

## 📝 Code Style

Try to follow the existing code style. Consistency is more important than perfection.

## ❓ Questions?

Open a [GitHub Discussion](https://github.com/DaryllLorenzo/asteroid/discussions) or tag `@DaryllLorenzo`.

---

**Thanks for contributing!** 🌟
