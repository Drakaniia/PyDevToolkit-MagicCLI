#!/usr/bin/env python3
"""
Version bumping script for PyDevToolkit-MagicCLI
Automatically updates version in pyproject.toml and creates git tags
"""

import re
import sys
from pathlib import Path
from typing import Tuple, Optional


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    with open(pyproject_path, 'r') as f:
        content = f.read()

    version_match = re.search(r'version = "([^"]+)"', content)
    if not version_match:
        raise ValueError("Version not found in pyproject.toml")

    return version_match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch"""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_pyproject_version(new_version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")

    with open(pyproject_path, 'r') as f:
        content = f.read()

    # Update version in pyproject.toml
    content = re.sub(r'version = "[^"]*"', f'version = "{new_version}"', content)

    with open(pyproject_path, 'w') as f:
        f.write(content)

    print(f"Updated pyproject.toml version to {new_version}")


def update_setup_py_version(new_version: str) -> None:
    """Update version in setup.py"""
    setup_path = Path("setup.py")

    if not setup_path.exists():
        return  # setup.py is legacy, might not exist

    with open(setup_path, 'r') as f:
        content = f.read()

    # Update version in setup.py
    content = re.sub(r'version="[^"]*"', f'version="{new_version}"', content)

    with open(setup_path, 'w') as f:
        f.write(content)

    print(f"Updated setup.py version to {new_version}")


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <major|minor|patch>")
        sys.exit(1)

    bump_type = sys.argv[1].lower()
    if bump_type not in ["major", "minor", "patch"]:
        print("Error: Bump type must be 'major', 'minor', or 'patch'")
        sys.exit(1)

    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        new_version = bump_version(current_version, bump_type)
        print(f"New version: {new_version}")

        update_pyproject_version(new_version)
        update_setup_py_version(new_version)

        print(f"\nVersion bumped successfully to {new_version}")
        print("Remember to:")
        print("1. Update CHANGELOG.md")
        print("2. Commit changes: git add . && git commit -m 'Bump version to {new_version}'")
        print("3. Create tag: git tag v{new_version}")
        print("4. Push: git push && git push --tags")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()