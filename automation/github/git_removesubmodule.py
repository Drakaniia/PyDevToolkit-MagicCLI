"""
Git Remove Submodule Module
Handles detection and management of nested repositories/submodules
"""

import os
import subprocess
from typing import List, Tuple, Optional
from automation.core.loading import loading_animation
from automation.core.exceptions import GitError
from automation.menu import Menu, MenuItem


class GitRemoveSubmodule:
    """Handles detection and management of nested repositories/submodules"""
    
    def __init__(self):
        self.nested_repos: List[Tuple[str, str]] = []  # (folder_name, full_path)
        self.disabled_repos: List[Tuple[str, str]] = []  # Track disabled repos for recovery
    
    def scan_nested_repositories(self, base_path: str = ".") -> List[Tuple[str, str]]:
        """
        Scan the codebase for nested repositories (folders containing .git)
        
        Args:
            base_path: Base directory to scan from
            
        Returns:
            List of tuples containing (folder_name, full_path)
        """
        nested_repos = []
        
        try:
            for root, dirs, files in os.walk(base_path):
                # Skip the root .git directory
                if root == base_path and ".git" in dirs:
                    dirs.remove(".git")
                    continue
                
                # Check if current directory contains .git
                if ".git" in dirs:
                    folder_name = os.path.basename(root)
                    nested_repos.append((folder_name, root))
                    # Don't traverse into nested .git directories
                    dirs.remove(".git")
            
            self.nested_repos = nested_repos
            return nested_repos
            
        except Exception as e:
            raise GitError(f"Error scanning for nested repositories: {str(e)}")
    
    def display_nested_repositories(self) -> None:
        """Display the list of found nested repositories"""
        if not self.nested_repos:
            print("No nested repositories found in the codebase.")
            return
        
        print("\n🔍 Found nested repositories/submodules:")
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
    
    def disable_repository(self, repo_path: str) -> bool:
        """
        Temporarily disable a repository by renaming .git to .git_disabled
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful, False otherwise
        """
        git_path = os.path.join(repo_path, ".git")
        disabled_path = os.path.join(repo_path, ".git_disabled")
        
        try:
            if not os.path.exists(git_path):
                print(f"❌ No .git directory found in {repo_path}")
                return False
            
            if os.path.exists(disabled_path):
                print(f"❌ Repository already appears to be disabled (.git_disabled exists)")
                return False
            
            # Rename .git to .git_disabled
            os.rename(git_path, disabled_path)
            
            # Add to disabled repos list for recovery tracking
            folder_name = os.path.basename(repo_path)
            self.disabled_repos.append((folder_name, repo_path))
            
            print(f"✅ Repository disabled: .git → .git_disabled")
            return True
            
        except Exception as e:
            print(f"❌ Error disabling repository: {str(e)}")
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
                print(f"✅ Removed {rel_path} from git cache")
                print("   The folder is now pushable as regular files")
                return True
            else:
                print(f"❌ Error removing from git cache: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running git rm --cached: {str(e)}")
            return False
    
    def recover_repository(self, repo_path: str) -> bool:
        """
        Recover a disabled repository by renaming .git_disabled back to .git
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful, False otherwise
        """
        git_path = os.path.join(repo_path, ".git")
        disabled_path = os.path.join(repo_path, ".git_disabled")
        
        try:
            if not os.path.exists(disabled_path):
                print(f"❌ No .git_disabled directory found in {repo_path}")
                return False
            
            if os.path.exists(git_path):
                print(f"❌ .git directory already exists in {repo_path}")
                return False
            
            # Rename .git_disabled back to .git
            os.rename(disabled_path, git_path)
            
            # Remove from disabled repos list
            folder_name = os.path.basename(repo_path)
            self.disabled_repos = [
                (name, path) for name, path in self.disabled_repos 
                if path != repo_path
            ]
            
            print(f"✅ Repository recovered: .git_disabled → .git")
            return True
            
        except Exception as e:
            print(f"❌ Error recovering repository: {str(e)}")
            return False
    
    def display_disabled_repositories(self) -> None:
        """Display list of currently disabled repositories"""
        if not self.disabled_repos:
            print("No disabled repositories found.")
            return
        
        print("\n🔄 Currently disabled repositories:")
        print("=" * 40)
        for i, (folder_name, full_path) in enumerate(self.disabled_repos, 1):
            print(f"{i}. {folder_name}")
            print(f"   Path: {full_path}")
            print()
    
    def run_interactive_menu(self) -> None:
        """Run the interactive menu for submodule management"""
        menu = SubmoduleMenu(self)
        menu.run()
    
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
        super().__init__("🔧 Git Submodule/Nested Repository Manager")
    
    def setup_items(self):
        """Setup menu items for submodule management"""
        self.items = [
            MenuItem("Scan for nested repositories", self._scan_repositories),
            MenuItem("Disable repository (rename .git)", self._disable_repository),
            MenuItem("Remove from git cache (git rm --cached)", self._remove_from_cache),
            MenuItem("Recover disabled repository", self._recover_repository),
            MenuItem("View disabled repositories", self._view_disabled),
            MenuItem("Back to GitHub Operations", lambda: "exit")
        ]
    
    def _scan_repositories(self):
        """Scan for nested repositories"""
        with loading_animation("Scanning for nested repositories..."):
            self.manager.scan_nested_repositories()
        
        self.manager.display_nested_repositories()
        input("\nPress Enter to continue...")
        return None
    
    def _disable_repository(self):
        """Disable a repository"""
        if not self.manager.nested_repos:
            print("Please scan for repositories first.")
            input("\nPress Enter to continue...")
            return None
        
        selected = self.manager.choose_repository()
        if selected:
            folder_name, repo_path = selected
            if self.manager.disable_repository(repo_path):
                print(f"\n✅ Successfully disabled repository: {folder_name}")
                print("   You can now use 'Remove from git cache' to make it pushable.")
            input("\nPress Enter to continue...")
        return None
    
    def _remove_from_cache(self):
        """Remove repository from git cache"""
        if not self.manager.nested_repos:
            print("Please scan for repositories first.")
            input("\nPress Enter to continue...")
            return None
        
        selected = self.manager.choose_repository()
        if selected:
            folder_name, repo_path = selected
            if self.manager.remove_from_git_cache(repo_path):
                print(f"\n✅ Successfully removed {folder_name} from git cache")
                print("   The folder can now be pushed as regular files.")
            input("\nPress Enter to continue...")
        return None
    
    def _recover_repository(self):
        """Recover a disabled repository"""
        if not self.manager.disabled_repos:
            self.manager.display_disabled_repositories()
            input("\nPress Enter to continue...")
            return None
        
        selected = self.manager.choose_disabled_repository()
        if selected:
            folder_name, repo_path = selected
            if self.manager.recover_repository(repo_path):
                print(f"\n✅ Successfully recovered repository: {folder_name}")
            input("\nPress Enter to continue...")
        return None
    
    def _view_disabled(self):
        """View disabled repositories"""
        self.manager.display_disabled_repositories()
        input("\nPress Enter to continue...")
        return None


class RepositorySelectionMenu(Menu):
    """Menu for selecting a repository from the list"""
    
    def __init__(self, repositories: List[Tuple[str, str]]):
        self.repositories = repositories
        super().__init__("📂 Select Repository")
    
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
        super().__init__("🔄 Select Disabled Repository to Recover")
    
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
        print(f"\n❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    main()