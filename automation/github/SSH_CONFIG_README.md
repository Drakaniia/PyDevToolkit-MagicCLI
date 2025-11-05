# Git SSH Configuration Module

## Overview

The `GitSSHConfig` module provides a complete automated SSH setup assistant that ensures users can securely connect to GitHub (or any Git remote) without manual intervention. This feature detects, validates, and configures SSH keys, GitHub SSH access, and SSH agent settings intelligently.

## Features

### 🔍 SSH Key Detection and Validation
- Detects existing SSH keys (id_rsa, id_ed25519, etc.) in `~/.ssh/`
- Validates key permissions (chmod 600 private key, chmod 644 public key)
- Displays key fingerprints and locations
- Automatically fixes permission issues

### 🔧 Automatic SSH Key Generation
- Generates new SSH key pairs if none exist
- Default: ed25519 (recommended for security)
- Support for RSA keys as fallback
- Custom filename and passphrase options
- Proper permission setup

### 🤖 SSH Agent Management
- Detects SSH agent availability
- Automatically starts SSH agent if needed
- Loads keys into SSH agent
- Cross-platform support (Windows, macOS, Linux)

### 🌐 GitHub Integration
- Detects if SSH key is already added to GitHub
- Automatic public key upload via GitHub API
- Uses Personal Access Token (PAT) authentication
- Intelligent duplicate detection

### ⚙️ SSH Config File Management
- Creates or updates `~/.ssh/config` file
- Intelligent merging without overwriting unrelated entries
- Validates configuration syntax
- Platform-specific optimizations

### 🧪 Connection Testing
- Automatic SSH connection testing to GitHub
- Clear success/failure reporting
- Actionable debugging suggestions
- Connection verification

### 🔄 Git Global Settings
- Configures URL rewriting for GitHub (SSH over HTTPS)
- User name and email verification
- Remote URL mapping summary

## Usage

### Command Line Interface

```bash
# Interactive mode (prompts for user input)
python automation/github/git_ssh_config.py

# Automatic mode (uses defaults, no prompts)
python automation/github/git_ssh_config.py --auto

# Custom log file
python automation/github/git_ssh_config.py --log my_setup.log

# Auto mode with custom log
python automation/github/git_ssh_config.py --auto --log setup.log
```

### Programmatic Usage

```python
from automation.github import GitSSHConfig

# Create instance
config = GitSSHConfig(auto_mode=True)

# Run full setup
success = config.run()

# Or use individual methods
keys = config.detect_existing_keys()
key_info = config.generate_ssh_key('ed25519')
config.configure_ssh_config(key_info['private_path'])
connected, output = config.verify_ssh_connection()
```

## Environment Variables

### GitHub Token
Set one of these environment variables for automatic GitHub integration:
- `GITHUB_TOKEN`
- `GH_TOKEN`

The token needs `write:public_key` or `admin:public_key` scope.

### Example
```bash
export GITHUB_TOKEN="ghp_your_token_here"
python automation/github/git_ssh_config.py --auto
```

## Interactive Mode Workflow

1. **🔍 Detection**: Scans for existing SSH keys
2. **❓ Choice**: Ask to use existing or generate new key
3. **🔧 Configuration**: Prompt for key type and settings
4. **🔐 Security**: Optional passphrase setup
5. **🌐 GitHub**: Request GitHub token for upload
6. **⚙️ Setup**: Configure SSH config file
7. **🧪 Testing**: Verify connection to GitHub
8. **📋 Summary**: Display configuration results

## Auto Mode Workflow

1. **🔍 Detection**: Scans for existing SSH keys
2. **🔧 Smart Choice**: Use existing ed25519 or generate new
3. **🔐 Security**: No passphrase for automation
4. **🌐 GitHub**: Use environment token if available
5. **⚙️ Setup**: Auto-configure SSH config file
6. **🧪 Testing**: Verify connection to GitHub
7. **📋 Summary**: Display configuration results

## Cross-Platform Support

### Windows
- SSH agent service management
- PowerShell integration
- Git Bash compatibility
- Windows-specific path handling

### macOS
- Keychain integration (`UseKeychain yes`)
- SSH agent optimization
- macOS-specific permissions

