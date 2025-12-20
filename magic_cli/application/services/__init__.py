"""
Application services - Simplified stubs that delegate to existing functionality
"""
import sys
from pathlib import Path

# Add the old src directory to path for importing existing functionality
old_src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(old_src_path) not in sys.path:
    sys.path.insert(0, str(old_src_path))


class GitService:
    """Git operations service"""

    def __init__(self):
        # Import existing GitMenu
        from modules.git_operations import GitMenu
        self._menu = GitMenu()

    def show_menu(self):
        """Show git operations menu"""
        self._menu.run()


class ProjectService:
    """Project management service"""

    def __init__(self):
        # Import existing services
        from modules.project_management import StructureViewer, FolderNavigator
        self._structure_viewer = StructureViewer()
        self._folder_navigator = FolderNavigator()

    def show_structure(self):
        """Show project structure"""
        self._structure_viewer.show_structure()

    def navigate_folders(self):
        """Navigate folders"""
        self._folder_navigator.navigate()


class DevModeService:
    """Dev mode service"""

    def __init__(self):
        # Import existing DevModeMenu
        from modules.web_development import DevModeMenu
        self._menu = DevModeMenu()

    def show_menu(self):
        """Show dev mode menu"""
        self._menu.run()


class OthersService:
    """Others menu service"""

    def __init__(self):
        # Import the OthersMenu we created earlier
        from modules.others_menu import OthersMenu
        self._menu = OthersMenu()

    def show_menu(self):
        """Show others menu"""
        self._menu.run()


# For now, BackendService is not implemented - would need to be added
class BackendService:
    """Backend development service - placeholder"""

    def show_menu(self):
        """Show backend development menu"""
        print("Backend development menu not yet implemented in new architecture")
        input("Press Enter to continue...")