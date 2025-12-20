# Agent Instructions for PyDevToolkit-MagicCLI

## Build/Lint/Test Commands

**Install package:** `pip install -e .` or `pip install -e ".[dev,test]"`

**Run all tests:** `python -m pytest tests/ -v --cov=magic_cli --cov-report=term-missing`

**Run single test:** `python -m pytest tests/test_filename.py::TestClass::test_function_name -v`

**Run linting:** `make lint` (includes flake8, mypy, bandit, safety)

**Format code:** `make format` (black + isort)

**Check formatting:** `make format-check`

**Build package:** `python -m build`

## Code Style Guidelines

### Formatting
- **Line length:** 88 characters (Black default)
- **Formatter:** Black with default settings
- **Import sorting:** isort with Black profile

### Type Hints
- **Required:** All functions must have type hints (`disallow_untyped_defs = true`)
- **Strict mode:** mypy with full strict checking enabled
- Use `typing` module for complex types (Dict, List, Optional, etc.)

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last (prefixed with `from src.` when needed)
- One import per line, sorted alphabetically within groups

### Naming Conventions
- **Functions/variables:** snake_case
- **Classes:** PascalCase
- **Constants:** UPPER_SNAKE_CASE
- **Modules:** lowercase with underscores if needed

### Error Handling
- Use custom `AutomationError` hierarchy from `core.utils.exceptions`
- Provide helpful error messages with suggestions
- Wrap external operations in try-catch with meaningful error messages
- Use `@handle_errors()` decorator for automatic error handling

### Code Structure
- Use dataclasses for configuration objects
- Add comprehensive docstrings to all public functions/classes
- Follow single responsibility principle
- Prefer composition over inheritance

### Security
- Always validate user inputs
- Use path sanitization from security config
- Avoid executing untrusted commands
- Log security events appropriately

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->