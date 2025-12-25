"""
Git operations module for PyDevToolkit MagicCLI
"""
from .menu import GitMenu
from .changelog import ChangelogGenerator

__all__ = ['GitMenu', 'ChangelogGenerator']