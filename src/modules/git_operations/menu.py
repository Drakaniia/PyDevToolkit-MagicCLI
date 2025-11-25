"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
UPDATED: Changelog is now auto-generated after successful push
"""
import sys
from pathlib import Path
from typing import Any, Optional

# Add src directory to path to enable imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from github.git_status import GitStatus
from github.git_log import GitLog
from github.git_pull import GitPull
from github.git_push import GitPush
from github.git_initializer import GitInitializer
from github.git_recover import GitRecover
from github.git_removesubmodule import GitRemoveSubmodule
from github.git_cache import GitCache
from github.git_diff import GitDiff
from github.git_stash import GitStash
from core.menu import Menu, MenuItem
from core.utils.git_client import get_git_client


class GitOperations:
    """Unified Git operations orchestrator with dynamic directory detection"""

    def __init__(self):
        # Don't cache components - create fresh for each operation
        pass

    def _get_current_path(self) -> Path:
        """
        Get current working directory (updates dynamically)

        Returns:
            Path: Current working directory
        """
        return Path.cwd()

    def _refresh_git_client(self):
        """
        Get fresh GitClient for current directory

        Returns:
            GitClient: Fresh Git client instance for current directory
        """
        return get_git_client(working_dir=self._get_current_path())

    # ========== BASIC GIT OPERATIONS ==========

    def status(self) -> None:
        """Show git status"""
        status_handler = GitStatus()
        status_handler.show_status()

    def log(self) -> None:
        """Show git log"""
        log_handler = GitLog()
        log_handler.show_log(limit=10)

    def show_advanced_log_menu(self) -> None:
        """Show advanced log menu (delegated to GitLog class)"""
        log_handler = GitLog()
        log_handler.show_advanced_log_menu()

    def pull(self) -> None:
        """Pull from remote"""
        pull_handler = GitPull()
        pull_handler.pull()

    def push(self) -> None:
        """Add, commit, and push changes"""
        # Create fresh push handler for current directory
        push_handler = GitPush()
        push_handler.push()

    # ========== GIT INITIALIZATION ==========

    def initialize_and_push(self) -> None:
        """Initialize git repo and push to GitHub"""
        initializer = GitInitializer()
        initializer.initialize_and_push()

    # ========== GIT RECOVERY ==========

    def show_recovery_menu(self) -> None:
        """Show the commit recovery interface"""
        log_handler = GitLog()
        recovery_handler = GitRecover()
        recovery_handler.show_recovery_menu(
            commit_history_func=log_handler.get_commit_history,
            commit_details_func=log_handler.get_commit_details,
            verify_commit_func=log_handler.verify_commit_exists
        )

    def manage_submodules(self) -> None:
        """Manage nested repositories and submodules"""
        submodule_handler = GitRemoveSubmodule()
        submodule_handler.run_interactive_menu()

    def manage_cache(self) -> None:
        """Manage git cache and handle sensitive files"""
        cache_handler = GitCache()
        cache_handler.show_cache_menu()

    def show_diff_menu(self) -> None:
        """Show comprehensive diff operations menu"""
        diff_handler = GitDiff()
        diff_handler.show_diff_menu()

    def show_stash_menu(self) -> None:
        """Show comprehensive git stash operations menu"""
        stash_handler = GitStash()
        stash_handler.execute_stash_operations()


class GitMenu(Menu):
    """Unified menu for all Git operations"""

    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("🔧 GitHub Operations")

    def setup_items(self) -> None:
        """Setup menu items with all Git operations"""
        self.items = [
            MenuItem("Push (Add, Commit & Push)", lambda: self.git_ops.push()),
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Advanced Log Operations", lambda: self.git_ops.show_advanced_log_menu()),
            MenuItem("Diff Operations", lambda: self.git_ops.show_diff_menu()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Initialize Git & Push to GitHub", lambda: self.git_ops.initialize_and_push()),
            MenuItem("Generate Changelog", lambda: self._generate_changelog()),
            MenuItem("Git Recovery (Revert to Previous Commit)", lambda: self.git_ops.show_recovery_menu()),
            MenuItem("Git Cache (Handle Sensitive Files)", lambda: self.git_ops.manage_cache()),
            MenuItem("Manage Submodules/Nested Repos", lambda: self.git_ops.manage_submodules()),
            MenuItem("Git Stash Operations", lambda: self.git_ops.show_stash_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]

    def _generate_changelog(self) -> None:
        """Generate changelog manually without pushing"""
        try:
            from .changelog import ChangelogGenerator
            print("\n" + "="*70)
            print("📝 CHANGLOG GENERATOR")
            print("="*70 + "\n")

            # Ask user for number of commits to process
            try:
                num_commits_input = input("Enter number of recent commits to include in changelog (default 1): ").strip()
                num_commits = int(num_commits_input) if num_commits_input else 1
            except ValueError:
                num_commits = 1
                print("Using default value of 1 commit\n")

            if num_commits <= 0:
                print("❌ Invalid number of commits. Must be positive.")
                input("\nPress Enter to continue...")
                return

            print(f"🔄 Processing last {num_commits} commit(s)...\n")

            generator = ChangelogGenerator()
            success = generator.generate_changelog(num_commits=num_commits)

            if success:
                print(f"✅ Changelog updated successfully!")
                print(f"📄 File: {generator.CONFIG['changelog_file']}\n")
            else:
                print("ℹ️  No new commits to process or changelog already up to date\n")

            input("Press Enter to continue...")

        except ImportError as e:
            print(f"❌ Error importing ChangelogGenerator: {e}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"❌ Error generating changelog: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to continue...")