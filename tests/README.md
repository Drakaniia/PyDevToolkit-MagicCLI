# Test Suite for Python Automation System

This directory contains the comprehensive test suite for the Python Automation System. The test suite ensures that all modules work correctly and verifies that new modules are automatically tested.

## Test Suite Overview

The test suite (`testall.py`) includes:
- **Unit tests** for individual modules and components
- **Integration tests** to verify modules work together
- **Import tests** to ensure all modules can be imported successfully
- **Automatic discovery** of new modules in the codebase

## Prerequisites

Before running the tests, ensure that:
- Python 3.7 or higher is installed
- The project dependencies are installed (run `pip install -r requirements-test.txt` if available)

## How to Run the Tests

### Method 1: Run all tests directly
```bash
python tests/testall.py
```

**Note for Windows users**: If you encounter a "Python was not found" error in Git Bash, try using:
```bash
py -3 tests/testall.py
```
or
```bash
python3 tests/testall.py
```

### Method 2: Run with verbose output
```bash
python -m unittest tests.testall -v
```

### Method 3: Run with pytest (if installed)
```bash
python -m pytest tests/testall.py -v
```

Note: If `pytest` command is not found, try using `python -m pytest` instead, or install pytest with:
```bash
pip install pytest
```

**Note**: Using pytest will only run the statically defined tests (27 tests). To run the full test suite including dynamically discovered modules (70 tests total), use Method 1.

### Method 4: Run specific test classes
```bash
python -m unittest tests.testall.TestCoreComponents -v
```

## Understanding the Test Output

- **Tests run**: Total number of tests executed
- **Failures**: Number of tests that failed
- **Errors**: Number of tests that had errors during execution
- **OK/FAIL**: Overall test result status

## Automatic Module Discovery

The test suite automatically discovers and tests:
- All Python files in the `src/` directory
- All subdirectories including `github/`, `core/`, `backend/`, and `dev_mode/`
- Any new modules added to the codebase

## Adding New Tests

The test suite is designed to be extensible. To add new tests:

1. Add test methods to existing test classes in `tests/testall.py`
2. Create new test classes that inherit from `unittest.TestCase`
3. The automatic discovery will detect new modules in the codebase automatically

## Maintaining Test Coverage

The test suite ensures:
- All existing modules are tested for importability
- Core functionality is verified
- Integration between modules works as expected
- New modules added to the codebase are automatically included in testing