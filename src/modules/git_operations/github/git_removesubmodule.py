"""
Git Remove Submodule Module
Handles detection and management of nested repositories/submodules
"""

import os
import subprocess
import json
from typing import List, Tuple, Optional
from core.loading import loading_animation
from core.utils.exceptions import GitError
from core.menu import Menu, MenuItem


class GitRemoveSubmodule:
    """Handles detection and management of nested repositories/submodules"""
    
    def __init__(self):
        self.nested_repos: List[Tuple[str, str]] = []  # (folder_name, full_path)
        self.disabled_repos: List[Tuple[str, str]] = []  # Track disabled repos for recovery
        self.state_file = ".submodule_state.json"  # File to persist state
        self.load_state()
    
    def scan_all_repositories(self, base_path: str = ".") -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Fast scan for both active (.git) and disabled (.git_disable) repositories in one pass
        
        Args:
            base_path: Base directory to scan from
            
        Returns:
            Tuple of (active_repos, disabled_repos) lists containing (folder_name, full_path)
        """
        nested_repos = []
        disabled_repos = []
        
        try:
            for root, dirs, files in os.walk(base_path):
                # Skip the root .git and .git_disable directories
                if root == base_path:
                    if ".git" in dirs:
                        dirs.remove(".git")
                    if ".git_disable" in dirs:
                        dirs.remove(".git_disable")
                    continue
                
                folder_name = os.path.basename(root)
                
                # Check for both .git and .git_disable in one pass
                has_git = ".git" in dirs
                has_git_disable = ".git_disable" in dirs
                
                if has_git:
                    nested_repos.append((folder_name, root))
                    dirs.remove(".git")  # Don't traverse into .git
                
                if has_git_disable:
                    disabled_repos.append((folder_name, root))
                    dirs.remove(".git_disable")  # Don't traverse into .git_disable
            
            # Update both lists
            self.nested_repos = nested_repos
            self.disabled_repos = disabled_repos
            self.save_state()
            
            return nested_repos, disabled_repos
            
        except Exception as e:
            raise GitError(f"Error scanning for repositories: {str(e)}")
    
    def scan_nested_repositories(self, base_path: str = ".") -> List[Tuple[str, str]]:
        """Legacy method - use scan_all_repositories for better performance"""
        active_repos, _ = self.scan_all_repositories(base_path)
        return active_repos
    
    def scan_disabled_repositories(self, base_path: str = ".") -> List[Tuple[str, str]]:
        """Legacy method - use scan_all_repositories for better performance"""
        _, disabled_repos = self.scan_all_repositories(base_path)
        return disabled_repos
    
    def load_state(self) -> None:
        """Load persistent state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.disabled_repos = data.get('disabled_repos', [])
        except Exception as e:
            print(f"Warning: Could not load state file: {str(e)}")
            self.disabled_repos = []
    
    def save_state(self) -> None:
        """Save persistent state to file"""
        try:
            data = {
                'disabled_repos': self.disabled_repos
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state file: {str(e)}")
    
    def display_nested_repositories(self) -> None:
        """Display the list of found nested repositories"""
        if not self.nested_repos:
            print("No nested repositories found in the codebase.")
            return
        
        print("\n Found nested repositories/submodules:")
        print("=" * 50)
        for i, (folder_name, full_path) in enumerate(self.nested_repos, 1):
            print(f"{i}. {folder_name}")
            print(f"   Path: {full_path}")
            print()
    
    def choose_repository(self) -> Optional[Tuple[str, str]]:
        """
        Allow user to choose a repository from the list using arrow navigation
        
        Returns:
            Tuple of (folder_name, full_path) or None if cancelled
        """
        if not self.nested_repos:
            print("No repositories available to choose from.")
            input("\nPress Enter to continue...")
            return None
        
        menu = RepositorySelectionMenu(self.nested_repos)
        choice = menu.run_selection()
        
        if choice == "cancel":
            return None
        
        return choice
    
    def disable_and_remove_repository(self, repo_path: str) -> bool:
        """
        Disable repository and remove from git cache in one operation
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful, False otherwise
        """
        git_path = os.path.join(repo_path, ".git")
        disabled_path = os.path.join(repo_path, ".git_disable")
        
        try:
            if not os.path.exists(git_path):
                print(f" No .git directory found in {repo_path}")
                return False
            
            if os.path.exists(disabled_path):
                print(f" Repository already appears to be disabled (.git_disable exists)")
                return False
            
            # Step 1: Rename .git to .git_disable
            os.rename(git_path, disabled_path)
            print(f" Repository disabled: .git → .git_disable")
            
            # Step 2: Remove from git cache
            rel_path = os.path.relpath(repo_path)
            result = subprocess.run(
                ["git", "rm", "--cached", "-r", rel_path],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                print(f" Removed {rel_path} from git cache")
                print("   The folder is now pushable as regular files")
                
                # Add to disabled repos list for recovery tracking
                folder_name = os.path.basename(repo_path)
                self.disabled_repos.append((folder_name, repo_path))
                self.save_state()  # Persist state
                
                return True
            else:
                # If git rm failed, revert the .git rename
                os.rename(disabled_path, git_path)
                print(f" Error removing from git cache: {result.stderr}")
                print("   Reverted repository disable operation")
                return False
                
        except Exception as e:
            # Try to revert if something went wrong
            try:
                if os.path.exists(disabled_path) and not os.path.exists(git_path):
                    os.rename(disabled_path, git_path)
            except (OSError, PermissionError, FileNotFoundError):
                pass
            print(f" Error in disable and remove operation: {str(e)}")
            return False
    
    def remove_from_git_cache(self, repo_path: str) -> bool:
        """
        Remove the folder from git cache to make it pushable
        
        Args:
            repo_path: Path to the repository folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the relative path from current working directory
            rel_path = os.path.relpath(repo_path)
            
            # Run git rm --cached command
            result = subprocess.run(
                ["git", "rm", "--cached", "-r", rel_path],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                print(f" Removed {rel_path} from git cache")
                print("   The folder is now pushable as regular files")
                return True
            else:
                print(f" Error removing from git cache: {result.stderr}")
                return False
                
        except Exception as e:
            print(f" Error running git rm --cached: {str(e)}")
            return False
    
    def recover_repository(self, repo_path: str) -> bool:
        """
        Recover a disabled repository by renaming .git_disable back to .git
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful, False otherwise
        """
        git_path = os.path.join(repo_path, ".git")
        disabled_path = os.path.join(repo_path, ".git_disable")
        
        try:
            if not os.path.exists(disabled_path):
                print(f" No .git_disable directory found in {repo_path}")
                return False
            
            if os.path.exists(git_path):
                print(f" .git directory already exists in {repo_path}")
                return False
            
            # Rename .git_disable back to .git
            os.rename(disabled_path, git_path)
            
            # Remove from disabled repos list
            folder_name = os.path.basename(repo_path)
            self.disabled_repos = [
                (name, path) for name, path in self.disabled_repos 
                if path != repo_path
            ]
            self.save_state()  # Persist state
            
            print(f" Repository recovered: .git_disable → .git")
            return True
            
        except Exception as e:
            print(f" Error recovering repository: {str(e)}")
            return False
    
    def display_disabled_repositories(self) -> None:
        """Display list of currently disabled repositories"""
        if not self.disabled_repos:
            print("No disabled repositories found.")
            return
        
        print("\n Currently disabled repositories:")
        print("=" * 40)
        for i, (folder_name, full_path) in enumerate(self.disabled_repos, 1):
            print(f"{i}. {folder_name}")
            print(f"   Path: {full_path}")
            print()
    
    def run_interactive_menu(self) -> None:
        """Run the interactive menu for submodule management with auto-scan"""
        # Scan with loading animation for better UX
        with loading_animation("Scanning for repositories (.git and .git_disable)..."):
            active_repos, disabled_repos = self.scan_all_repositories()
        
        # Enhanced validation: allow access if either active OR disabled repositories exist
        has_active_repos = len(active_repos) > 0
        has_disabled_repos = len(disabled_repos) > 0
        
        if not has_active_repos and not has_disabled_repos:
            print("\n No nested repositories or disabled repositories found in the current directory.")
            print("   The submodule manager requires nested repositories (.git) or disabled repositories (.git_disable) to function.")
            input("\nPress Enter to return to the previous menu...")
            return
        
        # Display repositories summary header for quick reference
        self._display_repositories_header(active_repos, disabled_repos)
        
        # Display detailed repository information
        if has_active_repos:
            print(f"\n Active Repositories ({len(active_repos)}):")
            self.display_nested_repositories()
        
        if has_disabled_repos:
            print(f"\n Disabled Repositories ({len(disabled_repos)}):")
            self.display_disabled_repositories()
        
        if not has_active_repos:
            print("\n Note: Only disabled repositories found. You can recover them to make them active again.")
        
        menu = SubmoduleMenu(self)
        menu.run()
    
    def _display_repositories_header(self, active_repos: List[Tuple[str, str]], disabled_repos: List[Tuple[str, str]]) -> None:
        """Display a quick summary header of found repositories"""
        print("\n" + "="*80)
        print(" REPOSITORY SCAN RESULTS")
        print("="*80)
        
        # Active repositories header
        if active_repos:
            active_names = [name for name, _ in active_repos]
            print(f" Active (.git): {', '.join(active_names)}")
        else:
            print(" Active (.git): None")
        
        # Disabled repositories header  
        if disabled_repos:
            disabled_names = [name for name, _ in disabled_repos]
            print(f" Disabled (.git_disable): {', '.join(disabled_names)}")
        else:
            print(" Disabled (.git_disable): None")
            
        print("="*80)
    
    def choose_disabled_repository(self) -> Optional[Tuple[str, str]]:
        """
        Allow user to choose a disabled repository using arrow navigation
        
        Returns:
            Tuple of (folder_name, full_path) or None if cancelled
        """
        if not self.disabled_repos:
            print("No disabled repositories available.")
            input("\nPress Enter to continue...")
            return None
        
        menu = DisabledRepositorySelectionMenu(self.disabled_repos)
        choice = menu.run_selection()
        
        if choice == "cancel":
            return None
        
        return choice


class SubmoduleMenu(Menu):
    """Menu for Git submodule/nested repository management with arrow navigation"""
    
    def __init__(self, submodule_manager: GitRemoveSubmodule):
        self.manager = submodule_manager
        super().__init__(" Git Submodule/Nested Repository Manager")
        
        # Show disabled repositories if any exist
        self._show_disabled_repos()
    
    def _show_disabled_repos(self):
        """Display disabled repositories if any exist"""
        if self.manager.disabled_repos:
            print("\n" + "="*60)
            print(" Previously disabled repositories:")
            self.manager.display_disabled_repositories()
            print("="*60)
    
    def setup_items(self):
        """Setup menu items for submodule management"""
        self.items = [
            MenuItem("Disable & Remove Repository (Combined)", self._disable_and_remove_repository),
            MenuItem("Recover Disabled Repository", self._recover_repository),
            MenuItem("Rescan for Nested Repositories", self._rescan_repositories),
            MenuItem("Back to GitHub Operations", lambda: "exit")
        ]
    
    def _disable_and_remove_repository(self):
        """Disable repository and remove from git cache in one operation"""
        if not self.manager.nested_repos:
            print("No nested repositories found to disable.")
            input("\nPress Enter to continue...")
            return None
        
        selected = self.manager.choose_repository()
        if selected:
            folder_name, repo_path = selected
            print(f"\n Processing repository: {folder_name}")
            print("   1. Disabling repository (.git → .git_disable)")
            print("   2. Removing from git cache (git rm --cached)")
            
            if self.manager.disable_and_remove_repository(repo_path):
                print(f"\n Successfully processed repository: {folder_name}")
                print("    Repository disabled and removed from git cache")
                print("    Folder is now pushable as regular files")
                print("    State saved - will remember this change")
            input("\nPress Enter to continue...")
        return None
    
    def _rescan_repositories(self):
        """Rescan for nested repositories and disabled repositories with loading animation"""
        with loading_animation("Rescanning for repositories (.git and .git_disable)..."):
            active_repos, disabled_repos = self.manager.scan_all_repositories()
        
        # Display results with header for quick reference
        has_active_repos = len(active_repos) > 0
        has_disabled_repos = len(disabled_repos) > 0
        
        if not has_active_repos and not has_disabled_repos:
            print("\n No repositories found (neither active nor disabled).")
        else:
            # Show header summary
            self.manager._display_repositories_header(active_repos, disabled_repos)
            
            # Show detailed information
            if has_active_repos:
                print(f"\n Active Repositories ({len(active_repos)}):")
                self.manager.display_nested_repositories()
            
            if has_disabled_repos:
                print(f"\n Disabled Repositories ({len(disabled_repos)}):")
                self.manager.display_disabled_repositories()
        
        input("\nPress Enter to continue...")
        return None
    
    def _recover_repository(self):
        """Recover a disabled repository"""
        if not self.manager.disabled_repos:
            print("No disabled repositories found to recover.")
            input("\nPress Enter to continue...")
            return None
        
        selected = self.manager.choose_disabled_repository()
        if selected:
            folder_name, repo_path = selected
            print(f"\n Recovering repository: {folder_name}")
            print("   Restoring .git_disable → .git")
            
            if self.manager.recover_repository(repo_path):
                print(f"\n Successfully recovered repository: {folder_name}")
                print("    Repository is now active again")
                print("    State saved - change remembered")
            input("\nPress Enter to continue...")
        return None


class RepositorySelectionMenu(Menu):
    """Menu for selecting a repository from the list"""
    
    def __init__(self, repositories: List[Tuple[str, str]]):
        self.repositories = repositories
        super().__init__(" Select Repository")
    
    def setup_items(self):
        """Setup menu items for repository selection"""
        self.items = []
        
        for folder_name, full_path in self.repositories:
            # Show folder name and truncated path
            display_path = full_path if len(full_path) <= 50 else "..." + full_path[-47:]
            label = f"{folder_name} ({display_path})"
            self.items.append(MenuItem(label, lambda p=full_path, n=folder_name: (n, p)))
        
        self.items.append(MenuItem("Cancel", lambda: "cancel"))
    
    def run_selection(self):
        """Run menu and return selection"""
        choice = self.get_choice_with_arrows()
        Menu.clear_screen()
        return self.items[choice - 1].action()


class DisabledRepositorySelectionMenu(Menu):
    """Menu for selecting a disabled repository from the list"""
    
    def __init__(self, repositories: List[Tuple[str, str]]):
        self.repositories = repositories
        super().__init__(" Select Disabled Repository to Recover")
    
    def setup_items(self):
        """Setup menu items for disabled repository selection"""
        self.items = []
        
        for folder_name, full_path in self.repositories:
            # Show folder name and truncated path
            display_path = full_path if len(full_path) <= 50 else "..." + full_path[-47:]
            label = f"{folder_name} ({display_path})"
            self.items.append(MenuItem(label, lambda p=full_path, n=folder_name: (n, p)))
        
        self.items.append(MenuItem("Cancel", lambda: "cancel"))
    
    def run_selection(self):
        """Run menu and return selection"""
        choice = self.get_choice_with_arrows()
        Menu.clear_screen()
        return self.items[choice - 1].action()


def main():
    """Main function to run the git submodule manager"""
    try:
        manager = GitRemoveSubmodule()
        manager.run_interactive_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n An error occurred: {str(e)}")


if __name__ == "__main__":
    main()