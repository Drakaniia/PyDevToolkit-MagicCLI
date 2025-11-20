"""
automation/menu.py
Responsive Menu System with Adaptive Viewport Handling
Refactored: Split into modular components for better maintainability
"""
from core.menu_base import Menu, MenuItem


class MainMenu(Menu):
    """Main menu for the automation system - Updated with Dev Mode"""

    def __init__(self):
        # Initialize dependencies ONCE before calling parent __init__
        self._git_menu = None
        self._structure_viewer = None
        self._folder_nav = None
        self._dev_mode_menu = None
        self._backend_dev_menu = None

        # Use different title based on system to avoid Unicode encoding issues
        import sys
        if sys.platform == "win32":
            title = "Python Automation System - Main Menu"
        else:
            title = "🚀 Python Automation System - Main Menu"
        super().__init__(title)

    def setup_items(self):
        """Setup main menu items - called only once during initialization"""
        # Only create items if not already initialized
        if self.items:
            return

        # Import here to avoid circular imports
        from git_operations import GitMenu
        from structure_viewer import StructureViewer
        from folder_navigator import FolderNavigator
        from dev_mode import DevModeMenu
        from backend.backend_menu import BackendDevMenu

        # Create instances once and reuse them
        if self._git_menu is None:
            self._git_menu = GitMenu()
        if self._structure_viewer is None:
            self._structure_viewer = StructureViewer()
        if self._folder_nav is None:
            self._folder_nav = FolderNavigator()
        if self._dev_mode_menu is None:
            self._dev_mode_menu = DevModeMenu()
        if self._backend_dev_menu is None:
            self._backend_dev_menu = BackendDevMenu()

        # Create menu items with bound methods
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Dev Mode (Web Dev Automation)", self._run_dev_mode),
            MenuItem("Backend Dev (Backend Automation)", self._run_backend_dev),
            MenuItem("Exit", self._exit_program)
        ]
    
    def _run_git_operations(self):
        """Run GitHub operations menu"""
        self._git_menu.run()
        return None
    
    def _show_structure(self):
        """Show project structure"""
        self._structure_viewer.show_structure()
        return None
    
    def _navigate_folders(self):
        """Navigate folders"""
        self._folder_nav.navigate()
        return None
    
    def _run_dev_mode(self):
        """Run Dev Mode menu"""
        self._dev_mode_menu.run()
        return None
    
    def _run_backend_dev(self):
        """Run Backend Dev menu"""
        self._backend_dev_menu.run()
        return None
    
    def _exit_program(self):
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  👋 Thanks for using Python Automation System!")
        print("  Made with ❤️  for developers")
        print("="*70 + "\n")
        return "exit"