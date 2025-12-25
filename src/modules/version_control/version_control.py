"""
Version Control Module
Handles advanced Git workflows, merge conflict resolution, code review integration, and release management
"""
import sys
import subprocess
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class VersionControlTools:
    """Handles advanced version control tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def setup_gitflow(self) -> None:
        """Help set up GitFlow workflow"""
        print("\n" + "="*70)
        print("GITFLOW WORKFLOW SETUP")
        print("="*70)

        print("\nGitFlow is a branching model for Git that provides a structured workflow.")
        print("It uses two main branches: main (production) and develop (integration).")

        # Check if Git is available
        try:
            result = subprocess.run(['git', '--version'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Git is not installed or not in PATH")
                input("\nPress Enter to continue...")
                return
        except FileNotFoundError:
            print("⚠ Git is not installed or not in PATH")
            input("\nPress Enter to continue...")
            return

        # Check if GitFlow is available
        result = subprocess.run(['git', 'flow', 'version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("\nGitFlow is not installed.")
            print("Installation instructions:")
            print("  - Linux: sudo apt-get install git-flow")
            print("  - macOS: brew install git-flow")
            print("  - Windows: Download from GitHub or use Git Bash")
            print("\nAlternatively, you can use a GitFlow-like workflow manually.")

            setup_manual = input("\nSet up GitFlow-like branches manually? (y/n): ").lower()
            if setup_manual != 'y':
                input("\nPress Enter to continue...")
                return
        else:
            print("✓ GitFlow is installed")
            init_gitflow = input("Initialize GitFlow? (y/n): ").lower()
            if init_gitflow == 'y':
                try:
                    result = subprocess.run([
                        'git', 'flow', 'init', '-d'  # -d for default branch names
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        print("✓ GitFlow initialized successfully!")
                    else:
                        print(f"GitFlow initialization error: {result.stderr}")
                except Exception as e:
                    print(f"Error initializing GitFlow: {e}")

            input("\nPress Enter to continue...")
            return

        print("\nSetting up GitFlow-like branches manually...")
        try:
            # Create develop branch if it doesn't exist
            result = subprocess.run(['git', 'rev-parse', '--verify', 'develop'],
                                  capture_output=True, text=True)

            if result.returncode != 0:
                print("Creating develop branch...")
                subprocess.run(['git', 'checkout', '-b', 'develop'], check=True)
                print("✓ Created develop branch")
            else:
                print("✓ Develop branch already exists")

            # Set up branch protection patterns
            print("\nGitFlow branching model:")
            print("  - main: Production-ready code")
            print("  - develop: Integration branch")
            print("  - feature/*: Feature branches")
            print("  - release/*: Release preparation")
            print("  - hotfix/*: Hotfixes")

            print("\nExample commands:")
            print("  - Start feature: git checkout -b feature/new-feature develop")
            print("  - Finish feature: git checkout develop && git merge feature/new-feature")
            print("  - Start release: git checkout -b release/1.2.0 develop")
            print("  - Finish release: git checkout main && git merge release/1.2.0")

        except subprocess.CalledProcessError as e:
            print(f"Error setting up GitFlow branches: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        input("\nPress Enter to continue...")

    def resolve_merge_conflicts(self) -> None:
        """Help resolve merge conflicts"""
        print("\n" + "="*70)
        print("MERGE CONFLICT RESOLUTION")
        print("="*70)

        print("\nThis tool helps identify and resolve merge conflicts in your Git repository.")

        try:
            # Check if we're in a Git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Not in a Git repository!")
                input("\nPress Enter to continue...")
                return

            # Check for merge conflicts
            result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
                                  capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                conflict_files = result.stdout.strip().split('\n')
                print(f"\nFound {len(conflict_files)} file(s) with merge conflicts:")

                for file_path in conflict_files:
                    print(f"  - {file_path}")

                print("\nMerge conflict markers look like this:")
                print("  <<<<<<< HEAD")
                print("  Your changes")
                print("  =======")
                print("  Incoming changes")
                print("  >>>>>>> Branch name")

                print("\nResolution options:")
                print("  1. Open conflicted files in your editor")
                print("  2. Use 'git checkout --ours <file>' to keep your changes")
                print("  3. Use 'git checkout --theirs <file>' to accept incoming changes")
                print("  4. Manually edit files to merge changes as needed")

                # Suggest using VS Code, if available
                try:
                    result = subprocess.run(['code', '--version'],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        open_in_editor = input("\nOpen conflicted files in VS Code? (y/n): ").lower()
                        if open_in_editor == 'y':
                            files_str = ' '.join(conflict_files)
                            subprocess.run(['code', files_str])
                except:
                    pass  # VS Code not available

            else:
                print("✓ No merge conflicts found!")

        except subprocess.CalledProcessError as e:
            print(f"Error checking for conflicts: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        input("\nPress Enter to continue...")

    def integrate_code_reviews(self) -> None:
        """Help integrate with code review systems"""
        print("\n" + "="*70)
        print("CODE REVIEW INTEGRATION")
        print("="*70)

        print("\nThis tool provides guidance for integrating with code review systems")
        print("like GitHub Pull Requests, GitLab Merge Requests, or similar platforms.")

        print("\nSupported platforms:")
        print("  1. GitHub (via GitHub CLI)")
        print("  2. GitLab (via GitLab CLI)")
        print("  3. Bitbucket (via Bitbucket CLI)")

        try:
            choice = input("\nEnter choice (1-3) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_github_reviews()
            elif choice == "2":
                self._setup_gitlab_reviews()
            elif choice == "3":
                self._setup_bitbucket_reviews()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_github_reviews(self) -> None:
        """Setup GitHub code review integration"""
        print("\nSetting up GitHub code review integration...")

        # Check if GitHub CLI is available
        result = subprocess.run(['gh', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ GitHub CLI (gh) is not installed")
            print("Install from: https://cli.github.com/")
            print("\nAfter installation, authenticate with:")
            print("  gh auth login")
            return

        print("✓ GitHub CLI is installed")

        # Get current branch
        result = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True)
        current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"

        print(f"\nCurrent branch: {current_branch}")

        # Check if we're in a GitHub repository
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            remotes = result.stdout
            if 'github.com' in remotes:
                print("✓ Repository is connected to GitHub")

                print("\nCommon GitHub CLI commands for code review:")
                print(f"  - Create PR: gh pr create --title \"Your Title\" --body \"Description\"")
                print(f"  - List PRs: gh pr list")
                print(f"  - View PR: gh pr view")
                print(f"  - Check out PR: gh pr checkout <number>")
                print(f"  - Review PR: gh pr review <number> --comment --body \"Your review\"")

                create_pr = input(f"\nCreate a pull request for '{current_branch}'? (y/n): ").lower()
                if create_pr == 'y':
                    title = input("Enter PR title: ").strip()
                    if title:
                        body = input("Enter PR description (optional): ").strip()

                        cmd = ['gh', 'pr', 'create', '--title', title]
                        if body:
                            cmd.extend(['--body', body])

                        try:
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            if result.returncode == 0:
                                print(f"✓ Pull request created successfully!")
                                print(result.stdout)
                            else:
                                print(f"Error creating PR: {result.stderr}")
                        except Exception as e:
                            print(f"Error creating PR: {e}")
            else:
                print("⚠ Repository is not connected to GitHub")
        else:
            print("⚠ Could not get remote information")

    def _setup_gitlab_reviews(self) -> None:
        """Setup GitLab code review integration"""
        print("\nSetting up GitLab code review integration...")

        # Check if GitLab CLI is available
        result = subprocess.run(['glab', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ GitLab CLI (glab) is not installed")
            print("Install from: https://gitlab.com/gitlab-org/cli")
            print("\nAfter installation, authenticate with:")
            print("  glab auth login")
            return

        print("✓ GitLab CLI is installed")

        print("\nCommon GitLab CLI commands for code review:")
        print("  - Create MR: glab mr create")
        print("  - List MRs: glab mr list")
        print("  - View MR: glab mr view <id>")
        print("  - Checkout MR: glab mr checkout <id>")
        print("  - Merge MR: glab mr merge <id>")

    def _setup_bitbucket_reviews(self) -> None:
        """Setup Bitbucket code review integration"""
        print("\nSetting up Bitbucket code review integration...")

        print("Bitbucket doesn't have an official CLI that's as comprehensive as GitHub's or GitLab's.")
        print("\nConsider using: ")
        print("  - Atlassian CLI: https://developer.atlassian.com/server/confluence/command-line-interface/")
        print("  - Bitbucket's REST API")
        print("  - Third-party tools like 'bb-cli'")

        print("\nCommon Git commands for Bitbucket:")
        print("  - Push branch: git push origin your-branch-name")
        print("  - Create pull request via web interface: https://bitbucket.org/your-repo/pull-requests/new")

    def manage_releases(self) -> None:
        """Help with release management"""
        print("\n" + "="*70)
        print("RELEASE MANAGEMENT")
        print("="*70)

        print("\nThis tool helps with creating and managing releases.")

        try:
            # Check if we're in a Git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Not in a Git repository!")
                input("\nPress Enter to continue...")
                return

            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"

            print(f"\nCurrent branch: {current_branch}")

            # Get last few tags
            result = subprocess.run(['git', 'tag', '--sort=-v:refname'],
                                  capture_output=True, text=True)
            tags = result.stdout.strip().split('\n') if result.returncode == 0 and result.stdout.strip() else []

            print(f"\nRecent tags: {', '.join(tags[:5])}" if tags else "\nNo tags found")

            # Suggest next version number
            if tags:
                latest_tag = tags[0]
                print(f"\nLatest tag: {latest_tag}")

                # Simple version increment logic (semantic versioning)
                match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', latest_tag)
                if match:
                    major, minor, patch = match.groups()
                    next_patch = f"v{major}.{minor}.{int(patch) + 1}"
                    next_minor = f"v{major}.{int(minor) + 1}.0"
                    next_major = f"v{int(major) + 1}.0.0"

                    print(f"\nSuggested next versions:")
                    print(f"  - Patch: {next_patch}")
                    print(f"  - Minor: {next_minor}")
                    print(f"  - Major: {next_major}")

            # Create new tag
            create_tag = input("\nCreate a new tag? (y/n): ").lower()
            if create_tag == 'y':
                tag_name = input("Enter tag name (e.g., v1.2.3): ").strip()
                if tag_name:
                    message = input("Enter tag message (optional): ").strip()

                    cmd = ['git', 'tag']
                    if message:
                        cmd.extend(['-a', '-m', message])
                    cmd.append(tag_name)

                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✓ Tag '{tag_name}' created successfully!")

                        # Ask if they want to push the tag
                        push_tag = input("Push tag to remote repository? (y/n): ").lower()
                        if push_tag == 'y':
                            result = subprocess.run(['git', 'push', 'origin', tag_name],
                                                  capture_output=True, text=True)

                            if result.returncode == 0:
                                print(f"✓ Tag '{tag_name}' pushed successfully!")
                            else:
                                print(f"Error pushing tag: {result.stderr}")
                    else:
                        print(f"Error creating tag: {result.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"Error managing releases: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        input("\nPress Enter to continue...")

    def compare_branches(self) -> None:
        """Compare differences between branches"""
        print("\n" + "="*70)
        print("BRANCH COMPARISON")
        print("="*70)

        print("\nThis tool compares differences between two branches.")

        try:
            # Check if we're in a Git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Not in a Git repository!")
                input("\nPress Enter to continue...")
                return

            # Get all branches
            result = subprocess.run(['git', 'branch', '--all'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                branches = [b.strip().replace('remotes/origin/', '').replace('*', '').strip()
                           for b in result.stdout.split('\n') if b.strip() and not b.startswith('(HEAD detached')]

                local_branches = [b for b in branches if not b.startswith('remotes/')]

                print(f"\nAvailable branches: {', '.join(local_branches)}")

                source_branch = input("\nEnter source branch: ").strip()
                target_branch = input("Enter target branch: ").strip()

                if source_branch and target_branch:
                    # Compare the branches
                    print(f"\nComparing {source_branch} → {target_branch}:")

                    # Get commits unique to source branch
                    result = subprocess.run([
                        'git', 'log', '--oneline', f'{target_branch}..{source_branch}'
                    ], capture_output=True, text=True)

                    if result.returncode == 0 and result.stdout:
                        commits = result.stdout.strip().split('\n')
                        print(f"\nCommits in '{source_branch}' but not in '{target_branch}' ({len(commits)}):")
                        for commit in commits[:20]:  # Show first 20
                            print(f"  {commit}")
                        if len(commits) > 20:
                            print(f"  ... and {len(commits) - 20} more commits")
                    else:
                        print(f"No commits in '{source_branch}' that are not in '{target_branch}'")

                    # Show file changes
                    result = subprocess.run([
                        'git', 'diff', '--name-only', target_branch, source_branch
                    ], capture_output=True, text=True)

                    if result.returncode == 0 and result.stdout:
                        files = result.stdout.strip().split('\n')
                        print(f"\nFiles changed ({len(files)}):")
                        for file_path in files[:30]:  # Show first 30
                            print(f"  {file_path}")
                        if len(files) > 30:
                            print(f"  ... and {len(files) - 30} more files")
                    else:
                        print("No files changed between branches")

            else:
                print("Could not retrieve branch information")

        except subprocess.CalledProcessError as e:
            print(f"Error comparing branches: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        input("\nPress Enter to continue...")
class VersionControlMenu(Menu):
    """Menu for version control tools"""

    def __init__(self):
        self.version_control = VersionControlTools()
        super().__init__("Advanced Version Control Tools")

    def setup_items(self) -> None:
        """Setup menu items for version control tools"""
        self.items = [
            MenuItem("Setup GitFlow Workflow", self.version_control.setup_gitflow),
            MenuItem("Resolve Merge Conflicts", self.version_control.resolve_merge_conflicts),
            MenuItem("Integrate Code Reviews", self.version_control.integrate_code_reviews),
            MenuItem("Manage Releases", self.version_control.manage_releases),
            MenuItem("Compare Branches", self.version_control.compare_branches),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]