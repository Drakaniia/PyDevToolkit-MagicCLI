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
        from modules.backend_development import BackendDevMenu
        from modules.dependency_management import DependencyMenu
        from modules.code_quality import CodeQualityMenu
        from modules.testing_cicd import TestingCICDMenu
        from modules.monitoring import MonitoringMenu
        from modules.documentation import DocumentationMenu
        from modules.scaffolding import ScaffoldingMenu
        from modules.database import DatabaseMenu
        from modules.api_tools import APIMenu
        from modules.devops import DevOpsMenu
        from modules.code_analysis import CodeAnalysisMenu
        from modules.security_tools import SecurityMenu
        from modules.debugging import DebuggingMenu
        from modules.version_control import VersionControlMenu
        from modules.cross_platform import CrossPlatformMenu
        from modules.ai_ml import AIMLMenu

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
        if not hasattr(self, '_dep_menu') or self._dep_menu is None:
            self._dep_menu = DependencyMenu()
        if not hasattr(self, '_code_quality_menu') or self._code_quality_menu is None:
            self._code_quality_menu = CodeQualityMenu()
        if not hasattr(self, '_testing_cicd_menu') or self._testing_cicd_menu is None:
            self._testing_cicd_menu = TestingCICDMenu()
        if not hasattr(self, '_monitoring_menu') or self._monitoring_menu is None:
            self._monitoring_menu = MonitoringMenu()
        if not hasattr(self, '_documentation_menu') or self._documentation_menu is None:
            self._documentation_menu = DocumentationMenu()
        if not hasattr(self, '_scaffolding_menu') or self._scaffolding_menu is None:
            self._scaffolding_menu = ScaffoldingMenu()
        if not hasattr(self, '_database_menu') or self._database_menu is None:
            self._database_menu = DatabaseMenu()
        if not hasattr(self, '_api_menu') or self._api_menu is None:
            self._api_menu = APIMenu()
        if not hasattr(self, '_devops_menu') or self._devops_menu is None:
            self._devops_menu = DevOpsMenu()
        if not hasattr(self, '_code_analysis_menu') or self._code_analysis_menu is None:
            self._code_analysis_menu = CodeAnalysisMenu()
        if not hasattr(self, '_security_menu') or self._security_menu is None:
            self._security_menu = SecurityMenu()
        if not hasattr(self, '_debugging_menu') or self._debugging_menu is None:
            self._debugging_menu = DebuggingMenu()
        if not hasattr(self, '_version_control_menu') or self._version_control_menu is None:
            self._version_control_menu = VersionControlMenu()
        if not hasattr(self, '_cross_platform_menu') or self._cross_platform_menu is None:
            self._cross_platform_menu = CrossPlatformMenu()
        if not hasattr(self, '_ai_ml_menu') or self._ai_ml_menu is None:
            self._ai_ml_menu = AIMLMenu()

        # Create menu items with bound methods
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Dev Mode (Web Dev Automation)", self._run_dev_mode),
            MenuItem("Backend Dev (Backend Automation)", self._run_backend_dev),
            MenuItem("Dependency Management", self._run_dependency_management),
            MenuItem("Code Quality Tools", self._run_code_quality),
            MenuItem("Testing & CI/CD Tools", self._run_testing_cicd),
            MenuItem("Monitoring & Performance Tools", self._run_monitoring),
            MenuItem("Documentation Tools", self._run_documentation),
            MenuItem("Project Scaffolding Tools", self._run_scaffolding),
            MenuItem("Database Management Tools", self._run_database),
            MenuItem("API Development Tools", self._run_api),
            MenuItem("DevOps & Infrastructure Tools", self._run_devops),
            MenuItem("Code Analysis Tools", self._run_code_analysis),
            MenuItem("Security & Compliance Tools", self._run_security),
            MenuItem("Debugging Tools", self._run_debugging),
            MenuItem("Advanced Version Control Tools", self._run_version_control),
            MenuItem("Cross-Platform Development Tools", self._run_cross_platform),
            MenuItem("AI & Machine Learning Tools", self._run_ai_ml),
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

    def _run_backend_dev(self) -> Optional[str]:
        """Run Backend Dev menu"""
        self._backend_dev_menu.run()
        return None

    def _run_dependency_management(self) -> Optional[str]:
        """Run Dependency Management menu"""
        self._dep_menu.run()
        return None

    def _run_code_quality(self) -> Optional[str]:
        """Run Code Quality Tools menu"""
        self._code_quality_menu.run()
        return None

    def _run_testing_cicd(self) -> Optional[str]:
        """Run Testing & CI/CD Tools menu"""
        self._testing_cicd_menu.run()
        return None

    def _run_monitoring(self) -> Optional[str]:
        """Run Monitoring & Performance Tools menu"""
        self._monitoring_menu.run()
        return None

    def _run_documentation(self) -> Optional[str]:
        """Run Documentation Tools menu"""
        self._documentation_menu.run()
        return None

    def _run_scaffolding(self) -> Optional[str]:
        """Run Project Scaffolding Tools menu"""
        self._scaffolding_menu.run()
        return None

    def _run_database(self) -> Optional[str]:
        """Run Database Management Tools menu"""
        self._database_menu.run()
        return None

    def _run_api(self) -> Optional[str]:
        """Run API Development Tools menu"""
        self._api_menu.run()
        return None

    def _run_devops(self) -> Optional[str]:
        """Run DevOps & Infrastructure Tools menu"""
        self._devops_menu.run()
        return None

    def _run_code_analysis(self) -> Optional[str]:
        """Run Code Analysis Tools menu"""
        self._code_analysis_menu.run()
        return None

    def _run_security(self) -> Optional[str]:
        """Run Security & Compliance Tools menu"""
        self._security_menu.run()
        return None

    def _run_debugging(self) -> Optional[str]:
        """Run Debugging Tools menu"""
        self._debugging_menu.run()
        return None

    def _run_version_control(self) -> Optional[str]:
        """Run Advanced Version Control Tools menu"""
        self._version_control_menu.run()
        return None

    def _run_cross_platform(self) -> Optional[str]:
        """Run Cross-Platform Development Tools menu"""
        self._cross_platform_menu.run()
        return None

    def _run_ai_ml(self) -> Optional[str]:
        """Run AI & Machine Learning Tools menu"""
        self._ai_ml_menu.run()
        return None

    def _exit_program(self) -> str:
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  Thanks for using Python Automation System!")
        print("  Made for developers")
        print("="*70 + "\n")
        return "exit"