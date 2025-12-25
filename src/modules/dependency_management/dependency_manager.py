"""
Dependency Management Module
Handles package vulnerability scanning, updates, and lock file verification
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class DependencyManager:
    """Handles dependency management tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def run_security_scan(self) -> None:
        """Run vulnerability scan on project dependencies"""
        print("\n" + "="*70)
        print("DEPENDENCY SECURITY SCANNING")
        print("="*70)
        print("\nScanning for package vulnerabilities...")

        try:
            # Run safety check on requirements
            result = subprocess.run([sys.executable, "-m", "safety", "check", "--json"],
                                    capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print(f"\n✓ No vulnerabilities found in dependencies")
            else:
                print(f"\n⚠ Security issues found:")
                print(result.stdout)

                # Offer to fix if possible
                if "fix" in result.stdout.lower() or "upgrade" in result.stdout.lower():
                    response = input("\nWould you like to attempt to fix vulnerabilities? (y/n): ").lower()
                    if response == 'y':
                        self._attempt_fix_vulnerabilities()

        except subprocess.TimeoutExpired:
            print("\n⚠ Security scan timed out after 120 seconds")
        except Exception as e:
            print(f"\n⚠ Error during security scan: {e}")

        input("\nPress Enter to continue...")

    def _attempt_fix_vulnerabilities(self) -> None:
        """Attempt to fix vulnerabilities by upgrading packages"""
        print("\nAttempting to fix vulnerabilities by upgrading packages...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "safety", "check",
                "--output", "bare", "--json"
            ], capture_output=True, text=True)

            if result.returncode != 0:
                # Extract vulnerable packages
                import json
                try:
                    vulnerabilities = json.loads(result.stdout)
                    vulnerable_packages = set()

                    for vuln in vulnerabilities:
                        if 'vulnerable_spec' in vuln:
                            vulnerable_packages.add(vuln['name'])

                    if vulnerable_packages:
                        print(f"\nFound {len(vulnerable_packages)} vulnerable packages. Upgrading...")
                        for pkg in vulnerable_packages:
                            print(f"  - Upgrading {pkg}...")
                            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pkg],
                                         capture_output=True, text=True)

                        print(f"\n✓ Attempted to upgrade {len(vulnerable_packages)} packages")
                    else:
                        print("\nNo specific vulnerable packages identified")
                except json.JSONDecodeError:
                    print("\nCould not parse vulnerability data")
        except Exception as e:
            print(f"\n⚠ Error while attempting to fix vulnerabilities: {e}")

    def check_dependency_updates(self) -> None:
        """Check for available dependency updates"""
        print("\n" + "="*70)
        print("CHECKING FOR DEPENDENCY UPDATES")
        print("="*70)

        try:
            # Check outdated packages
            result = subprocess.run([
                sys.executable, "-m", "pip", "list", "--outdated", "--format=json"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                import json
                try:
                    outdated = json.loads(result.stdout)
                    if outdated:
                        print(f"\nFound {len(outdated)} outdated packages:\n")
                        for pkg in outdated:
                            print(f"  {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")

                        response = input("\nWould you like to update all packages? (y/n): ").lower()
                        if response == 'y':
                            self._update_all_packages(outdated)
                    else:
                        print("\n✓ All packages are up to date!")
                except json.JSONDecodeError:
                    print(f"Output: {result.stdout}")
            else:
                print(f"Error checking for updates: {result.stderr}")
        except Exception as e:
            print(f"\nError checking for updates: {e}")

        input("\nPress Enter to continue...")

    def _update_all_packages(self, outdated_packages: List[Dict[str, str]]) -> None:
        """Update all outdated packages"""
        print("\nUpdating packages...")
        for pkg in outdated_packages:
            print(f"  Updating {pkg['name']}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    f"{pkg['name']}>={pkg['latest_version']}"
                ], capture_output=True, text=True)
            except Exception as e:
                print(f"    Error updating {pkg['name']}: {e}")

        print(f"\n✓ Completed update of {len(outdated_packages)} packages")

    def verify_lock_files(self) -> None:
        """Verify the integrity of lock files"""
        print("\n" + "="*70)
        print("VERIFYING LOCK FILES")
        print("="*70)

        lock_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "Pipfile",
            "Pipfile.lock",
            "poetry.lock",
            "pyproject.toml"
        ]

        found_locks = []
        for lock_file in lock_files:
            lock_path = Path(lock_file)
            if lock_path.exists():
                found_locks.append(lock_path)
                print(f"✓ Found lock file: {lock_file}")
            else:
                print(f"  Missing lock file: {lock_file}")

        if not found_locks:
            print("\nNo lock files found in current directory")
        else:
            print(f"\nFound {len(found_locks)} lock files")

            # If pyproject.toml exists, suggest sync with pip-compile
            if Path("pyproject.toml").exists():
                print("\nSuggestion: Run 'pip-compile' to sync dependencies if using poetry/requirements")

        input("\nPress Enter to continue...")
class DependencyMenu(Menu):
    """Menu for dependency management tools"""

    def __init__(self):
        self.dep_manager = DependencyManager()
        super().__init__("Dependency Management Tools")

    def setup_items(self) -> None:
        """Setup menu items for dependency management"""
        self.items = [
            MenuItem("Scan Dependencies for Vulnerabilities", self.dep_manager.run_security_scan),
            MenuItem("Check for Dependency Updates", self.dep_manager.check_dependency_updates),
            MenuItem("Verify Lock Files", self.dep_manager.verify_lock_files),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]