# Global Installation Guide for MagicCLI

## Overview
This guide explains how to install the MagicCLI toolkit globally on your system, similar to `npm install -g`, without needing to clone the repository. After installation, you'll be able to run the `magic` command from anywhere in your terminal.

## Entry Point Configuration
Before installing, ensure your project is properly configured to expose a command-line interface. The current configuration defines an entry point named `magic`:

### In setup.py:
```python
entry_points={
    "console_scripts": [
        "magic=cli.magic:main",  # Note: This should match your actual module structure
    ],
},
```

### In pyproject.toml:
```toml
[project.scripts]
magic = "src.main:main"  # This should match your actual module structure
```

> **Note**: There's a discrepancy between the entry points defined in setup.py and pyproject.toml. The pyproject.toml defines it as `"src.main:main"` while setup.py defines it as `"cli.magic:main"`. Based on the actual code structure, `src.main:main` appears to be correct.

## Installation Methods

### Method 1: Install Directly from GitHub (Recommended for Global Use)
Install the latest version directly from GitHub without cloning the repository:

```bash
pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git
```

For global installation (requires elevated privileges):
```bash
sudo pip install git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git  # Linux/macOS
pip install --user git+https://github.com/Drakaniia/PyDevToolkit-MagicCLI.git  # Alternative for user only
```

After installation, you can run the tool from anywhere with:
```bash
magic
```

### Method 2: Development Installation from Local Directory
If you have a local copy of the repository (cloned or downloaded):

```bash
pip install -e /path/to/your/PyDevToolkit-MagicCLI
```

This creates a "development install" where changes to your code are reflected without reinstalling.

### Method 3: From PyPI (When Available)
Once published to PyPI, the installation would be as simple as:
```bash
pip install PyDevToolkit-MagicCLI
```

## Verification
After installation, verify that the tool is accessible globally:

```bash
# Check if the magic command is recognized
which magic  # On Unix-like systems
where magic  # On Windows

# Run the magic command to open the main menu
magic
```

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

## Post-Installation Usage

After successful installation, you can access the MagicCLI from any directory:

```bash
# Access the main menu
magic

# The menu provides access to many development tools including:
# - GitHub Operations (push, pull, status, etc.)
# - Project Structure Viewer
# - Folder Navigation
# - Dev Mode (Web Development Automation)
# - Backend Development Tools
# - Dependency Management
# - Code Quality Tools
# - Testing & CI/CD Tools
# - And much more!
```

## Uninstallation
To uninstall the globally installed package:

```bash
pip uninstall PyDevToolkit-MagicCLI
```

## Notes
- This installation method bypasses the need to manually clone and set up the repository
- The tool will be available system-wide (assuming proper PATH configuration)
- Updates can be performed by reinstalling with the same command
- Consider using virtual environments for development to avoid conflicts with other packages