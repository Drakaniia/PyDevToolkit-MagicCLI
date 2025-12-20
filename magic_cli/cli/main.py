"""
Magic CLI Main Entry Point
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    # Ensure stdout uses UTF-8 encoding
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from magic_cli.presentation.cli.menu import MainMenu


def main():
    """Entry point for the magic command"""
    try:
        menu = MainMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()