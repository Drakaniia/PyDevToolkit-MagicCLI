"""
Git Diff Module
Handles comprehensive diff operations for Git repositories
"""
import subprocess
import sys

try:
    from termcolor import colored
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False
    # Only print warning if directly running this file
    import sys
    if __name__ == "__main__":
        print("Warning: termcolor library not found. Install it using: pip install termcolor")

# Import arrow navigation utility
try:
    from modules.web_development.dev_mode.menu_utils import get_choice_with_arrows
    HAS_ARROW_NAVIGATION = True
except ImportError:
    HAS_ARROW_NAVIGATION = False
class GitDiff:
    """Handles comprehensive git diff operations"""

    def __init__(self):
        pass

    def show_diff_menu(self):
        """Display the comprehensive diff operations menu with arrow navigation"""
        print("\n" + "="*70)
        if HAS_TERMCOLOR:
            print(colored(" GIT DIFF OPERATIONS", 'cyan', attrs=['bold']))
        else:
            print(" GIT DIFF OPERATIONS")
        print("="*70)

        if not self._is_git_repo():
            if HAS_TERMCOLOR:
                print(colored(" Not a git repository. Please initialize git first.", 'red'))
            else:
                print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        while True:
            # Define the menu options
            if HAS_TERMCOLOR:
                options = [
                    f"{colored('Show Unstaged Changes', 'cyan')} ({colored('git diff', 'white')})",
                    f"{colored('Show Staged Changes', 'cyan')} ({colored('git diff --staged', 'white')})",
                    f"{colored('Changes Since Last Commit', 'cyan')} ({colored('git diff HEAD', 'white')})",
                    f"{colored('Compare Branches', 'cyan')} ({colored('git diff branch1..branch2', 'white')})",
                    f"{colored('Back to main menu', 'red')}"
                ]
            else:
                options = [
                    "Show Unstaged Changes (git diff)",
                    "Show Staged Changes (git diff --staged)",
                    "Changes Since Last Commit (git diff HEAD)",
                    "Compare Branches (git diff branch1..branch2)",
                    "Back to main menu"
                ]

            # Get user choice with arrow navigation
            if HAS_ARROW_NAVIGATION:
                choice_idx = get_choice_with_arrows(options, "Select a diff operation")
            else:
                # Fallback to traditional input method
                print("\nSelect a diff operation:")
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
                print()

                try:
                    choice = input("Enter your choice (1-5): ").strip()
                    choice_idx = int(choice)
                    if choice_idx < 1 or choice_idx > len(options):
                        print("Invalid choice. Please enter a number between 1 and 5.")
                        input("\nPress Enter to continue...")
                        continue
                except ValueError:
                    print("Please enter a valid number")
                    input("\nPress Enter to continue...")
                    continue

            # Execute the selected option
            if choice_idx == 1:
                self.show_unstaged_diff()
            elif choice_idx == 2:
                self.show_staged_diff()
            elif choice_idx == 3:
                self.show_head_diff()
            elif choice_idx == 4:
                self.show_branch_diff()
            elif choice_idx == 5:
                if HAS_TERMCOLOR:
                    print(colored("Returning to main menu...", 'green'))
                else:
                    print("Returning to main menu...")
                break
            else:
                if HAS_TERMCOLOR:
                    print(colored("\n Invalid choice. Please enter 1-5.", 'red'))
                else:
                    print("\n Invalid choice. Please enter 1-5.")
                input("\nPress Enter to continue...")

    def show_unstaged_diff(self):
        """Show unstaged changes (git diff)"""
        print("\n" + "="*70)
        if HAS_TERMCOLOR:
            print(colored(" GIT DIFF - Unstaged Changes", 'cyan', attrs=['bold']))
        else:
            print(" GIT DIFF - Unstaged Changes")
        print("="*70)

        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.stdout:
            print("\n Unstaged changes:")
            print("-" * 70)
            self._print_colored_diff(result.stdout)
        else:
            if HAS_TERMCOLOR:
                print(colored("\n No unstaged changes found.", 'green'))
            else:
                print("\n No unstaged changes found.")

        input("\nPress Enter to continue...")

    def show_staged_diff(self):
        """Show staged changes (git diff --staged)"""
        print("\n" + "="*70)
        if HAS_TERMCOLOR:
            print(colored(" GIT DIFF --STAGED - Staged Changes", 'cyan', attrs=['bold']))
        else:
            print(" GIT DIFF --STAGED - Staged Changes")
        print("="*70)

        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.stdout:
            print("\n Staged changes (to be committed):")
            print("-" * 70)
            self._print_colored_diff(result.stdout)
        else:
            if HAS_TERMCOLOR:
                print(colored("\n No staged changes found (nothing to commit).", 'green'))
            else:
                print("\n No staged changes found (nothing to commit).")

        input("\nPress Enter to continue...")

    def show_head_diff(self):
        """Show all changes since last commit (git diff HEAD)"""
        print("\n" + "="*70)
        if HAS_TERMCOLOR:
            print(colored(" GIT DIFF HEAD - All Changes Since Last Commit", 'cyan', attrs=['bold']))
        else:
            print(" GIT DIFF HEAD - All Changes Since Last Commit")
        print("="*70)

        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.stdout:
            print("\n All changes since last commit (staged + unstaged):")
            print("-" * 70)
            self._print_colored_diff(result.stdout)
        else:
            if HAS_TERMCOLOR:
                print(colored("\n No changes found since last commit.", 'green'))
            else:
                print("\n No changes found since last commit.")

        input("\nPress Enter to continue...")

    def show_branch_diff(self):
        """Show differences between two branches (git diff branch1..branch2)"""
        print("\n" + "="*70)
        if HAS_TERMCOLOR:
            print(colored(" GIT DIFF Branch Comparison", 'cyan', attrs=['bold']))
        else:
            print(" GIT DIFF Branch Comparison")
        print("="*70)

        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        # Get list of available branches
        branches_result = subprocess.run(
            ["git", "branch", "--list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("\n Available branches:")
        if branches_result.stdout:
            branches = [branch.strip().replace('*', '').strip() for branch in branches_result.stdout.split('\n') if branch.strip()]
            for i, branch in enumerate(branches, 1):
                if HAS_TERMCOLOR:
                    print(f"  {i}. {colored(branch, 'yellow')}")
                else:
                    print(f"  {i}. {branch}")
        else:
            print("  No branches found")

        print()

        branch1 = input("Enter the first branch name: ").strip()
        branch2 = input("Enter the second branch name: ").strip()

        if not branch1 or not branch2:
            print("\n Both branch names must be provided.")
            input("\nPress Enter to continue...")
            return

        print(f"\n Differences between '{branch1}' and '{branch2}':")
        print("-" * 70)

        result = subprocess.run(
            ["git", "diff", f"{branch1}..{branch2}"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            if result.stdout:
                self._print_colored_diff(result.stdout)
            else:
                if HAS_TERMCOLOR:
                    print(colored(f"No differences found between '{branch1}' and '{branch2}'.", 'green'))
                else:
                    print(f"No differences found between '{branch1}' and '{branch2}'.")
        else:
            if HAS_TERMCOLOR:
                print(colored(f" Error comparing branches: {result.stderr}", 'red'))
            else:
                print(f" Error comparing branches: {result.stderr}")

        input("\nPress Enter to continue...")

    def _print_colored_diff(self, diff_output):
        """Print diff output with colors based on diff content"""
        if not diff_output:
            return

        lines = diff_output.split('\n')

        for line in lines:
            if HAS_TERMCOLOR:
                if line.startswith('diff --git'):
                    print(colored(line, 'blue', attrs=['bold']))
                elif line.startswith('index '):
                    print(colored(line, 'blue'))
                elif line.startswith('---'):
                    print(colored(line, 'red'))
                elif line.startswith('+++'):
                    print(colored(line, 'green'))
                elif line.startswith('-'):
                    print(colored(line, 'red'))
                elif line.startswith('+'):
                    print(colored(line, 'green'))
                elif line.startswith('@@'):
                    print(colored(line, 'yellow'))
                else:
                    print(line)
            else:
                print(line)

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

    def get_all_diffs_formatted(self):
        """Get all types of diffs for external use"""
        diffs = {}

        if not self._is_git_repo():
            return diffs

        # Get unstaged diff
        unstaged_result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        diffs['unstaged'] = unstaged_result.stdout if unstaged_result.stdout else ""

        # Get staged diff
        staged_result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        diffs['staged'] = staged_result.stdout if staged_result.stdout else ""

        # Get diff against HEAD
        head_result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        diffs['head'] = head_result.stdout if head_result.stdout else ""

        return diffs