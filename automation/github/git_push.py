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

from automation.core.git_client import get_git_client
from automation.core.exceptions import (
    ExceptionHandler,
    GitError,
    GitCommandError,
    UncommittedChangesError,
    handle_errors
)
from automation.core.loading import LoadingSpinner, loading_animation


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
        print("\n" + "="*70)
        print("⬆️  ENHANCED GIT PUSH WITH RETRY")
        print("="*70 + "\n")
        
        # Pre-flight checks
        if not self._pre_push_checks():
            return False
        
        # Get current branch if not specified
        if not branch:
            try:
                branch = self.git.current_branch()
            except Exception as e:
                print(f"❌ Could not determine current branch: {e}")
                return False
        
        # Stage and commit if there are changes
        if commit_message and self._has_changes():
            if not self._stage_and_commit(commit_message):
                return False
        
        # Execute push with progressive strategies
        push_success = self._execute_push_with_strategies(remote, branch)
        
        # Handle results
        if push_success:
            print("✅ Push completed successfully!")
            self._show_push_summary()
            # Generate changelog after successful push
            if self.config.auto_generate_changelog:
                self._auto_generate_changelog()
        else:
            print("❌ Push failed after all retry attempts")
            self._provide_push_failure_guidance()
        
        return push_success
    
    def _auto_generate_changelog(self):
        """Automatically generate changelog for the latest commit"""
        try:
            print("\n" + "="*70)
            print("📝 GENERATING CHANGELOG")
            print("="*70 + "\n")
            
            # Import here to avoid circular dependency
            from automation.changelog_generator import ChangelogGenerator
            
            changelog_gen = ChangelogGenerator()
            
            # Generate changelog for the most recent commit
            print("🔄 Updating changelog with latest commit...")
            success = changelog_gen.generate_changelog(num_commits=1)
            
            if success:
                print(f"✅ Changelog updated successfully!")
                print(f"📄 File: {changelog_gen.CONFIG['changelog_file']}\n")
            else:
                print("ℹ️  Changelog already up to date\n")
        
        except Exception as e:
            print(f"⚠️  Could not generate changelog: {e}")
            print("   (Push was successful, but changelog generation failed)\n")
    
    def _execute_push_with_strategies(self, remote: str, branch: str) -> bool:
        """Try push with progressive strategies until success"""
        print(f"📤 Pushing to {remote}/{branch}")
        print(f"🔄 Max attempts: {len(self.config.strategies)}\n")
        
        last_error = None
        
        for idx, strategy in enumerate(self.config.strategies, 1):
            self.attempt_count = idx
            
            print(f"{'─'*70}")
            print(f"🔹 Attempt {idx}/{len(self.config.strategies)}: {strategy.name}")
            print(f"   Description: {strategy.description}")
            print(f"{'─'*70}\n")
            
            # Check if confirmation needed
            if strategy.requires_confirmation:
                if not self._confirm_destructive_operation(strategy):
                    print("❌ Operation cancelled by user\n")
                    continue
            
            # Try the strategy
            success, error = self._try_push_strategy(strategy, remote, branch)
            
            if success:
                print(f"\n{'='*70}")
                print(f"✅ SUCCESS on attempt {idx} using: {strategy.name}")
                print(f"{'='*70}\n")
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
                print(f"\n⏳ Waiting {wait_time}s before next attempt...")
                time.sleep(wait_time)
                print()
        
        # All strategies failed
        print(f"\n{'='*70}")
        print("❌ PUSH FAILED - All retry strategies exhausted")
        print(f"{'='*70}\n")
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
            
            print(f"   ✅ Push successful!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            
            return True, None
        
        except GitCommandError as e:
            print(f"   ❌ Failed: {self._extract_error_message(e.stderr)}")
            return False, e
        
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
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
            'authentication failed', 'could not authenticate'
        ])
        
        is_network = any(x in error_msg for x in [
            'network', 'timeout', 'connection', 'could not resolve',
            'connection refused', 'connection timed out'
        ])
        
        is_hook_error = any(x in error_msg for x in [
            'pre-push hook', 'hook declined', 'hook failed'
        ])
        
        is_diverged = any(x in error_msg for x in [
            'diverged', 'non-fast-forward', 'rejected'
        ])
        
        is_no_upstream = any(x in error_msg for x in [
            'no upstream', 'no tracking', 'upstream branch'
        ])
        
        print(f"\n   🔍 Error Analysis:")
        
        if is_auth:
            print(f"      • Authentication failure")
            print(f"      → Action: Check credentials")
            return False, 0
        
        if is_network:
            print(f"      • Network/connection issue")
            print(f"      → Next: Retry with backoff")
            wait_time = 0
            if self.config.exponential_backoff:
                wait_time = min(2 ** attempt, 8)
            else:
                wait_time = self.config.retry_delay
            should_continue = attempt < len(self.config.strategies)
            return should_continue, wait_time
        
        if is_hook_error:
            print(f"      • Pre-push hooks blocking push")
            print(f"      → Next: Retry with --no-verify")
        elif is_diverged:
            print(f"      • Remote branch has diverged")
            print(f"      → Next: Force push with confirmation")
        elif is_no_upstream:
            print(f"      • Upstream branch not set")
            print(f"      → Next: Retry with --set-upstream")
        else:
            print(f"      • Unknown error type")
            print(f"      → Next: Try next strategy")
        
        should_continue = attempt < len(self.config.strategies)
        return should_continue, 0
    
    def _confirm_destructive_operation(self, strategy: PushStrategy) -> bool:
        """Get user confirmation for destructive operations"""
        print(f"\n⚠️  WARNING: {strategy.name.upper()} is a destructive operation!")
        print(f"   This will overwrite remote history.")
        print(f"   Description: {strategy.description}\n")
        
        try:
            self._show_divergence_info()
        except Exception:
            pass
        
        print("\n❓ Do you want to proceed?")
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
                print("   📊 Local commits that will overwrite remote:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"      • {line}")
        except Exception:
            pass
    
    def _pre_push_checks(self) -> bool:
        """Run pre-push validation checks"""
        print("🔍 Pre-push validation...\n")
        
        checks = [
            ("Git repository", self.git.is_repo),
            ("Remote configured", lambda: self.git.has_remote('origin')),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: {e}")
                all_passed = False
        
        print()
        
        if not all_passed:
            print("⚠️  Pre-push checks failed\n")
            print("💡 Suggestions:")
            
            if not self.git.is_repo():
                print("   • Initialize Git: magic → Initialize Git & Push to GitHub")
            
            if not self.git.has_remote('origin'):
                print("   • Configure remote: git remote add origin <url>")
            
            print()
            input("Press Enter to continue...")
        
        return all_passed
    
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
        
        # Step 1: Pre-staging diagnostics with auto-fix
        staging_issues = self._diagnose_staging_issues()
        if staging_issues:
            print("🔍 Pre-staging analysis found potential issues:")
            for issue in staging_issues:
                print(f"   ⚠️  {issue}")
            
            # Try to auto-fix critical issues (like lock files)
            if any("lock file" in issue.lower() for issue in staging_issues):
                print("\n🔧 Attempting to auto-fix Git lock file issues...")
                if self._auto_fix_git_issues(staging_issues):
                    print("✅ Auto-fix successful, retrying diagnostics...\n")
                    
                    # Re-run diagnostics to confirm fix
                    new_issues = self._diagnose_staging_issues()
                    if new_issues:
                        print("⚠️  Some issues remain after auto-fix:")
                        for issue in new_issues:
                            print(f"   • {issue}")
                        if any("lock file" in issue.lower() for issue in new_issues):
                            print("\n❌ Lock file issues persist after auto-fix")
                            self._provide_manual_fix_guidance(new_issues)
                            return False
                    else:
                        print("✅ All issues resolved!\n")
                else:
                    print("❌ Auto-fix failed")
                    self._provide_manual_fix_guidance(staging_issues)
                    return False
            print()
        
        # Step 2: Smart staging with fallbacks
        if not self._smart_stage_changes():
            return False
        
        # Step 3: Commit with validation
        return self._smart_commit(message)
    
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
                    except:
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
                    print("   ✅ Fixed Git lock file issues")
                    fixed_any = True
                else:
                    print("   ❌ Failed to fix Git lock file issues")
        
        return fixed_any
    
    def _fix_git_lock_files(self) -> bool:
        """Fix Git lock file issues by safely removing lock files"""
        try:
            git_dir = Path(self.git.working_dir) / '.git'
            lock_files = self._check_git_lock_files(git_dir)
            
            if not lock_files:
                return True  # No lock files to fix
            
            print(f"   🔧 Found {len(lock_files)} lock file(s) to remove:")
            
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
                            print(f"        ✅ Successfully removed {lock_path.name}")
                        else:
                            print(f"        ❌ Failed to remove {lock_path.name}")
                    
                except Exception as e:
                    print(f"      ❌ Error removing {lock_file_path}: {e}")
            
            if removed_count > 0:
                print(f"   ✅ Successfully removed {removed_count} lock file(s)")
                
                # Wait a moment for filesystem to catch up
                import time
                time.sleep(0.5)
                
                # Verify Git operations work now
                try:
                    self.git.status(porcelain=True)
                    print("   ✅ Git operations restored")
                    return True
                except Exception as e:
                    print(f"   ⚠️  Git still has issues after lock removal: {e}")
                    return False
            else:
                print("   ❌ No lock files were successfully removed")
                return False
        
        except Exception as e:
            print(f"   ❌ Error during lock file fix: {e}")
            return False
    
    def _provide_manual_fix_guidance(self, issues: List[str]) -> None:
        """Provide manual fix guidance for remaining issues"""
        print("\n" + "="*60)
        print("🔧 MANUAL FIX REQUIRED")
        print("="*60)
        
        lock_file_issues = [issue for issue in issues if "lock file" in issue.lower()]
        
        if lock_file_issues:
            print("\n🔒 Git Lock File Issues:")
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
            
            print("\n💡 One-liner fix commands:")
            print("   Windows: del \".git\\index.lock\" 2>nul")
            print("   Linux/Mac: rm -f .git/index.lock")
        
        print("\n" + "="*60)
    
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
                print(f"📝 Trying {strategy_name.lower()}...")
                if strategy_func():
                    print(f"✅ {strategy_name} successful\n")
                    return True
                else:
                    print(f"⚠️  {strategy_name} had issues, trying next strategy...\n")
            except Exception as e:
                print(f"❌ {strategy_name} failed: {e}")
                print(f"   Trying next strategy...\n")
        
        print("❌ All staging strategies failed")
        self._provide_staging_guidance()
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
                            print(f"   ⚠️  Skipped problematic file: {file_path}")
                    except:
                        print(f"   ⚠️  Skipped problematic file: {file_path}")
            
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
                print(f"   ✅ Successfully staged {len(successful_files)} files")
                if failed_files:
                    print(f"   ⚠️  Failed to stage {len(failed_files)} files:")
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
                print("⚠️  No staged changes to commit")
                return False
            
            print(f"💾 Creating commit: '{message}'")
            self.git.commit(message)
            print("✅ Commit created\n")
            return True
        
        except Exception as e:
            print(f"❌ Failed to commit: {e}")
            self._provide_commit_guidance()
            return False
    
    def _provide_staging_guidance(self) -> None:
        """Provide guidance when staging fails"""
        print("\n🔧 Staging Troubleshooting Guide:")
        print("   1. Check if you're in a Git repository: git status")
        print("   2. Check for file permission issues")
        print("   3. Look for large files or binary files that might be problematic")
        print("   4. Try staging files individually: git add <filename>")
        print("   5. Check .gitignore for conflicting patterns")
        print("   6. Verify file paths don't contain special characters")
        print()
    
    def _provide_commit_guidance(self) -> None:
        """Provide guidance when commit fails"""
        print("\n🔧 Commit Troubleshooting Guide:")
        print("   1. Ensure you have staged changes: git status")
        print("   2. Check commit message length and characters")
        print("   3. Verify Git user configuration: git config user.name/user.email")
        print("   4. Try with a simpler commit message")
        print()
    
    def _provide_push_failure_guidance(self) -> None:
        """Provide comprehensive guidance when push fails completely"""
        print("\n" + "="*60)
        print("🔧 PUSH FAILURE DIAGNOSTIC & SOLUTIONS")
        print("="*60)
        
        print("\n🔍 Common Push Failure Causes & Solutions:")
        
        print("\n1. 📡 NETWORK/CONNECTIVITY ISSUES:")
        print("   • Check internet connection")
        print("   • Verify remote URL: git remote -v")
        print("   • Test connectivity: git ls-remote origin")
        print("   • Try with different network or VPN")
        
        print("\n2. 🔐 AUTHENTICATION ISSUES:")
        print("   • Check Git credentials: git config --list")
        print("   • Update GitHub token/SSH key")
        print("   • Run: git credential-manager-core erase")
        print("   • Re-authenticate: git push (will prompt)")
        
        print("\n3. 📝 REPOSITORY STATE ISSUES:")
        print("   • Check repo status: git status")
        print("   • View recent commits: git log --oneline -5")
        print("   • Check branch tracking: git branch -vv")
        print("   • Ensure branch exists on remote")
        
        print("\n4. 🔒 PERMISSION ISSUES:")
        print("   • Verify you have push access to the repository")
        print("   • Check if branch is protected")
        print("   • Ensure you're pushing to correct remote/branch")
        
        print("\n5. 📦 REPOSITORY SIZE ISSUES:")
        print("   • Check for large files: git ls-files | xargs ls -la")
        print("   • Use Git LFS for large files")
        print("   • Consider splitting large commits")
        
        print("\n🚀 IMMEDIATE TROUBLESHOOTING STEPS:")
        print("   1. Run: git status (check current state)")
        print("   2. Run: git remote -v (verify remote URL)")
        print("   3. Run: git branch -vv (check branch tracking)")
        print("   4. Run: git push --verbose (detailed push output)")
        print("   5. Try: git push --force-with-lease (if safe)")
        
        print("\n💡 ALTERNATIVE APPROACHES:")
        print("   • Create new branch: git checkout -b new-feature")
        print("   • Reset and retry: git reset --soft HEAD~1")
        print("   • Manual push: git push origin <branch-name>")
        print("   • Use GitHub CLI: gh repo sync")
        
        print("\n" + "="*60)
    
    def _show_push_summary(self):
        """Show summary after successful push"""
        try:
            commits = self.git.log(limit=1)
            if commits:
                commit = commits[0]
                print("📝 Latest commit:")
                print(f"   {commit['short_hash']} - {commit['message']}")
                print(f"   by {commit['author']}")
                print()
        except Exception:
            pass
    
    def _show_failure_guidance(self, last_error: Optional[Exception]):
        """Show guidance when all strategies fail"""
        print("🔧 Manual intervention required\n")
        
        if last_error:
            error_msg = str(last_error).lower()
            
            if 'network' in error_msg or 'timeout' in error_msg:
                print("📡 Network Issues Detected:")
                print("   • Check internet connection")
                print("   • Verify firewall settings")
                print("   • Try: ping github.com")
                print("   • Try later when network is stable\n")
            
            elif 'authentication' in error_msg or 'permission' in error_msg:
                print("🔐 Authentication Issues Detected:")
                print("   • Verify SSH keys: ssh -T git@github.com")
                print("   • Or use HTTPS with token")
                print("   • Check repository permissions\n")
            
            elif 'repository' in error_msg or 'not found' in error_msg:
                print("📁 Repository Issues Detected:")
                print("   • Verify remote URL: git remote -v")
                print("   • Check if repo exists on GitHub")
                print("   • Create repo first if needed\n")
            
            elif 'large' in error_msg or 'size' in error_msg:
                print("📦 Large File Issues Detected:")
                print("   • Consider using Git LFS")
                print("   • Or split into smaller commits")
                print("   • Check .gitignore for large files\n")
        
        print("💡 Fallback Commands:")
        print("   # View full error details")
        print("   $ git push origin HEAD -v\n")
        print("   # Force push (destructive!)")
        print("   $ git push origin HEAD --force\n")
        print("   # Pull and merge first")
        print("   $ git pull origin HEAD --rebase\n")
        
        input("Press Enter to continue...")
    
    def _extract_error_message(self, stderr: str) -> str:
        """Extract clean error message from stderr"""
        if not stderr:
            return "Unknown error"
        
        lines = [l.strip() for l in stderr.split('\n') if l.strip()]
        error_lines = [l for l in lines if l.startswith('!') or 'error' in l.lower()]
        
        if error_lines:
            return error_lines[0][:100]
        
        return lines[0][:100] if lines else "Unknown error"


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
        print("⬆️  GIT PUSH (With Auto-Retry & Auto-Changelog)")
        print("="*70 + "\n")
        
        # IMPORTANT: Refresh Git client to avoid stale state
        # This prevents the "nothing to commit" bug that requires restarting
        print("🔄 Refreshing Git state...")
        self.git = get_git_client(working_dir=Path.cwd(), force_new=True)
        self.push_retry.git = get_git_client(working_dir=Path.cwd(), force_new=True)
        
        # Also refresh the Git index to ensure we see all filesystem changes
        try:
            subprocess.run(['git', 'status'], capture_output=True, cwd=Path.cwd(), timeout=5)
        except:
            pass  # Not critical if this fails
        
        # Check for changes
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            print("\n💡 This includes:")
            print("   • No modified files")
            print("   • No deleted files")
            print("   • No untracked (new) files")
            print("   • No staged changes")
            input("\nPress Enter to continue...")
            return
        
        # Show changes summary
        self._show_changes_summary()
        
        if dry_run:
            print("\n🏃 DRY RUN - No changes will be made")
            input("\nPress Enter to continue...")
            return
        
        # Get commit message
        commit_message = self._get_commit_message()
        if not commit_message:
            print("\n❌ Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Execute push with retry (changelog will be auto-generated)
        success = self.push_retry.push_with_retry(commit_message=commit_message)
        
        if success:
            print("🎉 Push completed successfully!")
            print("📝 Changelog has been automatically updated!")
        else:
            print("⚠️  Push failed after all retry attempts")
        
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
                print("🔄 Double-checking for changes with direct Git command...")
                result = subprocess.run(
                    ['git', 'status', '--porcelain', '--untracked-files=all'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=10
                )
                if result.stdout.strip():
                    print(f"✅ Found changes via direct Git command:")
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:5]:  # Show first 5 changes
                        print(f"   {line}")
                    if len(lines) > 5:
                        print(f"   ... and {len(lines) - 5} more")
                    return True
            
            # Also check for staged changes that might not show in porcelain
            if not has_changes:
                staged_result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=10
                )
                if staged_result.stdout.strip():
                    print("✅ Found staged changes:")
                    staged_files = staged_result.stdout.strip().split('\n')
                    for file in staged_files[:5]:
                        print(f"   staged: {file}")
                    return True
            
            return has_changes
            
        except Exception as e:
            print(f"⚠️  Error checking for changes: {e}")
            # In case of error, be conservative and assume there might be changes
            print("🔄 Attempting direct git status as fallback...")
            try:
                fallback_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    timeout=5
                )
                return bool(fallback_result.stdout.strip())
            except:
                print("⚠️  All change detection methods failed")
                return False
    
    def _show_changes_summary(self):
        """Display detailed summary of all changes"""
        print("📊 Changes to be committed:\n")
        
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
                print(f"  📄 Untracked files: {len(untracked)}")
            if new_files:
                print(f"  ➕ New files (staged): {len(new_files)}")
            if modified:
                print(f"  📝 Modified: {len(modified)}")
            if deleted:
                print(f"  ➖ Deleted: {len(deleted)}")
            
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
            print(f"  ⚠️  Could not get summary: {e}\n")
    
    def _get_commit_message(self) -> Optional[str]:
        """Get commit message from user with automatic heart emoji prefix"""
        message = input("💭 Commit message: ").strip()
        
        if not message:
            return None
        
        if len(message) < 3:
            print("\n⚠️  Commit message too short (minimum 3 characters)")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return self._get_commit_message()
            return None
        
        # Always add heart emoji at the beginning if not already present
        if not message.startswith("❤️"):
            message = f"❤️ {message}"
        
        return message


# Backward compatibility
def push():
    """Legacy function"""
    pusher = GitPush()
    pusher.push()


if __name__ == "__main__":
    print("🧪 Testing Enhanced Git Push with Auto-Changelog\n")
    
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
    print("  from automation.github.git_push import GitPush")
    print("  pusher = GitPush()")
    print("  pusher.push()")
    print("\n✨ Changelog will be automatically generated after successful push!")