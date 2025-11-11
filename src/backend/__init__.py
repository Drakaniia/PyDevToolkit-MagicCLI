"""
automation/backend/__init__.py
Backend development automation tools
"""

from .database_assistant import DatabaseAssistantCommand
from .api_generator import APIGeneratorCommand
from .auth_helper import AuthHelperCommand
from .migration_assistant import MigrationAssistantCommand

__all__ = [
    'DatabaseAssistantCommand',
    'APIGeneratorCommand', 
    'AuthHelperCommand',
    'MigrationAssistantCommand'
]