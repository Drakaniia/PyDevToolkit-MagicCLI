# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Key commands

### Environment and installation
- Install in editable mode:
  - `pip install -e .`
- Install with development and test dependencies (preferred for working on the repo):
  - `pip install -e ".[dev,test]"`
  - or `make install-dev`
- Basic editable install via Makefile:
  - `make install`

### Running the CLI
- Installed script (after `pip install`):
  - `magic`
- From the repo root without installing:
  - `python src/main.py`
  - or `python -m src.main`
- The console script entrypoint is defined in `pyproject.toml` as:
  - `magic = "src.main:main"`

### Tests
- Run the full pytest suite with coverage (Makefile):
  - `make test`
- Direct pytest invocation (matches `tests/README.md` and `pyproject.toml` config):
  - `python -m pytest tests/ -v`
- Run the comprehensive import/"smoke" suite:
  - `python tests/testall.py`
- Run a specific test file (examples from `tests/README.md`):
  - `python tests/test_security.py`
  - `python tests/test_error_handling.py`
  - `python tests/test_integration.py`

### Linting, formatting, and security
- Lint/typecheck and security checks (flake8, mypy, bandit, safety):
  - `make lint`
- Format code (black + isort):
  - `make format`
- Check formatting without changing files:
  - `make format-check`
- Aggregate "all checks" target used by CI:
  - `make check-all`
- Security/audit-only target:
  - `make audit`

### Build and release
- Clean build artifacts:
  - `make clean`
- Build the package (wheel/sdist via `python -m build`):
  - `make build`
- Publish to Test PyPI (requires configured credentials):
  - `make upload-test`
- Publish to PyPI (requires configured credentials):
  - `make upload`

## High-level architecture

### Top-level structure
- Python package code lives under `src/`.
  - Entrypoints: `src/main.py` and `src/cli/magic.py`.
  - Core framework and infrastructure: `src/core/`.
  - Feature modules and menus: `src/modules/`.
  - UI helpers (banner, etc.): `src/ui/`.
- Tests live in `tests/` with focused suites (`test_security.py`, `test_error_handling.py`, `test_integration.py`) plus a comprehensive `tests/testall.py` import/coverage harness.

The root `README.md` describes an intended domain-driven layering; the current implementation expresses similar ideas using `core/` and `modules/` under `src/` rather than a `magic_cli/` package directory.

### Entrypoints and main menu
- **`src/main.py`**
  - Primary entrypoint for the "Magic CLI" / Python automation system.
  - Handles Windows console UTF-8 setup, `magic --verify` installation diagnostics, and `--help` handling.
  - Adds `src/` to `sys.path` and instantiates `menu.MainMenu`, then runs the interactive menu loop.
- **`src/cli/magic.py`**
  - Thin wrapper used by the `magic` console script.
  - Imports `MainMenu` from `menu` and runs it; shares the same menu system as `src/main.py`.
- **`src/menu.py` (`MainMenu`)**
  - Orchestrates the top-level UX.
  - Uses the generic `core.menu.Menu` / `MenuItem` abstractions.
  - Wires the main navigation items to feature modules:
    - "GitHub Operations" → `modules.git_operations.GitMenu` (Git workflows, changelog, recovery, branches, stash, etc.).
    - "Show Project Structure" → `modules.project_management.StructureViewer`.
    - "Navigate Folders" → `modules.project_management.FolderNavigator`.
    - "Dev Mode (Web Dev Automation)" → `modules.web_development.DevModeMenu`.
    - "Others" → `modules.others_menu.OthersMenu` (aggregates additional tools such as code quality, analysis, etc.).

### Core menu framework (`src/core/menu/*`)
- **`core.menu.base`**
  - Defines the `Menu` abstract base class and `MenuItem`.
  - `Menu` owns a `MenuRenderer` and `MenuNavigation` instance and implements the generic `run()` loop.
  - All concrete menus (e.g., `MainMenu`, `GitMenu`, `DevModeMenu`) subclass this and implement `setup_items()` to populate `self.items` with `MenuItem` instances.
- **`core.menu.navigation`**
  - Detects whether termios (Unix) or msvcrt (Windows) is available.
  - Provides `MenuNavigation.get_choice_with_arrows(...)` which either:
    - Runs a responsive arrow-key driven loop, or
    - Falls back to "enter a number" input on terminals without low-level key support.
  - Encapsulates key decoding, debouncing, and cross-platform differences.
- **`core.menu.renderer`**
  - Computes terminal size and viewport (via `TerminalInfo`) with caching.
  - Renders headers, current directory line, scroll indicators, and menu items, with partial updates for smooth navigation.
  - Handles ANSI control codes for clearing the screen, hiding/showing the cursor, and drawing highlighted selections.

When adding new menus, reuse this framework instead of implementing custom input/rendering logic.

### Core utilities and security (`src/core/utils/*`, `src/core/security/*`)
- **Configuration (`core.utils.config`)**
  - `ConfigManager` owns two dataclasses:
    - `SecurityConfig` (limits, blocked commands, allowed extensions, timeouts, flags for sanitization and rate limiting).
    - `OperationalConfig` (logging level, color output, loading animations, etc.).
  - Provides helpers `get_config_manager()`, `get_security_config()`, `get_operational_config()` for global access.
  - Default config file detection/creation:
    - Looks for `config.yaml` / `config.json` in the CWD or in `~/.magiccli/`.
    - If no config exists, creates a default `config.yaml` in the current working directory.
