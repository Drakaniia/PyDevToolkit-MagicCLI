"""
automation/dev_mode/menu_utils.py
Shared menu utilities for dev mode commands with arrow key navigation
"""
import sys
import os

# Try to import platform-specific modules
try:
    import tty
    import termios
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


def get_choice_with_arrows(options, prompt="Your choice", show_numbers=True):
    """
    Display options and get user choice with arrow key navigation
    
    Args:
        options: List of option strings to display
        prompt: Prompt text to show
        show_numbers: Whether to show numbers (1, 2, 3...) for each option
    
    Returns:
        int: 1-based index of selected option
    """
    if not options:
        return 1
    
    # Check if arrow keys are supported
    if not (HAS_TERMIOS or HAS_MSVCRT):
        return _traditional_choice_input(options, prompt, show_numbers)
    
    return _arrow_choice_input(options, prompt, show_numbers)


def _traditional_choice_input(options, prompt, show_numbers):
    """Traditional number input method for systems without arrow key support"""
    while True:
        try:
            choice = input(f"\n{prompt} (1-{len(options)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled")
            return len(options)  # Return last option (usually Cancel/Exit)


def _arrow_choice_input(options, prompt, show_numbers):
    """Arrow key navigation input method"""
    selected_idx = 0
    
    # Initial display
    _display_options(options, selected_idx, prompt, show_numbers)
    _hide_cursor()
    
    try:
        while True:
            try:
                key = _getch()
                
                old_idx = selected_idx
                new_idx = selected_idx
                should_select = False
                
                if HAS_MSVCRT:  # Windows
                    if key in ('\xe0', '\x00'):
                        arrow = _getch()
                        if arrow == 'H':  # Up
                            new_idx = (selected_idx - 1) % len(options)
                        elif arrow == 'P':  # Down
                            new_idx = (selected_idx + 1) % len(options)
                    elif key == '\r':  # Enter
                        should_select = True
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(options):
                            selected_idx = num - 1
                            should_select = True
                    elif key == '\x03':  # Ctrl+C
                        selected_idx = len(options) - 1
                        should_select = True
                
                else:  # Unix/Linux/Mac
                    if key == '\x1b':  # ESC sequence
                        next_key = _getch()
                        if next_key == '[':
                            arrow = _getch()
                            if arrow == 'A':  # Up
                                new_idx = (selected_idx - 1) % len(options)
                            elif arrow == 'B':  # Down
                                new_idx = (selected_idx + 1) % len(options)
                    elif key in ['\r', '\n']:  # Enter
                        should_select = True
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(options):
                            selected_idx = num - 1
                            should_select = True
                    elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                        selected_idx = len(options) - 1
                        should_select = True
                
                # Update selection if changed - use full redraw instead of partial update
                if new_idx != old_idx:
                    selected_idx = new_idx
                    _redraw_options(options, selected_idx, prompt, show_numbers)
                
                if should_select:
                    _show_cursor()
                    print()  # Add newline after selection
                    return selected_idx + 1
            
            except KeyboardInterrupt:
                _show_cursor()
                print("\n\nOperation cancelled")
                return len(options)  # Return last option (usually Cancel/Exit)
            except Exception:
                # Continue on any other errors
                continue
    
    finally:
        _show_cursor()


def _display_options(options, selected_idx, prompt, show_numbers):
    """Display all options with current selection highlighted"""
    print(f"\n{prompt}:")
    for i, option in enumerate(options):
        if show_numbers:
            line_text = f"  {i + 1}. {option}"
        else:
            line_text = f"  {option}"
        
        if i == selected_idx:
            # Highlighted selection
            print(f"\033[1;46m   {line_text[4:]}\033[0m")
        else:
            print(line_text)
    
    print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")


def _redraw_options(options, selected_idx, prompt, show_numbers):
    """Redraw the entire options menu - more reliable than partial updates"""
    # Calculate how many lines to clear (options + prompt + instruction line)
    lines_to_clear = len(options) + 3
    
    # Move cursor up to the start of the menu
    sys.stdout.write(f'\033[{lines_to_clear}A')
    
    # Clear all the lines
    for _ in range(lines_to_clear):
        sys.stdout.write('\033[2K\n')  # Clear line and move down
    
    # Move cursor back up to start redrawing
    sys.stdout.write(f'\033[{lines_to_clear}A')
    
    # Redraw the complete menu
    print(f"{prompt}:")
    for i, option in enumerate(options):
        if show_numbers:
            line_text = f"  {i + 1}. {option}"
        else:
            line_text = f"  {option}"
        
        if i == selected_idx:
            # Highlighted selection
            print(f"\033[1;46m   {line_text[4:]}\033[0m")
        else:
            print(line_text)
    
    print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
    sys.stdout.flush()


def _getch():
    """Get a single character from stdin"""
    if HAS_MSVCRT:  # Windows
        char = msvcrt.getch()
        try:
            return char.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            return chr(ord(char))
    elif HAS_TERMIOS:  # Unix/Linux/Mac
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    else:
        return input()


def _hide_cursor():
    """Hide terminal cursor"""
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()


def _show_cursor():
    """Show terminal cursor"""
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()