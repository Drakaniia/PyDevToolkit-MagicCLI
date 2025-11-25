#!/usr/bin/env python3
"""
automation/dev_mode/port_manager.py
Standalone command-line utility for port management
Provides easy access to all port killer functionality
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional

from .port_killer import (
    PortKiller,
    kill_all_dev_ports,
    kill_port,
    scan_active_servers,
    force_clear_all_ports,
    get_port_conflicts,
    ensure_ports_free
)


def cmd_scan(args):
    """Scan for active server processes"""
    print("🔍 SCANNING FOR ACTIVE SERVER PROCESSES")
    print("="*70)
    
    if args.all:
        # Scan all server processes
        servers = scan_active_servers(verbose=True)
        if servers:
            print(f"\n📊 Found {len(servers)} active server process(es)")
        else:
            print("✅ No active server processes found")
    else:
        # Scan common dev ports only
        conflicts = get_port_conflicts()
        if conflicts:
            print(f"⚠️  Found processes on {len(conflicts)} port(s):")
            for port, processes in conflicts.items():
                print(f"\n🔹 Port {port}:")
                for proc in processes:
                    print(f"  PID {proc['pid']} | {proc['name']} | {proc['protocol']}")
        else:
            print("✅ No conflicts detected on common development ports")


def cmd_kill(args):
    """Kill processes on specified ports or all dev ports"""
    if args.port:
        # Kill specific port
        print(f"💀 KILLING PROCESSES ON PORT {args.port}")
        print("="*70)
        success = kill_port(args.port, verbose=True)
        if success:
            print(f"✅ Port {args.port} is now free")
        else:
            print(f"❌ Failed to clear port {args.port}")
    elif args.all:
        # Kill all server processes
        print("💀 FORCE CLEARING ALL SERVER PROCESSES")
        print("="*70)
        result = force_clear_all_ports(verbose=True)
        print(f"\n✅ Killed {result['total_killed']} processes")
    else:
        # Kill common dev ports
        print("💀 CLEARING COMMON DEVELOPMENT PORTS")
        print("="*70)
        result = kill_all_dev_ports(verbose=True)
        print(f"\n✅ Killed {result['total_killed']} processes")


def cmd_ensure(args):
    """Ensure specific ports are free"""
    ports = args.ports
    print(f"🎯 ENSURING PORTS ARE FREE: {ports}")
    print("="*70)
    
    success = ensure_ports_free(ports, verbose=True)
    if success:
        print(f"✅ All specified ports are now free")
    else:
        print(f"❌ Some ports could not be cleared")


def cmd_check(args):
    """Check if specific ports are free"""
    ports = args.ports
    print(f"🔍 CHECKING PORT STATUS: {ports}")
    print("="*70)
    
    killer = PortKiller(verbose=False)
    all_free, occupied = killer.validate_ports_free(ports)
    
    if all_free:
        print("✅ All specified ports are free")
    else:
        print(f"⚠️  Occupied ports: {occupied}")
        
        # Show details for occupied ports
        for port in occupied:
            processes = killer._get_processes_on_port(port)
            print(f"\n🔹 Port {port}:")
            for proc in processes:
                print(f"  PID {proc['pid']} | {proc['name']} | {proc['protocol']}")


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Port Manager - Development server port management utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan                    # Scan common dev ports for conflicts
  %(prog)s scan --all              # Scan all active server processes
  %(prog)s kill                    # Kill processes on common dev ports
  %(prog)s kill --all              # Kill all detected server processes
  %(prog)s kill --port 3000        # Kill processes on port 3000
  %(prog)s ensure 3000 8080        # Ensure ports 3000 and 8080 are free
  %(prog)s check 3000 3001 5173    # Check if ports are free
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for active processes')
    scan_parser.add_argument('--all', action='store_true', 
                           help='Scan all server processes, not just common dev ports')
    scan_parser.set_defaults(func=cmd_scan)
    
    # Kill command
    kill_parser = subparsers.add_parser('kill', help='Kill processes')
    kill_group = kill_parser.add_mutually_exclusive_group()
    kill_group.add_argument('--port', type=int, 
                          help='Kill processes on specific port')
    kill_group.add_argument('--all', action='store_true',
                          help='Kill all detected server processes')
    kill_parser.set_defaults(func=cmd_kill)
    
    # Ensure command
    ensure_parser = subparsers.add_parser('ensure', help='Ensure ports are free')
    ensure_parser.add_argument('ports', type=int, nargs='+',
                              help='Port numbers to ensure are free')
    ensure_parser.set_defaults(func=cmd_ensure)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check port status')
    check_parser.add_argument('ports', type=int, nargs='+',
                             help='Port numbers to check')
    check_parser.set_defaults(func=cmd_check)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()