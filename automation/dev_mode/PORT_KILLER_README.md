# Enhanced Port Killer Documentation

## Overview

The enhanced `port_killer.py` provides comprehensive port management and process termination capabilities for development environments. It forcefully terminates all active ports before starting any server to prevent port conflicts.

## Key Features

### 🔍 **Comprehensive Detection**
- **Common Dev Ports**: Monitors 20+ common development ports (React, Vue, Angular, Flask, Django, etc.)
- **All Server Processes**: Scans ALL active server processes, not just specific ports
- **Smart Process Recognition**: Identifies development-related processes safely
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 💀 **Reliable Termination**
- **Graceful + Force Kill**: Attempts SIGTERM first, then SIGKILL if needed
- **Safety Checks**: Only kills known development processes by default
- **Batch Operations**: Can clear all ports at once or target specific ones
- **Validation**: Verifies ports are actually free after termination

### 🛡️ **Safety Features**
- **Safe Process List**: Only kills known development tools (node, npm, python, etc.)
- **Force Mode**: Optional aggressive mode for stubborn processes
- **Error Handling**: Robust error handling with detailed reporting
- **Non-Destructive**: Won't kill system processes or unrecognized services

## API Reference

### Core Class: `PortKiller`

```python
from automation.dev_mode.port_killer import PortKiller

killer = PortKiller(verbose=True)
```

#### Methods

##### `kill_all_dev_ports(custom_ports=None)`
Kills processes on common development ports.
```python
result = killer.kill_all_dev_ports()
# Returns: {'killed_processes': [...], 'failed_kills': [...], 'total_killed': 5}
```

##### `kill_processes_on_port(port)`
Kills all processes on a specific port.
```python
success = killer.kill_processes_on_port(3000)
# Returns: True if successful, False otherwise
```

##### `scan_all_server_processes()`
Scans for ALL active server processes (new feature).
```python
servers = killer.scan_all_server_processes()
# Returns: [{'pid': 1234, 'port': 3000, 'name': 'node', 'protocol': 'TCP'}, ...]
```

##### `kill_all_server_processes(force=False)`
Kills ALL detected server processes (new feature).
```python
result = killer.kill_all_server_processes(force=False)
# force=True: Kill all detected processes
# force=False: Only kill processes in safe list
```

##### `validate_ports_free(ports)`
Validates that specific ports are free.
```python
all_free, occupied = killer.validate_ports_free([3000, 8080])
# Returns: (True, []) if all free, (False, [3000]) if 3000 occupied
```

### Convenience Functions

```python
from automation.dev_mode.port_killer import (
    kill_all_dev_ports,
    kill_port, 
    ensure_ports_free,
    scan_active_servers,
    force_clear_all_ports,
    get_port_conflicts
)

# Quick operations
kill_all_dev_ports()                    # Kill common dev ports
kill_port(3000)                         # Kill specific port
ensure_ports_free([3000, 8080])         # Ensure ports are free
scan_active_servers()                   # Scan all servers
force_clear_all_ports()                 # Nuclear option - kill everything
get_port_conflicts()                    # Get conflict info
```

## Command Line Usage

### Port Manager CLI

The new `port_manager.py` provides a standalone command-line interface:

```bash
# Scan for conflicts
python automation/dev_mode/port_manager.py scan
python automation/dev_mode/port_manager.py scan --all

# Kill processes
python automation/dev_mode/port_manager.py kill
python automation/dev_mode/port_manager.py kill --port 3000
python automation/dev_mode/port_manager.py kill --all

# Ensure ports are free
python automation/dev_mode/port_manager.py ensure 3000 8080 5173

# Check port status
python automation/dev_mode/port_manager.py check 3000 3001
```

## Integration

### Automatic Integration in Dev Workflow

The port killer is automatically integrated into the development workflow:

1. **Run Project Command**: Automatically clears ports before starting dev servers
2. **Smart Detection**: Scans for active servers first, then chooses appropriate clearing method
3. **Comprehensive Clearing**: Uses force clear if multiple servers detected
4. **Validation**: Verifies all ports are clear before starting new server

### Manual Integration

