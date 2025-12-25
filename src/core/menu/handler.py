"""
Menu Handler Module for Python Automation System

This module provides a standardized menu system with arrow key navigation
that can be used throughout the application for consistent UI/UX.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional
try:
    from ..menu import Menu, MenuItem
except ImportError:
    from .base import Menu, MenuItem


class BaseMenuHandler:
    """Base class for handling menus with consistent navigation"""

    def __init__(self, title: str):
        self.title = title

    def create_menu(self, items: List[tuple], action_map: Optional[dict] = None) -> Menu:
        """
        Create a menu with given items
        
        Args:
            items: List of tuples (display_text, action_function)
            action_map: Optional mapping of items to specific actions (for string key access)
        
        Returns:
            An initialized Menu object
        """
        class DynamicMenu(Menu):
            def __init__(self, title: str, items: List[tuple]):
                self.items_data = items
                super().__init__(title)
            
            def setup_items(self):
                for item in self.items_data:
                    if isinstance(item, tuple) and len(item) == 2:
                        display_text, action = item
                        self.items.append(MenuItem(display_text, action))
                    else:
                        # Handle string items with default action
                        self.items.append(MenuItem(str(item), lambda: None))
        
        return DynamicMenu(self.title, items)

    def run_menu(self, items: List[tuple], action_map: Optional[dict] = None) -> Any:
        """
        Run a menu with the given items
        
        Args:
            items: List of tuples (display_text, action_function)
            action_map: Optional mapping of items to specific actions
        
        Returns:
            Result of the selected action
        """
        menu = self.create_menu(items, action_map)
        menu.run()


class GitMenuHandler(BaseMenuHandler):
    """Menu handler specifically for Git operations"""

    def __init__(self, title: str = "Git Operations"):
        super().__init__(title)

    def create_git_operations_menu(self, git_instance) -> Menu:
        """Create a standardized Git operations menu"""
        class GitOperationsMenu(Menu):
            def __init__(self, git_instance):
                self.git_instance = git_instance
                super().__init__("Git Operations")
            
            def setup_items(self):
                # This is a template - actual items would depend on the git_instance
                # Common git operations
                self.items = [
                    MenuItem("Git Status", self.git_status),
                    MenuItem("Git Log", self.git_log),
                    MenuItem("Git Diff", self.git_diff),
                    MenuItem("Git Stash Operations", self.git_stash),
                    MenuItem("Git Recovery", self.git_recover),
                    MenuItem("Back", self.exit_menu)
                ]

            def git_status(self):
                # Placeholder for git status action
                print("Running git status...")
                # Replace with actual method call from git_instance
                if hasattr(self.git_instance, 'show_status'):
                    self.git_instance.show_status()

            def git_log(self):
                print("Running git log...")
                # Replace with actual method call from git_instance
                if hasattr(self.git_instance, 'show_log'):
                    self.git_instance.show_log()

            def git_diff(self):
                print("Running git diff...")
                # Replace with actual method call from git_instance
                if hasattr(self.git_instance, 'show_diff'):
                    self.git_instance.show_diff()

            def git_stash(self):
                print("Running git stash operations...")
                # Replace with actual method call from git_instance
                if hasattr(self.git_instance, 'show_stash_menu'):
                    self.git_instance.show_stash_menu()

            def git_recover(self):
                print("Running git recovery...")
                # Replace with actual method call from git_instance
                if hasattr(self.git_instance, 'show_recovery_menu'):
                    self.git_instance.show_recovery_menu()

            def exit_menu(self):
                return "exit"

        return GitOperationsMenu(git_instance)

    def create_commit_selection_menu(self, commits: List[dict], action_func: Callable) -> Menu:
        """Create a menu for selecting commits"""
        class CommitSelectionMenu(Menu):
            def __init__(self, commits: List[dict], action_func: Callable):
                self.commits = commits
                self.action_func = action_func
                # Truncate title if necessary
                title = f"Select a Commit ({len(commits)} available)"[:50]
                super().__init__(title)
            
            def setup_items(self):
                # Add commit options to the menu
                for idx, commit in enumerate(self.commits):
                    commit_id = commit.get('hash', '')[:10] if commit.get('hash') else 'Unknown'
                    timestamp = commit.get('date', '')
                    message = commit.get('message', '')[:40]
                    message = message + "..." if len(commit.get('message', '')) > 40 else message
                    display_text = f"{idx+1}. {commit_id} - {message} ({timestamp})"
                    # Bind the commit as a default argument so it's captured correctly in the lambda
                    self.items.append(MenuItem(display_text, lambda commit=commit: self.action_func(commit)))
                
                # Add a cancel option
                self.items.append(MenuItem("Cancel", lambda: None))

        return CommitSelectionMenu(commits, action_func)


class OperationSelectionHandler(BaseMenuHandler):
    """Menu handler for selecting operations"""

    def create_operation_menu(self, operations: List[tuple], title: str = "Select Operation") -> Menu:
        """
        Create a menu for selecting from a list of operations
        
        Args:
            operations: List of tuples (operation_name, operation_function)
            title: Title for the menu
        
        Returns:
            Initialized Menu object
        """
        class OperationMenu(Menu):
            def __init__(self, ops: List[tuple], title: str):
                self.operations = ops
                super().__init__(title)
            
            def setup_items(self):
                for op_name, op_func in self.operations:
                    if callable(op_func):
                        self.items.append(MenuItem(op_name, op_func))
                    else:
                        self.items.append(MenuItem(op_name, lambda: print(f"Action not implemented: {op_name}")))
                
                # Add a back/exit option
                self.items.append(MenuItem("Back", lambda: "exit"))

        return OperationMenu(operations, title)


class ConfirmationHandler:
    """Handler for confirmation dialogs"""

    @staticmethod
    def create_confirmation_menu(title: str, on_confirm: Callable, on_cancel: Optional[Callable] = None) -> Menu:
        """
        Create a simple yes/no confirmation menu
        
        Args:
            title: Confirmation message
            on_confirm: Function to call if user confirms
            on_cancel: Function to call if user cancels (defaults to exit)
        
        Returns:
            Initialized Menu object
        """
        if on_cancel is None:
            on_cancel = lambda: "exit"

        class ConfirmationMenu(Menu):
            def __init__(self, title: str, confirm_action: Callable, cancel_action: Callable):
                super().__init__(title)
                self.confirm_action = confirm_action
                self.cancel_action = cancel_action
            
            def setup_items(self):
                self.items = [
                    MenuItem("Yes", self.confirm_action),
                    MenuItem("No", self.cancel_action)
                ]

        return ConfirmationMenu(title, on_confirm, on_cancel)


class MenuHelper:
    """Helper class to provide common menu operations"""

    @staticmethod
    def run_simple_selection(items: List[str], title: str = "Select an option") -> Optional[str]:
        """
        Run a simple selection menu from a list of strings
        
        Args:
            items: List of strings to select from
            title: Title for the menu
        
        Returns:
            Selected string or None if cancelled
        """
        class SimpleSelectionMenu(Menu):
            def __init__(self, items: List[str], title: str):
                self.items_list = items
                super().__init__(title)
            
            def setup_items(self):
                for item in self.items_list:
                    self.items.append(MenuItem(item, lambda selected=item: selected))
                
                self.items.append(MenuItem("Cancel", lambda: None))

        menu = SimpleSelectionMenu(items, title)
        selection = menu.get_choice_with_arrows()

        if 1 <= selection <= len(items):  # Valid selection
            return items[selection - 1]
        else:  # Cancel or invalid selection
            return None

    @staticmethod
    def run_action_selection(actions: List[tuple], title: str = "Select an action") -> Any:
        """
        Run a menu where each item is an action to execute
        
        Args:
            actions: List of tuples (action_name, action_function)
            title: Title for the menu
        
        Returns:
            Result of the executed action
        """
        class ActionSelectionMenu(Menu):
            def __init__(self, actions: List[tuple], title: str):
                self.actions = actions
                super().__init__(title)
            
            def setup_items(self):
                for action_name, action_func in self.actions:
                    self.items.append(MenuItem(action_name, action_func))
                
                self.items.append(MenuItem("Back", lambda: "exit"))

        menu = ActionSelectionMenu(actions, title)
        menu.run()


# Example usage and testing
if __name__ == "__main__":
    # Example: Creating and running a simple menu
    def test_action():
        print("Test action executed!")
        return "Test completed"
    
    def list_files():
        print("Listing files...")
        return "Files listed"
    
    def exit_app():
        print("Exiting...")
        return "exit"
    
    # Create a menu handler
    handler = BaseMenuHandler("Test Menu")
    
    # Define menu items
    items = [
        ("Run Test Action", test_action),
        ("List Files", list_files),
        ("Exit", exit_app)
    ]
    
    # Run the menu
    print("Example usage of MenuHandler:")
    menu = handler.create_menu(items)
    menu.run()
    
    print("\nExample of Simple Selection:")
    options = ["Option 1", "Option 2", "Option 3", "Cancel"]
    selection = MenuHelper.run_simple_selection(options, "Choose an option")
    print(f"Selected: {selection}")