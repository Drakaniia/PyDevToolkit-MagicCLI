# Project Context

## Purpose
Magic CLI (PyDevToolkit-MagicCLI) is a powerful, secure developer toolkit that provides comprehensive automation for Git operations, project management, and web development. It offers a unified command-line interface to simplify development workflows and improve productivity, with features including GitHub operations, changelog generation, dev mode for web development, and backend development tools.

## Tech Stack
- **Python 3.7+** - Primary programming language
- **Terminal UI** - Menu-driven interface using arrow-key navigation
- **FastAPI** - Modern, fast web framework for backend development
- **Flask** - Web framework for building web applications
- **SQLAlchemy** - SQL toolkit and ORM for database operations
- **Pydantic** - Data validation and settings management
- **PyYAML** - YAML processing for configuration files
- **Colorama** - Cross-platform colored terminal text
- **PyFiglet** - ASCII art text generation
- **Termcolor** - Colored terminal output
- **pytest** - Testing framework
- **Black** - Code formatter
- **Flake8** - Code linter
- **MyPy** - Static type checker

## Project Conventions

### Code Style
- Follow PEP 8 Python style guidelines
- Use Black for consistent code formatting (88 character line length)
- Use Isort for import ordering
- Use MyPy for type checking with strict settings
- Use descriptive variable and function names
- Include docstrings for all public functions and classes
- Use snake_case for function and variable names
- Use PascalCase for class names
- File names should be descriptive and in snake_case
- Include emojis in user-facing output to enhance the experience

### Architecture Patterns
- Modular architecture organized by functionality (core, modules, ui, cli)
- Separation of concerns with dedicated directories for specific responsibilities
- Menu-driven architecture for user interaction
- Security-first design with input sanitization and rate limiting
- Configuration-driven behavior through YAML files
- Plugin-style modules for different operational areas (git, web dev, backend)
- Centralized error handling and logging

### Testing Strategy
- Unit tests using pytest for individual components
- Integration tests for cross-component functionality
- Test coverage measurement using pytest-cov
- Security tests using bandit for static analysis
- Dependency vulnerability scanning with safety
- Continuous integration with automated testing on all platforms
- Test organization follows the pattern: tests/unit/ and tests/integration/

### Git Workflow
- Feature branch workflow (git checkout -b feature/amazing-feature)
- Descriptive commit messages in present tense
- Include issue references when applicable (#123)
- Comprehensive changelog maintained automatically and manually
- Branch-based development with pull requests for code review
- Commit messages follow conventional style with automated formatting
- Regular updates to main branch after review and approval

## Domain Context
Magic CLI serves as a comprehensive automation platform for developers, integrating Git operations, project management, and development environment setup into a single, easy-to-use interface. The system includes security measures to protect against harmful commands and validates file access to prevent unauthorized operations. The project places emphasis on user experience with colored output, loading animations, and intuitive navigation.

## Important Constraints
- Support for Python 3.7+ only
- Cross-platform compatibility (Linux, macOS, Windows)
- Security restrictions on certain commands (rm, rmdir, del, etc.)
- Maximum command length limited to 500 characters
- Maximum path length limited to 1000 characters
- Subprocess timeout limited to 30 seconds
- Limited file extension whitelist for safe operations
- Network access can be disabled via configuration

## External Dependencies
- Git for version control operations
- Various web development frameworks: React, Next.js, Vue, Svelte, etc.
- Backend frameworks: FastAPI, Flask, Django REST Framework
- Database systems: PostgreSQL, MySQL, MongoDB, Redis
- Node.js and npm for frontend project creation
- Shell access for executing system commands
- GitHub/GitLab for Git remote operations
