"""
Comprehensive Git Stash Operations Module
Provides an interactive interface for all git stash commands with arrow key navigation.
"""
import os
import subprocess
from typing import List, Optional
from colorama import init, Fore, Style

# Import the menu system from the core module
from core.menu import Menu, MenuItem

init(autoreset=True)

class GitStash:
    """Git stash operations handler class"""

    def __init__(self):
        pass

    def run_command(self, cmd: str, cwd: str = None) -> tuple:
        """Run a shell command and return (stdout, stderr, return_code)"""
        try:
            if isinstance(cmd, str):
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, cwd=cwd
                )
            else:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=cwd
                )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1

    def get_stash_list(self) -> List[str]:
        """Get the list of stashes"""
        stdout, stderr, code = self.run_command(["git", "stash", "list"])
        if code == 0:
            return stdout.strip().split('\n') if stdout.strip() else []
        return []

    def display_stash_menu(self, stashes: List[str]) -> Optional[str]:
        """Display interactive stash menu using the main menu system"""
        if not stashes:
            print(Fore.YELLOW + "No stashes found.")
            input("\nPress Enter to continue...")
            return None

        # Create a menu for stashes
        class StashMenu(Menu):
            def __init__(self, stashes):
                self.stashes = stashes
                super().__init__("Git Stash List - Select a Stash")

            def setup_items(self):
                for i, stash in enumerate(self.stashes):
                    self.items.append(MenuItem(f"{stash}", lambda stash_idx=i: stash_idx))

                # Add a cancel option
                self.items.append(MenuItem("Cancel", lambda: -1))

        stash_menu = StashMenu(stashes)
        selected_idx = stash_menu.get_choice_with_arrows() - 1  # Adjust for 0-based indexing

        # The last item is the cancel option
        if selected_idx == len(stashes):
            return None
        elif 0 <= selected_idx < len(stashes):
            return self.stashes[selected_idx].split(':')[0]  # Return stash name
        else:
            return None

    def execute_stash_operations(self):
        """Main function to handle git stash operations using the menu system"""

        class GitStashMenu(Menu):
            def __init__(self, git_stash_instance):
                self.git_stash = git_stash_instance
                super().__init__("Git Stash Operations")

            def setup_items(self):
                self.items = [
                    MenuItem("git stash - Save current state", self._stash_save),
                    MenuItem("git stash list - Show saved stashes", self._stash_list),
                    MenuItem("git stash apply - Apply a stash", self._stash_apply),
                    MenuItem("git stash pop - Apply and remove a stash", self._stash_pop),
                    MenuItem("git stash drop - Remove a specific stash", self._stash_drop),
                    MenuItem("git stash clear - Remove all stashes", self._stash_clear),
                    MenuItem("View stash details", self._stash_details),
                    MenuItem("Back to main menu", self._exit_menu)
                ]

            def _stash_save(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Save")
                print(Fore.CYAN + "="*50)

                message = input("Enter optional stash message (or press Enter to skip): ").strip()
                if message:
                    cmd = f'git stash push -m "{message}"'
                else:
                    cmd = 'git stash'

                print(Fore.CYAN + f"Running: {cmd}")
                stdout, stderr, code = self.git_stash.run_command(cmd)
                if code == 0:
                    print(Fore.GREEN + "Stash saved successfully!")
                    if stdout:
                        print(Fore.WHITE + stdout)
                else:
                    print(Fore.RED + f"Error: {stderr}")
                input("\nPress Enter to continue...")

            def _stash_list(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash List")
                print(Fore.CYAN + "="*50)

                stashes = self.git_stash.get_stash_list()
                if stashes:
                    print(Fore.CYAN + "Current stashes:")
                    for i, stash in enumerate(stashes):
                        print(f"{i}: {stash}")
                else:
                    print(Fore.YELLOW + "No stashes found.")
                input("\nPress Enter to continue...")

            def _stash_apply(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Apply")
                print(Fore.CYAN + "="*50)

                stashes = self.git_stash.get_stash_list()
                if not stashes:
                    print(Fore.YELLOW + "No stashes available to apply.")
                    input("\nPress Enter to continue...")
                    return

                stash_id = self.git_stash.display_stash_menu(stashes)
                if stash_id:
                    cmd = f'git stash apply {stash_id}'
                    print(Fore.CYAN + f"Running: {cmd}")
                    stdout, stderr, code = self.git_stash.run_command(cmd)
                    if code == 0:
                        print(Fore.GREEN + "Stash applied successfully!")
                        if stdout:
                            print(Fore.WHITE + stdout)
                    else:
                        print(Fore.RED + f"Error applying stash: {stderr}")
                else:
                    print(Fore.YELLOW + "Operation cancelled.")
                input("\nPress Enter to continue...")

            def _stash_pop(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Pop")
                print(Fore.CYAN + "="*50)

                stashes = self.git_stash.get_stash_list()
                if not stashes:
                    print(Fore.YELLOW + "No stashes available to pop.")
                    input("\nPress Enter to continue...")
                    return

                stash_id = self.git_stash.display_stash_menu(stashes)
                if stash_id:
                    cmd = f'git stash pop {stash_id}'
                    print(Fore.CYAN + f"Running: {cmd}")
                    stdout, stderr, code = self.git_stash.run_command(cmd)
                    if code == 0:
                        print(Fore.GREEN + "Stash popped successfully!")
                        if stdout:
                            print(Fore.WHITE + stdout)
                    else:
                        print(Fore.RED + f"Error popping stash: {stderr}")
                else:
                    print(Fore.YELLOW + "Operation cancelled.")
                input("\nPress Enter to continue...")

            def _stash_drop(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Drop")
                print(Fore.CYAN + "="*50)

                stashes = self.git_stash.get_stash_list()
                if not stashes:
                    print(Fore.YELLOW + "No stashes available to drop.")
                    input("\nPress Enter to continue...")
                    return

                stash_id = self.git_stash.display_stash_menu(stashes)
                if stash_id:
                    confirm = input(f"Are you sure you want to drop {stash_id}? (y/N): ")
                    if confirm.lower() == 'y':
                        cmd = f'git stash drop {stash_id}'
                        print(Fore.CYAN + f"Running: {cmd}")
                        stdout, stderr, code = self.git_stash.run_command(cmd)
                        if code == 0:
                            print(Fore.GREEN + "Stash dropped successfully!")
                            if stdout:
                                print(Fore.WHITE + stdout)
                        else:
                            print(Fore.RED + f"Error dropping stash: {stderr}")
                    else:
                        print(Fore.YELLOW + "Drop operation cancelled.")
                else:
                    print(Fore.YELLOW + "Operation cancelled.")
                input("\nPress Enter to continue...")

            def _stash_clear(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Clear")
                print(Fore.CYAN + "="*50)

                confirm = input("Are you sure you want to clear all stashes? This cannot be undone! (y/N): ")
                if confirm.lower() == 'y':
                    cmd = 'git stash clear'
                    print(Fore.CYAN + f"Running: {cmd}")
                    stdout, stderr, code = self.git_stash.run_command(cmd)
                    if code == 0:
                        print(Fore.GREEN + "All stashes cleared successfully!")
                        if stdout:
                            print(Fore.WHITE + stdout)
                    else:
                        print(Fore.RED + f"Error clearing stashes: {stderr}")
                else:
                    print(Fore.YELLOW + "Clear operation cancelled.")
                input("\nPress Enter to continue...")

            def _stash_details(self):
                self.clear_screen()
                print(Fore.CYAN + Style.BRIGHT + "Git Stash Details")
                print(Fore.CYAN + "="*50)

                stashes = self.git_stash.get_stash_list()
                if not stashes:
                    print(Fore.YELLOW + "No stashes available.")
                    input("\nPress Enter to continue...")
                    return

                stash_id = self.git_stash.display_stash_menu(stashes)
                if stash_id:
                    cmd = f'git stash show -p {stash_id}'
                    print(Fore.CYAN + f"Running: {cmd}")
                    stdout, stderr, code = self.git_stash.run_command(cmd)
                    if code == 0:
                        print(Fore.GREEN + f"Details for {stash_id}:")
                        print(Fore.WHITE + stdout)
                    else:
                        print(Fore.RED + f"Error showing stash details: {stderr}")
                else:
                    print(Fore.YELLOW + "Operation cancelled.")
                input("\nPress Enter to continue...")

            def _exit_menu(self):
                return "exit"

        stash_menu = GitStashMenu(self)
        stash_menu.run()

if __name__ == "__main__":
    stash = GitStash()
    stash.execute_stash_operations()