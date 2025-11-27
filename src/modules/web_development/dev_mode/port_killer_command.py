"""
automation/dev_mode/port_killer_command.py
Port Killer command for the Dev Mode menu
Provides interactive port management and termination
"""
from typing import Any, List, Dict
from ._base import DevModeCommand
from .menu_utils import get_choice_with_arrows
from .port_killer import (
    PortKiller,
    kill_all_dev_ports,
    scan_active_servers,
    force_clear_all_ports,
    get_port_conflicts,
    ensure_ports_free
)


class PortKillerCommand(DevModeCommand):
    """Command for port management and process termination"""
    
    label = "Port Killer (Clear Conflicts)"
    description = "Detect and terminate processes using development ports"
    
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute port killer command"""
        if interactive:
            return self._interactive_run()
        else:
            return self._noninteractive_run(**kwargs)
    
    def _interactive_run(self):
        """Interactive port killer menu"""
        while True:
            print("\n" + "="*70)
            print(" PORT KILLER - Port Management & Process Termination")
            print("="*70)
            print(" Detect and terminate processes using development ports")
            print("="*70 + "\n")
            
            # Show current port status
            self._show_port_status()
            
            # Menu options
            options = [
                " Scan for Port Conflicts",
                " Scan All Server Processes", 
                " Kill Common Dev Ports",
                " Force Clear All Servers",
                " Kill Specific Port",
                " Ensure Ports Free",
                " Detailed Port Report",
                " Back to Dev Mode Menu"
            ]
            
            choice = get_choice_with_arrows(options, "Port Killer Options")
            
            if choice == 1:
                self._scan_conflicts()
            elif choice == 2:
                self._scan_all_servers()
            elif choice == 3:
                self._kill_common_ports()
            elif choice == 4:
                self._force_clear_all()
            elif choice == 5:
                self._kill_specific_port()
            elif choice == 6:
                self._ensure_ports_free()
            elif choice == 7:
                self._detailed_report()
            elif choice == 8:
                break
            else:
                print(" Invalid choice")
                input("\nPress Enter to continue...")
    
    def _noninteractive_run(self, action: str = 'scan', **kwargs):
        """Non-interactive port killer operations"""
        if action == 'scan':
            return scan_active_servers(verbose=kwargs.get('verbose', False))
        elif action == 'kill_common':
            return kill_all_dev_ports(verbose=kwargs.get('verbose', True))
        elif action == 'force_clear':
            return force_clear_all_ports(verbose=kwargs.get('verbose', True))
        elif action == 'kill_port':
            port = kwargs.get('port')
            if not port:
                raise ValueError("Port number required for kill_port action")
            killer = PortKiller(verbose=kwargs.get('verbose', True))
            return killer.kill_processes_on_port(port)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _show_port_status(self):
        """Show current port status summary"""
        print(" CURRENT PORT STATUS")
        print("-" * 30)
        
        try:
            # Quick scan for conflicts
            conflicts = get_port_conflicts()
            servers = scan_active_servers(verbose=False)
            
            if conflicts:
                print(f"  Conflicts on {len(conflicts)} common dev ports")
            else:
                print(" No conflicts on common dev ports")
            
            if servers:
                print(f" {len(servers)} active server processes detected")
            else:
                print(" No active server processes detected")
                
        except Exception as e:
            print(f"  Error checking status: {e}")
        
        print()
    
    def _scan_conflicts(self):
        """Scan for port conflicts on common dev ports"""
        print("\n SCANNING COMMON DEVELOPMENT PORTS")
        print("="*70)
        
        try:
            conflicts = get_port_conflicts()
            
            if conflicts:
                print(f"  Found conflicts on {len(conflicts)} port(s):")
                print("-" * 50)
                
                for port, processes in conflicts.items():
                    print(f"\n Port {port}:")
                    for proc in processes:
                        print(f"  PID {proc['pid']:>6} | {proc['name']:<20} | {proc['protocol']}")
            else:
                print(" No conflicts detected on common development ports")
                
        except Exception as e:
            print(f" Error scanning ports: {e}")
        
        input("\nPress Enter to continue...")
    
    def _scan_all_servers(self):
        """Scan for all active server processes"""
        print("\n SCANNING ALL ACTIVE SERVER PROCESSES")
        print("="*70)
        
        try:
            servers = scan_active_servers(verbose=True)
            
            if servers:
                print(f"\n Found {len(servers)} active server process(es):")
                print("-" * 50)
                
                for server in servers:
                    print(f"Port {server['port']:>5} | PID {server['pid']:>6} | {server['name']:<20} | {server['protocol']}")
            else:
                print(" No active server processes detected")
                
        except Exception as e:
            print(f" Error scanning servers: {e}")
        
        input("\nPress Enter to continue...")
    
    def _kill_common_ports(self):
        """Kill processes on common development ports"""
        print("\n KILLING PROCESSES ON COMMON DEV PORTS")
        print("="*70)
        print("  This will terminate processes on common development ports")
        
        confirm = input("\nContinue? (y/N): ").lower().strip()
        if confirm != 'y':
            print(" Operation cancelled")
            input("\nPress Enter to continue...")
            return
        
        try:
            result = kill_all_dev_ports(verbose=True)
            
            print(f"\n RESULTS:")
            print(f" Processes killed: {result['total_killed']}")
            if result['failed_kills']:
                print(f" Failed to kill: {len(result['failed_kills'])}")
                
        except Exception as e:
            print(f" Error during kill operation: {e}")
        
        input("\nPress Enter to continue...")
    
    def _force_clear_all(self):
        """Force clear all server processes"""
        print("\n FORCE CLEARING ALL SERVER PROCESSES")
        print("="*70)
        print("  This will terminate ALL detected development server processes")
        print(" This is the nuclear option - use with caution!")
        
        confirm = input("\nAre you sure you want to continue? (y/N): ").lower().strip()
        if confirm != 'y':
            print(" Operation cancelled")
            input("\nPress Enter to continue...")
            return
        
        try:
            result = force_clear_all_ports(verbose=True)
            
            print(f"\n FINAL RESULTS:")
            print(f" Total processes killed: {result['total_killed']}")
            print(f" Common ports cleared: {result['common_ports_result']['total_killed']}")
            print(f" Additional servers cleared: {result['server_scan_result']['total_killed']}")
            
        except Exception as e:
            print(f" Error during force clear: {e}")
        
        input("\nPress Enter to continue...")
    
    def _kill_specific_port(self):
        """Kill processes on a specific port"""
        print("\n KILL PROCESSES ON SPECIFIC PORT")
        print("="*70)
        
        try:
            port_input = input("Enter port number (e.g., 3000): ").strip()
            port = int(port_input)
            
            if port < 1 or port > 65535:
                print(" Invalid port number (must be 1-65535)")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n Killing processes on port {port}...")
            
            killer = PortKiller(verbose=True)
            success = killer.kill_processes_on_port(port)
            
            if success:
                print(f" Port {port} is now free")
            else:
                print(f"  Some processes on port {port} could not be killed")
                
        except ValueError:
            print(" Invalid port number")
        except Exception as e:
            print(f" Error killing port processes: {e}")
        
        input("\nPress Enter to continue...")
    
    def _ensure_ports_free(self):
        """Ensure specific ports are free"""
        print("\n ENSURE SPECIFIC PORTS ARE FREE")
        print("="*70)
        
        try:
            ports_input = input("Enter port numbers (comma-separated, e.g., 3000,8080,5173): ").strip()
            
            if not ports_input:
                print(" No ports specified")
                input("\nPress Enter to continue...")
                return
            
            # Parse ports
            ports = []
            for port_str in ports_input.split(','):
                try:
                    port = int(port_str.strip())
                    if 1 <= port <= 65535:
                        ports.append(port)
                    else:
                        print(f"  Skipping invalid port: {port}")
                except ValueError:
                    print(f"  Skipping invalid port: {port_str.strip()}")
            
            if not ports:
                print(" No valid ports specified")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n Ensuring ports are free: {ports}")
            
            success = ensure_ports_free(ports, verbose=True)
            
            if success:
                print(" All specified ports are now free")
            else:
                print("  Some ports could not be cleared")
                
        except Exception as e:
            print(f" Error ensuring ports free: {e}")
        
        input("\nPress Enter to continue...")
    
    def _detailed_report(self):
        """Show detailed port and process report"""
        print("\n DETAILED PORT & PROCESS REPORT")
        print("="*70)
        
        try:
            killer = PortKiller(verbose=False)
            
            # Common dev ports
            print(" COMMON DEVELOPMENT PORTS:")
            print("-" * 40)
            conflicts = get_port_conflicts()
            
            if conflicts:
                for port, processes in conflicts.items():
                    print(f"Port {port:>5}: {len(processes)} process(es)")
                    for proc in processes:
                        print(f"         PID {proc['pid']:>6} | {proc['name']}")
            else:
                print("   All common dev ports are free")
            
            # All server processes
            print(f"\n ALL SERVER PROCESSES:")
            print("-" * 40)
            servers = scan_active_servers(verbose=False)
            
            if servers:
                for server in servers:
                    print(f"Port {server['port']:>5} | PID {server['pid']:>6} | {server['name']:<20} | {server['protocol']}")
            else:
                print("   No active server processes detected")
            
            # Safe vs unsafe processes
            print(f"\n PROCESS SAFETY ANALYSIS:")
            print("-" * 40)
            safe_count = 0
            unsafe_count = 0
            
            for server in servers:
                is_safe = any(safe_proc in server['name'].lower() 
                             for safe_proc in killer.SAFE_TO_KILL_PROCESSES)
                if is_safe:
                    safe_count += 1
                else:
                    unsafe_count += 1
            
            print(f"   Safe to kill: {safe_count} process(es)")
            print(f"    Not in safe list: {unsafe_count} process(es)")
            
        except Exception as e:
            print(f" Error generating report: {e}")
        
        input("\nPress Enter to continue...")


# Export command instance
COMMAND = PortKillerCommand()