"""
Tests for git_pull.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.github.git_pull import GitPull
import subprocess


class TestGitPull:
    """Test GitPull functionality"""

    @patch('src.github.git_pull.subprocess.run')
    def test_init(self, mock_run):
        """Test GitPull initialization"""
        mock_run.return_value.returncode = 0
        git_pull = GitPull()
        
        assert git_pull.loading_active is False
        assert git_pull.loading_thread is None

    @patch('src.github.git_pull.subprocess.run')
    def test_is_git_repo_true(self, mock_run):
        """Test repository detection - positive"""
        mock_run.return_value.returncode = 0
        git_pull = GitPull()
        
        result = git_pull._is_git_repo()
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )

    @patch('src.github.git_pull.subprocess.run')
    def test_is_git_repo_false(self, mock_run):
        """Test repository detection - negative"""
        mock_run.return_value.returncode = 1
        git_pull = GitPull()
        
        result = git_pull._is_git_repo()
        assert result is False

    @patch('src.github.git_pull.subprocess.run')
    def test_has_remote_true(self, mock_run):
        """Test remote detection - positive"""
        mock_run.return_value.returncode = 0
        git_pull = GitPull()
        
        result = git_pull._has_remote()
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )

    @patch('src.github.git_pull.subprocess.run')
    def test_has_remote_false(self, mock_run):
        """Test remote detection - negative"""
        mock_run.return_value.returncode = 1
        git_pull = GitPull()
        
        result = git_pull._has_remote()
        assert result is False

    @patch('src.github.git_pull.GitPull._is_git_repo')
    @patch('src.github.git_pull.GitPull._has_remote')
    @patch('builtins.input', return_value='y')
    @patch('src.github.git_pull.subprocess.run')
    def test_pull_success(self, mock_run, mock_input, mock_has_remote, mock_is_git_repo):
        """Test successful pull operation"""
        # Setup mocks
        mock_is_git_repo.return_value = True
        mock_has_remote.return_value = True
        
        # Mock the fetch and pull commands
        fetch_result = Mock()
        fetch_result.returncode = 0
        fetch_result.stdout = ""
        fetch_result.stderr = ""
        
        pull_result = Mock()
        pull_result.returncode = 0
        pull_result.stdout = "Already up to date"
        pull_result.stderr = ""
        
        mock_run.side_effect = [fetch_result, pull_result]
        
        git_pull = GitPull()
        result = git_pull.pull()
        
        assert result is True
        assert mock_run.call_count >= 2  # fetch and pull commands

    @patch('src.github.git_pull.GitPull._is_git_repo')
    @patch('src.github.git_pull.GitPull._has_remote')
    @patch('builtins.input', return_value='n')
    @patch('src.github.git_pull.subprocess.run')
    def test_pull_cancelled_by_user(self, mock_run, mock_input, mock_has_remote, mock_is_git_repo):
        """Test pull cancelled by user"""
        # Setup mocks
        mock_is_git_repo.return_value = True
        mock_has_remote.return_value = True
        
        # Mock the fetch command only (should not proceed to pull)
        fetch_result = Mock()
        fetch_result.returncode = 0
        fetch_result.stdout = ""
        fetch_result.stderr = ""
        
        mock_run.return_value = fetch_result
        
        git_pull = GitPull()
        result = git_pull.pull()
        
        assert result is False
        # Only fetch should be called, not pull
        mock_run.assert_called_once()

    @patch('src.github.git_pull.GitPull._is_git_repo')
    @patch('src.github.git_pull.GitPull._has_remote')
    @patch('builtins.input', return_value='y')
    @patch('src.github.git_pull.subprocess.run')
    def test_pull_sync_fail(self, mock_run, mock_input, mock_has_remote, mock_is_git_repo):
        """Test pull when sync (fetch) fails"""
        # Setup mocks
        mock_is_git_repo.return_value = True
        mock_has_remote.return_value = True
        
        # Mock the fetch command to fail
        fetch_result = Mock()
        fetch_result.returncode = 1
        fetch_result.stdout = ""
        fetch_result.stderr = "error: failed to fetch"
        
        mock_run.return_value = fetch_result
        
        git_pull = GitPull()
        result = git_pull.pull()
        
        assert result is False

    @patch('src.github.git_pull.GitPull._is_git_repo')
    @patch('src.github.git_pull.GitPull._has_remote')
    @patch('builtins.input', return_value='y')
    @patch('src.github.git_pull.subprocess.run')
    def test_pull_with_rebase_success(self, mock_run, mock_input, mock_has_remote, mock_is_git_repo):
        """Test successful pull with rebase operation"""
        # Setup mocks
        mock_is_git_repo.return_value = True
        mock_has_remote.return_value = True
        
        # Mock the fetch and pull commands
        fetch_result = Mock()
        fetch_result.returncode = 0
        fetch_result.stdout = ""
        fetch_result.stderr = ""
        
        pull_result = Mock()
        pull_result.returncode = 0
        pull_result.stdout = "Successfully rebased and updated"
        pull_result.stderr = ""
        
        mock_run.side_effect = [fetch_result, pull_result]
        
        git_pull = GitPull()
        result = git_pull.pull_with_rebase()
        
        assert result is True
        assert mock_run.call_count >= 2  # fetch and pull commands

    @patch('src.github.git_pull.GitPull._is_git_repo')
    @patch('src.github.git_pull.GitPull._has_remote')
    @patch('builtins.input', return_value='n')
    @patch('src.github.git_pull.subprocess.run')
    def test_pull_with_rebase_cancelled_by_user(self, mock_run, mock_input, mock_has_remote, mock_is_git_repo):
        """Test pull with rebase cancelled by user"""
        # Setup mocks
        mock_is_git_repo.return_value = True
        mock_has_remote.return_value = True
        
        # Mock the fetch command only (should not proceed to pull)
        fetch_result = Mock()
        fetch_result.returncode = 0
        fetch_result.stdout = ""
        fetch_result.stderr = ""
        
        mock_run.return_value = fetch_result
        
        git_pull = GitPull()
        result = git_pull.pull_with_rebase()
        
        assert result is False
        # Only fetch should be called, not pull
        mock_run.assert_called_once()

    @patch('src.github.git_pull.subprocess.run')
    def test_fetch_success(self, mock_run):
        """Test successful fetch operation"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        git_pull = GitPull()
        result = git_pull.fetch()
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "fetch"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('src.github.git_pull.subprocess.run')
    def test_fetch_failure(self, mock_run):
        """Test fetch operation failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "fetch"], stderr="error")
        
        git_pull = GitPull()
        result = git_pull.fetch()
        
        assert result is False

    @patch('src.github.git_pull.subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        git_pull = GitPull()
        result = git_pull._run_command(["git", "status"])
        
        assert result is True

    @patch('src.github.git_pull.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test command execution failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "status"], stderr="error")
        
        git_pull = GitPull()
        result = git_pull._run_command(["git", "status"])
        
        assert result is False

    @patch('src.github.git_pull.subprocess.run')
    def test_run_command_file_not_found(self, mock_run):
        """Test command execution when git is not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        git_pull = GitPull()
        result = git_pull._run_command(["git", "status"])
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])