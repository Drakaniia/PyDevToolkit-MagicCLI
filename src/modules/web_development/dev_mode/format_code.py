"""
automation/dev_mode/format_code.py
Simple Prettier setup - installs once and configures format-on-save
FIXED: Searches parent folders for .code-workspace file and modifies it
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from ._base import DevModeCommand
from core.loading import LoadingSpinner, loading_animation
class FormatCodeCommand(DevModeCommand):
    """Command to setup Prettier with format-on-save"""

    label = "Setup Prettier (Format on Save)"
    description = "Install and configure Prettier for auto-formatting"

    # Required VS Code workspace settings
    REQUIRED_VSCODE_SETTINGS = {
        "editor.formatOnSave": True,
        "editor.formatOnPaste": True,
        "editor.formatOnType": True,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "[javascript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[javascriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[json]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[html]": {
            "editor.defaultFormatter": "vscode.html-language-features"
        },
        "[css]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[scss]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[vue]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[markdown]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        }
    }

    def run(self, interactive: bool = True, **kwargs) -> any:
        """Execute Prettier setup"""
        if interactive:
            return self._interactive_setup()
        else:
            return self._noninteractive_setup(**kwargs)

    def _interactive_setup(self):
        """Interactive Prettier setup"""
        current_dir = Path.cwd()

        print("\n" + "="*70)
        print(" PRETTIER SETUP (Format on Save)")
        print("="*70 + "\n")

        # Check if package.json exists
        package_json = current_dir / 'package.json'
        if not package_json.exists():
            print("  No package.json found")
            create = input("Create package.json? (y/n): ").strip().lower()
            if create == 'y':
                if not self._init_package_json(current_dir):
                    input("\nPress Enter to continue...")
                    return
                print()
            else:
                print("\n Operation cancelled - package.json is required")
                input("\nPress Enter to continue...")
                return

        # Check if Prettier is already installed
        prettier_installed = self._check_prettier_installed(current_dir)

        if prettier_installed:
            print(" Prettier is already installed\n")
        else:
            print("  Prettier is not installed yet\n")
            print(" Installing Prettier...")
            print("="*70 + "\n")

            if not self._install_prettier_with_progress(current_dir):
                print("\n Failed to install Prettier")
                input("\nPress Enter to continue...")
                return

            print("\n Prettier installed successfully!\n")

        # Create/update configuration files
        print(" Setting up configuration files...\n")

        # 1. Create .prettierrc
        if not self._check_prettier_config(current_dir):
            self._create_prettier_config(current_dir)
            print(" Created .prettierrc")
        else:
            print(" .prettierrc already exists")

        # 2. Create .prettierignore
        self._create_prettier_ignore(current_dir)
        print(" Created/Updated .prettierignore")

        # 3. Configure VS Code workspace settings (searches parent folders)
        workspace_configured = self._configure_vscode_workspace_settings(current_dir)

        # 4. Add format script to package.json
        self._add_format_script(current_dir)
        print(" Added format script to package.json")

        print("\n" + "="*70)
        print(" PRETTIER SETUP COMPLETE!")
        print("="*70)
        print("\n What was configured:")
        print("  • Prettier installed as dev dependency")
        print("  • .prettierrc configuration file")
        print("  • .prettierignore (excludes node_modules, etc.)")
        if workspace_configured:
            print("  • .code-workspace settings ")
        print("  • npm run format script added")

        print("\n How to use:")
        print("  • Auto-format: Just press Ctrl+S (save) in VS Code")
        print("  • Manual format: npm run format")

        print("\n  FINAL STEPS:")
        print("="*70)

        if workspace_configured:
            print("\n1⃣  Reload VS Code Window:")
            print("     • Press Ctrl+Shift+P")
            print("     • Type: 'Reload Window'")
            print("     • Press Enter")
            print("\n2⃣  Install Prettier VS Code Extension (if not installed):")
            print("     • Press Ctrl+Shift+X (Extensions)")
            print("     • Search: 'Prettier - Code formatter'")
            print("     • Click Install")
            print("\n3⃣  Test it:")
            print("     • Open any file")
            print("     • Write messy code")
            print("     • Press Ctrl+S → Auto-format! ")
        else:
            print("\n  NO WORKSPACE FILE FOUND!")
            print("\n   The .code-workspace file could not be found.")
            print("   Prettier is installed, but auto-format on save won't work")
            print("   until you configure your workspace.")
            print("\n    How to fix:")
            print("      1. In VS Code: File → Save Workspace As...")
            print("      2. Save as '<project-name>.code-workspace' in parent folder")
            print("      3. Run this setup again")
            print("\n    Alternative (manual):")
            print("      1. Install Prettier extension in VS Code")
            print("      2. Open Settings (Ctrl+,)")
            print("      3. Enable: 'Format On Save'")
            print("      4. Set Prettier as default formatter")

        print("="*70 + "\n")

        input("Press Enter to continue...")

    def _noninteractive_setup(self, auto_install: bool = True):
        """Non-interactive setup"""
        current_dir = Path.cwd()

        if auto_install and not self._check_prettier_installed(current_dir):
            if not self._install_prettier_with_progress(current_dir):
                raise RuntimeError("Failed to install Prettier")

        self._create_prettier_config(current_dir)
        self._create_prettier_ignore(current_dir)
        self._configure_vscode_workspace_settings(current_dir)
        self._add_format_script(current_dir)

    # ============================================================
    # VS Code Workspace Configuration
    # ============================================================

    def _configure_vscode_workspace_settings(self, project_dir: Path) -> bool:
        """
        Find and configure VS Code workspace file
        Searches current directory, parent, and grandparent for .code-workspace

        Args:
            project_dir: Starting project directory

        Returns:
            True if workspace file was found and configured
        """
        print("\n Searching for VS Code workspace file...")
        print("="*70)

        # Find .code-workspace file (searches up to 3 levels)
        workspace_file = self._find_workspace_file(project_dir, max_depth=3)

        if not workspace_file:
            print("     No .code-workspace file found")
            print("\n    Searched in:")
            print(f"      • {project_dir}")
            print(f"      • {project_dir.parent}")
            print(f"      • {project_dir.parent.parent}")
            print("\n    Cannot configure workspace settings")
            print("    Solution: Open your project as a workspace in VS Code")
            print("="*70 + "\n")
            return False

        print(f"    Found workspace file: {workspace_file.name}")
        print(f"      Location: {workspace_file.parent}")

        # Load existing workspace data
        workspace_data = self._load_workspace_file(workspace_file)

        if workspace_data is None:
            print("    Failed to load workspace file")
            print("="*70 + "\n")
            return False

        # Merge with required settings
        workspace_data = self._merge_workspace_settings(workspace_data)

        # Write back to workspace file
        success = self._write_workspace_file(workspace_file, workspace_data)

        print("="*70)
        if success:
            print(" Workspace settings configured successfully!")
            print(f" File: {workspace_file}")
        else:
            print(" Failed to configure workspace settings")
        print("="*70 + "\n")

        return success

    def _find_workspace_file(self, start_dir: Path, max_depth: int = 3) -> Optional[Path]:
        """
        Search for .code-workspace file in current directory, parent, and grandparent

        Args:
            start_dir: Starting directory
            max_depth: Maximum number of parent directories to search (3 = current, parent, grandparent)

        Returns:
            Path to workspace file or None
        """
        current = start_dir

        for depth in range(max_depth):
            print(f"   Searching: {current}")

            # Search for .code-workspace files in current directory
            workspace_files = list(current.glob('*.code-workspace'))

            if workspace_files:
                return workspace_files[0]

            # Move to parent directory
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent

        return None

    def _load_workspace_file(self, workspace_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load .code-workspace file

        Args:
            workspace_file: Path to workspace file

        Returns:
            Workspace data dictionary or None if failed
        """
        try:
            with open(workspace_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

                if not content:
                    # Empty file - create minimal structure
                    return {
                        "folders": [{"path": "."}],
                        "settings": {}
                    }

                data = json.loads(content)

                # Ensure settings section exists
                if "settings" not in data:
                    data["settings"] = {}

                existing_count = len(data.get('settings', {}))
                print(f"      Loaded {existing_count} existing settings")
                return data

        except json.JSONDecodeError as e:
            print(f"        Invalid JSON: {e}")
            return None
        except Exception as e:
            print(f"        Error: {e}")
            return None

    def _merge_workspace_settings(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge required settings into workspace data

        Args:
            workspace_data: Current workspace data

        Returns:
            Updated workspace data
        """
        print("\n    Merging settings...")

        if "settings" not in workspace_data:
            workspace_data["settings"] = {}

        settings = workspace_data["settings"]
        added = 0
        updated = 0

        for key, value in self.REQUIRED_VSCODE_SETTINGS.items():
            if key not in settings:
                added += 1
                settings[key] = value
            elif settings[key] != value:
                updated += 1
                settings[key] = value

        if added:
            print(f"       Added {added} new settings")
        if updated:
            print(f"       Updated {updated} existing settings")
        if not added and not updated:
            print("       All required settings already configured")

        return workspace_data

    def _write_workspace_file(self, workspace_file: Path, workspace_data: Dict[str, Any]) -> bool:
        """
        Write workspace data to file

        Args:
            workspace_file: Path to workspace file
            workspace_data: Workspace data to write

        Returns:
            True if successful
        """
        print(f"\n    Writing to {workspace_file.name}...")

        try:
            json_content = json.dumps(
                workspace_data,
                indent=2,
                ensure_ascii=False
            )

            with open(workspace_file, 'w', encoding='utf-8') as f:
                f.write(json_content)
                f.write('\n')

            print(f"       Updated successfully")
            return True

        except Exception as e:
            print(f"       Failed: {e}")
            return False

    # ============================================================
    # Helper Methods
    # ============================================================

    def _check_prettier_installed(self, project_dir: Path) -> bool:
        """Check if Prettier is installed"""
        package_json = project_dir / 'package.json'

        if not package_json.exists():
            return False

        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            dev_deps = data.get('devDependencies', {})
            deps = data.get('dependencies', {})

            return 'prettier' in dev_deps or 'prettier' in deps
        except Exception:
            return False

    def _install_prettier_with_progress(self, project_dir: Path) -> bool:
        """Install Prettier with progress"""
        pkg_manager = self._detect_package_manager(project_dir)

        if pkg_manager == 'npm':
            cmd = ['npm', 'install', '--save-dev', 'prettier']
        elif pkg_manager == 'yarn':
            cmd = ['yarn', 'add', '--dev', 'prettier']
        elif pkg_manager == 'pnpm':
            cmd = ['pnpm', 'add', '--save-dev', 'prettier']
        else:
            cmd = ['npm', 'install', '--save-dev', 'prettier']

        print(f"$ {' '.join(cmd)}")

        try:
            use_shell = sys.platform == 'win32'

            with LoadingSpinner(f"Installing Prettier with {pkg_manager}", style='dots'):
                if use_shell:
                    result = subprocess.run(
                        ' '.join(cmd),
                        cwd=project_dir,
                        shell=True,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                else:
                    result = subprocess.run(
                        cmd,
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )

            if result.returncode == 0:
                print(" Prettier installed successfully!")
                return True
            else:
                print(f" Installation failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"\n Error: {e}")
            return False

    def _init_package_json(self, project_dir: Path) -> bool:
        """Initialize package.json"""
        print(" Creating package.json...\n")

        try:
            use_shell = sys.platform == 'win32'

            subprocess.run(
                ['npm', 'init', '-y'] if not use_shell else 'npm init -y',
                cwd=project_dir,
                check=True,
                capture_output=True,
                shell=use_shell,
                encoding='utf-8',
                errors='replace'
            )

            print(" package.json created")
            return True
        except subprocess.CalledProcessError:
            print(" Failed to create package.json")
            return False

    def _detect_package_manager(self, project_dir: Path) -> str:
        """Detect package manager from lock files"""
        if (project_dir / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (project_dir / 'yarn.lock').exists():
            return 'yarn'
        else:
            return 'npm'

    def _check_prettier_config(self, project_dir: Path) -> bool:
        """Check if Prettier config exists"""
        config_files = [
            '.prettierrc',
            '.prettierrc.json',
            '.prettierrc.js',
        ]
        return any((project_dir / config).exists() for config in config_files)

    def _create_prettier_config(self, project_dir: Path):
        """Create .prettierrc configuration"""
        config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False,
            "arrowParens": "avoid",
            "endOfLine": "auto"
        }

        config_file = project_dir / '.prettierrc'

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"  Could not create .prettierrc: {e}")

    def _create_prettier_ignore(self, project_dir: Path):
        """Create .prettierignore file"""
        ignore_patterns = [
            "node_modules/",
            "dist/",
            "build/",
            ".next/",
            "out/",
            ".cache/",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            ".git/",
            "__pycache__/",
            "*.pyc",
            ".venv/",
            ".env",
        ]

        ignore_file = project_dir / '.prettierignore'

        try:
            with open(ignore_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ignore_patterns))
        except Exception as e:
            print(f"  Could not create .prettierignore: {e}")

    def _add_format_script(self, project_dir: Path):
        """Add format script to package.json"""
        package_json = project_dir / 'package.json'

        if not package_json.exists():
            return

        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'scripts' not in data:
                data['scripts'] = {}

            data['scripts']['format'] = 'prettier --write .'
            data['scripts']['format:check'] = 'prettier --check .'

            with open(package_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  Could not update package.json: {e}")
# Export command instance
COMMAND = FormatCodeCommand()