"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
UPDATED: Changelog is now auto-generated after successful push
"""
from pathlib import Path
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
from menu import Menu, MenuItem
from core.git_client import get_git_client


class GitOperations:
    """Unified Git operations orchestrator with dynamic directory detection"""
    
    def __init__(self):
        # Don't cache components - create fresh for each operation
        pass
    
    def _get_current_path(self):
        """Get current working directory (updates dynamically)"""
        return Path.cwd()
    
    def _refresh_git_client(self):
        """Get fresh GitClient for current directory"""
        return get_git_client(working_dir=self._get_current_path())
    
    # ========== BASIC GIT OPERATIONS ==========
    
    def status(self):
        """Show git status"""
        status_handler = GitStatus()
        status_handler.show_status()
    
    def log(self):
        """Show git log"""
        log_handler = GitLog()
        log_handler.show_log(limit=10)

    def show_advanced_log_menu(self):
        """Show advanced log menu (delegated to GitLog class)"""
        log_handler = GitLog()
        log_handler.show_advanced_log_menu()
    
    def pull(self):
        """Pull from remote"""
        pull_handler = GitPull()
        pull_handler.pull()
    
    def push(self):
        """Add, commit, and push changes"""
        # Create fresh push handler for current directory
        push_handler = GitPush()
        push_handler.push()
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        initializer = GitInitializer()
        initializer.initialize_and_push()
    
    # ========== GIT RECOVERY ==========
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        log_handler = GitLog()
        recovery_handler = GitRecover()
        recovery_handler.show_recovery_menu(
            commit_history_func=log_handler.get_commit_history,
            commit_details_func=log_handler.get_commit_details,
            verify_commit_func=log_handler.verify_commit_exists
        )
    
    def manage_submodules(self):
        """Manage nested repositories and submodules"""
        submodule_handler = GitRemoveSubmodule()
        submodule_handler.run_interactive_menu()
    
    def manage_cache(self):
        """Manage git cache and handle sensitive files"""
        cache_handler = GitCache()
        cache_handler.show_cache_menu()

    def show_diff_menu(self):
        """Show comprehensive diff operations menu"""
        diff_handler = GitDiff()
        diff_handler.show_diff_menu()

    def show_stash_menu(self):
        """Show comprehensive git stash operations menu"""
        stash_handler = GitStash()
        stash_handler.execute_stash_operations()


class GitMenu(Menu):
    """Unified menu for all Git operations"""
    
    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("🔧 GitHub Operations")
    
    def setup_items(self):
        """Setup menu items with all Git operations"""
        self.items = [
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Advanced Log Operations", lambda: self.git_ops.show_advanced_log_menu()),
            MenuItem("Diff Operations", lambda: self.git_ops.show_diff_menu()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Push (Add, Commit & Push)", lambda: self.git_ops.push()),
            MenuItem("Initialize Git & Push to GitHub", lambda: self.git_ops.initialize_and_push()),
            MenuItem("Git Recovery (Revert to Previous Commit)", lambda: self.git_ops.show_recovery_menu()),
            MenuItem("Git Cache (Handle Sensitive Files)", lambda: self.git_ops.manage_cache()),
            MenuItem("Manage Submodules/Nested Repos", lambda: self.git_ops.manage_submodules()),
            MenuItem("Git Stash Operations", lambda: self.git_ops.show_stash_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]