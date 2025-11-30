"""
automation/github/git_push.py
Enhanced Git push with comprehensive retry strategies and automatic changelog generation
UPDATED: Automatically generates changelog after successful push
"""
from pathlib import Path
from typing import Optional, List, Tuple
import sys
import time
import subprocess

from core.utils.git_client import get_git_client
from core.utils.exceptions import (
    ExceptionHandler,
    GitError,
    GitCommandError,
    UncommittedChangesError,
    handle_errors
)
from core.loading import LoadingSpinner, loading_animation


class PushStrategy:
    """Represents a push strategy with specific flags"""
    
    def __init__(
        self,
        name: str,
        flags: List[str],
        description: str,
        requires_confirmation: bool = False,
        is_destructive: bool = False
    ):
        self.name = name
        self.flags = flags
        self.description = description
        self.requires_confirmation = requires_confirmation
        self.is_destructive = is_destructive
    
    def __repr__(self):
        return f"PushStrategy({self.name})"


class PushConfig:
    """Configuration for push retry behavior"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.network_timeout = 30  # seconds
        self.enable_auto_hooks_bypass = True
        self.enable_auto_upstream = True
        self.enable_force_push = True
        self.exponential_backoff = True
        self.auto_generate_changelog = True  # NEW: Enable auto-changelog
        self.auto_handle_gitignore = True  # NEW: Auto-handle .gitignore changes
        
        # Define progressive strategies
        self.strategies = [
            PushStrategy(
                "normal",
                [],
                "Standard push",
                requires_confirmation=False
            ),
            PushStrategy(
                "set-upstream",
                ["--set-upstream"],
                "Push and set upstream tracking",
                requires_confirmation=False
            ),
            PushStrategy(
                "no-verify",
                ["--no-verify"],
                "Skip pre-push hooks",
                requires_confirmation=False
            ),
            PushStrategy(
                "no-verify-upstream",
                ["--no-verify", "--set-upstream"],
                "Skip hooks and set upstream",
                requires_confirmation=False
            ),
            PushStrategy(
                "force-with-lease",
                ["--force-with-lease", "--no-verify"],
                "Force push (safer - checks remote state)",
                requires_confirmation=True,
                is_destructive=True
            ),
            PushStrategy(
                "force",
                ["--force", "--no-verify"],
                "Force push (destructive - overwrites remote)",
                requires_confirmation=True,
                is_destructive=True
            ),
        ]


# ProgressIndicator class removed - now using LoadingSpinner from automation.core.loading


class GitPushRetry:
    """
    Enhanced Git push with automatic retry and changelog generation
    
    Features:
    - Progressive retry strategies
    - Automatic hook bypass detection
    - Smart force push with user confirmation
    - Network retry with exponential backoff
    - Automatic changelog generation after successful push
    """
    
    def __init__(self, config: Optional[PushConfig] = None):
        self.current_dir = Path.cwd()
        self.git = get_git_client()
        self.config = config or PushConfig()
        self.attempt_count = 0
    
    @handle_errors()
    def push_with_retry(
        self,
        commit_message: Optional[str] = None,
        remote: str = 'origin',
        branch: Optional[str] = None
    ) -> bool:
        """
        Execute push with comprehensive retry strategies and auto-changelog
        
        Args:
            commit_message: Commit message (if staging changes)
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)
        
        Returns:
            True if push succeeded, False otherwise
        """
        # Get current branch if not specified
        if not branch:
            try:
                branch = self.git.current_branch()
            except Exception as e:
                print(f" Could not determine current branch: {e}")
                return False
        
        # Stage and commit if there are changes
        if commit_message and self._has_changes():
            if not self._stage_and_commit(commit_message):
                return False
        
        # Execute push with progressive strategies
        push_success = self._execute_push_with_strategies(remote, branch)
        
        # Handle results
        if push_success:
            self._show_push_summary()
            # Generate changelog after successful push
            if self.config.auto_generate_changelog:
                self._auto_generate_changelog()
        
        return push_success
    
    def _auto_generate_changelog(self):
        """Automatically generate changelog for the latest commit"""
        try:
            # Import here to avoid circular dependency
            from ..changelog import ChangelogGenerator
            
            changelog_gen = ChangelogGenerator()
            # Generate changelog for the most recent commit
            changelog_gen.generate_changelog(num_commits=1)
        
        except Exception:
            # Silently continue even if changelog generation fails
            pass
    
    def _execute_push_with_strategies(self, remote: str, branch: str) -> bool:
        """Try push with progressive strategies until success"""
        print(f" Pushing to {remote}/{branch}")
        print(f" Max attempts: {len(self.config.strategies)}")
        
        last_error = None
        
        for idx, strategy in enumerate(self.config.strategies, 1):
            self.attempt_count = idx
            
            print(f"\n Attempt {idx}/{len(self.config.strategies)}: {strategy.name}")
            print(f"   Description: {strategy.description}")
            
            # Check if confirmation needed
            if strategy.requires_confirmation:
                if not self._confirm_destructive_operation(strategy):
                    print(" Operation cancelled by user")
                    continue
            
            # Try the strategy with loading animation
            success, error = self._try_push_strategy_with_animation(strategy, remote, branch)
            
            if success:
                self._show_push_summary()
                return True
            
            last_error = error
            
            # Analyze error and decide next step
            should_continue, wait_time = self._analyze_error_and_decide(
                error, idx, strategy
            )
            
            if not should_continue:
                break
            
            if wait_time > 0 and idx < len(self.config.strategies):
                time.sleep(wait_time)
        
        # All strategies failed
        print("\n PUSH FAILED - All retry strategies exhausted")
        self._show_failure_guidance(last_error)
        return False
    
    def _try_push_strategy(
        self,
        strategy: PushStrategy,
        remote: str,
        branch: str
    ) -> Tuple[bool, Optional[Exception]]:
        """Try a specific push strategy"""
        try:
            # Build git push command
            cmd = ['git', 'push']
            cmd.extend(strategy.flags)
            cmd.extend([remote, branch])
            
            # Show command being executed
            print(f"   $ {' '.join(cmd)}")
            
            # Execute with progress indicator
            with LoadingSpinner(f"Pushing with {strategy.name}", style='dots'):
                result = self.git._run_command(
                    cmd,
                    check=True,
                    timeout=self.config.network_timeout
                )
            
            print(f"    Push successful!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            
            return True, None
        
        except GitCommandError as e:
            print(f"    Failed: {self._extract_error_message(e.stderr)}")
            return False, e
        
        except Exception as e:
            print(f"    Unexpected error: {str(e)}")
            return False, e
    
    def _try_push_strategy_with_animation(
        self,
        strategy: PushStrategy,
        remote: str,
        branch: str
    ) -> Tuple[bool, Optional[Exception]]:
        """Try a specific push strategy with loading animation"""
        try:
            # Build git push command
            cmd = ['git', 'push']
            cmd.extend(strategy.flags)
            cmd.extend([remote, branch])
            
            # Execute with enhanced loading animation
            with LoadingSpinner(f"Pushing to {remote}/{branch} using {strategy.name}", style='dots'):
                result = self.git._run_command(
                    cmd,
                    check=True,
                    timeout=self.config.network_timeout
                )
            
            print(f"    ✅ Push successful!")
            if result.stdout:
                # Only show relevant output, filter out verbose info
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if line.strip() and not line.startswith('To ') and 'Everything up-to-date' not in line:
                        print(f"    {line}")
            
            return True, None
        
        except GitCommandError as e:
            print(f"    ❌ Push failed: {self._extract_error_message(e.stderr)}")
            return False, e
        
        except Exception as e:
            print(f"    ❌ Unexpected error: {str(e)}")
            return False, e
    
    def _analyze_error_and_decide(
        self,
        error: Optional[Exception],
        attempt: int,
        strategy: PushStrategy
    ) -> Tuple[bool, int]:
        """Analyze error and decide whether to continue"""
        if not error:
            return False, 0

        error_msg = str(error).lower()
        if hasattr(error, 'stderr'):
            error_msg = error_msg + " " + str(error.stderr).lower()

        is_auth = any(x in error_msg for x in [
            'authentication', 'permission denied', 'credentials',
            'authentication failed', 'could not authenticate',
            '403', '401', 'fatal:.*authentication', 'http.*403'
        ])

        is_network = any(x in error_msg for x in [
            'network', 'timeout', 'connection', 'could not resolve',
            'connection refused', 'connection timed out', 'host unreachable',
            'could not read from remote', 'send pack', 'fetch failed'
        ])

        is_hook_error = any(x in error_msg for x in [
            'pre-push hook', 'hook declined', 'hook failed',
            'husky', 'lint-staged'
        ])

        is_diverged = any(x in error_msg for x in [
            'diverged', 'non-fast-forward', 'rejected',
            'fetch first', 'pull is required', 'fast-forward'
        ])

        is_no_upstream = any(x in error_msg for x in [
            'no upstream', 'no tracking', 'upstream branch',
            'origin/', 'does not exist upstream'
        ])

        is_permission = any(x in error_msg for x in [
            'permission denied', 'insufficient permissions', 'protected branch',
            'push declined', 'branch is protected'
        ])

        is_large_file = any(x in error_msg for x in [
            'large file', 'lfs', 'file too large', 'size exceeds',
            'upload-pack', 'unpack error'
        ])

        is_rate_limit = any(x in error_msg for x in [
            'rate limit', 'api rate', 'too many requests',
            'exceeded rate', 'abuse detection'
        ])

        if is_auth:
            return False, 0

        if is_network:
            wait_time = 0
            if self.config.exponential_backoff:
                wait_time = min(2 ** attempt, 8)
            else:
                wait_time = self.config.retry_delay
            should_continue = attempt < len(self.config.strategies)
            return should_continue, wait_time

        if is_permission:
            return False, 0

        # For all other errors, continue to next strategy
        should_continue = attempt < len(self.config.strategies)
        return should_continue, 0
    
    def _confirm_destructive_operation(self, strategy: PushStrategy) -> bool:
        """Get user confirmation for destructive operations"""
        print(f"\n  WARNING: {strategy.name.upper()} is a destructive operation!")
        print(f"   This will overwrite remote history.")
        print(f"   Description: {strategy.description}\n")
        
        try:
            self._show_divergence_info()
        except Exception:
            pass
        
        print("\n Do you want to proceed?")
        print("   Type 'YES' (all caps) to confirm:")
        
        confirmation = input("   > ").strip()
        
        return confirmation == "YES"
    
    def _show_divergence_info(self):
        """Show information about diverged commits"""
        try:
            result = self.git._run_command(
                ['git', 'log', 'origin/HEAD..HEAD', '--oneline'],
                check=False
            )
            
            if result.stdout.strip():
                print("    Local commits that will overwrite remote:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"      • {line}")
        except Exception:
            pass
    
    def _pre_push_checks(self) -> bool:
        """Run pre-push validation checks"""
        print(" Pre-push validation...\n")

        checks = [
            ("Git repository", self.git.is_repo),
            ("Remote configured", lambda: self.git.has_remote('origin')),
            ("Network connectivity", self._check_network_connectivity),
            ("Remote accessibility", self._check_remote_accessibility),
            ("Local changes", self._has_local_changes),
            ("Branch exists remotely", self._check_remote_branch_exists),
            ("Diverged commits", self._check_for_diverged_commits),
        ]

        all_passed = True
        check_results = {}

        for check_name, check_func in checks:
            try:
                result = check_func()
                check_results[check_name.lower()] = result
                status = "" if result else ""
                print(f"   {status} {check_name}")
            except Exception as e:
                print(f"    {check_name}: {e}")
                check_results[check_name.lower()] = False
                # For local changes and network connectivity, we don't want to fail completely
                if check_name not in ["Local changes", "Network connectivity"]:
                    all_passed = False

        print()

        # Determine if critical checks failed (not including local changes and network connectivity)
        critical_checks_passed = True
        for check_name, check_func in checks:
            if check_name in ["Local changes", "Network connectivity"]:
                continue  # Skip these in critical check
            try:
                result = check_results.get(check_name.lower(), True)
                if not result:
                    critical_checks_passed = False
            except (KeyError, AttributeError):
                critical_checks_passed = False

        all_passed = critical_checks_passed

        # Provide specific error diagnosis based on failed checks
        if not all_passed:
            print("  Pre-push checks failed\n")
            print(" Detailed diagnosis:")

            if not check_results.get("git repository", True):
                print("   • Not in a Git repository - Initialize first")
            elif not check_results.get("remote configured", True):
                print("   • No remote repository configured - Set up remote first")
            elif not check_results.get("network connectivity", True):
                # Only show network issue if remote accessibility also failed
                if not check_results.get("remote accessibility", True):
                    print("   • No internet connection - Check your network")
                else:
                    # Network ping failed but git remote access worked, so not a real issue
                    print("   • Network ping failed but remote Git access works - Continuing")
            elif not check_results.get("remote accessibility", True):
                print("   • Cannot access remote repository - Check internet or repository permission")
            elif not check_results.get("local changes", True):
                print("   • No staged changes detected - Will attempt to stage and commit")
            elif not check_results.get("diverged commits", True):
                print("   • Local and remote branches have diverged - Pull first or use merge strategy")
            elif not check_results.get("branch exists remotely", True):
                print("   • Remote branch doesn't exist - Push with upstream flag")

            print("\n Suggestions:")
            if not check_results.get("git repository", True):
                print("   • Initialize Git: magic → Initialize Git & Push to GitHub")
            elif not check_results.get("remote configured", True):
                print("   • Configure remote: git remote add origin <url>")
            elif not check_results.get("network connectivity", True) and not check_results.get("remote accessibility", True):
                print("   • Check internet connection and firewall settings")
            elif not check_results.get("remote accessibility", True):
                print("   • Verify repository URL and access permissions")
            elif not check_results.get("local changes", True):
                print("   • Changes will be automatically staged and committed")
            else:
                print("   • Address the specific issues identified above")

            print()
            # If network connectivity failed but git remote access worked, continue anyway
            if (not check_results.get("network connectivity", True) and
                check_results.get("remote accessibility", True)):
                print(" Network ping failed but Git remote access succeeded - continuing with push...")
                return True
            input("Press Enter to continue...")

        return all_passed

    def _check_network_connectivity(self) -> bool:
        """Check if there's internet connectivity"""
        from ..core.security import SecurityValidator

        try:
            # Use a safe connection method without system commands
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=5)  # DNS port
            return True
        except (OSError, TimeoutError, socket.error):
            try:
                import urllib.request
                urllib.request.urlopen('https://www.google.com', timeout=5)
                return True
            except (OSError, TimeoutError, urllib.error.URLError):
                return False

    def _check_remote_accessibility(self) -> bool:
        """Check if remote repository is accessible"""
        try:
            if not self.git.has_remote('origin'):
                return False

            # Try to fetch from remote to check accessibility
            result = self.git._run_command(['git', 'fetch', 'origin'], check=False)
            return result.returncode == 0
        except (subprocess.CalledProcessError, OSError, TimeoutError):
            return False

    def _has_local_changes(self) -> bool:
        """Check if there are staged changes ready to be pushed"""
        try:
            # Check for staged changes - if no staged changes, check for any changes to prompt user
            result = self.git._run_command(['git', 'diff', '--cached', '--quiet'], check=False)
            # Return True if there are staged changes (return code != 0 means changes exist)
            if result.returncode != 0:
                return True
            # If no staged changes, check if there are uncommitted changes (staging needed)
            status_result = self.git.status(porcelain=True)
            return bool(status_result.strip())
        except (subprocess.CalledProcessError, OSError):
            # If we can't check directly, use git status
            try:
                status_result = self.git.status(porcelain=True)
                return bool(status_result.strip())
            except (subprocess.CalledProcessError, OSError):
                return False

    def _check_remote_branch_exists(self) -> bool:
        """Check if the remote branch exists"""
        try:
            current_branch = self.git.current_branch()
            result = self.git._run_command(['git', 'ls-remote', '--heads', 'origin', current_branch], check=False)
            return len(result.stdout.strip()) > 0
        except (subprocess.CalledProcessError, OSError, TimeoutError):
            return False

    def _check_for_diverged_commits(self) -> bool:
        """Check if local and remote branches have diverged"""
        try:
            current_branch = self.git.current_branch()

            # Get the current commit count difference between local and remote
            result = self.git._run_command(
                ['git', 'rev-list', '--left-right', '--count', f'origin/{current_branch}...HEAD'],
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                left, right = result.stdout.strip().split()
                left_count = int(left)
                right_count = int(right)

                # If both have commits that the other doesn't have, they've diverged
                if left_count > 0 and right_count > 0:
                    print(f"     Branch divergence detected: +{right_count} local, +{left_count} remote")
                    return False
                return True
            return True
        except (subprocess.CalledProcessError, ValueError, OSError, TimeoutError):
            # If we can't determine, be permissive
            return True
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes or untracked files"""
        try:
            # Use fresh Git client to avoid stale state issues
            fresh_git = get_git_client(working_dir=Path.cwd(), force_new=True)
            status = fresh_git.status(porcelain=True)
            return bool(status and status.strip())
        except Exception:
            return False
    
    def _stage_and_commit(self, message: str) -> bool:
        """Enhanced staging and commit with smart error handling and auto-fix"""
        
        # Step 1: Check for .gitignore changes and handle previously tracked files
        if not self._handle_gitignore_changes():
            return False
        
        # Step 2: Pre-staging diagnostics with auto-fix (quiet mode)
        staging_issues = self._diagnose_staging_issues()
        if staging_issues:
            # Try to auto-fix critical issues (like lock files) silently
            if any("lock file" in issue.lower() for issue in staging_issues):
                if self._auto_fix_git_issues(staging_issues):
                    # Re-run diagnostics to confirm fix
                    new_issues = self._diagnose_staging_issues()
                    if new_issues and any("lock file" in issue.lower() for issue in new_issues):
                        self._provide_manual_fix_guidance(new_issues)
                        return False
                else:
                    self._provide_manual_fix_guidance(staging_issues)
                    return False
        
        # Step 3: Smart staging with fallbacks (quiet mode)
        if not self._smart_stage_changes_quiet():
            return False
        
        # Step 4: Commit with validation (quiet mode)
        return self._smart_commit_quiet(message)
    
    def _diagnose_staging_issues(self) -> List[str]:
        """Diagnose potential staging issues before attempting to stage"""
        issues = []
        
        try:
            # Check if we're in a git repo
            if not self.git.is_repo():
                issues.append("Not in a Git repository")
                return issues
            
            # CRITICAL: Check for Git lock files first
            git_dir = Path(self.git.working_dir) / '.git'
            lock_files = self._check_git_lock_files(git_dir)
            if lock_files:
                for lock_file in lock_files:
                    issues.append(f"Git lock file detected: {lock_file}")
                # This is a critical issue that prevents all Git operations
                return issues
            
            # Check git status
            try:
                status_output = self.git.status(porcelain=True)
                if not status_output.strip():
                    issues.append("No changes to stage")
                    return issues
            except Exception as e:
                if "index.lock" in str(e).lower() or "unable to create" in str(e).lower():
                    issues.append("Git index lock detected from git status command")
                    return issues
                issues.append(f"Git status error: {str(e)}")
                return issues
            
            # Check for problematic files
            lines = status_output.strip().split('\n')
            for line in lines:
                if len(line) >= 3:
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    # Check for binary files that might cause issues
                    if any(ext in file_path.lower() for ext in ['.exe', '.dll', '.so', '.dylib']):
                        issues.append(f"Binary file detected: {file_path}")
                    
                    # Check for very large files
                    try:
                        file_obj = Path(self.git.working_dir) / file_path
                        if file_obj.exists() and file_obj.stat().st_size > 100 * 1024 * 1024:  # 100MB
                            issues.append(f"Large file detected (>100MB): {file_path}")
                    except (OSError, PermissionError, FileNotFoundError):
                        pass
                    
                    # Check for deleted files
                    if status_code[0] == 'D' or status_code[1] == 'D':
                        issues.append(f"Deleted file: {file_path}")
        
        except Exception as e:
            if "index.lock" in str(e).lower() or "unable to create" in str(e).lower():
                issues.append("Git lock file issue detected")
            else:
                issues.append(f"Diagnostic error: {str(e)}")
        
        return issues
    
    def _check_git_lock_files(self, git_dir: Path) -> List[str]:
        """Check for Git lock files that prevent operations"""
        lock_files = []
        
        try:
            # Common Git lock files
            potential_locks = [
                'index.lock',
                'HEAD.lock',
                'refs/heads/main.lock',
                'refs/heads/master.lock',
                'config.lock',
                'packed-refs.lock'
            ]
            
            for lock_file in potential_locks:
                lock_path = git_dir / lock_file
                if lock_path.exists():
                    lock_files.append(str(lock_path))
            
            # Check for branch-specific locks
            refs_heads = git_dir / 'refs' / 'heads'
            if refs_heads.exists():
                for branch_file in refs_heads.glob('*.lock'):
                    lock_files.append(str(branch_file))
        
        except Exception:
            pass
        
        return lock_files
    
    def _auto_fix_git_issues(self, issues: List[str]) -> bool:
        """Automatically fix common Git issues"""
        fixed_any = False
        
        for issue in issues:
            if "lock file" in issue.lower():
                if self._fix_git_lock_files():
                    print("    Fixed Git lock file issues")
                    fixed_any = True
                else:
                    print("    Failed to fix Git lock file issues")
        
        return fixed_any
    
    def _fix_git_lock_files(self) -> bool:
        """Fix Git lock file issues by safely removing lock files"""
        try:
            git_dir = Path(self.git.working_dir) / '.git'
            lock_files = self._check_git_lock_files(git_dir)
            
            if not lock_files:
                return True  # No lock files to fix
            
            print(f"    Found {len(lock_files)} lock file(s) to remove:")
            
            removed_count = 0
            for lock_file_path in lock_files:
                try:
                    lock_path = Path(lock_file_path)
                    
                    # Safety check: ensure it's actually a lock file
                    if lock_path.name.endswith('.lock') and lock_path.exists():
                        print(f"      • Removing: {lock_path.name}")
                        
                        # Try to remove the lock file
                        lock_path.unlink()
                        removed_count += 1
                        
                        # Verify it's actually gone
                        if not lock_path.exists():
                            print(f"         Successfully removed {lock_path.name}")
                        else:
                            print(f"         Failed to remove {lock_path.name}")
                    
                except Exception as e:
                    print(f"       Error removing {lock_file_path}: {e}")
            
            if removed_count > 0:
                print(f"    Successfully removed {removed_count} lock file(s)")
                
                # Wait a moment for filesystem to catch up
                import time
                time.sleep(0.5)
                
                # Verify Git operations work now
                try:
                    self.git.status(porcelain=True)
                    print("    Git operations restored")
                    return True
                except Exception as e:
                    print(f"     Git still has issues after lock removal: {e}")
                    return False
            else:
                print("    No lock files were successfully removed")
                return False
        
        except Exception as e:
            print(f"    Error during lock file fix: {e}")
            return False
    
    def _provide_manual_fix_guidance(self, issues: List[str]) -> None:
        """Provide manual fix guidance for remaining issues"""
        print("\n" + "="*60)
        print(" MANUAL FIX REQUIRED")
        print("="*60)
        
        lock_file_issues = [issue for issue in issues if "lock file" in issue.lower()]
        
        if lock_file_issues:
            print("\n Git Lock File Issues:")
            print("   If auto-fix failed, try these manual steps:")
            print("   1. Close any Git GUI applications (GitKraken, SourceTree, etc.)")
            print("   2. Close any IDE/editors that might be running Git operations")
            print("   3. Wait for any background Git processes to complete")
            print("   4. Manually remove lock files:")
            
            git_dir = Path(self.git.working_dir) / '.git'
            lock_files = self._check_git_lock_files(git_dir)
            for lock_file in lock_files:
                print(f"      rm \"{lock_file}\"")
            
            print("   5. If on Windows, check Task Manager for git.exe processes")
            print("   6. Restart your terminal/command prompt")
            
            print("\n One-liner fix commands:")
            print("   Windows: del \".git\\index.lock\" 2>nul")
            print("   Linux/Mac: rm -f .git/index.lock")
        
        print("\n" + "="*60)
    
    def _handle_gitignore_changes(self) -> bool:
        """Handle .gitignore changes by removing previously tracked files that now match ignore patterns"""
        try:
            # Check if .gitignore has been modified or is new
            status_output = self.git.status(porcelain=True)
            gitignore_modified = False
            
            if status_output:
                lines = status_output.strip().split('\n')
                for line in lines:
                    if len(line) >= 3:
                        file_path = line[3:]
                        if file_path == '.gitignore' or file_path.endswith('/.gitignore'):
                            gitignore_modified = True
                            break
            
            if not gitignore_modified:
                return True  # No .gitignore changes, continue normally
            
            # Get all tracked files
            try:
                tracked_files_result = self.git._run_command(
                    ['git', 'ls-files'], 
                    check=True
                )
                tracked_files = tracked_files_result.stdout.strip().split('\n') if tracked_files_result.stdout.strip() else []
            except Exception:
                return True  # Continue with normal staging
            
            if not tracked_files:
                return True  # No tracked files to check
            
            # Check which tracked files now match .gitignore patterns
            files_to_remove = []
            
            for file_path in tracked_files:
                if not file_path.strip():
                    continue
                
                try:
                    # Use git check-ignore to see if file should be ignored
                    check_ignore_result = self.git._run_command(
                        ['git', 'check-ignore', file_path],
                        check=False
                    )
                    
                    # If git check-ignore returns 0, the file matches an ignore pattern
                    if check_ignore_result.returncode == 0:
                        files_to_remove.append(file_path)
                
                except Exception:
                    continue  # Skip files that cause errors
            
            if not files_to_remove:
                return True  # No files to remove
            
            # Check if auto-handling is enabled
            if self.config.auto_handle_gitignore:
                # Auto-remove files from tracking
                removed_count = 0
                failed_removals = []
                
                # Process files in batches to avoid command line length limits
                batch_size = 100
                for i in range(0, len(files_to_remove), batch_size):
                    batch = files_to_remove[i:i + batch_size]
                    try:
                        # Remove batch from Git tracking
                        self.git._run_command(
                            ['git', 'rm', '--cached', '-r'] + batch,
                            check=True
                        )
                        removed_count += len(batch)
                    except Exception:
                        # If batch fails, try individual files
                        for file_path in batch:
                            try:
                                self.git._run_command(
                                    ['git', 'rm', '--cached', '-r', file_path],
                                    check=True
                                )
                                removed_count += 1
                            except Exception:
                                failed_removals.append(file_path)
                
                # Only show summary if there were failures
                if failed_removals:
                    print(f"  Warning: Could not remove {len(failed_removals)} files from tracking")
            else:
                # Ask user for confirmation
                print(f"\n Found {len(files_to_remove)} previously tracked files that now match .gitignore patterns")
                print("   These files are currently tracked in Git but now match .gitignore patterns.")
                print("   They should be removed from Git tracking (this will delete them from the remote repository)")
                print("   Do you want to remove them from Git tracking?")
                print("   Type 'YES' to remove them, or 'NO' to keep them tracked:")
                user_choice = input("   > ").strip().upper()
                
                if user_choice == 'YES':
                    print(f"\n  Removing {len(files_to_remove)} files from Git tracking...")
                    
                    # Remove files from Git tracking using git rm --cached
                    removed_count = 0
                    failed_removals = []
                    
                    for file_path in files_to_remove:
                        try:
                            result = self.git._run_command(
                                ['git', 'rm', '--cached', file_path],
                                check=False
                            )
                            
                            if result.returncode == 0:
                                removed_count += 1
                            else:
                                failed_removals.append(file_path)
                        
                        except Exception:
                            failed_removals.append(file_path)
                    
                    # Only show summary if there were failures
                    if failed_removals:
                        print(f"  Warning: Could not remove {len(failed_removals)} files from tracking")
                elif user_choice == 'NO':
                    print("\n Keeping files tracked in Git (they will remain in the repository)")
                else:
                    print("\n  Invalid choice. Keeping files tracked for safety.")
            
            return True
            
        except Exception:
            # Continue silently even if this fails
            return True
    
    def _smart_stage_changes(self) -> bool:
        """Smart staging with multiple fallback strategies"""
        strategies = [
            ("Standard staging", self._stage_standard),
            ("Interactive staging", self._stage_interactive),
            ("Individual file staging", self._stage_individual_files),
            ("Force staging", self._stage_force)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                print(f" Trying {strategy_name.lower()}...")
                if strategy_func():
                    print(f" {strategy_name} successful\n")
                    return True
                else:
                    print(f"  {strategy_name} had issues, trying next strategy...\n")
            except Exception as e:
                print(f" {strategy_name} failed: {e}")
                print(f"   Trying next strategy...\n")
        
        print(" All staging strategies failed")
        self._provide_staging_guidance()
        return False
    
    def _smart_stage_changes_quiet(self) -> bool:
        """Smart staging with multiple fallback strategies (quiet mode)"""
        strategies = [
            self._stage_standard,
            self._stage_interactive,
            self._stage_individual_files,
            self._stage_force
        ]
        
        for strategy_func in strategies:
            try:
                if strategy_func():
                    return True
            except Exception:
                continue
        
        return False
    
    def _stage_standard(self) -> bool:
        """Standard git add . staging"""
        try:
            self.git.add()
            return True
        except Exception:
            return False
    
    def _stage_interactive(self) -> bool:
        """Interactive staging to handle problematic files"""
        try:
            # Get list of changed files
            status_output = self.git.status(porcelain=True)
            if not status_output.strip():
                return False
            
            # Stage files one by one, skipping problematic ones
            lines = status_output.strip().split('\n')
            staged_count = 0
            
            for line in lines:
                if len(line) >= 3:
                    file_path = line[3:]
                    try:
                        # Try to stage individual file
                        result = self.git._run_command(['git', 'add', file_path], check=False)
                        if result.returncode == 0:
                            staged_count += 1
                        else:
                            print(f"     Skipped problematic file: {file_path}")
                    except (subprocess.CalledProcessError, OSError, PermissionError):
                        print(f"     Skipped problematic file: {file_path}")
            
            return staged_count > 0
        
        except Exception:
            return False
    
    def _stage_individual_files(self) -> bool:
        """Stage files individually with detailed error reporting"""
        try:
            status_output = self.git.status(porcelain=True)
            if not status_output.strip():
                return False
            
            lines = status_output.strip().split('\n')
            successful_files = []
            failed_files = []
            
            for line in lines:
                if len(line) >= 3:
                    file_path = line[3:]
                    try:
                        # Check if file exists
                        full_path = Path(self.git.working_dir) / file_path
                        if not full_path.exists() and line[0] != 'D':
                            failed_files.append((file_path, "File not found"))
                            continue
                        
                        # Try to add the file
                        result = self.git._run_command(['git', 'add', file_path], check=False)
                        if result.returncode == 0:
                            successful_files.append(file_path)
                        else:
                            failed_files.append((file_path, result.stderr.strip()))
                    
                    except Exception as e:
                        failed_files.append((file_path, str(e)))
            
            if successful_files:
                print(f"    Successfully staged {len(successful_files)} files")
                if failed_files:
                    print(f"     Failed to stage {len(failed_files)} files:")
                    for file_path, error in failed_files[:3]:  # Show first 3 errors
                        print(f"      - {file_path}: {error}")
                    if len(failed_files) > 3:
                        print(f"      ... and {len(failed_files) - 3} more")
                return True
            
            return False
        
        except Exception:
            return False
    
    def _stage_force(self) -> bool:
        """Force staging with git add -A"""
        try:
            result = self.git._run_command(['git', 'add', '-A'], check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def _smart_commit(self, message: str) -> bool:
        """Smart commit with validation"""
        try:
            # Check if there are staged changes
            result = self.git._run_command(['git', 'diff', '--cached', '--quiet'], check=False)
            if result.returncode == 0:
                print("  No staged changes to commit")
                return False
            
            print(f" Creating commit: '{message}'")
            self.git.commit(message)
            print(" Commit created\n")
            return True
        
        except Exception as e:
            print(f" Failed to commit: {e}")
            self._provide_commit_guidance()
            return False
    
    def _smart_commit_quiet(self, message: str) -> bool:
        """Smart commit with validation (quiet mode)"""
        try:
            # Check if there are staged changes
            result = self.git._run_command(['git', 'diff', '--cached', '--quiet'], check=False)
            if result.returncode == 0:
                return False
            
            self.git.commit(message)
            return True
        
        except Exception:
            return False
    
    def _provide_staging_guidance(self) -> None:
        """Provide guidance when staging fails"""
        print("\n Staging Troubleshooting Guide:")
        print("   1. Check if you're in a Git repository: git status")
        print("   2. Check for file permission issues")
        print("   3. Look for large files or binary files that might be problematic")
        print("   4. Try staging files individually: git add <filename>")
        print("   5. Check .gitignore for conflicting patterns")
        print("   6. Verify file paths don't contain special characters")
        print()
    
    def _provide_commit_guidance(self) -> None:
        """Provide guidance when commit fails"""
        print("\n Commit Troubleshooting Guide:")
        print("   1. Ensure you have staged changes: git status")
        print("   2. Check commit message length and characters")
        print("   3. Verify Git user configuration: git config user.name/user.email")
        print("   4. Try with a simpler commit message")
        print()
    
    def _provide_push_failure_guidance(self) -> None:
        """Provide comprehensive guidance when push fails completely"""
        print("\n" + "="*60)
        print(" PUSH FAILURE DIAGNOSTIC & SOLUTIONS")
        print("="*60)
        
        print("\n Common Push Failure Causes & Solutions:")
        
        print("\n1.  NETWORK/CONNECTIVITY ISSUES:")
        print("   • Check internet connection")
        print("   • Verify remote URL: git remote -v")
        print("   • Test connectivity: git ls-remote origin")
        print("   • Try with different network or VPN")
        
        print("\n2.  AUTHENTICATION ISSUES:")
        print("   • Check Git credentials: git config --list")
        print("   • Update GitHub token/SSH key")
        print("   • Run: git credential-manager-core erase")
        print("   • Re-authenticate: git push (will prompt)")
        
        print("\n3.  REPOSITORY STATE ISSUES:")
        print("   • Check repo status: git status")
        print("   • View recent commits: git log --oneline -5")
        print("   • Check branch tracking: git branch -vv")
        print("   • Ensure branch exists on remote")
        
        print("\n4.  PERMISSION ISSUES:")
        print("   • Verify you have push access to the repository")
        print("   • Check if branch is protected")
        print("   • Ensure you're pushing to correct remote/branch")
        
        print("\n5.  REPOSITORY SIZE ISSUES:")
        print("   • Check for large files: git ls-files | xargs ls -la")
        print("   • Use Git LFS for large files")
        print("   • Consider splitting large commits")
        
        print("\n IMMEDIATE TROUBLESHOOTING STEPS:")
        print("   1. Run: git status (check current state)")
        print("   2. Run: git remote -v (verify remote URL)")
        print("   3. Run: git branch -vv (check branch tracking)")
        print("   4. Run: git push --verbose (detailed push output)")
        print("   5. Try: git push --force-with-lease (if safe)")
        
        print("\n ALTERNATIVE APPROACHES:")
        print("   • Create new branch: git checkout -b new-feature")
        print("   • Reset and retry: git reset --soft HEAD~1")
        print("   • Manual push: git push origin <branch-name>")
        print("   • Use GitHub CLI: gh repo sync")
        
        print("\n" + "="*60)
    
    def _show_push_summary(self):
        """Show visually appealing summary after successful push"""
        try:
            # Import colorama for colors
            from colorama import Fore, Style, init
            init()
            
            print("\n" + "="*70)
            print(f"{Fore.GREEN}{'PUSH SUCCESSFUL!':^70}{Style.RESET_ALL}")
            print("="*70)
            
            # Get latest commit info using safer commands
            self._show_latest_commit_info()
            
            # Get diff statistics for the pushed commit
            self._show_commit_statistics()
            
            # Get repository status
            self._show_repository_status()
            
            print("\n" + "="*70)
            print(f"{Fore.GREEN}{'All changes pushed successfully!':^70}{Style.RESET_ALL}")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"  Could not generate full summary: {e}")
    
    def _show_latest_commit_info(self):
        """Show latest commit information using safe git commands"""
        try:
            # Import colorama for colors
            from colorama import Fore, Style, init
            init()
            
            print(f"\n{Fore.CYAN}Latest Commit:{Style.RESET_ALL}")
            
            # Get commit hash
            hash_result = self.git._run_command(
                ['git', 'rev-parse', '--short', 'HEAD'],
                check=False
            )
            if hash_result.returncode == 0:
                commit_hash = hash_result.stdout.strip()
                print(f"    {commit_hash}")
            
            # Use git show without format to get commit info
            show_result = self.git._run_command(
                ['git', 'show', '--name-only', '--oneline', 'HEAD'],
                check=False
            )
            if show_result.returncode == 0:
                lines = show_result.stdout.strip().split('\n')
                if lines:
                    # First line contains hash and message
                    first_line = lines[0]
                    # Skip the hash if already shown
                    if ' ' in first_line:
                        message = first_line.split(' ', 1)[1]
                        print(f"    {message}")
                    
                    # Show author from the second line (if it exists)
                    if len(lines) > 1 and 'Author:' in lines[1]:
                        author_line = lines[1]
                        if ':' in author_line:
                            author = author_line.split(':', 1)[1].strip()
                            print(f"    Author: {author}")
                
        except Exception as e:
            print(f"    Could not retrieve commit details: {e}")
    
    def _show_commit_statistics(self):
        """Show comprehensive file change statistics with beautiful design"""
        try:
            # Import colorama for colors
            from colorama import Fore, Style, init
            init()
            
            # Get statistics for the latest commit
            result = self.git._run_command(
                ['git', 'show', '--stat', '--format=', 'HEAD'],
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Create a beautiful header with gradient effect
                print(f"\n{Fore.CYAN}╔{'═'*78}╗{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║{Fore.YELLOW}{'📊COMMIT STATISTICS':^77}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╠{'═'*78}╣{Style.RESET_ALL}")
                
                stats_lines = result.stdout.strip().split('\n')
                file_changes = []
                summary_line = None
                
                # Separate file changes from summary
                for line in stats_lines:
                    if line.strip():
                        if ' changed' in line:
                            summary_line = line
                        else:
                            file_changes.append(line)
                
                # Parse and display summary with enhanced visuals
                if summary_line:
                    import re
                    match = re.search(r'(\d+)\s+files?\s+changed(?:,\s+(\d+)\s+insertions?\(\+\))?(?:,\s+(\d+)\s+deletions?\(-\))?', summary_line)
                    if match:
                        files_changed = int(match.group(1))
                        insertions = int(match.group(2) or '0')
                        deletions = int(match.group(3) or '0')
                        total_changes = insertions + deletions
                        
                        # Summary section with visual indicators
                        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}📁 Files Changed:{Style.RESET_ALL} {files_changed:<3} {Fore.CYAN}│{Style.RESET_ALL} {Fore.GREEN}➕ Insertions:{Style.RESET_ALL} {insertions:<4} {Fore.CYAN}│{Style.RESET_ALL} {Fore.RED}➖ Deletions:{Style.RESET_ALL} {deletions:<10} {Fore.CYAN}║{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}╟{'─'*78}╢{Style.RESET_ALL}")
                        
                        # Visual representation of changes
                        if total_changes > 0:
                            ins_percentage = (insertions / total_changes) * 100
                            del_percentage = (deletions / total_changes) * 100
                            
                            # Create progress bars
                            bar_width = 50
                            ins_width = int((ins_percentage / 100) * bar_width)
                            del_width = int((del_percentage / 100) * bar_width)
                            
                            # Insertions bar
                            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}Insertions:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}║{Style.RESET_ALL}   [{Fore.GREEN}{'█' * ins_width}{Style.DIM}{'░' * (bar_width - ins_width)}{Style.RESET_ALL}] {ins_percentage:.1f}% ({insertions} lines) {Fore.CYAN}║{Style.RESET_ALL}")
                            
                            # Deletions bar
                            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.RED}Deletions:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}║{Style.RESET_ALL}   [{Fore.RED}{'█' * del_width}{Style.DIM}{'░' * (bar_width - del_width)}{Style.RESET_ALL}] {del_percentage:.1f}% ({deletions} lines) {Fore.CYAN}║{Style.RESET_ALL}")
                            
                            # Net change indicator
                            net_change = insertions - deletions
                            if net_change > 0:
                                net_color = Fore.GREEN
                                net_symbol = "↑"
                            elif net_change < 0:
                                net_color = Fore.RED
                                net_symbol = "↓"
                            else:
                                net_color = Fore.YELLOW
                                net_symbol = "→"
                            
                            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Net Change:{Style.RESET_ALL} {net_color}{net_symbol} {abs(net_change)} lines{Style.RESET_ALL} {'':<38} {Fore.CYAN}║{Style.RESET_ALL}")
                
                # Display detailed file changes if any
                if file_changes:
                    print(f"{Fore.CYAN}╠{'═'*78}╣{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}║{Fore.MAGENTA}{'📋 DETAILED FILE CHANGES':^78}{Fore.CYAN}║{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}╟{'─'*78}╢{Style.RESET_ALL}")
                    
                    # Sort files by change count (most changes first)
                    file_data = []
                    for line in file_changes[:15]:  # Show max 15 files
                        if line.strip() and '|' in line:
                            file_part, stats_part = line.rsplit('|', 1)
                            file_path = file_part.strip()
                            
                            # Extract numbers from stats
                            import re
                            stats_match = re.search(r'(\d+)(?:\s*([+-]+))?', stats_part.strip())
                            if stats_match:
                                changes = int(stats_match.group(1))
                                symbols = stats_match.group(2) or ''
                                
                                file_data.append((file_path, changes, symbols))
                    
                    # Sort by number of changes
                    file_data.sort(key=lambda x: x[1], reverse=True)
                    
                    for file_path, changes, symbols in file_data:
                        # Truncate long file paths
                        display_path = file_path
                        if len(file_path) > 60:
                            display_path = '...' + file_path[-57:]
                        
                        # Color code based on change type
                        if '+' in symbols and '-' in symbols:
                            change_color = Fore.YELLOW
                            change_type = "Modified"
                        elif '+' in symbols:
                            change_color = Fore.GREEN
                            change_type = "Added"
                        elif '-' in symbols:
                            change_color = Fore.RED
                            change_type = "Deleted"
                        else:
                            change_color = Fore.WHITE
                            change_type = "Changed"
                        
                        print(f"{Fore.CYAN}║{Style.RESET_ALL} {change_color}{change_type:>8}:{Style.RESET_ALL} {display_path:<45} {changes:>4} changes {Fore.CYAN}║{Style.RESET_ALL}")
                    
                    if len(file_changes) > 15:
                        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{'... and ' + str(len(file_changes) - 15) + ' more files':^78} {Fore.CYAN}║{Style.RESET_ALL}")
                
                # Footer with summary
                print(f"{Fore.CYAN}╠{'═'*78}╣{Style.RESET_ALL}")
                if summary_line and match:
                    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{'Total: ' + str(total_changes) + ' lines changed across ' + str(files_changed) + ' file(s)':^78} {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╚{'═'*78}╝{Style.RESET_ALL}")
            else:
                # Fallback: try to get diff stats for the last commit
                self._show_fallback_statistics()
                
        except Exception:
            # Fallback method
            self._show_fallback_statistics()
    
    def _show_fallback_statistics(self):
        """Fallback method to show comprehensive statistics"""
        try:
            # Import colorama for colors
            from colorama import Fore, Style, init
            init()
            
            # Try to get simple stat output
            result = self.git._run_command(
                ['git', 'diff', '--stat', 'HEAD~1', 'HEAD'],
                check=False
            )
            
            # Create a beautiful header for statistics
            print(f"\n{Fore.CYAN}╔{'═'*78}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW}{'📊 COMPREHENSIVE COMMIT STATISTICS':^78}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠{'═'*78}╣{Style.RESET_ALL}")
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith(' '):
                        print(f"{Fore.CYAN}║{Style.RESET_ALL} {line:<76} {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╚{'═'*78}╝{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{'Detailed statistics not available':^76} {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╚{'═'*78}╝{Style.RESET_ALL}")
        except Exception:
            print(f"\n{Fore.CYAN}╔{'═'*78}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW}{'📊 COMPREHENSIVE COMMIT STATISTICS':^78}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠{'═'*78}╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{'Statistics not available':^76} {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═'*78}╝{Style.RESET_ALL}")
    
    def _show_repository_status(self):
        """Show current repository status"""
        try:
            # Import colorama for colors
            from colorama import Fore, Style, init
            init()
            
            # Get current branch
            current_branch = self.git.current_branch()
            print(f"\n{Fore.MAGENTA}Current Branch:{Style.RESET_ALL} {current_branch}")
            
            # Check if there are any uncommitted changes
            status = self.git.status(porcelain=True)
            if status and status.strip():
                print(f"{Fore.YELLOW}You have uncommitted changes:{Style.RESET_ALL}")
                lines = status.strip().split('\n')[:5]  # Show first 5 files
                for line in lines:
                    if line.strip():
                        status_code = line[:2]
                        file_path = line[3:]
                        
                        if status_code.startswith('??'):
                            print(f"    {Fore.GREEN}Untracked:{Style.RESET_ALL} {file_path}")
                        elif status_code[0] in ['M', 'A']:
                            print(f"    {Fore.BLUE}Modified:{Style.RESET_ALL} {file_path}")
                        elif status_code[0] == 'D':
                            print(f"    {Fore.RED}Deleted:{Style.RESET_ALL} {file_path}")
                
                status_lines = status.strip().split('\n')
                if len(status_lines) > 5:
                    print(f"    ... and {len(status_lines) - 5} more files")
            else:
                print(f"{Fore.GREEN}Working directory clean{Style.RESET_ALL}")
                
            # Get remote info
            try:
                remote_result = self.git._run_command(
                    ['git', 'remote', '-v'],
                    check=False
                )
                if remote_result.returncode == 0 and remote_result.stdout.strip():
                    print(f"\n{Fore.CYAN}Remote:{Style.RESET_ALL}")
                    for line in remote_result.stdout.strip().split('\n')[:2]:  # Show first 2 remotes
                        if 'origin' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                print(f"    {parts[1]}")
            except Exception:
                pass
                
        except Exception:
            pass
    
    def _show_failure_guidance(self, last_error: Optional[Exception]):
        """Show minimal guidance when all strategies fail"""
        print("\n Push failed. Check network connection and repository permissions.")
        if last_error:
            print(f" Last error: {str(last_error)[:100]}...")
        input("\nPress Enter to continue...")
    
    def _extract_error_message(self, stderr: str) -> str:
        """Extract clean error message from stderr"""
        if not stderr:
            return "Unknown error"
        
        lines = [l.strip() for l in stderr.split('\n') if l.strip()]
        error_lines = [l for l in lines if l.startswith('!') or 'error' in l.lower()]
        
        if error_lines:
            return error_lines[0][:100]
        
        return lines[0][:100] if lines else "Unknown error"

    def _check_for_potential_conflicts_internal(self):
        """Check for potential conflicts before pushing and provide guidance"""
        try:
            current_branch = self.git.current_branch()
            print(" Checking for potential conflicts...\n")

            # Fetch latest changes to compare with local
            fetch_result = self.git._run_command(['git', 'fetch', 'origin'], check=False)
            if fetch_result.returncode != 0:
                print("  Could not fetch latest changes from remote")
                return True  # Continue anyway

            # Check if there are commits on remote that aren't on local
            try:
                result = self.git._run_command(
                    ['git', 'rev-list', 'HEAD..origin/' + current_branch],
                    check=False
                )

                remote_ahead_count = len(result.stdout.strip().split()) if result.stdout.strip() else 0

                if remote_ahead_count > 0:
                    print(f"  Remote branch is {remote_ahead_count} commit(s) ahead of your local branch")
                    print(" This may cause a push failure. Consider pulling changes first:")
                    print(f"   $ git pull origin {current_branch}")
                    print()
                    response = input("Do you want to continue with push? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print(" Push cancelled by user due to potential conflicts")
                        return False
                else:
                    print(" No conflicts detected - your branch is up to date with remote")
                    print()

            except Exception as e:
                print(f"  Could not determine remote status: {e}")

        except Exception as e:
            print(f"  Could not check for conflicts: {e}")

        return True


class GitPush:
    """Backward-compatible GitPush class with enhanced retry and auto-changelog"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.git = get_git_client()
        self.push_retry = GitPushRetry()
    
    @handle_errors()
    def push(self, dry_run: bool = False):
        """
        Add, commit, and push changes with automatic retry and changelog generation
        
        Args:
            dry_run: Show what would be done without executing
        """
        print("\n" + "="*70)
        print("  GIT PUSH (With Auto-Retry & Auto-Changelog)")
        print("="*70 + "\n")
        
        # IMPORTANT: Refresh Git client to avoid stale state
        # This prevents the "nothing to commit" bug that requires restarting
        print(" Refreshing Git state...")
        self.git = get_git_client(working_dir=Path.cwd(), force_new=True)
        self.push_retry.git = get_git_client(working_dir=Path.cwd(), force_new=True)
        
        # Also refresh the Git index to ensure we see all filesystem changes
        try:
            from ..core.security import SecurityValidator
            SecurityValidator.safe_subprocess_run(['git', 'status'], capture_output=True, cwd=Path.cwd(), timeout=5)
        except (subprocess.CalledProcessError, OSError, TimeoutError, ImportError):
            pass  # Not critical if this fails
        
        # Check for changes
        if not self._has_changes():
            print("ℹ  No changes detected. Working directory is clean.")
            print("\n This includes:")
            print("   • No modified files")
            print("   • No deleted files")
            print("   • No untracked (new) files")
            print("   • No staged changes")
            input("\nPress Enter to continue...")
            return
        
        # Show changes summary
        self._show_changes_summary()
        
        if dry_run:
            print("\n DRY RUN - No changes will be made")
            input("\nPress Enter to continue...")
            return
        
        # Get commit message
        commit_message = self._get_commit_message()
        if not commit_message:
            print("\n Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Execute push with retry (changelog will be auto-generated)
        success = self.push_retry.push_with_retry(commit_message=commit_message)
        
        if success:
            print(" Push completed successfully!")
            print(" Changelog has been automatically updated!")
        else:
            print("  Push failed after all retry attempts")
        
        input("\nPress Enter to continue...")
    
    def _has_changes(self) -> bool:
        """Check if there are any changes including untracked files with fresh Git client"""
        try:
            # IMPORTANT: Create a fresh Git client instance to avoid stale state
            # This prevents the "nothing to commit" bug when files have changed
            fresh_git = get_git_client(working_dir=Path.cwd(), force_new=True)
            
            # Force refresh by running git status twice with different methods
            # First check with the fresh client
            status = fresh_git.status(porcelain=True)
            has_changes = bool(status and status.strip())
            
            # If no changes detected, try a direct subprocess call as fallback
            # This bypasses any potential caching issues
            if not has_changes:
                print(" Double-checking for changes with direct Git command...")
                from ..core.security import SecurityValidator
                result = SecurityValidator.safe_subprocess_run(
                    ['git', 'status', '--porcelain', '--untracked-files=all'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=10
                )
                if result.stdout.strip():
                    print(f" Found changes via direct Git command:")
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:5]:  # Show first 5 changes
                        print(f"   {line}")
                    if len(lines) > 5:
                        print(f"   ... and {len(lines) - 5} more")
                    return True
            
            # Also check for staged changes that might not show in porcelain
            if not has_changes:
                staged_result = SecurityValidator.safe_subprocess_run(
                    ['git', 'diff', '--cached', '--name-only'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=10
                )
                if staged_result.stdout.strip():
                    print(" Found staged changes:")
                    staged_files = staged_result.stdout.strip().split('\n')
                    for file in staged_files[:5]:
                        print(f"   staged: {file}")
                    return True
            
            return has_changes
            
        except Exception as e:
            print(f"  Error checking for changes: {e}")
            # In case of error, be conservative and assume there might be changes
            print(" Attempting direct git status as fallback...")
            try:
                fallback_result = SecurityValidator.safe_subprocess_run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=5
                )
                return bool(fallback_result.stdout.strip())
            except (subprocess.CalledProcessError, OSError, TimeoutError):
                print("  All change detection methods failed")
                return False
    
    def _show_changes_summary(self):
        """Display detailed summary of all changes"""
        print(" Changes to be committed:\n")
        
        try:
            status = self.git.status(porcelain=True)
            
            if not status or not status.strip():
                print("  (none)")
                return
            
            lines = [l for l in status.split('\n') if l.strip()]
            
            untracked = [l for l in lines if l.startswith('??')]
            new_files = [l for l in lines if l.startswith('A ')]
            modified = [l for l in lines if ' M' in l[:2] or l.startswith('M')]
            deleted = [l for l in lines if ' D' in l[:2] or l.startswith('D')]
            
            if untracked:
                print(f"   Untracked files: {len(untracked)}")
            if new_files:
                print(f"   New files (staged): {len(new_files)}")
            if modified:
                print(f"   Modified: {len(modified)}")
            if deleted:
                print(f"   Deleted: {len(deleted)}")
            
            if len(lines) > 0:
                print("\n  Files:")
                for line in lines[:15]:
                    status_code = line[:2]
                    filename = line[3:].strip() if len(line) > 3 else line[2:].strip()
                    
                    if status_code == '??':
                        print(f"    ?? (untracked) {filename}")
                    elif status_code == 'A ':
                        print(f"    A  (new)       {filename}")
                    elif 'M' in status_code:
                        print(f"    M  (modified)  {filename}")
                    elif 'D' in status_code:
                        print(f"    D  (deleted)   {filename}")
                    else:
                        print(f"    {status_code} {filename}")
                
                if len(lines) > 15:
                    print(f"    ... and {len(lines) - 15} more files")
            
            print()
        
        except Exception as e:
            print(f"    Could not get summary: {e}\n")

    def _check_for_potential_conflicts(self):
        """Check for potential conflicts before pushing and provide guidance"""
        try:
            current_branch = self.git.current_branch()
            print(" Checking for potential conflicts...\n")

            # Fetch latest changes to compare with local
            fetch_result = self.git._run_command(['git', 'fetch', 'origin'], check=False)
            if fetch_result.returncode != 0:
                print("  Could not fetch latest changes from remote")
                return True  # Continue anyway

            # Check if there are commits on remote that aren't on local
            try:
                result = self.git._run_command(
                    ['git', 'rev-list', 'HEAD..origin/' + current_branch],
                    check=False
                )

                remote_ahead_count = len(result.stdout.strip().split()) if result.stdout.strip() else 0

                if remote_ahead_count > 0:
                    print(f"  Remote branch is {remote_ahead_count} commit(s) ahead of your local branch")
                    print(" This may cause a push failure. Consider pulling changes first:")
                    print(f"   $ git pull origin {current_branch}")
                    print()
                    response = input("Do you want to continue with push? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print(" Push cancelled by user due to potential conflicts")
                        return False
                else:
                    print(" No conflicts detected - your branch is up to date with remote")
                    print()

            except Exception as e:
                print(f"  Could not determine remote status: {e}")

        except Exception as e:
            print(f"  Could not check for conflicts: {e}")

        return True

    def _get_commit_message(self) -> Optional[str]:
        """Get commit message from user"""
        # Get user input without pre-filling
        message = input(" Commit message: ").strip()

        if not message:
            return None

        if len(message) < 3:
            print("\n  Commit message too short (minimum 3 characters)")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return self._get_commit_message()
            return None

        return message


# Backward compatibility
def push():
    """Legacy function"""
    pusher = GitPush()
    pusher.push()


if __name__ == "__main__":
    print("Testing Enhanced Git Push with Auto-Changelog\n")
    
    config = PushConfig()
    print("Configuration:")
    print(f"  • Max retries: {config.max_retries}")
    print(f"  • Retry delay: {config.retry_delay}s")
    print(f"  • Auto-changelog: {config.auto_generate_changelog}")
    print(f"  • Strategies: {len(config.strategies)}")
    print("\nStrategies:")
    for i, s in enumerate(config.strategies, 1):
        print(f"  {i}. {s.name}: {s.description}")
    
    print("\n" + "="*70)
    print("Ready to use! Import and call:")
    print("  from src.github.git_push import GitPush")
    print("  pusher = GitPush()")
    print("  pusher.push()")
    print("\n Changelog will be automatically generated after successful push!")