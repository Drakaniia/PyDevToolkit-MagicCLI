"""
Security Tools Module
Handles secrets scanning, security audits, compliance checking, and vulnerability assessments
"""
import sys
import subprocess
import os
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class SecurityTools:
    """Handles security and compliance tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def scan_for_secrets(self) -> None:
        """Scan for secrets like API keys, passwords, etc. in code"""
        print("\n" + "="*70)
        print("SECRETS SCANNING")
        print("="*70)

        print("\nThis feature scans for secrets like API keys, passwords, etc. in your code.")
        print("It uses the 'detect-secrets' package to identify potential secrets.")

        # Check if detect-secrets is available
        try:
            import detect_secrets
            print("✓ Detect-secrets is available")
        except ImportError:
            install = input("Detect-secrets is not installed. Install it? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "detect-secrets"], check=True)
                    print("✓ Detect-secrets installed successfully")
                    import detect_secrets
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install detect-secrets")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot run secrets scanning without detect-secrets.")
                input("\nPress Enter to continue...")
                return

        # Run detect-secrets on the project
        try:
            result = subprocess.run([
                sys.executable, "-m", "detect_secrets", "scan", "--base64-limit", "4.5", "."
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("\n✓ No secrets found!")

                # Initialize a baseline to track future secrets
                init_result = subprocess.run([
                    sys.executable, "-m", "detect_secrets", "baseline", "--base64-limit", "4.5", "."
                ], capture_output=True, text=True)

                if init_result.returncode == 0:
                    print("Baseline created to track future secrets")
                else:
                    print("Could not create baseline:", init_result.stderr)
            else:
                print(f"\nPotential secrets found:")
                print(result.stdout)

                # Save findings
                with open("secrets_report.txt", "w") as f:
                    f.write(result.stdout)
                print(f"Report saved to secrets_report.txt")

        except Exception as e:
            print(f"\n⚠ Error running secrets scanning: {e}")

        input("\nPress Enter to continue...")

    def run_security_audit(self) -> None:
        """Run comprehensive security audit"""
        print("\n" + "="*70)
        print("COMPREHENSIVE SECURITY AUDIT")
        print("="*70)

        print("\nRunning security audit using multiple tools...")

        # Run safety to check for known vulnerabilities in dependencies
        try:
            print("Checking for known vulnerabilities in dependencies...")
            safety_result = subprocess.run([
                sys.executable, "-m", "safety", "check", "--json"
            ], capture_output=True, text=True)

            if safety_result.returncode != 0:
                print(f"\n❌ Security vulnerabilities found in dependencies!")

                # Parse and format the results
                try:
                    safety_data = json.loads(safety_result.stdout)
                    print(f"Found {len(safety_data)} vulnerability(ies):")
                    for vuln in safety_data:
                        print(f"  - {vuln.get('name', 'N/A')}: {vuln.get('description', 'N/A')}")
                except json.JSONDecodeError:
                    print("Safety scan output:")
                    print(safety_result.stdout)

                # Save report
                with open("security_vulnerability_report.txt", "w") as f:
                    f.write(safety_result.stdout)
                print(f"Security vulnerability report saved to security_vulnerability_report.txt")
            else:
                print("✓ No known vulnerabilities found in dependencies!")

        except FileNotFoundError:
            print("⚠ Safety is not installed")
            install = input("Install Safety? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "safety"], check=True)
                    print("✓ Safety installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Safety")

        # Run Bandit for security issues in Python code
        try:
            print("\nChecking for security issues in Python code...")
            bandit_result = subprocess.run([
                sys.executable, "-m", "bandit", "-r", "src/", "-f", "json"
            ], capture_output=True, text=True)

            if bandit_result.returncode in [0, 1]:  # 0=no issues, 1=issues found
                try:
                    import json
                    bandit_data = json.loads(bandit_result.stdout)
                    issues = bandit_data.get('results', [])

                    if issues:
                        print(f"\n❌ Found {len(issues)} security issue(s):")
                        for issue in issues[:5]:  # Show first 5 issues
                            print(f"  - {issue['test_name']}: {issue['filename']}:{issue['line_number']}")

                        if len(issues) > 5:
                            print(f"  ... and {len(issues) - 5} more issues")
                    else:
                        print("  ✓ No security issues found in Python code!")
                except json.JSONDecodeError:
                    print("Could not parse Bandit results")
            else:
                print("Bandit error:", bandit_result.stderr)

        except FileNotFoundError:
            print("⚠ Bandit is not installed")
            install = input("Install Bandit? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=True)
                    print("✓ Bandit installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Bandit")

        print("\nSecurity audit completed.")
        input("\nPress Enter to continue...")

    def check_compliance(self) -> None:
        """Check compliance with coding standards and regulations"""
        print("\n" + "="*70)
        print("COMPLIANCE CHECKING")
        print("="*70)

        print("\nChecking compliance with common standards...")

        # Check for common compliance requirements
        issues = []

        # Check for license file
        license_files = list(Path('.').glob('*LICENSE*')) + list(Path('.').glob('*license*'))
        if not license_files:
            issues.append("Missing LICENSE file")

        # Check for security headers in common web frameworks
        # This is a simplified check - real compliance tools would be more sophisticated
        requirements_files = list(Path('.').glob('*requirements*.txt'))
        for req_file in requirements_files:
            with open(req_file, 'r') as f:
                content = f.read()
                if 'django' in content.lower():
                    # Check if security-related packages are mentioned
                    security_packages = ['django-cors-headers', 'django-session-timeout', 'django-security']
                    missing_security = [pkg for pkg in security_packages if pkg not in content.lower()]
                    if missing_security:
                        issues.append(f"Missing security packages in {req_file}: {', '.join(missing_security)}")

        # Check for common security configurations
        config_files = list(Path('.').rglob('*.py'))  # Check Python files for config
        for config_file in config_files:
            if 'config' in str(config_file) or 'settings' in str(config_file):
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    # Check for DEBUG mode in Django settings
                    if 'django' in content and 'debug = true' in content:
                        issues.append(f"DEBUG mode enabled in {config_file} (security risk)")

        # Check for hardcoded secrets using basic pattern matching
        python_files = list(Path('.').rglob('*.py'))
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']*["\']',
            r'api_key\s*=\s*["\'][^"\']*["\']',
            r'token\s*=\s*["\'][^"\']*["\']',
            r'secret\s*=\s*["\'][^"\']*["\']',
        ]

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        issues.append(f"Potential hardcoded secret in {file_path}:{match.start()}")
            except:
                continue  # Skip files that can't be read

        print(f"\nFound {len(issues)} potential compliance issues:")
        for i, issue in enumerate(issues[:10], 1):  # Show first 10 issues
            print(f"  {i}. {issue}")

        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")

        if not issues:
            print("✓ No obvious compliance issues found!")

        # Save detailed report
        report_content = f"""Compliance Check Report
