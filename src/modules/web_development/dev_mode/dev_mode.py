"""
automation/dev_mode/dev_mode.py
Dev Mode menu and command orchestration
FINAL VERSION: Includes all 6 commands with Run Tests as option 3
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
from core.menu import Menu, MenuItem
from ._base import DevModeCommand


class DevModeMenu(Menu):
    """Dev Mode submenu for web development automation"""
    
    def __init__(self):
        self.commands: List[DevModeCommand] = []
        super().__init__(" Dev Mode - Web Development Automation")
    
    def setup_items(self):
        """Setup menu items by loading command modules"""
# Import command modules in the order they should appear
        from .create_frontend import COMMAND as create_frontend
        from .run_project import COMMAND as run_project
        from .test_project import COMMAND as test_project
        from .port_killer_command import COMMAND as port_killer
        from .install_deps import COMMAND as install_deps
        from .format_code import COMMAND as format_code
        from .docker_quick import COMMAND as docker_quick
        
        # Store commands for access
        # ORDER MATTERS - This determines menu item numbers:
        # 1. Create Frontend Project (React / Next.js / Vue)
        # 2. Run Project (Dev / Build)
        # 3. Run Tests (All Types)
        # 4. Port Killer (Clear Conflicts) ← NEW!
        # 5. Install Dependencies (npm install)
        # 6. Setup Prettier (Format on Save)
        # 7. Docker Quick Commands
        # 8. Back to Main Menu (added automatically)
        self.commands = [
            create_frontend,
            run_project,
            test_project,
            port_killer,      # This is the new option 4
            install_deps,
            format_code,
            docker_quick
        ]
        
        # Create menu items dynamically from commands
        self.items = []
        for cmd in self.commands:
            self.items.append(
                MenuItem(cmd.label, lambda c=cmd: self._execute_command(c))
            )
        
        # Add back option
        self.items.append(MenuItem("Back to Main Menu", lambda: "exit"))
    
    def _execute_command(self, command: DevModeCommand):
        """Execute a Dev Mode command"""
        try:
            command.run(interactive=True)
        except KeyboardInterrupt:
            print("\n\n Operation cancelled by user")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"\n{'='*70}")
            print(f" ERROR: {str(e)}")
            print(f"{'='*70}\n")
            import traceback
            traceback.print_exc()
            input("Press Enter to continue...")
        
        return None  # Stay in menu


def run_dev_mode():
    """Entry point for Dev Mode"""
    menu = DevModeMenu()
    menu.run()


if __name__ == "__main__":
    run_dev_mode()