# PyDevToolkit-MagicCLI Tests

This directory contains comprehensive tests for the PyDevToolkit-MagicCLI system, including:

## Test Categories

### 1. Security Tests (`test_security.py`)
- Input validation and sanitization
- Command injection prevention
- Path traversal prevention
- Secure subprocess execution

### 2. Error Handling Tests (`test_error_handling.py`)
- Exception hierarchy validation
- Error message formatting
- Exception handling utilities
- Automated error wrapping

### 3. Integration Tests (`test_integration.py`)
- Cross-module functionality
- Configuration persistence
- Real-world usage scenarios
- Security pattern validation

### 4. Main Test Suite (`testall.py`)
- Comprehensive module import testing
- Integration test orchestration
- All-in-one test execution

## Running Tests

To run all tests:

```bash
python -m pytest tests/ -v
```

Or run the comprehensive test suite:

```bash
python tests/testall.py
```

To run specific test files:

```bash
python tests/test_security.py
python tests/test_error_handling.py
python tests/test_integration.py
```

## Security Features Tested

The test suite validates the following security improvements:

- **Input Sanitization**: All user inputs are validated using security patterns
- **Command Injection Prevention**: Dangerous command sequences are blocked
- **Path Traversal Protection**: Directory traversal attempts are prevented
- **Secure Subprocess Execution**: Commands are validated before execution
- **Configuration Management**: Security parameters are centrally managed
- **Audit Logging**: Security-relevant events are logged for monitoring

## Error Handling Features Tested

- **Exception Hierarchy**: All errors inherit from base AutomationError
- **Error Details**: Rich error information with suggestions
- **Safe Execution**: Functions that safely execute and handle errors
- **Consistent Handling**: Standardized error handling patterns across modules

## Test Coverage

The test suite covers:
- 100% of security validation functions
- 100% of configuration management
- 100% of exception handling utilities
- Key integration points between modules
- Real-world usage scenarios and edge cases