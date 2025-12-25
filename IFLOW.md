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

# PyDevToolkit MagicCLI - iFlow Context File

## Project Overview

PyDevToolkit MagicCLI is a powerful Python developer toolkit that provides Git operations, project management, and web development automation features. This is a command-line interface (CLI) tool that offers a comprehensive development automation experience through the simple `magic` command.

### Main Technology Stack
- **Python 3.7+** - Primary programming language
- **Terminal Interface** - Colorized terminal interface based on Colorama and PyFiglet
- **Modular Architecture** - Clear module separation including core functionality, development mode, backend development, etc.
- **Security Configuration** - Security restrictions and operation control through YAML configuration files

### Core Architecture
```
src/
 core/           # Core functionality modules (menu base, configuration, security, etc.)
 dev_mode/       # Web development automation tools
 backend/        # Backend development automation tools
 github/         # Git operation tools
 menu.py         # Main menu system
```

## Build and Run

### Installation and Setup
```bash
# 1. Clone repository
git clone https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
cd PyDevToolkit-MagicCLI

# 2. Run setup script (Linux/macOS or Windows Git Bash)
bash setup.sh

# 3. Reload shell
source ~/.bashrc  # or ~/.zshrc

# 4. Start using in any directory
magic
```

### Direct Run
```bash
# Run through main.py
python main.py

# Or run through src/magic.py
python src/magic.py
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python tests/test_security.py
python tests/test_integration.py
python tests/test_error_handling.py
```

### Development Mode Installation
```bash
# Development mode installation
pip install -e .

# Or install specific dependencies
pip install -e ".[test]"     # Install test dependencies
pip install -e ".[backend]"  # Install backend development dependencies
```

## Feature Modules

### 1. Main Menu System (`src/menu.py`)
- GitHub Operations - Git operation management
- Show Project Structure - Project structure viewing
- Navigate Folders - Folder navigation
- Dev Mode (Web Dev Automation) - Web development automation
- Backend Dev (Backend Automation) - Backend development automation

### 2. Development Mode (`src/dev_mode/`)
- **Create Frontend Project** - Create modern frontend projects (React, Next.js, Vue, Svelte, etc.)
- **Run Project** - Run development servers and production builds
- **Run Tests** - Run various types of tests (JS/Python)
- **Port Killer** - Clean up port conflicts
- **Install Dependencies** - Install project dependencies
- **Setup Prettier** - Code formatting configuration
- **Docker Quick Commands** - Docker quick commands

### 3. Backend Development (`src/backend/`)
- **Database Management** - Database management and connection configuration
- **API Development Tools** - API scaffolding (FastAPI, Flask, DRF, Express.js)
- **Authentication & Security** - Authentication and user management scaffolding
- **Backend Framework Tools** - Backend framework tools

### 4. Git Operations (`src/github/`)
- Push to GitHub (Auto-commit) - Auto-commit and push
- Pull from GitHub - Pull changes
- Repository Status - Repository status viewing
- Commit Recovery - Commit recovery
- Generate Changelog - Generate changelog
- Git Submodule Manager - Git submodule management

### 5. Core Functionality (`src/core/`)
- **Menu System** - Responsive menu system with adaptive viewport handling
- **Security** - Security configuration and input validation
- **Configuration** - YAML configuration file management
- **Logging** - Logging system
- **Exception Handling** - Exception handling mechanism

## Development Conventions

### Code Style
- Use Python 3.7+ syntax features
- Follow PEP 8 code style guidelines
- Use type hints
- Modular design, avoid circular imports

### Security Configuration
The project implements security control through `config.yaml`:
- Maximum command length limit (500 characters)
- Maximum path length limit (1000 characters)
- Network access control
- Dangerous command blocklist (rm, del, format, etc.)
- Allowed file extension whitelist

### Menu System Conventions
- All menus inherit from `core.menu_base.Menu` base class
- Menu items are defined using `MenuItem` class
- Support nested menus and return functionality
- Unified error handling and user interaction

### Testing Conventions
- Use pytest framework
- Test files located in `tests/` directory
- Include security tests, integration tests, and error handling tests
- Support coverage reports

## Special Features

### Changelog Generation
- Automatic mode: Automatically updates after each successful Git push
- Manual mode: Through GitHub Operations → Generate Changelog menu
- Command line: `python src/changelog_generator.py generate [N]`

### Cross-platform Support
- Windows UTF-8 encoding handling
- Cross-platform shell command support
- Terminal display adaptation for different operating systems

### Extensibility
- Plugin-style command system (Dev Mode)
- Modular backend tools
- Configurable security policies
- Support for custom menu items

## Configuration Files

### config.yaml
Main configuration file, containing:
- Security settings (command restrictions, file extensions, etc.)
- Operation settings (log levels, debug mode, etc.)
- Network access control

### requirements.txt
Production dependency package list, containing:
- YAML processing (PyYAML)
- Terminal beautification (Colorama, PyFiglet, Termcolor)
- Web frameworks (FastAPI, Flask, Django REST Framework)
- Database connections (PostgreSQL, MySQL, MongoDB, Redis)

### setup.py
Package configuration file, defining:
- Package metadata and dependencies
- Console script entry point (`magic` command)
- Optional dependency groups (test, backend)

## Project Structure Description

```
PyDevToolkit-MagicCLI/
 main.py                 # Main entry point
 src/                    # Source code directory
    menu.py            # Main menu system
    magic.py           # magic command entry point
    core/              # Core functionality modules
    dev_mode/          # Web development automation
    backend/           # Backend development automation
    github/            # Git operation tools
 tests/                  # Test files
 config.yaml            # Main configuration file
 requirements.txt       # Production dependencies
 setup.py              # Package configuration
 setup.sh              # Installation script
```

This project provides Python developers with a one-stop command-line development environment, especially suitable for scenarios that require frequent Git operations, project management, and web/backend development.