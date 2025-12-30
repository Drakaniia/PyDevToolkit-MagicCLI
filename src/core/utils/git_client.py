"""
automation/core/git_client.py
Unified Git client for all Git operations
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .exceptions import (
    GitError,
    GitCommandError,
    NotGitRepositoryError,
    NoRemoteError,
    GitNotInstalledError,
    UncommittedChangesError
)
# Import security and logging modules inside functions to avoid circular
# imports


class GitClient:
    """
    Unified Git client providing clean interface to Git operations

    Features:
    - Automatic error handling and user-friendly messages
    - Type-safe return values
    - Consistent API across all operations
    - Proper encoding handling
    """

    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize Git client

        Args:
            working_dir: Working directory (defaults to current directory)
        """
        self.working_dir = working_dir or Path.cwd()
        self._verify_git_installed()

    # ========== Repository Checks ==========

    def _run_internal_command(
        self,
        cmd: List[str],
        timeout: int = 10
    ) -> subprocess.CompletedProcess:
        """
        Run Git command for internal operations without security validation
        Used for operations that need to work before full security validation is set up

        Args:
            cmd: Command to run
            timeout: Command timeout in seconds
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            raise GitError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}",
                suggestion="Check for hung processes or network issues"
            )
        except FileNotFoundError:
            raise GitNotInstalledError()
        except Exception as e:
            raise GitError(
                f"Command failed: {' '.join(cmd)}",
                details={"error": str(e)}
            )

    def is_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = self._run_internal_command(
                ['git', 'rev-parse', '--is-inside-work-tree'])
            return result.returncode == 0
        except Exception:
            return False

    def ensure_repo(self) -> None:
        """Ensure we're in a Git repository, raise if not"""
        if not self.is_repo():
            raise NotGitRepositoryError(str(self.working_dir))

    # ========== Status Operations ==========

    def status(self, porcelain: bool = False) -> str:
        """
        Get repository status

        Args:
            porcelain: Return machine-readable format
        """
        self.ensure_repo()

        cmd = ['git', 'status']
        if porcelain:
            cmd.append('--porcelain')

        result = self._run_command(cmd, check=True)
        return result.stdout.strip()

    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes or untracked files

        This includes:
        - Modified tracked files
        - Deleted tracked files
        - Staged changes
        - Untracked files (new files not yet added)
        """
        try:
            status = self.status(porcelain=True)
            # Any non-empty output from git status --porcelain means there are changes
            # This includes both tracked changes AND untracked files (??)
            return bool(status and status.strip())
        except Exception:
            return False

    # ========== Add/Stage Operations ==========

    def add(self, files: Optional[List[str]] = None) -> bool:
        """
        Stage files for commit

        Args:
            files: Specific files to add (None = add all)
        """
        self.ensure_repo()

        cmd = ['git', 'add']
        if files:
            cmd.extend(files)
        else:
            cmd.append('.')

        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise

    # ========== Commit Operations ==========

    def commit(self, message: str, amend: bool = False) -> bool:
        """
        Create commit

        Args:
            message: Commit message
            amend: Amend previous commit
        """
        self.ensure_repo()

        if not message or not message.strip():
            raise GitError("Commit message cannot be empty")

        cmd = ['git', 'commit', '-m', message]
        if amend:
            cmd.append('--amend')

        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise

    # ========== Log Operations ==========

    def log(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get commit history

        Args:
            limit: Maximum number of commits to return
        """
        self.ensure_repo()

        result = self._run_command([
            'git', 'log',
            f'-{limit}',
            '--pretty=format:%H|%an|%ai|%s'
        ], check=True)

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('|', 3)
            if len(parts) == 4:
                commit_hash, author, date, message = parts

                commits.append({
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'author': author,
                    'date': date,
                    'message': message
                })

        return commits

    # ========== Branch Operations ==========

    def current_branch(self) -> str:
        """Get current branch name"""
        self.ensure_repo()

        result = self._run_command(
            ['git', 'branch', '--show-current'],
            check=True
        )
        return result.stdout.strip()

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create new branch

        Args:
            branch_name: Name of new branch
            checkout: Switch to new branch
        """
        self.ensure_repo()

        cmd = ['git', 'branch', branch_name]
        self._run_command(cmd, check=True)

        if checkout:
            self._run_command(['git', 'checkout', branch_name], check=True)

        return True

    def get_all_branches(self, include_remote: bool = True) -> List[Dict[str, str]]:
        """
        Get all branches with metadata

        Args:
            include_remote: Whether to include remote branches

        Returns:
            List of branch dictionaries with name, type, commit, message, date
        """
        self.ensure_repo()
        branches = []

        try:
            # Get current branch
            current_branch = self.current_branch()

            # Get local branches
            result = self._run_command(['git', 'branch', '-v', '--no-color'], check=True)
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue

                # Parse branch line
                is_current = line.startswith('*')
                parts = line.split()
                if len(parts) >= 2:
                    branch_name = parts[1].strip()
                    commit_hash = parts[2] if len(parts) > 2 else ""
                    message = ' '.join(parts[3:]) if len(parts) > 3 else ""

                    branches.append({
                        'name': branch_name,
                        'type': 'local',
                        'is_current': is_current,
                        'commit': commit_hash,
                        'message': message
                    })

            # Get remote branches if requested
            if include_remote:
                result = self._run_command(['git', 'branch', '-r', '-v', '--no-color'], check=True)
                for line in result.stdout.strip().split('\n'):
                    if not line.strip() or '->' in line:
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        branch_name = parts[0].strip()
                        commit_hash = parts[1] if len(parts) > 1 else ""
                        message = ' '.join(parts[2:]) if len(parts) > 2 else ""

                        # Avoid duplicates with local branches
                        local_name = branch_name.split('/')[-1]
                        is_duplicate = any(b['name'] == local_name for b in branches)

                        if not is_duplicate:
                            branches.append({
                                'name': branch_name,
                                'type': 'remote',
                                'is_current': False,
                                'commit': commit_hash,
                                'message': message
                            })

        except GitCommandError:
            pass

        return branches

    def get_remote_branches(self) -> List[str]:
        """
        Get list of remote branch names

        Returns:
            List of remote branch names
        """
        self.ensure_repo()

        try:
            result = self._run_command(['git', 'branch', '-r'], check=True)
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and '->' not in line:
                    branches.append(line.strip())
            return branches
        except GitCommandError:
            return []

    def rename_branch(self, old_name: str, new_name: str) -> bool:
        """
        Rename a branch

        Args:
            old_name: Old branch name
            new_name: New branch name
        """
        self.ensure_repo()

        cmd = ['git', 'branch', '-m', old_name, new_name]
        self._run_command(cmd, check=True)
        return True

    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """
        Delete a local branch

        Args:
            branch_name: Branch name to delete
            force: Force delete even if unmerged
        """
        self.ensure_repo()

        cmd = ['git', 'branch', '-d']
        if force:
            cmd = ['git', 'branch', '-D']
        cmd.append(branch_name)

        self._run_command(cmd, check=True)
        return True

    def delete_remote_branch(self, branch_name: str, remote: str = 'origin') -> bool:
        """
        Delete a remote branch

        Args:
            branch_name: Branch name to delete (without remote prefix)
            remote: Remote name
        """
        self.ensure_repo()

        cmd = ['git', 'push', remote, f':{branch_name}']
        self._run_command(cmd, check=True)
        return True

    def merge_branch(self, branch_name: str, no_ff: bool = False) -> bool:
        """
        Merge a branch into current branch

        Args:
            branch_name: Branch name to merge
            no_ff: Create merge commit even if fast-forward is possible
        """
        self.ensure_repo()

        cmd = ['git', 'merge']
        if no_ff:
            cmd.append('--no-ff')
        cmd.append(branch_name)

        self._run_command(cmd, check=True)
        return True

    def get_branch_diff(self, branch1: str, branch2: str) -> str:
        """
        Get diff between two branches

        Args:
            branch1: First branch name
            branch2: Second branch name

        Returns:
            Diff output
        """
        self.ensure_repo()

        result = self._run_command(['git', 'diff', f'{branch1}...{branch2}'], check=True)
        return result.stdout

    def get_branch_ahead_behind(self, branch1: str, branch2: str) -> Tuple[int, int]:
        """
        Get commit counts ahead/behind between two branches

        Args:
            branch1: First branch name
            branch2: Second branch name

        Returns:
            Tuple of (behind_count, ahead_count)
        """
        self.ensure_repo()

        result = self._run_command(
            ['git', 'rev-list', '--left-right', '--count', f'{branch1}...{branch2}'],
            check=True
        )

        left, right = result.stdout.strip().split()
        return (int(left), int(right))

    def set_upstream(self, branch_name: str, remote: str = 'origin') -> bool:
        """
        Set upstream tracking for current branch

        Args:
            branch_name: Remote branch name to track
            remote: Remote name
        """
        self.ensure_repo()

        cmd = ['git', 'branch', '--set-upstream-to', f'{remote}/{branch_name}']
        self._run_command(cmd, check=True)
        return True

    def checkout_branch(self, branch_name: str) -> bool:
        """
        Switch to a branch

        Args:
            branch_name: Branch name to switch to
        """
        self.ensure_repo()

        cmd = ['git', 'checkout', branch_name]
        self._run_command(cmd, check=True)
        return True

    def fetch_remote_branches(self, remote: str = 'origin') -> bool:
        """
        Fetch all remote branches

        Args:
            remote: Remote name
        """
        self.ensure_repo()

        cmd = ['git', 'fetch', remote]
        self._run_command(cmd, check=True)
        return True

    # ========== Remote Operations ==========

    def has_remote(self, remote_name: str = 'origin') -> bool:
        """Check if remote exists"""
        try:
            result = self._run_command(
                ['git', 'remote', 'get-url', remote_name],
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_remote_url(self, remote_name: str = 'origin') -> Optional[str]:
        """Get remote URL"""
        try:
            result = self._run_command(
                ['git', 'remote', 'get-url', remote_name],
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
            pass
        return None

    def add_remote(self, remote_name: str, url: str) -> bool:
        """Add remote repository"""
        self.ensure_repo()

        self._run_command(
            ['git', 'remote', 'add', remote_name, url],
            check=True
        )
        return True

    def set_remote_url(self, remote_name: str, url: str) -> bool:
        """Update remote URL"""
        self.ensure_repo()

        self._run_command(
            ['git', 'remote', 'set-url', remote_name, url],
            check=True
        )
        return True

    # ========== Push/Pull Operations ==========

    def push(
        self,
        remote: str = 'origin',
        branch: Optional[str] = None,
        set_upstream: bool = False,
        force: bool = False
    ) -> bool:
        """
        Push commits to remote

        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            set_upstream: Set upstream tracking
            force: Force push
        """
        self.ensure_repo()

        if not self.has_remote(remote):
            raise NoRemoteError(remote)

        cmd = ['git', 'push']

        if set_upstream:
            cmd.append('--set-upstream')
        if force:
            cmd.append('--force')

        cmd.append(remote)

        if branch:
            cmd.append(branch)
        elif set_upstream:
            # Need explicit branch for set-upstream
            cmd.append(self.current_branch())

        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError as e:
            # Check for common issues
            if "no upstream" in e.stderr.lower():
                raise GitError(
                    "No upstream branch set",
                    suggestion="Use set_upstream=True to set upstream"
                )
            raise

    def pull(
        self,
        remote: str = 'origin',
        branch: Optional[str] = None,
        rebase: bool = False
    ) -> bool:
        """
        Pull changes from remote

        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            rebase: Use rebase instead of merge
        """
        self.ensure_repo()

        cmd = ['git', 'pull']

        if rebase:
            cmd.append('--rebase')

        cmd.append(remote)

        if branch:
            cmd.append(branch)

        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise

    # ========== Reset Operations ==========

    def reset(
        self,
        commit: str,
        mode: str = 'mixed'
    ) -> bool:
        """
        Reset to specific commit

        Args:
            commit: Commit hash or reference
            mode: Reset mode (soft, mixed, hard)
        """
        self.ensure_repo()

        valid_modes = ['soft', 'mixed', 'hard']
        if mode not in valid_modes:
            raise GitError(f"Invalid reset mode: {mode}")

        cmd = ['git', 'reset', f'--{mode}', commit]

        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise

    # ========== Init Operations ==========

    def init(self) -> bool:
        """Initialize new Git repository"""
        if self.is_repo():
            raise GitError("Already a Git repository")

        self._run_command(['git', 'init'], check=True)
        return True

    # ========== Internal Helpers ==========

    def _verify_git_installed(self) -> None:
        """Verify Git is installed"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                raise GitNotInstalledError()
        except FileNotFoundError:
            raise GitNotInstalledError()
        except subprocess.TimeoutExpired:
            raise GitError("Git command timed out during verification")

    def _run_command(
        self,
        cmd: List[str],
        check: bool = False,
        timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """
        Run Git command with proper error handling

        Args:
            cmd: Command to run
            check: Raise on non-zero return code
            timeout: Command timeout in seconds
        """
        # Import security and logging modules here to avoid circular imports
        from core.security.validator import SecurityValidator
        from core.utils.logging import log_command_execution

        # Validate the command for security
        for element in cmd:
            if not SecurityValidator.validate_command_input(str(element)):
                raise GitError(
                    f"Command contains potentially dangerous element: {element}",
                    suggestion="Use only safe command elements without shell metacharacters")

        try:
            # Ensure shell=False to prevent shell injection
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                shell=False  # Explicitly disable shell to prevent injection
            )

            # Log command execution for audit purposes
            log_command_execution(' '.join(cmd), 'N/A', result.returncode == 0)

            if check and result.returncode != 0:
                raise GitCommandError(
                    command=' '.join(cmd),
                    return_code=result.returncode,
                    stderr=result.stderr
                )

            return result

        except subprocess.TimeoutExpired:
            log_command_execution(' '.join(cmd), 'N/A', False)
            raise GitError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}",
                suggestion="Check for hung processes or network issues"
            )
        except FileNotFoundError:
            log_command_execution(' '.join(cmd), 'N/A', False)
            raise GitNotInstalledError()
        except Exception as e:
            log_command_execution(' '.join(cmd), 'N/A', False)
            raise GitError(
                f"Command failed: {' '.join(cmd)}",
                details={"error": str(e)}
            )


# Singleton instance
_git_client: Optional[GitClient] = None


def get_git_client(
        working_dir: Optional[Path] = None,
        force_new: bool = False) -> GitClient:
    """
    Get or create GitClient singleton

    Args:
        working_dir: Working directory (creates new instance if different)
        force_new: Force creation of new instance (bypasses singleton)
    """
    global _git_client

    # Force new instance if requested (helps with stale state issues)
    if force_new:
        return GitClient(working_dir)

    if _git_client is None or (
            working_dir and working_dir != _git_client.working_dir):
        _git_client = GitClient(working_dir)

    return _git_client