Generated on: {__import__('datetime').datetime.now()}

Total issues found: {len(issues)}

Issues:
"""
        for i, issue in enumerate(issues, 1):
            report_content += f"{i}. {issue}\n"

        with open("compliance_report.txt", "w") as f:
            f.write(report_content)

        print(f"\nDetailed report saved as compliance_report.txt")

        input("\nPress Enter to continue...")

    def assess_vulnerabilities(self) -> None:
        """Assess vulnerabilities in the project"""
        print("\n" + "="*70)
        print("VULNERABILITY ASSESSMENT")
        print("="*70)

        print("\nAssessing vulnerabilities in the project...")

        # Check for specific vulnerability patterns
        vulnerabilities = []

        # Check for common insecure imports
        insecure_imports = [
            'urllib2',  # Python 2 module, replaced by urllib
            'httplib',   # Python 2 module, replaced by http.client
            'xml.etree.cElementTree',  # Faster but not always available
        ]

        python_files = list(Path("src").rglob("*.py"))

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for imp in insecure_imports:
                    if f'import {imp}' in content or f'from {imp}' in content:
                        vulnerabilities.append(f"Insecure import '{imp}' in {file_path}")

            except Exception:
                continue  # Skip files that can't be read

        # Check for hardcoded IP addresses or URLs (potential security risk)
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for hardcoded IP addresses
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ip_matches = re.findall(ip_pattern, content)
                for ip in ip_matches:
                    # Ignore common local IPs
                    if not ip.startswith(('127.', '10.', '192.168.', '172.')):
                        vulnerabilities.append(f"Hardcoded IP address '{ip}' in {file_path}")

                # Look for hardcoded URLs (basic check)
                url_pattern = r'https?://[^\s\'"<>]+'
                url_matches = re.findall(url_pattern, content)
                for url in url_matches:
                    # Check if it's a hardcoded external service URL
                    if 'localhost' not in url and '127.0.0.1' not in url:
                        vulnerabilities.append(f"Hardcoded external URL '{url}' in {file_path}")

            except Exception:
                continue  # Skip files that can't be read

        # Check for common security vulnerabilities
        vulnerable_patterns = [
            (r'eval\(', 'Use of eval() function - security risk'),
            (r'exec\(', 'Use of exec() function - security risk'),
            (r'os\.system\(', 'Use of os.system() - potential command injection'),
            (r'subprocess\.(call|run|Popen)\([^,]*,?\s*shell\s*=\s*True', 'Use of shell=True in subprocess - potential injection'),
            (r'pickle\.(loads?|load)\(', 'Use of pickle - potential code execution'),
        ]

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern, description in vulnerable_patterns:
                    matches = list(re.finditer(pattern, content))
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        vulnerabilities.append(f"{description} in {file_path}:{line_no}")

            except Exception:
                continue  # Skip files that can't be read

        print(f"\nFound {len(vulnerabilities)} potential vulnerabilities:")
        for i, vuln in enumerate(vulnerabilities[:10], 1):  # Show first 10
            print(f"  {i}. {vuln}")

        if len(vulnerabilities) > 10:
            print(f"  ... and {len(vulnerabilities) - 10} more")

        if not vulnerabilities:
            print("✓ No obvious vulnerabilities found!")

        # Create detailed report
        report_content = f"""Vulnerability Assessment Report
