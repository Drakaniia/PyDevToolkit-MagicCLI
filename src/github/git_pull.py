"""
Git Pull Module
Handles pull operations from remote repository
"""
import subprocess
import sys
import threading
import time


class GitPull:
    """Handles git pull operations"""

    def __init__(self):
        self.loading_active = False
        self.loading_thread = None

    def _start_loading(self, message="🔄 Loading"):
        """Start loading animation in a separate thread"""
        self.loading_active = True
        self.loading_thread = threading.Thread(target=self._loading_animation, args=(message,))
        self.loading_thread.start()

    def _stop_loading(self):
        """Stop the loading animation"""
        self.loading_active = False
        if self.loading_thread:
            self.loading_thread.join()

    def _loading_animation(self, message):
        """Display loading animation"""
        chars = "|/-\\"
        idx = 0
        while self.loading_active:
            sys.stdout.write(f"\r{message} {chars[idx % len(chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

    def pull(self):
        """Pull from remote repository"""
        print("\n" + "="*70)
        print("⬇️  GIT PULL")
        print("="*70 + "\n")

        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        # Check if remote exists
        if not self._has_remote():
            print("❌ No remote repository configured.")
            print("💡 Use 'Initialize Git & Push to GitHub' to set up remote.")
            input("\nPress Enter to continue...")
            return False

        # Sync first by fetching
        print("🔄 Syncing with remote...")
        self._start_loading("🔄 Fetching latest changes")
        fetch_success = self.fetch()
        self._stop_loading()

        if not fetch_success:
            print("\n❌ Sync failed. Cannot continue with pull.")
            input("\nPress Enter to continue...")
            return False

        print("\n✅ Sync completed successfully!")

        # Ask user if they want to proceed with pull
        response = input("\nDo you want to pull the changes now? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Pull operation cancelled by user.")
            input("\nPress Enter to continue...")
            return False

        print("\n🔄 Pulling changes from remote...")
        success = self._run_command(["git", "pull"])

        if success:
            print("\n✅ Successfully pulled from remote!")
        else:
            print("\n❌ Pull failed. Check your network connection and remote configuration.")

        input("\nPress Enter to continue...")
        return success

    def pull_with_rebase(self):
        """Pull with rebase strategy"""
        print("\n" + "="*70)
        print("⬇️  GIT PULL (with rebase)")
        print("="*70 + "\n")

        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False

        # Sync first by fetching
        print("🔄 Syncing with remote...")
        self._start_loading("🔄 Fetching latest changes")
        fetch_success = self.fetch()
        self._stop_loading()

        if not fetch_success:
            print("\n❌ Sync failed. Cannot continue with pull.")
            input("\nPress Enter to continue...")
            return False

        print("\n✅ Sync completed successfully!")

        # Ask user if they want to proceed with pull
        response = input("\nDo you want to pull with rebase? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Pull operation cancelled by user.")
            input("\nPress Enter to continue...")
            return False

        print("🔄 Pulling with rebase...")
        success = self._run_command(["git", "pull", "--rebase"])

        if success:
            print("\n✅ Successfully pulled with rebase!")

        input("\nPress Enter to continue...")
        return success

    def fetch(self):
        """Fetch from remote without merging"""
        try:
            result = subprocess.run(
                ["git", "fetch"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False

    def get_remote_info(self):
        """Get information about remote repository"""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _has_remote(self):
        """Check if remote repository is configured"""
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def _run_command(self, command):
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False