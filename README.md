# Magic CLI

**One command to rule them all** - A powerful, secure developer toolkit that puts Git operations, project management, and web development automation at your fingertips.

![PyPI](https://img.shields.io/pypi/v/pydevtoolkit-magiccli)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![Security](https://img.shields.io/badge/security-audited-brightgreen)

---

**Just type `magic` in your terminal and get instant access to powerful development automation.**

---

## How to Use

### Installation

#### Option 1: Automated Global Installation (Recommended - No Python Required!)
Install globally with our automated installer - **Python not required!**

```bash
# One-liner installation (works on Linux, macOS, Windows)
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh | bash

# Or download and run manually:
wget https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh
bash install.sh

# Use anywhere
magic
```

**What this installer does:**
- ✅ Detects your operating system
- ✅ Installs Python 3.8+ automatically (if needed)
- ✅ Installs the package and sets up the `magic` command
- ✅ Configures your shell environment
- ✅ Works on any system with bash (Linux/macOS) or Git Bash (Windows)

#### Option 2: Manual Installation (For Advanced Users)
If you already have Python installed:

```bash
# Install via pip
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git

# Or from PyPI (when published)
pip install pydevtoolkit-magiccli
```

#### Option 3: Development Installation
For contributors:

```bash
# Clone and develop
git clone https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
cd PyDevToolkit-MagicCLI
pip install -e .
```

> **Note**: The automated installer eliminates all complexity. Just run one command and you're ready to go!

### Uninstallation

#### Global Installation Removal (Recommended)
To completely remove the automated installation:

```bash
# Use the uninstall script (handles everything automatically)
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/uninstall.sh | bash

# Or download and run manually:
wget https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/uninstall.sh
bash uninstall.sh
```

The uninstall script automatically:
- Removes the package from all Python installations
- Cleans up configuration files and cache
- Removes the global `magic` command
- Restores your shell configuration

#### Manual Removal (Advanced)
If you installed manually via pip:

```bash
# Remove the package
pip uninstall pydevtoolkit-magiccli

# Remove installation directory
rm -rf ~/.pydevtoolkit-magiccli

# Clean shell config (remove PATH entries manually)
```

#### Development Installation Removal
For development installations:

```bash
# Remove the package
pip uninstall -e .

# Optional: Remove repository
cd ..
rm -rf PyDevToolkit-MagicCLI
```

### Quick Start

Once installed, just type `magic` in any directory:

```bash
$ magic
```

Then use arrow keys ↑↓ to navigate and Enter to select!

## Sample Terminal Output

```bash
$ magic

======================================================================
  Python Automation System - Main Menu
======================================================================
  Current Directory: /home/user/my-project
======================================================================

   1. GitHub Operations
    2. Show Project Structure
    3. Navigate Folders
    4. Dev Mode (Web Dev Automation)
    5. Exit

======================================================================

  Use ↑/↓ arrow keys to navigate, Enter to select, or type number

# Select "GitHub Operations" →

======================================================================
  GitHub Operations
======================================================================
  Current Directory: /home/user/my-project
======================================================================

    1. Push to GitHub (Auto-commit)
    2. Pull from GitHub
    3. Repository Status
    4. Commit Recovery
    5. Generate Changelog
    6. Git Submodule Manager
    7. Back to Main Menu

# Select "Push to GitHub" →

======================================================================
GIT PUSH (With Auto-Retry & Auto-Changelog)
======================================================================

Refreshing Git state...
Found 3 changed files:
   M  src/components/Button.tsx
   A  src/utils/helpers.ts
   M  README.md

Commit message:
```

---

## Prerequisites

- **Python 3.7+**
- **Git** (optional but recommended for full functionality)
- **Bash shell** (Linux/macOS) or **Git Bash** (Windows)

## Project Structure

```
magic_cli/
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Production dependencies
├── README.md              # This file
├── magic_cli/             # Main package
│   ├── __init__.py
│   ├── __main__.py         # Module entry point
│   ├── cli/               # CLI presentation layer
│   │   ├── __init__.py
│   │   ├── main.py        # CLI entry point
│   │   ├── menu.py        # Main menu
│   │   ├── menu_base.py   # Base menu classes
│   │   ├── renderer.py    # Menu rendering
│   │   └── navigation.py  # Input handling
│   ├── core/              # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── exceptions.py  # Error handling
│   │   └── security.py    # Security utilities
│   ├── domain/            # Business logic
│   │   ├── __init__.py
│   │   ├── git/          # Git domain models & services
│   │   ├── project/      # Project management domain
│   │   └── backend/      # Backend development domain
│   ├── infrastructure/    # External dependencies
│   │   ├── __init__.py
│   │   ├── git_client.py # Git operations
│   │   └── file_system.py # File operations
│   ├── application/       # Application services & use cases
│   │   ├── __init__.py
│   │   ├── services/     # Application services
│   │   └── use_cases/    # Use case orchestrators
│   ├── presentation/      # Presentation layer
│   │   ├── __init__.py
│   │   └── ui/           # UI components & banners
│   └── plugins/          # Plugin system
│       ├── __init__.py
│       └── registry.py   # Plugin management
├── assets/               # Static assets (fonts, etc.)
├── scripts/              # Setup and utility scripts
└── tests/                # Test suite
    ├── __init__.py
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Development notes

- **Architecture**: The codebase follows Domain-Driven Design (DDD) principles with clean architecture:
  - `magic_cli/core/` - Cross-cutting concerns (config, exceptions, security)
  - `magic_cli/domain/` - Business logic and domain models
  - `magic_cli/application/` - Application services and use cases
  - `magic_cli/infrastructure/` - External dependencies and adapters
  - `magic_cli/presentation/` - UI and CLI presentation layer
- **Entry Points**: Multiple ways to run:
  - `python -m magic_cli` (module execution)
  - `magic` (installed script)
  - `python magic_cli/cli/main.py` (direct execution)
- **Web Development (Dev Mode)**: from the main menu, opens tools for:
  - Creating modern frontend/mobile projects (React, Next.js, Vue, Svelte, React Native, etc.).
  - Running Node-based dev servers (`npm run dev`, `npm run start`, etc.).
  - Running JS/Python tests via the "Run Tests (All Types)" option.
- **Backend Development**: from the main menu, opens tools for:
  - Database setup and connection config.
  - API scaffolding (FastAPI, Flask, DRF, Express.js).
  - Auth and user-management scaffolding.
- **Running tests directly** (when Python tests are present under `tests/`):
  - All tests via pytest:
    ```bash
    python -m pytest tests/ -v
    ```
  - Or a specific test file:
    ```bash
    python tests/test_security.py
    ```
- **Changelog Generation**: The system includes automatic and manual changelog generation:
  - Automatic: Changelog is updated after each successful Git push
  - Manual: Access via GitHub Operations → Generate Changelog menu option
  - Command line: `python src/modules/git_operations/changelog.py generate [N]`
- For Warp users, repository-specific agent rules and commands are documented in `WARP.md`.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - feel free to use this in your own projects!

---

**Made for developers who love automation**