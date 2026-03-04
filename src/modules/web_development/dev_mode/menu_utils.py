import sys
import os

# Platform-specific imports for keyboard input handling
if sys.platform == "win32":
    # Windows-specific modules
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    # Unix-specific modules
    import tty
    import termios

"""
automation/dev_mode/menu_utils.py
Shared menu utilities for dev mode commands with arrow key navigation
"""

# Determine platform-specific module availability
if sys.platform == "win32":
    HAS_TERMIOS = False
    HAS_MSVCRT = msvcrt is not None
else:
    HAS_TERMIOS = True
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
    """Arrow key navigation input method with stable viewport"""
    selected_idx = 0
    previous_idx = -1

    _display_options(options, selected_idx, prompt, show_numbers)
    _hide_cursor()

    # Calculate base line for menu items:
    # Line 1: prompt
    # Lines 2+: options (starting from line 2)
    # Last line + 1: instruction line (static, not updated)
    base_line = 2  # Options start from line 2 (1-indexed)

    try:
        while True:
            try:
                key = _getch()

                old_idx = selected_idx
                new_idx = selected_idx
                should_select = False

                if HAS_MSVCRT:
                    if key in ('\xe0', '\x00'):
                        arrow = _getch()
                        if arrow == 'H':
                            new_idx = (selected_idx - 1) % len(options)
                        elif arrow == 'P':
                            new_idx = (selected_idx + 1) % len(options)
                    elif key == '\r':
                        should_select = True
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(options):
                            selected_idx = num - 1
                            should_select = True
                    elif key == '\x03':
                        selected_idx = len(options) - 1
                        should_select = True

                else:
                    if key == '\x1b':
                        next_key = _getch()
                        if next_key == '[':
                            arrow = _getch()
                            if arrow == 'A':
                                new_idx = (selected_idx - 1) % len(options)
                            elif arrow == 'B':
                                new_idx = (selected_idx + 1) % len(options)
                    elif key in ['\r', '\n']:
                        should_select = True
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(options):
                            selected_idx = num - 1
                            should_select = True
                    elif key in ['\x03', '\x04']:
                        selected_idx = len(options) - 1
                        should_select = True

                if new_idx != old_idx:
                    previous_idx = selected_idx
                    selected_idx = new_idx
                    _update_selection(options, previous_idx, selected_idx, base_line, show_numbers)

                if should_select:
                    _show_cursor()
                    print()
                    return selected_idx + 1

            except KeyboardInterrupt:
                _show_cursor()
                print("\n\nOperation cancelled")
                return len(options)
            except Exception:
                continue

    finally:
        _show_cursor()


def _build_menu_string(options, selected_idx, prompt, show_numbers):
    """Build the complete menu as a single string - internal helper"""
    output_lines = []

    # Add prompt
    output_lines.append(f"{prompt}:")

    # Add all options
    for i, option in enumerate(options):
        if show_numbers:
            line_text = f"  {i + 1}. {option}"
        else:
            line_text = f"  {option}"

        if i == selected_idx:
            # Highlighted selection
            output_lines.append(f"\033[1;46m   {line_text[4:]}\033[0m")
        else:
            output_lines.append(line_text)

    # Join all lines into single string
    return '\n'.join(output_lines)


def _display_options(options, selected_idx, prompt, show_numbers):
    """Display all options with current selection highlighted - initial display"""
    # Move cursor to line 1 and clear screen below to ensure menu displays at top
    # This prevents the menu from appearing at the bottom of previous output
    sys.stdout.write('\033[1;1H\033[J')  # Move to line 1, column 1 and clear to end of screen
    sys.stdout.flush()
    
    full_output = _build_menu_string(options, selected_idx, prompt, show_numbers)
    print(full_output, flush=True)
    # Print instruction line separately (static, not part of dynamic content)
    print("  Use ↑/↓ arrow keys to navigate, Enter to select, or type number", flush=True)


def _update_selection(options, old_idx, new_idx, base_line, show_numbers):
    """Update only the two changed lines - no screen clearing, no jumping"""
    if show_numbers:
        old_line_text = f"  {old_idx + 1}. {options[old_idx]}"
        new_line_text = f"  {new_idx + 1}. {options[new_idx]}"
    else:
        old_line_text = f"  {options[old_idx]}"
        new_line_text = f"  {options[new_idx]}"
    
    sys.stdout.write(
        f'\033[{base_line + old_idx};1H\033[2K{old_line_text}'
        f'\033[{base_line + new_idx};1H\033[2K\033[1;46m   {new_line_text[4:]}\033[0m'
    )
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
