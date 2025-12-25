"""
Security tests for PyDevToolkit-MagicCLI
Tests security validation, input sanitization, and security controls
"""
import unittest
import os
import sys
from pathlib import Path
import tempfile

# Add the src directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.security import SecurityValidator
from core.exceptions import AutomationError


class TestSecurityValidation(unittest.TestCase):
    """Test security validation functions"""

    def test_validate_safe_command_input(self):
        """Test validation of safe command inputs"""
        safe_inputs = [
            "git status",
            "npm install",
            "python app.py",
            "docker build -t myapp .",
            "ls -la",
            "echo hello",
            "cat file.txt",
            "mkdir newdir"
        ]
        
        for safe_input in safe_inputs:
            with self.subTest(input=safe_input):
                self.assertTrue(
                    SecurityValidator.validate_command_input(safe_input),
                    f"Safe input '{safe_input}' should validate as safe"
                )

    def test_validate_dangerous_command_input(self):
        """Test validation of dangerous command inputs"""
        dangerous_inputs = [
            "git status; rm -rf /",
            "echo hello && rm -rf /",
            "ls || rm -rf /",
            "cat file.txt | rm -rf /",
            "ls & rm -rf /",
            "$(rm -rf /)",
            "`rm -rf /`",
            "git status; echo hi; rm -rf /"
        ]
        
        for dangerous_input in dangerous_inputs:
            with self.subTest(input=dangerous_input):
                self.assertFalse(
                    SecurityValidator.validate_command_input(dangerous_input),
                    f"Dangerous input '{dangerous_input}' should validate as unsafe"
                )

    def test_validate_safe_path(self):
        """Test validation of safe paths"""
        safe_paths = [
            "src/main.py",
            "docs/README.md",
            "dist/build/",
            "app/module.js",
            "static/css/style.css",
            "test_dir",
            "./relative/path",
            "../sibling/path"
        ]
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            for safe_path in safe_paths:
                with self.subTest(path=safe_path):
                    # Create the path if it doesn't exist
                    full_path = Path(temp_dir) / safe_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    if not full_path.is_dir():
                        full_path.touch()
                    
                    self.assertTrue(
                        SecurityValidator.validate_path(safe_path),
                        f"Safe path '{safe_path}' should validate as safe"
                    )

    def test_validate_dangerous_path(self):
        """Test validation of dangerous paths (directory traversal)"""
        dangerous_paths = [
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32\\config\\sam",
            "/proc/self/environ"
        ]
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            for dangerous_path in dangerous_paths:
                with self.subTest(path=dangerous_path):
                    self.assertFalse(
                        SecurityValidator.validate_path(dangerous_path),
                        f"Dangerous path '{dangerous_path}' should validate as unsafe"
                    )
    
    def test_validate_safe_file_name(self):
        """Test validation of safe file names"""
        safe_file_names = [
            "main.py",
            "config.json",
            "style.css",
            "app.js",
            "readme.md",
            "test_file.txt",
            "my-app.tsx",
            "_private.py"
        ]
        
        for safe_file_name in safe_file_names:
            with self.subTest(file_name=safe_file_name):
                self.assertTrue(
                    SecurityValidator.validate_file_name(safe_file_name),
                    f"Safe file name '{safe_file_name}' should validate as safe"
                )
    
    def test_validate_dangerous_file_name(self):
        """Test validation of dangerous file names"""
        dangerous_file_names = [
            "file;rm -rf /",
            "$(cat /etc/passwd)",
            "`rm -rf /`",
            "file && malicious_command",
            "file || malicious_command"
        ]
        
        for dangerous_file_name in dangerous_file_names:
            with self.subTest(file_name=dangerous_file_name):
                self.assertFalse(
                    SecurityValidator.validate_file_name(dangerous_file_name),
                    f"Dangerous file name '{dangerous_file_name}' should validate as unsafe"
                )

    def test_sanitize_command_input_safe(self):
        """Test sanitization of safe command input"""
        safe_input = "git status"
        
        # This should not raise an exception
        sanitized = SecurityValidator.sanitize_command_input(safe_input)
        self.assertEqual(sanitized, safe_input)

    def test_sanitize_command_input_dangerous(self):
        """Test sanitization of dangerous command input"""
        dangerous_input = "git status; rm -rf /"
        
        # This should raise an exception
        with self.assertRaises(AutomationError):
            SecurityValidator.sanitize_command_input(dangerous_input)

    def test_sanitize_path_safe(self):
        """Test sanitization of safe path"""
        safe_path = "src/main.py"
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            # Create the path
            (Path(temp_dir) / "src").mkdir(exist_ok=True)
            (Path(temp_dir) / "src" / "main.py").touch()
            
            # This should not raise an exception
            sanitized = SecurityValidator.sanitize_path(safe_path)
            self.assertEqual(sanitized, safe_path)

    def test_sanitize_path_dangerous(self):
        """Test sanitization of dangerous path"""
        dangerous_path = "../../../etc/passwd"
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # This should raise an exception
            with self.assertRaises(AutomationError):
                SecurityValidator.sanitize_path(dangerous_path)


class TestSecurityIntegration(unittest.TestCase):
    """Test security integration with other modules"""

    def test_safe_subprocess_run_safe_command(self):
        """Test that safe subprocess run works with safe commands"""
        # Test with a simple safe command
        result = SecurityValidator.safe_subprocess_run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)

    def test_safe_subprocess_run_dangerous_command(self):
        """Test that safe subprocess run blocks dangerous commands"""
        # This should raise an exception due to dangerous command
        with self.assertRaises(AutomationError):
            SecurityValidator.safe_subprocess_run(
                ["python", "; rm -rf /"],  # Dangerous command
                capture_output=True,
                text=True
            )


if __name__ == '__main__':
    print("Running security tests...")
    unittest.main(verbosity=2)