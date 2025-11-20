"""
Menu navigation and input handling
"""
import sys
from typing import Optional, List, Callable, Any


class MenuNavigation:
    """Handles menu navigation and user input"""
    
    def __init__(self):
        self._has_termios: bool = self._check_termios()
        self._has_msvcrt: bool = self._check_msvcrt()
    
    def _check_termios(self) -> bool:
        """Check if termios is available"""
        try:
            import tty
            import termios
            return True
        except ImportError:
            return False
    
    def _check_msvcrt(self) -> bool:
        """Check if msvcrt is available"""
        try:
            import msvcrt
            return True
        except ImportError:
            return False
    
    def has_arrow_support(self) -> bool:
        """Check if terminal supports arrow keys"""
        return self._has_termios or self._has_msvcrt
    
    def get_choice_with_arrows(self, items: List[Any], renderer: Any, initial_display: bool = True) -> int:
        """Get user choice using arrow keys (if available)"""
        if self._has_msvcrt or self._has_termios:
            return self._arrow_navigation(items, renderer, initial_display)
        else:
            return self._traditional_input(items, renderer)
    
    def _arrow_navigation(self, items: List[Any], renderer: Any, initial_display: bool = True) -> int:
        """
        Navigate with arrow keys - optimized for responsiveness
        
        Improvements:
        - Smooth scrolling in small viewports
        - Minimal redraws for large menus
        - Proper cursor positioning
        - Terminal resize detection
        """
        selected_idx = 0
        
        # Initial display
        if initial_display:
            renderer.display(items, selected_idx, initial=True)
        sys.stdout.write(renderer.HIDE_CURSOR)
        sys.stdout.flush()

        try:
            while True:
                try:
                    key = self._getch()

                    old_idx = selected_idx
                    new_idx = selected_idx
                    should_exit = False
                    should_select = False

                    if self._has_msvcrt:  # Windows
                        if key in ('\xe0', '\x00'):
                            arrow = self._getch()
                            if arrow == 'H':  # Up
                                new_idx = (selected_idx - 1) % len(items)
                            elif arrow == 'P':  # Down
                                new_idx = (selected_idx + 1) % len(items)
                        elif key == '\r':  # Enter
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key == '\x03':  # Ctrl+C
                            should_exit = True
                            selected_idx = len(items) - 1
                            should_select = True

                    else:  # Unix/Linux/Mac
                        if key == '\x1b':  # ESC sequence
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':  # Up
                                    new_idx = (selected_idx - 1) % len(items)
                                elif arrow == 'B':  # Down
                                    new_idx = (selected_idx + 1) % len(items)
                        elif key in ['\r', '\n']:  # Enter
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                            should_exit = True
                            selected_idx = len(items) - 1
                            should_select = True

                    # Update selection if changed
                    if new_idx != old_idx:
                        selected_idx = new_idx
                        renderer.display(items, selected_idx, initial=False)

                    if should_select:
                        sys.stdout.write(renderer.SHOW_CURSOR)
                        sys.stdout.flush()
                        return selected_idx + 1

                except KeyboardInterrupt:
                    sys.stdout.write(renderer.SHOW_CURSOR)
                    sys.stdout.flush()
                    return len(items)
                except Exception as e:
                    # Log error but continue
                    continue

        finally:
            sys.stdout.write(renderer.SHOW_CURSOR)
            sys.stdout.flush()
    
    def _traditional_input(self, items: List[Any], renderer: Any) -> int:
        """Traditional number input method"""
        renderer.display(items, 0, initial=True)

        while True:
            try:
                choice = input("\nEnter your choice: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(items):
                    return choice_num
                print(f"Please enter a number between 1 and {len(items)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return len(items)
    
    def _getch(self) -> str:
        """Get a single character from stdin"""
        if self._has_msvcrt:  # Windows
            import msvcrt
            char = msvcrt.getch()
            try:
                return char.decode('utf-8')
            except:
                return chr(ord(char))
        elif self._has_termios:  # Unix/Linux/Mac
            import tty
            import termios
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