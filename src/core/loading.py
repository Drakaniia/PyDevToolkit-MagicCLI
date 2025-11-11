"""
automation/core/loading.py
Comprehensive loading animation utilities for automation tools
"""
import sys
import time
import threading
from typing import Optional, List, Callable, Any
from contextlib import contextmanager


class LoadingSpinner:
    """Enhanced loading spinner with multiple animation types"""
    
    # Different spinner styles
    SPINNER_STYLES = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'classic': ['|', '/', '-', '\\'],
        'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'bouncing': ['⠁', '⠂', '⠄', '⠂'],
        'pulse': ['●', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗'],
        'blocks': ['▁', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃'],
        'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
        'moon': ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
    }
    
    def __init__(self, message: str = "Loading", style: str = 'dots', speed: float = 0.1):
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
        self.frames = self.SPINNER_STYLES.get(style, self.SPINNER_STYLES['dots'])
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
    
    def stop(self, success: bool = True, final_message: Optional[str] = None):
        """
        Stop the spinner and show final status
        
        Args:
            success: Whether operation was successful
            final_message: Custom final message to display
        """
        with self._lock:
            if not self.active:
                return
            self.active = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Clear current line and show final status
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
        
        icon = "✅" if success else "❌"
        message = final_message or self.message
        print(f"{icon} {message}")
    
    def update_message(self, new_message: str):
        """Update the spinner message while running"""
        with self._lock:
            self.message = new_message
    
    def _animate(self):
        """Internal animation loop"""
        while self.active:
            with self._lock:
                if not self.active:
                    break
                frame = self.frames[self.index % len(self.frames)]
                sys.stdout.write(f'\r{frame} {self.message}...')
                sys.stdout.flush()
                self.index += 1
            
            time.sleep(self.speed)
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        success = exc_type is None
        self.stop(success=success)
        return False


class ProgressBar:
    """Simple progress bar for operations with known total"""
    
    def __init__(self, total: int, width: int = 50, message: str = "Progress"):
        """
        Initialize progress bar
        
        Args:
            total: Total number of items
            width: Width of progress bar in characters
            message: Message to display
        """
        self.total = total
        self.width = width
        self.message = message
        self.current = 0
    
    def update(self, increment: int = 1, message: Optional[str] = None):
        """
        Update progress bar
        
        Args:
            increment: Number to add to current progress
            message: Optional message update
        """
        self.current = min(self.current + increment, self.total)
        
        if message:
            self.message = message
        
        # Calculate progress
        percentage = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * percentage)
        
        # Create progress bar
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        percent_text = f"{percentage:.1%}"
        
        # Display progress
        sys.stdout.write(f'\r{self.message}: |{bar}| {percent_text} ({self.current}/{self.total})')
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line when complete
    
    def complete(self, message: Optional[str] = None):
        """Mark progress as complete"""
        self.current = self.total
        self.update(0, message or f"{self.message} Complete")


class LoadingDots:
    """Simple loading dots animation"""
    
    def __init__(self, message: str = "Loading", max_dots: int = 3, speed: float = 0.5):
        """
        Initialize loading dots
        
        Args:
            message: Base message
            max_dots: Maximum number of dots
            speed: Speed of animation
        """
        self.message = message
        self.max_dots = max_dots
        self.speed = speed
        self.dots = 0
        self.active = False
        self.thread = None
        self._lock = threading.Lock()
    
    def start(self):
        """Start dots animation"""
        with self._lock:
            if self.active:
                return
            self.active = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self, success: bool = True, final_message: Optional[str] = None):
        """Stop animation and show final status"""
        with self._lock:
            if not self.active:
                return
            self.active = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Clear line and show final status
        sys.stdout.write('\r' + ' ' * (len(self.message) + self.max_dots + 5) + '\r')
        sys.stdout.flush()
        
        icon = "✅" if success else "❌"
        message = final_message or self.message
        print(f"{icon} {message}")
    
    def _animate(self):
        """Internal animation loop"""
        while self.active:
            with self._lock:
                if not self.active:
                    break
                dots_str = '.' * self.dots
                sys.stdout.write(f'\r{self.message}{dots_str}')
                sys.stdout.flush()
                self.dots = (self.dots + 1) % (self.max_dots + 1)
            
            time.sleep(self.speed)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        self.stop(success=success)
        return False


@contextmanager
def loading_animation(message: str = "Loading", style: str = 'dots', speed: float = 0.1):
    """
    Context manager for easy loading animation
    
    Args:
        message: Message to display
        style: Animation style
        speed: Animation speed
    
    Usage:
        with loading_animation("Installing packages"):
            # Long running operation
            time.sleep(5)
    """
    spinner = LoadingSpinner(message, style, speed)
    try:
        spinner.start()
        yield spinner
    except Exception as e:
        spinner.stop(success=False, final_message=f"{message} failed: {str(e)}")
        raise
    else:
        spinner.stop(success=True, final_message=f"{message} completed")


def run_with_loading(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    message: str = "Processing",
    style: str = 'dots',
    success_message: Optional[str] = None,
    error_message: Optional[str] = None
) -> Any:
    """
    Run a function with loading animation
    
    Args:
        func: Function to run
        args: Function arguments
        kwargs: Function keyword arguments
        message: Loading message
        style: Animation style
        success_message: Message on success
        error_message: Message on error
    
    Returns:
        Function result
    """
    kwargs = kwargs or {}
    
    with LoadingSpinner(message, style) as spinner:
        try:
            result = func(*args, **kwargs)
            spinner.stop(success=True, final_message=success_message or f"{message} completed")
            return result
        except Exception as e:
            error_msg = error_message or f"{message} failed: {str(e)}"
            spinner.stop(success=False, final_message=error_msg)
            raise


# Convenience functions for common operations
def with_spinner(message: str = "Loading", style: str = 'dots'):
    """Decorator for adding spinner to functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return run_with_loading(
                func, args, kwargs, 
                message=message, 
                style=style,
                success_message=f"{func.__name__} completed"
            )
        return wrapper
    return decorator


# Export main classes and functions
__all__ = [
    'LoadingSpinner',
    'ProgressBar', 
    'LoadingDots',
    'loading_animation',
    'run_with_loading',
    'with_spinner'
]