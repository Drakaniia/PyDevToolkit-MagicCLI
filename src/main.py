#!/usr/bin/env python3
"""
Main entry point for Python Automation System
"""

import sys
import os
import io
from pathlib import Path
import subprocess

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        import ctypes
        # Enable ANSI escape codes on Windows 10+
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except (OSError, AttributeError):
        # Fall back gracefully if ANSI not supported
        pass
    # Ensure stdout uses UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# Add src directory to path to enable imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from menu import MainMenu
from core.utils.exceptions import AutomationError


def verify_installation():
    """Verify the installation status and display system information"""
    print("\n" + "=" * 70)
    print("  Magic CLI - Installation Verification")
    print("=" * 70 + "\n")

    all_good = True

    # Check Python version
    print("Python Environment:")
    print(f"  • Python Version: {sys.version.split()[0]}")
    print(f"  • Python Path: {sys.executable}")
    if sys.version_info < (3, 8):
        print("  ⚠  Warning: Python 3.8+ is recommended")
        all_good = False
    else:
        print("  ✓ Python version meets requirements")

    # Check package installation
    print("\nPackage Installation:")
    try:
        import importlib.metadata as metadata
        version = metadata.version("magic-cli")
        print(f"  • Package Name: magic-cli")
        print(f"  • Package Version: {version}")
        print("  ✓ Package installed correctly")
    except Exception:
        print("  ⚠  Warning: Could not verify package version")
        all_good = False

    # Check PATH configuration
    print("\nPATH Configuration:")
    magic_path = os.path.expanduser("~/.magic-cli/bin" if sys.platform != "win32" else os.path.join(os.path.expanduser("~"), ".magic-cli", "bin"))
    path_env = os.environ.get("PATH", "")
    if magic_path in path_env:
        print(f"  ✓ Magic CLI directory in PATH: {magic_path}")
    else:
        print(f"  ⚠  Magic CLI directory not in PATH: {magic_path}")
        print(f"  → Add to PATH: export PATH=\"{magic_path}:$PATH\"")
        all_good = False

    # Check wrapper script
    print("\nWrapper Script:")
    if sys.platform != "win32":
        wrapper = os.path.join(magic_path, "magic")
        if os.path.exists(wrapper):
            print(f"  ✓ Wrapper script exists: {wrapper}")
            if os.access(wrapper, os.X_OK):
                print("  ✓ Wrapper script is executable")
            else:
                print("  ⚠  Wrapper script is not executable")
                print(f"  → Run: chmod +x {wrapper}")
                all_good = False
        else:
            print(f"  ⚠  Wrapper script not found: {wrapper}")
            all_good = False
    else:
        wrapper_cmd = os.path.join(magic_path, "magic.cmd")
        wrapper_ps1 = os.path.join(magic_path, "magic.ps1")
        if os.path.exists(wrapper_cmd) or os.path.exists(wrapper_ps1):
            print(f"  ✓ Wrapper script exists")
        else:
            print(f"  ⚠  Wrapper script not found")
            all_good = False

    # Check dependencies
    print("\nDependencies:")
    dependencies = {
        "pyyaml": "yaml",  # Package name vs import name
        "colorama": "colorama",
        "pyfiglet": "pyfiglet",
        "termcolor": "termcolor",
        "psutil": "psutil"
    }
    for pkg_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"  ✓ {pkg_name}")
        except ImportError:
            print(f"  ⚠  {pkg_name} not installed")
            all_good = False

    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print("  ✓ All checks passed! Installation is correct.")
    else:
        print("  ⚠  Some issues detected. Please review the warnings above.")
    print("=" * 70 + "\n")

    return 0 if all_good else 1


