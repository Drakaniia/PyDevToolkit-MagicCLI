"""
automation/dev_mode/port_killer.py
Port termination utility for Web Development operations
Detects and kills all processes using open ports before starting servers
"""
import subprocess
import sys
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from core.loading import LoadingSpinner


class PortKiller:
    """Utility class to detect and terminate processes using ports"""
    
    # Common development ports to monitor
    COMMON_DEV_PORTS = [
        3000, 3001, 3002, 3003, 3004, 3005,  # React, Next.js, Node.js
        4200, 4201, 4202,                      # Angular
        5000, 5001, 5002,                      # Flask, development servers
        5173, 5174, 5175,                      # Vite
        8000, 8001, 8080, 8081,               # Django, general web servers
        8888, 9000, 9001,                      # Jupyter, misc
        9009, 9229,                            # Node.js debugging
        19006,                                 # Expo
        4000, 4040,                            # Gatsby
        3333, 4444, 5555,                      # Custom dev servers
        7000, 7001, 7777,                      # Additional common ports
        6006,                                  # Storybook
        24678,                                 # Webpack dev server alternative
    ]
    
    # Process names that are definitely safe to kill (development-related)
    SAFE_TO_KILL_PROCESSES = [
        'node', 'npm', 'yarn', 'pnpm',
        'webpack', 'webpack-dev-server',
        'next-server', 'react-scripts',
        'vite', 'rollup', 'parcel',
        'serve', 'http-server',
        'live-server', 'browser-sync',
        'nodemon', 'ts-node',
        'python', 'python3', 'flask',
        'django', 'gunicorn',
        'jupyter', 'jupyter-notebook'
    ]
    
    def __init__(self, verbose: bool = True):
        """
        Initialize PortKiller
        
        Args:
            verbose: If True, show detailed output
        """
        self.verbose = verbose
        self.is_windows = sys.platform == 'win32'
    
    def kill_all_dev_ports(self, custom_ports: Optional[List[int]] = None) -> Dict[str, any]:
        """
        Kill all processes on common development ports
        
        Args:
            custom_ports: Additional ports to check beyond common ones
            
        Returns:
            Dict with results containing:
            - killed_processes: List of killed processes
            - failed_kills: List of processes that couldn't be killed
            - ports_checked: List of all ports that were checked
            - total_killed: Number of processes killed
        """
        ports_to_check = self.COMMON_DEV_PORTS.copy()
        
        if custom_ports:
            ports_to_check.extend(custom_ports)
        
        # Remove duplicates and sort
        ports_to_check = sorted(list(set(ports_to_check)))
        
        if self.verbose:
            print("\n🔍 SCANNING FOR ACTIVE PORTS")
            print("="*70)
            print(f"📋 Checking {len(ports_to_check)} development ports...")
        
        # Find all processes using ports
        active_processes = []
        with LoadingSpinner("Scanning ports"):
            for port in ports_to_check:
                processes = self._get_processes_on_port(port)
                active_processes.extend(processes)
        
        if not active_processes:
            if self.verbose:
                print("✅ No active processes found on development ports")
            return {
                'killed_processes': [],
                'failed_kills': [],
                'ports_checked': ports_to_check,
                'total_killed': 0
            }
        
        if self.verbose:
            print(f"\n⚠️  Found {len(active_processes)} active process(es):")
            print("-" * 50)
            for proc in active_processes:
                print(f"  Port {proc['port']:>5} | PID {proc['pid']:>6} | {proc['name']}")
        
        # Kill processes
        killed_processes = []
        failed_kills = []
        
        if self.verbose:
            print(f"\n💀 TERMINATING PROCESSES")
            print("="*70)
        
        for proc in active_processes:
            if self._kill_process(proc):
                killed_processes.append(proc)
                if self.verbose:
                    print(f"✅ Killed PID {proc['pid']} ({proc['name']}) on port {proc['port']}")
            else:
                failed_kills.append(proc)
                if self.verbose:
                    print(f"❌ Failed to kill PID {proc['pid']} ({proc['name']}) on port {proc['port']}")
        
        # Wait a moment for processes to fully terminate
        if killed_processes:
            if self.verbose:
                print("\n⏳ Waiting for processes to terminate...")
            time.sleep(2)
        
        if self.verbose:
            print(f"\n📊 SUMMARY")
            print("="*70)
            print(f"✅ Successfully killed: {len(killed_processes)} process(es)")
            if failed_kills:
                print(f"❌ Failed to kill: {len(failed_kills)} process(es)")
            print(f"🔍 Total ports checked: {len(ports_to_check)}")
        
        return {
            'killed_processes': killed_processes,
            'failed_kills': failed_kills,
            'ports_checked': ports_to_check,
            'total_killed': len(killed_processes)
        }
    
    def kill_processes_on_port(self, port: int) -> bool:
        """
        Kill all processes on a specific port
        
        Args:
            port: Port number to clear
            
        Returns:
            True if all processes were killed successfully, False otherwise
        """
        processes = self._get_processes_on_port(port)
        
        if not processes:
            if self.verbose:
                print(f"✅ Port {port} is already free")
            return True
        
        if self.verbose:
            print(f"\n🔍 Found {len(processes)} process(es) on port {port}:")
            for proc in processes:
                print(f"  PID {proc['pid']} | {proc['name']}")
        
        success = True
        for proc in processes:
            if not self._kill_process(proc):
                success = False
        
        # Verify port is now free
        time.sleep(1)
        remaining_processes = self._get_processes_on_port(port)
        if remaining_processes:
            if self.verbose:
                print(f"⚠️  Some processes still active on port {port}")
            success = False
        elif self.verbose:
            print(f"✅ Port {port} is now free")
        
        return success
    
    def get_port_usage(self, ports: Optional[List[int]] = None) -> Dict[int, List[Dict]]:
        """
        Get information about which processes are using specific ports
        
        Args:
            ports: List of ports to check. If None, checks common dev ports
            
        Returns:
            Dict mapping port numbers to list of process info dicts
        """
        if ports is None:
            ports = self.COMMON_DEV_PORTS
        
        port_usage = {}
        
        for port in ports:
            processes = self._get_processes_on_port(port)
            if processes:
                port_usage[port] = processes
        
        return port_usage
    
    def _get_processes_on_port(self, port: int) -> List[Dict[str, any]]:
        """
        Get all processes using a specific port
        
        Args:
            port: Port number to check
            
        Returns:
            List of process info dictionaries
        """
        processes = []
        
        try:
            if self.is_windows:
                processes = self._get_processes_windows(port)
            else:
                processes = self._get_processes_unix(port)
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error checking port {port}: {e}")
        
        return processes
    
    def _get_processes_windows(self, port: int) -> List[Dict[str, any]]:
        """Get processes on Windows using netstat"""
        processes = []
        
        try:
            # Use netstat to find processes
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse netstat output
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            pid = int(parts[-1])
                            
                            # Get process name using tasklist
                            name_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            
                            # Parse process name from CSV output
                            name_lines = name_result.stdout.split('\n')
                            if len(name_lines) > 1:
                                name_parts = name_lines[1].split(',')
                                if len(name_parts) > 0:
                                    process_name = name_parts[0].strip('"')
                                else:
                                    process_name = 'Unknown'
                            else:
                                process_name = 'Unknown'
                            
                            processes.append({
                                'pid': pid,
                                'port': port,
                                'name': process_name,
                                'protocol': 'TCP' if 'TCP' in line else 'UDP'
                            })
                        except (ValueError, subprocess.CalledProcessError):
                            continue
        
        except subprocess.CalledProcessError:
            pass
        
        return processes
    
    def _get_processes_unix(self, port: int) -> List[Dict[str, any]]:
        """Get processes on Unix/Linux/macOS using lsof or ss"""
        processes = []
        
        # Try lsof first (more detailed)
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-t'],
                capture_output=True,
                text=True,
                check=True
            )
            
            pids = [pid.strip() for pid in result.stdout.split('\n') if pid.strip()]
            
            for pid in pids:
                try:
                    # Get process name using ps
                    ps_result = subprocess.run(
                        ['ps', '-p', pid, '-o', 'comm='],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    process_name = ps_result.stdout.strip()
                    
                    processes.append({
                        'pid': int(pid),
                        'port': port,
                        'name': process_name,
                        'protocol': 'TCP'
                    })
                except (subprocess.CalledProcessError, ValueError):
                    continue
        
        except subprocess.CalledProcessError:
            # Fallback to ss if lsof is not available
            try:
                result = subprocess.run(
                    ['ss', '-tulpn', f'sport = :{port}'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse ss output
                lines = result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        # Extract PID from ss output (format: users:(("process",pid=1234,fd=5)))
                        pid_match = re.search(r'pid=(\d+)', line)
                        name_match = re.search(r'users:\(\("([^"]+)"', line)
                        
                        if pid_match:
                            pid = int(pid_match.group(1))
                            process_name = name_match.group(1) if name_match else 'Unknown'
                            
                            processes.append({
                                'pid': pid,
                                'port': port,
                                'name': process_name,
                                'protocol': 'TCP' if line.startswith('tcp') else 'UDP'
                            })
            
            except subprocess.CalledProcessError:
                pass
        
        return processes
    
    def _kill_process(self, process_info: Dict[str, any]) -> bool:
        """
        Kill a specific process
        
        Args:
            process_info: Process information dictionary
            
        Returns:
            True if process was killed successfully, False otherwise
        """
        pid = process_info['pid']
        
        try:
            if self.is_windows:
                # Windows: Use taskkill
                subprocess.run(
                    ['taskkill', '/F', '/PID', str(pid)],
                    capture_output=True,
                    check=True
                )
            else:
                # Unix: Use kill
                subprocess.run(
                    ['kill', '-TERM', str(pid)],
                    capture_output=True,
                    check=True
                )
                
                # If TERM doesn't work, try KILL after a moment
                time.sleep(1)
                try:
                    subprocess.run(
                        ['kill', '-0', str(pid)],
                        capture_output=True,
                        check=True
                    )
                    # Process still exists, force kill
                    subprocess.run(
                        ['kill', '-KILL', str(pid)],
                        capture_output=True,
                        check=True
                    )
                except subprocess.CalledProcessError:
                    # Process no longer exists (kill -0 failed), which is good
                    pass
            
            return True
        
        except subprocess.CalledProcessError:
            return False
    
    def validate_ports_free(self, ports: List[int]) -> Tuple[bool, List[int]]:
        """
        Validate that specific ports are free
        
        Args:
            ports: List of ports to validate
            
        Returns:
            Tuple of (all_free: bool, occupied_ports: List[int])
        """
        occupied_ports = []
        
        for port in ports:
            processes = self._get_processes_on_port(port)
            if processes:
                occupied_ports.append(port)
        
        return len(occupied_ports) == 0, occupied_ports
    
    def scan_all_server_processes(self) -> List[Dict[str, any]]:
        """
        Scan for ALL active server processes on any port
        
        Returns:
            List of all server process info dictionaries
        """
        server_processes = []
        
        try:
            if self.is_windows:
                server_processes = self._scan_all_servers_windows()
            else:
                server_processes = self._scan_all_servers_unix()
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error scanning for server processes: {e}")
        
        return server_processes
    
    def _scan_all_servers_windows(self) -> List[Dict[str, any]]:
        """Scan for all server processes on Windows"""
        processes = []
        
        try:
            # Get all network connections
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                check=True
            )
            
            seen_pids = set()
            
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line or 'ESTABLISHED' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            pid = int(parts[-1])
                            if pid in seen_pids:
                                continue
                            seen_pids.add(pid)
                            
                            # Get process info
                            name_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            
                            name_lines = name_result.stdout.split('\n')
                            if len(name_lines) > 1:
                                name_parts = name_lines[1].split(',')
                                if len(name_parts) > 0:
                                    process_name = name_parts[0].strip('"').lower()
                                    
                                    # Check if it's a development server process
                                    if any(safe_proc in process_name for safe_proc in self.SAFE_TO_KILL_PROCESSES):
                                        # Extract port from the connection
                                        local_addr = parts[1] if len(parts) > 1 else ''
                                        if ':' in local_addr:
                                            try:
                                                port = int(local_addr.split(':')[-1])
                                                processes.append({
                                                    'pid': pid,
                                                    'port': port,
                                                    'name': process_name,
                                                    'protocol': 'TCP' if 'TCP' in line else 'UDP'
                                                })
                                            except ValueError:
                                                continue
                        except (ValueError, subprocess.CalledProcessError):
                            continue
        
        except subprocess.CalledProcessError:
            pass
        
        return processes
    
    def _scan_all_servers_unix(self) -> List[Dict[str, any]]:
        """Scan for all server processes on Unix/Linux/macOS"""
        processes = []
        
        # Try lsof to get all listening processes
        try:
            result = subprocess.run(
                ['lsof', '-i', '-sTCP:LISTEN', '-n'],
                capture_output=True,
                text=True,
                check=True
            )
            
            seen_pids = set()
            
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 10:
                        try:
                            pid = int(parts[1])
                            if pid in seen_pids:
                                continue
                            seen_pids.add(pid)
                            
                            process_name = parts[0].lower()
                            
                            # Check if it's a development server process
                            if any(safe_proc in process_name for safe_proc in self.SAFE_TO_KILL_PROCESSES):
                                # Extract port
                                addr_info = parts[8]  # Format: *:port or addr:port
                                if ':' in addr_info:
                                    try:
                                        port = int(addr_info.split(':')[-1])
                                        processes.append({
                                            'pid': pid,
                                            'port': port,
                                            'name': process_name,
                                            'protocol': 'TCP'
                                        })
                                    except ValueError:
                                        continue
                        except (ValueError, IndexError):
                            continue
        
        except subprocess.CalledProcessError:
            # Fallback to ss if lsof is not available
            try:
                result = subprocess.run(
                    ['ss', '-tulpn'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                seen_pids = set()
                
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    if 'LISTEN' in line:
                        # Extract PID and process name from ss output
                        pid_match = re.search(r'pid=(\d+)', line)
                        name_match = re.search(r'users:\(\("([^"]+)"', line)
                        port_match = re.search(r':(\d+)\s', line)
                        
                        if pid_match and name_match and port_match:
                            try:
                                pid = int(pid_match.group(1))
                                if pid in seen_pids:
                                    continue
                                seen_pids.add(pid)
                                
                                process_name = name_match.group(1).lower()
                                port = int(port_match.group(1))
                                
                                # Check if it's a development server process
                                if any(safe_proc in process_name for safe_proc in self.SAFE_TO_KILL_PROCESSES):
                                    processes.append({
                                        'pid': pid,
                                        'port': port,
                                        'name': process_name,
                                        'protocol': 'TCP' if line.startswith('tcp') else 'UDP'
                                    })
                            except ValueError:
                                continue
            
            except subprocess.CalledProcessError:
                pass
        
        return processes
    
    def kill_all_server_processes(self, force: bool = False) -> Dict[str, any]:
        """
        Kill ALL detected server processes, not just those on common ports
        
        Args:
            force: If True, kill all detected processes. If False, only kill safe ones
            
        Returns:
            Dict with results
        """
        if self.verbose:
            print("\n🔍 SCANNING FOR ALL SERVER PROCESSES")
            print("="*70)
        
        # Get all server processes
        with LoadingSpinner("Scanning all server processes"):
            all_processes = self.scan_all_server_processes()
        
        if not all_processes:
            if self.verbose:
                print("✅ No active server processes found")
            return {
                'killed_processes': [],
                'failed_kills': [],
                'total_killed': 0
            }
        
        if self.verbose:
            print(f"\n⚠️  Found {len(all_processes)} server process(es):")
            print("-" * 50)
            for proc in all_processes:
                print(f"  Port {proc['port']:>5} | PID {proc['pid']:>6} | {proc['name']}")
        
        # Kill processes
        killed_processes = []
        failed_kills = []
        
        if self.verbose:
            print(f"\n💀 TERMINATING SERVER PROCESSES")
            print("="*70)
        
        for proc in all_processes:
            # Safety check: only kill if force=True or process is in safe list
            process_name = proc['name'].lower()
            is_safe = any(safe_proc in process_name for safe_proc in self.SAFE_TO_KILL_PROCESSES)
            
            if force or is_safe:
                if self._kill_process(proc):
                    killed_processes.append(proc)
                    if self.verbose:
                        print(f"✅ Killed PID {proc['pid']} ({proc['name']}) on port {proc['port']}")
                else:
                    failed_kills.append(proc)
                    if self.verbose:
                        print(f"❌ Failed to kill PID {proc['pid']} ({proc['name']}) on port {proc['port']}")
            else:
                if self.verbose:
                    print(f"⚠️  Skipped PID {proc['pid']} ({proc['name']}) - not in safe list")
                failed_kills.append(proc)
        
        # Wait for processes to terminate
        if killed_processes:
            if self.verbose:
                print("\n⏳ Waiting for processes to terminate...")
            time.sleep(2)
        
        if self.verbose:
            print(f"\n📊 SUMMARY")
            print("="*70)
            print(f"✅ Successfully killed: {len(killed_processes)} process(es)")
            if failed_kills:
                print(f"⚠️  Skipped/Failed: {len(failed_kills)} process(es)")
        
        return {
            'killed_processes': killed_processes,
            'failed_kills': failed_kills,
            'total_killed': len(killed_processes)
        }


# Convenience functions for easy integration

def kill_all_dev_ports(verbose: bool = True) -> Dict[str, any]:
    """
    Kill all processes on common development ports
    
    Args:
        verbose: If True, show detailed output
        
    Returns:
        Dict with results
    """
    killer = PortKiller(verbose=verbose)
    return killer.kill_all_dev_ports()


def kill_port(port: int, verbose: bool = True) -> bool:
    """
    Kill all processes on a specific port
    
    Args:
        port: Port number to clear
        verbose: If True, show detailed output
        
    Returns:
        True if successful, False otherwise
    """
    killer = PortKiller(verbose=verbose)
    return killer.kill_processes_on_port(port)


def ensure_ports_free(ports: List[int], verbose: bool = True) -> bool:
    """
    Ensure specific ports are free by killing any processes using them
    
    Args:
        ports: List of ports to ensure are free
        verbose: If True, show detailed output
        
    Returns:
        True if all ports are now free, False otherwise
    """
    killer = PortKiller(verbose=verbose)
    
    # Check which ports are occupied
    all_free, occupied_ports = killer.validate_ports_free(ports)
    
    if all_free:
        if verbose:
            print("✅ All specified ports are already free")
        return True
    
    if verbose:
        print(f"🔍 Found processes on {len(occupied_ports)} port(s): {occupied_ports}")
    
    # Kill processes on occupied ports
    success = True
    for port in occupied_ports:
        if not killer.kill_processes_on_port(port):
            success = False
    
    return success


def get_port_conflicts(ports: Optional[List[int]] = None) -> Dict[int, List[Dict]]:
    """
    Get information about port conflicts
    
    Args:
        ports: List of ports to check. If None, checks common dev ports
        
    Returns:
        Dict mapping port numbers to list of process info dicts
    """
    killer = PortKiller(verbose=False)
    return killer.get_port_usage(ports)


def kill_all_server_processes(force: bool = False, verbose: bool = True) -> Dict[str, any]:
    """
    Kill ALL detected server processes on any port
    
    Args:
        force: If True, kill all detected processes. If False, only kill safe ones
        verbose: If True, show detailed output
        
    Returns:
        Dict with results
    """
    killer = PortKiller(verbose=verbose)
    return killer.kill_all_server_processes(force=force)


def scan_active_servers(verbose: bool = False) -> List[Dict[str, any]]:
    """
    Scan for all active development server processes
    
    Args:
        verbose: If True, show detailed output
        
    Returns:
        List of server process info dictionaries
    """
    killer = PortKiller(verbose=verbose)
    return killer.scan_all_server_processes()


def force_clear_all_ports(verbose: bool = True) -> Dict[str, any]:
    """
    Nuclear option: Kill ALL development-related processes
    
    Args:
        verbose: If True, show detailed output
        
    Returns:
        Dict with results
    """
    if verbose:
        print("🚨 FORCE CLEARING ALL DEVELOPMENT PORTS")
        print("="*70)
        print("⚠️  This will terminate ALL detected development server processes")
        print("="*70)
    
    killer = PortKiller(verbose=verbose)
    
    # First try killing common dev ports
    common_result = killer.kill_all_dev_ports()
    
    # Then scan for any remaining server processes and kill them
    server_result = killer.kill_all_server_processes(force=False)
    
    total_killed = common_result['total_killed'] + server_result['total_killed']
    
    if verbose:
        print(f"\n🎯 FINAL SUMMARY")
        print("="*70)
        print(f"✅ Total processes killed: {total_killed}")
        print(f"📋 Common dev ports cleared: {common_result['total_killed']}")
        print(f"🔍 Additional servers cleared: {server_result['total_killed']}")
    
    return {
        'common_ports_result': common_result,
        'server_scan_result': server_result,
        'total_killed': total_killed,
        'all_killed_processes': common_result['killed_processes'] + server_result['killed_processes'],
        'all_failed_kills': common_result['failed_kills'] + server_result['failed_kills']
    }