# Contributing to Asteroid

Thank you for your interest in contributing to Asteroid. This guide will help you get started.

## Getting Started

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

## Reporting Bugs

Before opening an issue:
1. Check if it already exists in the issue tracker
2. Use the bug report template
3. Include clear steps to reproduce the problem
4. Add screenshots if they help explain the issue

## Feature Requests

When suggesting a feature:
- Explain the problem you are trying to solve
- Describe your proposed solution
- Mention if you can help implement it

## Pull Requests

### Steps
1. Fork the repository and create a branch from `development`
2. Make your changes
3. Test that the application still runs without errors
4. Open a Pull Request

### PR Checklist
- Code follows existing style
- Code must pass code quality job (ruff and mypy)
- No unnecessary dependencies added
- Commit messages are clear and descriptive
- Changes tested manually (app runs without errors)

## Code Style

Try to follow the existing code style. Consistency is more important than perfection. Look at how similar features are implemented and match that approach.

## Questions?

Open a [GitHub Discussion](https://github.com/DaryllLorenzo/asteroid/discussions) or tag `@DaryllLorenzo`.

---

Thank you for contributing.
