"""
Git Recovery Module
Handles commit recovery, rollback, and history management
"""
import subprocess


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
        print("  3. Cancel and return to menu\n")
        
        choice = input("Your choice (1/2/3): ").strip()
        
        if choice == '1':
            self._select_by_number(commits)
        elif choice == '2':
            self._select_by_id(commit_details_func, verify_commit_func)
        elif choice == '3':
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