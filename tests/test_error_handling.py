"""
Error handling tests for PyDevToolkit-MagicCLI
Tests comprehensive error handling and exception management
"""
import sys
import unittest
from pathlib import Path

from core.security import SecurityValidator
from core.utils.exceptions import (
    AutomationError,
    ErrorSeverity,
    ExceptionHandler,
    GitCommandError,
    GitError,
    GitNotInstalledError,
    NoRemoteError,
    NotGitRepositoryError,
    UncommittedChangesError,
)

# Add the src directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestErrorHandling(unittest.TestCase):
    """Test error handling and exception management"""

    def test_automation_error_creation(self):
        """Test creation of basic AutomationError"""
        error = AutomationError("Test error message")
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.details, {})
        self.assertIsNone(error.suggestion)

    def test_automation_error_with_details(self):
        """Test AutomationError with details and suggestions"""
        details = {"type": "test", "code": 404}
        suggestion = "Try again later"

        error = AutomationError(
            "Test error message",
            severity=ErrorSeverity.WARNING,
            details=details,
            suggestion=suggestion,
        )

        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.severity, ErrorSeverity.WARNING)
        self.assertEqual(error.details, details)
        self.assertEqual(error.suggestion, suggestion)

    def test_automation_error_display(self):
        """Test error display formatting"""
        error = AutomationError(
            "Test error message",
            severity=ErrorSeverity.CRITICAL,
            details={"test": "value"},
            suggestion="Try this solution",
        )

        display_text = error.display()
        self.assertIn("CRITICAL", display_text)
        self.assertIn("Test error message", display_text)
        self.assertIn("test: value", display_text)
        self.assertIn("Try this solution", display_text)

    def test_git_errors_hierarchy(self):
        """Test Git-specific error hierarchy"""
        # All Git errors should inherit from GitError
        git_errors = [
            GitCommandError("test", 1, "stderr"),
            NotGitRepositoryError("/test/path"),
            NoRemoteError("origin"),
            GitNotInstalledError(),
            UncommittedChangesError("push"),
        ]

        for git_error in git_errors:
            self.assertIsInstance(git_error, GitError)
            self.assertIsInstance(git_error, AutomationError)

    def test_git_command_error_generation(self):
        """Test GitCommandError with different stderr messages"""
        test_cases = [
            ("not a git repository", "Initialize Git with: git init"),
            (
                "remote origin not found",
                "Configure remote with: git remote add origin <url>",
            ),
            ("permission denied", "Check file permissions or SSH keys"),
            ("conflict", "Resolve merge conflicts before continuing"),
            ("up to date", "Nothing to push - repository is up to date"),
            (
                "no upstream",
                "Set upstream with: git push --set-upstream origin <branch>",
            ),
        ]

        for stderr_text, expected_suggestion in test_cases:
            with self.subTest(stderr=stderr_text):
                error = GitCommandError("git test", 1, stderr_text)
                if expected_suggestion:
                    self.assertIn(expected_suggestion, error.suggestion or "")

    def test_security_validation_errors(self):
        """Test security validation error handling"""
        # Test command validation
        with self.assertRaises(AutomationError):
            SecurityValidator.sanitize_command_input("ls; rm -rf /")

        # Test path validation
        with self.assertRaises(AutomationError):
            SecurityValidator.sanitize_path("../../../etc/passwd")


class TestExceptionHandler(unittest.TestCase):
    """Test exception handling utilities"""

    def test_handle_automation_error(self):
        """Test handling of AutomationError"""
        error = AutomationError("Test error")

        # This should handle the error without issues
        ExceptionHandler.handle(error)

        # Test with exit_on_critical
        critical_error = AutomationError(
            "Critical error", severity=ErrorSeverity.CRITICAL
        )

        # For non-critical errors, it should not exit
        ExceptionHandler.handle(error, exit_on_critical=True)

    def test_handle_regular_exception(self):
        """Test handling of regular exceptions"""
        regular_error = ValueError("Test value error")

        # This should wrap the error and handle it
        ExceptionHandler.handle(regular_error)

    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""

        def successful_func():
            return "success"

        result, error = ExceptionHandler.safe_execute(successful_func)
        self.assertEqual(result, "success")
        self.assertIsNone(error)

    def test_safe_execute_with_automation_error(self):
        """Test safe_execute with AutomationError"""

        def error_func():
            raise AutomationError("Test error")

        result, error = ExceptionHandler.safe_execute(error_func)
        self.assertIsNone(result)
        self.assertIsInstance(error, AutomationError)

    def test_safe_execute_with_regular_exception(self):
        """Test safe_execute with regular exception"""

        def error_func():
            raise ValueError("Test error")

        result, error = ExceptionHandler.safe_execute(error_func)
        self.assertIsNone(result)
        self.assertIsInstance(error, AutomationError)  # Should be wrapped


class TestExceptionSubclasses(unittest.TestCase):
    """Test specific exception subclasses"""

    def test_not_git_repository_error(self):
        """Test NotGitRepositoryError"""
        error = NotGitRepositoryError("/test/path")
        self.assertEqual(error.message, "Not a Git repository: /test/path")
        self.assertIn("git init", error.suggestion)

    def test_no_remote_error(self):
        """Test NoRemoteError"""
        error = NoRemoteError("upstream")
        self.assertEqual(error.message, "No remote 'upstream' configured")
        self.assertIn("git remote add upstream", error.suggestion)

    def test_git_not_installed_error(self):
        """Test GitNotInstalledError"""
        error = GitNotInstalledError()
        self.assertIn("Git is not installed", error.message)
        self.assertEqual(error.severity, ErrorSeverity.CRITICAL)

    def test_uncommitted_changes_error(self):
        """Test UncommittedChangesError"""
        error = UncommittedChangesError("push")
        self.assertIn("Cannot push", error.message)
        self.assertIn("commit or stash", error.suggestion.lower())


if __name__ == "__main__":
    print("Running error handling tests...")
    unittest.main(verbosity=2)
