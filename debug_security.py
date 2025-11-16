#!/usr/bin/env python3
"""
Debug the security validation step by step
"""
import re
import sys
sys.path.insert(0, sys.argv[1])

def debug_validation(user_input):
    """Debug the validation step by step"""

    # Copy the exact logic from the security module to debug
    if not user_input:
        print(f"Input '{user_input}' is empty, returning True")
        return True

    # Check for dangerous characters/sequences
    dangerous_patterns = [
        r';',           # Command separators
        r'&&',          # Command execution
        r'||',          # Command execution
        r'\|',          # Pipe
        r'\$\(',        # Command substitution
        r'`',           # Command substitution
        r'&',           # Background execution
    ]

    print(f"Checking input: '{user_input}'")

    for i, pattern in enumerate(dangerous_patterns):
        if re.search(pattern, user_input):
            print(f"  Pattern {i} ({pattern}) matched: '{user_input}'")
            print(f"  Returning False due to dangerous pattern match")
            return False
        else:
            print(f"  Pattern {i} ({pattern}) did not match: '{user_input}'")

    # Check against safe command pattern
    SAFE_COMMAND_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\/\s=]+$')
    match_result = bool(SAFE_COMMAND_PATTERN.match(user_input))
    print(f"  Safe pattern match result: {match_result} for pattern: {SAFE_COMMAND_PATTERN.pattern}")

    return match_result

# Test with multiple inputs
test_inputs = ["git", "status", "--porcelain", "--untracked-files=all"]

for test_input in test_inputs:
    print(f"\n--- Testing: '{test_input}' ---")
    result = debug_validation(test_input)
    print(f"Final result: {result}")
    print("-" * 30)

# Let's also test the actual security validator
print("\n--- Testing with actual SecurityValidator ---")
from core.security import SecurityValidator

for test_input in test_inputs:
    result = SecurityValidator.validate_command_input(test_input)
    print(f"'{test_input}' -> {result}")