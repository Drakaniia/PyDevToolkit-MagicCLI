# Magic CLI

A powerful, secure developer toolkit built with clean architecture principles. This package provides a comprehensive CLI interface for development automation, Git operations, project management, and backend development tools.

## 🏗️ Architecture

Built with Domain-Driven Design (DDD) principles and Clean Architecture:

```
magic_cli/
├── cli/               # CLI entry points and commands
├── core/              # Cross-cutting concerns
│   ├── config.py      # Configuration management
│   ├── exceptions.py  # Error handling and custom exceptions
│   └── security.py    # Security utilities and validation
├── domain/            # Business logic and domain models
│   ├── git/          # Git operations domain
│   ├── project/      # Project management domain
│   └── backend/      # Backend development domain
├── application/       # Application services and use cases
│   ├── services/     # Application services layer
│   └── use_cases/    # Use case orchestrators
├── infrastructure/    # External dependencies and adapters
│   ├── git_client.py # Git operations client
│   └── file_system.py # File system operations
├── presentation/      # Presentation layer
│   └── cli/          # CLI interface components
│       ├── menu.py        # Main menu implementation
│       ├── menu_base.py   # Base menu classes
│       ├── renderer.py    # Menu rendering and display
│       └── navigation.py  # Input handling and navigation
└── plugins/          # Plugin system for extensibility
```

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev,test]"
```

### Usage

```bash
# Run as module
python -m magic_cli

# Or use the installed command
magic
```

## 📦 Package Components

### Core Layer

**Configuration Management (`core/config.py`)**
- Centralized configuration for security settings and operational parameters
- YAML/JSON configuration file support
- Environment-specific configurations

**Error Handling (`core/exceptions.py`)**
- Comprehensive exception hierarchy
- Custom automation errors with helpful suggestions
- Centralized error handling and logging

### Domain Layer

**Git Domain (`domain/git/`)**
- Git operations business logic
- Repository state management
- Commit and branch operations

**Project Domain (`domain/project/`)**
- Project structure analysis
- File system operations
- Project navigation utilities

**Backend Domain (`domain/backend/`)**
- Backend development tools
- API generation logic
- Database operations

### Application Layer

**Services (`application/services/`)**
- Application services that orchestrate domain objects
- Use case implementations
- Business workflow coordination

### Infrastructure Layer

**Git Client (`infrastructure/git_client.py`)**
- Git command execution
- Repository state detection
- External Git API integrations

**File System (`infrastructure/file_system.py`)**
- File and directory operations
- Path management utilities
- Cross-platform file system handling

### Presentation Layer

**CLI Interface (`presentation/cli/`)**
- Interactive menu system
- Terminal rendering and navigation
- User input handling

## 🔧 Configuration

The package uses a hierarchical configuration system:

1. **Default Configuration**: Built-in sensible defaults
2. **User Configuration**: `~/.magiccli/config.yaml` or `~/.magiccli/config.json`
3. **Project Configuration**: `./config.yaml` or `./config.json`

### Security Configuration

```yaml
security:
  max_command_length: 500
  max_path_length: 1000
  allow_network_access: true
  enable_rate_limiting: true
  enable_input_sanitization: true
  blocked_commands: ['rm', 'rmdir', 'del', 'format']
  allowed_file_extensions: ['.py', '.js', '.ts', '.md', '.txt']
```

### Operational Configuration

```yaml
operational:
  log_level: INFO
  log_file: null
  enable_debug: false
  max_log_size: 10485760  # 10MB
  enable_color_output: true
  enable_loading_animations: true
```

## 🛠️ Development

### Project Structure

- **`cli/`**: Command-line interface entry points
- **`core/`**: Shared utilities and cross-cutting concerns
- **`domain/`**: Business domain logic and entities
- **`application/`**: Application-specific logic and services
- **`infrastructure/`**: External service integrations
- **`presentation/`**: User interface and presentation logic

### Code Quality

The package maintains high code quality standards:

- **Type Hints**: Full type annotation coverage
- **Testing**: Comprehensive test suite with pytest
- **Linting**: Black formatting, isort imports, flake8 linting
- **Documentation**: Comprehensive docstrings and API documentation

### Testing

```bash
# Run all tests
python -m pytest tests/ -v --cov=magic_cli

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage report
python -m pytest tests/ --cov=magic_cli --cov-report=html
```

## 🔌 Plugin System

The package includes a plugin architecture for extensibility:

```python
from magic_cli.plugins.registry import PluginRegistry

# Register custom plugins
registry = PluginRegistry()
registry.register_plugin('my_plugin', MyCustomPlugin())
```

## 📚 API Reference

### Main Entry Points

- `magic_cli.cli.main:main()` - CLI entry point
- `magic_cli.presentation.cli.menu.MainMenu` - Main menu class
- `magic_cli.core.config.get_config_manager()` - Configuration access

### Key Classes

- `Menu` - Base menu class with navigation
- `MenuRenderer` - Terminal display management
- `MenuNavigation` - Input handling and navigation
- `ConfigManager` - Configuration management
- `AutomationError` - Base exception class

## 🤝 Contributing

1. Follow the established architecture patterns
2. Maintain separation of concerns
3. Add comprehensive tests for new features
4. Update documentation for API changes
5. Follow the commit message conventions

## 📄 License

MIT License - see project root LICENSE file for details.

## 🙏 Acknowledgments

Built with clean architecture principles to provide a maintainable, scalable, and extensible developer toolkit.