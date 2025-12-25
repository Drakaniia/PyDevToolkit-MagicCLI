"""
Core utilities for PyDevToolkit MagicCLI
"""
from .config import ConfigManager
from .logging import SecurityAuditLogger
from .exceptions import (
    AutomationError,
    GitError,
    GitCommandError,
    NotGitRepositoryError,
    NoRemoteError,
    GitNotInstalledError,
    UncommittedChangesError,
    SSHConfigError,
    GitHubAPIError,
    ErrorSeverity,
    ExceptionHandler
)
from .git_client import GitClient

__all__ = [
    'ConfigManager', 'SecurityAuditLogger', 'AutomationError',
    'GitError', 'GitCommandError', 'NotGitRepositoryError', 'NoRemoteError',
    'GitNotInstalledError', 'UncommittedChangesError', 'SSHConfigError',
    'GitHubAPIError', 'ErrorSeverity', 'ExceptionHandler', 'GitClient'
]
