"""
Code Analysis Module
Handles code duplication detection, static analysis, complexity metrics, and code review automation
"""
import sys
import subprocess
import os
import ast
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class CodeAnalysisTools:
    """Handles code analysis and metrics tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def detect_code_duplication(self) -> None:
        """Detect code duplication using tools like Vulture or custom logic"""
        print("\n" + "="*70)
        print("CODE DUPLICATION DETECTION")
        print("="*70)

        print("\nThis feature detects duplicate code across your project.")
        print("It uses the 'vulture' package to find unused code and potential duplicates.")

        # Check if vulture is available
        try:
            import vulture
            print("✓ Vulture is available")
        except ImportError:
            install = input("Vulture is not installed. Install Vulture? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "vulture"], check=True)
                    print("✓ Vulture installed successfully")
                    import vulture
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Vulture")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot run duplication detection without Vulture.")
                input("\nPress Enter to continue...")
                return

        # Run vulture on the project
        try:
            result = subprocess.run([
                sys.executable, "-m", "vulture", "src/"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("\n✓ No unused code found!")
            else:
                print(f"\nPotential issues found:")
                print(result.stdout)

                # Save report
                with open("vulture_report.txt", "w") as f:
                    f.write(result.stdout)
                print(f"Report saved to vulture_report.txt")

        except Exception as e:
            print(f"\n⚠ Error running duplication detection: {e}")

        input("\nPress Enter to continue...")

    def run_static_analysis(self) -> None:
        """Run comprehensive static analysis on code"""
        print("\n" + "="*70)
        print("STATIC CODE ANALYSIS")
        print("="*70)

        print("\nRunning static analysis using multiple tools...")

        # Using Pylint (if available)
        try:
            result = subprocess.run([
                sys.executable, "-m", "pylint", "src/"
            ], capture_output=True, text=True)

            print("\nPYLINT ANALYSIS:")
            if result.returncode in [0, 1, 2]:  # 0=ok, 1=error in code, 2=error in pylint
                print(result.stdout[-1000:])  # Show last 1000 characters to avoid too much output
            else:
                print("Pylint error:", result.stderr)

        except FileNotFoundError:
            print("\n⚠ Pylint is not installed")
            install = input("Install Pylint? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "pylint"], check=True)
                    print("✓ Pylint installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Pylint")

        # Using Bandit for security analysis
        try:
            result = subprocess.run([
                sys.executable, "-m", "bandit", "-r", "src/", "-ll"
            ], capture_output=True, text=True)

            print("\nBANDIT SECURITY ANALYSIS:")
            if result.returncode in [0, 1]:  # 0=no issues, 1=issues found
                print(result.stdout[-1000:])  # Show last 1000 characters
            else:
                print("Bandit error:", result.stderr)

        except FileNotFoundError:
            print("\n⚠ Bandit is not installed")
            install = input("Install Bandit? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=True)
                    print("✓ Bandit installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Bandit")

        print("\nStatic analysis completed.")
        input("\nPress Enter to continue...")

    def measure_complexity_metrics(self) -> None:
        """Measure code complexity metrics"""
        print("\n" + "="*70)
        print("COMPLEXITY METRICS ANALYSIS")
        print("="*70)

        print("\nAnalyzing code complexity metrics...")

        # Using Radon for complexity analysis
        try:
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", "src/", "-s"
            ], capture_output=True, text=True)

            print("\nCYCLOMATIC COMPLEXITY ANALYSIS:")
            if result.returncode == 0:
                print(result.stdout)

                # Save report
                with open("complexity_report.txt", "w") as f:
                    f.write(result.stdout)
                print(f"Complexity report saved to complexity_report.txt")
            else:
                print("Radon error:", result.stderr)

        except FileNotFoundError:
            print("\n⚠ Radon is not installed")
            install = input("Install Radon? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "radon"], check=True)
                    print("✓ Radon installed successfully")

                    # Rerun the analysis
                    result = subprocess.run([
                        sys.executable, "-m", "radon", "cc", "src/", "-s"
                    ], capture_output=True, text=True)

                    print("\nCYCLOMATIC COMPLEXITY ANALYSIS:")
                    if result.returncode == 0:
                        print(result.stdout)

                        # Save report
                        with open("complexity_report.txt", "w") as f:
                            f.write(result.stdout)
                        print(f"Complexity report saved to complexity_report.txt")
                    else:
                        print("Radon error:", result.stderr)
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Radon")

        print("\nComplexity metrics analysis completed.")
        input("\nPress Enter to continue...")

    def analyze_code_maintainability(self) -> None:
        """Analyze code maintainability using various metrics"""
        print("\n" + "="*70)
        print("CODE MAINTAINABILITY ANALYSIS")
        print("="*70)

        print("\nAnalyzing code maintainability...")

        # Using Radon for maintainability index
        try:
            result = subprocess.run([
                sys.executable, "-m", "radon", "mi", "src/", "-s"
            ], capture_output=True, text=True)

            print("\nMAINTAINABILITY INDEX ANALYSIS:")
            if result.returncode == 0:
                print(result.stdout)

                # Save report
                with open("maintainability_report.txt", "w") as f:
                    f.write(result.stdout)
                print(f"Maintainability report saved to maintainability_report.txt")
            else:
                print("Radon error:", result.stderr)

        except FileNotFoundError:
            print("\n⚠ Radon is not installed")
            print("Install with: pip install radon")

        # Additional maintainability checks could go here
        print("\nAnalyzing function and class sizes...")

        # Find Python files
        python_files = list(Path("src").rglob("*.py"))

        large_functions = []
        large_classes = []

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                # Analyze functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        line_count = node.end_lineno - node.lineno
                        if line_count > 50:  # Threshold for "large" function
                            large_functions.append({
                                'file': str(file_path),
                                'function': node.name,
                                'lines': line_count
                            })

                    # Analyze classes
                    elif isinstance(node, ast.ClassDef):
                        line_count = node.end_lineno - node.lineno
                        if line_count > 200:  # Threshold for "large" class
                            large_classes.append({
                                'file': str(file_path),
                                'class': node.name,
                                'lines': line_count
                            })

            except Exception:
                continue  # Skip files that can't be parsed

        print(f"\nFound {len(large_functions)} large functions (>50 lines):")
        for func in large_functions[:10]:  # Show first 10
            print(f"  - {func['file']}::{func['function']} ({func['lines']} lines)")
        if len(large_functions) > 10:
            print(f"  ... and {len(large_functions) - 10} more")

        print(f"\nFound {len(large_classes)} large classes (>200 lines):")
        for cls in large_classes[:10]:  # Show first 10
            print(f"  - {cls['file']}::{cls['class']} ({cls['lines']} lines)")
        if len(large_classes) > 10:
            print(f"  ... and {len(large_classes) - 10} more")

        input("\nPress Enter to continue...")

    def generate_metrics_report(self) -> None:
        """Generate a comprehensive metrics report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE METRICS REPORT")
        print("="*70)

        print("\nGenerating a comprehensive metrics report combining:")
        print("  - Code complexity metrics")
        print("  - Maintainability index")
        print("  - Code duplication analysis")
        print("  - Static analysis results")

        # Count total lines of code
        total_lines = 0
        total_files = 0
        python_files = list(Path("src").rglob("*.py"))

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    total_files += 1
            except:
                continue

        print(f"\nPROJECT STATISTICS:")
        print(f"  - Total Python files: {total_files}")
        print(f"  - Total lines of code: {total_lines}")
        print(f"  - Average lines per file: {total_lines/total_files if total_files > 0 else 0:.1f}")

        # Function count
        function_count = 0
        class_count = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                # Count functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_count += 1
                    elif isinstance(node, ast.ClassDef):
                        class_count += 1
            except:
                continue

        print(f"  - Total functions: {function_count}")
        print(f"  - Total classes: {class_count}")

        # Run complexity analysis if Radon is available
        try:
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", "src/", "-s", "--total-average"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"\nCOMPLEXITY ANALYSIS:")
                # Extract average complexity from radon output
                for line in result.stdout.split('\n'):
                    if 'total average' in line.lower():
                        print(f"  - {line.strip()}")
            else:
                print(f"\nComplexity analysis error: {result.stderr}")
        except FileNotFoundError:
            print("\n⚠ Radon is not installed - run complexity analysis separately")

        # Generate detailed report
        report_content = f"""# Comprehensive Metrics Report

## Project Statistics
- Total Python files: {total_files}
- Total lines of code: {total_lines}
- Average lines per file: {total_lines/total_files if total_files > 0 else 0:.1f}
- Total functions: {function_count}
- Total classes: {class_count}

## Analysis Results
- Code complexity: Run 'radon cc src/' for detailed complexity
- Maintainability index: Run 'radon mi src/' for maintainability scores
- Code duplication: Run 'vulture src/' for unused code detection
- Static analysis: Run 'pylint src/' or 'flake8 src/' for static analysis

## Recommendations
- Keep functions under 50 lines where possible
- Keep classes under 200 lines where possible
- Aim for cyclomatic complexity under 10 per function
- Maintain high maintainability index (A/B grades)

Generated on: {__import__('datetime').datetime.now()}
"""

        with open("metrics_report.md", "w") as f:
            f.write(report_content)

        print(f"\nDetailed report saved as metrics_report.md")

        input("\nPress Enter to continue...")

    def automated_code_review(self) -> None:
        """Perform automated code review"""
        print("\n" + "="*70)
        print("AUTOMATED CODE REVIEW")
        print("="*70)

        print("\nPerforming automated code review using multiple tools...")

        review_results = {
            'pep8_issues': 0,
            'complexity_issues': [],
            'security_issues': [],
            'maintainability_issues': [],
            'suggestions': []
        }

        # Run flake8 for PEP 8 issues
        try:
            result = subprocess.run([
                sys.executable, "-m", "flake8", "src/",
                "--max-line-length=88", "--format='%(path)s:%(line)d:%(col)d: %(code)s %(text)s'"
            ], capture_output=True, text=True)

            if result.returncode != 0:
                review_results['pep8_issues'] = len(result.stdout.strip().split('\n'))
                print(f"  - Found {review_results['pep8_issues']} PEP 8 issues")

        except FileNotFoundError:
            print("  - Flake8 not installed (install with: pip install flake8)")

        # Check for complexity issues with Radon
        try:
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", "src/", "-n", "10"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                high_complexity = [line for line in result.stdout.split('\n') if 'C' in line]
                review_results['complexity_issues'] = len(high_complexity)
                print(f"  - Found {review_results['complexity_issues']} high-complexity functions (complexity > 10)")

        except FileNotFoundError:
            print("  - Radon not installed (install with: pip install radon)")

        # Check for security issues with Bandit
        try:
            result = subprocess.run([
                sys.executable, "-m", "bandit", "-r", "src/", "-lll"
            ], capture_output=True, text=True)

            if result.returncode in [0, 1]:  # 0=no issues, 1=issues found
                security_issues = [line for line in result.stdout.split('\n') if 'Issue:' in line]
                review_results['security_issues'] = len(security_issues)
                if review_results['security_issues'] > 0:
                    print(f"  - Found {review_results['security_issues']} potential security issues")

        except FileNotFoundError:
            print("  - Bandit not installed (install with: pip install bandit)")

        # Analyze code structure
        python_files = list(Path("src").rglob("*.py"))
        total_functions = 0
        total_classes = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        # Check if function is too long
                        line_count = node.end_lineno - node.lineno
                        if line_count > 50:
                            review_results['suggestions'].append(
                                f"Function '{node.name}' in {file_path} is very long ({line_count} lines), consider refactoring"
                            )
                    elif isinstance(node, ast.ClassDef):
                        total_classes += 1
                        # Check if class is too long
                        line_count = node.end_lineno - node.lineno
                        if line_count > 200:
                            review_results['suggestions'].append(
                                f"Class '{node.name}' in {file_path} is very long ({line_count} lines), consider refactoring"
                            )
            except:
                continue

        print(f"  - Analyzed {total_functions} functions and {total_classes} classes")

        # Provide specific suggestions
        if review_results['suggestions']:
            print(f"\nAUTOMATED SUGGESTIONS:")
            for i, suggestion in enumerate(review_results['suggestions'][:5], 1):  # Show first 5
                print(f"  {i}. {suggestion}")
            if len(review_results['suggestions']) > 5:
                print(f"  ... and {len(review_results['suggestions']) - 5} more")

        print(f"\nReview completed. Total findings: {sum(len(review_results[key]) if isinstance(review_results[key], list) else review_results[key] for key in ['pep8_issues', 'complexity_issues', 'security_issues'])}")

        input("\nPress Enter to continue...")
class CodeAnalysisMenu(Menu):
    """Menu for code analysis tools"""

    def __init__(self):
        self.code_analysis = CodeAnalysisTools()
        super().__init__("Code Analysis & Metrics Tools")

    def setup_items(self) -> None:
        """Setup menu items for code analysis tools"""
        self.items = [
            MenuItem("Detect Code Duplication", self.code_analysis.detect_code_duplication),
            MenuItem("Run Static Analysis", self.code_analysis.run_static_analysis),
            MenuItem("Measure Complexity Metrics", self.code_analysis.measure_complexity_metrics),
            MenuItem("Analyze Code Maintainability", self.code_analysis.analyze_code_maintainability),
            MenuItem("Generate Metrics Report", self.code_analysis.generate_metrics_report),
            MenuItem("Automated Code Review", self.code_analysis.automated_code_review),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]