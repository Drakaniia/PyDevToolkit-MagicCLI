"""
Backend Development Menu System
Comprehensive backend development automation tools
"""
import os
import sys
from pathlib import Path

from menu import Menu, MenuItem


class BackendDevMenu(Menu):
    """Backend Development Menu with comprehensive automation options"""

    def __init__(self):
        # Initialize dependencies
        self._db_manager = None
        self._api_generator = None
        self._auth_manager = None
        self._framework_tools = None
        
        super().__init__("🔧 Backend Development Automation")

    def setup_items(self):
        """Setup backend development menu items"""
        if self.items:
            return

        # Import backend modules using package-qualified paths
        from backend.database.db_manager import DatabaseManager
        from backend.api.api_generator import APIGenerator
        from backend.auth.auth_manager import AuthManager
        from backend.framework.framework_tools import FrameworkTools

        # Create instances
        if self._db_manager is None:
            self._db_manager = DatabaseManager()
        if self._api_generator is None:
            self._api_generator = APIGenerator()
        if self._auth_manager is None:
            self._auth_manager = AuthManager()
        if self._framework_tools is None:
            self._framework_tools = FrameworkTools()

        # Create menu items
        self.items = [
            MenuItem("🗄️  Database Management", self._run_database_manager),
            MenuItem("🚀 API Development Tools", self._run_api_generator),
            MenuItem("🔐 Authentication & Security", self._run_auth_manager),
            MenuItem("⚙️  Backend Framework Tools", self._run_framework_tools),
            MenuItem("🔙 Back to Main Menu", self._back_to_main)
        ]

    def _run_database_manager(self):
        """Run database management tools"""
        self._db_manager.run()
        return None

    def _run_api_generator(self):
        """Run API development tools"""
        self._api_generator.run()
        return None

    def _run_auth_manager(self):
        """Run authentication & security tools"""
        self._auth_manager.run()
        return None

    def _run_framework_tools(self):
        """Run backend framework tools"""
        self._framework_tools.run()
        return None

    

    def _back_to_main(self):
        """Return to main menu"""
        return "exit"