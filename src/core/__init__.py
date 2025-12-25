"""
automation/core/__init__.py
Core Git operations and utilities
"""

from .utils.git_client import GitClient, get_git_client
from .utils.exceptions import (
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
    ExceptionHandler,
    handle_errors
)

__all__ = [
    'GitClient',
    'get_git_client',
    'AutomationError',
    'GitError',
    'GitCommandError',
    'NotGitRepositoryError',
    'NoRemoteError',
    'GitNotInstalledError',
    'UncommittedChangesError',
    'SSHConfigError',
    'GitHubAPIError',
    'ErrorSeverity',
    'ExceptionHandler',
    'handle_errors'
]
