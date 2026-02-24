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
    previous_idx = -1  # Track previous selection for efficient updates

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

                # Update selection if changed - only redraw affected lines
                if new_idx != old_idx:
                    previous_idx = selected_idx
                    selected_idx = new_idx
                    _update_selection(options, previous_idx, selected_idx, prompt, show_numbers)

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


def _update_selection(options, old_idx, new_idx, prompt, show_numbers):
    """Update only the two changed lines - no screen clearing, no jumping"""
    # Calculate line positions (menu starts at line 1)
    base_line = 2  # Line 1 is the prompt
    
    # Build old line (now unselected)
    if show_numbers:
        old_line_text = f"  {old_idx + 1}. {options[old_idx]}"
    else:
        old_line_text = f"  {options[old_idx]}"
    
    # Build new line (now selected)
    if show_numbers:
        new_line_text = f"  {new_idx + 1}. {options[new_idx]}"
    else:
        new_line_text = f"  {options[new_idx]}"
    
    # Build escape sequences for both lines
    output = []
    
    # Update old selection (remove highlight)
    output.append(f'\033[{base_line + old_idx};1H')  # Move to old line
    output.append('\033[2K')  # Clear line
    output.append(old_line_text)
    
    # Update new selection (add highlight)
    output.append(f'\033[{base_line + new_idx};1H')  # Move to new line
    output.append('\033[2K')  # Clear line
    output.append(f"\033[1;46m   {new_line_text[4:]}\033[0m")
    
    # Write all at once
    sys.stdout.write(''.join(output))
    sys.stdout.flush()


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
    
    # Add instruction line (as separate line, no leading newline)
    output_lines.append("  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
    
    # Join all lines into single string
    return '\n'.join(output_lines)


def _display_options(options, selected_idx, prompt, show_numbers):
    """Display all options with current selection highlighted - initial display"""
    full_output = _build_menu_string(options, selected_idx, prompt, show_numbers)
    print(full_output)
    sys.stdout.flush()


def _update_selection(options, old_idx, new_idx, prompt, show_numbers):
    """Update only the two changed lines - no screen clearing, no jumping"""
    # Calculate line positions (menu starts at line 1)
    # Line 1: prompt
    # Lines 2 to len(options)+1: options
    # Line len(options)+2: instruction
    base_line = 2  # First option is on line 2
    
    # Build old line text (now unselected)
    if show_numbers:
        old_line_text = f"  {old_idx + 1}. {options[old_idx]}"
    else:
        old_line_text = f"  {options[old_idx]}"
    
    # Build new line text (now selected)
    if show_numbers:
        new_line_text = f"  {new_idx + 1}. {options[new_idx]}"
    else:
        new_line_text = f"  {options[new_idx]}"
    
    # Build escape sequences for both lines
    output = []
    
    # Update old selection (remove highlight)
    output.append(f'\033[{base_line + old_idx};1H')  # Move to old line
    output.append('\033[2K')  # Clear line
    output.append(old_line_text)
    
    # Update new selection (add highlight)
    output.append(f'\033[{base_line + new_idx};1H')  # Move to new line
    output.append('\033[2K')  # Clear line
    output.append(f"\033[1;46m   {new_line_text[4:]}\033[0m")
    
    # Write all at once
    sys.stdout.write(''.join(output))
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
