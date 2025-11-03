"""
automation/dev_mode/install_deps.py
Install Node.js dependencies (npm install)
FIXED: Windows compatibility for npm/yarn/pnpm commands
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Any
from automation.dev_mode._base import DevModeCommand
from automation.core.loading import LoadingSpinner, loading_animation
from automation.dev_mode.menu_utils import get_choice_with_arrows


class InstallDepsCommand(DevModeCommand):
    """Command to install Node.js dependencies"""
    
    label = "Install Dependencies (npm install)"
    description = "Install project dependencies using npm, yarn, or pnpm"
    
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute dependency installation"""
        if interactive:
            return self._interactive_install()
        else:
            return self._noninteractive_install(**kwargs)
    
    def _interactive_install(self):
        """Interactive dependency installation"""
        print("\n" + "="*70)
        print("📦 INSTALL DEPENDENCIES")
        print("="*70 + "\n")
        
        # Check if package.json exists
        package_json = Path.cwd() / 'package.json'
        if not package_json.exists():
            print("❌ No package.json found in current directory")
            print("💡 Navigate to a Node.js project first")
            input("\nPress Enter to continue...")
            return
        
        # Detect package manager
        detected_manager = self._detect_package_manager()
        print(f"Detected package manager: {detected_manager}")
        
        # Prompt for package manager with arrow navigation
        package_manager_options = [
            "npm",
            "pnpm", 
            "yarn",
            f"Use detected ({detected_manager})"
        ]
        
        print("\n📦 Select Package Manager:")
        choice = get_choice_with_arrows(package_manager_options, "Package Manager")
        
        manager_map = {
            1: 'npm',
            2: 'pnpm',
            3: 'yarn',
            4: detected_manager
        }
        
        manager = manager_map.get(choice, detected_manager)
        
        # Check if manager is available
        if not self.validate_binary(manager):
            print(f"\n❌ {manager} not found in PATH")
            print(f"💡 Install {manager}:")
            if manager == 'pnpm':
                print("   npm install -g pnpm")
            elif manager == 'yarn':
                print("   npm install -g yarn")
            else:
                print("   https://nodejs.org/")
            input("\nPress Enter to continue...")
            return
        
        # Install type with arrow navigation
        install_type_options = [
            "Install all dependencies",
            "Install specific package", 
            "Install package as dev dependency"
        ]
        
        print("\n🔨 Select Install Type:")
        install_type = get_choice_with_arrows(install_type_options, "Install Type")
        
        if install_type == 1:
            # Install all
            self._install_all(manager)
        elif install_type in [2, 3]:
            # Install specific package
            package_name = input("\nPackage name: ").strip()
            if not package_name:
                print("❌ Package name cannot be empty")
                input("\nPress Enter to continue...")
                return
            
            is_dev = (install_type == 3)
            self._install_package(manager, package_name, is_dev)
        
        input("\nPress Enter to continue...")
    
    def _noninteractive_install(
        self,
        manager: str = 'npm',
        packages: Optional[List[str]] = None,
        dev: bool = False
    ):
        """Non-interactive dependency installation"""
        if not self.validate_binary(manager):
            raise FileNotFoundError(f"{manager} not found in PATH")
        
        if packages:
            for package in packages:
                self._install_package(manager, package, dev, interactive=False)
        else:
            self._install_all(manager, interactive=False)
    
    def _install_all(self, manager: str, interactive: bool = True):
        """Install all dependencies"""
        print(f"\n🔨 Installing dependencies with {manager}...")
        print("="*70 + "\n")
        
        cmd = [manager, 'install']
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            # Use shell=True on Windows
            use_shell = sys.platform == 'win32'
            
            with LoadingSpinner(f"Installing dependencies with {manager}", style='dots'):
                result = subprocess.run(
                    cmd if not use_shell else ' '.join(cmd),
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True,
                    shell=use_shell,
                    text=True
                )
            
            print("✅ Dependencies installed successfully!")
            if interactive and result.stdout and not result.stdout.isspace():
                print(f"Output: {result.stdout.strip()}")
        
        except subprocess.CalledProcessError as e:
            if interactive:
                print(f"❌ Installation failed with exit code {e.returncode}")
                if e.stderr:
                    print(f"Error: {e.stderr.strip()}")
            else:
                raise
        except FileNotFoundError:
            if interactive:
                print(f"❌ Error: '{manager}' not found in PATH")
            else:
                raise
        except Exception as e:
            if interactive:
                print(f"❌ Error: {e}")
            else:
                raise
    
    def _install_package(
        self,
        manager: str,
        package: str,
        dev: bool = False,
        interactive: bool = True
    ):
        """Install specific package"""
        dep_type = "dev dependency" if dev else "dependency"
        print(f"\n🔨 Installing {package} as {dep_type}...")
        print("="*70 + "\n")
        
        # Build command
        if manager == 'npm':
            cmd = ['npm', 'install']
            if dev:
                cmd.append('--save-dev')
            cmd.append(package)
        elif manager == 'yarn':
            cmd = ['yarn', 'add']
            if dev:
                cmd.append('--dev')
            cmd.append(package)
        elif manager == 'pnpm':
            cmd = ['pnpm', 'add']
            if dev:
                cmd.append('--save-dev')
            cmd.append(package)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            # Use shell=True on Windows
            use_shell = sys.platform == 'win32'
            
            with LoadingSpinner(f"Installing {package} as {dep_type}", style='dots'):
                result = subprocess.run(
                    cmd if not use_shell else ' '.join(cmd),
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True,
                    shell=use_shell,
                    text=True
                )
            
            print(f"✅ Package '{package}' installed successfully!")
            if interactive and result.stdout and not result.stdout.isspace():
                print(f"Output: {result.stdout.strip()}")
        
        except subprocess.CalledProcessError as e:
            if interactive:
                print(f"❌ Installation failed with exit code {e.returncode}")
                if e.stderr:
                    print(f"Error: {e.stderr.strip()}")
            else:
                raise
        except FileNotFoundError:
            if interactive:
                print(f"❌ Error: '{manager}' not found in PATH")
            else:
                raise
        except Exception as e:
            if interactive:
                print(f"❌ Error: {e}")
            else:
                raise
    
    def _detect_package_manager(self) -> str:
        """Detect which package manager to use based on lock files"""
        cwd = Path.cwd()
        
        if (cwd / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (cwd / 'yarn.lock').exists():
            return 'yarn'
        elif (cwd / 'package-lock.json').exists():
            return 'npm'
        else:
            return 'npm'  # Default


# Export command instance
COMMAND = InstallDepsCommand()