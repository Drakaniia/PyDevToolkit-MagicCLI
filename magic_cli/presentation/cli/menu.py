"""
Main menu implementation for Magic CLI
"""
import sys
from pathlib import Path

# Add the project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from magic_cli.presentation.cli.menu_base import Menu, MenuItem
from magic_cli.application.services import (
    GitService,
    ProjectService,
    BackendService,
    DevModeService,
    OthersService
)


class MainMenu(Menu):
    """Main menu for the Magic CLI application"""

    def __init__(self):
        # Initialize dependencies
        self._git_service = GitService()
        self._project_service = ProjectService()
        self._dev_mode_service = DevModeService()
        self._others_service = OthersService()

        super().__init__("Magic CLI - Developer Toolkit")

    def setup_items(self) -> None:
        """Setup main menu items"""
        if self.items:
            return

        # Create menu items
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Dev Mode (Web Dev Automation)", self._run_dev_mode),
            MenuItem("Others", self._run_others),
            MenuItem("Exit", self._exit_program)
        ]

    def _run_git_operations(self) -> None:
        """Run GitHub operations menu"""
        self._git_service.show_menu()

    def _show_structure(self) -> None:
        """Show project structure"""
        self._project_service.show_structure()

    def _navigate_folders(self) -> None:
        """Navigate folders"""
        self._project_service.navigate_folders()

    def _run_dev_mode(self) -> None:
        """Run Dev Mode menu"""
        self._dev_mode_service.show_menu()

    def _run_others(self) -> None:
        """Run Others menu"""
        self._others_service.show_menu()

    def _exit_program(self) -> str:
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  Thanks for using Magic CLI!")
        print("  Made for developers")
        print("="*70 + "\n")
        return "exit"