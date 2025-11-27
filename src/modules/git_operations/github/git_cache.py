"""
Git Cache Module
Runs git rm --cached -r to unstage the working directory and shows success/failure message.
The folder will be removed from git tracking but kept in your local directory.
"""
import subprocess
import os


class GitCache:
    """Simple git cache operations to unstage files"""
    
    def unstage_directory(self):
        """Run git rm --cached -r on working directory to unstage all files"""
        print("\n" + "="*70)
        print("  UNSTAGE WORKING DIRECTORY")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print(" Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        print("This will remove all files from git tracking (unstage) but keep them in your local directory.")
        print("Files will remain on disk but will no longer be tracked by git.")
        
        confirm = input("\nContinue with unstaging? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Run git rm --cached -r .
        try:
            result = subprocess.run(
                ["git", "rm", "--cached", "-r", "."],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                print(" SUCCESS! Working directory has been unstaged.")
                print(" All files remain in your local directory")
                print(" Files are no longer tracked by git")
                if result.stdout:
                    print(f"\nGit output:\n{result.stdout}")
            else:
                print(" FAILED to unstage directory.")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                    
        except FileNotFoundError:
            print(" Git is not installed or not in PATH")
        except Exception as e:
            print(f" Unexpected error: {e}")
        
        input("\nPress Enter to continue...")
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False