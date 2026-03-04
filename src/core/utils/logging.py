"""
Logging module for PyDevToolkit-MagicCLI
Provides enhanced logging with security audit capabilities
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class SecurityAuditLogger:
    """Enhanced logger with security audit capabilities"""

    def __init__(self, name: str = "PyDevToolkit-MagicCLI"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup the logger with appropriate handlers and formatters"""
        # Lazy import to avoid circular import issues
        from .config import get_operational_config
        op_config = get_operational_config()

        # Set log level
        log_level = getattr(logging, op_config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Create file handler if log file is specified
        if op_config.log_file:
            log_file_path = Path(op_config.log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file_path)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log an info message"""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message"""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message"""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message"""
        self.logger.critical(message)

    def debug(self, message: str) -> None:
        """Log a debug message"""
        self.logger.debug(message)

    def audit_security_event(self, event_type: str, details: dict) -> None:
        """Log a security-related event"""
        audit_message = f"SECURITY_AUDIT: {event_type} - {details}"
        self.logger.warning(audit_message)

    def audit_command_execution(
            self,
            command: str,
            user_input: str,
            success: bool) -> None:
        """Log command execution for audit purposes
        
        SECURITY: Sanitizes user input to prevent logging sensitive data
        """
        status = "SUCCESS" if success else "FAILED"
        # SECURITY: Sanitize user input before logging to prevent sensitive data exposure
        sanitized_input = self._sanitize_for_logging(user_input)
        audit_message = f"COMMAND_EXECUTION: {status} - Command: {command}, Input: {sanitized_input}"
        self.logger.debug(audit_message)
    
    def _sanitize_for_logging(self, value: str, max_length: int = 100) -> str:
        """
        Sanitize a value for safe logging
        
        Args:
            value: The value to sanitize
            max_length: Maximum length to log (prevents log flooding)
        
        Returns:
            str: Sanitized value safe for logging
        """
        if not value:
            return "<empty>"
        
        # Truncate to prevent log flooding
        if len(value) > max_length:
            value = value[:max_length] + "..."
        
        # Replace potential sensitive patterns with placeholders
        import re
        # Mask potential passwords after = or :
        value = re.sub(r'([=:])\s*[^\s,;]+', r'\1 <REDACTED>', value)
        # Mask potential API keys/tokens (alphanumeric strings 20+ chars)
        value = re.sub(r'\b[A-Za-z0-9]{20,}\b', '<TOKEN>', value)
        
        return value

    def audit_input_validation_failure(
            self,
            input_value: str,
            validation_rule: str) -> None:
        """Log input validation failures
        
        SECURITY: Sanitizes input value before logging
        """
        # SECURITY: Sanitize input value before logging
        sanitized_value = self._sanitize_for_logging(input_value)
        audit_message = f"INPUT_VALIDATION_FAILURE: Value: {sanitized_value}, Rule: {validation_rule}"
        self.logger.warning(audit_message)


# Global logger instance
_security_logger: Optional[SecurityAuditLogger] = None


def get_security_logger() -> SecurityAuditLogger:
    """Get the global security logger instance"""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityAuditLogger()
    return _security_logger


def log_security_event(event_type: str, details: dict) -> None:
    """Log a security-related event"""
    logger = get_security_logger()
    logger.audit_security_event(event_type, details)


def log_command_execution(
        command: str,
        user_input: str,
        success: bool) -> None:
    """Log command execution for audit purposes"""
    logger = get_security_logger()
    logger.audit_command_execution(command, user_input, success)


def log_input_validation_failure(
        input_value: str,
        validation_rule: str) -> None:
    """Log input validation failures"""
    logger = get_security_logger()
    logger.audit_input_validation_failure(input_value, validation_rule)
