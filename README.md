# Magic CLI

**Magic CLI** is a Python-based developer automation toolkit that provides an interactive CLI menu system for common development tasks. It streamlines Git operations, project management, and web development automation.

### Key Features
- **Interactive Menu System**: Navigate via arrow keys or numbered selection
- **Git Operations**: Auto-commit, push/pull, changelog generation, submodule management, stash operations
- **Web Development**: Scaffold React, Next.js, Vue, Svelte, React Native projects; run dev servers
- **Project Management**: Visualize project structure, navigate folders
- **Security**: Input sanitization, blocked dangerous commands, rate limiting
- **Cross-Platform**: Works on Linux, macOS, and Windows

![PyPI](https://img.shields.io/pypi/v/magic-cli)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![Security](https://img.shields.io/badge/security-audited-brightgreen)

> **Note**: This is a Python CLI tool designed to be installed globally with pip. Python CLI tools are installed using `pip install package-name` rather than npm. This tool can be installed globally with `pip install magic-cli` (once published) or using the installation methods below.

---

**Just type `magic` in your terminal and get instant access to powerful development automation.**

---

## How to Use

### Installation

#### Option 1: Automated Global Installation (Recommended - No Python Required!)
Install globally with our automated installer - **Python not required!**

```bash
# One-liner installation (works on Linux, macOS, Windows)
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/scripts/install.sh | bash

# Or download and run manually:
wget https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/scripts/install.sh
bash scripts/install.sh

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
# Install via pip from GitHub (latest development version)
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git

# Or from PyPI (when published)
pip install magic-cli

# Or build and install from local source
python -m build
pip install dist/magic_cli-*.whl
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
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/scripts/uninstall.sh | bash

# Or download and run manually:
wget https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/scripts/uninstall.sh
bash scripts/uninstall.sh
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
pip uninstall magic-cli

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

## Environment Setup

### API Keys Configuration

For AI-powered features (like auto-generated commit messages), you'll need to configure API keys:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

3. Get your Groq API key from [https://console.groq.com/](https://console.groq.com/)

**Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

For detailed setup instructions, see [docs/GROQ_API_SETUP.md](docs/GROQ_API_SETUP.md).

## Project Structure

```
magic_cli/
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Production dependencies
├── config.yaml             # Runtime security & operational settings
├── README.md              # This file
├── src/                   # Main package
│   ├── __init__.py
│   ├── main.py            # Module entry point
│   ├── menu.py            # Main menu orchestration
│   ├── cli/               # CLI presentation layer
│   │   └── __init__.py
│   ├── core/              # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── exceptions.py  # Error handling
│   │   ├── security/      # Security utilities
│   │   ├── menu/          # Menu base classes
│   │   └── utils/         # Shared utilities
│   ├── modules/           # Feature modules
│   │   ├── __init__.py
│   │   ├── git_operations/  # Git automation
│   │   ├── web_development/ # Web dev scaffolding
│   │   └── project_management/ # Project tools
│   ├── ui/                # UI components
│   │   └── banner.py      # ASCII art banners
│   └── assets/            # Static assets
├── scripts/               # Setup and utility scripts
└── tests/                # Test suite
    ├── __init__.py
    ├── unit/
    └── integration/
```

---

## Development notes

- **Architecture**: The codebase follows a modular structure with clear separation of concerns:
  - `src/core/` - Cross-cutting concerns (config, exceptions, security, menu system)
  - `src/modules/` - Feature modules (git_operations, web_development, project_management)
  - `src/cli/` - CLI presentation layer
  - `src/ui/` - UI components and banners
- **Entry Points**: Multiple ways to run:
  - `python -m src.main` (module execution)
  - `magic` (installed script)
- **Web Development (Dev Mode)**: from the main menu, opens tools for:
  - Creating modern frontend/mobile projects (React, Next.js, Vue, Svelte, React Native, etc.).
  - Running Node-based dev servers (`npm run dev`, `npm run start`, etc.).
  - Running JS/Python tests via the "Run Tests (All Types)" option.
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
- **Package Distribution**: This tool can be distributed as a Python package with a console script entry point:
  - To build the package: `python -m build`
  - To install built package: `pip install dist/magic_cli-*.whl`
  - To upload to PyPI: `python -m twine upload dist/*` (requires PyPI account)
  - The console script "magic" is defined in `pyproject.toml` under `[project.scripts]`

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - feel free to use this in your own projects!

---

**Made for developers who love automation**