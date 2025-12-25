"""
Git Log Module
Handles commit history viewing and log operations
"""
import subprocess
from datetime import datetime
from core.loading import LoadingSpinner, loading_animation
class GitLog:
    """Handles git log and commit history operations"""

    def __init__(self):
        pass

    def fetch_remote_commits(self):
        """Fetch commits from all remotes before displaying local log"""
        try:
            spinner = LoadingSpinner("Fetching remote changes", style='classic')
            spinner.start()

            result = subprocess.run(
                ["git", "fetch", "--all"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )

            spinner.stop(success=True, final_message="Fetching complete: Remote changes fetched successfully!")

            if result.stdout:
                print("Remote changes fetched successfully!")
            return True
        except subprocess.CalledProcessError as e:
            spinner.stop(success=False, final_message="Fetching failed: Error fetching remote changes")
            print(f"Error fetching remote changes: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except FileNotFoundError:
            spinner.stop(success=False, final_message="Fetching failed: Git is not installed or not in PATH")
            print("Git is not installed or not in PATH")
            return False

    def show_advanced_log_menu(self):
        """Show submenu for advanced log operations after fetching remote changes"""
        from core.menu import Menu, MenuItem

        # First, fetch remote changes
        self.fetch_remote_commits()

        class AdvancedLogMenu(Menu):
            """Advanced log operations submenu"""

            def __init__(self, git_log_instance):
                self.git_log_instance = git_log_instance
                super().__init__("Advanced Git Log Operations - After Fetching Remote Changes")

            def setup_items(self):
                self.items = [
                    MenuItem("Log (Last 10 commits)", lambda: self.git_log_instance.show_log(limit=10, fetch_remote=False)),
                    MenuItem("Visual Branch History (git log --oneline --graph --all)", lambda: self.git_log_instance.show_visual_branch_history()),
                    MenuItem("Commit Changes Statistics (git log --stat)", lambda: self.git_log_instance.show_stat_log()),
                    MenuItem("Author Commit Summary (git shortlog)", lambda: self.git_log_instance.show_shortlog()),
                    MenuItem("Back to Git Operations Menu", lambda: "exit")
                ]

        submenu = AdvancedLogMenu(self)
        submenu.run()

    def show_log(self, limit=10, fetch_remote=True):
        """Display git commit log with option to fetch remote commits first"""
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)  # Initialize colorama
        except ImportError:
            if fetch_remote:
                self.fetch_remote_commits()
            print("\n" + "="*70)
            print(f"GIT LOG (Last {limit} commits)")
            print("="*70 + "\n")

            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                input("\nPress Enter to continue...")
                return

            self._run_command(["git", "log", "--oneline", f"-{limit}"])
            input("\nPress Enter to continue...")
            return

        if fetch_remote:
            self.fetch_remote_commits()

        print("\n" + Fore.CYAN + "="*70)
        print(Fore.YELLOW + Style.BRIGHT + f"GIT LOG (Last {limit} commits)")
        print(Fore.CYAN + "="*70 + Style.RESET_ALL + "\n")

        if not self._is_git_repo():
            print(Fore.RED + "Not a git repository. Please initialize git first.")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"-{limit}", "--color=always"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout:
                # Process and colorize the output
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        # Colorize different parts of the git log
                        processed_line = line
                        import re
                        # Colorize commit hashes (7-character hex)
                        processed_line = re.sub(r'\b([0-9a-f]{7,})\b',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Print the processed line with colors
                        print(processed_line)
            else:
                print(Fore.YELLOW + "No commits found in the repository.")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running git command: {e}")
            if e.stderr:
                print(Fore.RED + f"Error details: {e.stderr}")
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")

        input(Fore.YELLOW + "\nPress Enter to continue...")

    def show_graph_log(self):
        """Show commit history as a graph with comprehensive design and colors"""
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)  # Initialize colorama
        except ImportError:
            print("Colorama library not found. Please install it with: pip install colorama")
            print("\n" + "="*70)
            print("GIT LOG --GRAPH (Commit history as a graph)")
            print("="*70 + "\n")

            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                input("\nPress Enter to continue...")
                return

            self._run_command(["git", "log", "--graph", "--oneline", "--all"])
            input("\nPress Enter to continue...")
            return

        print("\n" + Fore.CYAN + "="*70)
        print(Fore.YELLOW + Style.BRIGHT + "GIT LOG --GRAPH (Commit history as a graph)")
        print(Fore.CYAN + "="*70 + Style.RESET_ALL + "\n")

        if not self._is_git_repo():
            print(Fore.RED + "Not a git repository. Please initialize git first.")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--graph", "--oneline", "--all", "--color=always"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout:
                # Process and colorize the output
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        # Colorize different parts of the git log
                        processed_line = line
                        import re
                        # Colorize commit hashes (7-character hex)
                        processed_line = re.sub(r'\b([0-9a-f]{7,})\b',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize branch names (words between *)
                        processed_line = re.sub(r'\*',
                                              Fore.RED + Style.BRIGHT + '*' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize branch references
                        processed_line = re.sub(r'(\(.*?\))',
                                              Fore.BLUE + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Print the processed line with colors
                        print(processed_line)
            else:
                print(Fore.YELLOW + "No commits found in the repository.")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running git command: {e}")
            if e.stderr:
                print(Fore.RED + f"Error details: {e.stderr}")
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")

        input(Fore.YELLOW + "\nPress Enter to continue...")

    def show_stat_log(self):
        """Show commit changes statistics with comprehensive design and colors"""
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)  # Initialize colorama
        except ImportError:
            print("Colorama library not found. Please install it with: pip install colorama")
            print("\n" + "="*70)
            print("GIT LOG --STAT (Commit changes statistics)")
            print("="*70 + "\n")

            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                input("\nPress Enter to continue...")
                return

            self._run_command(["git", "log", "--stat"])
            input("\nPress Enter to continue...")
            return

        print("\n" + Fore.CYAN + "="*70)
        print(Fore.YELLOW + Style.BRIGHT + "GIT LOG --STAT (Commit changes statistics)")
        print(Fore.CYAN + "="*70 + Style.RESET_ALL + "\n")

        if not self._is_git_repo():
            print(Fore.RED + "Not a git repository. Please initialize git first.")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--stat", "--color=always"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout:
                # Process and colorize the output
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        # Colorize different parts of the git log
                        processed_line = line
                        import re
                        # Colorize commit hashes (7-character hex)
                        processed_line = re.sub(r'\b([0-9a-f]{7,})\b',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize file names in the stat output
                        processed_line = re.sub(r'(\S+\.(?:\w+))',
                                              Fore.CYAN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize number of insertions
                        processed_line = re.sub(r'(\d+)\s+insertions?',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL + " insertions?",
                                              processed_line)

                        # Colorize number of deletions
                        processed_line = re.sub(r'(\d+)\s+deletions?',
                                              Fore.RED + Style.BRIGHT + r'\1' + Style.RESET_ALL + " deletions?",
                                              processed_line)

                        # Print the processed line with colors
                        print(processed_line)
            else:
                print(Fore.YELLOW + "No commits found in the repository.")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running git command: {e}")
            if e.stderr:
                print(Fore.RED + f"Error details: {e.stderr}")
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")

        input(Fore.YELLOW + "\nPress Enter to continue...")

    def show_visual_branch_history(self):
        """Show visual branch history with comprehesive design and colors"""
        try:
            from colorama import Fore, Back, Style, init
            init(autoreset=True)  # Initialize colorama
        except ImportError:
            print("Colorama library not found. Please install it with: pip install colorama")
            print("\n" + "="*70)
            print("GIT LOG --ONELINE --GRAPH --ALL (Visual branch history)")
            print("="*70 + "\n")

            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                input("\nPress Enter to continue...")
                return

            self._run_command(["git", "log", "--oneline", "--graph", "--all"])
            input("\nPress Enter to continue...")
            return

        print("\n" + Fore.CYAN + "="*70)
        print(Fore.YELLOW + Style.BRIGHT + "GIT LOG --ONELINE --GRAPH --ALL (Visual branch history)")
        print(Fore.CYAN + "="*70 + Style.RESET_ALL + "\n")

        if not self._is_git_repo():
            print(Fore.RED + "Not a git repository. Please initialize git first.")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--graph", "--all", "--color=always"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout:
                # Process and colorize the output
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        # Colorize different parts of the git log
                        processed_line = line
                        # Colorize commit hashes (7-character hex)
                        import re
                        processed_line = re.sub(r'\b([0-9a-f]{7,})\b',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize branch names (words between *)
                        processed_line = re.sub(r'\*',
                                              Fore.RED + Style.BRIGHT + '*' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize branch references
                        processed_line = re.sub(r'(\(.*?\))',
                                              Fore.BLUE + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Print the processed line with colors
                        print(processed_line)
            else:
                print(Fore.YELLOW + "No commits found in the repository.")

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running git command: {e}")
            if e.stderr:
                print(Fore.RED + f"Error details: {e.stderr}")
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")

        input(Fore.YELLOW + "\nPress Enter to continue...")

    def show_shortlog(self):
        """Show condensed commit log by author with comprehensive design and colors"""
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)  # Initialize colorama
        except ImportError:
            print("Colorama library not found. Please install it with: pip install colorama")
            print("\n" + "="*70)
            print("GIT SHORTLOG (Condensed commit log by author)")
            print("="*70 + "\n")

            if not self._is_git_repo():
                print("Not a git repository. Please initialize git first.")
                input("\nPress Enter to continue...")
                return

            self._run_command(["git", "shortlog", "-s", "-n"])
            input("\nPress Enter to continue...")
            return

        print("\n" + Fore.CYAN + "="*70)
        print(Fore.YELLOW + Style.BRIGHT + "GIT SHORTLOG (Condensed commit log by author)")
        print(Fore.CYAN + "="*70 + Style.RESET_ALL + "\n")

        if not self._is_git_repo():
            print(Fore.RED + "Not a git repository. Please initialize git first.")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            return

        try:
            result = subprocess.run(
                ["git", "shortlog", "-s", "-n", "--color=always"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout:
                # Process and colorize the output
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        # Colorize different parts of the shortlog
                        processed_line = line
                        import re
                        # Colorize commit counts (numbers at the beginning of the line)
                        processed_line = re.sub(r'^(\s*\d+)',
                                              Fore.GREEN + Style.BRIGHT + r'\1' + Style.RESET_ALL,
                                              processed_line)

                        # Colorize author names
                        processed_line = re.sub(r'(\d+\s+)(.+)',
                                              r'\1' + Fore.CYAN + Style.BRIGHT + r'\2' + Style.RESET_ALL,
                                              processed_line)

                        # Print the processed line with colors
                        print(processed_line)
            else:
                print(Fore.YELLOW + "No commits found in the repository.")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error running git command: {e}")
            if e.stderr:
                print(Fore.RED + f"Error details: {e.stderr}")
        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")

        input(Fore.YELLOW + "\nPress Enter to continue...")

    def get_commit_history(self, limit=50, fetch_remote=True):
        """Get detailed commit history with metadata, with option to fetch remote commits first"""
        if fetch_remote:
            self.fetch_remote_commits()

        try:
            # Format: hash|author|date|message
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ai|%s"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )

            if not result.stdout:
                return []

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commit_hash, author, date, message = parts
                        # Parse and format date
                        try:
                            dt = datetime.fromisoformat(date.replace(' +', '+').replace(' -', '-'))
                            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except (ValueError, AttributeError):
                            formatted_date = date[:19]  # Fallback

                        commits.append({
                            'hash': commit_hash,
                            'author': author,
                            'date': formatted_date,
                            'message': message
                        })

            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history: {e}")
            return []
        except FileNotFoundError:
            print("Git not found in PATH")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def get_commit_details(self, commit_id, fetch_remote=False):
        """Get details for a specific commit with option to fetch remote commits first"""
        if fetch_remote:
            self.fetch_remote_commits()

        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ai|%s", commit_id],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )

            if not result.stdout:
                return None

            parts = result.stdout.strip().split('|', 3)
            if len(parts) == 4:
                commit_hash, author, date, message = parts
                try:
                    dt = datetime.fromisoformat(date.replace(' +', '+').replace(' -', '-'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, AttributeError):
                    formatted_date = date[:19]

                return {
                    'hash': commit_hash,
                    'author': author,
                    'date': formatted_date,
                    'message': message
                }
        except Exception as e:
            print(f"Error getting commit details: {e}")
            pass

        return None

    def verify_commit_exists(self, commit_id, fetch_remote=False):
        """Verify if a commit exists in the repository with option to fetch remote commits first"""
        if fetch_remote:
            self.fetch_remote_commits()

        result = subprocess.run(
            ["git", "cat-file", "-t", commit_id],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0

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
        """Run a shell command and display output with optional color support"""
        try:
            # Add color support to git commands if not already included
            if "git" in command and "--color" not in " ".join(command):
                command_with_color = command + ["--color=always"]
            else:
                command_with_color = command

            result = subprocess.run(
                command_with_color,
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
            print(f"Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("Git is not installed or not in PATH")
            return False