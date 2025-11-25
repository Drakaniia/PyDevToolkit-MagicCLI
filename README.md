# Magic CLI

**One command to rule them all** - A powerful, secure developer toolkit that puts Git operations, project management, and web development automation at your fingertips.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![Security](https://img.shields.io/badge/security-audited-brightgreen)

---

**Just type `magic` in your terminal and get instant access to powerful development automation.**

---

## How to Use

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
cd PyDevToolkit-MagicCLI

# 2. Run the setup script (Linux/macOS or Git Bash on Windows)
bash scripts/setup.sh

# 3. Reload your shell
source ~/.bashrc  # or ~/.zshrc

# 4. Start using it anywhere!
magic
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

  ► 1. GitHub Operations
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
PyDevToolkit-MagicCLI/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   │   ├── menu/          # Menu system
│   │   ├── security/      # Security validation
│   │   └── utils/         # Utilities
│   ├── modules/           # Feature modules
│   │   ├── git_operations/
│   │   ├── web_development/
│   │   ├── backend_development/
│   │   └── project_management/
│   ├── ui/                # UI components
│   └── cli/               # CLI entry points
├── config/                # Configuration files
├── scripts/               # Setup and utility scripts
├── tests/                 # Test files
└── bin/                   # Executable scripts
```

---

## Development notes

- The main entrypoint for the menu is `src/main.py` (executed via the `magic` alias or `bin/magic` script).
- **Project Structure**: The codebase has been reorganized with a modular architecture:
  - `src/core/` - Core functionality (menu system, security, utilities)
  - `src/modules/` - Feature modules (git_operations, web_development, backend_development, project_management)
  - `src/ui/` - User interface components (banners, etc.)
  - `src/cli/` - CLI entry points
  - `config/` - Configuration files (default, development, security)
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

**Made with ❤️ for developers who love automation**