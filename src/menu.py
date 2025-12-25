"""
automation/menu.py
Responsive Menu System with Adaptive Viewport Handling
Refactored: Split into modular components for better maintainability
"""
import sys
from pathlib import Path

# Ensure the src directory is in the Python path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.menu import Menu, MenuItem
from typing import Any, Optional
from modules.others_menu import OthersMenu
class MainMenu(Menu):
    """Main menu for the automation system - Updated with Dev Mode"""

    def __init__(self):
        # Initialize dependencies ONCE before calling parent __init__
        self._git_menu = None
        self._structure_viewer = None
        self._folder_nav = None
        self._dev_mode_menu = None
        self._others_menu = None

        # Use different title based on system to avoid Unicode encoding issues
        import sys
        if sys.platform == "win32":
            title = "Python Automation System - Main Menu"
        else:
            title = "Python Automation System - Main Menu"
        super().__init__(title)

    def setup_items(self) -> None:
        """Setup main menu items - called only once during initialization"""
        # Only create items if not already initialized
        if self.items:
            return

        # Import here to avoid circular imports
        from modules.git_operations import GitMenu
        from modules.project_management import StructureViewer, FolderNavigator
        from modules.web_development import DevModeMenu

        # Create instances once and reuse them
        if self._git_menu is None:
            self._git_menu = GitMenu()
        if self._structure_viewer is None:
            self._structure_viewer = StructureViewer()
        if self._folder_nav is None:
            self._folder_nav = FolderNavigator()
        if self._dev_mode_menu is None:
            self._dev_mode_menu = DevModeMenu()
        if self._others_menu is None:
            self._others_menu = OthersMenu()

        # Create menu items with bound methods
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Dev Mode (Web Dev Automation)", self._run_dev_mode),
            MenuItem("Others", self._run_others),
            MenuItem("Exit", self._exit_program)
        ]

    def _run_git_operations(self) -> Optional[str]:
        """Run GitHub operations menu"""
        self._git_menu.run()
        return None

    def _show_structure(self) -> Optional[str]:
        """Show project structure"""
        self._structure_viewer.show_structure()
        return None

    def _navigate_folders(self) -> Optional[str]:
        """Navigate folders"""
        self._folder_nav.navigate()
        return None

    def _run_dev_mode(self) -> Optional[str]:
        """Run Dev Mode menu"""
        self._dev_mode_menu.run()
        return None

    def _run_others(self) -> Optional[str]:
        """Run Others menu"""
        self._others_menu.run()
        return None

    def _exit_program(self) -> str:
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  Thanks for using Python Automation System!")
        print("  Made for developers")
        print("="*70 + "\n")
        return "exit"