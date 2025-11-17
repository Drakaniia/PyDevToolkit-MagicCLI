#!/usr/bin/env python3
"""
Main entry point for Python Automation System
"""
import sys
import os
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    # Ensure stdout uses UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add automation modules to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from menu import MainMenu


def main():
    """Entry point for the automation system"""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()