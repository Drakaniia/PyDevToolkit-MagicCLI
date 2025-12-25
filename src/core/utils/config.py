"""
Configuration management module for PyDevToolkit-MagicCLI
Centralized configuration for security settings and operational parameters
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
@dataclass
class SecurityConfig:
    """Security-related configuration settings"""
    max_command_length: int = 500
    max_path_length: int = 1000
    allow_network_access: bool = True
    enable_rate_limiting: bool = True
    max_subprocess_timeout: int = 30  # seconds
    enable_input_sanitization: bool = True
    blocked_commands: list = None
    allowed_file_extensions: list = None

    def __post_init__(self):
        if self.blocked_commands is None:
            self.blocked_commands = [
                'rm', 'rmdir', 'del', 'format', 'mkfs', 'dd', 'chmod', 'chown'
            ]
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = [
                '.py', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml',
                '.txt', '.md', '.html', '.css', '.jsx', '.tsx', '.sql',
                '.xml', '.ini', '.cfg', '.conf', '.dockerfile', 'dockerfile',
                '.gitignore', '.env', '.sh', '.bash', '.zsh', '.bat', '.cmd'
            ]
@dataclass
class OperationalConfig:
    """Operational configuration settings"""
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_debug: bool = False
    max_log_size: int = 10485760  # 10MB
    backup_count: int = 5
    enable_color_output: bool = True
    enable_loading_animations: bool = True
class ConfigManager:
    """Centralized configuration manager"""

    def __init__(self, config_file: Optional[str] = None):
        self.security_config = SecurityConfig()
        self.operational_config = OperationalConfig()
        self.config_file = config_file or self._get_default_config_path()
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default path for configuration file"""
        # Look for config in current directory or in user's home directory
        config_paths = [
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.json",
            Path.home() / ".magiccli" / "config.yaml",
            Path.home() / ".magiccli" / "config.json",
        ]

        for path in config_paths:
            if path.exists():
                return str(path)

        # If no config exists, create default in project root
        default_path = Path.cwd() / "config.yaml"
        self._create_default_config(default_path)
        return str(default_path)

    def _create_default_config(self, path: Path) -> None:
        """Create a default configuration file"""
        config_data = {
            "security": asdict(self.security_config),
            "operational": asdict(self.operational_config)
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            if str(path).endswith('.yaml') or str(path).endswith('.yml'):
                # Try to use yaml if available, otherwise fallback to json
                try:
                    import yaml
                    yaml.dump(config_data, f, default_flow_style=False)
                except ImportError:
                    # Fall back to JSON if yaml is not available
                    json.dump(config_data, f, indent=2)
            else:
                json.dump(config_data, f, indent=2)

    def _load_config(self) -> None:
        """Load configuration from file"""
        if not Path(self.config_file).exists():
            return

        with open(self.config_file, 'r') as f:
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                # Try to use yaml if available, otherwise fallback to json
                try:
                    import yaml
                    config_data = yaml.safe_load(f)
                except ImportError:
                    # If yaml is not available, assume it's JSON format
                    config_data = json.load(f)
            else:
                config_data = json.load(f)

        if config_data:
            if 'security' in config_data:
                security_data = config_data['security']
                self.security_config = SecurityConfig(**security_data)

            if 'operational' in config_data:
                operational_data = config_data['operational']
                self.operational_config = OperationalConfig(**operational_data)

    def save_config(self) -> None:
        """Save current configuration to file"""
        config_data = {
            "security": asdict(self.security_config),
            "operational": asdict(self.operational_config)
        }

        with open(self.config_file, 'w') as f:
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                try:
                    import yaml
                    yaml.dump(config_data, f, default_flow_style=False)
                except ImportError:
                    # Fall back to JSON if yaml is not available
                    json.dump(config_data, f, indent=2)
            else:
                json.dump(config_data, f, indent=2)

    def get_security_setting(self, key: str) -> Any:
        """Get a security configuration setting"""
        return getattr(self.security_config, key, None)

    def get_operational_setting(self, key: str) -> Any:
        """Get an operational configuration setting"""
        return getattr(self.operational_config, key, None)

    def set_security_setting(self, key: str, value: Any) -> None:
        """Set a security configuration setting"""
        setattr(self.security_config, key, value)

    def set_operational_setting(self, key: str, value: Any) -> None:
        """Set an operational configuration setting"""
        setattr(self.operational_config, key, value)
# Global configuration instance
_config_manager: Optional[ConfigManager] = None
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
def get_security_config() -> SecurityConfig:
    """Get the security configuration"""
    config_manager = get_config_manager()
    return config_manager.security_config
def get_operational_config() -> OperationalConfig:
    """Get the operational configuration"""
    config_manager = get_config_manager()
    return config_manager.operational_config