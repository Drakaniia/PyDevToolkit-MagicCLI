# Magic CLI - Project Context

## Project Overview

**Magic CLI** is a Python-based developer automation toolkit that provides an interactive CLI menu system for common development tasks. It streamlines Git operations, project management, web/backend development scaffolding, and DevOps automation.

### Key Features
- **Interactive Menu System**: Navigate via arrow keys or numbered selection
- **Git Operations**: Auto-commit, push/pull, changelog generation, submodule management
- **Web Development**: Scaffold React, Next.js, Vue, Svelte, React Native projects; run dev servers
- **Project Management**: Visualize project structure, navigate folders
- **Security**: Input sanitization, blocked dangerous commands, rate limiting
- **Cross-Platform**: Works on Linux, macOS, and Windows

### Architecture

The project follows a modular structure with separation of concerns:

```
src/
├── main.py              # Entry point (verify, help, launch menu)
├── menu.py              # Main menu orchestration
├── cli/                 # CLI presentation layer
├── core/                # Cross-cutting concerns
│   ├── command_handler.py
│   ├── loading.py
│   ├── menu/            # Menu base classes
│   ├── security/        # Security utilities
│   └── utils/           # Shared utilities
├── modules/             # Feature modules
│   ├── git_operations/
│   ├── web_development/
│   └── project_management/
├── ui/                  # UI components
│   └── banner.py        # ASCII art banners
└── assets/              # Static assets
```

## Building & Running

### Installation

```bash
# Development installation (editable)
pip install -e .

# Or via Makefile
make install

# Install with dev dependencies
make install-dev
```

### Running

```bash
# Via installed command
magic

# Via module
python -m src.main

# Via Makefile
make run

# Verify installation
magic --verify
```

### Testing

```bash
# All tests
make test
# or
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Specific test file
python tests/test_security.py
```

### Code Quality

```bash
# Format code
make format

# Run all checks (lint, format, test)
make check-all

# Lint only
make lint

# Security audit
make audit
```

### Building & Publishing

```bash
# Clean build artifacts
make clean

# Build distribution
make build

# Upload to PyPI
make upload

# Upload to Test PyPI
make upload-test
```

## Development Conventions

### Code Style
- **Formatter**: Black (line-length: 88) + isort
- **Linting**: flake8, mypy (strict mode)
- **Python Version**: 3.8+

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Descriptive and clear
- Reference issues when applicable: `#123`
- Automated formatting available via scripts

### Testing Practices
- Tests located in `tests/unit/` and `tests/integration/`
- Use pytest fixtures from `tests/conftest.py` and `tests/fixtures/`
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Bug fixes should include tests (enforced in PR checks)

### Project Structure Conventions
- **Modules**: Each feature domain lives in `src/modules/<domain>/`
- **Security**: All user input sanitized; dangerous commands blocked via `config.yaml`
- **Configuration**: Read from `config.yaml` (security settings, operational flags)
- **UI**: Consistent banner styling via `src/ui/banner.py`

### Key Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, tool configs (black, isort, mypy, pytest) |
| `config.yaml` | Runtime security & operational settings |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development dependencies |
| `Makefile` | Common development commands |

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/install.sh` | Global installation (auto-installs Python if needed) |
| `scripts/uninstall.sh` | Clean uninstall |
| `scripts/setup.sh` | Development setup |
| `scripts/bump_version.py` | Version management |

## Key Dependencies

### Runtime
- `pyyaml` - Configuration parsing
- `colorama`, `termcolor` - Colored terminal output
- `pyfiglet` - ASCII art banners
- `psutil` - System monitoring
- `python-dotenv` - Environment variable management

### Development
- `pytest`, `pytest-cov`, `pytest-mock` - Testing
- `black`, `isort` - Formatting
- `flake8`, `mypy` - Linting & type checking
- `bandit`, `safety` - Security auditing

## Common Tasks

### Adding a New Feature Module
1. Create directory under `src/modules/<feature_name>/`
2. Implement module logic following existing patterns
3. Register in main menu (see `src/menu.py`)
4. Add tests under `tests/unit/` or `tests/integration/`
5. Update documentation if needed

### Modifying Security Settings
Edit `config.yaml`:
- `security.blocked_commands` - Add dangerous commands to block
- `security.allowed_file_extensions` - Whitelist file types
- `security.max_command_length` - Rate limiting thresholds

### Updating Version
```bash
make bump-major   # 1.0.0 -> 2.0.0
make bump-minor   # 1.0.0 -> 1.1.0
make bump-patch   # 1.0.0 -> 1.0.1

# Or release targets (bump + commit + tag + push)
make release-major
make release-minor
make release-patch
```

## Troubleshooting

### Windows-Specific
- Console UTF-8 encoding handled automatically in `src/main.py`
- Wrapper scripts: `.cmd` and `.ps1` provided alongside `.sh`

### Import Issues
- Entry point adds `src/` to `sys.path` for module imports
- Use `from menu import MainMenu` not `from src.menu import MainMenu`

### Permission Errors
- Global install: `scripts/install.sh` handles permissions
- Manual fix: `chmod +x ~/.magic-cli/bin/magic`

## Related Documentation

- `README.md` - User-facing documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history (auto-generated)
- `docs/` - Additional documentation (if present)
