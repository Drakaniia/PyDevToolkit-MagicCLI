"""
Git SSH Configuration Module
Handles complete automated SSH setup for Git-based workflows with GitHub
"""
import os
import sys
import subprocess
import platform
import json
import requests
import getpass
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import re
import logging
from datetime import datetime

from automation.core.exceptions import (
    GitError, 
    AutomationError, 
    ErrorSeverity, 
    handle_errors,
    ExceptionHandler,
    SSHConfigError,
    GitHubAPIError
)


class GitSSHConfig:
    """Complete SSH configuration and management for Git workflows"""
    
    def __init__(self, auto_mode: bool = False, log_file: Optional[str] = None):
        self.auto_mode = auto_mode
        self.os_type = platform.system().lower()
        self.home_dir = Path.home()
        self.ssh_dir = self.home_dir / ".ssh"
        self.config_file = self.ssh_dir / "config"
        self.log_file = log_file or str(self.home_dir / ".ssh_setup.log")
        
        # Setup logging
        self._setup_logging()
        
        # Color codes for CLI output
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'blue': '\033[94m',
            'bold': '\033[1m',
            'end': '\033[0m'
        } if not self._is_windows() else {k: '' for k in ['green', 'yellow', 'red', 'blue', 'bold', 'end']}
        
        # SSH key types and preferences
        self.key_types = {
            'ed25519': {
                'filename': 'id_ed25519',
                'command': ['-t', 'ed25519', '-a', '100'],
                'preferred': True
            },
            'rsa': {
                'filename': 'id_rsa',
                'command': ['-t', 'rsa', '-b', '4096'],
                'preferred': False
            }
        }
        
        self.logger.info(f"Initialized GitSSHConfig for {self.os_type} system")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)
        self.logger.info("SSH Configuration Session Started")
    
    def _is_windows(self) -> bool:
        """Check if running on Windows"""
        return self.os_type == 'windows'
    
    def _is_wsl(self) -> bool:
        """Check if running in WSL environment"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text"""
        return f"{self.colors[color]}{text}{self.colors['end']}"
    
    def _print_status(self, message: str, status: str = "info"):
        """Print colored status message"""
        color_map = {
            'success': 'green',
            'warning': 'yellow', 
            'error': 'red',
            'info': 'blue'
        }
        color = color_map.get(status, 'blue')
        
        icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        }
        icon = icons.get(status, 'ℹ️')
        
        print(f"{icon} {self._colorize(message, color)}")
        self.logger.info(f"{status.upper()}: {message}")
    
    def _run_command(self, command: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run shell command with proper error handling"""
        try:
            self.logger.info(f"Executing command: {' '.join(command)}")
            result = subprocess.run(
                command, 
                capture_output=capture_output, 
                text=True, 
                check=check
            )
            if result.stdout:
                self.logger.info(f"Command output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            raise SSHConfigError(
                f"Command failed: {' '.join(command)}",
                details={
                    'command': ' '.join(command),
                    'return_code': e.returncode,
                    'stderr': e.stderr or '',
                    'stdout': e.stdout or ''
                },
                suggestion="Check the command and try again"
            )
        except FileNotFoundError:
            raise SSHConfigError(
                f"Command not found: {command[0]}",
                suggestion=f"Make sure {command[0]} is installed and in your PATH"
            )
    
    def detect_existing_keys(self) -> List[Dict[str, Any]]:
        """Detect existing SSH keys in ~/.ssh directory"""
        self._print_status("Detecting existing SSH keys...", "info")
        
        if not self.ssh_dir.exists():
            self._print_status("SSH directory doesn't exist, will create it", "warning")
            return []
        
        keys = []
        for key_type, config in self.key_types.items():
            private_key = self.ssh_dir / config['filename']
            public_key = self.ssh_dir / f"{config['filename']}.pub"
            
            if private_key.exists() and public_key.exists():
                # Check permissions
                private_perms = oct(private_key.stat().st_mode)[-3:]
                public_perms = oct(public_key.stat().st_mode)[-3:]
                
                # Get fingerprint
                fingerprint = self._get_key_fingerprint(str(public_key))
                
                key_info = {
                    'type': key_type,
                    'private_path': str(private_key),
                    'public_path': str(public_key),
                    'private_perms': private_perms,
                    'public_perms': public_perms,
                    'fingerprint': fingerprint,
                    'perms_correct': private_perms == '600' and public_perms in ['644', '644']
                }
                keys.append(key_info)
                
                self._print_status(
                    f"Found {key_type} key: {fingerprint}", 
                    "success" if key_info['perms_correct'] else "warning"
                )
        
        if not keys:
            self._print_status("No existing SSH keys found", "warning")
        
        return keys
    
    def _get_key_fingerprint(self, public_key_path: str) -> str:
        """Get SSH key fingerprint"""
        try:
            result = self._run_command(['ssh-keygen', '-lf', public_key_path])
            return result.stdout.strip().split()[1]
        except Exception as e:
            self.logger.warning(f"Could not get fingerprint for {public_key_path}: {e}")
            return "Unknown"
    
    def _fix_key_permissions(self, private_key: str, public_key: str) -> bool:
        """Fix SSH key permissions"""
        try:
            # Set private key permissions to 600
            os.chmod(private_key, 0o600)
            # Set public key permissions to 644  
            os.chmod(public_key, 0o644)
            self._print_status(f"Fixed permissions for {Path(private_key).name}", "success")
            return True
        except Exception as e:
            self._print_status(f"Failed to fix permissions: {e}", "error")
            return False
    
    @handle_errors()
    def generate_ssh_key(self, key_type: str = 'ed25519', custom_filename: Optional[str] = None, passphrase: Optional[str] = None) -> Dict[str, str]:
        """Generate new SSH key pair"""
        self._print_status(f"Generating new {key_type} SSH key...", "info")
        
        # Ensure SSH directory exists
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Determine filename
        if custom_filename:
            key_filename = custom_filename
        else:
            key_filename = self.key_types[key_type]['filename']
        
        private_key_path = self.ssh_dir / key_filename
        public_key_path = self.ssh_dir / f"{key_filename}.pub"
        
        # Check if key already exists
        if private_key_path.exists():
            if not self.auto_mode:
                overwrite = input(f"Key {key_filename} already exists. Overwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    raise SSHConfigError("Key generation cancelled by user")
            else:
                self._print_status(f"Overwriting existing key {key_filename}", "warning")
        
        # Get passphrase
        if passphrase is None and not self.auto_mode:
            passphrase = getpass.getpass(f"Enter passphrase for the key (press Enter for no passphrase): ")
        elif passphrase is None:
            passphrase = ""
        
        # Build ssh-keygen command
        cmd = ['ssh-keygen'] + self.key_types[key_type]['command']
        cmd.extend(['-f', str(private_key_path)])
        
        if passphrase:
            cmd.extend(['-N', passphrase])
        else:
            cmd.extend(['-N', ''])
        
        # Add comment with hostname and date
        hostname = platform.node()
        comment = f"auto-generated-{hostname}-{datetime.now().strftime('%Y%m%d')}"
        cmd.extend(['-C', comment])
        
        # Generate key
        self._run_command(cmd, capture_output=True)
        
        # Verify key was created and fix permissions
        if not private_key_path.exists() or not public_key_path.exists():
            raise SSHConfigError("SSH key generation failed - files not created")
        
        self._fix_key_permissions(str(private_key_path), str(public_key_path))
        
        # Get fingerprint
        fingerprint = self._get_key_fingerprint(str(public_key_path))
        
        key_info = {
            'private_path': str(private_key_path),
            'public_path': str(public_key_path), 
            'fingerprint': fingerprint,
            'type': key_type
        }
        
        self._print_status(f"Successfully generated {key_type} key", "success")
        self._print_status(f"Fingerprint: {fingerprint}", "info")
        self._print_status(f"Location: {private_key_path}", "info")
        
        return key_info
    
    def _check_ssh_agent(self) -> bool:
        """Check if SSH agent is running and start if needed"""
        try:
            # Try to list keys to see if agent is accessible
            result = self._run_command(['ssh-add', '-l'], check=False)
            if result.returncode == 0:
                self._print_status("SSH agent is running", "success")
                return True
            elif result.returncode == 1:
                # Agent running but no keys
                self._print_status("SSH agent running but no keys loaded", "info")
                return True
            else:
                # Agent not running
                return self._start_ssh_agent()
        except Exception:
            return self._start_ssh_agent()
    
    def _start_ssh_agent(self) -> bool:
        """Start SSH agent"""
        try:
            if self._is_windows():
                # On Windows, try to start ssh-agent service
                self._run_command(['powershell', '-Command', 'Start-Service ssh-agent'], check=False)
                self._print_status("Started SSH agent service", "success")
            else:
                # On Unix-like systems, eval ssh-agent output
                result = self._run_command(['ssh-agent', '-s'])
                # Parse and set environment variables
                for line in result.stdout.split('\n'):
                    if 'SSH_AUTH_SOCK' in line or 'SSH_AGENT_PID' in line:
                        key, value = line.split('=', 1)
                        value = value.rstrip(';')
                        os.environ[key] = value
                self._print_status("Started SSH agent", "success")
            return True
        except Exception as e:
            self._print_status(f"Failed to start SSH agent: {e}", "warning")
            return False
    
    def add_key_to_agent(self, private_key_path: str) -> bool:
        """Add SSH key to the SSH agent"""
        try:
            self._check_ssh_agent()
            self._run_command(['ssh-add', private_key_path])
            self._print_status(f"Added key to SSH agent: {Path(private_key_path).name}", "success")
            return True
        except Exception as e:
            self._print_status(f"Failed to add key to agent: {e}", "warning")
            return False
    
    def _get_github_token(self) -> Optional[str]:
        """Get GitHub Personal Access Token"""
        # Check environment variable first
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        if token:
            self._print_status("Found GitHub token in environment", "success")
            return token
        
        if self.auto_mode:
            self._print_status("No GitHub token found in environment for auto mode", "warning")
            return None
        
        print(f"\n{self._colorize('GitHub Personal Access Token Required', 'bold')}")
        print("To automatically upload your SSH key to GitHub, we need a Personal Access Token.")
        print("Create one at: https://github.com/settings/tokens")
        print("Required scope: 'write:public_key' or 'admin:public_key'")
        print()
        
        token = getpass.getpass("Enter your GitHub Personal Access Token (or press Enter to skip): ")
        return token.strip() if token.strip() else None
    
    def check_key_on_github(self, public_key_content: str, token: str) -> bool:
        """Check if SSH key is already added to GitHub"""
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/user/keys', headers=headers, timeout=10)
            response.raise_for_status()
            
            existing_keys = response.json()
            public_key_content = public_key_content.strip()
            
            for key in existing_keys:
                if key['key'].strip() == public_key_content:
                    self._print_status(f"Key already exists on GitHub: {key['title']}", "info")
                    return True
            
            return False
            
        except requests.RequestException as e:
            raise GitHubAPIError(
                f"Failed to check GitHub keys: {e}",
                suggestion="Check your token permissions and internet connection"
            )
    
    def upload_key_to_github(self, public_key_path: str, token: str) -> bool:
        """Upload SSH public key to GitHub"""
        try:
            # Read public key
            with open(public_key_path, 'r') as f:
                public_key_content = f.read().strip()
            
            # Check if key already exists
            if self.check_key_on_github(public_key_content, token):
                return True
            
            # Prepare key data
            hostname = platform.node()
            title = f"Auto-configured by git_ssh_config.py on {hostname}"
            
            key_data = {
                'title': title,
                'key': public_key_content
            }
            
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Upload key
            response = requests.post(
                'https://api.github.com/user/keys',
                headers=headers,
                json=key_data,
                timeout=10
            )
            
            if response.status_code == 201:
                self._print_status("Successfully uploaded SSH key to GitHub", "success")
                return True
            elif response.status_code == 422:
                error_msg = response.json().get('message', 'Unknown error')
                if 'already exists' in error_msg.lower():
                    self._print_status("SSH key already exists on GitHub", "info")
                    return True
                else:
                    raise GitHubAPIError(f"GitHub API error: {error_msg}")
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            raise GitHubAPIError(
                f"Failed to upload key to GitHub: {e}",
                suggestion="Check your token permissions and internet connection"
            )
        
        return False
    
    def _backup_ssh_config(self) -> Optional[str]:
        """Create backup of existing SSH config"""
        if not self.config_file.exists():
            return None
        
        backup_path = f"{self.config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with open(self.config_file, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            self._print_status(f"Backed up SSH config to {backup_path}", "info")
            return backup_path
        except Exception as e:
            self._print_status(f"Failed to backup SSH config: {e}", "warning")
            return None
    
    def configure_ssh_config(self, private_key_path: str, host: str = "github.com") -> bool:
        """Configure SSH config file for GitHub"""
        try:
            # Ensure SSH directory exists
            self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
            
            # Backup existing config
            self._backup_ssh_config()
            
            # Read existing config
            existing_config = ""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    existing_config = f.read()
            
            # Check if GitHub host already configured
            github_pattern = r'Host\s+github\.com'
            if re.search(github_pattern, existing_config, re.IGNORECASE):
                if not self.auto_mode:
                    update = input("GitHub SSH config already exists. Update it? (y/n): ").strip().lower()
                    if update != 'y':
                        self._print_status("Skipped SSH config update", "info")
                        return True
                
                # Remove existing GitHub config
                pattern = r'Host\s+github\.com.*?(?=Host\s+|\Z)'
                existing_config = re.sub(pattern, '', existing_config, flags=re.DOTALL | re.IGNORECASE)
            
            # Prepare new GitHub config
            use_keychain = "yes" if self.os_type == "darwin" else "no"
            
            github_config = f"""
# Auto-configured by git_ssh_config.py
Host github.com
    HostName github.com
    User git
    IdentityFile {private_key_path}
    AddKeysToAgent yes
    UseKeychain {use_keychain}
    IdentitiesOnly yes

"""
            
            # Write updated config
            with open(self.config_file, 'w') as f:
                f.write(github_config + existing_config)
            
            # Set proper permissions
            os.chmod(self.config_file, 0o600)
            
            self._print_status("Updated SSH config file", "success")
            return True
            
        except Exception as e:
            raise SSHConfigError(
                f"Failed to configure SSH config: {e}",
                suggestion="Check file permissions and try again"
            )
    
    def verify_ssh_connection(self, host: str = "github.com") -> Tuple[bool, str]:
        """Test SSH connection to GitHub"""
        self._print_status(f"Testing SSH connection to {host}...", "info")
        
        try:
            # Test SSH connection
            result = self._run_command(
                ['ssh', '-T', f'git@{host}', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10'],
                check=False
            )
            
            output = result.stdout + result.stderr
            
            if "successfully authenticated" in output.lower():
                self._print_status("SSH authentication successful!", "success")
                return True, output
            elif "permission denied" in output.lower():
                self._print_status("SSH connection failed - permission denied", "error")
                return False, output
            else:
                self._print_status(f"SSH connection test completed with output: {output}", "info")
                return "authenticated" in output.lower(), output
                
        except Exception as e:
            error_msg = str(e)
            self._print_status(f"SSH connection test failed: {error_msg}", "error")
            return False, error_msg
    
    def configure_git_settings(self) -> bool:
        """Configure Git global settings for SSH usage"""
        try:
            self._print_status("Configuring Git global settings...", "info")
            
            # Set URL rewriting for GitHub
            self._run_command([
                'git', 'config', '--global', 
                'url.git@github.com:.insteadOf', 
                'https://github.com/'
            ])
            
            # Check and configure user name and email
            try:
                user_name = self._run_command(['git', 'config', '--global', 'user.name']).stdout.strip()
                user_email = self._run_command(['git', 'config', '--global', 'user.email']).stdout.strip()
                
                if user_name and user_email:
                    self._print_status(f"Git user: {user_name} <{user_email}>", "info")
                else:
                    if not self.auto_mode:
                        if not user_name:
                            user_name = input("Enter your Git username: ").strip()
                            if user_name:
                                self._run_command(['git', 'config', '--global', 'user.name', user_name])
                        
                        if not user_email:
                            user_email = input("Enter your Git email: ").strip()
                            if user_email:
                                self._run_command(['git', 'config', '--global', 'user.email', user_email])
                    else:
                        self._print_status("Git user name/email not configured (auto mode)", "warning")
                        
            except subprocess.CalledProcessError:
                # Git config not set
                if not self.auto_mode:
                    self._print_status("Git user not configured", "warning")
            
            self._print_status("Git global settings configured", "success")
            return True
            
        except Exception as e:
            self._print_status(f"Failed to configure Git settings: {e}", "warning")
            return False
    
    def get_configuration_summary(self, key_info: Dict[str, str]) -> Dict[str, Any]:
        """Generate configuration summary"""
        summary = {
            'ssh_key': {
                'path': key_info.get('private_path', 'N/A'),
                'type': key_info.get('type', 'N/A'),
                'fingerprint': key_info.get('fingerprint', 'N/A')
            },
            'config_file': str(self.config_file),
            'ssh_agent': 'Running' if self._check_ssh_agent() else 'Not running',
            'github_connection': 'Unknown',
            'git_settings': 'Configured'
        }
        
        # Test GitHub connection
        connected, _ = self.verify_ssh_connection()
        summary['github_connection'] = 'Success' if connected else 'Failed'
        
        return summary
    
    def display_summary(self, summary: Dict[str, Any]):
        """Display configuration summary"""
        print(f"\n{self._colorize('SSH Configuration Summary', 'bold')}")
        print("="*50)
        print(f"SSH Key Type: {summary['ssh_key']['type']}")
        print(f"SSH Key Path: {summary['ssh_key']['path']}")
        print(f"Key Fingerprint: {summary['ssh_key']['fingerprint']}")
        print(f"SSH Config File: {summary['config_file']}")
        print(f"SSH Agent Status: {summary['ssh_agent']}")
        print(f"GitHub Connection: {self._colorize(summary['github_connection'], 'green' if summary['github_connection'] == 'Success' else 'red')}")
        print(f"Git Settings: {summary['git_settings']}")
        print("="*50)
    
    @handle_errors()
    def run(self) -> bool:
        """Main execution method"""
        try:
            print(f"\n{self._colorize('🔐 Git SSH Configuration Assistant', 'bold')}")
            print("="*70)
            print(f"Platform: {platform.system()} {platform.release()}")
            print(f"Home Directory: {self.home_dir}")
            print(f"SSH Directory: {self.ssh_dir}")
            print(f"Auto Mode: {'Enabled' if self.auto_mode else 'Disabled'}")
            print("="*70 + "\n")
            
            # Step 1: Detect existing keys
            existing_keys = self.detect_existing_keys()
            
            # Step 2: Use existing key or generate new one
            if existing_keys:
                # Use the first valid key (prefer ed25519)
                ed25519_keys = [k for k in existing_keys if k['type'] == 'ed25519']
                key_to_use = ed25519_keys[0] if ed25519_keys else existing_keys[0]
                
                if not key_to_use['perms_correct']:
                    self._fix_key_permissions(key_to_use['private_path'], key_to_use['public_path'])
                
                key_info = {
                    'private_path': key_to_use['private_path'],
                    'public_path': key_to_use['public_path'],
                    'fingerprint': key_to_use['fingerprint'],
                    'type': key_to_use['type']
                }
                
                self._print_status(f"Using existing {key_to_use['type']} key", "info")
            else:
                # Generate new key
                key_type = 'ed25519'  # Default to ed25519
                if not self.auto_mode:
                    print("\nAvailable key types:")
                    for i, (ktype, config) in enumerate(self.key_types.items(), 1):
                        preferred = " (recommended)" if config['preferred'] else ""
                        print(f"{i}. {ktype}{preferred}")
                    
                    choice = input(f"Select key type (1-{len(self.key_types)}) or press Enter for ed25519: ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(self.key_types):
                        key_type = list(self.key_types.keys())[int(choice) - 1]
                
                key_info = self.generate_ssh_key(key_type)
            
            # Step 3: Add key to SSH agent
            self.add_key_to_agent(key_info['private_path'])
            
            # Step 4: GitHub integration
            github_token = self._get_github_token()
            if github_token:
                try:
                    self.upload_key_to_github(key_info['public_path'], github_token)
                except GitHubAPIError as e:
                    self._print_status(f"GitHub integration failed: {e.message}", "warning")
            else:
                self._print_status("Skipping GitHub key upload (no token provided)", "warning")
            
            # Step 5: Configure SSH config file
            self.configure_ssh_config(key_info['private_path'])
            
            # Step 6: Configure Git settings
            self.configure_git_settings()
            
            # Step 7: Verify connection
            self.verify_ssh_connection()
            
            # Step 8: Display summary
            summary = self.get_configuration_summary(key_info)
            self.display_summary(summary)
            
            self._print_status("SSH configuration completed successfully!", "success")
            self.logger.info("SSH configuration completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"SSH configuration failed: {e}")
            ExceptionHandler.handle(e)
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automated SSH configuration for Git workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python git_ssh_config.py                 # Interactive mode
  python git_ssh_config.py --auto          # Automatic mode with defaults
  python git_ssh_config.py --log custom.log # Custom log file
        """
    )
    
    parser.add_argument(
        '--auto', 
        action='store_true',
        help='Run in automatic mode (no prompts, use defaults)'
    )
    
    parser.add_argument(
        '--log',
        type=str,
        help='Custom log file path'
    )
    
    args = parser.parse_args()
    
    try:
        config = GitSSHConfig(auto_mode=args.auto, log_file=args.log)
        success = config.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()