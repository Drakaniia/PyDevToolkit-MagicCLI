#!/usr/bin/env python3
"""
Test script to verify git_log and git_recover enhancements
This tests that the remote fetch functionality works correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from github.git_log import GitLog
from github.git_recover import GitRecover


def test_git_log_enhancement():
    """Test that GitLog can fetch remote commits and display logs"""
    print("Testing GitLog enhancements...")

    git_log = GitLog()

    # Test that the fetch_remote_commits method exists and works
    print("  - Testing fetch_remote_commits method...")
    success = git_log.fetch_remote_commits()
    print(f"    Fetch result: {'Success' if success else 'May have failed (not in git repo or no remotes)'}")

    # Test that show_log accepts fetch_remote parameter
    print("  - Testing show_log with fetch_remote parameter...")
    try:
        git_log.show_log(limit=5, fetch_remote=True)
        print("    Success: show_log with fetch_remote=True works")
    except Exception as e:
        print(f"    Error: show_log with fetch_remote=True failed: {e}")

    # Test that get_commit_history accepts fetch_remote parameter
    print("  - Testing get_commit_history with fetch_remote parameter...")
    try:
        commits = git_log.get_commit_history(limit=10, fetch_remote=True)
        print(f"    Success: get_commit_history with fetch_remote=True works, found {len(commits)} commits")
    except Exception as e:
        print(f"    Error: get_commit_history with fetch_remote=True failed: {e}")

    # Test that get_commit_details accepts fetch_remote parameter
    print("  - Testing get_commit_details with fetch_remote parameter...")
    try:
        # This might fail if no commits exist, but the method should be callable
        details = git_log.get_commit_details("HEAD", fetch_remote=True)
        print("    Success: get_commit_details with fetch_remote=True works")
    except Exception as e:
        print(f"    Error: get_commit_details with fetch_remote=True failed: {e}")

    # Test that verify_commit_exists accepts fetch_remote parameter
    print("  - Testing verify_commit_exists with fetch_remote parameter...")
    try:
        exists = git_log.verify_commit_exists("HEAD", fetch_remote=True)
        print("    Success: verify_commit_exists with fetch_remote=True works")
    except Exception as e:
        print(f"    Error: verify_commit_exists with fetch_remote=True failed: {e}")


def test_git_recover_integration():
    """Test that GitRecover works with the enhanced GitLog functions"""
    print("\nTesting GitRecover integration...")

    git_log = GitLog()
    git_recover = GitRecover()

    # Test that the functions can be passed to GitRecover as expected
    print("  - Testing function parameter passing...")

    # These functions should now accept the additional fetch_remote parameter
    commit_history_func = git_log.get_commit_history
    commit_details_func = git_log.get_commit_details
    verify_commit_func = git_log.verify_commit_exists

    print("    Success: Function references obtained successfully")

    # Verify that these functions have the new fetch_remote parameter by checking their signatures
    import inspect
    sig_history = inspect.signature(commit_history_func)
    sig_details = inspect.signature(commit_details_func)
    sig_verify = inspect.signature(verify_commit_func)

    has_fetch_remote_history = 'fetch_remote' in sig_history.parameters
    has_fetch_remote_details = 'fetch_remote' in sig_details.parameters
    has_fetch_remote_verify = 'fetch_remote' in sig_verify.parameters

    print(f"    - get_commit_history has fetch_remote param: {'Success' if has_fetch_remote_history else 'Error'}")
    print(f"    - get_commit_details has fetch_remote param: {'Success' if has_fetch_remote_details else 'Error'}")
    print(f"    - verify_commit_exists has fetch_remote param: {'Success' if has_fetch_remote_verify else 'Error'}")


def test_backward_compatibility():
    """Test that the enhanced functions still work without the new parameter"""
    print("\nTesting backward compatibility...")

    git_log = GitLog()

    # Test original function calls still work (without fetch_remote parameter)
    try:
        commits = git_log.get_commit_history(limit=5)  # Without fetch_remote
        print("    Success: get_commit_history works without fetch_remote parameter")
    except Exception as e:
        print(f"    Error: get_commit_history without fetch_remote failed: {e}")

    try:
        details = git_log.get_commit_details("HEAD")  # Without fetch_remote
        print("    Success: get_commit_details works without fetch_remote parameter")
    except Exception as e:
        print(f"    Error: get_commit_details without fetch_remote failed: {e}")

    try:
        exists = git_log.verify_commit_exists("HEAD")  # Without fetch_remote
        print("    Success: verify_commit_exists works without fetch_remote parameter")
    except Exception as e:
        print(f"    Error: verify_commit_exists without fetch_remote failed: {e}")


def main():
    print("Testing Git Log and Recover Enhancements")
    print("=" * 50)

    test_git_log_enhancement()
    test_git_recover_integration()
    test_backward_compatibility()

    print("\n" + "=" * 50)
    print("Testing completed!")


if __name__ == "__main__":
    main()