### Linux
- Standard SSH agent handling
- Distribution-agnostic approach
- Proper file permissions

### WSL (Windows Subsystem for Linux)
- Automatic WSL detection
- Path adaptation (`/mnt/c/Users/...` to `~`)
- Cross-environment compatibility

## Security Features

### Key Security
- Enforces proper file permissions (600 for private, 644 for public)
- Supports passphrase-protected keys
- Uses modern ed25519 encryption by default
- Automatic permission fixing

### Connection Security
- Validates SSH connections before use
- Batch mode testing (non-interactive)
- Connection timeout protection
- Host key verification

### Token Security
- Environment variable preference
- Secure token input (hidden)
- Minimal required permissions
- No token storage

## Configuration Files

### SSH Config Template
```
# Auto-configured by git_ssh_config.py
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    UseKeychain yes  # macOS only
    IdentitiesOnly yes
```

### Git Global Config
```
# URL rewriting for SSH
[url "git@github.com:"]
    insteadOf = https://github.com/
```

## Logging

### Log File Location
- Default: `~/.ssh_setup.log`
- Custom: Use `--log` parameter
- Appends to existing logs

### Log Content
- Timestamp for each operation
- Command execution details
- Success/failure status
- Error messages and stack traces
- Configuration changes

## Error Handling

### Custom Exceptions
- `SSHConfigError`: SSH configuration issues
- `GitHubAPIError`: GitHub API problems
- Inherits from project's `AutomationError`

### Error Recovery
- Automatic retry mechanisms
- Clear error messages
- Actionable suggestions
- Graceful fallbacks

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Wrong key permissions | Auto-fix with chmod 600/644 |
| SSH agent not running | Agent service stopped | Auto-start SSH agent |
| GitHub API error | Invalid token/permissions | Check token scopes |
| Host key verification failed | First connection to GitHub | Accept host key manually |
| Command not found | SSH/Git not in PATH | Install Git and SSH tools |

## Advanced Features

### Multiple SSH Identities
```bash
# Work identity
Host github.com-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_work

# Personal identity  
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_personal
```

### GitHub Enterprise Support
- Custom domain detection
- Enterprise API endpoints
- Organization-specific configurations

### Backup and Recovery
- Automatic SSH config backup
- Timestamped backup files
- Recovery instructions in logs

## Integration Examples

### CI/CD Pipeline
```bash
# Set token in CI environment
export GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}"

# Run automated setup
python automation/github/git_ssh_config.py --auto --log ci_setup.log
```

### Development Setup Script
```python
from automation.github import GitSSHConfig

def setup_developer_environment():
    config = GitSSHConfig(auto_mode=False)
    
    # Interactive setup for new developers
    if config.run():
        print("✅ SSH setup complete!")
        print("🚀 Ready for Git operations")
    else:
        print("❌ Setup failed, check logs")
```

## Troubleshooting

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

config = GitSSHConfig()
config.run()
```

### Manual Verification
```bash
# Test SSH connection manually
ssh -T git@github.com

# Check SSH agent
ssh-add -l

# Verify SSH config
cat ~/.ssh/config
```

### Common Commands
```bash
# Regenerate host keys
ssh-keygen -R github.com

# Add key manually
ssh-add ~/.ssh/id_ed25519

# Test with verbose output
ssh -vT git@github.com
```

## Requirements

### System Requirements
- Python 3.8+
- Git installed and in PATH
- SSH client (openssh)
- Internet connection for GitHub API

### Python Dependencies
- `requests` (for GitHub API)
- `pathlib` (built-in)
- `subprocess` (built-in)
- `platform` (built-in)

### Optional Dependencies
- PowerShell (Windows)
- Keychain services (macOS)

## License

This module is part of the automation project and follows the same license terms.

## Contributing

When contributing to this module:
1. Test on all supported platforms
2. Add unit tests for new features
3. Update this documentation
4. Follow the project's coding standards
5. Test both interactive and auto modes

## Support

For issues or questions:
1. Check the logs in `~/.ssh_setup.log`
2. Run with `--help` for usage information
3. Test individual components programmatically
4. Refer to the troubleshooting section above