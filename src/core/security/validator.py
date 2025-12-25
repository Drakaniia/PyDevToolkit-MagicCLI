"""
Security module for PyDevToolkit-MagicCLI
Provides security utilities, input validation, and sanitization functions
"""
import re
import os
import subprocess
from pathlib import Path
from typing import Union, List, Optional
from ..utils.exceptions import AutomationError, ErrorSeverity
class SecurityValidator:
    """Centralized security validation and sanitization utilities"""

    # Patterns for validating inputs
    SAFE_COMMAND_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\:\/\s=]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\/\\]+$')
    SAFE_FILE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
    SAFE_BRANCH_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\:\/]+$')

    @staticmethod
    def validate_command_input(user_input: str) -> bool:
        """
        Validate command input for safety

        Args:
            user_input: The command input to validate

        Returns:
            bool: True if safe, False otherwise
        """
        if not user_input:
            return True  # Empty input is safe

        # Check for dangerous characters/sequences
        dangerous_patterns = [
            r';',           # Command separators
            r'&&',          # Command execution
            r'\|\|',        # Command execution (OR operator)
            r'\|',          # Pipe
            r'\$\(',        # Command substitution
            r'`',           # Command substitution
            r'&',           # Background execution
            r'\$\{',        # Variable expansion
            r'\$\[',        # Array expansion
            r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
            r'\\u[0-9a-fA-F]{4}',  # Unicode escape sequences
            r'\x00',        # Null bytes (null byte injection)
            r'%00',         # URL encoded null bytes
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False

        # Check against safe command pattern
        return bool(SecurityValidator.SAFE_COMMAND_PATTERN.match(user_input))

    @staticmethod
    def validate_path(path: str) -> bool:
        """
        Validate file path for safety

        Args:
            path: The path to validate

        Returns:
            bool: True if safe, False otherwise
        """
        if not path:
            return True  # Empty path is safe

        # Check for directory traversal
        if '..' in path.replace('\\', '/').split('/'):
            return False

        # Check for absolute paths that might lead outside project
        try:
            abs_path = Path(path).resolve()
            project_root = Path.cwd().resolve()
            # Only allow paths within or relative to project root
            abs_path.relative_to(project_root)
        except ValueError:
            # Path is outside project root
            return False

        # Check against safe path pattern
        if not SecurityValidator.SAFE_PATH_PATTERN.match(path):
            return False

        # Additional check: prohibit certain dangerous patterns
        dangerous_path_patterns = [
            r'\x00',  # Null bytes (null byte injection)
            r'%00',   # URL encoded null bytes
        ]

        for pattern in dangerous_path_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def validate_file_name(filename: str) -> bool:
        """
        Validate file name for safety

        Args:
            filename: The file name to validate

        Returns:
            bool: True if safe, False otherwise
        """
        if not filename:
            return True  # Empty filename is safe

        # Get just the filename part (not the path)
        file_part = Path(filename).name

        # Prevent directory traversal even in filename
        if '..' in file_part or '/' in file_part or '\\' in file_part:
            return False

        # Check for null bytes
        if '\x00' in file_part:
            return False

        return bool(SecurityValidator.SAFE_FILE_NAME_PATTERN.match(file_part))

    @staticmethod
    def validate_branch_name(branch_name: str) -> bool:
        """
        Validate Git branch name for safety

        Args:
            branch_name: The branch name to validate

        Returns:
            bool: True if safe, False otherwise
        """
        if not branch_name:
            return True  # Empty branch name is safe

        # Git has specific rules for branch names - validate against them
        dangerous_patterns = [
            r'\.\..',        # Cannot contain .lock or .. in them.
            r'@{',          # Cannot end with .lock or contain sequence @{.
            r'\.$',         # Cannot end with .
            r'^/',          # Cannot begin with /
            r'//',          # Cannot contain double /
            r'\s+$',        # Cannot end with whitespace
            r'^\s+',        # Cannot begin with whitespace
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, branch_name):
                return False

        return bool(SecurityValidator.SAFE_BRANCH_NAME_PATTERN.match(branch_name))

    @staticmethod
    def sanitize_command_input(user_input: str) -> str:
        """
        Sanitize command input to remove potentially dangerous characters

        Args:
            user_input: The command input to sanitize

        Returns:
            str: Sanitized command input

        Raises:
            AutomationError: If input cannot be safely sanitized
        """
        if not user_input:
            return user_input

        # Check if the input is already valid
        if SecurityValidator.validate_command_input(user_input):
            return user_input

        # If not valid, raise an error instead of attempting to sanitize
        # (as sanitization might change the intended command)
        raise AutomationError(
            "Command input contains potentially dangerous characters",
            ErrorSeverity.WARNING,
            suggestion="Use only alphanumeric characters, hyphens, underscores, dots, and slashes"
        )

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitize path to prevent directory traversal and other path-based attacks

        Args:
            path: The path to sanitize

        Returns:
            str: Sanitized path

        Raises:
            AutomationError: If path cannot be safely sanitized
        """
        if not path:
            return path

        # Check if the path is already valid
        if SecurityValidator.validate_path(path):
            return path

        # If not valid, raise an error
        raise AutomationError(
            "Path contains potentially dangerous elements",
            ErrorSeverity.WARNING,
            suggestion="Use only relative paths within the project directory"
        )

    @staticmethod
    def safe_subprocess_run(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """
        Safely run a subprocess command with validation

        Args:
            cmd: Command to run as a list of strings
            **kwargs: Additional arguments for subprocess.run

        Returns:
            subprocess.CompletedProcess: Result of the command execution

        Raises:
            AutomationError: If command contains potentially dangerous elements
        """
        # Validate each command element
        for element in cmd:
            if not SecurityValidator.validate_command_input(str(element)):
                raise AutomationError(
                    f"Command contains potentially dangerous element: {element}",
                    ErrorSeverity.ERROR,
                    suggestion="Use only safe command elements without shell metacharacters"
                )

        # Ensure shell=False to prevent shell injection
        if 'shell' in kwargs:
            kwargs.pop('shell')  # Remove any shell parameter to enforce shell=False

        # Execute the command with subprocess using shell=False (default)
        return subprocess.run(cmd, **kwargs)
def safe_input(prompt: str) -> str:
    """
    Secure input function that validates user input

    Args:
        prompt: The prompt to display to the user

    Returns:
        str: The validated user input
    """
    user_input = input(prompt).strip()

    if not SecurityValidator.validate_command_input(user_input):
        raise AutomationError(
            "Input contains potentially dangerous characters",
            ErrorSeverity.WARNING,
            suggestion="Use only alphanumeric characters, hyphens, underscores, dots, and slashes"
        )

    return user_input
def safe_path_input(prompt: str) -> str:
    """
    Secure path input function that validates user-provided paths

    Args:
        prompt: The prompt to display to the user

    Returns:
        str: The validated user input
    """
    user_input = input(prompt).strip()

    if not SecurityValidator.validate_path(user_input):
        raise AutomationError(
            "Path contains potentially dangerous elements",
            ErrorSeverity.WARNING,
            suggestion="Use only relative paths within the project directory"
        )

    return user_input