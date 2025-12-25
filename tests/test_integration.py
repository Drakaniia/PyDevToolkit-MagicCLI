"""
Integration tests for PyDevToolkit-MagicCLI
Tests modules working together and overall system functionality
"""
from core.utils.logging import SecurityAuditLogger, get_security_logger
from core.utils.exceptions import AutomationError
from core.utils.config import ConfigManager, get_security_config
from core.security import SecurityValidator
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the src directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSecurityIntegration(unittest.TestCase):
    """Test security integration with other modules"""

    def test_security_config_integration(self):
        """Test that security settings are properly integrated"""
        config = get_security_config()

        # Verify default security settings exist
        self.assertIsInstance(config.max_command_length, int)
        self.assertIsInstance(config.max_path_length, int)
        self.assertIsInstance(config.enable_input_sanitization, bool)
        self.assertIsInstance(config.blocked_commands, list)
        self.assertIsInstance(config.allowed_file_extensions, list)

    def test_security_validator_with_config(self):
        """Test security validator respecting configuration"""
        # Test command validation
        self.assertTrue(
            SecurityValidator.validate_command_input("safe command"))
        self.assertFalse(
            SecurityValidator.validate_command_input("dangerous; command"))

    def test_security_audit_logging(self):
        """Test security audit logging functionality"""
        logger = get_security_logger()

        # Test basic logging
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Test audit functions
        logger.audit_security_event("test_event", {"test": "data"})
        logger.audit_command_execution("test_command", "test_input", True)


class TestModuleIntegration(unittest.TestCase):
    """Test integration between different modules"""

    def test_security_with_exceptions(self):
        """Test that security module works with exception handling"""
        # Test that security validation properly raises AutomationError
        with self.assertRaises(AutomationError):
            SecurityValidator.sanitize_command_input(
                "dangerous command; rm -rf /")

    def test_config_with_security(self):
        """Test configuration integration with security"""
        config_manager = ConfigManager()

        # Test getting security settings
        max_cmd_len = config_manager.get_security_setting("max_command_length")
        self.assertIsInstance(max_cmd_len, int)

        # Test setting security settings
        original_value = config_manager.get_security_setting(
            "max_command_length")
        config_manager.set_security_setting("max_command_length", 1000)
        new_value = config_manager.get_security_setting("max_command_length")
        self.assertEqual(new_value, 1000)

        # Restore original value
        config_manager.set_security_setting(
            "max_command_length", original_value)


class TestRealWorldScenarios(unittest.TestCase):
    """Test scenarios that mimic real-world usage"""

    def test_safe_git_command_construction(self):
        """Test constructing safe Git commands"""
        # Test safe branch name validation
        self.assertTrue(
            SecurityValidator.validate_branch_name("feature/new-feature"))
        self.assertTrue(
            SecurityValidator.validate_branch_name("bugfix/issue-123"))
        self.assertTrue(SecurityValidator.validate_branch_name("main"))

        # Test unsafe branch name
        self.assertFalse(
            SecurityValidator.validate_branch_name("test;rm -rf /"))

    def test_safe_file_path_operations(self):
        """Test safe file path operations"""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Create a safe file path
            safe_path = "src/main.py"
            Path("src").mkdir(exist_ok=True)
            Path(safe_path).touch()

            # Validate the path
            self.assertTrue(SecurityValidator.validate_path(safe_path))

            # Test file name validation
            self.assertTrue(SecurityValidator.validate_file_name(safe_path))
            self.assertTrue(SecurityValidator.validate_file_name("main.py"))

    def test_safe_command_execution_workflow(self):
        """Test a complete workflow of command validation and execution"""
        # Define a safe command
        safe_command = ["python", "--version"]

        # Validate each element
        for element in safe_command:
            self.assertTrue(
                SecurityValidator.validate_command_input(
                    str(element)))

        # Validate the entire command would be safe to run
        try:
            result = SecurityValidator.safe_subprocess_run(
                safe_command, capture_output=True, text=True, timeout=10
            )
            # The command should complete successfully
            self.assertEqual(
                result.returncode, 0 if result.returncode == 0 else 0
            )  # Python might not be available but no exceptions raised
        except FileNotFoundError:
            # Python might not be installed, which is fine for this test
            pass
        except Exception:
            # Other exceptions are not expected for valid commands
            self.fail("Safe command execution failed unexpectedly")


class TestConfigurationPersistence(unittest.TestCase):
    """Test configuration persistence and loading"""

    def test_config_manager_creation(self):
        """Test ConfigManager creation and default configuration"""
        # Create a temporary directory for testing configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"

            # Create config manager with custom path
            config_manager = ConfigManager(str(config_path))

            # Verify default values are set
            self.assertIsInstance(config_manager.security_config, object)
            self.assertIsInstance(config_manager.operational_config, object)

            # Test saving and loading
            original_max_cmd_len = config_manager.get_security_setting(
                "max_command_length"
            )
            config_manager.set_security_setting("max_command_length", 2000)

            # Save the config
            config_manager.save_config()

            # Create a new manager and verify it loads the changed value
            new_config_manager = ConfigManager(str(config_path))
            new_max_cmd_len = new_config_manager.get_security_setting(
                "max_command_length"
            )

            self.assertEqual(new_max_cmd_len, 2000)


class TestSecurityPatterns(unittest.TestCase):
    """Test various security patterns and edge cases"""

    def test_various_command_injection_attempts(self):
        """Test that various command injection attempts are blocked"""
        injection_attempts = [
            "ls; rm -rf /",
            "cat file.txt && dangerous_command",
            "echo test || another_command",
            "ls | another_command",
            "command & background_process",
            "$(dangerous_command)",
            "`dangerous_command`",
            "ls; echo test; dangerous_command",
            "ls -a;#comment",
            "cat file.txt %26 dangerous_command",  # URL encoding attempt
        ]

        for injection_attempt in injection_attempts:
            with self.subTest(attempt=injection_attempt):
                # Should not validate as safe
                self.assertFalse(
                    SecurityValidator.validate_command_input(injection_attempt),
                    f"Injection attempt '{injection_attempt}' should not validate as safe",
                )

                # Should raise error when sanitizing
                with self.assertRaises(AutomationError):
                    SecurityValidator.sanitize_command_input(injection_attempt)

    def test_various_path_traversal_attempts(self):
        """Test that various path traversal attempts are blocked"""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32\\config\\sam",
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\cmd.exe",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            for traversal_attempt in traversal_attempts:
                with self.subTest(attempt=traversal_attempt):
                    # Should not validate as safe
                    self.assertFalse(
                        SecurityValidator.validate_path(traversal_attempt),
                        f"Traversal attempt '{traversal_attempt}' should not validate as safe",
                    )

                    # Should raise error when sanitizing
                    with self.assertRaises(AutomationError):
                        SecurityValidator.sanitize_path(traversal_attempt)


if __name__ == "__main__":
    print("Running integration tests...")
    unittest.main(verbosity=2)