```python
from automation.dev_mode.port_killer import force_clear_all_ports

# Before starting your server
result = force_clear_all_ports(verbose=True)
if result['total_killed'] > 0:
    print(f"Cleared {result['total_killed']} port conflicts")

# Start your server here
```

## Monitored Ports

### Common Development Ports
- **3000-3005**: React, Next.js, Node.js
- **4200-4202**: Angular
- **5000-5002**: Flask, development servers  
- **5173-5175**: Vite
- **8000, 8001, 8080, 8081**: Django, general web servers
- **6006**: Storybook
- **7000, 7001, 7777**: Additional common ports
- **8888, 9000, 9001**: Jupyter, misc
- **9009, 9229**: Node.js debugging
- **19006**: Expo
- **4000, 4040**: Gatsby
- **24678**: Webpack dev server alternative

### Safe-to-Kill Processes
- **Node.js**: node, npm, yarn, pnpm, nodemon, ts-node
- **Bundlers**: webpack, vite, rollup, parcel
- **Servers**: serve, http-server, live-server, browser-sync
- **Python**: python, python3, flask, django, gunicorn, jupyter
- **Framework Tools**: next-server, react-scripts

## Error Handling

The port killer includes comprehensive error handling:

- **Process Not Found**: Gracefully handles processes that exit during scanning
- **Permission Denied**: Reports processes that cannot be killed due to permissions
- **Platform Differences**: Handles Windows vs Unix command differences
- **Network Scanning Failures**: Falls back to alternative detection methods
- **Encoding Issues**: Handles various text encoding problems

## Safety Considerations

### What Gets Killed
✅ **Safe to Kill**:
- Development servers (node, python dev servers)
- Build tools (webpack, vite, parcel)
- Package managers (npm, yarn, pnpm)
- Local development services

❌ **Never Killed**:
- System services
- Database servers (unless explicitly in dev mode)
- Production services
- Unknown/unrecognized processes (unless force=True)

### Force Mode Warning
⚠️ **Use with Caution**: `force=True` will attempt to kill ALL detected server processes, including those not in the safe list. Only use when you're certain about what processes are running.

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Run with elevated privileges if needed
   - Some system processes cannot be killed by user processes

2. **Process Still Running**
   - Some processes may restart automatically
   - Check for process managers (PM2, forever, etc.)
   - Use force mode for stubborn processes

3. **Port Still Occupied**
   - Process may take time to release port
   - Check for child processes
   - Restart terminal/IDE if needed

### Debug Mode

Add verbose output for troubleshooting:
```python
killer = PortKiller(verbose=True)
result = killer.kill_all_dev_ports()
```

## Performance

- **Fast Scanning**: Optimized port scanning using native OS commands
- **Parallel Operations**: Concurrent process detection where possible  
- **Minimal Overhead**: Lightweight operation suitable for frequent use
- **Smart Caching**: Avoids redundant scans within the same session

## Examples

### Basic Usage
```python
# Clear all common dev ports before starting server
from automation.dev_mode.port_killer import kill_all_dev_ports

result = kill_all_dev_ports(verbose=True)
print(f"Cleared {result['total_killed']} processes")
```

### Advanced Usage
```python
# Comprehensive port clearing with validation
from automation.dev_mode.port_killer import PortKiller

killer = PortKiller(verbose=True)

# Scan for any active servers
servers = killer.scan_all_server_processes()
if servers:
    print(f"Found {len(servers)} active servers")
    
    # Kill all server processes
    result = killer.kill_all_server_processes(force=False)
    print(f"Killed {result['total_killed']} processes")
    
    # Validate specific ports are free
    important_ports = [3000, 8080, 5173]
    all_free, occupied = killer.validate_ports_free(important_ports)
    
    if not all_free:
        print(f"Still occupied: {occupied}")
        # Force clear remaining
        killer.kill_all_server_processes(force=True)
```

### Integration with Dev Servers
```python
# Before starting your development server
from automation.dev_mode.port_killer import ensure_ports_free

# Ensure your specific ports are available
required_ports = [3000, 3001]  # main + HMR ports
success = ensure_ports_free(required_ports, verbose=True)

if success:
    print("✅ Ports ready - starting server...")
    # start_your_dev_server()
else:
    print("❌ Could not clear required ports")
```