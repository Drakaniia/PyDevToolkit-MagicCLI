# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common commands

All commands below assume the working directory is the project root (`PyDevToolkit-MagicCLI`).

### Initial setup

The project is designed to be installed via the provided setup script (see `README.md` and `CONTRIBUTING.md`):

```bash
bash setup.sh
```

This script:
- Validates Python (>= 3.7) and Git
- Installs Python dependencies from `requirements.txt`
- Configures a shell alias (`magic`) that runs the main menu

If you want to reproduce what the script does manually for Python deps:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt  # only if you are using the pytest-based tests described in tests/README.md
```

### Running the CLI locally

From the project root you can run the main menu directly without the alias:

```bash
python main.py
```

Alternate entrypoint (functionally equivalent, used by the `magic` alias):

```bash
python src/magic.py
```

Both entrypoints construct and run `menu.MainMenu`, which exposes:
- **GitHub Operations** – interactive Git flows
- **Show Project Structure** – tree-style view of the current project
- **Navigate Folders** – interactive directory navigation
- **Dev Mode (Web Dev Automation)** – frontend/dev-server/test helpers
- **Backend Dev (Backend Automation)** – backend scaffolding and DB/API/auth tools

### Tests

There are two testing approaches referenced in this repo.

1. **Python test suite (pytest-based)**

`tests/README.md` documents a pytest/unittest-style test layout (security, error handling, integration, and `testall.py`). When that suite is present, the canonical commands are:

```bash
# Run all tests via pytest
python -m pytest tests/ -v

# Run orchestration script
python tests/testall.py