- **Exceptions and error handling (`core.utils.exceptions`)**
  - Defines `AutomationError` (base app exception) with severity, details, and suggestions.
  - Git-specific error hierarchy (`GitError`, `GitCommandError`, `NotGitRepositoryError`, `NoRemoteError`, `GitNotInstalledError`, `UncommittedChangesError`, etc.).
  - `ExceptionHandler` centralizes display/handling and exposes `safe_execute()` and the `@handle_errors` decorator used to wrap operations.
  - Tests in `tests/test_error_handling.py` cover the formatting and hierarchy; prefer raising these domain-specific errors instead of raw exceptions.
- **Git client (`core.utils.git_client.GitClient`)**
  - Single abstraction around calling Git with rich error handling.
  - Provides high-level methods (`status`, `add`, `commit`, `log`, branch CRUD, push/pull, reset, init, etc.).
  - Internally validates all command elements via `SecurityValidator` and logs executions with `core.utils.logging.log_command_execution`.
  - Used by the `modules.git_operations.github.*` helpers and by higher-level menus.
- **Security validation (`core.security.validator.SecurityValidator`)**
  - Central place for validating and sanitizing **all external inputs and commands**:
    - `validate_command_input`, `sanitize_command_input` for shell-safe commands.
    - `validate_path`, `sanitize_path` for safe filesystem paths.
    - `validate_file_name` and `validate_branch_name` for file/branch naming.
    - `safe_subprocess_run(cmd, **kwargs)` – validated wrapper around `subprocess.run` that enforces `shell=False` and rejects dangerous tokens.
  - The test suite (`tests/test_security.py`, `tests/test_integration.py`) exercises many edge cases for command injection and path traversal.

When adding new subprocess calls or Git wrappers, route them through `SecurityValidator.safe_subprocess_run` or through `GitClient` instead of calling `subprocess.run` directly.

### Feature modules (`src/modules/*`)

#### Git operations (`src/modules/git_operations/*`)
- **`menu.GitMenu`**
  - Subclass of `core.menu.Menu` that presents the Git-focused submenu under "GitHub Operations".
  - Items include: push (add/commit/push with auto-changelog), status, advanced log, diff operations, pull, initialize-and-push, manual changelog generation, recovery, cache management, submodule management, stash operations, and branch operations.
- **`menu.GitOperations`**
  - Orchestrator used by `GitMenu`.
  - For each operation it constructs short-lived helper objects from `modules.git_operations.github.*` (e.g., `GitStatus`, `GitLog`, `GitPush`, `GitPull`, `GitRecover`, `GitStash`, `BranchMenu`).
  - `initialize_and_push` delegates to `GitInitializer` to bootstrap a new repo and push to GitHub.
  - Manual changelog generation uses `ChangelogGenerator` from `modules.git_operations.changelog` and prompts for number of commits to include.

#### Dev Mode / web development automation (`src/modules/web_development/dev_mode/*`)
- **Pattern**
  - Each Dev Mode action is a `DevModeCommand` implementation (see `dev_mode._base.DevModeCommand`) exposing a `label` and `run(interactive=True)` method.
  - Examples: `create_frontend`, `run_project`, `test_project`, `port_killer`, `install_deps`, `format_code`, `docker_quick`.
- **`dev_mode.DevModeMenu`**
  - Subclass of `Menu` that:
    - Builds its `commands` list in a specific order that controls menu numbering.
    - Creates a `MenuItem` per command, each calling `_execute_command` with the respective `DevModeCommand`.
    - Wraps execution to handle `KeyboardInterrupt` and unexpected exceptions with a consistent UX.
  - Accessible from the main menu under "Dev Mode (Web Dev Automation)".

This Dev Mode layer is the hook point for any new web/frontend automation tasks; follow the existing `DevModeCommand` pattern.

#### Project management and navigation (`src/modules/project_management/*`)
- `StructureViewer` and `FolderNavigator` underpin the main menu options for showing project structure and navigating folders.
- These utilities rely on the shared menu renderer and may call out to the filesystem helpers and security layer when listing and traversing directories.

#### Other modules
- Additional feature areas under `src/modules/` include:
  - `ai_ml`, `api_tools`, `backend_development`, `code_analysis`, `code_quality`, `cross_platform`, `database`, `debugging`, `dependency_management`, `devops`, `documentation`, `monitoring`, `scaffolding`, `security_tools`, `testing_cicd`, `version_control`, and `web_development`.
- These are organized as focused automation domains and are typically surfaced either via the Git, Dev Mode, or "Others" menu paths.

## UI helpers
- **`src/ui/banner.py`**
  - Provides `create_qwenzyy_banner(font_style="...")` to render the QWENZYY banner using `pyfiglet`, with a fallback ASCII banner.
  - `get_available_fonts()` lists fonts that work well with the banner system.

## Testing configuration
- Pytest configuration is defined in `pyproject.toml` under `[tool.pytest.ini_options]`:
  - Test discovery limited to the `tests/` directory; file patterns: `test_*.py`, `*_test.py`.
  - Common markers: `slow`, `integration`, `unit`.
  - Coverage configuration targets `magic_cli`/`src` with multiple report formats (terminal, HTML, XML).
- `tests/test_security.py`, `tests/test_error_handling.py`, and `tests/test_integration.py` provide good reference patterns for:
  - Using `SecurityValidator` and `ConfigManager` correctly.
  - Raising and handling `AutomationError` and its subclasses.
  - Using the security audit logging utilities (`SecurityAuditLogger`, `get_security_logger`).

Future changes that add new subsystems should mirror these existing patterns: expose a clear menu entry, centralize security and configuration in `core`, and cover behavior with focused tests under `tests/` plus import coverage in `tests/testall.py`.