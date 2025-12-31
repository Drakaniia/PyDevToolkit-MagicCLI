"""
Git Branch Module
Handles all branch-related operations including create, switch, rename, delete, list, sync, merge
"""
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from core.utils.git_client import get_git_client
from core.utils.config import get_operational_config
from core.loading import LoadingSpinner

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


class GitBranch:
    """Handles all git branch operations"""

    def __init__(self):
        self.git = get_git_client()
        self.current_dir = Path.cwd()

    def _run_command(self, command: List[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
        """Run git command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                cwd=self.current_dir,
                capture_output=capture,
                text=True,
                check=check,
                encoding='utf-8',
                errors='replace'
            )
            return result
        except subprocess.CalledProcessError as e:
            if capture:
                return e
            raise
        except (FileNotFoundError, OSError) as e:
            print(f"Git command error: {e}")
            raise subprocess.CalledProcessError(1, command, stderr=str(e))

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = self._run_command(['git', 'rev-parse', '--is-inside-work-tree'], check=False)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False

    def _get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            result = self._run_command(['git', 'branch', '--show-current'], check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            pass
        return ""

    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = self._run_command(['git', 'status', '--porcelain'], check=False)
            if result.returncode == 0:
                return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            pass
        return False

    def _print_header(self, title: str) -> None:
        """Print formatted header"""
        print("\n" + "=" * 70)
        if HAS_COLORAMA:
            print(f"{Fore.CYAN}{Style.BRIGHT} {title} {Style.RESET_ALL}")
        else:
            print(f" {title} ")
        print("=" * 70 + "\n")

    def _print_success(self, message: str) -> None:
        """Print success message"""
        if HAS_COLORAMA:
            print(f"{Fore.GREEN} {message} {Style.RESET_ALL}")
        else:
            print(f" {message} ")

    def _print_error(self, message: str) -> None:
        """Print error message"""
        if HAS_COLORAMA:
            print(f"{Fore.RED} {message} {Style.RESET_ALL}")
        else:
            print(f" {message} ")

    def _print_warning(self, message: str) -> None:
        """Print warning message"""
        if HAS_COLORAMA:
            print(f"{Fore.YELLOW} {message} {Style.RESET_ALL}")
        else:
            print(f" {message} ")

    def _print_info(self, message: str) -> None:
        """Print info message"""
        if HAS_COLORAMA:
            print(f"{Fore.CYAN} {message} {Style.RESET_ALL}")
        else:
            print(f" {message} ")

    def validate_branch_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate branch name according to Git rules

        Args:
            name: Branch name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Branch name cannot be empty"

        name = name.strip()

        # Check for forbidden characters
        forbidden_chars = [' ', '~', '^', ':', '\\', '*', '?', '[', '..']
        for char in forbidden_chars:
            if char in name:
                return False, f"Branch name cannot contain '{char}'"

        # Check for starting/ending with dot
        if name.startswith('.') or name.endswith('.'):
            return False, "Branch name cannot start or end with a dot"

        # Check for consecutive dots
        if '..' in name:
            return False, "Branch name cannot contain consecutive dots"

        # Check for reserved names
        reserved_names = ['HEAD', 'FETCH_HEAD', 'ORIG_HEAD', 'MERGE_HEAD']
        if name.upper() in reserved_names:
            return False, f"'{name}' is a reserved name"

        # Check for lock file extension
        if name.endswith('.lock'):
            return False, "Branch name cannot end with '.lock'"

        return True, ""

    def get_all_branches(self, include_remote: bool = True) -> List[Dict[str, str]]:
        """
        Get all branches with metadata

        Args:
            include_remote: Whether to include remote branches

        Returns:
            List of branch dictionaries with name, type, commit, message, date
        """
        branches = []

        try:
            # Get current branch
            current_branch = self._get_current_branch()

            # Get local branches
            result = self._run_command(['git', 'branch', '-v', '--no-color'], check=False)
            if result.returncode == 0:
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
                result = self._run_command(['git', 'branch', '-r', '-v', '--no-color'], check=False)
                if result.returncode == 0:
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

        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError) as e:
            self._print_error(f"Error getting branches: {e}")

        return branches

    def create_branch(self, branch_name: str, checkout: bool = True, start_point: str = "") -> bool:
        """
        Create a new branch

        Args:
            branch_name: Name of the new branch
            checkout: Whether to switch to the new branch
            start_point: Starting point (commit hash or branch name)

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        # Validate branch name
        is_valid, error_msg = self.validate_branch_name(branch_name)
        if not is_valid:
            self._print_error(f"Invalid branch name: {error_msg}")
            input("\nPress Enter to continue...")
            return False

        # Check if branch already exists
        try:
            result = self._run_command(['git', 'branch', '--list', branch_name], check=False)
            if result.returncode == 0 and result.stdout.strip():
                self._print_error(f"Branch '{branch_name}' already exists.")
                input("\nPress Enter to continue...")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
            pass

        self._print_header("CREATE NEW BRANCH")
        print(f"Branch name: {branch_name}")
        print(f"Checkout after creation: {'Yes' if checkout else 'No'}")
        if start_point:
            print(f"Start point: {start_point}")
        print()

        try:
            # Create the branch
            cmd = ['git', 'branch']
            if start_point:
                cmd.extend([branch_name, start_point])
            else:
                cmd.append(branch_name)

            result = self._run_command(cmd, check=True)

            if result.returncode == 0:
                self._print_success(f"Branch '{branch_name}' created successfully!")

                # Checkout if requested
                if checkout:
                    result = self._run_command(['git', 'checkout', branch_name], check=True)
                    if result.returncode == 0:
                        self._print_success(f"Switched to branch '{branch_name}'")
                    else:
                        self._print_error("Failed to switch to new branch")
                        input("\nPress Enter to continue...")
                        return False

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error("Failed to create branch")
                if result.stderr:
                    print(result.stderr)
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error creating branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def switch_branch(self, branch_name: Optional[str] = None) -> bool:
        """
        Switch to a branch

        Args:
            branch_name: Name of branch to switch to (None for interactive selection)

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        current_branch = self._get_current_branch()

        # Handle uncommitted changes
        if self._has_uncommitted_changes():
            self._print_warning("You have uncommitted changes!")
            print("\nOptions:")
            print("  1. Stash changes")
            print("  2. Commit changes")
            print("  3. Discard changes")
            print("  4. Cancel operation")

            choice = input("\nSelect option (1-4): ").strip()

            if choice == '1':
                # Stash changes
                result = self._run_command(['git', 'stash', 'push', '-m', 'Auto-stash before branch switch'], check=True)
                if result.returncode != 0:
                    self._print_error("Failed to stash changes")
                    input("\nPress Enter to continue...")
                    return False
                self._print_success("Changes stashed successfully")
            elif choice == '2':
                # Commit changes
                message = input("Enter commit message: ").strip()
                if not message:
                    self._print_error("Commit message cannot be empty")
                    input("\nPress Enter to continue...")
                    return False

                result = self._run_command(['git', 'add', '.'], check=True)
                if result.returncode != 0:
                    self._print_error("Failed to stage changes")
                    input("\nPress Enter to continue...")
                    return False

                result = self._run_command(['git', 'commit', '-m', message], check=True)
                if result.returncode != 0:
                    self._print_error("Failed to commit changes")
                    input("\nPress Enter to continue...")
                    return False
                self._print_success("Changes committed successfully")
            elif choice == '3':
                # Discard changes
                self._print_warning("This will discard ALL uncommitted changes!")
                confirm = input("Are you sure? (type 'yes' to confirm): ").strip().lower()
                if confirm != 'yes':
                    print("Operation cancelled")
                    input("\nPress Enter to continue...")
                    return False

                result = self._run_command(['git', 'reset', '--hard', 'HEAD'], check=True)
                if result.returncode != 0:
                    self._print_error("Failed to discard changes")
                    input("\nPress Enter to continue...")
                    return False
                self._print_success("Changes discarded successfully")
            else:
                print("Operation cancelled")
                input("\nPress Enter to continue...")
                return False

        # If no branch name provided, show interactive selection
        if not branch_name:
            return self._select_branch_interactive()

        # Switch to specified branch
        self._print_header("SWITCH BRANCH")
        print(f"Current branch: {current_branch}")
        print(f"Switching to: {branch_name}")
        print()

        try:
            result = self._run_command(['git', 'checkout', branch_name], check=True)

            if result.returncode == 0:
                self._print_success(f"Switched to branch '{branch_name}'")
                
                # Auto-pull if configured
                self._auto_pull_branch(branch_name)
                
                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error(f"Failed to switch to branch '{branch_name}'")
                if result.stderr:
                    print(result.stderr)
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error switching branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def _auto_pull_branch(self, branch_name: str) -> bool:
        """
        Automatically pull from remote after switching branch if configured

        Args:
            branch_name: Name of the branch to pull

        Returns:
            True if successful or disabled, False otherwise
        """
        config = get_operational_config()
        
        # Check if auto-pull is enabled
        if not config.auto_pull_on_branch_switch:
            return True
        
        # Check if branch has remote tracking
        try:
            result = self._run_command(['git', 'branch', '-vv', '--list', branch_name], check=False)
            if result.returncode == 0 and result.stdout:
                # Check if branch has tracking info (indicated by [origin/branch_name])
                if '[' not in result.stdout:
                    # No remote tracking, skip pull
                    return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return True
        
        # Auto-pull from remote
        self._print_info(f"Auto-pulling branch '{branch_name}' from remote...")
        
        try:
            with LoadingSpinner("Pulling", style='dots'):
                result = self._run_command(['git', 'pull', 'origin', branch_name], check=False)
            
            if result.returncode == 0:
                self._print_success(f"Branch '{branch_name}' synced with remote")
                return True
            else:
                self._print_warning(f"Auto-pull failed: {result.stderr}")
                return True  # Don't fail the switch operation if pull fails
        except Exception as e:
            self._print_warning(f"Auto-pull error: {e}")
            return True  # Don't fail the switch operation if pull fails

    def _select_branch_interactive(self) -> bool:
        """Interactive branch selection with numbered list"""
        self._print_header("SELECT BRANCH TO SWITCH")

        # Fetch remote branches first
        self._print_info("Fetching remote branches...")
        result = self._run_command(['git', 'fetch', '--all'], check=False)
        if result.returncode == 0:
            self._print_success("Remote branches fetched")
        else:
            self._print_warning("Could not fetch remote branches, using local only")

        # Get all branches
        branches = self.get_all_branches(include_remote=True)

        if not branches:
            self._print_error("No branches found")
            input("\nPress Enter to continue...")
            return False

        # Separate local and remote
        local_branches = [b for b in branches if b['type'] == 'local']
        remote_branches = [b for b in branches if b['type'] == 'remote']

        # Display local branches
        current_branch = self._get_current_branch()
        print("\n--- Local Branches ---")
        for idx, branch in enumerate(local_branches, 1):
            marker = "*" if branch['is_current'] else " "
            prefix = f"{Fore.GREEN}*{Style.RESET_ALL}" if HAS_COLORAMA and branch['is_current'] else "*"
            print(f"  {idx}. {prefix} {branch['name']}")
            if branch['message']:
                print(f"     {branch['message']}")

        # Display remote branches
        if remote_branches:
            print("\n--- Remote Branches ---")
            for idx, branch in enumerate(remote_branches, len(local_branches) + 1):
                print(f"  {idx}.   {branch['name']}")
                if branch['message']:
                    print(f"     {branch['message']}")

        print(f"\n  {len(branches) + 1}. Cancel")

        # Get user selection
        choice = input(f"\nSelect branch (1-{len(branches) + 1}): ").strip()

        try:
            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(branches) + 1:
                self._print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return False

            if choice_idx == len(branches) + 1:
                print("Operation cancelled")
                input("\nPress Enter to continue...")
                return False

            selected_branch = branches[choice_idx - 1]

            # If remote branch, create local tracking branch
            if selected_branch['type'] == 'remote':
                local_name = selected_branch['name'].split('/')[-1]
                self._print_info(f"Creating local branch '{local_name}' to track '{selected_branch['name']}'")

                result = self._run_command(['git', 'checkout', '-b', local_name, selected_branch['name']], check=True)
                if result.returncode == 0:
                    self._print_success(f"Switched to new branch '{local_name}' tracking '{selected_branch['name']}'")
                    
                    # Auto-pull if configured
                    self._auto_pull_branch(local_name)
                    
                    input("\nPress Enter to continue...")
                    return True
                else:
                    self._print_error("Failed to create tracking branch")
                    input("\nPress Enter to continue...")
                    return False
            else:
                # Switch to local branch
                result = self._run_command(['git', 'checkout', selected_branch['name']], check=True)
                if result.returncode == 0:
                    self._print_success(f"Switched to branch '{selected_branch['name']}'")
                    
                    # Auto-pull if configured
                    self._auto_pull_branch(selected_branch['name'])
                    
                    input("\nPress Enter to continue...")
                    return True
                else:
                    self._print_error("Failed to switch branch")
                    input("\nPress Enter to continue...")
                    return False

        except ValueError:
            self._print_error("Invalid input")
            input("\nPress Enter to continue...")
            return False

    def rename_branch(self, old_name: Optional[str] = None, new_name: Optional[str] = None) -> bool:
        """
        Rename a branch

        Args:
            old_name: Old branch name (None for current branch)
            new_name: New branch name (None for interactive input)

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("RENAME BRANCH")

        # Get old branch name
        if not old_name:
            old_name = self._get_current_branch()
            if not old_name:
                self._print_error("Could not determine current branch")
                input("\nPress Enter to continue...")
                return False
            print(f"Current branch: {old_name}")
            confirm = input("Rename current branch? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Operation cancelled")
                input("\nPress Enter to continue...")
                return False
        else:
            print(f"Branch to rename: {old_name}")

        # Get new branch name
        if not new_name:
            new_name = input("Enter new branch name: ").strip()

        # Validate new branch name
        is_valid, error_msg = self.validate_branch_name(new_name)
        if not is_valid:
            self._print_error(f"Invalid branch name: {error_msg}")
            input("\nPress Enter to continue...")
            return False

        # Check if new name already exists
        try:
            result = self._run_command(['git', 'branch', '--list', new_name], check=False)
            if result.returncode == 0 and result.stdout.strip():
                self._print_error(f"Branch '{new_name}' already exists.")
                input("\nPress Enter to continue...")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
            pass

        print(f"\nRenaming '{old_name}' to '{new_name}'...")

        try:
            # Rename the branch
            result = self._run_command(['git', 'branch', '-m', old_name, new_name], check=True)

            if result.returncode == 0:
                self._print_success(f"Branch renamed successfully from '{old_name}' to '{new_name}'")

                # Check if branch was pushed to remote
                try:
                    result = self._run_command(['git', 'branch', '-r', '--list', f'origin/{old_name}'], check=False)
                    if result.returncode == 0 and result.stdout.strip():
                        self._print_warning(f"Branch '{old_name}' exists on remote 'origin'")
                        print("\nTo update remote, run:")
                        print(f"  git push origin :{old_name}")
                        print(f"  git push origin {new_name}")
                except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
                    pass

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error("Failed to rename branch")
                if result.stderr:
                    print(result.stderr)
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error renaming branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def delete_branch(self, branch_name: Optional[str] = None, force: bool = False) -> bool:
        """
        Delete a branch

        Args:
            branch_name: Branch name to delete (None for interactive selection)
            force: Force delete even if unmerged

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("DELETE BRANCH")

        # Get branch name if not provided
        if not branch_name:
            branches = self.get_all_branches(include_remote=False)
            if not branches:
                self._print_error("No local branches found")
                input("\nPress Enter to continue...")
                return False

            current_branch = self._get_current_branch()

            print("\nSelect branch to delete:")
            for idx, branch in enumerate(branches, 1):
                marker = "*" if branch['is_current'] else " "
                current_marker = f"{Fore.GREEN}*{Style.RESET_ALL}" if HAS_COLORAMA and branch['is_current'] else "*"
                print(f"  {idx}. {current_marker} {branch['name']}")
                if branch['message']:
                    print(f"     {branch['message']}")

            print(f"  {len(branches) + 1}. Cancel")

            choice = input(f"\nSelect branch (1-{len(branches) + 1}): ").strip()

            try:
                choice_idx = int(choice)
                if choice_idx < 1 or choice_idx > len(branches) + 1:
                    self._print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return False

                if choice_idx == len(branches) + 1:
                    print("Operation cancelled")
                    input("\nPress Enter to continue...")
                    return False

                selected_branch = branches[choice_idx - 1]
                branch_name = selected_branch['name']

                # Check if trying to delete current branch
                if selected_branch['is_current']:
                    self._print_error("Cannot delete the current branch. Switch to another branch first.")
                    input("\nPress Enter to continue...")
                    return False

            except ValueError:
                self._print_error("Invalid input")
                input("\nPress Enter to continue...")
                return False

        # Confirm deletion
        self._print_warning(f"WARNING: This will delete branch '{branch_name}'!")
        if not force:
            print("This operation cannot be undone.")
        else:
            print("This is a FORCE DELETE - even unmerged commits will be lost!")

        confirm = input(f"\nType '{branch_name}' to confirm deletion: ").strip()

        if confirm != branch_name:
            print("Operation cancelled")
            input("\nPress Enter to continue...")
            return False

        # Ask about remote deletion
        delete_remote = False
        try:
            result = self._run_command(['git', 'branch', '-r', '--list', f'origin/{branch_name}'], check=False)
            if result.returncode == 0 and result.stdout.strip():
                remote_choice = input(f"\nBranch '{branch_name}' exists on remote. Delete from remote too? (y/n): ").strip().lower()
                if remote_choice == 'y':
                    delete_remote = True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
            pass

        try:
            # Delete local branch
            cmd = ['git', 'branch', '-d']
            if force:
                cmd = ['git', 'branch', '-D']
            cmd.append(branch_name)

            result = self._run_command(cmd, check=False)

            if result.returncode == 0:
                self._print_success(f"Branch '{branch_name}' deleted successfully")

                # Delete from remote if requested
                if delete_remote:
                    self._print_info(f"Deleting '{branch_name}' from remote...")
                    result = self._run_command(['git', 'push', 'origin', f':{branch_name}'], check=False)
                    if result.returncode == 0:
                        self._print_success(f"Branch '{branch_name}' deleted from remote")
                    else:
                        self._print_warning(f"Failed to delete branch from remote. You may need to run: git push origin :{branch_name}")

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error(f"Failed to delete branch '{branch_name}'")
                if result.stderr:
                    print(result.stderr)
                    if "not fully merged" in result.stderr:
                        print("\nHint: Use force delete (-D) to delete unmerged branches")
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error deleting branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def list_branches(self, include_remote: bool = True) -> None:
        """
        List all branches with details

        Args:
            include_remote: Whether to include remote branches
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        self._print_header("LIST ALL BRANCHES")

        # Fetch remote branches
        if include_remote:
            self._print_info("Fetching remote branches...")
            result = self._run_command(['git', 'fetch', '--all'], check=False)
            if result.returncode == 0:
                self._print_success("Remote branches fetched")
            else:
                self._print_warning("Could not fetch remote branches")

        # Get branches
        branches = self.get_all_branches(include_remote=include_remote)

        if not branches:
            self._print_error("No branches found")
            input("\nPress Enter to continue...")
            return

        # Separate local and remote
        local_branches = [b for b in branches if b['type'] == 'local']
        remote_branches = [b for b in branches if b['type'] == 'remote']

        # Display local branches
        print("\n--- Local Branches ---")
        for branch in local_branches:
            if HAS_COLORAMA:
                if branch['is_current']:
                    print(f"  {Fore.GREEN}*{Style.RESET_ALL} {Fore.CYAN}{branch['name']}{Style.RESET_ALL}")
                else:
                    print(f"    {Fore.CYAN}{branch['name']}{Style.RESET_ALL}")
            else:
                marker = "*" if branch['is_current'] else " "
                print(f"  {marker} {branch['name']}")

            if branch['commit']:
                print(f"    Commit: {branch['commit']}")
            if branch['message']:
                print(f"    {branch['message']}")

            # Show tracking info
            try:
                result = self._run_command(['git', 'branch', '-vv', '--list', branch['name']], check=False)
                if result.returncode == 0 and result.stdout:
                    line = result.stdout.strip()
                    if '[' in line:
                        tracking = line.split('[')[1].split(']')[0]
                        print(f"    Tracking: {tracking}")
            except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
                pass

        # Display remote branches
        if remote_branches:
            print("\n--- Remote Branches ---")
            for branch in remote_branches:
                if HAS_COLORAMA:
                    print(f"    {Fore.YELLOW}{branch['name']}{Style.RESET_ALL}")
                else:
                    print(f"    {branch['name']}")

                if branch['commit']:
                    print(f"    Commit: {branch['commit']}")
                if branch['message']:
                    print(f"    {branch['message']}")

        input("\nPress Enter to continue...")

    def sync_branch(self, branch_name: Optional[str] = None, strategy: str = 'merge') -> bool:
        """
        Sync branch with remote

        Args:
            branch_name: Branch name to sync (None for current branch)
            strategy: Sync strategy ('merge', 'rebase', 'pull')

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("SYNC BRANCH WITH REMOTE")

        # Get branch name
        if not branch_name:
            branch_name = self._get_current_branch()
            if not branch_name:
                self._print_error("Could not determine current branch")
                input("\nPress Enter to continue...")
                return False

        print(f"Branch: {branch_name}")
        print(f"Strategy: {strategy}")
        print()

        try:
            # Fetch from remote
            self._print_info("Fetching from remote...")
            with LoadingSpinner("Fetching", style='dots'):
                result = self._run_command(['git', 'fetch', 'origin'], check=True)

            if result.returncode != 0:
                self._print_error("Failed to fetch from remote")
                input("\nPress Enter to continue...")
                return False

            self._print_success("Fetch completed")

            # Check if branch exists on remote
            result = self._run_command(['git', 'branch', '-r', '--list', f'origin/{branch_name}'], check=False)
            remote_exists = result.returncode == 0 and result.stdout.strip()

            if not remote_exists:
                # Branch doesn't exist on remote, push it
                self._print_info(f"Branch '{branch_name}' does not exist on remote")
                print("Pushing branch to remote...")

                with LoadingSpinner("Pushing", style='dots'):
                    result = self._run_command(['git', 'push', '-u', 'origin', branch_name], check=True)

                if result.returncode == 0:
                    self._print_success(f"Branch '{branch_name}' pushed to remote successfully")
                    input("\nPress Enter to continue...")
                    return True
                else:
                    self._print_error("Failed to push branch to remote")
                    if result.stderr:
                        print(result.stderr)
                    input("\nPress Enter to continue...")
                    return False

            # Branch exists on remote, sync it
            self._print_info(f"Syncing '{branch_name}' with remote...")

            if strategy == 'merge':
                with LoadingSpinner("Pulling with merge", style='dots'):
                    result = self._run_command(['git', 'pull', 'origin', branch_name], check=True)
            elif strategy == 'rebase':
                with LoadingSpinner("Pulling with rebase", style='dots'):
                    result = self._run_command(['git', 'pull', '--rebase', 'origin', branch_name], check=True)
            else:  # pull
                with LoadingSpinner("Pulling", style='dots'):
                    result = self._run_command(['git', 'pull', 'origin', branch_name], check=True)

            if result.returncode == 0:
                self._print_success(f"Branch '{branch_name}' synced successfully")

                # Check for ahead/behind status
                try:
                    result = self._run_command(['git', 'rev-list', '--left-right', '--count', f'origin/{branch_name}...{branch_name}'], check=False)
                    if result.returncode == 0 and result.stdout.strip():
                        left, right = result.stdout.strip().split()
                        if left == '0' and right == '0':
                            print("  Branch is up to date with remote")
                        elif left != '0' and right != '0':
                            print(f"  Branch has diverged: {left} behind, {right} ahead")
                        elif left != '0':
                            print(f"  Branch is {left} commits behind remote")
                        else:
                            print(f"  Branch is {right} commits ahead of remote")
                except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
                    pass

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error("Failed to sync branch")
                if result.stderr:
                    print(result.stderr)
                    if "CONFLICT" in result.stderr:
                        print("\nMerge conflicts detected! Please resolve conflicts and complete the merge.")
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error syncing branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def create_from_commit(self) -> bool:
        """
        Create a new branch from a specific commit

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("CREATE BRANCH FROM COMMIT")

        # Get branch name
        branch_name = input("Enter new branch name: ").strip()

        # Validate branch name
        is_valid, error_msg = self.validate_branch_name(branch_name)
        if not is_valid:
            self._print_error(f"Invalid branch name: {error_msg}")
            input("\nPress Enter to continue...")
            return False

        # Get commit history
        self._print_info("Fetching commit history...")
        try:
            result = self._run_command(['git', 'log', '--oneline', '-20'], check=True)
            if result.returncode != 0:
                self._print_error("Failed to get commit history")
                input("\nPress Enter to continue...")
                return False

            commits = result.stdout.strip().split('\n')

            print("\nRecent commits:")
            for idx, commit in enumerate(commits, 1):
                print(f"  {idx}. {commit}")

            print(f"  {len(commits) + 1}. Cancel")

            choice = input(f"\nSelect commit (1-{len(commits) + 1}): ").strip()

            try:
                choice_idx = int(choice)
                if choice_idx < 1 or choice_idx > len(commits) + 1:
                    self._print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return False

                if choice_idx == len(commits) + 1:
                    print("Operation cancelled")
                    input("\nPress Enter to continue...")
                    return False

                selected_commit = commits[choice_idx - 1].split()[0]

            except ValueError:
                self._print_error("Invalid input")
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error getting commit history: {e}")
            input("\nPress Enter to continue...")
            return False

        # Create branch from commit
        print(f"\nCreating branch '{branch_name}' from commit {selected_commit}...")

        try:
            result = self._run_command(['git', 'branch', branch_name, selected_commit], check=True)

            if result.returncode == 0:
                self._print_success(f"Branch '{branch_name}' created from commit {selected_commit}")

                # Ask if user wants to switch to new branch
                switch = input("\nSwitch to new branch? (y/n): ").strip().lower()
                if switch == 'y':
                    result = self._run_command(['git', 'checkout', branch_name], check=True)
                    if result.returncode == 0:
                        self._print_success(f"Switched to branch '{branch_name}'")

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error("Failed to create branch")
                if result.stderr:
                    print(result.stderr)
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error creating branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def compare_branches(self) -> None:
        """Compare two branches"""
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        self._print_header("COMPARE BRANCHES")

        current_branch = self._get_current_branch()
        branches = self.get_all_branches(include_remote=False)

        if not branches or len(branches) < 2:
            self._print_error("Need at least 2 branches to compare")
            input("\nPress Enter to continue...")
            return

        # Select first branch
        print("\nSelect first branch:")
        for idx, branch in enumerate(branches, 1):
            marker = "*" if branch['is_current'] else " "
            current_marker = f"{Fore.GREEN}*{Style.RESET_ALL}" if HAS_COLORAMA and branch['is_current'] else "*"
            print(f"  {idx}. {current_marker} {branch['name']}")

        choice1 = input(f"\nSelect first branch (1-{len(branches)}): ").strip()

        try:
            idx1 = int(choice1)
            if idx1 < 1 or idx1 > len(branches):
                self._print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return
            branch1 = branches[idx1 - 1]['name']
        except ValueError:
            self._print_error("Invalid input")
            input("\nPress Enter to continue...")
            return

        # Select second branch
        print("\nSelect second branch:")
        for idx, branch in enumerate(branches, 1):
            if branch['name'] != branch1:
                marker = "*" if branch['is_current'] else " "
                current_marker = f"{Fore.GREEN}*{Style.RESET_ALL}" if HAS_COLORAMA and branch['is_current'] else "*"
                print(f"  {idx}. {current_marker} {branch['name']}")

        choice2 = input(f"\nSelect second branch: ").strip()

        try:
            idx2 = int(choice2)
            if idx2 < 1 or idx2 > len(branches) or branches[idx2 - 1]['name'] == branch1:
                self._print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return
            branch2 = branches[idx2 - 1]['name']
        except ValueError:
            self._print_error("Invalid input")
            input("\nPress Enter to continue...")
            return

        # Compare branches
        print(f"\nComparing '{branch1}' and '{branch2}'...\n")

        try:
            # Get ahead/behind counts
            result = self._run_command(['git', 'rev-list', '--left-right', '--count', f'{branch1}...{branch2}'], check=False)
            if result.returncode == 0 and result.stdout.strip():
                left, right = result.stdout.strip().split()
                print(f"  {branch2} is {left} commit(s) ahead of {branch1}")
                print(f"  {branch1} is {right} commit(s) ahead of {branch2}")

            # Get commit diff summary
            result = self._run_command(['git', 'log', '--oneline', f'{branch1}..{branch2}'], check=False)
            if result.returncode == 0 and result.stdout.strip():
                print(f"\n  Commits in {branch2} but not in {branch1}:")
                for commit in result.stdout.strip().split('\n')[:10]:
                    print(f"    {commit}")
                total = len(result.stdout.strip().split('\n'))
                if total > 10:
                    print(f"    ... and {total - 10} more")

            result = self._run_command(['git', 'log', '--oneline', f'{branch2}..{branch1}'], check=False)
            if result.returncode == 0 and result.stdout.strip():
                print(f"\n  Commits in {branch1} but not in {branch2}:")
                for commit in result.stdout.strip().split('\n')[:10]:
                    print(f"    {commit}")
                total = len(result.stdout.strip().split('\n'))
                if total > 10:
                    print(f"    ... and {total - 10} more")

            # Ask if user wants to see full diff
            show_diff = input("\nShow full diff? (y/n): ").strip().lower()
            if show_diff == 'y':
                print(f"\nDiff between {branch1} and {branch2}:")
                result = self._run_command(['git', 'diff', f'{branch1}...{branch2}'], check=False)
                if result.returncode == 0:
                    # Show first 50 lines of diff
                    lines = result.stdout.split('\n')
                    for line in lines[:50]:
                        print(line)
                    if len(lines) > 50:
                        print(f"\n... ({len(lines) - 50} more lines)")
                else:
                    self._print_error("Failed to get diff")

        except Exception as e:
            self._print_error(f"Error comparing branches: {e}")

        input("\nPress Enter to continue...")

    def merge_branch(self) -> bool:
        """
        Merge a branch into current branch

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("MERGE BRANCH")

        current_branch = self._get_current_branch()
        print(f"Current branch: {current_branch}")

        # Get branches
        branches = self.get_all_branches(include_remote=False)
        if not branches:
            self._print_error("No branches found")
            input("\nPress Enter to continue...")
            return False

        # Filter out current branch
        other_branches = [b for b in branches if not b['is_current']]

        if not other_branches:
            self._print_error("No other branches to merge")
            input("\nPress Enter to continue...")
            return False

        # Select branch to merge
        print("\nSelect branch to merge:")
        for idx, branch in enumerate(other_branches, 1):
            print(f"  {idx}. {branch['name']}")
            if branch['message']:
                print(f"     {branch['message']}")

        print(f"  {len(other_branches) + 1}. Cancel")

        choice = input(f"\nSelect branch (1-{len(other_branches) + 1}): ").strip()

        try:
            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(other_branches) + 1:
                self._print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return False

            if choice_idx == len(other_branches) + 1:
                print("Operation cancelled")
                input("\nPress Enter to continue...")
                return False

            source_branch = other_branches[choice_idx - 1]['name']

        except ValueError:
            self._print_error("Invalid input")
            input("\nPress Enter to continue...")
            return False

        # Confirm merge
        print(f"\nMerging '{source_branch}' into '{current_branch}'...")

        # Ask for merge strategy
        self._print_info("Merge options:")
        print("  1. Fast-forward merge (if possible)")
        print("  2. Always create merge commit (--no-ff)")
        print("  3. Squash merge (--squash)")

        strategy_choice = input("\nSelect strategy (1-3, default 1): ").strip() or '1'

        try:
            cmd = ['git', 'merge']
            if strategy_choice == '2':
                cmd.append('--no-ff')
            elif strategy_choice == '3':
                cmd.append('--squash')
            cmd.append(source_branch)

            with LoadingSpinner(f"Merging {source_branch}", style='dots'):
                result = self._run_command(cmd, check=True)

            if result.returncode == 0:
                self._print_success(f"Branch '{source_branch}' merged successfully into '{current_branch}'")

                # Show merge result
                if result.stdout:
                    print(result.stdout)

                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error(f"Failed to merge branch '{source_branch}'")
                if result.stderr:
                    print(result.stderr)
                    if "CONFLICT" in result.stderr:
                        print("\nMerge conflicts detected!")
                        print("Please resolve conflicts manually:")
                        print("  1. Edit conflicted files")
                        print("  2. Stage resolved files: git add <file>")
                        print("  3. Complete merge: git commit")
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error merging branch: {e}")
            input("\nPress Enter to continue...")
            return False

    def set_upstream(self) -> bool:
        """
        Set upstream tracking for current branch

        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            self._print_error("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        self._print_header("SET UPSTREAM TRACKING")

        current_branch = self._get_current_branch()
        if not current_branch:
            self._print_error("Could not determine current branch")
            input("\nPress Enter to continue...")
            return False

        print(f"Current branch: {current_branch}\n")

        # Check current tracking
        try:
            result = self._run_command(['git', 'branch', '-vv', '--list', current_branch], check=False)
            if result.returncode == 0 and result.stdout:
                line = result.stdout.strip()
                if '[' in line:
                    tracking = line.split('[')[1].split(']')[0]
                    print(f"Current tracking: {tracking}")
                    change = input("\nChange upstream branch? (y/n): ").strip().lower()
                    if change != 'y':
                        print("Operation cancelled")
                        input("\nPress Enter to continue...")
                        return True
                else:
                    print("No upstream tracking configured")
        except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError):
            pass

        # Get remote branches
        self._print_info("Fetching remote branches...")
        result = self._run_command(['git', 'fetch', '--all'], check=False)

        result = self._run_command(['git', 'branch', '-r'], check=False)
        if result.returncode != 0:
            self._print_error("Failed to get remote branches")
            input("\nPress Enter to continue...")
            return False

        remote_branches = [b.strip() for b in result.stdout.strip().split('\n') if b.strip() and '->' not in b]

        if not remote_branches:
            self._print_error("No remote branches found")
            input("\nPress Enter to continue...")
            return False

        # Select remote branch
        print("\nSelect remote branch to track:")
        for idx, branch in enumerate(remote_branches, 1):
            print(f"  {idx}. {branch}")

        print(f"  {len(remote_branches) + 1}. Cancel")

        choice = input(f"\nSelect branch (1-{len(remote_branches) + 1}): ").strip()

        try:
            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(remote_branches) + 1:
                self._print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return False

            if choice_idx == len(remote_branches) + 1:
                print("Operation cancelled")
                input("\nPress Enter to continue...")
                return False

            remote_branch = remote_branches[choice_idx - 1]

        except ValueError:
            self._print_error("Invalid input")
            input("\nPress Enter to continue...")
            return False

        # Set upstream
        print(f"\nSetting upstream to '{remote_branch}'...")

        try:
            result = self._run_command(['git', 'branch', '--set-upstream-to', remote_branch], check=True)

            if result.returncode == 0:
                self._print_success(f"Upstream set to '{remote_branch}'")
                input("\nPress Enter to continue...")
                return True
            else:
                self._print_error("Failed to set upstream")
                if result.stderr:
                    print(result.stderr)
                input("\nPress Enter to continue...")
                return False

        except Exception as e:
            self._print_error(f"Error setting upstream: {e}")
            input("\nPress Enter to continue...")
            return False


class BranchMenu:
    """Menu for all branch operations"""

    def __init__(self):
        self.git_branch = GitBranch()

    def run(self):
        """Run branch operations menu"""
        from core.menu import Menu, MenuItem

        class BranchOperationsMenu(Menu):
            def __init__(self, git_branch_instance):
                self.git_branch = git_branch_instance
                super().__init__("BRANCH OPERATIONS")

            def setup_items(self):
                self.items = [
                    MenuItem("Create New Branch", lambda: self.git_branch.create_branch(
                        input("\nEnter branch name: ").strip() if self._prompt_for_name() else ""
                    )),
                    MenuItem("Switch/Checkout Branch", lambda: self.git_branch.switch_branch()),
                    MenuItem("Rename Branch", lambda: self.git_branch.rename_branch()),
                    MenuItem("Delete Branch", lambda: self.git_branch.delete_branch()),
                    MenuItem("List All Branches", lambda: self.git_branch.list_branches()),
                    MenuItem("Sync Branch with Remote", lambda: self.git_branch.sync_branch()),
                    MenuItem("Create Branch from Commit", lambda: self.git_branch.create_from_commit()),
                    MenuItem("Compare Branches", lambda: self.git_branch.compare_branches()),
                    MenuItem("Merge Branch", lambda: self.git_branch.merge_branch()),
                    MenuItem("Set Upstream Tracking", lambda: self.git_branch.set_upstream()),
                    MenuItem("Back to Git Operations Menu", lambda: "exit")
                ]

            def _prompt_for_name(self):
                """Helper to prompt for branch name"""
                return True

        menu = BranchOperationsMenu(self.git_branch)
        menu.run()
