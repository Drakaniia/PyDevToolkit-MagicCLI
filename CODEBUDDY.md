# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

**Magic CLI (PyDevToolkit-MagicCLI)** is a powerful, secure developer toolkit that provides Git operations, project management, and web development automation through an interactive CLI. Users type `magic` to access the main menu system.

## Essential Commands

### Installation & Setup
```bash
# Clone and setup
bash scripts/setup.sh

# Install in development mode
pip install -e .

# Install with all dev dependencies
pip install -e ".[dev,test]"
# or
make install-dev

# Run the application
python src/main.py
# or
make run
# or (after installation)
magic
```

### Testing
```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing
# or
make test

# Run specific test file
python tests/test_security.py

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration
```

### Code Quality
```bash
# Format code
make format
# Runs: black src/ tests/ && isort src/ tests/

# Check formatting without changes
make format-check

# Run linting
make lint
# Runs: flake8, mypy, bandit, safety check

# Security audit
make audit
# Runs: safety check && bandit -r src/

# Run all checks (CI-style)
make check-all
# Runs: format-check, lint, test
```

### Building & Distribution
```bash
# Build package
make build

# Clean build artifacts
make clean
```

## Architecture

### Directory Structure
```
src/
├── main.py              # Entry point (executed via 'magic' command)
├── menu.py              # MainMenu class definition
├── core/                # Core functionality
│   ├── menu/           # Menu system (base, renderer, navigation, handler)
│   ├── security/       # Security validation and sanitization
│   └── utils/          # Utilities (config, git_client, logging, exceptions)
├── modules/             # Feature modules
│   ├── git_operations/ # Git push, pull, status, stash, changelog, etc.
│   ├── web_development/# Dev mode for web projects
│   ├── backend_development/ # Backend scaffolding & database tools
│   └── project_management/  # Structure viewer, folder navigator
├── ui/                  # UI components (banners)
└── cli/                 # CLI entry points

config/                  # Configuration files
├── default.yaml        # Default operational settings
├── development.yaml    # Development-specific config
└── security.yaml       # Security policies
```

### Key Architecture Patterns

**Menu System**: All menus inherit from `core.menu.base.Menu` abstract class. Menus define items via `setup_items()` and use `MenuItem` objects that link labels to callable actions. The menu system includes:
- `MenuRenderer`: Handles display, viewport adaptation, and scrolling
- `MenuNavigation`: Handles arrow key navigation and user input
- Automatic terminal size detection and responsive scrolling

**Module Organization**: Features are organized into self-contained modules under `src/modules/`. Each module can define its own menu (inheriting from `Menu`) and expose functionality through menu items.

**Security Layer**: `core.security.validator.SecurityValidator` provides centralized validation for:
- Command input sanitization (checks for dangerous characters, command injection)
- Path validation (prevents directory traversal)
- File extension validation
- Configuration-driven security policies (see `config/security.yaml` and root `config.yaml`)

**Git Operations**: Uses a centralized `GitClient` abstraction (`core.utils.git_client`) that wraps subprocess calls. Git operations modules include:
- Progressive retry strategies for push operations
- Automatic changelog generation after successful pushes
- Commit recovery and stash management
- Git submodule manager

**Configuration**: Uses YAML-based configuration with layered loading:
- `config/default.yaml`: Operational settings
- `config/security.yaml`: Security policies
- Root `config.yaml`: Active configuration (merged settings)

### Important Implementation Details

**Entry Point Flow**:
1. `bin/magic` shell script → calls Python
2. `src/main.py` → imports and runs `MainMenu`
3. `src/menu.py` defines `MainMenu` which inherits from `core.menu.Menu`
4. Menu items link to feature modules in `src/modules/`

**Windows Compatibility**: 
- The codebase explicitly handles Windows console encoding (UTF-8 setup in `src/main.py`)
- Uses `sys.platform == "win32"` checks throughout

**Dev Mode (Web Development)**:
Located in `src/modules/web_development/dev_mode/`. Provides:
- Frontend project creation (React, Next.js, Vue, Svelte, React Native, etc.)
- Running dev servers and builds
- Test execution (JS/Python)
- Port management (killing ports)
- Dependency installation
- Code formatting setup (Prettier)
- Docker quick commands

**Backend Development**:
Located in `src/modules/backend_development/backend/`. Provides:
- Database setup and connection config
- API scaffolding (FastAPI, Flask, DRF, Express.js)
- Auth and user management scaffolding
- Prisma tools and PostgreSQL commands

**Error Handling**: Centralized exception hierarchy in `core.utils.exceptions`:
- `AutomationError` (base)
- `GitError`, `GitCommandError`, `UncommittedChangesError`
- Decorator `@handle_errors` for consistent error handling
- `ExceptionHandler` class for formatted error output

## Testing Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── fixtures/            # Test fixtures
├── unit/               # Unit tests
├── integration/        # Integration tests
├── test_security.py    # Security validation tests
├── test_error_handling.py
├── test_integration.py
└── testall.py          # Comprehensive test runner
```

**Test Markers**:
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.unit`: Unit tests

Run specific test types: `pytest -m unit` or `pytest -m "not slow"`

## Configuration Files

- `pyproject.toml`: Modern Python project configuration (preferred)
- `setup.py`: Legacy setup file (maintained for compatibility)
- `config.yaml`: Active runtime configuration
- `config/`: Directory with layered config files
- `requirements.txt`: Runtime dependencies
- `requirements-dev.txt`: Development dependencies
- `Makefile`: Development task automation

## Changelog System

The project includes automatic changelog generation:
- **Automatic**: Triggered after each successful Git push
- **Manual**: Via GitHub Operations menu → "Generate Changelog"
- **CLI**: `python src/modules/git_operations/changelog.py generate [N]`
- Generates from git commit history with smart formatting

## Python Version & Dependencies

- **Python 3.7+** required
- Core dependencies: PyYAML, colorama, pyfiglet, termcolor
- Optional backend dependencies: FastAPI, Flask, Django REST Framework, SQLAlchemy
- Dev dependencies: pytest, black, isort, flake8, mypy, bandit, safety

## Code Style

- **Formatter**: Black (line length: 88)
- **Import sorting**: isort (black-compatible profile)
- **Type hints**: Enforced via mypy (strict configuration)
- **Linting**: flake8
- **Security**: bandit + safety

Configuration in `pyproject.toml` under `[tool.black]`, `[tool.isort]`, `[tool.mypy]`

## Git Workflow Notes

- The system includes sophisticated Git push retry logic with progressive strategies
- Handles upstream tracking, hook bypassing, and force-push scenarios
- Auto-generates changelog on successful pushes
- Provides commit recovery tools for reflog-based recovery
