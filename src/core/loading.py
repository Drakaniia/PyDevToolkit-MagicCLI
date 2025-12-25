"""
automation/core/loading.py
Comprehensive loading animation utilities for automation tools
"""

import sys
import time
import threading
from typing import Callable, Any
from contextlib import contextmanager


class LoadingSpinner:
    """Enhanced loading spinner with multiple animation types"""

    # Different spinner styles
    SPINNER_STYLES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "classic": ["|", "/", "-", "\\"],
        "arrows": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "bouncing": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
        "pulse": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "blocks": ["⣀", "⣄", "⣤", "⣦", "⣶", "⣷", "⣿", "⡿", "⢿", "⣻", "⣽", "⣾"],
        "clock": [
            "🕐",
            "🕑",
            "🕒",
            "🕓",
            "🕔",
            "🕕",
            "🕖",
            "🕗",
            "🕘",
            "🕙",
            "🕚",
            "🕛",
        ],
        "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    }

    def __init__(
        self, message: str = "Loading", style: str = "dots", speed: float = 0.1
    ):
        """
        Initialize loading spinner

        Args:
            message: Message to display
            style: Spinner style ('dots', 'classic', 'arrows', etc.)
            speed: Animation speed in seconds
        """
        self.message = message
        self.style = style
        self.speed = speed
        self.frames = self.SPINNER_STYLES.get(style, self.SPINNER_STYLES["dots"])
        self.index = 0
        self.active = False
        self.thread = None
        self._lock = threading.Lock()

    def start(self):
        """Start the spinner animation"""
        with self._lock:
            if self.active:
                return
            self.active = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the spinner animation"""
        with self._lock:
            if not self.active:
                return
            self.active = False
            if self.thread:
                self.thread.join(timeout=0.1)

    def _animate(self):
        """Animation loop"""
        while self.active:
            with self._lock:
                if not self.active:
                    break
                frame = self.frames[self.index]
                self.index = (self.index + 1) % len(self.frames)

            # Write the frame
            sys.stdout.write(f"\r{frame} {self.message}")
            sys.stdout.flush()
            time.sleep(self.speed)

        # Clear the line when stopped
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class ProgressBar:
    """Progress bar with customizable appearance"""

    def __init__(self, total: int, width: int = 50, message: str = "Progress"):
        """
        Initialize progress bar

        Args:
            total: Total number of items
            width: Width of the progress bar
            message: Message to display
        """
        self.total = total
        self.width = width
        self.message = message
        self.current = 0
        self.start_time = time.time()

    def update(self, increment: int = 1):
        """Update progress by increment"""
        self.current += increment
        self._render()

    def set_progress(self, value: int):
        """Set progress to specific value"""
        self.current = min(value, self.total)
        self._render()

    def _render(self):
        """Render the progress bar"""
        if self.total == 0:
            return

        percentage = self.current / self.total
        filled_width = int(self.width * percentage)
        bar = "█" * filled_width + "░" * (self.width - filled_width)

        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"

        sys.stdout.write(
            f"\r{self.message}: |{bar}| {percentage:.1%} "
            f"({self.current}/{self.total}) {eta_str}"
        )
        sys.stdout.flush()

    def finish(self):
        """Finish the progress bar"""
        self.current = self.total
        self._render()
        sys.stdout.write("\n")
        sys.stdout.flush()


@contextmanager
def loading_context(message: str = "Loading", style: str = "dots"):
    """Context manager for loading animations"""
    spinner = LoadingSpinner(message, style)
    try:
        spinner.start()
        yield spinner
    finally:
        spinner.stop()


def timed_operation(func: Callable, *args, **kwargs) -> Any:
    """
    Execute a function with timing and optional progress display

    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Result of the function execution
    """
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"✓ Operation completed in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Operation failed after {elapsed:.2f}s: {e}")
        raise


class LoadingManager:
    """Manager for multiple loading operations"""

    def __init__(self):
        self.active_spinners = {}
        self.progress_bars = {}

    def start_spinner(self, name: str, message: str, style: str = "dots"):
        """Start a named spinner"""
        spinner = LoadingSpinner(message, style)
        spinner.start()
        self.active_spinners[name] = spinner
        return spinner

    def stop_spinner(self, name: str):
        """Stop a named spinner"""
        if name in self.active_spinners:
            self.active_spinners[name].stop()
            del self.active_spinners[name]

    def create_progress_bar(self, name: str, total: int, message: str = "Progress"):
        """Create a named progress bar"""
        progress_bar = ProgressBar(total, message=message)
        self.progress_bars[name] = progress_bar
        return progress_bar

    def finish_progress_bar(self, name: str):
        """Finish a named progress bar"""
        if name in self.progress_bars:
            self.progress_bars[name].finish()
            del self.progress_bars[name]

    def stop_all(self):
        """Stop all active operations"""
        for spinner in self.active_spinners.values():
            spinner.stop()
        for progress_bar in self.progress_bars.values():
            progress_bar.finish()
        self.active_spinners.clear()
        self.progress_bars.clear()


# Global loading manager instance
loading_manager = LoadingManager()


# Convenience functions
def start_loading(message: str, style: str = "dots") -> LoadingSpinner:
    """Start a loading spinner with the given message"""
    spinner = LoadingSpinner(message, style)
    spinner.start()
    return spinner


def show_progress(total: int, message: str = "Progress") -> ProgressBar:
    """Show a progress bar for the given total"""
    return ProgressBar(total, message=message)


def load_with_progress(
    items: list, processor: Callable, message: str = "Processing"
) -> list:
    """
    Process a list of items with progress display

    Args:
        items: List of items to process
        processor: Function to process each item
        message: Progress message

    Returns:
        List of processed items
    """
    progress = show_progress(len(items), message)
    results = []

    for item in items:
        try:
            result = processor(item)
            results.append(result)
        except Exception as e:
            print(f"Error processing item: {e}")
        progress.update()

    progress.finish()
    return results


if __name__ == "__main__":
    # Example usage
    print("Testing LoadingSpinner...")
    with LoadingSpinner("Testing spinner", "dots"):
        time.sleep(2)

    print("\nTesting ProgressBar...")
    progress = ProgressBar(100, message="Test progress")
    for i in range(101):
        progress.set_progress(i)
        time.sleep(0.02)

    print("\nTesting LoadingManager...")
    manager = LoadingManager()
    spinner = manager.start_spinner("test", "Manager test")
    time.sleep(1)
    manager.stop_spinner("test")

    print("\nAll tests completed!")