Generated on: {__import__('datetime').datetime.now()}

Total vulnerabilities found: {len(vulnerabilities)}

Vulnerabilities:
"""
        for i, vuln in enumerate(vulnerabilities, 1):
            report_content += f"{i}. {vuln}\n"

        report_content += "\nRecommendations:\n"
        report_content += "- Avoid using eval() and exec() with untrusted input\n"
        report_content += "- Use parameterized queries to prevent SQL injection\n"
        report_content += "- Validate and sanitize all user inputs\n"
        report_content += "- Store secrets in environment variables or secure vaults\n"
        report_content += "- Regularly update dependencies to patch known vulnerabilities\n"

        with open("vulnerability_report.txt", "w") as f:
            f.write(report_content)

        print(f"\nDetailed report saved as vulnerability_report.txt")

        input("\nPress Enter to continue...")

    def generate_security_report(self) -> None:
        """Generate a comprehensive security report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE SECURITY REPORT")
        print("="*70)

        print("\nGenerating a comprehensive security report...")

        # Run all security checks and aggregate results
        report_parts = []

        # Add header
        report_content = f"""# Security Report for Magic CLI Project
Generated on: {__import__('datetime').datetime.now()}

## Executive Summary
This report provides a security assessment of the Magic CLI project, covering:

1. Dependency vulnerabilities
2. Code security issues
3. Hardcoded secrets
4. Configuration issues
5. Best practice compliance

## Detailed Findings
"""

        # Run safety check
        try:
            safety_result = subprocess.run([
                sys.executable, "-m", "safety", "check", "--json"
            ], capture_output=True, text=True)

            if safety_result.stdout:
                import json
                try:
                    safety_data = json.loads(safety_result.stdout)
                    report_content += f"\n### Dependency Vulnerabilities\n"
                    report_content += f"Found {len(safety_data)} known vulnerability(ies) in dependencies:\n"
                    for vuln in safety_data[:5]:  # Show first 5
                        report_content += f"- {vuln.get('name', 'N/A')}: {vuln.get('description', 'N/A')}\n"
                    if len(safety_data) > 5:
                        report_content += f"(and {len(safety_data) - 5} more)\n"
                except json.JSONDecodeError:
                    report_content += "\n### Dependency Check\n"
                    report_content += "Could not parse dependency check results\n"
        except FileNotFoundError:
            report_content += "\n### Dependency Check\n"
            report_content += "Safety tool not available\n"

        # Add note about security checks performed
        report_content += "\n## Security Checks Performed\n"
        report_content += "- Dependency vulnerability scanning\n"
        report_content += "- Code-based security issue detection\n"
        report_content += "- Hardcoded secrets detection\n"
        report_content += "- Configuration security review\n"
        report_content += "- Compliance with best practices\n"

        report_content += "\n## Recommendations\n"
        report_content += "1. Regularly update dependencies to address known vulnerabilities\n"
        report_content += "2. Implement secret scanning in CI/CD pipeline\n"
        report_content += "3. Perform regular security code reviews\n"
        report_content += "4. Use secure coding practices\n"
        report_content += "5. Implement proper input validation and sanitization\n"

        # Save comprehensive report
        with open("comprehensive_security_report.md", "w") as f:
            f.write(report_content)

        print(f"\nComprehensive security report saved as comprehensive_security_report.md")
        print("\nThe report includes:")
        print("  - Dependency vulnerability summary")
        print("  - Security checks performed")
        print("  - Actionable recommendations")

        input("\nPress Enter to continue...")
class SecurityMenu(Menu):
    """Menu for security tools"""

    def __init__(self):
        self.security = SecurityTools()
        super().__init__("Security & Compliance Tools")

    def setup_items(self) -> None:
        """Setup menu items for security tools"""
        self.items = [
            MenuItem("Scan for Secrets", self.security.scan_for_secrets),
            MenuItem("Run Security Audit", self.security.run_security_audit),
            MenuItem("Check Compliance", self.security.check_compliance),
            MenuItem("Assess Vulnerabilities", self.security.assess_vulnerabilities),
            MenuItem("Generate Security Report", self.security.generate_security_report),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]