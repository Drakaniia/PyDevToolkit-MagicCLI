"""
Git Recovery Module
Handles commit recovery, rollback, and history management
"""
import subprocess
import sys

# Try to import platform-specific modules for keyboard input
try:
    import tty
    import termios
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class GitRecover:
    """Handles git commit recovery and rollback operations"""
    
    def __init__(self):
        pass
    
    def show_recovery_menu(self, commit_history_func, commit_details_func, verify_commit_func):
        """
        Show the commit recovery interface

        Args:
            commit_history_func: Function to get commit history
            commit_details_func: Function to get commit details by ID
            verify_commit_func: Function to verify commit exists
        """
        print("\n" + "="*70)
        print("GIT COMMIT RECOVERY")
        print("="*70 + "\n")

        # Check if we're in a git repository
        if not self._is_git_repo():
            print("Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        # Get commit history with remote fetch enabled by default
        commits = commit_history_func(fetch_remote=True)

        if not commits:
            print("No commits found in this repository.")
            input("\nPress Enter to continue...")
            return

        # Display commits
        print("Commit History:\n")
        print(f"{'#':<5} {'Commit ID':<12} {'Date & Time':<25} {'Message'}")
        print("-" * 70)

        for idx, commit in enumerate(commits, 1):
            commit_id = commit['hash'][:10]
            timestamp = commit['date']
            message = commit['message'][:40] + "..." if len(commit['message']) > 40 else commit['message']
            print(f"{idx:<5} {commit_id:<12} {timestamp:<25} {message}")

        print("-" * 70 + "\n")

        # Ask user how they want to select
        print("How would you like to select a commit?")
        print("  1. By commit number (from the list above)")
        print("  2. By entering commit ID directly")
        print("  3. Reset & Revert Operations")
        print("  4. Cancel and return to menu\n")

        choice = input("Your choice (1/2/3/4): ").strip()

        if choice == '1':
            self._select_by_number(commits)
        elif choice == '2':
            self._select_by_id(commit_details_func, verify_commit_func)
        elif choice == '3':
            self._show_reset_revert_menu()
        elif choice == '4':
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice.")
            input("\nPress Enter to continue...")
    
    def _select_by_number(self, commits):
        """Select commit by number from list"""
        try:
            num = input("\nEnter commit number to recover: ").strip()
            num = int(num)

            if 1 <= num <= len(commits):
                commit = commits[num - 1]
                self._confirm_and_revert(commit)
            else:
                print(f"\nInvalid number. Please enter between 1 and {len(commits)}")
                input("\nPress Enter to continue...")
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            input("\nPress Enter to continue...")
    
    def _select_by_id(self, commit_details_func, verify_commit_func):
        """Select commit by entering commit ID"""
        commit_id = input("\nEnter commit ID (hash): ").strip()

        if not commit_id:
            print("\nCommit ID cannot be empty.")
            input("\nPress Enter to continue...")
            return

        # Verify commit exists with remote fetch enabled by default
        if not verify_commit_func(commit_id, fetch_remote=True):
            print(f"\nCommit '{commit_id}' not found.")
            input("\nPress Enter to continue...")
            return

        # Get commit details with remote fetch enabled by default
        commit_info = commit_details_func(commit_id, fetch_remote=True)
        if commit_info:
            self._confirm_and_revert(commit_info)
        else:
            print(f"\nCould not retrieve details for commit '{commit_id}'.")
            input("\nPress Enter to continue...")
    
    def _confirm_and_revert(self, commit):
        """Confirm and perform the revert operation"""
        print("\n" + "="*70)
        print("COMMIT RECOVERY CONFIRMATION")
        print("="*70)
        print(f"\nCommit ID:  {commit['hash']}")
        print(f"Date:       {commit['date']}")
        print(f"Author:     {commit['author']}")
        print(f"Message:    {commit['message']}\n")

        print("Recovery Options:")
        print("  1. Hard Reset (DESTRUCTIVE - loses all changes after this commit)")
        print("  2. Soft Reset (keeps changes as uncommitted)")
        print("  3. Create new branch from this commit")
        print("  4. Cancel\n")
        
        choice = input("Your choice (1/2/3/4): ").strip()
        
        if choice == '1':
            self.hard_reset(commit['hash'])
        elif choice == '2':
            self.soft_reset(commit['hash'])
        elif choice == '3':
            self.create_branch(commit['hash'])
        elif choice == '4':
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice.")
            input("\nPress Enter to continue...")
    
    def hard_reset(self, commit_hash):
        """Perform hard reset to commit"""
        print("\nWARNING: This will permanently delete all commits after this point!")
        print("Are you absolutely sure?")
        confirm = input("Type 'YES' to confirm: ").strip()

        if confirm == 'YES':
            print("\nPerforming hard reset...")
            result = subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print("\nSuccessfully reset to commit!")
                print(result.stdout)
                print("\nNote: Use 'git push --force' to update remote (if needed)")
            else:
                print(f"\nError: {result.stderr}")

            input("\nPress Enter to continue...")
        else:
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
    
    def soft_reset(self, commit_hash):
        """Perform soft reset to commit"""
        print("\nPerforming soft reset...")
        result = subprocess.run(
            ["git", "reset", "--soft", commit_hash],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print("\nSuccessfully reset to commit!")
            print("Your changes are now uncommitted and staged.")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\nError: {result.stderr}")

        input("\nPress Enter to continue...")
    
    def create_branch(self, commit_hash):
        """Create a new branch from commit"""
        branch_name = input("\nEnter new branch name: ").strip()

        if not branch_name:
            print("\nBranch name cannot be empty.")
            input("\nPress Enter to continue...")
            return

        print(f"\nCreating branch '{branch_name}' from commit...")
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name, commit_hash],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print(f"\nSuccessfully created and switched to branch '{branch_name}'!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\nError: {result.stderr}")

        input("\nPress Enter to continue...")
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0

    def _show_reset_revert_menu(self):
        """Show menu for reset and revert operations"""
        print("\n" + "="*70)
        print("GIT RESET & REVERT OPERATIONS")
        print("="*70 + "\n")

        print("Recovery Options:")
        print("  1. git revert - Create new commit reverting changes (safer than reset)")
        print("  2. git reset HEAD - Unstage files")
        print("  3. git restore <file> - Discard changes in working directory (modern replacement for git checkout --)")
        print("  4. Cancel and return to main menu\n")

        choice = input("Your choice (1/2/3/4): ").strip()

        if choice == '1':
            self._show_git_revert()
        elif choice == '2':
            self._show_git_reset_head()
        elif choice == '3':
            self._show_git_checkout_file()
        elif choice == '4':
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice.")
            input("\nPress Enter to continue...")

    def _show_git_revert(self):
        """Show git revert operation"""
        print("\n" + "="*50)
        print("GIT REVERT - Create new commit reverting changes")
        print("="*50)
        print("\nThis command creates a new commit that undoes the changes from a previous commit.")
        print("This is safer than reset because it doesn't modify history.\n")

        # Get commit history to select from
        commits = self._get_recent_commits()
        if not commits:
            print("No commits found.")
            input("\nPress Enter to continue...")
            return

        # Display commits for selection
        print("Recent commits:")
        print(f"{'#':<5} {'Commit ID':<12} {'Date & Time':<25} {'Message'}")
        print("-" * 70)

        for idx, commit in enumerate(commits, 1):
            commit_id = commit['hash'][:10]
            timestamp = commit['date']
            message = commit['message'][:40] + "..." if len(commit['message']) > 40 else commit['message']
            print(f"{idx:<5} {commit_id:<12} {timestamp:<25} {message}")

        print("-" * 70 + "\n")

        print("How would you like to select a commit to revert?")
        print("  1. By commit number (from the list above)")
        print("  2. By entering commit ID directly")
        print("  3. Cancel\n")

        choice = input("Your choice (1/2/3): ").strip()

        if choice == '1':
            self._select_commit_for_revert_by_number(commits)
        elif choice == '2':
            self._select_commit_for_revert_by_id()
        elif choice == '3':
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice.")
            input("\nPress Enter to continue...")

    def _select_commit_for_revert_by_number(self, commits):
        """Select commit by number for revert"""
        try:
            num = input("\nEnter commit number to revert: ").strip()
            num = int(num)

            if 1 <= num <= len(commits):
                commit = commits[num - 1]
                self._confirm_and_perform_revert(commit)
            else:
                print(f"\nInvalid number. Please enter between 1 and {len(commits)}")
                input("\nPress Enter to continue...")
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            input("\nPress Enter to continue...")

    def _select_commit_for_revert_by_id(self):
        """Select commit by ID for revert"""
        commit_id = input("\nEnter commit ID (hash) to revert: ").strip()

        if not commit_id:
            print("\nCommit ID cannot be empty.")
            input("\nPress Enter to continue...")
            return

        # Verify commit exists
        if not self._verify_commit_exists(commit_id):
            print(f"\nCommit '{commit_id}' not found.")
            input("\nPress Enter to continue...")
            return

        # Get commit details
        commit_info = self._get_commit_details(commit_id)
        if commit_info:
            self._confirm_and_perform_revert(commit_info)
        else:
            print(f"\nCould not retrieve details for commit '{commit_id}'.")
            input("\nPress Enter to continue...")

    def _confirm_and_perform_revert(self, commit):
        """Confirm and perform git revert operation"""
        print("\n" + "="*70)
        print("GIT REVERT CONFIRMATION")
        print("="*70)
        print(f"\nCommit ID:  {commit['hash']}")
        print(f"Date:       {commit['date']}")
        print(f"Author:     {commit['author']}")
        print(f"Message:    {commit['message']}\n")

        print("This will create a new commit that reverses the changes from the selected commit.")
        print("This is safer than reset because it doesn't modify history.")
        print("\nOptions:")
        print("  1. Standard revert (creates a new commit immediately)")
        print("  2. Revert with no commit (stages changes for review)")

        choice = input("Choose option (1/2): ").strip()

        if choice == '2':
            # Use --no-commit option to stage changes without committing
            revert_cmd = ["git", "revert", "--no-commit", commit['hash']]
            success_message = "Changes have been staged. You can now commit or modify before committing."
        elif choice == '1':
            # Standard revert command
            revert_cmd = ["git", "revert", commit['hash']]
            success_message = "Successfully reverted the commit with a new commit."
        else:
            print("\nInvalid choice. Operation cancelled.")
            input("\nPress Enter to continue...")
            return

        confirm = input("\nDo you want to proceed? (y/N): ").strip().lower()

        if confirm == 'y':
            print(f"\nReverting commit {commit['hash'][:10]}...")
            result = subprocess.run(
                revert_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"\n{success_message}")
                if result.stdout:
                    print(result.stdout)
            else:
                # If there are conflicts, try to abort the revert
                print(f"\nError during revert: {result.stderr}")
                print("The revert operation may have failed. You might need to resolve conflicts manually.")
                # Try to abort the revert attempt if it's still in progress
                abort_result = subprocess.run(["git", "revert", "--abort"], capture_output=True, text=True)
                if abort_result.returncode != 0:
                    print("Could not abort revert. Manual intervention may be needed.")

            input("\nPress Enter to continue...")
        else:
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")

    def _show_git_reset_head(self):
        """Show git reset HEAD operation to unstage files"""
        print("\n" + "="*50)
        print("GIT RESET HEAD - Unstage files")
        print("="*50)
        print("\nThis command unstages files that have been added to the staging area.")
        print("The changes will remain in your working directory.\n")

        # Show current status
        print("Current git status:")
        status_result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if status_result.stdout:
            print(status_result.stdout)
        else:
            print("Working directory is clean (no changes).")

        print("\nOptions:")
        print("  1. Unstage all files")
        print("  2. Unstage specific file")
        print("  3. Cancel\n")

        choice = input("Your choice (1/2/3): ").strip()

        if choice == '1':
            self._unstage_all_files()
        elif choice == '2':
            self._unstage_specific_file()
        elif choice == '3':
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice.")
            input("\nPress Enter to continue...")

    def _unstage_all_files(self):
        """Unstage all files using git reset HEAD"""
        print("\nUnstaging all files...")
        result = subprocess.run(
            ["git", "reset"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print("\nAll files have been successfully unstaged.")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\nError: {result.stderr}")

        input("\nPress Enter to continue...")

    def _unstage_specific_file(self):
        """Unstage specific file using git reset HEAD <file>"""
        file_path = input("\nEnter file path to unstage (e.g., src/main.py): ").strip()

        if not file_path:
            print("\nFile path cannot be empty.")
            input("\nPress Enter to continue...")
            return

        print(f"\nUnstaging file '{file_path}'...")
        result = subprocess.run(
            ["git", "reset", "HEAD", file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print(f"\nFile '{file_path}' has been successfully unstaged.")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\nError: {result.stderr}")

        input("\nPress Enter to continue...")

    def _show_git_checkout_file(self):
        """Show git restore operation to discard changes in working directory"""
        print("\n" + "="*60)
        print("GIT RESTORE <FILE> - Discard changes in working directory")
        print("="*60)
        print("\nThis command discards changes in the working directory for specified files.")
        print("This is a destructive operation - you will lose your uncommitted changes!\n")

        # Show current status
        print("Current git status:")
        status_result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if status_result.stdout:
            print(status_result.stdout)
        else:
            print("Working directory is clean (no changes).")

        file_path = input("\nEnter file path to discard changes (e.g., src/main.py) or 'all' for all files: ").strip()

        if not file_path:
            print("\nFile path cannot be empty.")
            input("\nPress Enter to continue...")
            return

        # Handle 'all' to restore all files
        if file_path.lower() == 'all':
            self._restore_all_files()
        else:
            self._restore_specific_file(file_path)

    def _restore_specific_file(self, file_path):
        """Restore a specific file to discard changes using git restore <file>"""
        print(f"\nWARNING: This will permanently discard all changes in '{file_path}'!")
        print("Are you absolutely sure?")
        confirm = input("Type 'YES' to confirm: ").strip()

        if confirm == 'YES':
            print(f"\nDiscarding changes in file '{file_path}'...")
            result = subprocess.run(
                ["git", "restore", file_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"\nSuccessfully discarded changes in file '{file_path}'!")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"\nError: {result.stderr}")

            input("\nPress Enter to continue...")
        else:
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")

    def _restore_all_files(self):
        """Restore all files to discard changes using git restore ."""
        print("\nWARNING: This will permanently discard ALL changes in your working directory!")
        print("Are you absolutely sure?")
        confirm = input("Type 'YES' to confirm: ").strip()

        if confirm == 'YES':
            print("\nDiscarding changes in all files...")
            result = subprocess.run(
                ["git", "restore", "."],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print("\nSuccessfully discarded changes in all files!")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"\nError: {result.stderr}")

            input("\nPress Enter to continue...")
        else:
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")

    def _get_recent_commits(self):
        """Get recent commits from git log"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            commit_hash = parts[0]
                            commit_message = parts[1]
                            # Get full commit details
                            full_result = subprocess.run(
                                ["git", "show", "--format=%H|%ai|%an|%s", "--no-patch", commit_hash],
                                capture_output=True,
                                text=True,
                                encoding='utf-8',
                                errors='replace'
                            )
                            if full_result.returncode == 0:
                                details = full_result.stdout.strip().split('|')
                                if len(details) >= 4:
                                    commits.append({
                                        'hash': details[0],
                                        'date': details[1],
                                        'author': details[2],
                                        'message': details[3]
                                    })
                return commits
            else:
                return []
        except Exception:
            return []

    def _verify_commit_exists(self, commit_hash):
        """Verify if a commit exists"""
        result = subprocess.run(
            ["git", "rev-parse", "--verify", commit_hash],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0

    def _get_commit_details(self, commit_hash):
        """Get commit details by hash"""
        result = subprocess.run(
            ["git", "show", "--format=%H|%ai|%an|%s", "--no-patch", commit_hash],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0 and result.stdout:
            details = result.stdout.strip().split('|')
            if len(details) >= 4:
                return {
                    'hash': details[0],
                    'date': details[1],
                    'author': details[2],
                    'message': details[3]
                }

        return None

    def _print_commit_list_with_selection(self, commits, selected_idx=0):
        """Print commit list with visual selection indicator"""
        print("Commit History:\n")
        print(f"{'#':<5} {'Commit ID':<12} {'Date & Time':<25} {'Message'}")
        print("-" * 70)

        for idx, commit in enumerate(commits, 1):
            commit_id = commit['hash'][:10]
            timestamp = commit['date']
            message = commit['message'][:40] + "..." if len(commit['message']) > 40 else commit['message']

            if idx - 1 == selected_idx:
                print(f">> {idx:<3} {commit_id:<12} {timestamp:<25} {message}")
            else:
                print(f"   {idx:<3} {commit_id:<12} {timestamp:<25} {message}")

        print("-" * 70 + "\n")

    def _getch(self):
        """Get a single character from stdin, cross-platform"""
        if HAS_MSVCRT:  # Windows
            char = msvcrt.getch()
            try:
                return char.decode('utf-8')
            except:
                return chr(ord(char))
        elif HAS_TERMIOS:  # Unix/Linux/Mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        else:
            # Fallback to input if no platform-specific methods available
            return input()

    def _arrow_selection_menu(self, commits, title="Select a commit"):
        """Display a menu with arrow key navigation for commit selection"""
        if not commits:
            return -1

        selected_idx = 0
        total_items = len(commits)

        while True:
            # Clear screen and display menu
            print("\033[2J\033[H", end='')  # ANSI escape codes to clear screen
            print("\n" + "="*70)
            print(f"{title}")
            print("="*70 + "\n")

            self._print_commit_list_with_selection(commits, selected_idx)

            print("Use ↑/↓ to navigate, Enter to select, 'q' to cancel")

            # Get key press
            key = self._getch()

            if HAS_MSVCRT:  # Windows
                if key in ('\xe0', '\x00'):  # Special keys
                    arrow = self._getch()
                    if arrow == 'H':  # Up arrow
                        selected_idx = (selected_idx - 1) % total_items
                    elif arrow == 'P':  # Down arrow
                        selected_idx = (selected_idx + 1) % total_items
                elif key.lower() == 'q':  # Quit
                    return -1
                elif key == '\r':  # Enter
                    return selected_idx
            else:  # Unix/Linux/Mac
                if key == '\x1b':  # ESC sequence for special keys
                    next_key = self._getch()
                    if next_key == '[':
                        arrow = self._getch()
                        if arrow == 'A':  # Up arrow
                            selected_idx = (selected_idx - 1) % total_items
                        elif arrow == 'B':  # Down arrow
                            selected_idx = (selected_idx + 1) % total_items
                elif key.lower() == 'q':  # Quit
                    return -1
                elif key in ['\r', '\n']:  # Enter
                    return selected_idx

    def _select_by_number_with_arrows(self, commits):
        """Select commit by number using arrow key navigation"""
        title = "Select a commit to recover"
        selected_idx = self._arrow_selection_menu(commits, title)

        if selected_idx == -1:  # User cancelled
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
            return

        commit = commits[selected_idx]
        self._confirm_and_revert(commit)

    def _select_commit_for_revert_by_number_with_arrows(self, commits):
        """Select commit by number for revert using arrow key navigation"""
        title = "Select a commit to revert"
        selected_idx = self._arrow_selection_menu(commits, title)

        if selected_idx == -1:  # User cancelled
            print("\nOperation cancelled.")
            input("\nPress Enter to continue...")
            return

        commit = commits[selected_idx]
        self._confirm_and_perform_revert(commit)