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

# Add src directory to path to enable imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from menu import MainMenu


def main():
    """Entry point for the automation system"""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()
