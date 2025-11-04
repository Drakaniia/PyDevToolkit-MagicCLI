"""
Git Cache Module
Handles caching of git state and recovery from accidental commits of sensitive files
"""
import subprocess
import os
from pathlib import Path
from automation.menu import Menu, MenuItem


class GitCache:
    """Handles git caching operations and recovery from accidental commits"""
    
    def __init__(self):
        self.sensitive_patterns = [
            '.env',
            '.env.*',
            'node_modules/',
            '__pycache__/',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db',
            '*.log',
            'dist/',
            'build/',
            '.vscode/',
            '.idea/',
            '*.key',
            '*.pem',
            'config.json',
            'secrets.*'
        ]
    
    def show_cache_menu(self):
        """Display the git cache management menu"""
        cache_menu = GitCacheMenu()
        cache_menu.run()
    
    def create_cache_point(self):
        """Create a cache point and push directory directly"""
        print("\n" + "="*70)
        print("💾 GIT CACHE & DIRECT PUSH")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return None
        
        # Show loading animation
        self._show_loading("Preparing cache operation...")
        
        # Generate cache name
        from datetime import datetime
        cache_name = f"cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create a tag for the cache point
        self._show_loading("Creating cache point...")
        if self._run_command_silent(["git", "tag", f"cache/{cache_name}"]):
            print(f"✅ Cache point '{cache_name}' created successfully!")
            self._show_cache_confirmation(cache_name)
            self._direct_push()
        else:
            print("❌ Failed to create cache point.")
            input("\nPress Enter to continue...")
        
        return None
    
    def list_cache_points(self):
        """List all available cache points"""
        print("\n" + "="*70)
        print("📋 AVAILABLE CACHE POINTS")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository.")
            input("\nPress Enter to continue...")
            return
        
        result = subprocess.run(
            ["git", "tag", "-l", "cache/*"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout.strip():
            cache_points = result.stdout.strip().split('\n')
            print("Available cache points:")
            for i, point in enumerate(cache_points, 1):
                clean_name = point.replace('cache/', '')
                print(f"{i}. {clean_name}")
        else:
            print("No cache points found.")
        
        input("\nPress Enter to continue...")
    
    def restore_from_cache(self):
        """Restore repository to a cache point"""
        print("\n" + "="*70)
        print("🔄 RESTORE FROM CACHE POINT")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository.")
            input("\nPress Enter to continue...")
            return
        
        # List cache points
        result = subprocess.run(
            ["git", "tag", "-l", "cache/*"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if not result.stdout.strip():
            print("No cache points found. Create a cache point first.")
            input("\nPress Enter to continue...")
            return
        
        cache_points = result.stdout.strip().split('\n')
        print("Available cache points:")
        for i, point in enumerate(cache_points, 1):
            clean_name = point.replace('cache/', '')
            print(f"{i}. {clean_name}")
        
        try:
            choice = int(input("\nSelect cache point number: ")) - 1
            if 0 <= choice < len(cache_points):
                selected_point = cache_points[choice]
                
                print(f"\n⚠️  WARNING: This will reset your repository to '{selected_point.replace('cache/', '')}'")
                print("All changes after this point will be lost!")
                confirm = input("Type 'YES' to confirm: ")
                
                if confirm == 'YES':
                    if self._run_command(["git", "reset", "--hard", selected_point]):
                        print(f"✅ Successfully restored to cache point '{selected_point.replace('cache/', '')}'")
                    else:
                        print("❌ Failed to restore from cache point.")
                else:
                    print("Operation cancelled.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        
        input("\nPress Enter to continue...")
    
    def remove_sensitive_files(self):
        """Remove sensitive files from git history"""
        print("\n" + "="*70)
        print("🔒 REMOVE SENSITIVE FILES FROM HISTORY")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository.")
            input("\nPress Enter to continue...")
            return
        
        print("This will help remove sensitive files from git history.")
        print("Common sensitive patterns:")
        for pattern in self.sensitive_patterns:
            print(f"  - {pattern}")
        
        print("\nOptions:")
        print("1. Remove by file pattern")
        print("2. Remove specific file")
        print("3. Auto-detect and remove common sensitive files")
        
        try:
            choice = int(input("\nSelect option (1-3): "))
            
            if choice == 1:
                self._remove_by_pattern()
            elif choice == 2:
                self._remove_specific_file()
            elif choice == 3:
                self._auto_remove_sensitive()
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")
    
    def _remove_by_pattern(self):
        """Remove files by pattern from git history"""
        pattern = input("Enter file pattern (e.g., *.env, node_modules/): ").strip()
        if not pattern:
            print("No pattern provided.")
            return
        
        print(f"\n⚠️  WARNING: This will remove all files matching '{pattern}' from git history!")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm == 'YES':
            # Use git filter-branch to remove files
            cmd = ["git", "filter-branch", "--force", "--index-filter", 
                   f"git rm --cached --ignore-unmatch '{pattern}'", 
                   "--prune-empty", "--tag-name-filter", "cat", "--", "--all"]
            
            if self._run_command(cmd):
                print(f"✅ Successfully removed files matching '{pattern}' from history.")
                print("⚠️  Remember to force push to update remote repository!")
            else:
                print("❌ Failed to remove files from history.")
    
    def _remove_specific_file(self):
        """Remove a specific file from git history"""
        filename = input("Enter filename to remove: ").strip()
        if not filename:
            print("No filename provided.")
            return
        
        print(f"\n⚠️  WARNING: This will remove '{filename}' from git history!")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm == 'YES':
            cmd = ["git", "filter-branch", "--force", "--index-filter", 
                   f"git rm --cached --ignore-unmatch '{filename}'", 
                   "--prune-empty", "--tag-name-filter", "cat", "--", "--all"]
            
            if self._run_command(cmd):
                print(f"✅ Successfully removed '{filename}' from history.")
                print("⚠️  Remember to force push to update remote repository!")
            else:
                print("❌ Failed to remove file from history.")
    
    def _auto_remove_sensitive(self):
        """Automatically detect and remove sensitive files"""
        print("Scanning for sensitive files in git history...")
        
        # Check for sensitive files in current directory
        found_files = []
        for pattern in self.sensitive_patterns:
            if '*' in pattern or '/' in pattern:
                continue  # Skip patterns for now, focus on exact matches
            
            if Path(pattern).exists():
                found_files.append(pattern)
        
        if not found_files:
            print("No sensitive files detected in current directory.")
            return
        
        print(f"\nFound {len(found_files)} potentially sensitive files:")
        for file in found_files:
            print(f"  - {file}")
        
        print(f"\n⚠️  WARNING: This will remove these files from git history!")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm == 'YES':
            for file in found_files:
                cmd = ["git", "filter-branch", "--force", "--index-filter", 
                       f"git rm --cached --ignore-unmatch '{file}'", 
                       "--prune-empty", "--tag-name-filter", "cat", "--", "--all"]
                
                print(f"Removing {file}...")
                self._run_command(cmd)
            
            print("✅ Sensitive files removal completed.")
            print("⚠️  Remember to force push to update remote repository!")
    
    def update_gitignore(self):
        """Update .gitignore with common sensitive patterns"""
        print("\n" + "="*70)
        print("📝 UPDATE .GITIGNORE")
        print("="*70 + "\n")
        
        gitignore_path = Path('.gitignore')
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        else:
            current_content = ""
        
        new_patterns = []
        for pattern in self.sensitive_patterns:
            if pattern not in current_content:
                new_patterns.append(pattern)
        
        if new_patterns:
            print("Adding the following patterns to .gitignore:")
            for pattern in new_patterns:
                print(f"  + {pattern}")
            
            confirm = input("\nAdd these patterns? (y/n): ").lower()
            if confirm == 'y':
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write("\n# Auto-added sensitive file patterns\n")
                    for pattern in new_patterns:
                        f.write(f"{pattern}\n")
                
                print("✅ .gitignore updated successfully!")
            else:
                print("Operation cancelled.")
        else:
            print("All sensitive patterns are already in .gitignore.")
        
        input("\nPress Enter to continue...")
    
    def _show_cache_confirmation(self, cache_name):
        """Show confirmation that repository is successfully cached"""
        print("\n" + "🎉" * 25)
        print("✅ REPOSITORY SUCCESSFULLY CACHED!")
        print("🎉" * 25)
        print(f"\n📍 Current Directory: {os.getcwd()}")
        print(f"💾 Cache Point: {cache_name}")
        print(f"🕒 Timestamp: {self._get_timestamp()}")
        print("\n" + "="*70)
        print("🚀 Now pushing changes to remote repository...")
        print("="*70 + "\n")
    
    def _direct_push(self):
        """Directly push current directory state"""
        try:
            # Show loading while adding files
            self._show_loading("Adding files to git...")
            
            # Add all files
            if not self._run_command_silent(["git", "add", "."]):
                print("❌ Failed to add files to git")
                input("\nPress Enter to continue...")
                return False
            
            # Check if there are changes to commit
            if not self._has_uncommitted_changes():
                print("✅ No changes to commit - repository is up to date!")
                input("\nPress Enter to continue...")
                return True
            
            # Show loading while committing
            self._show_loading("Committing changes...")
            
            # Commit changes
            commit_message = f"🔄 Cache point commit - {self._get_timestamp()}"
            if not self._run_command_silent(["git", "commit", "-m", commit_message]):
                print("❌ Failed to commit changes")
                input("\nPress Enter to continue...")
                return False
            
            # Show loading while pushing
            self._show_loading("Pushing to remote repository...")
            
            # Push to remote
            if self._run_command_silent(["git", "push"]):
                print("\n" + "🎉" * 25)
                print("✅ SUCCESS! DIRECTORY CACHED & PUSHED!")
                print("🎉" * 25)
                print("\n🔒 Your repository has been cached safely!")
                print("💾 Cache point preserved for recovery if needed")
                print("🚀 All changes pushed to remote repository")
                print("\n" + "="*70)
            else:
                print("⚠️  Changes committed locally but failed to push to remote")
                print("You may need to push manually or check remote configuration")
            
            input("\nPress Enter to continue...")
            return True
            
        except Exception as e:
            print(f"❌ Error during push operation: {e}")
            input("\nPress Enter to continue...")
            return False
    
    
    def _run_command_silent(self, command):
        """Run a command silently and return success status"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _show_loading(self, message):
        """Show loading animation"""
        import time
        import sys
        
        print(f"\n{message}")
        
        # Loading animation
        for i in range(3):
            for char in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
                sys.stdout.write(f"\r{char} Loading...")
                sys.stdout.flush()
                time.sleep(0.1)
        
        # Clear loading line
        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()
    
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
    
    def _has_uncommitted_changes(self):
        """Check if there are uncommitted changes"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
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
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False


class GitCacheMenu(Menu):
    """Menu for git cache operations"""
    
    def __init__(self):
        self.git_cache = GitCache()
        super().__init__("💾 Git Cache & Security Operations")
    
    def setup_items(self):
        """Setup menu items for git cache operations"""
        self.items = [
            MenuItem("🚀 Cache Directory & Push to Remote", lambda: self.git_cache.create_cache_point()),
            MenuItem("📋 List Cache Points", lambda: self.git_cache.list_cache_points()),
            MenuItem("🔄 Restore from Cache", lambda: self.git_cache.restore_from_cache()),
            MenuItem("🗑️  Remove Sensitive Files from History", lambda: self.git_cache.remove_sensitive_files()),
            MenuItem("📝 Update .gitignore", lambda: self.git_cache.update_gitignore()),
            MenuItem("🔙 Back to Git Menu", lambda: "exit")
        ]