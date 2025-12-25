# Global Installation Guide for PyDevToolkit-MagicCLI

## Overview
This guide explains how to install the PyDevToolkit-MagicCLI globally on your system, similar to `npm install -g`, without needing to clone the repository. After installation, you'll be able to run the `magic` command from anywhere in your terminal.

## Quick Start
```bash
# Install globally from PyPI (when available)
pip install pydevtoolkit-magiccli

# Or install directly from GitHub
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git

# Use the magic command
magic
```

## Installation Methods

## Installation Methods

### Method 1: PyPI Installation (Recommended)
Once published to PyPI, installation is as simple as:
```bash
pip install pydevtoolkit-magiccli
```

### Method 2: Direct GitHub Installation
Install the latest development version directly from GitHub:
```bash
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
```

### Method 3: Development Installation
If you have a local copy of the repository:
```bash
# Clone the repository
git clone https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
cd PyDevToolkit-MagicCLI

# Install in development mode
pip install -e .
```

## System Requirements
- Python 3.8 or higher
- pip package manager
- Git (for GitHub installation method)

## Verification
After installation, verify that the tool is accessible globally:

```bash
# Check if the magic command is recognized
which magic  # On Unix-like systems
where magic  # On Windows

# Run the magic command to open the main menu
magic
```

## What You Get
After installation, the `magic` command provides access to a comprehensive developer toolkit including:

- **Git Operations**: Push, pull, status, branching, and GitHub integration
- **Project Structure Viewer**: Visualize and navigate project directories
- **Folder Navigation**: Interactive file system browser
- **Dev Mode**: Web development automation tools
- **Backend Development**: API, database, and framework tools
- **Dependency Management**: Package installation and management
- **Code Quality**: Linting, formatting, and analysis tools
- **Testing & CI/CD**: Testing frameworks and pipeline tools
- **Security Tools**: Code security scanning and validation
- **And much more!**

## Troubleshooting

### Permission Issues
If you encounter permission errors during installation:

1. **Use user flag**:
   ```bash
   pip install --user git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
   ```
   
2. **Use virtual environment**:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
   ```

### Command Not Found
If the `magic` command is not found after installation:

1. **Check your PATH**: Ensure pip's script directory is in your system PATH
   - On Unix: Usually `~/.local/bin` (when using `--user`)
   - On Windows: Usually `%APPDATA%\Python\PythonXX\Scripts` (when using `--user`)

2. **Manually add to PATH** (temporary fix):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"  # Add to your shell profile for permanence
   ```

### Module Import Errors
If you encounter import errors after installation:

1. **Verify installation location**:
   ```bash
   pip show PyDevToolkit-MagicCLI
   ```

2. **Reinstall with verbose output**:
   ```bash
   pip install -v git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
   ```

### Windows-Specific Issues
When installing on Windows:

1. **Use PowerShell as Administrator** if encountering permission issues
2. **Ensure Python and pip are properly added to PATH**
3. **Use Git Bash for installation** if using the command-line installation method

## Publishing to PyPI
The package is configured for PyPI publishing with the following setup:

### Package Configuration
- **Name**: `pydevtoolkit-magiccli`
- **Entry Point**: `magic = src.main:main`
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Dependencies**: Core dependencies only (optional extras available)

### Build and Publish
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

## Post-Installation Usage

After successful installation, you can access the toolkit from any directory:

```bash
# Launch the interactive menu
magic
```

The menu provides organized access to all development tools and features.

## Uninstallation
To uninstall the globally installed package:

```bash
pip uninstall pydevtoolkit-magiccli
```

## Notes
- This installation method bypasses the need to manually clone and set up the repository
- The tool will be available system-wide (assuming proper PATH configuration)
- Updates can be performed by reinstalling with the same command
- Consider using virtual environments for development to avoid conflicts with other packages