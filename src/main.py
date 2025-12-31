#!/usr/bin/env python3
"""
Main entry point for Python Automation System
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import ctypes; ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    # Ensure stdout uses UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import sys
from pathlib import Path
import subprocess

# Add src directory to path to enable imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from menu import MainMenu


def verify_installation():
    """Verify the installation status and display system information"""
    print("\n" + "=" * 70)
    print("  Magic CLI - Installation Verification")
    print("=" * 70 + "\n")

    all_good = True

    # Check Python version
    print("Python Environment:")
    print(f"  • Python Version: {sys.version.split()[0]}")
    print(f"  • Python Path: {sys.executable}")
    if sys.version_info < (3, 8):
        print("  ⚠  Warning: Python 3.8+ is recommended")
        all_good = False
    else:
        print("  ✓ Python version meets requirements")

    # Check package installation
    print("\nPackage Installation:")
    try:
        import importlib.metadata as metadata
        version = metadata.version("magic-cli")
        print(f"  • Package Name: magic-cli")
        print(f"  • Package Version: {version}")
        print("  ✓ Package installed correctly")
    except Exception:
        print("  ⚠  Warning: Could not verify package version")
        all_good = False

    # Check PATH configuration
    print("\nPATH Configuration:")
    magic_path = os.path.expanduser("~/.magic-cli/bin" if sys.platform != "win32" else os.path.join(os.path.expanduser("~"), ".magic-cli", "bin"))
    path_env = os.environ.get("PATH", "")
    if magic_path in path_env:
        print(f"  ✓ Magic CLI directory in PATH: {magic_path}")
    else:
        print(f"  ⚠  Magic CLI directory not in PATH: {magic_path}")
        print(f"  → Add to PATH: export PATH=\"{magic_path}:$PATH\"")
        all_good = False

    # Check wrapper script
    print("\nWrapper Script:")
    if sys.platform != "win32":
        wrapper = os.path.join(magic_path, "magic")
        if os.path.exists(wrapper):
            print(f"  ✓ Wrapper script exists: {wrapper}")
            if os.access(wrapper, os.X_OK):
                print("  ✓ Wrapper script is executable")
            else:
                print("  ⚠  Wrapper script is not executable")
                print(f"  → Run: chmod +x {wrapper}")
                all_good = False
        else:
            print(f"  ⚠  Wrapper script not found: {wrapper}")
            all_good = False
    else:
        wrapper_cmd = os.path.join(magic_path, "magic.cmd")
        wrapper_ps1 = os.path.join(magic_path, "magic.ps1")
        if os.path.exists(wrapper_cmd) or os.path.exists(wrapper_ps1):
            print(f"  ✓ Wrapper script exists")
        else:
            print(f"  ⚠  Wrapper script not found")
            all_good = False

    # Check dependencies
    print("\nDependencies:")
    dependencies = ["pyyaml", "colorama", "pyfiglet", "termcolor", "psutil"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ⚠  {dep} not installed")
            all_good = False

    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print("  ✓ All checks passed! Installation is correct.")
    else:
        print("  ⚠  Some issues detected. Please review the warnings above.")
    print("=" * 70 + "\n")

    return 0 if all_good else 1


def main():
    """Entry point for the automation system"""
    # Check for --verify flag
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        return verify_installation()

    # Check for --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("\nMagic CLI - Python Developer Toolkit\n")
        print("Usage:")
        print("  magic              Launch the interactive menu")
        print("  magic --verify     Verify installation status")
        print("  magic --help       Show this help message\n")
        return 0

    # Launch the main menu
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    sys.exit(main() or 0)
