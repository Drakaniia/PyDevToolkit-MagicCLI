"""
pytest configuration and fixtures for PyDevToolkit MagicCLI
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create a mock git repository for testing"""
    import subprocess

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir,
                   check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True
    )
    subprocess.run(["git",
                    "config",
                    "user.email",
                    "test@example.com"],
                   cwd=temp_dir,
                   check=True)

    # Create a test file and commit
    test_file = temp_dir / "test.txt"
    test_file.write_text("Test content")
    subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"],
                   cwd=temp_dir, check=True)

    return temp_dir


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "security": {
            "max_command_length": 500,
            "max_path_length": 1000,
            "allow_network_access": False,
            "blocked_commands": ["rm", "del"],
            "allowed_file_extensions": [".py", ".txt", ".md"],
        },
        "operational": {
            "log_level": "DEBUG",
            "enable_color_output": False,
            "enable_loading_animations": False,
        },
    }


@pytest.fixture(autouse=True)
def disable_color_output():
    """Disable color output for all tests"""
    os.environ["NO_COLOR"] = "1"


@pytest.fixture
def sample_project_structure(temp_dir):
    """Create a sample project structure for testing"""
    # Create directory structure
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()
    (temp_dir / "config").mkdir()

    # Create sample files
    (temp_dir / "src" / "main.py").write_text("def main(): pass")
    (temp_dir / "src" / "utils.py").write_text("def helper(): pass")
    (temp_dir / "tests" / "test_main.py").write_text("def test_main(): pass")
    (temp_dir / "README.md").write_text("# Test Project")
    (temp_dir / "requirements.txt").write_text("pytest>=7.0.0")
    (temp_dir / "config" / "settings.yaml").write_text("app: test")

    return temp_dir
