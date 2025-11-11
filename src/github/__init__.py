"""
GitHub Module Package
Contains modular Git operation handlers
UPDATED: Now exports ChangelogGenerator from parent automation package
"""

from github.git_status import GitStatus
from github.git_log import GitLog
from github.git_push import GitPush
from github.git_initializer import GitInitializer
from github.git_recover import GitRecover
from github.git_removesubmodule import GitRemoveSubmodule
from github.git_cache import GitCache
from changelog_generator import ChangelogGenerator

__all__ = [
    'GitStatus',
    'GitLog',
    'GitPush',
    'GitInitializer',
    'GitRecover',
    'GitRemoveSubmodule',
    'GitCache',
    'ChangelogGenerator',
]