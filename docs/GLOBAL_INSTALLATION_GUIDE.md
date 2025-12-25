# Global Installation Guide for PyDevToolkit-MagicCLI

## Overview
This guide explains how to install the PyDevToolkit-MagicCLI globally on your system using our automated bash installer. **No Python or pip required** - the installer handles everything automatically! After installation, you'll be able to run the `magic` command from anywhere in your terminal.

## Quick Start (Recommended)
```bash
# Download and run the installer (works on any system)
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh | bash

# Or if you have the repository:
bash install.sh

# Use the magic command
magic
```

## What the Installer Does
The installer automatically:
- ✅ Detects your operating system (Linux, macOS, Windows)
- ✅ Installs Python 3.8+ if not present
- ✅ Installs pip if needed
- ✅ Downloads and installs PyDevToolkit-MagicCLI
- ✅ Sets up the global `magic` command
- ✅ Configures your shell environment

## Installation Methods

### Method 1: Automated Installer (Recommended - No Python Required)
The easiest way - just run our installer:
```bash
# One-liner installation (works on any system)
curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh | bash

# Or download and run manually:
wget https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh
bash install.sh
```

**What this does:**
- Automatically installs Python if not present
- Installs the package and sets up the `magic` command
- Works on Linux, macOS, and Windows (Git Bash)

### Method 2: Manual Installation (For Advanced Users)
If you prefer manual control:
```bash
# 1. Install Python 3.8+ manually from https://python.org
# 2. Install the package
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git

# 3. Run the setup script
python -m src.main --setup
```

### Method 3: Development Installation
For contributors:
```bash
# Clone and install in development mode
git clone https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
cd PyDevToolkit-MagicCLI
pip install -e .
```

## System Requirements
- **None!** The installer handles everything automatically
- Internet connection for downloading Python (if needed)
- bash shell (Linux/macOS) or Git Bash (Windows)
- curl or wget for downloading the installer

## Verification
After installation, verify that everything works:

```bash
# Check if the magic command is recognized
which magic    # On Unix-like systems
where magic    # On Windows

# Test the command (restart terminal first if needed)
magic --help

# Run the full interface
magic
```

**Expected output:**
```
======================================================================
  Python Automation System - Main Menu
======================================================================
  Current Directory: /your/current/path
======================================================================

   1. GitHub Operations
   2. Show Project Structure
   3. Navigate Folders
   ...
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

### Installation Fails
If the automated installer fails:

1. **Check internet connection**:
   ```bash
   curl -I https://github.com  # Should return 200 OK
   ```

2. **Manual installation fallback**:
   ```bash
   # Install Python manually from https://python.org
   # Then run:
   pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
   ```

3. **Permission issues on Linux/macOS**:
   ```bash
   # Run with sudo if needed for system Python
   sudo bash install.sh
   ```

### Command Not Found After Installation
If `magic` command is not found:

1. **Restart your terminal completely**
2. **Check if PATH was updated**:
   ```bash
   echo $PATH | grep pydevtoolkit
   cat ~/.bashrc | grep pydevtoolkit  # or ~/.zshrc
   ```

3. **Manual PATH setup**:
   ```bash
   export PATH="$HOME/.pydevtoolkit-magiccli/bin:$PATH"
   magic  # Test it
   ```

### Python Installation Issues
If Python installation fails:

1. **Check system package manager**:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3 python3-pip

   # macOS with Homebrew
   brew install python3

   # CentOS/RHEL
   sudo yum install python3 python3-pip
   ```

2. **Verify Python version**:
   ```bash
   python3 --version  # Should be 3.8 or higher
   ```

### Windows-Specific Issues
When installing on Windows:

1. **Use Git Bash** instead of Command Prompt
2. **Run as Administrator** if permission issues occur
3. **Check antivirus** - it may block Python installation
4. **Manual Python install**: Download from python.org and ensure "Add to PATH"

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

### Quick Uninstall
To uninstall the globally installed package:

```bash
pip uninstall pydevtoolkit-magiccli
```

### Complete Removal
For a complete removal including configuration files:

```bash
# Uninstall the package
pip uninstall pydevtoolkit-magiccli

# Remove any cached data (optional)
pip cache purge

# Remove configuration files (if any were created)
# These are typically stored in:
# - Linux/macOS: ~/.config/pydevtoolkit-magiccli/
# - Windows: %APPDATA%\pydevtoolkit-magiccli\
rm -rf ~/.config/pydevtoolkit-magiccli/  # Linux/macOS
# or
rmdir /s %APPDATA%\pydevtoolkit-magiccli\  # Windows
```

### Troubleshooting Uninstallation

#### Permission Issues
If you encounter permission errors during uninstallation:
```bash
# Try with user flag (if installed with --user)
pip uninstall --user pydevtoolkit-magiccli

# Or use elevated privileges
sudo pip uninstall pydevtoolkit-magiccli  # Linux/macOS
# On Windows, run Command Prompt/PowerShell as Administrator
```

#### Package Not Found
If pip can't find the package:
```bash
# Check if package is installed
pip list | grep pydevtoolkit

# Check installation location
pip show pydevtoolkit-magiccli

# Force uninstall if needed
pip uninstall --yes pydevtoolkit-magiccli
```

#### Multiple Installations
If you have multiple Python versions:
```bash
# Check all pip installations
python3 -m pip uninstall pydevtoolkit-magiccli
python -m pip uninstall pydevtoolkit-magiccli
py -m pip uninstall pydevtoolkit-magiccli

# Or specify the pip executable
/path/to/python -m pip uninstall pydevtoolkit-magiccli
```

## Notes
- This installation method bypasses the need to manually clone and set up the repository
- The tool will be available system-wide (assuming proper PATH configuration)
- Updates can be performed by reinstalling with the same command
- Consider using virtual environments for development to avoid conflicts with other packages