def run_port_killer(port=None, kill_all=False):
    """Run the port killer functionality directly"""
    try:
        from modules.web_development.dev_mode.port_killer_command import PortKillerCommand
        from modules.web_development.dev_mode.port_killer import scan_active_servers, kill_all_dev_ports, force_clear_all_ports
        command = PortKillerCommand()
        
        if kill_all:
            # Kill all active server processes
            print("\n FORCE CLEARING ALL DEVELOPMENT PORTS")
            print("="*70)
            print("  This will terminate ALL detected development server processes")
            print("="*70)
            
            result = force_clear_all_ports(verbose=True)
            
            print("\n FINAL SUMMARY")
            print("="*70)
            print(f" Total processes killed: {result['total_killed']}")
            print(f" Common dev ports cleared: {result['common_ports_result']['total_killed']}")
            print(f" Additional servers cleared: {result['server_scan_result']['total_killed']}")
            return 0
        elif port is not None:
            # Kill specific port
            result = command.run(interactive=False, action='kill_port', port=port)
            print(f"Port {port} processes killed successfully" if result else f"Failed to kill processes on port {port}")
            return 0 if result else 1
        else:
            # Just scan and display port usage
            servers = scan_active_servers(verbose=True)
            if servers:
                print(f"\nFound {len(servers)} active server process(es):")
                print("-" * 50)
                for server in servers:
                    print(f"Port {server['port']:>5} | PID {server['pid']:>6} | {server['name']:<20} | {server['protocol']}")
            else:
                print("No active server processes detected")
            return 0
    except Exception as e:
        print(f"\n❌ Error running port killer: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Entry point for the automation system"""
    # Check for --verify flag
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        return verify_installation()


    


    # Check for kill command
    if len(sys.argv) > 1 and sys.argv[1] == "kill":
        # If no subcommand is provided, show available options
        if len(sys.argv) == 2:
            print("\n📋 Magic Kill Commands:")
            print("  magic kill all     Kill all active server processes")
            print("  magic kill a       (shorthand for 'all')")
            print("  magic kill p       Kill specific port (usage: magic kill p <port_number>)")
            print("  magic kill <port>  Kill specific port (usage: magic kill <port_number>)")
            print("")
            return 0
        # Check if 'all' is specified to kill all ports
        elif sys.argv[2] in ["all", "a"]:
            return run_port_killer(kill_all=True)
        # Check if 'p' is specified for a specific port
        elif sys.argv[2] == "p":
            if len(sys.argv) == 4:
                try:
                    port = int(sys.argv[3])
                    return run_port_killer(port=port)
                except ValueError:
                    print(f"\n❌ Invalid port number: {sys.argv[3]}")
                    print("Usage: magic kill p <port_number>")
                    return 1
            else:
                print(f"\n❌ Port number required after 'p'")
                print("Usage: magic kill p <port_number>")
                return 1
        # Check if a direct port number is provided (magic kill <port>)
        elif len(sys.argv) == 3:
            try:
                port = int(sys.argv[2])
                return run_port_killer(port=port)
            except ValueError:
                print(f"\n❌ Invalid port number: {sys.argv[2]}")
                print("Usage: magic kill <port_number> or magic kill p <port_number>")
                print("   Or: magic kill all to kill all active server processes")
                return 1
        else:
            print(f"\n❌ Unknown kill command: {' '.join(sys.argv[1:])}")
            print("Usage: magic kill all     Kill all active server processes")
            print("   Or: magic kill a       (shorthand for 'all')")
            print("   Or: magic kill p <port> Kill specific port")
            print("   Or: magic kill <port>  Kill specific port")
            return 1

    # Check for "show" command
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        if len(sys.argv) > 2 and sys.argv[2] in ["-s", "--structure"]:
            # Show folder structure
            from modules.project_management.structure_viewer import StructureViewer
            viewer = StructureViewer()
            viewer.show_structure()
            return 0
        else:
            # Show help for show command
            print("\nMagic CLI - Show Command\n")
            print("Usage:")
            print("  magic show -s          Show project folder structure")
            print("  magic show --structure Show project folder structure\n")
            return 0

    # Check for --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("\nMagic CLI - Python Developer Toolkit\n")
        print("Usage:")
        print("  magic                    Launch the interactive menu")
        print("  magic --verify           Verify installation status")
        print("  magic kill all           Kill all active server processes")
        print("  magic kill a             (shorthand for 'all')")
        print("  magic kill p <port>      Kill specific port")
        print("  magic kill <port>        Kill specific port")
        print("  magic show -s            Show project folder structure")
        print("  magic --help             Show this help message\n")
        return 0

    # Launch the main menu with global exception handling
    try:
        menu = MainMenu()
        menu.run()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        return 130
    except AutomationError as e:
        print(f"\n❌ Automation Error: {e.message}")
        if e.suggestion:
            print(f"💡 Suggestion: {e.suggestion}")
        return 1
    except Exception as e:
        # Global exception handler - prevent crashes and provide helpful error
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        print("\n💡 This may be a bug. Please check:")
        print("   1. Your Python version (3.8+ required)")
        print("   2. All dependencies are installed: pip install -e .")
        print("   3. File permissions in the project directory")
        print("\nIf the issue persists, please report it on GitHub.")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
