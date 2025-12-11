"""
Monitoring Module
Handles performance profiling, memory usage analysis, and runtime metrics
"""
import sys
import subprocess
import os
import time
from pathlib import Path
from typing import List, Optional
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator

# Import psutil only if available
try:
    import psutil
except ImportError:
    psutil = None


class MonitoringTools:
    """Handles monitoring and performance analysis tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def show_system_resources(self) -> None:
        """Show current system resource usage"""
        print("\n" + "="*70)
        print("SYSTEM RESOURCE USAGE")
        print("="*70)

        if psutil is None:
            print("\n⚠ psutil is not installed. Install with: pip install psutil")
            input("\nPress Enter to continue...")
            return

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # Convert to GB
            memory_total = memory.total / (1024**3)  # Convert to GB

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free = disk.free / (1024**3)  # Convert to GB
            disk_total = disk.total / (1024**3)  # Convert to GB

            # Network I/O
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent / (1024**2)  # Convert to MB
            bytes_recv = net_io.bytes_recv / (1024**2)  # Convert to MB

            print(f"\nCPU Usage: {cpu_percent}% (Physical cores: {cpu_count})")
            print(f"Memory: {memory_percent}% used ({memory_available:.2f}GB free of {memory_total:.2f}GB)")
            print(f"Disk: {disk_percent:.1f}% used ({disk_free:.2f}GB free of {disk_total:.2f}GB)")
            print(f"Network: Sent {bytes_sent:.2f}MB, Received {bytes_recv:.2f}MB")

        except Exception as e:
            print(f"\n⚠ Error getting system resources: {e}")

        input("\nPress Enter to continue...")

    def monitor_process(self) -> None:
        """Monitor a specific process"""
        print("\n" + "="*70)
        print("PROCESS MONITOR")
        print("="*70)

        if psutil is None:
            print("\n⚠ psutil is not installed. Install with: pip install psutil")
            input("\nPress Enter to continue...")
            return

        try:
            # Get Magic CLI's own process info
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)

            print(f"\nMonitoring Magic CLI Process (PID: {current_pid}):")
            print(f"  Name: {current_process.name()}")
            print(f"  Status: {current_process.status()}")
            print(f"  CPU %: {current_process.cpu_percent()}")
            print(f"  Memory %: {current_process.memory_percent():.2f}")
            print(f"  Memory RSS: {current_process.memory_info().rss / (1024**2):.2f} MB")
            print(f"  Started: {time.ctime(current_process.create_time())}")

            # List child processes
            children = current_process.children(recursive=True)
            if children:
                print(f"\nChild processes:")
                for child in children:
                    try:
                        print(f"  PID {child.pid}: {child.name()}")
                    except psutil.NoSuchProcess:
                        print(f"  PID {child.pid}: (terminated)")
            else:
                print("\nNo child processes")

        except Exception as e:
            print(f"\n⚠ Error monitoring process: {e}")

        input("\nPress Enter to continue...")

    def profile_performance(self) -> None:
        """Run performance profiling on the application"""
        print("\n" + "="*70)
        print("PERFORMANCE PROFILING")
        print("="*70)
        
        print("\nThis feature will profile your application's performance.")
        print("It measures execution time and resource usage of code.")
        
        try:
            # Check if cProfile is available
            import cProfile
            
            # We'll create a simple profile of the current module
            print("\nProfiling Python interpreter (as a demonstration)...")
            
            # This is a demonstration - in a real scenario, 
            # we would profile actual application code
            profiler = cProfile.Profile()
            profiler.enable()
            
            # Simulate some work (replace with actual profiling in real usage)
            for i in range(10000):
                _ = i * i
            
            profiler.disable()
            
            print("\nProfiling completed! (Demo only)")
            print("Note: In production, this would profile actual application functions.")
            
            # Save profile to file
            profile_file = "profile_output.prof"
            profiler.dump_stats(profile_file)
            print(f"Profile data saved to: {profile_file}")
            print(f"Use 'python -m pstats {profile_file}' to analyze the results")
        
        except ImportError:
            print("\n⚠ cProfile module not available")
        except Exception as e:
            print(f"\n⚠ Error during profiling: {e}")
        
        input("\nPress Enter to continue...")

    def analyze_memory_usage(self) -> None:
        """Analyze memory usage - requires memory-profiler package"""
        print("\n" + "="*70)
        print("MEMORY USAGE ANALYSIS")
        print("="*70)

        print("This feature analyzes memory usage line by line.")
        print("It requires the memory-profiler package.")

        try:
            # Check if memory-profiler is available
            import memory_profiler
            print("\nMemory profiler is available.")
            print("To use it, run: python -m memory_profiler your_script.py")
            print("Or use @profile decorator on functions you want to analyze")
        except ImportError:
            print("\n⚠ Memory profiler not available.")
            print("Install with: pip install memory-profiler")
            print("Then you can run: python -m memory_profiler your_script.py")

        # Show current memory usage by the application if psutil is available
        if psutil is not None:
            try:
                current_pid = os.getpid()
                current_process = psutil.Process(current_pid)

                print(f"\nCurrent Magic CLI memory usage:")
                print(f"  RSS (Resident Set Size): {current_process.memory_info().rss / (1024**2):.2f} MB")
                print(f"  VMS (Virtual Memory Size): {current_process.memory_info().vms / (1024**2):.2f} MB")
                print(f"  Percentage of total system memory: {current_process.memory_percent():.2f}%")
            except Exception as e:
                print(f"\n⚠ Error getting memory info: {e}")
        else:
            print("\n⚠ psutil not available for memory monitoring. Install with: pip install psutil")

        input("\nPress Enter to continue...")

    def run_performance_benchmark(self) -> None:
        """Run a simple performance benchmark"""
        print("\n" + "="*70)
        print("PERFORMANCE BENCHMARK")
        print("="*70)

        try:
            import time

            print("\nRunning performance benchmark...")
            print("(Press Ctrl+C to cancel anytime)")

            # CPU benchmark: Calculate sum of squares
            start_time = time.time()
            sum_of_squares = sum(i*i for i in range(1000000))
            cpu_time = time.time() - start_time

            # Memory benchmark: Create and delete large list
            start_time = time.time()
            large_list = [i for i in range(1000000)]
            memory_creation_time = time.time() - start_time

            start_time = time.time()
            del large_list
            memory_cleanup_time = time.time() - start_time

            print(f"\nBenchmark Results:")
            print(f"  CPU: Calculated sum of squares for 1,000,000 numbers in {cpu_time:.4f}s")
            print(f"  Memory: Created 1M element list in {memory_creation_time:.4f}s")
            print(f"  Memory: Cleaned up in {memory_cleanup_time:.4f}s")
            print(f"  Total benchmark time: {cpu_time + memory_creation_time + memory_cleanup_time:.4f}s")

        except KeyboardInterrupt:
            print("\n\nBenchmark cancelled by user.")
        except Exception as e:
            print(f"\n⚠ Error during benchmark: {e}")

        input("\nPress Enter to continue...")

    def monitor_application_logs(self) -> None:
        """Monitor application logs"""
        print("\n" + "="*70)
        print("APPLICATION LOG MONITOR")
        print("="*70)
        
        print("\nThis feature would monitor application logs in real-time.")
        print("Currently, Magic CLI uses basic print statements for output.")
        print("\nSuggested log files to monitor:")
        
        # Look for common log files in the project
        log_extensions = ['.log', '.txt', '.out']
        project_files = Path('.').glob('**/*')
        log_files = [f for f in project_files if f.suffix.lower() in log_extensions]
        
        if log_files:
            print("\nFound potential log files:")
            for log_file in log_files[:10]:  # Show first 10
                print(f"  - {log_file}")
            if len(log_files) > 10:
                print(f"  ... and {len(log_files) - 10} more")
        else:
            print("\n  No log files found in current project")
        
        print("\nTo implement full log monitoring, you would need to:")
        print("  1. Set up a proper logging system")
        print("  2. Write logs to specific files")
        print("  3. Monitor those files in real-time")
        
        input("\nPress Enter to continue...")


class MonitoringMenu(Menu):
    """Menu for monitoring tools"""

    def __init__(self):
        self.monitoring = MonitoringTools()
        super().__init__("Monitoring & Performance Tools")

    def setup_items(self) -> None:
        """Setup menu items for monitoring tools"""
        self.items = [
            MenuItem("Show System Resources", self.monitoring.show_system_resources),
            MenuItem("Monitor Current Process", self.monitoring.monitor_process),
            MenuItem("Run Performance Profiling", self.monitoring.profile_performance),
            MenuItem("Analyze Memory Usage", self.monitoring.analyze_memory_usage),
            MenuItem("Run Performance Benchmark", self.monitoring.run_performance_benchmark),
            MenuItem("Monitor Application Logs", self.monitoring.monitor_application_logs),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]