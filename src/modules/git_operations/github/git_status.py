"""
Git Status Module
Handles repository status checking and display
"""
import subprocess
try:
    from termcolor import colored
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False
    # Only print warning if directly running this file
    import sys
    if __name__ == "__main__":
        print(
            "Warning: termcolor library not found. Install it using: pip install termcolor")


class GitStatus:
    """Handles git status operations"""

    def __init__(self):
        pass

    def show_status(self):
        """Display current git status in verbose format with colors"""
        print("\n" + "=" * 70)
        print(" GIT STATUS (VERBOSE FORMAT WITH COLORS)")
        print("=" * 70 + "\n")

        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return

        # Get full git status output (verbose format)
        try:
            result = subprocess.run(
                ["git", "status", "--verbose"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.stdout:
                # Parse the verbose output and organize it by section
                self._parse_and_display_verbose_status(result.stdout)
            else:
                print(" Working directory clean (no changes)")

        except subprocess.CalledProcessError as e:
            print(f" Error getting git status: {e}")
            if e.stderr:
                print(e.stderr)
        except FileNotFoundError:
            print(" Git is not installed or not in PATH")

        input("\nPress Enter to continue...")

    def _colorize_status_line(self, line):
        """Colorize a single status line based on file status"""
        if not line:
            return

        # Extract the status codes (first 2 characters typically)
        status_code = line[:2].strip()

        if HAS_TERMCOLOR:
            # Different status codes and their meanings
            # M = Modified
            # A = Added
            # D = Deleted
            # R = Renamed
            # C = Copied
            # U = Updated but unmerged
            # ?? = Untracked

            # Determine color based on status code
            if 'D' in status_code or status_code == 'D':  # Deleted
                color = 'red'
            elif 'M' in status_code or status_code == 'M':  # Modified
                color = 'green'
            elif 'A' in status_code or status_code == 'A':  # Added
                color = 'green'
            elif 'R' in status_code or status_code == 'R':  # Renamed
                color = 'yellow'
            elif 'C' in status_code or status_code == 'C':  # Copied
                color = 'cyan'
            elif 'U' in status_code or status_code == 'U':  # Unmerged
                color = 'magenta'
            elif status_code == '??':  # Untracked
                color = 'blue'
            else:
                color = 'white'  # Default

            # Colorize the status code and filename separately
            if len(line) > 2:
                status_part = line[:2]
                filename_part = line[2:]
                print(colored(status_part, color) + filename_part)
            else:
                print(colored(line, color))
        else:
            # If termcolor is not available, just print the line as is
            print(line)

    def _parse_and_display_verbose_status(self, status_output):
        """Parse verbose git status output and display it in organized sections with colors"""
        lines = status_output.split('\n')

        # Identify sections based on common git status headers
        staged_files = []
        unstaged_files = []
        untracked_files = []
        other_info = []

        current_section = "other"

        for line in lines:
            if line.startswith("On branch"):
                other_info.append(line)
                continue
            elif line.startswith("Your branch is"):
                other_info.append(line)
                continue
            elif "Changes to be committed" in line:
                current_section = "staged"
                other_info.append(line)  # Header line
                continue
            elif "Changes not staged" in line:
                current_section = "unstaged"
                other_info.append(line)  # Header line
                continue
            elif "Untracked files" in line:
                current_section = "untracked"
                other_info.append(line)  # Header line
                continue
            elif line.strip() == "":  # Empty line
                if current_section != "other":
                    # Maintain spacing between sections
                    other_info.append(line)
                continue
            elif line.startswith("\t") or line.startswith("  "):  # File information
                if current_section == "staged":
                    staged_files.append(line.strip())
                elif current_section == "unstaged":
                    unstaged_files.append(line.strip())
                elif current_section == "untracked":
                    untracked_files.append(line.strip())
                else:
                    other_info.append(line)
            else:
                other_info.append(line)

        # Display organized sections
        for info_line in other_info:
            if HAS_TERMCOLOR:
                # Color other info lines differently (like branch info)
                if "On branch" in info_line:
                    print(colored(info_line, 'blue'))
                elif "Your branch is" in info_line:
                    print(colored(info_line, 'cyan'))
                else:
                    print(info_line)
            else:
                print(info_line)

        # Display staged files section
        if staged_files:
            print("\n" + "=" * 50)
            if HAS_TERMCOLOR:
                print(
                    colored(
                        "STAGED FILES (Changes to be committed):",
                        'green',
                        attrs=['bold']))
            else:
                print("STAGED FILES (Changes to be committed):")
            print("=" * 50)

            for file_line in staged_files:
                if HAS_TERMCOLOR:
                    # Color based on status (added, modified, deleted, etc.)
                    if file_line.startswith('new file:'):
                        print(colored("    new file:",
                              'green') + file_line[11:])
                    elif file_line.startswith('modified:'):
                        print(colored("    modified:",
                              'green') + file_line[9:])
                    elif file_line.startswith('deleted:'):
                        print(colored("    deleted:", 'red') + file_line[8:])
                    elif file_line.startswith('renamed:'):
                        print(colored("    renamed:",
                              'yellow') + file_line[8:])
                    else:
                        print(colored(file_line, 'green'))
                else:
                    print(file_line)

        # Display unstaged files section
        if unstaged_files:
            print("\n" + "=" * 50)
            if HAS_TERMCOLOR:
                print(
                    colored(
                        "UNSTAGED FILES (Changes not staged for commit):",
                        'yellow',
                        attrs=['bold']))
            else:
                print("UNSTAGED FILES (Changes not staged for commit):")
            print("=" * 50)

            for file_line in unstaged_files:
                if HAS_TERMCOLOR:
                    # Color based on status
                    if file_line.startswith('modified:'):
                        print(colored("    modified:", 'red') + file_line[9:])
                    elif file_line.startswith('deleted:'):
                        print(colored("    deleted:", 'red') + file_line[8:])
                    elif file_line.startswith('renamed:'):
                        print(colored("    renamed:",
                              'yellow') + file_line[8:])
                    else:
                        print(colored(file_line, 'yellow'))
                else:
                    print(file_line)

        # Display untracked files section
        if untracked_files:
            print("\n" + "=" * 50)
            if HAS_TERMCOLOR:
                print(colored("UNTRACKED FILES:", 'blue', attrs=['bold']))
            else:
                print("UNTRACKED FILES:")
            print("=" * 50)

            for file_line in untracked_files:
                if HAS_TERMCOLOR:
                    print(colored("    " + file_line, 'blue'))
                else:
                    print("    " + file_line)

    def get_status_porcelain(self):
        """Get git status in machine-readable format"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def has_uncommitted_changes(self):
        """Check if there are uncommitted changes"""
        status = self.get_status_porcelain()
        return bool(status)

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

    def _run_command(self, command):
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f" Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print(" Git is not installed or not in PATH")
            return False
