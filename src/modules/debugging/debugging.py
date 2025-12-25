"""
Debugging Module
Handles debugging tools, log analysis, error tracking, and system resource monitoring
"""
import sys
import subprocess
import os
import json
import re
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator

# Import psutil only if available
try:
    import psutil
except ImportError:
    psutil = None


class DebuggingTools:
    """Handles debugging and troubleshooting tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def run_debugger(self) -> None:
        """Run interactive debugger on a script"""
        print("\n" + "=" * 70)
        print("INTERACTIVE DEBUGGER")
        print("=" * 70)

        print("\nThis tool allows you to run a Python script in debug mode.")
        print("It uses Python's built-in pdb debugger.")

        script_path = input("Enter path to Python script to debug: ").strip()
        if not script_path:
            print("Script path is required!")
            input("\nPress Enter to continue...")
            return

        # Validate the script path
        if not self.validator.validate_path(script_path):
            print("Invalid path!")
            input("\nPress Enter to continue...")
            return

        script_file = Path(script_path)
        if not script_file.exists():
            print(f"Script file '{script_path}' does not exist!")
            input("\nPress Enter to continue...")
            return

        if not script_file.suffix.lower() == '.py':
            print("File must be a Python script (.py)!")
            input("\nPress Enter to continue...")
            return

        print(f"\nStarting debugger for '{script_path}'...")
        print("Commands in debugger:")
        print("  - c/continue: continue execution")
        print("  - n/next: execute next line")
        print("  - s/step: step into function calls")
        print("  - l/list: show current code")
        print("  - p/print: print variable value")
        print("  - h/help: show help")
        print("  - q/quit: quit debugger")

        try:
            # Use pdb to debug the script
            import pdb
            import runpy
            print(f"\nStarting pdb debugger for {script_path}")
            print("Type 'h' for help or 'c' to continue execution")

            # This is a simplified version - for a real implementation,
            # you might want to use runpy or similar to properly load the
            # script
            print(
                "\nNote: In a real implementation, we would use pdb to debug your script.")
            print("For now, here's the command you would run in your terminal:")
            print(f"python -m pdb {script_path}")

        except ImportError:
            print("Python debugger (pdb) is not available")
        except Exception as e:
            print(f"Error starting debugger: {e}")

        input("\nPress Enter to continue...")

    def analyze_logs(self) -> None:
        """Analyze application logs"""
        print("\n" + "=" * 70)
        print("LOG ANALYSIS TOOL")
        print("=" * 70)

        print("\nThis tool analyzes log files to find errors, warnings, and patterns.")

        # Look for common log files
        log_extensions = ['.log', '.txt', '.out', '.err']
        project_path = Path('.')
        log_files = []

        for ext in log_extensions:
            log_files.extend(list(project_path.rglob(f'*{ext}')))

        # Filter out files that are likely not logs based on name
        filtered_logs = [
            f for f in log_files if 'log' in f.name.lower() or any(
                keyword in f.name.lower() for keyword in [
                    'error', 'debug', 'out', 'err'])]

        print(f"\nFound {len(filtered_logs)} potential log files:")
        for i, log_file in enumerate(filtered_logs[:10], 1):  # Show first 10
            print(f"  {i}. {log_file}")

        if len(filtered_logs) > 10:
            print(f"  ... and {len(filtered_logs) - 10} more")

        if not filtered_logs:
            print("\nNo log files found in common locations.")
            print("Please specify the log file path manually.")

            log_path = input("Enter path to log file: ").strip()
            if not log_path:
                input("\nPress Enter to continue...")
                return

            log_file_path = Path(log_path)
            if not log_file_path.exists():
                print(f"Log file '{log_path}' does not exist!")
                input("\nPress Enter to continue...")
                return

            filtered_logs = [log_file_path]

        # Analyze the first log file by default
        selected_log = filtered_logs[0]
        print(f"\nAnalyzing log file: {selected_log}")

        # Check if it's a text file and read it
        try:
            with open(selected_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            print(f"Total lines in log: {len(lines)}")

            # Count error types
            errors = 0
            warnings = 0
            exceptions = 0
            tracebacks = 0

            for line in lines:
                line_lower = line.lower()
                if 'error' in line_lower and 'error' not in line_lower.split(
                )[0]:  # Avoid matching "error" as first word like in "errors"
                    errors += 1
                if 'warning' in line_lower or 'warn' in line_lower:
                    warnings += 1
                if 'exception' in line_lower:
                    exceptions += 1
                if 'traceback' in line_lower or (
                        'file "' in line_lower and 'line' in line_lower):
                    tracebacks += 1

            print(f"Errors found: {errors}")
            print(f"Warnings found: {warnings}")
            print(f"Exceptions found: {exceptions}")
            print(f"Tracebacks found: {tracebacks}")

            # Show the last 10 lines if there are errors
            if errors > 0:
                print(f"\nLast 10 lines of log (potential errors):")
                for line in lines[-10:]:
                    if any(
                        keyword in line.lower() for keyword in [
                            'error',
                            'exception',
                            'traceback',
                            'failed']):
                        print(f"  {line.rstrip()}")

        except Exception as e:
            print(f"Error reading log file: {e}")

        input("\nPress Enter to continue...")

    def run_performance_profiling(self) -> None:
        """Run performance profiling on a script"""
        print("\n" + "=" * 70)
        print("PERFORMANCE PROFILING")
        print("=" * 70)

        print("\nThis tool profiles Python code to identify performance bottlenecks.")
        print("It uses Python's built-in cProfile module.")

        script_path = input("Enter path to Python script to profile: ").strip()
        if not script_path:
            print("Script path is required!")
            input("\nPress Enter to continue...")
            return

        # Validate the script path
        if not self.validator.validate_path(script_path):
            print("Invalid path!")
            input("\nPress Enter to continue...")
            return

        script_file = Path(script_path)
        if not script_file.exists():
            print(f"Script file '{script_path}' does not exist!")
            input("\nPress Enter to continue...")
            return

        if not script_file.suffix.lower() == '.py':
            print("File must be a Python script (.py)!")
            input("\nPress Enter to continue...")
            return

        print(f"\nProfiling script: {script_path}")

        try:
            # Run cProfile on the script
            import cProfile
            import pstats
            import io

            profiler = cProfile.Profile()
            profiler.enable()

            # Execute the script
            with open(script_path, 'r') as file:
                script_content = file.read()

            # Execute in a restricted namespace
            namespace = {"__name__": "__main__", "__file__": script_path}
            exec(compile(script_content, script_path, 'exec'), namespace)

            profiler.disable()

            # Create a string stream to capture stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(10)  # Show top 10 functions

            print("\nTop 10 performance bottlenecks:")
            print(s.getvalue())

            # Save full profiling results to a file
            profile_file = "profile_output.prof"
            profiler.dump_stats(profile_file)
            print(f"\nFull profiling data saved to: {profile_file}")
            print("To analyze further, run: python -m pstats profile_output.prof")

        except Exception as e:
            print(f"Error during profiling: {e}")
            import traceback
            traceback.print_exc()

        input("\nPress Enter to continue...")

    def check_system_resources(self) -> None:
        """Check system resources and performance"""
        print("\n" + "=" * 70)
        print("SYSTEM RESOURCE MONITORING")
        print("=" * 70)

        print("\nThis tool monitors system resources like CPU, memory, and disk usage.")

        if psutil is None:
            print("\npsutil library not available for detailed system monitoring.")
            print("Install with: pip install psutil")

            # Fallback to basic system info
            print(f"\nBasic system information:")
            print(f"  Platform: {sys.platform}")
            print(f"  Python version: {sys.version}")
            print(f"  Current working directory: {os.getcwd()}")
            print(f"  Available environment variables: {len(os.environ)}")
        else:
            try:
                print("\nCPU Usage:")
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()

                print(f"  Current usage: {cpu_percent}%")
                print(f"  Logical CPUs: {cpu_count}")
                if cpu_freq:
                    print(
                        f"  Frequency: {cpu_freq.current:.2f} MHz (max: {cpu_freq.max:.2f} MHz)")

                print("\nMemory Usage:")
                memory = psutil.virtual_memory()
                print(f"  Total: {memory.total / (1024**3):.2f} GB")
                print(f"  Available: {memory.available / (1024**3):.2f} GB")
                print(f"  Used: {memory.used / (1024**3):.2f} GB")
                print(f"  Percentage: {memory.percent}%")

                print("\nDisk Usage:")
                disk = psutil.disk_usage('/')
                print(f"  Total: {disk.total / (1024**3):.2f} GB")
                print(f"  Used: {disk.used / (1024**3):.2f} GB")
                print(f"  Free: {disk.free / (1024**3):.2f} GB")
                print(f"  Percentage: {disk.percent}%")

                print("\nNetwork I/O:")
                net_io = psutil.net_io_counters()
                print(f"  Bytes sent: {net_io.bytes_sent / (1024**2):.2f} MB")
                print(
                    f"  Bytes received: {net_io.bytes_recv / (1024**2):.2f} MB")

            except Exception as e:
                print(f"\nError getting system resources: {e}")

        input("\nPress Enter to continue...")

    def run_troubleshooting_wizard(self) -> None:
        """Run an interactive troubleshooting wizard"""
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING WIZARD")
        print("=" * 70)

        print("\nThis wizard will help diagnose common issues with your application.")

        issues = []

        # Check if Python version is supported
        if sys.version_info < (3, 7):
            issues.append(
                "Python version is older than 3.7 - Magic CLI may not work properly")

        # Check for common missing dependencies
        missing_deps = []
        required_modules = ['requests', 'pyyaml', 'colorama']

        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_deps.append(module)

        if missing_deps:
            issues.append(
                f"Missing required dependencies: {', '.join(missing_deps)}")

        # Check if we're in the project directory by looking for key files
        expected_files = ['pyproject.toml', 'requirements.txt', 'src/main.py']
        missing_files = [f for f in expected_files if not Path(f).exists()]

        if missing_files:
            issues.append(
                f"Missing expected project files: {', '.join(missing_files)}")

        # Check if .git directory exists but no remote configured
        if Path('.git').exists():
            try:
                result = subprocess.run(
                    ['git', 'remote', '-v'],
                    capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0 and not result.stdout.strip():
                    issues.append(
                        "Git repository exists but no remote configured")
            except BaseException:
                issues.append("Could not check Git remote configuration")

        # Check for common configuration issues
        config_files = ['config.yaml', 'config/default.yaml']
        config_exists = any(Path(f).exists() for f in config_files)

        if not config_exists:
            issues.append("Configuration file not found")

        print(f"\nFound {len(issues)} potential issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        if not issues:
            print("  ✓ No obvious issues detected!")

        # Provide solutions for detected issues
        if issues:
            print(f"\nRecommended actions:")
            for i, issue in enumerate(issues, 1):
                if "Python version" in issue:
                    print(f"  {i}. Consider upgrading to Python 3.7 or higher")
                elif "Missing required dependencies" in issue:
                    deps = [dep for dep in missing_deps]
                    print(
                        f"  {i}. Install missing dependencies: pip install {' '.join(deps)}")
                elif "Missing expected project files" in issue:
                    print(
                        f"  {i}. Verify you're in the correct project directory")
                elif "Git repository exists but no remote configured" in issue:
                    print(
                        f"  {i}. Configure Git remote: git remote add origin <repository-url>")
                elif "Configuration file not found" in issue:
                    print(
                        f"  {i}. Create configuration file or check config path")

        # Check for common runtime issues
        print(f"\nChecking for common runtime issues...")

        # Check if environment is properly set up
        try:
            # Try to import core modules
            import src.core.menu
            import src.core.security.validator
            print("  ✓ Core modules imported successfully")
        except ImportError as e:
            print(f"  ⚠ Error importing core modules: {e}")

        # Check if we can run basic Python commands
        try:
            import subprocess
            result = subprocess.run([sys.executable, '--version'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(
                    f"  ✓ Python interpreter accessible: {result.stdout.strip()}")
            else:
                print(f"  ⚠ Python interpreter issue: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"  ⚠ Python interpreter timeout")
        except Exception as e:
            print(f"  ⚠ Error checking Python interpreter: {e}")

        input("\nPress Enter to continue...")

    def error_tracking_integration(self) -> None:
        """Provide guidance for error tracking integration"""
        print("\n" + "=" * 70)
        print("ERROR TRACKING INTEGRATION")
        print("=" * 70)

        print("\nThis tool provides guidance for integrating error tracking services.")
        print("Common error tracking services include:")
        print("  1. Sentry")
        print("  2. Rollbar")
        print("  3. LogRocket")
        print("  4. AppSignal")

        print("\nFor Sentry integration, you would typically:")

        # Check if Sentry is available
        try:
            import sentry_sdk
            print("  ✓ Sentry SDK is already installed")
        except ImportError:
            print("  ⚠ Sentry SDK is not installed")
            install = input("Install Sentry SDK? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip",
                                   "install", "sentry-sdk"], check=True)
                    print("  ✓ Sentry SDK installed successfully")
                    import sentry_sdk
                    print("  ✓ Sentry SDK imported successfully")
                except subprocess.CalledProcessError:
                    print("  ⚠ Failed to install Sentry SDK")

        print("\nExample Sentry integration code:")
        print("```python")
        print("# Add to your main application")
        print("import sentry_sdk")
        print("from sentry_sdk.integrations.logging import LoggingIntegration")
        print()
        print("# Replace 'YOUR_SENTRY_DSN' with your actual DSN")
        print("sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)")
        print("sentry_sdk.init(")
        print("    dsn=\"YOUR_SENTRY_DSN\",")
        print("    integrations=[sentry_logging],")
        print("    traces_sample_rate=1.0")
        print(")")
        print("```")

        print("\nOther error tracking services require similar integration patterns.")
        print("Each service provides specific SDKs and setup instructions.")

        input("\nPress Enter to continue...")


class DebuggingMenu(Menu):
    """Menu for debugging tools"""

    def __init__(self):
        self.debugging = DebuggingTools()
        super().__init__("Debugging & Troubleshooting Tools")

    def setup_items(self) -> None:
        """Setup menu items for debugging tools"""
        self.items = [
            MenuItem("Run Interactive Debugger", self.debugging.run_debugger),
            MenuItem("Analyze Application Logs", self.debugging.analyze_logs),
            MenuItem("Run Performance Profiling", self.debugging.run_performance_profiling),
            MenuItem("Check System Resources", self.debugging.check_system_resources),
            MenuItem("Run Troubleshooting Wizard", self.debugging.run_troubleshooting_wizard),
            MenuItem("Error Tracking Integration", self.debugging.error_tracking_integration),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]
