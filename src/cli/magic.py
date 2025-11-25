#!/usr/bin/env python3
"""
CLI entry point for the magic command
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path so imports work properly
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from menu import MainMenu


def main():
    """Entry point for the magic command"""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()