# Run a single test file
python tests/test_security.py
```

Before using these commands, check that the corresponding files actually exist under `tests/` (they have been added and removed over time in this repo).

2. **Dev Mode test runner (language-agnostic)**

From the main menu (`python main.py`), choose:

> Dev Mode (Web Dev Automation) → Run Tests (All Types)

The `Run Tests` Dev Mode command:
- Auto-detects test frameworks from `package.json` (e.g., Jest, Vitest, Mocha, Cypress) and from Python tooling (`pytest.ini`, `pyproject.toml`, `test_*.py`, etc.)
- Presents an arrow-key-driven menu of detected test commands
- Executes the selected test command, streaming output and handling cross-platform encoding differences

This is the preferred way to run tests for Node/JS projects that live alongside this CLI.

## High-level architecture

### Top-level structure and entrypoints

- `main.py` – primary entrypoint for the "Python Automation System"; ensures UTF‑8 console behavior on Windows, adds `src/` to `sys.path`, and launches the main menu.
- `src/magic.py` – secondary entrypoint used by the `magic` shell alias created in `setup.sh`; also instantiates `menu.MainMenu` and runs it.
- `src/menu.py` – defines `MainMenu`, the central interactive menu for the tool. It wires together several subsystems:
  - Git operations (`git_operations.GitMenu`)
  - Project structure viewer (`structure_viewer.StructureViewer`)
  - Folder navigator (`folder_navigator.FolderNavigator`)
  - Web-oriented Dev Mode (`dev_mode.dev_mode.DevModeMenu`)
  - Backend automation menu (`backend.backend_menu.BackendDevMenu`)

The rest of the codebase is organized into packages under `src/` that plug into this menu system.

### Core menu and interaction framework (`src/core` + `src/menu.py`)

The menu/rendering/navigation stack is shared across all interactive features:

- `core.menu_base` defines:
  - `MenuItem` – a simple label + callback pair
  - `Menu` – abstract base for all menus; owns the list of `MenuItem`s, a `MenuRenderer`, and a `MenuNavigation` instance, and provides `run()` which loops until a menu item returns the sentinel string `"exit"`.
- `core.menu_renderer` handles all terminal-oriented rendering concerns:
  - Reads terminal size and caches it (`TerminalInfo`)
  - Implements responsive layouts with scrollable menus when there are more items than visible lines
  - Provides arrow-key selection highlighting with efficient partial redraws to avoid flicker
  - Displays current working directory and shows context-appropriate footer instructions
- `core.menu_navigation` abstracts away keyboard input handling:
  - Detects whether arrow keys are supported via `termios`/`tty` (Unix) or `msvcrt` (Windows)
  - Provides `get_choice_with_arrows(...)`, which loops reading keypresses and updates the selected item index; falls back to numeric input when arrow keys aren't available
- `menu.MainMenu` composes all top-level menus and reuses this common infrastructure. Every submenu in `backend`, `dev_mode`, and `github` is either a direct subclass of `core.menu_base.Menu` or built on top of it.

When adding new interactive features, prefer to:
- Subclass `core.menu_base.Menu` (or re-use helpers in `core.menu_handler`) instead of writing custom input loops.
- Use the existing arrow-key navigation APIs so UX stays consistent with the rest of the tool.

### Configuration, security, logging, and exceptions (`src/core`)

The core package centralizes cross-cutting concerns that other modules rely on.

**Configuration (`core.config`)**

- `SecurityConfig` and `OperationalConfig` are dataclasses representing security-related and operational settings respectively (command length limits, allowed file extensions, logging behavior, etc.).
- `ConfigManager` handles:
  - Discovering or creating a config file (`config.yaml`/`config.json` in the CWD or `~/.magiccli/config.{yaml,json}`)
  - Serializing both configs as YAML (if `pyyaml` is installed) or JSON as a fallback
  - Providing getters/setters for individual security/operational settings
- Module-level helpers (`get_config_manager`, `get_security_config`, `get_operational_config`) expose a lazily-initialized global configuration instance used by logging and other systems.

**Error handling (`core.exceptions`)**

- Defines an exception hierarchy rooted in `AutomationError`, with a severity field (`ErrorSeverity`) and optional details/suggestions for user-facing messaging.
- Git-specific subclasses (`GitError`, `GitCommandError`, `NotGitRepositoryError`, `NoRemoteError`, `GitNotInstalledError`, `UncommittedChangesError`, etc.) encapsulate the most common failure modes and embed human-readable guidance.
- `ExceptionHandler` provides centralized printing/formatting and a `handle_errors(...)` decorator that wraps functions, catching `AutomationError` (and generic `Exception`) and printing structured errors instead of raw tracebacks. Git workflows such as the enhanced push flow use this decorator.

**Security (`core.security`)**

- `SecurityValidator` implements strict regex-based validation for:
  - Command strings (`validate_command_input`) to block separators, pipes, command substitution, null bytes, etc.
  - Paths and filenames (`validate_path`, `validate_file_name`) to prevent directory traversal and disallow paths that escape the project root.
  - Git branch names (`validate_branch_name`) to enforce Git's naming rules and avoid dangerous constructs.
- Sanitization helpers (`sanitize_command_input`, `sanitize_path`) validate and either return the input or raise `AutomationError` instead of attempting risky "fixups".
- `safe_subprocess_run(cmd, **kwargs)` wraps `subprocess.run`, validating each `cmd` element via `SecurityValidator` and forcing `shell=False` even if the caller attempts to override it.
- `safe_input` / `safe_path_input` implement validated user input for commands and paths.

When writing new code that shells out or accepts user-provided paths/commands:
- Prefer `SecurityValidator.safe_subprocess_run` (or manual `validate_*` checks) over raw `subprocess.run`/`Popen`.
- Use the existing exception types from `core.exceptions` to describe failures, so they integrate with the standardized error UX.

**Logging (`core.logging`)**

- `SecurityAuditLogger` configures a `logging` logger based on `OperationalConfig` (log level and optional log file path) and provides structured audit helpers:
  - `audit_security_event`
  - `audit_command_execution`
  - `audit_input_validation_failure`
- Helper functions (`log_security_event`, `log_command_execution`, `log_input_validation_failure`) provide a thin functional interface, and are integrated into `core.git_client` and other modules.

### Git client and GitHub operations (`src/core/git_client.py`, `src/github`) 

**Core Git client (`core.git_client`)**

- `GitClient` is the canonical abstraction around Git CLI operations. It:
  - Validates commands through `SecurityValidator` and logs them for auditing
  - Encapsulates subprocess invocation with consistent encoding/timeout behavior
  - Provides high-level methods such as `status`, `has_uncommitted_changes`, `add`, `commit`, `log`, `current_branch`, `create_branch`, `has_remote`, `push`, `pull`, `reset`, and `init`
- Errors are raised as `GitError`/`GitCommandError` (and friends), rather than bare exceptions, for better UX.
- `get_git_client(...)` exposes a singleton-style accessor with an optional override for per-directory instances.

Any new Git-related functionality should use `GitClient` (via `get_git_client`) instead of invoking `git` directly.

**Interactive Git flows (`src/github`)**

The `github` package implements higher-level, user-facing Git workflows on top of `GitClient` and the menu framework:

- `git_status.GitStatus` – runs `git status --verbose`, parses the output into staged/unstaged/untracked sections, and colorizes lines using `termcolor` when available.
- `git_pull.GitPull` – orchestrates safe pull operations:
  - Verifies the directory is a Git repo and has a configured remote
  - Fetches first with a simple spinner, checks if there are remote changes, and warns about local uncommitted changes
  - Offers options to discard local changes (via `git reset --hard HEAD`) or cancel before pulling
  - Supports both standard pull and pull-with-rebase flows
- `git_push.GitPushRetry` – performs a multi-step push with retries and automatic changelog generation:
  - Runs pre-push checks (repo presence, remotes, uncommitted changes)
  - Applies a series of `PushStrategy` variants (normal, `--set-upstream`, `--no-verify`, `--force-with-lease`, `--force`) with exponential backoff and optional user confirmation for destructive operations
  - On success, uses a `ChangelogGenerator` (external module referenced in this repo) to append entries to `CHANGELOG.md`

Other modules under `src/github/` (e.g., `git_log`, `git_diff`, `git_stash`, `git_recover`, `git_initializer`) follow the same pattern: present a menu- or prompt-driven UX and call into `GitClient` and `core.security` rather than shelling out directly.

### Dev Mode – web/frontend automation (`src/dev_mode`)

Dev Mode provides a layered system for frontend project creation, running dev servers, managing ports, installing dependencies, running tests, and dockerizing projects.

- `_base.DevModeCommand` (not shown here) is the base class for Dev Mode commands; individual commands subclass it and expose `label`, `description`, and a `run(interactive: bool = True, **kwargs)` method.
- `dev_mode.DevModeMenu` is a `Menu` subclass that:
  - Imports the various `COMMAND` instances from sibling modules (e.g., `create_frontend`, `run_project`, `test_project`, `port_killer_command`, `install_deps`, `format_code`, `docker_quick`)
  - Populates menu items from those command objects and routes selection to `command.run(interactive=True)`

Key commands:

- `create_frontend.CreateFrontendCommand`
  - Interactive scaffolder for modern frontend and mobile frameworks (React, Next.js, Vue, Angular, Svelte/SvelteKit, Nuxt, Vite, Astro, Remix, Gatsby, Solid, Qwik, React Native/Expo/Ionic/Capacitor/Flutter, T3, Blitz, Redwood, etc.).
  - Validates presence of Node, guides the user through framework, package manager, TypeScript, CSS stack, target directory, and optional Git init.
  - Builds the underlying `npx`/CLI commands in a cross-platform way (with special handling for Windows) and handles basic error reporting.
  - Exposes a non-interactive `run(...)` variant for programmatic use.

- `run_project.RunProjectCommand`
  - Discovers `package.json` in the current directory and inspects `scripts` for common entries (`dev`, `start`, `build`, `serve`, `preview`).
  - Presents them as a menu, then runs the chosen script via the appropriate package manager (`npm`, `pnpm`, or `yarn`, detected from lock files).
  - Uses `subprocess.Popen` with platform-specific parameters (e.g., `shell=True` on Windows) and streams output line-by-line, handling Unicode/encoding issues gracefully.

- `test_project.TestProjectCommand`
  - Auto-detects JS test scripts (e.g., `npm run test`, `test:unit`, `test:integration`, `test:e2e`) from `package.json` and infers the underlying framework when possible (Jest, Vitest, Mocha, Cypress, Playwright, or generic `npm` script).
  - Detects Python test setups via `pytest` configuration, presence of `test_*.py`, and standard unittest naming patterns.
  - Provides both interactive and non-interactive modes and normalizes command execution across platforms while streaming logs.

Supporting modules such as `port_killer`, `port_killer_command`, `port_manager`, `install_deps`, `format_code`, and `docker_quick` implement specialized automation flows (port cleanup, dependency installation, code formatting, and Docker orchestration) that are exposed through Dev Mode menus.

### Backend automation (`src/backend`)

The backend package exposes a parallel automation surface focused on server-side development.

- `backend_menu.BackendDevMenu` is a `Menu` subclass that instantiates and wires four main subsystems into a single "Backend Development Automation" menu:
  - `DatabaseManager` (DB setup and configuration)
  - `APIGenerator` (API scaffolding)
  - `AuthManager` (authentication and user management)
  - `FrameworkTools` (backend framework project generators)

Representative responsibilities:

- `database.db_manager.DatabaseManager`
  - Detects probable DB usage by scanning common config files (`requirements.txt`, `Pipfile`, `pyproject.toml`) and DB file extensions.
  - Guides creation of SQLite DB files or JSON-based connection configs for PostgreSQL/MySQL/MongoDB/Redis and writes them to `database_config.json`.
  - Provides follow-on flows for generating connection strings, environment-specific configs, and basic connection tests.

- `api.api_generator.APIGenerator`
  - Implements interactive menus to scaffold REST APIs for several frameworks (FastAPI, Flask, Django REST Framework, Express.js).
  - Generates framework-specific handler files (e.g., `*_api.py`, route blueprints) with basic CRUD endpoints and in-memory storage, along with documentation/testing helpers.

- `auth.auth_manager.AuthManager`
  - Presents options for JWT/session/OAuth/API-key authentication setups.
  - Generates modules such as `jwt_auth.py`, `user_model.py`, and corresponding Flask routes for registration/login, including password hashing and token issuance.

- `framework.framework_tools.FrameworkTools`
  - Can scaffold a full FastAPI application tree (app package, core config/security, database setup, API routing, tests, Docker artifacts, and `.env.example`).
  - Uses nested dictionary representations of the desired directory tree and writes them out to disk.

These backend tools are designed to be invoked from within a project you want to augment; they primarily operate via interactive menus rather than being composed as imports.

### Loading and progress utilities (`core/loading.py`)

Long-running tasks across the repo reuse a shared set of loading/progress UI helpers:

- `LoadingSpinner` – configurable animated spinner usable as a context manager or manual start/stop.
- `LoadingDots` – simpler dot animation variant.
- `ProgressBar` – text progress bar for known-size operations.
- `loading_animation(...)`, `run_with_loading(...)`, and the `with_spinner` decorator – convenience functions for instrumenting functions with loading feedback while preserving control flow.

These are used in various modules (e.g., Git workflows, Dev Mode commands) to provide consistent UX for blocking operations.

## How to extend or modify behavior safely

When using Warp Agents to modify this project:

- For **new menus or interactive flows**, build on `core.menu_base.Menu` and, where appropriate, the helper patterns in `core.menu_handler` so that arrow-key navigation, viewport handling, and the "type number to select" fallback work consistently.
- For **Git and filesystem operations**, route through `core.git_client.GitClient` and `core.security.SecurityValidator` (or `safe_subprocess_run`) instead of invoking `subprocess` with `shell=True` or unvalidated command strings.
- For **new long-running automation tasks**, consider wrapping them with `core.loading.run_with_loading` or `with_spinner` to match the project's existing UX patterns.
- For **errors and user-facing failures**, raise or wrap them as `AutomationError`/`GitError` subclasses so they integrate with the standardized formatting and suggestions defined in `core.exceptions`.
