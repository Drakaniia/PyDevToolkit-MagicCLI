"""
GitHub Module Package
Contains modular Git operation handlers
UPDATED: Now exports ChangelogGenerator from parent automation package
"""

from .git_status import GitStatus
from .git_log import GitLog
from .git_push import GitPush
from .git_initializer import GitInitializer
from .git_recover import GitRecover
from .git_removesubmodule import GitRemoveSubmodule
from .git_cache import GitCache
from .git_stash import GitStash
from modules.git_operations.changelog import ChangelogGenerator

__all__ = [
    'GitStatus',
    'GitLog',
    'GitPush',
    'GitInitializer',
    'GitRecover',
    'GitRemoveSubmodule',
    'GitCache',
    'GitStash',
    'ChangelogGenerator',
]